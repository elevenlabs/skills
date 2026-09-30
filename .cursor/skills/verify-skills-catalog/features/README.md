# Skills catalog verification map

This directory is the maintained source for verifying the user-facing behavior of the ElevenLabs skills catalog. Read the index before driving the CLI, then use the matching feature file as the recipe.

The surface is `npx skills` 1.5.18 against this repository. There is no app server.

## Baseline preconditions

- Resolve `$SKILLS_CATALOG` to the checkout that contains `.cursor/skills/verify-skills-catalog`.
- Launch with `.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh launch`, which creates `$VERIFY_PROJECT` under `/tmp/verify-skills-catalog.*`.
- Require `npx --yes skills --version` to print `1.5.18`.
- Run the helper's `doctor` and require that catalog listing, an empty Cursor project list, and a project that does not yet contain `text-to-speech`.
- Never drive `$HOME`, the catalog checkout, or a project the verification run did not create.

## Driving conventions

- Start every recipe from the doctor baseline unless its preconditions say otherwise.
- Treat every command as literal. Keep quoted flags unchanged.
- Run install, list, and remove with cwd `$VERIFY_PROJECT`.
- Pass `$SKILLS_CATALOG` as the local source. Do not pass `-g` or `--global`.
- Do not pass `--agent` to `skills use`.
- Record stdout, stderr, and the exit code.
- Restore the disposable project after a mutation by removing the installed skill and deleting the project. Do not remove proof artifacts during cleanup.

## Proof and skip reporting

- Capture the user action and the resulting state, not only the final banner.
- CLI proof includes the command, stdout, stderr, and exit code.
- Mutation proof includes the files the command wrote and a second `npx --yes skills list --agent cursor --json` view.
- Record the feature ID and entry point used with every artifact.
- Report an unreachable path with the attempted command and the unmet precondition.
- Do not report a skipped entry point as verified through a different path.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph describing the user-visible behavior. It then uses exactly four H2 sections in this order.

1. `Sub-features` lists short IDs with one line for each behavior.
2. `How to get to it (user POV)` lists every user entry point.
3. `Driving it with the skills CLI` starts with `Preconditions:` and uses labeled bullets that pair each user action with an exact command and observable result.
4. `Gotchas` lists traps that can waste or invalidate a verification run.

Keep implementation details out of the map. Name only user paths, stable handles, required state, commands, and observable proof.

## Features

- [List the catalog](./list-catalog.md) prints the skills in this repository and writes nothing.
- [Install text-to-speech](./install-text-to-speech.md) copies `text-to-speech` into a Cursor project and writes `skills-lock.json`.
- [Render a skill prompt](./render-skill-prompt.md) prints a `text-to-speech` prompt without installing it.
- [List installed skills](./list-installed.md) shows an empty project and the project after install.
- [Remove an installed skill](./remove-installed-skill.md) deletes the copied skill directory and leaves the lock file behind.
