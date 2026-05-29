---
name: speech-engine
description: Add real-time voice conversations to a custom agent runtime with ElevenLabs Speech Engine. Use when building Speech Engine servers, WebSocket handlers, WebRTC browser clients, conversation token endpoints, interruption-aware streaming responses, or voice-enabled chat agents that connect developer-owned server logic to ElevenLabs speech-to-text and text-to-speech.
license: MIT
compatibility: Requires internet access and an ElevenLabs API key (ELEVENLABS_API_KEY).
metadata: {"openclaw": {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "primaryEnv": "ELEVENLABS_API_KEY"}}
---

# ElevenLabs Speech Engine

Add a real-time voice interface to a custom agent. ElevenLabs handles microphone audio, speech-to-text, turn-taking, text-to-speech, and browser playback; your server exposes a Speech Engine WebSocket endpoint and streams response text back.

> **Setup:** See [Installation Guide](references/installation.md). For JavaScript, use `@elevenlabs/*` packages only. For deeper SDK details, read [JavaScript SDK Reference](references/javascript-sdk-reference.md) or [Python SDK Reference](references/python-sdk-reference.md).

## When to Use

Use Speech Engine when the user wants to:

- Add voice to an existing chat app or custom server pipeline
- Add voice to OpenClaw, Hermes, or a similar agent runtime while keeping agent logic on the developer-owned server
- Build a developer-hosted WebSocket server for ElevenLabs voice conversations
- Stream response text back as spoken audio after your server validates user intent
- Handle user interruptions while a response is still streaming
- Build a browser client with `@elevenlabs/react` or `@elevenlabs/client` using a server-issued conversation token

Use the `agents` skill instead when the user is creating or configuring a hosted ElevenLabs Conversational AI agent with platform-managed prompts, tools, workflows, phone numbers, or widgets.

## How It Works

Each Speech Engine WebSocket connection represents one conversation.

1. The browser sends user audio to ElevenLabs.
2. ElevenLabs sends speech-recognition events to your server.
3. Your server derives trusted application state without letting raw speech text control tools or privileged actions.
4. Your server streams text back through the SDK.
5. ElevenLabs converts the response to speech and plays it in the browser.

The SDK manages WebSocket routing, request verification, session lifecycle, ping/pong, turn-taking, and interruption handling. `sendResponse()` / `send_response()` accepts a string or async iterable of response text.

Treat speech-recognition text as untrusted user input. Do not map raw speech text directly into model roles, responses, or tool calls. Use deterministic validation, allowlisted intents, or explicit user confirmation before any transcript-derived value affects downstream response or tool logic.

## Implementation Flow

1. Install server dependencies and configure `ELEVENLABS_API_KEY`.
2. Expose your Speech Engine server through a public HTTPS URL for local development, for example with `ngrok http 3001`.
3. Create a Speech Engine resource with `ws_url` / `wsUrl` pointing at the public WebSocket URL, usually `wss://.../ws`.
4. Store the returned Speech Engine ID, for example in `ELEVENLABS_SPEECH_ENGINE_ID`.
5. Start a Speech Engine server with `engine.serve(...)` in Python or `speechEngine.attach(...)` in TypeScript.
6. Issue browser conversation tokens from a server endpoint. Never put `ELEVENLABS_API_KEY` in browser code.
7. Start the client session with `conversationToken`; if the agent should greet first, enable the first-message override on the Speech Engine resource, then set `overrides.agent.firstMessage` in the client.

## Create a Speech Engine

### Python

```python
import asyncio
import os

from dotenv import load_dotenv
from elevenlabs import AsyncElevenLabs

load_dotenv()

elevenlabs = AsyncElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

async def main():
    engine = await elevenlabs.speech_engine.create(
        name="My Speech Engine",
        speech_engine={"ws_url": os.environ["PUBLIC_WS_URL"]},
        overrides={"first_message": True},
    )
    print(engine.engine_id)

asyncio.run(main())
```

