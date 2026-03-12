# Radio Broadcast Monitor

## Problem/Feature Description

A media analytics company monitors radio broadcasts for brand mentions and competitor activity. They need a Python script that connects to an internet radio stream URL and transcribes it in real-time, logging the transcript to a file as it progresses. The script should handle the streaming connection, process the incoming audio, and write both interim updates and finalized transcript segments to separate log files so analysts can review what was said.

The script should connect to a given stream URL, transcribe continuously, and write output to log files. It should handle connection errors and support graceful shutdown.

## Output Specification

Produce the following files:

1. `monitor_broadcast.py` - A Python script that:
   - Accepts a stream URL as a command-line argument
   - Connects to the ElevenLabs real-time transcription service
   - Streams audio from the given URL for transcription
   - Writes partial transcripts to `partial_log.txt`
   - Writes committed/finalized transcripts to `committed_log.txt`
   - Handles errors and supports clean shutdown via KeyboardInterrupt
   - Uses async/await patterns

2. `requirements.txt` - Python dependencies needed to run the script
