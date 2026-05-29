---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
when_to_use: When user asks to create a skill, write a SKILL.md, build a custom command, wants help with skill development, needs to run evals, or wants to benchmark performance.
disable-model-invocation: true
license: MIT
compatibility: Works with Claude Code CLI, web, and IDE extensions. No external dependencies.
---

# Skill Creator

Facilitates creation, modification, optimization, and evaluation of skills.

## Overview

- Use for new skill creation, edits, optimizations, or performance measurement
- Support evals, benchmarking with variance analysis, and trigger accuracy improvements
- Follow init, validate, and iteration processes for robust skill development
- Ensure skills are concise, trigger-accurate, and add real value

## Skill Structure

Skills live in directories with a `SKILL.md` entrypoint:

```
my-skill/
├── SKILL.md           # Main instructions (required)
├── references/        # Detailed docs Claude loads on demand
├── scripts/           # Executable scripts
└── examples/          # Example outputs
```

## SKILL.md Format

Every skill needs YAML frontmatter between `---` markers, followed by markdown instructions:

```yaml
---
name: my-skill
description: What this skill does and when to use it. Put the key use case first.
when_to_use: Additional trigger phrases or example requests.
argument-hint: [optional-args]
disable-model-invocation: true  # Only user can invoke
allowed-tools: Bash(git *) Read  # Pre-approved tools
context: fork  # Run in subagent
agent: Explore  # Which subagent type
model: sonnet  # Model override
effort: high   # Reasoning effort
---

Instructions Claude follows when the skill runs...
```

### Required Fields

- `description`: What it does and when to use it. Claude uses this to decide when to load the skill automatically.

### Optional Fields

| Field | Purpose |
|-------|---------|
| `name` | Display name (defaults to directory name) |
| `when_to_use` | Additional context for auto-invocation |
| `argument-hint` | Shown during autocomplete (e.g., `[filename]`) |
| `arguments` | Named positional args for `$name` substitution |
| `disable-model-invocation` | `true` = only user can invoke |
| `user-invocable` | `false` = only Claude can invoke |
| `allowed-tools` | Tools Claude can use without permission |
| `disallowed-tools` | Tools blocked while skill is active |
| `context` | `fork` to run in isolated subagent |
| `agent` | Subagent type when `context: fork` |
| `model` | Model override for this skill |
| `effort` | Reasoning effort: low/medium/high/xhigh/max |
| `paths` | Glob patterns limiting when skill activates |
| `shell` | `bash` (default) or `powershell` |

## Writing Effective Descriptions

Descriptions determine when Claude auto-invokes the skill. Write them to be specific and "pushy":

**Bad**: "Helps with deployments"
**Good**: "Deploy the application to production. Use when the user mentions deploying, shipping, releasing, or pushing to prod."

Put the key use case first - combined `description` and `when_to_use` truncate at 1,536 chars.

## String Substitutions

| Variable | Expands to |
|----------|------------|
| `$ARGUMENTS` | All arguments passed to skill |
| `$ARGUMENTS[N]` or `$N` | Specific argument by index (0-based) |
| `$name` | Named argument from `arguments` frontmatter |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_EFFORT}` | Current effort level |
| `${CLAUDE_SKILL_DIR}` | Directory containing SKILL.md |

## Dynamic Context Injection

Run shell commands before Claude sees the content:

```markdown
## Current state
!`git status --short`

## Recent commits
!`git log --oneline -5`
```

For multi-line commands:
````markdown
```!
node --version
npm --version
```
````

## Skill Types

### Reference Skills
Add knowledge Claude applies to current work:
```yaml
---
description: API design patterns for this codebase
---

When writing API endpoints:
- Use RESTful naming
- Return consistent error formats
```

### Task Skills
Step-by-step instructions for specific actions:
```yaml
---
description: Deploy the application
disable-model-invocation: true
context: fork
---

Deploy steps:
1. Run tests
2. Build
3. Push to target
```

## Creating a New Skill

1. **Identify the pattern**: What instructions do you keep repeating?

2. **Choose location**:
   - `~/.claude/skills/` - Personal, all projects
   - `.claude/skills/` - Project-specific
   - Plugin `skills/` - Distributed with plugin

3. **Write SKILL.md**:
   - Start with a clear, specific description
   - Keep instructions concise - they stay in context
   - Reference supporting files for detailed docs

4. **Test the skill**:
   - Invoke directly with `/skill-name`
   - Check it triggers on expected phrases
   - Verify it doesn't over-trigger

5. **Iterate**:
   - Refine description if undertriggering
   - Add `disable-model-invocation` if overtriggering
   - Move verbose content to references/

## Example: Git Commit Skill

```yaml
---
name: commit
description: Stage and commit changes with a good message. Use when user wants to commit, save changes, or create a checkpoint.
disable-model-invocation: true
allowed-tools: Bash(git *)
argument-hint: [message]
---

## Current changes
!`git diff --stat`

## Instructions

1. Review the diff above
2. Stage appropriate files (prefer specific files over `git add -A`)
3. Write a commit message that explains WHY, not just what
4. Create the commit

If `$ARGUMENTS` provided, use it as the commit message.
```

## Troubleshooting

**Skill not triggering**: Add more trigger phrases to description, check `/skills` menu

**Triggers too often**: Make description more specific, add `disable-model-invocation: true`

**Content too long**: Move reference material to separate files, keep SKILL.md under 500 lines

## References

- [Claude Code Skills Docs](https://code.claude.com/docs/en/skills)
- [Agent Skills Spec](https://agentskills.io)
