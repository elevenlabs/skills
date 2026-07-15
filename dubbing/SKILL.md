---
name: dubbing
description: Dub audio and video into other languages using the ElevenLabs Dubbing API (dubbing_v2), preserving the original speakers' voices. Use when translating videos, podcasts, or recordings into other languages, localizing media content, reviewing or correcting dubbing transcripts and translations, or regenerating a dub after edits.
license: MIT
compatibility: Requires internet access and an ElevenLabs API key (ELEVENLABS_API_KEY). The Dubbing Projects API is prerelease and gated per workspace.
metadata: {"openclaw": {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "primaryEnv": "ELEVENLABS_API_KEY"}}
---

# ElevenLabs Dubbing

Dub audio or video into other languages while preserving the original speakers' voices. Create a project from a file or URL, review and edit the source transcript, add one or more target languages, refine translations per segment, and regenerate outputs.

> **Prerelease:** These endpoints are gated per workspace. A "feature not available" error means the workspace hasn't been enabled for the Dubbing Projects API yet. Use direct REST calls (shown below) — do **not** use the SDK's legacy `client.dubbing` methods, which target the older `/v1/dubbing` (v1) API, not `/v1/dubbing/project`.

> **Setup:** See [Installation Guide](references/installation.md). Base URL is `https://api.elevenlabs.io`; send your API key in the `xi-api-key` header on every request.

## Concepts

| Concept | Meaning |
|---------|---------|
| **Project** | One source of media (file or URL) plus its source transcript. Prepared (transcribed) once, then rests in `ready` while you add languages. |
| **Source transcript** | Editable segments (text, speaker, timing) transcribed from the source. The single source of truth every language is translated from. |
| **Language (target)** | One dubbed output language. Each has its own transcript (source segments + a translation per segment) and its own dubbed audio output. |
| **Revisions** | Independent monotonic counters. The project's `revision` bumps on source-transcript edits; a language's `revision` bumps on translation edits or source edits that affect it. A language's `output_revision` is the revision its current audio was generated from — when it's behind `revision`, the output is out of date. |

**Recommended order of operations:** finalize the source transcript **before** adding any languages. Translations are produced from the source, so correcting the source first means every language starts from the right text — editing the source after a language completes marks it `stale` and requires a (charged) regeneration.

## Workflow

1. **Create** the project from a file or URL → `queued`
2. **Poll** the project until `ready`
3. **Review and finalize the source transcript** (edit/add/delete segments)
4. **Add** one language per target → `queued` → `processing` → `completed`
5. **Download** each language's `outputs.lossless_audio` when `completed`
6. **Refine** translations per segment if needed → the language goes `stale`
7. **Regenerate** the language → `completed` again with fresh output

## Quick Start (cURL)

```bash
# 1. Create a project (use -F "source_url=https://..." instead of file to dub from a URL)
curl -X POST "https://api.elevenlabs.io/v1/dubbing/project" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "file=@promo.mp4" \
  -F "source_language=en" \
  -F "reference=Q3 marketing video"
# → {"project_id": "proj_...", "status": "queued", ...}

# 2. Poll until status is "ready"
curl "https://api.elevenlabs.io/v1/dubbing/project/proj_..." \
  -H "xi-api-key: $ELEVENLABS_API_KEY"

# 3. Add a target language
curl -X POST "https://api.elevenlabs.io/v1/dubbing/project/proj_.../language" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"target_language": "es"}'
# → {"language_id": "lang_...", "status": "queued", ...}

# 4. Poll the language until "completed", then download outputs.lossless_audio
curl "https://api.elevenlabs.io/v1/dubbing/project/proj_.../language/lang_..." \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

## Quick Start (Python, end-to-end)

```python
import os
import time
import requests

API = "https://api.elevenlabs.io"
HEADERS = {"xi-api-key": os.environ["ELEVENLABS_API_KEY"]}

# 1. Create a project from a local file
with open("promo.mp4", "rb") as f:
    project = requests.post(
        f"{API}/v1/dubbing/project",
        headers=HEADERS,
        files={"file": f},
        data={"source_language": "en", "reference": "Q3 marketing video"},
    ).json()
project_id = project["project_id"]

# 2. Poll until the project is ready (source fetched + transcribed)
while True:
    project = requests.get(f"{API}/v1/dubbing/project/{project_id}", headers=HEADERS).json()
    if project["status"] == "ready":
        break
    if project["status"] == "failed":
        raise RuntimeError("Project preparation failed")
    time.sleep(5)

# 3. Add a target language
language = requests.post(
    f"{API}/v1/dubbing/project/{project_id}/language",
    headers=HEADERS,
    json={"target_language": "es"},
).json()
language_id = language["language_id"]

