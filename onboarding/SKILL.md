---
name: onboarding
description: Add ElevenLabs to a project from scratch. Use when the user wants to start using ElevenLabs, add text to speech, speech to text, voice agents, sound effects, music, voice changing, voice isolation, or dubbing to their app, or get set up with an ElevenLabs account or API key for the first time. Handles sign-in, API key creation, SDK install and a first request end to end; the user leaves the conversation once, to approve a browser page. Not for a key that already exists and stopped working (use setup-api-key).
license: MIT
compatibility: Requires internet access to elevenlabs.io and api.elevenlabs.io and the ElevenLabs CLI, which the skill updates to the latest release (or installs) at the start of every run. Where no browser can reach the machine (SSH, containers, cloud agents) or the CLI cannot be installed or updated, the user creates the key by hand and the skill continues.
---

# ElevenLabs Onboarding

Take the user from "I want ElevenLabs in my app" to a working integration. The
only step outside this conversation is one browser approval, where the user
signs in or creates an account and the approval page creates an API key for
this project. You never see the key, and the user never copies it by hand,
except where no browser can reach this machine or the CLI cannot be installed (the manual key path in Step 4).

## Safety rules

- Never ask the user for an API key and never accept one pasted into the chat.
  If one appears, tell them to rotate it on the API keys page.
- Never read the env file after the CLI has written it, never echo environment
  variables, and never print the output of commands that could contain the key.
- Never paste the key into code. The SDKs read `ELEVENLABS_API_KEY` from the
  environment.
- Run every CLI command below with `--format json` and branch on the fields it
  returns. Do not parse prose.

## Workflow

### Step 1: Bring the CLI up to date

The approval flow lives in the ElevenLabs CLI, and fixes to it ship as new CLI
releases, so start every run by updating the CLI. Never compare version
numbers and never look for a particular version: update, then check for the
one command this skill needs.

Work out how the CLI is installed and run that channel's update command, or
its install command when the CLI is missing. Tell the user in one line what
you are running (a global update of the ElevenLabs CLI; it does not touch
their project), then run it without waiting for an answer:

| How it is installed | Check | Command |
| --- | --- | --- |
| Homebrew (`brew list --versions elevenlabs` prints a version) | macOS or Linux | `brew update && brew upgrade elevenlabs/tap/elevenlabs` |
| npm (`npm ls -g @elevenlabs/cli` lists it) | any platform | `npm install -g @elevenlabs/cli@latest` |
| Scoop (`scoop list elevenlabs` lists it) | Windows | `scoop update elevenlabs` |
| Not installed, Homebrew available | macOS or Linux | `brew install elevenlabs/tap/elevenlabs` |
| Not installed, Node.js available | any platform | `npm install -g @elevenlabs/cli@latest` |
| Not installed, Scoop available | Windows | `scoop bucket add elevenlabs https://github.com/elevenlabs/scoop-bucket && scoop install elevenlabs` |
| Not installed, none of the above | macOS or Linux | `curl --proto '=https' --tlsv1.2 -LsSf https://github.com/elevenlabs/cli/releases/latest/download/elevenlabs-cli-installer.sh \| sh` |

Use the channel the CLI already came from; never install through a second
channel, or an older copy can shadow the new one. "Already up to date" or
"already installed" from the channel is success. Then check for the command:

```bash
elevenlabs onboard --help
```

If that prints the command's help, the CLI is ready: go to Step 2.

- **`elevenlabs` is not found after an install:** the shell's `PATH` has not
  picked it up yet. Use the absolute path the installer printed, or ask the
  user to open a new terminal, then check again.
- **The update or install fails** (no network, no permission, the channel
  reports an error), **or `elevenlabs onboard --help` still fails afterwards:**
  do not retry and do not install any other way. Say in one sentence what
  failed, then take **the manual key path** in Step 4: the user creates a key
  themselves, and this skill continues from there without the CLI. Never stand
  in for the CLI by creating a key or the env file yourself.

### Step 2: Pick the product

Map what the user asked for to one product slug. If the request is generic
("add ElevenLabs", "set me up"), ask which of these they want first, or omit the
product to get a key with the default permissions.

| User wants | `--product` | Skill to use for the code |
| --- | --- | --- |
| Speech from text, voiceovers, narration | `text-to-speech` | `text-to-speech` |
| Transcription, subtitles, speech recognition | `speech-to-text` | `speech-to-text` |
| A voice agent, phone or web assistant | `agents` | `agents` |
| Real-time voice for a custom LLM or agent runtime | `speech-engine` | `speech-engine` |
| Sound effects, ambience, UI sounds | `sound-effects` | `sound-effects` |
| Music, jingles, background tracks | `music` | `music` |
| Change the voice in a recording | `voice-changer` | `voice-changer` |
| Remove background noise from audio | `voice-isolator` | `voice-isolator` |
| Translate a video or podcast into other languages | `dubbing` | `dubbing` |

### Step 3: Pick the env file

Decide where the key lives before anything opens, and tell the user. Look at
the project the user is working in, not the repository root, when they differ.

