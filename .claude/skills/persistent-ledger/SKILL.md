---
name: persistent-ledger
description: Maintain a SQLite ledger for tracking agent work across sessions. Use when you need persistent memory, work tracking, deployment pipelines, or any task requiring state that survives session restarts.
when_to_use: When user needs to track work across sessions, maintain persistent state, build deployment pipelines, or create audit trails. When "the data is on disk" matters.
disable-model-invocation: true
allowed-tools: Bash(sqlite3 *) Bash(git *)
argument-hint: [action] [details]
license: MIT
compatibility: Requires sqlite3 CLI.
---

# The Persistent Ledger

Live retest hits the file every minute. No "trust me bro" - the data is on disk.

## The Architecture

```
Truth                          Action
  |                              |
  v                              v
SQLite     -->  Local    -->  GitHub  -->  Vercel
Ledger          Codex         Push        Auto-Deploy
                Build
```

The workflow layer sits underneath the agent layer. The agent makes decisions, and the CI/CD workflow executes them reliably without the agent needing to understand deployment infrastructure.

## The Amnesia Problem

| Stateless Agents | Vector RAG | Human-Inspired Memory |
|------------------|------------|----------------------|
| Treat each interaction independently | Stores embeddings | Multi-tier storage |
| Lose all context between sessions | Treats all information equally | Offline consolidation |
| | Cannot consolidate or forget | Adaptive forgetting |
| | Leading to compounding information loss | Engram saturation |
| | | Scalable and self-governing |

**Solution**: SQLite ledger provides structured, queryable persistence.

## Usage

```
/persistent-ledger init project-name
/persistent-ledger log "Completed feature X"
/persistent-ledger status
/persistent-ledger query "SELECT * FROM work WHERE status='pending'"
```

## Schema

```sql
CREATE TABLE IF NOT EXISTS work_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT,
    action TEXT NOT NULL,
    details TEXT,
    status TEXT DEFAULT 'pending',
    outcome TEXT,
    files_changed TEXT,
    commit_sha TEXT
);

CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    goal TEXT NOT NULL,
    success_condition TEXT,
    failure_condition TEXT,
    status TEXT DEFAULT 'active',
    completed_at DATETIME
);

CREATE TABLE IF NOT EXISTS checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    state_snapshot TEXT,
    recoverable BOOLEAN DEFAULT 1
);
```

## Instructions

### `init [project-name]`
Create ledger at `.claude/ledger.db`:
```bash
sqlite3 .claude/ledger.db < schema.sql
echo "Ledger initialized for $1"
```

### `log [message]`
Record work:
```bash
sqlite3 .claude/ledger.db "INSERT INTO work_log (session_id, action, details) VALUES ('${CLAUDE_SESSION_ID}', 'log', '$ARGUMENTS')"
```

### `status`
Show current state:
```bash
sqlite3 -header -column .claude/ledger.db "
SELECT 
  (SELECT COUNT(*) FROM work_log WHERE status='pending') as pending,
  (SELECT COUNT(*) FROM work_log WHERE status='done') as done,
  (SELECT COUNT(*) FROM goals WHERE status='active') as active_goals
"
```

### `query [sql]`
Run arbitrary query:
```bash
sqlite3 -header -column .claude/ledger.db "$ARGUMENTS"
```

### `checkpoint [description]`
Save recoverable state:
```bash
sqlite3 .claude/ledger.db "INSERT INTO checkpoints (description, state_snapshot) VALUES ('$ARGUMENTS', '$(git rev-parse HEAD)')"
```

## Deployment Pipeline Integration

The ledger enables reliable deployment:

1. **Record intent**: Log what you're about to deploy
2. **Build locally**: Codex build, tests pass
3. **Push to GitHub**: Triggers CI
4. **Auto-deploy**: Vercel picks up from GitHub
5. **Record outcome**: Log success/failure with commit SHA

```bash
# Before deploy
sqlite3 .claude/ledger.db "INSERT INTO work_log (action, details, status) VALUES ('deploy', 'Deploying feature X', 'in_progress')"

# After deploy
sqlite3 .claude/ledger.db "UPDATE work_log SET status='done', outcome='success', commit_sha='$(git rev-parse HEAD)' WHERE id=(SELECT MAX(id) FROM work_log)"
```

## Recovery

When session restarts, query the ledger:

```sql
-- What was I working on?
SELECT * FROM work_log WHERE status='in_progress' ORDER BY timestamp DESC LIMIT 5;

-- What goals are active?
SELECT * FROM goals WHERE status='active';

-- Last checkpoint?
SELECT * FROM checkpoints ORDER BY timestamp DESC LIMIT 1;
```

## The 2026 Blueprint Stack

| Layer | Component |
|-------|-----------|
| Output | Deployed Skills (MCP, B2B Pipelines, Vercel) |
| Cognition | Episodic Vector Store & Semantic Graph |
| Engine | /goal - Autonomous Loops & Stop Hooks |
| Protocol | XML Tag Cognitive Boundaries |
| OS | tmux / Zellij - Persistence & Git Worktrees |

**Build the infrastructure. Define the taxonomy. Let the machine run.**
