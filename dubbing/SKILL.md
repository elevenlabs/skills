---
name: dubbing
description: Dub audio and video into other languages using the ElevenLabs Dubbing API (dubbing_v2), preserving the original speakers' voices. Use when translating videos, podcasts, or recordings into other languages, localizing media content, reviewing or correcting dubbing transcripts and translations, or regenerating a dub after edits.
license: MIT
compatibility: Requires internet access and an ElevenLabs API key (ELEVENLABS_API_KEY).
metadata: {"openclaw": {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "primaryEnv": "ELEVENLABS_API_KEY"}}
---

# ElevenLabs Dubbing

Dub audio or video into other languages while preserving the original speakers' voices. Create a project from a file or URL, review and edit the source transcript, add one or more target languages, refine translations per segment, and regenerate outputs.

> **Important:** Use the Dubbing Projects API — `elevenlabs.dubbing.project.*` in the SDKs, or the `/v1/dubbing/project` REST endpoints. Do **not** use the legacy v1 dubbing surface (`client.dubbing.create()`, `client.dubbing.get()`, `client.dubbing.audio.get()`, or bare `/v1/dubbing` routes) — that is the older dubbing API, now under Legacy in the API reference.

> **Setup:** See [Installation Guide](references/installation.md). REST base URL is `https://api.elevenlabs.io` with your API key in the `xi-api-key` header; the SDKs read `ELEVENLABS_API_KEY` automatically.

## Concepts

| Concept | Meaning |
|---------|---------|
| **Project** | One source of media (file or URL) plus its source transcript. Prepared (transcribed) once, then rests in `ready` while you add languages. |
| **Source transcript** | Editable segments (text, speaker, timing) transcribed from the source. The single source of truth every language is translated from. |
| **Language (target)** | One dubbed output language. Each has its own transcript (source segments + a translation per segment) and its own dubbed audio output. |
| **Revisions** | Independent monotonic counters. The project's `revision` bumps on source-transcript edits; a language's `revision` bumps on translation edits or source edits that affect it. A language's `output_revision` is the revision its current audio was generated from — when it's behind `revision`, the output is out of date. |

**Recommended order of operations:** finalize the source transcript **before** adding any languages. Translations are produced from the source, so correcting the source first means every language starts from the right text — editing the source after a language completes marks it `stale` and requires a (charged) regeneration.

> **Enterprise:** Transcript editing and regeneration are available to enterprise workspaces only. Creating projects, adding languages, and downloading dubs work on all plans.

## Workflow

1. **Create** the project from a file or URL → `queued`
2. **Poll** the project until `ready`
3. **Review and finalize the source transcript** (edit/add/delete segments)
4. **Add** one language per target → `queued` → `processing` → `completed`
5. **Download** each language's `outputs.lossless_audio` when `completed`
6. **Refine** translations per segment if needed → the language goes `stale`
7. **Regenerate** the language → `completed` again with fresh output

## Quick Start (Python)

```python
import os
import time
import requests
from elevenlabs.client import ElevenLabs

elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# 1. Create a project from a local file (or pass source_url=... instead of file)
with open("promo.mp4", "rb") as f:
    project = elevenlabs.dubbing.project.create(
        file=f,
        source_language="en",
        reference="Q3 marketing video",
    )

# 2. Wait for the source media to be transcribed
while True:
    project = elevenlabs.dubbing.project.get(project.project_id)
    if project.status == "ready":
        break
    if project.status == "failed":
        raise RuntimeError("Project preparation failed")
    time.sleep(5)

# 3. Add a Spanish language target
language = elevenlabs.dubbing.project.language.create(
    project.project_id,
    target_language="es",
)

# 4. Wait for the dub to finish generating
while True:
    language = elevenlabs.dubbing.project.language.get(
        project.project_id, language.language_id
    )
    if language.status == "completed":
        break
    if language.status == "failed":
        raise RuntimeError("Dub generation failed")
    time.sleep(5)

# 5. Download the dubbed audio (signed URL, valid ~1 hour — re-fetch the language for a fresh one)
audio = requests.get(language.outputs.lossless_audio)
with open("promo_es.wav", "wb") as f:
    f.write(audio.content)
```

