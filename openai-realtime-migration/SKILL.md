---
name: openai-realtime-migration
description: Migrate an existing voice app built on OpenAI's Realtime API to ElevenLabs Realtime, the OpenAI-compatible realtime endpoint, keeping OpenAI's Realtime SDK (`@openai/agents-realtime` / `@openai/agents/realtime`). Use when the user wants to switch, port, or point an OpenAI Realtime or `gpt-realtime` voice app at ElevenLabs, swap the ephemeral key / `client_secrets` endpoint, replace OpenAI realtime models with `eleven_realtime_v1_mini` or `eleven_realtime_v1_max`, or debug a migrated app (WebSocket closes with 4001/4003, no audio after leaving WebRTC). Not for migrating Chat Completions or Responses API text calls, and not for building a new ElevenLabs agent from scratch.
license: MIT
---

# Migrate from OpenAI Realtime to ElevenLabs Realtime

ElevenLabs Realtime speaks the same wire protocol as OpenAI's GA Realtime API: the same client and server events over WebSocket. An app built on OpenAI's Realtime SDK keeps that SDK; the migration changes where credentials are minted, which URL the transport connects to, and the model, voice, and session configuration.

The one structural change: ElevenLabs Realtime is WebSocket-only. In a browser, `RealtimeSession` defaults to WebRTC, which wires the microphone and speaker for you. After switching to the WebSocket transport, the app has to capture and play audio itself.

## Models

| Model ID                  | Optimized for             |
| ------------------------- | ------------------------- |
| `eleven_realtime_v1_mini` | Price and speed           |
| `eleven_realtime_v1_max`  | Quality and complex tasks |

Default to `eleven_realtime_v1_mini` unless the app was on a larger OpenAI model for reasoning-heavy work.

## Step 0: Inventory the app

Find every place the app touches OpenAI Realtime before editing anything:

```bash
grep -rnE "api\.openai\.com/v1/realtime|client_secrets|realtime/sessions|@openai/agents-realtime|@openai/agents/realtime|gpt-realtime|gpt-4o(-mini)?-realtime|OpenAIRealtimeWebRTC|OpenAIRealtimeWebSocket|RealtimeSession|OPENAI_API_KEY" --include='*.{ts,tsx,js,jsx,mjs,py}' .
```

Classify what you find, because each part migrates differently:

- **Credential minting**: a server route that calls `/v1/realtime/client_secrets` (GA) or `/v1/realtime/sessions` (beta). Migrate in Step 1.
- **Browser session**: `RealtimeSession`, `OpenAIRealtimeWebRTC`, `OpenAIRealtimeWebSocket`, or a hand-rolled `WebSocket`/`RTCPeerConnection`. Migrate in Steps 2 to 4.
- **Server-side realtime connections**: a Node or Python process that opens the realtime socket itself, for example a telephony bridge, `openai` Python's `client.realtime.connect()`, or a `RealtimeSession` running in Node with a full API key. ElevenLabs hasn't documented this path yet. Stop and tell the user rather than guessing at it.
- **Features beyond a voice conversation**: function tools, handoffs, guardrails, MCP servers, image input, SIP. ElevenLabs documents the voice conversation flow only. Leave this code in place, list it for the user as unverified against ElevenLabs, and have them test it.

`OPENAI_API_KEY` often serves other OpenAI calls too. Remove it only if nothing else uses it.

## Step 1: Mint the client secret from ElevenLabs

The browser never sees the ElevenLabs API key. A server route mints a short-lived client secret and returns only its `value`.

| What            | OpenAI                                                   | ElevenLabs                                                         |
| --------------- | -------------------------------------------------------- | ------------------------------------------------------------------ |
| URL             | `POST https://api.openai.com/v1/realtime/client_secrets` | `POST https://api.elevenlabs.io/v1/convai/realtime/client_secrets` |
| Auth header     | `Authorization: Bearer $OPENAI_API_KEY`                  | `xi-api-key: $ELEVENLABS_API_KEY`                                  |
| `session.model` | `gpt-realtime`, …                                        | `eleven_realtime_v1_mini` or `eleven_realtime_v1_max`              |
| Response        | `{ value, expires_at, session }`                         | Same shape                                                         |

