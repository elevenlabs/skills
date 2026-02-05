---
name: telnyx-telephony
description: Connect ElevenLabs voice AI agents to phone networks via Telnyx. Use when adding inbound/outbound calling, SMS follow-ups, or building production telephony for voice agents. Alternative to Twilio with lower latency and carrier-grade infrastructure.
license: MIT
compatibility: Requires internet access, a Telnyx account, and API key (TELNYX_API_KEY). Works with ElevenLabs agents.
metadata: {"openclaw": {"requires": {"env": ["TELNYX_API_KEY", "ELEVENLABS_API_KEY"]}, "primaryEnv": "TELNYX_API_KEY"}}
---

# Telnyx Telephony for ElevenLabs Agents

Connect your ElevenLabs voice AI agents to real phone numbers using Telnyx's carrier-grade telephony platform.

> **Why Telnyx?** Own network infrastructure means lower latency than aggregators. Global coverage, competitive pricing, and full SIP/WebRTC flexibility for production deployments.

## Quick Start

### 1. Get Your API Keys

```bash
# Telnyx: https://portal.telnyx.com/#/app/api-keys
export TELNYX_API_KEY="KEY..."

# ElevenLabs: https://elevenlabs.io/app/settings/api-keys
export ELEVENLABS_API_KEY="sk_..."
```

### 2. Buy a Phone Number

```bash
# Search for available numbers
curl -X GET "https://api.telnyx.com/v2/available_phone_numbers?filter[country_code]=US&filter[features][]=voice" \
  -H "Authorization: Bearer $TELNYX_API_KEY"

# Purchase a number
curl -X POST "https://api.telnyx.com/v2/number_orders" \
  -H "Authorization: Bearer $TELNYX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"phone_numbers": [{"phone_number": "+12025551234"}]}'
```

### 3. Create a TeXML Application

TeXML applications handle incoming calls and route them to your ElevenLabs agent:

```bash
curl -X POST "https://api.telnyx.com/v2/texml_applications" \
  -H "Authorization: Bearer $TELNYX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "friendly_name": "ElevenLabs Voice Agent",
    "voice_url": "https://your-server.com/texml/incoming",
    "voice_method": "POST"
  }'
```

### 4. Handle Incoming Calls

Your webhook receives calls and connects them to ElevenLabs via WebSocket:

```python
from flask import Flask, Response
import os

app = Flask(__name__)

ELEVENLABS_AGENT_ID = "your-agent-id"

@app.route("/texml/incoming", methods=["POST"])
def handle_incoming():
    # Get signed WebSocket URL from ElevenLabs
    # Then stream audio bidirectionally
    texml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Connecting you to our AI assistant.</Say>
    <Connect>
        <Stream url="wss://api.elevenlabs.io/v1/convai/conversation?agent_id={ELEVENLABS_AGENT_ID}" />
    </Connect>
</Response>"""
    return Response(texml, mimetype="application/xml")
```

See [Inbound Calls Reference](references/inbound-calls.md) for complete implementation with audio streaming.

## Outbound Calls

Initiate calls from your ElevenLabs agent to any phone number:

### Python

```python
import telnyx

telnyx.api_key = os.environ["TELNYX_API_KEY"]

# Start an outbound call
call = telnyx.Call.create(
    connection_id="your-texml-app-id",
    to="+12025559876",
    from_="+12025551234",  # Your Telnyx number
    webhook_url="https://your-server.com/texml/outbound"
)
print(f"Call started: {call.call_control_id}")
```

### JavaScript

```javascript
const Telnyx = require("telnyx");
const telnyx = Telnyx(process.env.TELNYX_API_KEY);

const call = await telnyx.calls.create({
  connection_id: "your-texml-app-id",
  to: "+12025559876",
  from: "+12025551234",
  webhook_url: "https://your-server.com/texml/outbound"
});
```

See [Outbound Calls Reference](references/outbound-calls.md) for handling answer events and streaming to ElevenLabs.

## SMS Follow-ups

Send conversation summaries or follow-up messages after calls:

```python
import telnyx

# Send SMS with conversation summary
message = telnyx.Message.create(
    from_="+12025551234",  # Your Telnyx number (SMS-enabled)
    to="+12025559876",
    text="Thanks for calling! Here's a summary of our conversation..."
)
```

See [SMS Integration Reference](references/sms-integration.md) for webhook-triggered follow-ups.

## Why Telnyx over Twilio?

| Feature | Telnyx | Twilio |
|---------|--------|--------|
| Network | Own global infrastructure | Aggregator |
| Latency | Lower (direct routes) | Higher (extra hops) |
| Pricing | ~40-60% lower | Premium pricing |
| SIP Control | Full access | Limited |
| Number Porting | Free | Often charged |

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELNYX_API_KEY` | Yes | API v2 key from Telnyx Portal |
| `ELEVENLABS_API_KEY` | Yes | ElevenLabs API key |
| `TELNYX_PUBLIC_KEY` | No | For webhook signature verification |

### TeXML Application Settings

Configure your TeXML app in the [Telnyx Portal](https://portal.telnyx.com/#/app/call-control/texml):

- **Voice URL**: Your server endpoint for incoming calls
- **Status Callback URL**: For call events (answered, ended, etc.)
- **Fallback URL**: Backup endpoint if primary fails

## References

- [Installation Guide](references/installation.md) - Complete setup walkthrough
- [Inbound Calls](references/inbound-calls.md) - Receiving calls and routing to ElevenLabs
- [Outbound Calls](references/outbound-calls.md) - Initiating calls from your agent
- [SMS Integration](references/sms-integration.md) - Follow-up messaging
- [Telnyx API Docs](https://developers.telnyx.com) - Full API reference
