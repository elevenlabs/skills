# ElevenLabs Key Validation Library

## Problem/Feature Description

We're building a suite of internal tools that interact with the ElevenLabs API. Multiple tools in the suite need to validate API keys before performing operations -- for example, the text-to-speech tool, the voice cloning tool, and the audio isolation tool all need to confirm the user's API key is valid before making expensive API calls.

Rather than duplicating key validation logic across every tool, we need a shared JavaScript/Node.js module that any tool can import. The module should handle validating a key against ElevenLabs, and persisting a validated key to the project's local configuration so other tools can pick it up later. It should also provide a function that loads a previously-stored key.

## Output Specification

Create the following files:

1. `elevenlabs-auth.js` - A Node.js module (CommonJS) that exports:
   - `validateKey(apiKey)` - Validates an API key against ElevenLabs, returns a boolean or throws on network error
   - `saveKey(apiKey)` - Persists a validated API key to local project configuration
   - `loadKey()` - Loads a previously stored API key, returns null if not found

2. `test-auth.js` - A script that demonstrates usage of the module: imports the module, shows how each function would be called with a placeholder key, and logs the results. This script should be runnable with `node test-auth.js` (it's acceptable for the validation call to fail with a network error or invalid key since no real key is available).

Use only Node.js built-in modules (no npm packages).
