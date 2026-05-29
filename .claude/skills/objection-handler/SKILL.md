---
name: objection-handler
description: Live AI objection handling that provides top-performer rebuttals to every rep in real-time during calls. 67% of lost deals cite objections not adequately addressed - this system fixes that.
when_to_use: When user needs help handling sales objections, wants to prepare rebuttals, or is building real-time call assistance.
disable-model-invocation: true
allowed-tools: Read
license: MIT
compatibility: Can integrate with Gong/Chorus for live transcription.
---

# Live AI Objection Handling Architecture

67% of lost deals cite objections not adequately addressed. This system provides top-performer rebuttals to every rep in real-time.

## The Architecture

```
Live Audio/Video   →   Gong/Chorus    →   Audio/Transcript
      Call              Integration         Data Stream
                                                ↓
                                        ┌─────────────────┐
                                        │  Claude 200K    │
                                        │ Context Window  │
                                        │        ↓        │
                                        │   Objection     │
                                        │   Classifier    │
                                        └────────┬────────┘
                                                 ↓
                                        ┌─────────────────┐
                                        │   Real-time     │
                                        │   Rebuttal      │
                                        └────────┬────────┘
                                                 ↓
                                        Suggested
                                        Rebuttal Script
```

## Dynamic Context: Adapting to the Prospect's Stance

When prospect says: **"Now's not a good time — check back next quarter."**

| Response Style | Example |
|----------------|---------|
| **Conversational** | "Totally get it — what's consuming your focus right now? Sometimes the thing keeping you busy is exactly what we solve." |
| **Value-Focused** | "If it's pipeline, that's our whole thing. If it's internal projects, I'll set a reminder. Which is it?" |
| **Direct Challenge** | "Your competitors aren't waiting. Every week without AI outreach is X leads lost. What must change to make this a priority now?" |

## Usage

```
/objection-handler [objection-text]
/objection-handler classify [transcript]
/objection-handler playbook [objection-type]
```

## Instructions

### `[objection-text]`

Generate contextual rebuttals:

```
Input: "$ARGUMENTS"

1. Classify objection type:
   - Timing ("not now", "next quarter")
   - Budget ("too expensive", "no budget")
   - Authority ("need to check with...", "not my decision")
   - Need ("we're fine", "don't see the value")
   - Competition ("using X already", "evaluating others")

2. Generate 3 rebuttals by style:
   - Conversational (empathetic, curious)
   - Value-Focused (ROI, pain-based)
   - Direct Challenge (urgency, loss aversion)

3. Add follow-up questions for each
```

### `classify [transcript]`

Identify objections in call transcript:

```markdown
# Objection Analysis

## Objections Detected

### 1. [Timestamp] Timing Objection
**Quote**: "We're too busy with Q4 planning right now"
**Type**: Timing
**Severity**: Medium
**Suggested response**: [Rebuttal]

### 2. [Timestamp] Authority Objection
**Quote**: "I'd need to run this by our VP"
**Type**: Authority
**Severity**: Low
**Suggested response**: [Multi-thread strategy]

## Objection Patterns
- Total objections: N
- Most common type: [Type]
- Recommendation: [Strategic advice]
```

### `playbook [objection-type]`

Return full playbook for objection type:

```markdown
# [Type] Objection Playbook

## Recognition Patterns
- "Not a good time"
- "Check back next quarter"
- "Too busy right now"
- "End of year crunch"

## Response Framework

### Step 1: Acknowledge
"I completely understand..."

### Step 2: Isolate
"Just so I understand, is it [X] or [Y]?"

### Step 3: Reframe
"What if I told you that [value prop]..."

### Step 4: Micro-commitment
"Would it make sense to [small ask]?"

## Top Performer Examples
[Real examples from successful calls]

## Common Mistakes
- Pushing too hard on timing
- Not isolating the real objection
- Skipping acknowledgment
```

## Objection Classification Matrix

| Type | Signals | Strategy |
|------|---------|----------|
| **Timing** | "busy", "later", "next quarter" | Isolate, create urgency |
| **Budget** | "expensive", "no budget", "cheaper" | ROI framing, payment options |
| **Authority** | "check with", "not my decision" | Multi-thread, coach them |
| **Need** | "we're fine", "don't need", "happy with" | Pain discovery, case studies |
| **Competition** | "using X", "evaluating", "competitor" | Differentiation, switching cost |

## Real-Time Integration

```python
# Gong/Chorus webhook handler
@webhook("/call-transcript")
def handle_transcript(event):
    transcript = event.data.transcript
    
    # Classify in real-time
    objections = classify_objections(transcript)
    
    for obj in objections:
        # Generate rebuttal
        rebuttal = generate_rebuttal(obj)
        
        # Push to rep's screen
        push_to_rep(event.rep_id, rebuttal)
```

## The 200K Context Advantage

With Claude's 200K token context window:
- Full call transcript (2 Gong calls ≈ 32K tokens)
- Previous call history with this account
- CRM notes and email threads
- Competitor positioning docs
- Product documentation

The AI knows everything about this deal when generating the rebuttal.
