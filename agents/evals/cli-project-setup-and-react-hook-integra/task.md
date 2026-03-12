# Bilingual Customer Service Agent Setup

## Problem/Feature Description

A SaaS company is building a bilingual (English and Spanish) voice customer service system. They want to set up two voice agents: one for English-speaking customers and one for Spanish-speaking customers. Both agents need to handle common support tasks like checking account status, resetting passwords, and escalating to a human agent.

The engineering team needs two things:

1. A setup guide document (`setup_guide.md`) that documents the exact CLI commands to: install the ElevenLabs CLI, authenticate, initialize a new project, create both agents from appropriate templates, and deploy them. The guide should list each command in order with brief explanations.

2. A React component (`VoiceSupport.jsx`) that provides a language-toggling voice support interface. The component should use the ElevenLabs React hook for managing the conversation. Based on the user's language selection, it should connect to the appropriate agent. The component should fetch a signed URL from a backend endpoint before starting the session and display the conversation status (listening, speaking, idle) and a transcript of the conversation. The backend provides signed URLs at `/api/voice/signed-url?agentId=<id>`.

The team wants to use the `customer-service` template for both agents since it includes common support patterns.

## Output Specification

Produce two files:
- `setup_guide.md` - Step-by-step CLI commands to install, authenticate, create both agents, and deploy
- `VoiceSupport.jsx` - React component implementing the bilingual voice support interface with language toggle
