---
name: agents
description: Build conversational voice AI agents with ElevenLabs. Use when creating voice assistants, customer service bots, interactive voice characters, or any real-time voice conversation experience.
---

# ElevenLabs Conversational AI

Build voice AI agents that can have natural conversations - supports multiple LLM providers, custom tools, and easy web embedding. Create customer service bots, voice assistants, interactive characters, and more.

> **Before you start:** See [Installation Guide](references/installation.md) for SDK setup. For JavaScript, always use the `@elevenlabs/*` packages - never `npm install elevenlabs` (outdated) or `@11labs/*` (deprecated).

## Quick Start

### Python

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

agent = client.conversational_ai.agents.create(
    name="My Assistant",
    conversation_config={
        "agent": {
            "first_message": "Hello! How can I help you today?",
            "language": "en"
        },
        "tts": {
            "voice_id": "JBFqnCBsd6RMkjVDRZzb"
        }
    },
    prompt={
        "prompt": "You are a helpful assistant. Be concise and friendly.",
        "llm": "gpt-4o-mini",
        "temperature": 0.7
    }
)

print(f"Agent created: {agent.agent_id}")
```

### JavaScript

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient();

const agent = await client.conversationalAi.agents.create({
  name: "My Assistant",
  conversationConfig: {
    agent: {
      firstMessage: "Hello! How can I help you today?",
      language: "en",
    },
    tts: {
      voiceId: "JBFqnCBsd6RMkjVDRZzb",
    },
  },
  prompt: {
    prompt: "You are a helpful assistant. Be concise and friendly.",
    llm: "gpt-4o-mini",
    temperature: 0.7,
  },
});

console.log(`Agent created: ${agent.agentId}`);
```

### cURL

```bash
curl -X POST "https://api.elevenlabs.io/v1/convai/agents/create" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Assistant",
    "conversation_config": {
      "agent": {
        "first_message": "Hello! How can I help you today?",
        "language": "en"
      },
      "tts": {
        "voice_id": "JBFqnCBsd6RMkjVDRZzb"
      }
    },
    "prompt": {
      "prompt": "You are a helpful assistant. Be concise and friendly.",
      "llm": "gpt-4o-mini",
      "temperature": 0.7
    }
  }'
```

## Starting Conversations

### Python (Server-Side)

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

# Get a signed URL for WebSocket connection
signed_url = client.conversational_ai.conversations.get_signed_url(
    agent_id="your-agent-id"
)

# Use this URL in your client to establish WebSocket connection
print(f"Connect to: {signed_url.signed_url}")
```

### JavaScript (Client-Side with WebRTC)

```javascript
import { Conversation } from "@elevenlabs/client";

const conversation = await Conversation.startSession({
  agentId: "your-agent-id",
  connectionType: "webrtc",
  onConnect: () => console.log("Connected"),
  onDisconnect: () => console.log("Disconnected"),
  onMessage: (message) => console.log("Agent:", message.message),
  onUserTranscript: (transcript) => console.log("User:", transcript.message),
  onError: (error) => console.error("Error:", error),
});

// Control the conversation
await conversation.endSession();
```

### React Hook

```typescript
import { useConversation } from "@elevenlabs/react";

