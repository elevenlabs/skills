# Writing Procedures

Check the current documentation before authoring procedure content:

- [Procedures](https://elevenlabs.io/docs/eleven-agents/customization/procedures.md) — what a procedure is, and when to use one instead of a workflow or the system prompt.
- [Free-form procedures](https://elevenlabs.io/docs/eleven-agents/customization/procedures/free-form-procedures.md) — anatomy, inline references, and how to write triggers and content.
- [Structured procedures](https://elevenlabs.io/docs/eleven-agents/customization/procedures/structured-procedures.md) — step types, branching, and the rules on branches.

## Authoring Rules

- A procedure has a `name`, a `trigger`, and `content`. The agent uses the trigger for routing and reads the content when the procedure starts.
- Use `free_form` for natural-language guidance that the agent can adapt. Only free-form procedures can reference knowledge base documents.
- Use `deterministic` ("structured" in the dashboard) for typed steps that run in a fixed order, such as identity verification, escalation, or payment collection.
- A procedure's `type` cannot change after creation. Always resend the existing `type` on a draft update. To convert between free-form and structured, create a new procedure and re-point any references to it.
- Write concrete, non-overlapping triggers from the user's perspective. Cover likely phrasing: `When the user asks to refund, return, or get money back for an order` routes better than `When the user requests a refund`.
- An empty `trigger` marks a sub-procedure that runs only when another procedure references it. Set `trigger` as its own field; do not embed a trigger inside `content`.
- Content is capped at 50,000 characters for both types.
- Keep each procedure focused on one task. Put tone and refusal policy in the system prompt.
- Extract steps shared across procedures into a separate procedure and reference it, rather than copying the steps. Copies drift.

## Free-Form Content

Write `content` as markdown. Use numbered steps for sequences and bullets for requirements within a step. Use the imperative. Explain a step's rationale only when it helps the agent handle cases the procedure does not enumerate.

Reference a tool, knowledge base document, or another procedure inline. The `id` binds the resource; `name` provides a readable label.

An inline reference attaches the resource automatically. Naming a tool in prose works only when it is already attached to the agent, so prefer the markup.

```markdown
1. Ask the user for their order ID.
2. Look it up with [tool id="tool_abc123" name="Get order"], because the refund window runs from the order date.
3. If the order is inside the 30-day window, check [kb id="kb_def456" name="Refund policy"] for the timeline on the payment method used and tell the user what to expect.
4. If it falls outside the window, explain why it is not eligible and offer store credit instead.
5. If the caller asks for a human at any point, run [procedure id="agtprc_xyz789" name="Escalate"].
6. Once the caller has no further questions, use [system_tool id="end_call" name="End call"].
```

A trigger can reference a resource's output, for example `When get_user returns tier 'gold'`.

## Structured Content

Set `content` to a serialized JSON object containing a non-empty `steps` array. The trigger goes in the procedure's top-level `trigger` field, not inside `content`. Each step is an object discriminated by `type`. The step type defines its behavior, so its instruction rarely needs to restate that behavior. The names in parentheses are the labels shown in the dashboard editor.

| `type` | Editor name | Fields | Behavior |
|--------|-------------|--------|----------|
| `ask` | Ask | `instruction` | Asks the user something and waits. Keeps asking until the user answers. The only step that pauses for the user. |
| `tell` | Tell | `instruction` | Conveys something in the agent's own words, then moves on immediately. |
| `say` | Say | `message`, optional `message_translations` (`{ "<lang>": { "value": "..." } }`) | Says an exact message verbatim, then moves on immediately. |
| `tool_call` | Tool | `tool_id`, `tool_name`, optional `instruction`, optional `schema_overrides`, optional `on_failure` | Calls the tool. Always calls it; a condition in the instruction cannot skip it. |
| `branch` | If | `branches` (arms), optional `fallback` (Else) | Evaluates arms in order; first match wins. `fallback` runs when nothing matches. With no `fallback` and no match, control falls through to the next step. |
| `sub_procedure` | Sub-procedure | `procedure_id` | Runs another structured procedure, then returns to the next step here. |
| `system_tool` | System tool | `system_tool_name` | Calls a built-in tool. Only `end_call` is supported; it ends the conversation. |
| `retry` | Retry | `max_retries` (1–3) | Only inside `on_failure`. Re-runs the whole failure handler, tool call included, until the tool succeeds or attempts run out. |

- An arm in `branches` is `{ "condition": <condition>, "steps": [...] }`. A condition is `{ "type": "llm", "condition": "<natural language>" }` (a text condition the model evaluates) or `{ "type": "expression", "expression": <AST> }` (an expression over dynamic variables). Expression conditions cannot read the user's reply; they test variables filled by tool results or set at conversation start.
- `schema_overrides` fixes a tool parameter so the model does not choose it. Keys are parameter paths; each value is `{ "source": "constant", "constant_value": ... }`, `{ "source": "dynamic_variable", "dynamic_variable": "..." }`, `{ "source": "llm", "prompt": "<optional prompt override>" }`, or `{ "source": "omit" }`.
- `on_failure` is `{ "branches": [], "fallback": [...] }`. Today the dashboard exposes only `fallback`, a single block of steps that runs when the tool fails; keep `branches` empty. The handler's steps run and the procedure continues to the next step. A tool step with no `on_failure` ends the conversation on failure.
- Where each step is allowed: inside an If arm, any step except `branch` and `retry`. Inside `on_failure`, any step except `branch` and `tool_call`.

### Validation rules

Saving an agent draft or publishing rejects a structured procedure that breaks any of these, with the offending step's `path`:

- Two `branch` steps cannot be adjacent at the top level.
- A `branch` that uses expression conditions cannot directly follow an `ask`.
- All conditions in one `branch` must be the same kind: all `llm` or all `expression`.
- `retry` may only appear in `on_failure`, and must be the last step there.
- `end_call` must be the last step in whichever list it appears in.
- `on_failure.fallback` must have at least one step.
- A `sub_procedure` must point at an existing structured procedure on the same agent, and not at itself.
- `tool_id` must be a tool on the agent, `tool_name` must match, and `schema_overrides` must match the tool's schema.
- `steps`, `instruction`, and `message` cannot be empty.

### Runtime rules that shape the design

- Only `ask` waits for the user. Every other step runs immediately and control moves to the next step within the same turn. There is no step that stops the turn other than `ask`; use `end_call` to end the conversation.
- Reaching the end of a procedure does not end the turn. The agent returns to its normal behavior with the turn still open and may say more.
- `ask`, `tell`, and `say` steps have no tools. Do not write "do not call tools" into them.
- Decisions made inside a `branch` arm are not remembered by later steps. Persist anything needed downstream with a tool call or a dynamic variable.

### Authoring guidance

- One question per `ask`. Bundled questions get skipped or merged.
- `tell` is for statements. A `tell` phrased as a question never waits for an answer.
- Do not insert an unrelated `tell` or `say` between two `branch` steps to satisfy the adjacency rule; fold the second decision into more arms of the first `branch`, or move it into a `sub_procedure`.
- Nested branching is not allowed. Put the nested steps in a `sub_procedure`.
- Place a `branch` with expression conditions right after the `tool_call` that fills the variables it tests.
- If a tool call is not always meant to happen, put the condition in a `branch` before the `tool_call`.
- When a parameter must always take a specific value, use a `constant` override rather than saying so in the instruction.
- Give every `tool_call` an `on_failure`; without one, any failure ends the conversation.
- Do not describe the next step inside a step, and do not try to end the turn with prose such as "this is the last message of this turn". The runtime does not enforce either.

Validation happens when you publish, or when you save an agent draft to check without publishing; [Using the Procedure API](using-procedure-api.md#validate-without-publishing) describes the loop.

```json
{
  "steps": [
    { "type": "ask", "instruction": "Ask for the order ID." },
    {
      "type": "tool_call",
      "tool_id": "tool_abc123",
      "tool_name": "Get order",
      "schema_overrides": { "include_history": { "source": "constant", "constant_value": false } },
      "on_failure": {
        "branches": [],
        "fallback": [
          { "type": "tell", "instruction": "Apologize that the order lookup failed and say you will try once more." },
          { "type": "retry", "max_retries": 1 }
        ]
      }
    },
    {
      "type": "branch",
      "branches": [
        {
          "condition": { "type": "llm", "condition": "the order is outside the refund window" },
          "steps": [
            { "type": "tell", "instruction": "Explain the order is no longer eligible." },
            { "type": "sub_procedure", "procedure_id": "agtprc_escalate123" }
          ]
        }
      ],
      "fallback": [
        {
          "type": "say",
          "message": "Your refund is on its way.",
          "message_translations": { "es": { "value": "Su reembolso está en camino." } }
        }
      ]
    },
    { "type": "system_tool", "system_tool_name": "end_call" }
  ]
}
```

## Building the Content String

Serialize the object before assigning it to `content`; do not hand-escape quotes.

### Python

```python
import json

content = json.dumps(
    {
        "steps": [
            {"type": "ask", "instruction": "Ask for the order ID."},
            {"type": "say", "message": "Your refund is on its way."},
        ],
    }
)
```

### JavaScript

```javascript
const content = JSON.stringify({
  steps: [
    { type: "ask", instruction: "Ask for the order ID." },
    { type: "say", message: "Your refund is on its way." },
  ],
});
```

### CLI

```bash
# Build the JSON string to pass to `elevenlabs agents procedures create --json`
CONTENT=$(jq -n '{
  steps: [
    { type: "ask", instruction: "Ask for the order ID." },
    { type: "say", message: "Your refund is on its way." }
  ]
}')
```
