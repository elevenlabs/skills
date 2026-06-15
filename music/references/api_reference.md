# Music API Reference

All endpoints below default to `music_v1` unless noted for backwards compatibility. Always pass `music_v2` unless the caller explicitly needs the legacy model.

## Table of Contents

- [compose](#compose)
- [stream](#stream)
- [composition_plan.create](#composition_plancreate)
- [compose_detailed](#compose_detailed)
- [upload](#upload)
- [video_to_music](#video_to_music)
- [Inpainting](#inpainting)
- [Error Handling](#error-handling)

## compose

Generate music from a text prompt or composition plan. Returns an audio stream.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes* | Description of desired music |
| `composition_plan` | object | Yes* | Pre-defined composition plan (alternative to prompt) |
| `music_length_ms` | integer | No | Duration in milliseconds (3,000–600,000) when using `prompt`; if omitted, the model chooses. Returns an error if a composition plan is also provided. |
| `model_id` | string | No | Music model. Defaults to `music_v1`. |
| `force_instrumental` | boolean | No | Guarantee an instrumental output (prompt mode only) |
| `respect_sections_durations` | boolean | No | Enforce exact `duration_ms` for each composition plan chunk. Ignored if using `music_v2` model. |

*Provide either `prompt` or `composition_plan`, not both.

### Python

```python
audio = client.music.compose(
    prompt="An upbeat electronic track with synth leads",
    music_length_ms=30000,
    model_id="music_v2",
)

with open("output.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### TypeScript

```typescript
const audio = await client.music.compose({
  prompt: "An upbeat electronic track with synth leads",
  musicLengthMs: 30000,
  modelId: "music_v2",
});

const writeStream = createWriteStream("output.mp3");
audio.pipe(writeStream);
```

### With Composition Plan

```python
plan = client.music.composition_plan.create(
    prompt="A jazz ballad with piano and saxophone",
    music_length_ms=60000,
    model_id="music_v2",
)

# Modify the plan as needed
audio = client.music.compose(
    composition_plan=plan,
    model_id="music_v2",
)
```

```typescript
const plan = await client.music.compositionPlan.create({
  prompt: "A jazz ballad with piano and saxophone",
  musicLengthMs: 60000,
  modelId: "music_v2",
});

// Modify the plan as needed
const audio = await client.music.compose({
  compositionPlan: plan,
  modelId: "music_v2",
});
```

## stream

Stream audio chunks as they are generated. Same parameters as [`compose`](#compose); returns an
iterable/async-iterable of audio bytes instead of a single response. Available on paid plans only.

### Python

```python
from io import BytesIO

stream = client.music.stream(
    prompt="A driving synthwave track with arpeggiated leads",
    music_length_ms=30000,
    model_id="music_v2",
)

buffer = BytesIO()
for chunk in stream:
    if chunk:
        buffer.write(chunk)
```

### TypeScript

```typescript
const stream = await client.music.stream({
  prompt: "A driving synthwave track with arpeggiated leads",
  musicLengthMs: 30000,
  modelId: "music_v2",
});

const chunks: Buffer[] = [];
for await (const chunk of stream) {
  chunks.push(chunk);
}
```

## composition_plan.create

Generate a structured composition plan from a prompt for granular control before generating audio.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Music description |
| `music_length_ms` | integer | Yes | Total duration in milliseconds (3,000–600,000) |
| `model_id` | string | No | Defaults to `music_v2`. Plan structure differs between models. |

### Plan Structure (`music_v2`)

A plan is an ordered list of `chunks`. Each chunk is either a **generation chunk** or an
**audio reference chunk** (see [Inpainting](#inpainting)).

| Field | Type | Description |
|-------|------|-------------|
| `chunks` | array | Up to 30 chunks; 3 s to 10 min total |
| `chunks[].text` | string | Section labels (`[Verse 1]`), lyrics, inline cues like `{guitar solo}` |
| `chunks[].duration_ms` | integer | 3,000–120,000 ms |
| `chunks[].positive_styles` | array&lt;string&gt; | Up to 50 desired qualities (genre, instrumentation, vocal style). Must be English. |
| `chunks[].negative_styles` | array&lt;string&gt; | Up to 50 qualities to avoid |
| `chunks[].context_adherence` | string | `low`, `medium`, or `high` (default). Higher = stays consistent with surrounding chunks. |

### Python

```python
plan = client.music.composition_plan.create(
    prompt="A peaceful ambient track with nature sounds",
    music_length_ms=60000,
    model_id="music_v2",
)

# Inspect or edit the plan in place
print(plan["chunks"][0]["positive_styles"])
plan["chunks"][0]["text"] = "[Intro]\nSoft pad with rain"

audio = client.music.compose(composition_plan=plan, model_id="music_v2")
```

### TypeScript

```typescript
const plan = await client.music.compositionPlan.create({
  prompt: "A peaceful ambient track with nature sounds",
  musicLengthMs: 60000,
  modelId: "music_v2",
});

plan.chunks[0].text = "[Intro]\nSoft pad with rain";
const audio = await client.music.compose({ compositionPlan: plan, modelId: "music_v2" });
```

## compose_detailed

Generate music while returning both the composition plan and metadata alongside the audio.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes* | Description of desired music |
| `composition_plan` | object | Yes* | Pre-defined composition plan (alternative to `prompt`) |
| `music_length_ms` | integer | No | Total duration in milliseconds when using `prompt` |
| `model_id` | string | No | Defaults to `music_v2` |
| `store_for_inpainting` | boolean | No | If `true`, retains the generated audio under a `song_id` so it can be referenced by later inpainting plans |
| `force_instrumental` | boolean | No | Guarantee an instrumental output (prompt mode only) |

*Provide either `prompt` or `composition_plan`, not both.

### Returns

| Field | Description |
|-------|-------------|
| `json` | Composition plan + song metadata (includes lyrics if applicable) |
| `filename` | Output file identifier |
| `audio` | Audio bytes |
| `song_id` | Identifier for the stored song (only when `store_for_inpainting=True`) |

### Python

```python
result = client.music.compose_detailed(
    prompt="A pop song about summer adventures",
    music_length_ms=120000,
    model_id="music_v2",
    store_for_inpainting=True,
)

print(result.json)        # composition plan + metadata
print(result.song_id)     # reusable identifier for inpainting

with open(result.filename, "wb") as f:
    f.write(result.audio)
```

### TypeScript

```typescript
import { writeFileSync } from "fs";

const result = await client.music.composeDetailed({
  prompt: "A pop song about summer adventures",
  musicLengthMs: 120000,
  modelId: "music_v2",
  storeForInpainting: true,
});

console.log(result.json);    // composition plan + metadata
console.log(result.songId);  // reusable identifier for inpainting

writeFileSync(result.filename, result.audio);
```

## upload

Upload a music file for later inpainting workflows. This endpoint is available to enterprise clients with access to the inpainting feature.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file | Yes | The audio file to upload |
| `extract_composition_plan` | boolean \| string | No | If `true` (or a model id such as `"music_v2"`), the response includes an extracted composition plan; passing a model id chooses the extraction model. The request may take longer to return. |

### Returns

| Field | Description |
|-------|-------------|
| `song_id` | Unique identifier for the uploaded song |
| `composition_plan` | Extracted composition plan, or `null` when `extract_composition_plan` is not enabled |

### Python

```python
response = client.music.upload(
    file=open("my-song.mp3", "rb"),
    extract_composition_plan="music_v2",
)
song_id = response.song_id
composition_plan = response.composition_plan
```

### TypeScript

```typescript
import { createReadStream } from "fs";

const response = await client.music.upload({
  file: createReadStream("my-song.mp3"),
  extractCompositionPlan: "music_v2",
});
const songId = response.songId;
const compositionPlan = response.compositionPlan;
```

### cURL

```bash
curl -X POST "https://api.elevenlabs.io/v1/music/upload" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "file=@<file1>" \
  -F "extract_composition_plan=music_v2"
```

## video_to_music

Generate background music from uploaded video clips. This is a **separate endpoint** from
[`compose`](#compose) (`POST /v1/music/video-to-music`, not `POST /v1/music`). See the
[Video to music API reference](https://elevenlabs.io/docs/api-reference/music/video-to-music).

Videos are combined in order before music generation.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `videos` | array of files | Yes | One or more video files. Up to 10 files, 200MB combined size, and 600 seconds total duration. |
| `description` | string | No | Optional text prompt describing the desired music (up to 1000 characters). |
| `tags` | array of strings | No | Optional style tags such as `upbeat` or `cinematic` (up to 10 tags). |
| `model_id` | string | No | Music model to use. Defaults to `music_v1` on this endpoint — pass `music_v2` to opt in. |
| `sign_with_c2pa` | boolean | No | Sign generated MP3 output with C2PA metadata. Defaults to `false`. |
| `output_format` | string | No | Output codec/sample-rate/bitrate, such as `mp3_44100_128`, `pcm_44100`, or `opus_48000_96`. |

### Python

```python
audio = client.music.video_to_music(
    videos=[open("scene-1.mp4", "rb"), open("scene-2.mp4", "rb")],
    description="Cinematic ambient score with a gentle build",
    tags=["cinematic", "ambient"],
    model_id="music_v2",
)

with open("video-score.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### TypeScript

```typescript
import { createReadStream, createWriteStream } from "fs";

const audio = await client.music.videoToMusic({
  videos: [createReadStream("scene-1.mp4"), createReadStream("scene-2.mp4")],
  description: "Cinematic ambient score with a gentle build",
  tags: ["cinematic", "ambient"],
  modelId: "music_v2",
});

audio.pipe(createWriteStream("video-score.mp3"));
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

## Inpainting

Inpainting edits or extends a stored song by combining **audio reference chunks** (unchanged
slices of stored audio) with **generation chunks** in a single `music_v2` composition plan.
Available to enterprise clients.

### Getting a `song_id`

- Call [`compose_detailed`](#compose_detailed) or [`compose`](#compose) with `store_for_inpainting=True` to keep a
  generation for later editing.
- Call [`upload`](#upload) with `extract_composition_plan="music_v2"` to import an existing
  track and recover its plan.

### Chunk Types

**Audio reference chunk** — replay a slice of a stored song unchanged:

| Field | Type | Description |
|-------|------|-------------|
| `song_id` | string | Stored song identifier |
| `range.start_ms` | integer | Start offset (minimum 50 ms range) |
| `range.end_ms` | integer | End offset |

**Generation chunk** — same fields as a normal `music_v2` plan chunk (`text`,
`duration_ms`, `positive_styles`, `negative_styles`, `context_adherence`), with two optional
fields for matching the feel of an existing slice:

| Field | Type | Description |
|-------|------|-------------|
| `conditioning_ref.song_id` | string | Song to condition on |
| `conditioning_ref.range` | object | `start_ms`/`end_ms`; up to 30,000 ms |
| `condition_strength` | string | `low`, `medium` (default), `high`, or `xhigh` |

`conditioning_ref` on the first chunk influences every subsequent chunk in the plan.

### Constraints

| Constraint | Limit |
|------------|-------|
| Chunks per plan | 30 |
| Chunk duration | 3,000–120,000 ms |
| Conditioning reference duration | up to 30,000 ms |
| Minimum time range | 50 ms |

### Python

```python
plan = {
    "chunks": [
        {"song_id": song_id, "range": {"start_ms": 0, "end_ms": 30000}},
        {
            "text": "[Chorus]\nWe're rising up tonight",
            "duration_ms": 30000,
            "positive_styles": ["bigger drums", "layered vocals", "anthemic"],
            "negative_styles": ["sparse"],
            "context_adherence": "high",
            "conditioning_ref": {
                "song_id": song_id,
                "range": {"start_ms": 30000, "end_ms": 45000},
            },
            "condition_strength": "high",
        },
    ]
}

audio = client.music.compose(composition_plan=plan, model_id="music_v2")
```

### TypeScript

```typescript
const plan = {
  chunks: [
    { songId, range: { startMs: 0, endMs: 30000 } },
    {
      text: "[Chorus]\nWe're rising up tonight",
      durationMs: 30000,
      positiveStyles: ["bigger drums", "layered vocals", "anthemic"],
      negativeStyles: ["sparse"],
      contextAdherence: "high",
      conditioningRef: { songId, range: { startMs: 30000, endMs: 45000 } },
      conditionStrength: "high",
    },
  ],
};

const audio = await client.music.compose({ compositionPlan: plan, modelId: "music_v2" });
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

```typescript
try {
  const audio = await client.music.compose({
    prompt: "A song like Beatles",
    musicLengthMs: 30000,
  });
} catch (err) {
  console.error("Request failed:", err);
}
```

### bad_composition_plan

Returned when a composition plan contains copyrighted styles. The error includes a `composition_plan_suggestion` with corrected styles. No suggestion is provided for harmful content.

### Common HTTP Errors

| Code | Meaning |
|------|---------|
| 401 | Invalid API key |
| 422 | Invalid parameters |
| 429 | Rate limit exceeded |
