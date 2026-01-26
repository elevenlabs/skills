# Transcription Options

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file | Yes | Audio or video file to transcribe |
| `model_id` | string | Yes | `scribe_v2` or `scribe_v2_realtime` |
| `language_code` | string | No | Language hint (ISO 639-3 code, e.g., `eng`) |
| `timestamps_granularity` | string | No | `none`, `word`, or `character` (default: `word`) |
| `diarize` | boolean | No | Enable speaker diarization (up to 48 speakers) |
| `keyterms` | array | No | Terms to bias transcription (up to 100) |
| `tag_audio_events` | boolean | No | Detect non-speech sounds (laughter, applause) |

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
| `language_code` | string | Detected language (ISO 639-3) |
| `language_probability` | float | Confidence in detection (0-1) |
| `words` | array | Word-level timestamps (if requested) |
| `words[].text` | string | The transcribed word or spacing |
| `words[].start` | float | Start time in seconds |
| `words[].end` | float | End time in seconds |
| `words[].type` | string | `word`, `spacing`, or `audio_event` |
| `words[].speaker_id` | string | Speaker identifier (if diarization enabled) |

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
- Maximum file size: 3GB
- Maximum duration: 10 hours

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
