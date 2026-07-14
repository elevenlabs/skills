# Testing — suite discipline and mining tickets into tests

## Test types

Created via `POST /v1/convai/agent-testing/create`, attached to the agent under `platform_settings.testing.attached_tests`, run with `POST /v1/convai/agents/{agent_id}/run-tests` (see the parent agents skill for schemas). How they earn their keep on a *support* agent:

- **`simulation` — the default for reply content.** A simulated customer persona runs the whole multi-turn flow; LLM graders check `success_conditions`. Costs: multi-turn + LLM-graded = real run-to-run variance.
- **`tool` — deterministic; use for routing and dispatch.** Asserts the agent's next tool call (tool, and per-parameter `exact`/`regex`/`llm` checks; `verify_absence` checks a tool is NOT called). Zero grader noise. Most reliable from the conversation opener; a test built by truncating a real conversation mid-thread does not reconstruct loaded-procedure state and will re-route — start routing tests from turn 1.
- **`llm` (next-reply) — use sparingly on tool-heavy agents.** It grades the next generation, which for a procedural agent is often a tool call with no customer-facing text; investigate before concluding "the agent didn't respond."

Seed the suite from the intake survey: per topic, one happy-path simulation + one escalation simulation + one turn-1 routing `tool` test.

## Suite discipline

- **Targeted subsets by default, full runs as gates.** After a change, run the changed test plus *adjacent* tests (same procedure, same routing tie-breaker, same tool). Pick adjacents adversarially: for a routing change, include a test of the procedure you route TO and one you might wrongly steal FROM. Reserve full runs for pre-merge gates — each test costs a full conversation.
- **Read finished runs from the API — never re-run to recover results.** Capture the invocation id when launching; `GET /v1/convai/test-invocations/{test_invocation_id}` returns per-test status and grader rationale (`condition_result.rationale`) for the stored run.
- **Variance discipline.** A red is a suspect, not a verdict: re-run it individually; genuine failures reproduce, stochastic ones don't. Aggregate pass rate is noise-bound — trust direction across runs and clear per-test effects, not single-run ±3% moves. `repeat_count` on run-tests separates flaky from consistent failures. The same rule applies to **fixes**: never iterate config edits on single-run signals — a ~50% flaky test will alternately "confirm" and "refute" every edit you make; measure with repeats before and after.
- **Silent behaviors can't be graded by conversation simulations.** A correct no-reply turn (e.g. a spam silent-close) makes the harness time out waiting for agent text — the run reads failed even though the tool calls show the exact desired behavior. Verify such behaviors from the transcript's tool calls, and don't leave an ungradable test attached to the suite; document it and detach.
- **Cluster failures by grader rationale and fix by cluster, not per test.** But don't blindly trust the rationale — it's the grader's interpretation. Pull the full transcript whenever the rationale is thin or surprising (and for a sample even when it isn't).

## Classify every failure BEFORE fixing

Read the failing transcript turn by turn *from the agent's point of view* — what did it see, which procedure was active, what did each tool return? Then bucket:

1. **Harness gap** — a tool returned "no mock matched" or similar: the test lacks a mock, the agent is innocent. Fix the mock. This is the #1 mis-triage: it masquerades as "agent never responded."
2. **Infra flake / timeout** — re-run; not a content fix. (If simulated turns time out consistently, check the test's conversation-source/turn-budget configuration rather than shortening the agent's work.)
3. **Stochastic variance** — doesn't reproduce in isolation; don't "fix" it.
4. **Bad criterion** — the criterion contradicts ground truth, is stale, grades the wrong turn, or demands what the conversation's *actual* tool data contradicts. Fix the test and say so explicitly — never silently weaken a criterion, and never bend the agent to a bad test. Re-verify criteria against the conversation's real tool results, not a prose summary of them.
5. **Real agent gap** — only now pick the fix layer ([improvement-loop.md](improvement-loop.md)).

