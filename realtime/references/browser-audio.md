# Browser audio over WebSocket

The OpenAI Realtime SDK wires microphone and speaker automatically only for its WebRTC transport. ElevenLabs Realtime is WebSocket-only, so the app captures and plays audio itself. Both directions use PCM16, 24 kHz, mono.

This reference uses [`wavtools`](https://www.npmjs.com/package/wavtools), the helper OpenAI uses in its own WebSocket examples. Any capture path that produces 24 kHz PCM16 `ArrayBuffer` chunks works, for example an `AudioWorklet` the app already has.

```bash
npm install @openai/agents-realtime wavtools
```

## Implementation

Framework-agnostic; in React, hold the returned handle in a `useRef` and call `stop()` on unmount.

```typescript
import {
  OpenAIRealtimeWebSocket,
  RealtimeAgent,
  RealtimeSession,
} from "@openai/agents-realtime";
import { WavRecorder, WavStreamPlayer } from "wavtools";

const SAMPLE_RATE = 24000;

export async function startVoiceSession() {
  const tokenResponse = await fetch("/api/token");
  if (!tokenResponse.ok)
    throw new Error(`Token request failed (${tokenResponse.status})`);
  const { value: clientSecret } = await tokenResponse.json();

  const recorder = new WavRecorder({ sampleRate: SAMPLE_RATE });
  const player = new WavStreamPlayer({ sampleRate: SAMPLE_RATE });
  await recorder.begin();
  await player.connect();

  const session = new RealtimeSession(
    new RealtimeAgent({
      name: "Assistant",
      instructions:
        "You are a helpful, friendly voice assistant. Keep replies concise.",
    }),
    {
      transport: new OpenAIRealtimeWebSocket({
        url: "wss://api.elevenlabs.io/v1/convai/realtime",
      }),
      model: "eleven_realtime_v1_mini",
      config: {
        outputModalities: ["audio"],
        audio: { output: { voice: "brian" } },
      },
    },
  );

  session.on("audio", (event) => {
    player.add16BitPCM(event.data, event.responseId);
  });
  session.on("audio_interrupted", () => {
    player.interrupt();
  });
  session.on("error", (event) => {
    console.error(event.error);
  });

  try {
    await session.connect({ apiKey: clientSecret });
    await recorder.record((data) => {
      session.sendAudio(data.mono as unknown as ArrayBuffer);
    });
  } catch (err) {
    await stop();
    throw err;
  }

  async function stop() {
    await recorder.quit().catch(() => {});
    player.interrupt();
    session.close();
  }

  return { session, stop };
}
```

Microphone audio streams continuously; server-side VAD decides when the user's turn ends, so there's no push-to-talk logic to port unless the app had one.

## Pitfalls

- **`data.mono` is mistyped.** `wavtools` types the `record()` callback's `mono` as `Int16Array`, but at runtime it's already the PCM16 `ArrayBuffer`. Pass it straight to `sendAudio`. Reading `.buffer` off it, or wrapping it in a new typed array, sends garbage.
- **Start from a user gesture.** `recorder.begin()` prompts for the microphone and `player.connect()` creates an `AudioContext`. Browsers block audio contexts created outside a click or keypress, so call `startVoiceSession()` from the handler that used to start the WebRTC session.
- **Stop playback on interruption.** `audio_interrupted` fires when the user barges in. `player.interrupt()` discards audio already queued; without it, the assistant keeps talking over the user.
- **Match the sample rate everywhere.** Recorder, player, and the mint body's `audio.input.format.rate` all use 24000. A mismatch plays back too fast, too slow, or as noise.
- **Tear down all three.** Quit the recorder (releases the microphone indicator), interrupt the player, and close the session. A leftover recorder keeps the microphone open after the conversation ends.

## Replacing WebRTC-specific code

| WebRTC-era code                                                    | WebSocket replacement                                                     |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| `new OpenAIRealtimeWebRTC({ audioElement, mediaStream })`          | `new OpenAIRealtimeWebSocket({ url })` plus the recorder and player above |
| `<audio autoplay>` element fed by the peer connection              | `WavStreamPlayer`; remove the element                                     |
| `getUserMedia` stream passed as `mediaStream`                      | `WavRecorder.begin()` (pass a `deviceId` to pick an input)                |
| Peer-connection event handlers (`changePeerConnection`, ICE state) | Remove; watch `session.on("error")` and transport events instead          |
