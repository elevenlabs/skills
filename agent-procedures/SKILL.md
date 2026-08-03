---
name: agent-procedures
description: Manage ElevenLabs Agents Platform procedures through the Python and JavaScript SDKs or the public REST API. Use when creating, listing, reading, updating, discarding, compiling, publishing, versioning, or removing free-form or structured agent procedures.
license: MIT
compatibility: Requires internet access, an ElevenLabs API key (ELEVENLABS_API_KEY), and either an ElevenLabs SDK (2.60.0 or newer) or curl and jq.
metadata: {"openclaw": {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "primaryEnv": "ELEVENLABS_API_KEY"}}
---

# ElevenLabs Agent Procedures

Procedures are reusable instruction blocks that an agent starts when a trigger matches. Create, edit, compile, and publish them with the Python or JavaScript SDK, or over the public REST API with `curl`. Reference: [Procedures](https://elevenlabs.io/docs/eleven-agents/customization/procedures.md) · [API Reference](https://elevenlabs.io/docs/api-reference/agents/procedures/).

Procedures are in Alpha. The feature set and the content schema are still changing, and some changes may break. Check the reference pages above before relying on a detail here.

## Prerequisites

- `ELEVENLABS_API_KEY` is set, with the `CONVAI_READ` and `CONVAI_WRITE` scopes.
- Reading requires the viewer role on the target agent. Creating, updating, removing, compiling, and publishing require the editor role. Publishing to a protected branch requires admin.
- The target `agent_id` is known.
- The target `branch_id` is known. If not, read `main_branch_id` from `GET /v1/convai/agents/{agent_id}`, or list branches with `GET /v1/convai/agents/{agent_id}/branches`.

```bash
API_BASE="https://api.elevenlabs.io/v1/convai"
AUTH_HEADER="xi-api-key: $ELEVENLABS_API_KEY"
```

Never print or persist the API key.

## SDKs

Procedures reached both SDKs in `2.60.0`. Earlier versions have no `procedures` client at all, so install at or above that version:

```bash
pip install "elevenlabs>=2.60.0"
npm install @elevenlabs/elevenlabs-js@^2.60.0
```

For JavaScript, use `@elevenlabs/elevenlabs-js`. The unscoped `elevenlabs` npm package is the deprecated v1.x and has no procedures client at any version.

Both clients read `ELEVENLABS_API_KEY` from the environment; never pass a literal key.

Every procedure endpoint has a method. Python nests them under `client.conversational_ai.agents`, JavaScript under `client.conversationalAi.agents`:

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

How arguments are passed differs by language, and in Python by method:

- JavaScript takes the IDs positionally, then a body object. Python takes keyword arguments — except `procedures.create`, which takes its body as `request=CreateProcedureRequestModel(...)`. Flat keywords on `create` raise `TypeError`.
- `procedures.drafts.update` omits `trigger` from the request when you leave it out, and the PATCH is a full replacement. Send `name`, `type`, `trigger`, and `content` on every call.
- Read one historical version with `procedures.get(..., version_id=...)` or `procedures.get(agentId, branchId, procedureId, { versionId })`.
- Publish with `agents.update`, passing the compile response's `workflow` straight through.

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

When the publish changed structured procedures, compile first and pass the result:

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

When the publish changed structured procedures, compile first and pass the result:

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

## Key Facts

- Procedures belong to an agent branch. Drafts are per user: you only ever read and write your own.
- Create, update, discard, and remove act on your draft working set. Nothing reaches the live agent until you publish.
- Publishing is not a procedure endpoint. It is `PATCH /v1/convai/agents/{agent_id}?branch_id=...`, and it versions every changed procedure draft on the branch at once.
- Each branch pins every `procedure_id` to one published `version_id`, or to nothing while only a draft exists. That mapping is what `version_id` and `has_draft` report, and it is why a branch-HEAD read returns `404` until the procedure's first publish.
- Compile before a publish that changed structured procedures. Free-form-only changes publish without it. See Compile and Publish.
- Structured content has no dry-run. Save the draft, compile to validate it, and repair what compile reports. See Compile and Publish.
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
curl -fsS \
  -H "$AUTH_HEADER" \
  "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures"
```

Each entry carries `procedure_id`, `version_id`, `name`, `type`, `trigger`, and `has_draft`. `has_draft` is true when the procedure has unpublished draft changes on this branch, in which case its `name`, `type`, and `trigger` reflect that draft. `version_id` is the version published on this branch, and is null exactly when `has_draft` is true — including for a procedure that was published earlier and has since been edited.

The list does not include procedure content. Read a body with `GET .../procedures/{procedure_id}` or its `/draft` variant.

## Create

```bash
CREATE_RESPONSE=$(
  curl -fsS -X POST \
    -H "$AUTH_HEADER" \
    -H "Content-Type: application/json" \
    "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures" \
    -d '{
      "name": "Refund requests",
      "type": "free_form",
      "trigger": "When the user asks for a refund",
      "content": "Confirm the order number, check eligibility, and explain the next step."
    }'
)
PROCEDURE_ID=$(printf '%s' "$CREATE_RESPONSE" | jq -r '.procedure_id')
```

Fail if `procedure_id` is empty or null.

A structured procedure uses the same endpoint with `type` set to `deterministic` and its steps JSON-encoded into `content`. See [Writing Procedures](references/writing-procedures.md) for what belongs in `trigger` and `content`, and for building that JSON string.

## Read and Update the Draft

```bash
curl -fsS \
  -H "$AUTH_HEADER" \
  "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures/$PROCEDURE_ID/draft"

