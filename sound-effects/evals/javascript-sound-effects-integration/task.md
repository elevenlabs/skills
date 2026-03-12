# Game Audio Asset Generator

## Problem/Feature Description

An indie game studio is building a 2D platformer and needs a Node.js command-line tool to generate sound effect assets from text descriptions using the ElevenLabs API. The tool should accept a JSON manifest file that lists sound effects to generate (each with a name, text description, and output filename), iterate through them, and save each generated audio file to an `output/` directory.

The team wants this as a reusable CLI script they can run during their build process. The script should read from the environment for credentials, handle the streaming response properly, and produce properly saved audio files.

## Output Specification

Produce the following files:

- `generate-sfx.js` -- The Node.js script that reads a manifest and generates sound effects
- `package.json` -- With the necessary dependencies declared
- `manifest.json` -- A sample manifest file containing at least 3 sound effects with descriptive names suitable for a platformer game (e.g., jump, coin collect, enemy defeat). Each entry should have a `name`, `text` (the prompt), and `filename` field.
