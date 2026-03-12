# Sound Effects API Wrapper with Validation

## Problem/Feature Description

A SaaS company is building an internal Node.js microservice that wraps the ElevenLabs sound effects API. Before forwarding requests to ElevenLabs, the wrapper needs to validate all input parameters to catch bad requests early and return helpful error messages to internal callers. The service will also provide a set of preset configurations for common sound effect categories (UI sounds, cinematic impacts, ambient loops, foley).

The wrapper should validate parameters against their allowed ranges, ensure mutually compatible option combinations, and provide a clean TypeScript-compatible interface. It should include preset configurations that demonstrate good prompt engineering for each category.

## Output Specification

Produce the following files:

- `sfx-service.js` -- The Node.js module exporting a `generateSoundEffect` function that validates inputs and calls the ElevenLabs API, plus a `PRESETS` object with at least 4 named presets
- `package.json` -- With the necessary dependencies
- `test-validation.js` -- A script that tests the validation logic by calling `generateSoundEffect` with various invalid inputs (without making real API calls) and logging whether validation correctly rejects them. Test at least: out-of-range duration, out-of-range prompt_influence, empty text, and invalid output_format.
