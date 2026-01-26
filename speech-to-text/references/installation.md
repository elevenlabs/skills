# Installation

## Python

```bash
pip install elevenlabs
```

Configure your API key:

```python
from elevenlabs import ElevenLabs

# Option 1: Pass directly
client = ElevenLabs(api_key="your-api-key")

# Option 2: Environment variable (recommended)
# Set ELEVENLABS_API_KEY in your environment
client = ElevenLabs()  # Automatically reads ELEVENLABS_API_KEY
```

## JavaScript / TypeScript

```bash
npm install @elevenlabs/elevenlabs-js
```

Configure your API key:

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

// Option 1: Pass directly
const client = new ElevenLabsClient({ apiKey: "your-api-key" });

// Option 2: Environment variable (recommended)
// Set ELEVENLABS_API_KEY in your environment
const client = new ElevenLabsClient();
```

## cURL / REST API

Set your API key as an environment variable:

```bash
export ELEVENLABS_API_KEY="your-api-key"
```

Include in requests:

```bash
curl -X POST "https://api.elevenlabs.io/v1/speech-to-text" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "file=@audio.mp3" \
  -F "model_id=scribe_v2"
```

## Getting an API Key

1. Sign up at [elevenlabs.io](https://elevenlabs.io)
2. Go to **Settings** → **API Keys**
3. Click **Create API Key**
4. Copy and store securely

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ELEVENLABS_API_KEY` | Your ElevenLabs API key (required) |
