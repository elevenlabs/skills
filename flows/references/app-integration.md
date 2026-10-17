# Wiring Flows into an app

How a user-facing app runs a template (or a generation) on a user's upload and shows them the result. The same shape works for single generations and chains: swap `templates.runs.create` for `flows.image|video.create` and `flows_template_run` for `flows_generation`.

## The pipeline

1. **Browser → your server.** The browser posts the file (multipart `FormData`) to your own endpoint. The ElevenLabs API key lives only on the server; never call the ElevenLabs API from the browser and never ship the key in client code or `NEXT_PUBLIC_*` env vars.
2. **Your server → `POST /v1/assets`.** Upload the bytes with `client.assets.create` and keep the returned `asset_id`. Validate size and MIME type first (images `image/jpeg|png|webp|heic|heif`, audio `audio/mpeg|wav`, video `video/mp4|quicktime|webm`).
3. **Start the run** with the asset as an `asset` reference, the pinned `version_id`, and `webhook: {type: "all"}` if the app has a public URL (see [Choose webhook or wait](#choose-webhook-or-wait)).
4. **Store the run id against the user's record** before responding: `{user_id, run_id, template_id, version_id, status: "pending"}` (for a generation or chain, store the last generation's `id`). Return your own job id to the browser.
5. **Receive the result**: webhook handler or background waiter updates the record by run id.
6. **Re-host each output** to your storage (S3, GCS, R2, your CDN) and store *your* URL. `content_url` expires about an hour after it was issued.
7. **The browser reads status from your server** (poll your own endpoint, SSE, or websockets), never from ElevenLabs.

## Choose webhook or wait

| The app | Use |
|---------|-----|
| Has a public HTTPS URL (deployed server, Vercel, Cloud Run) | **Webhook.** Start with `runs.create(..., webhook=all)`, return immediately, finish in the `flows_template_run` handler |
| Has no public URL (local-only, intranet, desktop app, a job runner behind a firewall) | **`create_and_wait` in a background worker**, not inside the HTTP request. Respond with your job id first, then wait in a queue job / background task and write the result to the record |

During local development of a webhook app, either expose the server with a tunnel, or temporarily use the background-wait path.

The webhook must exist and be subscribed to the `flows` event before the first run ([setup](templates.md#1-subscribe-a-webhook-to-template-runs-once-per-workspace)); store its signing secret as `WEBHOOK_SECRET` in the server's secret store.

## Handle the webhook idempotently

- Verify `elevenlabs-signature` over the **raw** body (`express.raw`, `await req.text()` in Next.js, `await request.body()` in FastAPI) with `constructEvent` / `construct_event`.
- Ignore event types you don't handle with a 2xx.
- Look the record up by `data.id` (run or generation id). If it's unknown, or already in a terminal state, return 2xx and do nothing.
- Make the transition atomic: e.g. `UPDATE jobs SET status = 'processing' WHERE run_id = $1 AND status = 'pending'` and only continue if one row changed. A unique index on `run_id` stops duplicate records.
- Return 2xx immediately; download and re-host in a background job. Repeated slow or failed deliveries auto-disable the webhook.
- Each targeted webhook gets its own event; with `{"type": "all"}` and several subscribed webhooks, every endpoint receives it, so each must tolerate events for jobs it didn't start.
- Reconcile on a schedule: list recent runs with `flows.templates.runs.list(template_id)` (or `flows.<modality>.list(status="completed")`) and process any terminal ones whose records are still pending.

## Re-host outputs

```typescript
async function rehost(output: { content_url: string; content_mime_type: string }, key: string) {
  const media = await fetch(output.content_url);
  if (!media.ok) throw new Error(`download failed: ${media.status}`);
  await storage.put(key, Buffer.from(await media.arrayBuffer()), { contentType: output.content_mime_type });
  return storage.publicUrl(key);
}
```

If a worker picks the job up after the URL expired, fetch the run (`runs.get(template_id, run_id)`) or generation (`flows.<modality>.get(id)`) again for a fresh `content_url`.

## Express (TypeScript): upload → packshot run → webhook

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import express from "express";
import multer from "multer";

const client = new ElevenLabsClient(); // ELEVENLABS_API_KEY from the server env
const app = express();
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 100 * 1024 * 1024 } });

const TEMPLATE_ID = "Yz4DETxRv4uXyIo5PnEy";
const VERSION_ID = "Kqs4nRrpndEjQ54BhbwE"; // pinned; from flows.templates.get
const IMAGE_TYPES = new Set(["image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"]);

