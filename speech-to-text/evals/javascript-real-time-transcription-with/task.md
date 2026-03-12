# Call Center Audio File Transcriber

## Problem/Feature Description

A call center company records all customer service calls as audio files and needs a Node.js script to transcribe these recordings using real-time streaming. They chose the real-time API over batch because they want to process the audio progressively and get word-level timestamps as segments are finalized, allowing them to build a timeline of the conversation. The recordings are stored locally as audio files that need to be read, converted to the right format, and streamed to the transcription service in chunks.

The script should read a local audio file, chunk it appropriately, stream the chunks to the ElevenLabs real-time transcription API, collect the results including timestamps, and write the final transcript with timing data to an output file. Since these are pre-recorded files (not live microphone input), the commit strategy should be chosen accordingly.

## Output Specification

Produce the following files:

1. `transcribe-recording.ts` - A TypeScript script that:
   - Reads a local audio file (path provided as command-line argument or hardcoded)
   - Streams it in chunks to the ElevenLabs real-time transcription API
   - Collects partial and committed transcripts
   - Writes the final committed transcript with word timestamps to `output.json`
   - Commits the transcript when audio streaming is complete
   - Handles session events (started, error, close)

2. `package.json` - With the necessary dependencies declared
