# Installation

## JavaScript / TypeScript

```bash
npm install @elevenlabs/elevenlabs-js
```

> **Important:** Always use `@elevenlabs/elevenlabs-js`. The old `elevenlabs` npm package (v1.x) is deprecated and should not be used.

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

// Option 1: Environment variable (recommended)
// Set ELEVENLABS_API_KEY in your environment
const client = new ElevenLabsClient();

// Option 2: Pass directly
const client = new ElevenLabsClient({ apiKey: "your-api-key" });
```

### Migrating from deprecated packages

If you have old packages installed, remove them:

```bash
# Remove deprecated packages
npm uninstall elevenlabs

# Install the current packages
npm install @elevenlabs/elevenlabs-js
```

**Import changes:**
```javascript
// OLD (deprecated)
import { ElevenLabsClient } from "elevenlabs";

// NEW (current)
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
```

## Python

```bash
pip install elevenlabs
```

```python
from elevenlabs import ElevenLabs

# Option 1: Environment variable (recommended)
# Set ELEVENLABS_API_KEY in your environment
client = ElevenLabs()

# Option 2: Pass directly
client = ElevenLabs(api_key="your-api-key")
```

## cURL / REST API

Set your API key as an environment variable:

```bash
export ELEVENLABS_API_KEY="your-api-key"
```

Include in requests via the `xi-api-key` header:

```bash
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "model_id": "eleven_multilingual_v2"}'
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
