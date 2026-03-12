# Live Transcription for Telehealth App

## Problem/Feature Description

A telehealth startup is building a web application where doctors conduct video consultations with patients. They need a React component that provides real-time speech-to-text transcription during the consultation, showing the doctor a live transcript of what the patient is saying. The transcript needs to update in real-time as the patient speaks, and finalized text should be accumulated into a complete session transcript.

The application is built with React and TypeScript. The frontend communicates with an Express.js backend. Security is critical because this is a healthcare application -- the architecture must ensure that API credentials are never exposed to the browser.

Write both the React frontend component and the Express.js backend endpoint needed to support this feature.

## Output Specification

Produce the following files:

1. `TranscriptionPanel.tsx` - A React component that:
   - Provides start/stop recording controls
   - Shows live transcription text that updates as the user speaks
   - Accumulates finalized transcript segments into a complete transcript
   - Obtains necessary credentials from the backend before connecting

2. `server.ts` - An Express.js backend file that:
   - Provides an endpoint that the frontend can call to get credentials for the real-time transcription service
   - Uses the ElevenLabs SDK to generate the credentials

3. `package.json` - With all necessary dependencies for both frontend and backend
