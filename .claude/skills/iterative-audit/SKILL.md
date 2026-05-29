---
name: iterative-audit
description: Run multi-pass audits where each pass reads failure patterns from the previous one. Use when auditing code, reviewing PRs, checking compliance, or any quality task where iterative refinement beats exhaustive single-pass review.
when_to_use: When user wants to audit, review, check quality, or validate something thoroughly. When a single review pass isn't enough.
disable-model-invocation: true
context: fork
agent: Explore
allowed-tools: Read Bash Grep
argument-hint: [target] [audit-type]
license: MIT
compatibility: Works with Claude Code CLI and web.
---

# Iterative Auditing

Three 10-minute audits where each reads the failure patterns of the previous one radically outperforms one exhaustive 60-minute audit.

## The Pattern

```
Pass 1 (Apply docs)     --> 29% fixed
Pass 2 (Read failures)  --> 64% fixed  
Pass 3 (Target parsers) --> 79% fixed
Pass 5 (Pivot creative) --> 100% fixed
```

**Key insight**: `Audit URL != Audit Parser != Fix Runtime`

Each pass has a different focus. Reading why the previous pass failed reveals patterns invisible to a fresh audit.

## Usage

```
/iterative-audit src/ security
/iterative-audit . code-quality
/iterative-audit api/ compliance
```

## Instructions

When invoked with target and audit type:

### Pass 1: Apply Standard Checks
- Run standard linting/analysis for the audit type
- Document all findings with file:line references
- Note which issues are auto-fixable vs manual
- Save findings to `audit-pass-1.md`

### Pass 2: Read Pass 1 Failures
- Read `audit-pass-1.md`
- For each unfixed issue, understand WHY it wasn't fixed
- Look for patterns: same error type? same file area? same root cause?
- Apply targeted fixes based on failure analysis
- Save remaining issues to `audit-pass-2.md`

### Pass 3: Target Specific Parsers
- Read `audit-pass-2.md`
- Identify the specific tools/parsers that keep flagging issues
- Understand the parser's expectations
- Make surgical fixes that satisfy the parser
- Save remaining issues to `audit-pass-3.md`

### Pass 4+: Pivot to Creative Solutions
- If standard approaches exhausted, consider:
  - Refactoring to avoid the pattern entirely
  - Documenting as intentional (with justification)
  - Proposing alternative approaches
- Continue until 100% addressed or honest "cannot fix"

## Audit Types

| Type | Pass 1 Focus | Pass 2 Pattern | Pass 3 Target |
|------|--------------|----------------|---------------|
| `security` | OWASP checks | Injection patterns | Specific CVEs |
| `code-quality` | Linter rules | Complexity hotspots | Style guides |
| `compliance` | Policy docs | Gap analysis | Specific controls |
| `performance` | Profiling | Bottleneck patterns | Algorithm fixes |
| `accessibility` | WCAG checks | Component patterns | Screen readers |

## Output Format

After all passes, produce:

```markdown
# Audit Report: [target] - [type]

## Summary
- Total issues found: N
- Fixed: X (Y%)
- Acknowledged: Z
- Needs human: W

## Pass-by-Pass Progress
### Pass 1: [findings]
### Pass 2: [pattern analysis]
### Pass 3: [targeted fixes]

## Remaining Issues
[List with justification for each]

## Recommendations
[Structural changes to prevent recurrence]
```

## Why This Works

- **Fresh eyes each pass**: Different focus reveals different issues
- **Pattern recognition**: Failures cluster; fixing the pattern fixes many
- **Diminishing returns awareness**: Know when to stop vs when to pivot
- **Honest accounting**: Track what's fixed vs acknowledged vs stuck
