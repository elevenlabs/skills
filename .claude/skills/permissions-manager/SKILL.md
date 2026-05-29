---
name: permissions-manager
description: Manage skill and agent permissions, tool access control, and directory-level authorization. Define which agents can access which skills, tools, and file paths.
when_to_use: When user needs to configure permissions, restrict tool access, define skill visibility, or set up access control for agents.
disable-model-invocation: true
license: MIT
compatibility: Works with Claude Code settings.json and skill frontmatter.
---

# Permissions Manager

Control skill visibility, tool access, and directory authorization for agents.

## Permission Layers

```
┌─────────────────────────────────────────────────┐
│  Layer 4: Skill-Level Permissions               │
│  (allowed-tools, disallowed-tools in SKILL.md)  │
├─────────────────────────────────────────────────┤
│  Layer 3: Agent-Level Permissions               │
│  (tools defined in agent config)                │
├─────────────────────────────────────────────────┤
│  Layer 2: Project-Level Permissions             │
│  (.claude/settings.json)                        │
├─────────────────────────────────────────────────┤
│  Layer 1: User-Level Permissions                │
│  (~/.claude/settings.json)                      │
└─────────────────────────────────────────────────┘

Resolution: Lower layers can RESTRICT, never EXPAND
```

## Usage

```
/permissions-manager audit
/permissions-manager grant [agent] [permission]
/permissions-manager revoke [agent] [permission]
/permissions-manager show [agent|skill]
```

## Instructions

### `audit`

Generate permissions audit report:

```markdown
# Permissions Audit Report

## Tool Permissions by Layer

### User Level (~/.claude/settings.json)
| Tool | Status |
|------|--------|
| Bash | Allowed with patterns |
| Edit | Allowed |
| Write | Allowed |
| Agent | Allowed |

### Project Level (.claude/settings.json)
| Tool | Status |
|------|--------|
| Bash(rm -rf *) | DENIED |
| Bash(git push --force) | DENIED |

### Active Skills
| Skill | Allowed Tools | Disallowed Tools |
|-------|---------------|------------------|
| ralph-loop | Bash, Agent | - |
| crm-hygiene | Bash, Agent | - |
| pre-call-brief | WebSearch, Read | Edit, Write |

## Directory Access

| Path | Read | Write | Execute |
|------|------|-------|---------|
| src/ | ✓ | ✓ | - |
| .env | ✗ | ✗ | - |
| node_modules/ | ✓ | ✗ | - |

## Recommendations
- [⚠] Consider restricting Bash patterns further
- [✓] Sensitive files properly excluded
```

### `grant [agent] [permission]`

Add permission to agent or skill:

```bash
# Grant tool access to skill
# Adds to allowed-tools in SKILL.md frontmatter
```

```yaml
# Before
allowed-tools: Read Grep

# After: /permissions-manager grant my-skill "Bash(git *)"
allowed-tools: Read Grep Bash(git *)
```

### `revoke [agent] [permission]`

Remove or block permission:

```yaml
# Add to disallowed-tools in SKILL.md
disallowed-tools: Bash(rm *) Write
```

### `show [agent|skill]`

Display effective permissions:

```markdown
# Effective Permissions: crm-hygiene

## Inherited (from settings)
- Read: ✓
- Edit: ✓ (with confirmation)
- Bash: ✓ (with patterns)

## Skill-Specific
- Allowed: Bash, Agent
- Disallowed: None

## Effective Access
| Tool | Status | Source |
|------|--------|--------|
| Read | ✓ Allowed | inherited |
| Edit | ✓ Allowed | inherited |
| Write | ✓ Allowed | inherited |
| Bash | ✓ Auto-allowed | skill:allowed-tools |
| Agent | ✓ Auto-allowed | skill:allowed-tools |
| WebSearch | ○ Prompt | inherited |
```

## Skill Directory Access Control

Define which skills are visible to which agents:

```yaml
# .claude/settings.json
{
  "skillOverrides": {
    "deploy-production": "off",           // Hidden from all
    "internal-tools": "user-invocable-only", // User only, not Claude
    "code-patterns": "name-only"          // Listed but no description
  }
}
```

| Override Value | Listed to Claude | In /skills menu |
|----------------|------------------|-----------------|
| `"on"` (default) | Name + description | Yes |
| `"name-only"` | Name only | Yes |
| `"user-invocable-only"` | Hidden | Yes |
| `"off"` | Hidden | Hidden |

## Tool Permission Patterns

### Bash Patterns

```yaml
# Allow specific commands
allowed-tools:
  - Bash(git *)           # All git commands
  - Bash(npm run *)       # npm scripts
  - Bash(pytest *)        # Python tests

# Deny dangerous patterns
# In .claude/settings.json
{
  "permissions": {
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force *)",
      "Bash(chmod 777 *)",
      "Bash(curl * | bash)"
    ]
  }
}
```

### File Path Restrictions

```yaml
# In skill frontmatter
paths:
  - "src/**/*.ts"         # Only TypeScript in src
  - "!src/secrets/**"     # Exclude secrets directory
  - "tests/**"            # Test files
```

## Agent Permission Inheritance

```
User Settings (base)
       │
       ▼
Project Settings (can restrict)
       │
       ▼
Agent Config (can restrict further)
       │
       ▼
Skill Frontmatter (can restrict or auto-allow)
       │
       ▼
Effective Permissions
```

### Example: Restricted Research Agent

```yaml
# .claude/agents/research-agent.yaml
name: research-agent
description: Read-only research agent
tools:
  - Read
  - Grep
  - Glob
  - WebSearch
denied_tools:
  - Edit
  - Write
  - Bash
  - Agent
paths:
  - "**/*.md"
  - "**/*.txt"
  - "docs/**"
```

## Security Best Practices

### 1. Principle of Least Privilege
```yaml
# Start with minimal permissions, add as needed
allowed-tools: Read
# NOT: allowed-tools: *
```

### 2. Explicit Denials for Dangerous Operations
```yaml
disallowed-tools:
  - Bash(rm *)
  - Bash(> /dev/*)
  - Write(*.env)
  - Write(*credentials*)
```

### 3. Path-Based Restrictions
```yaml
paths:
  - "src/**"
  - "!src/secrets/**"
  - "!**/*.key"
  - "!**/*.pem"
```

### 4. Agent Isolation
```yaml
# Research agents: read-only
# Execute agents: scoped to task directories
# Deploy agents: explicit approval required
```

## Permission Resolution Example

```
Query: Can "deploy-skill" use Bash(git push)?

1. Check user settings: Bash allowed with patterns ✓
2. Check project settings: No explicit deny ✓
3. Check agent config: Has Bash access ✓
4. Check skill frontmatter: 
   - allowed-tools: Bash(git *)  ✓
   
Result: ALLOWED (auto-approved via skill)
```

```
Query: Can "deploy-skill" use Bash(rm -rf /)?

1. Check user settings: Bash allowed ✓
2. Check project settings: Bash(rm -rf *) DENIED ✗

Result: DENIED (blocked at project level)
```
