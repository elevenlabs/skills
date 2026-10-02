# Install text-to-speech

Install text-to-speech copies the `text-to-speech` skill into a Cursor project and records that install in `skills-lock.json`.

## Sub-features

- `install-copy` copies the skill into `.agents/skills/text-to-speech`.
- `install-lock` writes a local `skills-lock.json` entry.
- `install-list` shows the installed skill from a second command.

## How to get to it (user POV)

- From a project directory, run `npx skills add <catalog> --skill text-to-speech --agent cursor --copy`.

## Driving it with the skills CLI

Preconditions:

- `$VERIFY_PROJECT` exists under `/tmp/verify-skills-catalog.*`, is the shell cwd, and is not `$HOME` or `$SKILLS_CATALOG`.
- `doctor` reports skills CLI `1.5.18` and an empty Cursor project list.
- `$SKILLS_CATALOG/text-to-speech/SKILL.md` exists.

- **Install.** Copy the skill into the project. Run `npx --yes skills add "$SKILLS_CATALOG" --skill text-to-speech --agent cursor -y --copy`. Exit code `0`, stderr empty, and stdout contains `Selected 1 skill: text-to-speech` and `text-to-speech (copied)`.
- **Confirm the copy.** Read `.agents/skills/text-to-speech/SKILL.md`. It is a regular file, not a symlink, and `cmp` against `$SKILLS_CATALOG/text-to-speech/SKILL.md` reports no differences. `references/installation.md`, `references/streaming.md`, and `references/voice-settings.md` exist beside it.
- **Confirm the lock.** Read `skills-lock.json`. `version` is `1`. `skills.text-to-speech.source` is the absolute `$SKILLS_CATALOG` path, `sourceType` is `local`, and `computedHash` is 64 hexadecimal characters.
- **Confirm from list.** Ask for installed skills. Run `npx --yes skills list --agent cursor --json`. Exit code `0` and the array contains one object whose `name` is `text-to-speech`, `scope` is `project`, `agents` is `["Cursor"]`, and `path` is `$VERIFY_PROJECT/.agents/skills/text-to-speech`.
- **Proof.** Save the install transcript and a copy of `skills-lock.json` and `.agents/skills/text-to-speech/` under the evidence directory. The helper does this when you run `.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh drive install-text-to-speech`.

## Gotchas

- `-g` installs into `~/.cursor/skills`. Do not pass it.
- Running the add command with cwd set to the catalog checkout writes into the catalog. Keep cwd on `$VERIFY_PROJECT`.
- Without `--copy`, the CLI may symlink. This proof passes `--copy` and rejects a symlink at `SKILL.md`.
- The success banner is not enough. The copied `SKILL.md` and the list JSON both have to match.
