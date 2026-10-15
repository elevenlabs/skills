# Polling by hand

Prefer the SDK's `create_and_wait` / `createAndWait`, which does all of this for you. Write your own loop only when the helper isn't available (another language, an older SDK, a shell script). In production, use a webhook instead.

These loops call the REST API directly because they need the `Retry-After` response header, which the `elevenlabs` CLI doesn't expose. For a one-off check from the terminal, use `elevenlabs flows templates runs get` instead.

## Rules

1. **Sleep for `Retry-After`.** The create response and every unfinished `GET /v1/flows/templates/{template_id}/runs/{run_id}` carry a `Retry-After` header: the number of seconds the server suggests waiting before the next check. It is derived from how long the template's models usually take. Finished (`completed`/`failed`) responses don't carry it.
2. **Fall back to a few seconds** if the header is missing, unparseable or `0` (3s is the SDK helpers' default).
3. **Add a little jitter** (0–20%) so many runs don't check in lockstep.
4. **Handle `429`.** Status checks are rate-limited per API key. A `429` carries its own `Retry-After`; wait that long and retry.
5. **Stop on `completed` or `failed`.** A `failed` run is a normal result: read each output's `failure_reason` and `error_message`.
6. **Set a deadline** for unattended jobs, and keep the run `id` so you can resume checking later.

Never use a fixed tight interval (e.g. every 1s) or poll in parallel for the same run.

## Python

```python
import os
import random
import time

import requests

API = "https://api.elevenlabs.io/v1/flows/templates"
HEADERS = {"xi-api-key": os.environ["ELEVENLABS_API_KEY"]}
TERMINAL = {"completed", "failed"}


def retry_after(response: requests.Response, default: float = 3.0) -> float:
    try:
        seconds = float(response.headers.get("Retry-After", ""))
    except ValueError:
        seconds = 0
    return max(seconds, default) * (1 + random.random() * 0.2)


def run_and_wait(template_id: str, body: dict, timeout: float = 600) -> dict:
    response = requests.post(f"{API}/{template_id}/runs", headers=HEADERS, json=body)
    response.raise_for_status()
    run = response.json()
    deadline = time.monotonic() + timeout

    while run["status"] not in TERMINAL:
        if time.monotonic() > deadline:
            raise TimeoutError(f"run {run['id']} still {run['status']}")
        time.sleep(retry_after(response))
        response = requests.get(f"{API}/{template_id}/runs/{run['id']}", headers=HEADERS)
        if response.status_code == 429:
            continue  # retry_after() reads the 429's Retry-After on the next loop
        response.raise_for_status()
        run = response.json()

    return run


run = run_and_wait(
    "Yz4DETxRv4uXyIo5PnEy",
    {
        "version_id": "Kqs4nRrpndEjQ54BhbwE",
        "inputs": {"garment_photo": {"type": "asset", "asset_id": "YOUR_ASSET_ID"}},
    },
)
for output_id, output in run["outputs"].items():
    if output["status"] == "completed":
        print(output_id, output.get("content_url") or output.get("content"))
    else:
        print(output_id, "failed:", output["failure_reason"], output["error_message"])
```

## TypeScript

```typescript
const API = "https://api.elevenlabs.io/v1/flows/templates";
const headers = { "xi-api-key": process.env.ELEVENLABS_API_KEY!, "Content-Type": "application/json" };

function retryAfterMs(response: Response, defaultSeconds = 3): number {
  const seconds = Number(response.headers.get("Retry-After"));
  const base = Number.isFinite(seconds) && seconds > 0 ? Math.max(seconds, defaultSeconds) : defaultSeconds;
  return base * 1000 * (1 + Math.random() * 0.2);
}

async function runAndWait(templateId: string, body: unknown, timeoutMs = 600_000) {
  let response = await fetch(`${API}/${templateId}/runs`, { method: "POST", headers, body: JSON.stringify(body) });
  if (!response.ok) throw new Error(`${response.status} ${await response.text()}`);
  let run = await response.json();
  const deadline = Date.now() + timeoutMs;

  while (run.status !== "completed" && run.status !== "failed") {
    if (Date.now() > deadline) throw new Error(`run ${run.id} still ${run.status}`);
    await new Promise((resolve) => setTimeout(resolve, retryAfterMs(response)));
    response = await fetch(`${API}/${templateId}/runs/${run.id}`, { headers });
    if (response.status === 429) continue;
    if (!response.ok) throw new Error(`${response.status} ${await response.text()}`);
    run = await response.json();
  }
  return run; // raw JSON: snake_case fields
}
```

## Shell

The `elevenlabs` CLI can't read `Retry-After`, so a shell loop uses cURL.

```bash
TEMPLATE_ID=Yz4DETxRv4uXyIo5PnEy
RUN_ID=$(curl -s -X POST "https://api.elevenlabs.io/v1/flows/templates/$TEMPLATE_ID/runs" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"inputs": {"garment_photo": {"type": "asset", "asset_id": "YOUR_ASSET_ID"}}}' | jq -r .id)

while :; do
  RESPONSE=$(curl -s -D /tmp/headers "https://api.elevenlabs.io/v1/flows/templates/$TEMPLATE_ID/runs/$RUN_ID" \
    -H "xi-api-key: $ELEVENLABS_API_KEY")
  STATUS=$(echo "$RESPONSE" | jq -r .status)
  [ "$STATUS" = completed ] || [ "$STATUS" = failed ] && break
  WAIT=$(grep -i '^retry-after:' /tmp/headers | tr -dc '0-9')
  sleep "${WAIT:-3}"
done
echo "$RESPONSE" | jq .outputs
```

## Resuming

A run keeps going server-side whether or not anyone is checking. If a script exits early, resume with `GET .../runs/{run_id}`, or find recent runs with `flows.templates.runs.list(template_id)` (newest first, filterable by `version_id`). A `completed` output's `content_url` expires about an hour after the response; fetch the run again for a fresh one.
