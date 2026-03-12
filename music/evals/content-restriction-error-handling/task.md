# Robust Music Generation Service with Content Moderation Recovery

## Problem/Feature Description

A music streaming startup is building a user-facing service where customers type in free-text descriptions of the music they want. Since users often request music "in the style of" famous artists or reference copyrighted material, the service needs to gracefully handle these situations rather than just failing. When a user's request is rejected for content policy reasons, the service should automatically retry with the corrected suggestion provided by the API, so the user still gets music that matches their intent as closely as possible.

The same applies when using the composition plan workflow -- if a generated plan contains problematic styles, the service should use the corrected plan suggestion from the error response and retry.

Write a Python module that wraps the ElevenLabs Music API with this resilient behavior built in.

## Output Specification

Create a Python file called `resilient_music_service.py` that provides:

1. A function `generate_music_safe(prompt, duration_ms, output_path)` that:
   - Attempts to generate music with the given prompt
   - If the request fails due to content restrictions, extracts the suggested alternative from the error and retries automatically
   - Saves the resulting audio to the output path
   - Returns a dictionary with keys: `success` (bool), `original_prompt`, `final_prompt` (which may differ if a retry was needed), and `retried` (bool)

2. A function `generate_with_plan_safe(prompt, duration_ms, output_path)` that:
   - Creates a composition plan from the prompt
   - If the plan is rejected due to content issues, extracts the corrected plan suggestion and uses that instead
   - Generates audio from the (possibly corrected) plan
   - Returns a dictionary with: `success` (bool), `plan_corrected` (bool), and `plan_data` (the final composition plan used)

3. A brief `if __name__ == "__main__"` block that demonstrates calling both functions with example prompts.
