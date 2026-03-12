# Dynamic Soundtrack Generator for a Video Game

## Problem/Feature Description

A small indie game studio is building a Node.js backend service that generates adaptive background music for different levels of their game. Each level has a specific emotional arc -- for example, a forest level starts calm and builds tension, while a boss fight level is intense throughout. The studio wants precise control over the musical structure: they need to define sections (intro, buildup, climax, outro), set styles for each section, and control timing so the music aligns with gameplay events.

They need a JavaScript module that first creates a structured musical plan based on a level description, allows programmatic modification of that plan (e.g., adjusting section styles or durations), and then generates the final audio from the modified plan. The section timings need to be exact since they sync with in-game animations.

## Output Specification

Create a Node.js module called `game-soundtrack.mjs` that exports an async function `generateLevelSoundtrack(levelDescription, totalDurationMs)` which:

1. Connects to the ElevenLabs API to create a structured music plan from the level description
2. Logs the generated plan's global styles and section details to the console
3. Modifies the plan by appending "gaming" to the positive global styles
4. Generates the final audio from the modified plan, ensuring sections match their specified durations exactly
5. Saves the audio to a file named `level-soundtrack.mp3`

Also create a file called `demo.mjs` that imports and calls the function with a sample forest level description and a 60-second duration.
