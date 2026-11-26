# Transcription: OpenAI to ElevenLabs

For `audio.transcriptions.create(...)` on a whole file and direct calls to `POST https://api.openai.com/v1/audio/transcriptions`.

The examples were checked against `elevenlabs` 2.80.0 (Python) and `@elevenlabs/elevenlabs-js` 2.80.0. If the installed SDK disagrees with them, the installed SDK is right.

## Settings

Every setting an OpenAI transcription call can pass, and what happens to it:

| OpenAI | ElevenLabs | Rule |
| --- | --- | --- |
| `model`: `whisper-1`, `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, or a dated version of one | `model_id` / `modelId`: `scribe_v3` | Always set it. |
| Nothing: OpenAI's text holds only what was said | `tag_audio_events=False` / `tagAudioEvents: false` | Always pass it. ElevenLabs otherwise writes sounds such as `(laughter)` into the text. |
| `model`: `gpt-4o-transcribe-diarize` | `scribe_v3` with `diarize=True` / `diarize: true` | See [Speaker labels](#speaker-labels). |
| `file` | `file` | See [Files](#files). |
| `language`, such as `en` | `language_code` / `languageCode` | Same value. |
| `temperature` | `temperature` | Same value. |
| `response_format`: not set, `json` or `text` | None | Drop it and read `result.text`. With `text`, OpenAI returned a plain string, so `result.text` replaces the whole value. |
| `response_format`: `verbose_json` | None | Drop it. See [Timestamps](#timestamps). |
| `response_format`: `srt` or `vtt` | `additional_formats` / `additionalFormats` | See [Subtitles](#subtitles). |
| `response_format`: `diarized_json` | `diarize` | See [Speaker labels](#speaker-labels). |
| `timestamp_granularities` | None | Drop it. Every transcript comes with word times. |
| `chunking_strategy` | None | Drop it. ElevenLabs takes a long file whole. |
| `prompt` | None | Drop it and tell the user. If it listed names or terms to spell correctly, tell them `keyterms` takes a list of such words. Don't build that list for them. |
| `include` (`logprobs`) | None | Leave the call on OpenAI and list it. |
| `known_speaker_names`, `known_speaker_references` | None | Leave the call on OpenAI and list it. |
| `stream`: `True` / `true` | None | Leave the call on OpenAI and list it. |
| `timeout`, `max_retries`, request headers | Request options | See [Errors, retries and timeouts](#errors-retries-and-timeouts). |
| `extra_body`, `extra_query`, or anything not in this table | None | Leave the call on OpenAI and list it. |

## Files

OpenAI stops at 25 MB. ElevenLabs takes files of several gigabytes, so code that splits or compresses audio to fit can stay as it is.

| OpenAI | ElevenLabs |
| --- | --- |
| Python: an open file, `file=open(path, "rb")` | The same |
| Python: `file=Path(path)` | Open it: `with open(path, "rb") as f:` and pass `f` |
| Python: `file=data` (bytes), `file=(filename, data)` | The same. Keep the filename where there is one |
| JavaScript: `fs.createReadStream(path)` | The same |
| JavaScript: a `File` or `Blob`, such as an upload from `formData` | The same |
| JavaScript: `await toFile(buffer, "audio.mp3")` | `{ data: buffer, filename: "audio.mp3" }` |

## How the transcript comes back

The plain text is `result.text` on both sides. Past that, the shapes differ:

| OpenAI | ElevenLabs |
| --- | --- |
| `transcript.text` | `result.text` |
| The transcript itself, with `response_format="text"` | `result.text` |
| `transcript.language`, a name such as `english` | `result.language_code` / `result.languageCode`, a code such as `eng`. A different value: if the app shows or compares it, tell the user. |
| `transcript.duration` | `result.audio_duration_secs` / `result.audioDurationSecs`, or the last word's `end` when it is missing |
| `transcript.words`: `word`, `start`, `end` | `result.words`: `text`, `start`, `end`, plus `type` and `speaker_id` / `speakerId`. See [Timestamps](#timestamps). |
| `transcript.segments`: `id`, `start`, `end`, `text` | Not returned. Build them from the words. See [Segments](#segments). |
| A segment's `avg_logprob`, `no_speech_prob`, `tokens`, `seek`, `compression_ratio`, `temperature` | None. If the app reads one, leave the call on OpenAI and list it. |
| `transcript.usage`, `transcript.logprobs` | None. If the app reads one, leave the call on OpenAI and list it. |

In a typed project, `convert` returns a union: the transcript, or the reply to a multichannel or webhook request, which this guide never makes. Narrow it once where the call is made.

### Python

Before:

```python
with open(path, "rb") as audio_file:
    transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
