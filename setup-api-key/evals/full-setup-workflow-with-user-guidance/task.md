# ElevenLabs Integration Bootstrap for New Projects

## Problem/Feature Description

We maintain a project scaffolding tool that sets up new microservices. We're adding ElevenLabs support, and need a bootstrap module that can be dropped into any new project. When a developer runs the bootstrap, it should guide them through the entire ElevenLabs setup from scratch -- including directing them to create an account if needed, walking them through key creation with the right settings, validating the key, and saving configuration.

The bootstrap needs to be thorough in its guidance because many developers on the team have never used ElevenLabs before. It should cover the full journey from "I have no account" to "my project is configured and ready to make API calls."

## Output Specification

Create a file called `bootstrap_elevenlabs.py` that implements the complete bootstrap flow:

- Displays setup instructions for the developer
- Collects the API key from the developer
- Validates and persists the key
- Handles errors with appropriate retry behavior

Also create `SETUP_GUIDE.txt` -- a plain text file containing the exact user-facing instructions that the bootstrap script displays at the start. This will be reviewed by the product team for tone and completeness. The guide should cover every step a brand-new user would need, from account creation through key generation.

Use only the Python standard library.
