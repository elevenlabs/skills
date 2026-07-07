# Speech-to-Text in Clinical Workflows

Using ElevenLabs Scribe (`scribe_v2` / `scribe_v2_realtime`) to transcribe doctor-patient conversations and turn them into structured clinical notes.

## Transcribing Doctor-Patient Conversations

The two features that matter most for a clinical encounter recording are **diarization** (separating doctor from patient) and **PHI-aware entity handling** (flagging or redacting protected health information in the transcript itself).

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

with open("visit_recording.mp3", "rb") as audio_file:
    result = client.speech_to_text.convert(
        model_id="scribe_v2",
        file=audio_file,
        diarize=True,               # separate speakers (doctor vs. patient)
        num_speakers=2,              # cap prediction to the expected count
        timestamps_granularity="word",
        tag_audio_events=True,       # capture coughing, pauses, etc. as events
        entity_detection="phi",      # flag PHI spans in the response
    )

print(result.text)
for word in result.words:
    print(f"[{word.speaker_id}] {word.text} ({word.start}s-{word.end}s)")
```

For call-center-style intake lines where roles are fixed (agent vs. caller rather than clinician vs. patient), `detect_speaker_roles=True` alongside `diarize=True` labels speakers as `agent`/`customer` instead of `speaker_0`/`speaker_1` — not compatible with `use_multi_channel=True`.

### Redacting PHI at Transcription Time

If the transcript itself needs to be safe to store or pass to a non-clinical system (analytics, QA review), redact instead of just detect. `entity_redaction` accepts the same category values as `entity_detection` (`'pii'`, `'phi'`, `'pci'`, `'other'`, `'offensive_language'`, or `'all'`), and must be a subset of what's enabled in `entity_detection`:

```python
result = client.speech_to_text.convert(
    model_id="scribe_v2",
    file=audio_file,
    diarize=True,
    entity_detection="phi",
    entity_redaction="phi",
    entity_redaction_mode="entity_type",  # -> "{PHI}" style placeholders in text
)

print(result.text)  # PHI spans replaced with placeholders, not raw text
```

`entity_redaction_mode` options: `"redacted"` (`{REDACTED}`), `"entity_type"` (`{ENTITY_TYPE}`), `"enumerated_entity_type"` (`{ENTITY_TYPE_1}`, `{ENTITY_TYPE_2}`, ...). Note both `entity_detection` and `entity_redaction` add a surcharge to the base transcription cost — factor that into per-encounter cost estimates.

### Keyterm Prompting for Clinical Vocabulary

Bias the model toward drug names, facility names, or clinical terms it might otherwise mis-transcribe (up to 1000 keyterms, each under 50 characters, max 5 words per term):

```python
result = client.speech_to_text.convert(
    model_id="scribe_v2",
    file=audio_file,
    keyterms=["levothyroxine", "atorvastatin", "PHQ-9", "St. Mary's Clinic"],
)
```

## Streaming vs. Batch — When to Use Each

| | Batch (`speech_to_text.convert`) | Real-time (`speech_to_text.realtime.connect`) |
|---|---|---|
| **Model** | `scribe_v2` | `scribe_v2_realtime` |
| **Latency** | Whole file processed at once | ~150ms |
| **Use for** | Recorded visits, uploaded consult recordings, retrospective QA | Live transcription during a telehealth visit, live captioning, voice agent input |
| **Diarization** | `diarize=True`, `num_speakers`, `detect_speaker_roles` | Speaker separation handled differently — check current real-time capabilities before relying on it for multi-speaker live encounters |
| **PHI handling** | `entity_detection`/`entity_redaction` on the full response | Not part of the streaming event payload — apply redaction as a post-processing step on committed transcripts before storage |

Default to batch for anything that touches the medical record (a completed encounter that will produce a note) — you get the full response with entity detection/redaction in one call. Reach for real-time only when the transcript needs to affect something happening *during* the conversation (live captions, a voice agent deciding what to say next).

### Real-Time (Server-Side) Transcription

```python
import asyncio
from elevenlabs import ElevenLabs

client = ElevenLabs()

async def transcribe_visit_realtime(audio_url: str):
    async with client.speech_to_text.realtime.connect(
        model_id="scribe_v2_realtime",
        include_timestamps=True,
        keyterms=["levothyroxine", "PHQ-9"],
        no_verbatim=True,   # drop filler words/false starts from the transcript
    ) as connection:
        await connection.stream_url(audio_url)

        async for event in connection:
            if event.type == "partial_transcript":
                # interim result — use for live captions only, not the record
                print(f"Partial: {event.text}")
            elif event.type == "committed_transcript":
                # finalized segment — this is what you persist / redact / summarize
                print(f"Final: {event.text}")

