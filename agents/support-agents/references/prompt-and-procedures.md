# System prompt and procedures

## Division of labor

- **System prompt** (in context every turn): identity + tone, the reply envelope (greeting/sign-off, any required disclosure), turn-1 routing priorities and tie-breakers, the verbatim escalation line, and one-line cross-cutting disciplines (e.g. exactly one reply per turn). Keep it short — long prompts measurably hurt instruction-following and latency.
- **Procedures** (loaded when their trigger matches): everything topic-specific — the steps, the policy, the facts-to-look-up, the topic's own escalation criteria.

A rule of thumb for what goes where: if it applies to *every* conversation, one authoritative sentence in the prompt; if it applies to a topic, it lives in that topic's procedure; if it's a product fact, it lives in the KB (see [knowledge-base.md](knowledge-base.md)).

## Writing procedures

**Format:** a `name`, a `trigger`, and a markdown body the agent reads verbatim — write for the agent, not a human reader.

- **Trigger = the condition to match, not an instruction.** Good: "Customer reports being charged twice or sees an unexpected invoice." Bad: "Handle billing disputes." Use real customer phrasing from ticket history — the trigger is matched against what customers actually write. List explicit signal phrases; vague triggers mean the procedure never loads and the model free-runs on priors.
- **Prefer several small procedures with distinct triggers** over one catch-all. When two procedures are chronically confused, merge them instead of adding tie-breaker prose.
- **Structure the body as numbered STEPs with explicit gates:** "STEP 1 look up the account → STEP 2 explain the finding → STEP 3 escalate. You may NOT reach STEP 3 until STEP 2 is done." This is the single most effective control against the model jumping to the end state (escalating before explaining).
- **Positive examples beat prohibitions.** A flat "do NOT X" is violated a surprising fraction of the time even when explicit. Counter the *specific* deviation with a "say this instead" example, or give the real mechanism so the instruction reconciles with the model's prior — don't stack a fourth paragraph of prohibitions.
- Happy path first, then branches and edge cases. Be explicit about when to stop.
- Each procedure must stand alone — the same fact appearing in two procedures is often intentional, not duplication to clean up.
- Don't paraphrase a shared template inside each topic; point at one verbatim template.

## Routing — the silent failure mode

Mis-routing (a scenario captured by the wrong procedure) doesn't error; it produces a confidently wrong flow. Watch for it explicitly:

- Fix routing captures with a **turn-1 tie-breaker list in the system prompt** ("payment made but plan inactive → billing-activation, NOT refund"), or by **adding a category procedure** — not by growing the wrong procedure's text.
- Encourage the model to start every plausible procedure candidate, read them, then follow the one that fits — loading an extra procedure is cheap; committing to the wrong one is not.
- Keep the routing menu (each procedure's trigger) crisp: put the non-obvious "this signal → that procedure" cases in the tie-breaker list.
- Distinguish causes that look alike but resolve differently. "I can't use feature X" can be a plan gate, an unpaid invoice, exhausted quota, or a not-enabled beta — each has a different correct reply. Keep triggers narrow to the genuine case and disambiguate the cause as STEP 1.
- Test routing with `tool`-type tests asserting the first procedure/tool call from the opening message — deterministic and cheap (see [testing.md](testing.md)).

## Reasoning effort (models that support it)

Internal deliberation leaking into customer text ("...this requires escalation, so I will now escalate") usually means the model has no internal outlet. Enabling reasoning gives deliberation a separate channel — but high effort makes the model conclusion-jump past prescribed steps. In practice **`low` is the sweet spot** for procedural support agents, *paired with* STEP-gated procedures (the gates contain the jumping). Re-measure your suite when changing this; the effect is real in both directions.

## Multi-language support

If the user opted into reply-in-customer's-language:

- The **entire customer-facing reply** is in the customer's language — greeting, body, and the escalation hand-off line (translated, meaning preserved). A translated body with an English verbatim escalation line appended is the common failure; make the language rule explicitly override any "copy this line verbatim" instruction, in the procedure body as well as the prompt (when a procedure is active, its wording dominates).
- Decide what stays untranslated (usually only the brand sign-off and any required AI disclosure) and say so explicitly.
- On escalation, the **internal note is written in the support team's working language** (usually English), ideally prefixed with the thread language — a teammate must be able to act without re-reading a foreign-language thread.
- Pin each language rule with a test (e.g. "reply fully in Spanish" + "internal note in English") — these regress easily.

## Escalation

- Define **one verbatim escalation line** in the system prompt, and require a one-sentence explanation of the finding *before* it when the agent has already pulled data — "I'll escalate this" with no explanation reads as a non-answer.
- The escalation *sequence* (post internal note → tag/update → hand off) is a fixed silent series of tool calls — a good candidate for a deterministic procedure or a single composite tool, so the model can't skip a step. Make mistakes impossible to execute rather than trying to catch them.
- The internal note should start with the customer's original issue, then what was checked and found — the model otherwise summarizes only the most recent step.
- Procedures loaded earlier in the conversation may no longer be in context by the time the escalation reply is written — cross-cutting rules about the escalation reply belong in the **system prompt**, not in topic procedures.

## Guardrails — last resort, kept narrow

Guardrails (configured under `platform_settings.guardrails`, see the parent agents skill) run independently of the LLM and can catch high-cost damage: false promises, data leaks, double replies. Use them as a **backstop, not a fix**:

- A hallucinated answer is a routing/missing-lookup bug — fix the upstream cause; an anti-fabrication guardrail is only the net under it.
- A blocking guardrail that false-positives can retry-exhaust and **drop the turn entirely** — a worse outcome than the imperfect reply. Keep the guardrail prompt narrow with a hard first gate, bias it to PASS when unsure, and scope it per-procedure rather than agent-global when the platform allows.
- A well-written blocking guardrail is a dense decision boundary — each example in it pins a real block/pass edge. Resist "slimming" guardrail prompts; the token savings are marginal and each cut example risks a false block.
- Guardrail behavior can differ between test harnesses and production (retry behavior, which parts of a turn get validated). Validate guardrails on real conversations, not only on the suite.

## Slimming an overgrown prompt

When the prompt/procedures have accreted: slim the **system prompt first** (it's sent every turn), then procedures. Per cut: remove one span → run the targeted tests for that area → re-run any red individually → keep the cut only if nothing regressed. If a span *sounds* load-bearing, add a test pinning the behavior first, then trim. Do not slim reply-discipline rules (one-reply-per-turn, envelope, no pre-tool commentary) — they backstop exactly the failures support owners care most about, and seemingly-redundant wording there is often load-bearing.