The request body keeps the GA shape, `{ session, expires_after }`. The session config sent here is the authoritative initial session for that credential. The `model` string selects the agent behavior directly; there is no `agent_id`.

Mint with the ElevenLabs SDK (`npm install @elevenlabs/elevenlabs-js` or `pip install elevenlabs`), which sends the `xi-api-key` header for you:

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const elevenlabs = new ElevenLabsClient();

const clientSecret =
  await elevenlabs.conversationalAi.realtime.createClientSecret({
    session: {
      type: "realtime",
      model: "eleven_realtime_v1_mini",
      instructions:
        "You are a helpful, friendly voice assistant. Keep replies concise.",
      outputModalities: ["audio"],
      audio: {
        input: {
          format: { type: "audio/pcm", rate: 24000 },
          turnDetection: { type: "semantic_vad", eagerness: "medium" },
        },
        output: {
          format: { type: "audio/pcm" },
          voice: "brian",
        },
      },
    },
    expiresAfter: { anchor: "created_at", seconds: 600 },
  });
```

```python
import os

from elevenlabs import (
    CreateClientSecretRequest,
    ExpiresAfter,
    OpenAiAudioConfigInput,
    OpenAiAudioInputConfigInput,
    OpenAiAudioInputFormat,
    OpenAiAudioOutputConfigInput,
    OpenAiAudioOutputFormat,
    OpenAiSessionConfigInput,
    OpenAiTurnDetection,
)
from elevenlabs.client import ElevenLabs

elevenlabs = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

client_secret = elevenlabs.conversational_ai.realtime.create_client_secret(
    request=CreateClientSecretRequest(
        session=OpenAiSessionConfigInput(
            type="realtime",
            model="eleven_realtime_v1_mini",
            instructions="You are a helpful, friendly voice assistant. Keep replies concise.",
            output_modalities=["audio"],
            audio=OpenAiAudioConfigInput(
                input=OpenAiAudioInputConfigInput(
                    format=OpenAiAudioInputFormat(type="audio/pcm", rate=24000),
                    turn_detection=OpenAiTurnDetection(type="semantic_vad", eagerness="medium"),
                ),
                output=OpenAiAudioOutputConfigInput(
                    format=OpenAiAudioOutputFormat(type="audio/pcm"),
                    voice="brian",
                ),
            ),
        ),
        expires_after=ExpiresAfter(anchor="created_at", seconds=600),
    ),
)
```

Return only `clientSecret.value` (`client_secret.value` in Python) to the browser.

Keep the route's existing framework, path, and response contract; only the upstream call changes. If the app minted with the beta `/v1/realtime/sessions` endpoint, its frontend reads `client_secret.value`. Either update the frontend to read the top-level `value`, or have the route return `{ client_secret: { value } }` so the frontend stays untouched.

## Step 2: Convert the session config to the GA shape

Send the GA session shape. Apps written against OpenAI's beta API use flat fields (`modalities`, `voice`, `input_audio_format`, `turn_detection`, …) that need converting, and ElevenLabs rejects the deprecated `modalities` field outright. This matters most for the mint request body and any hand-rolled `session.update`: the SDK's `config` option converts deprecated camelCase fields to the GA wire shape for you, though moving it to the GA form too removes the deprecation warnings.

Read [Session config mapping](references/session-config.md) for the full beta-to-GA field table, voice handling, and the camelCase form the SDK's `config` option uses.

## Step 3: Point the browser session at ElevenLabs

Replace the transport with `OpenAIRealtimeWebSocket` aimed at the ElevenLabs URL, set the model on the session, and pass the minted `value` as the API key:

```typescript
import {
  OpenAIRealtimeWebSocket,
  RealtimeAgent,
  RealtimeSession,
} from "@openai/agents-realtime";

