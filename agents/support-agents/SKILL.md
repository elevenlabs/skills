---
name: support-agents
description: Build, test, and improve a customer-support agent on the ElevenLabs Agents Platform through a guided, interview-driven workflow. Use when the user wants to build a support agent for their product, connect or improve an existing support agent, tune its knowledge base, write procedures, build a regression test suite from real tickets, or set up an improvement loop from production conversations.
license: MIT
compatibility: Requires internet access and an ElevenLabs API key (ELEVENLABS_API_KEY).
metadata: {"openclaw": {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "primaryEnv": "ELEVENLABS_API_KEY"}}
---

# Building Support Agents

Act as a support-agent engineer. This skill is a guided journey: interview the user, set up (or adopt) an agent, ground it in verified knowledge, then iterate failure → verified fix with a test suite as the gate. The typical entry point is a user in this directory saying "walk me through building a support agent for X".

For general Agents Platform reference (creating agents, tools, workflows, widget, guardrails config), see the parent [agents skill](../SKILL.md). This skill covers what is specific to *support* agents.

Reference files (read when you reach the phase):
- [references/ground-truth.md](references/ground-truth.md) — ranking sources of truth, deriving correct answers
- [references/knowledge-base.md](references/knowledge-base.md) — KB setup and RAG tuning
- [references/prompt-and-procedures.md](references/prompt-and-procedures.md) — system prompt and procedure authoring
- [references/channel-integration.md](references/channel-integration.md) — wiring the agent to a ticketing channel (trigger, identity binding)
- [references/escalation.md](references/escalation.md) — the human hand-off: deterministic write sequence, hand-off reply language rules, internal note
- [references/testing.md](references/testing.md) — test types, suite discipline, mining tickets into tests
- [references/improvement-loop.md](references/improvement-loop.md) — analyzing production conversations, picking the fix layer

## Operating principles

These are hard-won; follow them even when a shortcut looks faster.

1. **Derive ground truth before touching config.** Never teach the agent an answer you haven't verified against the user's most authoritative source. Corroborate important facts from at least two independent sources; if sources disagree, the disagreement is the finding — surface it, don't average.
2. **Tests are the gate.** Every improvement ships with a test that failed before the change and passes after. Keep a change only if the targeted tests improve and nothing previously green regresses.
3. **Smallest change at the right layer.** Prefer, in order: knowledge base > tool description > procedure > system prompt > guardrail. Most product knowledge should be retrievable, not memorized in the prompt. If a session produces more prompt text than KB/tool changes, stop and re-justify.
4. **The agent is read-only by default.** Start with diagnostic (read) tools plus an escalation path. A ticket whose only resolution is an action the agent can't take (refund, plan change, account restore) is *correctly* handled by escalation — that's a good reply, not a missing-tool gap. Add write tools only after the read-only agent is reliable and the user explicitly accepts the risk.
5. **One change at a time.** Config changes are proposals: show the diff, get approval, apply, test, keep or revert. Never batch unrelated edits between test runs.
6. **Validate the test before blaming the agent.** LLM graders misfire and generated criteria drift. A failing criterion that contradicts ground truth is a test fix, not an agent fix. Never bend the agent to a bad test.

## How to run the journey

- Ask questions in small groups (2–3 per message), acknowledge answers, then move on. Don't dump a 20-question form.
- Keep a local project directory as the source of truth — config as files the user can review and diff:

```
support-agent/
├── survey.md            # intake answers (Phase 0)
├── prompt.md            # system prompt
├── procedures/*.md      # one file per procedure
├── tools/*.json         # tool definitions
├── tests/*.json         # saved tests (the committed suite)
└── kb/sources.md        # KB source inventory + doc ids
```

- After each phase, checkpoint: summarize what's set, what's default, what's missing; get explicit confirmation before deploying anything.
- Never delete an agent, test, or KB document without explicit approval.
- API calls use the `xi-api-key: $ELEVENLABS_API_KEY` header against `https://api.elevenlabs.io`. If the key is missing or invalid, run the [setup-api-key skill](../../setup-api-key/SKILL.md) flow — never ask the user to paste a key into chat.

## Phase 0 — Intake survey

### 0.1 The agent

Ask: **"Do you already have an ElevenLabs support agent, or are we starting from scratch?"**

If they have one, accept a dashboard URL and parse it:

```
https://elevenlabs.io/app/agents/agents/{agent_id}?branchId={branch_id}
```

