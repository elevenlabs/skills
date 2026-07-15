# System prompt and procedures

## Division of labor

- **System prompt** (in context every turn): identity + tone, the reply envelope (greeting/sign-off, any required disclosure), turn-1 routing priorities and tie-breakers, the verbatim escalation line, and one-line cross-cutting disciplines (e.g. exactly one reply per turn). Keep it short — long prompts measurably hurt instruction-following and latency.
- **Procedures** (loaded when their trigger matches): everything topic-specific — the steps, the policy, the facts-to-look-up, the topic's own escalation criteria.

A rule of thumb for what goes where: if it applies to *every* conversation, one authoritative sentence in the prompt; if it applies to a topic, it lives in that topic's procedure; if it's a product fact, it lives in the KB (see [knowledge-base.md](knowledge-base.md)).

## Writing procedures

**Format:** a `name`, a `trigger`, and a markdown body the agent reads verbatim — write for the agent, not a human reader.

- **Trigger = the condition to match, not an instruction.** Good: "Customer reports being charged twice or sees an unexpected invoice." Bad: "Handle billing disputes." Use real customer phrasing from ticket history — the trigger is matched against what customers actually write. List explicit signal phrases; vague triggers mean the procedure never loads and the model free-runs on priors.
- **Prefer several small procedures with distinct triggers** over one catch-all. When two procedures are chronically confused, merge them. When they're distinct but occasionally mis-capture each other, put the tie-breaker *inside the capturing procedure* ("if this is really about Y, route to Y instead") — a redirect at the point of confusion beats more global routing prose.
- **Structure the body as numbered STEPs with explicit gates:** "STEP 1 look up the account → STEP 2 explain the finding → STEP 3 escalate. You may NOT reach STEP 3 until STEP 2 is done." This is the single most effective control against the model jumping to the end state (escalating before explaining).
- **Positive examples beat prohibitions.** A flat "do NOT X" is violated a surprising fraction of the time even when explicit. Counter the *specific* deviation with a "say this instead" example, or give the real mechanism so the instruction reconciles with the model's prior — don't stack a fourth paragraph of prohibitions.
- **A rule only exists where the model actually is.** A rule inside a procedure does nothing on conversations that never load that procedure — behaviors that must apply before routing (e.g. "obvious spam gets no reply") belong in the always-in-context system prompt, with the procedure carrying only the mechanics.
- **Guard at the point of action, not (only) globally.** When the failure is an *action* (closing a ticket, firing a write), a global system-prompt rule routinely loses to action momentum — put an explicit gate inside the procedure that performs the action ("check BOTH before doing anything below; if either fails, stop"). A prompt rule against premature ticket-closing kept failing until the same check became the first step of the close procedure itself.
- **Gate with turn structure, not facts.** A bullet that *names* what to collect before escalating ("the load-bearing diagnostics are X and Y — ask before escalating") reliably fails: once the model decides to escalate, the whole tool chain runs in one turn and the "ask" gets bundled into the hand-off message. What works is constraining what this turn may BE: "if the customer hasn't provided X and Y, you may NOT escalate this turn — this turn's reply is ONLY the ask; the escalation tools are forbidden until they answer." Tested head-to-head: the naming version went 0/2, the turn-structure version 3/3 on the same scenario, with no suppression of legitimate escalations elsewhere.
- **Describe the behavior; don't rely on a worked example.** A confused model reuses an embedded example verbatim instead of adapting it (a sample sentence gets copied into the wrong language; a sample value becomes the answer). State *what to do* ("translate this sentence into the customer's language"); add examples only when the description alone demonstrably fails, and then several varied ones, never exactly one.
- **Answer every component of a compound ask.** Customers routinely ask two things in one message ("refund this charge, and also why was I charged twice?"); the model reliably answers the component its loaded procedure covers and silently swallows the rest — which reads to the customer as evasion. Require an explicit split ("list each distinct ask; address each, even if the answer is 'escalating this part'") in the reply-discipline rules, and grade multi-ask tests on *both* components.
- Happy path first, then branches and edge cases. Be explicit about when to stop.
- Each procedure must stand alone — the same fact appearing in two procedures is often intentional, not duplication to clean up.
- Don't paraphrase a shared template inside each topic; point at one verbatim template.

## Routing — the silent failure mode

Mis-routing (a scenario captured by the wrong procedure) doesn't error; it produces a confidently wrong flow. Watch for it explicitly:

