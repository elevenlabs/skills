You are tasked with updating ElevenLabs agent skills based on a weekly "Skills Update Brief" issue from the elevenlabs-dx changelog process.

## Cursor CLI

This command is intended to run in Cursor CLI headless mode with GPT-5.4 High.

Recommended invocation:

```bash
agent -p \
  --model gpt-5.4-high \
  --output-format text \
  --force \
  --trust \
  --workspace /path/to/skills \
  "$(cat .claude/commands/update-skills.md)"
```

Execution rules for Cursor CLI:

- Use `-p` / `--print` so the workflow runs non-interactively and writes the final report to stdout.
- Use `--model gpt-5.4-high` for this workflow.
- Use `--force` when you want the agent to make file edits, create a branch, and commit without an extra approval step.
- Use `--trust` in headless mode to avoid workspace trust prompts.
- Prefer `--output-format text` so the final answer is a plain markdown report.

Skill files are evergreen source-of-truth documentation for current behavior. Use the brief and changelog to discover what changed, but write final `SKILL.md` and `references/*.md` content as timeless present-tense documentation.

Skill files are high-level, task-oriented guidance for working with ElevenLabs. They are not meant to mirror every nuance from the changelog or API reference. Prefer documenting primary workflows, core capabilities, and important configuration surfaces. Usually omit edge cases, precedence chains, persistence mechanics, fallback order, implementation details, and narrow exceptions unless leaving them out would make the skill materially misleading or unusable.

## Workflow

1. Find the latest open `skills-update` issue
2. Parse the brief to identify which skills are affected and what needs changing
3. For each affected skill, read the current files and make targeted updates
4. Verify each delta against the changelog and each documented detail against the API reference
5. Self-check all edits before committing
6. Create a branch, commit changes if needed, and return only a markdown report suitable for Cursor CLI stdout

## Step 1: Find the issue

```bash
gh issue list --repo elevenlabs/skills --label "skills-update" --state open --limit 1 --json number,title,body
```

If no open issues exist, stop and report that there are no pending skills updates.

If multiple open issues exist, process the most recent one first:

```bash
gh issue list --repo elevenlabs/skills --label "skills-update" --state open --limit 10 --json number,title,body,createdAt --jq 'sort_by(.createdAt) | reverse | .[0]'
```

## Step 2: Parse the brief

The issue body follows this structure:

```markdown
## Skills Update Brief — YYYY-MM-DD

Source: [Changelog YYYY-MM-DD](https://elevenlabs.io/docs/changelog/YYYY-MM-DD)

### skill-name

- Description of change — **affected area** needs updating

### Summary

N skills affected. Changes are additive/breaking.
```

Extract:
- The date (for branch naming)
- Each skill section and its bullet points
- Whether changes are breaking or additive (from the Summary line)

## Step 3: Read current skill files

For each affected skill listed in the brief, read:
- `{skill}/SKILL.md` — the main skill file
- All files in `{skill}/references/` — the reference documents

The skill directories are:
- `text-to-speech/` (SKILL.md + references: installation.md, streaming.md, voice-settings.md)
- `speech-to-text/` (SKILL.md + references: installation.md, transcription-options.md, realtime-server-side.md, realtime-client-side.md, realtime-commit-strategies.md, realtime-events.md)
- `agents/` (SKILL.md + references: installation.md, agent-configuration.md, client-tools.md, widget-embedding.md, outbound-calls.md)
- `sound-effects/` (SKILL.md + references: installation.md)
- `music/` (SKILL.md + references: installation.md, api_reference.md)
- `setup-api-key/` (SKILL.md only)

## Step 3.5: Verify changes against source documentation

Before making any edits, fetch and read the actual source material. The brief and changelog tell you *what changed*; API/reference docs tell you *what to document as the current state*. You must verify every detail before writing documentation.

1. **Fetch the changelog page** linked in the brief's `Source:` field (e.g., `https://elevenlabs.io/docs/changelog/YYYY-MM-DD`). Use it to identify deltas and affected surfaces, not as final wording for skill files.
2. **Fetch the relevant API reference pages** for each change. The ElevenLabs API reference lives at `https://elevenlabs.io/docs/api-reference/`. For common areas:
   - Agents: `https://elevenlabs.io/docs/api-reference/agents/create`, `https://elevenlabs.io/docs/api-reference/agents/update`
   - TTS: `https://elevenlabs.io/docs/api-reference/text-to-speech/convert`
   - STT: `https://elevenlabs.io/docs/api-reference/speech-to-text/convert`
