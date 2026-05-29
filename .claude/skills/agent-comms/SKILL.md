---
name: agent-comms
description: Cross-agent communication protocol for task coordination, source sharing, and collaborative workflows. Enables agents to share findings, cross-reference sources, and coordinate on complex multi-agent tasks.
when_to_use: When multiple agents need to collaborate, share research findings, cross-reference sources, or coordinate on a complex task.
disable-model-invocation: true
license: MIT
compatibility: Works with Claude Code Agent tool and subagents.
---

# Agent Communication & Collaboration Protocol

Enable cross-agent communication, source sharing, and coordinated task completion.

## Communication Patterns

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                              │
│  Coordinates tasks, aggregates results, resolves conflicts   │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────┐       ┌─────────┐       ┌─────────┐
   │ Agent A │◄─────►│ Agent B │◄─────►│ Agent C │
   └─────────┘       └─────────┘       └─────────┘
        │                  │                  │
        └──────────────────┴──────────────────┘
                    Shared Context
                   (Ledger + Sources)
```

## Usage

```
/agent-comms broadcast [message]
/agent-comms share-source [source-ref]
/agent-comms request [agent] [query]
/agent-comms aggregate [task-id]
```

## Instructions

### `broadcast [message]`

Send message to all active agents:

```xml
<broadcast>
  <from>orchestrator</from>
  <timestamp>2026-05-29T13:45:00Z</timestamp>
  <priority>normal|high|urgent</priority>
  
  <message>
    $ARGUMENTS
  </message>
  
  <context>
    <task_id>current-task</task_id>
    <relevant_files>
      - src/auth/jwt.ts
      - docs/auth-spec.md
    </relevant_files>
  </context>
</broadcast>
```

### `share-source [source-ref]`

Share a verified source with other agents:

```xml
<source_share>
  <from>explore-agent-1</from>
  <source_id>src-001</source_id>
  
  <source>
    <type>file|url|api|document</type>
    <location>src/auth/patterns.ts</location>
    <verified>true</verified>
    <verification_method>file_read</verification_method>
    <timestamp>2026-05-29T13:40:00Z</timestamp>
  </source>
  
  <summary>
    Authentication patterns used in the codebase:
    - JWT with refresh tokens (lines 45-120)
    - Session management (lines 125-200)
  </summary>
  
  <key_findings>
    - Uses RS256 algorithm
    - 15-minute access token TTL
    - 7-day refresh token TTL
  </key_findings>
  
  <cross_references>
    - Related: src/auth/middleware.ts
    - Config: src/config/auth.ts
  </cross_references>
</source_share>
```

### `request [agent] [query]`

Request information from specific agent:

```xml
<agent_request>
  <from>execute-agent</from>
  <to>explore-agent-1</to>
  <request_id>req-001</request_id>
  
  <query>
    What authentication patterns are used in src/auth/?
    I need this to implement the new OAuth flow.
  </query>
  
  <context>
    <current_task>Implement OAuth2 PKCE flow</current_task>
    <blocking>true</blocking>
  </context>
  
  <expected_response>
    - List of auth patterns
    - File locations
    - Any relevant constraints
  </expected_response>
</agent_request>
```

### `aggregate [task-id]`

Collect and synthesize results from multiple agents:

```xml
<aggregation_request>
  <task_id>$ARGUMENTS</task_id>
  <requestor>orchestrator</requestor>
  
  <collect_from>
    - explore-agent-1: research findings
    - explore-agent-2: competitor analysis
    - plan-agent: architecture recommendation
  </collect_from>
  
  <synthesis_instructions>
    Combine findings into unified recommendation.
    Resolve any conflicts between sources.
    Highlight areas of agreement and disagreement.
  </synthesis_instructions>
</aggregation_request>
```

## Source Cross-Referencing

### The Source Registry

Maintain a shared registry of verified sources:

```yaml
# .claude/source-registry.yaml
sources:
  src-001:
    type: file
    location: src/auth/jwt.ts
    verified_by: explore-agent-1
    timestamp: 2026-05-29T13:40:00Z
    summary: JWT authentication implementation
    tags: [auth, jwt, security]
    
  src-002:
    type: url
    location: https://docs.example.com/auth
    verified_by: explore-agent-2
    timestamp: 2026-05-29T13:42:00Z
    summary: Official authentication documentation
    tags: [auth, docs, external]
    
  src-003:
    type: api_response
    endpoint: /api/v1/config
    verified_by: execute-agent
    timestamp: 2026-05-29T13:44:00Z
    summary: Current auth configuration
    tags: [auth, config, runtime]
