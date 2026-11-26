# Text to speech: OpenAI to ElevenLabs

For `audio.speech.create(...)`, `audio.speech.with_streaming_response.create(...)` and direct calls to `POST https://api.openai.com/v1/audio/speech`.

The examples were checked against `elevenlabs` 2.80.0 (Python) and `@elevenlabs/elevenlabs-js` 2.80.0. If the installed SDK disagrees with them, the installed SDK is right.

## Settings

Every setting an OpenAI speech call can pass, and what happens to it:

| OpenAI | ElevenLabs | Rule |
| --- | --- | --- |
| `model`: `tts-1`, `tts-1-hd`, `gpt-4o-mini-tts`, or a dated version of one | `model_id` / `modelId`: `eleven_v4` | Always set it. Use `eleven_multilingual_v2` instead when the call keeps a `speed` (below). |
| `input` | `text` | Same text. `eleven_v4` takes up to 100,000 characters, so code that splits text to fit OpenAI's 4,096 can stay as it is. |
| `voice`: a name such as `alloy` or `coral` | `voice_id`: an ID | See [Voices](#voices). In JavaScript it is the first argument, not a field. |
| `voice`: an object with an `id` (a custom voice) | None | Leave the call on OpenAI and list it. |
| `response_format` | `output_format` / `outputFormat` | See [Formats](#formats). Not set means MP3 on both sides, so leave it unset. |
| `speed`: `1.0`, or not set | None | Drop it. |
| `speed`: from `0.7` to `1.2` | `voice_settings.speed` / `voiceSettings.speed` | Keep the value, and use `eleven_multilingual_v2`: `eleven_v4` doesn't change speed. Tell the user which model the call uses and why. |
| `speed`: outside `0.7` to `1.2`, or a value only known when the app runs | None | Leave the call on OpenAI and list it. |
| `instructions` | None | Drop it and tell the user: delivery now comes from the voice they choose. |
| `stream_format`: `audio`, or not set | None | Drop it. |
| `stream_format`: `sse` | None | Leave the call on OpenAI and list it. |
| `timeout`, `max_retries`, request headers | Request options | See [Errors, retries and timeouts](#errors-retries-and-timeouts). |
| `extra_body`, `extra_query`, or anything not in this table | None | Leave the call on OpenAI and list it. |

## Voices

There is no like-for-like match between OpenAI's voices and ElevenLabs voices, so don't pick one that "sounds like" the old one. Use one placeholder, George, in one named constant the user can change:

```python
ELEVENLABS_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George, a placeholder: choose your own voice
```

- **One voice in the code:** replace it with the constant.
- **The voice is a value the app passes around** (a function argument, a setting, a list the user picks from): keep that value's name and type so callers don't change, and map each OpenAI name the app uses to a voice ID in one place. Every name maps to the placeholder until the user chooses voices, so tell them that all voices sound the same for now.

```python
ELEVENLABS_VOICE_IDS = {
    "alloy": ELEVENLABS_VOICE_ID,
    "nova": ELEVENLABS_VOICE_ID,
}

voice_id = ELEVENLABS_VOICE_IDS.get(voice, ELEVENLABS_VOICE_ID)
```

Don't use any other voice ID from memory: many in older tutorials have been retired.

## Formats

| OpenAI `response_format` | ElevenLabs `output_format` | Notes |
| --- | --- | --- |
| not set, or `mp3` | not set, or `mp3_44100_128` | |
| `opus` | `opus_48000_128` | |
| `pcm` | `pcm_24000` | Both are raw 24 kHz, 16-bit, mono samples with no header. |
| `wav` | `wav_24000` | Only with `convert`. `stream` has no WAV formats. Where the app streamed WAV, keep it WAV with `convert`, so whatever reads the header still works, and tell the user the audio now arrives once the whole clip is ready. If they want it as it is generated, `stream` with `pcm_24000` is the same samples without the header. |
| `aac`, `flac` | None | Leave the call on OpenAI and list it. The docs guide says to ask for another format and convert it, but that adds an audio tool to the app, which is the user's call. |

If the app sets a `Content-Type` or a file extension from the format, keep them matching (`audio/mpeg` and `.mp3` for MP3).

## Which method

Choose by how the app uses the audio, not by which OpenAI method it called. OpenAI's own examples save a file through `with_streaming_response`; that is still a file, so it becomes `convert`.

- It needs all the bytes, or a file: `text_to_speech.convert` / `textToSpeech.convert`.
- It passes audio on piece by piece as it is generated (to an HTTP response, a player, a socket): `text_to_speech.stream` / `textToSpeech.stream`. Same arguments.

## How the audio comes back

This is the part that differs most. OpenAI returns a response object with helpers. ElevenLabs returns the audio itself, in pieces.

### Python

`convert` and `stream` return an iterator of `bytes`. **Nothing is sent until the first piece is read**, so an error from ElevenLabs is raised where the audio is read, not where `convert` is called.

| OpenAI | ElevenLabs |
| --- | --- |
| `response.content`, `response.read()` | `b"".join(audio)` |
| `response.write_to_file(path)`, `response.stream_to_file(path)` | Read the audio, then write the file (below) |
| `for chunk in response.iter_bytes()` | `for chunk in audio` |
| `with client.audio.speech.with_streaming_response.create(...) as response:` | No `with`: call `convert(...)` or `stream(...)`, whichever [Which method](#which-method) says, and read it |

Before:

```python
response = client.audio.speech.create(model="tts-1", voice="alloy", input=text)
response.write_to_file(path)
```

After:

```python
audio = elevenlabs.text_to_speech.convert(
    voice_id=ELEVENLABS_VOICE_ID,
    text=text,
    model_id="eleven_v4",
)
data = b"".join(audio)
with open(path, "wb") as f:
    f.write(data)
```

Read the audio before opening the file. If the request fails, the error is raised at `b"".join(audio)` and no empty file is left behind, which is how the OpenAI call behaved.

Streaming to a client, for example from FastAPI. Read the first piece before the response starts: that is when the request is sent, so a failure is raised here, where the route can still answer with an error, and not halfway through a response that has already begun.

```python
import itertools

audio = elevenlabs.text_to_speech.stream(
    voice_id=ELEVENLABS_VOICE_ID,
    text=text,
    model_id="eleven_v4",
)
first = next(audio, b"")
return StreamingResponse(itertools.chain([first], audio), media_type="audio/mpeg")
```

With a setting kept:

```python
from elevenlabs import VoiceSettings

audio = elevenlabs.text_to_speech.convert(
    voice_id=ELEVENLABS_VOICE_ID,
    text=text,
    model_id="eleven_multilingual_v2",
    output_format="pcm_24000",
    voice_settings=VoiceSettings(speed=1.1),
)
pcm = b"".join(audio)
```

### Python, async

With `AsyncElevenLabs`, `convert` and `stream` return an async iterator. **Don't `await` the call**; iterate it.

| OpenAI (`AsyncOpenAI`) | ElevenLabs (`AsyncElevenLabs`) |
| --- | --- |
| `response = await client.audio.speech.create(...)` then `response.content` or `await response.aread()` | `audio = elevenlabs.text_to_speech.convert(...)` then `b"".join([chunk async for chunk in audio])` |
| `async for chunk in response.aiter_bytes()` | `async for chunk in audio` |
| `async with client.audio.speech.with_streaming_response.create(...) as response:` | No `async with`: call `convert(...)` or `stream(...)` and iterate it |

```python
audio = elevenlabs.text_to_speech.convert(
    voice_id=ELEVENLABS_VOICE_ID,
    text=text,
    model_id="eleven_v4",
)
data = b"".join([chunk async for chunk in audio])
```

Streaming to a client, with the first piece read before the response starts:

```python
audio = elevenlabs.text_to_speech.stream(
    voice_id=ELEVENLABS_VOICE_ID,
    text=text,
    model_id="eleven_v4",
)
first = await audio.__anext__()


async def pieces():
    yield first
    async for chunk in audio:
        yield chunk


return StreamingResponse(pieces(), media_type="audio/mpeg")
```

### JavaScript and TypeScript

`convert` and `stream` resolve to a web `ReadableStream<Uint8Array>`, where OpenAI resolved to a `Response`. Wrap it in a `Response` to get the same helpers back. The request is sent by the call itself, so a failure rejects the `await`, before any audio is read.

| OpenAI | ElevenLabs |
| --- | --- |
| `Buffer.from(await response.arrayBuffer())` | `Buffer.from(await new Response(audio).arrayBuffer())` |
| `await response.blob()` | `await new Response(audio).blob()` |
| `response.body` returned from a route: `new Response(response.body, { headers })` | `new Response(audio, { headers })` |
| `Readable.fromWeb(response.body).pipe(res)` | `Readable.from(audio).pipe(res)` |
| `for await (const chunk of response.body)` | `for await (const chunk of audio)` |

Before:

```typescript
const response = await openai.audio.speech.create({ model: "tts-1", voice: "alloy", input: text });
await fs.promises.writeFile(path, Buffer.from(await response.arrayBuffer()));
```

After:

```typescript
const audio = await elevenlabs.textToSpeech.convert(ELEVENLABS_VOICE_ID, {
  text,
  modelId: "eleven_v4",
});
await fs.promises.writeFile(path, Buffer.from(await new Response(audio).arrayBuffer()));
```

Streaming from a route handler (Next.js, Hono, any `fetch`-style server):

```typescript
const audio = await elevenlabs.textToSpeech.stream(ELEVENLABS_VOICE_ID, {
  text,
  modelId: "eleven_v4",
});
return new Response(audio, { headers: { "Content-Type": "audio/mpeg" } });
```

Streaming from Express or plain Node:

```typescript
import { Readable } from "node:stream";

const audio = await elevenlabs.textToSpeech.stream(ELEVENLABS_VOICE_ID, {
  text,
  modelId: "eleven_v4",
});
res.setHeader("Content-Type", "audio/mpeg");
Readable.from(audio).pipe(res);
```

With a setting kept:

```typescript
const audio = await elevenlabs.textToSpeech.convert(ELEVENLABS_VOICE_ID, {
  text,
  modelId: "eleven_multilingual_v2",
  outputFormat: "pcm_24000",
  voiceSettings: { speed: 1.1 },
});
```

## Direct HTTP calls

A Python or JavaScript/TypeScript project that calls `https://api.openai.com/v1/audio/speech` itself (`requests`, `httpx`, `fetch`, `axios`) moves to the SDK call above: read the request body's fields as the settings in the table, and replace the code that read the HTTP response with the matching row in [How the audio comes back](#how-the-audio-comes-back). Remove the `Authorization` header the call built; the SDK sends the key.

## Errors, retries and timeouts

Keep what the app does when a call fails; change only which error it catches.

### Python

| OpenAI | ElevenLabs |
| --- | --- |
| `openai.APIStatusError`, `openai.APIError` | `elevenlabs.core.ApiError`, with `status_code` and `body` |
| `openai.RateLimitError` | `ApiError` with `status_code == 429` |
| `openai.AuthenticationError` | `ApiError` with `status_code == 401` |
| `openai.BadRequestError` | `ApiError` with `status_code` 400 or 422 |
| `openai.APITimeoutError` | `httpx.TimeoutException` |
| `openai.APIConnectionError` | `httpx.TransportError` |
| `OpenAI(timeout=30)` | `ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"), timeout=30)` (seconds on both) |
| `timeout=30` on one call, `client.with_options(timeout=30)` | `request_options={"timeout_in_seconds": 30}` on the call |
| `OpenAI(max_retries=...)`, `client.with_options(max_retries=...)`, or neither | None for text to speech. See below. |

**Retries.** OpenAI's Python client tries a failed call twice more by default (a 429, a 5xx, a dropped connection). The ElevenLabs Python SDK doesn't retry `text_to_speech.convert` or `stream`, and `max_retries` in `request_options` has no effect on them. Don't write a retry loop: tell the user that text to speech calls are no longer retried, and what `max_retries` was if the app set it. Transcription is retried, twice by default, and takes `request_options={"max_retries": 3}`.

Because the request is sent when the audio is first read, the `try` has to cover the reading:

```python
import httpx
from elevenlabs.core import ApiError

try:
    audio = elevenlabs.text_to_speech.convert(
        voice_id=ELEVENLABS_VOICE_ID,
        text=text,
        model_id="eleven_v4",
        request_options={"timeout_in_seconds": 30},
    )
    data = b"".join(audio)
except ApiError as error:
    if error.status_code == 429:
        ...  # what the app did for openai.RateLimitError
    raise
except httpx.TimeoutException:
    ...  # what the app did for openai.APITimeoutError
```

The OpenAI client fails when it is created without a key. The ElevenLabs client doesn't: a missing key shows up as a 401 on the first call. If the app checked for the key at startup, keep that check, on `ELEVENLABS_API_KEY`.

### JavaScript and TypeScript

| OpenAI | ElevenLabs |
| --- | --- |
| `OpenAI.APIError`, with `status` | `ElevenLabsError`, with `statusCode` and `body` |
| `OpenAI.RateLimitError` | `ElevenLabsError` with `statusCode === 429` |
| `OpenAI.AuthenticationError` | `ElevenLabsError` with `statusCode === 401` |
| `OpenAI.APIConnectionTimeoutError` | `ElevenLabsTimeoutError` |
| `new OpenAI({ timeout: 30_000 })` (milliseconds) | `new ElevenLabsClient({ timeoutInSeconds: 30 })` (seconds) |
| `new OpenAI({ maxRetries: 3 })` | `new ElevenLabsClient({ maxRetries: 3 })`. Both retry twice by default, so drop a `maxRetries: 2`. |
| `{ timeout, maxRetries, signal }` as the call's last argument | `{ timeoutInSeconds, maxRetries, abortSignal }` as the call's last argument |

Retries carry over in JavaScript: both SDKs retry twice by default, text to speech included, so there is nothing to report.

```typescript
import { ElevenLabsError, ElevenLabsTimeoutError } from "@elevenlabs/elevenlabs-js";

try {
  const audio = await elevenlabs.textToSpeech.convert(
    ELEVENLABS_VOICE_ID,
    { text, modelId: "eleven_v4" },
    { timeoutInSeconds: 30, abortSignal: signal },
  );
  return Buffer.from(await new Response(audio).arrayBuffer());
} catch (error) {
  if (error instanceof ElevenLabsTimeoutError) {
    // what the app did for a timeout
  } else if (error instanceof ElevenLabsError && error.statusCode === 429) {
    // what the app did for OpenAI.RateLimitError
  }
  throw error;
}
```
