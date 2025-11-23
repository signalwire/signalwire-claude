---
name: signalwire-expert
description: Expert knowledge for building SignalWire applications including all SDKs, REST APIs, SWML, Relay/Fabric, AI Agents, and modern JSON/YAML-based communication systems
---

# SignalWire Expert Skill

Use this skill when working on SignalWire communication applications, APIs, or integrations.

## When to Use This Skill

Use this skill whenever you are:
- Building telephony, messaging, or video applications with SignalWire
- Working with SignalWire REST APIs, SWML, or SDKs
- Implementing AI agents or voice AI features
- Setting up Call Fabric, Relay applications, or Subscribers
- Debugging SignalWire webhooks or API responses
- Answering questions about SignalWire capabilities or best practices

## Important: Modern APIs Only

**AVOID** these deprecated/compatibility APIs:
- LAML (compatibility API - use modern REST or SWML instead)
- CXML (XML-based markup - use SWML in JSON/YAML instead)
- Any API endpoints containing `/laml/`
- XML-based request/response formats

**PREFER** these modern approaches:
- SignalWire REST API (`/api/calling/`, `/api/video/`, etc.) with JSON
- SWML (SignalWire Markup Language) in YAML or JSON
- Relay SDK for real-time WebSocket communication
- AI Agents SDK for voice AI applications

## SignalWire Architecture Overview

SignalWire provides several complementary technologies:

### 1. REST APIs
HTTP-based APIs for managing calls, messages, video rooms, and other resources. Use when you need to trigger actions or query state from your backend.

### 2. SWML (SignalWire Markup Language)
Declarative YAML/JSON documents that define call flows, IVR systems, and AI interactions. SWML can be:
- Served via HTTP endpoint (SignalWire fetches your SWML document)
- Sent inline via Relay SDK
- Deployed serverless via the SignalWire Dashboard

### 3. SDKs
Client and server libraries available in multiple languages:
- **JavaScript/TypeScript**: Browser SDK, Realtime SDK, Node.js SDK
- **Python**: Realtime SDK, AI Agents SDK
- Both SDKs and REST APIs can be used together in the same application

### 4. Call Fabric & Relay
Real-time communication framework using WebSockets:
- **Subscribers**: Internal account-holders within your SignalWire application
- **Fabric Addresses**: Routing identifiers (phone numbers, SIP addresses, etc.)
- **Relay Applications**: Your server or client apps connected via WebSocket
- **Resources**: AI Agents, SWML Scripts, Video Rooms, SIP Gateways

### 5. AI & SWAIG
Voice AI capabilities:
- **AI Agents**: Conversational AI for phone calls
- **SWAIG** (SignalWire AI Gateway): Functions your AI agent can call via HTTP
- **POM** (Prompt Object Model): Structured prompt building
- **Datasphere**: RAG (Retrieval-Augmented Generation) stack

## Workflow Documentation

This skill is organized by developer workflow. Choose the workflow that matches your task:

### Core Workflows

- **[Authentication & Setup](workflows/authentication-setup.md)** - Getting started, credentials, project setup
- **[Outbound Calling](workflows/outbound-calling.md)** - Initiating calls via REST API
- **[Inbound Call Handling](workflows/inbound-call-handling.md)** - Receiving calls and responding with SWML
- **[Call Control](workflows/call-control.md)** - Transfer, recording, conferencing during active calls
- **[Messaging](workflows/messaging.md)** - Sending/receiving SMS/MMS
- **[Voice AI](workflows/voice-ai.md)** - Building AI agents with SWAIG and POM
- **[Video](workflows/video.md)** - Creating and managing video rooms
- **[Fabric & Relay](workflows/fabric-relay.md)** - Real-time WebSocket communication, Subscribers
- **[Webhooks & Events](workflows/webhooks-events.md)** - Handling status callbacks and events
- **[Number Management](workflows/number-management.md)** - Provisioning and configuring phone numbers

## Common Patterns

### Authentication

Most SignalWire APIs use **HTTP Basic Authentication**:
- Username: Your Project ID
- Password: Your API Token
- Format: `Authorization: Basic <base64(project_id:api_token)>`

### Spaces and URLs

Your SignalWire Space URL format: `https://{space-name}.signalwire.com`

All API requests go to your Space URL, not a generic API endpoint.

### Variable Substitution in SWML

Use `%{variable_name}` format to access dynamic values:
- `%{call.from}` - Caller's phone number
- `%{call.to}` - Destination number
- `%{params.custom_field}` - Custom parameter from API call
- `%{args.user_input}` - User input from prompt

### Webhook Formats

SignalWire sends webhooks as HTTP POST with JSON body. Common fields:
- `call_id` - Unique call identifier
- `call_state` - Current state (queued, created, ringing, answered, ended)
- `from` - Calling party
- `to` - Called party
- `direction` - inbound or outbound

### Error Handling

REST API errors return:
- HTTP status codes (400, 401, 403, 404, 500, etc.)
- JSON response with `error` and `message` fields

SWML errors are typically logged to your SignalWire Dashboard logs.

## Key Concepts

### Call States
- **queued**: Call request received, not yet initiated
- **created**: Call has been created
- **ringing**: Destination is ringing
- **answered**: Call was answered
- **ended**: Call has terminated

### SWML Sections
Every SWML document has sections (like functions). The `main` section is required and is where execution starts. Navigate between sections with:
- `execute`: Call a section and return (like a function call)
- `transfer`: Permanently move to a section (like a goto)

### Resource Types
In Call Fabric, everything is a "resource":
- Subscribers (internal users)
- AI Agents
- SWML Scripts
- Video Rooms
- SIP Gateways
- Relay Applications

Resources can be created via Dashboard or REST API.

## Next Steps

1. Read the [Authentication & Setup](workflows/authentication-setup.md) workflow first
2. Choose the workflow that matches your current task
3. Reference the detailed API documentation in each workflow file
4. Check example apps in the SignalWire GitHub organization for real-world patterns

## Additional Resources

- Main Documentation: https://developer.signalwire.com/
- GitHub Examples: https://github.com/signalwire
- Dashboard: `https://{your-space-name}.signalwire.com`