# 4. Poll the language until the dub completes
while True:
    language = requests.get(
        f"{API}/v1/dubbing/project/{project_id}/language/{language_id}", headers=HEADERS
    ).json()
    if language["status"] == "completed":
        break
    if language["status"] == "failed":
        raise RuntimeError("Dub generation failed")
    time.sleep(5)

# 5. Download the dubbed audio (signed URL, valid ~1 hour — re-fetch the language for a fresh one)
audio = requests.get(language["outputs"]["lossless_audio"])
with open("promo_es.wav", "wb") as f:
    f.write(audio.content)
```

## Quick Start (JavaScript)

```javascript
import { readFileSync } from "fs";

const API = "https://api.elevenlabs.io";
const HEADERS = { "xi-api-key": process.env.ELEVENLABS_API_KEY };

const form = new FormData();
form.append("file", new Blob([readFileSync("promo.mp4")]), "promo.mp4");
form.append("source_language", "en");

const project = await fetch(`${API}/v1/dubbing/project`, {
  method: "POST",
  headers: HEADERS,
  body: form,
}).then((r) => r.json());

// Poll project until ready, then add a language:
const language = await fetch(`${API}/v1/dubbing/project/${project.project_id}/language`, {
  method: "POST",
  headers: { ...HEADERS, "Content-Type": "application/json" },
  body: JSON.stringify({ target_language: "es" }),
}).then((r) => r.json());
// Poll the language until completed, then download outputs.lossless_audio
```

## Create Options

`POST /v1/dubbing/project` takes `multipart/form-data` with **either** `file` **or** `source_url` (not both):

| Field | Required | Notes |
|-------|----------|-------|
| `file` | one of file/source_url | Source media to dub (audio or video), up to 3 GiB |
| `source_url` | one of file/source_url | Public URL to fetch the source media from |
| `source_language` | no | ISO 639 code (e.g. `en`). Omit to auto-detect — the detected language is reported on the source transcript's `language` field |
| `reference` | no | Free-form label to identify the project on your end (max 500 chars) |
| `model_id` | no | `dubbing_v2` (default and only model today; `dubbing_v1` support will follow) |
| `keyterms` | no | Terms to bias transcription/translation toward (product/brand names). Up to 100 terms of 200 chars each; repeat the field once per term in multipart |

## Editing the Source Transcript

Once the project is `ready`, read the transcript, then correct it before adding languages. Every edit bumps the project's `revision` (returned in each response). Each segment has a stable `id` used to edit or delete it.

```bash
# Read
curl "https://api.elevenlabs.io/v1/dubbing/project/{project_id}/transcript" \
  -H "xi-api-key: $ELEVENLABS_API_KEY"

# Edit a segment — send only the fields to change (text, speaker_id, start_s, end_s)
curl -X PATCH "https://api.elevenlabs.io/v1/dubbing/project/{project_id}/transcript/segment/{segment_id}" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"text": "Welcome to our latest product demo."}'
```

Add segments with `POST .../transcript/segment` (all of `text`, `speaker_id`, `start_s`, `end_s` required — reuse an existing `speaker_id` so the new line is dubbed with that speaker's voice) and delete with `DELETE .../transcript/segment/{segment_id}`.

## Refining Translations and Regenerating

A language's transcript pairs each source segment with its `translation` (`null` = not yet translated). Edit a single translation, then regenerate:

```bash
# Fix one translated segment (pass null to clear it and mark it for re-translation)
curl -X PATCH "https://api.elevenlabs.io/v1/dubbing/project/{project_id}/language/{language_id}/transcript/segment/{segment_id}" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"translation": "Bienvenido a nuestra última demostración de producto."}'

# Regenerate the dub from the current transcript (charged like a generation) → 202 Accepted
curl -X POST "https://api.elevenlabs.io/v1/dubbing/project/{project_id}/language/{language_id}/transcript/regenerate" \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

A translation edit affects only that language. After the edit, a `completed` language becomes `stale` — it keeps serving its previous output until you regenerate. Poll until `completed`; `output_revision` then equals `revision` and `outputs.lossless_audio` reflects the current transcript.

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

You can add a language before the project is `ready` — it stays `queued` and starts automatically once the project becomes `ready`. Adding a language accepts optional `model_id` (defaults to the project's) and `voice_settings` (e.g. `{"cloning_strength": 7}`, range 0–10).

## Error Handling

- **401**: Invalid API key
- **"feature not available"**: Workspace not enabled for the Dubbing Projects API (prerelease gating)
- **409 Conflict** on regenerate: The project isn't `ready` or the language isn't settled (e.g. already generating) — wait and retry
- **Expired download URL**: `outputs.lossless_audio` is signed and valid ~1 hour; re-fetch the language for a fresh URL

## References

- [Installation Guide](references/installation.md)
- [API Reference](references/api-reference.md) — every endpoint with full request/response schemas
