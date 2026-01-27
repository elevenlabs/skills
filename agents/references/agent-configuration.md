# Agent Configuration

Complete reference for configuring conversational AI agents.

## Configuration Structure

```python
agent = client.conversational_ai.agents.create(
    name="My Agent",
    conversation_config={...},  # TTS, ASR, turn-taking settings
    prompt={...},               # LLM and system prompt
    tools=[...],                # Webhook, client, and system tools
    platform_settings={...}     # Auth, privacy, call limits
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
        "max_tokens_agent_response": 500
    }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `first_message` | string | What the agent says when conversation starts |
| `language` | string | ISO 639-1 language code (en, es, fr, etc.) |
| `max_tokens_agent_response` | int | Max tokens per agent response |

### tts (Text-to-Speech)

```python
conversation_config={
    "tts": {
        "voice_id": "JBFqnCBsd6RMkjVDRZzb",
        "model_id": "eleven_flash_v2_5",
        "stability": 0.5,
        "similarity_boost": 0.75,
        "optimize_streaming_latency": 3
    }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `voice_id` | string | Voice to use (required) |
| `model_id` | string | TTS model - use flash models for low latency |
| `stability` | float | 0-1, lower = more expressive |
| `similarity_boost` | float | 0-1, higher = closer to original voice |
| `optimize_streaming_latency` | int | 0-4, higher = faster but lower quality |

**Recommended TTS models for real-time:**
- `eleven_flash_v2_5` - Ultra-low latency (~75ms)
- `eleven_turbo_v2_5` - Balanced quality/speed

### asr (Automatic Speech Recognition)

```python
conversation_config={
    "asr": {
        "model_id": "scribe_v2_realtime",
        "keyterms": ["ElevenLabs", "TechCorp"]
    }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `model_id` | string | ASR model (default: scribe_v2_realtime) |
| `keyterms` | array | Words to recognize accurately |

### turn (Turn-Taking)

```python
conversation_config={
    "turn": {
        "mode": "server_vad",
        "silence_threshold_ms": 500,
        "interrupt_sensitivity": 0.5
    }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `mode` | string | `server_vad` (auto) or `turn_based` (manual) |
| `silence_threshold_ms` | int | Silence duration before agent responds |
| `interrupt_sensitivity` | float | 0-1, how easily user can interrupt |

## prompt

Configures the LLM behavior.

```python
prompt={
    "prompt": "You are a helpful customer service agent...",
    "llm": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 500,
    "tools_strict_mode": True
}
```

| Field | Type | Description |
|-------|------|-------------|
| `prompt` | string | System prompt defining agent behavior |
| `llm` | string | Model ID (see LLM providers below) |
| `temperature` | float | 0-1, higher = more creative |
| `max_tokens` | int | Max tokens for LLM response |
| `tools_strict_mode` | bool | Enforce strict tool parameter validation |

### LLM Providers

| Provider | Model IDs |
|----------|-----------|
| OpenAI | `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` |
| Anthropic | `claude-3-5-sonnet`, `claude-3-5-haiku` |
| Google | `gemini-1.5-pro`, `gemini-1.5-flash` |
| Custom | `custom-llm` (requires custom_llm config) |

### Custom LLM

```python
prompt={
    "prompt": "You are helpful.",
    "llm": "custom-llm",
    "custom_llm": {
        "url": "https://your-llm-endpoint.com/v1/chat/completions",
        "model_id": "your-model-id",
        "api_key": "your-api-key"
    }
}
```

## platform_settings

Platform-level configuration for security and limits.

```python
platform_settings={
    "auth": {
        "enable_auth": True,
        "allowlist": ["https://example.com"]
    },
    "privacy": {
        "record_conversation": False,
        "retention_days": 30
    },
    "call_limits": {
        "max_call_duration_secs": 600,
        "max_concurrent_calls": 10
    }
}
```

### auth

| Field | Type | Description |
|-------|------|-------------|
| `enable_auth` | bool | Require signed URLs for connections |
| `allowlist` | array | Allowed origins for CORS |

### privacy

| Field | Type | Description |
|-------|------|-------------|
| `record_conversation` | bool | Store conversation audio/transcripts |
| `retention_days` | int | How long to keep recordings |

### call_limits

| Field | Type | Description |
|-------|------|-------------|
| `max_call_duration_secs` | int | Max conversation length |
| `max_concurrent_calls` | int | Max simultaneous conversations |

## Knowledge Base / RAG

Add documents for the agent to reference:

```python
# Upload a document
doc = client.conversational_ai.knowledge_base.upload(
    file=open("product_guide.pdf", "rb"),
    name="Product Guide"
)

# Create agent with knowledge base
agent = client.conversational_ai.agents.create(
    name="Support Agent",
    knowledge_base=[doc.document_id],
    prompt={
        "prompt": "You are a support agent. Use the knowledge base to answer questions.",
        "llm": "gpt-4o-mini"
    }
)
```

## Example Configurations

### Customer Support Agent

```python
agent = client.conversational_ai.agents.create(
    name="Support Agent",
    conversation_config={
        "agent": {
            "first_message": "Hi! Thanks for calling TechCorp support. How can I help?",
            "language": "en"
        },
        "tts": {
            "voice_id": "XB0fDUnXU5powFXDhCwa",
            "model_id": "eleven_flash_v2_5"
        },
        "turn": {
            "mode": "server_vad",
            "silence_threshold_ms": 700
        }
    },
    prompt={
        "prompt": """You are a customer support agent for TechCorp.
Be helpful, professional, and concise.
If you can't resolve an issue, offer to transfer to a human agent.""",
        "llm": "gpt-4o-mini",
        "temperature": 0.5
    },
    tools=[
        {"type": "system", "name": "end_call"},
        {"type": "system", "name": "transfer_to_number", "phone_number": "+1234567890"}
    ],
    platform_settings={
        "call_limits": {"max_call_duration_secs": 900}
    }
)
```

### Voice Character

```python
agent = client.conversational_ai.agents.create(
    name="Adventure Guide",
    conversation_config={
        "agent": {
            "first_message": "Greetings, brave adventurer! What quest brings you to my domain?",
            "language": "en"
        },
        "tts": {
            "voice_id": "onwK4e9ZLuTAKqWW03F9",
            "model_id": "eleven_multilingual_v2",
            "stability": 0.3,
            "similarity_boost": 0.8
        },
        "turn": {
            "mode": "server_vad",
            "silence_threshold_ms": 400
        }
    },
    prompt={
        "prompt": """You are a wise wizard guide in a fantasy world.
Speak dramatically and mysteriously.
Reference magic, quests, and ancient lore.
Keep responses under 3 sentences for natural conversation flow.""",
        "llm": "gpt-4o",
        "temperature": 0.9
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
            "language": "en",
            "max_tokens_agent_response": 100
        },
        "tts": {
            "voice_id": "JBFqnCBsd6RMkjVDRZzb",
            "model_id": "eleven_flash_v2_5",
            "optimize_streaming_latency": 4
        },
        "turn": {
            "mode": "server_vad",
            "silence_threshold_ms": 300,
            "interrupt_sensitivity": 0.8
        }
    },
    prompt={
        "prompt": "You are a fast, efficient assistant. Give very brief answers.",
        "llm": "gpt-4o-mini",
        "temperature": 0.3,
        "max_tokens": 100
    }
)
```
