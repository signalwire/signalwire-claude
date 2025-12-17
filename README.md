# SignalWire Builder - Claude Code Plugin

A comprehensive Claude Code plugin that transforms Claude into an expert SignalWire developer, combining complete API documentation with practical production knowledge from real-world deployments.

## Features

- **Complete API Coverage**: All SignalWire REST APIs, SWML, Relay SDK, AI Agents SDK, Video API (excludes deprecated LAML/CXML)
- **Practical Production Knowledge**: Best practices, patterns, and anti-patterns from 89 SignalWire training videos
- **Multi-Language Examples**: 110+ Python examples, 24+ JavaScript examples, 44+ SWML examples
- **Workflow-Organized**: Find what you need by developer workflow (calling, messaging, video, AI, etc.)
- **Production-Ready Code**: Complete working examples with error handling and security best practices
- **Real-World Patterns**: IVR systems, AI agents, video conferencing, context-aware transfers, MFA implementation

## What's Included

### Core Workflows (14,800+ lines of documentation)

Each workflow combines technical API documentation with practical implementation guidance:

**Telephony Core:**
1. **Authentication & Setup** - Credentials, MFA patterns, metadata for security, token management
2. **Outbound Calling** - REST API, CRM integration, appointment reminders, healthcare workflows
3. **Inbound Call Handling** - Complete SWML reference, loop protection, variable management, IVR patterns
4. **Call Control** - Context-aware transfers, screen pop, recording best practices, conference management
5. **Messaging** - SMS/MMS, Campaign Registry, templates, opt-in/opt-out, Relay SDK v4
6. **Video** - WebRTC integration, room management, Browser SDK, click-to-call widgets
7. **Fabric & Relay** - Subscribers, resource architecture, context routing, high availability
8. **Webhooks & Events** - Post-prompt analytics, webhook testing, transcription integration
9. **Number Management** - Campaign Registry compliance, number association, bulk management

**AI Voice Agents (Voice AI):**
- **Voice AI Overview** - Navigation hub and decision guide for AI agents
- **AI Agent SDK Basics** - Python SDK fundamentals, installation, tool decorator
- **AI Agent Prompting** - Best practices, RISE-M framework, anti-patterns
- **AI Agent Functions** - SWAIG patterns, progressive knowledge building, DataMap
- **AI Agent Deployment** - Traditional server, Docker, serverless (Lambda/GCF/Azure)
- **AI Agent Patterns** - Common reusable flows (data lookup, confirmation, MFA)
- **AI Agent Error Handling** - Robust error handling patterns
- **AI Agent Security** - Authentication, input validation, secrets management
- **AI Agent Testing** - swaig-test CLI, pytest patterns, integration testing
- **AI Agent Debug Webhooks** - Real-time monitoring and debugging

### What Makes This Skill Different

**Technical Knowledge (What APIs Do):**
- REST API endpoints and parameters
- SWML method reference
- SDK function signatures
- Authentication formats

**Practical Knowledge (How to Best Use Them):**
- Best practices from production deployments
- Common patterns and real-world examples
- Anti-patterns and mistakes to avoid
- Testing and debugging strategies
- Performance optimization techniques
- Security patterns (metadata, encryption, MFA)

### Knowledge Sources

- **Technical Documentation**: Official SignalWire REST APIs, SWML, SDKs
- **Practical Wisdom**: Analysis of 89 SignalWire training videos including:
  - LiveWire sessions
  - SignalWire in Seconds tutorials
  - ClueCon 2025 workshops
  - Digital Employees examples
  - Production deployment case studies

### Key Principles Documented

1. **Treat AI Like a Person, Not a Program** - "How would you instruct your mother?" approach
2. **Use Metadata for Security** - Keep sensitive data out of LLM context
3. **Test Continuously** - AI behavior is probabilistic
4. **Preserve Context Through Transfers** - 72% of customers expect it
5. **Implement Loop Protection** - Always protect gather/prompt nodes

## Installation

### Option 1: Install from Marketplace (Recommended)

Install the plugin directly using Claude Code:

```bash
/plugin install signalwire-builder@signalwire
```

The plugin will be installed to `~/.claude/plugins/signalwire-builder/` and will be available in all your Claude Code sessions.

### Option 2: Install from GitHub Release

Download and install from the latest release:

```bash
# Download and extract
curl -L https://github.com/signalwire/signalwire-claude/releases/latest/download/signalwire-builder.tar.gz | tar -xz

# Run installer
cd signalwire-builder
./install.sh
```

### Option 3: Manual Installation

Clone the repository and install manually:

```bash
# Clone the repository
git clone https://github.com/signalwire/signalwire-claude.git
cd signalwire-claude/skills/signalwire

# Run installer
./install.sh
```

### Verify Installation

Restart Claude Code after installation. The plugin will automatically activate when you work with SignalWire applications.

## Usage

Once installed, Claude will automatically use this plugin when:

- Building telephony, messaging, or video applications with SignalWire
- Working with SignalWire REST APIs, SWML, or SDKs
- Implementing AI agents or voice AI features
- Setting up Call Fabric, Relay applications, or Subscribers
- Debugging SignalWire webhooks or API responses
- Answering questions about SignalWire capabilities or best practices

The plugin activates automatically based on your conversation context - no manual invocation needed!

## Examples of What Claude Can Do

### Generate Complete SWML IVR with Best Practices

```
You: "Create an IVR system that routes to sales, support, or billing"
Claude: [Generates complete SWML with proper structure, loop protection, error handling,
         and variable management following production best practices]
```

### Write Production API Code

```
You: "Write Python code to send SMS with delivery tracking"
Claude: [Generates code with uv shebang, Campaign Registry compliance,
         error handling, retry logic, and webhook handler]
```

