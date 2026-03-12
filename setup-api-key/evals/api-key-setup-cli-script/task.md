# ElevenLabs API Key Setup Script

## Problem/Feature Description

Our team is onboarding several new developers who will be working with the ElevenLabs API for various audio generation tasks. Currently, each developer has to manually figure out where to get their API key, how to validate it works, and where to store it. This is error-prone and wastes time.

We need a Python script that automates this process: it should prompt the developer for their API key, verify it against the ElevenLabs API, handle cases where the key is invalid (with a retry), and store the validated key for use by other tools in the project.

## Output Specification

Create a file called `setup_elevenlabs.py` that:
- Prompts the user for their ElevenLabs API key
- Validates the key against the ElevenLabs API
- Handles invalid keys with appropriate error messaging and a retry opportunity
- Stores the validated key for use by other project tools
- Provides clear feedback at each step

The script should be runnable with `python setup_elevenlabs.py`. Use only the Python standard library (no third-party packages required).
