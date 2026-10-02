# Using the Procedure API

Procedures are reusable instruction blocks that an agent runs when a trigger matches. Use the ElevenLabs CLI by default to create, edit, and publish them. Python and JavaScript SDKs are also available for application code. Reference: [Procedures](https://elevenlabs.io/docs/eleven-agents/customization/procedures.md) · [API Reference](https://elevenlabs.io/docs/api-reference/agents/procedures/).

For what belongs in `trigger` and `content`, see [Writing Procedures](writing-procedures.md).

One term to know: turning a structured procedure's steps into the form the agent executes is called compiling. The platform compiles every structured procedure on the branch when you publish; you never compile anything yourself or send a `workflow` in a request. The compiled result is currently visible as read-only nodes in the dashboard's Workflow tab.

The CLI exposes the complete procedure lifecycle, including draft operations.

## Prerequisites

- `ELEVENLABS_API_KEY` is set, with the `CONVAI_READ` and `CONVAI_WRITE` scopes.
- Reading requires the viewer role on the target agent. Creating, updating, removing, and publishing require the editor role. Publishing to a protected branch requires admin.
- The target `agent_id` is known.
- The target `branch_id` is known. If not, read `main_branch_id` with `elevenlabs agents get --agent-id "$AGENT_ID" --query main_branch_id`, or list branches with `elevenlabs agents branches list --agent-id "$AGENT_ID"`.

```bash
AGENT_ID="your-agent-id"
BRANCH_ID="your-branch-id"
```

The CLI reads `ELEVENLABS_API_KEY` from the environment automatically; never pass the key as a flag, and never print or persist it.

## CLI

Use these command groups for procedure management:

| Operation | Command |
|-----------|---------|
| List, create, read, remove | `elevenlabs agents procedures ...` |
| Read, update, discard draft | `elevenlabs agents procedures drafts ...` |
| Publish pending changes | `elevenlabs agents update` |

Use `--dry-run` to validate and inspect a generated request without sending it. Use `--schema`
on any command to inspect its machine-readable input and output contract.

## SDKs

Procedure APIs are available in both SDKs starting in `2.60.0`. Earlier versions do not include a `procedures` client, so install at or above that version:

```bash
pip install "elevenlabs>=2.60.0"
npm install @elevenlabs/elevenlabs-js@^2.60.0
```

For JavaScript, use `@elevenlabs/elevenlabs-js`. The unscoped `elevenlabs` npm package is the deprecated v1.x and has no procedures client at any version.

Both clients read `ELEVENLABS_API_KEY` from the environment; never pass a literal key.

Use these SDK methods for the procedure endpoints. Python nests them under `client.conversational_ai.agents`; JavaScript uses `client.conversationalAi.agents`:

| Operation | Endpoint | Method |
|-----------|----------|--------|
| List | `GET .../procedures` | `procedures.list` |
| Create | `POST .../procedures` | `procedures.create` |
| Read branch HEAD | `GET .../procedures/{procedure_id}` | `procedures.get` |
| Read draft | `GET .../procedures/{procedure_id}/draft` | `procedures.drafts.get` |
| Update draft | `PATCH .../procedures/{procedure_id}/draft` | `procedures.drafts.update` |
| Discard draft | `DELETE .../procedures/{procedure_id}/draft` | `procedures.drafts.delete` |
| Remove | `DELETE .../procedures/{procedure_id}` | `procedures.remove` |
| Publish | `PATCH /v1/convai/agents/{agent_id}?branch_id=...` | `agents.update` |

SDK notes:

- JavaScript takes the IDs positionally, then a body object. Python takes keyword arguments — except `procedures.create`, which takes its body as `request=CreateProcedureRequestModel(...)`. Flat keywords on `create` raise `TypeError`.
- Read one historical version with `procedures.get(..., version_id=...)` or `procedures.get(agentId, branchId, procedureId, { versionId })`.
- Pass `agent_version_id` to `procedures.list` or `procedures.get` to resolve the procedures attached to a specific agent version.
- To publish, call `agents.update` with `branch_id` and an optional `version_description`. That is the whole call.

The flow below creates a free-form procedure, edits its draft, and publishes it.

### Python

```python
from elevenlabs import ElevenLabs
from elevenlabs.types import CreateProcedureRequestModel

client = ElevenLabs()
procedures = client.conversational_ai.agents.procedures

created = procedures.create(
    agent_id=AGENT_ID,
    branch_id=BRANCH_ID,
    request=CreateProcedureRequestModel(
        name="Refund requests",
        type="free_form",
        trigger="When the user asks for a refund",
        content="Confirm the order number, check eligibility, and explain the next step.",
    ),
)

draft = procedures.drafts.get(
    agent_id=AGENT_ID, branch_id=BRANCH_ID, procedure_id=created.procedure_id
)
procedures.drafts.update(
    agent_id=AGENT_ID,
    branch_id=BRANCH_ID,
    procedure_id=created.procedure_id,
    name=draft.name,
    type="free_form",
    trigger=draft.trigger,
    content="Confirm the order number. Check refund eligibility. Explain the refund timeline.",
)

client.conversational_ai.agents.update(
    agent_id=AGENT_ID,
    branch_id=BRANCH_ID,
    version_description="Publish refund procedure",
)
```

If the branch has structured procedures, the publish validates them. Catch the validation error and repair the procedure draft:

```python
from elevenlabs.errors import BadRequestError

try:
    client.conversational_ai.agents.update(
        agent_id=AGENT_ID,
        branch_id=BRANCH_ID,
        version_description="Publish refund procedure",
    )
except BadRequestError as error:
    detail = error.body.get("detail", {})
    if detail.get("status") == "procedure_validation_failed":
        for procedure_id, errors in detail["data"]["errors"].items():
            for item in errors:
                print(procedure_id, item["path"], item["message"])
    raise
```

### JavaScript

```javascript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const client = new ElevenLabsClient();
const procedures = client.conversationalAi.agents.procedures;

const created = await procedures.create(agentId, branchId, {
  name: "Refund requests",
  type: "free_form",
  trigger: "When the user asks for a refund",
  content: "Confirm the order number, check eligibility, and explain the next step.",
});

const draft = await procedures.drafts.get(agentId, branchId, created.procedureId);
await procedures.drafts.update(agentId, branchId, created.procedureId, {
  name: draft.name,
  type: "free_form",
  trigger: draft.trigger,
  content: "Confirm the order number. Check refund eligibility. Explain the refund timeline.",
});

await client.conversationalAi.agents.update(agentId, {
  branchId,
  versionDescription: "Publish refund procedure",
});
```

If the branch has structured procedures, the publish validates them. Catch the validation error and repair the procedure draft:

```javascript
import { ElevenLabsError } from "@elevenlabs/elevenlabs-js";

try {
  await client.conversationalAi.agents.update(agentId, {
    branchId,
    versionDescription: "Publish refund procedure",
  });
} catch (error) {
  if (error instanceof ElevenLabsError && error.statusCode === 400) {
    const detail = error.body?.detail;
    if (detail?.status === "procedure_validation_failed") {
      for (const [procedureId, errors] of Object.entries(detail.data.errors)) {
        for (const item of errors) console.error(procedureId, item.path, item.message);
      }
    }
  }
  throw error;
}
```

## Procedure Lifecycle

- Procedures belong to an agent branch. Drafts are scoped to the current user.
- Create, update, discard, and remove act on your draft working set. Nothing reaches the live agent until you publish.
- Publishing is not a procedure endpoint. Use `PATCH /v1/convai/agents/{agent_id}?branch_id=...` to version all changed procedure drafts on the branch.
- Each branch maps every `procedure_id` to a published `version_id`, or to no version while only a draft exists. A branch-HEAD read therefore returns `404` until the first publish.
- Publishing validates structured procedures. If one is invalid, the publish fails with `procedure_validation_failed` and nothing is written. See [Publish](#publish). To run the same check without publishing, save an agent draft; see [Validate without publishing](#validate-without-publishing).
- A procedure's `type` cannot change after creation. A draft update with a different `type` is rejected.
- Draft writes are last-write-wins. Read the draft immediately before editing and avoid concurrent writers.

Reads resolve against different sources:

| Request | Returns |
|---------|---------|
| `GET .../procedures/{procedure_id}` | Branch HEAD. `404` until the procedure's first publish. |
| `GET .../procedures/{procedure_id}/draft` | Your draft, falling back to branch HEAD when you have none. |
| `GET .../procedures/{procedure_id}?version_id=...` | One pinned, immutable historical version. |

## List Procedures

List the effective working set:

```bash
elevenlabs agents procedures list \
  --agent-id "$AGENT_ID" --branch-id "$BRANCH_ID"
```

In the SDKs, pass `agent_version_id` when you need the procedure versions attached to one
immutable agent version.

Each entry carries `procedure_id`, `version_id`, `name`, `type`, `trigger`, and `has_draft`. `has_draft` is true when the procedure has unpublished draft changes on this branch, in which case its `name`, `type`, and `trigger` reflect that draft. `version_id` is the version published on this branch, and is null exactly when `has_draft` is true — including for a procedure that was published earlier and has since been edited.

The list does not include procedure content. Read a body with `GET .../procedures/{procedure_id}` or its `/draft` variant.

## Create

```bash
CREATE_RESPONSE=$(
  elevenlabs agents procedures create \
    --agent-id "$AGENT_ID" --branch-id "$BRANCH_ID" \
    --json '{
      "name": "Refund requests",
      "type": "free_form",
      "trigger": "When the user asks for a refund",
      "content": "Confirm the order number, check eligibility, and explain the next step."
    }'
)
PROCEDURE_ID=$(printf '%s' "$CREATE_RESPONSE" | jq -r '.procedure_id')
```

Fail if `procedure_id` is empty or null.

A structured procedure uses the same endpoint with `type` set to `deterministic` and its steps JSON-encoded into `content`. See [Writing Procedures](writing-procedures.md) for what belongs in `trigger` and `content`, and for building that JSON string.

## Read and Update the Draft

```bash
elevenlabs agents procedures drafts get \
  --agent-id "$AGENT_ID" --branch-id "$BRANCH_ID" --procedure-id "$PROCEDURE_ID"

elevenlabs agents procedures drafts update \
  --agent-id "$AGENT_ID" --branch-id "$BRANCH_ID" --procedure-id "$PROCEDURE_ID" \
  --json '{
    "name": "Refund requests",
    "type": "free_form",
    "trigger": "When the user asks for a refund",
    "content": "Confirm the order number. Check refund eligibility. Explain the refund timeline."
  }'
```

Treat the draft update body as a full replacement. Read the current draft, preserve `name` and `trigger` unless the user requested changes to them, and send them with the new `content`. Always send the existing `type`; it cannot change after creation, and a different value is rejected with `procedure_type_cannot_change`. Always send `trigger` explicitly rather than relying on a trigger embedded in `content`.

Publish with the flow under [Publish](#publish).

## Publish

One publish versions every changed procedure draft on the branch:

```bash
elevenlabs agents update \
  --agent-id "$AGENT_ID" --branch-id "$BRANCH_ID" \
  --json '{"version_description": "Publish refund procedure"}'
```

If the branch has structured procedures, the publish validates each one and, if all pass, publishes them in the new version. The publish above is the whole call. This also runs when the change was free-form only, and when the last structured procedure was removed, in which case its compiled result is removed.

On a validation failure the publish returns `400` and nothing is written:

```json
{
  "detail": {
    "status": "procedure_validation_failed",
    "message": "Structured procedures failed validation.",
    "data": {
      "errors": {
        "agtprc_abc123": [
          { "path": "steps[0].ask.instruction", "message": "Step 1: Ask step requires an instruction" }
        ]
      }
    }
  }
}
```

`errors` is keyed by procedure ID. Each entry carries the `path` of the offending field and a message naming the step. Repair every entry in the procedure draft and publish again. Each attempt reports the errors detected in that pass; fixing field-level errors may reveal structural errors on the next pass.

Saving a procedure draft with `PATCH .../procedures/{procedure_id}/draft` does not validate structured content. The check happens at publish, or at agent draft save as described next.

The legacy `POST .../procedures/compile` endpoint still exists as a dry-run for existing callers, but do not use it. It will eventually be deprecated.

### Validate without publishing

A failed publish writes nothing, so when you are ready to publish, the publish itself is the validation step. Use the flow below only when you need to check structured content and are not ready to publish, for example while other edits on the branch are still pending, or on a protected branch you cannot publish to.

Saving an agent draft runs the same validation as publish and returns the same `procedure_validation_failed` payload. This is how the dashboard surfaces errors while editing. The endpoint is `POST /v1/convai/agents/{agent_id}/drafts?branch_id=...` (`agents.drafts.create` in the SDKs). There is no CLI command for it.

The body is the full agent draft, not a flag: `name`, `conversation_config`, `platform_settings`, and `workflow` are all required. Read them from the agent and resend them unchanged. Do not edit anything else in that body; a validation check is not the place to change agent configuration.

```bash
AGENT=$(
  curl -sS "https://api.elevenlabs.io/v1/convai/agents/$AGENT_ID?branch_id=$BRANCH_ID" \
    -H "xi-api-key: $ELEVENLABS_API_KEY"
)

curl -sS -X POST "https://api.elevenlabs.io/v1/convai/agents/$AGENT_ID/drafts?branch_id=$BRANCH_ID" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(printf '%s' "$AGENT" | jq '{name, conversation_config, platform_settings, workflow}')"
```

A `400` with `procedure_validation_failed` carries the same `errors` map as a failed publish. Repair the procedure draft with `PATCH .../procedures/{procedure_id}/draft` and save the agent draft again.

A `200` means every structured procedure on the branch validated, and it also stored an agent draft for you on that branch. If you only wanted the check, discard it with `DELETE /v1/convai/agents/{agent_id}/drafts?branch_id=...` (`agents.drafts.delete`) so it does not linger as an unsaved change in the dashboard. Discarding the agent draft does not touch your procedure drafts.

Verify a published procedure and record its `version_id`:

```bash
elevenlabs agents procedures get \
  --agent-id "$AGENT_ID" --branch-id "$BRANCH_ID" --procedure-id "$PROCEDURE_ID"
```

## Discard Edits

Discard only your own unpublished draft:

```bash
elevenlabs agents procedures drafts delete \
  --agent-id "$AGENT_ID" --branch-id "$BRANCH_ID" --procedure-id "$PROCEDURE_ID"
```

This restores the branch-HEAD version. For a procedure that was never published, it deletes the procedure. Read the draft afterwards to confirm what remains.

## Remove a Procedure

Stage the removal:

```bash
elevenlabs agents procedures remove \
  --agent-id "$AGENT_ID" --branch-id "$BRANCH_ID" --procedure-id "$PROCEDURE_ID"
```

This removes the procedure from the branch working set. It does not erase versions still referenced by agent history.

The removal remains a draft until published. Publishing removes the compiled result of a structured procedure along with it. Then confirm that the procedure is absent from the list and that a branch-HEAD lookup returns `404`.

## Error Handling

Common errors:
- **400** from publish or agent draft save, with `status` `procedure_validation_failed`: a structured procedure is invalid. Fix every entry under `detail.data.errors` and publish again.
- **400** from a procedure draft update, with `procedure_type_cannot_change`: the body's `type` differs from the procedure's type. Resend the existing type.
- **401**: `ELEVENLABS_API_KEY` is unset or invalid.
- **403**: the key lacks `CONVAI_READ`/`CONVAI_WRITE`, the agent role is too low, or the branch is protected and only admins may publish to it.
- **404**: verify that the agent, branch, and procedure IDs belong together. Before a procedure's first publish, read the draft endpoint rather than branch HEAD.

The SDKs raise for these responses. The payload is on `error.body`, and the status is on `error.status_code` in Python or `error.statusCode` in JavaScript.

Do not blindly retry create, update, delete, or publish requests. Read current state before deciding whether a retry is safe.
