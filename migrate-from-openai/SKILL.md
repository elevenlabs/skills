---
name: migrate-from-openai
description: Move a project's OpenAI speech code to ElevenLabs. Use when the user wants to migrate, switch, port or replace OpenAI text to speech (`audio.speech`, `/v1/audio/speech`, `tts-1`, `tts-1-hd`, `gpt-4o-mini-tts`) or OpenAI transcription (`audio.transcriptions`, `/v1/audio/transcriptions`, `whisper-1`, `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, `gpt-4o-transcribe-diarize`) in a Python or JavaScript/TypeScript project, or asks what to do about OpenAI retiring those models in 2027. Finds every OpenAI speech call, converts the ones with a clear ElevenLabs match to the ElevenLabs SDK, leaves chat, embeddings and images on OpenAI, and reports what it left alone. Not for OpenAI chat, embeddings or image calls, for upgrading the openai package, or for changing voices or models in code that already uses ElevenLabs. Not for a voice app on OpenAI's Realtime API (use realtime), and not for adding ElevenLabs to a project that has no OpenAI speech code (use onboarding).
license: MIT
compatibility: Converts Python and JavaScript/TypeScript projects. Requires internet access to install the ElevenLabs SDK. The converted code reads ELEVENLABS_API_KEY; the last step offers to set one up.
---

# Migrate from OpenAI speech to ElevenLabs

OpenAI is retiring its speech models: text to speech on January 6, 2027, Realtime voice on January 20, and transcription on February 26. This guide moves a project's OpenAI text to speech and transcription calls to the ElevenLabs SDK.

ElevenLabs has no OpenAI-compatible speech endpoint, so this is a port, not a URL change: a different SDK, different calls, and different code wherever the app reads the result. Follow the steps in order. Everything else in the project (chat, embeddings, images, moderation) stays on OpenAI.

## What moves

| OpenAI | What to do |
| --- | --- |
| Text to speech: `audio.speech.create`, `POST /v1/audio/speech` | Convert. See [Text to speech](references/text-to-speech.md). |
| Transcription of a file: `audio.transcriptions.create`, `POST /v1/audio/transcriptions` | Convert. See [Transcription](references/transcription.md). |
| Realtime voice: `@openai/agents-realtime`, `/v1/realtime`, `gpt-realtime*`, `gpt-4o-realtime*` | Move it with the `realtime` skill, which sits next to this one (`../realtime/SKILL.md`): follow that skill for it after Step 4, then carry on here from Step 5. It covers a browser app whose code is in this project. Leave and list anything else, including one side on its own, such as a route that only mints the credential for an app kept elsewhere: moving one side would break the other. |
| Live transcription (`/v1/realtime` transcription sessions, `stream=True` on a transcription) | Leave it and list it. |
| Audio translation (`audio.translations`), `gpt-audio*` in chat, custom voices | Leave it and list it. ElevenLabs has no direct match. |

## Rules

- **Never guess.** Every OpenAI setting has a written rule in the references: it becomes an ElevenLabs setting, it is dropped and the user is told, or the whole call stays on OpenAI and is listed. A setting the references don't mention is in the last group.
- **Keep the app's own shape.** The app's functions, routes and components keep their names, inputs and outputs. Change what happens inside them, so nothing that calls them has to change.
- **Only speech moves.** Don't touch other OpenAI calls, and don't remove the `openai` package or `OPENAI_API_KEY` while anything still uses them.
- **The key.** The converted code reads `ELEVENLABS_API_KEY` from the environment. Never ask for a key in chat, never accept one pasted there, never put one in code or in anything that runs in a browser, and never open, print or `cat` an env file.
- **Don't run the app or make speech** to try the result. The last step offers a test, and it asks the user first.

## Step 1: List every OpenAI speech call

Before changing anything, find them all:

```bash
grep -rnE "audio\.speech|audio\.transcriptions|audio\.translations|audio/speech|audio/transcriptions|audio/translations|tts-1|gpt-4o-mini-tts|whisper-1|gpt-4o(-mini)?-transcribe|gpt-audio|gpt-realtime|gpt-4o(-mini)?-realtime|v1/realtime|agents-realtime|experimental_(generateSpeech|transcribe)|OpenAIWhisper|OPENAI_API_KEY|OPENAI_BASE_URL" \
  --include='*.py' --include='*.ipynb' --include='*.ts' --include='*.tsx' --include='*.mts' --include='*.cts' --include='*.js' --include='*.jsx' --include='*.mjs' --include='*.cjs' --include='*.vue' --include='*.svelte' --include='*.astro' \
  --include='*.go' --include='*.rb' --include='*.java' --include='*.kt' --include='*.cs' --include='*.php' --include='*.rs' --include='*.swift' \
  --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=venv --exclude-dir=dist --exclude-dir=build --exclude-dir=.next --exclude-dir=.git .
```

The model is often a variable or a setting, so also read how each OpenAI client in the project is created and used. For each speech call, write down:

- the file and line, and which API it is
- which client it is called on, and how that client is created
- every setting it passes, and where each value comes from
- how the app uses the result afterwards: saved to a file, returned from a route, streamed, parsed for timestamps
- its error handling, retries and timeouts

## Step 2: Decide what moves

Go through the list. A call moves only when all of these hold:

