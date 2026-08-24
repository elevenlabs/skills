# Installation

The Dubbing Projects API is available via the `elevenlabs` CLI under `elevenlabs dubbing project`, in the official SDKs under `dubbing.project.*`, and via REST at `/v1/dubbing/project`. The older `client.dubbing.*` methods (`create`, `get`, `audio.get`) are the **legacy v1 dubbing API** — do not use them for new work.

## CLI (Recommended)

macOS / Linux (Homebrew):

```bash
brew install elevenlabs/tap/elevenlabs
```

Windows (Scoop):

```bash
scoop bucket add elevenlabs https://github.com/elevenlabs/scoop-bucket
scoop install elevenlabs
```

Shell installer:

```bash
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/elevenlabs/cli/releases/latest/download/elevenlabs-cli-installer.sh | sh
```

Authenticate with an API key (picked up automatically from the environment):

```bash
export ELEVENLABS_API_KEY="your-api-key"
```

Or log in via OAuth, which stores credentials in the OS keyring:

```bash
elevenlabs auth login
```

Verify it works:

```bash
elevenlabs dubbing project list
```

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

## CLI Usage

The REST base URL is `https://api.elevenlabs.io`, with your API key in the `xi-api-key` header on every request. For command-line use, prefer the CLI — it wraps the same endpoints and reads `ELEVENLABS_API_KEY` automatically:

```bash
elevenlabs dubbing project create --file promo.mp4 --source-language en
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
