---
name: verify-skills-catalog
description: "Drive the ElevenLabs skills catalog with the skills CLI (npx skills 1.5.18). Use to prove list, install, prompt render, installed-list, and remove against an isolated project directory. There is no app server."
---

# Verify the skills catalog

The user-facing surface is the skills CLI. This repository is a catalog of agent skills. It does not start a web server, and `evals/run_all.py` is a maintainer runner, not this surface.

Users list the catalog, install a skill into a project, render a skill prompt, list what is installed, and remove a skill. Cursor project installs copy into `./.agents/skills/<name>/` and write `skills-lock.json` in the project directory. Global installs (`-g`) write under the home directory and are out of scope.

The catalog root is the checkout that contains this skill. The helper resolves it from its own path. Commands below use `$SKILLS_CATALOG` for that root and `$VERIFY_PROJECT` for a disposable directory under `/tmp`.

## Launch

There is no process to keep alive. Launch resolves the CLI once, then each later command starts its own `npx skills` process with cwd set to the disposable project.

```bash
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh launch
```

That command runs `mktemp -d /tmp/verify-skills-catalog.XXXXXX`, records the path in the evidence `session.env`, and runs:

```bash
npx --yes skills --version
```

Ready when stdout is exactly `1.5.18` and stderr is empty. The new directory exists and does not contain `.agents/skills/text-to-speech` or `skills-lock.json`.

Teardown is [Cleanup](#cleanup). Do not leave the disposable directory in place after the run.

## Doctor

Run this before a drive, and again whenever the CLI output looks wrong. It is read-only: it does not install, remove, or edit the catalog.

```bash
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh doctor
```

From `$VERIFY_PROJECT` the helper runs:

```bash
npx --yes skills --version
npx --yes skills add "$SKILLS_CATALOG" --list
npx --yes skills list --agent cursor --json
```

The instance is worth driving when all three succeed and:

- version stdout is `1.5.18`
- the catalog listing's skill-name lines are `agents`, `dubbing`, `music`, `setup-api-key`, `sound-effects`, `speech-engine`, `speech-to-text`, `text-to-speech`, `voice-changer`, `voice-isolator`, and `update-skills-from-changelog`
- installed JSON is `[]`
- `$VERIFY_PROJECT` is still free of `text-to-speech` and `skills-lock.json`

Refuse to drive when the project path is `$HOME`, the catalog checkout, or anywhere outside `/tmp/verify-skills-catalog.*`. The `--list` banner says `Agent detected — installing non-interactively` even though `--list` writes no files. An install is proved by the project tree, not by that banner.

## Drive

The harness is the skills CLI. These commands are non-interactive when `--list`, `--json`, and `-y` are present, so a PTY is not required. Run each command in its own shell with cwd `$VERIFY_PROJECT` unless the feature file says otherwise. Do not pass `-g` or `--global`. Do not pass `--agent` to `skills use`.

Record stdout, stderr, and the exit code for every command. The feature map in `features/` is the source for the other entry points. The helper automates one of them:

```bash
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh drive install-text-to-speech
```

That runs, with cwd `$VERIFY_PROJECT`:

```bash
npx --yes skills add "$SKILLS_CATALOG" --skill text-to-speech --agent cursor -y --copy
npx --yes skills list --agent cursor --json
```

A passing install exits 0, prints `Selected 1 skill: text-to-speech` and `text-to-speech (copied)`, and leaves a regular file at `.agents/skills/text-to-speech/SKILL.md` that is byte-identical to `$SKILLS_CATALOG/text-to-speech/SKILL.md`. `skills-lock.json` has `version` 1 and `skills.text-to-speech.sourceType` `local`, with `source` equal to the absolute catalog path. The follow-up list is one object: `name` `text-to-speech`, `scope` `project`, `agents` `["Cursor"]`, `path` `$VERIFY_PROJECT/.agents/skills/text-to-speech`.

## Evidence

Write proof to `$VERIFY_SKILLS_EVIDENCE_DIR` when that variable is set. Otherwise the helper writes `.cursor/skills/verify-skills-catalog/evidence/latest/` (gitignored). Both locations are outside the disposable project.

For `install-text-to-speech`, keep:

- `feature-id.txt` containing `install-text-to-speech`
- `transcript/commands.log` plus `transcript/drive-install.stdout`, `transcript/drive-install.stderr`, and `transcript/drive-install.exit`
- `transcript/list-after.stdout` from the follow-up list
- `installed/skills-lock.json`
- `installed/.agents/skills/text-to-speech/` including `SKILL.md` and `references/`

Capture the command and the resulting state. The file copy and the list JSON are both required. Compare `SKILL.md` to the catalog with `cmp`. Do not call ElevenLabs speech APIs, do not set `ELEVENLABS_API_KEY`, and do not mock the CLI. `--copy` is the real install mode, not a dry run.

## Cleanup

```bash
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh cleanup
```

With cwd `$VERIFY_PROJECT`, that runs:

```bash
npx --yes skills remove --skill text-to-speech --agent cursor -y
```

Then it deletes `$VERIFY_PROJECT` and only that directory. `skills remove` deletes `.agents/skills/text-to-speech` and leaves both the empty `.agents/skills` directory and `skills-lock.json` (the lock entry is unchanged). The project delete removes those leftovers. After cleanup, `test ! -d "$VERIFY_PROJECT"` and the evidence files named above still exist. Cleanup never deletes `$VERIFY_SKILLS_EVIDENCE_DIR` or `.cursor/skills/verify-skills-catalog/evidence/`.

Run cleanup after a failed drive too, so a broken attempt does not leave a project under `/tmp`.

## Helpers

`scripts/verify-skills-catalog.sh` is the harness. From the catalog root:

```bash
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh launch
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh doctor
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh drive install-text-to-speech
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh cleanup
```

`drive` accepts only `install-text-to-speech`. The other features in `features/` are driven with the `npx skills` commands in those files. Launch fails if `session.env` already exists; run cleanup first. Cleanup of a finished run leaves `session.env` in the evidence directory, so the next launch needs a new `VERIFY_SKILLS_EVIDENCE_DIR` or a fresh `evidence/latest` directory.