1. If the project has a `.env.local`, use it.
2. Otherwise, if it has a `.env` that git does not track, use that.
3. Otherwise use `.env.local`.

If the project already loads secrets another way (a secrets manager, `direnv`),
still use the file above for onboarding and tell the user where the key is so
they can move it.

### Step 4: Check what is already in place

```bash
elevenlabs onboard status --env-file <file> --format json
```

Skip this command when Step 1 ended without a usable CLI: go straight to the
manual key path at the end of this step.

Read five fields: `api_key_present`, `api_key_valid`, `api_key_source`,
`dotenv_file` and `browser_reachable`. `api_key_source` is one of:

- `env_file`: the key is in `<file>`.
- `dotenv`: the key is in a `.env` file the SDKs' loaders read first, named in
  `dotenv_file` (often the project root's `.env`, not `<file>`). Treat that
  file as `<file>` from here on: writing a key anywhere else would be ignored.
- `env`: a variable exported in the shell. It wins over any env file, because
  the SDKs' env loaders do not override an existing variable, so a bad shell
  key cannot be fixed by writing `<file>`; the user has to unset or fix it.
- `none`: no key anywhere.

First look at `browser_reachable`: when it is false, every "Step 5" below
means the manual key path at the end of this step instead.

| `api_key_present` | `api_key_valid` | `api_key_source` | Do this |
| --- | --- | --- | --- |
| false | | | Go to Step 5. |
| true | true | `env_file` | A working key is already in `<file>`. Skip to Step 6. |
| true | true | `dotenv` | A working key is already in `dotenv_file`. Say so, use that file as `<file>` from now on, and skip to Step 6. |
| true | false | `dotenv` | Say the key in `dotenv_file` is rejected by the API. Go to Step 5 with `--env-file <dotenv_file> --replace`. |
| true | null | `dotenv` | Say the API could not be reached to check the key in `dotenv_file`, so it is not known to be bad. Skip to Step 6, or Step 5 with `--env-file <dotenv_file> --replace` if the user wants a fresh key. |
| true | true | `env` | Say the key comes from the shell, not `<file>`, and ask the user to choose: keep running the app from the shell variable (then skip to Step 6), or unset it so a key can live in `<file>` (then go to Step 5). Do not decide for them. |
| true | false | `env_file` | Say the key in `<file>` is rejected by the API. Go to Step 5 with `--replace`. |
| true | false | `env` | Say the shell variable holds a rejected key and ask them to unset or fix it. A variable they change in their own terminal does not reach this session, so check again with `env -u ELEVENLABS_API_KEY` in front of the Step 4 command to read `<file>` on its own, and tell them to restart their own session before running the app. |
| true | null | `env_file` | Say the API could not be reached to check the key, so it is not known to be bad. Skip to Step 6, unless the user wants a fresh key: then Step 5 with `--replace`. |
| true | null | `env` | Same as above; a fresh key means asking them to unset the variable first. |

**The manual key path.** Take it when `browser_reachable` is false (the CLI
is running somewhere the user's browser cannot land: an SSH session, a
container, a cloud agent, so the approval page cannot hand it a key and
`elevenlabs onboard` refuses to run) and when Step 1 ended without a usable
CLI. Do not pass `--no-browser` to get around a remote machine: the key would
land on the wrong machine's clipboard. The path:

1. Ask the user to create an API key at
   https://elevenlabs.io/app/settings/api-keys with the permissions for the
   product they want plus Text to Speech (for the test request in Step 7) and
   User: Read (the CLI checks the key with it), or all permissions.
2. Ask them to make it available as `ELEVENLABS_API_KEY` the way they normally
   handle secrets in this environment: an exported variable, the sandbox's
   secrets, or an env file they manage. Never paste it into this chat. Do not
   create an env file or placeholder for them; that is their call here.
3. Wait for them to say it is done, then check the key. With a usable CLI, run
   Step 4 again: `api_key_present` true and `api_key_valid` true means it works
   (its `api_key_source` will usually be `env` or `dotenv`); skip to Step 6.
   Without the CLI, check it the way the `setup-api-key` skill does (its Step
   2: `GET https://api.elevenlabs.io/v1/user` with the `xi-api-key` header,
   reading the value from where they put it, never printing it). If it is
   still missing or invalid, say so and wait.

### Step 5: Sign in and get a key

Before running the command, tell the user three things: a browser page will
open where they sign in or create an account and click Authorize, the only
step outside the conversation; the page creates an API key that the CLI stores
in `<file>` without showing it; and on macOS the system may show a Keychain
dialog asking whether `elevenlabs` may use the "elevenlabs" item, which is the
CLI storing or reading its own sign-in token, so they should click "Always
Allow". That dialog can sit behind the browser window; if the command seems to
hang after Authorize, that is where to look.

```bash
elevenlabs onboard --product <slug> --env-file <file> --format json
```

Add `--replace` only when Step 4 said to. Wait for the command to finish.

**It printed a result.** Read `next` and `key_status`:

| `next` | `key_status` | What happened | Do this |
| --- | --- | --- | --- |
| `none` | `created` | The key is in `<file>`; `key_last4` is its last four characters. | Tell the user which file. If `gitignore_updated` is true, say the file was added to `.gitignore`; otherwise remind them to keep it out of version control. Go to Step 6. |
| `paste_key` | `no_key` or `clipboard_invalid` | The sign-in worked but no usable key arrived (nothing was copied, or what was copied belongs to another account). The clipboard was cleared. | Say: click "Copy key" on the approval page if it is still open, or create a key at https://elevenlabs.io/app/settings/api-keys, and paste it after `ELEVENLABS_API_KEY=` in `<file>`, never into this chat. If `existing_key_kept` is true, add that the old key is still on that line and must be replaced. Then wait for the user to confirm and run the Step 4 command again to check the key. |
| `legacy` | `not_available` | The flow is not on for this account. | Stop this skill. Hand off to the `setup-api-key` skill for the key, telling it the key goes on the `ELEVENLABS_API_KEY=` line in `<file>`, then to the product skill for the code. |
| `legacy` | `not_permitted` | The user's role cannot create keys; an administrator has to issue one. | Say so. Stop this skill. Hand off to the `setup-api-key` skill for the key, telling it the role cannot create keys and that the key goes in `<file>`, then to the product skill for the code. |
| `legacy` | `failed` (`key_reason` `page_could_not_create` or `could_not_verify`) | The approval page could not create a key, or the API could not be reached to check the one it made. Nothing was stored and the clipboard was cleared. | Say the key could not be set up automatically this time. Stop this skill. Hand off to the `setup-api-key` skill for the key, telling it the key goes on the `ELEVENLABS_API_KEY=` line in `<file>`, then to the product skill for the code. |

After a `paste_key` result, Step 4 is only a check: if it still shows no
working key, say the line in `<file>` is still empty or still wrong and wait
for the user. Never run `elevenlabs onboard` a second time after a result;
each run that succeeds creates another key.

**It printed an error instead.** Every refusal arrives as `reason`
`validationError`, so read `error.message` to tell them apart:

| The error says | What it means | Do this |
| --- | --- | --- |
| the env file is tracked by git, or is a symlink | `<file>` is not a safe place for a secret. | Switch `<file>` to `.env.local`, tell the user, run the command again. |
| the env file already sets `ELEVENLABS_API_KEY` | `<file>` holds a key Step 4 did not report, usually because a shell variable took precedence. | Ask the user whether to replace it. If yes, run the command again with `--replace`. |
| a `.env` already sets `ELEVENLABS_API_KEY`, and the SDKs read that file first | A `.env` in the project holds a key while `<file>` is another file. | Use that `.env` as `<file>` from now on. Run Step 4 with `--env-file` naming it: a working key means skip to Step 6; a rejected one means Step 5 with `--env-file <that .env> --replace`. |
| the sign-in did not finish; a key left on the clipboard was discarded | The browser flow broke after the page had created a key. The key was cleared, not stored. | Run the command again when the user says they are ready; the earlier key can be revoked on the API keys page. |
| the env file could not be read or written | Permissions, or the path is a directory. Nothing was stored. | If the error came before the browser opened, fix the file or choose another with `--env-file` and run the command again. If it came after the sign-in, a key was created and is on the user's clipboard: have them paste it into the fixed file, never into this chat, and do not run the command again. |
| unexpected argument, or invalid value for `--product` | A usage error: the flag or slug is not one the CLI knows. | Fix the command (product slugs are exactly those in Step 2) and run it again. |
| no browser can reach this machine | Same situation as `browser_reachable` false. | Take the manual key path in Step 4. |
| anything else (denied, timed out, page closed) | The sign-in did not finish. Nothing was stored. | Run the command again when the user says they are ready. |

### Step 6: Install the SDK

Follow the product skill's `references/installation.md` for the user's
language. Prefer `@elevenlabs/elevenlabs-js` for JavaScript and `elevenlabs`
for Python.

### Step 7: Offer one test request

Offer to turn one sentence into speech: "Welcome to ElevenLabs" with the SDK's
text to speech call, saved to a small audio file. Offer this same request
whatever product the user chose: every key the CLI stores can make it, and it
needs no input audio, no agent and no project code. (A key the user created
themselves needs the Text to Speech permission.) Read the key the way the app
will: `<file>` through `dotenv` in Node (`dotenv.config({ path: "<file>" })`)
or `python-dotenv` in Python (`load_dotenv("<file>")`), since neither reads
`.env.local` on its own; through the framework's own env loading; or from the
shell variable or `dotenv_file` when Step 4 found the key there. Say that it spends a few credits. Play the file or say where it is. Do
this before touching the user's code: it proves the key and the SDK work
regardless of the state of the project.

### Step 8: Integrate

Use the product skill from the table in Step 2 to wire the SDK into the user's
application for what they asked for.

### Step 9: Report

Say what was built, where the key lives (`<file>`, or the shell environment
when Step 4 found it there) and whether it is ignored by git, what the test
request produced, and offer next steps from the product skill.
