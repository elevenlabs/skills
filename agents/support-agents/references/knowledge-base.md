# Knowledge base — setup and RAG tuning

## Where the knowledge lives

Knowledge sources come in three shapes; establish per source at intake which one you have, because it decides the whole Phase 2 route:

1. **Platform KB (preferred).** Ingest into the Agents Platform knowledge base and retrieve via RAG — single source of truth, refreshable crawls, retrieval you can inspect. Everything below assumes this route where possible.
2. **Local files** — internal docs, policy files, or code that isn't public. These are ground-truth *research* material first: verify facts from them, then upload verified extracts as text documents when the agent should retrieve them. Never ingest raw internal material wholesale — anything in the KB can surface verbatim in a customer reply.
3. **Web-only help center** — the knowledge exists only as public web articles and resists clean ingestion: no markdown export, raw crawls full of nav noise, or articles whose substance is screenshots. Teams in this spot usually end up **inlining facts into procedures** instead. That works, but it decays silently — pair it with the procedures-vs-source audit below, and re-try ingestion per article class (a custom parser for one help-center platform often unlocks the whole site).

Web-only traps worth checking before you commit to a route:

- **Image-heavy articles:** key facts living in screenshots don't survive text ingestion — transcribe what the image shows into the ingested text or the procedure, marked as such.
- **Deflection pages poison retrieval:** help-center articles that conclude "contact support" rank high for exactly the questions the agent should answer, and retrieved chunks are hard to override from prompt/procedure text — so the agent starts telling customers to contact support. Exclude or clean deflection-style pages at ingest; the KB carries *facts*, procedures carry *handling*.

## Auditing procedures against the source of truth

