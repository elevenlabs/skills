---
name: flows
description: Generate images and video with the ElevenLabs Image & Video (Flows) API, chain one generation into another (image to video, speech to lip-sync video), and run ElevenCreative Flows templates from code. Covers /v1/flows/image, /v1/flows/video, /v1/flows/text-to-speech and /v1/flows/templates, asset uploads for reference media, waiting with create_and_wait or receiving flows_generation / flows_template_run webhooks, and diagnosing 401/402/403/404 and model_access_denied errors. Use when generating an image or video with ElevenLabs via API, SDK or CLI (e.g. "generate a product video with ElevenLabs"); turning a generated image into a video; given an elevenlabs.io/app/templates/<id> link; given a pasted prompt starting "Help me run the ElevenLabs template"; wiring template runs or generations into a web app (uploads, webhooks, storing results); or when a template run is rejected. Not for plain text-to-speech.
license: MIT
compatibility: Requires internet access and an ElevenLabs API key (ELEVENLABS_API_KEY). Pro plan or above.
metadata: {"openclaw": {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "primaryEnv": "ELEVENLABS_API_KEY"}}
---

# ElevenLabs Flows

The public Flows API generates images, video and speech, chains generations together, and runs published Flows templates. Everything is asynchronous: create, then wait or receive a webhook.

> **Setup:** See [Installation Guide](references/installation.md). Pro plan or above. The API key needs **Image & Video** (and **Text to Speech** for `/v1/flows/text-to-speech`). REST base URL `https://api.elevenlabs.io`, key in the `xi-api-key` header; the SDKs and `elevenlabs` CLI read `ELEVENLABS_API_KEY`.

## Route the request

| The user arrives with | Do this | Read |
|-----------------------|---------|------|
| "Generate an image / video / speech" | One call to `flows.image` / `flows.video` / `flows.text_to_speech` `.create`; the body is keyed by `model_id` | [Generations](references/generations.md) |
| "Turn this image into a video", any multi-step pipeline | Chain with `{"type": "generation", "generation_id": ...}` references; don't wait between steps; webhook (or wait) only on the last step | [Generations](references/generations.md#chain-generations) |
| A local or remote file as input | Upload with `POST /v1/assets` and pass an `asset` reference, or `inline_base64` for one-off files up to 25 MB. There is no URL reference type | [Generations](references/generations.md#reference-media) |
| An `elevenlabs.io/app/templates/<id>` link, or a template id | Take the id from the path, read its ports with `flows.templates.get`, then run it | [Templates](references/templates.md) |
| A pasted prompt starting "Help me run the ElevenLabs template" | It already holds the template id, version id, input/output ids and SDK snippets: trust them, don't re-fetch or restate them, and use this skill only for what the prompt doesn't cover | [Templates](references/templates.md#when-the-user-pasted-copy-for-llm) |
| A template or generation inside a web app (uploads, users, results) | Upload on the server, store the run/generation id on the user's record, webhook if the app has a public URL, re-host outputs | [App integration](references/app-integration.md) |
| A 401 / 402 / 403 / 404 / `model_access_denied`, or "it's not in `templates.list`" | Map the status to its cause and the user's next step | [Access and errors](references/access-errors.md) |

Read the linked reference before writing code: it has the request shapes, SDK class names and field spellings.

## Choose MCP or code

When the hosted ElevenLabs MCP is connected (tools named `creative_*`, e.g. `creative_generate_image`, `creative_generate_video`), use it for one-off generations and quick chains the user wants to see now. Use the API/SDK/CLI when the user wants code, a script, or an integration. The MCP has no tool to publish a template or run a published template; for templates use the API. If only speech tools are present, the connector is the voice-only one; for images and video the user adds the full connector `https://api.elevenlabs.io/v1/mcp`.

## Choose how to get the result

| Approach | Use for | How |
|----------|---------|-----|
| **Webhook** | Production: app servers, queue workers, anything with a public HTTPS URL | Pass `webhook: {"type": "all"}` on create (on a chain, only the last step); handle `flows_generation` / `flows_template_run` |
| **Wait** | Scripts, notebooks, batch jobs, trying something out, apps with no public URL | SDK `create_and_wait` / `createAndWait`, or CLI `elevenlabs flows ... create-and-wait` |

Never write a fixed-interval poll loop: the server paces checks with `Retry-After` and rate-limits status reads. If neither helper is available, follow [Polling by hand](references/polling.md).

## Rules that apply everywhere

- A failed generation or run is returned, not raised: check `status` (and each template output's `status`) before reading `content_url`.
- `content_url` is a signed URL that expires about an hour after it was issued: download or re-host it, don't store it. Fetch the generation/run again for a fresh URL.
- Keep the API key on the server. Browser uploads go through your server to `POST /v1/assets`.
- Pin a template's `version_id` in code you ship.

## References

- [Installation Guide](references/installation.md)
- [Generations](references/generations.md): image, video and TTS requests, reference types, chaining, assets
- [Templates](references/templates.md): template URL to running code, inputs, outputs, versions, templates with a custom page, Copy for LLM
- [Access and errors](references/access-errors.md): every rejection and what to do about it
- [App integration](references/app-integration.md): browser upload to asset, storing ids, webhook vs wait, re-hosting, idempotency
- [Webhook handlers](references/webhooks.md): complete FastAPI and Express servers
- [Polling by hand](references/polling.md): Retry-After loops without `create_and_wait`
