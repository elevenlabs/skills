# List installed skills

List installed skills shows which skills are installed for Cursor in the current project.

## Sub-features

- `list-empty` prints an empty array before any install.
- `list-one` prints the `text-to-speech` install after the install feature.

## How to get to it (user POV)

- From a project directory, run `npx skills list --agent cursor`.
- Add `--json` for a stable machine-readable list.

## Driving it with the skills CLI

Preconditions:

- `$VERIFY_PROJECT` exists under `/tmp/verify-skills-catalog.*` and is the shell cwd.
- `doctor` has already shown the empty list for this project.

- **Empty project.** List before installing. Run `npx --yes skills list --agent cursor --json`. Exit code `0` and stdout is `[]`.
- **After install.** Install with the [Install text-to-speech](./install-text-to-speech.md) command, then list again. Run `npx --yes skills list --agent cursor --json`. Exit code `0` and the array contains one object whose `name` is `text-to-speech`, `scope` is `project`, and `agents` is `["Cursor"]`.
- **Proof.** Save both JSON documents. The empty document is the baseline. The one-object document is the post-install state.

## Gotchas

- Omit `-g`. Without `-g`, the CLI lists the project at cwd, not the home directory.
- A leftover `skills-lock.json` does not make the list non-empty. The list follows skill directories that contain `SKILL.md`.
- Listing from the catalog checkout sees `update-skills-from-changelog` because that skill already lives in the repo's `.agents/skills`. List from `$VERIFY_PROJECT` instead.
- Human-readable `skills list` output is not the assertion format. Pass `--json`.
