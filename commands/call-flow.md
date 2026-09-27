---
description: Write a SWML call flow (IVR, routing, voicemail, forwarding) from a plain-language description
argument-hint: "[what should happen when someone calls]"
---

Write a SWML call flow. The user described it as: $ARGUMENTS

If that description is empty, ask what should happen when someone calls: the menu options, where each one goes, business hours, and what happens when nobody answers.

Use the signalwire skill: the Inbound Call Handling workflow for structure and variables, and the SWML Methods workflow for any method beyond answer, play, prompt, connect, and transfer. Check exact parameter names against the live SWML docs when you can fetch them.

Every menu gets loop protection (`goto` with `max`), and every `connect` gets a fallback for no answer. Write the flow as YAML unless the user asked for JSON, and comment each section with what it does for the caller.

Finish with where the document goes: pasted into a SWML Script resource in the Dashboard, or served from the user's own URL, then assigned to a phone number.