3. **For each bullet in the brief**, find the corresponding section in the API reference. Note the exact field names, types, nesting, and allowed values for the final docs.
4. If a feature appears in the brief/changelog but the API reference does not provide enough schema detail, do not create field tables or code examples for it. Put it under "Needs Manual Authoring" in the final report.

Do NOT proceed to editing until you have read the actual API reference for every field, parameter, or schema you intend to document. If a referenced page returns an error or doesn't contain the expected information, flag it — do not guess.

## Step 3.6: Decide if each bullet belongs in skill docs

Not every changelog bullet requires a skill-file edit. Before editing, run this decision gate for each bullet:

1. **Map to a natural home first.** Try to place the change in an existing section/table/list/example in `SKILL.md` or `references/*.md`.
2. **Pass the abstraction filter.** Only document the change if it reflects a primary capability, common workflow, or important top-level configuration concept that helps users work with ElevenLabs at a high level.
3. **Skip secondary nuances.** If the bullet is mostly an edge case, precedence rule, persistence detail, fallback order, implementation nuance, narrow exception, deprecation notice, or "do not use X" warning, do not add it to skill files even if it is verified and even if it could fit somewhere.
4. **Edit only when fit is clear.** If a natural home exists and the change passes the abstraction filter, make the smallest useful update there.
5. **Prefer no-op over forced structure.** If no natural home exists, or the change is too low-level for skill docs, do not add a one-off sentence or heading just to "cover" the bullet.
6. **Record no-op in report.** Put skipped bullets under `No Skill Change Needed` in the final report with a one-line reason and source link.
7. **Only add a new section when all are true:** the feature is substantial, user-facing, reusable, high-level enough for skill docs, and clearly missing from current structure.
8. **Prefer the current path.** When a changelog says one field, endpoint, model, package, or pattern replaces another, update the docs to show the current supported way to do the task. Do not document the deprecated or removed path in skill content unless the user explicitly asks for migration guidance.

### Fit examples

- Good: update an existing model table with a new supported model row.
- Good: add a new top-level parameter to an existing configuration table when it changes how users commonly set up the product.
- Good: changelog item has no natural section in current skills; leave skill files unchanged and note it in `No Skill Change Needed`.
- Good: verified change is real but too low-level for skill docs; leave skill files unchanged and note it in `No Skill Change Needed`.
- Good: add `pre_tool_speech` to a tool options table because it is the current field; omit `force_pre_tool_speech` from skill files and mention the deprecation only in the report.
- Bad: insert a standalone sentence between unrelated sections just to mention a changelog item.
- Bad: add a sentence documenting internal precedence, local persistence behavior, fallback language resolution, or a one-off override nuance unless that behavior is central to successful usage.
- Bad: add rows, warnings, or examples for deprecated/removed fields solely to tell users not to use them.

## Step 4: Make targeted updates

For each bullet that passes Step 3.6, identify the **affected area** (bolded in the brief) and apply the change to the correct file and section using current-state, present-tense wording.

### Update patterns by affected area

**Model table** — Find the markdown table listing models in SKILL.md. Add, remove, or modify rows. Verify model IDs, language counts, and latency descriptions match the changelog.

**Code examples** — Find the relevant code blocks in SKILL.md or reference files. Update method signatures, add new parameters to examples, or fix import paths. Always update Python, JavaScript, and cURL examples together if all three exist.

**LLM provider table** — In agents/SKILL.md or agents/references/agent-configuration.md, find the table listing LLM providers and model IDs. Add or remove entries.

**Tools section** — In agents/SKILL.md, find the tools section. Add new tool types with examples in the same style as existing ones.

**CLI section** — In agents/SKILL.md or agents/references/, find CLI command examples. Add new commands or update existing ones.

**Parameter documentation** — Find the relevant parameter list or table. Add new parameters with type, description, and whether they're required or optional.

**Configuration tables** — In reference files (e.g., agent-configuration.md, voice-settings.md), find field tables and add/modify rows.

**Output format table** — In text-to-speech/SKILL.md, find the output formats table. Add or modify entries.

### Hard rules — never break these

