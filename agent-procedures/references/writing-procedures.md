# Writing Procedures

Craft guidance for procedure content. `SKILL.md` carries the schema — step types, the inline reference markup, and the structural rules. This file covers writing content the agent follows reliably.

Procedures are in Alpha and the content schema is still changing. Check [Procedures](https://elevenlabs.io/docs/eleven-agents/customization/procedures.md) before relying on a detail here.

## Writing Free-Form Content

- Use the imperative: `Look up the customer's last order`, not `You should look up the order`.
- Say why a step matters. A short `because we need the order ID to issue a refund` generalizes to edge cases the steps do not enumerate. Prefer that over all-caps MUSTs and rigid scripts.
- Keep one procedure to one task. If it branches into unrelated outcomes, split it and let the agent route between them.
- Put tone, identity, and refusal policy in the system prompt, not in procedures.
- Extract steps repeated across procedures — identity checks, order lookups, escalation — into their own procedure and reference it from each one.

A reference in the `trigger` lets the procedure fire on a resource's output, for example `When get_user returns tier 'gold'`.

## Writing Structured Steps

Each step type already enforces its own behavior, so you rarely need to restate it in the instruction text. An `ask` step will not advance until it has a usable answer, and `tell` and `say` each deliver exactly one message — no need to tell a step to send a single message.

Write branch conditions as a plain description of the case rather than as true/false: `NOT a billing question` reads better than `false if it is a billing question`. When the decision depends on a value you already know, use a dynamic variable in an expression condition instead of asking the agent to work it out.

A worked example combining an `ask`, a `tool_call`, and a `branch`:

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
    }
  ]
}
```

## Building the Content String

`content` is a JSON string, so build it with `jq` rather than hand-escaping quotes:

```bash
STEPS=$(jq -n '{
  trigger: "When the user asks for a refund",
  steps: [
    { type: "ask", instruction: "Ask for the order ID." },
    { type: "say", message: "Your refund is on its way." }
  ]
}')

jq -n \
  --arg name "Structured refund" \
  --arg trigger "When the user asks for a refund" \
  --arg content "$STEPS" \
  '{name: $name, type: "deterministic", trigger: $trigger, content: $content}'
```
