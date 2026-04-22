---
name: voice-changer
description: Transform the voice in an audio recording into a different target voice while preserving emotion, timing, and delivery using the ElevenLabs Voice Changer (speech-to-speech) API. Use when converting one voice to another, changing the speaker/narrator of an existing recording, dubbing a voice-over in a different voice, creating character voices from a scratch performance, anonymizing a speaker, or any "voice conversion / voice transfer / speech-to-speech" task. Make sure to use this skill whenever the user mentions voice changing, voice conversion, speech-to-speech, swapping a voice in audio, re-voicing a clip, or applying a different voice to an existing recording — even if they don't explicitly say "voice changer".
license: MIT
compatibility: Requires internet access and an ElevenLabs API key (ELEVENLABS_API_KEY).
metadata: {"openclaw": {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "primaryEnv": "ELEVENLABS_API_KEY"}}
---

# ElevenLabs Voice Changer

Transform the voice in an audio recording into a different target voice. Voice Changer (also known as speech-to-speech) keeps the original performance — emotion, pacing, intonation, breaths — and only swaps who is speaking.

> **Setup:** See [Installation Guide](references/installation.md). For JavaScript, use `@elevenlabs/*` packages only.

## Quick Start

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

with open("source.mp3", "rb") as audio_file:
    audio_stream = client.speech_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",  # George
        audio=audio_file,
        model_id="eleven_multilingual_sts_v2",
        output_format="mp3_44100_128",
    )

with open("converted.mp3", "wb") as f:
    for chunk in audio_stream:
        f.write(chunk)
```

### JavaScript

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createReadStream, createWriteStream } from "fs";

const client = new ElevenLabsClient();

const audioStream = await client.speechToSpeech.convert("JBFqnCBsd6RMkjVDRZzb", {
  audio: createReadStream("source.mp3"),
  modelId: "eleven_multilingual_sts_v2",
  outputFormat: "mp3_44100_128",
});

audioStream.pipe(createWriteStream("converted.mp3"));
```

### cURL

```bash
curl -X POST "https://api.elevenlabs.io/v1/speech-to-speech/JBFqnCBsd6RMkjVDRZzb?output_format=mp3_44100_128" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "audio=@source.mp3" \
  -F "model_id=eleven_multilingual_sts_v2" \
  --output converted.mp3
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `voice_id` | string (required) | — | Target voice to speak in. Use a pre-made voice ID, a cloned voice, or a voice from the library |
| `audio` | file (required) | — | Source audio whose performance (emotion, timing, delivery) will be preserved |
| `model_id` | string | `eleven_english_sts_v2` | `eleven_multilingual_sts_v2` for 29 languages, `eleven_english_sts_v2` for English-only |
| `output_format` | string | `mp3_44100_128` | See output formats table below |
| `voice_settings` | JSON string | — | Override stored voice settings for this request only |
| `seed` | integer | — | Best-effort deterministic sampling (0 – 4294967295) |
| `remove_background_noise` | boolean | `false` | Run the isolation model on the input before conversion |
| `file_format` | string | `other` | `other` for any encoded audio, or `pcm_s16le_16` for 16-bit PCM mono @ 16kHz little-endian (lower latency) |

## Models

| Model ID | Languages | Best For |
|----------|-----------|----------|
| `eleven_multilingual_sts_v2` | 29 | Default choice — highest-quality conversion, multilingual |
| `eleven_english_sts_v2` | English | English-only, default on the API |

Only models whose `can_do_voice_conversion` property is true can be used here. Voice Changer does not currently have a low-latency "flash/turbo" tier — if you need one, keep `pcm_s16le_16` input and an `opus_*` / low-bitrate `mp3_*` output.

## Target Voices

Use any voice ID from pre-made voices, your cloned voices, or the voice library.

**Popular voices:**
- `JBFqnCBsd6RMkjVDRZzb` — George (male, narrative)
- `EXAVITQu4vr4xnSDxMaL` — Sarah (female, soft)
- `onwK4e9ZLuTAKqWW03F9` — Daniel (male, authoritative)
- `XB0fDUnXU5powFXDhCwa` — Charlotte (female, conversational)

```python
voices = client.voices.get_all()
for voice in voices.voices:
    print(f"{voice.voice_id}: {voice.name}")
```

## Converting from a URL

```python
import requests
from io import BytesIO
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio_url = "https://storage.googleapis.com/eleven-public-cdn/audio/marketing/nicole.mp3"
response = requests.get(audio_url)
audio_data = BytesIO(response.content)