function VoiceAgent() {
  const conversation = useConversation({
    onConnect: () => console.log("Connected"),
    onMessage: (message) => console.log("Agent:", message.message),
    onError: (error) => console.error("Error:", error),
  });

  const start = async () => {
    // Get token from your backend (never expose API key to client)
    const { token } = await fetch("/convai-token").then((r) => r.json());

    await conversation.startSession({
      signedUrl: token,
    });
  };

  return (
    <div>
      <button onClick={start} disabled={conversation.status === "connected"}>
        Start Conversation
      </button>
      <button onClick={() => conversation.endSession()}>End</button>
      <p>Status: {conversation.status}</p>
    </div>
  );
}
```

## LLM Configuration

| Provider | Model ID | Notes |
|----------|----------|-------|
| OpenAI | `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` | Default provider |
| Anthropic | `claude-3-5-sonnet`, `claude-3-5-haiku` | Claude models |
| Google | `gemini-1.5-pro`, `gemini-1.5-flash` | Gemini models |
| Custom | `custom-llm` | Bring your own LLM endpoint |

```python
agent = client.conversational_ai.agents.create(
    name="Claude Assistant",
    prompt={
        "prompt": "You are a helpful assistant.",
        "llm": "claude-3-5-sonnet",
        "temperature": 0.7,
        "max_tokens": 500
    },
    # ...
)
```

## Voice Selection

Choose a voice for your agent. Use flash models for lower latency in real-time conversations:

```python
agent = client.conversational_ai.agents.create(
    name="Fast Assistant",
    conversation_config={
        "tts": {
            "voice_id": "JBFqnCBsd6RMkjVDRZzb",
            "model_id": "eleven_flash_v2_5"  # Ultra-low latency
        }
    },
    # ...
)
```

**Popular voices:**
- `JBFqnCBsd6RMkjVDRZzb` - George (male, narrative)
- `EXAVITQu4vr4xnSDxMaL` - Sarah (female, soft)
- `onwK4e9ZLuTAKqWW03F9` - Daniel (male, authoritative)
- `XB0fDUnXU5powFXDhCwa` - Charlotte (female, conversational)

## System Prompts

The system prompt defines your agent's personality, knowledge, and behavior:

```python
agent = client.conversational_ai.agents.create(
    name="Support Agent",
    prompt={
        "prompt": """You are a customer support agent for TechCorp.

Your responsibilities:
- Answer questions about our products
- Help troubleshoot common issues
- Escalate complex problems to human agents

Guidelines:
- Be friendly but professional
- Keep responses concise (1-2 sentences when possible)
- If you don't know something, say so
- Never make up information about products or policies

Product knowledge:
- TechWidget Pro: $99, supports Windows/Mac, 1-year warranty
- TechWidget Plus: $149, adds cloud sync and priority support""",
        "llm": "gpt-4o-mini",
        "temperature": 0.5
    },
    # ...
)
```

## Turn-Taking Modes

Control how the agent handles conversation flow:

| Mode | Description | Best For |
|------|-------------|----------|
| `server_vad` | Voice Activity Detection - agent responds when user stops speaking | Natural conversations |
| `turn_based` | Explicit turn signals required | Noisy environments, precise control |

```python
agent = client.conversational_ai.agents.create(
    name="VAD Assistant",
    conversation_config={
        "turn": {
            "mode": "server_vad",
            "silence_threshold_ms": 500  # Wait 500ms of silence before responding
        }
    },
    # ...
)
```

## Tools

Extend your agent with custom capabilities using webhook tools, client tools, or built-in system tools.

### Webhook Tool

Server-side execution via HTTP:

```python
agent = client.conversational_ai.agents.create(
    name="Weather Assistant",
    tools=[{
        "type": "webhook",
        "name": "get_weather",
        "description": "Get current weather for a location",
        "webhook": {
            "url": "https://api.example.com/weather",
            "method": "POST"
        },
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name"
                }
            },
            "required": ["location"]
        }
    }],
    # ...
)
```

### Client Tool

Execute in the user's browser:

```javascript
const conversation = await Conversation.startSession({
  agentId: "your-agent-id",
  clientTools: {
    show_product: async ({ productId }) => {
      // Run in the browser - update UI, navigate, etc.
      document.getElementById("product").src = `/products/${productId}`;
      return { success: true };
    },
  },
});
```

### System Tools

Built-in capabilities:

```python
agent = client.conversational_ai.agents.create(
    name="Transfer Agent",
    tools=[
        {"type": "system", "name": "end_call"},
        {"type": "system", "name": "transfer_to_number", "phone_number": "+1234567890"}
    ],
    # ...
)
```

See [Client Tools Reference](references/client-tools.md) for complete documentation.

## Widget Embedding

Add a voice agent to any website with a single line of code:

```html
<script src="https://elevenlabs.io/convai-widget/index.js" async></script>
<elevenlabs-convai agent-id="your-agent-id"></elevenlabs-convai>
```

### Customization

```html
<elevenlabs-convai
  agent-id="your-agent-id"
  avatar-image-url="https://example.com/avatar.png"
  action-text="Talk to our assistant"
  start-call-text="Start call"
  end-call-text="End call"
  expand-text="Open chat"
  collapse-text="Close chat"
></elevenlabs-convai>
```

See [Widget Embedding Reference](references/widget-embedding.md) for all options.

## Event Handling

Handle conversation events for logging, UI updates, or custom logic:

```javascript
const conversation = await Conversation.startSession({
  agentId: "your-agent-id",
  onConnect: () => {
    console.log("Connected to agent");
  },
  onDisconnect: () => {
    console.log("Disconnected");
  },
  onMessage: (message) => {
    // Agent's spoken response
    console.log("Agent:", message.message);
  },
  onUserTranscript: (transcript) => {
    // User's transcribed speech
    console.log("User:", transcript.message);
  },
  onModeChange: (mode) => {
    // "listening" or "speaking"
    console.log("Mode:", mode.mode);
  },
  onError: (error) => {
    console.error("Error:", error);
  },
});
```

## Error Handling

```python
from elevenlabs import ElevenLabsError

