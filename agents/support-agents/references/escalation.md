# Escalation — wiring the hand-off to humans

Escalation is a first-class flow with three parts: a fixed sequence of ticketing writes, a customer-facing hand-off reply, and an internal note for the human. Each has its own failure modes.

## Derive the write sequence at intake — ask, don't guess

The concrete calls depend on the customer's ticketing platform *and their team's workflow* — who picks up escalated tickets, which tags/queues route them, what stops the agent from re-engaging. During the intake survey, ask explicitly:

- "When your human team takes over a ticket today, what exactly changes on it — assignee, status, tags, group?"
- "What should mark a ticket so the agent stays out of it afterwards?"
- "Is there a tag or field your reporting relies on for escalated-by-AI tickets?"

Then freeze their answers into a **deterministic procedure** (fixed tool order, model can't skip or reorder a step). Worked example — the Zendesk sequence one production support agent uses, as four silent tool-call steps:

1. `zendesk_add_comment` — internal note (`public: false`) summarizing the case for the human
2. `zendesk_update_ticket` — unassign (`assignee_id: null`) + `status: open` so it lands in the human queue
3. `zendesk_add_tags` — the suppress-AI tag (loop prevention: the trigger excludes it, so the agent never re-engages)
4. `zendesk_remove_tags` — clear any tag that would route it back to an automated workflow

Other platforms have equivalents (Intercom assignment + snooze rules, Front tags + inbox moves) — the shape is the same: note → reassign/status → routing tags.

## The hand-off reply

- Define **one verbatim hand-off sentence** and require a one-sentence acknowledgment of the finding before it when the agent has already pulled data — a bare "I'll escalate this" reads as a non-answer.
- **Branch on language before presenting the verbatim sentence.** An instruction that leads with "include this exact sentence word-for-word" and only then says "translate for non-English threads" loses: the model appends the quoted English sentence to non-English replies. Structure it as: check the thread language first → non-English: write the hand-off entirely in the customer's language, the English sentence must not appear → English only: the exact sentence. Keep the quoted sentence out of the procedure body if the always-loaded prompt already carries it — every extra copy is another attractor.
- The reply is ONE message: no separate findings message before the escalation writes (double-reply).
- Cross-cutting hand-off reply rules belong in the **system prompt**: by escalation time, the topic procedure that routed here may no longer be in context.

## Partial eligibility: order the carve-out before the escalation

When one request splits into an in-policy part and an out-of-policy part (e.g. the latest charge is refund-eligible, earlier ones need review), the failure mode under customer pressure is **escalate-everything**: the model hands the whole case to a human and the customer loses the self-serve resolution they were entitled to. Wording it as a preference ("handle the eligible part; escalate the rest if warranted") does not survive pushback — the model reads exception-pressure as the warrant. What works is an explicit ordering constraint at the point of action: *the eligible part's resolution step must be completed first, and the escalation writes for the remainder may only fire in a turn whose reply also carries the eligible part's deliverable.* That makes skipping the carve-out structurally impossible rather than merely discouraged.

## The internal note

- Start with the customer's original issue, then what was checked and found — otherwise the model summarizes only the most recent step.
- For a disputed claim, include both the claim and the verified figures so the reviewer sees the discrepancy framing.
- For non-English threads the note is written in the support team's working language, prefixed with the thread language.

## Testing it

Pin with simulations per language you care about (the hand-off-language failure regresses easily), plus one asserting the full write sequence fired (note + status + tags). Escalation of an action-only request is a *success* outcome in grading, not a failure.
