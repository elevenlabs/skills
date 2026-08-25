# Installation

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

Authenticate either way:

```bash
# Option 1: Environment variable (picked up automatically)
export ELEVENLABS_API_KEY="your-api-key"

# Option 2: OAuth login (stores credentials in the OS keyring)
elevenlabs auth login
```

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

Once the CLI is installed and authenticated, generate music directly from the terminal:

```bash
elevenlabs music compose \
  --prompt "A chill lo-fi beat" \
  --music-length-ms 30000 \
  --output output.mp3
```

## Getting an API Key

1. Sign up at [elevenlabs.io](https://elevenlabs.io)
2. Go to [API Keys](https://elevenlabs.io/app/settings/api-keys)
3. Click **Create API Key**
4. Copy and store securely

Or use the `setup-api-key` skill for guided setup.

**Note:** Music generation requires a paid ElevenLabs plan.
