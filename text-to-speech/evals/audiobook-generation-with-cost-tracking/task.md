# Audiobook Chapter Processor with Usage Monitoring

## Problem/Feature Description

A small publishing house is experimenting with generating audiobook previews using AI voices. They want to convert the first few chapters of a book into audio, with each chapter becoming a separate audio file. Because they are on a limited budget, they need to track exactly how many characters they consume with each API call so they can monitor costs in real time and stop if they exceed a threshold.

The book content has a narrative style, so the voice should be tuned for long-form narration -- consistent tone, natural variation, and normal speaking pace. Each chapter is long enough to require multiple API requests, and the transitions between requests within a chapter should be seamless.

Write a Python script that processes chapters from a book, generates audio for each, tracks character usage across all requests, and logs the running total. The script should also allow adjusting speech speed for accessibility purposes (some listeners prefer slightly slower narration).

## Output Specification

Produce the following files:

- `audiobook_generator.py` -- A Python script that:
  - Defines sample book data with at least 2 chapters, each containing at least 3 paragraphs of placeholder narration text
  - Generates audio for each chapter, splitting into multiple requests as needed and combining the results
  - Ensures seamless audio between consecutive requests within the same chapter
  - Uses voice characteristics suited for audiobook narration
  - Accepts a configurable speech speed setting
  - Tracks character usage from each request and maintains a running total
  - Logs the character count after each API call and prints a summary at the end
  - Stops processing if a configurable character budget is exceeded

- `config.py` -- Configuration file containing the voice settings, model selection, character budget, and speed setting as adjustable constants
