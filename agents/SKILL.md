---
name: agents
description: Build voice AI agents with ElevenLabs. Use when creating voice assistants, customer service bots, interactive voice characters, or any real-time voice conversation experience.
license: MIT
compatibility: Requires internet access and an ElevenLabs API key (ELEVENLABS_API_KEY).
metadata: {"openclaw": {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "primaryEnv": "ELEVENLABS_API_KEY"}}
---

# ElevenLabs Agents Platform

Build voice AI agents with natural conversations, multiple LLM providers, custom tools, and easy web embedding.

> **Setup:** See [Installation Guide](references/installation.md) for CLI and SDK setup.

## Quick Start with CLI

The ElevenLabs CLI is the recommended way to create and manage agents:

```bash
# Install CLI and authenticate
npm install -g @elevenlabs/cli
elevenlabs auth login

# Initialize project and create an agent
elevenlabs agents init
elevenlabs agents add "My Assistant" --template complete

# Push to ElevenLabs platform
elevenlabs agents push
```

**Available templates:** `complete`, `minimal`, `voice-only`, `text-only`, `customer-service`, `assistant`

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

agent = client.conversational_ai.agents.create(
    name="My Assistant",
    conversation_config={
        "agent": {
            "first_message": "Hello! How can I help?",
            "language": "en",
            "prompt": {
                "prompt": "You are a helpful assistant. Be concise and friendly.",
                "llm": "gemini-2.0-flash",
                "temperature": 0.7
            }
        },
        "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb"}
    }
)
```

### JavaScript

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
const client = new ElevenLabsClient();

const agent = await client.conversationalAi.agents.create({
  name: "My Assistant",
  conversationConfig: {
    agent: {
      firstMessage: "Hello! How can I help?",
      language: "en",
      prompt: {
        prompt: "You are a helpful assistant.",
        llm: "gemini-2.0-flash",
        temperature: 0.7
      }
    },
    tts: { voiceId: "JBFqnCBsd6RMkjVDRZzb" }
  }
});
```

### cURL

```bash
curl -X POST "https://api.elevenlabs.io/v1/convai/agents/create" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"name": "My Assistant", "conversation_config": {"agent": {"first_message": "Hello!", "language": "en", "prompt": {"prompt": "You are helpful.", "llm": "gemini-2.0-flash"}}, "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb"}}}'
```

## Starting Conversations

**Server-side (Python):** Get signed URL for client connection:
```python
signed_url = client.conversational_ai.conversations.get_signed_url(agent_id="your-agent-id")
```

**Client-side (JavaScript):**
```javascript
import { Conversation } from "@elevenlabs/client";

const conversation = await Conversation.startSession({
  agentId: "your-agent-id",
  onMessage: (msg) => console.log("Agent:", msg.message),
  onUserTranscript: (t) => console.log("User:", t.message),
  onError: (e) => console.error(e)
});
```

**React Hook:**
```typescript
import { useConversation } from "@elevenlabs/react";

const conversation = useConversation({ onMessage: (msg) => console.log(msg) });
// Get signed URL from backend, then:
await conversation.startSession({ signedUrl: token });
```

## Configuration

