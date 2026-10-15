---
name: flows-templates
description: Run ElevenCreative Flows templates from code with the ElevenLabs Templates API (/v1/flows/templates), and get the result by waiting (SDK create_and_wait, CLI create-and-wait, or polling with Retry-After) or by webhook (flows_template_run). Use when calling a published Flows template from a script or app (including when given an elevenlabs.io/app/templates/<template_id> link), passing template inputs (text, images, video, audio, voices), polling a template run until it finishes, receiving finished runs by webhook, or pinning a template version.
license: MIT
compatibility: Requires internet access and an ElevenLabs API key (ELEVENLABS_API_KEY). Pro plan or above.
metadata: {"openclaw": {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "primaryEnv": "ELEVENLABS_API_KEY"}}
---

# ElevenLabs Flows Templates

Run a template built in ElevenCreative Flows from your own code. A **template** is a published Flow: a chain of models with a fixed set of named **inputs** and **outputs**. Its author already chose the models and prompts, so your code only passes the input values and reads the outputs.

> **Setup:** See [Installation Guide](references/installation.md). The API key needs the **Image & Video** permission, and the workspace must be on a Pro plan or above. The SDKs and the `elevenlabs` CLI read `ELEVENLABS_API_KEY` automatically; REST base URL is `https://api.elevenlabs.io` with the key in the `xi-api-key` header.

## Choose how to get the result

A run takes from seconds to several minutes. There are two ways to get the finished run:

| Approach | Use for | How |
|----------|---------|-----|
| **Wait** | Scripts, one-off and batch jobs, trying a template out | SDK `create_and_wait` / `createAndWait`, CLI `elevenlabs flows templates runs create-and-wait`, or poll `GET .../runs/{run_id}` honoring `Retry-After` |
| **Webhook** | Production applications | Pass `webhook` on create; ElevenLabs sends a `flows_template_run` event when the run finishes |

**Default to webhooks for anything that runs in production** — an app server, a queue worker, a user-facing feature. Use waiting only when there is no server to receive the event (a CLI script, a notebook, a batch job) or the user is just trying the template. Never write a fixed-interval poll loop: the server sets the pace with the `Retry-After` header and rate-limits status checks, so a loop that ignores it gets `429`s.

## Concepts

| Concept | Meaning |
|---------|---------|
| **Template** | A published Flow, identified by `template_id`. Shown in the app URL (`/app/templates/<template_id>`) and by `flows.templates.list`. |
| **Version** | A published snapshot, identified by `version_id`. Each version has its own `inputs` and `outputs` ports. `latest` (the default) runs the newest published version. |
| **Input port** | One required input, keyed by its `id`. Its `content_schema.type` decides what value it takes. |
| **Output port** | One result, keyed by its `id` in the run's `outputs`. Each output has its own `status`. |
| **Run** | One execution. `status` is rolled up from its outputs: `pending` → `generating` → `completed` or `failed`. |

## Find the template's inputs and outputs

Every template page in the app has an **API** tab with ready-to-run cURL, Python and TypeScript snippets, in both **Wait for the result** and **Webhook** modes. From code, read the ports from the template itself:

```python
template = client.flows.templates.get("Yz4DETxRv4uXyIo5PnEy")
version = template.versions[0]  # newest version the API can run
print(version.version_id)
for port in version.inputs:
    print("input ", port.id, port.content_schema.type)
for port in version.outputs:
    print("output", port.id, port.content_schema.type)
```

```bash
elevenlabs flows templates get --template-id Yz4DETxRv4uXyIo5PnEy
```

