# Knowledge base — setup and RAG tuning

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
