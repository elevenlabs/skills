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
- **Variance discipline.** A red is a suspect, not a verdict: re-run it individually; genuine failures reproduce, stochastic ones don't. Aggregate pass rate is noise-bound — trust direction across runs and clear per-test effects, not single-run ±3% moves. `repeat_count` on run-tests separates flaky from consistent failures.
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
