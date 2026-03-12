# Podcast Episode Subtitle Generator

## Problem/Feature Description

A podcast production company wants a Node.js command-line tool that takes a podcast audio file and generates subtitle files in SRT format. The tool needs to support episodes recorded in various languages -- the company produces content in English, Spanish, and French. The production team wants to specify a language hint when they know the language, but the tool should also work without one (auto-detecting the language). Each subtitle entry should include timestamps so the SRT file can be used for video overlays.

The company has standardized on TypeScript for their toolchain and needs this to integrate with their existing Node.js build pipeline.

## Output Specification

Produce the following files:

1. `generate-subtitles.ts` - A TypeScript file that:
   - Accepts an audio file path as input (via command-line argument or hardcoded for demo purposes)
   - Optionally accepts a language code
   - Calls the ElevenLabs API to transcribe the audio with word-level timing
   - Converts the transcription result into SRT subtitle format
   - Writes the output to a `.srt` file
   - Logs the detected language and confidence

2. `package.json` - With the necessary dependencies declared

3. `tsconfig.json` - A basic TypeScript configuration
