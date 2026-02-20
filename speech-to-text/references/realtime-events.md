# Real-Time Event Reference

Complete reference for events in real-time speech-to-text streaming.

## Sent Events (Client → Server)

### input_audio_chunk

Send audio data for transcription.

```json
{
  "message_type": "input_audio_chunk",
  "audio_base_64": "<base64-encoded-pcm-audio>",
  "commit": false,
  "sample_rate": 16000
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message_type` | string | Yes | Always `"input_audio_chunk"` |
| `audio_base_64` | string | Yes | Base64-encoded PCM audio data |
| `commit` | boolean | Yes | Whether to commit after this chunk |
| `sample_rate` | number | No | Sample rate in Hz (8000-48000) |
| `previous_text` | string | No | Context from prior transcript (first chunk only, max 50 chars) |

### commit

Finalize the current transcript segment.

```json
{
  "message_type": "commit"
}
```

## Received Events (Server → Client)

All received events use `message_type` as the discriminator field.

### session_started

Connection established successfully.

```json
{
  "message_type": "session_started",
  "session_id": "0b0a72b57fd743ebbed6555d44836cf2",
  "config": {
    "sample_rate": 16000,
    "audio_format": "pcm_16000",
    "language_code": "en",
    "model_id": "scribe_v2_realtime",
    "commit_strategy": "manual",
    "include_timestamps": true
  }
}
```

### partial_transcript

Interim transcription results, updates frequently as audio is processed.

```json
{
  "message_type": "partial_transcript",
  "text": "Hello, how are"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `message_type` | string | `"partial_transcript"` |
| `text` | string | Current partial transcription |

### committed_transcript

Final transcription after commit.

```json
{
  "message_type": "committed_transcript",
  "text": "Hello, how are you today?"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `message_type` | string | `"committed_transcript"` |
| `text` | string | Finalized transcription |

### committed_transcript_with_timestamps

Final transcription with word-level timing. Sent after `committed_transcript` when `include_timestamps=true`.

```json
{
  "message_type": "committed_transcript_with_timestamps",
  "text": "Hello, how are you today?",
  "language_code": "en",
  "words": [
    {"text": "Hello", "start": 0.0, "end": 0.32, "type": "word"},
    {"text": " ", "start": 0.32, "end": 0.35, "type": "spacing"},
    {"text": "how", "start": 0.40, "end": 0.55, "type": "word"}
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `message_type` | string | `"committed_transcript_with_timestamps"` |
| `text` | string | Full transcription text |
| `language_code` | string | Detected language code |
| `words` | array | Word-level timing data |
| `words[].text` | string | The word or token |
| `words[].start` | number | Start time in seconds |
| `words[].end` | number | End time in seconds |
| `words[].type` | string | `"word"`, `"spacing"`, or `"audio_event"` |
| `words[].speaker_id` | string | Speaker identifier (if diarization enabled) |

## Error Events

### error

Sent when an error occurs.

```json
{
  "message_type": "error",
  "error": "input_error"
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `auth_error` | Invalid API key or token |
| `quota_exceeded` | Usage limit reached |
| `input_error` | Unsupported audio format or invalid input |
| `rate_limited` | Too many requests |
| `commit_throttled` | Commits sent too frequently |
| `session_time_limit_exceeded` | Session exceeded max duration |
| `unaccepted_terms` | Terms not accepted in dashboard |
| `resource_exhausted` | Server capacity reached |
| `queue_overflow` | Server queue capacity reached |
| `chunk_size_exceeded` | Audio chunk too large |
| `insufficient_audio_activity` | Not enough speech detected |
| `transcriber_error` | Internal processing error |

## Connection Events

### open

WebSocket connection established (standard WebSocket event, not a JSON message).

### close

WebSocket connection closed (standard WebSocket close frame with code and reason).

## Event Handling Examples

### Python

The Python SDK abstracts the wire protocol. You can use `event.type` (not `message_type`) when using the SDK's event objects:

```python
async for event in connection:
    if event.type == "session_started":
        print(f"Session: {event.session_id}")
    elif event.type == "partial_transcript":
        print(f"Partial: {event.text}")
    elif event.type == "committed_transcript":
        print(f"Final: {event.text}")
    elif event.type == "committed_transcript_with_timestamps":
        for word in event.words:
            print(f"  {word.text}: {word.start}s - {word.end}s")
    elif event.type == "error":
        print(f"Error: {event.error}")
```

### JavaScript

The JavaScript SDK uses event names matching the `message_type` values:

```javascript
connection.on("session_started", (data) => {
  console.log("Session:", data.sessionId);
});

connection.on("partial_transcript", (data) => {
  console.log("Partial:", data.text);
});

connection.on("committed_transcript", (data) => {
  console.log("Final:", data.text);
});

connection.on("committed_transcript_with_timestamps", (data) => {
  for (const word of data.words) {
    console.log(`  ${word.text}: ${word.start}s - ${word.end}s`);
  }
});

connection.on("error", (error) => {
  console.error("Error:", error);
});
```
