# ElevenLabs API Health Check and Configuration Tool

## Problem/Feature Description

Our CI/CD pipeline needs a pre-flight check that verifies the ElevenLabs API key is configured and working before deploying our voice synthesis service. Currently, deployments sometimes fail midway because the API key in the environment is expired or misconfigured, wasting build minutes and causing confusion.

We need a Python utility that can be called from our deployment scripts. It should load an existing key from configuration, test it against ElevenLabs, and report the result. It should also have a "setup" mode where it can interactively collect a new key from a developer, validate it with appropriate retry logic (we don't want to lock out accounts with infinite retries), and persist it.

## Output Specification

Create a file called `elevenlabs_config.py` that provides:
- A function `check_key(api_key)` that validates a given key against the ElevenLabs API and returns True/False
- A function `setup_key()` that interactively prompts for a key, validates it, handles failures with limited retries, and persists the validated key
- A function `load_key()` that retrieves a previously stored key from the project configuration
- A `if __name__ == "__main__"` block that runs in two modes:
  - `python elevenlabs_config.py check` - loads and checks the stored key
  - `python elevenlabs_config.py setup` - runs the interactive setup

Use only the Python standard library.
