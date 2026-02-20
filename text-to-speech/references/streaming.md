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

audio_stream = client.text_to_speech.stream(
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

audio_stream = client.text_to_speech.stream(
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

For text-streaming input where you send text chunks as they arrive (e.g., from an LLM).

### Connection

```
wss://api.elevenlabs.io/v1/text-to-speech/{voiceId}/stream-input?model_id={modelId}
```

**Note:** WebSockets are unavailable for the `eleven_v3` model. Use `eleven_flash_v2_5` for lowest latency.

### Message Flow

1. **Initialize** - Send voice settings and configuration
2. **Send text** - Stream text chunks as they arrive
3. **Close** - Send empty string to signal completion
4. **Receive** - Process audio chunks as they're generated

### Python WebSocket

```python
import asyncio
import json
import base64
import os
import websockets
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

async def text_to_speech_ws_streaming(voice_id: str, model_id: str):
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id={model_id}"

    async with websockets.connect(uri) as websocket:
        # Initialize connection
        await websocket.send(json.dumps({
            "text": " ",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8
            },
            "generation_config": {
                "chunk_length_schedule": [120, 160, 250, 290]
            },
            "xi_api_key": ELEVENLABS_API_KEY
        }))

        # Send text chunks
        await websocket.send(json.dumps({"text": "Hello, "}))
        await websocket.send(json.dumps({"text": "this is streaming text "}))
        await websocket.send(json.dumps({"text": "from a WebSocket connection."}))

        # Close stream (empty text signals completion)
        await websocket.send(json.dumps({"text": ""}))

        # Receive and process audio chunks
        audio_chunks = []
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            if data.get("audio"):
                audio_chunks.append(base64.b64decode(data["audio"]))
            elif data.get("isFinal"):
                break

        return b"".join(audio_chunks)

async def main():
    audio = await text_to_speech_ws_streaming(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_flash_v2_5"
    )
    with open("output.mp3", "wb") as f:
        f.write(audio)

if __name__ == "__main__":
    asyncio.run(main())
```

### JavaScript WebSocket

```javascript
import "dotenv/config";
import WebSocket from "ws";
import * as fs from "node:fs";

const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;

async function textToSpeechWsStreaming(voiceId, modelId) {
  const uri = `wss://api.elevenlabs.io/v1/text-to-speech/${voiceId}/stream-input?model_id=${modelId}`;

  return new Promise((resolve, reject) => {
    const websocket = new WebSocket(uri, {
      headers: { "xi-api-key": ELEVENLABS_API_KEY },
    });

    const audioChunks = [];

    websocket.on("open", () => {
      // Initialize connection
      websocket.send(
        JSON.stringify({
          text: " ",
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.8,
          },
          generation_config: {
            chunk_length_schedule: [120, 160, 250, 290],
          },
        })
      );

      // Send text chunks
      websocket.send(JSON.stringify({ text: "Hello, " }));
      websocket.send(JSON.stringify({ text: "this is streaming text " }));
      websocket.send(JSON.stringify({ text: "from a WebSocket connection." }));

      // Close stream
      websocket.send(JSON.stringify({ text: "" }));
    });

    websocket.on("message", (event) => {
      const data = JSON.parse(event.toString());
      if (data.audio) {
        audioChunks.push(Buffer.from(data.audio, "base64"));
      } else if (data.isFinal) {
        websocket.close();
        resolve(Buffer.concat(audioChunks));
      }
    });

    websocket.on("error", reject);
  });
}

const audio = await textToSpeechWsStreaming(
  "JBFqnCBsd6RMkjVDRZzb",
  "eleven_flash_v2_5"
);
fs.writeFileSync("output.mp3", audio);
```

### Input Messages

**Initialization (first message):**

```json
{
  "text": " ",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.8,
    "use_speaker_boost": false
  },
  "generation_config": {
    "chunk_length_schedule": [120, 160, 250, 290]
  },
  "xi_api_key": "your_api_key"
}
```

**Text chunks:**

```json
{ "text": "Your text content here" }
```

**Force flush (generate audio immediately):**

```json
{ "text": "End of sentence.", "flush": true }
```

**Close connection:**

```json
{ "text": "" }
```

### Output Messages

**Audio chunk:**

```json
{
  "audio": "base64_encoded_audio_data"
}
```

**Stream complete:**

```json
{
  "isFinal": true
}
```

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| `chunk_length_schedule` | Array of character counts that trigger audio generation. The model waits until it has this many characters before generating audio, which improves quality but adds latency. Lower values = faster response, higher values = better prosody. Example: `[120, 160, 250, 290]` means generate after 120 chars, then after 160 more, etc. |
| `flush` | Set `true` to force immediate audio generation without waiting for the character threshold. Use at the end of sentences or when you need audio NOW. |
| `voice_settings` | Adjustable per-message: `stability`, `similarity_boost`, `use_speaker_boost` |

### Important Notes

- **Inactivity timeout**: Connection closes after 20 seconds without activity. Send a space `" "` to keep alive.
- **TTFB (Time to First Byte)**: How long until audio starts playing. Affected by `chunk_length_schedule` - the model waits for enough text before generating.
- **Model limitation**: WebSockets are unavailable for `eleven_v3`.
- **Best practice**: Use `flush: true` at conversation turn endings to ensure the buffered text gets spoken.
- **Alignment data**: Word-level timestamps available via `alignment` field for lip-sync or captions.

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
