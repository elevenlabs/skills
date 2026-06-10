---
name: setup-api-key
description: Guides users through setting up an ElevenLabs API key for ElevenLabs MCP tools. Use when the user needs to configure an ElevenLabs API key, when ElevenLabs tools fail due to missing API key, or when the user mentions needing access to ElevenLabs. First checks whether ELEVENLABS_API_KEY is already configured and valid, and only runs full setup when needed.
license: MIT
compatibility: Requires internet access to elevenlabs.io and api.elevenlabs.io.
---

# ElevenLabs API Key Setup

Guide the user through obtaining and configuring an ElevenLabs API key.

## Workflow

### Step 0: Check for an existing API key first

Before asking the user for a key, check for an existing `ELEVENLABS_API_KEY`:

1. Check whether `ELEVENLABS_API_KEY` exists in the current environment. If it does, use that value for this initial check.
2. Only if it is not in the environment, check `.env` for `ELEVENLABS_API_KEY=<value>`.
3. Do not print, quote, or repeat the key. If you mention it, redact it.
4. If an existing key is found, validate it:
   ```text
   GET https://api.elevenlabs.io/v1/user
   Header: xi-api-key: <existing-api-key>
   ```
4. **If existing key validation succeeds:**
   - Tell the user ElevenLabs is already configured and working
   - Skip the setup flow
   - Ask whether they want to replace/rotate the key; if not, stop
5. **If existing key validation fails:**
   - Tell the user the existing key appears invalid or expired
   - Continue to Step 1

### Step 1: Request the API key

Tell the user:

> To set up ElevenLabs, open the API keys page: https://elevenlabs.io/app/settings/api-keys
>
> (Need an account? Create one at https://elevenlabs.io/app/sign-up first)
>
> If you don't have an API key yet:
> 1. Click "Create key"
> 2. Name it (or use the default)
> 3. Set permission for your key. If you provide a key with "User" permission set to "Read" this skill will automatically verify if your key works
> 4. Click "Create key" to confirm
> 5. **Copy the key immediately** - it's only shown once!
>
> Do not paste the key into this chat. Instead, copy/paste it into your local `.env` file:
>
> ```
> ELEVENLABS_API_KEY=your-api-key
> ```
>
> If `.env` already has an `ELEVENLABS_API_KEY=...` line, replace that line.
> Tell me when you've saved it, without sharing the key.

Then wait for the user to confirm that the key is saved locally.

### Step 2: Validate and configure

After the user says the key is saved:

1. Re-check both `.env` and the current environment for `ELEVENLABS_API_KEY`, but treat `.env` as the source of truth for this step.
2. If `.env` contains a value, validate that value even when the current environment also has a different `ELEVENLABS_API_KEY`.
3. If `.env` does not contain the key:
   - Tell the user `.env` does not appear to contain `ELEVENLABS_API_KEY`.
   - Show the expected line again.
   - If the current environment does contain a key, note that this step still requires saving the key in `.env`.
   - Remind them not to paste the key into chat.
4. If a `.env` key is found, validate it:
   ```text
   GET https://api.elevenlabs.io/v1/user
   Header: xi-api-key: <local-api-key>
   ```
5. If validation fails:
   - Tell the user the local key appears invalid or expired.
   - Remind them of the API keys page.
   - Ask them to replace the `.env` value and tell you when it is saved.
6. If validation succeeds, confirm:
   > Done. ElevenLabs is configured and the key in `.env` works.

## Safety Rules

- Never ask the user to paste an API key, token, or secret into chat.
- Never print or echo API key values from environment variables or `.env`.
- Prefer `.env` or managed secrets over shell history for persistent local configuration.
- For browser or client-side apps, keep `ELEVENLABS_API_KEY` on the server and issue short-lived tokens where applicable.