- `agent_id` starts with `agent_`; the optional `branchId` query param (starts with `agtbrch_`) is the branch they're working on.
- Verify and dump the config: `GET /v1/convai/agents/{agent_id}`. Materialize the config into the project directory (prompt, tools, attached tests, KB references) so all later edits are reviewable diffs.

If they don't have one, you'll create it in Phase 1.

### 0.2 Channel and language

- **Channel:** support tickets/email (e.g. via the Zendesk integration), a chat widget, or voice? Ticket/chat agents should set `conversation_config.conversation.text_only: true`; voice adds TTS/ASR concerns covered in the parent agents skill.
- **Languages:** English-only or reply-in-customer's-language? If multilingual, plan for it from the start (see the language section of [references/prompt-and-procedures.md](references/prompt-and-procedures.md)) — retrofitting language rules is much harder.

### 0.3 Ground-truth sources

This is the highest-leverage part of the interview. Read [references/ground-truth.md](references/ground-truth.md), then survey the user for what exists:

- an **authoritative code repository** (how the product actually behaves — billing logic, error codes, feature gating)
- **existing support procedures / SOPs / macros** (how a human agent is told to handle each case)
- a **help center / docs site** and a **pricing page**
- **historical tickets or conversations** and how to access them:
  - their ticketing system's export (a local dump is ideal — ask how they can produce one)
  - or, if an ElevenLabs agent already handles traffic, pull conversations via `GET /v1/convai/conversations?agent_id=...` (paginate with `cursor`), then `GET /v1/convai/conversations/{conversation_id}` for full transcripts
