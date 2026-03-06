You are tasked with updating ElevenLabs agent skills based on a weekly "Skills Update Brief" issue from the elevenlabs-dx changelog process.

## Workflow

1. Find the latest open `skills-update` issue
2. Parse the brief to identify which skills are affected and what needs changing
3. For each affected skill, read the current files and make targeted updates
4. Verify every change against the actual changelog and API reference
5. Self-check all edits before committing
6. Create a branch, commit changes, and open a PR referencing the issue

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

Before making any edits, fetch and read the actual source material. The brief is a summary that tells you *what* changed, not the exact shape of the API. You must verify every detail before writing documentation.

1. **Fetch the changelog page** linked in the brief's `Source:` field (e.g., `https://elevenlabs.io/docs/changelog/YYYY-MM-DD`). This contains the authoritative description of what changed.
2. **Fetch the relevant API reference pages** for each change. The ElevenLabs API reference lives at `https://elevenlabs.io/docs/api-reference/`. For common areas:
   - Agents: `https://elevenlabs.io/docs/api-reference/agents/create`, `https://elevenlabs.io/docs/api-reference/agents/update`
   - TTS: `https://elevenlabs.io/docs/api-reference/text-to-speech/convert`
   - STT: `https://elevenlabs.io/docs/api-reference/speech-to-text/convert`
3. **For each bullet in the brief**, find the corresponding section in the API reference. Note the exact field names, types, nesting, and allowed values.

Do NOT proceed to editing until you have read the actual API reference for every field, parameter, or schema you intend to document. If a referenced page returns an error or doesn't contain the expected information, flag it — do not guess.

## Step 4: Make targeted updates

For each bullet in the brief, identify the **affected area** (bolded in the brief) and apply the change to the correct file and section.

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

- **Never invent field names, types, or schemas.** Every field you document must come from the API reference or the changelog, not from inference based on the brief's description. If the brief says "new `sanitize` field" but you cannot find its exact type and parent object in the API reference, do not document it.
- **Never write code examples for new features without verifying the exact API shape.** If you cannot fetch or find the API reference for a new feature, add a stub like `<!-- TODO: Add code example — verify schema against API reference -->` instead of guessing.
- **Treat the brief as a table of contents, not a specification.** The brief tells you *which* things changed. The changelog and API reference tell you *how* they changed. Never use the brief's description alone to construct parameter tables or code examples.
- **Never fabricate example values.** If you're adding a code example, use values from the API reference or changelog. Do not invent model IDs, field names, or configuration values that "seem right."

### Risk tiers for changes

**Low risk** (proceed with information from the brief):
- Adding a new enum value to an existing list (e.g., new model ID to a model table)
- Updating a version number
- Adding a new bullet to an existing list of options

**Medium risk** (verify against changelog before editing):
- Adding a new field to an existing parameter table
- Adding a new option to an existing code example

**High risk** (verify against API reference — do not guess):
- Writing a new section with code examples from scratch
- Documenting a new schema or configuration object
- Adding field tables for features that don't already have documentation in the skills

For high-risk changes where you cannot verify the exact schema, add a stub section with the feature name and a brief description, but no code examples or field tables. Note it under "Needs Manual Authoring" in the PR.

### Style rules

- Make minimal, targeted changes. Do not rewrite sections that aren't mentioned in the brief.
- Match the existing style exactly — same heading levels, table formats, code block languages, indentation.
- Keep code examples internally consistent. If a Python example uses `client = ElevenLabs()`, keep that pattern.
- When adding a new model to a table, place it in a logical position (e.g., by quality tier or alphabetically, matching the existing order).
- When adding new parameters to code examples, only add them if they're significant enough to demonstrate. Not every optional field needs a code example.
- If the brief mentions an SDK version bump but no method signature changes, update any version-specific comments but don't change code examples.

## Step 4.5: Self-check before committing

Review every change you made and verify:

1. Every field name in a parameter table appears in the API reference you fetched in Step 3.5.
2. Every code example uses the actual parameter names and nesting from the API reference.
3. You did not add any field, type, or description that you inferred rather than read from the changelog or API reference.
4. No code example contains fabricated values (model IDs, config names, etc.) that you didn't find in the source documentation.

If any change fails this check, revert it. Move it to the "Needs Manual Authoring" section of the PR description instead.

## Step 5: Create branch and PR

```bash
git checkout -b skills-update/YYYY-MM-DD
git add -A
git commit -m "Update skills from changelog YYYY-MM-DD"
git push -u origin HEAD
```

Create the PR:

```bash
gh pr create --repo elevenlabs/skills \
  --title "Update skills — YYYY-MM-DD" \
  --body-file /tmp/skills-pr-body.md
```

The PR body should follow this structure:

```markdown
## Summary

Updates skills based on the weekly changelog brief.

Closes #ISSUE_NUMBER

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

If all changes were verified and applied, write "All items from the brief were applied."

### Source

[Skills Update Brief — YYYY-MM-DD](#ISSUE_NUMBER)
[Changelog YYYY-MM-DD](https://elevenlabs.io/docs/changelog/YYYY-MM-DD)
```

## Important

- Do not modify skills that are not mentioned in the brief.
- Do not update the `openclaw/` directory — that is community-maintained.
- Do not change the YAML frontmatter in SKILL.md files unless the brief specifically calls for it (e.g., description change).
- If the brief mentions a change you cannot verify against the API reference or changelog, do NOT add it to the skill files. Instead, list it in the PR description under "Needs Manual Authoring" with what the brief says and why you couldn't verify it. A wrong code example is worse than a missing one.
- If the brief's Summary says changes are "breaking", add a warning in the PR description highlighting which examples may need migration guidance.

## Note on brief quality

If the brief only provides feature names and high-level descriptions without API reference links or schema details, many items will likely end up under "Needs Manual Authoring." This is the correct outcome — it surfaces gaps for a human to fill rather than hallucinating plausible-looking documentation. Over time, the brief generation process should be improved to include exact field paths, types, and API reference links for each change.
