# Developer Onboarding Guide for ElevenLabs Integration

## Problem/Feature Description

Our company is starting a new project that integrates ElevenLabs for AI voice generation. The engineering lead has asked for a comprehensive onboarding script that new team members can run to get set up with the ElevenLabs API. The script should walk the developer through every step -- from creating an account if they don't have one, to generating an API key with the right permissions, to having the key stored and ready for the project's tooling.

The onboarding script needs to be self-contained and handle the full happy path as well as edge cases like the developer pasting an incorrect key. The team uses a standard project layout where configuration is loaded from environment files.

## Output Specification

Create a file called `onboard.sh` -- a Bash script that:
- Displays clear step-by-step instructions for the developer to follow
- Prompts the developer for their API key
- Attempts to verify the key works
- Saves the key for use by the project
- Handles the case where the key doesn't work

The script should be executable with `bash onboard.sh`. It should use `curl` for any HTTP requests.

Also create a file called `onboard-instructions.txt` that contains the exact text the script would display to the user as the initial setup instructions (before prompting for the key). This file serves as a reference for the team to review the messaging.
