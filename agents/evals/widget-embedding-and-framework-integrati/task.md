# Voice Agent Widget for Multi-Page Website

## Problem/Feature Description

A dental clinic is launching a new website and wants to add a voice AI assistant that patients can talk to for basic questions about services, office hours, and appointment scheduling. The website has three versions of pages that need the widget:

1. A plain HTML landing page for the clinic's main site
2. A React component for their patient portal (standard React, not Next.js)
3. A Next.js page for their blog section

Each page should embed the same voice agent (agent ID: `agent_abc123xyz`). The clinic wants the widget customized with their branding: a custom avatar image showing their logo (`https://dentalclinic.example.com/logo.png`), brand colors (primary: `#1B5E20`, secondary: `#A5D6A7`), and friendly text labels (the tooltip should say "Ask Dr. Smith's Assistant" and the call button should say "Start voice chat"). On the landing page, they want an expanded widget style. On the React and Next.js pages, they want the compact default.

The clinic also wants a custom trigger button on the HTML page so they can hide the default floating widget and use their own styled button instead.

Additionally, the clinic wants the widget positioned in the bottom-left corner (not the default bottom-right) and needs proper mobile responsiveness so the widget is full-width on phone screens.

## Output Specification

Produce three files:
- `landing.html` - Complete HTML page with the embedded widget, custom trigger button, positioning, and mobile CSS
- `PatientPortal.jsx` - React component with the embedded widget
- `BlogPage.jsx` - Next.js page component with the embedded widget
