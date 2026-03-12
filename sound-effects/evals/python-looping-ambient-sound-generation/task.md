# Ambient Soundscape Generator for a Meditation App

## Problem/Feature Description

A wellness startup is building a meditation app and needs a Python script that generates looping ambient soundscapes using the ElevenLabs API. The script should generate several ambient audio tracks that loop seamlessly -- things like rain, forest sounds, ocean waves, etc. Each track needs to be a specific duration (between 5 and 15 seconds) since the app will loop them continuously during meditation sessions. The team also wants control over how closely the generated audio follows the prompt descriptions, since some sounds benefit from more creative interpretation while others need to be precise.

Write a Python script that generates a set of at least 4 ambient soundscapes, saves them to disk, and includes a configuration section at the top defining the soundscapes to generate.

## Output Specification

Produce the following files:

- `generate_ambience.py` -- The Python script that generates the ambient soundscapes
- `soundscapes.json` -- A JSON configuration file listing the soundscapes to generate. Each entry should have fields for: `name`, `prompt` (the text description), `duration` (in seconds), `prompt_influence` (a float), and `output_file`.