text = transcript.text
```

After:

```python
from elevenlabs import SpeechToTextChunkResponseModel

with open(path, "rb") as audio_file:
    result = elevenlabs.speech_to_text.convert(
        file=audio_file,
        model_id="scribe_v3",
        tag_audio_events=False,
    )
assert isinstance(result, SpeechToTextChunkResponseModel)
text = result.text
```

With `AsyncElevenLabs`, `await` the call: `result = await elevenlabs.speech_to_text.convert(...)`.

### JavaScript and TypeScript

Before:

```typescript
const transcript = await openai.audio.transcriptions.create({
  model: "whisper-1",
  file: fs.createReadStream(path),
});
const text = transcript.text;
```

After:

```typescript
const result = await elevenlabs.speechToText.convert({
  file: fs.createReadStream(path),
  modelId: "scribe_v3",
  tagAudioEvents: false,
});
if (!("text" in result)) throw new Error("Expected one transcript");
const text = result.text;
```

## Timestamps

OpenAI returns words only when asked (`verbose_json` with `timestamp_granularities=["word"]`). ElevenLabs always does, and its list holds more than words: each entry has a `type` of `word` or `spacing` (the space between two words), and `audio_event` for a sound when those are tagged. Keep only the words when the app expects OpenAI's list:

```python
words = [
    {"word": w.text, "start": w.start or 0.0, "end": w.end or 0.0}
    for w in result.words
    if w.type == "word"
]
```

```typescript
const words = result.words
  .filter((w) => w.type === "word")
  .map((w) => ({ word: w.text, start: w.start ?? 0, end: w.end ?? 0 }));
```

Times are in seconds on both sides.

## Segments

OpenAI's `verbose_json` groups the text into segments. ElevenLabs returns words, so where the app reads `transcript.segments`, build them: a new segment starts after a sentence ends, after a pause, or when the speaker changes. Add this once and call it where the app read `segments`:

```python
def segments(result, max_gap=1.0):
    out = []
    text, start, end, speaker = "", None, 0.0, ""

    def push():
        if text.strip():
            out.append({"id": len(out), "start": start or 0.0, "end": end, "text": text.strip(), "speaker": speaker})

    for w in result.words:
        if w.type == "audio_event":
            continue
        spoken = w.type == "word"
        if spoken and start is not None and (
            (w.speaker_id or "") != speaker
            or (w.start or 0.0) - end > max_gap
            or text.rstrip().endswith((".", "?", "!"))
        ):
            push()
            text, start = "", None
        if spoken:
            if start is None:
                start, speaker = w.start or 0.0, w.speaker_id or ""
            end = w.end or end
        text += w.text
    push()
    return out
```

```typescript
import type { ElevenLabs } from "@elevenlabs/elevenlabs-js";

interface Segment {
  id: number;
  start: number;
  end: number;
  text: string;
  speaker?: string;
}

