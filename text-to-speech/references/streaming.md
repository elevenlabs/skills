# Streaming Audio

Stream audio chunks as they're generated for lower latency.

## Model Selection for Streaming

| Model | Latency | Transport | Use Case |
|-------|---------|-----------|----------|
| `eleven_v4` | Standard | HTTP streaming, Text to Dialogue WebSocket | Highest quality, 90+ languages |
| `eleven_v4_turbo` | ~100ms | [Text to Dialogue WebSocket](#eleven-v4-turbo-websocket) | Real-time v4 quality for agents and interactive apps |
| `eleven_flash_v2_5` | ~75ms | HTTP streaming, `stream-input` WebSocket | Lowest latency, 32 languages |
| `eleven_flash_v2` | ~75ms | HTTP streaming, `stream-input` WebSocket | Lowest latency, English only |

`eleven_turbo_v2_5` is superseded by `eleven_flash_v2_5`, which is functionally equivalent with lower latency.

## Python Streaming

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()

audio_stream = client.text_to_speech.stream(
    text="This is a streaming example.",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_v4"
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
    model_id="eleven_v4"
)
play_stream(audio_stream)
```

## JavaScript Streaming

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { createWriteStream } from "fs";
import { Readable } from "stream";

const client = new ElevenLabsClient();

const audioStream = await client.textToSpeech.convert("JBFqnCBsd6RMkjVDRZzb", {
  text: "Streaming audio in JavaScript.",
  modelId: "eleven_v4",
});

// Write to file (convert() returns a web ReadableStream — bridge to a Node stream first)
Readable.fromWeb(audioStream).pipe(createWriteStream("output.mp3"));

// Or process chunks
for await (const chunk of audioStream) {
  console.log(`Received ${chunk.length} bytes`);
}
```

## Eleven v4 Turbo WebSocket

For real-time Eleven v4 quality (~100ms), stream text to `eleven_v4_turbo` over the Text to Dialogue WebSocket (`/v1/text-to-dialogue/stream-input`). This endpoint only accepts Eleven v3 and v4 models. `eleven_v4_turbo` allows exactly **one** registered voice per connection; `eleven_v4` allows up to 10.

```python
import asyncio
import base64
import json
import os
import websockets
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
URI = (
    "wss://api.elevenlabs.io/v1/text-to-dialogue/stream-input"
    "?model_id=eleven_v4_turbo&output_format=mp3_44100_128"
)

async def stream_v4_turbo(text: str):
    async with websockets.connect(URI) as websocket:
        # First message registers voices and authenticates
        await websocket.send(json.dumps({
            "voices": [VOICE_ID],
            "xi_api_key": ELEVENLABS_API_KEY,
        }))
        await websocket.send(json.dumps({
            "inputs": [{"text": text, "voice_id": VOICE_ID, "new_turn": False}],
        }))
        # Flush remaining text and close after the final audio frame
        await websocket.send(json.dumps({"close_socket": True}))

        with open("output.mp3", "wb") as f:
            while True:
                msg = json.loads(await websocket.recv())
                if msg.get("error"):
                    raise RuntimeError(msg)
                if msg.get("audio"):
                    f.write(base64.b64decode(msg["audio"]))
                if msg.get("is_final"):
                    break

asyncio.run(stream_v4_turbo(
    "This is a longer line of dialogue so the server has enough text to start streaming audio. "
))
```

```javascript
import "dotenv/config";
import * as fs from "node:fs";
import WebSocket from "ws";

const voiceId = "JBFqnCBsd6RMkjVDRZzb";
const uri =
  "wss://api.elevenlabs.io/v1/text-to-dialogue/stream-input?model_id=eleven_v4_turbo&output_format=mp3_44100_128";

const websocket = new WebSocket(uri);
const out = fs.createWriteStream("output.mp3");

websocket.on("open", () => {
  websocket.send(JSON.stringify({ voices: [voiceId], xi_api_key: process.env.ELEVENLABS_API_KEY }));
  websocket.send(JSON.stringify({
    inputs: [{
      text: "This is a longer line of dialogue so the server has enough text to start streaming audio. ",
      voice_id: voiceId,
      new_turn: false,
    }],
  }));
  websocket.send(JSON.stringify({ close_socket: true }));
});

websocket.on("message", (data) => {
  const msg = JSON.parse(data.toString());
  if (msg.error) return console.error(msg);
  if (msg.audio) out.write(Buffer.from(msg.audio, "base64"));
});

websocket.on("close", () => out.end());
```

**Behavior notes:**
- The server buffers about **40 characters and 8 words** before emitting audio. Send `{"flush": true}` to force generation of shorter text without closing.
- Omit `close_socket` to keep the connection open between lines; send `{"keep_alive": true}` to reset the **20 second** inactivity timeout.
- Set `new_turn: true` when a speaker finishes a turn so prosody resets.
- Add `sync_alignment=true` to the query string to receive `alignment` timing data.
- Response fields are snake_case (`is_final`). Each open connection holds one dialogue session from a pool separate from standard concurrency.

## WebSocket Streaming

For text-streaming input where you send text chunks as they arrive (e.g., from an LLM) using Flash or Multilingual v2 models. The `stream-input` WebSocket does not support `eleven_v3` or `eleven_v4` — use the [Eleven v4 Turbo WebSocket](#eleven-v4-turbo-websocket) for those.

### Connection

```
wss://api.elevenlabs.io/v1/text-to-speech/{voiceId}/stream-input?model_id={modelId}
```

**Note:** This WebSocket does not support `eleven_v3` or `eleven_v4`. Use `eleven_flash_v2_5` here for lowest latency, or `eleven_v4_turbo` over the [Text to Dialogue WebSocket](#eleven-v4-turbo-websocket).

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
- **Model limitation**: The `stream-input` WebSocket does not support `eleven_v3` or `eleven_v4`; use the [Text to Dialogue WebSocket](#eleven-v4-turbo-websocket) for those.
- **Best practice**: Use `flush: true` at conversation turn endings to ensure the buffered text gets spoken.
- **Alignment data**: Word-level timestamps available via `alignment` field for lip-sync or captions.

## Best Practices

1. **Pick a real-time model**:
   - `eleven_v4_turbo` for the most expressive real-time speech (~100ms, Text to Dialogue WebSocket)
   - `eleven_flash_v2_5` for the lowest latency and cost, multilingual (~75ms)
   - `eleven_flash_v2` for English-only (~75ms)

2. **Buffer audio** before playback to prevent choppy output

3. **Handle disconnections** gracefully in WebSocket streams

4. **Choose output format based on use case**:
   - `pcm_24000` - lowest latency processing
   - `mp3_44100_128` - direct playback
   - `ulaw_8000` - telephony/Twilio integration