- **Never invent field names, types, or schemas.** Every field you document must be verified against API reference documentation, not inferred from the brief. If the brief says "new `sanitize` field" but you cannot find its exact type and parent object in the API reference, do not document it.
- **Never write code examples for new features without verifying the exact API shape.** If you cannot fetch or find the API reference for a new feature, add a stub like `<!-- TODO: Add code example — verify schema against API reference -->` instead of guessing.
- **Treat the brief and changelog as discovery inputs, not skill-file prose.** They tell you *which* things changed; API/reference docs tell you the current behavior to document. Never use brief/changelog phrasing directly in skill content.
- **Do not treat verified details as automatically skill-worthy.** A detail being true and documented in the API reference is necessary but not sufficient for inclusion in `SKILL.md` or `references/*.md`.
- **Skill files must be evergreen.** Never mention changelog, brief, issue, PR, release date, or temporal phrases like "added in", "introduced in", "as of YYYY-MM-DD", or "now supports" inside `SKILL.md` or `references/*.md`.
- **Document current positive workflows, not negative history.** Skill files should focus on the way things work now. Do not add deprecated fields, removed enum values, old package names, migration warnings, or "do not use" examples just because they appear in a changelog. Keep that context in the final report unless the skill already has an explicit migration/troubleshooting section and the user asked for it.
- **Rewrite release-note phrasing into timeless docs.** Example:
  - Bad: `For RAG indexing, the 2026-02-23 changelog added support for the qwen3_embedding_4b embedding model.`
  - Good: `RAG indexing supports the qwen3_embedding_4b embedding model.`
  - Bad: `As of 2026-02-23, agents now support X.`
  - Good: `Agents support X.`
- **Never fabricate example values.** If you're adding a code example, use values from source docs and present them as current behavior. Do not invent model IDs, field names, or configuration values that "seem right."
- **Not every changelog bullet requires a skill edit.** If an item has no natural home in existing docs, choose no-op and document that in the final report.
- **Prefer high-signal docs over exhaustive docs.** Skill files should explain the main way to use ElevenLabs features, not catalog every caveat or exception from the platform docs.
- **Prefer replacement over deprecation.** If a new capability replaces an old one, document only the replacement as the current workflow. Do not add the old field or old behavior to tables, examples, or prose unless omitting it would make an existing migration section incorrect.
- **Do not create a new section solely because a changelog bullet exists.**
- **Do not insert orphan content.** Never add standalone lines or mini-sections that do not belong to surrounding structure.
- **New sections require justification.** Create a new section only when the concept is substantial, reusable, user-facing, and cannot be documented cleanly by extending existing sections.
- **Default to omission for edge-case behavior.** If the detail mainly describes fallback behavior, precedence between multiple config sources, persistence internals, or a rare branch-specific exception, leave it out of skill docs unless users routinely need it to succeed.

### Risk tiers for changes

**Low risk** (brief + changelog verification is usually sufficient):
- Adding a new enum value to an existing list (e.g., new model ID to a model table)
- Updating a version number
- Adding a new bullet to an existing list of options

**Medium risk** (verify against changelog and API reference before editing):
- Adding a new field to an existing parameter table
- Adding a new option to an existing code example

**High risk** (verify against API reference — do not guess):
- Writing a new section with code examples from scratch
- Documenting a new schema or configuration object
- Adding field tables for features that don't already have documentation in the skills

For high-risk changes where you cannot verify the exact schema, do not add placeholder sections in skill files. Record the item under "Needs Manual Authoring" in the final report. If the schema is verified but there is no natural home in current skill structure, record it under "No Skill Change Needed" instead of forcing a section.

### Style rules

- Make minimal, targeted changes. Do not rewrite sections that aren't mentioned in the brief.
- Match the existing style exactly — same heading levels, table formats, code block languages, indentation.
- Keep code examples internally consistent. If a Python example uses `client = ElevenLabs()`, keep that pattern.
- Keep the docs focused on "how to use this capability" rather than "every rule the platform follows in edge conditions."
- Keep tables focused on supported current fields. Avoid adding deprecated fields to tables just to signal that they should not be used.
- When adding a new model to a table, place it in a logical position (e.g., by quality tier or alphabetically, matching the existing order).
- When adding new parameters to code examples, only add them if they're significant enough to demonstrate. Not every optional field needs a code example.
- If the brief mentions an SDK version bump but no method signature changes, update any version-specific comments but don't change code examples.
- Prefer extending existing headings over creating new headings.
- If a bullet has no natural documentation home, leave skill files unchanged and capture that decision in the final report.
- If a bullet is accurate but too narrow or exception-oriented for the skills, leave skill files unchanged and capture that decision in the final report.

## Step 4.5: Self-check before committing

Review every change you made and verify:

