---
name: hyper-personalization
description: 75-second hyper-personalization engine that researches prospects across LinkedIn, Crunchbase, and G2 to build 5-point dossiers. What previously took 15 minutes of tab-hopping now executes in under 2 minutes.
when_to_use: When user needs to research a prospect quickly, write personalized outreach, or prepare for a sales call with context.
disable-model-invocation: true
context: fork
allowed-tools: WebSearch Read Agent
license: MIT
compatibility: Works with web search and public data sources.
---

# The 75-Second Hyper-Personalization Engine

What previously took a rep 15 minutes of tab-hopping across LinkedIn, Crunchbase, and G2 is now executed by Claude in seconds.

## The Research Pipeline

```
1. Research          2. Draft              3. Review
   30s                  15s                   30s
    ↓                    ↓                     ↓
Claude executes    Agent synthesizes    Human-in-the-loop
web searches,      into a 120-word      validation before
extracting recent  email applying       loading into the
LinkedIn posts,    strict constraints   delivery sequence.
company news,      (no buzzwords,
and hiring         one CTA).
signals to build
a 5-point dossier.
```

## The 30-Second Human Filter

Even with autonomous agents, the human remains the final quality filter. Reviewing and tweaking an AI draft takes 30 seconds—infinitely faster than writing from a blank page.

**Quality Checklist:**
- Does the tone sound like me?
- Is the personalization accurate and verified?
- Would I respond to this email?
- Is there only one low-friction Call to Action?
- Is the total length under 120 words?

## Usage

```
/hyper-personalization [prospect-name] [company]
/hyper-personalization research [linkedin-url]
/hyper-personalization email [prospect-context]
```

## Instructions

### `[prospect-name] [company]`

Full research and draft:

```
1. Research (30s):
   - Search for recent LinkedIn activity
   - Find company news and announcements
   - Check for hiring signals
   - Look for technology mentions
   
2. Build 5-Point Dossier:
   - Recent achievement or post
   - Company momentum signal
   - Tech stack or tool usage
   - Shared connection or interest
   - Pain point indicator

3. Draft Email (15s):
   - Lead with specific insight
   - Connect to their pain point
   - Single low-friction CTA
   - Under 120 words
```

### `research [linkedin-url]`

Deep research only, no draft:

```markdown
# Prospect Research: [Name]

## Professional Summary
- Current role and tenure
- Previous companies
- Key skills and expertise

## Recent Activity
- Latest LinkedIn posts
- Articles or comments
- Conference appearances

## Company Context
- Recent news
- Funding status
- Hiring activity
- Tech stack signals

## Personalization Hooks
1. [Specific recent post or achievement]
2. [Shared interest or connection]
3. [Relevant company news]
```

### `email [prospect-context]`

Generate email from existing research:

```markdown
Subject: [Specific reference to their situation]

Hi [First Name],

[Opening: Reference specific insight from research]

[Middle: Connect to relevant pain point]

[CTA: Single, low-friction ask]

[Sign-off]

---
Total words: <120
Personalization points: 3
```

## Output Quality: Templates vs Insight

| Before (Template) | After (Insight) |
|-------------------|-----------------|
| "Hi Sarah, congrats on the Series B!" | "Hi Sarah," |
| "Fake urgency: As you scale, pipeline is a bottleneck." | "saw your post about the SDR hiring challenge—scaling into Europe without brand recognition is a different beast." |
| "Company-centric: We offer an innovative, AI-powered solution..." | "Letting AI handle initial research cuts ramp time dramatically." |
| "Buzzwords: Transform your sales process..." | "Worth 15 mins to see how it helps the EU push?" |

**Labels:**
- Fake urgency → Specific LinkedIn reference
- Company-centric → Specific pain point connection
- Buzzwords → Low-friction CTA

## The Dossier Format

```markdown
# 5-Point Dossier: [Name] @ [Company]

## 1. Recent Achievement
[Specific post, promotion, or accomplishment]

## 2. Company Momentum
[Funding, growth, expansion news]

## 3. Tech Stack
[Tools they use, integrations mentioned]

## 4. Shared Context
[Mutual connections, similar background, common interests]

## 5. Pain Indicator
[Hiring challenges, scaling mentions, tech gaps]

---
Research completed: [timestamp]
Sources: LinkedIn, Crunchbase, Company blog, G2
```

## Integration with Outreach

```
Signal fires → /hyper-personalization runs → Draft queued
                                               ↓
                                        Rep reviews (30s)
                                               ↓
                                        Sent via sequence
```

## Performance Metrics

| Metric | Manual Research | Automated |
|--------|-----------------|-----------|
| Time per prospect | 15 minutes | 75 seconds |
| Personalization depth | 1-2 points | 5 points |
| Consistency | Variable | Standardized |
| Scale | 20/day max | 100+/day |