Also validate tests **proactively**: when config changes (a tool renamed, a price updated, a policy changed), sweep the suite for criteria referencing the old state — a stale test punishes correct behavior. Cheap static checks (does every referenced tool still exist on the agent? do figures in criteria still match the KB?) catch these before they cost a debugging session.

## Mocks

- In saved tests, webhook tools resolve from mock configuration (`tool_mock_config` / tool-level response mocks) — after adding or changing a test, make sure every tool the scenario touches has a matching mock, keyed by the parameters the agent will actually send.
- **Give every simulation a unique persona** (unique email, unique account id). Mocks keyed by a shared parameter collide across tests — the wrong account's data silently wins and the test fails for a fake reason. Verify the intended mock actually reached the agent (read the lookup result in the transcript) before trusting a verdict.
- **Match the persona's mock to the scenario's real account state** (tier, platform, status). A generic mock makes the grader fail tickets whose correct answer depends on the real state.
- **Client tools need catch-all mocks** — a simulation has no client, so an unmocked client tool rejects the run.
- **Never let tests write to production systems.** Mock every ticketing/CRM *write* tool with `mocking_strategy: "selected"` + the write-tool ids, and keep the fallback on raise-error, never call-real-tool. For maximum realism run **pre-production tests**: real read tools against a real (consenting) account, only the writes mocked — this surfaces payload shapes synthetic mocks miss.
- You generally cannot mock a tool *error* — an unmocked call is the only "failure" the harness produces. Exclude those runs when judging agent behavior.
- **Mocks resolve first-match-wins against a list** — a broad "catch-all" entry (no/empty parameter conditions, usually returning some empty/default template) shadows every entry appended after it in the list. If your mock-sync tooling appends new personas to the end rather than sorting conditioned entries before catch-alls, every persona added after the catch-all silently gets the default template instead of its own keyed data — and only tests that assert a *specific value* (a tier, a balance) catch it; tests that only assert *behavior* pass on the wrong data and hide the bug. Sort catch-all mocks last (or re-sort on every sync) and, when a new persona's test fails on an unexpectedly-empty/default field, check for this before debugging the agent.

## Replaying real tickets with real reads (preprod batch)

