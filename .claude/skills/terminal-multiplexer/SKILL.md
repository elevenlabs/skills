---
name: terminal-multiplexer
description: Set up persistent terminal sessions with tmux or Zellij for long-running agent operations. Use when you need sessions that survive SSH disconnects, network drops, or laptop closure.
when_to_use: When user mentions tmux, zellij, screen, persistent sessions, or needs agents to run for 9+ hours unattended.
disable-model-invocation: true
allowed-tools: Bash
license: MIT
compatibility: Requires tmux or Zellij installed.
---

# Terminal Multiplexer Setup

AI agents operating for 9+ hours inevitably face network drops or timeouts. Terminal Multiplexers detach the session from the network state, ensuring the agent keeps running when you close your laptop.

## The Persistence Problem

```
[Network cables] --> [Session Restored] --> [Server rack]
                           |
                    The agent keeps
                    running after
                    SSH disconnect
```

## Terminal Multiplexer Showdown

| Feature | tmux | Zellij | GNU Screen |
|---------|------|--------|------------|
| **Memory** | ~6MB per session | ~80MB per session | Low |
| **Architecture** | C, Unix sockets | Rust, WebAssembly | Classic 1980s foundation |
| **Learning Curve** | Steep (2-4 weeks) | Immediate (floating panes) | Moderate (Ctrl+A prefix) |
| **Best For** | Production servers & plugins | Modern UX & fast productivity | Legacy environments |

## Quick Setup

### tmux (Recommended for servers)

```bash
# Install
brew install tmux  # macOS
apt install tmux   # Ubuntu

# Start named session
tmux new -s agent-session

# Detach (keeps running): Ctrl+B, then D

# Reattach
tmux attach -t agent-session

# List sessions
tmux ls
```

### Zellij (Recommended for development)

```bash
# Install
brew install zellij  # macOS
cargo install zellij # From source

# Start session
zellij

# Detach: Ctrl+O, then D

# Reattach
zellij attach
```

## Agent Session Pattern

```bash
# 1. Start persistent session
tmux new -s claude-agent

# 2. Run your agent inside
claude --continue

# 3. Detach when needed (Ctrl+B, D)
# Session continues running!

# 4. Reattach from anywhere
ssh your-server
tmux attach -t claude-agent
```

## The Aha Moment

```
[Multiplexer] + [/goal Loop] + [Cognitive Graph]
                    =
           The Tireless Engineer
```

**Autonomy without Memory is just a fast loop.**
**Memory without Autonomy is just a database.**

By fusing persistence, strict XML protocols, autonomous stop-hooks, and a self-pruning memory graph, you transition from chatting with an AI to deploying an engineer that runs unattended, remembers its mistakes, and pushes to production.

## tmux Configuration for Agents

Create `~/.tmux.conf`:

```bash
# Increase history
set -g history-limit 50000

# Enable mouse
set -g mouse on

# Status bar with session info
set -g status-right "Session: #S | %H:%M"

# Auto-save session state
set -g @plugin 'tmux-plugins/tmux-resurrect'
set -g @plugin 'tmux-plugins/tmux-continuum'
set -g @continuum-restore 'on'
```

## Usage

```
/terminal-multiplexer setup tmux
/terminal-multiplexer setup zellij
/terminal-multiplexer status
```

## Instructions

### `setup [tmux|zellij]`

1. Check if multiplexer is installed
2. Create optimal configuration for agent work
3. Create named session for agent
4. Provide attach/detach instructions

### `status`

1. List all active sessions
2. Show which have running processes
3. Report memory usage per session

## Managing Background Agents

```bash
# Run agent with /goal in background
tmux new -d -s buying-signals 'claude "/goal Monitor Buying Signals"'
tmux new -d -s crm-hygiene 'claude "/goal Background CRM Hygiene"'

# Live Event Stream
tmux attach -t buying-signals
# [09:14:02] Success: Alert pushed to Slack
# [09:14:45] Success: Record updated in Salesforce
# [09:15:12] Processing: Waterfall enrichment on 14 contacts...
```

## The 2026 Blueprint OS Layer

| Layer | Component |
|-------|-----------|
| Output | Deployed Skills (MCP, B2B Pipelines, Vercel) |
| Cognition | Episodic Vector Store & Semantic Graph |
| Engine | /goal - Autonomous Loops & Stop Hooks |
| Protocol | XML Tag Cognitive Boundaries |
| **OS** | **tmux / Zellij - Persistence & Git Worktrees** |
