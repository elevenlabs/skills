# Sound Effects Build Pipeline Script

## Problem/Feature Description

A video production company wants a portable shell script (Bash) that generates sound effects via the ElevenLabs REST API using cURL. They do not want to install any SDKs or language runtimes beyond what a standard Linux system provides. The script should read sound effect definitions from a simple JSON file and generate each one, saving the audio files to an `output/` directory.

Some of their sound effects need to be in specific formats -- they need MP3 for web delivery, Opus for their mobile app, and PCM for their audio editing pipeline. The script should support per-effect format configuration. Each sound effect also has a specific desired duration.

Write a Bash script and an accompanying configuration file.

## Output Specification

Produce the following files:

- `generate.sh` -- A Bash script that reads the config, creates the output directory, and generates each sound effect via cURL
- `effects.json` -- A JSON config file listing at least 4 sound effects. Each entry should have: `name`, `prompt`, `duration`, `output_format`, and `filename`. Use a mix of at least 2 different output formats. Include at least one effect shorter than 2 seconds and at least one longer than 10 seconds.
