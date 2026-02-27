# Client-Side Real-Time Streaming

Stream audio from the browser directly to ElevenLabs for real-time transcription.

## Installation

```bash
# React
npm install @elevenlabs/react @elevenlabs/elevenlabs-js

# JavaScript
npm install @elevenlabs/client @elevenlabs/elevenlabs-js
```

> **Warning:** Always use the `@elevenlabs/*` namespace for client-side packages.

## Token Generation

Client-side streaming requires a single-use token to protect your API key. Generate tokens on your backend:

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const elevenlabs = new ElevenLabsClient({
  apiKey: process.env.ELEVENLABS_API_KEY,
});

app.get("/scribe-token", yourAuthMiddleware, async (req, res) => {
  const token = await elevenlabs.tokens.singleUse.create("realtime_scribe");
  res.json(token);
});
```

**Note:** Single-use tokens expire after 15 minutes.

## React Implementation

```typescript
import { useScribe, CommitStrategy } from "@elevenlabs/react";

function TranscriptionComponent() {
  const [transcript, setTranscript] = useState("");

  const scribe = useScribe({
    modelId: "scribe_v2_realtime",
    commitStrategy: CommitStrategy.VAD, // Auto-commit on silence for mic input
    onPartialTranscript: (data) => {
      // Show live feedback as user speaks
      console.log("Partial:", data.text);
    },
    onCommittedTranscript: (data) => {
      // Final transcript for this segment
      setTranscript((prev) => prev + data.text);
    },
  });

  const startRecording = async () => {
    const tokenResponse = await fetch("/scribe-token");
    const { token } = await tokenResponse.json();

    await scribe.connect({
      token,
      microphone: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    });
  };

  const stopRecording = () => {
    scribe.disconnect();
  };

  return (
    <div>
      <div>Status: {scribe.status}</div>
      <button onClick={startRecording}>Start</button>
      <button onClick={stopRecording}>Stop</button>
      <p>{transcript}</p>
    </div>
  );
}
```

> **Important:** The default commit strategy is `CommitStrategy.MANUAL`, which requires you to call `scribe.commit()` explicitly. For microphone input, always set `CommitStrategy.VAD` so the server auto-commits when silence is detected. Without this, committed transcripts will never fire and the connection may drop.

### `scribe.status` Values

| Status | Meaning |
|--------|---------|
| `"disconnected"` | No active connection |
| `"connecting"` | Connection is being established |
| `"connected"` | Connected and ready to receive audio |
| `"transcribing"` | Actively processing speech (transitions from `"connected"` when audio is detected or VAD commits) |
| `"error"` | An error occurred |

> **Important:** When checking if the session is active, always check for both `"connected"` and `"transcribing"`. The status transitions to `"transcribing"` during speech processing, so checking only `"connected"` will cause UI elements (buttons, waveforms, indicators) to incorrectly reset mid-session.

```typescript
// Correct - handles both active states
const isListening = scribe.status === "connected" || scribe.status === "transcribing";

// Wrong - will flicker/reset when VAD commits
const isListening = scribe.status === "connected";
```

## JavaScript Implementation

```typescript
import { Scribe, RealtimeEvents } from "@elevenlabs/client";

async function startTranscription() {
  const tokenResponse = await fetch("/scribe-token");
  const { token } = await tokenResponse.json();

  const connection = Scribe.connect({
    token,
    modelId: "scribe_v2_realtime",
    includeTimestamps: true,
    microphone: {
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
    },
  });

  connection.on(RealtimeEvents.OPEN, () => {
    console.log("Connected");
  });

  connection.on(RealtimeEvents.PARTIAL_TRANSCRIPT, (data) => {
    console.log("Partial:", data.text);
  });

  connection.on(RealtimeEvents.COMMITTED_TRANSCRIPT, (data) => {
    console.log("Committed:", data.text);
  });

  connection.on(RealtimeEvents.COMMITTED_TRANSCRIPT_WITH_TIMESTAMPS, (data) => {
    for (const word of data.words) {
      console.log(`${word.text}: ${word.start}s - ${word.end}s`);
    }
  });

  connection.on(RealtimeEvents.ERROR, (error) => {
    console.error("Error:", error);
  });

  connection.on(RealtimeEvents.CLOSE, () => {
    console.log("Disconnected");
  });

  return connection;
}
```

## Manual Audio Chunking

For file uploads or custom audio sources, encode to PCM-16 and send in chunks:

```typescript
const chunkSize = 4096;

for (let offset = 0; offset < pcmData.length; offset += chunkSize) {
  const chunk = pcmData.slice(offset, offset + chunkSize);
  const bytes = new Uint8Array(chunk.buffer);
  const base64 = btoa(String.fromCharCode(...bytes));

  scribe.sendAudio(base64);

  // Simulate real-time streaming
  await new Promise((resolve) => setTimeout(resolve, 50));
}

// Finalize transcription
scribe.commit();
```

## Microphone Options

| Option | Description |
|--------|-------------|
| `echoCancellation` | Remove echo from speakers |
| `noiseSuppression` | Filter background noise |
| `autoGainControl` | Normalize volume levels |

## Security

- Never expose your API key to the client
- Always generate single-use tokens on your backend
- Use authentication middleware to protect token endpoints
