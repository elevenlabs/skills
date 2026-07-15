# Installation

The Dubbing Projects API is prerelease and REST-only for now — call the HTTP endpoints directly rather than using SDK helper methods. (The SDK's existing `client.dubbing` methods target the older v1 `/v1/dubbing` API, not `/v1/dubbing/project`.)

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

## Python

Use `requests` (or `httpx`) against the REST API:

```bash
pip install requests
```

```python
import os
import requests

HEADERS = {"xi-api-key": os.environ["ELEVENLABS_API_KEY"]}
resp = requests.get("https://api.elevenlabs.io/v1/dubbing/project", headers=HEADERS)
```

## JavaScript / TypeScript

Use the built-in `fetch` (Node 18+):

```javascript
const resp = await fetch("https://api.elevenlabs.io/v1/dubbing/project", {
  headers: { "xi-api-key": process.env.ELEVENLABS_API_KEY },
});
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

## Workspace Gating

These endpoints are gated per workspace during the prerelease. If a call returns a "feature not available" error, the workspace hasn't been enabled for the Dubbing Projects API yet.
