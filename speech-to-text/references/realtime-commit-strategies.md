# Transcripts and Commit Strategies

Control when and how transcripts are finalized in real-time streaming.

## Why Commits Matter

In real-time transcription, the model continuously refines its understanding as more audio arrives. A word that sounds like "their" might become "there" or "they're" once more context is heard. The **commit** mechanism lets you decide when to "lock in" the transcript.

## Transcript Types

| Type | Description |
|------|-------------|
| **Partial** | Interim "best guess" results that update frequently as audio is processed. Use for live feedback (showing text as the user speaks), but don't save these - they may change. |
| **Committed** | Final, stable results after a commit occurs. Use these as the source of truth for your application - they won't change. |
| **Committed with Timestamps** | Same as committed, but includes word-level timing data for subtitles, karaoke, or lip-sync. |

## Manual Commit (Default)

You explicitly control when transcript segments finalize.

### Python

```python
from elevenlabs import AudioFormat, CommitStrategy, RealtimeAudioOptions

connection = await client.speech_to_text.realtime.connect(RealtimeAudioOptions(
    model_id="scribe_v2_realtime",
    audio_format=AudioFormat.PCM_16000,
    sample_rate=16000,
    commit_strategy=CommitStrategy.MANUAL,
))

# Send audio
await connection.send({"audio_base_64": audio_base_64})

# Commit when ready (e.g., pause in speech, end of sentence)
await connection.commit()
```

### JavaScript

```javascript
const connection = await client.speechToText.realtime.connect({
  modelId: "scribe_v2_realtime",
});

// Send audio
connection.send({
  audioBase64: audioBase64,
  sampleRate: 16000,
});

// Commit when ready
connection.commit();
```

### Best Practices

- **Commit every 20-30 seconds** for optimal performance
- **Commit during silence** or logical breaks (end of sentence, speaker change)
- **Auto-commit at 90 seconds** if no manual commit is sent

### Providing Context

Send previous text with the first audio chunk to help the model:

```python
await connection.send({
    "audio_base_64": first_chunk,
    "previous_text": "So as I was saying,"  # Keep under 50 characters
})
```

This helps with:
- Continuing conversations after reconnection
- Providing context for better accuracy
- Handling sentence fragments

## Voice Activity Detection (VAD)

VAD listens for silence and automatically commits when the speaker pauses. This creates natural transcript segments that match how people actually speak - pausing between sentences and thoughts. Recommended for live microphone input.

### Configuration

#### React (`useScribe`)

```typescript
import { useScribe, CommitStrategy } from "@elevenlabs/react";

const scribe = useScribe({
  modelId: "scribe_v2_realtime",
  commitStrategy: CommitStrategy.VAD,
  // Optional VAD tuning:
  vadSilenceThresholdSecs: 1.5,    // Silence duration before commit
  vadThreshold: 0.4,               // Speech detection sensitivity (0-1)
  minSpeechDurationMs: 100,        // Minimum speech length required
  minSilenceDurationMs: 100,       // Minimum silence length required
});
```

> **Important:** The default is `CommitStrategy.MANUAL`. For microphone input, always set `CommitStrategy.VAD` — without it, committed transcripts will never fire and the connection may drop.

#### JavaScript client

```javascript
const connection = await client.speechToText.realtime.connect({
  modelId: "scribe_v2_realtime",
  vad: {
    silenceThresholdSecs: 1.5,    // Silence duration before commit
    threshold: 0.4,               // Speech detection sensitivity (0-1)
    minSpeechDurationMs: 100,     // Minimum speech length required
    minSilenceDurationMs: 100,    // Minimum silence length required
  },
});
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `silenceThresholdSecs` | Seconds of silence before auto-commit | 1.5 |
| `threshold` | Speech detection sensitivity (lower = more sensitive) | 0.4 |
| `minSpeechDurationMs` | Ignore speech shorter than this | 100 |
| `minSilenceDurationMs` | Ignore silence shorter than this | 100 |

### When to Use VAD

- Live microphone input
- Conversational applications
- When natural speech boundaries are preferred
- Client-side implementations

### When to Use Manual Commit

- Processing audio files
- Known segment boundaries
- Maximum control over timing
- Server-side batch processing

## Supported Audio Formats

| Format | Sample Rate | Notes |
|--------|-------------|-------|
| PCM 16-bit | 16kHz | Recommended, best balance |
| PCM 16-bit | 8kHz - 48kHz | Supported range |
| μ-law 8-bit | 8kHz | Telephony compatibility |