`versions` only lists versions the API can run (a version built on a model the API doesn't offer is left out), so it can be empty. `flows.templates.list` lists the workspace's templates; templates shared by link or from Explore aren't listed but can still be fetched and run by id.

## Wait for the result (scripts)

`create_and_wait` starts the run, then checks on it at the interval the server suggests (`Retry-After`) until it is `completed` or `failed`. It needs a recent SDK; see the [Installation Guide](references/installation.md).

### Python

```python
import base64
import os

import requests
from elevenlabs import ElevenLabs, TemplateInputReference_InlineBase64

client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

with open("garment.jpg", "rb") as f:
    photo = base64.b64encode(f.read()).decode()

run = client.flows.templates.runs.create_and_wait(
    "Yz4DETxRv4uXyIo5PnEy",
    version_id="Kqs4nRrpndEjQ54BhbwE",  # pin the version you tested against
    inputs={
        "garment_photo": TemplateInputReference_InlineBase64(
            content_base_64=photo,  # field name is content_base_64 in Python
            mime_type="image/jpeg",
        ),
    },
    wait_timeout_in_seconds=600,  # optional; omit to wait indefinitely
)

packshot = run.outputs["packshot"]
# Checking `type` narrows the output union, so type checkers know it has content_url.
if packshot.type == "image" and packshot.status == "completed" and packshot.content_url:
    with open("packshot.jpg", "wb") as f:
        f.write(requests.get(packshot.content_url).content)
else:
    print("Failed:", packshot.failure_reason, packshot.error_message)
```

### TypeScript

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { readFile, writeFile } from "fs/promises";

const client = new ElevenLabsClient();
const photo = await readFile("garment.jpg");

const run = await client.flows.templates.runs.createAndWait(
  "Yz4DETxRv4uXyIo5PnEy",
  {
    versionId: "Kqs4nRrpndEjQ54BhbwE",
    inputs: {
      garment_photo: {
        type: "inline_base64",
        contentBase64: photo.toString("base64"),
        mimeType: "image/jpeg",
      },
    },
  },
  { waitTimeoutInSeconds: 600 }, // optional; omit to wait indefinitely
);

const packshot = run.outputs["packshot"];
if (packshot.type === "image" && packshot.status === "completed" && packshot.contentUrl) {
  const response = await fetch(packshot.contentUrl);
  await writeFile("packshot.jpg", Buffer.from(await response.arrayBuffer()));
} else {
  console.error("Failed:", packshot.failureReason, packshot.errorMessage);
}
```

### Behavior of `create_and_wait`

- A **failed run is returned, not raised** — always check each output's `status` before reading its content.
- With a wait timeout (`wait_timeout_in_seconds` / `waitTimeoutInSeconds`), an unfinished run raises `FlowsWaitTimeoutError` carrying the run `id`, `template_id` and the last response. In Python, import it from `elevenlabs.flows_custom`. Don't use `timeout`/`timeoutInSeconds` for this — that is the per-HTTP-request timeout.
- `min_poll_interval_in_seconds` / `minPollIntervalInSeconds` sets the floor between checks (default 3s, minimum 0.5s). There's normally no reason to change it.
- `429`s on status checks are retried automatically after their `Retry-After`.

### From the terminal

`elevenlabs flows templates runs create-and-wait` takes the same flags as `runs create`, waits the way `create_and_wait` does, and prints the finished run:

```bash
run=$(elevenlabs flows templates runs create-and-wait \
  --template-id Yz4DETxRv4uXyIo5PnEy \
  --version-id Kqs4nRrpndEjQ54BhbwE \
  --inputs '{"garment_photo": {"type": "asset", "asset_id": "YOUR_ASSET_ID"}}' \
  --wait-timeout 600) || { echo "run failed or timed out: $run" >&2; exit 1; }
jq -r '.outputs.packshot.content_url' <<<"$run"
```

- stdout carries only the final run (the same JSON as `runs get`), so `jq`, `--query` and `--format` work on it. `--query` keeps JSON quoting; use `jq -r` for a bare URL. Progress goes to stderr, and only when stderr is a terminal or with `--debug`.
- Exit code `0` means `completed`. A `failed` run is still printed, but the command exits `1`. Check the exit code before reading outputs, and don't pipe the command straight into `jq` without `set -o pipefail`, which would hide it.
- If `--wait-timeout` runs out, it exits `1` with an error whose `reason` is `waitTimeout`; its `help` field holds the `runs get` command for that run. The run keeps going on the server.
- `--json '{"version_id": ..., "inputs": {...}}'` works in place of the per-field flags, and `--json -` reads the body from stdin.
- The same command exists for single generations: `elevenlabs flows image|video|text-to-speech create-and-wait --json '{...}'`.

Don't wrap `runs create` and `runs get` in your own shell loop; `create-and-wait` already reads `Retry-After`, which `runs get` doesn't show. To check on a run started elsewhere, use `elevenlabs flows templates runs get --template-id ... --run-id ...` once.

### Polling by hand (other languages, older SDKs and CLIs)

Without the helper, poll the run yourself and **sleep for the `Retry-After` header value** between checks. See [Polling by hand](references/polling.md) for complete Python, TypeScript and shell loops.

## Get the result by webhook (production)

### 1. Subscribe a webhook to template runs (once per workspace)

Template runs are delivered to workspace webhooks subscribed to the **`flows`** event (shown in the app as **Image & Video API generation or template run completed**). Set one up in [Developers → Webhooks](https://elevenlabs.io/app/developers/webhooks), or via the API:

```python
from elevenlabs import WebhookHmacSettings

created = client.webhooks.create(
    settings=WebhookHmacSettings(
        auth_type="hmac",
        name="Template runs",
        webhook_url="https://example.com/webhooks/elevenlabs",
    ),
)
# Store created.webhook_secret securely; it is needed to verify events.
client.webhooks.update(created.webhook_id, is_disabled=False, name="Template runs", events=["flows"])
```

REST: `POST /v1/workspace/webhooks`, then `PATCH /v1/workspace/webhooks/{webhook_id}` with `{"is_disabled": false, "name": "...", "events": ["flows"]}` (`events` is the complete set, so include any events the webhook already has). Creating or subscribing webhooks needs the **Webhooks Manage** permission or workspace admin. The URL must be public HTTPS; for local development, expose your server with a tunnel.

### 2. Start the run with `webhook`

```python
from elevenlabs import TemplateInputReference_Asset, WebhookTarget_All

run = client.flows.templates.runs.create(
    template_id="Yz4DETxRv4uXyIo5PnEy",
    version_id="Kqs4nRrpndEjQ54BhbwE",
    inputs={"garment_photo": TemplateInputReference_Asset(asset_id="YOUR_ASSET_ID")},
    webhook=WebhookTarget_All(),  # every webhook subscribed to `flows`
)
print(run.id, run.status)  # return now; the result arrives at the webhook
```

```typescript
const run = await client.flows.templates.runs.create("Yz4DETxRv4uXyIo5PnEy", {
  versionId: "Kqs4nRrpndEjQ54BhbwE",
  inputs: { garment_photo: { type: "asset", assetId: "YOUR_ASSET_ID" } },
  webhook: { type: "all" },
});
```

To target specific webhooks, use `WebhookTarget_Ids(ids=["..."])` / `{ type: "ids", ids: ["..."] }`. The create call is **rejected** if delivery is impossible:

| Error | Cause |
|-------|-------|
| `no_webhooks_configured` | `all` was requested but no webhook is subscribed to `flows` |
| `invalid_webhook_id` | A listed webhook doesn't exist or isn't subscribed to `flows` |
| `webhook_disabled` | A targeted webhook is disabled (manually, or automatically after repeated delivery failures) |

### 3. Handle the `flows_template_run` event

Verify the `ElevenLabs-Signature` header over the **raw** request body with `construct_event` / `constructEvent`, check the event `type`, then read `data` — the run in the same shape as the terminal `GET .../runs/{run_id}` response.

```python
from elevenlabs import TemplateRunResponse
from elevenlabs.errors import BadRequestError

@app.post("/webhooks/elevenlabs")
async def receive(request: Request):
    try:
        event = client.webhooks.construct_event(
            rawBody=(await request.body()).decode("utf-8"),
            sig_header=request.headers.get("elevenlabs-signature"),
            secret=os.environ["WEBHOOK_SECRET"],
        )
    except BadRequestError:
        return JSONResponse({"error": "invalid signature"}, status_code=401)

    if event["type"] != "flows_template_run":  # construct_event returns a dict
        return {"status": "ignored"}

    run = TemplateRunResponse.model_validate(event["data"])
    enqueue_run(run)  # hand off; download outside the request
    return {"status": "received"}
```

```typescript
app.post("/webhooks/elevenlabs", express.raw({ type: "application/json" }), async (req, res) => {
  let event;
  try {
    event = await client.webhooks.constructEvent(
      req.body.toString(),
      req.headers["elevenlabs-signature"] as string,
      process.env.WEBHOOK_SECRET!,
    );
  } catch {
    return res.status(401).json({ error: "invalid signature" });
  }
  if (event.type !== "flows_template_run") return res.sendStatus(200);

  const run = event.data; // raw JSON: fields are snake_case (content_url, failure_reason)
  await enqueueRun(run);
  res.sendStatus(200);
});
```

Payload:

```json
{
  "type": "flows_template_run",
  "event_timestamp": 1739721600,
  "data": {
    "id": "RUN_ID",
    "template_id": "Yz4DETxRv4uXyIo5PnEy",
    "version_id": "Kqs4nRrpndEjQ54BhbwE",
    "status": "completed",
    "outputs": {
      "packshot": {
        "type": "image",
        "id": "GENERATION_ID",
        "status": "completed",
        "content_url": "https://storage.googleapis.com/generations/GENERATION_ID",
        "content_mime_type": "image/jpeg"
      }
    }
  }
}
```

Full FastAPI and Express servers: [Webhook handlers](references/webhooks.md).

### Delivery rules

- One event per run per targeted webhook, sent once the run is `completed` or `failed`. Use the run `id` to **deduplicate** — make the handler idempotent.
- Return **2xx quickly**. Download media in a background worker, not inside the request; repeated delivery failures auto-disable the webhook.
- `data.template_id` identifies the template, so one endpoint can serve several templates.
- Webhooks are the fast path. Where a missed result is unacceptable, also reconcile periodically with `flows.templates.runs.list(template_id)` (newest first).

## Inputs

Pass one value per input port of the version you run, keyed by the port id. Missing or unknown ids are rejected.

| Port `type` | Value |
|-------------|-------|
| `string` | The text, or a `generation` reference. If the schema has an `enum`, only those values. |
| `number`, `integer`, `boolean` | A JSON value of that type |
| `image`, `video`, `audio` | An `asset`, `generation` or `inline_base64` reference |
| `voice` | A `voice` reference |
| `array` | A list, one value per element in the form its `items` type takes |
| `object` | Not supported through the API yet |

| Reference | Python | TypeScript / JSON |
|-----------|--------|-------------------|
| Uploaded asset (`POST /v1/assets`) | `TemplateInputReference_Asset(asset_id=...)` | `{ type: "asset", assetId }` / `{"type": "asset", "asset_id": ...}` |
| Previous generation's output | `TemplateInputReference_Generation(generation_id=...)` | `{ type: "generation", generationId }` |
| Inline base64 | `TemplateInputReference_InlineBase64(content_base_64=..., mime_type=...)` | `{ type: "inline_base64", contentBase64, mimeType }` |
| Voice | `TemplateInputReference_Voice(voice_id=...)` | `{ type: "voice", voiceId }` |

Inline base64 is limited to 25 MB decoded and isn't kept after the run; allowed MIME types are `image/jpeg`, `image/png`, `image/webp`, `image/heic`, `image/heif`, `audio/mpeg`, `audio/wav`, `video/mp4`, `video/quicktime`, `video/webm`. To reuse a file across runs, upload it once and pass its `asset_id`.

Input ids keep the template's spelling in both SDKs (`garment_photo`, not `garmentPhoto`); only the fields of a reference are camelCased in TypeScript.

## Outputs

`run.outputs` has one entry per output port, keyed by id, each with its own `status`, so one output can fail while others complete.

| Output `type` | Fields when `completed` |
|---------------|-------------------------|
| `image`, `video`, `audio` | `content_url` (signed, expires ~1 hour — fetch the run again for a fresh URL), `content_mime_type` |
| `string` | `content` |

A failed output has `failure_reason` (`timeout`, `model_error`, `moderated`, `invalid_parameters`, `dependency_failed`, `charging_failed`, `internal_error`) and `error_message`. Failed generations are not charged. Each output's `id` is a generation id: pass it as a `generation` reference to feed the output into another run or generation.

## Pin a version

Pass the `version_id` you tested against. `latest` (or omitting it) switches to whatever the author publishes next, which can rename or add inputs and break your code. To upgrade, read the new version's ports with `flows.templates.get`, update your inputs, then change `version_id`.

## Error Handling

- **401 / 403**: Invalid API key, or the key lacks the Image & Video permission
- **402 `paid_plan_required`**: The workspace is below Pro
- **422**: Missing/unknown input id, or a value of the wrong shape for its port
- **429** on status checks: Too many reads for this API key — wait `Retry-After` seconds; prefer webhooks
- **Template not found / not runnable**: It isn't shared with your workspace (`Just me` templates only run for their author), or no published version can run through the API (`versions` is empty)

## References

- [Installation Guide](references/installation.md)
- [Polling by hand](references/polling.md) — Retry-After-driven loops without `create_and_wait`
- [Webhook handlers](references/webhooks.md) — complete FastAPI and Express servers
