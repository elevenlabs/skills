---
name: setup-api-key
description: Fix or hand-configure an existing ElevenLabs API key. Use when a key stopped working (401 or invalid_api_key), when an administrator issued the key, when the user's role cannot create keys, or when the user already has a key and needs it in the right place. Checks whether ELEVENLABS_API_KEY is configured and valid, without reading it into the conversation. Not for first-time setup or adding ElevenLabs to a project (use onboarding).
license: MIT
compatibility: Requires internet access to elevenlabs.io and api.elevenlabs.io, and Node.js for npx (or the ElevenLabs CLI installed another way).
---

# ElevenLabs API Key Setup

For a key the user already has, or one that stopped working. For adding
ElevenLabs to a project from scratch, use the `onboarding` skill.

**A key the user already has (for example from an administrator):** don't
sign in for a new one. Tell them to paste it after `ELEVENLABS_API_KEY=` in
the env file of the app that uses it (`.env.local`, or `.env` in a Python
project), never into this chat, and to tell you when it's done. Then check it
(if `check` finds no key, or ElevenLabs rejects it, and offers to sign in,
ask the user to check the paste instead of signing in):

```bash
npx -y @elevenlabs/cli@latest onboard check
```

**A key that stopped working:** run the same command from the app's folder.
It finds the key the app would use (the shell, the env file, or a `.env` up
the tree), checks it with ElevenLabs without printing it, and prints JSON:
`next` is the step (spelled out in `instruction`; where the list below differs,
follow the list), `run` the exact command, and `say` what to tell the user (tell
them as written). Follow it until the key works; for a rejected key it
signs the user in for a new one. What each `next` means:

- `run`: run `run`. `wait`: show `say`, then run `run` again right away.
- `ask_user`, or a `fix` that needs the user's shell or secrets: ask them
  what `say` says, wait for their answer, then run `run`, unless they said no.
- `write_code`: if the app already reads `ELEVENLABS_API_KEY` (through the
  SDK or its own requests), don't change its code: after `connect`, run
  `run`; after `check`, tell the user the key works (not `say`) and stop.
  Otherwise make sure the code uses the SDK, then run `run`; if nothing
  shows what the app should do with ElevenLabs, ask the user first, and don't
  pick a product for them.
- `offer_test`: ask the question in `say`; run `run` only if they say yes.
- `done`: tell the user `say`.

## Rules

- Never open, print or `cat` the env file, and never echo
  `ELEVENLABS_API_KEY`; `onboard check` verifies the key for you.
- Never ask for an API key in chat, and never accept one pasted there. If one
  appears, tell the user to rotate it on the API keys page.
- Never put the key in code; the SDK reads `ELEVENLABS_API_KEY`.
- Don't run the app or make your own API calls to try the key unless the
  user says yes. Once the code is written, run `onboard check` before you
  finish: it verifies the key and the code.
- For browser or client-side apps, keep the key on the server and issue
  short-lived tokens where the product supports them.

## No npx

If `npx` isn't available (Node.js isn't installed), install the CLI (or
update it if it's already installed: `brew upgrade elevenlabs`, or run the
installer again), then run `elevenlabs onboard check` instead:

- macOS or Linux: `brew install elevenlabs/tap/elevenlabs`, or
  `curl --proto '=https' --tlsv1.2 -LsSf https://github.com/elevenlabs/cli/releases/latest/download/elevenlabs-cli-installer.sh | sh`
- Windows: `powershell -ExecutionPolicy ByPass -c "irm https://github.com/elevenlabs/cli/releases/latest/download/elevenlabs-cli-installer.ps1 | iex"`

If `elevenlabs` isn't found after the installer ran, use
`~/.cargo/bin/elevenlabs` in its place, here and in every `run` the CLI gives.