const { value: clientSecret } = await fetch("/api/token").then((res) =>
  res.json(),
);

const agent = new RealtimeAgent({
  name: "Assistant",
  instructions:
    "You are a helpful, friendly voice assistant. Keep replies concise.",
});

const transport = new OpenAIRealtimeWebSocket({
  url: "wss://api.elevenlabs.io/v1/convai/realtime",
});

const session = new RealtimeSession(agent, {
  transport,
  model: "eleven_realtime_v1_mini",
  config: {
    outputModalities: ["audio"],
    audio: { output: { voice: "brian" } },
  },
});

await session.connect({ apiKey: clientSecret });
```

Keep the app's existing `RealtimeAgent` name, instructions, and event handlers. Drop WebRTC-only options (`audioElement`, `mediaStream`, `changePeerConnection`) and any `transport: "webrtc"` setting; they have no WebSocket equivalent.

## Step 4: Wire up audio (when the app was on WebRTC)

If the app previously used WebRTC (an explicit `OpenAIRealtimeWebRTC`, `transport: "webrtc"`, or no transport at all in a browser), it now has to:

1. Capture microphone audio as PCM16 at 24 kHz and stream it with `session.sendAudio(...)`.
2. Play PCM16 chunks from the session's `audio` event.
3. Stop playback on `audio_interrupted`. Without this, the assistant keeps talking over the user after a barge-in, because already-buffered audio keeps playing.
4. Release the microphone and close the session on teardown.

Read [Browser audio over WebSocket](references/browser-audio.md) for a working implementation with `wavtools`, the helper OpenAI uses in its own WebSocket examples, and its pitfalls.

Apps already on `OpenAIRealtimeWebSocket` have this wiring; check the sample rate is 24 kHz and keep it.

## Step 5: Verify

1. Find where the server loads `OPENAI_API_KEY` from (`.env`, `.env.local`, deployment secrets) and ask the user to store `ELEVENLABS_API_KEY` there. Don't ask for the key in the conversation or write it into a file yourself. Add an empty `ELEVENLABS_API_KEY=` to `.env.example` if the project has one.
2. Once the user confirms the key is in place, run the app, start a conversation, and speak.
3. Confirm the `session.created` transport event reports the `eleven_realtime_*` model and the chosen voice:

   ```typescript
   session.on("transport_event", (event) => {
     if (event.type === "session.created") console.log(event);
   });
   ```

4. Interrupt the assistant mid-sentence and confirm playback stops.
5. Tell the user which features from Step 0 remain unverified (tools, handoffs, guardrails, …).

## Troubleshooting

| Symptom                                             | Cause and fix                                                                                         |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| WebSocket closes with code `4003`                   | Realtime isn't enabled for this ElevenLabs workspace. Contact ElevenLabs; the code can't fix this.    |
| WebSocket closes with code `4001`                   | Client secret rejected: expired, or not the minted `value` passed as `apiKey` to `session.connect()`. |
| Mint returns 401                                    | Still sending `Authorization: Bearer`; ElevenLabs uses the `xi-api-key` header.                       |
| Mint or `session.update` is rejected                | Beta-shaped fields such as `modalities`. Convert with the [mapping](references/session-config.md).    |
| Connects, but no audio either way                   | The app was on WebRTC and audio isn't wired yet. See Step 4.                                          |
| Audio is noise, chipmunk-fast, or slowed down       | Sample-rate or buffer mismatch. Capture and play at 24 kHz; see the pitfalls in the audio reference.  |
| Assistant talks over the user after an interruption | Playback isn't stopped on `audio_interrupted`.                                                        |

## References

- [Session config mapping](references/session-config.md)
- [Browser audio over WebSocket](references/browser-audio.md)
