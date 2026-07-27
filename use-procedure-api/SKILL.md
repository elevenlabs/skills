---
name: use-procedure-api
description: Manage ElevenLabs Agents Platform procedures through the public REST API. Use when creating, listing, reading, updating, discarding, compiling, publishing, versioning, or removing free-form or structured agent procedures.
license: MIT
compatibility: Requires internet access, curl, jq, and an ElevenLabs API key (ELEVENLABS_API_KEY).
metadata: {"openclaw": {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "primaryEnv": "ELEVENLABS_API_KEY"}}
---

# Use the Procedure API

Procedures are reusable instruction blocks that an agent starts when a trigger matches. Manage them with the public REST API using `curl`.

## Prerequisites

- `ELEVENLABS_API_KEY` is set. The key needs `CONVAI_READ` and `CONVAI_WRITE`, plus the viewer or editor role on the target agent.
- The target `agent_id` is known.
- The target `branch_id` is known. If not, read `main_branch_id` from `GET /v1/convai/agents/{agent_id}`, or list branches with `GET /v1/convai/agents/{agent_id}/branches`.

```bash
API_BASE="https://api.elevenlabs.io/v1/convai"
AUTH_HEADER="xi-api-key: $ELEVENLABS_API_KEY"
```

Never print or persist the API key.

## Lifecycle rules

- Procedures belong to an agent branch.
- Create, update, discard, and remove operate on the caller's draft working set.
- Draft mutations do not affect the live agent until the branch is published through the agent update endpoint.
- `GET .../procedures/{procedure_id}` reads branch HEAD. It returns `404` for a newly created procedure until that draft is published.
- `GET .../procedures/{procedure_id}/draft` reads the caller's draft, falling back to branch HEAD.
- `GET .../procedures/{procedure_id}?version_id=...` reads an immutable historical version.
- `DELETE .../procedures/{procedure_id}` stages removal from the branch. It does not erase versions still referenced by agent history.
- `DELETE .../procedures/{procedure_id}/draft` discards the caller's edits. For a never-published procedure with no other references, this deletes the procedure.
- Draft updates are last-write-wins. Read the effective draft immediately before editing and avoid concurrent writers.

## List procedures

List the effective working set:

```bash
curl -fsS \
  -H "$AUTH_HEADER" \
  "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures"
```

Each entry carries `procedure_id`, `version_id`, `name`, `type`, `trigger`, and `has_draft`. `has_draft` is true when the procedure has unpublished draft changes on this branch, in which case its `name`, `type`, and `trigger` reflect that draft. `version_id` is the version published on this branch, and is null exactly when `has_draft` is true — including for a procedure that was published earlier and has since been edited.

The list does not include procedure content. Read a body with `GET .../procedures/{procedure_id}` or its `/draft` variant.

## Free-form procedures

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

An empty `trigger` marks a sub-procedure that only starts when another procedure references it. Omit `trigger` entirely to derive it from the content.

### Read and update the draft

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

The draft update body is a full replacement. Send `name`, `type`, `trigger`, and `content` on every call, not just the changed field.

### Publish

Free-form procedures need no compilation:

```bash
curl -fsS -X PATCH \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  "$API_BASE/agents/$AGENT_ID?branch_id=$BRANCH_ID" \
  -d '{"version_description":"Publish refund procedure"}'
```

Verify the published procedure and record its `version_id`:

```bash
curl -fsS \
  -H "$AUTH_HEADER" \
  "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures/$PROCEDURE_ID"
```

## Structured procedures

Structured procedures use `type: "deterministic"` and JSON-encoded `content`.

### Validate before writing

```bash
curl -fsS -X POST \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures/validate-structured-procedure" \
  -d '{
    "content": "{\"trigger\":\"When the user asks for a refund\",\"steps\":[{\"type\":\"say\",\"message\":\"I can help with your refund.\"}]}"
  }'
```

Continue only when `errors` is empty. Each entry carries a `path` into the content and a human-readable `message`.

### Create or update

Use the same create and draft-update endpoints as free-form procedures, with:

```json
{
  "name": "Structured refund",
  "type": "deterministic",
  "trigger": "When the user asks for a refund",
  "content": "{\"trigger\":\"When the user asks for a refund\",\"steps\":[{\"type\":\"say\",\"message\":\"I can help with your refund.\"}]}"
}
```

### Compile and publish

Compilation validates every structured procedure in the branch working set, including tool and MCP references. It returns a workflow but does not publish it.

```bash
COMPILE_RESPONSE=$(
  curl -sS -X POST \
    -H "$AUTH_HEADER" \
    "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures/compile"
)
COMPILE_ERRORS=$(printf '%s' "$COMPILE_RESPONSE" | jq -c '.errors // empty')
WORKFLOW=$(printf '%s' "$COMPILE_RESPONSE" | jq -c '.workflow')
```

If `COMPILE_ERRORS` is non-empty, report the errors keyed by procedure ID and do not publish. Otherwise, fail if `workflow` is null.

Publish the compiled workflow and procedure drafts together:

```bash
PUBLISH_BODY=$(
  jq -n \
    --argjson workflow "$WORKFLOW" \
    --arg description "Publish structured procedures" \
    '{workflow: $workflow, version_description: $description}'
)

curl -fsS -X PATCH \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  "$API_BASE/agents/$AGENT_ID?branch_id=$BRANCH_ID" \
  -d "$PUBLISH_BODY"
```

Always recompile after adding, changing, or removing a structured procedure. Publishing a stale workflow can leave generated workflow nodes inconsistent with the procedure set.

## Discard edits

Discard only the caller's unpublished draft:

```bash
curl -fsS -X DELETE \
  -H "$AUTH_HEADER" \
  "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures/$PROCEDURE_ID/draft"
```

Then read the effective draft to confirm it reverted to branch HEAD.

## Remove a procedure

Stage removal:

```bash
curl -fsS -X DELETE \
  -H "$AUTH_HEADER" \
  "$API_BASE/agents/$AGENT_ID/branches/$BRANCH_ID/procedures/$PROCEDURE_ID"
```

For a structured procedure, compile the remaining working set first. Publish the branch through the agent update endpoint, then verify the procedure is absent from the list and that a branch-HEAD lookup of it returns `404`.

## Error handling

- `400` from compile: fix all returned procedure errors before publishing.
- `401`: check that `ELEVENLABS_API_KEY` is set and valid.
- `403`: the key lacks `CONVAI_READ`/`CONVAI_WRITE` or the required agent viewer/editor role.
- `404`: verify that agent, branch, and procedure IDs belong together. Before first publish, use the draft endpoint instead of branch-HEAD lookup.
- Do not blindly retry create, update, delete, or publish requests. Read current state before deciding whether a retry is safe.

## Completion report

Report:

- Agent and branch IDs
- Procedure ID and type
- Whether changes remain draft or were published
- Published procedure `version_id`, when applicable
- Validation or compile errors that prevented publication
