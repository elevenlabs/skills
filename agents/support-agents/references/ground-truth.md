# Ground truth — ranking sources and deriving correct answers

The single biggest quality lever for a support agent is knowing, per question, what the *correct* answer actually is. Most bad agent behavior traces back to teaching it something unverified.

## The hierarchy (most authoritative first)

Rank the user's sources during intake and record the ranking in `survey.md`. A generic ordering that holds for most products:

1. **Product source code** — how the product *actually* behaves: billing logic, credit/quota consumption order, what an error code means, what a flow really does. Overrides policy docs, the KB, old tickets, and the model's priors. Caveats: code can be ahead of what's released (check whether a fact hinges on something just merged), and feature flags / plan gating change what a given customer sees.
2. **Support policy / SOPs** (the human-agent playbook) — how to *handle* a case: when to escalate, what to offer, what tone. Source code says what is true; policy says what to do about it.
3. **Customer-facing knowledge base / help center** — public facts (prices, limits, UI paths). For anything the agent will literally say to a customer, customer-facing-correct wording matters as much as technical truth — so for phrasing, this can outrank the code.
4. **Historical tickets** — real scenarios plus what a human actually did. High value as *evidence*, but human replies go stale and contain mistakes: verify a ticket-only claim against policy or code before treating it as truth.
5. **Sibling agents / competitor transcripts** — last resort for a product fact; handling policy does not transfer between products.

The hierarchy ranks *authority*; it says nothing about *where* a source lives. Any of these can sit in the platform KB, in local files (an internal repo, a policy folder), or only on the public web — record the location next to the ranking in `survey.md`, because it changes how you verify: platform-KB facts are verified the way the agent retrieves them (see [knowledge-base.md](knowledge-base.md)), local files are read directly, and web-only sources are fetched fresh (beware JS-rendered pages and crawl noise — what you see in a browser is not what a crawler captured).

Two rules on top of the ranking:

- **Never average conflicting sources.** If the pricing page and the code disagree, that conflict is a real finding — surface it to the user and let them resolve it (often the finding is "your docs are stale," which is valuable on its own).
- **Tests are never ground truth.** Generated criteria drift and encode old policy. When a test contradicts the hierarchy, fix the test.

## Corroboration discipline

For any fact that will drive an agent behavior change or a test criterion:

- Confirm it from **at least two independent sources** (different origins — code + policy, not two pages of the same doc site).
- To call an agent reply a *fabrication*, you must positively cite a source that contradicts the agent's exact words. No citation → you cannot call it a fabrication. First-pass reviews over-flag hallucinations; a common error is confusing a **unit** (what something is billed in), a **metric** (per-character vs per-minute), and a **display** (a converted equivalent shown in the UI).
- Facts you *cannot* verify (a mock's return value, a KB doc you can't read) get flagged as unverified, not guessed.

## The intake questions

Ask, in the user's terms:

- "Is there a code repository that's authoritative for how the product behaves? Can I read it from here?"
- "Do you have written support procedures, SOPs, macros, or a human-agent playbook?"
- "Where's your help center / docs / pricing page? Which of those is most current?"
- "Where does each source live — already in the platform KB, in files/repos I can read, or only on the public web?"
- "How can we get historical tickets or conversations? An export from your ticketing system? API access? If an ElevenLabs agent already answers traffic, I can pull its conversations."
- "When sources disagree — say the docs and the app — which wins?"
- "Who are the humans behind escalation, and what do they wish the agent told them in a handoff?"

## Using ticket history well

- Full resolution threads (what the human actually replied, not just the customer's opening message) are the highest-value slice — they show real resolutions and real escalation judgment.
- Ticket dumps are PII. Keep them in local, uncommitted files; anonymize anything that flows into a committed test or an uploaded document.
- When mining tickets for expected behavior, derive the correct answer from the hierarchy per ticket — do NOT assume the human reply, an existing procedure, or a current test criterion is correct. If the verified answer contradicts an existing procedure, you found a real agent gap, not a reason to copy the old behavior.
