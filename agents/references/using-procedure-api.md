# Using the Procedure API

Procedures are reusable instruction blocks that an agent runs when a trigger matches. Create, edit, compile, and publish them with the Python or JavaScript SDK, or from the shell with the ElevenLabs CLI. Reference: [Procedures](https://elevenlabs.io/docs/eleven-agents/customization/procedures.md) · [API Reference](https://elevenlabs.io/docs/api-reference/agents/procedures/).

For what belongs in `trigger` and `content`, see [Writing Procedures](writing-procedures.md).

Procedures are in Alpha. The feature set and the content schema are still changing, and some changes may break. Check the reference pages above before relying on a detail here.

## Prerequisites

- `ELEVENLABS_API_KEY` is set, with the `CONVAI_READ` and `CONVAI_WRITE` scopes.
- Reading requires the viewer role on the target agent. Creating, updating, removing, compiling, and publishing require the editor role. Publishing to a protected branch requires admin.
- The target `agent_id` is known.
- The target `branch_id` is known. If not, read `main_branch_id` with `elevenlabs agents get --agent-id "$AGENT_ID" --query main_branch_id`, or list branches with `elevenlabs agents branches list --agent-id "$AGENT_ID"`.

```bash
AGENT_ID="your-agent-id"
BRANCH_ID="your-branch-id"
```

The CLI reads `ELEVENLABS_API_KEY` from the environment automatically; never pass the key as a flag, and never print or persist it.

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
| Compile | `POST .../procedures/compile` | `procedures.compile` |
| Publish | `PATCH /v1/convai/agents/{agent_id}?branch_id=...` | `agents.update` |

SDK notes:

- JavaScript takes the IDs positionally, then a body object. Python takes keyword arguments — except `procedures.create`, which takes its body as `request=CreateProcedureRequestModel(...)`. Flat keywords on `create` raise `TypeError`.
- Read one historical version with `procedures.get(..., version_id=...)` or `procedures.get(agentId, branchId, procedureId, { versionId })`.
- For structured changes, pass the `workflow` returned by `procedures.compile` to `agents.update`.

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

If the pending changes include structured procedures, compile before publishing:

```python
from elevenlabs.errors import BadRequestError

try:
    compiled = procedures.compile(agent_id=AGENT_ID, branch_id=BRANCH_ID)
except BadRequestError as error:
    print(f"Compile failed, nothing published: {error.body}")
    raise

client.conversational_ai.agents.update(
    agent_id=AGENT_ID,
    branch_id=BRANCH_ID,
    workflow=compiled.workflow,
    version_description="Publish refund procedure",
)
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

If the pending changes include structured procedures, compile before publishing:

```javascript
import { ElevenLabsError } from "@elevenlabs/elevenlabs-js";

try {
  const compiled = await procedures.compile(agentId, branchId);
  await client.conversationalAi.agents.update(agentId, {
    branchId,
    workflow: compiled.workflow,
    versionDescription: "Publish refund procedure",
  });
} catch (error) {
  if (error instanceof ElevenLabsError && error.statusCode === 400) {
    console.error("Compile or publish failed, nothing published:", error.body);
  }
  throw error;
}
```

## Procedure Lifecycle

- Procedures belong to an agent branch. Drafts are scoped to the current user.
- Create, update, discard, and remove act on your draft working set. Nothing reaches the live agent until you publish.
- Publishing is not a procedure endpoint. Use `PATCH /v1/convai/agents/{agent_id}?branch_id=...` to version all changed procedure drafts on the branch.
- Each branch maps every `procedure_id` to a published `version_id`, or to no version while only a draft exists. A branch-HEAD read therefore returns `404` until the first publish.
- Compile structured-procedure changes before publishing. Publish free-form-only changes without compiling. See [Compile and Publish](#compile-and-publish).
- Structured content has no dry-run. Save the draft, compile to validate it, and repair what compile reports. See [Compile and Publish](#compile-and-publish).
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

Treat the draft update body as a full replacement. Read the current draft, preserve `name`, `type`, and `trigger` unless the user requested changes to them, and send them with the new `content`. The API accepts an omitted `trigger` and then derives it from `content`; omit it only when that is intentional. Preserve `type` unless the user explicitly requests a conversion.

Publish with the flow under [Compile and Publish](#compile-and-publish).

## Compile and Publish

One publish versions every changed procedure draft on the branch:

```bash
elevenlabs agents update \
  --agent-id "$AGENT_ID" --branch-id "$BRANCH_ID" \
  --json '{"version_description": "Publish refund procedure"}'
```

Compile only when structured procedures have changed. Compilation turns structured drafts into workflow nodes and merges them into the existing agent workflow. The agent loads free-form procedures from their published versions at the start of a conversation, so publish free-form-only changes without `workflow`.

Also compile after removing the last structured procedure; compilation removes the workflow nodes generated for it.

Compilation requires a pending draft on the branch. With nothing staged, it fails with `no_draft_to_compile`, which also means there is nothing to publish.

Compilation validates structured content using saved drafts rather than an inline request body:

1. Save the content as a draft. A draft that does not validate still saves.
2. Compile. On `400`, `errors` is keyed by procedure ID, and each entry carries the `path` of the offending field and a message naming the step, such as `steps[0].ask.instruction` and `Step 1: Ask step requires an instruction`.
3. Repair every entry and compile again. Each compile returns the errors detected in that pass; fixing field-level errors may reveal structural errors on the next pass. Continue until compile returns a workflow.
4. Publish, sending that `workflow` with the publish.

```bash
WORKFLOW=$(
  elevenlabs agents procedures compile \
    --agent-id "$AGENT_ID" --branch-id "$BRANCH_ID" \
    | jq -c '.workflow'
)
```

A successful compile returns `200` with `workflow`; validation failure returns `400` with `errors` and no workflow, and the CLI exits non-zero and prints that error payload. Do not publish while compile reports errors — repair and recompile — and fail if `WORKFLOW` is empty or null.

SDK methods raise on compile failure. Catch the error around `procedures.compile`; see [SDKs](#sdks) for the flow and [Error Handling](#error-handling) for the response fields.

Publish the drafts with the compiled workflow:

```bash
PUBLISH_BODY=$(
  jq -n \
    --argjson workflow "$WORKFLOW" \
    --arg description "Publish refund procedure" \
    '{workflow: $workflow, version_description: $description}'
)

elevenlabs agents update \
  --agent-id "$AGENT_ID" --branch-id "$BRANCH_ID" \
  --json "$PUBLISH_BODY"
```

Include `workflow` whenever publishing structured changes. Without it, the publish versions the procedure drafts but leaves the previously published workflow unchanged.

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

The removal remains a draft until published. If the procedure is structured, compile before publishing to remove its generated workflow nodes. Then confirm that the procedure is absent from the list and that a branch-HEAD lookup returns `404`.

## Error Handling

Common errors:
- **400** from compile, with `errors`: structured validation failed. Fix every returned procedure error, recompile, and only then publish.
- **400** from compile, with `no_draft_to_compile`: nothing is staged on this branch, so there is nothing to publish either.
- **401**: `ELEVENLABS_API_KEY` is unset or invalid.
- **403**: the key lacks `CONVAI_READ`/`CONVAI_WRITE`, the agent role is too low, or the branch is protected and only admins may publish to it.
- **404**: verify that the agent, branch, and procedure IDs belong together. Before a procedure's first publish, read the draft endpoint rather than branch HEAD.

The SDKs raise for these responses. The payload is on `error.body`, and the status is on `error.status_code` in Python or `error.statusCode` in JavaScript.

Do not blindly retry create, update, delete, or publish requests. Read current state before deciding whether a retry is safe.
