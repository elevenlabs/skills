# Dubbing Projects API Reference

Full endpoint-by-endpoint reference for the prerelease Dubbing Projects API.

- **Base URL:** `https://api.elevenlabs.io`
- **Authentication:** `xi-api-key` header on every request
- **Model:** `dubbing_v2` (default and only model today; `dubbing_v1` support will follow)
- **Source size limit:** up to 3 GiB per source (upload or URL)

## Contents

- [Endpoint quick reference](#endpoint-quick-reference)
- [Projects](#projects)
- [Source transcript](#source-transcript)
- [Languages](#languages)
- [Language transcript (translations)](#language-transcript-translations)
- [Regeneration](#regeneration)
- [Revisions](#revisions)

## Endpoint quick reference

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/dubbing/project` | Create a project (file or URL) |
| GET | `/v1/dubbing/project` | List projects (paginated) |
| GET | `/v1/dubbing/project/{project_id}` | Get a project |
| DELETE | `/v1/dubbing/project/{project_id}` | Delete a project and its languages |
| GET | `/v1/dubbing/project/{project_id}/transcript` | Get the source transcript |
| PATCH | `/v1/dubbing/project/{project_id}/transcript/segment/{segment_id}` | Edit a source segment |
| POST | `/v1/dubbing/project/{project_id}/transcript/segment` | Add a source segment |
| DELETE | `/v1/dubbing/project/{project_id}/transcript/segment/{segment_id}` | Delete a source segment |
| POST | `/v1/dubbing/project/{project_id}/language` | Add a language target |
| GET | `/v1/dubbing/project/{project_id}/language` | List language targets (paginated) |
| GET | `/v1/dubbing/project/{project_id}/language/{language_id}` | Get a language target |
| DELETE | `/v1/dubbing/project/{project_id}/language/{language_id}` | Delete a language target |
| GET | `/v1/dubbing/project/{project_id}/language/{language_id}/transcript` | Get a language's transcript (translations) |
| PATCH | `/v1/dubbing/project/{project_id}/language/{language_id}/transcript/segment/{segment_id}` | Edit a translation |
| POST | `/v1/dubbing/project/{project_id}/language/{language_id}/transcript/regenerate` | Regenerate a language from its edited transcript |

## Projects

### Create a project

`POST /v1/dubbing/project` — `multipart/form-data` with **either** `file` **or** `source_url` (not both).

| Field | Required | Notes |
|-------|----------|-------|
| `file` | one of file/source_url | The source media to dub (audio or video) |
| `source_url` | one of file/source_url | Public URL to fetch the source media from |
| `source_language` | no | ISO 639 code (e.g. `en`). Omit to auto-detect |
| `reference` | no | Free-form label to identify the project on your end (max 500 chars) |
| `model_id` | no | `dubbing_v2` (default) |
| `keyterms` | no | Terms to bias transcription/translation toward (e.g. product or brand names), up to 100 terms of 200 characters each. In multipart, repeat the field once per term |

**Auto-detected source language:** if `source_language` is omitted, the project's `source_language` stays `null`; the detected language is reported as the `language` field on the source transcript.

**Response (`201 Created`)** — the project starts in `queued`; `media` is `null` until preparation finishes:

```json
{
  "project_id": "proj_1601kwkyxp0hfzvtmyxwqxx6mcy3",
  "status": "queued",
  "reference": "Q3 marketing video",
  "source_language": "en",
  "model_id": "dubbing_v2",
  "media": null,
  "language_ids": [],
  "revision": 0,
  "created_at": "2026-07-03T10:15:30Z",
  "updated_at": "2026-07-03T10:15:30Z"
}
```

The source is fetched (for a URL) and transcribed asynchronously — poll the project until it reaches `ready`.

### Get a project

`GET /v1/dubbing/project/{project_id}`

Once `ready`, `media` is populated:

```json
{
  "project_id": "proj_1601kwkyxp0hfzvtmyxwqxx6mcy3",
  "status": "ready",
  "reference": "Q3 marketing video",
  "source_language": "en",
  "model_id": "dubbing_v2",
  "media": {
    "filename": "promo.mp4",
    "duration_s": 42.5,
    "has_video": true,
    "mime_type": "video/mp4"
  },
  "language_ids": [],
  "revision": 0,
  "created_at": "2026-07-03T10:15:30Z",
  "updated_at": "2026-07-03T10:17:12Z"
}
```

`language_ids` stays empty until languages are added; `revision` stays 0 until the source transcript is edited (transcription itself doesn't bump it).

**Project states:**

| Status | Meaning |
|--------|---------|
| `queued` | Created; the source is being fetched and preparation is enqueued, but no worker has started it yet |
| `preparing` | Preparation tasks are running |
| `ready` | Preparation finished. The source transcript is available and languages can be added/generated. A project **stays** at `ready` — per-language progress lives on the languages |
| `failed` | Preparation failed (e.g. the source couldn't be fetched or decoded) |

### List projects

`GET /v1/dubbing/project` — cursor-paginated.

Query params: `page_size` (default 20, max 100), `cursor`, `status` (`queued`/`preparing`/`ready`/`failed`), `sort_direction` (`DESCENDING` default).

```json
{ "projects": [ /* ProjectResponse... */ ], "next_cursor": null }
```

Pass `next_cursor` back as `cursor` to fetch the next page; `null` means the end.

### Delete a project

`DELETE /v1/dubbing/project/{project_id}` — deletes the project and its languages.

## Source transcript

Every source edit bumps the project's `revision`; each edit response returns the new value. Editing the source after a language exists marks that language's output `stale` and requires a regeneration — finalize the source **before** adding languages.

### Get the source transcript

`GET /v1/dubbing/project/{project_id}/transcript`

```json
{
  "language": "en",
  "segments": [
    {
      "id": "0199a3f0-1c2d-7abc-8def-0123456789ab",
      "text": "Welcome to our product demo.",
      "speaker_id": "default_speaker",
      "start_s": 0.0,
      "end_s": 2.5
    }
  ],
  "revision": 0
}
```

Each segment has a stable `id` used to edit or delete it.

### Edit a segment

`PATCH /v1/dubbing/project/{project_id}/transcript/segment/{segment_id}`

Send only the fields to change (`text`, `speaker_id`, `start_s`, `end_s`); at least one is required. If sending both `start_s` and `end_s`, `end_s` must be greater than `start_s`.

```json
{
  "segment": {
    "id": "0199a3f0-1c2d-7abc-8def-0123456789ab",
    "text": "Welcome to our latest product demo.",
    "speaker_id": "default_speaker",
    "start_s": 0.0,
    "end_s": 2.5
  },
  "revision": 1
}
```

### Add a segment

`POST /v1/dubbing/project/{project_id}/transcript/segment`

All fields required (`text`, `speaker_id`, `start_s`, `end_s`). The server assigns the segment `id`. Use a `speaker_id` that already appears in the source transcript so the new line is dubbed with that speaker's voice.

The response echoes the new segment with its server-assigned `id` plus the new project `revision`.

### Delete a segment

`DELETE /v1/dubbing/project/{project_id}/transcript/segment/{segment_id}`

```json
{ "revision": 3 }
```

## Languages

### Add a language

`POST /v1/dubbing/project/{project_id}/language`

JSON body:

| Field | Required | Notes |
|-------|----------|-------|
| `target_language` | yes | ISO 639 code (e.g. `es`) |
| `model_id` | no | Defaults to the project's model |
| `voice_settings` | no | e.g. `{"cloning_strength": 7}` — `cloning_strength` accepts values between 0 and 10 inclusive |

**Response (`201 Created`)** — starts `queued`:

```json
{
  "language_id": "lang_1001kwkyxp0je6ktn4knsfrasx5s",
  "project_id": "proj_1601kwkyxp0hfzvtmyxwqxx6mcy3",
  "target_language": "es",
  "status": "queued",
  "model_id": "dubbing_v2",
  "outputs": null,
  "revision": 0,
  "output_revision": null,
  "created_at": "2026-07-03T10:16:00Z",
  "updated_at": "2026-07-03T10:16:00Z"
}
```

A language can be added to a project that isn't `ready` yet — it stays `queued` and starts automatically once the project becomes `ready`. (The walkthrough also mentions a `target_language` shortcut on project create.)

**Language states:**

| Status | Meaning |
|--------|---------|
| `queued` | Created and waiting — either on the project becoming `ready`, or on a worker to pick up its generation |
| `processing` | The dub is being generated |
| `completed` | The dub finished; `outputs` is populated |
| `stale` | Previously completed, but its transcript (source or translation) changed, so the current output no longer matches. It keeps its last output until regenerated |
| `failed` | Generation failed |

### Get a language

`GET /v1/dubbing/project/{project_id}/language/{language_id}`

Once `completed`, `outputs` carries a signed, time-limited download URL (valid ~1 hour; re-fetch the language for a fresh URL):

```json
{
  "language_id": "lang_1001kwkyxp0je6ktn4knsfrasx5s",
  "project_id": "proj_1601kwkyxp0hfzvtmyxwqxx6mcy3",
  "target_language": "es",
  "status": "completed",
  "model_id": "dubbing_v2",
  "outputs": {
    "lossless_audio": "https://storage.googleapis.com/eleven-dubbing/.../output.wav?X-Goog-Signature=..."
  },
  "revision": 0,
  "output_revision": 0,
  "created_at": "2026-07-03T10:16:00Z",
  "updated_at": "2026-07-03T10:20:45Z"
}
```

When `output_revision` equals `revision`, the downloadable output reflects the current transcript. When it's behind (and status is `stale`), the output is out of date and needs a regeneration.

### List languages

`GET /v1/dubbing/project/{project_id}/language` — cursor-paginated, optional `status` filter.

### Delete a language

`DELETE /v1/dubbing/project/{project_id}/language/{language_id}` → `204 No Content`.

## Language transcript (translations)

### Get a language's transcript

`GET /v1/dubbing/project/{project_id}/language/{language_id}/transcript`

Pairs each source segment with its translation (`null` = not yet translated). Segment ids match the source transcript, so translations line up against the source.

```json
{
  "source_language": "en",
  "target_language": "es",
  "segments": [
    {
      "id": "0199a3f0-1c2d-7abc-8def-0123456789ab",
      "speaker_id": "default_speaker",
      "start_s": 0.0,
      "end_s": 2.5,
      "source_text": "Welcome to our latest product demo.",
      "translation": "Bienvenido a la demostración de nuestro producto."
    }
  ],
  "revision": 0
}
```

### Edit a translation

`PATCH /v1/dubbing/project/{project_id}/language/{language_id}/transcript/segment/{segment_id}`

Body: `{"translation": "..."}`. Pass `null` to clear it and mark the segment for re-translation.

A translation edit affects only this language — the source transcript and other languages are untouched. It bumps this language's `revision`, and a `completed` language becomes `stale`: its downloadable output still reflects the previous `output_revision` until regenerated.

## Regeneration

`POST /v1/dubbing/project/{project_id}/language/{language_id}/transcript/regenerate`

Produces a fresh dub from the current transcript after editing a language's translation (or after source edits marked it `stale`). **Charged like a generation.**

**Response (`202 Accepted`)** — the language goes back to `queued`; `output_revision` still points at the previous output until the new one finishes:

```json
{
  "language_id": "lang_1001kwkyxp0je6ktn4knsfrasx5s",
  "project_id": "proj_1601kwkyxp0hfzvtmyxwqxx6mcy3",
  "target_language": "es",
  "status": "queued",
  "model_id": "dubbing_v2",
  "outputs": null,
  "revision": 1,
  "output_revision": 0,
  "created_at": "2026-07-03T10:16:00Z",
  "updated_at": "2026-07-03T10:25:10Z"
}
```

Poll the language until `completed`, then download the refreshed `outputs.lossless_audio`. At that point `output_revision` equals `revision`.

Returns `409 Conflict` if the project isn't `ready` or the language isn't in a settled state (e.g. it's already generating).

## Revisions

Every project and language carries its own monotonic revision counter, each starting at 0 and independent of the others:

- The **project's** `revision` increases on each source-transcript edit (transcription itself doesn't bump it).
- A **language's** `revision` starts at 0 when the language is created — it does **not** inherit the project's current revision — and increases when its translation is edited **or** when a source edit affects it.
- A language's `output_revision` is the revision its current audio was generated from. When `output_revision` is behind `revision`, the output is out of date and needs a regeneration.