- **human escalation targets** (who handles what the agent can't)

Record the resulting hierarchy in `survey.md` — you will consult it on every fix.

### 0.4 Scope and escalation policy

- Which topics must the agent answer, which must it *always* escalate (legal threats, security incidents, VIP accounts)?
- What data may it read? What actions (if any) may it take? Default to read-only (principle 4).
- Tone/brand rules: greeting/sign-off envelope, phrases to avoid, disclosure requirements (e.g. an "AI-generated" notice).

**Checkpoint:** present the full survey (including empty fields) and get confirmation before Phase 1.

## Phase 1 — Create or adopt the agent

Creating a text support agent:

```bash
curl -s -X POST "https://api.elevenlabs.io/v1/convai/agents/create" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Support",
    "conversation_config": {
      "conversation": {"text_only": true},
      "agent": {
        "first_message": "",
        "language": "en",
        "prompt": {"prompt": "<from prompt.md>", "llm": "claude-sonnet-4-5"}
      }
    }
  }'
```

- Pick the LLM deliberately: support agents follow multi-step policies and call tools, so prefer a strong tool-calling model; check `GET /v1/convai/llm/list` for the current catalog. If the model supports a reasoning-effort setting, start at `low` or `medium` for procedural support agents and pick by measuring — see [references/prompt-and-procedures.md](references/prompt-and-procedures.md).
- **Config PATCH gotchas:** GET returns the prompt block with both resolved `tools` and `tool_ids` — strip `tools` before PATCHing the config back or the API rejects it; and always re-verify tool wiring (`tool_ids`) and `platform_settings.testing.attached_tests` after any agent write, since careless writes can silently reset them. Prefer round-tripping the *live* config (GET → surgical edit → PATCH) over pushing a locally-stored copy.
- **Branch discipline:** make changes on a working branch, not the live one. `POST /v1/convai/agents/{agent_id}/branches` creates one; pass `branch_id` on reads/patches; merge via `POST /v1/convai/agents/{agent_id}/branches/{source_branch_id}/merge` once the suite is green. Traffic can be split between branches for staged rollout (start ~10%, watch, then promote).

## Phase 2 — Knowledge base

Read [references/knowledge-base.md](references/knowledge-base.md). Summary of the flow:

1. Ingest the help center / docs / pricing sources (`POST /v1/convai/knowledge-base/url|file|text`), RAG-index them, attach to the agent.
2. Keep the KB **wide** (the agent must eventually answer all query types) but **clean** — noisy or off-topic pages in a shared folder actively hurt retrieval.
3. Verify facts the way the agent retrieves them, not by browsing the public site.
4. Watch for JS-rendered pages (pricing pages are the classic case): a crawler often captures only navigation cruft. Verify what was actually ingested before trusting it.

## Phase 3 — System prompt and procedures

Read [references/prompt-and-procedures.md](references/prompt-and-procedures.md). Core rules:

- Keep the system prompt **short**: identity, tone/envelope, turn-1 routing priorities, escalation line, cross-cutting reply discipline. Everything topic-specific goes in a procedure.
- One procedure per support topic, with a trigger written as *the condition to match* ("Customer reports being charged twice") in real customer phrasing — not as an instruction. Prefer several small procedures over one catch-all.
- Write procedures as numbered STEP sequences with explicit gates ("do not reach STEP 3 (escalate) until STEP 2 (explain) is done"). Positive "say this" examples beat prohibitions — a bare "do NOT X" is violated surprisingly often.
- Routing is the silent failure mode: when a scenario is grabbed by the wrong procedure, fix it with a turn-1 routing tie-breaker in the system prompt or by merging chronically-confused procedures — not by bloating procedure text.

Procedures are edited in the dashboard (Agent → Procedures). A REST surface for procedures exists under `/v1/convai/agents/{agent_id}/branches/{branch_id}/procedures` but is **alpha and absent from the public OpenAPI spec** — if you use it, warn the user it may change without notice, and prefer the dashboard for anything they'll maintain long-term.

## Phase 4 — Tools and escalation

- Start with **read-only diagnostic tools**: account/subscription lookup, usage overview, invoice list, order status — whatever lets the agent *explain* instead of guessing. Wrap the user's existing APIs as webhook tools (see the parent agents skill for schemas).
- **Tool descriptions carry prompt-level leverage** (they're read every turn): state what the tool returns AND what it does NOT return, naming the tool to use instead. Overlapping/vague descriptions are a top cause of wrong-tool calls.
- **Escalation is a first-class flow, not a fallback.** Ask the user at intake how their team takes over tickets today, then freeze that into a deterministic write sequence — see [references/escalation.md](references/escalation.md).
- If a ticketing system is involved, mock its **write** tools during all testing — never let a test post to production tickets (see [references/testing.md](references/testing.md)).

## Phase 5 — Test suite

Read [references/testing.md](references/testing.md). The arc:

1. Seed the suite from the survey's key scenarios (one happy path + one escalation per topic), then grow it by mining historical tickets: convert tickets the agent likely handles poorly into simulation tests, derive expected behavior from ground truth (never from the old human reply alone), and keep only the ones that fail — a passing ticket-test adds no signal.
2. Use `simulation` tests for reply content, `tool`-type tests for routing/dispatch (deterministic, no grader noise).
3. Run via `POST /v1/convai/agents/{agent_id}/run-tests` (branch-aware); read results from `GET /v1/convai/test-invocations/{test_invocation_id}` — never re-run a suite just to recover results.
4. **Always download and read the full transcript** of a failing (or surprising-passing) run — the grader's pass/fail and rationale are an LLM's interpretation, not ground truth. Judge from what the agent actually saw and did.
5. Respect variance discipline: re-run a red individually before treating it as real; LLM-graded multi-turn tests are stochastic.
6. Anonymize any real customer data before it lands in a committed test (emails → `example.com`, fake names/ids that preserve shape).
7. **Delete temporary tests when done** — throwaway replay/probe sims and their agent attachments. Anything left attached pollutes the suite and its pass rate; only validated failures stay, re-authored as anonymized committed regressions.

## Phase 6 — Improvement loop (once live)

Read [references/improvement-loop.md](references/improvement-loop.md). Loop:

1. Recommend a fresh branch per tuning pass (user-configurable); fixes land there and the user reviews + merges.
2. Pull a dated batch of production conversations (transcripts + tool results + RAG retrieval info + the human resolution when escalated). Classify thread authors first — threads mix your agent, other AI systems, and humans.
3. For each conversation, derive the ground-truth answer, then judge the agent's reply: complete, accurate, policy-following? Where the agent's handling diverges from the thread, validate with an independent checker (N independent sources) before calling it a failure. Group into **no action needed / agent-config fix / platform limitation**.
4. For each config fix: validate the eval criterion, pick the fix layer, make the smallest change, run the target test plus adjacent tests, keep only on improvement without regression.
5. Encode every confirmed gap as a permanent regression test before fixing it.

## Safety rules

- Never ask for or echo API keys, passwords, or tokens in chat; keys live in `.env` or the environment.
- Treat the user's ticketing system as **read-only**; mock all write tools in tests and pre-production runs.
- Real customer data (tickets, transcripts, emails, invoices) stays in local uncommitted files; anything committed or uploaded is anonymized first.
- Never delete agents, branches, tests, or KB documents without explicit user approval — including as error-recovery.
- All agent config changes go through the review-diff-approve flow; don't silently patch a live branch.
