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
| [sound-effects](./sound-effects) | Generate sound effects from text descriptions |

## Configuration

All skills require an ElevenLabs API key. Set it as an environment variable:

```bash
export ELEVENLABS_API_KEY="your-api-key"
```

Get your API key from the [ElevenLabs dashboard](https://elevenlabs.io/app/settings/api-keys).

## SDK Support

Each skill includes examples for:

- **Python** - `elevenlabs` package
- **JavaScript/TypeScript** - `@elevenlabs/elevenlabs-js`
- **cURL** - Direct REST API calls

## License

MIT
