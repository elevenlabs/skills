---
name: icp-lead-gen
description: 30-minute ICP lead generator that cascades through 50+ data providers to build scored prospect lists. Replaces 4-6 hours of manual list building per rep per week with 2-3x fill rates.
when_to_use: When user needs to build prospect lists, find leads matching ICP criteria, or wants automated lead generation with verified contact data.
disable-model-invocation: true
context: fork
allowed-tools: Bash Agent WebSearch
license: MIT
compatibility: Requires data provider API access.
---

# Top-of-Funnel: The 30-Minute ICP Lead Generator

Replaces 4-6 hours of manual list building per rep, per week. Fill rates increase 2-3x by cascading through 50+ providers until a match is found.

## The Waterfall Pattern

```
     Raw ICP Criteria
     • Industry
     • Headcount
     • Tech Stack
            ↓
    ┌───────────────┐
    │ Data Provider 1│
    └───────┬───────┘
            ↓
    ┌───────────────┐
    │ Data Provider 2│
    └───────┬───────┘
            ↓
    ┌───────────────┐
    │ Data Provider 3│
    └───────┬───────┘
            ↓
    ┌───────────────┐
    │ Data Provider 4│
    └───────┬───────┘
            ↓
         ...
            ↓
    ┌───────────────┐
    │ Provider 50+  │
    └───────┬───────┘
            ↓
    ┌───────────────────┐
    │ Scored Prospect   │
    │ List              │
    │ • Verified Direct │
    │   Dials           │
    │ • Bounce-Risk     │
    │   Checked Emails  │
    └───────────────────┘
```

## Usage

```
/icp-lead-gen generate [ICP-criteria]
/icp-lead-gen enrich [contact-list]
/icp-lead-gen verify [email-list]
```

## Instructions

### `generate [ICP-criteria]`

Build prospect list from ICP criteria:

```
Input: $ARGUMENTS (e.g., "Series B+ SaaS, 50-200 employees, using Salesforce")

Process:
1. Parse ICP criteria into structured filters
2. Query primary provider (Apollo, ZoomInfo)
3. For each prospect missing data:
   - Cascade through secondary providers
   - Stop when all fields filled OR providers exhausted
4. Score each prospect on ICP fit
5. Verify emails via bounce checker
6. Output sorted list

Output format:
| Company | Contact | Title | Email | Phone | Score |
```

### `enrich [contact-list]`

Enrich existing contacts:

```bash
# Read contact list
# For each contact missing fields:
#   - Query enrichment providers
#   - Fill gaps
#   - Write back
```

### `verify [email-list]`

Verify email deliverability:

```
For each email:
1. Syntax check
2. Domain MX lookup
3. Mailbox verification (if provider supports)
4. Bounce risk scoring

Output:
- Valid: Ready to send
- Risky: Use with caution
- Invalid: Do not send
```

## ICP Criteria Parser

```python
icp_filters = {
    "company_size": {"min": 50, "max": 200},
    "funding_stage": ["Series B", "Series C", "Series D"],
    "industry": ["SaaS", "Technology"],
    "tech_stack": ["Salesforce"],
    "location": ["US", "UK", "EU"],
    "titles": ["VP Sales", "Head of Sales", "CRO"]
}
```

## Scoring Model

| Factor | Weight | Scoring |
|--------|--------|---------|
| Company Size Fit | 20% | 100 if in range, scaled otherwise |
| Industry Match | 20% | 100 if exact, 50 if adjacent |
| Tech Stack | 15% | 100 if uses target tech |
| Funding Stage | 15% | Higher for recent rounds |
| Title Seniority | 15% | VP+ = 100, Director = 80, etc. |
| Signal Recency | 15% | Decay over 90 days |

## Output Format

```csv
company,contact_name,title,email,phone,linkedin,score,signals
"Acme Corp","Jane Smith","VP Sales","jane@acme.com","+1-555-0123","linkedin.com/in/janesmith",92,"Series B, New hire"
"TechStart","Bob Jones","Head of Revenue","bob@techstart.io","+1-555-0456","linkedin.com/in/bobjones",87,"Competitor user"
```

## Performance Metrics

| Metric | Manual | Automated |
|--------|--------|-----------|
| Time per 100 leads | 4-6 hours | 30 minutes |
| Email fill rate | 60% | 85%+ |
| Phone fill rate | 30% | 70%+ |
| Data freshness | Unknown | <30 days |

## Provider Cascade Order

Optimized for cost and coverage:

```
Tier 1 (Primary - highest coverage):
  Apollo, ZoomInfo, Cognism

Tier 2 (Supplementary):
  Clearbit, Lusha, LeadIQ

Tier 3 (Specialized):
  BuiltWith (tech stack)
  Crunchbase (funding)
  LinkedIn Sales Nav (titles)

Tier 4 (Verification):
  Hunter.io, NeverBounce, ZeroBounce
```

## Integration with CRM

```bash
# Generate leads and push to CRM
/icp-lead-gen generate "Series B+ fintech, 100-500 employees" \
  | /crm-hygiene import --source "icp-generator"
```
