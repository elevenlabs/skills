# Installation Guide

Complete setup for Telnyx telephony with ElevenLabs voice agents.

## Prerequisites

- A [Telnyx account](https://telnyx.com/sign-up) (free to create)
- An [ElevenLabs account](https://elevenlabs.io) with an agent created
- A server capable of receiving webhooks (for call handling)

## Step 1: Get Your Telnyx API Key

1. Log into the [Telnyx Portal](https://portal.telnyx.com)
2. Navigate to **Auth** > **API Keys**
3. Create a new API v2 key
4. Save it securely:

```bash
export TELNYX_API_KEY="KEY017..."
```

## Step 2: Purchase a Phone Number

### Via Portal

1. Go to **Numbers** > **Search & Buy**
2. Select your country and features (Voice, SMS if needed)
3. Purchase the number

### Via API

```bash
# Search available numbers
curl -X GET "https://api.telnyx.com/v2/available_phone_numbers" \
  -H "Authorization: Bearer $TELNYX_API_KEY" \
  -G \
  --data-urlencode "filter[country_code]=US" \
  --data-urlencode "filter[features][]=voice" \
  --data-urlencode "filter[limit]=5"

# Purchase (replace with actual number from search)
curl -X POST "https://api.telnyx.com/v2/number_orders" \
  -H "Authorization: Bearer $TELNYX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"phone_numbers": [{"phone_number": "+12025551234"}]}'
```

## Step 3: Create a TeXML Application

TeXML applications define how Telnyx handles your calls.

### Via Portal

1. Go to **Voice** > **TeXML**
2. Click **Add New App**
3. Configure:
   - **Name**: ElevenLabs Voice Agent
   - **Voice URL**: `https://your-server.com/texml/incoming`
   - **Voice Method**: POST

### Via API

```bash
curl -X POST "https://api.telnyx.com/v2/texml_applications" \
  -H "Authorization: Bearer $TELNYX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "friendly_name": "ElevenLabs Voice Agent",
    "voice_url": "https://your-server.com/texml/incoming",
    "voice_method": "POST",
    "status_callback_url": "https://your-server.com/texml/status",
    "status_callback_method": "POST"
  }'
```

Save the returned `id` - you'll need it to assign phone numbers.

## Step 4: Assign Number to Application

Link your phone number to the TeXML application:

```bash
# Get your number's ID
curl -X GET "https://api.telnyx.com/v2/phone_numbers?filter[phone_number]=+12025551234" \
  -H "Authorization: Bearer $TELNYX_API_KEY"

# Update the number to use your TeXML app
curl -X PATCH "https://api.telnyx.com/v2/phone_numbers/{number_id}" \
  -H "Authorization: Bearer $TELNYX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"connection_id": "your-texml-app-id"}'
```

## Step 5: Set Up Your Server

You need a publicly accessible server to receive webhooks. Options:

- **Production**: Deploy to any cloud provider (AWS, GCP, Vercel, Railway)
- **Development**: Use [ngrok](https://ngrok.com) for local testing

### Minimal Flask Server

```python
from flask import Flask, request, Response
import os

app = Flask(__name__)

@app.route("/texml/incoming", methods=["POST"])
def incoming_call():
    # Log the incoming call details
    caller = request.form.get("From", "Unknown")
    print(f"Incoming call from: {caller}")
    
    # Return TeXML to handle the call
    texml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Hello! Connecting you now.</Say>
    <Pause length="1"/>
</Response>"""
    return Response(texml, mimetype="application/xml")

@app.route("/texml/status", methods=["POST"])
def call_status():
    # Handle call status updates
    status = request.form.get("CallStatus")
    print(f"Call status: {status}")
    return "", 200

if __name__ == "__main__":
    app.run(port=5000)
```

### Test with ngrok

```bash
# Terminal 1: Run your server
python server.py

# Terminal 2: Expose via ngrok
ngrok http 5000

# Update your TeXML app's voice_url to the ngrok URL
```

## Step 6: Configure ElevenLabs Agent

Ensure your ElevenLabs agent is set up for phone conversations:

1. Go to [ElevenLabs Conversational AI](https://elevenlabs.io/app/conversational-ai)
2. Create or select an agent
3. Note the **Agent ID** for use in your integration
4. Configure the agent's system prompt for phone interactions

## Verification

Test your setup:

1. Call your Telnyx number
2. You should hear the greeting from your TeXML response
3. Check your server logs for the incoming call webhook

Once verified, proceed to [Inbound Calls](inbound-calls.md) to connect calls to ElevenLabs.

## SDK Installation

### Python

```bash
pip install telnyx
```

```python
import telnyx
telnyx.api_key = os.environ["TELNYX_API_KEY"]
```

### JavaScript

```bash
npm install telnyx
```

```javascript
const Telnyx = require("telnyx");
const telnyx = Telnyx(process.env.TELNYX_API_KEY);
```

## Troubleshooting

**Webhooks not received?**
- Verify your URL is publicly accessible
- Check Telnyx Portal > Logs for webhook delivery status
- Ensure your server responds with 200 status

**Number not working?**
- Confirm the number is assigned to your TeXML application
- Check that the number is active (not pending or suspended)

**API authentication errors?**
- Use API v2 key (starts with `KEY`)
- Include `Bearer` prefix in Authorization header
