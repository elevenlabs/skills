# Installation

The Templates API is available in the official SDKs under `flows.templates.*`, via the `elevenlabs` CLI under `elevenlabs flows templates`, and via REST at `/v1/flows/templates`.

## Requirements

- A workspace on a **Pro plan or above**.
- An API key with the **Image & Video** permission.
- For webhooks: the **Webhooks Manage** permission (or workspace admin) to create and subscribe the webhook.
- The template must be shared with your workspace (or be public, or shared with you by link). A template shared as **Just me** only runs for its author.

## Python

```bash
pip install --upgrade elevenlabs requests
```

`create_and_wait` is only in recent SDK releases. If `client.flows.templates.runs.create_and_wait` doesn't exist, upgrade, or [poll by hand](polling.md).

```python
import os
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

templates = client.flows.templates.list(page_size=10)
```

## JavaScript / TypeScript

```bash
npm install @elevenlabs/elevenlabs-js@latest
```

> **Important:** Always use `@elevenlabs/elevenlabs-js`. The old `elevenlabs` npm package (v1.x) is deprecated and should not be used.

`createAndWait` is only in recent SDK releases. If `client.flows.templates.runs.createAndWait` doesn't exist, upgrade, or [poll by hand](polling.md).

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

// Reads ELEVENLABS_API_KEY from the environment
const client = new ElevenLabsClient();

const templates = await client.flows.templates.list({ pageSize: 10 });
```

## CLI

```bash
npm install -g @elevenlabs/cli
# or: brew install elevenlabs/tap/elevenlabs
```

```bash
elevenlabs flows templates list --search packshot
elevenlabs flows templates get --template-id Yz4DETxRv4uXyIo5PnEy
elevenlabs flows templates runs create-and-wait --template-id Yz4DETxRv4uXyIo5PnEy \
  --inputs '{"garment_photo": {"type": "asset", "asset_id": "YOUR_ASSET_ID"}}'
elevenlabs flows templates runs get --template-id Yz4DETxRv4uXyIo5PnEy --run-id RUN_ID
```

`create-and-wait` is only in recent CLI releases. If `elevenlabs flows templates runs create-and-wait --help` reports an unrecognized subcommand, upgrade the CLI, or use the cURL loop in [Polling by hand](polling.md).

## Getting an API Key

1. Sign up at [elevenlabs.io](https://elevenlabs.io)
2. Go to [API Keys](https://elevenlabs.io/app/settings/api-keys)
3. Click **Create API Key** and give it the **Image & Video** permission
4. Copy and store securely

Or use the `setup-api-key` skill for guided setup.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ELEVENLABS_API_KEY` | Your ElevenLabs API key (required) |
| `WEBHOOK_SECRET` | The webhook's signing secret, returned when the webhook is created (webhook handlers only) |
