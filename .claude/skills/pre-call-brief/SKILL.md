---
name: pre-call-brief
description: Automated 2-minute pre-call brief that runs via API trigger when a Calendly meeting is booked. Delivers formatted talking points directly to the AE's Slack with company overview, sales signals, and personalization hooks.
when_to_use: When user has a sales call coming up, needs quick prospect research, or wants to automate pre-call preparation.
disable-model-invocation: true
context: fork
allowed-tools: WebSearch Read Agent
license: MIT
compatibility: Can integrate with Calendly, Slack, and CRM APIs.
---

# Mid-Funnel: The Automated 2-Minute Pre-Call Brief

Runs automatically via API trigger when a Calendly meeting is booked. Delivers a formatted brief detailing exact talking points directly to the AE's Slack.

## Sample Output

```
┌─────────────────────────────────────────────┐
│ # Message                                    │
│ ──────────────────────────────────────────── │
│                                              │
│ Claude Sales Agent                    8:55 AM│
│                                              │
│ 1. Company Overview & Recent News            │
│    • Launched Hyper network for IoT on Feb 26│
│                                              │
│ 2. Sales Signals                             │
│    • Active on G2 responding to negative     │
│      reviews                                 │
│                                              │
│ 3. Personalization Hooks                     │
│    • Reference their recent AWS IoT Core     │
│      partnership                             │
│                                              │
└─────────────────────────────────────────────┘
```

## Usage

```
/pre-call-brief [company-name]
/pre-call-brief [meeting-link]
/pre-call-brief setup-automation
```

## Instructions

### `[company-name]`

Generate pre-call brief:

```markdown
# Pre-Call Brief: [Company]
Generated: [timestamp]
Meeting: [time if available]

## 1. Company Overview & Recent News
- **Founded**: [year]
- **Size**: [employees]
- **Funding**: [stage, amount]
- **Recent News**:
  - [News item 1]
  - [News item 2]

## 2. Sales Signals
- **Buying Intent**: [High/Medium/Low]
- **Signals Detected**:
  - [Signal 1 with context]
  - [Signal 2 with context]
- **Tech Stack**: [Relevant tools]

## 3. Personalization Hooks
- [Hook 1: Recent achievement or post]
- [Hook 2: Shared connection or interest]
- [Hook 3: Pain point mentioned publicly]

## 4. Suggested Talk Track
**Opening**: "[Personalized opener referencing hook]"
**Discovery**: Ask about [specific challenge]
**Value Prop**: Focus on [most relevant benefit]

## 5. Potential Objections
- [Likely objection]: [Prepared response]

## 6. Competitive Intel
- **Current tools**: [What they use]
- **Differentiation**: [Why we're better for them]

---
Sources: LinkedIn, Crunchbase, G2, Company blog
Research time: 2 minutes
```

### `[meeting-link]`

Parse meeting details and generate brief:

```
1. Extract company/contact from meeting invite
2. Cross-reference with CRM data
3. Run full research
4. Generate brief
5. Post to Slack channel
```

### `setup-automation`

Configure automated brief generation:

```yaml
# .claude/pre-call-config.yaml
trigger:
  type: calendly_webhook
  event: meeting_scheduled

filters:
  - meeting_type: "Discovery Call"
  - meeting_type: "Demo"

output:
  destination: slack
  channel: "#sales-briefs"
  mention: "@{rep_slack_id}"

research_depth:
  company_news: 3 months
  linkedin_posts: 5 recent
  g2_reviews: 10 recent
```

## The Automation Flow

```
Calendly Meeting    →    API Trigger    →    Claude Agent
    Booked                                   Researches
                                                 ↓
                                          Formats Brief
                                                 ↓
    Rep receives    ←    Posts to Slack  ←   2 minutes
    brief before                             later
    the call
```

## Brief Quality Checklist

- [ ] Company facts verified (not hallucinated)
- [ ] Recent news is actually recent (<3 months)
- [ ] Signals are actionable (not generic)
- [ ] Personalization hooks are specific
- [ ] Talk track matches their stage
- [ ] Objection prep is relevant

## Integration Points

```python
# Calendly webhook handler
@webhook("/calendly/meeting-created")
async def handle_meeting(event):
    company = extract_company(event.invitee_email)
    
    # Generate brief
    brief = await generate_pre_call_brief(company)
    
    # Post to Slack
    slack.post_message(
        channel=get_rep_channel(event.rep_id),
        text=brief,
        mention=event.rep_slack_id
    )
```

## Timing Optimization

| Stage | Time |
|-------|------|
| Meeting booked | T+0 |
| Brief generation | T+2 min |
| Brief delivered | T+2.5 min |
| Rep reviews | T+3 min |
| Call starts | T+30 min to T+24 hrs |

**Result**: Rep always has context, zero prep time required.

## The 30-Second Review

Rep receives brief → Scans 3 sections → Ready for call

No more:
- Tab-hopping through LinkedIn
- Searching CRM for notes
- Googling company news
- Asking "so, what do you do?" on calls
