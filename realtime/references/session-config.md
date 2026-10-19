# Session config mapping

ElevenLabs Realtime takes OpenAI's GA session shape. Use this when converting a mint request body, a hand-rolled `session.update`, or the SDK's `config` option.

## Where session config lives

A migrated app usually sets session config in two places:

1. **The mint request** (`POST /v1/convai/realtime/client_secrets`, snake_case wire format). This is the authoritative initial session for the credential.
2. **The browser session**: `RealtimeAgent` instructions and tools, plus `RealtimeSession`'s `model` and `config` (camelCase). The SDK sends these as a `session.update` after connecting.

Keep both consistent, especially `model`, `instructions`, and `voice`. A shared module that both the server route and the browser import, exporting the model, voice, and instructions as constants, keeps them from drifting.

## Beta to GA field mapping

| Beta wire field (flat)                 | GA wire field                                            | SDK `config` (camelCase)     |
| -------------------------------------- | -------------------------------------------------------- | ---------------------------- |
| _(none)_                               | `type: "realtime"` (required)                            | _(set by the SDK)_           |
| `modalities`                           | `output_modalities`                                      | `outputModalities`           |
| `voice`                                | `audio.output.voice`                                     | `audio.output.voice`         |
| `input_audio_format: "pcm16"`          | `audio.input.format: { type: "audio/pcm", rate: 24000 }` | `audio.input.format`         |
| `output_audio_format: "pcm16"`         | `audio.output.format: { type: "audio/pcm" }`             | `audio.output.format`        |
| `turn_detection`                       | `audio.input.turn_detection`                             | `audio.input.turnDetection`  |
| `input_audio_transcription`            | `audio.input.transcription`                              | `audio.input.transcription`  |
| `input_audio_noise_reduction`          | `audio.input.noise_reduction`                            | `audio.input.noiseReduction` |
| `speed`                                | `audio.output.speed`                                     | `audio.output.speed`         |
| `instructions`, `tools`, `tool_choice` | unchanged                                                | unchanged                    |

ElevenLabs rejects the deprecated `modalities` field, so a beta-shaped body fails rather than degrading. The SDK's `config` converts deprecated camelCase fields (`modalities`, `voice`, `turnDetection`, …) to the GA wire shape itself, so only raw request bodies strictly need converting. Convert `config` too, so the code reads the same as the mint body.

## ElevenLabs-specific values

These are the values documented for ElevenLabs Realtime. Don't fill gaps with OpenAI values or guesses; when the app needs something not listed here, keep the documented value and tell the user what you couldn't map.

| Setting                      | Documented value                                                   |
| ---------------------------- | ------------------------------------------------------------------ |
| `model`                      | `eleven_realtime_v1_mini` or `eleven_realtime_v1_max`              |
| `audio.output.voice`         | `brian`                                                            |
| `audio.input.format`         | `{ type: "audio/pcm", rate: 24000 }` (PCM16, 24 kHz, mono)         |
| `audio.output.format`        | `{ type: "audio/pcm" }`                                            |
| `audio.input.turn_detection` | `{ type: "semantic_vad", eagerness: "low" \| "medium" \| "high" }` |
| `output_modalities`          | `["audio"]`                                                        |

### Voices

OpenAI voice names (`alloy`, `ash`, `ballad`, `coral`, `echo`, `sage`, `shimmer`, `verse`, `marin`, `cedar`) belong to OpenAI. Replace them, in the mint body and the SDK `config`. `brian` is the documented ElevenLabs value; the full set of accepted voices isn't documented yet. Use `brian`, and tell the user the voice is a placeholder to revisit.

### Audio formats

Only 24 kHz PCM is documented. Apps on G.711 (`audio/pcmu`, `audio/pcma`), typically telephony bridges, are server-side integrations, which are out of scope until ElevenLabs documents them.

## Example: beta mint body to ElevenLabs

Before (OpenAI beta, `POST https://api.openai.com/v1/realtime/sessions`):

```json
{
  "model": "gpt-4o-realtime-preview",
  "modalities": ["audio", "text"],
  "voice": "alloy",
  "instructions": "You are a helpful assistant.",
  "input_audio_format": "pcm16",
  "output_audio_format": "pcm16",
  "turn_detection": { "type": "server_vad" }
}
```

After (ElevenLabs, `POST https://api.elevenlabs.io/v1/convai/realtime/client_secrets`):

```json
{
  "session": {
    "type": "realtime",
    "model": "eleven_realtime_v1_mini",
    "instructions": "You are a helpful assistant.",
    "output_modalities": ["audio"],
    "audio": {
      "input": {
        "format": { "type": "audio/pcm", "rate": 24000 },
        "turn_detection": { "type": "semantic_vad", "eagerness": "medium" }
      },
      "output": {
        "format": { "type": "audio/pcm" },
        "voice": "brian"
      }
    }
  },
  "expires_after": { "anchor": "created_at", "seconds": 600 }
}
```

The beta response nests the credential at `client_secret.value`; the GA and ElevenLabs response has it at the top-level `value`.
