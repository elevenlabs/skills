# Installation

The Dubbing Projects API is available in the official SDKs under `dubbing.project.*` and via REST at `/v1/dubbing/project`. The older `client.dubbing.*` methods (`create`, `get`, `audio.get`) are the **legacy v1 dubbing API** — do not use them for new work.

## Python

```bash
pip install --upgrade elevenlabs requests
```

(`requests` is used to download the dubbed audio from the signed output URL.)

```python
import os
from elevenlabs.client import ElevenLabs

# Reads ELEVENLABS_API_KEY from the environment
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

page = elevenlabs.dubbing.project.list(page_size=20)
```

## JavaScript / TypeScript

```bash
npm install @elevenlabs/elevenlabs-js@latest
```

> **Important:** Always use `@elevenlabs/elevenlabs-js`. The old `elevenlabs` npm package (v1.x) is deprecated and should not be used.

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

// Reads ELEVENLABS_API_KEY from the environment
const elevenlabs = new ElevenLabsClient();

const page = await elevenlabs.dubbing.project.list({ pageSize: 20 });
```

## cURL / REST API

Set your API key as an environment variable:

```bash
export ELEVENLABS_API_KEY="your-api-key"
```

Include it in every request via the `xi-api-key` header:

```bash
curl -X POST "https://api.elevenlabs.io/v1/dubbing/project" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "file=@promo.mp4" \
  -F "source_language=en"
```

## Getting an API Key

1. Sign up at [elevenlabs.io](https://elevenlabs.io)
2. Go to [API Keys](https://elevenlabs.io/app/settings/api-keys)
3. Click **Create API Key**
4. Copy and store securely

Or use the `setup-api-key` skill for guided setup.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ELEVENLABS_API_KEY` | Your ElevenLabs API key (required) |
