---
description: Diagnose a SignalWire problem such as failed calls, webhooks that never arrive, 401/403 errors, or SWAIG functions that don't run
argument-hint: "[symptom, error, or log excerpt]"
---

Diagnose a SignalWire problem. The user reported: $ARGUMENTS

If that is empty, ask for the symptom, the exact error text or HTTP status, and a call or message ID if they have one.

Use the signalwire skill. Match the symptom to a workflow before guessing:

- 401/403, or wrong credentials or Space URL: Authentication & Setup
- Webhook or status callback never arrives or arrives malformed: Webhooks & Events
- AI agent doesn't call a function, times out, or says the wrong thing: AI Agent Debug Webhooks, then AI Agent Functions
- Agent interrupts callers or leaves dead air: AI Agent Turn Taking
- Call drops, loops, or ends up in the wrong place: Inbound Call Handling and Call Control
- Messages fail or get filtered: Messaging, including Campaign Registry status

Check first for the problems the skill flags as common: a LAML/CXML endpoint where the modern REST API or SWML belongs, a webhook URL that isn't publicly reachable over HTTPS, and a SWAIG response in the wrong shape.

Give the most likely cause first, the evidence that would confirm it, and the fix. If you can run commands, gather that evidence yourself (curl the endpoint, run `swaig-test`, read the logs) before answering.
