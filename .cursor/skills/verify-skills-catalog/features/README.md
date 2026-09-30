# Skills catalog verification map

This directory is the maintained source for verifying the user-facing behavior of the ElevenLabs skills catalog. Read the index before driving the CLI, then use the matching feature file as the recipe.

The surface is `npx skills` 1.5.18. The README installs this catalog with `npx skills add elevenlabs/skills`. There is no app server.

## Baseline preconditions

- Resolve `$SKILLS_CATALOG` to the checkout that contains `.cursor/skills/verify-skills-catalog`.
- Launch with `.cursor/skills/verify-skills-catalog/scripts/verify-skills-catalog.sh launch`, which creates `$VERIFY_PROJECT` under `/tmp/verify-skills-catalog.*` and runs `npx --yes skills add elevenlabs/skills` there.
- Require `npx --yes skills --version` to print `1.5.18`.
- Require `CURSOR_AGENT` to be set so the README command installs non-interactively.
- Run the helper's `doctor` and require the 11 installed Cursor project skills, a GitHub `skills-lock.json`, and an unchanged global Cursor list.
- Never drive `$HOME`, the catalog checkout, or a project the verification run did not create.

## Driving conventions

- The helper's doctor baseline is the README install: 11 Cursor project skills and a GitHub lock file.
- Recipes other than [Install the catalog](./install-catalog.md) describe different entry points. They are not the state launch leaves behind, and this run does not verify them.
- Treat every command as literal. Keep quoted flags unchanged.
- Run install, list, and remove with cwd `$VERIFY_PROJECT`.
- The README install passes `elevenlabs/skills` and no other skills flags. Do not pass `-g` or `--global`.
- Do not pass `--agent` to `skills use`.
- Record stdout, stderr, and the exit code.
- After the README install, delete the disposable project. Do not remove proof artifacts during cleanup.

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

- [Install the catalog](./install-catalog.md) runs the README command and installs every skill from `elevenlabs/skills`.
- [List the catalog](./list-catalog.md) prints the skills in this repository and writes nothing.
- [Install text-to-speech](./install-text-to-speech.md) is a different local `--skill text-to-speech --copy` entry point. Launch does not run it.
- [Render a skill prompt](./render-skill-prompt.md) prints a `text-to-speech` prompt without installing it.
- [List installed skills](./list-installed.md) shows an empty project and the project after install.
- [Remove an installed skill](./remove-installed-skill.md) deletes the copied skill directory and leaves the lock file behind.