## Quick Start (JavaScript)

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { writeFile } from "fs/promises";

const elevenlabs = new ElevenLabsClient();

// 1. Create a project (sourceUrl shown; file upload is also supported)
let project = await elevenlabs.dubbing.project.create({
  sourceUrl: "https://example.com/promo.mp4",
  sourceLanguage: "en",
  reference: "Q3 marketing video",
});

// 2. Wait for the source media to be transcribed
while (true) {
  project = await elevenlabs.dubbing.project.get(project.projectId);
  if (project.status === "ready") break;
  if (project.status === "failed") throw new Error("Project preparation failed");
  await new Promise((resolve) => setTimeout(resolve, 5000));
}

// 3. Add a Spanish language target
let language = await elevenlabs.dubbing.project.language.create(project.projectId, {
  targetLanguage: "es",
});

// 4. Wait for the dub to finish generating
while (true) {
  language = await elevenlabs.dubbing.project.language.get(project.projectId, language.languageId);
  if (language.status === "completed") break;
  if (language.status === "failed") throw new Error("Dub generation failed");
  await new Promise((resolve) => setTimeout(resolve, 5000));
}

// 5. Download the dubbed audio from the signed URL
const response = await fetch(language.outputs!.losslessAudio!);
await writeFile("promo_es.wav", Buffer.from(await response.arrayBuffer()));
```

## Quick Start (cURL)

```bash
# 1. Create a project (use -F "source_url=https://..." instead of file to dub from a URL)
curl -X POST "https://api.elevenlabs.io/v1/dubbing/project" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "file=@promo.mp4" \
  -F "source_language=en"
# → {"project_id": "proj_...", "status": "queued", ...}

# 2. Poll until status is "ready"
curl "https://api.elevenlabs.io/v1/dubbing/project/proj_..." \
  -H "xi-api-key: $ELEVENLABS_API_KEY"

# 3. Add a target language
curl -X POST "https://api.elevenlabs.io/v1/dubbing/project/proj_.../language" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"target_language": "es"}'

# 4. Poll the language until "completed", then download outputs.lossless_audio
curl "https://api.elevenlabs.io/v1/dubbing/project/proj_.../language/lang_..." \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

## Create Options

`POST /v1/dubbing/project` takes `multipart/form-data` with **either** `file` **or** `source_url` (not both):

| Field | Required | Notes |
|-------|----------|-------|
| `file` | one of file/source_url | Source media to dub (audio or video), up to 3 GiB |
| `source_url` | one of file/source_url | Public URL to fetch the source media from |
| `source_language` | no | ISO 639 code (e.g. `en`). Omit to auto-detect — the detected language is reported on the source transcript's `language` field |
| `reference` | no | Free-form label to identify the project on your end (max 500 chars) |
| `model_id` | no | `dubbing_v2` (default) |
| `target_language` | no | Optionally queue the first language target at creation; add more with `language.create` |
| `keyterms` | no | Terms to bias transcription/translation toward (product/brand names). Up to 100 terms of 200 chars each; repeat the field once per term in multipart |

## Editing the Source Transcript

Once the project is `ready`, read the transcript, then correct it before adding languages. Every edit bumps the project's `revision`. Each segment has a stable `id` used to edit or delete it. (Enterprise workspaces only.)

```python
# Read the source transcript
transcript = elevenlabs.dubbing.project.transcript.get(project_id)

# Correct a segment's text — send only the fields to change (text, speaker_id, start_s, end_s)
elevenlabs.dubbing.project.transcript.update_segment(
    project_id,
    segment_id=transcript.segments[0].id,
    text="Welcome to our latest product demo.",
)

# Add a segment (reuse an existing speaker_id so it's dubbed with that speaker's voice)
added = elevenlabs.dubbing.project.transcript.create_segment(
    project_id,
    text="Thanks for watching.",
    speaker_id=transcript.segments[0].speaker_id,
    start_s=40.0,
    end_s=42.0,
)

# Delete a segment
elevenlabs.dubbing.project.transcript.delete_segment(project_id, segment_id=added.segment.id)
```

