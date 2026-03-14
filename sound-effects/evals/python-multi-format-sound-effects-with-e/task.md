# Sound Effects Library Builder

## Problem/Feature Description

A podcast production team needs a Python tool that can generate a library of sound effects in various audio formats for different delivery channels. They have a web player that needs MP3, a high-fidelity archive that needs uncompressed PCM, and a mobile app that uses Opus. They also need telephone hold music in a telephony-compatible format.

The tool should accept a list of sound effects to generate, where each can specify its own output format, duration, and how closely the generation should follow the prompt. It needs robust error handling since the team runs it in a CI pipeline and needs clear error messages when things go wrong (invalid parameters, authentication issues, rate limits, etc.).

Build a Python module that provides a function to generate sound effects and a CLI entry point that processes a batch of effects from a config file.

## Output Specification

Produce the following files:

- `sfx_generator.py` -- A Python module with a function to generate a single sound effect (accepting text, duration, prompt_influence, output_format, and output path) and a `main()` that processes a batch config
- `batch_config.json` -- A JSON config with at least 5 sound effects, using at least 3 different output formats. Include at least one entry targeting telephony (8kHz format) and at least one targeting high-fidelity uncompressed audio.
