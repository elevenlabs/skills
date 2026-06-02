# Outbound Calls

Make outbound phone calls using your ElevenLabs agent via Twilio or Exotel integration.

## Prerequisites

1. A configured ElevenLabs agent
2. A Twilio or Exotel phone number linked to your agent (obtain `agent_phone_number_id` from the ElevenLabs dashboard)
3. Your ElevenLabs API key

## Basic Usage

See the [main agents skill](../SKILL.md#outbound-calls) for basic Twilio Python, JavaScript, and cURL examples.

## Request Parameters

| Parameter | Type | Provider | Required | Description |
|-----------|------|----------|----------|-------------|
| `agent_id` | string | Twilio, Exotel | Yes | The ID of your ElevenLabs agent |
| `agent_phone_number_id` | string | Twilio, Exotel | Yes | The ID of the linked phone number |
| `to_number` | string | Twilio, Exotel | Yes | The destination phone number in E.164 format |
| `conversation_initiation_client_data` | object | Twilio, Exotel | No | Override conversation settings for this call |
| `telephony_call_config` | object | Twilio, Exotel | No | Telephony call settings like ringing timeout |
| `call_recording_enabled` | boolean | Twilio | No | Whether to let Twilio record the call |

`conversation_initiation_client_data` also accepts `branch_id` to route the call to a specific
agent branch and `environment` to control how environment variables resolve for that call.

## Response

```json
{
  "success": true,
  "message": "Call initiated successfully",
  "conversation_id": "conv_abc123",
  "callSid": "CA1234567890abcdef"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the call was initiated successfully |
| `message` | string | Status message |
| `conversation_id` | string | ElevenLabs conversation ID for tracking |
| `callSid` | string | Provider call SID for reference |

## Exotel Calls

Use the Exotel endpoint when the linked phone number uses the Exotel provider:

```bash
curl -X POST "https://api.elevenlabs.io/v1/convai/exotel/outbound-call" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"agent_id": "your-agent-id", "agent_phone_number_id": "your-phone-number-id", "to_number": "+1234567890"}'
```

## Customizing the Call

Override agent settings for a specific call using `conversation_initiation_client_data`:

### Python

```python
response = client.conversational_ai.twilio.outbound_call(
    agent_id="your-agent-id",
    agent_phone_number_id="your-phone-number-id",
    to_number="+1234567890",
    call_recording_enabled=True,
    conversation_initiation_client_data={
        "branch_id": "branch_support_staging",
        "environment": "staging",
        "conversation_config_override": {
            "agent": {
                "first_message": "Hello! This is a reminder about your appointment tomorrow.",
                "language": "en"
            },
            "tts": {
                "voice_id": "JBFqnCBsd6RMkjVDRZzb"
            }
        },
        "dynamic_variables": {
            "customer_name": "John",
            "appointment_time": "2:00 PM"
        }
    }
)
```

### JavaScript

```javascript
const response = await client.conversationalAi.twilio.outboundCall({
  agentId: "your-agent-id",
  agentPhoneNumberId: "your-phone-number-id",
  toNumber: "+1234567890",
  callRecordingEnabled: true,
  conversationInitiationClientData: {
    branchId: "branch_support_staging",
    environment: "staging",
    conversationConfigOverride: {
      agent: {
        firstMessage: "Hello! This is a reminder about your appointment tomorrow.",
        language: "en",
      },
      tts: {
        voiceId: "JBFqnCBsd6RMkjVDRZzb",
      },
    },
    dynamicVariables: {
      customer_name: "John",
      appointment_time: "2:00 PM",
    },
  },
});
```

## Configuration Overrides

### Agent Settings

| Option | Type | Description |
|--------|------|-------------|
| `first_message` | string | Custom greeting for this call |
| `language` | string | Language code (e.g., "en", "es", "fr") |
| `prompt` | object | Override agent prompt and LLM settings |

### TTS Settings

| Option | Type | Description |
|--------|------|-------------|
| `voice_id` | string | Voice ID to use for this call |
| `stability` | number | Voice stability (0.0-1.0) |
| `similarity_boost` | number | Voice similarity boost (0.0-1.0) |
| `speed` | number | Speech speed multiplier |

### Telephony Call Configuration

| Option | Type | Description |
|--------|------|-------------|
| `ringing_timeout_secs` | integer | How long to ring the recipient before giving up (default: `60`) |

### Dynamic Variables

Pass custom data to your agent's prompt using `dynamic_variables`. Reference them in your agent's prompt with `{{variable_name}}` syntax.

### Branch and Environment Routing

Use `branch_id` inside `conversation_initiation_client_data` for per-call branch routing on
Twilio, Exotel, or SIP trunk outbound calls. Use `environment` alongside it when the call should resolve
workspace environment variables against a non-default deployment target such as `staging` or
`production`.

When assigning dynamic variables, you can use the `sanitize` option to remove sensitive values from tool responses before they are sent to the LLM and transcript, while still allowing variable assignment:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sanitize` | boolean | `false` | If true, the assignment's value is removed from tool responses before sending to LLM/transcript but still processed for variable assignment |

## Complete Example

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

# Make personalized outbound calls
customers = [
    {"name": "Alice", "phone": "+1234567890", "balance": "$150.00"},
    {"name": "Bob", "phone": "+0987654321", "balance": "$75.50"},
]

for customer in customers:
    try:
        response = client.conversational_ai.twilio.outbound_call(
            agent_id="payment-reminder-agent",
            agent_phone_number_id="your-phone-number-id",
            to_number=customer["phone"],
            call_recording_enabled=True,
            conversation_initiation_client_data={
                "conversation_config_override": {
                    "agent": {
                        "first_message": f"Hello {customer['name']}, this is a friendly reminder about your account."
                    }
                },
                "dynamic_variables": {
                    "customer_name": customer["name"],
                    "balance": customer["balance"]
                }
            }
        )
        print(f"Called {customer['name']}: {response.conversation_id}")
    except Exception as e:
        print(f"Failed to call {customer['name']}: {e}")
```
