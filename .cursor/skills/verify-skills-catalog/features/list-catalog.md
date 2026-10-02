# List the catalog

List the catalog shows the skills in this repository without installing them into the project.

## Sub-features

- `list-names` prints the eleven skill names in this checkout.
- `list-no-write` leaves the disposable project empty.

## How to get to it (user POV)

- Run `npx skills add <catalog> --list` against this repository.

## Driving it with the skills CLI

Preconditions:

- `$VERIFY_PROJECT` exists under `/tmp/verify-skills-catalog.*` and is the shell cwd.
- `doctor` reports skills CLI `1.5.18`, and `npx --yes skills list --agent cursor --json` prints `[]`.

- **List skills.** Ask the CLI for the catalog. Run `npx --yes skills add "$SKILLS_CATALOG" --list`. Exit code `0`, stderr empty, and the skill-name lines are `agents`, `dubbing`, `music`, `setup-api-key`, `sound-effects`, `speech-engine`, `speech-to-text`, `text-to-speech`, `voice-changer`, `voice-isolator`, and `update-skills-from-changelog`.
- **Confirm nothing was installed.** List the project again. Run `npx --yes skills list --agent cursor --json`. Stdout is `[]`. `$VERIFY_PROJECT` still has no `skills-lock.json` and no `.agents/skills/text-to-speech`.

## Gotchas

- The banner `Agent detected — installing non-interactively` appears for `--list` and does not mean an install happened.
- `update-skills-from-changelog` is part of this catalog. A listing that stops at the README table is short one skill.
- Running `skills add` without `--list` installs. This feature always passes `--list`.
