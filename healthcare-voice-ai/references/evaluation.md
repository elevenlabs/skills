# Evaluating Voice AI Quality in Clinical Settings

Clinical voice AI needs evaluation on axes that generic voice apps don't: medical terminology accuracy, transcription quality on multi-speaker clinical audio, latency against a hard clinical threshold, and a PHI-safety gate before any TTS request goes out. This reference gives runnable patterns for each.

## 1. Scoring TTS Output for Clarity and Medical Terminology Accuracy

The most reliable way to check whether a TTS clip pronounced medical terms correctly is a round-trip: synthesize the clinical text, transcribe the result with Scribe, and diff the transcript against the original terms.

```python
from elevenlabs import ElevenLabs

client = ElevenLabs()


def round_trip_terminology_check(text: str, required_terms: list[str], voice_id: str, model_id: str = "eleven_multilingual_v2") -> dict:
    """Synthesize `text`, transcribe it back, and check that clinical terms survived intact."""
    audio_chunks = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id=model_id,
    )
    audio_bytes = b"".join(audio_chunks)

    import io
    result = client.speech_to_text.convert(
        model_id="scribe_v2",
        file=io.BytesIO(audio_bytes),
    )

    transcript_lower = result.text.lower()
    missing_terms = [term for term in required_terms if term.lower() not in transcript_lower]

    return {
        "original_text": text,
        "round_trip_transcript": result.text,
        "required_terms": required_terms,
        "missing_terms": missing_terms,
        "terminology_accuracy": (len(required_terms) - len(missing_terms)) / len(required_terms) if required_terms else 1.0,
    }


result = round_trip_terminology_check(
    text="Prescribe levothyroxine 50 milligrams once daily.",
    required_terms=["levothyroxine", "50", "milligrams", "daily"],
    voice_id="JBFqnCBsd6RMkjVDRZzb",
)
print(f"Terminology accuracy: {result['terminology_accuracy']:.0%}")
if result["missing_terms"]:
    print(f"Missing/mispronounced: {result['missing_terms']}")
```

Run this check against a fixed set of representative clinical sentences (drug names you use often, dosage phrasing, common abbreviations after expansion) whenever you change voice, model, or pronunciation dictionary — treat it as a regression suite, not a one-time check.

## 2. Evaluating STT Transcription Quality for Clinical Conversations

For recorded encounters where you have a reference transcript (e.g., a clinician-corrected gold transcript for a sample of visits), compute Word Error Rate (WER) and check diarization accuracy separately, since a clinical note needs both correct words and correct speaker attribution.

```python
def word_error_rate(reference: str, hypothesis: str) -> float:
    """Simple WER: edit distance over words, normalized by reference length."""
    ref_words = reference.lower().split()
    hyp_words = hypothesis.lower().split()

    # standard Levenshtein distance over word sequences
    dp = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    for i in range(len(ref_words) + 1):
        dp[i][0] = i
    for j in range(len(hyp_words) + 1):
        dp[0][j] = j
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            cost = 0 if ref_words[i - 1] == hyp_words[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,       # deletion
                dp[i][j - 1] + 1,       # insertion
                dp[i - 1][j - 1] + cost # substitution
            )

    return dp[len(ref_words)][len(hyp_words)] / max(len(ref_words), 1)


def evaluate_clinical_transcript(audio_path: str, reference_transcript: str, expected_speaker_count: int) -> dict:
    with open(audio_path, "rb") as audio_file:
        result = client.speech_to_text.convert(
            model_id="scribe_v2",
            file=audio_file,
            diarize=True,
            num_speakers=expected_speaker_count,
        )

    speaker_ids = {word.speaker_id for word in result.words if word.type == "word" and word.speaker_id}

    return {
        "wer": word_error_rate(reference_transcript, result.text),
        "detected_speakers": len(speaker_ids),
        "expected_speakers": expected_speaker_count,
        "diarization_correct": len(speaker_ids) == expected_speaker_count,
    }
```

A WER under ~0.10-0.15 is a reasonable bar for clinical transcripts feeding an LLM summarization step, but validate against your own clinician-reviewed sample — medical vocabulary and accented speech will push this higher than general-purpose benchmarks suggest, and `keyterms` (see [speech-to-text.md](speech-to-text.md)) is your main lever for pulling it back down.

## 3. Latency Benchmarking Patterns

For alerts, benchmark against the ElevenLabs skill's stated latency budget (`eleven_flash_v2_5` at ~75ms model latency) against your actual end-to-end target of under 2 seconds — the gap between the two is your network, queueing, and playback overhead, and it's usually the larger share of the budget.

