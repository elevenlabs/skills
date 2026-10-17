# Access and errors

Every Flows route needs a logged-in caller (an API key or OAuth token), a workspace on Pro or above, and the route's permission. Error bodies carry `detail.code`, `detail.status` and `detail.message`; read them, not only the HTTP status.

## Map the status to the cause

| Status | `code` | Cause | Tell the user |
|--------|--------|-------|---------------|
| 401 | `unauthorized` | The key is missing, mistyped, revoked, or sent in the wrong header | Send it as `xi-api-key: <key>` (or set `ELEVENLABS_API_KEY` for the SDK/CLI); create a new key at Settings → API Keys if it was revoked |
| 401 | `unauthorized`, `status: missing_permissions` ("The API key you used is missing the permission ...") | The key lacks **Image & Video** (or **Text to Speech** for `/v1/flows/text-to-speech`) | Edit the key's permissions at Settings → API Keys, or create a key with them |
| 402 | `paid_plan_required` | The key's workspace is below Pro | Upgrade the workspace to Pro or above, or use a key from a workspace that is |
| 403 | `forbidden`, `status: missing_group_permissions` | The key's user has no Image & Video access in their workspace role | Ask a workspace admin to grant it |
| 403 | `forbidden`, "You do not have access to this template." | The template is private ("Just me") and the caller isn't its author, or it's shared with **Workspace** and the caller is in a different workspace | Ask the author to share it with the caller's workspace, turn on link sharing, or publish it; or run it with a key belonging to the author |
| 404 | `template_not_found` | No template has this id: a typo, a deleted template, or an id that isn't a template id (a run id, version id or asset id) | Re-copy the id from the `/app/templates/<id>` URL. Anonymous callers also get 404 for private templates, but API calls are never anonymous, so through the API a 404 means the id is wrong |
| 404 | `run_not_found` | The run id is wrong, belongs to a different template id, or was created by a different user | Runs are only readable by the user whose key created them; fetch with the same key and the run's own `template_id` |
| 404 | `content_generation_not_found` | The generation id is wrong, or it's fetched from the wrong modality endpoint | Fetch a video from `/v1/flows/video/{id}`, an image from `/v1/flows/image/{id}` |
| 403 | `model_access_denied` | Governance blocks a model the request (or one of the template version's nodes) uses. The message names the models. ByteDance models are off until support enables them | For a template: pin a `version_id` that `flows.templates.get` lists, run it in the app, or ask the author to publish a version on [API models](https://elevenlabs.io/docs/eleven-api/guides/cookbooks/image-and-video#available-models). For a generation: switch models, or ask a workspace admin / support to allow it |
| 400 | `invalid_parameters` | Missing or unknown template input ids, a value of the wrong shape for its port, an invalid field combination, or a template with no published version | Fix the field named in `param` |
| 422 | validation error | The JSON doesn't match the schema: unknown field for that `model_id`, wrong type, a reference without `type` | Compare with the SDK request class |
| 429 | `rate_limit_error` type | Too many status checks for this key | Wait `Retry-After` seconds; use `create_and_wait` or a webhook |
| 400 | `invalid_parameters`, `status`: `no_webhooks_configured`, `invalid_webhook_id` or `webhook_disabled` | `webhook` was requested but no subscribed, enabled webhook matches | Subscribe a webhook to the `flows` event, or re-enable it (see [Templates](templates.md#get-the-result-by-webhook-production)) |
| 400 | `bad_request`, `status: asset_storage_limit_exceeded` | Uploading would exceed the workspace's asset storage | Delete unused assets with `assets.delete` |

Before suggesting a fix for a 401 or 403 on a template, confirm which case it is: a key or role problem also fails `flows.image.list()`; a template access problem doesn't.

## Who can run a template

| Sharing | Who can read and run it through the API |
|---------|-----------------------------------------|
| **Just me** (private) | Only its author (and anyone the author added to the flow). Everyone else gets 403 |
| **Workspace** | Members of the template's workspace. Other workspaces get 403 |
| **Link sharing** | Anyone with the id, in any workspace |
| **Explore** (public) | Anyone |

Each run is charged to the caller's workspace, not the author's.

## "It's not in `templates.list`"

`flows.templates.list` returns only published templates of the caller's own workspace. These don't appear but still work by id with `flows.templates.get` and `runs.create`:

- templates shared by link from another workspace,
- templates published to Explore from another workspace.

A template with no published version isn't listed and can't be run, except by its author pinning a saved snapshot's `version_id`.

## `versions` is empty

`flows.templates.get` returns the template with `versions: []` when no published version can run through the API for this caller, usually because a node uses a model the API doesn't offer. Running it is rejected with `model_access_denied`. Run it in the app, or ask the author to switch those nodes to API models and publish again.
