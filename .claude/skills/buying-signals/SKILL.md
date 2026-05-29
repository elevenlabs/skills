---
name: buying-signals
description: Monitor and surface buying signals from prospects - VP-level job changes, funding rounds, tech stack additions, rapid headcount growth. Signal-based outreach converts at 3-5x the rate of cold outreach.
when_to_use: When user needs to monitor prospect signals, wants to time outreach based on buying windows, or needs a daily rep digest of hot prospects.
disable-model-invocation: true
context: fork
allowed-tools: Bash Agent WebSearch
license: MIT
compatibility: Requires data provider integrations (LinkedIn, Crunchbase, news APIs).
---

# The Buying Signal Monitor

Signal-based outreach converts at 3-5x the rate of cold outreach because the timing aligns with active buying windows. Claude surfaces these triggers as a daily rep digest.

## Signal Priority Ranking

| Priority | Signal | Why It Matters |
|----------|--------|----------------|
| **1** | VP-Level Job Changes | New leaders bring new budgets |
| **2** | Series B+ Funding Rounds | Money to spend, pressure to scale |
| **3** | Tech Stack Additions (Competitor installs) | Evaluating solutions now |
| **4** | Rapid Headcount Growth | Scaling pains = tool needs |

## The Cold Outreach Personalization Paradox

```
                    ┌─────────────────┐
                    │  Level 3:       │
                    │  Agentic Hyper- │
                    │  Personalization│
                    │  100+ genuinely │
Level 2:            │  researched     │
Manual Crafting     │  emails per day │
High personalization│                 │
terrible scale      │                 │
(Max 20 emails/day) │                 │
        ┌───────────┤                 │
        │           │                 │
        │           └─────────────────┘
        │     Level 1: The Spam Cannon
        │     High scale, generic
        │     "Hi {First_Name}" templates
        └────────────────────────────────
              Scale →
```

**Signal monitoring enables Level 3**: Genuine personalization at scale.

## Usage

```
/buying-signals start [ICP-criteria]
/buying-signals digest
/buying-signals add-source [provider]
```

## Instructions

### `start [ICP-criteria]`

Initialize signal monitoring as a background /goal:

```
/goal Monitor Buying Signals

ICP: $ARGUMENTS

Signals to track:
1. VP+ job changes at target accounts
2. Series B+ funding announcements
3. Competitor tool installations
4. Headcount growth >20% QoQ

Actions:
- On signal detection: Score prospect, push alert to Slack
- Daily: Compile digest of top signals
- Weekly: Report on signal conversion rates

Success: Continuous monitoring with <1hr signal latency
Failure: API rate limits OR data provider outage
```

### `digest`

Generate today's signal digest:

```markdown
# Buying Signals Digest - [DATE]

## Hot Prospects (Score 85+)

### 1. Acme Corp (Score: 92)
**Signal**: New VP of Engineering started 2 days ago
**Context**: Previously at [Competitor]. Likely re-evaluating tools.
**Action**: Reach out with [specific value prop]

### 2. TechStart Inc (Score: 88)
**Signal**: Series B announced ($45M)
**Context**: Expanding engineering team. Posted 12 jobs this week.
**Action**: Position around scaling challenges

## Medium Priority (Score 65-84)

### 3. DataFlow Systems (Score: 71)
**Signal**: Competitor tool detected in job postings
**Context**: Mentions [Competitor] in 3 recent job descriptions
**Action**: Competitive displacement angle

## Signal Summary
- VP Changes: 4 detected
- Funding Rounds: 2 detected
- Tech Stack: 7 detected
- Headcount: 3 companies >20% growth
```

### `add-source [provider]`

Add new signal source:

```bash
# Supported providers
PROVIDERS=(
    "linkedin-sales-nav"
    "crunchbase"
    "g2-intent"
    "builtwith"
    "zoominfo-intent"
    "bombora"
)

# Add to monitoring config
echo "$1" >> .claude/signal-sources.txt
echo "Added signal source: $1"
```

## Signal Detection Rules

```python
signals = {
    "vp_job_change": {
        "condition": "title contains VP|Director|Head AND tenure < 90 days",
        "score_boost": 25,
        "alert": True
    },
    "funding_round": {
        "condition": "series >= B AND amount >= 20M",
        "score_boost": 20,
        "alert": True
    },
    "tech_stack": {
        "condition": "competitor_tool in job_postings",
        "score_boost": 15,
        "alert": False  # Batch in digest
    },
    "headcount": {
        "condition": "growth_rate > 0.2 AND period = 'quarter'",
        "score_boost": 10,
        "alert": False
    }
}
```

## Integration with Pre-Call Brief

When a signal fires, automatically generate context:

```
Signal: VP Engineering job change at Acme Corp
    ↓
/pre-call-brief Acme Corp
    ↓
Brief delivered to rep's Slack:
- Company Overview & Recent News
- Why this signal matters
- Personalization hooks
- Suggested talk track
```

## Running in Background

```bash
# Start signal monitor
tmux new -d -s buying-signals 'claude "/goal Monitor Buying Signals"'

# Check status
tmux attach -t buying-signals
# [09:14:02] Success: Alert pushed to Slack
# [09:14:45] Detected: VP change at TargetCo
# [09:15:12] Processing: Enriching 14 new signals...
```

## ROI Metrics

| Metric | Cold Outreach | Signal-Based |
|--------|---------------|--------------|
| Reply Rate | 2-3% | 8-12% |
| Meeting Rate | 0.5% | 2-4% |
| Time to Research | 15 min/prospect | 30 seconds |