- Fix routing captures at the right altitude: chronically-confused procedures get **merged**; occasional mis-captures get an in-procedure redirect ("if this is really about Y, route to Y"); only genuinely global turn-1 priorities ("payment made but plan inactive → billing-activation, NOT refund") earn a **system-prompt tie-breaker**. Adding a category procedure beats a blanket escalate.
- Encourage the model to start every plausible procedure candidate, read them, then follow the one that fits — loading an extra procedure is cheap; committing to the wrong one is not.
- Keep the routing menu (each procedure's trigger) crisp: put the non-obvious "this signal → that procedure" cases in the tie-breaker list.
- Distinguish causes that look alike but resolve differently. "I can't use feature X" can be a plan gate, an unpaid invoice, exhausted quota, or a not-enabled beta — each has a different correct reply. Keep triggers narrow to the genuine case and disambiguate the cause as STEP 1.
- Test routing with `tool`-type tests asserting the first procedure/tool call from the opening message — deterministic and cheap (see [testing.md](testing.md)).

## Reasoning effort (models that support it)

Internal deliberation leaking into customer text ("...this requires escalation, so I will now escalate") usually means the model has no internal outlet. Enabling reasoning gives deliberation a separate channel — but high effort makes the model conclusion-jump past prescribed steps. **Start at `low` or `medium`** for procedural support agents, *paired with* STEP-gated procedures (the gates contain the jumping); the non-monotonic trade-off is real in both directions, so pick by measuring your suite, not by intuition.

## Multi-language support

If the user opted into reply-in-customer's-language:

- The **entire customer-facing reply** is in the customer's language — greeting, body, and the escalation hand-off line (translated, meaning preserved). A translated body with an English verbatim escalation line appended is the common failure — and note the canonical English sentence quoted in the instruction is itself an exemplar the model copies. Structure such instructions to **branch on language first** ("IF English, use verbatim: …; IF NOT, write one sentence in the customer's language and do NOT include the English sentence anywhere in the reply"), in the procedure body as well as the prompt (when a procedure is active, its wording dominates).
- Decide what stays untranslated (usually only the brand sign-off and any required AI disclosure) and say so explicitly.
- **Never give exactly one translated worked example.** A single-language exemplar ("e.g. Spanish: '…'") becomes a template: in threads of *other* languages the model copies that sentence verbatim instead of translating — producing a three-language reply. Write the directive language-neutrally ("translate this sentence, meaning preserved, into the customer's language — do not copy any example verbatim"), or give examples in several languages, never one.
- On escalation, the **internal note is written in the support team's working language** (usually English), ideally prefixed with the thread language — a teammate must be able to act without re-reading a foreign-language thread.
- Pin each language rule with a test (e.g. "reply fully in Spanish" + "internal note in English") — these regress easily.

## Escalation

See [escalation.md](escalation.md): derive the write sequence from the customer's own workflow at intake and freeze it in a deterministic procedure; branch the hand-off reply on language *before* presenting the verbatim sentence; internal note starts with the original issue and carries claim + verified figures.

## Guardrails — last resort, kept narrow

Guardrails (configured under `platform_settings.guardrails`, see the parent agents skill) run independently of the LLM and can catch high-cost damage: false promises, data leaks, double replies. Use them as a **backstop, not a fix**:

- A hallucinated answer is a routing/missing-lookup bug — fix the upstream cause; an anti-fabrication guardrail is only the net under it.
- A blocking guardrail that false-positives can retry-exhaust and **drop the turn entirely** — a worse outcome than the imperfect reply. Keep the guardrail prompt narrow with a hard first gate, bias it to PASS when unsure, and scope it per-procedure rather than agent-global when the platform allows.
- A well-written blocking guardrail is a dense decision boundary — each example in it pins a real block/pass edge. Resist "slimming" guardrail prompts; the token savings are marginal and each cut example risks a false block.
- Guardrail behavior can differ between test harnesses and production (retry behavior, which parts of a turn get validated). Validate guardrails on real conversations, not only on the suite.

## Slimming an overgrown prompt

When the prompt/procedures have accreted: slim the **system prompt first** (it's sent every turn), then procedures. Per cut: remove one span → run the targeted tests for that area → re-run any red individually → keep the cut only if nothing regressed. If a span *sounds* load-bearing, add a test pinning the behavior first, then trim. Do not slim reply-discipline rules (one-reply-per-turn, envelope, no pre-tool commentary) — they backstop exactly the failures support owners care most about, and seemingly-redundant wording there is often load-bearing.
