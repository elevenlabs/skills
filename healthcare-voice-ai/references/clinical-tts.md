# Clinical Text-to-Speech Patterns

Converting clinical notes, SOAP notes, and medication lists to speech reliably — including getting medical terminology right and handling multi-speaker scenarios.

## Converting Clinical Notes and SOAP Notes to Speech

Clinical notes are long-form and structured (Subjective / Objective / Assessment / Plan). Two things matter more here than in general narration TTS: getting through the full note without pops or tone drift at chunk boundaries, and pronouncing medical shorthand correctly.

For a note short enough for a single request, `eleven_multilingual_v2` (higher quality, not optimized for lowest latency) is the right model — this is being read back for review, not an urgent alert:

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

soap_note_text = (
    "Subjective: patient reports shortness of breath for two days. "
    "Objective: blood pressure 128 over 82, heart rate 88. "
    "Assessment: acute bronchitis. "
    "Plan: azithromycin 500 milligrams by mouth once daily for 3 days."
)

audio = client.text_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",  # George
    text=soap_note_text,
    model_id="eleven_multilingual_v2",
    apply_text_normalization="on",
)

with open("soap_note.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

For notes too long for one request, use **request stitching** (`previous_text` / `next_text` or `previous_request_ids` / `next_request_ids`) so section boundaries don't produce audio pops or unnatural pauses:

```python
# Subjective section
audio_1 = client.text_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    text="Subjective: patient reports shortness of breath for two days.",
    model_id="eleven_multilingual_v2",
    next_text="Objective: blood pressure 128 over 82, heart rate 88.",
)

# Objective section, aware of what came before
audio_2 = client.text_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    text="Objective: blood pressure 128 over 82, heart rate 88.",
    model_id="eleven_multilingual_v2",
    previous_text="Subjective: patient reports shortness of breath for two days.",
    next_text="Assessment: acute bronchitis.",
)
```

## Handling Medical Terminology Correctly

Generic TTS mispronounces drug names, dosage units, and clinical abbreviations by default. There are two fixes, and they solve different problems.

### 1. Pre-expand abbreviations before sending text

Abbreviations are ambiguous to a language model reading them cold (`"PRN"`, `"BID"`, `"SOB"`, `"q.i.d."`). Expand them in your application layer before the TTS call — this is more reliable than hoping the model infers clinical context:

```python
CLINICAL_ABBREVIATIONS = {
    "PRN": "as needed",
    "BID": "twice daily",
    "TID": "three times daily",
    "QID": "four times daily",
    "SOB": "shortness of breath",
    "NPO": "nothing by mouth",
    "STAT": "immediately",
}

def expand_abbreviations(text: str) -> str:
    for abbr, expansion in CLINICAL_ABBREVIATIONS.items():
        text = text.replace(abbr, expansion)
    return text
```

### 2. Use pronunciation dictionaries for drug names and terms you can't just expand

For terms that need a specific pronunciation rather than a text substitution (drug brand names, dosage units, clinical jargon that should be spoken a particular way), create a pronunciation dictionary from rules using the real SDK types:

```python
from elevenlabs import ElevenLabs
from elevenlabs.pronunciation_dictionaries import (
    BodyAddAPronunciationDictionaryV1PronunciationDictionariesAddFromRulesPostRulesItem_Alias,
)

client = ElevenLabs()

dictionary = client.pronunciation_dictionaries.create_from_rules(
    name="Clinical Drug Names",
    description="Pronunciation fixes for commonly mispronounced drug names",
    rules=[
        BodyAddAPronunciationDictionaryV1PronunciationDictionariesAddFromRulesPostRulesItem_Alias(
            string_to_replace="levothyroxine",
            alias="lee-voh-thy-ROCK-sin",
            case_sensitive=False,
            word_boundaries=True,
        ),
        BodyAddAPronunciationDictionaryV1PronunciationDictionariesAddFromRulesPostRulesItem_Alias(
            string_to_replace="mg",
            alias="milligrams",
            case_sensitive=True,
            word_boundaries=True,
        ),
    ],
)

print(dictionary.id, dictionary.version_id)
```

Then apply it on every clinical TTS request via `pronunciation_dictionary_locators` (accepts up to 3 locators per request):

```python
from elevenlabs.types import PronunciationDictionaryVersionLocator

audio = client.text_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    text="Prescribe levothyroxine 50 mg once daily.",
    model_id="eleven_multilingual_v2",
    pronunciation_dictionary_locators=[
        PronunciationDictionaryVersionLocator(
            pronunciation_dictionary_id=dictionary.id,
            version_id=dictionary.version_id,
        )
    ],
)
```

Store the dictionary ID and version ID in your application config once created — do not recreate the dictionary on every request.

## Converting Medication Lists to Speech

Medication lists are a sequence of discrete, structurally similar items (drug, dose, route, frequency). Read them as a paced list rather than one run-on sentence — insert brief pauses between items so a listener can track where one medication ends and the next begins:

```python
medications = [
    "Lisinopril, 10 milligrams, by mouth, once daily.",
    "Metformin, 500 milligrams, by mouth, twice daily.",
    "Atorvastatin, 20 milligrams, by mouth, at bedtime.",
]

# Join with a pause marker the model respects as a break; a period plus
# short silence reads more clearly than a comma-separated run-on list.
medication_list_text = " ".join(medications)

audio = client.text_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    text=medication_list_text,
    model_id="eleven_multilingual_v2",
    apply_text_normalization="on",
    pronunciation_dictionary_locators=[
        PronunciationDictionaryVersionLocator(
            pronunciation_dictionary_id=dictionary.id,
            version_id=dictionary.version_id,
        )
    ],
)
```

## Multi-Speaker Scenarios: Doctor / Patient / System Alert Voices

When a single audio experience needs to represent multiple roles (e.g., replaying a visit summary that quotes both clinician and patient, or a system that narrates alerts distinctly from conversational responses), assign a fixed, distinct voice per role and generate each role's lines as separate requests, then concatenate the audio:

```python
ROLE_VOICES = {
    "system_alert": "onwK4e9ZLuTAKqWW03F9",  # Daniel - authoritative, for alerts
    "clinician": "JBFqnCBsd6RMkjVDRZzb",     # George - narrative, for notes/summaries
    "patient_voice_agent": "EXAVITQu4vr4xnSDxMaL",  # Sarah - conversational, patient-facing
}

def synthesize_role_line(role: str, text: str, model_id: str = "eleven_multilingual_v2") -> bytes:
    voice_id = ROLE_VOICES[role]
    audio_chunks = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id=model_id,
    )
    return b"".join(audio_chunks)

visit_summary_audio = b"".join([
    synthesize_role_line("system_alert", "Visit summary follows."),
    synthesize_role_line("clinician", "Assessment: acute bronchitis. Plan: azithromycin 500 milligrams daily for 3 days."),
])

with open("visit_summary.mp3", "wb") as f:
    f.write(visit_summary_audio)
```

Keep the role-to-voice mapping fixed and centrally configured (not chosen per-request) so a listener learns to associate a given voice with a given role — this matters clinically, since a patient should always be able to tell a system-generated alert from a clinician's own recorded note.

## Function Signatures Reference (elevenlabs-python)

To avoid parameter-name mistakes, the core signatures used above:

```python
# client.text_to_speech.convert(...)
def convert(
    voice_id: str,
    *,
    text: str,
    enable_logging: bool | None = None,
    optimize_streaming_latency: int | None = None,
    output_format: str | None = None,
    model_id: str | None = None,
    language_code: str | None = None,
    voice_settings: VoiceSettings | None = None,
    pronunciation_dictionary_locators: list[PronunciationDictionaryVersionLocator] | None = None,
    seed: int | None = None,
    previous_text: str | None = None,
    next_text: str | None = None,
    previous_request_ids: list[str] | None = None,
    next_request_ids: list[str] | None = None,
    apply_text_normalization: str | None = None,   # "auto" | "on" | "off"
    apply_language_text_normalization: bool | None = None,
) -> typing.Iterator[bytes]: ...

# client.pronunciation_dictionaries.create_from_rules(...)
def create_from_rules(
    *,
    rules: list,       # Alias or Phoneme rule objects
    name: str,
    description: str | None = None,
    workspace_access: str | None = None,   # "admin" | "editor" | "viewer"
) -> AddPronunciationDictionaryResponseModel: ...
```

`voice_id` is positional-or-keyword and comes first; every other TTS parameter is keyword-only (note the `*` in the signature). Passing `text=` and `voice_id=` as keywords always works and is what the official examples use.