try:
    agent = client.conversational_ai.agents.create(
        name="My Agent",
        # ...
    )
except ElevenLabsError as e:
    print(f"API error: {e.message}")
```

Common errors:
- **401**: Invalid API key
- **404**: Agent not found
- **422**: Invalid configuration (check agent config, voice_id, llm)
- **429**: Rate limit exceeded

## Managing Agents

### List Agents

#### Python

```python
agents = client.conversational_ai.agents.list()
for agent in agents.agents:
    print(f"{agent.name}: {agent.agent_id}")
```

#### JavaScript

```javascript
const agents = await client.conversationalAi.agents.list();
agents.agents.forEach((agent) => {
  console.log(`${agent.name}: ${agent.agentId}`);
});
```

#### cURL

```bash
curl -X GET "https://api.elevenlabs.io/v1/convai/agents" \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

### Get Agent

#### Python

```python
agent = client.conversational_ai.agents.get(agent_id="your-agent-id")
print(f"Name: {agent.name}")
print(f"Voice: {agent.conversation_config.tts.voice_id}")
```

#### JavaScript

```javascript
const agent = await client.conversationalAi.agents.get("your-agent-id");
console.log(`Name: ${agent.name}`);
console.log(`Voice: ${agent.conversationConfig.tts.voiceId}`);
```

#### cURL

```bash
curl -X GET "https://api.elevenlabs.io/v1/convai/agents/your-agent-id" \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

### Update Agent

Update any agent configuration after creation. Only include the fields you want to change - all other settings remain unchanged.

#### Python

```python
# Update basic settings
client.conversational_ai.agents.update(
    agent_id="your-agent-id",
    name="Updated Assistant Name"
)

# Update conversation config
client.conversational_ai.agents.update(
    agent_id="your-agent-id",
    conversation_config={
        "agent": {
            "first_message": "Welcome back! How can I assist you?",
            "language": "en"
        },
        "tts": {
            "voice_id": "EXAVITQu4vr4xnSDxMaL",
            "model_id": "eleven_flash_v2_5"
        },
        "turn": {
            "mode": "server_vad",
            "silence_threshold_ms": 600
        }
    }
)

# Update prompt and LLM settings
client.conversational_ai.agents.update(
    agent_id="your-agent-id",
    prompt={
        "prompt": "You are an updated assistant with new instructions.",
        "llm": "claude-3-5-sonnet",
        "temperature": 0.8,
        "max_tokens": 600
    }
)

# Update tools
client.conversational_ai.agents.update(
    agent_id="your-agent-id",
    tools=[
        {
            "type": "webhook",
            "name": "check_inventory",
            "description": "Check product inventory",
            "webhook": {
                "url": "https://api.example.com/inventory",
                "method": "GET"
            },
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "Product ID"}
                },
                "required": ["product_id"]
            }
        },
        {"type": "system", "name": "end_call"}
    ]
)

# Update platform settings
client.conversational_ai.agents.update(
    agent_id="your-agent-id",
    platform_settings={
        "auth": {
            "enable_auth": True,
            "allowlist": ["https://myapp.com", "https://staging.myapp.com"]
        },
        "call_limits": {
            "max_call_duration_secs": 1200,
            "max_concurrent_calls": 20
        },
        "privacy": {
            "record_conversation": True,
            "retention_days": 90
        }
    }
)

# Full update - combine multiple sections
client.conversational_ai.agents.update(
    agent_id="your-agent-id",
    name="Production Assistant",
    conversation_config={
        "agent": {"first_message": "Hello! I'm your production assistant."},
        "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb"}
    },
    prompt={
        "prompt": "You are a production-ready assistant.",
        "llm": "gpt-4o",
        "temperature": 0.5
    },
    platform_settings={
        "call_limits": {"max_concurrent_calls": 50}
    }
)
```

#### JavaScript

```javascript
// Update basic settings
await client.conversationalAi.agents.update("your-agent-id", {
  name: "Updated Assistant Name",
});

// Update conversation config
await client.conversationalAi.agents.update("your-agent-id", {
  conversationConfig: {
    agent: {
      firstMessage: "Welcome back! How can I assist you?",
      language: "en",
    },
    tts: {
      voiceId: "EXAVITQu4vr4xnSDxMaL",
      modelId: "eleven_flash_v2_5",
    },
    turn: {
      mode: "server_vad",
      silenceThresholdMs: 600,
    },
  },
});

