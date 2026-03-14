# Meeting Transcription Tool

## Problem/Feature Description

A legal firm needs a Python script to transcribe recorded depositions. Each deposition recording is a multi-speaker audio file (MP3 format) where attorneys and witnesses speak. The firm needs the script to produce a transcript that identifies each speaker, includes precise timing for every word, and correctly handles specialized legal terminology that might be misheard by generic speech recognition (e.g., "voir dire", "habeas corpus", "amicus curiae", "certiorari").

The firm wants a standalone Python script called `transcribe_deposition.py` that takes an audio file path as a command-line argument, calls the ElevenLabs speech-to-text API, and writes the output to a structured JSON file. The script should also generate a human-readable text file grouping the transcript by speaker.

## Output Specification

Produce the following files:

1. `transcribe_deposition.py` - A Python script that:
   - Accepts an audio file path as a command-line argument
   - Transcribes it using the ElevenLabs API
   - Writes a JSON file (`transcript.json`) containing the raw API response
   - Writes a text file (`transcript.txt`) with speaker-grouped output, where each line shows `[speaker_id] text (start_time - end_time)`
   - Handles errors gracefully with informative messages

2. `requirements.txt` - Python dependencies needed to run the script
