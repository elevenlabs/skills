---
name: flows
description: Use ElevenCreative Flows from code. Currently covers Flows templates via the ElevenLabs Templates API (/v1/flows/templates), getting the result by waiting (SDK create_and_wait, CLI create-and-wait, or polling with Retry-After) or by webhook (flows_template_run). Use when calling a published Flows template from a script or app (including when given an elevenlabs.io/app/templates/<template_id> link), passing template inputs (text, images, video, audio, voices), polling a template run until it finishes, receiving finished runs by webhook, or pinning a template version.
license: MIT
compatibility: Requires internet access and an ElevenLabs API key (ELEVENLABS_API_KEY). Pro plan or above.
metadata: {"openclaw": {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "primaryEnv": "ELEVENLABS_API_KEY"}}
---

# ElevenLabs Flows

ElevenCreative Flows chains image, video, audio and text models into a pipeline. This skill covers running Flows from your own code.

> **Setup:** See [Installation Guide](references/installation.md). The API key needs the **Image & Video** permission, and the workspace must be on a Pro plan or above. The SDKs and the `elevenlabs` CLI read `ELEVENLABS_API_KEY` automatically; REST base URL is `https://api.elevenlabs.io` with the key in the `xi-api-key` header.

## What's covered

| Feature | Use for | Guide |
|---------|---------|-------|
| **Templates** | Running a published Flow (a fixed set of named inputs and outputs) by `template_id` | [Flows templates](references/templates.md) |

Templates are the only part of Flows this skill covers so far. For a template task, read [Flows templates](references/templates.md) before writing code: it has the input and output shapes, the SDK, CLI and REST examples, and the webhook setup.

## Choose how to get the result

A run takes from seconds to several minutes. There are two ways to get the finished run:

| Approach | Use for | How |
|----------|---------|-----|
| **Wait** | Scripts, one-off and batch jobs, trying a template out | SDK `create_and_wait` / `createAndWait`, CLI `elevenlabs flows templates runs create-and-wait`, or poll `GET .../runs/{run_id}` honoring `Retry-After` |
| **Webhook** | Production applications | Pass `webhook` on create; ElevenLabs sends a `flows_template_run` event when the run finishes |

**Default to webhooks for anything that runs in production** — an app server, a queue worker, a user-facing feature. Use waiting only when there is no server to receive the event (a CLI script, a notebook, a batch job) or the user is just trying the template. Never write a fixed-interval poll loop: the server sets the pace with the `Retry-After` header and rate-limits status checks, so a loop that ignores it gets `429`s.

## References

- [Installation Guide](references/installation.md)
- [Flows templates](references/templates.md) — find a template's ports, run it, wait or receive a webhook, inputs, outputs, versions, errors
- [Polling by hand](references/polling.md) — Retry-After-driven loops without `create_and_wait`
- [Webhook handlers](references/webhooks.md) — complete FastAPI and Express servers