1. Every field name in a parameter table appears in the API reference you fetched in Step 3.5.
2. Every code example uses the actual parameter names and nesting from the API reference.
3. You did not add any field, type, or description that you inferred rather than verifying in source documentation (prefer API reference for schema details).
4. No code example contains fabricated values (model IDs, config names, etc.) that you didn't find in the source documentation.
5. No edited `SKILL.md` or `references/*.md` line references a changelog, brief, issue, PR, or date as part of feature documentation.
6. No release-note phrasing remains in skill files (e.g., "added in", "introduced in", "as of", "now supports", "the changelog added").
7. Any historical/provenance notes are kept in the final report only, not in skill files.
8. Every new heading/section is justified by Step 3.6 and is not a placeholder for a single changelog bullet.
9. No orphan insertions remain (standalone one-off sentences that do not fit the section).
10. No edited skill content exists solely to capture an edge case, precedence rule, persistence detail, fallback chain, or narrow exception that would be better left to API docs.
11. No edited skill content documents deprecated, removed, or replaced fields/packages/patterns merely as negative guidance.
12. Every brief bullet is accounted for via one of: (a) natural-home docs update, (b) justified new section, (c) "No Skill Change Needed", or (d) "Needs Manual Authoring" in the final report.

If any change fails this check, revert it. Move it to "Needs Manual Authoring" or "No Skill Change Needed" in the final report, as appropriate.

## Step 5: Create branch, commit, and return report

```bash
git checkout -b skills-update/YYYY-MM-DD
git add -A
git diff --cached --quiet || git commit -m "Update skills from changelog YYYY-MM-DD"
```

After the edits are complete, return a markdown report in the final response instead of opening a PR.

The report should follow this structure:

```markdown
# Skills Update Report

## Outcome

- Issue: `#ISSUE_NUMBER` - Skills Update Brief — YYYY-MM-DD
- Branch: `skills-update/YYYY-MM-DD`
- Commit: `<commit sha or "No commit created">`
- Result: `<updated skills | no skill changes needed | partial update>`

## Summary

Updates skills based on the weekly changelog brief.

If the brief's Summary says changes are breaking, add a short warning here describing which examples or docs may need migration guidance.

### Changes

- **skill-name**: Brief description of what was changed (e.g., "Added `eleven_v4` to model table, updated code examples with `seed` parameter")
- **skill-name**: Brief description

### Verification

For each change, note how it was verified:
- `field_name` in `file.md` — verified against [API reference page](url)
- `other_field` in `file.md` — verified against [changelog](url)

### Needs Manual Authoring

List any items from the brief that were NOT applied because the schema could not be
verified against the API reference. For each, include:
- What the brief said
- Why it couldn't be verified (e.g., "API reference page doesn't document this field yet")
- Suggested API reference link to check when it becomes available

If no items apply, write "None."

### No Skill Change Needed

List verified changelog items that were intentionally not added to skill files because
they have no natural home in current skill structure. For each, include:
- What changed
- Why no skill edit was appropriate
- Source link used for verification

If no items apply, write "None."

### Open Questions

List blockers, ambiguous source material, or follow-up items for the next human/agent.

If no items apply, write "None."

### Source

[Skills Update Brief — YYYY-MM-DD](#ISSUE_NUMBER)
[Changelog YYYY-MM-DD](https://elevenlabs.io/docs/changelog/YYYY-MM-DD)
```

When run via Cursor CLI headless mode, return only the completed markdown report in the final response unless the invoking user explicitly asks for extra commentary.

## Important

- Do not modify skills that are not mentioned in the brief.
- Do not update the `openclaw/` directory — that is community-maintained.
- Do not change the YAML frontmatter in SKILL.md files unless the brief specifically calls for it (e.g., description change).
- If the brief mentions a change you cannot verify against the API reference (or another canonical documentation page), do NOT add it to the skill files. Instead, list it in the final report under "Needs Manual Authoring" with what the brief says and why you couldn't verify it. A wrong code example is worse than a missing one.
- If a brief item is verified but does not fit naturally into existing skill structure, do NOT force a new section or sentence. List it under "No Skill Change Needed" in the final report with a short rationale.
- If the brief's Summary says changes are "breaking", add a warning in the report highlighting which examples may need migration guidance.
- Keep changelog dates, issue references, and release-history wording in the report/issue context only — never in `SKILL.md` or `references/*.md`.

## Note on brief quality

If the brief only provides feature names and high-level descriptions without API reference links or schema details, many items will likely end up under "Needs Manual Authoring." This is the correct outcome — it surfaces gaps for a human to fill rather than hallucinating plausible-looking documentation. Over time, the brief generation process should be improved to include exact field paths, types, and API reference links for each change.
