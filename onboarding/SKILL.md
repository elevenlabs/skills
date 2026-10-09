---
name: onboarding
description: Add ElevenLabs to a project from scratch. Use when the user wants to start using ElevenLabs, add text to speech, speech to text, voice agents, real-time voice for their own agent runtime (Speech Engine), sound effects, music, voice changing, voice isolation, or dubbing to their app, or get set up with an ElevenLabs account or API key for the first time. Handles sign-in, API key creation, SDK install and a test request end to end; the user leaves the conversation once, to approve a browser page. Not for fixing a key that stopped working or placing one an administrator issued (use setup-api-key).
license: MIT
compatibility: Requires internet access to elevenlabs.io and api.elevenlabs.io, and Node.js for npx (or the ElevenLabs CLI installed another way). Where no browser can reach the machine (SSH, containers, cloud agents), the user adds the key by hand and the flow continues.
---

# ElevenLabs Onboarding

The ElevenLabs CLI runs the whole setup and tells you each step. From the
folder of the app that will use the key (in a monorepo, that app's folder),
run:

```bash
npx -y @elevenlabs/cli@latest onboard init
```

Every `onboard` command prints JSON. Act on it, and keep going until `next`
is `done`:

- `next`: what to do now, spelled out in `instruction`.
- `run`: the exact next command. Run it as given.
- `say`: what to tell the user. Tell them as written.
- `details`: facts for the next step, such as how the app loads the key and
  the SDK install command.
- `rules`: rules for the whole setup. Follow them.

What each `next` means:

- `run`: run `run`.
- `wait`: the approval page is open. Show `say` (it has the link), then run
  `run` again right away, without ending your turn.
- `write_code`: install the SDK and write the integration for what the user
  asked for, using `details.sdk_install` and `details.load_key`, then run
  `run`. If nothing in the conversation or the project shows what they want
  to build, ask them first, and don't pick a product for them. Before writing
  code, read the skill for that product, as `instruction` says.
- `fix`: do what `say` describes, then run `run`. If it needs the user's
  shell, settings or secrets, ask them instead, as for `ask_user`.
- `ask_user`: ask the user what `say` says and wait for their answer, then
  run `run`, unless they said no.
- `offer_test`: ask the user the question in `say`. Run `run` only if they
  say yes.
- `done`: tell the user `say`.

## Rules

- Never open, print or `cat` the env file; `onboard check` verifies it.
- Never ask for an API key in chat, and never accept one pasted there. If one
  appears, tell the user to rotate it on the API keys page.
- Never put the key in code; the SDK reads `ELEVENLABS_API_KEY`.
- Never run `git clean` or delete untracked files: the key is in one.
- Don't run the app or make your own API calls to try the key unless the
  user says yes. Once the code is written, run `onboard check` before you
  finish: it verifies the key and the code.

## No npx

If `npx` isn't available (Node.js isn't installed), install the CLI (or
update it if it's already installed: `brew upgrade elevenlabs`, or run the
installer again), then run `elevenlabs onboard init` instead. Everything after
that is the same.

- macOS or Linux: `brew install elevenlabs/tap/elevenlabs`, or
  `curl --proto '=https' --tlsv1.2 -LsSf https://github.com/elevenlabs/cli/releases/latest/download/elevenlabs-cli-installer.sh | sh`
- Windows: `powershell -ExecutionPolicy ByPass -c "irm https://github.com/elevenlabs/cli/releases/latest/download/elevenlabs-cli-installer.ps1 | iex"`

If `elevenlabs` isn't found after the installer ran, use
`~/.cargo/bin/elevenlabs` in its place, here and in every `run` the CLI gives.
