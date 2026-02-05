# Outbound Calls

Initiate phone calls from your ElevenLabs voice AI agent using Telnyx.

## Use Cases

- Appointment reminders with AI confirmation
- Proactive customer outreach
- Automated follow-up calls
- Survey and feedback collection

## Basic Implementation

### Python

```python
import telnyx
import os

telnyx.api_key = os.environ["TELNYX_API_KEY"]

def make_outbound_call(to_number: str, from_number: str, webhook_url: str):
    """
    Initiate an outbound call that connects to ElevenLabs agent.
    
    Args:
        to_number: Destination phone number (E.164 format)
        from_number: Your Telnyx phone number
        webhook_url: URL to handle the call when answered
    """
    
    call = telnyx.Call.create(
        connection_id=os.environ["TELNYX_CONNECTION_ID"],
        to=to_number,
        from_=from_number,
        webhook_url=webhook_url,
        webhook_url_method="POST"
    )
    
    print(f"Call initiated: {call.call_control_id}")
    return call.call_control_id


# Example usage
call_id = make_outbound_call(
    to_number="+12025559876",
    from_number="+12025551234",
    webhook_url="https://your-server.com/texml/outbound"
)
```

### JavaScript

```javascript
const Telnyx = require("telnyx");
const telnyx = Telnyx(process.env.TELNYX_API_KEY);

async function makeOutboundCall(toNumber, fromNumber, webhookUrl) {
  const call = await telnyx.calls.create({
    connection_id: process.env.TELNYX_CONNECTION_ID,
    to: toNumber,
    from: fromNumber,
    webhook_url: webhookUrl,
    webhook_url_method: "POST"
  });
  
  console.log(`Call initiated: ${call.data.call_control_id}`);
  return call.data.call_control_id;
}

// Example usage
makeOutboundCall(
  "+12025559876",
  "+12025551234",
  "https://your-server.com/texml/outbound"
);
```

### cURL

```bash
curl -X POST "https://api.telnyx.com/v2/calls" \
  -H "Authorization: Bearer $TELNYX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "your-connection-id",
    "to": "+12025559876",
    "from": "+12025551234",
    "webhook_url": "https://your-server.com/texml/outbound",
    "webhook_url_method": "POST"
  }'
```

## Handling the Answered Call

When the call is answered, Telnyx sends a webhook. Connect to ElevenLabs:

### Python (Flask)

```python
from flask import Flask, request, Response
import requests

app = Flask(__name__)

ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
ELEVENLABS_AGENT_ID = os.environ["ELEVENLABS_AGENT_ID"]

@app.route("/texml/outbound", methods=["POST"])
def handle_outbound():
    """Handle outbound call when answered."""
    
    event_type = request.form.get("Event", request.json.get("data", {}).get("event_type"))
    
    # Check if call was answered
    if event_type == "call.answered":
        # Get signed URL from ElevenLabs
        signed_url = get_elevenlabs_signed_url()
        
        texml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Hello! This is an automated call from your AI assistant.</Say>
    <Pause length="1"/>
    <Connect>
        <Stream url="{signed_url}" />
    </Connect>
</Response>"""
        
        return Response(texml, mimetype="application/xml")
    
    elif event_type == "call.hangup":
        print("Call ended")
        return "", 200
    
    elif event_type == "call.machine.detection.ended":
        # Handle voicemail detection
        result = request.json.get("data", {}).get("payload", {}).get("result")
        if result == "machine":
            return handle_voicemail()
    
    return "", 200


def get_elevenlabs_signed_url():
    response = requests.post(
        "https://api.elevenlabs.io/v1/convai/conversation/get-signed-url",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={"agent_id": ELEVENLABS_AGENT_ID}
    )
    response.raise_for_status()
    return response.json()["signed_url"]


def handle_voicemail():
    """Leave a message if voicemail is detected."""
    texml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Hello, this is a message from your AI assistant. Please call us back at your convenience.</Say>
    <Hangup/>
</Response>"""
    return Response(texml, mimetype="application/xml")
```

## Answering Machine Detection

