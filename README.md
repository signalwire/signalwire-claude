# SignalWire Expert Skill for Claude Code

A comprehensive Claude Code skill that transforms Claude into an expert SignalWire developer, with complete knowledge of REST APIs, SWML, SDKs, AI Agents, Video, Fabric/Relay, and modern communication APIs.

## Features

- **Complete API Coverage**: All SignalWire REST APIs, SWML, Relay SDK, AI Agents SDK, Video API (excludes deprecated, legacy, and migration-focused APIs)
- **Multi-Language Examples**: 110+ Python examples, 24+ JavaScript examples, 44+ SWML examples
- **Workflow-Organized**: Find what you need by developer workflow (calling, messaging, video, AI, etc.)
- **Production-Ready Code**: Complete working examples with error handling and best practices
- **All SDKs Documented**: Python, JavaScript/Node.js, Browser SDK
- **Real-World Patterns**: IVR systems, chatbots, video conferencing, AI agents

## What's Included

### Core Workflows (6,056 lines of documentation)

1. **Authentication & Setup** - Credentials, environment variables, token types, security
2. **Outbound Calling** - REST API for making calls, status callbacks, phone number formats
3. **Inbound Call Handling** - Complete SWML reference with IVR patterns
4. **Call Control** - Transfer, recording, conferencing, real-time manipulation
5. **Messaging** - SMS/MMS sending/receiving, chatbots, compliance, delivery tracking
6. **Voice AI** - SWAIG functions, AI Agents SDK, POM (Prompt Object Model)
7. **Video** - Room management, tokens, layouts, browser SDK, recording
8. **Fabric & Relay** - Subscribers, WebSocket SDK, real-time communication
9. **Webhooks & Events** - Status callbacks, security, retry handling
10. **Number Management** - Provisioning, configuring, porting, E911

### Technical Coverage

- **REST API Endpoints**: All modern `/api/calling/`, `/api/messaging/`, `/api/video/`, `/api/fabric/` endpoints
- **SWML Methods**: All 30+ methods (answer, play, say, prompt, connect, ai, etc.)
- **SDKs**: Realtime SDK (Python/JS), AI Agents SDK (Python), Browser SDK (JS)
- **Advanced Features**: SWAIG, POM, Call Fabric, Subscribers, Relay contexts
- **Security**: Authentication, webhook security, token scopes, best practices

## Installation

### For Your Own Use

```bash
# Create skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Copy the signalwire skill
cp -r signalwire ~/.claude/skills/

# Verify installation
ls ~/.claude/skills/signalwire/
```

## Usage

Once installed, Claude will automatically use this skill when:

- Building telephony, messaging, or video applications with SignalWire
- Working with SignalWire REST APIs, SWML, or SDKs
- Implementing AI agents or voice AI features
- Setting up Call Fabric, Relay applications, or Subscribers
- Debugging SignalWire webhooks or API responses
- Answering questions about SignalWire capabilities

### Accessing via Slash Command

If you have Claude Code with slash command support:

```
/signalwire
```

This will activate the SignalWire expert skill.

## Examples of What Claude Can Do

### Generate Complete SWML IVR

```
You: "Create an IVR system that routes to sales, support, or billing"
Claude: [Generates complete SWML with proper structure, error handling, and fallbacks]
```

### Write Production API Code

```
You: "Write Python code to send SMS with delivery tracking"
Claude: [Generates code with uv shebang, error handling, retry logic, and webhook handler]
```

### Build AI Voice Agents

```
You: "Create a restaurant ordering AI agent with SWAIG"
Claude: [Generates complete AI Agents SDK code with menu matching, state management, and payment processing]
```

### Configure Video Rooms

```
You: "Set up a video conference with moderator controls"
Claude: [Generates backend token creation, frontend client, layout controls, and recording]
```

## Skill Structure

```
signalwire/
├── SKILL.md                           # Main entry point
├── README.md                          # This file
└── workflows/
    ├── authentication-setup.md         # Getting started, credentials
    ├── outbound-calling.md            # Making calls via REST API
    ├── inbound-call-handling.md       # SWML reference
    ├── call-control.md                # Transfer, recording, conferencing
    ├── messaging.md                   # SMS/MMS
    ├── voice-ai.md                    # AI Agents, SWAIG, POM
    ├── video.md                       # Video rooms
    ├── fabric-relay.md                # Subscribers, WebSocket SDK
    ├── webhooks-events.md             # Status callbacks, webhooks
    └── number-management.md           # Provisioning, configuration
```

## What This Skill Avoids

The skill explicitly avoids deprecated, legacy, and migration APIs:

- ❌ LAML (compatibility API)
- ❌ CXML (XML-based markup)
- ❌ Any `/laml/` endpoints
- ❌ XML request/response formats

Instead, it uses:

- ✅ Modern REST APIs with JSON
- ✅ SWML in YAML or JSON
- ✅ Relay SDK for real-time communication
- ✅ AI Agents SDK for voice AI

## Requirements

- Claude Code (with skills support)
- No additional dependencies required for the skill itself
- For running generated code: Python 3.11+ or Node.js 18+

## Sources

This skill was built from:

- Official SignalWire documentation (developer.signalwire.com)
- 6 official SignalWire example repositories
- Real-world application patterns
- Best practices for production systems
- Expert SignalWire knowledge from SignalWire training content

## Updates

The skill is based on SignalWire APIs as of October 2025. For the latest SignalWire features, check:

- https://developer.signalwire.com/
- https://github.com/signalwire

## Contributing

To update or improve this skill:

1. Edit the relevant workflow file in `workflows/`
2. Follow the existing format and style
3. Include working code examples
4. Test examples before adding
5. Update this README if adding new workflows

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

SignalWire is a trademark of SignalWire, Inc.

## Support

For SignalWire API questions:
- Documentation: https://developer.signalwire.com/
- Support: https://signalwire.com/support

For skill issues:
- Check that files are in `~/.claude/skills/signalwire/`
- Verify SKILL.md is present and readable
- Restart Claude Code after installation

## Version

**Version**: 1.0.0
**Last Updated**: October 2025
**SignalWire API Version**: 1.0.0 (SWML), REST API v2024
