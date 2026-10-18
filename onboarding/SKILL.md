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
  `run` again right away, without ending your turn. Whenever you give the
  user the link, copy it whole, exactly as printed: a shortened link doesn't
  work.
- `ask_what_to_build`: tell the user `say`, which asks what they want to
  build or whether to just add the SDK, and wait for their answer before
  writing any code. Ask it even if they said earlier, and don't pick a product
  for them. Once they answer, run `run`.
- `write_code`: write what they asked for, as `instruction` says: the SDK
  alone, or the integration, with the skill that fits from
  `details.fetch_skills` when there is one. If it needs something made in
  ElevenLabs first, like an agent, make it yourself with the key (load the
  env file in the command, never print it), not a script for the user to run.
  Load the key the way `details.load_key` says, then run `run`.
- `load_key`: the code already uses the SDK, so there is nothing to build.
  Make sure the app loads the key the way `details.load_key` says, change
  nothing else, then run `run`.
- `fix`: do what `say` describes, then run `run`. If it needs the user's
  shell, settings or secrets, ask them instead, as for `ask_user`.
- `ask_user`: ask the user what `say` says and wait for their answer, then
  run `run`, unless they said no.
- `offer_test`: say what you set up and anything the user still has to do
  themselves, like installing the packages you added. Then end your reply
  with the question in `say`. Run `run` only if they say yes.
- `done`: tell the user `say`, then anything they still have to do
  themselves, in one or two concrete steps.

## Rules

- Never open, print or `cat` the env file; `onboard check` verifies it.
- Never ask for an API key in chat, and never accept one pasted there. If one
  appears, tell the user to rotate it on the API keys page.
- Never put the key in code; the SDK reads `ELEVENLABS_API_KEY`.
- Never run `git clean` or delete untracked files: the key is in one.
- Don't write or change any code until a reply's `next` is `write_code` or
  `load_key`.
- Put anything you download only to read, like a package or an archive, in a
  temp folder, never in the project.
- Don't run the app (or its start script) or make speech to try it until the
  user says yes to the test request. API calls that what they asked for
  needs, like creating an agent, are fine. Once the code is written, run
  `onboard check` before you finish: it verifies the key and the code.

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
