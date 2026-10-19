---
name: realtime
description: Use ElevenLabs Realtime models (`eleven_realtime_v1_mini`, `eleven_realtime_v1_max`), the low-latency models built for voice conversation. Use when the user wants to create an ElevenAgents agent on a Realtime model or switch an existing agent's Voice mode to Realtime, set `conversation_config.realtime_model`, choose between Realtime Mini and Max, or debug a Realtime agent that won't publish or transfer. Also use when migrating a voice app built on OpenAI's Realtime API and SDK (`@openai/agents-realtime`, `gpt-realtime`) to the OpenAI-compatible ElevenLabs Realtime API, including the `client_secrets` mint, the WebSocket transport, and audio after leaving WebRTC (closes with 4001/4003, no audio). Not for choosing an agent's LLM or TTS model in Custom mode, Scribe realtime speech-to-text, or migrating Chat Completions or Responses API text calls.
license: MIT
---

# ElevenLabs Realtime

Realtime models are ElevenLabs models built for low-latency voice conversation. There are two ways to use them:

- **An ElevenAgents agent** (an agent ID, the dashboard, or an `elevenlabs agents` project with `agent_configs/`): set the agent's Voice mode to Realtime with `conversation_config.realtime_model`, and ElevenLabs manages its LLM, TTS model, and ASR settings. See [Run an agent on a Realtime model](#run-an-agent-on-a-realtime-model).
- **A browser app built on OpenAI's Realtime SDK**: keep the SDK and point it at the OpenAI-compatible ElevenLabs Realtime API, `wss://api.elevenlabs.io/v1/convai/realtime`. See [Migrate an app from OpenAI Realtime](#migrate-an-app-from-openai-realtime).

When the user is starting from scratch and it's unclear which they want, ask. An agent brings a managed system prompt, tools, knowledge base, widget, and telephony; the Realtime API is the quicker path for code that already speaks OpenAI's realtime events. For agent features beyond the voice mode (prompt, tools, workflows, widget), use the `agents` skill.

## Models

| Model                   | Model ID                  | Optimized for                                                                             |
| ----------------------- | ------------------------- | ----------------------------------------------------------------------------------------- |
| Eleven Realtime v1 Mini | `eleven_realtime_v1_mini` | Lowest latency and cost. The default.                                                     |
| Eleven Realtime v1 Max  | `eleven_realtime_v1_max`  | Reasons before it responds, for complex instructions and multi-step tool use. Costs more. |

