---
name: setup-api-key
description: Fix or hand-configure an existing ElevenLabs API key. Use when a key stopped working (401 or invalid_api_key), when an administrator issued the key, when the user's role cannot create keys, when the user already has a key and needs it in the right place, or when the onboarding skill reported that it cannot create a key for this account. First checks whether ELEVENLABS_API_KEY is configured and valid. Not for first-time setup or adding ElevenLabs to a project (use onboarding).
license: MIT
compatibility: Requires internet access to elevenlabs.io and api.elevenlabs.io.
---

# ElevenLabs API Key Setup

Fix or hand-configure an ElevenLabs API key. For adding ElevenLabs to a project
from scratch, use the `onboarding` skill instead; it hands off here when it
reports `legacy`, meaning the account cannot create keys through the approval
page.

**Which env file.** Everything below says `<file>`. It is `.env.local` when
the project has one (the `onboarding` skill writes an empty
`ELEVENLABS_API_KEY=` line there before handing off), otherwise `.env`. An
empty `ELEVENLABS_API_KEY=` line counts as no key.

Two cases need no key from this skill, only the right placement:

- **An administrator issued the key.** Skip Step 1 and go to Step 2: the user
  saves the key they were given into `<file>` and you validate it.
- **The user's role cannot create keys** (`onboarding` reported
  `not_permitted`). Tell them to ask a workspace administrator for a key
  (Workspace settings, Members), then go to Step 2 once they have it.

When `onboarding` reported `not_available` or `failed`, the account can create
keys but the approval page could not do it this time: run the normal flow from
Step 0.

## Workflow

### Step 0: Check for an existing API key first

Before asking the user for a key, check for an existing `ELEVENLABS_API_KEY`:

1. Check whether `ELEVENLABS_API_KEY` exists in the current environment. If it does, use that value for this initial check.
2. Only if it is not in the environment, check `<file>` for `ELEVENLABS_API_KEY=<value>` with a non-empty value.
3. Do not print, quote, or repeat the key. If you mention it, redact it.
4. If an existing key is found, validate it:
   ```text
   GET https://api.elevenlabs.io/v1/user
   Header: xi-api-key: <existing-api-key>
   ```
5. **If existing key validation succeeds:**
   - Tell the user ElevenLabs is already configured and working
   - Skip the setup flow
   - Ask whether they want to replace/rotate the key; if not, stop
6. **If existing key validation fails:**
   - Tell the user the existing key appears invalid or expired
   - Continue to Step 1

### Step 1: Request the API key

Tell the user:

> Open the API keys page: https://elevenlabs.io/app/settings/api-keys
>
> Create a key (and if an old key stopped working, delete it there too):
> 1. Click "Create key"
> 2. Name it (or use the default)
> 3. Set permission for your key. If you provide a key with "User" permission set to "Read" this skill will automatically verify if your key works
> 4. Click "Create key" to confirm
> 5. **Copy the key immediately** - it's only shown once!
>
> Do not paste the key into this chat. Instead, copy/paste it into your local `<file>`:
>
> ```
> ELEVENLABS_API_KEY=your-api-key
> ```
>
> If `<file>` already has an `ELEVENLABS_API_KEY=` line (even an empty one), put the key on that line.
> Tell me when you've saved it, without sharing the key.

Then wait for the user to confirm that the key is saved locally.

### Step 2: Validate and configure

After the user says the key is saved:

1. Re-check both `<file>` and the current environment for `ELEVENLABS_API_KEY`, but treat `<file>` as the source of truth for this step.
2. If `<file>` contains a non-empty value, validate that value even when the current environment also has a different `ELEVENLABS_API_KEY`.
3. If `<file>` does not contain the key:
   - Tell the user `<file>` does not appear to contain `ELEVENLABS_API_KEY`.
   - Show the expected line again.
   - If the current environment does contain a key, note that this step still requires saving the key in `<file>`.
   - Remind them not to paste the key into chat.
4. If a `<file>` key is found, validate it:
   ```text
   GET https://api.elevenlabs.io/v1/user
   Header: xi-api-key: <local-api-key>
   ```
5. If validation fails:
   - Tell the user the local key appears invalid or expired.
   - Remind them of the API keys page.
   - Ask them to replace the `<file>` value and tell you when it is saved.
6. If validation succeeds, confirm:
   > Done. ElevenLabs is configured and the key in `<file>` works.

## Safety Rules

- Never ask the user to paste an API key, token, or secret into chat.
- Never print or echo API key values from environment variables or env files.
- Prefer `<file>` or managed secrets over shell history for persistent local configuration.
- For browser or client-side apps, keep `ELEVENLABS_API_KEY` on the server and issue short-lived tokens where applicable.
