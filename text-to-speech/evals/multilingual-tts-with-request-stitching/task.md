# Multilingual Podcast Episode Generator

## Problem/Feature Description

A media company produces a daily podcast that covers international news. Each episode has segments in different languages -- for example, a French segment, a Spanish segment, and an English summary. The segments are long enough that they need to be split across multiple API calls to stay within character limits, but the final audio for each segment must sound seamless with no audible pops or tonal shifts between parts.

The company wants a Python script that automates generating audio for a single episode. The script should accept a list of text segments (each with its language and text content), split long segments into smaller parts if needed, and produce one audio file per segment. The script should use the highest quality model available that supports their target languages.

## Output Specification

Produce the following files:

- `generate_episode.py` -- A Python script that:
  - Defines a list of at least 3 sample segments (one in French, one in Spanish, one in English) each with at least 2 paragraphs of placeholder text
  - For each segment, splits the text into chunks of roughly 500 characters, generates audio for each chunk, and concatenates the results into one file per segment (e.g. `segment_0.mp3`, `segment_1.mp3`, etc.)
  - Ensures smooth audio transitions between chunks within a segment
  - Forces the correct language pronunciation for non-English segments
  - Uses an appropriate model for the language requirements
  - Includes error handling for API failures

- `README.md` -- A short explanation of how to configure and run the script, including any environment setup needed
