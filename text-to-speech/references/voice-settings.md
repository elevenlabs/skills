# Voice Settings

Fine-tune voice characteristics for your use case.

## Parameters

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `stability` | 0.0 - 1.0 | 0.5 | How consistent the voice sounds across the generation. Lower = more emotional variation and expressiveness (but can sound erratic). Higher = steady, predictable tone. |
| `similarity_boost` | 0.0 - 1.0 | 0.75 | How closely to match the original voice sample. Higher sounds more like the source voice but may amplify audio artifacts or background noise from the original recording. |
| `style` | 0.0 - 1.0 | 0.0 | Exaggerates the unique characteristics of the voice's speaking style (v2+ and v3 models only). Higher values make the voice more "characterful" but can reduce stability. |
| `speed` | 0.25 - 4.0 | 1.0 | Speech speed multiplier. 1.0 = normal speed. Range is 0.25-4.0 for the REST API; the Agents Platform restricts to 0.7-1.2. |
| `use_speaker_boost` | boolean | true | Post-processing that enhances voice clarity and similarity to the original. Generally leave this on unless you're experiencing artifacts. |

## Python Example

```python
from elevenlabs import ElevenLabs
from elevenlabs import VoiceSettings

client = ElevenLabs()

audio = client.text_to_speech.convert(
    text="Testing different voice settings.",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_v3",
    voice_settings=VoiceSettings(
        stability=0.5,
        similarity_boost=0.75,
        style=0.0,
        use_speaker_boost=True
    )
)
```

## JavaScript Example

```javascript
const audio = await client.textToSpeech.convert("JBFqnCBsd6RMkjVDRZzb", {
  text: "Testing different voice settings.",
  modelId: "eleven_v3",
  voiceSettings: {
    stability: 0.5,
    similarityBoost: 0.75,
    style: 0.0,
    useSpeakerBoost: true,
  },
});
```

## cURL Example

```bash
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Testing different voice settings.",
    "model_id": "eleven_v3",
    "voice_settings": {
      "stability": 0.5,
      "similarity_boost": 0.75,
      "style": 0.0,
      "use_speaker_boost": true
    }
  }' \
  --output output.mp3
```

## Use Case Recommendations

### Audiobooks / Narration
```python
voice_settings=VoiceSettings(
    stability=0.7,        # Consistent tone
    similarity_boost=0.5, # Natural variation
    style=0.0
)
```

### Conversational / Chatbots
```python
voice_settings=VoiceSettings(
    stability=0.4,        # More expressive
    similarity_boost=0.75,
    style=0.3             # Slight style emphasis
)
```

### News / Professional
```python
voice_settings=VoiceSettings(
    stability=0.8,        # Very consistent
    similarity_boost=0.6,
    style=0.0
)
```

### Character Voices / Drama
```python
voice_settings=VoiceSettings(
    stability=0.3,        # Highly expressive
    similarity_boost=0.8,
    style=0.5             # Strong style
)
```

## Tips

- **Start with defaults** and adjust incrementally
- **Lower stability** if voice sounds monotonous
- **Reduce similarity_boost** if you hear audio artifacts
- **Style works** with v2+, v3, and multilingual models
- **Test with representative text** from your actual use case
- **Flash models** ignore some voice settings for speed
