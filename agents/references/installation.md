# Installation

## CLI (Recommended)

The ElevenLabs CLI is the recommended way to create and manage agents:

```bash
npm install -g @elevenlabs/cli
# or
pnpm add -g @elevenlabs/cli
# or
yarn global add @elevenlabs/cli
```

Requires Node.js 16.0.0 or higher.

### Authentication

```bash
elevenlabs auth login          # Authenticate with API key
elevenlabs auth whoami         # Verify current login status
elevenlabs auth logout         # Remove stored credentials
```

API keys are securely stored in `~/.agents/api_keys.json`.

### Quick Start

```bash
# Initialize a new project
elevenlabs agents init

# Create an agent from template
elevenlabs agents add "My Assistant" --template complete

# Push to ElevenLabs platform
elevenlabs agents push
```

## JavaScript / TypeScript SDK

For programmatic access and client-side integration:

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

# For client-side/browser usage, also install:
npm install @elevenlabs/client  # Browser client
npm install @elevenlabs/react   # React hooks
```

**Import changes:**
```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { Conversation } from "@elevenlabs/client";
import { useConversation } from "@elevenlabs/react";
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
curl -X POST "https://api.elevenlabs.io/v1/convai/agents/create" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Agent", "conversation_config": {"agent": {"prompt": {"prompt": "You are helpful.", "llm": "gemini-2.0-flash"}}, "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb"}}}'
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