```

### Cross-Reference Protocol

When citing sources in agent communication:

```markdown
## Finding: Authentication uses RS256

**Source**: [src-001] src/auth/jwt.ts (lines 45-60)
**Verified**: 2026-05-29T13:40:00Z by explore-agent-1
**Cross-ref**: Confirmed in [src-002] official docs

**Confidence**: High (multiple sources agree)
```

### Conflict Resolution

When sources disagree:

```xml
<source_conflict>
  <conflict_id>conf-001</conflict_id>
  
  <sources>
    <source ref="src-001">
      <claim>Token TTL is 15 minutes</claim>
      <location>src/auth/jwt.ts:52</location>
    </source>
    <source ref="src-003">
      <claim>Token TTL is 30 minutes</claim>
      <location>API response: config.auth.ttl</location>
    </source>
  </sources>
  
  <resolution_needed>
    Which is the actual runtime value?
    Is there environment-specific configuration?
  </resolution_needed>
  
  <assigned_to>explore-agent-1</assigned_to>
</source_conflict>
```

## Collaborative Workflows

### Pattern 1: Parallel Research

```
Orchestrator
    │
    ├── spawn Explore-1: "Research auth patterns"
    ├── spawn Explore-2: "Research competitor auth"
    └── spawn Explore-3: "Research security best practices"
    
    │ (parallel execution)
    ▼
    
Aggregate findings
    │
    ▼
    
Synthesize into unified recommendation
```

### Pattern 2: Research-Plan-Execute Pipeline

```
Orchestrator
    │
    └── spawn Explore: "Research current implementation"
              │
              └── share-source findings
                        │
                        ▼
              spawn Plan: "Design solution"
                   (receives Explore's sources)
                        │
                        └── share-source design
                                  │
                                  ▼
                        spawn Execute: "Implement"
                             (receives Plan's design + Explore's sources)
```

### Pattern 3: Iterative Refinement

```
Orchestrator
    │
    └── spawn Execute: "First implementation"
              │
              └── request Explore: "Verify approach"
                        │
                        └── share-source verification
                                  │
                                  ▼
                        Execute refines based on feedback
                              │
                              └── repeat until verified
```

## Communication Best Practices

### 1. Always Cite Sources
```markdown
Bad: "The token expires in 15 minutes"
Good: "The token expires in 15 minutes [src-001:52]"
```

### 2. Indicate Confidence Levels
```markdown
- High: Multiple verified sources agree
- Medium: Single verified source
- Low: Inferred from indirect evidence
- Unverified: Needs confirmation
```

### 3. Flag Assumptions
```xml
<assumption>
  <statement>OAuth2 PKCE is preferred over implicit flow</statement>
  <basis>Security best practices, not codebase evidence</basis>
  <verification_needed>true</verification_needed>
</assumption>
```

### 4. Structured Handoffs
```xml
<handoff>
  <from>explore-agent-1</from>
  <to>plan-agent</to>
  <context_transferred>
    - 3 source files analyzed
    - 2 external docs reviewed
    - 1 conflict identified (needs resolution)
  </context_transferred>
  <open_questions>
    - Confirm token TTL value
    - Clarify refresh token rotation policy
  </open_questions>
</handoff>
```

## Integration with Persistent Ledger

Log all agent communications for audit trail:

```sql
-- Schema addition for agent comms
CREATE TABLE agent_messages (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    from_agent TEXT NOT NULL,
    to_agent TEXT,  -- NULL for broadcasts
    message_type TEXT,  -- broadcast, request, response, share
    content TEXT,
    source_refs TEXT,  -- JSON array of source IDs
    task_id TEXT
);

-- Query communication history
SELECT * FROM agent_messages 
WHERE task_id = 'task-001' 
ORDER BY timestamp;
```
