# Transcription Options

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file | Yes | Audio or video file to transcribe |
| `model_id` | string | Yes | `scribe_v2` (or legacy `scribe_v1`) for batch transcription |
| `language_code` | string | No | Language hint (ISO 639-1 or ISO 639-3, e.g., `en` or `eng`) |
| `timestamps_granularity` | string | No | `none`, `word`, or `character` (default: `word`) |
| `diarize` | boolean | No | Enable speaker diarization (default: `false`; up to 32 speakers) |
| `num_speakers` | integer | No | Maximum speakers to detect (up to 32 for batch) |
| `diarization_threshold` | number | No | Tune diarization sensitivity (default: ~0.22; only when `diarize=true` and `num_speakers` is not set) |
| `keyterms` | array | No | Terms to bias transcription (up to 100 terms; each ≤50 chars, ≤5 words) |
| `tag_audio_events` | boolean | No | Detect non-speech sounds like laughter, applause (default: `true`) |
| `entity_detection` | string or array | No | Detect entities (e.g., `pii`, `phi`, `pci`, `offensive_language`) |
| `use_multi_channel` | boolean | No | Split multichannel audio into separate transcripts (default: `false`; max 5 channels, max 1 hour) |
| `cloud_storage_url` | string | No | HTTPS URL to transcribe instead of uploading a file (max 2GB) |
| `webhook` | boolean | No | Process async and send result to webhook (default: `false`) |
| `webhook_id` | string | No | Target specific webhook (only when `webhook=true`) |
| `webhook_metadata` | string or object | No | Custom metadata included in webhook responses (max 16KB) |
| `temperature` | double | No | Output randomness (0.0-2.0); defaults vary by model |
| `seed` | integer | No | Deterministic output (0-2147483647); same seed = same result |
| `additional_formats` | array | No | Export transcript as `docx`, `html`, `pdf`, `srt`, `txt`, or `segmented_json` |
| `file_format` | string | No | `pcm_s16le_16` (for lower latency) or `other` (default) |
| `enable_logging` | boolean | No | Set `false` for zero retention mode (enterprise only; default: `true`) |

## Python Example

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

with open("audio.mp3", "rb") as audio_file:
    result = client.speech_to_text.convert(
        file=audio_file,
        model_id="scribe_v2",
        language_code="eng",
        timestamps_granularity="word",
        diarize=True,
        keyterms=["ElevenLabs", "Scribe"]
    )
```

## JavaScript Example

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createReadStream } from "fs";

const client = new ElevenLabsClient();

const result = await client.speechToText.convert({
  file: createReadStream("audio.mp3"),
  modelId: "scribe_v2",
  languageCode: "eng",
  timestampsGranularity: "word",
  diarize: true,
  keyterms: ["ElevenLabs", "Scribe"],
});
```

## cURL Example

```bash
curl -X POST "https://api.elevenlabs.io/v1/speech-to-text" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "file=@audio.mp3" \
  -F "model_id=scribe_v2" \
  -F "language_code=eng" \
  -F "timestamps_granularity=word" \
  -F "diarize=true"
```

## Response Structure

```json
{
  "text": "The complete transcribed text from the audio file.",
  "language_code": "eng",
  "language_probability": 0.98,
  "words": [
    {
      "text": "The",
      "start": 0.0,
      "end": 0.15,
      "type": "word",
      "speaker_id": "speaker_0"
    },
    {
      "text": " ",
      "start": 0.15,
      "end": 0.16,
      "type": "spacing",
      "speaker_id": "speaker_0"
    }
  ]
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Full transcription text |
| `language_code` | string | Detected language (ISO 639-1 or ISO 639-3) |
| `language_probability` | float | Confidence in detection (0-1) |
| `words` | array | Word-level timestamps (if requested) |
| `words[].text` | string | The transcribed word or spacing |
| `words[].start` | float | Start time in seconds |
| `words[].end` | float | End time in seconds |
| `words[].type` | string | `word`, `spacing`, or `audio_event` |
| `words[].speaker_id` | string | Speaker identifier (if diarization enabled) |
| `transcription_id` | string | Unique identifier for this transcription |
| `additional_formats` | array | Exported transcript formats (if requested) |
| `entities` | array | Detected entities with text, type, and character offsets (if entity_detection enabled) |

## Supported Languages (90+)

Common languages (ISO 639-3 codes):

| Code | Language | Code | Language |
|------|----------|------|----------|
| `eng` | English | `jpn` | Japanese |
| `spa` | Spanish | `kor` | Korean |
| `fra` | French | `zho` | Mandarin |
| `deu` | German | `ara` | Arabic |
| `ita` | Italian | `hin` | Hindi |
| `por` | Portuguese | `tur` | Turkish |
| `nld` | Dutch | `swe` | Swedish |
| `pol` | Polish | `dan` | Danish |
| `rus` | Russian | `fin` | Finnish |

Full list: Afrikaans, Amharic, Armenian, Azerbaijani, Belarusian, Bengali, Bosnian, Bulgarian, Burmese, Cantonese, Catalan, Cebuano, Croatian, Czech, Estonian, Filipino, Georgian, Greek, Gujarati, Hausa, Hebrew, Hungarian, Icelandic, Indonesian, Irish, Javanese, Kannada, Kazakh, Khmer, Kyrgyz, Lao, Latvian, Lithuanian, Luxembourgish, Macedonian, Malay, Malayalam, Maltese, Māori, Marathi, Mongolian, Nepali, Norwegian, Odia, Pashto, Persian, Punjabi, Romanian, Serbian, Shona, Sindhi, Slovak, Slovenian, Somali, Swahili, Tamil, Tajik, Telugu, Thai, Ukrainian, Urdu, Uzbek, Vietnamese, Welsh, Wolof, Xhosa, Yoruba, Zulu.

## Format Requirements

**Audio:** MP3, WAV, M4A, FLAC, OGG, WebM, AAC, AIFF, Opus
**Video:** MP4, AVI, MKV, MOV, WMV, FLV, WebM, MPEG, 3GPP

**Limits:**
- Maximum file size: 3GB (file upload) or 2GB (cloud storage URL)
- Maximum duration: 10 hours (standard) or 1 hour (multichannel mode)

## Use Cases

### Subtitle Generation with Speakers

```python
result = client.speech_to_text.convert(
    file=audio_file,
    model_id="scribe_v2",
    timestamps_granularity="word",
    diarize=True
)

# Generate SRT with speaker labels
for i, word in enumerate(result.words, 1):
    if word.type == "word":
        print(f"[{word.speaker_id}] {word.text} ({word.start:.2f}s)")
```

### Meeting Transcription with Custom Terms

```python
with open("meeting.mp3", "rb") as f:
    result = client.speech_to_text.convert(
        file=f,
        model_id="scribe_v2",
        diarize=True,
        keyterms=["Q4 forecast", "revenue target", "ACME Corp"]
    )

# Group by speaker
current_speaker = None
for word in result.words:
    if word.type == "word":
        if word.speaker_id != current_speaker:
            current_speaker = word.speaker_id
            print(f"\n[{current_speaker}]:", end=" ")
        print(word.text, end="")
```
