# Streaming Audio

Stream audio chunks as they're generated for lower latency.

## Model Selection for Streaming

| Model | Latency | Use Case |
|-------|---------|----------|
| `eleven_flash_v2_5` | ~75ms | Lowest latency, 32 languages |
| `eleven_flash_v2` | ~75ms | Lowest latency, English only |
| `eleven_turbo_v2_5` | Low | Balanced quality/speed |

## Python Streaming

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio_stream = client.text_to_speech.convert(
    text="This is a streaming example with ultra-low latency.",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_flash_v2_5"
)

with open("output.mp3", "wb") as f:
    for chunk in audio_stream:
        f.write(chunk)
```

### Real-Time Playback

```python
import subprocess

def play_stream(audio_stream):
    process = subprocess.Popen(
        ["ffplay", "-nodisp", "-autoexit", "-"],
        stdin=subprocess.PIPE
    )
    for chunk in audio_stream:
        process.stdin.write(chunk)
    process.stdin.close()
    process.wait()

audio_stream = client.text_to_speech.convert(
    text="Playing this audio in real-time.",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_flash_v2_5"
)
play_stream(audio_stream)
```

## JavaScript Streaming

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createWriteStream } from "fs";

const client = new ElevenLabsClient();

const audioStream = await client.textToSpeech.convert("JBFqnCBsd6RMkjVDRZzb", {
  text: "Streaming audio in JavaScript.",
  modelId: "eleven_flash_v2_5",
});

// Write to file
const writeStream = createWriteStream("output.mp3");
audioStream.pipe(writeStream);

// Or process chunks
for await (const chunk of audioStream) {
  console.log(`Received ${chunk.length} bytes`);
}
```

## WebSocket Streaming

For text-streaming input (send text chunks as they arrive):

### Python WebSocket

```python
import asyncio
import websockets
import json
import base64
import os

async def stream_tts():
    voice_id = "JBFqnCBsd6RMkjVDRZzb"
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input"

    async with websockets.connect(
        uri,
        extra_headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]}
    ) as ws:
        # Initialize stream
        await ws.send(json.dumps({
            "text": " ",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
            "model_id": "eleven_flash_v2_5"
        }))

        # Send text chunks as they arrive
        await ws.send(json.dumps({"text": "Hello, "}))
        await ws.send(json.dumps({"text": "this is streaming. "}))

        # End stream (empty text signals completion)
        await ws.send(json.dumps({"text": ""}))

        # Receive audio chunks
        async for message in ws:
            data = json.loads(message)
            if data.get("audio"):
                audio_chunk = base64.b64decode(data["audio"])
                # Process audio chunk

asyncio.run(stream_tts())
```

## Best Practices

1. **Use Flash models** for real-time:
   - `eleven_flash_v2_5` for multilingual (~75ms)
   - `eleven_flash_v2` for English-only (~75ms)

2. **Buffer audio** before playback to prevent choppy output

3. **Handle disconnections** gracefully in WebSocket streams

4. **Choose output format based on use case**:
   - `pcm_24000` - lowest latency processing
   - `mp3_44100_128` - direct playback
   - `ulaw_8000` - telephony/Twilio integration
