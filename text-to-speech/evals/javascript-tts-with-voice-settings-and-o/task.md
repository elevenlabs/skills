# Voice Notification Service for a Web Application

## Problem/Feature Description

A SaaS company wants to add voice notifications to their web platform. When certain events happen (new message, system alert, scheduled reminder), the platform should generate a spoken audio notification and store it as a file. Different event types require different voice characteristics -- alerts should sound authoritative and steady, while friendly reminders should sound warm and conversational.

The engineering team needs a Node.js module that can generate these voice notifications using ElevenLabs. The module should support configuring voice characteristics per notification type and allow choosing the audio output format depending on whether the notification will be played in a browser (compressed format) or processed server-side (raw format).

## Output Specification

Produce the following files:

- `notification-service.js` -- An ES module that exports:
  - A function `generateNotification(type, text, outputPath)` where type is one of "alert", "reminder", "message"
  - Each type should use different voice settings appropriate to the tone (e.g., alerts are steady/authoritative, reminders are warm/conversational)
  - Accepts an optional `format` parameter to specify the audio output encoding
  - Uses a male voice for alerts and a female voice for reminders and messages
  - Handles errors gracefully and logs them

- `demo.js` -- A script that demonstrates calling `generateNotification` for each of the three event types with sample text, producing three audio files with different output formats

- `package.json` -- With the necessary dependencies listed
