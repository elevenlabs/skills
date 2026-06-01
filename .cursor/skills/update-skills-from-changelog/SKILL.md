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

For detailed editing rules, verification gates, self-checks, and style constraints, follow `.claude/commands/update-skills.md` from **Step 3.5** onward. This skill covers trigger handling, changelog ingestion, relevance filtering, and pull request creation.

## Trigger input

Determine `CHANGELOG_DATE` (`YYYY-MM-DD`) from the automation trigger or user message.

Fetch the changelog markdown from `elevenlabs-dx` `main`:

```bash
gh api "repos/elevenlabs/elevenlabs-dx/contents/fern/docs/pages/changelog/${CHANGELOG_DATE}.md?ref=main" \
  --jq '.content' | base64 -d > "/tmp/changelog-${CHANGELOG_DATE}.md"
```

Also read the live page when helpful:

`https://elevenlabs.io/docs/changelog#${CHANGELOG_DATE}T00:00:00.000Z`

## Relevance filter (required before editing)

Analyze the changelog against these skills:

| Skill            | What triggers an update                                                                                                                               |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `text-to-speech` | New/deprecated models, new TTS parameters, voice settings changes, output format changes, SDK method signature changes for `text_to_speech.convert()` |
| `speech-to-text` | New transcription models, new parameters, changed response schemas, SDK method changes                                                                |
| `agents`         | New LLM providers/models, new tool types, new agent config fields, conversation config schema changes, new CLI commands, widget changes               |
| `sound-effects`  | New generation parameters, model changes, SDK method changes                                                                                          |
| `music`          | New endpoints, new parameters, model changes                                                                                                          |
| `voice-isolator` | New parameters, model changes, SDK method changes for `audio_isolation.convert()`                                                                     |
| `setup-api-key`  | Authentication flow changes, new environment variables                                                                                                |

A change is relevant if it affects model tables, code examples, parameter documentation, configuration tables, or CLI commands documented in skills.

A change is **not** relevant if it only affects internal/admin APIs, optional fields with no usage-level impact, backward-compatible renames, or pricing/dashboard UI.

If **no skills are affected**, stop successfully. Do not open a pull request. Report `No skills-relevant changes for CHANGELOG_DATE`.

## Workflow

1. Resolve `CHANGELOG_DATE` and fetch the merged changelog from `elevenlabs-dx` `main`.
2. Apply the relevance filter. Exit without a PR if nothing qualifies.
3. For each affected skill, read `{skill}/SKILL.md` and `{skill}/references/`.
   If `voice-isolator` is affected, read `voice-isolator/SKILL.md` and `voice-isolator/references/installation.md`.
4. Follow `.claude/commands/update-skills.md` **Step 3.5 through Step 4.5** for verification, fit decisions, edits, and self-checks.
5. Create a branch, commit if needed, and open a pull request.

Do not modify skills not implicated by the changelog. Do not edit `openclaw/`.

## Branch, commit, and pull request

Use branch name `skills-update/YYYY-MM-DD`.

Before creating a branch, skip if an open PR already exists for that date:

```bash
gh pr list --repo elevenlabs/skills --head "skills-update/${CHANGELOG_DATE}" --state open --json number --jq 'length == 0'
```

Create the branch and commit:

```bash
git fetch origin main
git checkout -b "skills-update/${CHANGELOG_DATE}" origin/main
git add -A
git diff --cached --quiet || git commit -m "Update skills from changelog ${CHANGELOG_DATE}"
git push -u origin "skills-update/${CHANGELOG_DATE}"
```

Write the pull request body to `/tmp/skills-update-report.md` using the report template from `.claude/commands/update-skills.md` **Step 5**, replacing issue references with the changelog source link.

Open the pull request:

```bash
gh pr create --repo elevenlabs/skills \
  --base main \
  --head "skills-update/${CHANGELOG_DATE}" \
  --title "Update skills from changelog ${CHANGELOG_DATE}" \
  --body-file /tmp/skills-update-report.md
```

If there are no file changes after analysis, do not push or open a PR. Report `No skill file changes needed for CHANGELOG_DATE` with items listed under **No Skill Change Needed**.

## Report and PR body requirements

The PR body must include:

- **Outcome** — changelog date, branch, commit SHA or `No commit created`, result
- **Summary** — short overview; note breaking changes if any
- **Changes** — per-skill bullet list
- **Verification** — API reference links used
- **Needs Manual Authoring** — unverified items
- **No Skill Change Needed** — verified changelog items intentionally omitted from skill files
- **Open Questions** — blockers, if any
- **Source** — link to `https://elevenlabs.io/docs/changelog#YYYY-MM-DDT00:00:00.000Z`

Never put changelog dates, issue numbers, or release-history phrasing inside `SKILL.md` or `references/*.md`.

## Important

- Never invent field names, types, or schemas.
- Verify every documented field against the ElevenLabs API reference.
- Prefer no-op over forced structure when a changelog item has no natural home in skill docs.
- A wrong code example is worse than a missing one.