app.post("/api/packshots", upload.single("photo"), async (req, res) => {
  const userId = req.user.id; // from your auth middleware
  if (!req.file || !IMAGE_TYPES.has(req.file.mimetype)) return res.status(400).json({ error: "Upload a JPEG, PNG, WebP or HEIC image" });

  const asset = await client.assets.create({
    asset: { data: req.file.buffer, filename: req.file.originalname, contentType: req.file.mimetype },
    name: `${userId}-${Date.now()}-${req.file.originalname}`,
  });

  const run = await client.flows.templates.runs.create(TEMPLATE_ID, {
    versionId: VERSION_ID,
    inputs: { garment_photo: { type: "asset", assetId: asset.assetId } },
    webhook: { type: "all" },
  });

  const job = await db.jobs.insert({ userId, runId: run.id, templateId: TEMPLATE_ID, versionId: VERSION_ID, status: "pending" });
  res.status(202).json({ jobId: job.id });
});

app.get("/api/packshots/:jobId", async (req, res) => {
  const job = await db.jobs.findForUser(req.params.jobId, req.user.id);
  if (!job) return res.sendStatus(404);
  res.json({ status: job.status, url: job.resultUrl, error: job.error });
});

// Registered before express.json(): the signature is computed over the raw bytes.
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

  const run = event.data; // raw JSON: snake_case
  const claimed = await db.jobs.claimPending(run.id); // atomic pending -> processing; null if unknown or done
  res.sendStatus(200);
  if (claimed) await queue.enqueue("finish-packshot", { jobId: claimed.id, run });
});

app.use(express.json());
```

The `finish-packshot` worker reads `run.outputs.packshot`: when `status === "completed"`, re-host `content_url` and set `resultUrl` and `status: "completed"`; otherwise store `failure_reason` / `error_message` and `status: "failed"`.

## Next.js (App Router): browser upload

```tsx
// app/packshot/upload-form.tsx
"use client";
export function UploadForm() {
  async function onSubmit(formData: FormData) {
    const res = await fetch("/api/packshots", { method: "POST", body: formData });
    const { jobId } = await res.json();
    // poll /api/packshots/{jobId} (your route) until status is completed or failed
  }
  return (
    <form action={onSubmit}>
      <input type="file" name="photo" accept="image/jpeg,image/png,image/webp" required />
      <button type="submit">Make packshot</button>
    </form>
  );
}
```

```typescript
// app/api/packshots/route.ts
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { NextResponse } from "next/server";

export const runtime = "nodejs";
const client = new ElevenLabsClient(); // server-only env var ELEVENLABS_API_KEY

export async function POST(req: Request) {
  const userId = await requireUserId(req); // your auth
  const file = (await req.formData()).get("photo");
  if (!(file instanceof File) || !file.type.startsWith("image/")) {
    return NextResponse.json({ error: "Upload an image" }, { status: 400 });
  }
  const asset = await client.assets.create({ asset: file, name: file.name });
  const run = await client.flows.templates.runs.create("Yz4DETxRv4uXyIo5PnEy", {
    versionId: "Kqs4nRrpndEjQ54BhbwE",
    inputs: { garment_photo: { type: "asset", assetId: asset.assetId } },
    webhook: { type: "all" },
  });
  const job = await db.jobs.insert({ userId, runId: run.id, status: "pending" });
  return NextResponse.json({ jobId: job.id }, { status: 202 });
}
```

```typescript
// app/api/webhooks/elevenlabs/route.ts
export const runtime = "nodejs";

export async function POST(req: Request) {
  const rawBody = await req.text(); // raw body; don't call req.json() first
  let event;
  try {
    event = await client.webhooks.constructEvent(rawBody, req.headers.get("elevenlabs-signature") ?? "", process.env.WEBHOOK_SECRET!);
  } catch {
    return new Response("invalid signature", { status: 401 });
  }
  if (event.type === "flows_template_run") {
    const claimed = await db.jobs.claimPending(event.data.id);
    if (claimed) await queue.enqueue("finish-packshot", { jobId: claimed.id, run: event.data });
  }
  return new Response(null, { status: 200 });
}
```

Server Actions work too (`"use server"` function receiving `FormData`); the same rule holds: the ElevenLabs call runs on the server. Serverless hosts cap request body size; for files larger than the host allows, upload from the browser straight to your own storage with a presigned URL, then have the server download it and call `assets.create`.

## Python (FastAPI) equivalents

```python
@app.post("/api/packshots")
async def create_packshot(photo: UploadFile, user=Depends(current_user)):
    asset = client.assets.create(asset=(photo.filename, await photo.read(), photo.content_type), name=photo.filename)
    run = client.flows.templates.runs.create(
        template_id=TEMPLATE_ID,
        version_id=VERSION_ID,
        inputs={"garment_photo": TemplateInputReference_Asset(asset_id=asset.asset_id)},
        webhook=WebhookTarget_All(),
    )
    job = jobs.insert(user_id=user.id, run_id=run.id, status="pending")
    return {"job_id": job.id}
```

The webhook handler is in [Webhook handlers](webhooks.md). Without a public URL, start the run with `create_and_wait` inside a background task (Celery, RQ, `BackgroundTasks`) and update the job when it returns.
