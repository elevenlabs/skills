# Writing Procedures

Read the docs before authoring procedure content. They are the source of truth for how procedures behave:

- [Procedures](https://elevenlabs.io/docs/eleven-agents/customization/procedures.md) — what a procedure is, and when to use one instead of a workflow or the system prompt.
- [Free-form procedures](https://elevenlabs.io/docs/eleven-agents/customization/procedures/free-form-procedures.md) — anatomy, inline references, and how to write triggers and content.
- [Structured procedures](https://elevenlabs.io/docs/eleven-agents/customization/procedures/structured-procedures.md) — step types, branching, and the rules on branches.

Procedures are in Alpha and the content schema is still changing. On conflict, take online documentation as source of truth.

## Key Takeaways

- A procedure is a `name`, a `trigger`, and `content`. The `trigger` and `content` are what the agent reads.
- Pick the type before writing, because a procedure cannot be converted later. `free_form` is natural-language guidance the agent interprets and adapts, and is the only type that can reference knowledge base documents. `deterministic` is an ordered list of typed steps that runs the same way every time — identity verification, taking a payment.
- The trigger carries the routing decision on its own. Keep triggers concrete and non-overlapping, write them from the user's perspective rather than as agent actions, and cover the phrasings users actually use: `When the user asks to refund, return, or get money back for an order` routes better than `When the user requests a refund`.
- An empty `trigger` marks a sub-procedure that runs only when another procedure references it. Omit `trigger` entirely to derive one from the content.
- Content is capped at 50,000 characters for both types.
- Keep one procedure to one task, put tone and refusal policy in the system prompt, and extract steps shared across procedures into a procedure of their own.

## Free-Form Content

Write `content` as markdown: numbered steps for sequential actions, bullets for requirements within a step. Use the imperative, and say why a step matters where the reason generalizes to cases the steps do not enumerate.

Reference a tool, knowledge base document, or another procedure inline. The `id` binds the reference and `name` is a readable label. An inline reference auto-attaches the resource; naming a tool in prose works only if it is already attached to the agent, so prefer the markup.

```markdown
1. Ask the user for their order ID.
2. Look it up with [tool id="tool_abc123" name="Get order"], because the refund window runs from the order date.
3. If the order is inside the 30-day window, check [kb id="kb_def456" name="Refund policy"] for the timeline on the payment method used and tell the user what to expect.
4. If it falls outside the window, explain why it is not eligible and offer store credit instead.
5. If the caller asks for a human at any point, run [procedure id="agtprc_xyz789" name="Escalate"].
6. Once the caller has no further questions, use [system_tool id="end_call" name="End call"].
```

A reference in the `trigger` fires the procedure on a resource's output, for example `When get_user returns tier 'gold'`.

## Structured Content

Set `content` to a JSON string holding a `trigger` and a non-empty `steps` array. Each step is an object discriminated by `type`. Every type enforces its own behavior, so the instruction text rarely needs to restate it.

| `type` | Dashboard | Fields | What it does |
|--------|-----------|--------|--------------|
| `ask` | Ask | `instruction` | Asks the user and waits for an answer. |
| `tell` | Tell | `instruction` | Agent composes one message conveying the instruction. |
| `say` | Say | `message` | Agent speaks the message verbatim. |
| `tool_call` | Tool | `tool_id`, `tool_name`, optional `instruction` | Runs one tool. |
| `branch` | If | `branches`, optional `fallback` | First-match-wins conditional. |
| `system_tool` | — | `system_tool_name` | Runs a system tool, such as `end_call`. |

Each entry in `branches` pairs a `condition` with its own `steps`. A condition is either natural language, `{"type": "llm", "condition": "the caller has no order ID"}`, or an expression over dynamic variables, `{"type": "expression", "expression": ...}`.

Which steps may follow which, and how they may be combined, is documented on the structured procedures page and enforced when you compile. Read that page rather than guessing. When you are writing against a live agent, save the draft and let compile find what the schema rejects — `SKILL.md` has that loop.

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

`content` carries the JSON as a string, so serialize an object rather than hand-escaping quotes.

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