function segments(result: ElevenLabs.SpeechToTextChunkResponseModel, maxGap = 1): Segment[] {
  const out: Segment[] = [];
  let text = "";
  let start: number | undefined;
  let end = 0;
  let speaker: string | undefined;
  const push = () => {
    if (text.trim()) out.push({ id: out.length, start: start ?? 0, end, text: text.trim(), speaker });
    text = "";
    start = undefined;
  };
  for (const w of result.words) {
    if (w.type === "audio_event") continue;
    const spoken = w.type === "word";
    if (
      spoken &&
      start !== undefined &&
      (w.speakerId !== speaker || (w.start ?? 0) - end > maxGap || /[.?!]$/.test(text.trimEnd()))
    ) {
      push();
    }
    if (spoken) {
      if (start === undefined) {
        start = w.start ?? 0;
        speaker = w.speakerId;
      }
      end = w.end ?? end;
    }
    text += w.text;
  }
  push();
  return out;
}
```

The segments won't break in exactly the places OpenAI's did. Tell the user if the app shows them.

## Subtitles

OpenAI returns SRT or VTT as the whole response. ElevenLabs returns it next to the transcript when asked:

```python
from elevenlabs import ExportOptions_Srt, SpeechToTextChunkResponseModel

result = elevenlabs.speech_to_text.convert(
    file=audio_file,
    model_id="scribe_v3",
    tag_audio_events=False,
    additional_formats=[ExportOptions_Srt()],
)
assert isinstance(result, SpeechToTextChunkResponseModel)
exported = (result.additional_formats or [None])[0]
srt = exported.content if exported else ""
```

```typescript
const result = await elevenlabs.speechToText.convert({
  file: fs.createReadStream(path),
  modelId: "scribe_v3",
  tagAudioEvents: false,
  additionalFormats: [{ format: "srt" }],
});
if (!("text" in result)) throw new Error("Expected one transcript");
const srt = result.additionalFormats?.[0]?.content ?? "";
```

There is no VTT export. Where the app asked for `vtt`, ask for SRT and convert it, which only changes the header and the decimal mark:

```python
import re

vtt = "WEBVTT\n\n" + re.sub(r"(\d{2}:\d{2}:\d{2}),(\d{3})", r"\1.\2", srt)
```

```typescript
const vtt = "WEBVTT\n\n" + srt.replace(/(\d{2}:\d{2}:\d{2}),(\d{3})/g, "$1.$2");
```

The subtitle lines won't break in exactly the places OpenAI's did. Tell the user.

## Speaker labels

`gpt-4o-transcribe-diarize` with `diarized_json` returns segments that each have a `speaker`. With ElevenLabs, pass `diarize`, and each word carries a `speaker_id` / `speakerId`. Build the segments with [the function above](#segments): it starts a new one when the speaker changes and puts the label on it.

```python
result = elevenlabs.speech_to_text.convert(
    file=audio_file,
    model_id="scribe_v3",
    tag_audio_events=False,
    diarize=True,
)
assert isinstance(result, SpeechToTextChunkResponseModel)
for segment in segments(result):
    print(segment["speaker"], segment["text"])
```

```typescript
const result = await elevenlabs.speechToText.convert({
  file: fs.createReadStream(path),
  modelId: "scribe_v3",
  tagAudioEvents: false,
  diarize: true,
});
```

The labels differ: OpenAI's are `A`, `B`, and ElevenLabs' are `speaker_0`, `speaker_1`. Tell the user if the app shows them.

## Direct HTTP calls

A Python or JavaScript/TypeScript project that calls `https://api.openai.com/v1/audio/transcriptions` itself (`requests`, `httpx`, `fetch`, `axios`) moves to the SDK call above: read the form fields as the settings in the table, and replace the code that read the JSON with the matching row in [How the transcript comes back](#how-the-transcript-comes-back). Remove the `Authorization` header the call built; the SDK sends the key.

## Errors, retries and timeouts

The errors to catch and the options for timeouts are the same as for text to speech: see [Errors, retries and timeouts](text-to-speech.md#errors-retries-and-timeouts). Two differences in Python: a transcription is sent when `convert` is called, so its `try` goes around the call itself, and it is retried twice by default, as OpenAI's was (`request_options={"max_retries": 3}` changes that).
