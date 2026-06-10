---
name: update-skills-from-changelog
description: >
  Update ElevenLabs agent skills from a merged weekly changelog in
  elevenlabs-dx, then open a pull request in elevenlabs/skills. Trigger
  after a changelog merges to main on elevenlabs-dx, or when asked to
  update skills from changelog YYYY-MM-DD.
---

You update ElevenLabs agent skills based on a merged weekly changelog in [elevenlabs-dx](https://github.com/elevenlabs/elevenlabs-dx). Do not read GitHub issues. Open a pull request in this repository when skill files change.

Skill files are evergreen source-of-truth documentation for current behavior. Use the changelog to discover what changed, but write final `SKILL.md` and `references/*.md` content as timeless present-tense documentation.

Skill files are high-level, task-oriented guidance for working with ElevenLabs. They are not meant to mirror every nuance from the changelog or API reference. Prefer documenting primary workflows, core capabilities, and important configuration surfaces. Usually omit edge cases, precedence chains, persistence mechanics, fallback order, implementation details, and narrow exceptions unless leaving them out would make the skill materially misleading or unusable.

## Workflow

1. Resolve `CHANGELOG_DATE` from the automation trigger or user message.
2. Fetch the merged changelog from `elevenlabs-dx` `main`.
3. Apply the relevance filter. Stop if no skills are affected.
4. Read every affected skill file and reference file.
5. Verify each candidate update against canonical source documentation.
6. Apply only targeted, evergreen skill edits that pass the fit gate.
7. Self-check all edits.
8. Create `skills-update/YYYY-MM-DD`, commit, push, and open a PR.

Do not modify skills not implicated by the changelog.

## Step 1: Fetch changelog

Determine `CHANGELOG_DATE` (`YYYY-MM-DD`) from the automation trigger or user message.

Fetch the merged changelog file:

```bash
gh api "repos/elevenlabs/elevenlabs-dx/contents/fern/docs/pages/changelog/${CHANGELOG_DATE}.md?ref=main" \
  --jq '.content' | base64 -d > "/tmp/changelog-${CHANGELOG_DATE}.md"
```

If the file does not exist, stop and report that no merged changelog was found for that date.

Also read the published page when helpful:

`https://elevenlabs.io/docs/changelog#${CHANGELOG_DATE}T00:00:00.000Z`

## Step 2: Apply relevance filter

Read `/tmp/changelog-${CHANGELOG_DATE}.md` and map changes against these skills:

| Skill | What triggers an update |
| --- | --- |
| `text-to-speech` | New/deprecated models, new TTS parameters, voice settings changes, output format changes, SDK method signature changes for `text_to_speech.convert()` |
| `speech-to-text` | New transcription models, new parameters, changed response schemas, SDK method changes |
| `agents` | New LLM providers/models, new tool types, new agent config fields, conversation config schema changes, new CLI commands, widget changes |
| `sound-effects` | New generation parameters, model changes, SDK method changes |
| `music` | New endpoints, new parameters, model changes |
| `voice-isolator` | New parameters, model changes, SDK method changes for `audio_isolation.convert()` |
| `speech-engine` | Speech Engine WebSocket API changes, conversation token changes, SDK method changes for real-time voice conversations |
| `voice-changer` | New speech-to-speech parameters, model changes, SDK method changes for `speech_to_speech.convert()` or `speechToSpeech.convert()` |
| `setup-api-key` | Authentication flow changes, API key dashboard changes, environment variable guidance |

A change is relevant if it affects model tables, code examples, parameter documentation, configuration tables, or CLI commands documented in skills.

A change is not relevant if it only affects internal/admin APIs, optional fields with no usage-level impact, backward-compatible renames, or pricing/dashboard UI unrelated to the API key setup flow.

If no skills are affected, stop successfully without opening a pull request. Report `No skills-relevant changes for CHANGELOG_DATE`.

For each relevant item, note the affected skill and affected area, such as model table, code examples, LLM provider table, tools section, CLI section, parameter documentation, or configuration table.

## Step 3: Read current skill files

For each affected skill, read:

- `{skill}/SKILL.md`
- All files in `{skill}/references/`

Skill directories:

- `text-to-speech/` (`SKILL.md` plus `references/installation.md`, `references/streaming.md`, `references/voice-settings.md`)
- `speech-to-text/` (`SKILL.md` plus `references/installation.md`, `references/transcription-options.md`, `references/realtime-server-side.md`, `references/realtime-client-side.md`, `references/realtime-commit-strategies.md`, `references/realtime-events.md`)
- `agents/` (`SKILL.md` plus `references/installation.md`, `references/agent-configuration.md`, `references/client-tools.md`, `references/widget-embedding.md`, `references/outbound-calls.md`)
- `sound-effects/` (`SKILL.md` plus `references/installation.md`)
- `music/` (`SKILL.md` plus `references/installation.md`, `references/api_reference.md`)
- `voice-isolator/` (`SKILL.md` plus `references/installation.md`)
- `speech-engine/` (`SKILL.md` plus `references/installation.md`, `references/javascript-sdk-reference.md`, `references/python-sdk-reference.md`)
- `voice-changer/` (`SKILL.md` plus `references/installation.md`)
- `setup-api-key/` (`SKILL.md` only)

## Step 4: Verify source documentation

Before editing, fetch and read the actual source material. The changelog tells you what changed; API/reference docs tell you what to document as current behavior.

For common areas, start with:

- Agents: `https://elevenlabs.io/docs/api-reference/agents/create`, `https://elevenlabs.io/docs/api-reference/agents/update`
- TTS: `https://elevenlabs.io/docs/api-reference/text-to-speech/convert`
- STT: `https://elevenlabs.io/docs/api-reference/speech-to-text/convert`

For every documented field, parameter, schema, enum, endpoint, model ID, or SDK method:

- Verify the exact field name, type, nesting, allowed values, and method signature in source documentation.
- Never infer schemas from changelog wording.
- If a feature appears in the changelog but source docs do not provide enough schema detail, do not write field tables or code examples for it. Put it under `Needs Manual Authoring` in the report.

## Step 5: Decide whether each item belongs

Run this fit gate before editing each changelog item:

1. Map to a natural home in an existing section, table, list, or example.
2. Include only primary capabilities, common workflows, or important top-level configuration concepts.
3. Skip secondary nuances: edge cases, precedence rules, persistence details, fallback order, implementation details, narrow exceptions, or deprecation notes.
4. Prefer no-op over forced structure. If no natural home exists, leave skill files unchanged and report it under `No Skill Change Needed`.
5. Add a new section only when the concept is substantial, reusable, user-facing, high-level, and clearly missing from current structure.
6. Prefer the current path. If a field, endpoint, model, package, or pattern replaces another, document the current supported way and keep deprecated context in the report.

Good fits:

- Add a new supported model row to an existing model table.
- Add a new top-level parameter to an existing parameter table.
- Update existing Python, JavaScript, and cURL examples when method signatures change.

Bad fits:

- Insert a standalone sentence between unrelated sections just to mention a changelog item.
- Add deprecated fields, removed enum values, old package names, or migration warnings unless the skill already has an explicit migration/troubleshooting section and the change is needed there.
- Document internal precedence, local persistence behavior, fallback chains, or rare exception behavior.

## Step 6: Make targeted edits

Apply the smallest useful change to the correct file and section. Match existing heading levels, table formats, code block languages, indentation, and naming style.

Update patterns:

- **Model table:** add, remove, or modify rows in the relevant `SKILL.md` model table. Verify model IDs and descriptions.
- **Code examples:** update method signatures, imports, and significant parameters. Keep Python, JavaScript, and cURL examples consistent when all exist.
- **LLM provider table:** update `agents/SKILL.md` or `agents/references/agent-configuration.md`.
- **Tools section:** update `agents/SKILL.md` with new tool types in the existing style.
- **CLI section:** update existing CLI examples in `agents/` files.
- **Parameter documentation:** add verified parameters to the relevant parameter list or table.
- **Configuration tables:** update field tables in reference files such as `agent-configuration.md` or `voice-settings.md`.
- **Output format table:** update the output format table in `text-to-speech/SKILL.md`.

Hard rules:

- Never invent field names, types, schemas, model IDs, config names, endpoint paths, or example values.
- Never write code examples for new features without verifying the exact API shape.
- Treat the changelog as discovery input, not skill-file prose.
- Skill files must be evergreen. Never mention changelog, issue, PR, release date, "added in", "introduced in", "as of", or "now supports" inside `SKILL.md` or `references/*.md`.
- Document current positive workflows, not negative history.
- Do not create a new section solely because a changelog bullet exists.
- Do not insert orphan content.
- Keep tables focused on supported current fields.
- If an SDK version bump has no method signature change, update version-specific comments only if such comments already exist.

## Step 7: Self-check before committing

Review every change and verify:

1. Every edited field name appears in the source docs read in Step 4.
2. Every code example uses verified parameter names and nesting.
3. No content was inferred from changelog wording alone.
4. No fabricated values remain.
5. No edited skill file references a changelog, issue, PR, release date, or release-history phrasing.
6. Every new heading or section is justified by Step 5.
7. No orphan sentences or forced one-off sections remain.
8. No edited content documents deprecated, removed, or replaced fields solely as negative guidance.
9. Every relevant changelog item is accounted for as one of: docs update, justified new section, `No Skill Change Needed`, or `Needs Manual Authoring`.

If any change fails this check, revert that edit and move the item to `Needs Manual Authoring` or `No Skill Change Needed`.

## Step 8: Branch, commit, and pull request

Use branch name `skills-update/YYYY-MM-DD`.

Before creating a branch, check for an existing open PR and stop if one exists:

```bash
gh pr list --repo elevenlabs/skills --head "skills-update/${CHANGELOG_DATE}" --state open --json number --jq 'length == 0'
```

Create the branch from current `origin/main`, commit only if files changed, and push:

```bash
git fetch origin main
git checkout -b "skills-update/${CHANGELOG_DATE}" origin/main
git add -A
git diff --cached --quiet || git commit -m "Update skills from changelog ${CHANGELOG_DATE}"
git push -u origin "skills-update/${CHANGELOG_DATE}"
```

Write the report to `/tmp/skills-update-report.md`, then open the PR:

```bash
gh pr create --repo elevenlabs/skills \
  --base main \
  --head "skills-update/${CHANGELOG_DATE}" \
  --title "Update skills from changelog ${CHANGELOG_DATE}" \
  --body-file /tmp/skills-update-report.md
```

If there are no file changes after analysis, do not push or open a PR. Report `No skill file changes needed for CHANGELOG_DATE` with relevant items under `No Skill Change Needed`.

## Report and PR body requirements

Write this report and use it as the PR body:

```markdown
# Skills Update Report

## Outcome

- Changelog: `YYYY-MM-DD`
- Branch: `skills-update/YYYY-MM-DD`
- Commit: `<commit sha or "No commit created">`
- Pull request: `<PR URL or "No PR created">`
- Result: `<updated skills | no skill changes needed | partial update>`

## Summary

Updates skills based on the merged weekly changelog.

If the changelog describes breaking API or SDK changes, add a short warning here describing which examples or docs may need migration guidance.

### Changes

- **skill-name**: Brief description of what changed.

### Verification

- `field_or_area` in `file.md` - verified against [API reference page](url)

### Needs Manual Authoring

List changelog items that were not applied because the schema could not be verified. Include what the changelog said, why it could not be verified, and the source link to check later.

If no items apply, write "None."

### No Skill Change Needed

List verified changelog items intentionally not added to skill files because they have no natural home or are too low-level for skills. Include what changed, why no edit was appropriate, and the source link.

If no items apply, write "None."

### Open Questions

List blockers, ambiguous source material, or follow-up items.

If no items apply, write "None."

### Source

[Changelog YYYY-MM-DD](https://elevenlabs.io/docs/changelog#YYYY-MM-DDT00:00:00.000Z)
[Changelog file on GitHub](https://github.com/elevenlabs/elevenlabs-dx/blob/main/fern/docs/pages/changelog/YYYY-MM-DD.md)
```

When run in an automated/headless agent environment with repository write access, opening the pull request is required unless no skill files changed. Return only the completed markdown report in the final response unless the invoking user explicitly asks for extra commentary.

## Important

- Do not change YAML frontmatter in skill files unless the changelog specifically requires it.
- Keep changelog dates and release-history wording in the report/PR context only.
- Prefer no-op over forced structure when a changelog item has no natural home.
- A wrong code example is worse than a missing one.
- If changelog coverage only gives feature names and high-level descriptions without source docs or schema details, put those items under `Needs Manual Authoring`.