curl -fsS -X PATCH \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures/$PROCEDURE_ID/draft" \
  -d '{
    "name": "Refund requests",
    "type": "free_form",
    "trigger": "When the user asks for a refund",
    "content": "Confirm the order number. Check refund eligibility. Explain the refund timeline."
  }'
```

The draft update body is a full replacement. Send `name`, `type`, `trigger`, and `content` on every call, not just the changed field. Keep `type` the same — a procedure cannot be converted between types.

Publish with the flow under Compile and Publish.

## Compile and Publish

Publishing versions every changed procedure draft on the branch in a single call:

```bash
curl -fsS -X PATCH \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  "$API_BASE/agents/$AGENT_ID?branch_id=$BRANCH_ID" \
  -d '{"version_description": "Publish refund procedure"}'
```

Compiling is the structured-procedure step, and only structured procedures need it. It turns the branch's structured drafts into workflow nodes and merges them into the agent's workflow, leaving a workflow you authored yourself in place. Free-form procedures are never compiled; the agent loads them from the published version at the start of a conversation, so a branch that only saw free-form edits publishes with the call above and no `workflow` in the body.

Compile when the branch's structured procedures changed, including the publish that removes your last structured procedure — compiling is what strips the nodes an earlier compile generated for it.

Compile needs a pending draft on the branch. With nothing staged it fails with `no_draft_to_compile`, which also means there is nothing to publish.

Compiling is also the only way to validate structured content, and it validates what is saved rather than what you hand it, so author against saved drafts:

1. Save the content as a draft. A draft that does not validate still saves.
2. Compile. On `400`, `errors` is keyed by procedure ID, and each entry carries the `path` of the offending field and a message naming the step, such as `steps[0].ask.instruction` and `Step 1: Ask step requires an instruction`.
3. Repair every entry and compile again. One compile reports all the failures it reached, but clearing field-level errors can expose structural ones behind them, which report against the procedure rather than a field. Iterate until compile returns a workflow.
4. Publish, sending that `workflow` with the publish.

```bash
COMPILE_RESPONSE=$(
  curl -sS -X POST \
    -H "$AUTH_HEADER" \
    "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures/compile"
)
COMPILE_ERRORS=$(printf '%s' "$COMPILE_RESPONSE" | jq -c '.errors // empty')
WORKFLOW=$(printf '%s' "$COMPILE_RESPONSE" | jq -c '.workflow')
```

A successful compile returns `200` with `workflow`; validation failure returns `400` with `errors` and no workflow. Do not publish while `COMPILE_ERRORS` is non-empty — repair and recompile — and fail if `workflow` is null.

Through an SDK the same failure raises rather than handing back a body to inspect, so the check becomes a `try`/`except` around `procedures.compile`. See SDKs for that flow and Error Handling for what the exception carries.

Publish the compiled workflow and the structured drafts together:

```bash
PUBLISH_BODY=$(
  jq -n \
    --argjson workflow "$WORKFLOW" \
    --arg description "Publish refund procedure" \
    '{workflow: $workflow, version_description: $description}'
)

curl -fsS -X PATCH \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  "$API_BASE/agents/$AGENT_ID?branch_id=$BRANCH_ID" \
  -d "$PUBLISH_BODY"
```

Send `workflow` on every publish that changed structured procedures. Omit it and the compile result is thrown away — the new version keeps the previously published workflow, which is the stale one the recompile was meant to replace.

Verify a published procedure and record its `version_id`:

```bash
curl -fsS \
  -H "$AUTH_HEADER" \
  "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures/$PROCEDURE_ID"
```

## Discard Edits

Discard only your own unpublished draft:

```bash
curl -fsS -X DELETE \
  -H "$AUTH_HEADER" \
  "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures/$PROCEDURE_ID/draft"
```

This restores the branch-HEAD version. For a procedure that was never published, it deletes the procedure. Read the draft afterwards to confirm what remains.

## Remove a Procedure

Stage the removal:

```bash
curl -fsS -X DELETE \
  -H "$AUTH_HEADER" \
  "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures/$PROCEDURE_ID"
```

This removes the procedure from the branch working set. It does not erase versions still referenced by agent history.

The removal is staged, not live. Publish it as described under Compile and Publish — removing a structured procedure needs a compile, since that is what strips the nodes it generated — then confirm the procedure is absent from the list and that a branch-HEAD lookup of it returns `404`.

## Error Handling

Common errors:
- **400** from compile, with `errors`: structured validation failed. Fix every returned procedure error, recompile, and only then publish.
- **400** from compile, with `no_draft_to_compile`: nothing is staged on this branch, so there is nothing to publish either.
- **401**: `ELEVENLABS_API_KEY` is unset or invalid.
- **403**: the key lacks `CONVAI_READ`/`CONVAI_WRITE`, the agent role is too low, or the branch is protected and only admins may publish to it.
- **404**: verify that the agent, branch, and procedure IDs belong together. Before a procedure's first publish, read the draft endpoint rather than branch HEAD.

The SDKs raise on every one of these instead of returning a body to inspect. The payload is on `error.body`, and the status on `error.status_code` in Python or `error.statusCode` in JavaScript.

Do not blindly retry create, update, delete, or publish requests. Read current state before deciding whether a retry is safe.

## References

- [Writing Procedures](references/writing-procedures.md)