// Update prompt and LLM settings
await client.conversationalAi.agents.update("your-agent-id", {
  prompt: {
    prompt: "You are an updated assistant with new instructions.",
    llm: "claude-3-5-sonnet",
    temperature: 0.8,
    maxTokens: 600,
  },
});

// Update tools
await client.conversationalAi.agents.update("your-agent-id", {
  tools: [
    {
      type: "webhook",
      name: "check_inventory",
      description: "Check product inventory",
      webhook: {
        url: "https://api.example.com/inventory",
        method: "GET",
      },
      parameters: {
        type: "object",
        properties: {
          product_id: { type: "string", description: "Product ID" },
        },
        required: ["product_id"],
      },
    },
    { type: "system", name: "end_call" },
  ],
});

// Update platform settings
await client.conversationalAi.agents.update("your-agent-id", {
  platformSettings: {
    auth: {
      enableAuth: true,
      allowlist: ["https://myapp.com", "https://staging.myapp.com"],
    },
    callLimits: {
      maxCallDurationSecs: 1200,
      maxConcurrentCalls: 20,
    },
    privacy: {
      recordConversation: true,
      retentionDays: 90,
    },
  },
});

// Full update - combine multiple sections
await client.conversationalAi.agents.update("your-agent-id", {
  name: "Production Assistant",
  conversationConfig: {
    agent: { firstMessage: "Hello! I'm your production assistant." },
    tts: { voiceId: "JBFqnCBsd6RMkjVDRZzb" },
  },
  prompt: {
    prompt: "You are a production-ready assistant.",
    llm: "gpt-4o",
    temperature: 0.5,
  },
  platformSettings: {
    callLimits: { maxConcurrentCalls: 50 },
  },
});
```

#### cURL

```bash
# Update basic settings
curl -X PATCH "https://api.elevenlabs.io/v1/convai/agents/your-agent-id" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Assistant Name"
  }'

# Update conversation config
curl -X PATCH "https://api.elevenlabs.io/v1/convai/agents/your-agent-id" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_config": {
      "agent": {
        "first_message": "Welcome back! How can I assist you?",
        "language": "en"
      },
      "tts": {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "model_id": "eleven_flash_v2_5"
      },
      "turn": {
        "mode": "server_vad",
        "silence_threshold_ms": 600
      }
    }
  }'

# Update prompt and LLM settings
curl -X PATCH "https://api.elevenlabs.io/v1/convai/agents/your-agent-id" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": {
      "prompt": "You are an updated assistant with new instructions.",
      "llm": "claude-3-5-sonnet",
      "temperature": 0.8,
      "max_tokens": 600
    }
  }'

# Full update - combine multiple sections
curl -X PATCH "https://api.elevenlabs.io/v1/convai/agents/your-agent-id" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Assistant",
    "conversation_config": {
      "agent": {"first_message": "Hello! I am your production assistant."},
      "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb"}
    },
    "prompt": {
      "prompt": "You are a production-ready assistant.",
      "llm": "gpt-4o",
      "temperature": 0.5
    },
    "platform_settings": {
      "call_limits": {"max_concurrent_calls": 50}
    }
  }'
```

#### Updatable Fields

| Section | Fields |
|---------|--------|
| Root | `name` |
| `conversation_config.agent` | `first_message`, `language`, `max_tokens_agent_response` |
| `conversation_config.tts` | `voice_id`, `model_id`, `stability`, `similarity_boost`, `optimize_streaming_latency` |
| `conversation_config.asr` | `model_id`, `keyterms` |
| `conversation_config.turn` | `mode`, `silence_threshold_ms`, `interrupt_sensitivity` |
| `prompt` | `prompt`, `llm`, `temperature`, `max_tokens`, `tools_strict_mode`, `custom_llm` |
| `tools` | Array of webhook, client, or system tools (replaces existing tools) |
| `platform_settings.auth` | `enable_auth`, `allowlist` |
| `platform_settings.privacy` | `record_conversation`, `retention_days` |
| `platform_settings.call_limits` | `max_call_duration_secs`, `max_concurrent_calls` |

See [Agent Configuration](references/agent-configuration.md) for complete field documentation.

### Delete Agent

#### Python

```python
client.conversational_ai.agents.delete(agent_id="your-agent-id")
```

#### JavaScript

```javascript
await client.conversationalAi.agents.delete("your-agent-id");
```

#### cURL

```bash
curl -X DELETE "https://api.elevenlabs.io/v1/convai/agents/your-agent-id" \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

## References

- [Installation Guide](references/installation.md)
- [Agent Configuration](references/agent-configuration.md)
- [Client Tools](references/client-tools.md)
- [Widget Embedding](references/widget-embedding.md)
