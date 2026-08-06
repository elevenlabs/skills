# Writing Procedures

Check the current documentation before authoring procedure content. Procedures are in Alpha, and the content schema may change:

- [Procedures](https://elevenlabs.io/docs/eleven-agents/customization/procedures.md) — what a procedure is, and when to use one instead of a workflow or the system prompt.
- [Free-form procedures](https://elevenlabs.io/docs/eleven-agents/customization/procedures/free-form-procedures.md) — anatomy, inline references, and how to write triggers and content.
- [Structured procedures](https://elevenlabs.io/docs/eleven-agents/customization/procedures/structured-procedures.md) — step types, branching, and the rules on branches.

## Authoring Rules

- A procedure has a `name`, a `trigger`, and `content`. The agent uses the trigger for routing and reads the content when the procedure starts.
- Use `free_form` for natural-language guidance that the agent can adapt. Only free-form procedures can reference knowledge base documents.
- Use `deterministic` for ordered, typed steps that must run consistently, such as identity verification or payment collection.
- Preserve the procedure type during routine updates unless the user explicitly requests a conversion.
- Write concrete, non-overlapping triggers from the user's perspective. Cover likely phrasing: `When the user asks to refund, return, or get money back for an order` routes better than `When the user requests a refund`.
- An empty `trigger` marks a sub-procedure that runs only when another procedure references it. Omit `trigger` entirely to derive one from the content.
- Content is capped at 50,000 characters for both types.
- Keep each procedure focused on one task. Put tone and refusal policy in the system prompt.
- Extract steps shared across procedures into a separate procedure.

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

Set `content` to a serialized JSON object containing a `trigger` and a non-empty `steps` array. Each step is an object discriminated by `type`. The step type defines its behavior, so its instruction rarely needs to restate that behavior.

Each entry in `branches` pairs a `condition` with its own `steps`. A condition is either an LLM condition such as `{"type": "llm", "condition": "the caller has no order ID"}` or an expression over dynamic variables such as `{"type": "expression", "expression": ...}`.

Use the structured procedures documentation for current step types, fields, and valid combinations. To validate against a live agent, save the draft and compile it. Fix every reported error before publishing; [Using the Procedure API](using-procedure-api.md) describes the loop.

```json
{
  "trigger": "When the user asks to refund, return, or get money back for an order",
  "steps": [
    { "type": "ask", "instruction": "Ask for the order ID." },
    { "type": "tool_call", "tool_id": "tool_abc123", "tool_name": "Get order" },
    {
      "type": "branch",
      "branches": [
        {
          "condition": { "type": "llm", "condition": "the order is outside the refund window" },
          "steps": [{ "type": "tell", "instruction": "Explain the order is no longer eligible." }]
        }
      ],
      "fallback": [{ "type": "say", "message": "Your refund is on its way." }]
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
        "trigger": "When the user asks for a refund",
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
  trigger: "When the user asks for a refund",
  steps: [
    { type: "ask", instruction: "Ask for the order ID." },
    { type: "say", message: "Your refund is on its way." },
  ],
});
```

### cURL

```bash
CONTENT=$(jq -n '{
  trigger: "When the user asks for a refund",
  steps: [
    { type: "ask", instruction: "Ask for the order ID." },
    { type: "say", message: "Your refund is on its way." }
  ]
}')
```
