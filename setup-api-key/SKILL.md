---
name: setup-api-key
description: Guides users through setting up an ElevenLabs API key for ElevenLabs tools. Use when the user needs to configure ELEVENLABS_API_KEY, when ElevenLabs API calls fail because of authentication, or when the user mentions needing ElevenLabs account/API access. Checks existing environment configuration first and never asks the user to paste secrets into chat.
license: MIT
compatibility: Requires internet access to elevenlabs.io and api.elevenlabs.io.
---

# ElevenLabs API Key Setup

Guide the user through obtaining and configuring an ElevenLabs API key without exposing the key in chat.

## Workflow

### Step 0: Check for an existing API key first

Before guiding setup, check for an existing `ELEVENLABS_API_KEY`:

1. Check whether `ELEVENLABS_API_KEY` exists in the current environment.
2. If it is not in the environment, check `.env` for `ELEVENLABS_API_KEY=<value>`.
3. Do not print, quote, or repeat the key. If you mention it, redact it.
4. If an existing key is found, validate it:
   ```text
   GET https://api.elevenlabs.io/v1/user
   Header: xi-api-key: <existing-api-key>
   ```
5. If validation succeeds:
   - Tell the user ElevenLabs is already configured and working.
   - Skip the setup flow.
   - Ask whether they want help rotating the key; if not, stop.
6. If validation fails:
   - Tell the user the existing key appears invalid or expired.
   - Continue to Step 1.

### Step 1: Tell the user how to create and save the key

Never ask the user to paste an API key into chat. Tell them:

> To set up ElevenLabs, open the API keys page:
> https://elevenlabs.io/app/settings/api-keys
>
> Need an account first? Create one at:
> https://elevenlabs.io/app/sign-up
>
> If you do not have an API key yet:
> 1. Click "Create key".
> 2. Name it, or use the default name.
> 3. Choose permissions appropriate for what you are building. For basic validation, the key needs "User" read access.
> 4. Click "Create key" to confirm.
> 5. Copy the key immediately; it is only shown once.
>
> Do not paste the key into this chat. Instead, copy/paste it into your local `.env` file:
>
> ```env
> ELEVENLABS_API_KEY=your-api-key
> ```
>
> If `.env` already has an `ELEVENLABS_API_KEY=...` line, replace that line. Tell me when you have saved it, without sharing the key.

Then wait for the user to confirm that the key is saved locally.

### Step 2: Validate local configuration

After the user says the key is saved:

1. Re-check the current environment and `.env` for `ELEVENLABS_API_KEY`.
2. If no key is found:
   - Tell the user `.env` does not appear to contain `ELEVENLABS_API_KEY`.
   - Show the expected line again.
   - Remind them not to paste the key into chat.
3. If a key is found, validate it:
   ```text
   GET https://api.elevenlabs.io/v1/user
   Header: xi-api-key: <local-api-key>
   ```
4. If validation fails:
   - Tell the user the local key appears invalid or expired.
   - Remind them of the API keys page.
   - Ask them to replace the `.env` value and tell you when it is saved.
5. If validation succeeds, confirm:
   > Done. ElevenLabs is configured and the key in `.env` works.

## Safety Rules

- Never ask the user to paste an API key, token, or secret into chat.
- Never print or echo API key values from environment variables or `.env`.
- Prefer `.env` or managed secrets over shell history for persistent local configuration.
- For browser or client-side apps, keep `ELEVENLABS_API_KEY` on the server and issue short-lived tokens where applicable.
