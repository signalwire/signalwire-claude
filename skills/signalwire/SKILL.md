---
name: signalwire
description: Use when building telephony, messaging, or video applications; implementing voice AI agents; adding real-time AI coaching or call observation (ai_sidecar) to live calls; working with SWML call flows; debugging webhook callbacks or call state issues; setting up real-time WebSocket communication; encountering authentication 401/403 errors; or troubleshooting SWAIG function errors - provides REST API patterns, SDK examples, and production-tested workflows for modern SignalWire communication systems
---

# SignalWire

## ⚠️ AVOID Deprecated APIs

SignalWire maintains compatibility APIs (LAML/CXML) that should NOT be used for new development:
- **LAML** endpoints (`/laml/`) → Use REST API (`/api/calling/`, `/api/video/`)
- **CXML** (XML markup) → Use SWML (YAML/JSON)

This skill documents ONLY modern APIs: REST with JSON, SWML, Relay SDK, AI Agents SDK.

## Read the Live Docs

SignalWire's documentation is machine-readable. Append `.md` to any page URL under `https://signalwire.com/docs` to get clean Markdown, or send `Accept: text/markdown`.

Start from `https://signalwire.com/docs/llms.txt` for the root index, or go straight to a product index:

| Index | Covers |
|-------|--------|
| `/docs/swml/llms.txt` | SWML methods and the `ai` verb |
| `/docs/apis/llms.txt` | REST APIs, calling commands, webhook payloads |
| `/docs/server-sdks/llms.txt` | Server SDKs and their guides |
| `/docs/platform/llms.txt` | Voices, TTS engines, SWSH, changelog |
| `/docs/browser-sdk/llms.txt` | Browser SDK v4 |

The root index warns that it is "an orientation page and directory, not an exhaustive list" — check the product index before concluding a page does not exist.

**Prefer fetching the live page over this skill's bundled reference** when the question is about an exact parameter name, a default, or an endpoint path. This skill is a snapshot; the docs are not.

There is also a changelog at `/docs/platform/changelog` (append `.rss` for a feed) covering new capabilities, changed defaults, and deprecations. Defaults in particular have moved more than once — see the voice default in [Voice AI](workflows/voice-ai.md).

## SignalWire Technologies Quick Reference

| Technology | Use When | Format/Protocol |
|------------|----------|-----------------|
| **REST APIs** | Trigger actions from backend, query state | HTTP + JSON |
| **SWML** | Define call flows, IVR, AI interactions | YAML/JSON documents |
| **Relay SDK** | Real-time WebSocket control | JavaScript/Python |
| **AI Agents SDK** | Build voice AI agents | Python decorators |
| **Call Fabric** | Route between subscribers/resources | WebSocket framework |
| **SWAIG** | AI agent calls server-side functions | HTTP POST to your endpoint |

## Practical Knowledge from Production

This skill combines technical API documentation with practical implementation guidance from real-world SignalWire deployments. Each workflow file includes:

- **Best Practices** - Production-tested techniques and patterns
- **Common Patterns** - Real-world implementation examples
- **Anti-Patterns** - What NOT to do, mistakes to avoid
- **Production Tips** - Deployment, monitoring, and testing insights
- **Real-World Examples** - Complete working patterns from live applications

These insights come from analysis of 89 SignalWire training videos, LiveWire sessions, and production deployments.

## Workflows by Use Case

**Getting Started:**
- [Authentication & Setup](workflows/authentication-setup.md) | [Number Management](workflows/number-management.md) | [SWSH CLI](workflows/swsh-cli.md)

**Voice Calls:**
- [Outbound Calling](workflows/outbound-calling.md) | [Inbound Handling](workflows/inbound-call-handling.md) | [Call Control](workflows/call-control.md)

