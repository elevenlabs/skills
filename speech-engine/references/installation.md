# Installation

## Server Environment

Set credentials on the server. Do not expose the ElevenLabs API key in browser code.

```bash
export ELEVENLABS_API_KEY="your-elevenlabs-api-key"
export ELEVENLABS_SPEECH_ENGINE_ID="seng_..."
```

For local development, expose the server publicly before creating the Speech Engine resource:

```bash
ngrok http 3001
export PUBLIC_WS_URL="wss://your-ngrok-domain.ngrok.app/ws"
```

The browser token endpoint uses the same `ELEVENLABS_SPEECH_ENGINE_ID`.

## JavaScript / TypeScript

Server dependencies:

```bash
npm install @elevenlabs/elevenlabs-js dotenv
```

If the server uses Express for the token endpoint:

```bash
npm install express
npm install -D tsx @types/express
```

Browser clients:

```bash
npm install @elevenlabs/react
# or, for vanilla browser JavaScript:
npm install @elevenlabs/client
```

### Temporary LiveKit WebRTC Pin

There is a known LiveKit server compatibility issue where WebRTC startup may hit the underlying LiveKit WebSocket path `/rtc/v1` and return 404, causing delays or failed sessions in React, Next.js, Electron, and other browser clients. Until the upstream issue is resolved, pin `livekit-client` to `2.16.1` when logs mention `/rtc/v1`, `v1 RTC path not found`, or `could not establish pc connection`:

```json
{
  "overrides": {
    "livekit-client": "2.16.1"
  }
}
```

This belongs in the app's `package.json`. Remove the override once the ElevenLabs LiveKit server or SDK no longer requires the workaround.

Always use `@elevenlabs/elevenlabs-js`, `@elevenlabs/react`, or `@elevenlabs/client`. Do not use the deprecated `elevenlabs` npm package.

## Python

Server dependencies:

```bash
pip install elevenlabs python-dotenv
```

If building the token endpoint in Flask:

```bash
pip install flask
```

Use the async SDK for Speech Engine servers:

```python
from elevenlabs import AsyncElevenLabs

client = AsyncElevenLabs()
```

## Local Development Checklist

- `ngrok http 3001` is running and points to the Speech Engine server port.
- The Speech Engine resource was created with a `wss://.../ws` `ws_url` / `wsUrl`.
- The server is listening on the same path, usually `/ws`.
- The token endpoint runs server-side and returns a short-lived conversation token.
- The browser asks for microphone permission before `startSession(...)`.
- First-message client overrides are enabled on the Speech Engine resource before passing `overrides.agent.firstMessage`.
- Server callbacks include `on_disconnect` / `onDisconnect` if unexpected WebSocket drops need handling.
- `debug: true` is enabled while developing so transcript and lifecycle issues are visible.

## Production Notes

- Replace ngrok with your public HTTPS host and use its `wss://` WebSocket URL.
- Keep the WebSocket path stable; updating the host requires updating or recreating the Speech Engine resource.
- Store API keys in managed secrets.
- Add shutdown handling so `SpeechEngineAttachment.close()` or the Python server process stops cleanly.
- Pass TypeScript `AbortSignal` values to downstream async work to cancel interrupted responses.
