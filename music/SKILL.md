---
name: music
description: Generate music using ElevenLabs Music API. Use when creating instrumental tracks, songs with lyrics, background music, jingles, or any AI-generated music composition. Supports prompt-based generation, composition plans for granular control, and detailed output with metadata.
license: MIT
compatibility: Requires internet access and an ElevenLabs API key (ELEVENLABS_API_KEY).
metadata: {"openclaw": {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "primaryEnv": "ELEVENLABS_API_KEY"}}
---

# ElevenLabs Music Generation

Generate music from text prompts - supports instrumental tracks, songs with lyrics, and fine-grained control via composition plans.

> **Setup:** See [Installation Guide](references/installation.md). For JavaScript, use `@elevenlabs/*` packages only.

All examples below default to `music_v2`, the current generation model. Pass `model_id="music_v1"` only when explicitly requested to.

## Quick Start

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio = client.music.compose(
    prompt="A chill lo-fi hip hop beat with jazzy piano chords",
    music_length_ms=30000,
    model_id="music_v2",
)

with open("output.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### TypeScript

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createWriteStream } from "fs";

const client = new ElevenLabsClient();
const audio = await client.music.compose({
  prompt: "A chill lo-fi hip hop beat with jazzy piano chords",
  musicLengthMs: 30000,
  modelId: "music_v2",
});
audio.pipe(createWriteStream("output.mp3"));
```

### cURL

```bash
curl -X POST "https://api.elevenlabs.io/v1/music" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"prompt": "A chill lo-fi beat", "music_length_ms": 30000, "model_id": "music_v2"}' \
  --output output.mp3
```

## Methods

| Method | Description |
|--------|-------------|
| `music.compose` | Generate audio from a prompt or composition plan |
| `music.stream` | Stream audio chunks as they are generated (paid plans) |
| `music.composition_plan.create` | Generate a structured plan for fine-grained control |
| `music.compose_detailed` | Generate audio + composition plan + metadata; pass `store_for_inpainting=True` to enable inpainting |
| `music.video_to_music` | Generate background music from one or more uploaded video files |
| `music.upload` | Upload an audio file for later inpainting workflows and optionally extract its composition plan |

See [API Reference](references/api_reference.md) for full parameter details.

`music.upload` is available to enterprise clients with access to the inpainting feature.

## Video to Music

Generate background music from uploaded video clips via
[`POST /v1/music/video-to-music`](https://elevenlabs.io/docs/api-reference/music/video-to-music)
(`client.music.video_to_music`). This is separate from prompt-based
[`music.compose`](https://elevenlabs.io/docs/api-reference/music/compose) (`POST /v1/music`).

The API combines videos in order, accepts an optional natural-language description, and lets you
steer style with up to 10 tags such as `upbeat` or `cinematic`. This endpoint still defaults to
`music_v1`; pass `model_id="music_v2"` to use the newer model.

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio = client.music.video_to_music(
    videos=["trailer.mp4"],
    description="Build suspense, then resolve with a warm cinematic finish.",
    tags=["cinematic", "suspenseful", "uplifting"],
    model_id="music_v2",
)

with open("video-score.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### TypeScript

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createReadStream, createWriteStream } from "fs";

const client = new ElevenLabsClient();

const audio = await client.music.videoToMusic({
  videos: [createReadStream("trailer.mp4")],
  description: "Build suspense, then resolve with a warm cinematic finish.",
  tags: ["cinematic", "suspenseful", "uplifting"],
  modelId: "music_v2",
});

audio.pipe(createWriteStream("video-score.mp3"));
```

### cURL

```bash
curl -X POST "https://api.elevenlabs.io/v1/music/video-to-music" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "videos=@trailer.mp4" \
  -F "description=Build suspense, then resolve with a warm cinematic finish." \
  -F "tags=cinematic" \
  -F "tags=suspenseful" \
  -F "tags=uplifting" \
  -F "model_id=music_v2" \
  --output video-score.mp3
```

Constraints from the current API schema:

- Upload 1-10 video files per request
- Keep total combined upload size at or below 200 MB
- Keep total combined video duration at or below 600 seconds
- Use `description` for high-level musical direction and `tags` for concise style cues

## Composition Plans

`music_v2` composition plans are an ordered list of `chunks`. Each chunk specifies its own
`text` (section label, lyrics, inline cues), `duration_ms`, `positive_styles`, `negative_styles`,
and `context_adherence` (`low`, `medium`, or `high`, default `high`). Up to 30 chunks per plan,
each 3,000–120,000 ms, total length 3 s to 10 minutes.

Generate a plan first, edit it, then compose:

```python
plan = client.music.composition_plan.create(
    prompt="An epic orchestral piece building to a climax",
    music_length_ms=60000,
    model_id="music_v2",
)

# Edit chunks in place
plan["chunks"][0]["text"] = "[Intro]\nQuiet strings rising"

audio = client.music.compose(
    composition_plan=plan,
    model_id="music_v2",
)
```

