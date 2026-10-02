# Install the catalog

Install the catalog follows the README and installs every skill from `elevenlabs/skills` into the current Cursor project.

## Sub-features

- `install-github` clones `https://github.com/elevenlabs/skills.git` and copies all 11 skills.
- `install-lock` writes a GitHub `skills-lock.json` entry for each skill.
- `install-list` shows those skills from a second command.

## How to get to it (user POV)

- From a project directory, run `npx skills add elevenlabs/skills`.

## Driving it with the skills CLI

Preconditions:

- `$VERIFY_PROJECT` exists under `/tmp/verify-skills-catalog.*`, is the shell cwd, and is not `$HOME` or `$SKILLS_CATALOG`.
- `CURSOR_AGENT` is set, so skills CLI 1.5.18 installs non-interactively.
- The project does not yet contain `.agents/skills` or `skills-lock.json`.
- `npx --yes skills list -g --agent cursor --json` has been recorded so a later list can show the home directory did not change.

- **Install.** Run the README command. Run `npx --yes skills add elevenlabs/skills`. `npx --yes` only skips the npm package prompt. Exit code `0`, stderr empty, and stdout contains `https://github.com/elevenlabs/skills.git`, `Found 11 skills`, `Installing all 11 skills`, `text-to-speech (copied)`, and `Installed 11 skills`.
- **Confirm the copy.** Read `.agents/skills/text-to-speech/SKILL.md`. It is a regular file, not a symlink, and `cmp` against `$SKILLS_CATALOG/text-to-speech/SKILL.md` reports no differences. `references/installation.md`, `references/streaming.md`, and `references/voice-settings.md` exist beside it. The other ten skill directories exist under `.agents/skills/` as regular files too.
- **Confirm the lock.** Read `skills-lock.json`. `version` is `1`. Every skill's `source` is `elevenlabs/skills`, `sourceType` is `github`, `skillPath` ends in `SKILL.md`, and `computedHash` is 64 hexadecimal characters. `skills.text-to-speech.skillPath` is `text-to-speech/SKILL.md`.
- **Confirm from list.** Ask for installed skills. Run `npx --yes skills list --agent cursor --json`. Exit code `0` and the array contains the 11 catalog skills. Each object's `scope` is `project`, `agents` is `["Cursor"]`, and `path` is `$VERIFY_PROJECT/.agents/skills/<name>`.
- **Confirm the home directory.** Run `npx --yes skills list -g --agent cursor --json` again. It matches the list recorded before install.
- **Proof.** Save the install transcript and a copy of `skills-lock.json` and `.agents/skills/` under the evidence directory. The helper does this when you run `.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh launch` and then `drive install-catalog`.

## Gotchas

- `-g` installs into `~/.cursor/skills`. Do not pass it.
- `--skill`, `--agent`, `-y`, and `--copy` are not in the README command. Do not add them. With `CURSOR_AGENT` set, the CLI already selects every skill and copies them into `.agents/skills`.
- Without `CURSOR_AGENT`, the same command opens a picker and waits. Launch refuses that case.
- Running the add command with cwd set to the catalog checkout writes into the catalog. Keep cwd on `$VERIFY_PROJECT`.
- The success banner is not enough. The copied `SKILL.md`, the lock file, and the list JSON all have to match.
