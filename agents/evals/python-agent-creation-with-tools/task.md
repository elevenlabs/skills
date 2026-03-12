# Restaurant Reservation Voice Agent

## Problem/Feature Description

A chain of upscale restaurants wants to deploy a voice AI agent that handles reservation inquiries over the phone. The agent should greet callers warmly, help them check reservation availability, and book tables. When a caller has a complex request (large party, special dietary needs, private dining), the agent should be able to transfer them to the restaurant's concierge line. The agent should also be able to end calls politely when the conversation is done.

The restaurants need the agent to feel natural and responsive during phone conversations. They want it to use a female voice with a professional tone and to respond quickly since callers on the phone expect low latency. The agent should automatically detect when the caller has stopped speaking rather than requiring them to press a button. The underlying language model should be cost-effective for high call volumes.

Write a Python script (`reservation_agent.py`) that creates this agent using the ElevenLabs platform. The agent should include:

1. A webhook tool that calls a hypothetical reservation API endpoint at `https://api.restaurant.example.com/reservations` to check availability (accepting date, time, and party_size parameters)
2. A system capability to transfer callers to the human concierge at +1-555-0199
3. A system capability to end calls gracefully
4. Platform settings that limit calls to 10 minutes and allow up to 5 simultaneous calls
5. A system prompt that instructs the agent to be a professional restaurant host

## Output Specification

Produce a single file:
- `reservation_agent.py` - A complete, runnable Python script that creates the agent using the ElevenLabs SDK
