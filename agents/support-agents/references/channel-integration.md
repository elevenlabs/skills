# Hooking the agent up to a channel

How conversations reach the agent and how its output lands back in the ticketing system. Zendesk is the worked example throughout (it's a first-class integration on the platform); the shape is the same for other ticketing systems.

## The wiring model

Four pieces, configured in this order:

1. **Connection** — credentials for the ticketing system, created once per environment (`POST /v1/convai/api-integrations/{integration_id}/connections`). The connection is *baked into each tool instance* — this matters later for dev/prod separation.
2. **Tools** — created from the integration's catalog and attached to the agent (see the parent agents skill, "Integration Tools"). For a support agent you typically want: post comment (public reply / internal note), update ticket (status, assignee), add/remove tags.
3. **Trigger** — the ticketing-system side: a rule that starts a conversation with your agent when a ticket is created or updated. The trigger is per-connection and lives outside the agent config. Scope it deliberately:
   - **Start narrow.** Route only a subset to the agent at first — a tag, a category, or (for a test instance) a subject prefix — and widen as the suite and prod reviews earn confidence.
   - **Prevent loops.** The escalation flow must set a tag (or equivalent) that the trigger excludes, so the agent stops re-triggering on tickets a human has taken over — and so a human/other-bot reply doesn't re-summon the agent.
4. **Dynamic variables** — the contract between trigger and agent. The trigger passes ticket context into the conversation: requester email, ticket id, subject, requester id, created-at. Everything the agent's tools need to identify the customer should come from here, not from the LLM.

## Identity binding (the security-critical part)

Bind identity-bearing tool parameters (customer email, account id) to trigger-supplied dynamic variables — e.g. `email` → `{{integration__zendesk_ticket_requester_email}}` — rather than letting the model fill them. The requester's identity is then anchored to what the ticketing system verified, and the model cannot be talked into looking up someone else's account. When the model legitimately must choose among several values (a customer with multiple workspaces), constrain the choice to a server-verified allowlist derived from a trusted lookup, not free text.

Two gotchas:

- A `{{var}}` referenced anywhere (prompt, first message, tool body) that the channel doesn't actually supply kills the conversation at turn 0. Only reference variables your trigger really sends; test by driving the real channel, not just simulations (which supply variables by hand).
- Downstream read tools usually need the same identity anchor — a lookup that works in mocked tests can 422 live because it lacked the bound email param. Real-channel testing (below) is what surfaces this.

## The reply path

The agent's customer-facing output is a public comment posted via the write tool. Decide the envelope once: greeting with the requester's first name (from a dynamic variable, with a neutral fallback), sign-off, and any required AI disclosure line — and pin it with tests.

## Escalation

The escalation write sequence (internal note → unassign/status → routing + suppress-AI tags) is a deterministic procedure derived from the customer's own workflow — full treatment in [escalation.md](escalation.md).

## Dev and prod instances

Keep two parallel tool sets — one wired to a production connection, one to a dev/sandbox instance of the ticketing system — because the connection is baked into the tool, switching environments means pointing the agent at the other set's tool ids (on a working branch), never re-pointing a shared tool's connection.

- Use the dev instance for **real end-to-end tests**: send a message into the dev inbox the way the trigger expects, and read the agent's actual reply plus the conversation's tool timeline in the platform's Conversations view. This is the only place real backend errors (422s, latency, timeouts) show up — mocked tests can't produce them.
- Production wiring is the only prod-ready state: switching back (tool ids, any bot-user id, tool mocks) is part of finishing a dev session, and the dev wiring must never be able to write to production tickets.