Start with Mini. Choose Max when the work involves long or complex instructions or multi-step tool calls and Mini's responses aren't good enough, or when an app being migrated was on a larger OpenAI model for reasoning-heavy work. Agents add compliance and data residency constraints on the choice; see [Choose the model](#step-2-choose-the-model).

## Run an agent on a Realtime model

Every voice agent has a Voice mode. In **Custom** mode the agent's LLM, TTS model, and ASR settings are chosen individually. In **Realtime** mode the agent runs on a Realtime model and ElevenLabs manages those settings. The mode is one field: `conversation_config.realtime_model` set to a model ID means Realtime, `null` means Custom.

The system prompt, first message, voice, languages, temperature, tools, knowledge base, and conversation flow settings (turn eagerness, timeouts, interruptions) work the same in both modes.

### Before you start

- These steps call the ElevenLabs API. The CLI and SDKs read `ELEVENLABS_API_KEY` from the environment; if it isn't set, use the `setup-api-key` skill. Never ask the user to paste the key into the conversation.
- Realtime models are rolling out gradually. If the API rejects `realtime_model` with `Realtime models are not available for this workspace.`, the workspace doesn't have access yet. Stop and tell the user; no configuration change fixes it.

### Step 1: Check the agent can use Realtime

For an existing agent, fetch its configuration first (`elevenlabs agents pull --agent <agent-id>`, or `agents.get` in the SDK). Keep the agent in Custom mode, and tell the user why, if any of these apply:

| Blocker                                                                                     | Where to look                                                                                                              |
| ------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Custom LLM or Amazon Bedrock                                                                | `conversation_config.agent.prompt.llm` is `custom-llm` or a Bedrock model                                                  |
| Created through another ElevenLabs product, such as Speech Engine                           | Ask the user if unsure; only ElevenAgents agents can use a Realtime model                                                  |
| Needs a specific LLM or TTS model                                                           | Ask the user whether the current `agent.prompt.llm` or `tts.model_id` is a requirement                                     |
| Workflow nodes override a [managed setting](#managed-settings) or `agent.prompt.max_tokens` | Overrides on the nodes under the agent's `workflow`                                                                        |
| Transfers to or from agents in Custom mode                                                  | `transfer_to_agent` tools and `agent_transfer` workflow nodes on this agent, and on any agent that transfers into this one |
| Text-only agent                                                                             | `conversation_config.conversation.text_only` is `true`; Realtime models are built for voice                                |

A workflow override can be removed and a transfer partner can be switched to Realtime too, but only with the user's agreement: both change how other parts of their setup behave.

### Step 2: Choose the model

Start with `eleven_realtime_v1_mini`. Choose `eleven_realtime_v1_max` when the agent follows long or complex instructions or relies on multi-step tool calls and Mini isn't good enough, or when the agent must comply with Zero Retention Mode or HIPAA. Then check availability:

| Environment                   | `eleven_realtime_v1_mini` | `eleven_realtime_v1_max`   |
| ----------------------------- | ------------------------- | -------------------------- |
| US                            | Available                 | Available                  |
| EU data residency             | Available                 | Available                  |
| India data residency          | Available                 | Not available              |
| Singapore data residency      | Available                 | Not available              |
| Zero Retention Mode and HIPAA | Not available             | Available in the US and EU |

Zero Retention Mode applies whether it's enforced on the workspace or enabled on the agent. Ask the user when the workspace's data residency or compliance settings aren't clear from the project. If neither model is available for the agent's environment, keep it in Custom mode.

Max also needs `agent.prompt.max_tokens` of at least 1024, or `-1` for no limit.

### Step 3: Set the model

On an existing agent, change only `realtime_model`; leave the rest of the configuration alone.

With the CLI, pull the agent, set the field in its file under `agent_configs/`, and push:

```bash
elevenlabs agents pull --agent <agent-id>
```

```json
{
  "conversation_config": {
    "realtime_model": "eleven_realtime_v1_mini"
  }
}
```

```bash
elevenlabs agents push --agent <agent-id>
```

With the SDKs:

```python
from elevenlabs import ElevenLabs

elevenlabs = ElevenLabs()

elevenlabs.conversational_ai.agents.update(
    agent_id="<agent-id>",
    conversation_config={
        "realtime_model": "eleven_realtime_v1_mini",
    },
)
```

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const elevenlabs = new ElevenLabsClient();

await elevenlabs.conversationalAi.agents.update("<agent-id>", {
  conversationConfig: {
    realtimeModel: "eleven_realtime_v1_mini",
  },
});
```

For a new agent, put `realtime_model` (`realtimeModel` in TypeScript) in the `conversation_config` passed to `agents.create`, alongside the prompt, first message, and voice. Don't pick an LLM or TTS model for it; a Realtime agent ignores them.

To turn Realtime off, set `realtime_model` to `null` (`None` in Python). The agent goes back to the LLM, TTS model, and ASR settings stored on it.

### Managed settings

While a Realtime model is set, the agent ignores the stored values of these fields in `conversation_config`. They come back into use when the agent switches to Custom, so don't clear them, and don't edit them to tune a Realtime agent:

| Setting             | Field                                     |
| ------------------- | ----------------------------------------- |
| LLM                 | `agent.prompt.llm`                        |
| Reasoning effort    | `agent.prompt.reasoning_effort`           |
| Thinking budget     | `agent.prompt.thinking_budget`            |
| Parallel tool calls | `agent.prompt.enable_parallel_tool_calls` |
| Cascade timeout     | `agent.prompt.cascade_timeout_seconds`    |
| TTS model           | `tts.model_id`                            |
| Expressive mode     | `tts.expressive_mode`                     |
| ASR provider        | `asr.provider`                            |

`agent.prompt.max_tokens` keeps applying. Temperature does too, but the dashboard hides it in Realtime mode, so change it through the CLI or API. If the Realtime model errors or doesn't respond in time, the agent falls back to its backup LLMs (LLM cascading); the Realtime model sets how long it waits.

### Step 4: Publish and verify

The Step 1 rules are checked when the agent is published, not when a draft is saved: a draft that breaks one saves, then publishing fails with an error naming the setting to change.

1. Fetch the agent and confirm `conversation_config.realtime_model` holds the chosen model. If the push, update, or the user's publish in the dashboard fails, match the error below.
2. Find every agent that transfers into this one and confirm it's in Realtime mode too. A Custom-mode agent's transfer into a Realtime agent is only caught when that agent is next published; until then the transfer is rejected mid-conversation and the caller stays with the current agent.
3. Have the user hold a test conversation.

### Errors

| Error                                                                   | Cause and fix                                                                                         |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `Realtime models are not available for this workspace.`                 | The workspace doesn't have access yet. Nothing to fix in the configuration.                           |
| `Transfers between default and Realtime model modes are not supported.` | A transfer to or from a Custom-mode agent ("default" means Custom). Put both agents in the same mode. |
| An error naming the Realtime model                                      | The model isn't available under the agent's compliance or data residency settings. See Step 2.        |
| Publishing fails naming a setting                                       | One of the Step 1 blockers or Max's token limit. Change that setting, or keep the agent in Custom.    |

### Pricing

A Realtime agent is billed the standard ElevenAgents per-minute rate plus its input, cached input, and output tokens at the Realtime model's rates; Max costs more per token than Mini. Point the user to https://elevenlabs.io/pricing rather than quoting rates.

## Migrate an app from OpenAI Realtime

ElevenLabs Realtime speaks the same wire protocol as OpenAI's GA Realtime API: the same client and server events over WebSocket. An app built on OpenAI's Realtime SDK keeps that SDK; the migration changes where credentials are minted, which URL the transport connects to, and the model, voice, and session configuration.

The one structural change: ElevenLabs Realtime is WebSocket-only. In a browser, `RealtimeSession` defaults to WebRTC, which wires the microphone and speaker for you. After switching to the WebSocket transport, the app has to capture and play audio itself.

This covers apps where the browser opens the realtime connection. It doesn't cover apps where a server opens the connection and streams audio to its clients over its own protocol, such as a bespoke WebSocket relay or a telephony bridge. Connecting to ElevenLabs Realtime from a server should work, but this skill has no steps for it. Tell the user so, and suggest they open an issue or a pull request at https://github.com/elevenlabs/skills describing their setup, rather than guessing at the server-side migration.

### Step 0: Inventory the app

Find every place the app touches OpenAI Realtime before editing anything:

```bash
grep -rnE "api\.openai\.com/v1/realtime|client_secrets|realtime/sessions|@openai/agents-realtime|@openai/agents/realtime|gpt-realtime|gpt-4o(-mini)?-realtime|OpenAIRealtimeWebRTC|OpenAIRealtimeWebSocket|RealtimeSession|OPENAI_API_KEY" --include='*.{ts,tsx,js,jsx,mjs,py}' .
```

Classify what you find, because each part migrates differently:

- **Credential minting**: a server route that calls `/v1/realtime/client_secrets` (GA) or `/v1/realtime/sessions` (beta). Migrate in Step 1.
- **Browser session**: `RealtimeSession`, `OpenAIRealtimeWebRTC`, `OpenAIRealtimeWebSocket`, or a hand-rolled `WebSocket`/`RTCPeerConnection`. Migrate in Steps 2 to 4.
- **Server-side realtime connections**: a Node or Python process that opens the realtime socket itself, for example a relay that streams audio to clients over its own WebSocket protocol, a telephony bridge, `openai` Python's `client.realtime.connect()`, or a `RealtimeSession` running in Node with a full API key. Not covered; see the scope above. If the app also has a browser session, migrate only that part, and only with the user's agreement.
- **Features beyond a voice conversation**: function tools, handoffs, guardrails, MCP servers, image input, SIP. ElevenLabs documents the voice conversation flow only. Leave this code in place, list it for the user as unverified against ElevenLabs, and have them test it.

`OPENAI_API_KEY` often serves other OpenAI calls too. Remove it only if nothing else uses it.

### Step 1: Mint the client secret from ElevenLabs

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

### Step 2: Convert the session config to the GA shape

Send the GA session shape. Apps written against OpenAI's beta API use flat fields (`modalities`, `voice`, `input_audio_format`, `turn_detection`, …) that need converting, and ElevenLabs rejects the deprecated `modalities` field outright. This matters most for the mint request body and any hand-rolled `session.update`: the SDK's `config` option converts deprecated camelCase fields to the GA wire shape for you, though moving it to the GA form too removes the deprecation warnings.

Read [Session config mapping](references/session-config.md) for the full beta-to-GA field table, voice handling, and the camelCase form the SDK's `config` option uses.

### Step 3: Point the browser session at ElevenLabs

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

### Step 4: Wire up audio (when the app was on WebRTC)

If the app previously used WebRTC (an explicit `OpenAIRealtimeWebRTC`, `transport: "webrtc"`, or no transport at all in a browser), it now has to:

1. Capture microphone audio as PCM16 at 24 kHz and stream it with `session.sendAudio(...)`.
2. Play PCM16 chunks from the session's `audio` event.
3. Stop playback on `audio_interrupted`. Without this, the assistant keeps talking over the user after a barge-in, because already-buffered audio keeps playing.
4. Release the microphone and close the session on teardown.

Read [Browser audio over WebSocket](references/browser-audio.md) for a working implementation with `wavtools`, the helper OpenAI uses in its own WebSocket examples, and its pitfalls.

Apps already on `OpenAIRealtimeWebSocket` have this wiring; check the sample rate is 24 kHz and keep it.

### Step 5: Verify

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

### Troubleshooting

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
