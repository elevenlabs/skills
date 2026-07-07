---
name: healthcare-voice-ai
description: Build voice AI for clinical and healthcare applications using ElevenLabs. Use when creating doctor-facing voice alerts, patient-facing voice agents, clinical note dictation, doctor-patient conversation transcription, or any real-time audio feature inside an EHR, telehealth, or care-coordination product. Covers PHI-safe handling of voice AI requests.
license: MIT
compatibility: Requires internet access and an ElevenLabs API key (ELEVENLABS_API_KEY).
metadata: {"openclaw": {"requires": {"env": ["ELEVENLABS_API_KEY"]}, "primaryEnv": "ELEVENLABS_API_KEY"}}
---

# ElevenLabs Clinical Voice Assistant

Build voice AI for clinical and healthcare workflows — urgent alerts for clinicians, patient-facing conversational agents, and transcription of doctor-patient conversations — using ElevenLabs' TTS, STT, and Agents platform.

> **Setup:** See the [installation guide](https://github.com/elevenlabs/skills/blob/main/text-to-speech/references/installation.md) in the `text-to-speech` skill for SDK install and API key configuration. For JavaScript, use `@elevenlabs/*` packages only.

## Why ElevenLabs for Clinical Voice, Not Generic TTS

Generic TTS engines are built for narration. Clinical voice AI has different failure modes, and ElevenLabs has features that map directly onto them:

- **Latency that matches clinical urgency.** `eleven_flash_v2_5` generates audio in ~75ms model latency, which is what makes a "missed screening" or "critical lab value" alert usable the moment it fires, instead of arriving 3-5 seconds late. See [references/voice-alerts.md](references/voice-alerts.md).
- **Pronunciation control for medical vocabulary.** Drug names, dosages, and abbreviations (mg, PRN, BID, SOB) are exactly what generic TTS mispronounces. Pronunciation dictionaries and text normalization settings let you fix this deterministically instead of hoping the model guesses right. See [references/clinical-tts.md](references/clinical-tts.md).
- **Transcription with built-in PHI awareness.** ElevenLabs Scribe (`scribe_v2`) supports `entity_detection` and `entity_redaction` with a `phi` category, so protected health information can be flagged or redacted from a transcript as part of the same API call that produces it, rather than as a separate pass you have to build yourself. See [references/speech-to-text.md](references/speech-to-text.md).
- **Zero-retention mode.** Passing `enable_logging=False` on TTS and STT requests keeps ElevenLabs from storing the request. This is necessary (not sufficient) for HIPAA-eligible use — see the PHI/HIPAA section below.
- **Guardrails built for regulated conversation.** The Agents platform has a `medical_and_legal_information` content-filter category and custom LLM-evaluated guardrails (e.g., "no medical diagnoses"), so a patient-facing agent can be constrained from giving diagnostic or treatment advice at the platform level, not just via prompt instructions.

## Decision Guide: TTS Alerts vs. Conversational Agents vs. Streaming

Pick based on who is listening and how the audio needs to reach them:

| If you need to... | Use | Why |
|---|---|---|
| Speak a single, time-critical alert to a clinician (missed screening, abnormal vital, critical lab) | **TTS `convert` or `stream`** with a Flash model | One-shot audio generation, no conversation state needed. Optimize for latency, not naturalness. |
| Let a patient ask questions, book appointments, or complete an intake conversation | **Conversational AI (Agents platform)** | Needs turn-taking, memory of the conversation, tool calls (e.g., check appointment slots), and guardrails against giving medical advice. |
| Pipe audio to a phone call, hardware speaker, or continuous monitor feed | **Streaming (`stream` / WebSocket / real-time STT)** | You need chunked audio or text as it's generated/spoken rather than a single file, e.g., IVR systems, bedside monitors, or live transcription during a visit. |
| Turn a doctor-patient conversation into a clinical note | **STT (batch or real-time) + LLM** | Transcribe first (with diarization so doctor and patient are separated), then summarize into SOAP format with an LLM. ElevenLabs does the transcription; your LLM does the clinical summarization. |

A rule of thumb: if the interaction has more than one turn or needs to understand what it's hearing, it's an agent. If it's "take this text, say it out loud, right now," it's TTS. If it's "take this audio, get text out," it's STT.

## Common Clinical Voice Patterns

**Doctor-facing alerts.** A backend job (e.g., a scheduled screening check) detects a condition — a missed PHQ-9, an overdue vaccination, a critical potassium value — and needs to speak it into a clinician's workflow (nurse station speaker, on-call phone line, desktop app). Use TTS with a Flash model and a professional, unambiguous voice. Full pattern and a runnable FastAPI endpoint: [references/voice-alerts.md](references/voice-alerts.md).

**Patient-facing voice agents.** A conversational agent handles appointment scheduling, medication reminders, or pre-visit intake questions. Configure `medical_and_legal_information` guardrails and a custom rule blocking diagnosis/treatment advice; keep the system prompt scoped to logistics, not clinical judgment.

**Clinical documentation from conversation.** Record or stream a doctor-patient visit, transcribe with `scribe_v2` and `diarize=True`, then pass the diarized transcript to an LLM to draft a SOAP note for clinician review (never auto-submit to the chart). See [references/speech-to-text.md](references/speech-to-text.md) and [references/clinical-tts.md](references/clinical-tts.md) for reading structured notes back as speech.

**Real-time audio processing.** Bedside monitoring, live captioning during a telehealth visit, or a voice interface embedded in a device — all lean on the same real-time STT and TTS streaming primitives, just wired into a different transport (WebSocket, Twilio, LiveKit).

## PHI / HIPAA Considerations

Read this before sending any patient data through a voice API.

1. **Never send raw patient identifiers in a TTS request.** Convert clinical facts into de-identified, alert-style text before calling `text_to_speech.convert` or `.stream`. "Missed PHQ-9 screening detected for patient in Room 4B" is safer than including a name, MRN, or date of birth. Route identity lookup through your own authenticated system, not through the spoken alert.
2. **Treat STT output as containing PHI by default.** Any transcript of a doctor-patient conversation is PHI. Use `entity_detection="phi"` or `entity_redaction="phi"` on `speech_to_text.convert` to flag or strip PHI spans before the transcript is logged, indexed, or handed to a downstream LLM that isn't part of your covered workflow.
3. **Zero-retention mode is necessary but not sufficient.** Setting `enable_logging=False` on TTS and STT requests stops ElevenLabs from retaining the request/response. It does **not** by itself make your integration HIPAA-compliant — you still need a signed Business Associate Agreement (BAA), which ElevenLabs only offers to Enterprise customers with Zero Retention Mode engaged, and only for HIPAA-eligible services (the Agents/Conversational AI platform). Confirm current BAA scope and eligible services with your ElevenLabs account team before handling real PHI in production.
4. **De-identify before you generate, not after.** Build the de-identification step (stripping names, MRNs, DOB, addresses) into your application layer before text ever reaches an ElevenLabs API call. Don't rely on the API to catch what you send it on the TTS side — there is no PHI filter on text-to-speech input, only on speech-to-text output.
5. **Scope conversational agents with guardrails, not just prompts.** For patient-facing agents, enable the `medical_and_legal_information` content guardrail and add a custom guardrail rule refusing diagnosis or treatment advice. Guardrails run independently of the LLM and fail closed on blocking rules, which a system prompt alone cannot guarantee.
6. **Log access, not content.** Where possible, log that an alert fired or a transcription ran (with a case/encounter ID), rather than logging the spoken text or transcript itself, in your own application logs.

See [references/evaluation.md](references/evaluation.md) for a PHI-safety check to run before any TTS call in a clinical pipeline.

## References

- [references/voice-alerts.md](references/voice-alerts.md) - Real-time clinical voice alerts: latency optimization, voice selection, FastAPI endpoint example
- [references/clinical-tts.md](references/clinical-tts.md) - Speaking clinical notes, SOAP notes, and medication lists; medical terminology and multi-speaker patterns
- [references/speech-to-text.md](references/speech-to-text.md) - Transcribing doctor-patient conversations, streaming vs. batch, LLM note generation
- [references/evaluation.md](references/evaluation.md) - Scoring TTS/STT quality, latency benchmarking, and PHI-safety checks
     