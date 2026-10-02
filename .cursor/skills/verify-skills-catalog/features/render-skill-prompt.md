# Render a skill prompt

Render a skill prompt prints instructions for `text-to-speech` on stdout and does not install the skill into the project.

## Sub-features

- `use-stdout` prints the skill prompt.
- `use-no-project-files` leaves the disposable project empty.
- `use-temp` materializes a temporary copy outside the project.

## How to get to it (user POV)

- Run `npx skills use <catalog> --skill text-to-speech`.

## Driving it with the skills CLI

Preconditions:

- `$VERIFY_PROJECT` exists under `/tmp/verify-skills-catalog.*` and is the shell cwd.
- `doctor` reports an empty Cursor project list.
- Do not pass `--agent`.

- **Render.** Print the prompt. Run `npx --yes skills use "$SKILLS_CATALOG" --skill text-to-speech`. Exit code `0`, stderr empty, and stdout begins `You are being given a Skill to execute for the user's next request.` and includes `<SKILL.md>` and `name: text-to-speech`.
- **Confirm the project is unchanged.** Run `npx --yes skills list --agent cursor --json`. Stdout is `[]`. `$VERIFY_PROJECT` has no `skills-lock.json` and no `.agents/skills/text-to-speech`.
- **Confirm the temp copy.** The prompt names a directory under `$TMPDIR` matching `skills-use-*/text-to-speech`. That directory contains `SKILL.md`. It is not the project install.
- **Proof.** Save stdout, stderr, and the exit code. Record that the project tree did not gain `text-to-speech`.

## Gotchas

- `--agent` launches an interactive coding agent. Omit it.
- The temporary `skills-use-*` directory is not an install. Delete that directory when finishing this feature, and do not treat it as proof that the project gained a skill.
- Supporting files are mentioned at the end of stdout. Their path is outside `$VERIFY_PROJECT`.
