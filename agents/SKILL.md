---
name: agents
description: Build conversational voice AI agents with ElevenLabs. Use when creating voice assistants, customer service bots, interactive voice characters, or any real-time voice conversation experience.
---

# ElevenLabs Conversational AI

Build voice AI agents with natural conversations, multiple LLM providers, custom tools, and easy web embedding.

> **Setup:** See [Installation Guide](references/installation.md). For JavaScript, use `@elevenlabs/*` packages only.

## Quick Start

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

agent = client.conversational_ai.agents.create(
    name="My Assistant",
    conversation_config={
        "agent": {"first_message": "Hello! How can I help?", "language": "en"},
        "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb"}
    },
    prompt={
        "prompt": "You are a helpful assistant. Be concise and friendly.",
        "llm": "gpt-4o-mini",
        "temperature": 0.7
    }
)
```

<details>
<summary>JavaScript / cURL examples</summary>

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
const client = new ElevenLabsClient();

const agent = await client.conversationalAi.agents.create({
  name: "My Assistant",
  conversationConfig: {
    agent: { firstMessage: "Hello! How can I help?", language: "en" },
    tts: { voiceId: "JBFqnCBsd6RMkjVDRZzb" }
  },
  prompt: { prompt: "You are a helpful assistant.", llm: "gpt-4o-mini", temperature: 0.7 }
});
```

```bash
curl -X POST "https://api.elevenlabs.io/v1/convai/agents/create" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"name": "My Assistant", "conversation_config": {"agent": {"first_message": "Hello!", "language": "en"}, "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb"}}, "prompt": {"prompt": "You are helpful.", "llm": "gpt-4o-mini"}}'
```
</details>

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
| OpenAI | `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` |
| Anthropic | `claude-3-5-sonnet`, `claude-3-5-haiku` |
| Google | `gemini-1.5-pro`, `gemini-1.5-flash` |
| Custom | `custom-llm` (bring your own endpoint) |

**Popular voices:** `JBFqnCBsd6RMkjVDRZzb` (George), `EXAVITQu4vr4xnSDxMaL` (Sarah), `onwK4e9ZLuTAKqWW03F9` (Daniel), `XB0fDUnXU5powFXDhCwa` (Charlotte)

**Turn-taking modes:** `server_vad` (auto-detect speech end) or `turn_based` (explicit signals)

See [Agent Configuration](references/agent-configuration.md) for all options.

## Tools

Extend agents with webhook, client, or system tools:

```python
tools=[
    # Webhook: server-side API call
    {"type": "webhook", "name": "get_weather", "description": "Get weather",
     "webhook": {"url": "https://api.example.com/weather", "method": "POST"},
     "parameters": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}},
    # System: built-in capabilities
    {"type": "system", "name": "end_call"},
    {"type": "system", "name": "transfer_to_number", "phone_number": "+1234567890"}
]
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
<script src="https://elevenlabs.io/convai-widget/index.js" async></script>
<elevenlabs-convai agent-id="your-agent-id"></elevenlabs-convai>
```

Customize with attributes: `avatar-image-url`, `action-text`, `start-call-text`, `end-call-text`.

See [Widget Embedding Reference](references/widget-embedding.md) for all options.

## Managing Agents

```python
# List
agents = client.conversational_ai.agents.list()

# Get
agent = client.conversational_ai.agents.get(agent_id="your-agent-id")

# Update (partial - only include fields to change)
client.conversational_ai.agents.update(agent_id="your-agent-id", name="New Name")
client.conversational_ai.agents.update(agent_id="your-agent-id",
    prompt={"prompt": "New instructions", "llm": "claude-3-5-sonnet"})

# Delete
client.conversational_ai.agents.delete(agent_id="your-agent-id")
```

See [Agent Configuration](references/agent-configuration.md) for update examples in JavaScript/cURL and all updatable fields.

## Error Handling

```python
from elevenlabs import ElevenLabsError
try:
    agent = client.conversational_ai.agents.create(...)
except ElevenLabsError as e:
    print(f"API error: {e.message}")
```

Common errors: **401** (invalid key), **404** (not found), **422** (invalid config), **429** (rate limit)

## References

- [Installation Guide](references/installation.md) - SDK setup and migration
- [Agent Configuration](references/agent-configuration.md) - All config options and CRUD examples
- [Client Tools](references/client-tools.md) - Webhook, client, and system tools
- [Widget Embedding](references/widget-embedding.md) - Website integration
