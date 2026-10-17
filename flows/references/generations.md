# Generations: image, video and speech

One generation is one model call. Each modality has its own endpoint; the request and response shapes are the same across them.

| Endpoint | Python | TypeScript | CLI |
|----------|--------|------------|-----|
| `POST /v1/flows/image` | `client.flows.image.create(request=...)` | `client.flows.image.create({...})` | `elevenlabs flows image create --json '{...}'` |
| `POST /v1/flows/video` | `client.flows.video.create(request=...)` | `client.flows.video.create({...})` | `elevenlabs flows video create --json '{...}'` |
| `POST /v1/flows/text-to-speech` | `client.flows.text_to_speech.create(request=...)` | `client.flows.textToSpeech.create({...})` | `elevenlabs flows text-to-speech create --json '{...}'` |
| `GET /v1/flows/{modality}/{generation_id}` | `.get(generation_id)` | `.get(generationId)` | `... get --generation-id ID` |
| `GET /v1/flows/{modality}` | `.list(page_size=, status=, model_id=, cursor=)` | `.list({...})` | `... list` |

Every create has a `create_and_wait` / `createAndWait` / `create-and-wait` variant that waits for the terminal status (see [Wait](#wait-for-the-result)).

## The request body is keyed by `model_id`

The body is a union discriminated on `model_id`; each model accepts only its own fields. An unknown field or a wrong type is rejected with 422, and an invalid combination (e.g. `end_frame` without `start_frame`) with a validation error naming the field. Neither starts or charges a generation.

- **Python**: one request class per model, named `<Modality>GenerationRequest_<Model>`, passed as `request=`. Examples: `ImageGenerationRequest_Gemini3ProImage`, `ImageGenerationRequest_GptImage2`, `VideoGenerationRequest_Veo31FastGenerate001`, `VideoGenerationRequest_CreatifyAurora`, `TextToSpeechGenerationRequest_ElevenV3`. The class sets `model_id` itself.
- **TypeScript**: a plain object with `modelId` and camelCased fields (`aspectRatio`, `durationSecs`, `startFrame`).
- **REST / CLI `--json`**: snake_case JSON with `model_id`.

### Models

| Modality | `model_id` | Media fields |
|----------|-----------|--------------|
| Image | `gpt-image-1`, `gpt-image-1.5` | `images` (up to 5), `mask` |
| Image | `gpt-image-2`, `gpt-image-2.5-sunburst`, `gpt-image-2.5-flare` | `images` (up to 10), `mask` |
| Image | `gemini-2.5-flash-image` | `images` (up to 5) |
| Image | `gemini-3-pro-image` | `images` (up to 10) |
| Image | `gemini-3.1-flash-image`, `gemini-3.1-flash-lite-image` | `images` (up to 14) |
| Image | `bytedance-seedream-5-lite`, `bytedance-seedream-5-pro` | `images` (up to 10) |
| Video | `veo-3.1-generate-001`, `veo-3.1-fast-generate-001` | `start_frame`, `end_frame`, or up to 3 `images` as `{"image": <ref>, "role": "subject" \| "style"}` (8 s only, not with frames) |
| Video | `bytedance-seedance-v2`, `-v2-fast`, `-v2-mini`, `-v2.5` | `start_frame`, `end_frame`, or `images` / `videos` / `audios` (not with frames) |
| Video | `creatify-aurora` (lip-sync) | `image` and `audio`, both required |
| Speech | `eleven_v3`, `eleven_multilingual_v2`, `eleven_flash_v2_5` | none; takes `text` and `voice` (a voice id string) |

Image and video requests take `prompt`; other output controls (`aspect_ratio`, `resolution`, `duration_secs`, `generate_audio`, `quality`, `seed`) vary per model. `end_frame` always needs `start_frame`. ByteDance models are off by default and return `model_access_denied` until support enables them. When unsure of a model's fields, read the SDK's request class or the [model table](https://elevenlabs.io/docs/eleven-api/guides/cookbooks/image-and-video#available-models). When the user names no model: `gemini-3-pro-image` for images, `veo-3.1-fast-generate-001` for video, `eleven_v3` for speech.

### One image

```python
import os
from elevenlabs import ElevenLabs, ImageGenerationRequest_Gemini3ProImage

client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

image = client.flows.image.create_and_wait(
    request=ImageGenerationRequest_Gemini3ProImage(
        prompt="A white sneaker on a pastel studio backdrop, soft shadow",
        aspect_ratio="1:1",
        resolution="2K",
    ),
    wait_timeout_in_seconds=300,
)
if image.status == "completed":
    print(image.content_url, image.content_mime_type)
else:
    print("failed:", image.failure_reason, image.error_message)
```

```typescript
const image = await client.flows.image.createAndWait(
  { modelId: "gemini-3-pro-image", prompt: "A white sneaker on a pastel studio backdrop", aspectRatio: "1:1" },
  { waitTimeoutInSeconds: 300 },
);
if (image.status === "completed") console.log(image.contentUrl);
```

```bash
elevenlabs flows image create-and-wait --json '{"model_id": "gemini-3-pro-image", "prompt": "A white sneaker on a pastel studio backdrop"}' \
  | jq -r .content_url
```

### Speech

```python
from elevenlabs import TextToSpeechGenerationRequest_ElevenV3

speech = client.flows.text_to_speech.create_and_wait(
    request=TextToSpeechGenerationRequest_ElevenV3(
        text="Meet the lightest running shoe we've ever made.",
        voice="JBFqnCBsd6RMkjVDRZzb",  # a voice id from the workspace
    ),
)
```

Output is MP3 (`audio/mpeg`).

## Reference media

Every media field takes a reference object tagged with `type`. There is **no URL reference type**.

| `type` | Points at | Fields | Python class |
|--------|-----------|--------|--------------|
| `generation` | Another generation's output, **finished or still pending** | `generation_id` | `ImageReference_Generation`, `VideoReference_Generation`, `AudioReference_Generation` |
| `asset` | A file uploaded with `POST /v1/assets` | `asset_id` | `ImageReference_Asset`, ... |
| `inline_base64` | Bytes in the request body, up to 25 MB decoded, not kept after the generation | `content_base64`, `mime_type` | `ImageReference_InlineBase64(content_base_64=..., mime_type=...)` |
| `voice` | A workspace voice | `voice_id` | `TemplateInputReference_Voice`; only for template `voice` inputs. TTS generations take `voice` as a plain id string |

In Python the inline field is `content_base_64`; in TypeScript `contentBase64`; in JSON `content_base64`.

Inline MIME types: images `image/jpeg`, `image/png`, `image/webp`, `image/heic`, `image/heif`; audio `audio/mpeg`, `audio/wav`; video `video/mp4`, `video/quicktime`, `video/webm`.

### Upload a file as an asset

Use an asset for anything reused, anything over 25 MB, and every file in production.

```python
with open("sneaker.jpg", "rb") as f:
    asset = client.assets.create(asset=f, name="sneaker.jpg")
ref = ImageReference_Asset(asset_id=asset.asset_id)
```

```typescript
import { createReadStream } from "fs";
const asset = await client.assets.create({ asset: createReadStream("sneaker.jpg"), name: "sneaker.jpg" });
const ref = { type: "asset", assetId: asset.assetId };
```

```bash
asset_id=$(elevenlabs assets create --asset ./sneaker.jpg --name sneaker --query asset_id | jq -r .)
```

`client.assets.create` also accepts bytes, a `Buffer`, a `Blob` or a `File`. Assets belong to the workspace and count against its storage limit (`asset_storage_limit_exceeded`); manage them with `assets.list`, `assets.get`, `assets.delete`.

### A file at a remote URL

The public API has no "create asset from URL" route. Download the file on your server, then upload it with `POST /v1/assets` (or send it as `inline_base64` if it is under 25 MB and used once):

```python
import requests
response = requests.get(url, timeout=60)
response.raise_for_status()
asset = client.assets.create(asset=("input.jpg", response.content, response.headers["content-type"]), name="input.jpg")
```

When the hosted MCP is connected, `creative_attach_reference_file` imports a direct https URL as an asset in the user's workspace and returns its id.

## Chain generations

Pass the first generation's `id` as a `generation` reference into the next create **immediately**, without waiting. The API queues the dependent generation and starts it when its input finishes. Chains can be any depth and width.

- Put `webhook` (or `create_and_wait`) on the **last** step only. Intermediate steps need no polling.
- If an upstream step fails, every dependent fails with `failure_reason: "dependency_failed"`, and nothing in the collapsed chain is charged.
- A `generation_id` that doesn't exist in the workspace is rejected on create.
- Each step is still fetched from its own modality's endpoint (`flows.image.get` for the image, `flows.video.get` for the video).

### Image → video (Python)

```python
from elevenlabs import (
    ImageGenerationRequest_Gemini3ProImage,
    ImageReference_Generation,
    VideoGenerationRequest_Veo31FastGenerate001,
)

still = client.flows.image.create(
    request=ImageGenerationRequest_Gemini3ProImage(
        prompt="A white sneaker on a pastel studio backdrop",
        aspect_ratio="16:9",
    )
)
# still.status is "pending"; don't wait for it.
clip = client.flows.video.create_and_wait(
    request=VideoGenerationRequest_Veo31FastGenerate001(
        prompt="Slow 360° turntable of the sneaker, soft studio light",
        start_frame=ImageReference_Generation(generation_id=still.id),
        duration_secs=8,
        aspect_ratio="16:9",
    ),
    wait_timeout_in_seconds=900,
)
if clip.status == "completed":
    print(clip.content_url)  # video/mp4
else:
    print("failed:", clip.failure_reason, clip.error_message)
```

For production, call `client.flows.video.create(request=VideoGenerationRequest_Veo31FastGenerate001(..., webhook=WebhookTarget_All()))` instead of `create_and_wait`, and handle the `flows_generation` event for `clip.id`.

### Image → video (TypeScript)

```typescript
const still = await client.flows.image.create({
  modelId: "gemini-3-pro-image",
  prompt: "A white sneaker on a pastel studio backdrop",
  aspectRatio: "16:9",
});
const clip = await client.flows.video.create({
  modelId: "veo-3.1-fast-generate-001",
  prompt: "Slow 360° turntable of the sneaker",
  startFrame: { type: "generation", generationId: still.id },
  durationSecs: 8,
  webhook: { type: "all" }, // only the last step
});
```

### Speech → talking video

```python
from elevenlabs import (
    AudioReference_Generation,
    ImageReference_Asset,
    TextToSpeechGenerationRequest_ElevenV3,
    VideoGenerationRequest_CreatifyAurora,
    WebhookTarget_All,
)

line = client.flows.text_to_speech.create(
    request=TextToSpeechGenerationRequest_ElevenV3(text="Hi, I'm Ava.", voice="JBFqnCBsd6RMkjVDRZzb")
)
talking = client.flows.video.create(
    request=VideoGenerationRequest_CreatifyAurora(
        image=ImageReference_Asset(asset_id=portrait_asset_id),
        audio=AudioReference_Generation(generation_id=line.id),
        webhook=WebhookTarget_All(),
    )
)
```

## Wait for the result

- `create_and_wait` (Python), `createAndWait` (TypeScript, options `{ waitTimeoutInSeconds }`), `elevenlabs flows <modality> create-and-wait --json '...'`: start, then check at the server's `Retry-After` until `completed` or `failed`.
- A failed generation is returned, not raised. On timeout the SDKs raise `FlowsWaitTimeoutError` (Python: `from elevenlabs.flows_custom import FlowsWaitTimeoutError`) carrying `id`; the generation keeps running.
- `wait_timeout_in_seconds` bounds the whole wait; `timeout` / `timeoutInSeconds` is per HTTP request, not this.
- Without the helpers: [Polling by hand](polling.md); the same loop works on `GET /v1/flows/{modality}/{generation_id}`.

## Get the result by webhook

Pass `webhook: {"type": "all"}` (Python `WebhookTarget_All()`), or `{"type": "ids", "ids": [...]}`, on create. The workspace needs a webhook subscribed to the `flows` event; setup, rejections (`no_webhooks_configured`, `invalid_webhook_id`, `webhook_disabled`) and handlers are in [Templates](templates.md#get-the-result-by-webhook-production) and [Webhook handlers](webhooks.md). A generation delivers a `flows_generation` event whose `data` is the terminal GET response:

```json
{"type": "flows_generation", "event_timestamp": 1739721600,
 "data": {"id": "GENERATION_ID", "status": "completed", "content_url": "https://...", "content_mime_type": "video/mp4"}}
```

A failed one carries `failure_reason` and `error_message` instead. The event doesn't say which modality it was; key your records by generation id.

## Response fields

| `status` | Fields |
|----------|--------|
| `pending`, `generating` | `id`, `status` (unfinished GETs carry `Retry-After`) |
| `completed` | `content_url` (signed, ~1 hour), `content_mime_type` |
| `failed` | `failure_reason` (`timeout`, `model_error`, `moderated`, `invalid_parameters`, `dependency_failed`, `charging_failed`, `internal_error`), `error_message` |

Failed generations are not charged. `list` returns only generations created through this API (not the app), newest first.
