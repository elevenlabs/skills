# Outbound Calls

Make outbound phone calls using your ElevenLabs agent via Twilio integration.

## Prerequisites

1. A configured ElevenLabs agent
2. A Twilio phone number linked to your agent (obtain `agent_phone_number_id` from ElevenLabs dashboard)
3. Your ElevenLabs API key

## Basic Usage

See the [main agents skill](../SKILL.md#outbound-calls) for basic Python, JavaScript, and cURL examples.

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | The ID of your ElevenLabs agent |
| `agent_phone_number_id` | string | Yes | The ID of the Twilio phone number linked to your agent |
| `to_number` | string | Yes | The destination phone number (E.164 format) |
| `conversation_initiation_client_data` | object | No | Override conversation settings for this call |

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
| `callSid` | string | Twilio Call SID for reference |

## Customizing the Call

Override agent settings for a specific call using `conversation_initiation_client_data`:

### Python

```python
response = client.conversational_ai.twilio.outbound_call(
    agent_id="your-agent-id",
    agent_phone_number_id="your-phone-number-id",
    to_number="+1234567890",
    conversation_initiation_client_data={
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
  conversationInitiationClientData: {
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

### Dynamic Variables

Pass custom data to your agent's prompt using `dynamic_variables`. Reference them in your agent's prompt with `{{variable_name}}` syntax.

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