Whenever facts are inlined in procedures (route 3, but also any inline fact from [the inline-vs-retrieval rule](#inline-facts-vs-retrieval)), they drift as the source changes. Run this audit on a cadence and after any known docs/policy change:

1. Enumerate the factual claims in each procedure (prices, limits, step sequences, feature availability — anything checkable).
2. Map each claim to its authoritative source (KB document, help-center article, code) — recording this mapping once makes every later audit cheap.
3. Re-fetch the source and diff: stale, contradicted, or no-longer-covered claims are findings; so are new articles covering a topic no procedure handles.
4. Propose the smallest updates one at a time through the normal review-diff-approve flow, each with a test where behavior changes.

## Setup

1. **Ingest sources** identified in the intake survey:

```bash
# From a URL (docs page, help-center article)
curl -s -X POST "https://api.elevenlabs.io/v1/convai/knowledge-base/url" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"url": "https://docs.example.com/billing"}'

# From text you assembled (returns a document id)
curl -s -X POST "https://api.elevenlabs.io/v1/convai/knowledge-base/text" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"name": "pricing", "text": "<verified pricing content>"}'
```

2. **RAG-index** documents (`POST /v1/convai/knowledge-base/{documentation_id}/rag-index`) and attach them to the agent's `knowledge_base` config. Record every document id and its source in `kb/sources.md`.
3. **Refresh policy:** URL documents can be re-crawled (`POST /v1/convai/knowledge-base/{documentation_id}/refresh`). Decide per source whether it refreshes on a cadence or is regenerated manually, and write that down — stale pricing is the classic silent failure.

## Keep the KB wide, keep it clean

- **Wide:** the agent must eventually answer every query type, so the fix for noisy retrieval is rarely "shrink the KB to nothing."
- **Clean:** noise usually has mundane causes, not a retrieval bug:
  - **Off-topic pages that lexically match** — e.g. an example/demo page containing the word "refund" will match refund queries. Keep demo and marketing content out of the support KB.
  - **HTML/nav cruft in chunks** ("Skip to main content…") — a crawl-quality problem. Inspect a few chunks (`GET /v1/convai/knowledge-base/{documentation_id}/chunks`) after ingesting; if they're full of markup, fix the source or ingest cleaned text instead.
- **JS-rendered pages don't crawl.** Pricing pages are the canonical case: the crawler captures only navigation, never the prices. Two reliable alternatives:
  - render the content from the code/data that already defines it (impossible-by-construction drift) and upload as a text document on a schedule;
  - give the agent a deterministic read tool that GETs the document's content directly — `GET /v1/convai/knowledge-base/{documentation_id}/content` — instead of gambling on retrieval, with a procedure rule like "before quoting any price, call the pricing tool and quote only from its result."

## Retrieval knobs (and their limits)

Under `conversation_config.agent.prompt.rag`:

- `max_vector_distance` — too loose lets off-topic chunks through; too tight starves legitimately broad queries. Tighten it as the first response to noisy retrieval.
- `max_retrieved_rag_chunks_count` and the retrieved-text budget cap how much text is pulled per query.
- Chunk size is a platform property, not an agent knob — content hygiene, not configuration, is the fix for bad chunks.

Tune distance + budget together and re-measure on the test suite; RAG-heavy tests vary run to run, so re-run a red before trusting it.

## Verify facts the way the agent retrieves them

When checking "can the agent answer this from the KB", do not fetch the public docs site — that's not what the agent sees.

- **Faithful check:** run the agent on a probe question that forces the lookup, then read the conversation's `rag_retrieval_info` (on `GET /v1/convai/conversations/{conversation_id}` transcripts): the retrieval query, the retrieved chunks, and `used_chunk_ids` (which chunks the model actually cited).
- **Quick approximation:** `GET /v1/convai/knowledge-base/search?query=...` confirms a fact exists *somewhere* in the KB — but it is a text search, not the agent's vector retrieval, so "found via search" ≠ "the agent will retrieve it."
- **The signal to chase:** *retrieved vs cited*. "5 chunks retrieved, 0 cited" means the model pulled noise and used none of it.

## Inline facts vs retrieval

Prefer a directed KB lookup with a verified query over repeating a fact inline in a procedure. Embed a fact inline only when you've confirmed retrieval won't reliably return it — and conversely, never strip an inline fact until you've probed that the KB reliably serves it (removing a fact RAG won't return silently breaks answers).

Zero RAG lookups before an escalation on an answerable question is a routing smell; a cited noise chunk is a KB smell. Both show up in `rag_retrieval_info` — read it whenever an answer surprises you.

## Delegating research to a subagent

Once a support agent carries many procedures and tools, adding direct KB retrieval competes for the same context budget. The platform's `run_subagent` built-in tool (see the parent [agents skill](../../SKILL.md)) is an alternative: the support agent calls out to a small, dedicated **KB research agent** — its whole job is turning one question into a synthesized, cited answer — instead of retrieving chunks itself.

- **Prompt the target agent for machine consumption, not a chat reply.** Require at least two lookups per question (an initial query, then a rephrased/narrowed follow-up informed by what the first returned) — a single-lookup research agent under-retrieves the same way a support agent would. Forbid answering from prior/background knowledge when the KB doesn't cover the question ("not covered in the KB" beats a guess). Forbid conversational filler entirely — no greeting, no "let me check that", no sign-off — its output is consumed by another agent, not read by a customer, so every extra token is pure noise in the caller's context.
- **Name the target's `description` like a tool description**, not a label: what it answers and when to call it instead of an inline lookup. The calling model chooses among `agents` entries by reading these descriptions, exactly like choosing between two overlapping tools.
- **The query is implicit** — the calling model just states its question; there is no per-call parameter to define (each target's `parameters` schema is typically empty) and no way to override the target's model per call. The target's own configured LLM, reasoning effort, and RAG settings run every lookup.
- **Platform gotcha: a KB folder reference is rejected once RAG is off.** A knowledge-base folder attached to an agent whose `rag.enabled` is `false` falls back to "prompt mode" (the platform tries to stuff the whole folder's text into the prompt), which it rejects outright for anything but a tiny folder. If the calling agent delegates all KB access to the subagent, give it either `rag.enabled: true` with an empty `knowledge_base: []`, or turn RAG off **and** remove every KB reference — never leave a folder wired to an agent with RAG disabled.
