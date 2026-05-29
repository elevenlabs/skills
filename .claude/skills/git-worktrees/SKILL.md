---
name: git-worktrees
description: Use git worktrees for filesystem-level parallelism in agentic workflows. Allows multiple agents to work on separate branches without git conflicts or corrupted builds.
when_to_use: When running parallel agent tasks, need to work on multiple branches simultaneously, or experiencing git conflicts from concurrent operations.
disable-model-invocation: true
allowed-tools: Bash(git *)
license: MIT
compatibility: Requires git 2.5+.
---

# Git Worktrees for Agentic Parallelism

Git worktrees provide filesystem-level parallelism. They allow agentic coding tools to operate concurrently on separate branches without sharing a mutable working directory.

## The Problem: Mutable State Collision

```
Multiple agents
writing to same repo
        |
        v
       [X]
        |
  Git conflicts &
  corrupted builds
```

## The Solution: Filesystem Parallelism

```
Agent A          Agent B          Agent C
   |                |                |
   v                v                v
[Git Worktree A] [Git Worktree B] [Git Worktree C]
   |                |                |
   +----------------+----------------+
                    |
                   [✓]
            No conflicts!
```

## Quick Start

```bash
# Create worktree for a feature
git worktree add ../feature-auth feature/auth

# Create worktree for a new branch
git worktree add -b feature/payments ../feature-payments

# List all worktrees
git worktree list

# Remove when done
git worktree remove ../feature-auth
```

## Directory Structure

```
projects/
├── main-repo/           # Main worktree (main branch)
│   ├── .git/            # Shared git directory
│   └── src/
├── feature-auth/        # Worktree (feature/auth branch)
│   └── src/
├── feature-payments/    # Worktree (feature/payments branch)
│   └── src/
└── hotfix-prod/         # Worktree (hotfix/prod branch)
    └── src/
```

## Parallel Agent Pattern

```bash
# Terminal 1: Agent working on auth
cd ~/projects/feature-auth
claude "Implement OAuth2 flow"

# Terminal 2: Agent working on payments
cd ~/projects/feature-payments
claude "Add Stripe integration"

# Terminal 3: Agent fixing production bug
cd ~/projects/hotfix-prod
claude "Fix the memory leak in the worker"

# All three run simultaneously, no conflicts!
```

## Usage

```
/git-worktrees create feature/my-feature
/git-worktrees list
/git-worktrees remove feature/my-feature
/git-worktrees setup-parallel 3
```

## Instructions

### `create [branch-name]`

```bash
# Derive worktree path from branch name
WORKTREE_PATH="../$(echo $BRANCH | tr '/' '-')"

# Create worktree
git worktree add "$WORKTREE_PATH" -b "$BRANCH" 2>/dev/null \
  || git worktree add "$WORKTREE_PATH" "$BRANCH"

echo "Worktree created at: $WORKTREE_PATH"
echo "To work in it: cd $WORKTREE_PATH"
```

### `list`

```bash
git worktree list --porcelain | while read line; do
  case "$line" in
    worktree*) echo "📁 ${line#worktree }" ;;
    branch*) echo "   Branch: ${line#branch refs/heads/}" ;;
  esac
done
```

### `remove [branch-name]`

```bash
WORKTREE_PATH="../$(echo $BRANCH | tr '/' '-')"
git worktree remove "$WORKTREE_PATH"
echo "Removed worktree: $WORKTREE_PATH"
```

### `setup-parallel [count]`

Create N worktrees for parallel agent work:

```bash
for i in $(seq 1 $COUNT); do
  git worktree add "../agent-workspace-$i" -b "agent/task-$i"
done
echo "Created $COUNT parallel workspaces"
```

## Best Practices

1. **Naming convention**: Use branch name as worktree directory
2. **Cleanup**: Remove worktrees when branches are merged
3. **Isolation**: Each agent gets its own worktree
4. **Shared history**: All worktrees share the same git history

## Integration with Terminal Multiplexers

```bash
# Create worktrees and tmux sessions together
for task in auth payments reporting; do
  git worktree add "../feature-$task" -b "feature/$task"
  tmux new-session -d -s "$task" -c "../feature-$task"
done

# Now you have 3 isolated agent workspaces running in parallel
tmux ls
# auth: 1 windows
# payments: 1 windows  
# reporting: 1 windows
```

## The Mutable State Rule

**Never let multiple agents write to the same working directory.**

Git worktrees enforce this at the filesystem level—each branch gets its own complete checkout. The agents can run builds, install dependencies, and modify files without stepping on each other.
