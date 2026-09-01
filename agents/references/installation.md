# Installation

## CLI (Recommended)

The ElevenLabs CLI is the recommended way to create and manage agents:

```bash
# npm (any platform with Node.js)
npm install -g @elevenlabs/cli
```

```bash
# macOS / Linux (Homebrew)
brew install elevenlabs/tap/elevenlabs
```

```powershell
# Windows (Scoop)
scoop bucket add elevenlabs https://github.com/elevenlabs/scoop-bucket
scoop install elevenlabs
```

```bash
# Shell installer (any platform)
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/elevenlabs/cli/releases/latest/download/elevenlabs-cli-installer.sh | sh
```

### Authentication

Set `ELEVENLABS_API_KEY` in your environment — the CLI picks it up automatically:

```bash
export ELEVENLABS_API_KEY="your-api-key"
```

Or authenticate with OAuth, which stores credentials in the OS keyring:

```bash
elevenlabs auth login          # Authenticate with OAuth
elevenlabs auth whoami         # Verify current login status
elevenlabs auth logout         # Remove stored credentials
```

### Quick Start

```bash
# Initialize a new project
elevenlabs agents init

# Create an agent from template
elevenlabs agents add "My Assistant" --template default

# Push to ElevenLabs platform
elevenlabs agents push
```

## JavaScript / TypeScript SDK

For programmatic access and client-side integration:

```bash
npm install @elevenlabs/elevenlabs-js@latest
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
npm install @elevenlabs/elevenlabs-js@latest

# For browser apps, install the package that matches your UI layer:
npm install @elevenlabs/client@latest  # Vanilla JavaScript in the browser
npm install @elevenlabs/react@latest   # React on the web
```

**Import changes:**
```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { Conversation } from "@elevenlabs/client";
import {
  ConversationProvider,
  useConversationControls,
  useConversationStatus,
} from "@elevenlabs/react";
```

`@elevenlabs/react` re-exports `@elevenlabs/client`, so React apps usually only need
`@elevenlabs/react`. Wrap hook consumers in `ConversationProvider` and prefer granular hooks
such as `useConversationControls` and `useConversationStatus`; `useConversation` remains
available as the convenience all-in-one hook.

Use `@elevenlabs/react-native` for React Native projects with the same provider-and-hooks API;
only the import path changes.

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

## CLI Usage

Every REST endpoint is available as a CLI subcommand. Set your API key as an environment variable and the CLI picks it up automatically — no headers or key flags needed:

```bash
export ELEVENLABS_API_KEY="your-api-key"

elevenlabs agents create \
  --json '{"name": "My Agent", "conversation_config": {"agent": {"prompt": {"prompt": "You are helpful.", "llm": "gemini-2.0-flash"}}, "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb"}}}'
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
