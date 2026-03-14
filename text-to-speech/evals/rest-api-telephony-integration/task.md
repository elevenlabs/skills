# Phone System Voice Prompts Generator

## Problem/Feature Description

A healthcare clinic is setting up an automated phone system (IVR) to handle appointment confirmations, prescription refill reminders, and after-hours greetings. The system runs on a standard telephony platform and needs pre-generated voice prompts stored as audio files in the format that phone systems expect.

The clinic wants a shell script that uses the ElevenLabs REST API directly (via cURL) to generate a set of voice prompts. Each prompt has different content but should use the same professional-sounding female voice. The prompts will be played over phone lines, so they need to be in the correct encoding for telephony. The script should also generate one prompt in Spanish for their bilingual patients, using a model that supports Spanish.

Because the ops team will maintain this script, it should be well-structured with the API key loaded from the environment, and each cURL command should be clear and self-contained.

## Output Specification

Produce the following files:

- `generate_prompts.sh` -- A bash script that:
  - Generates at least 4 voice prompts: a greeting, an appointment confirmation, a prescription reminder, and a Spanish-language after-hours message
  - Uses cURL to call the ElevenLabs REST API for each prompt
  - Outputs each prompt to a separate file (e.g., `greeting.audio`, `appointment.audio`, etc.)
  - Uses the same female voice for all prompts
  - Selects an audio format appropriate for telephone playback
  - Uses a model that can handle both English and Spanish
  - Includes text normalization for prompts that contain phone numbers or dates
  - Includes basic error checking (e.g., check cURL exit codes)

- `prompts.json` -- A JSON file listing all prompts with their text content, output filenames, and language codes
