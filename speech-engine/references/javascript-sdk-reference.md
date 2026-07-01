# JavaScript SDK Reference

Use `@elevenlabs/elevenlabs-js` for server-side Speech Engine work.

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const elevenlabs = new ElevenLabsClient();
```

## Resource Methods

### Create

Only `speechEngine.wsUrl` is required. Use a secure WebSocket URL such as `wss://example.com/ws`. Add optional config blocks when the Speech Engine needs custom voice, speech recognition, turn-taking, request headers, client-side first-message overrides, or privacy behavior.

```typescript
const engine = await elevenlabs.speechEngine.create({
  name: "My Speech Engine",
  speechEngine: {
    wsUrl: "wss://example.com/ws",
    requestHeaders: {
      "x-agent-runtime": "openclaw",
    },
  },
  overrides: {
    firstMessage: true,
  },
  tts: {
    modelId: "eleven_flash_v2_5",
    voiceId: "cjVigY5qzO86Huf0OWal",
    optimizeStreamingLatency: "2",
  },
  asr: {
    provider: "scribe_realtime",
    keywords: ["OpenClaw", "Acme Cloud"],
  },
  turn: {
    turnEagerness: "normal",
    speculativeTurn: true,
  },
  privacy: {
    recordVoice: false,
  },
});

console.log(engine.engineId);
```

Enable `overrides.firstMessage` before using `overrides.agent.firstMessage` when starting a browser session.

### Get

```typescript
const engine = await elevenlabs.speechEngine.get("seng_...");
```

The returned resource has an engine ID plus helpers for attaching Speech Engine handling to a trusted HTTP server.

### Attach

Attach Speech Engine WebSocket handling to an existing Node HTTP server. Keep response generation behind a validation boundary so raw speech-recognition text does not directly control responses, tools, secrets, or privileged actions.

```typescript
const engine = await elevenlabs.speechEngine.get(process.env.ELEVENLABS_SPEECH_ENGINE_ID!);
engine.attach(httpServer, "/ws", { debug: true, ...validatedCallbacks });
```

Call `await attachment.close()` to stop accepting Speech Engine connections without shutting down the HTTP server.

Callback options include `onInit`, `onTranscript`, `onClose`, `onDisconnect`, `onError`, `debug`, and `disableAuth`. Use `onClose` for clean disconnects from ElevenLabs and `onDisconnect` when the WebSocket drops unexpectedly.

### disableAuth (dangerous)

`attach()` and `SpeechEngine.Server` verify the `X-Elevenlabs-Speech-Engine-Authorization` JWT on every incoming connection by default. Passing `disableAuth: true` in the callback options turns that check off. When it is off, the server accepts any client that can reach it — an attacker who finds the URL can open unlimited conversations, drain your ElevenLabs and downstream LLM quota, and inject arbitrary transcripts into your response pipeline.

Only recommend this option when the developer has already implemented **at least one** compensating control:

- an **IP allowlist** restricting inbound traffic to [ElevenLabs' egress ranges](https://elevenlabs.io/docs/overview/capabilities/speech-engine#ip-allowlisting), or
- a **custom shared-secret header** — configured via `speechEngine.requestHeaders` on the Speech Engine resource at create time — validated by an upstream proxy or middleware before the request reaches the SDK.

If neither is in place, do not disable auth. When it is enabled, the SDK also emits a `console.warn` at startup to make the state visible in logs. `apiKey` is not required in this mode, since it is only used for JWT verification.

### verifyRequest

Use only when managing WebSocket upgrades manually:

```typescript
const isValid = await engine.verifyRequest(req);
```

It checks `X-Elevenlabs-Speech-Engine-Authorization` against a JWT signed with the SHA-256 hash of the ElevenLabs API key.

## Session API

Each Speech Engine session represents one conversation.

| Member | Purpose |
| --- | --- |
| `conversationId` | Assigned after initialization |
| `isOpen` | Whether the WebSocket is open |
| `sendResponse(response)` | Send response text or a text stream back for TTS |
| `close()` | Close the WebSocket |

`sendResponse()` accepts a string or async iterable of response text.

## Safety

Speech-recognition text is untrusted user-controlled data. Validate intent with deterministic checks, allowlists, or explicit confirmation before it affects response generation, tool calls, secrets, or privileged workflows.

## Wire Protocol

The SDK handles protocol details automatically. Outgoing messages from your server are response text chunks and connection keep-alives.
