---
name: verify-skills-catalog
description: "Drive the ElevenLabs skills catalog the way the README installs it: npx skills add elevenlabs/skills. Use to prove that install in an isolated project. There is no app server."
---

# Verify the skills catalog

The user-facing surface is the skills CLI. This repository is a catalog of agent skills. It does not start a web server, and `evals/run_all.py` is a maintainer runner, not this surface.

The README installation command is:

```bash
npx skills add elevenlabs/skills
```

That command clones `https://github.com/elevenlabs/skills.git` and installs the catalog into the current project. Cursor project installs land in `./.agents/skills/<name>/` and write `skills-lock.json` beside them. Global installs (`-g`) write under the home directory and are out of scope.

The catalog root is the checkout that contains this skill. The helper resolves it from its own path. Commands below use `$SKILLS_CATALOG` for that root and `$VERIFY_PROJECT` for a disposable directory under `/tmp`.

## Launch

There is no process to keep alive. Launch resolves the CLI, creates a disposable project, and runs the README install in that project.

```bash
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh launch
```

That command runs `mktemp -d /tmp/verify-skills-catalog.XXXXXX`, records the path in the evidence `session.env`, and then runs:

```bash
npx --yes skills --version
npx --yes skills list -g --agent cursor --json
npx --yes skills add elevenlabs/skills
npx --yes skills list -g --agent cursor --json
```

`npx --yes` only skips npm's package-install prompt. The skills arguments are exactly the README's `add elevenlabs/skills`. Do not add `--skill`, `--agent`, `-y`, `--copy`, or `-g`.

The add command's cwd is `$VERIFY_PROJECT`. With `CURSOR_AGENT` set, skills CLI 1.5.18 detects `cursor-cli` and installs every skill in the catalog without a prompt. On this catalog that is 11 skills, copied as regular files into `.agents/skills/`.

Ready when:

- version stdout is exactly `1.5.18`
- the add command exits 0 and its stderr is empty
- add stdout contains `https://github.com/elevenlabs/skills.git`, `Found 11 skills`, `Installing all 11 skills`, `text-to-speech (copied)`, and `Installed 11 skills`
- `skills-lock.json` has `version` 1 and each skill's `source` is `elevenlabs/skills` and `sourceType` is `github`
- the global Cursor list is unchanged, so nothing was written under the home directory

The new directory must not already contain `.agents/skills` or `skills-lock.json`. Launch fails if `CURSOR_AGENT` is unset, because the same command would then open a skill picker and wait.

Teardown is [Cleanup](#cleanup). Do not leave the disposable directory in place after the run.

## Doctor

Run this after launch, and again whenever the CLI output looks wrong. It is read-only: it does not install, remove, or edit the catalog.

```bash
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh doctor
```

From `$VERIFY_PROJECT` the helper runs:

```bash
npx --yes skills --version
npx --yes skills add "$SKILLS_CATALOG" --list
npx --yes skills list --agent cursor --json
```

It also reads `skills-lock.json` and compares `.agents/skills/text-to-speech/SKILL.md` to `$SKILLS_CATALOG/text-to-speech/SKILL.md`. A last `npx --yes skills list -g --agent cursor --json` must match the global list captured before the README install.

The instance is worth driving when all of these hold:

- version stdout is `1.5.18`
- the local catalog listing's skill-name lines are `agents`, `dubbing`, `music`, `setup-api-key`, `sound-effects`, `speech-engine`, `speech-to-text`, `text-to-speech`, `voice-changer`, `voice-isolator`, and `update-skills-from-changelog`
- the project list is those same 11 skills, each with `scope` `project` and `agents` `["Cursor"]`
- `text-to-speech` `SKILL.md` is a regular file and `cmp` reports no differences
- the global Cursor list is unchanged

Refuse to drive when the project path is `$HOME`, the catalog checkout, or anywhere outside `/tmp/verify-skills-catalog.*`. The `--list` banner says `Agent detected — installing non-interactively` even though `--list` writes no files. The README install is proved by the project tree and `skills-lock.json`, not by that banner.

## Drive

The harness is the skills CLI. Launch already ran the README install. Drive records that result. It does not run a second, different add command.

```bash
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh drive install-catalog
```

That re-reads the project and, with cwd `$VERIFY_PROJECT`, runs:

```bash
npx --yes skills list --agent cursor --json
```

A passing drive leaves a regular file at `.agents/skills/text-to-speech/SKILL.md` that is byte-identical to `$SKILLS_CATALOG/text-to-speech/SKILL.md`. `skills-lock.json` has `version` 1, and `skills.text-to-speech.source` is `elevenlabs/skills`, `sourceType` is `github`, and `skillPath` is `text-to-speech/SKILL.md`. The list is the 11 catalog skills, each with `scope` `project`, `agents` `["Cursor"]`, and `path` `$VERIFY_PROJECT/.agents/skills/<name>`.

## Evidence

Write proof to `$VERIFY_SKILLS_EVIDENCE_DIR` when that variable is set. Otherwise the helper writes `.cursor/skills/verify-skills-catalog/evidence/latest/` (gitignored). Both locations are outside the disposable project.

For `install-catalog`, keep:

- `feature-id.txt` containing `install-catalog`
- `transcript/commands.log` plus `transcript/launch-add.stdout`, `transcript/launch-add.stderr`, and `transcript/launch-add.exit`
- `transcript/list-after.stdout` from the follow-up list
- `installed/skills-lock.json`
- `installed/.agents/skills/` including `text-to-speech/SKILL.md`

Capture the README command and the resulting state. The file copy and the list JSON are both required. Compare `text-to-speech/SKILL.md` to the catalog with `cmp`. Do not call ElevenLabs speech APIs, do not set `ELEVENLABS_API_KEY`, and do not mock the CLI.

## Cleanup

```bash
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh cleanup
```

That deletes `$VERIFY_PROJECT` and only that directory. It does not run `skills remove`, and it does not delete anything under `$HOME`. After cleanup, `test ! -d "$VERIFY_PROJECT"` and the evidence files named above still exist. Cleanup never deletes `$VERIFY_SKILLS_EVIDENCE_DIR` or `.cursor/skills/verify-skills-catalog/evidence/`.

Run cleanup after a failed drive too, so a broken attempt does not leave a project under `/tmp`.

## Helpers

`scripts/verify-skills-catalog.sh` is the harness. From the catalog root:

```bash
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh launch
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh doctor
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh drive install-catalog
.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh cleanup
```

`drive` accepts only `install-catalog`. The other features in `features/` are different CLI entry points and are not what launch runs. Launch fails if `session.env` already exists; run cleanup first. Cleanup of a finished run leaves `session.env` in the evidence directory, so the next launch needs a new `VERIFY_SKILLS_EVIDENCE_DIR` or a fresh `evidence/latest` directory.
