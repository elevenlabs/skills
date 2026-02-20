# Server-Side Real-Time Streaming

Transcribe audio streams in real-time from your server with ultra-low latency.

## Installation

```bash
# Python
pip install elevenlabs python-dotenv pydub

# JavaScript
npm install @elevenlabs/elevenlabs-js dotenv
```

> **Warning:** Do not use `npm install elevenlabs` - that's an outdated v1.x package. Always use `@elevenlabs/elevenlabs-js`.

## Configuration

Store your API key in a `.env` file:

```
ELEVENLABS_API_KEY=<your_api_key_here>
```

## Stream from URL

### Python

```python
from dotenv import load_dotenv
import os
import asyncio
from elevenlabs import ElevenLabs
from elevenlabs import RealtimeEvents, RealtimeUrlOptions

load_dotenv()

async def main():
    elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    stop_event = asyncio.Event()

    connection = await elevenlabs.speech_to_text.realtime.connect(RealtimeUrlOptions(
        model_id="scribe_v2_realtime",
        url="https://npr-ice.streamguys1.com/live.mp3",
        include_timestamps=True,
    ))

    def on_partial_transcript(data):
        print(f"Partial: {data.get('text', '')}")

    def on_committed_transcript(data):
        print(f"Committed: {data.get('text', '')}")

    def on_error(error):
        print(f"Error: {error}")
        stop_event.set()

    def on_close():
        print("Connection closed")

    connection.on(RealtimeEvents.PARTIAL_TRANSCRIPT, on_partial_transcript)
    connection.on(RealtimeEvents.COMMITTED_TRANSCRIPT, on_committed_transcript)
    connection.on(RealtimeEvents.ERROR, on_error)
    connection.on(RealtimeEvents.CLOSE, on_close)

    try:
        await stop_event.wait()
    except KeyboardInterrupt:
        print("\nStopping transcription...")
    finally:
        await connection.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### JavaScript

```javascript
import "dotenv/config";
import { ElevenLabsClient, RealtimeEvents } from "@elevenlabs/elevenlabs-js";

const elevenlabs = new ElevenLabsClient();

const connection = await elevenlabs.speechToText.realtime.connect({
  modelId: "scribe_v2_realtime",
  url: "https://npr-ice.streamguys1.com/live.mp3",
  includeTimestamps: true,
});

connection.on(RealtimeEvents.PARTIAL_TRANSCRIPT, (transcript) => {
  console.log("Partial transcript", transcript);
});

connection.on(RealtimeEvents.COMMITTED_TRANSCRIPT, (transcript) => {
  console.log("Committed transcript", transcript);
});

connection.on(RealtimeEvents.ERROR, (error) => {
  console.log("Error", error);
});

connection.on(RealtimeEvents.CLOSE, () => {
  console.log("Connection closed");
});
```

## Manual Audio Chunking

For local files or custom audio streams, convert to PCM format and send in chunks.

### Python

```python
import asyncio
import base64
import os
from dotenv import load_dotenv
from pathlib import Path
from elevenlabs import ElevenLabs
from elevenlabs import AudioFormat, CommitStrategy, RealtimeEvents, RealtimeAudioOptions
from pydub import AudioSegment

load_dotenv()

def load_and_convert_audio(audio_path: str | Path, target_sample_rate: int = 16000) -> bytes:
    if str(audio_path).lower().endswith('.pcm'):
        with open(audio_path, 'rb') as f:
            return f.read()

    audio = AudioSegment.from_file(audio_path)
    if audio.channels > 1:
        audio = audio.set_channels(1)
    if audio.frame_rate != target_sample_rate:
        audio = audio.set_frame_rate(target_sample_rate)
    audio = audio.set_sample_width(2)
    return audio.raw_data

