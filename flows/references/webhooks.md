# Webhook handlers

Complete servers that receive `flows_template_run` events (template runs). Single generations and chains deliver `flows_generation` events to the same webhooks; their `data` is the terminal generation (`id`, `status`, `content_url`, `content_mime_type`, or `failure_reason` / `error_message`). Before these work, a workspace webhook pointing at the server must be subscribed to the `flows` event (see [Flows templates](templates.md), "Subscribe a webhook to template runs"), and runs or generations must be started with `webhook: {"type": "all"}` or a list of webhook ids.

Every handler:

1. Reads the **raw** request body — signature verification runs over the exact bytes sent, so don't parse JSON first.
2. Verifies the `ElevenLabs-Signature` header with `construct_event` / `constructEvent` and the webhook's signing secret; rejects with 401 on failure.
3. Branches on the event type: `flows_template_run` or `flows_generation`; anything else gets a 2xx and is ignored.
4. Deduplicates on `data.id` (the run or generation id).
5. Returns 2xx immediately and does slow work (downloads) in the background.

## Python (FastAPI)

```bash
pip install --upgrade elevenlabs fastapi uvicorn requests
```

```python
# server.py
import os

import requests
from elevenlabs import ElevenLabs, TemplateRunResponse
from elevenlabs.errors import BadRequestError
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()
client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
seen_runs: set[str] = set()  # run and generation ids; use your database in production


def save_outputs(run: TemplateRunResponse) -> None:
    for output_id, output in run.outputs.items():
        if output.status == "failed":
            print(f"{run.id} {output_id} failed: {output.failure_reason} {output.error_message}")
        elif output.type in ("image", "video", "audio") and output.content_url:
            # content_url expires about an hour after the event; download promptly.
            media = requests.get(output.content_url).content
            with open(f"{run.id}-{output_id}", "wb") as f:
                f.write(media)
        elif output.type == "string":
            print(f"{run.id} {output_id}: {output.content}")


def save_generation(generation: dict) -> None:
    if generation["status"] == "completed":
        with open(generation["id"], "wb") as f:
            f.write(requests.get(generation["content_url"]).content)
    else:
        print(f"{generation['id']} failed: {generation['failure_reason']} {generation['error_message']}")


@app.post("/webhooks/elevenlabs")
async def receive(request: Request, background: BackgroundTasks):
    try:
        event = client.webhooks.construct_event(
            rawBody=(await request.body()).decode("utf-8"),
            sig_header=request.headers.get("elevenlabs-signature"),
            secret=WEBHOOK_SECRET,
        )
    except BadRequestError:
        return JSONResponse({"error": "invalid signature"}, status_code=401)

    # construct_event returns the parsed JSON as a dict.
    if event["type"] == "flows_generation":
        generation = event["data"]  # id, status, content_url | failure_reason
        if generation["id"] not in seen_runs:
            seen_runs.add(generation["id"])
            background.add_task(save_generation, generation)
        return {"status": "received"}
    if event["type"] != "flows_template_run":
        return {"status": "ignored"}

    run = TemplateRunResponse.model_validate(event["data"])
    if run.id in seen_runs:
        return {"status": "duplicate"}
    seen_runs.add(run.id)

    background.add_task(save_outputs, run)
    return {"status": "received"}
```

```bash
uvicorn server:app --port 3000
```

## TypeScript (Express)

```bash
npm install @elevenlabs/elevenlabs-js express
```

```typescript
// server.mts
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import express from "express";
import { writeFile } from "fs/promises";

const client = new ElevenLabsClient();
const app = express();
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET!;
const seenRuns = new Set<string>(); // use your database in production

async function saveOutputs(run: any) {
  // constructEvent returns the JSON as sent, so fields are snake_case.
  for (const [outputId, output] of Object.entries<any>(run.outputs)) {
    if (output.status === "failed") {
      console.error(run.id, outputId, "failed:", output.failure_reason, output.error_message);
    } else if (["image", "video", "audio"].includes(output.type) && output.content_url) {
      const response = await fetch(output.content_url);
      await writeFile(`${run.id}-${outputId}`, Buffer.from(await response.arrayBuffer()));
    } else if (output.type === "string") {
      console.log(run.id, outputId, output.content);
    }
  }
}

// express.raw keeps the exact bytes for signature verification.
app.post("/webhooks/elevenlabs", express.raw({ type: "application/json" }), async (req, res) => {
  let event;
  try {
    event = await client.webhooks.constructEvent(
      req.body.toString(),
      req.headers["elevenlabs-signature"] as string,
      WEBHOOK_SECRET,
    );
  } catch {
    return res.status(401).json({ error: "invalid signature" });
  }

  if (event.type === "flows_generation") {
    const generation = event.data; // id, status, content_url | failure_reason
    if (seenRuns.has(generation.id)) return res.status(200).json({ status: "duplicate" });
    seenRuns.add(generation.id);
    res.status(200).json({ status: "received" });
    if (generation.status === "completed") {
      fetch(generation.content_url)
        .then(async (r) => writeFile(generation.id, Buffer.from(await r.arrayBuffer())))
        .catch(console.error);
    } else {
      console.error(generation.id, "failed:", generation.failure_reason, generation.error_message);
    }
    return;
  }
  if (event.type !== "flows_template_run") return res.status(200).json({ status: "ignored" });

  const run = event.data;
  if (seenRuns.has(run.id)) return res.status(200).json({ status: "duplicate" });
  seenRuns.add(run.id);

  res.status(200).json({ status: "received" });
  saveOutputs(run).catch(console.error); // after responding
});

app.listen(3000);
```

## Local development

The webhook URL must be public HTTPS. To receive events on a local server, expose it with a tunnel and register the tunnel's HTTPS URL as the webhook's callback URL. If that's too much setup for a quick test, use `create_and_wait` instead and switch to the webhook when deploying.

## Missed events

Delivery is independent of the run: if your endpoint is down, the run still finishes and stays readable from `GET /v1/flows/templates/{template_id}/runs/{run_id}`. For workflows where a missed result is unacceptable, periodically list recent runs with `flows.templates.runs.list(template_id)` and process any finished ones you haven't seen.
