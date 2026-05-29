---
name: ralph-loop
description: Run autonomous goal loops with verifiable end states. Use when you need to babysit a task until completion, monitor CI until green, watch a deployment, or any task requiring persistent attention with a defined success condition.
when_to_use: When user says "keep trying until", "babysit this", "watch until done", "loop until success", "monitor until green", or needs autonomous retry logic.
disable-model-invocation: true
allowed-tools: Bash Agent
argument-hint: [goal-condition]
license: MIT
compatibility: Works with Claude Code CLI and web. Requires goal definition.
---

# The Ralph Loop

Autonomous goal loops that run until a verifiable condition is met.

## The Pattern

```
Define condition (/goal)
       |
       v
   [Failed?]---> Agent plans & executes turn
       |              |
       v              v
  Fast model      [Evaluate]
  evaluates           |
  condition           |
  silently            |
       |<-------------+
       v
  [Successful] --> Exit
```

Instead of prompting at every step, declare a durable objective with a verifiable end state. The agent runs, and an independent judge model confirms success.

## The Stop Hook Contract

Every success criterion needs a paired **honest-failure clause**:

| Strict Taxonomy | Honest Failure |
|-----------------|----------------|
| Clear condition | Explicit fail state |

**The Rule**: If the condition is too tight, the agent loops forever. If too loose, you get a fake "done".

## Usage

```
/ralph-loop "CI is green on main branch"
/ralph-loop "All tests pass with no flaky failures"
/ralph-loop "Deployment health check returns 200"
```

## Instructions

When invoked with a goal condition (`$ARGUMENTS`):

1. **Parse the goal** - Extract the verifiable success condition
2. **Define failure criteria** - What constitutes honest failure (not just "try again")
3. **Execute loop**:
   - Plan and execute one turn toward the goal
   - Evaluate condition silently (don't narrate every check)
   - If failed, analyze why and adjust approach
   - If succeeded, report completion
4. **Honest exit** - Report success OR explain why goal is unreachable

## Example: CI Babysitting

Goal: "CI is green on main"

```
Condition: All checks pass on HEAD of main
Failure: 3 consecutive identical failures (not flaky)
         OR unfixable infrastructure issue
         OR test requires manual intervention

Loop:
1. Check CI status
2. If red: analyze failure, push fix, wait for re-run
3. If still investigating: continue
4. If green: exit with success
5. If stuck: exit with honest failure explanation
```

## Stop Conditions

Always define when to STOP, not just when to succeed:

- **Max iterations**: Don't loop infinitely
- **Stale detection**: Same failure 3+ times = stop
- **Scope creep**: Fix drifted too far from original goal
- **Human needed**: Issue requires decisions beyond agent scope

## Case Study

9-hour, 27-minute autonomous session:
- 45 commits
- 4.16M rows of ingested data
- Condition: `14 fix code + 3 ack stale + 1 abandon. 0 jobs queued left.`

The agent looped until the job queue was empty, acknowledging stale items and abandoning truly stuck ones.
