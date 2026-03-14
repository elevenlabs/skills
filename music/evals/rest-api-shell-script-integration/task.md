# Shell-Based Music Generation Pipeline for CI/CD

## Problem/Feature Description

A media agency automates their content pipeline using shell scripts that run in CI/CD environments where Python and Node.js are not guaranteed to be installed. They need a bash script that can generate background music tracks directly using cURL calls to the ElevenLabs REST API. The script should be self-contained and work in any POSIX environment with cURL available.

The script will be called by their CI pipeline to generate music assets as part of their automated content build process. It needs to accept a prompt, a duration, and an output filename, and make the appropriate API call to generate and save the music.

## Output Specification

Create a bash script called `generate_music.sh` that:

1. Accepts three arguments: a text prompt, duration in seconds, and output filename
2. Reads the API key from the environment
3. Makes a cURL request to the ElevenLabs music generation API
4. Saves the output as an MP3 file
5. Exits with appropriate error codes on failure

Also create a companion script called `batch_generate.sh` that calls `generate_music.sh` multiple times to generate three tracks:
- A 10-second news intro jingle
- A 30-second corporate presentation background
- A 20-second upbeat social media clip

Both scripts should include comments explaining the API interaction.
