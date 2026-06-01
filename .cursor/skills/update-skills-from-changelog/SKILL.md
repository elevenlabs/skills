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

Use `.claude/commands/update-skills.md` as the source of truth for the exact changelog fetch command, the relevance filter, the detailed editing rules from **Step 3.5** onward, and the pull request creation flow. This skill adds the Cursor Cloud Automation trigger handling and stop conditions around that workflow.

## Trigger input

Determine `CHANGELOG_DATE` (`YYYY-MM-DD`) from the automation trigger or user message.

Fetch the changelog markdown from `elevenlabs-dx` `main` using the command in `.claude/commands/update-skills.md` **Step 1**.

Also read the live page from **Step 1** when helpful:

`https://elevenlabs.io/docs/changelog#${CHANGELOG_DATE}T00:00:00.000Z`

## Relevance filter (required before editing)

Apply the relevance filter in `.claude/commands/update-skills.md` **Step 2** to determine whether any skills are affected.

If **no skills are affected**, stop successfully. Do not open a pull request. Report `No skills-relevant changes for CHANGELOG_DATE`.

## Workflow

1. Resolve `CHANGELOG_DATE` and fetch the merged changelog from `elevenlabs-dx` `main`.
2. Apply the relevance filter. Exit without a PR if nothing qualifies.
3. For each affected skill, read `{skill}/SKILL.md` and `{skill}/references/`.
4. Follow `.claude/commands/update-skills.md` **Step 3.5 through Step 4.5** for verification, fit decisions, edits, and self-checks.
5. Create a branch, commit if needed, and open a pull request.

Do not modify skills not implicated by the changelog. Do not edit `openclaw/`.

## Branch, commit, and pull request

Use branch name `skills-update/YYYY-MM-DD`.

Before creating a branch, run the open-PR check from `.claude/commands/update-skills.md` **Step 5** and stop if it reports an existing PR for that date.

Write the pull request body to `/tmp/skills-update-report.md` using the report template from `.claude/commands/update-skills.md` **Step 5**, replacing issue references with the changelog source link.

Create the branch, commit, push, and open the pull request using the commands in `.claude/commands/update-skills.md` **Step 5**.

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
