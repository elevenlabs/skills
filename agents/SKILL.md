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
    enable_versioning=True,
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
  enableVersioning: true,
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
curl -X POST "https://api.elevenlabs.io/v1/convai/agents/create?enable_versioning=true" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"name": "My Assistant", "conversation_config": {"agent": {"first_message": "Hello!", "language": "en", "prompt": {"prompt": "You are helpful.", "llm": "gemini-2.0-flash"}}, "tts": {"voice_id": "JBFqnCBsd6RMkjVDRZzb"}}}'
```

## Starting Conversations

**Server-side (Python):** Get signed URL for client connection:
```python
signed_url = client.conversational_ai.conversations.get_signed_url(
    agent_id="your-agent-id",
    environment="staging",
)
```

**Client-side (JavaScript):**
```javascript
import { Conversation } from "@elevenlabs/client";

const conversation = await Conversation.startSession({
  agentId: "your-agent-id",
  environment: "staging",
  onMessage: (msg) => console.log("Agent:", msg.message),
  onUserTranscript: (t) => console.log("User:", t.message),
  onError: (e) => console.error(e)
});
```

**React Hook:** Wrap hook consumers in `ConversationProvider`. Prefer granular hooks such as
`useConversationControls` and `useConversationStatus` for session controls and UI state;
`useConversation` remains available as the convenience all-in-one hook. Pass provider-level
callbacks such as `onError` when you want React to handle conversation errors in one place.
```typescript
import {
  ConversationProvider,
  useConversationControls,
  useConversationStatus,
} from "@elevenlabs/react";

function Agent({ signedUrl }: { signedUrl: string }) {
  const { startSession, endSession } = useConversationControls();
  const { status } = useConversationStatus();

  if (status === "connected") {
    return <button onClick={endSession}>End conversation</button>;
  }

  return (
    <button onClick={() => startSession({ signedUrl })}>
      Start conversation
    </button>
  );
}

function App({ signedUrl }: { signedUrl: string }) {
  return (
    <ConversationProvider
      onError={(error) => console.error("Conversation error:", error)}
    >
      <Agent signedUrl={signedUrl} />
    </ConversationProvider>
  );
}
```

## Configuration

| Provider | Models |
|----------|--------|
| OpenAI | `gpt-5.4`, `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`, `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` |
| Anthropic | `claude-sonnet-4-6`, `claude-sonnet-4-5`, `claude-sonnet-4`, `claude-haiku-4-5`, `claude-3-7-sonnet`, `claude-3-5-sonnet`, `claude-3-haiku` |
| Google | `gemini-3.1-flash-lite-preview`, `gemini-3.1-pro-preview`, `gemini-3-pro-preview`, `gemini-3-flash-preview`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-2.0-flash`, `gemini-2.0-flash-lite` |
| ElevenLabs | `glm-45-air-fp8`, `qwen3-30b-a3b`, `qwen35-35b-a3b`, `qwen35-397b-a17b`, `gpt-oss-120b` |
| Custom | `custom-llm` (bring your own endpoint) |

Use `GET /v1/convai/llm/list` to inspect the current model catalog, including deprecation state, token/context limits, capability flags such as image-input support, and model-specific reasoning effort support.

**Popular voices:** `JBFqnCBsd6RMkjVDRZzb` (George), `EXAVITQu4vr4xnSDxMaL` (Sarah), `onwK4e9ZLuTAKqWW03F9` (Daniel), `XB0fDUnXU5powFXDhCwa` (Charlotte)

**Turn eagerness:** `patient` (waits longer for user to finish), `normal`, or `eager` (responds quickly)

See [Agent Configuration](references/agent-configuration.md) for all options.

## System Prompt Structure

