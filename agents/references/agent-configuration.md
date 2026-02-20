# Agent Configuration

Complete reference for configuring conversational AI agents.

## Configuration Structure

```python
agent = client.conversational_ai.agents.create(
    name="My Agent",
    conversation_config={
        "agent": {
            "first_message": "Hello!",
            "language": "en",
            "prompt": {           # LLM, system prompt, tools, and knowledge base
                "prompt": "You are helpful.",
                "llm": "gemini-2.0-flash",
                "tools": [...],
                "built_in_tools": {...}
            }
        },
        "tts": {...},             # Voice and TTS model settings
        "asr": {...},             # Speech recognition settings
        "turn": {...},            # Turn-taking behavior
        "conversation": {...},    # Duration, events, monitoring
        "vad": {...},             # Voice activity detection config
        "language_presets": {...}  # Language-specific overrides
    },
    platform_settings={...}       # Auth, call limits
)
```

## conversation_config

Controls the real-time conversation behavior.

### agent

```python
conversation_config={
    "agent": {
        "first_message": "Hello! How can I help you today?",
        "language": "en",
        "disable_first_message_interruptions": False,
        "prompt": {
            "prompt": "You are a helpful assistant.",
            "llm": "gemini-2.0-flash",
            "temperature": 0.7
        }
    }
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `first_message` | string | `""` | What the agent says when conversation starts |
| `language` | string | `"en"` | ISO 639-1 language code (en, es, fr, etc.) |
| `disable_first_message_interruptions` | bool | `false` | Prevent user from interrupting the first message |
| `hinglish_mode` | bool | `false` | When enabled and language is Hindi, agent responds in Hinglish |
| `dynamic_variables` | object | - | Config with `dynamic_variable_placeholders` containing key-value pairs |
| `prompt` | object | - | LLM configuration (see prompt section below) |

### tts (Text-to-Speech)

```python
conversation_config={
    "tts": {
        "voice_id": "JBFqnCBsd6RMkjVDRZzb",
        "model_id": "eleven_flash_v2_5",
        "stability": 0.5,
        "similarity_boost": 0.8,
        "speed": 1.0,
        "optimize_streaming_latency": 3,
        "expressive_mode": True
    }
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `voice_id` | string | `"cjVigY5qzO86Huf0OWal"` | Voice to use |
| `model_id` | string | - | TTS model (see below) |
| `stability` | float | `0.5` | 0-1, lower = more expressive |
| `similarity_boost` | float | `0.8` | 0-1, higher = closer to original voice |
| `speed` | float | `1.0` | 0.7-1.2, speech speed multiplier |
| `optimize_streaming_latency` | int | - | 0-4, higher = faster but lower quality |
| `expressive_mode` | bool | `true` | Enable expressive voice generation |
| `agent_output_audio_format` | string | - | Output audio codec format |
| `pronunciation_dictionary_locators` | array | - | Pronunciation overrides |

**Available TTS models for agents:**

| Model ID | Languages | Latency |
|----------|-----------|---------|
| `eleven_flash_v2_5` | 32 | ~75ms (recommended) |
| `eleven_flash_v2` | English | ~75ms |
| `eleven_turbo_v2_5` | 32 | ~250-300ms |
| `eleven_turbo_v2` | English | ~250-300ms |
| `eleven_multilingual_v2` | 29 | Standard |
| `eleven_v3_conversational` | 70+ | Standard |

### asr (Automatic Speech Recognition)

```python
conversation_config={
    "asr": {
        "quality": "high",
        "keywords": ["ElevenLabs", "TechCorp"],
        "user_input_audio_format": "pcm_16000"
    }
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `quality` | string | `"high"` | Transcription quality level |
| `provider` | string | `"elevenlabs"` | ASR provider (`elevenlabs` or `scribe_realtime`) |
| `keywords` | array | - | Words to boost recognition accuracy |
| `user_input_audio_format` | string | - | Input audio format (e.g., `pcm_16000`, `ulaw_8000`) |

### turn (Turn-Taking)

```python
conversation_config={
    "turn": {
        "turn_timeout": 7,
        "turn_eagerness": "normal",
        "silence_end_call_timeout": -1
    }
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `turn_timeout` | number | `7` | Seconds to wait before re-engaging the user |
| `turn_eagerness` | string | `"normal"` | How quickly agent responds: `patient`, `normal`, or `eager` |
| `silence_end_call_timeout` | number | `-1` | Seconds of silence before ending call (-1 = disabled) |
| `initial_wait_time` | number | - | Seconds to wait for user to start speaking |
| `spelling_patience` | string | `"auto"` | Entity detection patience: `auto` or `off` |
| `speculative_turn` | bool | `false` | Enable speculative turn detection |
| `soft_timeout_config` | object | - | Configures a message if user is silent (see below) |

**soft_timeout_config:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `timeout_seconds` | number | `-1` | Seconds before soft timeout (-1 = disabled) |
| `message` | string | `"Hhmmmm...yeah."` | What agent says on timeout |
| `use_llm_generated_message` | bool | `false` | Let LLM generate the timeout message |

## prompt (nested in conversation_config.agent)

Configures the LLM behavior. This object lives at `conversation_config.agent.prompt`:

```python
conversation_config={
    "agent": {
        "prompt": {
            "prompt": "You are a helpful customer service agent...",
            "llm": "gemini-2.0-flash",
            "temperature": 0.7,
            "max_tokens": 500,
            "tools": [...],
            "built_in_tools": {...},
            "knowledge_base": [...]
        }
    }
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `prompt` | string | `""` | System prompt defining agent behavior |
| `llm` | string | - | Model ID (see LLM providers below) |
| `temperature` | float | `0` | 0-1, higher = more creative |
| `max_tokens` | int | `-1` | Max tokens for LLM response (-1 = unlimited) |
| `reasoning_effort` | string | - | Reasoning depth: `none`, `minimal`, `low`, `medium`, `high` (model-dependent) |
| `thinking_budget` | int | - | Max thinking tokens for reasoning models |
| `tools` | array | - | Webhook and client tool definitions |
| `built_in_tools` | object | - | System tools (end_call, transfer, etc.) |
| `tool_ids` | array | - | References to pre-configured tools |
| `knowledge_base` | array | - | Documents for RAG |
| `custom_llm` | object | - | Custom LLM endpoint config |
| `timezone` | string | - | IANA timezone (e.g., `America/New_York`) |
| `backup_llm_config` | object | - | Fallback LLM configuration |
| `cascade_timeout_seconds` | number | `8` | Seconds before cascading to backup LLM (2-15) |
| `mcp_server_ids` | array | - | MCP server IDs to connect |
| `native_mcp_server_ids` | array | - | Native MCP server IDs |
| `ignore_default_personality` | bool | - | Skip default personality instructions |

### LLM Providers

| Provider | Model IDs |
|----------|-----------|
| OpenAI | `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`, `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` |
| Anthropic | `claude-sonnet-4-5`, `claude-sonnet-4`, `claude-haiku-4-5`, `claude-3-7-sonnet`, `claude-3-5-sonnet`, `claude-3-haiku` |
| Google | `gemini-3-pro-preview`, `gemini-3-flash-preview`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-2.0-flash`, `gemini-2.0-flash-lite` |
| ElevenLabs | `glm-45-air-fp8`, `qwen3-30b-a3b`, `gpt-oss-120b` (hosted, ultra-low latency) |
| Custom | `custom-llm` (requires custom_llm config) |

### Custom LLM

The `custom_llm` field is nested inside `conversation_config.agent.prompt`:

```python
conversation_config={
    "agent": {
        "prompt": {
            "prompt": "You are helpful.",
            "llm": "custom-llm",
            "custom_llm": {
                "url": "https://your-llm-endpoint.com/v1/chat/completions",
                "model_id": "your-model-id",
                "api_key": {"secret_id": "your-secret-id"},
                "api_type": "chat_completions"  # or "responses"
            }
        }
    }
}
```

## platform_settings

Platform-level configuration for security and limits.

```python
platform_settings={
    "auth": {
        "enable_auth": True,
        "allowlist": [{"hostname": "example.com"}]
    },
    "call_limits": {
        "agent_concurrency_limit": 10,
        "daily_limit": 100
    }
}
```

### auth

| Field | Type | Description |
|-------|------|-------------|
| `enable_auth` | bool | Require signed URLs/tokens for connections |
| `allowlist` | array | Allowed origins for CORS |
| `shareable_token` | string | Public conversation token |

### call_limits

| Field | Type | Description |
|-------|------|-------------|
| `agent_concurrency_limit` | int | Max simultaneous conversations (default: -1, unlimited) |
| `daily_limit` | int | Max conversations per day (default: 100000) |
| `bursting_enabled` | bool | Allow exceeding limits at 2x cost (default: true) |

### conversation (inside conversation_config)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_duration_seconds` | int | `600` | Max conversation duration |
| `text_only` | bool | `false` | Text-only mode (avoids audio pricing) |
| `monitoring_enabled` | bool | `false` | Enable real-time WebSocket monitoring |

## Additional Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `tags` | array | Classification labels for filtering (e.g., `["production"]`, `["test"]`) |
| `coaching_settings` | object | Configuration for agent coaching and evaluation |
| `workflow` | object | Conversation flow definition and tool interaction sequences |

## Knowledge Base / RAG

Knowledge base is configured inside `conversation_config.agent.prompt`:

```python
agent = client.conversational_ai.agents.create(
    name="Support Agent",
    conversation_config={
        "agent": {
            "prompt": {
                "prompt": "You are a support agent. Use the knowledge base to answer questions.",
                "llm": "gemini-2.0-flash",
                "knowledge_base": [
                    {"type": "file", "id": "doc-id", "name": "Product Guide", "usage_mode": "auto"}
                ],
                "rag": {
                    "enabled": True,
                    "max_documents_length": 50000,
                    "max_retrieved_rag_chunks_count": 20
                }
            }
        },
        "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb"}
    }
)
```

## CRUD Operations

### Using CLI (Recommended)

```bash
# Initialize project
elevenlabs agents init

# Create agent from template
elevenlabs agents add "My Agent" --template complete
elevenlabs agents add "Support Bot" --template customer-service

# List agents
elevenlabs agents list

# Check status
elevenlabs agents status

# Push local changes to platform
elevenlabs agents push
elevenlabs agents push --dry-run    # Preview changes first

# Import agents from platform
elevenlabs agents pull                      # Import all
elevenlabs agents pull --agent <agent-id>   # Import specific agent
elevenlabs agents pull --update             # Override local configs

# View available templates
elevenlabs agents templates list
elevenlabs agents templates show <template-name>

# Add tools
elevenlabs tools add-webhook "API Tool"
elevenlabs tools add-client "UI Tool"

# Generate widget code
elevenlabs agents widget <agent-id>
```

### SDK: List Agents

```python
agents = client.conversational_ai.agents.list()
for agent in agents.agents:
    print(f"{agent.name}: {agent.agent_id}")
```

```javascript
const agents = await client.conversationalAi.agents.list();
```

```bash
curl -X GET "https://api.elevenlabs.io/v1/convai/agents" -H "xi-api-key: $ELEVENLABS_API_KEY"
```

### SDK: Get Agent

```python
agent = client.conversational_ai.agents.get(agent_id="your-agent-id")
```

```javascript
const agent = await client.conversationalAi.agents.get("your-agent-id");
```

```bash
curl -X GET "https://api.elevenlabs.io/v1/convai/agents/your-agent-id" -H "xi-api-key: $ELEVENLABS_API_KEY"
```

### SDK: Update Agent

Only include fields you want to change. All other settings remain unchanged.

**Python:**
```python
# Update name
client.conversational_ai.agents.update(agent_id="id", name="New Name")

# Update TTS voice
client.conversational_ai.agents.update(agent_id="id", conversation_config={
    "tts": {"voice_id": "EXAVITQu4vr4xnSDxMaL", "model_id": "eleven_flash_v2_5"}
})

# Update prompt/LLM (nested in agent)
client.conversational_ai.agents.update(agent_id="id", conversation_config={
    "agent": {"prompt": {"prompt": "New instructions.", "llm": "claude-sonnet-4", "temperature": 0.8}}
})

# Update first message
client.conversational_ai.agents.update(agent_id="id", conversation_config={
    "agent": {"first_message": "Welcome back!"}
})

# Update platform settings
client.conversational_ai.agents.update(agent_id="id", platform_settings={
    "auth": {"enable_auth": True, "allowlist": [{"hostname": "myapp.com"}]}
})
```

**JavaScript:**
```javascript
await client.conversationalAi.agents.update("id", { name: "New Name" });
await client.conversationalAi.agents.update("id", {
  conversationConfig: { tts: { voiceId: "EXAVITQu4vr4xnSDxMaL" } }
});
await client.conversationalAi.agents.update("id", {
  conversationConfig: { agent: { prompt: { prompt: "New instructions.", llm: "claude-sonnet-4" } } }
});
```

**cURL:**
```bash
curl -X PATCH "https://api.elevenlabs.io/v1/convai/agents/your-agent-id" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"name": "New Name"}'
```

#### Updatable Fields

| Section | Fields |
|---------|--------|
| Root | `name`, `tags` |
| `conversation_config.agent` | `first_message`, `language`, `disable_first_message_interruptions`, `dynamic_variables` |
| `conversation_config.agent.prompt` | `prompt`, `llm`, `temperature`, `max_tokens`, `reasoning_effort`, `tools`, `built_in_tools`, `knowledge_base`, `custom_llm`, `timezone` |
| `conversation_config.tts` | `voice_id`, `model_id`, `stability`, `similarity_boost`, `speed`, `optimize_streaming_latency`, `expressive_mode` |
| `conversation_config.asr` | `quality`, `provider`, `keywords`, `user_input_audio_format` |
| `conversation_config.turn` | `turn_timeout`, `turn_eagerness`, `silence_end_call_timeout`, `soft_timeout_config` |
| `conversation_config.conversation` | `max_duration_seconds`, `text_only`, `monitoring_enabled` |
| `platform_settings.auth` | `enable_auth`, `allowlist` |
| `platform_settings.call_limits` | `agent_concurrency_limit`, `daily_limit`, `bursting_enabled` |

### SDK: Delete Agent

```python
client.conversational_ai.agents.delete(agent_id="your-agent-id")
```

```javascript
await client.conversationalAi.agents.delete("your-agent-id");
```

```bash
curl -X DELETE "https://api.elevenlabs.io/v1/convai/agents/your-agent-id" -H "xi-api-key: $ELEVENLABS_API_KEY"
```

## CI/CD Integration

Use the CLI in your deployment pipeline:

```bash
# Set API key as environment variable
export ELEVENLABS_API_KEY="your-api-key"

# Push changes (non-interactive)
elevenlabs agents push
```

## Example Configurations

### Customer Support Agent

```python
agent = client.conversational_ai.agents.create(
    name="Support Agent",
    conversation_config={
        "agent": {
            "first_message": "Hi! Thanks for calling TechCorp support.",
            "language": "en",
            "prompt": {
                "prompt": "You are a customer support agent. Be helpful, professional, concise.",
                "llm": "gemini-2.0-flash",
                "temperature": 0.5,
                "built_in_tools": {
                    "end_call": {},
                    "transfer_to_number": {
                        "transfers": [{"transfer_destination": {"type": "phone", "phone_number": "+1234567890"}, "condition": "User asks for human support"}]
                    }
                }
            }
        },
        "tts": {"voice_id": "XB0fDUnXU5powFXDhCwa", "model_id": "eleven_flash_v2_5"},
        "turn": {"turn_eagerness": "normal", "turn_timeout": 7},
        "conversation": {"max_duration_seconds": 900}
    }
)
```

### Low-Latency Assistant

```python
agent = client.conversational_ai.agents.create(
    name="Quick Assistant",
    conversation_config={
        "agent": {
            "first_message": "Hey! What do you need?",
            "prompt": {
                "prompt": "Fast, efficient assistant. Brief answers.",
                "llm": "gemini-2.0-flash",
                "temperature": 0.3,
                "max_tokens": 100
            }
        },
        "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb", "model_id": "eleven_flash_v2_5", "optimize_streaming_latency": 4},
        "turn": {"turn_eagerness": "eager", "turn_timeout": 3}
    }
)
```
