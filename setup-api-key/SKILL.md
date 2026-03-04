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

1. Check whether `ELEVENLABS_API_KEY` exists in the current environment.
2. If it's not in the environment, check `.env` for `ELEVENLABS_API_KEY=<value>`.
3. If an existing key is found, **validate it**:
   ```
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
> Paste your API key here when ready.

Then wait for the user's next message which should contain the API key.

### Step 2: Validate and configure

Once the user provides the API key:

1. **Validate the key** by making a request:
   ```
   GET https://api.elevenlabs.io/v1/user
   Header: xi-api-key: <the-api-key>
   ```

2. **If validation fails:**
   - Tell the user the API key appears to be invalid
   - Ask them to try again
   - Remind them of the URL: https://elevenlabs.io/app/settings/api-keys
   - If it fails a second time, display an error and exit

3. **If validation succeeds**, save the API key in a `.env` file:
   ```
   ELEVENLABS_API_KEY=<the-api-key>
   ```
   - If `.env` already has `ELEVENLABS_API_KEY=...`, replace that line
   - Otherwise add a new line for `ELEVENLABS_API_KEY`

4. **Confirm success:**
   > Done! Your key is stored as an environment variable in .env
   > Keep the key safe! Don't share it with anyone!