Detect voicemail vs. human answer:

```python
def make_outbound_call_with_amd(to_number: str, from_number: str, webhook_url: str):
    """Make call with answering machine detection."""
    
    call = telnyx.Call.create(
        connection_id=os.environ["TELNYX_CONNECTION_ID"],
        to=to_number,
        from_=from_number,
        webhook_url=webhook_url,
        answering_machine_detection="detect",
        answering_machine_detection_config={
            "after_greeting_silence_millis": 800,
            "between_words_silence_millis": 50,
            "greeting_duration_millis": 3500,
            "initial_silence_millis": 3500,
            "maximum_number_of_words": 5,
            "maximum_word_length_millis": 3500,
            "silence_threshold": 256,
            "total_analysis_time_millis": 5000
        }
    )
    
    return call.call_control_id
```

## Scheduled Calls

Use a task queue to schedule outbound calls:

```python
from datetime import datetime, timedelta
import schedule
import time

def schedule_reminder_call(phone_number: str, appointment_time: datetime):
    """Schedule a reminder call 1 hour before appointment."""
    
    reminder_time = appointment_time - timedelta(hours=1)
    
    def make_call():
        make_outbound_call(
            to_number=phone_number,
            from_number=os.environ["TELNYX_FROM_NUMBER"],
            webhook_url="https://your-server.com/texml/reminder"
        )
    
    # Schedule the call
    schedule.every().day.at(reminder_time.strftime("%H:%M")).do(make_call)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

## Batch Calling

Make multiple calls with rate limiting:

```python
import time
from concurrent.futures import ThreadPoolExecutor

def batch_outbound_calls(phone_numbers: list, calls_per_minute: int = 10):
    """
    Make batch outbound calls with rate limiting.
    
    Args:
        phone_numbers: List of numbers to call
        calls_per_minute: Rate limit
    """
    
    delay = 60 / calls_per_minute
    
    for number in phone_numbers:
        try:
            make_outbound_call(
                to_number=number,
                from_number=os.environ["TELNYX_FROM_NUMBER"],
                webhook_url="https://your-server.com/texml/outbound"
            )
            print(f"Called {number}")
        except Exception as e:
            print(f"Failed to call {number}: {e}")
        
        time.sleep(delay)
```

## Dynamic Agent Configuration

Pass context to ElevenLabs for personalized conversations:

```python
@app.route("/texml/outbound", methods=["POST"])
def handle_outbound():
    """Handle outbound call with dynamic context."""
    
    to_number = request.form.get("To")
    
    # Look up customer info
    customer = get_customer_by_phone(to_number)
    
    # Get signed URL with customer context
    signed_url = get_elevenlabs_signed_url_with_context(
        customer_name=customer.name,
        appointment_date=customer.next_appointment,
        account_balance=customer.balance
    )
    
    texml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{signed_url}" />
    </Connect>
</Response>"""
    
    return Response(texml, mimetype="application/xml")


def get_elevenlabs_signed_url_with_context(**kwargs):
    response = requests.post(
        "https://api.elevenlabs.io/v1/convai/conversation/get-signed-url",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "agent_id": ELEVENLABS_AGENT_ID,
            "dynamic_variables": kwargs
        }
    )
    response.raise_for_status()
    return response.json()["signed_url"]
```

## Call Control

Manage active calls programmatically:

```python
# Hangup a call
def hangup_call(call_control_id: str):
    call = telnyx.Call()
    call.call_control_id = call_control_id
    call.hangup()

# Transfer to human agent
def transfer_call(call_control_id: str, transfer_to: str):
    call = telnyx.Call()
    call.call_control_id = call_control_id
    call.transfer(to=transfer_to)

# Play audio during call
def play_audio(call_control_id: str, audio_url: str):
    call = telnyx.Call()
    call.call_control_id = call_control_id
    call.playback_start(audio_url=audio_url)
```

## Next Steps

- [SMS Integration](sms-integration.md) - Send follow-up messages after calls
- [Inbound Calls](inbound-calls.md) - Handle incoming calls