The agent is almost always *picking up from* an incumbent — usually human support associates, sometimes an older or weaker AI model. The highest-signal validation short of production is to replay a batch of recent real tickets through the agent with **real read tools** (the lookup resolves the ticket's actual requester) and **only the write tools mocked**, then compare each reply against what the incumbent actually did on that ticket. Two outputs, both valuable:

- **Behavior gaps** — where the agent's handling diverges from the incumbent's (validate before treating as a failure; the incumbent isn't always right).
- **Capability gaps** — places the incumbent used data or took actions the agent has no tool or knowledge source for. Log these explicitly ("human quoted the decline reason from the payment processor; agent has no lookup for it") — they're the tooling/KB roadmap, and per the read-only doctrine some are correctly answered by escalation rather than a new tool.

Outline of the runner (write it as a small script against the public API — don't hand-run 20 tickets):

1. **Safety pre-flight (non-negotiable):** fetch the agent config for the branch, extract every tool id referenced anywhere in it, resolve each tool's name, and abort unless every ticketing-system tool is in the mocked list. This is the only thing standing between a real-account run and a mutated production ticket.
2. Per ticket, create a `simulation` test: persona built from the ticket (below), `tool_mock_config` with `mocking_strategy: "selected"` + the write-tool ids + fallback raise-error, dynamic variables carrying the **real requester email** (so reads resolve their real account) but a **fake ticket id**, and the production conversation-initiation source (real turn budget).
3. Attach the tests to the working branch, run them in one `run-tests` invocation (the platform caps concurrency itself), and poll the invocation for results.
4. Save the full invocation JSON locally — the transcripts (replies + every tool call marked real vs mocked) are your comparison corpus. It contains customer PII: keep it out of version control.
5. These tests are throwaways: after analysis, delete them and remove their attachments; only validated failures get re-authored as anonymized committed regressions.

### Building a faithful persona from a ticket

The simulated customer is only as good as its briefing. Craft the persona deliberately:

- **Faithful first message.** The persona's opening message should be the ticket's actual first message (lightly trimmed), in the ticket's original language — not a paraphrase. Paraphrases quietly drop the phrasing that drives routing.
  - **Trim quoted-reply/forward chains with a precise header pattern, not a bare prefix.** Real tickets often carry the whole email chain below the new text ("On Tue, ... wrote:", or the localized equivalents "El ... escribió:", "Le ... a écrit :", "Am ... schrieb"). Cutting on a bare leading token ("On ", "El ", "Le ", "Am ") false-positives on ordinary sentences that happen to start the same way ("On my account…", Spanish "El problema es…") and truncates the real opener. Match the *whole* header shape instead (e.g. `\bOn [^\n]{2,140}? wrote:`) so only genuine quote/forward headers get cut.
- **Hidden information.** Real customers know things they didn't put in the opener (which email they paid with, what they already tried, the exact error text, their purchase platform). Put those facts *in the persona description* — drawn from the **whole thread**, not just the opener — so when the agent probes, the sim answers consistently instead of inventing. A persona that invents "I subscribed on the website" when the real customer later said "Google Play" sends the whole comparison down the wrong branch.
- **Identity consistency.** If the harness resolves real data via the ticket's requester email, the persona must know that email is *its own* — a persona claiming a different address than the one the tools resolve produces a fake "account not found" dispute.
- **Disposition fidelity.** Carry the real customer's later-turn behavior into the persona: if they refused self-serve steps and demanded direct action, the persona must too. A compliant sim customer makes the agent's handling look better than it would have played out; an extra-suspicious one (e.g. distrusting a link the real customer accepted) makes it look worse.
- **Describe attachments in text.** Customers convey key facts via screenshots (an invoice, an error dialog, a bank statement). If the agent is image-blind — and in most test harnesses even vision-capable agents won't get the pixels — the persona description must carry what the image showed, marked as such ("you have a screenshot showing a $22 charge dated the 3rd; describe it if asked").
- **Explicit stop rule.** Tell the persona when the conversation is over ("stop once the agent gives its substantive answer or hands off to a human") — otherwise simulations pad turns and burn budget.
- **Don't leak the answer.** The persona must know what the customer knew, not what the resolution was. A persona that hints at the expected fix invalidates the test.

## Mining historical tickets into tests

Once the seeded suite is green, grow it from real traffic:

1. **Shortlist tickets close to existing topics** (depth on covered categories beats exotic one-offs). Dedupe against scenarios the suite already covers.
2. **Derive the verified correct answer per ticket** from the ground-truth hierarchy ([ground-truth.md](ground-truth.md)) — not from the old human reply. Only the verified answer becomes criteria.
3. Build the simulation: persona/opening from the ticket's first message, mocks matching the inferred account state, criteria from the verified answer.
4. **Run → pass ⇒ delete, fail ⇒ commit.** A passing ticket-test adds no signal and pollutes the suite denominator; a failing one is a real gap and becomes a permanent regression test. Never delete an already-committed test.
5. When deleting a throwaway test, also remove its attachment from the agent — a deleted-but-attached test shows as a broken row and skews the suite.
6. Periodically run a **stratified random sample** of tickets (weighted by category volume) graded against each ticket's actual resolution — curated probes are optimistic and miss whole failure classes. Sample tests embed real customer text: treat them as throwaway (never commit), and write clean anonymized regression tests only for confirmed gaps.

## Grader traps worth knowing

- Don't write an absolute "no tools were called" criterion — grader-side evaluation calls can show up in the transcript and fail it spuriously. Grade observable behavior ("did not start a refund flow") instead.
- If the agent's first message interpolates a dynamic variable, every test persona must supply it, or the conversation dies at turn 0.
- A criterion that enforces a first-reply rule on a later turn, or reads a compliant "both A and B" ask as either/or, is a criterion bug — seen repeatedly in generated suites.
- When you PATCH agent config, preserve `platform_settings.testing.attached_tests` — careless config writes can silently detach the suite.
