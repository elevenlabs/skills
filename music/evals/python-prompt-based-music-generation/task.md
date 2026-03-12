# Background Music Generator for a Podcast

## Problem/Feature Description

A podcast production team needs a Python script that generates short instrumental background music tracks for different segments of their show. They want a tool that takes a mood description and a duration (in seconds), and produces an MP3 file. The team needs tracks for intros (around 15 seconds), transitions (5 seconds), and full background segments (up to 3 minutes). They specifically need instrumental-only output since any vocals would clash with the hosts' voices.

The script should use the ElevenLabs Music API and handle the generation cleanly, including proper error handling for API failures. The team wants to run it from the command line.

## Output Specification

Create a Python script called `generate_podcast_music.py` that:

1. Accepts command-line arguments for: a text prompt describing the mood, a duration in seconds, and an output filename
2. Connects to the ElevenLabs Music API and generates the requested music
3. Saves the result as an MP3 file
4. Includes error handling for common API issues
5. Prints a confirmation message when complete

Also create a file called `example_usage.sh` showing example shell commands to generate:
- A 15-second upbeat intro jingle
- A 5-second calm transition
- A 2-minute ambient background track