audio_stream = client.speech_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    audio=audio_data,
    model_id="eleven_multilingual_sts_v2",
    output_format="mp3_44100_128",
)

with open("converted.mp3", "wb") as f:
    for chunk in audio_stream:
        f.write(chunk)
```

## Voice Settings Override

Fine-tune the target voice for a single request without changing its stored defaults:

```python
from elevenlabs import VoiceSettings

audio_stream = client.speech_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    audio=audio_file,
    model_id="eleven_multilingual_sts_v2",
    voice_settings=VoiceSettings(
        stability=0.5,
        similarity_boost=0.75,
        style=0.0,
        use_speaker_boost=True,
    ),
)
```

- **Stability**: lower = more emotional range (follows the source more freely), higher = steadier delivery.
- **Similarity boost**: higher = closer to the target voice's timbre, may amplify source artifacts.
- **Style**: exaggerates the target voice's unique characteristics (v2+ models).
- **Speaker boost**: post-processing to sharpen clarity of the target voice.

## Cleaning Up Noisy Source Audio

If the input recording is noisy, either pre-process with the voice-isolator skill or pass `remove_background_noise=True` to do it in a single call:

```python
audio_stream = client.speech_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    audio=audio_file,
    model_id="eleven_multilingual_sts_v2",
    remove_background_noise=True,
)
```

Cleaner input almost always produces better conversion — the model is trying to match phonemes and prosody, and background noise gets in the way.

## Low-Latency PCM Input

If you already have raw 16-bit PCM mono @ 16kHz, passing `file_format="pcm_s16le_16"` skips decoding and reduces latency:

```python
audio_stream = client.speech_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    audio=pcm_bytes,
    model_id="eleven_multilingual_sts_v2",
    file_format="pcm_s16le_16",
)
```

Pair this with `optimize_streaming_latency` (0–4) as a query param for further latency reductions at some quality cost.

## Output Formats

| Format | Description |
|--------|-------------|
| `mp3_44100_128` | MP3 44.1kHz 128kbps (default) — good for web/apps |
| `mp3_44100_192` | MP3 44.1kHz 192kbps (Creator+) — higher quality |
| `mp3_44100_64` | MP3 44.1kHz 64kbps — smaller files |
| `mp3_22050_32` | MP3 22.05kHz 32kbps — smallest MP3 |
| `pcm_16000` | Raw PCM 16kHz — real-time pipelines |
| `pcm_24000` | Raw PCM 24kHz — good streaming balance |
| `pcm_44100` | Raw PCM 44.1kHz (Pro+) — CD quality |
| `pcm_48000` | Raw PCM 48kHz (Pro+) — highest quality |
| `ulaw_8000` | μ-law 8kHz — Twilio / telephony |
| `alaw_8000` | A-law 8kHz — telephony |
| `opus_48000_64` | Opus 48kHz 64kbps — efficient streaming |

## Deterministic Output

Pass a `seed` to make repeated conversions of the same input return (best-effort) identical audio — useful for testing and A/B comparisons.

```python
audio_stream = client.speech_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    audio=audio_file,
    model_id="eleven_multilingual_sts_v2",
    seed=12345,
)
```

## Common Workflows

- **Re-voice a narration** — keep the performance of a scratch recording, swap in a different narrator voice.
- **Localize / dub** — convert a voice-over into the same speaker's cloned voice in another language (using `eleven_multilingual_sts_v2`).
- **Create character voices** — act out a line yourself, convert into a distinctive character voice for games or animation.
- **Anonymize a speaker** — replace a recognizable voice with a neutral pre-made voice while preserving what was said and how.
- **Pair with voice-isolator** — isolate the source voice first (or set `remove_background_noise=True`) for noisy field recordings before conversion.
- **Pair with voice cloning** — clone a target voice from a short sample, then use its `voice_id` here as the conversion target.

## Error Handling

```python
try:
    audio_stream = client.speech_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        audio=audio_file,
        model_id="eleven_multilingual_sts_v2",
    )
except Exception as e:
    print(f"Voice changer failed: {e}")
```

Common errors:
- **401**: Invalid API key
- **422**: Invalid parameters (check `voice_id`, `model_id`, or `file_format` vs the supplied audio)
- **429**: Rate limit exceeded

## References

- [Installation Guide](references/installation.md)
