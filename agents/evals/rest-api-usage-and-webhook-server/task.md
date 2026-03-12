# IT Helpdesk Agent with Ticket Lookup via cURL and Webhook

## Problem/Feature Description

A mid-size company's IT department wants to automate their internal helpdesk phone line with a voice agent. They don't use any SDKs in their infrastructure -- everything is managed through shell scripts and direct HTTP API calls. They need:

1. A shell script that creates the helpdesk voice agent via the ElevenLabs REST API. The agent should be configured to answer IT support questions, use a male voice, and be powered by an Anthropic model. It should have a webhook tool that calls their internal ticket system at `https://helpdesk.internal.example.com/api/tickets/lookup` to look up ticket status (accepting a `ticket_id` parameter).

2. A second shell script that updates the existing agent to change just its system prompt and LLM temperature, without modifying any other settings.

3. A Python webhook server (using FastAPI) that acts as the ticket lookup endpoint. When the ElevenLabs platform calls this webhook, the server should parse the incoming request, look up the ticket (simulate with mock data), and respond in the correct format that ElevenLabs expects.

The IT team stores their API key in the `ELEVENLABS_API_KEY` environment variable and needs all scripts to reference it from there.

## Output Specification

Produce three files:
- `create_agent.sh` - A bash script using cURL to create the helpdesk agent via the REST API
- `update_agent.sh` - A bash script using cURL to update just the prompt and temperature of the agent (assume agent ID is in an `AGENT_ID` environment variable)
- `webhook_server.py` - A FastAPI server implementing the ticket lookup webhook endpoint
