# SMS Integration

Send SMS messages as follow-ups to voice conversations with ElevenLabs agents.

## Use Cases

- Send conversation summaries after calls
- Share links or confirmation numbers mentioned during calls
- Follow-up with additional information
- Appointment confirmations

## Prerequisites

Your Telnyx phone number must be SMS-enabled. Check in the [Telnyx Portal](https://portal.telnyx.com) under **Numbers** > **My Numbers**.

## Basic SMS Sending

### Python

```python
import telnyx
import os

telnyx.api_key = os.environ["TELNYX_API_KEY"]

def send_sms(to_number: str, from_number: str, message: str):
    """
    Send an SMS message.
    
    Args:
        to_number: Recipient phone number (E.164 format)
        from_number: Your Telnyx SMS-enabled number
        message: Message content (max 1600 characters)
    """
    
    response = telnyx.Message.create(
        from_=from_number,
        to=to_number,
        text=message
    )
    
    print(f"SMS sent: {response.id}")
    return response.id


# Example usage
send_sms(
    to_number="+12025559876",
    from_number="+12025551234",
    message="Thanks for calling! Your appointment is confirmed for tomorrow at 2pm."
)
```

### JavaScript

```javascript
const Telnyx = require("telnyx");
const telnyx = Telnyx(process.env.TELNYX_API_KEY);

async function sendSms(toNumber, fromNumber, message) {
  const response = await telnyx.messages.create({
    from: fromNumber,
    to: toNumber,
    text: message
  });
  
  console.log(`SMS sent: ${response.data.id}`);
  return response.data.id;
}

// Example usage
sendSms(
  "+12025559876",
  "+12025551234",
  "Thanks for calling! Your appointment is confirmed."
);
```

### cURL

```bash
curl -X POST "https://api.telnyx.com/v2/messages" \
  -H "Authorization: Bearer $TELNYX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+12025551234",
    "to": "+12025559876",
    "text": "Thanks for calling! Your appointment is confirmed for tomorrow at 2pm."
  }'
```

## Post-Call SMS Follow-up

Send SMS automatically when a call ends:

```python
from flask import Flask, request
import telnyx

app = Flask(__name__)
telnyx.api_key = os.environ["TELNYX_API_KEY"]

@app.route("/texml/status", methods=["POST"])
def call_status():
    """Handle call status webhooks and send follow-up SMS."""
    
    event_type = request.form.get("CallStatus") or request.json.get("data", {}).get("event_type")
    
    if event_type in ["completed", "call.hangup"]:
        caller_number = request.form.get("From") or request.json.get("data", {}).get("payload", {}).get("from")
        call_duration = request.form.get("CallDuration", "0")
        
        # Only send follow-up for calls longer than 30 seconds
        if int(call_duration) > 30:
            send_followup_sms(caller_number)
    
    return "", 200


def send_followup_sms(phone_number: str):
    """Send a follow-up SMS after the call."""
    
    message = """Thanks for speaking with our AI assistant today! 

Here's a summary of what we discussed:
- Your appointment is confirmed
- Reference number: #12345

Reply to this message if you have any questions."""
    
    telnyx.Message.create(
        from_=os.environ["TELNYX_FROM_NUMBER"],
        to=phone_number,
        text=message
    )
```

## Conversation Summary via Webhook

If your ElevenLabs agent sends conversation data to a webhook, use it for personalized SMS:

```python
@app.route("/elevenlabs/conversation-ended", methods=["POST"])
def conversation_ended():
    """Handle ElevenLabs conversation end webhook."""
    
    data = request.json
    
    # Extract relevant info from the conversation
    phone_number = data.get("metadata", {}).get("caller_phone")
    summary = data.get("analysis", {}).get("summary", "")
    action_items = data.get("analysis", {}).get("action_items", [])
    
    if phone_number and summary:
        # Build follow-up message
        message = f"Call Summary:\n{summary}\n"
        
        if action_items:
            message += "\nNext steps:\n"
            for item in action_items:
                message += f"• {item}\n"
        
        send_sms(
            to_number=phone_number,
            from_number=os.environ["TELNYX_FROM_NUMBER"],
            message=message[:1600]  # SMS character limit
        )
    
    return "", 200
```

## MMS: Send Images and Media

Send images, PDFs, or other media:

```python
def send_mms(to_number: str, from_number: str, message: str, media_urls: list):
    """
    Send an MMS with media attachments.
    
    Args:
        media_urls: List of publicly accessible media URLs
    """
    
    response = telnyx.Message.create(
        from_=from_number,
        to=to_number,
        text=message,
        media_urls=media_urls
    )
    
    return response.id


# Example: Send appointment confirmation with calendar invite
send_mms(
    to_number="+12025559876",
    from_number="+12025551234",
    message="Here's your appointment confirmation:",
    media_urls=["https://your-server.com/calendar/appointment-12345.ics"]
)
```

## Two-Way SMS Conversations

Handle incoming SMS replies:

```python
@app.route("/sms/incoming", methods=["POST"])
def handle_incoming_sms():
    """Handle incoming SMS messages."""
    
    data = request.json.get("data", {}).get("payload", {})
    
    from_number = data.get("from", {}).get("phone_number")
    to_number = data.get("to", [{}])[0].get("phone_number")
    message_text = data.get("text", "")
    
    print(f"SMS from {from_number}: {message_text}")
    
    # Auto-reply logic
    reply = generate_auto_reply(message_text)
    
    if reply:
        send_sms(
            to_number=from_number,
            from_number=to_number,
            message=reply
        )
    
    return "", 200


def generate_auto_reply(incoming_message: str) -> str:
    """Generate automatic reply based on incoming message."""
    
    message_lower = incoming_message.lower()
    
    if "confirm" in message_lower:
        return "Great! Your appointment is confirmed. See you then!"
    elif "cancel" in message_lower:
        return "Your appointment has been cancelled. Reply RESCHEDULE to book a new time."
    elif "help" in message_lower:
        return "Reply CONFIRM to confirm, CANCEL to cancel, or call us at +12025551234."
    
    return None  # No auto-reply for unrecognized messages
```

## Configure SMS Webhook

Set up your Telnyx number to receive incoming SMS:

```bash
# Get your messaging profile ID
curl -X GET "https://api.telnyx.com/v2/messaging_profiles" \
  -H "Authorization: Bearer $TELNYX_API_KEY"

# Update the profile with your webhook URL
curl -X PATCH "https://api.telnyx.com/v2/messaging_profiles/{profile_id}" \
  -H "Authorization: Bearer $TELNYX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_url": "https://your-server.com/sms/incoming",
    "webhook_api_version": "2"
  }'
```

## Rate Limiting and Best Practices

```python
import time
from collections import deque
from datetime import datetime, timedelta

class SMSRateLimiter:
    """Simple rate limiter for SMS sending."""
    
    def __init__(self, max_per_second: int = 1):
        self.max_per_second = max_per_second
        self.timestamps = deque()
    
    def wait_if_needed(self):
        """Block if we're sending too fast."""
        now = datetime.now()
        
        # Remove timestamps older than 1 second
        while self.timestamps and self.timestamps[0] < now - timedelta(seconds=1):
            self.timestamps.popleft()
        
        # Wait if at rate limit
        if len(self.timestamps) >= self.max_per_second:
            sleep_time = (self.timestamps[0] + timedelta(seconds=1) - now).total_seconds()
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.timestamps.append(now)


# Usage
rate_limiter = SMSRateLimiter(max_per_second=1)

def send_sms_rate_limited(to_number: str, from_number: str, message: str):
    rate_limiter.wait_if_needed()
    return send_sms(to_number, from_number, message)
```

## Character Limits and Concatenation

- Standard SMS: 160 characters (GSM-7 encoding)
- Unicode SMS: 70 characters
- Telnyx auto-concatenates up to 1600 characters
- Concatenated messages are billed as multiple segments

```python
def estimate_sms_segments(message: str) -> int:
    """Estimate number of SMS segments for billing."""
    
    # Check if message contains non-GSM characters
    gsm_chars = set('@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ !"#¤%&\'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà')
    is_unicode = not all(c in gsm_chars for c in message)
    
    if is_unicode:
        # Unicode: 70 chars per segment, 67 if concatenated
        if len(message) <= 70:
            return 1
        return (len(message) + 66) // 67
    else:
        # GSM-7: 160 chars per segment, 153 if concatenated
        if len(message) <= 160:
            return 1
        return (len(message) + 152) // 153


# Example
message = "Thanks for calling! Your appointment is confirmed."
segments = estimate_sms_segments(message)
print(f"Message will use {segments} SMS segment(s)")
```

## Next Steps

- [Inbound Calls](inbound-calls.md) - Handle incoming voice calls
- [Outbound Calls](outbound-calls.md) - Initiate calls from your agent
