---
name: voice-isolator
description: Remove background noise and isolate vocals/speech from audio using ElevenLabs Voice Isolator (audio isolation) API. Use when cleaning up noisy recordings, removing music or background ambience from dialogue, isolating speech from field recordings, preparing audio for transcription, extracting vocals, or any "denoise / clean up / isolate voice" task.
license: MIT
compatibility: Requires internet access and an ElevenLabs API key (ELEVENLABS_API_KEY).
metadata: {"openclaw": {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "primaryEnv": "ELEVENLABS_API_KEY"}}
---

# ElevenLabs Voice Isolator

Removes background noise from audio and isolates vocals/speech — useful for cleaning up noisy recordings, prepping audio for transcription, or pulling dialogue out of a mixed track.

> **Setup:** See [Installation Guide](references/installation.md). For JavaScript, use `@elevenlabs/*` packages only.

## Quick Start

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

with open("noisy.mp3", "rb") as audio_file:
    audio_stream = client.audio_isolation.convert(audio=audio_file)

with open("clean.mp3", "wb") as f:
    for chunk in audio_stream:
        f.write(chunk)
```

### JavaScript

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createReadStream, createWriteStream } from "fs";

const client = new ElevenLabsClient();

const audioStream = await client.audioIsolation.convert({
  audio: createReadStream("noisy.mp3"),
});

audioStream.pipe(createWriteStream("clean.mp3"));
```

### cURL

```bash
curl -X POST "https://api.elevenlabs.io/v1/audio-isolation" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "audio=@noisy.mp3" \
  --output clean.mp3
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audio` | file (required) | — | Audio file with vocals/speech to isolate |
| `file_format` | string | `other` | `other` for any encoded audio, or `pcm_s16le_16` for 16-bit PCM mono @ 16kHz little-endian (lower latency) |

## Isolating from a URL

```python
import requests
from io import BytesIO
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio_url = "https://example.com/noisy.mp3"
response = requests.get(audio_url)
audio_data = BytesIO(response.content)

audio_stream = client.audio_isolation.convert(audio=audio_data)

with open("clean.mp3", "wb") as f:
    for chunk in audio_stream:
        f.write(chunk)
```

## Low-Latency PCM Input

If you already have raw 16-bit PCM mono @ 16kHz, passing `file_format="pcm_s16le_16"` skips decoding and reduces latency:

```python
audio_stream = client.audio_isolation.convert(
    audio=pcm_bytes,
    file_format="pcm_s16le_16",
)
```

## Supported Formats

Any common encoded audio/video container works as input (MP3, WAV, M4A, FLAC, OGG, WebM, MP4, etc.). Response is a streamed MP3 by default.

## Common Workflows

- **Clean up interview/podcast recordings** — strip room tone, HVAC, traffic before editing.
- **Prep noisy audio for Speech-to-Text** — isolate voice first, then pass through `speech_to_text.convert()` for better transcription accuracy.
- **Extract dialogue from mixed tracks** — pull vocals out of a track with music/SFX.
- **Pre-processing for Voice Changer** — isolate the source voice before applying voice transformation.

## Error Handling

```python
try:
    audio_stream = client.audio_isolation.convert(audio=audio_file)
except Exception as e:
    print(f"Voice isolation failed: {e}")
```

Common errors:
- **401**: Invalid API key
- **422**: Invalid parameters (e.g. wrong `file_format` for the supplied audio)
- **429**: Rate limit exceeded

## References

- [Installation Guide](references/installation.md)