### Build AI Voice Agents Following Best Practices

```
You: "Create a restaurant ordering AI agent with SWAIG"
Claude: [Uses Voice AI workflow hub to generate complete AI Agents SDK code with:
         - Natural prompting following RISE-M framework
         - Metadata for sensitive data (payment info)
         - Progressive knowledge building via SWAIG functions
         - Latency optimization with fillers
         - Error handling and security patterns
         - Post-prompt analytics]
```

### Implement Context-Aware Transfers

```
You: "Set up call transfers that preserve customer context"
Claude: [Generates SWAIG functions to collect context, screen pop implementation
         for agent dashboard, and transfer patterns that never lose information]
```

### Configure Video with Security Best Practices

```
You: "Set up a video conference with moderator controls"
Claude: [Generates secure token creation, frontend client with never-expose-API-token
         pattern, layout controls, and recording configuration]
```

## Plugin Structure

```
signalwire-builder/
├── plugin.json                        # Plugin manifest
├── SKILL.md                           # Main entry point (optimized, 624 words)
├── README.md                          # This file
├── workflows/                         # 19 workflow files, 14,844 lines total
│   ├── authentication-setup.md        # 593 lines: Auth, MFA, security
│   ├── outbound-calling.md            # 819 lines: Dialer, CRM, reminders
│   ├── inbound-call-handling.md       # 1,296 lines: SWML, loops, IVR
│   ├── call-control.md                # 1,143 lines: Transfers, recording
│   ├── messaging.md                   # 1,228 lines: Campaign Registry
│   ├── video.md                       # 1,232 lines: WebRTC, rooms
│   ├── fabric-relay.md                # 1,111 lines: Subscribers, resources
│   ├── webhooks-events.md             # 1,114 lines: Analytics, testing
│   ├── number-management.md           # 960 lines: Compliance
│   ├── voice-ai.md                    # 444 lines: AI navigation hub
│   ├── ai-agent-sdk-basics.md         # 529 lines: SDK fundamentals
│   ├── ai-agent-prompting.md          # 683 lines: Best practices
│   ├── ai-agent-functions.md          # 827 lines: SWAIG patterns
│   ├── ai-agent-deployment.md         # 835 lines: Server/serverless
│   ├── ai-agent-patterns.md           # 467 lines: Common flows
│   ├── ai-agent-error-handling.md     # 391 lines: Error patterns
│   ├── ai-agent-security.md           # 410 lines: Auth, secrets
│   ├── ai-agent-testing.md            # 383 lines: Testing patterns
│   └── ai-agent-debug-webhooks.md     # 379 lines: Monitoring
└── reference/                         # SDK API docs (loaded only when needed)
    ├── sdk/                           # 12 files: AgentBase, SWAIG, etc.
    ├── deployment/                    # 3 files: Serverless, env vars
    └── examples/                      # 6 complete agent examples
```

Each workflow file includes:
- Technical API documentation
- Best Practices sections
- Common Patterns with complete examples
- Anti-Patterns to avoid
- Production Tips for deployment
- Real-world code examples

## What This Plugin Avoids

The plugin explicitly excludes deprecated and compatibility APIs:

- ❌ LAML (compatibility API)
- ❌ CXML (XML-based markup)
- ❌ Any `/laml/` endpoints
- ❌ XML request/response formats

Instead, it focuses on modern approaches:

- ✅ Modern REST APIs with JSON (`/api/calling/`, `/api/messaging/`, etc.)
- ✅ SWML in YAML or JSON format
- ✅ Relay SDK v4 for real-time communication
- ✅ AI Agents SDK for voice AI
- ✅ Call Fabric resource-based architecture

## Real-World Knowledge Included

### Production Metrics and Benchmarks
- Latency targets (~500ms average)
- Quality metrics (completion rates, function success)
- Operational efficiency patterns

### Security Patterns
- MFA implementation (phone-based, voice-based)
- Metadata for sensitive data (keep out of LLM)
- Payment data handling (SWML Pay)
- Encryption patterns for stored data

### Testing and Debugging
- AI-driven testing approaches
- Webhook.site development workflow
- Post-prompt data analysis
- Common issues and solutions

### Anti-Patterns to Avoid
- Over-prompting AI agents
- Treating AI like code instead of conversation
- Exposing sensitive data to LLM
- Creating infinite loops without protection
- Losing context during transfers

## Requirements

- Claude Code (with skills support)
- No additional dependencies required for the skill itself
- For running generated code: Python 3.11+ with uv, or Node.js 18+

## Updates

The skill is based on SignalWire APIs and training content as of December 2025. For the latest SignalWire features, check:

- https://developer.signalwire.com/
- https://github.com/signalwire

## Contributing

To update or improve this plugin:

1. Fork the repository at https://github.com/signalwire/signalwire-claude
2. Edit the relevant workflow file in `skills/signalwire/workflows/`
3. Follow the existing format (Technical + Practical knowledge)
4. Include working code examples
5. Add to Best Practices, Common Patterns, or Anti-Patterns sections
6. Update this README if adding new workflows
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

SignalWire is a trademark of SignalWire, Inc.

## Support

For SignalWire API questions:
- Documentation: https://developer.signalwire.com/
- Support: https://signalwire.com/support

For plugin issues:
- GitHub Issues: https://github.com/signalwire/signalwire-claude/issues
- Check that files are in `~/.claude/plugins/signalwire-builder/`
- Verify plugin.json and SKILL.md are present
- Restart Claude Code after installation

## Version

**Version**: 1.0.0-beta3
**Last Updated**: December 2025
**Content**: 14,800+ lines combining technical documentation with practical production knowledge from SignalWire training videos, production applications, and support tickets