Section the prompt with markdown headings — the model prioritizes and interprets instructions more reliably ([prompting guide](https://elevenlabs.io/docs/eleven-agents/best-practices/prompting-guide)):

```
# Personality   – named character, 2-3 traits
# Environment   – where they work, who they talk to
# Tone          – vocal style as 4-5 bullets
# Goal          – what success looks like (numbered for multi-step flows)
```

Keep instructions short and action-based. Mark critical steps with "This step is important." Configure refusal/safety rules via `platform_settings.guardrails` rather than embedding them in the prompt (see [Guardrails](#guardrails)).

## Tools

Extend agents with webhook, client, or built-in system tools. Tools are defined inside `conversation_config.agent.prompt`:

Workspace environment variables can resolve per-environment server tool URLs, headers, and auth connections, and runtime system variables such as `{{system__conversation_history}}` can pass full conversation context into tool calls when needed.

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

### Built-in System Tools

Set under `conversation_config.agent.prompt.built_in_tools`. `{}` enables defaults; provide `description` to customize; omit to disable.

| Tool | Enable for |
|------|------------|
| `end_call` | All agents |
| `language_detection` | Multilingual agents |
| `transfer_to_number` | Phone-based human escalation |
| `transfer_to_agent` | Multi-agent workflows |
| `skip_turn` | Tutoring / coaching (silent listening) |
| `voicemail_detection` | Outbound calling |
| `play_keypad_touch_tone` | IVR navigation |

### Integration Tools

Pre-built connectors managed by the platform. Create a connection with credentials, then attach via `tool_ids`:

| Integration | Use case |
|-------------|----------|
| `calcom` | Scheduling appointments |
| `salesforce` | CRM lookups, case creation |
| `hubspot` | CRM, marketing, contacts |
| `zendesk` | Support ticketing |

Three-step flow: `POST /v1/convai/api-integrations/{id}/connections` → `GET /v1/convai/api-integrations/{id}/tools` → `POST /v1/convai/tools` with `api_integration_id` and `api_integration_connection_id`. Attach to the agent with `"prompt": {"tool_ids": ["tool_xxxx"]}`. Inline `tools` and `tool_ids` can coexist — prefer an integration over a duplicate custom webhook.

### Public-API Webhook Examples

No-auth APIs useful for prototypes (URLs must be HTTPS):

| Tool | URL | Purpose |
|------|-----|---------|
| `get_weather` | `https://wttr.in/{location}?format=j1` | Current weather |
| `search_wikipedia` | `https://en.wikipedia.org/api/rest_v1/page/summary/{topic}` | Topic summary |
| `get_exchange_rate` | `https://open.er-api.com/v6/latest/{base_currency}` | FX rates |

## Workflows

Route conversations through discrete steps with branching logic. Define under the agent's top-level `workflow` field. Reference: [Agent Workflows](https://elevenlabs.io/docs/eleven-agents/customization/agent-workflows).

**Node types:** `start` (ID must be `"start_node"`), `end`, `override_agent` (subagent step with `label` + `additional_prompt`), `dispatch_tool` (executes a tool with success/failure routing), `agent_transfer`, `transfer_to_number`.

**Edge types:** `unconditional`, `llm` (natural-language condition), `expression` (deterministic data check). Tool nodes have separate success/failure edges.

**Scope tools per step** with `additional_tool_ids` on a node — prevents the wrong tool firing at the wrong step (use `[]` to disable all tools at that step):

```json
{
  "type": "override_agent",
  "label": "Book Appointment",
  "additional_prompt": "Discuss preferred dates and doctors. Show the booking form once agreed.",
  "additional_tool_ids": ["show_booking_form", "display_appointment_card"],
  "position": {"x": 0, "y": 400}
}
```

Include `position` (`{x, y}`) on every node so the editor renders cleanly. Suggested spacing: 200px vertical between levels, 300px horizontal between branches. Keep workflows to 4-7 nodes and always have a path to `end`.

## Guardrails

Layered safety enforcement that runs independently of the LLM — configured under `platform_settings.guardrails`, not in the system prompt. Reference: [Guardrails](https://elevenlabs.io/docs/eleven-agents/best-practices/guardrails).

```json
"platform_settings": {
  "guardrails": {
    "version": "1",
    "focus": {"is_enabled": true},
    "prompt_injection": {"is_enabled": true},
    "content": {"config": {"harassment": {"is_enabled": true, "threshold": 0.5}}},
    "custom": {
      "config": {
        "configs": [{
          "is_enabled": true,
          "name": "No medical diagnoses",
          "prompt": "Block the agent from providing medical diagnoses or treatment advice.",
          "execution_mode": "blocking",
          "trigger_action": {"type": "retry", "feedback": "Reason: {{trigger_reason}}"}
        }]
      }
    }
  }
}
```

**Types:** `focus` (on-topic), `prompt_injection` (manipulation defense), `content` (category filters), `custom` (LLM-evaluated domain rules). Content categories include `harassment`, `profanity`, `sexual`, `violence`, `self_harm`, and `medical_and_legal_information` — threshold range `0.0`–`1.0` (default `0.3`). Custom rules use `execution_mode: "blocking"` with a `trigger_action` (e.g., `retry` with feedback). Custom guardrails evaluate in parallel and fail-open.

**Per vertical:** healthcare/finance/legal → enable `medical_and_legal_information`; education/youth → `sexual`/`violence`/`self_harm`/`profanity`; support/sales → `harassment`/`profanity`. All agents benefit from `focus` + `prompt_injection` + 2-4 custom rules.

## Testing Agents

Three test types via `POST /v1/convai/agent-testing/create`, then attached with PATCH on the agent. Reference: [Agent Testing](https://elevenlabs.io/docs/eleven-agents/customization/agent-testing).

| Type | Purpose |
|------|---------|
| `llm` | Scenario test — does the agent respond appropriately to a message? |
| `tool` | Tool-call test — right tool, right parameters? |
| `simulation` | Multi-turn flow with a simulated user persona |

```json
// Tool-call test (snake_case throughout; chat_history role is "user" or "agent")
{
  "name": "Books with correct doctor and date",
  "type": "tool",
  "chat_history": [
    {"role": "user", "message": "Dr. Smith on March 5 at 2pm", "time_in_call_secs": 10}
  ],
  "tool_call_parameters": {
    "referenced_tool": {"id": "show_booking_form", "type": "client"},
    "parameters": [
      {"path": "doctor_name", "eval": {"type": "llm", "description": "Should reference Dr. Smith"}},
      {"path": "date", "eval": {"type": "regex", "pattern": "2025-03-05|March 5"}}
    ]
  }
}
```

Eval strategies: `exact`, `regex`, `llm`. Attach via PATCH:

```bash
curl -s -X PATCH "https://api.elevenlabs.io/v1/convai/agents/{agent_id}" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"platform_settings": {"testing": {"attached_tests": [{"test_id": "test_xxxx"}]}}}'
```

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
    to_number="+1234567890",
    call_recording_enabled=True
)
print(f"Call initiated: {response.conversation_id}")
```

### JavaScript

```javascript
const response = await client.conversationalAi.twilio.outboundCall({
  agentId: "your-agent-id",
  agentPhoneNumberId: "your-phone-number-id",
  toNumber: "+1234567890",
  callRecordingEnabled: true,
});
```

### cURL

```bash
curl -X POST "https://api.elevenlabs.io/v1/convai/twilio/outbound-call" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"agent_id": "your-agent-id", "agent_phone_number_id": "your-phone-number-id", "to_number": "+1234567890", "call_recording_enabled": true}'
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
