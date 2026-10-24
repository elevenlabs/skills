# Installation

The Flows API is available in the official SDKs under `flows.image`, `flows.video`, `flows.text_to_speech` (`flows.textToSpeech` in TypeScript), `flows.templates` and `assets`; via the `elevenlabs` CLI under `elevenlabs flows ...` and `elevenlabs assets ...`; and via REST at `/v1/flows/...` and `/v1/assets`.

## Requirements

- A workspace on a **Pro plan or above**.
- An API key with the **Image & Video** permission (plus **Text to Speech** for `/v1/flows/text-to-speech`).
- For webhooks: the **Webhooks Manage** permission (or workspace admin) to create and subscribe the webhook.
- For templates: the template must be shared with your workspace (or be public, or shared with you by link). A template shared as **Just me** only runs for its author. See [Access and errors](access-errors.md).

## Python

```bash
pip install --upgrade elevenlabs requests
```

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

## Getting an API Key

1. Sign up at [elevenlabs.io](https://elevenlabs.io)
2. Go to [API Keys](https://elevenlabs.io/app/settings/api-keys)
3. Click **Create API Key** and give it the **Image & Video** permission (and **Text to Speech** if you generate speech)
4. Copy and store securely

Or use the `setup-api-key` skill for guided setup.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ELEVENLABS_API_KEY` | Your ElevenLabs API key (required) |
| `WEBHOOK_SECRET` | The webhook's signing secret, returned when the webhook is created (webhook handlers only) |
