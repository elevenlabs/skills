# Polling by hand

This page is for code that calls the REST API directly: a language without an official SDK (Go, Ruby, PHP, Java, Rust, ...), or an existing hand-written loop that needs fixing. Everyone else has a helper that already does all of this:

- Python: `create_and_wait`. TypeScript: `createAndWait`.
- Shell: `elevenlabs flows templates runs create-and-wait` (or `elevenlabs flows <modality> create-and-wait`). It follows `Retry-After`, exits `1` on a `failed` run, and prints only the finished run on stdout.

If you're fixing a hand-written loop in Python or TypeScript, replace it with the helper rather than patching it. In production, use a webhook instead of waiting at all.

## The contract

| | Template run | Single generation |
|---|---|---|
| Start | `POST /v1/flows/templates/{template_id}/runs` | `POST /v1/flows/{image\|video\|text-to-speech}` |
| Check | `GET /v1/flows/templates/{template_id}/runs/{run_id}` | `GET /v1/flows/{image\|video\|text-to-speech}/{generation_id}` |
| Done when | `status` is `completed` or `failed` | `status` is `completed` or `failed` |
| Result | `outputs.{output_id}`: `status`, `content_url` or `content`, `failure_reason`, `error_message` | top level: `content_url`, `failure_reason` |

Authenticate with the `xi-api-key` header. Responses are snake_case JSON.

## Rules

1. **Sleep for `Retry-After`.** The create response and every unfinished check carry a `Retry-After` header: the number of seconds the server suggests waiting before the next check. It is derived from how long the models usually take. Finished (`completed`/`failed`) responses don't carry it.
2. **Fall back to a few seconds** if the header is missing, unparseable or `0` (3s is the SDK helpers' default).
3. **Add a little jitter** (0–20%) so many runs don't check in lockstep.
4. **Handle `429`.** Status checks are rate-limited per API key. A `429` carries its own `Retry-After`; wait that long and retry.
5. **Stop on `completed` or `failed`.** A `failed` run is a normal result, not an error: read each output's `failure_reason` and `error_message`.
6. **Set a deadline** for unattended jobs, and keep the run `id` so you can resume checking later.

Never use a fixed tight interval (e.g. every 1s) or poll in parallel for the same run.

## Reference loop

In cURL, as a spec to port to your language:

```bash
TEMPLATE_ID=Yz4DETxRv4uXyIo5PnEy
API="https://api.elevenlabs.io/v1/flows/templates/$TEMPLATE_ID/runs"
HEADERS=$(mktemp)

RUN_ID=$(curl -s -D "$HEADERS" -X POST "$API" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"version_id": "Kqs4nRrpndEjQ54BhbwE", "inputs": {"garment_photo": {"type": "asset", "asset_id": "YOUR_ASSET_ID"}}}' \
  | jq -r .id)
DEADLINE=$(( $(date +%s) + 600 ))

while :; do
  # Rules 1-3: sleep for the last response's Retry-After (the create, a check, or a 429), else 3s, plus jitter
  WAIT=$(grep -i '^retry-after:' "$HEADERS" | tr -dc '0-9')
  [ "${WAIT:-0}" -gt 0 ] || WAIT=3
  sleep "$(awk -v w="$WAIT" 'BEGIN { srand(); print w * (1 + rand() * 0.2) }')"

  CODE=$(curl -s -D "$HEADERS" -o run.json -w '%{http_code}' "$API/$RUN_ID" -H "xi-api-key: $ELEVENLABS_API_KEY")
  [ "$CODE" = 429 ] && continue                          # rule 4
  [ "$CODE" = 200 ] || { cat run.json; exit 1; }

  STATUS=$(jq -r .status run.json)
  [ "$STATUS" = completed ] || [ "$STATUS" = failed ] && break  # rule 5
  [ "$(date +%s)" -lt "$DEADLINE" ] || { echo "run $RUN_ID still $STATUS" >&2; exit 2; }  # rule 6
done

jq '.outputs | to_entries[] | {id: .key, status: .value.status, url: .value.content_url, failure: .value.failure_reason}' run.json
```

## Resuming

A run keeps going server-side whether or not anyone is checking. If a script exits early, resume with `GET .../runs/{run_id}` (`elevenlabs flows templates runs get` from a shell; a `create-and-wait` timeout prints this command for you), or find recent runs with `GET /v1/flows/templates/{template_id}/runs` (newest first, filterable by `version_id`). A `completed` output's `content_url` expires about an hour after the response; fetch the run again for a fresh one.
