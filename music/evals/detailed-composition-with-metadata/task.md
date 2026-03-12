# Music Catalog Builder with Metadata Extraction

## Problem/Feature Description

A content licensing company wants to build a catalog of AI-generated music tracks for their stock music library. For each track, they need not just the audio file but also rich metadata -- the composition plan that was used, any lyrics that were generated, and song structure information. This metadata will be stored alongside each track in their catalog database so customers can search by style, mood, structure, and lyrical content.

They need a Python script that generates a music track and simultaneously captures all available metadata from the API response, then saves both the audio and a structured JSON metadata file.

## Output Specification

Create a Python script called `catalog_builder.py` that:

1. Takes a music description prompt and duration in milliseconds as inputs (can be hardcoded for demonstration)
2. Generates a music track using the ElevenLabs API in a way that returns both audio and full metadata (composition plan, song info, lyrics if applicable)
3. Saves the audio to a file
4. Saves the metadata (composition plan, song structure, any lyrics) to a separate JSON file called `track_metadata.json`
5. Prints a summary of what was generated, including the number of sections in the composition plan and whether lyrics were found

Use a prompt that would produce a short song with lyrics (e.g., a pop song about something cheerful) with a duration of 30 seconds.
