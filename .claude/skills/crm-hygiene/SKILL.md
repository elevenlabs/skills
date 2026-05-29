---
name: crm-hygiene
description: Silent background agent that cleans CRM data - deduplicates contacts, standardizes titles, flags stale records, and enriches missing fields. Removes data entry from the sales floor permanently.
when_to_use: When user needs CRM cleanup, data hygiene, contact deduplication, or wants to automate data quality maintenance.
disable-model-invocation: true
context: fork
allowed-tools: Bash Agent
license: MIT
compatibility: Requires CRM API access (Salesforce, HubSpot, etc.) via MCP or direct integration.
---

# RevOps: The Silent CRM Hygiene Loop

Reps do not enrich records manually because it is slow. This background agent entirely removes data entry from the sales floor, cutting bad-data churn permanently.

## The Hygiene Loop

```
           Detect Missing
              Fields
                ↓
Write-back to  ←→  Waterfall Enrich
Salesforce/HubSpot    via SyncGTM
       ↑                  ↓
       ←  Deduplicate &   →
          Standardize
              Titles
                ↓
          Flag Stale Records
            (>90 Days)
```

## The Problem

| Issue | Impact |
|-------|--------|
| Missing fields | Reps waste time researching |
| Duplicate contacts | Multiple reps work same account |
| Stale records | Outreach to dead leads |
| Unstandardized titles | Broken ICP filters |

## The Solution

Run a continuous background agent that:
1. **Detects** missing critical fields
2. **Enriches** via waterfall across 50+ providers
3. **Deduplicates** contacts and accounts
4. **Standardizes** job titles to your taxonomy
5. **Flags** records with no activity >90 days
6. **Writes back** directly to CRM

## Usage

```
/crm-hygiene start
/crm-hygiene status
/crm-hygiene report
```

## Instructions

### `start`

Initialize the hygiene loop as a background /goal:

```
/goal Background CRM Hygiene

Success condition: 0 records with missing required fields
Failure condition: API rate limit exceeded OR manual review needed

Loop:
1. Query CRM for records with missing fields
2. For each record:
   - Attempt enrichment via configured providers
   - If enriched: write back to CRM
   - If not: flag for manual review
3. Run deduplication pass
4. Standardize job titles
5. Flag stale records
6. Report progress every 100 records
7. Continue until all records processed
```

### `status`

```bash
# Query current progress
echo "CRM Hygiene Status"
echo "=================="
echo "Records processed: $(sqlite3 .claude/ledger.db 'SELECT COUNT(*) FROM work_log WHERE action LIKE "crm-hygiene%"')"
echo "Enriched: $(sqlite3 .claude/ledger.db 'SELECT COUNT(*) FROM work_log WHERE action="crm-enriched"')"
echo "Deduplicated: $(sqlite3 .claude/ledger.db 'SELECT COUNT(*) FROM work_log WHERE action="crm-deduped"')"
echo "Flagged stale: $(sqlite3 .claude/ledger.db 'SELECT COUNT(*) FROM work_log WHERE action="crm-flagged-stale"')"
```

### `report`

Generate hygiene report:

```markdown
# CRM Hygiene Report

## Summary
- Total records scanned: N
- Enriched: X (Y%)
- Deduplicated: Z sets
- Stale flagged: W

## Field Coverage
| Field | Before | After |
|-------|--------|-------|
| Email | 78% | 94% |
| Phone | 45% | 82% |
| Title | 92% | 100% |

## Deduplication
- Duplicate sets found: N
- Merged into: X records
- Confidence threshold: 0.85

## Recommendations
- [High-impact gaps identified]
```

## Required Fields Matrix

| Object | Required Fields |
|--------|-----------------|
| Contact | Email, Phone, Title, Company |
| Account | Industry, Size, Website, HQ Location |
| Opportunity | Stage, Amount, Close Date, Primary Contact |

## Enrichment Waterfall

```
Raw Contact
    ↓
Data Provider 1 (Apollo)
    ↓ (if miss)
Data Provider 2 (ZoomInfo)
    ↓ (if miss)
Data Provider 3 (Clearbit)
    ↓ (if miss)
...
Provider 50+
    ↓
Scored Prospect
(Verified email, direct dial, bounce-checked)
```

**Result**: Fill rates increase 2-3x by cascading through 50+ providers until a match is found.

## Title Standardization

Map free-text titles to your ICP taxonomy:

| Raw Title | Standardized |
|-----------|--------------|
| "VP of Eng" | "VP Engineering" |
| "Head of Engineering" | "VP Engineering" |
| "Engineering Lead" | "Director Engineering" |
| "CTO / Co-founder" | "CTO" |

## Integration Pattern

```python
# MCP connection to CRM
mcp_config = {
    "enrichment_engine": "SyncGTM",
    "system_of_record": "Salesforce/HubSpot",
    "communication": "Slack/Email"
}

# The agent has secure, real-time access without manual API juggling
```

## Running in Background

```bash
# Start hygiene loop in tmux
tmux new -d -s crm-hygiene 'claude "/goal Background CRM Hygiene"'

# Monitor progress
tmux attach -t crm-hygiene

# Live output:
# [09:14:02] Processing: Waterfall enrichment on 14 contacts...
# [09:14:45] Success: Record updated in Salesforce
# [09:15:12] Success: Deduplicated 3 contact records
```