async def main():
    elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    transcription_complete = asyncio.Event()

    connection = await elevenlabs.speech_to_text.realtime.connect(RealtimeAudioOptions(
        model_id="scribe_v2_realtime",
        audio_format=AudioFormat.PCM_16000,
        sample_rate=16000,
        commit_strategy=CommitStrategy.MANUAL,
        include_timestamps=True,
    ))

    def on_session_started(data):
        print(f"Session started: {data}")
        asyncio.create_task(send_audio())

    def on_partial_transcript(data):
        transcript = data.get('text', '')
        if transcript:
            print(f"Partial: {transcript}")

    def on_committed_transcript(data):
        transcript = data.get('text', '')
        print(f"\nCommitted transcript: {transcript}")

    def on_committed_transcript_with_timestamps(data):
        print(f"Timestamps: {data.get('words', '')}")
        transcription_complete.set()

    def on_error(error):
        print(f"Error: {error}")
        transcription_complete.set()

    def on_close():
        print("Connection closed")
        transcription_complete.set()

    connection.on(RealtimeEvents.SESSION_STARTED, on_session_started)
    connection.on(RealtimeEvents.PARTIAL_TRANSCRIPT, on_partial_transcript)
    connection.on(RealtimeEvents.COMMITTED_TRANSCRIPT, on_committed_transcript)
    connection.on(RealtimeEvents.COMMITTED_TRANSCRIPT_WITH_TIMESTAMPS, on_committed_transcript_with_timestamps)
    connection.on(RealtimeEvents.ERROR, on_error)
    connection.on(RealtimeEvents.CLOSE, on_close)

    async def send_audio():
        audio_file_path = Path("audio.mp3")
        audio_data = load_and_convert_audio(audio_file_path)
        chunk_size = 32000  # 1 second of audio at 16kHz
        chunks = [audio_data[i:i + chunk_size] for i in range(0, len(audio_data), chunk_size)]

        for i, chunk in enumerate(chunks):
            chunk_base64 = base64.b64encode(chunk).decode('utf-8')
            await connection.send({"audio_base_64": chunk_base64, "sample_rate": 16000})

            if i < len(chunks) - 1:
                await asyncio.sleep(1)

        await asyncio.sleep(0.5)
        await connection.commit()

    try:
        await transcription_complete.wait()
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        await connection.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### JavaScript

```javascript
import "dotenv/config";
import * as fs from "node:fs";
import { ElevenLabsClient, RealtimeEvents, AudioFormat } from "@elevenlabs/elevenlabs-js";

const elevenlabs = new ElevenLabsClient();

const connection = await elevenlabs.speechToText.realtime.connect({
  modelId: "scribe_v2_realtime",
  audioFormat: AudioFormat.PCM_16000,
  sampleRate: 16000,
  includeTimestamps: true,
});

connection.on(RealtimeEvents.SESSION_STARTED, (data) => {
  console.log("Session started", data);
  sendAudio();
});

connection.on(RealtimeEvents.PARTIAL_TRANSCRIPT, (transcript) => {
  console.log("Partial transcript", transcript);
});

connection.on(RealtimeEvents.COMMITTED_TRANSCRIPT, (transcript) => {
  console.log("Committed transcript", transcript);
});

connection.on(RealtimeEvents.COMMITTED_TRANSCRIPT_WITH_TIMESTAMPS, (transcript) => {
  console.log("Committed with timestamps", transcript);
});

connection.on(RealtimeEvents.ERROR, (error) => {
  console.log("Error", error);
});

connection.on(RealtimeEvents.CLOSE, () => {
  console.log("Connection closed");
});

async function sendAudio() {
  const pcmFilePath = "audio.pcm";
  const chunkSize = 32000;
  const audioBuffer = fs.readFileSync(pcmFilePath);
  const chunks: Buffer[] = [];

  for (let i = 0; i < audioBuffer.length; i += chunkSize) {
    const chunk = audioBuffer.subarray(i, i + chunkSize);
    chunks.push(chunk);
  }

  for (let i = 0; i < chunks.length; i++) {
    const chunk = chunks[i];
    const chunkBase64 = chunk.toString("base64");

    connection.send({
      audioBase64: chunkBase64,
      sampleRate: 16000,
    });

    if (i < chunks.length - 1) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
  }

  await new Promise((resolve) => setTimeout(resolve, 500));
  connection.commit();
}
```

## Direct WebSocket Connection

For cases where the SDK cannot be used:

```
wss://api.elevenlabs.io/v1/speech-to-text/realtime?model_id=scribe_v2_realtime
```

### Message Format

```json
{
  "message_type": "input_audio_chunk",
  "audio_base_64": "<base64-encoded-audio>",
  "commit": false,
  "sample_rate": 16000
}
```

### Commit Message

```json
{
  "message_type": "commit"
}
```

## Audio Requirements

| Parameter | Value |
|-----------|-------|
| Format | PCM 16-bit |
| Sample Rate | 16000 Hz (recommended) |
| Channels | Mono |
| Chunk Size | 32,000 bytes = 1 second |

Supported sample rates: 8kHz to 48kHz
