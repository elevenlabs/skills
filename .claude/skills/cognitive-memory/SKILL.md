---
name: cognitive-memory
description: Human-inspired memory architecture with multi-tier storage, adaptive forgetting, and engram maturation. Use when building persistent agent memory systems that consolidate, prioritize, and forget intelligently.
when_to_use: When user needs agent memory, knowledge management, or wants to implement forgetting/consolidation in AI systems.
disable-model-invocation: true
license: MIT
compatibility: Conceptual framework - implement with your preferred storage backend.
---

# Cognitive Memory Architecture

Multi-tier storage, offline consolidation, adaptive forgetting, and engram maturation.

## The Amnesia Problem

| Approach | Problem |
|----------|---------|
| **Stateless Agents** | Treat each interaction independently. Lose all context between sessions. |
| **Vector RAG** | Stores embeddings. Treats all information equally. Cannot consolidate or forget, leading to compounding information loss. |
| **Human-Inspired Memory** | Multi-tier storage, offline consolidation, adaptive forgetting, and engram saturation. Scalable and self-governing. |

## Neuro-Architectural Mapping

| Biological | Technical |
|------------|-----------|
| **Neocortex** | Hot Cache (In-memory, TTL min-hrs) |
| **Hippocampus** | Episodic Store (Vector database, high-fidelity, TTL days-weeks) |
| **Prefrontal Cortex** | Semantic Knowledge Graph (Entity relationships, multi-hop traversal, permanent) |

**Key insight**: Rapid episodic encoding handles recent events; slow semantic extraction builds permanent relationship graphs.

## Forgetting is a Feature, Not a Bug

```
Decay Rate: λ = 0.001 (~29-day half-life)

1.0 |----___
    |       ~~~---___  2. Engram Maturation
0.8 |                ~~~---___
    |                         ~~~---
0.6 |  1. Interference-Based Forgetting
    |
0.4 |
    |
0.2 |
    | Memories start silent (Activation ≈ 0.03).
0.0 | Reach full maturity explicitly retrievable
    | (A > 0.9) at two weeks.
    +------------------------------------------
      0   2   4   6   8   10  12  14
                   Time (Days)
```

**Result**: Deduplication-based consolidation achieves 97.2% retention precision while reducing store size by 58%.

## Three-Tier Implementation

### Tier 1: Hot Cache (Minutes to Hours)
```python
# In-memory, fast access, auto-expires
hot_cache = {
    "current_context": {...},
    "ttl": "30m",
    "purpose": "Working memory for current task"
}
```

### Tier 2: Episodic Store (Days to Weeks)
```python
# Vector DB with high-fidelity recall
episodic_store = {
    "type": "vector_db",
    "ttl": "14d",
    "purpose": "Recent experiences, detailed recall",
    "decay_rate": 0.001
}
```

### Tier 3: Semantic Graph (Permanent)
```python
# Knowledge graph with entity relationships
semantic_graph = {
    "type": "knowledge_graph",
    "ttl": None,  # Permanent
    "purpose": "Consolidated knowledge, relationships",
    "operations": ["multi-hop traversal", "entity linking"]
}
```

## Consolidation Process

1. **Encoding**: New information enters Hot Cache
2. **Rehearsal**: Repeated access strengthens episodic traces
3. **Extraction**: Patterns extracted to semantic graph
4. **Forgetting**: Low-activation memories decay
5. **Maturation**: Surviving memories reach full retrievability

## The 200K Context Window

When your AI knows everything about a deal—every email, every call, every document—it stops being a generic assistant and starts being a genuine copilot.

| Token Budget | Content |
|--------------|---------|
| 4K tokens (~3,000 words) | Basic context |
| 32K tokens (~24,000 words) | Extended history |
| 200K tokens (~150,000 words) | Full deal context: 2 Gong transcripts, 3 reps' CRM notes, competitor pricing, company 10-K filing |

## Usage

```
/cognitive-memory design "sales deal context"
/cognitive-memory analyze "current memory architecture"
/cognitive-memory consolidate
```

## Instructions

When invoked:

1. **Design mode**: Create memory architecture for specified domain
   - Map to three-tier structure
   - Define TTLs and decay rates
   - Specify consolidation triggers

2. **Analyze mode**: Evaluate existing memory system
   - Identify tier coverage gaps
   - Check for forgetting mechanisms
   - Assess retrieval patterns

3. **Consolidate**: Run consolidation pass
   - Identify patterns in episodic store
   - Extract to semantic graph
   - Prune decayed memories
