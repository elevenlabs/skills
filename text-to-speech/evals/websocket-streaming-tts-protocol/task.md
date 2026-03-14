# Real-Time Voice Output for an AI Chatbot

## Problem/Feature Description

A startup is building an AI chatbot that generates responses token-by-token from a language model. They want to speak each response aloud in real time as the LLM produces text, rather than waiting for the entire response before generating audio. This requires streaming text to the TTS service as it arrives and receiving audio chunks back to play immediately.

The system needs to handle conversation turns properly -- when the bot finishes a response and waits for user input, the audio should not be left buffering silently. It also needs to stay connected during thinking pauses without the connection dropping. The team needs a Python implementation using WebSockets that connects to ElevenLabs and streams text from a simulated LLM output.

## Output Specification

Produce the following files:

- `chatbot_voice.py` -- A Python async module that:
  - Establishes a WebSocket connection to ElevenLabs for text-to-speech streaming
  - Has a function that accepts an async iterator of text chunks (simulating LLM token output) and streams them to the TTS service
  - Properly initializes the WebSocket connection with voice configuration
  - Handles end-of-turn correctly so audio is not left in a buffer
  - Implements keepalive logic for periods when the LLM is thinking
  - Collects the returned audio chunks and writes them to an output file
  - Properly closes the connection when done
  - Selects a model appropriate for low-latency streaming

- `demo_chat.py` -- A demonstration script that simulates a 2-turn conversation: it creates a fake LLM iterator that yields words one at a time with small delays, feeds them to the chatbot_voice module, and saves the resulting audio. Include at least 2 conversation turns.