asyncio.run(transcribe_visit_realtime("https://example.com/live-visit-audio"))
```

Treat `partial_transcript` events as UI-only. Only `committed_transcript` events are stable enough to redact, store, or feed into an LLM for note generation — partials can change as more audio arrives.

## Combining with LLMs for Clinical Note Generation

ElevenLabs transcribes; your LLM turns the diarized, PHI-redacted transcript into a structured note. Keep these as two distinct steps so you can audit and review each independently:

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

def transcribe_encounter(audio_path: str) -> str:
    with open(audio_path, "rb") as audio_file:
        result = client.speech_to_text.convert(
            model_id="scribe_v2",
            file=audio_file,
            diarize=True,
            num_speakers=2,
            entity_detection="phi",
            entity_redaction="phi",
            entity_redaction_mode="entity_type",
        )
    # Build a role-labeled transcript for the LLM
    lines = []
    current_speaker = None
    current_line = []
    for word in result.words:
        if word.type != "word":
            continue
        if word.speaker_id != current_speaker:
            if current_line:
                lines.append(f"{current_speaker}: {' '.join(current_line)}")
            current_speaker = word.speaker_id
            current_line = [word.text]
        else:
            current_line.append(word.text)
    if current_line:
        lines.append(f"{current_speaker}: {' '.join(current_line)}")
    return "\n".join(lines)


def draft_soap_note(redacted_transcript: str, llm_client) -> str:
    # redacted_transcript already has PHI replaced with {ENTITY_TYPE} placeholders
    prompt = (
        "Draft a SOAP note from this redacted clinical encounter transcript. "
        "Do not invent details not present in the transcript. "
        "Flag any {ENTITY_TYPE} placeholder for the clinician to fill in manually.\n\n"
        f"{redacted_transcript}"
    )
    return llm_client.generate(prompt)  # your LLM of choice
```

A drafted note should always go to the clinician for review before it's finalized in the chart — this pipeline produces a draft, not a signed note.

## Exact API Parameter Names (Avoid These Mistakes)

The parameter names below are easy to get wrong by guessing from other SDKs. These are the real names from `elevenlabs-python`:

| Correct parameter | Common mistake |
|---|---|
| `model_id` | `model` |
| `file` | `audio_file`, `audio` |
| `diarize` | `diarization`, `enable_diarization` |
| `num_speakers` | `speaker_count`, `max_speakers` |
| `timestamps_granularity` | `granularity`, `timestamp_level` |
| `entity_detection` | `pii_detection`, `detect_entities` |
| `entity_redaction` | `redact_entities`, `redact_pii` |
| `entity_redaction_mode` | `redaction_format` |
| `detect_speaker_roles` | `speaker_roles`, `role_detection` |
| `tag_audio_events` | `audio_events`, `detect_events` |
| `no_verbatim` | `clean_transcript`, `remove_fillers` |
| `keyterms` | `hotwords`, `boost_words`, `vocabulary` |
| `language_code` | `language`, `lang` |

Full `convert()` signature for reference:

```python
def convert(
    *,
    model_id: str,                       # "scribe_v2" | "scribe_v2_realtime"
    enable_logging: bool | None = None,   # False = zero-retention mode
    file: "core.File | None" = None,
    language_code: str | None = None,     # ISO-639-1 or ISO-639-3
    tag_audio_events: bool | None = None,
    num_speakers: int | None = None,      # max 32
    timestamps_granularity: str | None = None,  # "word" | "character"
    diarize: bool | None = None,
    diarization_threshold: float | None = None,  # requires diarize=True, num_speakers=None
    file_format: str | None = None,       # "pcm_s16le_16" | "other"
    source_url: str | None = None,        # transcribe from a hosted URL instead of a file
    temperature: float | None = None,     # 0.0-2.0
    seed: int | None = None,
    use_multi_channel: bool | None = None,
    entity_detection: str | list[str] | None = None,   # "all" | "pii" | "phi" | "pci" | ...
    entity_redaction: str | list[str] | None = None,    # must be subset of entity_detection
    entity_redaction_mode: str | None = None,           # "redacted" | "entity_type" | "enumerated_entity_type"
    no_verbatim: bool | None = None,
    detect_speaker_roles: bool | None = None,   # requires diarize=True, incompatible with use_multi_channel
    keyterms: list[str] | None = None,          # max 1000 items, each <50 chars, <=5 words
) -> SpeechToTextConvertResponse: ...
```

## Error Handling

```python
try:
    result = client.speech_to_text.convert(model_id="scribe_v2", file=audio_file, diarize=True)
except Exception as e:
    print(f"Transcription failed: {e}")
```

Common errors: **401** (invalid API key), **422** (invalid parameters — e.g., `diarization_threshold` set without `diarize=True`), **429** (rate limit).