```typescript
const plan = await client.music.compositionPlan.create({
  prompt: "An epic orchestral piece building to a climax",
  musicLengthMs: 60000,
  modelId: "music_v2",
});

plan.chunks[0].text = "[Intro]\nQuiet strings rising";

const audio = await client.music.compose({
  compositionPlan: plan,
  modelId: "music_v2",
});
```

Or hand-build a plan to control lyrics and style per section:

```python
composition_plan = {
    "chunks": [
        {
            "text": "[Verse]\nWalking down an empty street",
            "duration_ms": 15000,
            "positive_styles": ["pop", "upbeat", "female vocals", "acoustic guitar"],
            "negative_styles": ["dark", "slow"],
            "context_adherence": "high",
        },
        {
            "text": "[Chorus]\nThis is my moment",
            "duration_ms": 15000,
            "positive_styles": ["powerful vocals", "full band"],
            "negative_styles": [],
            "context_adherence": "high",
        },
    ]
}

audio = client.music.compose(composition_plan=composition_plan, model_id="music_v2")
```

```typescript
const compositionPlan = {
  chunks: [
    {
      text: "[Verse]\nWalking down an empty street",
      durationMs: 15000,
      positiveStyles: ["pop", "upbeat", "female vocals", "acoustic guitar"],
      negativeStyles: ["dark", "slow"],
      contextAdherence: "high",
    },
    {
      text: "[Chorus]\nThis is my moment",
      durationMs: 15000,
      positiveStyles: ["powerful vocals", "full band"],
      negativeStyles: [],
      contextAdherence: "high",
    },
  ],
};

const audio = await client.music.compose({
  compositionPlan,
  modelId: "music_v2",
});
```

Put broader characteristics (genre, instrumentation, vocal style) in `positive_styles`, not in
`text`. The first chunk's styles set the overall tone — include 6–7 styles there.

## Streaming

For paid plans, stream audio chunks as they are generated instead of waiting for the full file:

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

## Inpainting

Inpainting edits or extends a stored song by mixing **audio reference chunks** (unchanged slices
of a stored song) with new **generation chunks** in a single composition plan. 

Step 1 — get a `song_id`, either by storing a fresh generation or uploading existing audio:

```python
# Option A: keep a generation for later editing
result = client.music.compose_detailed(
    prompt="An upbeat pop song with verse and chorus",
    music_length_ms=60000,
    model_id="music_v2",
    store_for_inpainting=True,
)
song_id = result.song_id

# Option B: upload an existing track and extract its plan
uploaded = client.music.upload(
    file=open("my-song.mp3", "rb"),
    extract_composition_plan="music_v2",
)
song_id = uploaded.song_id
composition_plan = uploaded.composition_plan
```

```typescript
import { createReadStream } from "fs";

// Option A: keep a generation for later editing
const result = await client.music.composeDetailed({
  prompt: "An upbeat pop song with verse and chorus",
  musicLengthMs: 60000,
  modelId: "music_v2",
  storeForInpainting: true,
});
let songId = result.songId;

// Option B: upload an existing track and extract its plan
const uploaded = await client.music.upload({
  file: createReadStream("my-song.mp3"),
  extractCompositionPlan: "music_v2",
});
songId = uploaded.songId;
const compositionPlan = uploaded.compositionPlan;
```

Step 2 — compose a plan that references the stored audio and regenerates the part you want to
change:

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
        },
    ]
}

audio = client.music.compose(composition_plan=plan, model_id="music_v2")
```

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
    },
  ],
};

const audio = await client.music.compose({
  compositionPlan: plan,
  modelId: "music_v2",
});
```

To match the feel of a stored slice without copying it, attach a `conditioning_ref` (up to
30,000 ms) plus a `condition_strength` of `low`, `medium`, `high`, or `xhigh` to a generation
chunk. Conditioning placed on the first chunk influences every later chunk.

See [API Reference](references/api_reference.md) for the full inpainting parameter list.

## Content Restrictions

- Cannot reference specific artists, bands, or copyrighted lyrics
- `bad_prompt` errors include a `prompt_suggestion` with alternative phrasing
- `bad_composition_plan` errors include a `composition_plan_suggestion`

## Error Handling

```python
try:
    audio = client.music.compose(prompt="...", music_length_ms=30000)
except Exception as e:
    print(f"API error: {e}")
```

```typescript
try {
  const audio = await client.music.compose({
    prompt: "...",
    musicLengthMs: 30000,
  });
} catch (err) {
  console.error("API error:", err);
}
```

Common errors: 401 (invalid key), 422 (invalid params), 429 (rate limit).

## References

- [Installation Guide](references/installation.md)
- [API Reference](references/api_reference.md)
