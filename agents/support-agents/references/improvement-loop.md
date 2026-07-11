# The improvement loop — production conversations to verified fixes

Run this loop on a cadence once the agent handles real traffic. Its shape: pull everything → derive ground truth → judge the agent → fix at the right layer → lock in with a test.

## 1. Pull a complete, dated corpus

One dated file per review (don't append to old ones — each review stays reproducible). List conversations with `GET /v1/convai/conversations?agent_id=...` (paginate via `cursor`, filter by start time), then fetch each transcript with `GET /v1/convai/conversations/{conversation_id}`.

**Pull everything for every conversation — never a partial dump.** Verdicts made on partial data are wrong (a working tool reads as "returns nothing" because the dump dropped results). Per conversation you need:

- every agent reply (`transcript[].message`)
- **every tool call AND its result** — `transcript[].tool_results[].result_value` holds the real payload; treat a missing result as a dump bug to fix, not as "the tool returned nothing"
- **every KB retrieval** — `rag_retrieval_info`: the query, retrieved chunks, and `used_chunk_ids`; resolve chunk text via `GET /v1/convai/knowledge-base/{documentation_id}/chunk/{chunk_id}`
- **the human resolution** when the ticket was escalated (from the user's ticketing system, read-only) — the primary evidence for what a human actually did
- attachments/screenshots the customer sent — if the agent can't see images, those are exactly the context it missed

Keep the corpus local and uncommitted; it's customer data.

### Classify thread authors before trusting them

A ticket thread is not a clean "customer + human agent" transcript. It may interleave: the customer, **your** agent's replies, a *different* AI system's replies (many teams run more than one, or a vendor bot answered first), human agents after escalation, and internal notes. Classify every comment (requester id → customer; non-public → internal note; AI signature/disclosure line → which AI; otherwise human) before treating anything as "the resolution". Two consequences:

- "What actually happened" = the *last* substantive handling, usually the human's post-escalation resolution when one exists — not the first AI reply.
- Teams without an incumbent AI agent will have human-only threads; the loop below works the same, the human reply is just the whole ground-truth side.

## 2. Judge each conversation against ground truth

Derive the correct answer independently ([ground-truth.md](ground-truth.md)) — never assume the agent's reply, the human's reply, or the current procedure is correct. Then judge the agent's reply on three axes:

- **Complete** — answered the whole ask, used the data it had already pulled
- **Accurate** — no invented prices, paths, or mechanics; matches the verified answer
- **Policy-following** — right escalate-vs-resolve call, firm where policy is firm, correct envelope

### Validate divergences with an independent checker

When the agent's handling *differs* from what the thread shows, don't trust your own first read — spawn a separate validation pass (a subagent on a cheaper model works well; the judging is retrieval-heavy, not reasoning-heavy) with a strict brief:

- It must find **N independent supporting sources** (3 is a good default) across the evidence — product code, KB/docs, pricing data, the written policy, the thread itself — before the divergence counts as a real agent failure. Independent means different origins, not three quotes from one page.
- It defaults to **exonerating the agent**: "different from the human" is not "wrong" (humans deviate from policy too; the old reply may be stale). The verdict must state which side the sources support.
- Give it the complete evidence (agent transcript incl. tool results, the thread, the ground-truth source list) — a checker on partial data returns confident nonsense.

Calibration rules:

- **Escalation of an action-only resolution is a GOOD reply.** If the fix requires an action the agent can't take (refund, credit restore, plan change), escalate-with-explanation is the best possible outcome — don't log it as a tool gap.
- Before recommending a new read tool, confirm the data isn't already available through an existing one — most "missing tool" flags turn out to be the agent not using data it already had.
- Treat any "the agent fabricated X" finding as a claim to re-verify with a citation, defaulting to exonerating the agent (see the corroboration rules in [ground-truth.md](ground-truth.md)).
- A reply that escalates something answerable, or answers without pulling data it had access to, is not "best" even if factually harmless.

Group every conversation into exactly one bucket: **no action needed** / **agent-config fix** (actionable now) / **platform limitation** (needs a product change — record it and move on; don't contort agent config around it).

## 3. Pick the fix layer

For each confirmed gap, choose the *layer* first — most wasted cycles come from fixing the right problem in the wrong place:

| Symptom | Layer |
|---|---|
| Wrong behavior/sequencing within a topic | The topic's **procedure** — a positive "say this" step, not another prohibition |
| Scenario captured by the wrong procedure | **Turn-1 routing tie-breaker** in the system prompt, or a new/merged category procedure |
| Wrong or missing product fact | **Knowledge base** (verify retrieval), or a deterministic read tool for facts retrieval can't serve |
| Answered from memory instead of looking up | Make the lookup an explicit, mandatory procedure step; prefer "look it up" wording over inline facts |
| Wrong/confused/absent tool call | **Tool description** — state what it returns and what it does NOT, naming the right alternative |
| Misread its own tool payload (conflated look-alike fields, e.g. plan quota vs actual usage) | **Procedure or tool description** — name the exact field to read and the look-alike to avoid; require the dedicated tool for that fact |
| A fact that must span topics or override a strong prior | A cross-cutting instruction — used sparingly; global additions pollute every topic |
| High-cost damage class (false promise, leak, double reply) | **Guardrail** — last resort, narrow, biased to pass ([prompt-and-procedures.md](prompt-and-procedures.md)) |
| Criterion contradicts ground truth | Fix the **test**, not the agent |

Hallucination is almost always a routing or missing-lookup bug — find why the model lacked the fact; "please don't hallucinate" prompt text fixes nothing.

## 4. Verify, then lock in

**Recommend a fresh branch per tuning pass** (named after the pass, e.g. a date), created off the live branch at the start of the pass: all fixes land there, the suite runs there, and the user reviews and merges when it gates green. This keeps live traffic untouched while you iterate and makes the whole pass revertible as a unit. It's a recommendation, not a mandate — some users prefer per-fix branches or direct edits with review; ask once and follow their preference.

Per change (one at a time):

1. Write or update the regression test first — it must fail on the current config.
2. Apply the smallest change at the chosen layer, on the working branch.
3. Run the target test + adjacent tests (same procedure/tie-breaker/tool). Re-run any red individually.
4. **Keep only if** the targeted set improves and nothing previously green regressed. Otherwise revert and log the dead end — a written "tried and reverted" list saves every future session from repeating it.
5. Merge the branch when the suite gates green; for riskier changes, split a small percentage of traffic to the branch and re-review real conversations before promoting.

A merged platform-side change is not necessarily deployed — before enabling config that depends on a brand-new platform field, confirm the live endpoint accepts it.

## Keep the human in the loop

All agent-config changes are proposals until a human approves them: show the diff, explain the failing-conversation evidence behind it, apply after approval, and keep changes versioned (branches) so anything can be reverted. Every proposal carries its before/after test — that's what makes the review concrete.