1. **It calls OpenAI itself.** A client created with a `base_url` / `baseURL` or as `AzureOpenAI` talks to something else. Leave it and list it, and say what it points at: another provider (Azure, Groq, a local server) isn't retiring these models, but a gateway that forwards to OpenAI is still affected, and that is the user's call. `OPENAI_BASE_URL` does the same from the environment. You can't read env files, so if nothing you can read sets it, say in the report that you assumed it isn't set.
2. **The project is Python or JavaScript/TypeScript.** Those are the languages with an ElevenLabs SDK. In any other language, change nothing: list each call with the [text to speech migration guide](https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/migrate-from-openai).
3. **It calls OpenAI's SDK or its HTTP API directly.** A call made through another library (Vercel AI SDK, LangChain, LlamaIndex, LiveKit, Pipecat) moves by changing that library's provider, which this guide doesn't cover. Leave it and list it.
4. **The table above says to convert it**, and every setting it passes has a rule that isn't "leave the call".

If nothing moves, change nothing: report why ([Step 6](#step-6-report)) and stop there, without the offer in Step 7.

## Step 3: Install the ElevenLabs SDK

Use the project's own package manager, the one its lockfile belongs to:

- Python: the `elevenlabs` package (`pip install elevenlabs`, `uv add elevenlabs`, `poetry add elevenlabs`). Add it wherever the project lists `openai` (`requirements.txt`, `pyproject.toml`).
- JavaScript/TypeScript: `@elevenlabs/elevenlabs-js` (`npm install`, `pnpm add`, `yarn add`, `bun add`). Not the `elevenlabs` npm package, which is outdated.

Create one client and reuse it:

```python
from elevenlabs import ElevenLabs  # AsyncElevenLabs where the app used AsyncOpenAI

elevenlabs = ElevenLabs()  # reads ELEVENLABS_API_KEY
```

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const elevenlabs = new ElevenLabsClient(); // reads ELEVENLABS_API_KEY
```

Put it in the file that makes the speech calls. In JavaScript, never in a module that other code loads, such as a shared `lib/openai.ts`: `new ElevenLabsClient()` throws when `ELEVENLABS_API_KEY` isn't set, so until the key is in place it would take the chat and embeddings code down with it. The Python client doesn't check for the key until a call is made.

Where the project lists the variables it needs (`.env.example`, a README, a config schema, deployment files), add `ELEVENLABS_API_KEY` the way `OPENAI_API_KEY` is listed, with no value.

Leave a call made from browser code and list it: the key can't go to a browser, and moving the call to a server is a change for the user to make.

## Step 4: Convert each call

Read the reference for each API before writing its code, and write the code the way it shows:

- [Text to speech](references/text-to-speech.md): the settings, voices, formats, streaming, and how the audio comes back.
- [Transcription](references/transcription.md): the settings, timestamps, speaker labels, subtitles, and how the transcript comes back.

Both cover Python and JavaScript/TypeScript, async clients, direct HTTP calls, errors, retries and timeouts. Change the tests and mocks that cover a converted call too, so they describe the new call.

## Step 5: Check your work

1. Run the project's type check or build, and its linter if it has one (`tsc --noEmit`, `mypy`, `pyright`, `ruff`). Fix what your change caused.
2. Run the project's unit tests if they run without calling OpenAI or ElevenLabs. Don't start the app.
3. If the type check flags an ElevenLabs call, read that call in the installed SDK (`node_modules/@elevenlabs/elevenlabs-js`, or the `elevenlabs` package in the environment) and follow it: the installed version wins over this guide.
4. Run the search from Step 1 again. Every OpenAI speech call still there must be on your list of calls that stay. No output means none are left; `grep` exits with 1 then, which is not a failure.

## Step 6: Report

Tell the user, briefly and with file and line:

- **Moved:** each call, and what it uses now (model, output format).
- **Dropped:** each setting that has no ElevenLabs match and what changes because of it, such as tone `instructions`.
- **Still on OpenAI:** each call that stays, why, and the date OpenAI retires it.
- **For you to do:**
  - Pick voices. Every converted call uses one placeholder voice, George. There is no like-for-like match for OpenAI's voices, so choose your own at https://elevenlabs.io/app/voice-library and replace the placeholder ID.
  - Set `ELEVENLABS_API_KEY` wherever the app runs: your machine, CI and production.
  - Anything else that came up, such as a subtitle format to check or a package to install.

## Step 7: Offer to set up the key

Only when at least one call moved: end that same message with this question, as it is, and end your turn:

> Want me to set up an ElevenLabs API key for this project and check it works? If it doesn't have one yet, I'll open a page in your browser for you to approve.

**If they say no,** you're done. Run nothing.

**If they say yes,** run the key command from the folder of the app that uses the key. If you got this guide from `migrate openai`, that is the `run` in its reply. Otherwise:

```bash
npx -y @elevenlabs/cli@latest onboard init
```

With no key in the project, the command opens the ElevenLabs approval page in the user's browser and waits up to five minutes. Tell the user before you run it, keep it running until it finishes, and don't end your turn while it waits. It prints one line of JSON. Do what its `instruction` says, with these in mind:

- **The migration is what the user asked you to build, and it is done.** Don't ask what to build, don't download the skills again, and write no new feature.
- **Do make sure the app loads the key**, as the reply's `details.load_key` describes: find what loads the env file the key is in when the app starts. If the app got `OPENAI_API_KEY` from that same file, it already does. If not, load it the way the reply says.
- **Then run the reply's `run`,** and follow what that prints. It offers a test request; make it only if the user says yes.
