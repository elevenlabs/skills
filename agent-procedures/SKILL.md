---
name: agent-procedures
description: Manage ElevenLabs Agents Platform procedures through the public REST API. Use when creating, listing, reading, updating, discarding, compiling, publishing, versioning, or removing free-form or structured agent procedures.
license: MIT
compatibility: Requires internet access, curl, jq, and an ElevenLabs API key (ELEVENLABS_API_KEY).
metadata: {"openclaw": {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "primaryEnv": "ELEVENLABS_API_KEY"}}
---

# ElevenLabs Agent Procedures

Procedures are reusable instruction blocks that an agent starts when a trigger matches. Create, edit, compile, and publish them over the public REST API with `curl`. Reference: [Procedures](https://elevenlabs.io/docs/eleven-agents/customization/procedures.md) · [API Reference](https://elevenlabs.io/docs/api-reference/agents/procedures/).

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

## Key Facts

- Procedures belong to an agent branch. Drafts are per user: you only ever read and write your own.
- Create, update, discard, and remove act on your draft working set. Nothing reaches the live agent until you publish.
- Publishing is not a procedure endpoint. It is `PATCH /v1/convai/agents/{agent_id}?branch_id=...`, and it versions every changed procedure draft on the branch at once.
- Each branch pins every `procedure_id` to one published `version_id`, or to nothing while only a draft exists. That mapping is what `version_id` and `has_draft` report, and it is why a branch-HEAD read returns `404` until the procedure's first publish.
- Compile before every publish that changed procedures. See Compile and Publish.
- Structured content has no public dry-run endpoint. Save the draft first; compile is what validates it.
- Draft writes are last-write-wins. Read the draft immediately before editing and avoid concurrent writers.

Reads resolve against different sources:

| Request | Returns |
|---------|---------|
| `GET .../procedures/{procedure_id}` | Branch HEAD. `404` until the procedure's first publish. |
| `GET .../procedures/{procedure_id}/draft` | Your draft, falling back to branch HEAD when you have none. |
| `GET .../procedures/{procedure_id}?version_id=...` | One pinned, immutable historical version. |

## Writing Procedures

A procedure has a `name`, a `trigger`, and `content`. The `name` is a dashboard label and is never sent to the model, so it has no effect on behavior. The `trigger` and `content` are what the agent actually reads.

Pick the type before writing, because a procedure cannot be converted later:

- `free_form` — natural-language guidance the agent interprets and adapts. Use when wording and order can flex to the situation. Only this type can reference knowledge base documents.
- `deterministic` — an ordered list of typed steps that runs the same way every time. Use when the steps must not vary, such as identity verification or taking a payment.

Content is capped at 50,000 characters for both types.

### Triggers

The trigger is the only thing the agent sees when deciding whether to start a procedure, so it carries the routing decision on its own.

- Keep triggers concrete and non-overlapping. `When the user asks to cancel a subscription` routes better than `When the user has a question about their account`.
- Write from the user's perspective — what they ask for, not what the agent should do.
- Cover the phrasings users actually use: `When the user asks to refund, return, or get money back for an order` beats `When the user requests a refund`.

An empty `trigger` marks a sub-procedure that only runs when another procedure references it. Omit `trigger` entirely to derive one from the content instead.

### Free-Form Content

Write `content` as markdown — numbered steps for sequential actions, bullets for requirements within a step. To use a tool, knowledge base document, or another procedure, reference it inline:

```markdown
1. Ask the user for their order ID.
2. Look it up with [tool id="tool_abc123" name="Get order"].
3. Check the policy in [kb id="kb_def456" name="Refund policy"].
4. If the caller needs a human, run [procedure id="agtprc_xyz789" name="Escalate"].
5. When finished, use [system_tool id="end_call" name="End call"].
```

The `id` binds the reference; `name` is a readable label. An inline reference auto-attaches the resource. Naming a tool in plain prose only works if it is already attached to the agent, so prefer the markup.

### Structured Steps

Set `content` to a JSON string with a `trigger` and a non-empty `steps` array. Each step is an object discriminated by `type`:

| `type` | Fields | Behavior |
|--------|--------|----------|
| `ask` | `instruction` | Asks the user and waits for a usable answer before advancing. |
| `tell` | `instruction` | Agent composes one message conveying the instruction. |
| `say` | `message` | Agent speaks the message verbatim. |
| `tool_call` | `tool_id`, `tool_name`, optional `instruction` | Runs one tool. The agent does not speak during this step. |
| `system_tool` | `system_tool_name` | Only `end_call` is supported, and it must be the last step. |
| `branch` | `branches`, optional `fallback` | First-match-wins conditional. The dashboard calls this an If step. |

Each entry in `branches` is `{"condition": ..., "steps": [...]}` with at least one step. A condition is either natural language, `{"type": "llm", "condition": "the caller has no order ID"}`, or an expression over dynamic variables, `{"type": "expression", "expression": ...}`. Conditions within one `branch` must all be the same kind; the API rejects a mix.

- A `tool_call` only calls the tool. To speak about the result or branch on it, add a separate step after it. If the tool fails, the procedure stops there — add a `branch` when a failure needs handling.
- A procedure cannot open with a `branch`, two `branch` steps cannot sit back to back, and a `branch` cannot nest inside another one.

See [Writing Procedures](references/writing-procedures.md) for worked examples, a `jq` recipe for building the JSON, and guidance on writing content the agent follows reliably.

## List Procedures

List the effective working set:

```bash
curl -fsS \
  -H "$AUTH_HEADER" \
  "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures"
```

Each entry carries `procedure_id`, `version_id`, `name`, `type`, `trigger`, and `has_draft`. `has_draft` is true when the procedure has unpublished draft changes on this branch, in which case its `name`, `type`, and `trigger` reflect that draft. `version_id` is the version published on this branch, and is null exactly when `has_draft` is true — including for a procedure that was published earlier and has since been edited.

The list does not include procedure content. Read a body with `GET .../procedures/{procedure_id}` or its `/draft` variant.

## Free-Form Procedures

### Create

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

See Writing Procedures for what belongs in `trigger` and `content`.

### Read and Update the Draft

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

## Structured Procedures

Structured procedures use `type: "deterministic"` and carry their steps as a JSON string in `content`. The step schema and a `jq` recipe for building that string are in [Writing Procedures](references/writing-procedures.md). There is no public way to validate the JSON before it is saved; save the draft, then validate by compiling.

### Create or Update

Use the same create and draft-update endpoints as free-form procedures, with the steps JSON encoded as a string:

```json
{
  "name": "Structured refund",
  "type": "deterministic",
  "trigger": "When the user asks for a refund",
  "content": "{\"trigger\":\"When the user asks for a refund\",\"steps\":[{\"type\":\"ask\",\"instruction\":\"Ask for the order ID.\"},{\"type\":\"say\",\"message\":\"Your refund is on its way.\"}]}"
}
```

## Compile and Publish

Publishing versions every changed procedure draft on the branch in a single call. Compile first.

Compiling turns the branch's current procedure set into the workflow the agent runs. Compile before every publish that changed procedures — including a publish that only touched free-form ones, and including the publish that removes your last structured procedure. Compiling is safe when the branch has no structured procedures and leaves a workflow you authored yourself intact, so there is no case where skipping it is the safer choice.

Compile needs a pending draft on the branch. With nothing staged it fails with `no_draft_to_compile`, which also means there is nothing to publish.

```bash
COMPILE_RESPONSE=$(
  curl -sS -X POST \
    -H "$AUTH_HEADER" \
    "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures/compile"
)
COMPILE_ERRORS=$(printf '%s' "$COMPILE_RESPONSE" | jq -c '.errors // empty')
WORKFLOW=$(printf '%s' "$COMPILE_RESPONSE" | jq -c '.workflow')
```

A successful compile returns `200` with `workflow`. Validation failure returns `400` with `errors` keyed by procedure ID and no workflow. If `COMPILE_ERRORS` is non-empty, report the errors and stop. Otherwise fail if `workflow` is null.

Publish the compiled workflow and the procedure drafts together:

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

Send `workflow` on every publish that changed procedures. Omit it and the compile result is thrown away — the new version keeps the previously published workflow, which is the stale one the recompile was meant to replace.

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

The removal is staged, not live. Publish it with the flow under Compile and Publish, then confirm the procedure is absent from the list and that a branch-HEAD lookup of it returns `404`.

## Error Handling

Common errors:
- **400** from compile, with `errors`: structured validation failed. Fix every returned procedure error, recompile, and only then publish.
- **400** from compile, with `no_draft_to_compile`: nothing is staged on this branch, so there is nothing to publish either.
- **401**: `ELEVENLABS_API_KEY` is unset or invalid.
- **403**: the key lacks `CONVAI_READ`/`CONVAI_WRITE`, the agent role is too low, or the branch is protected and only admins may publish to it.
- **404**: verify that the agent, branch, and procedure IDs belong together. Before a procedure's first publish, read the draft endpoint rather than branch HEAD.

Do not blindly retry create, update, delete, or publish requests. Read current state before deciding whether a retry is safe.

## References

- [Writing Procedures](references/writing-procedures.md)
