---
name: agent-hierarchy
description: Define and manage agent hierarchies with parent-child relationships, delegation rules, and task escalation paths. Use when orchestrating multiple agents, defining agent roles, or establishing chain of command for complex workflows.
when_to_use: When user needs to set up multi-agent systems, define agent roles, establish delegation patterns, or create agent orchestration workflows.
disable-model-invocation: true
license: MIT
compatibility: Works with Claude Code subagents and the Agent tool.
---

# Agent Hierarchy & Orchestration

Define agent roles, delegation rules, and communication patterns for multi-agent workflows.

## The Hierarchy Model

```
                    ┌─────────────────┐
                    │  Orchestrator   │
                    │  (Parent Agent) │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │  Explore    │   │    Plan     │   │  Execute    │
    │  Agent      │   │   Agent     │   │   Agent     │
    └─────────────┘   └─────────────┘   └─────────────┘
           │                 │                 │
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │  Specialist │   │  Specialist │   │  Specialist │
    │  Subagents  │   │  Subagents  │   │  Subagents  │
    └─────────────┘   └─────────────┘   └─────────────┘
```

## Agent Roles

| Role | Responsibility | Tools | Delegation |
|------|----------------|-------|------------|
| **Orchestrator** | Task decomposition, coordination | Agent, AskUserQuestion | Can spawn all agent types |
| **Explore** | Read-only research, code search | Read, Grep, Glob | Cannot spawn agents |
| **Plan** | Architecture, design decisions | Read, Grep, WebSearch | Can spawn Explore |
| **Execute** | Code changes, file operations | Read, Edit, Write, Bash | Can spawn Explore |
| **Specialist** | Domain-specific tasks | Varies by domain | Limited delegation |

## Usage

```
/agent-hierarchy define [workflow-name]
/agent-hierarchy visualize
/agent-hierarchy validate
```

## Instructions

### `define [workflow-name]`

Create agent hierarchy configuration:

```yaml
# .claude/agents/[workflow-name].yaml
name: $ARGUMENTS
version: 1.0

hierarchy:
  orchestrator:
    role: "Coordinate multi-step task completion"
    can_spawn:
      - explore
      - plan
      - execute
    escalate_to: user
    
  explore:
    role: "Research and gather information"
    tools: [Read, Grep, Glob, WebSearch]
    can_spawn: []
    reports_to: orchestrator
    
  plan:
    role: "Design solutions and architectures"
    tools: [Read, Grep, WebSearch, Agent]
    can_spawn: [explore]
    reports_to: orchestrator
    
  execute:
    role: "Implement changes and run commands"
    tools: [Read, Edit, Write, Bash, Agent]
    can_spawn: [explore]
    reports_to: orchestrator

communication:
  protocol: structured_handoff
  format: xml
  require_summary: true
  
escalation:
  triggers:
    - "requires user decision"
    - "scope exceeds authorization"
    - "conflicting requirements"
  path: agent -> orchestrator -> user
```

### `visualize`

Generate hierarchy diagram:

```
Current Agent Hierarchy
=======================

[User]
   │
   └── [Orchestrator: main]
          │
          ├── [Explore: research-a] ──► Read-only
          │      └── Status: completed
          │
          ├── [Plan: architecture] ──► Design
          │      └── [Explore: patterns] ──► Read-only
          │
          └── [Execute: implement] ──► Full access
                 └── [Explore: verify] ──► Read-only

Legend:
  ──► : Delegation relationship
  Read-only: No write permissions
  Design: Read + WebSearch
  Full access: All tools
```

### `validate`

Check hierarchy for issues:

```markdown
# Hierarchy Validation Report

## Structure
- [✓] All agents have defined roles
- [✓] No circular dependencies
- [✓] Escalation paths defined

## Permissions
- [✓] Explore agents are read-only
- [✓] Execute agents have write access
- [⚠] Plan agent can spawn Execute (review needed)

## Communication
- [✓] All agents report to parent
- [✓] Handoff format defined
- [✓] Summary requirements set

## Recommendations
- Consider restricting Plan->Execute spawning
- Add timeout for long-running agents
```

## Delegation Rules

### The Principle of Least Privilege

```
Rule 1: Agents inherit permissions from parent, never exceed
Rule 2: Read-only agents cannot spawn write-capable agents
Rule 3: Specialist agents have narrow, defined scope
Rule 4: Only orchestrator can escalate to user
```

### Spawn Authorization Matrix

| Parent | Can Spawn | Cannot Spawn |
|--------|-----------|--------------|
| Orchestrator | Explore, Plan, Execute | - |
| Plan | Explore | Execute |
| Execute | Explore | Plan |
| Explore | - | Any |

## Task Handoff Protocol

When delegating to a subagent:

```xml
<task_handoff>
  <from>orchestrator</from>
  <to>execute</to>
  <task_id>task-001</task_id>
  
  <context>
    <objective>Implement authentication module</objective>
    <constraints>
      - Use existing auth patterns from src/auth/
      - No new dependencies without approval
      - Must pass existing tests
    </constraints>
    <resources>
      - Design doc: docs/auth-design.md
      - Reference: src/auth/existing.ts
    </resources>
  </context>
  
  <deliverables>
    - Implemented auth module
    - Updated tests
    - Summary of changes
  </deliverables>
  
  <escalation_triggers>
    - New dependency required
    - Design ambiguity
    - Test failures not resolvable
  </escalation_triggers>
</task_handoff>
```

## Completion Report Protocol

When returning to parent:

```xml
<task_completion>
  <task_id>task-001</task_id>
  <agent>execute</agent>
  <status>completed|blocked|escalated</status>
  
  <summary>
    Implemented JWT-based authentication with refresh tokens.
    Added 12 tests, all passing.
  </summary>
  
  <changes>
    - src/auth/jwt.ts (new)
    - src/auth/refresh.ts (new)
    - tests/auth.test.ts (modified)
  </changes>
  
  <blockers></blockers>
  
  <recommendations>
    Consider adding rate limiting in follow-up task.
  </recommendations>
</task_completion>
```

## Built-in Agent Types

Claude Code provides these agent types:

| Type | Purpose | Default Tools |
|------|---------|---------------|
| `claude` | General purpose | All tools |
| `Explore` | Read-only research | Read, Grep, Glob, WebSearch |
| `Plan` | Architecture design | Read, Grep, WebSearch |
| `general-purpose` | Flexible execution | All tools |

## Custom Agent Definition

```yaml
# .claude/agents/security-reviewer.yaml
name: security-reviewer
description: Review code for security vulnerabilities
tools:
  - Read
  - Grep
  - Glob
can_spawn: []
permissions:
  write: false
  execute: false
  network: false
```
