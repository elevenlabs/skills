# Music API Reference

## Table of Contents

- [compose](#compose)
- [composition_plan.create](#composition_plancreate)
- [compose_detailed](#compose_detailed)
- [video_to_music](#video_to_music)
- [upload](#upload)
- [Error Handling](#error-handling)

## compose

Generate music from a text prompt. Returns an audio stream.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes* | Description of desired music |
| `composition_plan` | object | Yes* | Pre-defined composition plan (alternative to prompt) |
| `music_length_ms` | integer | No | Duration in milliseconds (3,000–600,000) when using `prompt`; if omitted, the model chooses |
| `model_id` | string | No | Defaults to `music_v1` |
| `force_instrumental` | boolean | No | Guarantee an instrumental output (prompt mode only) |
| `respect_sections_durations` | boolean | No | Enforce exact `duration_ms` in each composition plan section |

*Provide either `prompt` or `composition_plan`, not both.

### Python

```python
audio = client.music.compose(
    prompt="An upbeat electronic track with synth leads",
    music_length_ms=30000
)

with open("output.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### JavaScript

```javascript
const audio = await client.music.compose({
  prompt: "An upbeat electronic track with synth leads",
  musicLengthMs: 30000,
});

const writeStream = createWriteStream("output.mp3");
audio.pipe(writeStream);
```

### With Composition Plan

```python
plan = client.music.composition_plan.create(
    prompt="A jazz ballad with piano and saxophone",
    music_length_ms=60000
)

# Modify the plan as needed
audio = client.music.compose(
    composition_plan=plan,
    music_length_ms=60000
)
```

## composition_plan.create

Generate a structured composition plan from a prompt for granular control before generating audio.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Music description |
| `music_length_ms` | integer | Yes | Duration in milliseconds |

### Response Structure

```json
{
  "positiveGlobalStyles": ["jazz", "smooth", "warm"],
  "negativeGlobalStyles": ["aggressive", "distorted"],
  "sections": [
    {
      "name": "Intro",
      "localStyles": ["soft", "building"],
      "duration_ms": 15000,
      "lines": [
        { "text": "Instrumental intro", "type": "instrumental" }
      ]
    }
  ]
}
```

### Python

```python
plan = client.music.composition_plan.create(
    prompt="A peaceful ambient track with nature sounds",
    music_length_ms=60000
)

# Inspect and modify the plan
print(plan.positiveGlobalStyles)
for section in plan.sections:
    print(f"{section.name}: {section.duration_ms}ms")
```

## compose_detailed

Generate music while returning both the composition plan and metadata alongside the audio.

### Returns

| Field | Description |
|-------|-------------|
| `json` | Composition plan + song metadata (includes lyrics if applicable) |
| `filename` | Output file identifier |
| `audio` | Audio bytes |

### Python

```python
result = client.music.compose_detailed(
    prompt="A pop song about summer adventures",
    music_length_ms=120000
)

# Access the composition plan and metadata
print(result.json)

# Save the audio
with open(result.filename, "wb") as f:
    f.write(result.audio)
```

## video_to_music

Generate background music from one or more uploaded video files. Videos are combined in order and
the response is an audio file whose format depends on `output_format`.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `videos` | array of files | Yes | One or more video files sent as multipart form data. Up to 10 videos, 200MB combined size, and 600 seconds total duration. |
| `description` | string | No | Optional text prompt describing the music to generate (max 1000 characters). |
| `tags` | array | No | Optional list of style tags such as `upbeat` or `cinematic` (max 10 tags). |
| `sign_with_c2pa` | boolean | No | Sign the generated song with C2PA when producing MP3 output (default: `false`). |
| `output_format` | string | No | Query parameter controlling the returned audio format. Supports MP3, PCM, u-law, A-law, and Opus variants. |

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio = client.music.video_to_music(
    videos=["trailer.mp4"],
    description="Cinematic background music with a steady build",
    tags=["cinematic", "uplifting"],
)
```

### JavaScript

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import fs from "fs";

const client = new ElevenLabsClient();

const audio = await client.music.videoToMusic({
  videos: [fs.createReadStream("trailer.mp4")],
  description: "Cinematic background music with a steady build",
  tags: ["cinematic", "uplifting"],
});
```

## upload

Upload a music file for later inpainting workflows. This endpoint is available to enterprise clients with access to the inpainting feature.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file | Yes | The audio file to upload |
| `extract_composition_plan` | boolean | No | If `true`, the response includes an extracted composition plan and may take longer to return |

### Returns

| Field | Description |
|-------|-------------|
| `song_id` | Unique identifier for the uploaded song |
| `composition_plan` | Extracted composition plan, or `null` when `extract_composition_plan` is not enabled |

### Python

```python
client.music.upload(
    file="example_file",
)
```

### cURL

```bash
curl -X POST "https://api.elevenlabs.io/v1/music/upload" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "file=@<file1>"
```

## Error Handling

### bad_prompt

Occurs when the prompt references copyrighted material (specific artists, bands, or copyrighted lyrics). The error response includes a `prompt_suggestion` with alternative phrasing.

```python
try:
    audio = client.music.compose(
        prompt="A song like Beatles",
        music_length_ms=30000
    )
except Exception as e:
    print(f"Request failed: {e}")
```

### bad_composition_plan

Returned when a composition plan contains copyrighted styles. The error includes a `composition_plan_suggestion` with corrected styles. No suggestion is provided for harmful content.

### Common HTTP Errors

| Code | Meaning |
|------|---------|
| 401 | Invalid API key |
| 422 | Invalid parameters |
| 429 | Rate limit exceeded |