**AI Voice Agents:** Start with [Voice AI](workflows/voice-ai.md) overview
- **SDK:** [Basics](workflows/ai-agent-sdk-basics.md) | [Prompting](workflows/ai-agent-prompting.md) | [Functions](workflows/ai-agent-functions.md) | [Deployment](workflows/ai-agent-deployment.md)
- **Conversation Feel:** [Turn Taking](workflows/ai-agent-turn-taking.md) - when the agent decides you stopped talking; fixes interrupting and dead air
- **Text Chat:** [AI Agent Chat](workflows/ai-agent-chat.md) - reach the same agents by text over JSON-RPC
- **AI Sidecar:** [Real-time agent coaching](workflows/ai-sidecar.md) - AI observer that coaches a human agent (never speaks on the call)
- **Best Practices:** [Patterns](workflows/ai-agent-patterns.md) | [Error Handling](workflows/ai-agent-error-handling.md) | [Security](workflows/ai-agent-security.md) | [Testing](workflows/ai-agent-testing.md) | [Debug Webhooks](workflows/ai-agent-debug-webhooks.md)

**Other:**
- [Messaging](workflows/messaging.md) | [Video](workflows/video.md) | [Fabric & Relay](workflows/fabric-relay.md) | [Webhooks & Events](workflows/webhooks-events.md)

**SWML Method Reference:** [All SWML methods](workflows/swml-methods.md) - complete method catalog including queuing, conferencing, AMD, fax, transcription, streaming, taps, payment, control flow, Messaging SWML (`reply` to SMS), and variable syntax

## Quick Start Patterns

**Authentication:** HTTP Basic Auth with Project ID (username) + API Token (password)

**Space URL:** All API requests go to `https://{space-name}.signalwire.com`

**SWML Variables:** `%{call.from}`, `%{call.to}`, `%{params.custom_field}`, `%{vars.my_variable}` (`%{args.x}` is SWAIG-only, inside `ai` function contexts)

**Webhooks:** HTTP POST with JSON (`call_id`, `call_state`, `from`, `to`, `direction`)

**Errors:** REST returns HTTP status + JSON with `error`/`message`. SWML logs to Dashboard.

## Key Concepts

**Call States:** queued → created → ringing → answered → ended

**SWML Sections:** `main` (required entry point) | `execute` (call + return) | `transfer` (goto)

**Resources:** Subscribers, AI Agents, SWML Scripts, Video Rooms, SIP Gateways, Relay Apps (created via Dashboard or REST API)

## Critical Pattern: Loop Protection

SWML menu loops (`prompt` + retry) can trap callers. Use `goto` with its built-in `max` jump limit:

```yaml
- label: menu
- prompt:
    play: "say:Press 1 for sales, 2 for support"
- switch:
    variable: prompt_value
    case:
      "1":
        - transfer: { dest: sales }
      "2":
        - transfer: { dest: support }
    default:
      - goto: { label: menu, max: 3 }  # retry cap prevents infinite loop
- play:
    url: "say:We didn't receive valid input. Goodbye."
- hangup: {}
```

For complete patterns, see [Inbound Call Handling](workflows/inbound-call-handling.md).

## AI Agents SDK Reference

**IMPORTANT:** For AI agent tasks, start with [Voice AI](workflows/voice-ai.md) - it covers 90% of use cases with examples and best practices.

**Only load reference docs for:** Complete API parameters, advanced features (Contexts/Steps, Prefabs), platform-specific deployment (Lambda/GCF/Azure), or debugging production issues.

See [Voice AI workflow](workflows/voice-ai.md) "When to Pull Additional Documentation" section for detailed guidance on when to use each reference document.

## Finding the Right Workflow

**New to SignalWire?** → [Authentication & Setup](workflows/authentication-setup.md)

**Changing something on an account (numbers, SIP, projects)?** → [SWSH CLI](workflows/swsh-cli.md) — usually a one-liner

**Building AI voice agent?** → [Voice AI](workflows/voice-ai.md)

**Agent interrupts callers, or leaves dead air?** → [Turn Taking](workflows/ai-agent-turn-taking.md)

**Coaching a live human agent with AI?** → [AI Sidecar](workflows/ai-sidecar.md)

**Making/receiving calls?** → [Outbound Calling](workflows/outbound-calling.md) or [Inbound Handling](workflows/inbound-call-handling.md)

**Debugging webhooks/callbacks?** → [Webhooks & Events](workflows/webhooks-events.md)

**Need real-time control?** → [Fabric & Relay](workflows/fabric-relay.md)

## Additional Resources

- Main Documentation: https://developer.signalwire.com/
- GitHub Examples: https://github.com/signalwire
- Server SDKs (10 languages, one package each): https://signalwire.com/docs/server-sdks
- Dashboard: `https://{your-space-name}.signalwire.com`
