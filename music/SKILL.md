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

## Quick Start

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio = client.music.compose(
    prompt="A chill lo-fi hip hop beat with jazzy piano chords",
    music_length_ms=30000
)

with open("output.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### JavaScript

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createWriteStream } from "fs";

const client = new ElevenLabsClient();
const audio = await client.music.compose({
  prompt: "A chill lo-fi hip hop beat with jazzy piano chords",
  musicLengthMs: 30000,
});
audio.pipe(createWriteStream("output.mp3"));
```

### cURL

```bash
curl -X POST "https://api.elevenlabs.io/v1/music" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"prompt": "A chill lo-fi beat", "music_length_ms": 30000}' --output output.mp3
```

## Methods

| Method | Description |
|--------|-------------|
| `music.compose` | Generate audio from a prompt or composition plan |
| `music.composition_plan.create` | Generate a structured plan for fine-grained control |
| `music.compose_detailed` | Generate audio + composition plan + metadata |

See [API Reference](references/api_reference.md) for full parameter details.

## Composition Plans

For granular control, generate a composition plan first, modify it, then compose:

```python
plan = client.music.composition_plan.create(
    prompt="An epic orchestral piece building to a climax",
    music_length_ms=60000
)

# Inspect/modify styles and sections
print(plan.positiveGlobalStyles)  # e.g. ["orchestral", "epic", "cinematic"]

audio = client.music.compose(
    composition_plan=plan,
    music_length_ms=60000
)
```

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

Common errors: 401 (invalid key), 422 (invalid params), 429 (rate limit).

## References

- [Installation Guide](references/installation.md)
- [API Reference](references/api_reference.md)
