# Music API Reference

## Table of Contents

- [compose](#compose)
- [composition_plan.create](#composition_plancreate)
- [compose_detailed](#compose_detailed)
- [upload](#upload)
- [video_to_music](#video_to_music)
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

## video_to_music

Generate background music that follows one or more uploaded video clips. Videos are combined in
order before music generation.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `videos` | array of files | Yes | One or more video files. Up to 10 files, 200MB combined size, and 600 seconds total duration. |
| `description` | string | No | Optional text prompt describing the desired music (up to 1000 characters). |
| `tags` | array of strings | No | Optional style tags such as `upbeat` or `cinematic` (up to 10 tags). |
| `sign_with_c2pa` | boolean | No | Sign generated MP3 output with C2PA metadata. Defaults to `false`. |
| `output_format` | string | No | Output codec/sample-rate/bitrate, such as `mp3_44100_128`, `pcm_44100`, or `opus_48000_96`. |

### Python

```python
audio = client.music.video_to_music(
    videos=[open("scene-1.mp4", "rb"), open("scene-2.mp4", "rb")],
    description="Cinematic ambient score with a gentle build",
    tags=["cinematic", "ambient"],
)

with open("video-score.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### cURL

```bash
curl -X POST "https://api.elevenlabs.io/v1/music/video-to-music?output_format=mp3_44100_128" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "videos=@scene-1.mp4" \
  -F "videos=@scene-2.mp4" \
  -F "description=Cinematic ambient score with a gentle build" \
  -F "tags=cinematic" \
  -F "tags=ambient" \
  --output video-score.mp3
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
