---
description: Build a SignalWire voice AI agent from a description of what it should do
argument-hint: "[what the agent should do]"
---

Build a SignalWire voice AI agent. The user described it as: $ARGUMENTS

If that description is empty, ask what the agent is for, what it needs to look up or change (these become SWAIG functions), and how a call should end or be transferred. Ask only for what you can't reasonably default.

Use the signalwire skill. Start from its Voice AI workflow and pick the architecture from its decision tree: plain SWML `ai` when the agent only talks, SWAIG functions or DataMap when it needs data, the Server SDK when it needs real logic. Say which one you picked and why in one sentence.

Then produce:

1. The prompt, written per the Prompting workflow.
2. Each function, with the arguments the model fills and what it returns, per the Functions workflow. Keep secrets and personal data in `meta_data`, not the prompt.
3. The full, runnable agent (SWML document or SDK code).
4. How to point a phone number at it and how to test it without calling, per the Deployment and Testing workflows.

If you can run commands, run the agent's local test before reporting. If you can't, tell the user the exact command to run and what a passing result looks like.
