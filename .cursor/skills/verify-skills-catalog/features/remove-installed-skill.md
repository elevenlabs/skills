# Remove an installed skill

Remove an installed skill deletes the copied `text-to-speech` directory from the Cursor project. The project list is empty afterward. `skills-lock.json` stays until the project directory is deleted.

## Sub-features

- `remove-directory` deletes `.agents/skills/text-to-speech`.
- `remove-list` shows an empty Cursor project list.
- `remove-lock-remains` leaves `skills-lock.json` in the project.

## How to get to it (user POV)

- From the project directory, run `npx skills remove --skill text-to-speech --agent cursor`.

## Driving it with the skills CLI

Preconditions:

- The [Install text-to-speech](./install-text-to-speech.md) feature has just succeeded in `$VERIFY_PROJECT`.
- `$VERIFY_PROJECT` is the shell cwd.
- Proof copies of the installed files already live in the evidence directory.

- **Remove.** Uninstall the skill. Run `npx --yes skills remove --skill text-to-speech --agent cursor -y`. Exit code `0`, stderr empty, and stdout contains `Successfully removed 1 skill(s)`.
- **Confirm the directory is gone.** `.agents/skills/text-to-speech` does not exist. `.agents/skills` remains as an empty directory.
- **Confirm the list.** Run `npx --yes skills list --agent cursor --json`. Stdout is `[]`.
- **Confirm the lock leftover.** `skills-lock.json` is still present and still has `skills.text-to-speech.sourceType` set to `local`.
- **Delete scratch.** Remove `$VERIFY_PROJECT` with `rm -rf` after the evidence copy exists. The evidence directory still contains the install transcript and the copied skill files.

## Gotchas

- `skills remove` does not delete `skills-lock.json` or the empty `.agents/skills` directory. A later `experimental_install` would see the stale lock. The verification cleanup deletes the whole disposable project.
- Do not `rm` the evidence directory while deleting the project.
- `-g` would remove a home-directory install. Do not pass it.
