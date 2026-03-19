![LOGO](/logo.png)

# ElevenLabs Skills

Agent skills for [ElevenLabs](https://elevenlabs.io) developer products. These skills follow the [Agent Skills specification](https://agentskills.io/specification) and can be used with any compatible AI coding assistant.

## Installation

```bash
npx skills add elevenlabs/skills
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [text-to-speech](./text-to-speech) | Convert text to lifelike speech using ElevenLabs' AI voices |
| [speech-to-text](./speech-to-text) | Transcribe audio files to text with timestamps |
| [agents](./agents) | Build conversational voice AI agents |
| [sound-effects](./sound-effects) | Generate sound effects from text descriptions |
| [music](./music) | Generate music tracks using AI composition |
| [setup-api-key](./setup-api-key) | Guide through obtaining and configuring an ElevenLabs API key |

## Configuration

All skills require an ElevenLabs API key. Set it as an environment variable:

```bash
export ELEVENLABS_API_KEY="your-api-key"
```

Get your API key from the `setup-api-key` skill or use the [ElevenLabs dashboard](https://elevenlabs.io/app/settings/api-keys).

## SDK Support

Most skills include examples for:

- **Python** - `pip install elevenlabs`
- **JavaScript/TypeScript** - `npm install @elevenlabs/elevenlabs-js`
- **cURL** - Direct REST API calls

> **JavaScript SDK Warning:** Always use `@elevenlabs/elevenlabs-js`. Do not use `npm install elevenlabs` (that's an outdated v1.x package).

See the installation guide in any skill's `references/` folder for complete setup instructions including migration from deprecated packages.

## License

MIT
test
