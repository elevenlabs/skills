---
name: speech-to-text
description: Transcribe audio to text using ElevenLabs Scribe. Use when converting audio/video to text, generating subtitles, transcribing meetings, or processing spoken content.
---

# ElevenLabs Speech-to-Text

Transcribe audio to text with Scribe v2 - supports 90+ languages, speaker diarization, entity detection, and word-level timestamps.

## Quick Start

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

with open("audio.mp3", "rb") as audio_file:
    result = client.speech_to_text.convert(
        file=audio_file,
        model_id="scribe_v2"
    )

print(result.text)
```

### JavaScript

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createReadStream } from "fs";

const client = new ElevenLabsClient();

const result = await client.speechToText.convert({
  file: createReadStream("audio.mp3"),
  modelId: "scribe_v2",
});

console.log(result.text);
```

### cURL

```bash
curl -X POST "https://api.elevenlabs.io/v1/speech-to-text" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "file=@audio.mp3" \
  -F "model_id=scribe_v2"
```

## Models

| Model ID | Description | Best For |
|----------|-------------|----------|
| `scribe_v2` | State-of-the-art accuracy, 90+ languages | Batch transcription, subtitles, long-form audio |
| `scribe_v2_realtime` | Low latency (~150ms) | Live transcription, voice agents |

## Transcription with Timestamps

Word-level timestamps include type classification and speaker identification:

### Python

```python
result = client.speech_to_text.convert(
    file=audio_file,
    model_id="scribe_v2",
    timestamps_granularity="word"
)

for word in result.words:
    print(f"{word.text}: {word.start}s - {word.end}s (type: {word.type})")
```

### JavaScript

```javascript
const result = await client.speechToText.convert({
  file: createReadStream("audio.mp3"),
  modelId: "scribe_v2",
  timestampsGranularity: "word",
});

for (const word of result.words) {
  console.log(`${word.text}: ${word.start}s - ${word.end}s (type: ${word.type})`);
}
```

## Speaker Diarization

Automatically identify up to 48 different speakers:

```python
result = client.speech_to_text.convert(
    file=audio_file,
    model_id="scribe_v2",
    diarize=True
)

for word in result.words:
    print(f"[{word.speaker_id}] {word.text}")
```

## Keyterm Prompting

Bias transcription toward specific terms (up to 100 terms):

```python
result = client.speech_to_text.convert(
    file=audio_file,
    model_id="scribe_v2",
    keyterms=["ElevenLabs", "Scribe", "API"]
)
```

## Language Detection

Automatic detection with optional language hint:

```python
result = client.speech_to_text.convert(
    file=audio_file,
    model_id="scribe_v2",
    language_code="eng"  # ISO 639-3 code
)

print(f"Detected: {result.language_code} ({result.language_probability:.0%})")
```

## Supported Formats

**Audio:** MP3, WAV, M4A, FLAC, OGG, WebM, AAC, AIFF, Opus
**Video:** MP4, AVI, MKV, MOV, WMV, FLV, WebM, MPEG, 3GPP

**Limits:** Up to 3GB file size, 10 hours duration

## Response Format

```json
{
  "text": "The full transcription text",
  "language_code": "eng",
  "language_probability": 0.98,
  "words": [
    {"text": "The", "start": 0.0, "end": 0.15, "type": "word", "speaker_id": "speaker_0"},
    {"text": " ", "start": 0.15, "end": 0.16, "type": "spacing", "speaker_id": "speaker_0"}
  ]
}
```

Word types: `word`, `spacing`, `audio_event` (laughter, applause, etc.)

## Error Handling

```python
from elevenlabs import ElevenLabsError

try:
    result = client.speech_to_text.convert(file=audio_file, model_id="scribe_v2")
except ElevenLabsError as e:
    print(f"Transcription failed: {e.message}")
```

Common errors:
- **401**: Invalid API key
- **422**: Invalid parameters
- **429**: Rate limit exceeded

## References

- [Installation Guide](references/installation.md)
- [Transcription Options](references/transcription-options.md)