Via REST: `GET /v1/dubbing/project/{project_id}/transcript`, then `PATCH .../transcript/segment/{segment_id}` with only the changed fields:

```bash
curl -X PATCH "https://api.elevenlabs.io/v1/dubbing/project/{project_id}/transcript/segment/{segment_id}" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"text": "Welcome to our latest product demo."}'
```

## Refining Translations and Regenerating

A language's transcript pairs each source segment with its `translation` (`null` = not yet translated; segment ids match the source). Edit a single translation, then regenerate. (Enterprise workspaces only.)

```python
# Read the language's translations
target = elevenlabs.dubbing.project.language.transcript.get(project_id, language_id)

# Refine a single translation (pass translation=None to clear it and mark for re-translation)
elevenlabs.dubbing.project.language.transcript.update_segment(
    project_id,
    language_id,
    segment_id=target.segments[0].id,
    translation="Bienvenido a nuestra última demostración de producto.",
)

# Regenerate the dub from the current transcript (charged like a generation)
elevenlabs.dubbing.project.language.transcript.regenerate(project_id, language_id)
```

Via REST: `PATCH /v1/dubbing/project/{project_id}/language/{language_id}/transcript/segment/{segment_id}` with `{"translation": "..."}`, then `POST .../language/{language_id}/transcript/regenerate` (returns `202 Accepted`).

A translation edit affects only that language. After the edit, a `completed` language becomes `stale` — it keeps serving its previous output until you regenerate. Poll until `completed`; `output_revision` then equals `revision` and `outputs.lossless_audio` reflects the current transcript.

## Dubbing into Multiple Languages

Add one language target per language — each generates independently. Track them all with `language.list` instead of polling one by one:

```python
for lang in ["es", "fr", "de", "ja"]:
    elevenlabs.dubbing.project.language.create(project_id, target_language=lang)

while True:
    result = elevenlabs.dubbing.project.language.list(project_id)
    if not any(l.status in ("queued", "processing") for l in result.languages):
        break
    time.sleep(5)
```

## States

**Project:**

| Status | Meaning |
|--------|---------|
| `queued` | Created; source fetch + preparation enqueued |
| `preparing` | Preparation (transcription) running |
| `ready` | Source transcript available; add/generate languages. Projects **stay** `ready` — per-language progress lives on the languages |
| `failed` | Preparation failed (e.g. source couldn't be fetched or decoded) |

**Language:**

| Status | Meaning |
|--------|---------|
| `queued` | Waiting on the project becoming `ready`, or on a generation worker |
| `processing` | The dub is being generated |
| `completed` | Finished; `outputs` populated with a signed download URL (valid ~1 hour — re-fetch for a fresh one) |
| `stale` | Previously completed, but the transcript changed; keeps the last output until regenerated |
| `failed` | Generation failed |

You can add a language before the project is `ready` — it stays `queued` and starts automatically once the project becomes `ready`. Adding a language accepts optional `model_id` (defaults to the project's) and `voice_settings` (e.g. `{"cloning_strength": 7}`, range 0–10, default 7 — controls how strongly dubbed speakers clone the source voices).

## Error Handling

- **401**: Invalid API key
- **409 Conflict** on regenerate: The project isn't `ready` or the language isn't settled (e.g. already generating) — wait and retry
- **Expired download URL**: `outputs.lossless_audio` is signed and valid ~1 hour; re-fetch the language for a fresh URL
- **Transcript editing / regeneration unavailable**: These endpoints are enterprise-only — on other plans, create the project with a finalized source and add languages directly

## References

- [Installation Guide](references/installation.md)
- [API Reference](references/api-reference.md) — every endpoint with full request/response schemas and SDK method names
