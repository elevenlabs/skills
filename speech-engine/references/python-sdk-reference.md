# Python SDK Reference

Use the async ElevenLabs SDK for Speech Engine servers.

```python
from elevenlabs import AsyncElevenLabs

elevenlabs = AsyncElevenLabs()
```

## Resource Methods

### Create

Only `speech_engine.ws_url` is required. Use a secure WebSocket URL such as `wss://example.com/ws`. Add optional config blocks when the Speech Engine needs custom voice, speech recognition, turn-taking, request headers, client-side first-message overrides, or privacy behavior.

```python
engine = await elevenlabs.speech_engine.create(
    name="My Speech Engine",
    speech_engine={
        "ws_url": "wss://example.com/ws",
        "request_headers": {
            "x-agent-runtime": "openclaw",
        },
    },
    overrides={
        "first_message": True,
    },
    tts={
        "model_id": "eleven_flash_v2_5",
        "voice_id": "cjVigY5qzO86Huf0OWal",
        "optimize_streaming_latency": "2",
    },
    asr={
        "provider": "scribe_realtime",
        "keywords": ["OpenClaw", "Acme Cloud"],
    },
    turn={
        "turn_eagerness": "normal",
        "speculative_turn": True,
    },
    privacy={
        "record_voice": False,
    },
)

print(engine.engine_id)
```

Enable `overrides.first_message` before using `overrides.agent.firstMessage` when starting a browser session.

### Get

```python
engine = await elevenlabs.speech_engine.get("seng_...")
```

The returned resource has an engine ID plus helpers for serving Speech Engine traffic from a trusted Python process.

### Serve

Run a Speech Engine server on the configured WebSocket path. Keep response generation behind a validation boundary so raw speech-recognition text does not directly control responses, tools, secrets, or privileged actions.

```python
engine = await elevenlabs.speech_engine.get(os.environ["ELEVENLABS_SPEECH_ENGINE_ID"])
await engine.serve(port=3001, path="/ws", debug=True, callbacks=validated_callbacks)
```

Key parameters:

| Parameter | Default | Purpose |
| --- | --- | --- |
| `port` | `3001` | Port to listen on |
| `path` | `None` | Restrict WebSocket connections to one path |
| `debug` | `False` | Log protocol details while developing |

Common callback keys include `on_init`, `on_transcript`, `on_close`, `on_disconnect`, and `on_error`. Use `on_close` for clean disconnects from ElevenLabs and `on_disconnect` when the WebSocket drops unexpectedly.

### verify_request

Use only when managing WebSocket upgrades manually:

```python
is_valid = engine.verify_request(headers)
```

It checks `X-Elevenlabs-Speech-Engine-Authorization` against a JWT signed with the SHA-256 hash of the ElevenLabs API key.

## Session API

Each Speech Engine session represents one conversation.

| Member | Purpose |
| --- | --- |
| `conversation_id` | Assigned after initialization |
| `is_open` | Whether the WebSocket is open |
| `send_response(response)` | Send response text or a text stream back for TTS |
| `run()` | Run the receive loop for manual sessions |
| `close()` | Close the WebSocket |

`send_response()` accepts a string or async iterable of response text.

## Safety

Speech-recognition text is untrusted user-controlled data. Validate intent with deterministic checks, allowlists, or explicit confirmation before it affects response generation, tool calls, secrets, or privileged workflows.

## Wire Protocol

The SDK handles protocol details automatically. Outgoing messages from your server are response text chunks and connection keep-alives.