```python
import time
import statistics


def benchmark_alert_latency(alert_texts: list[str], voice_id: str, n_runs: int = 20) -> dict:
    """Measure time-to-first-byte and total generation time for streamed TTS alerts."""
    ttfb_samples = []
    total_samples = []

    for i in range(n_runs):
        text = alert_texts[i % len(alert_texts)]
        start = time.monotonic()
        first_byte_time = None
        total_bytes = 0

        audio_stream = client.text_to_speech.stream(
            voice_id=voice_id,
            text=text,
            model_id="eleven_flash_v2_5",
            optimize_streaming_latency=3,
            output_format="pcm_24000",
        )

        for chunk in audio_stream:
            if first_byte_time is None:
                first_byte_time = time.monotonic()
            total_bytes += len(chunk)

        end = time.monotonic()
        ttfb_samples.append(first_byte_time - start)
        total_samples.append(end - start)

    return {
        "ttfb_p50_ms": statistics.median(ttfb_samples) * 1000,
        "ttfb_p95_ms": sorted(ttfb_samples)[int(len(ttfb_samples) * 0.95)] * 1000,
        "total_p50_ms": statistics.median(total_samples) * 1000,
        "total_p95_ms": sorted(total_samples)[int(len(total_samples) * 0.95)] * 1000,
        "under_2s_rate": sum(1 for t in total_samples if t < 2.0) / len(total_samples),
    }


benchmark = benchmark_alert_latency(
    alert_texts=[
        "Missed PHQ-9 screening detected for patient in Room 4B.",
        "Critical potassium value resulted for patient in Room 4B.",
    ],
    voice_id="onwK4e9ZLuTAKqWW03F9",
)
print(f"P95 total latency: {benchmark['total_p95_ms']:.0f}ms")
print(f"Under 2s: {benchmark['under_2s_rate']:.0%}")
```

Run this benchmark from the same network location/deployment as your production alert system (not from a laptop on a different network) — network path to the ElevenLabs API is usually a bigger factor in your P95 than model choice.

## 4. PHI-Safety Checks Before TTS Generation

Since there is no PHI filter on the text-to-speech input path (unlike `entity_detection`/`entity_redaction` on STT output), build a pre-flight check into your alert pipeline that blocks obviously-identifying patterns from ever reaching a TTS call:

```python
import re

# Not exhaustive — this is a defense-in-depth guard, not a substitute for
# de-identifying text at the point it's generated in your application.
PHI_PATTERNS = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "mrn_labeled": re.compile(r"\bMRN[:\s]*\d{4,}\b", re.IGNORECASE),
    "dob_labeled": re.compile(r"\bDOB[:\s]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", re.IGNORECASE),
    "phone": re.compile(r"\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "full_date": re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
}


def phi_safety_check(text: str) -> dict:
    """Block-list check for common PHI patterns before a TTS request is sent."""
    findings = {name: bool(pattern.search(text)) for name, pattern in PHI_PATTERNS.items()}
    flagged = [name for name, found in findings.items() if found]
    return {
        "safe_to_send": len(flagged) == 0,
        "flagged_patterns": flagged,
    }


def safe_speak_alert(text: str, voice_id: str, model_id: str = "eleven_flash_v2_5"):
    check = phi_safety_check(text)
    if not check["safe_to_send"]:
        raise ValueError(
            f"Refusing to send to TTS: text matched PHI patterns {check['flagged_patterns']}. "
            "De-identify the alert text before calling this function."
        )
    return client.text_to_speech.convert(voice_id=voice_id, text=text, model_id=model_id)
```

Wire `phi_safety_check` (or an equivalent, tuned to your data) in as a gate in front of every clinical TTS call, not just the alert endpoint — the same check belongs in front of clinical-notes and medication-list synthesis (see [clinical-tts.md](clinical-tts.md)). Log a blocked attempt with enough detail to fix the upstream text generator, but never log the flagged text itself.

## Putting It Together: A Minimal Eval Suite

```python
def run_clinical_voice_eval_suite(voice_id: str) -> dict:
    terminology_results = [
        round_trip_terminology_check(
            text="Prescribe levothyroxine 50 milligrams once daily.",
            required_terms=["levothyroxine", "50", "milligrams"],
            voice_id=voice_id,
        ),
        round_trip_terminology_check(
            text="Administer albuterol via nebulizer every four hours as needed.",
            required_terms=["albuterol", "nebulizer", "four hours"],
            voice_id=voice_id,
        ),
    ]

    latency_results = benchmark_alert_latency(
        alert_texts=["Missed PHQ-9 screening detected for patient in Room 4B."],
        voice_id=voice_id,
        n_runs=10,
    )

    phi_check_should_pass = phi_safety_check("Missed PHQ-9 screening detected for patient in Room 4B.")
    phi_check_should_fail = phi_safety_check("Patient DOB: 04/12/1980 missed screening.")

    return {
        "avg_terminology_accuracy": statistics.mean(r["terminology_accuracy"] for r in terminology_results),
        "latency_p95_ms": latency_results["total_p95_ms"],
        "under_2s_rate": latency_results["under_2s_rate"],
        "phi_gate_working": phi_check_should_pass["safe_to_send"] and not phi_check_should_fail["safe_to_send"],
    }
```

Run this suite in CI whenever the voice, model, or pronunciation dictionary changes, and fail the build if `phi_gate_working` is `False` — a broken PHI gate is a release blocker, not a warning.