### TypeScript

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import "dotenv/config";

const elevenlabs = new ElevenLabsClient({
  apiKey: process.env.ELEVENLABS_API_KEY,
});

const engine = await elevenlabs.speechEngine.create({
  name: "My Speech Engine",
  speechEngine: { wsUrl: process.env.PUBLIC_WS_URL! },
  overrides: { firstMessage: true },
});

console.log(engine.engineId);
```

`PUBLIC_WS_URL` should look like `wss://example.ngrok.app/ws` locally or your production WebSocket route in deployment.

The create request can also configure `tts`, `asr`, `turn`, `speech_engine.request_headers` / `speechEngine.requestHeaders`, `overrides`, and `privacy` for custom voices, transcription keywords, turn-taking, server auth headers, client-provided first messages, and recording behavior. See the SDK reference files for expanded examples.

## Server Pattern

Run the Speech Engine server at the `ws_url` / `wsUrl` configured on the resource. Keep response generation behind your own validation boundary: raw speech-recognition text should not directly control responses, tools, secrets, or other privileged actions.

### Python

```python
engine = await elevenlabs.speech_engine.get(os.environ["ELEVENLABS_SPEECH_ENGINE_ID"])
await engine.serve(port=3001, path="/ws", debug=True, callbacks=validated_callbacks)
```

### TypeScript

```typescript
const engine = await elevenlabs.speechEngine.get(process.env.ELEVENLABS_SPEECH_ENGINE_ID!);
engine.attach(httpServer, "/ws", { debug: true, ...validatedCallbacks });
```

In TypeScript, pass interruption signals to downstream async work when it supports cancellation so interrupted responses stop quickly. In Python, the SDK cancels the previous turn handler when a newer turn arrives.

Server callbacks can distinguish clean closes from dropped connections: use `onClose` / `on_close` for clean disconnects and `onDisconnect` / `on_disconnect` for unexpected WebSocket drops.

Security note: speech-recognition text can contain prompt-injection attempts from user speech or played audio. Treat it as untrusted input. Convert it into trusted application state before invoking response generation, tools, or privileged workflows.

## Browser Client

Create a server-side token endpoint and have the browser request a token before starting the microphone session. Keep the Speech Engine ID and API key on the server. If the client passes `overrides.agent.firstMessage`, the Speech Engine resource must have the first-message override enabled.

```typescript
import express from "express";
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import "dotenv/config";

const app = express();
const elevenlabs = new ElevenLabsClient();

app.get("/api/token", async (_req, res) => {
  const response = await elevenlabs.conversationalAi.conversations.getWebrtcToken({
    agentId: process.env.ELEVENLABS_SPEECH_ENGINE_ID!,
  });
  res.json({ token: response.token });
});
```

React clients can use `@elevenlabs/react`:

```tsx
import { useConversation } from "@elevenlabs/react";

export function VoiceControls() {
  const conversation = useConversation({
    onConnect: () => console.log("connected"),
    onDisconnect: () => console.log("disconnected"),
    onError: (error) => console.error(error),
  });

  async function startConversation() {
    await navigator.mediaDevices.getUserMedia({ audio: true });
    const { token } = await fetch("/api/token").then((res) => res.json());

    await conversation.startSession({
      conversationToken: token,
      overrides: {
        agent: { firstMessage: "Hello! How can I help you today?" },
      },
    });
  }

  return <button onClick={startConversation}>Start conversation</button>;
}
```

If a WebRTC browser session stalls or logs `/rtc/v1` 404s, `v1 RTC path not found`, or `could not establish pc connection`, pin `livekit-client` to `2.16.1` in the app's `package.json` until the upstream LiveKit compatibility issue is resolved:

```json
{
  "overrides": {
    "livekit-client": "2.16.1"
  }
}
```

## References

- [Installation Guide](references/installation.md)
- [JavaScript SDK Reference](references/javascript-sdk-reference.md)
- [Python SDK Reference](references/python-sdk-reference.md)