| Provider | Models |
|----------|--------|
| OpenAI | `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`, `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` |
| Anthropic | `claude-sonnet-4-5`, `claude-sonnet-4`, `claude-haiku-4-5`, `claude-3-7-sonnet`, `claude-3-5-sonnet`, `claude-3-haiku` |
| Google | `gemini-3-pro-preview`, `gemini-3-flash-preview`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-2.0-flash`, `gemini-2.0-flash-lite` |
| ElevenLabs | `glm-45-air-fp8`, `qwen3-30b-a3b`, `gpt-oss-120b` |
| Custom | `custom-llm` (bring your own endpoint) |

**Popular voices:** `JBFqnCBsd6RMkjVDRZzb` (George), `EXAVITQu4vr4xnSDxMaL` (Sarah), `onwK4e9ZLuTAKqWW03F9` (Daniel), `XB0fDUnXU5powFXDhCwa` (Charlotte)

**Turn eagerness:** `patient` (waits longer for user to finish), `normal`, or `eager` (responds quickly)

See [Agent Configuration](references/agent-configuration.md) for all options.

## Tools

Extend agents with webhook, client, or built-in system tools. Tools are defined inside `conversation_config.agent.prompt`:

```python
"prompt": {
    "prompt": "You are a helpful assistant that can check the weather.",
    "llm": "gemini-2.0-flash",
    "tools": [
        # Webhook: server-side API call
        {"type": "webhook", "name": "get_weather", "description": "Get weather",
         "api_schema": {"url": "https://api.example.com/weather", "method": "POST",
             "request_body_schema": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}}},
        # Client: runs in the browser
        {"type": "client", "name": "show_product", "description": "Display a product",
         "parameters": {"type": "object", "properties": {"productId": {"type": "string"}}, "required": ["productId"]}}
    ],
    "built_in_tools": {
        "end_call": {},
        "transfer_to_number": {"transfers": [{"transfer_destination": {"type": "phone", "phone_number": "+1234567890"}, "condition": "User asks for human support"}]}
    }
}
```

**Client tools** run in browser:
```javascript
clientTools: {
  show_product: async ({ productId }) => {
    document.getElementById("product").src = `/products/${productId}`;
    return { success: true };
  }
}
```

See [Client Tools Reference](references/client-tools.md) for complete documentation.

## Widget Embedding

```html
<elevenlabs-convai agent-id="your-agent-id"></elevenlabs-convai>
<script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async type="text/javascript"></script>
```

Customize with attributes: `avatar-image-url`, `action-text`, `start-call-text`, `end-call-text`.

See [Widget Embedding Reference](references/widget-embedding.md) for all options.

## Outbound Calls

Make outbound phone calls using your agent via Twilio integration:

### Python

```python
response = client.conversational_ai.twilio.outbound_call(
    agent_id="your-agent-id",
    agent_phone_number_id="your-phone-number-id",
    to_number="+1234567890"
)
print(f"Call initiated: {response.conversation_id}")
```

### JavaScript

```javascript
const response = await client.conversationalAi.twilio.outboundCall({
  agentId: "your-agent-id",
  agentPhoneNumberId: "your-phone-number-id",
  toNumber: "+1234567890",
});
```

### cURL

```bash
curl -X POST "https://api.elevenlabs.io/v1/convai/twilio/outbound-call" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"agent_id": "your-agent-id", "agent_phone_number_id": "your-phone-number-id", "to_number": "+1234567890"}'
```

See [Outbound Calls Reference](references/outbound-calls.md) for configuration overrides and dynamic variables.

## Managing Agents

### Using CLI (Recommended)

```bash
# List agents and check status
elevenlabs agents list
elevenlabs agents status

# Import agents from platform to local config
elevenlabs agents pull                      # Import all agents
elevenlabs agents pull --agent <agent-id>   # Import specific agent

# Push local changes to platform
elevenlabs agents push              # Upload configurations
elevenlabs agents push --dry-run    # Preview changes first

# Add tools
elevenlabs tools add-webhook "Weather API"
elevenlabs tools add-client "UI Tool"
```

### Project Structure

The CLI creates a project structure for managing agents:

```
your_project/
├── agents.json       # Agent definitions
├── tools.json        # Tool configurations
├── tests.json        # Test configurations
├── agent_configs/    # Individual agent configs
├── tool_configs/     # Individual tool configs
└── test_configs/     # Individual test configs
```

### SDK Examples

```python
# List
agents = client.conversational_ai.agents.list()

# Get
agent = client.conversational_ai.agents.get(agent_id="your-agent-id")

# Update (partial - only include fields to change)
client.conversational_ai.agents.update(agent_id="your-agent-id", name="New Name")
client.conversational_ai.agents.update(agent_id="your-agent-id",
    conversation_config={
        "agent": {"prompt": {"prompt": "New instructions", "llm": "claude-sonnet-4"}}
    })

# Delete
client.conversational_ai.agents.delete(agent_id="your-agent-id")
```

See [Agent Configuration](references/agent-configuration.md) for all configuration options and SDK examples.

## Error Handling

```python
try:
    agent = client.conversational_ai.agents.create(...)
except Exception as e:
    print(f"API error: {e}")
```

Common errors: **401** (invalid key), **404** (not found), **422** (invalid config), **429** (rate limit)

## References

- [Installation Guide](references/installation.md) - SDK setup and migration
- [Agent Configuration](references/agent-configuration.md) - All config options and CRUD examples
- [Client Tools](references/client-tools.md) - Webhook, client, and system tools
- [Widget Embedding](references/widget-embedding.md) - Website integration
- [Outbound Calls](references/outbound-calls.md) - Twilio phone call integration
