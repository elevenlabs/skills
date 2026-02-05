# Inbound Calls

Handle incoming phone calls and route them to your ElevenLabs voice AI agent.

## Architecture

```
Caller → Telnyx Number → TeXML Webhook → Your Server → ElevenLabs Agent
                                              ↓
                                    Bidirectional Audio Stream
```

## Basic Implementation

### Python (Flask)

```python
from flask import Flask, request, Response
import requests
import os

app = Flask(__name__)

ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
ELEVENLABS_AGENT_ID = os.environ.get("ELEVENLABS_AGENT_ID", "your-agent-id")

@app.route("/texml/incoming", methods=["POST"])
def handle_incoming():
    """Handle incoming calls and connect to ElevenLabs agent."""
    
    caller_number = request.form.get("From", "Unknown")
    call_sid = request.form.get("CallSid")
    
    print(f"Incoming call from {caller_number}, SID: {call_sid}")
    
    # Get signed WebSocket URL from ElevenLabs
    signed_url = get_elevenlabs_signed_url()
    
    # TeXML response with streaming to ElevenLabs
    texml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Please wait while I connect you to our AI assistant.</Say>
    <Connect>
        <Stream url="{signed_url}" />
    </Connect>
</Response>"""
    
    return Response(texml, mimetype="application/xml")


def get_elevenlabs_signed_url():
    """Get a signed WebSocket URL for the ElevenLabs agent."""
    
    response = requests.post(
        f"https://api.elevenlabs.io/v1/convai/conversation/get-signed-url",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={"agent_id": ELEVENLABS_AGENT_ID}
    )
    response.raise_for_status()
    return response.json()["signed_url"]


@app.route("/texml/status", methods=["POST"])
def call_status():
    """Handle call status webhooks."""
    
    status = request.form.get("CallStatus")
    duration = request.form.get("CallDuration", "0")
    
    print(f"Call ended with status: {status}, duration: {duration}s")
    
    # Optionally trigger follow-up actions here
    # e.g., send SMS summary, log to database, etc.
    
    return "", 200


if __name__ == "__main__":
    app.run(port=5000)
```

### JavaScript (Express)

```javascript
const express = require("express");
const axios = require("axios");

const app = express();
app.use(express.urlencoded({ extended: true }));

const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;
const ELEVENLABS_AGENT_ID = process.env.ELEVENLABS_AGENT_ID || "your-agent-id";

app.post("/texml/incoming", async (req, res) => {
  const callerNumber = req.body.From || "Unknown";
  const callSid = req.body.CallSid;
  
  console.log(`Incoming call from ${callerNumber}, SID: ${callSid}`);
  
  // Get signed WebSocket URL from ElevenLabs
  const signedUrl = await getElevenLabsSignedUrl();
  
  const texml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Please wait while I connect you to our AI assistant.</Say>
    <Connect>
        <Stream url="${signedUrl}" />
    </Connect>
</Response>`;
  
  res.type("application/xml").send(texml);
});

async function getElevenLabsSignedUrl() {
  const response = await axios.post(
    "https://api.elevenlabs.io/v1/convai/conversation/get-signed-url",
    { agent_id: ELEVENLABS_AGENT_ID },
    {
      headers: {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
      }
    }
  );
  return response.data.signed_url;
}

app.post("/texml/status", (req, res) => {
  const status = req.body.CallStatus;
  console.log(`Call status: ${status}`);
  res.sendStatus(200);
});

app.listen(5000, () => console.log("Server running on port 5000"));
```

## Advanced: Custom Greeting Based on Caller

Personalize the experience using caller ID lookup:

```python
@app.route("/texml/incoming", methods=["POST"])
def handle_incoming():
    caller_number = request.form.get("From")
    
    # Look up caller in your database
    caller_name = lookup_caller(caller_number)
    
    if caller_name:
        greeting = f"Hello {caller_name}! Let me connect you to your assistant."
    else:
        greeting = "Welcome! Let me connect you to our AI assistant."
    
    signed_url = get_elevenlabs_signed_url()
    
    texml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{greeting}</Say>
    <Connect>
        <Stream url="{signed_url}" />
    </Connect>
</Response>"""
    
    return Response(texml, mimetype="application/xml")
```

## Advanced: Pass Context to ElevenLabs

Send caller information to your ElevenLabs agent via dynamic variables:

```python
def get_elevenlabs_signed_url_with_context(caller_number, caller_name=None):
    """Get signed URL with caller context."""
    
    response = requests.post(
        f"https://api.elevenlabs.io/v1/convai/conversation/get-signed-url",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "agent_id": ELEVENLABS_AGENT_ID,
            "dynamic_variables": {
                "caller_phone": caller_number,
                "caller_name": caller_name or "Guest"
            }
        }
    )
    response.raise_for_status()
    return response.json()["signed_url"]
```

Then reference these in your ElevenLabs agent prompt:
```
The caller's name is {{caller_name}} and their phone number is {{caller_phone}}.
```

## Call Recording

Enable call recording in your TeXML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Record 
        action="/texml/recording-complete"
        recordingStatusCallback="/texml/recording-status"
        maxLength="3600"
        playBeep="false"
    />
    <Say>This call may be recorded for quality purposes.</Say>
    <Connect>
        <Stream url="{signed_url}" />
    </Connect>
</Response>
```

## Error Handling

Handle cases where ElevenLabs is unavailable:

```python
@app.route("/texml/incoming", methods=["POST"])
def handle_incoming():
    try:
        signed_url = get_elevenlabs_signed_url()
        
        texml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Connecting you now.</Say>
    <Connect>
        <Stream url="{signed_url}" />
    </Connect>
</Response>"""
    
    except Exception as e:
        print(f"Error getting ElevenLabs URL: {e}")
        
        # Fallback: take a message or transfer to human
        texml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>We're experiencing technical difficulties. Please leave a message after the beep.</Say>
    <Record maxLength="120" action="/texml/voicemail" />
</Response>"""
    
    return Response(texml, mimetype="application/xml")
```

## Webhook Security

Verify that webhooks are actually from Telnyx:

```python
import hmac
import hashlib
import base64

TELNYX_PUBLIC_KEY = os.environ.get("TELNYX_PUBLIC_KEY")

def verify_telnyx_signature(request):
    """Verify the webhook signature from Telnyx."""
    
    signature = request.headers.get("telnyx-signature-ed25519")
    timestamp = request.headers.get("telnyx-timestamp")
    
    if not signature or not timestamp:
        return False
    
    # Verify signature using Telnyx public key
    # See: https://developers.telnyx.com/docs/v2/development/api-guide/webhooks
    
    return True  # Implement full verification
```

## Next Steps

- [Outbound Calls](outbound-calls.md) - Initiate calls from your agent
- [SMS Integration](sms-integration.md) - Send follow-up messages after calls
