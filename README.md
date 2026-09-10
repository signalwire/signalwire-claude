# SignalWire Builder - Claude Code Plugin

A comprehensive Claude Code plugin that transforms Claude into an expert SignalWire developer, combining complete API documentation with practical production knowledge from real-world deployments.

## Quick install

From inside a Claude Code session:

```bash
/plugin marketplace add signalwire/signalwire-claude
/plugin install signalwire-builder
```

## Features

- **Broad API Coverage**: SignalWire REST APIs, the calling commands endpoint, SWML (calling *and* messaging), the AI chat API, Relay, Server SDKs, Browser SDK v4, and the Video API — excludes deprecated LAML/CXML
- **Reads the Live Docs**: The skill knows SignalWire's docs are machine-readable (`.md` suffix, per-product `llms.txt` indexes) and fetches the current page when an exact parameter, default, or endpoint path matters
- **Ahead of the Docs Where It Counts**: Turn-taking behavior, `ai_sidecar` constraints, and SWAIG traps are documented from verified platform behavior in places the published docs are incomplete or wrong — and marked as such
- **Practical Production Knowledge**: Best practices, patterns, and anti-patterns from 89 SignalWire training videos
- **Ten-Language SDK**: One unified package per language covering AI Agents + Relay + REST; Python and TypeScript examples throughout
- **Account Operations, Not Just Code**: SWSH CLI coverage, so "how do I change X on my account" has a one-line answer
- **Workflow-Organized**: Find what you need by developer workflow (calling, messaging, video, AI, etc.)
- **Production-Ready Code**: Complete working examples with error handling and security best practices
- **Real-World Patterns**: IVR systems, AI agents, live agent coaching, video conferencing, context-aware transfers, MFA implementation

## What's Included

### Core Workflows (24 files, 17,100+ lines of documentation)

Each workflow combines technical API documentation with practical implementation guidance:

**Telephony Core:**
1. **Authentication & Setup** - Credentials, MFA patterns, metadata for security, token management
2. **Outbound Calling** - REST API, CRM integration, appointment reminders, healthcare workflows
3. **Inbound Call Handling** - SWML verb reference, loop protection, variable management, IVR patterns
4. **Call Control** - Context-aware transfers, screen pop, recording best practices, conference management
5. **SWML Method Reference** - Full method catalog: queuing, conferencing, AMD, fax, transcription, streaming, taps, payment, control flow, and Messaging SWML
6. **Messaging** - SMS/MMS, Messaging SWML (`reply`), Campaign Registry, templates, opt-in/opt-out
7. **Video** - WebRTC integration, room management, Browser SDK v4, click-to-call widgets
8. **Fabric & Relay** - Calling commands over HTTP, subscribers, resource architecture, context routing
9. **Webhooks & Events** - Signature verification, post-prompt analytics, webhook testing, transcription
10. **Number Management** - Campaign Registry compliance, number association, bulk management
11. **SWSH CLI** - Operating on an account from the command line; WireStarter for local development

**AI Voice Agents (Voice AI):**
- **Voice AI Overview** - Navigation hub and decision guide for AI agents
- **AI Agent SDK Basics** - Server SDK across ten languages, installation, tool decorator
- **AI Agent Prompting** - Best practices, RISE-M framework, inner dialog, anti-patterns
- **AI Agent Functions** - SWAIG patterns, MCP tool servers, remote includes, DataMap
- **AI Agent Turn Taking** - How end-of-turn is decided, and the one knob worth tuning
- **AI Agent Chat** - Reaching the same agents by text over JSON-RPC
- **AI Sidecar** - Real-time coaching for a human agent; observes without ever speaking
- **AI Agent Deployment** - Traditional server, Docker, serverless (Lambda/GCF/Azure)
- **AI Agent Patterns** - Common reusable flows (data lookup, confirmation, MFA)
- **AI Agent Error Handling** - Robust error handling patterns
- **AI Agent Security** - Request signing, content redaction, input validation, secrets management
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
/plugin marketplace add signalwire/signalwire-claude
/plugin install signalwire-builder
```

The plugin will be installed to `~/.claude/plugins/signalwire-builder/` and will be available in all your Claude Code sessions.

### Option 2: Manual Installation

Clone the repository and install manually:

```bash
# Clone the repository
git clone https://github.com/signalwire/signalwire-claude.git
cd signalwire-claude

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

The plugin activates automatically based on your conversation context - no manual invocation needed.

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
├── .claude-plugin/
│   ├── plugin.json                    # Plugin manifest
│   └── marketplace.json               # Marketplace listing
├── skills/
│   └── signalwire/                    # SignalWire skill
│       ├── SKILL.md                   # Main entry point
│       ├── workflows/                 # 24 workflow files, 17,150 lines total
│       │   ├── inbound-call-handling.md       # 1,350 lines: SWML, loops, IVR
│       │   ├── video.md                       # 1,287 lines: WebRTC, Browser SDK v4
│       │   ├── messaging.md                   # 1,233 lines: SMS, Messaging SWML
│       │   ├── call-control.md                # 1,185 lines: Transfers, recording
│       │   ├── fabric-relay.md                # 1,166 lines: Calling commands, subscribers
│       │   ├── webhooks-events.md             # 1,162 lines: Signatures, analytics
│       │   ├── number-management.md           #   960 lines: Compliance
│       │   ├── ai-agent-functions.md          #   915 lines: SWAIG, MCP, includes
│       │   ├── swml-methods.md                #   868 lines: Full method catalog
│       │   ├── ai-agent-deployment.md         #   835 lines: Server/serverless
│       │   ├── outbound-calling.md            #   824 lines: Dialer, CRM, reminders
│       │   ├── ai-agent-prompting.md          #   750 lines: Prompting, inner dialog
│       │   ├── authentication-setup.md        #   602 lines: Auth, MFA, security
│       │   ├── ai-agent-sdk-basics.md         #   591 lines: Ten-language SDK
│       │   ├── voice-ai.md                    #   571 lines: AI navigation hub
│       │   ├── ai-agent-security.md           #   515 lines: Signing, redaction
│       │   ├── ai-agent-patterns.md           #   467 lines: Common flows
│       │   ├── ai-agent-error-handling.md     #   391 lines: Error patterns
│       │   ├── ai-agent-testing.md            #   383 lines: Testing patterns
│       │   ├── ai-agent-debug-webhooks.md     #   379 lines: Monitoring
│       │   ├── ai-sidecar.md                  #   359 lines: Live agent coaching
│       │   ├── swsh-cli.md                    #   125 lines: Account operations
│       │   ├── ai-agent-turn-taking.md        #   123 lines: End-of-turn detection
│       │   └── ai-agent-chat.md               #   109 lines: Text chat, JSON-RPC
│       └── reference/                 # SDK API docs (loaded only when needed)
│           ├── sdk/                   # 12 files: AgentBase, SWAIG, etc.
│           ├── deployment/            # 3 files: Serverless, env vars
│           └── examples/              # 6 complete agent examples
├── README.md                          # This file
├── INSTALL.md                         # Installation guide
├── install.sh                         # Installation script
└── LICENSE
```

Each workflow file includes:
- Technical API documentation
- Best Practices sections
- Common Patterns with complete examples
- Anti-Patterns to avoid
- Production Tips for deployment
- Real-world code examples


## Requirements

- Claude Code (with skills support)
- No additional dependencies required for the skill itself
- For running generated code: Python 3.10+ with uv, or Node.js 18+ (`pip install signalwire-sdk` / `npm install @signalwire/sdk`)

## Updates

Content current as of **September 2026**.

The skill is designed to partially self-update: it knows SignalWire's documentation is machine-readable and will fetch the live page when an exact parameter name, default, or endpoint path matters. Append `.md` to any page under `https://signalwire.com/docs`, or start from a product index such as `/docs/swml/llms.txt`.

For what has changed since:

- Changelog: https://signalwire.com/docs/platform/changelog (append `.rss` for a feed)
- Docs: https://signalwire.com/docs
- GitHub: https://github.com/signalwire

## Contributing

To update or improve this plugin:

1. Fork the repository at https://github.com/signalwire/signalwire-claude
2. Edit the relevant workflow file in `skills/signalwire/workflows/`
3. Follow the existing format (Technical + Practical knowledge)
4. Include working code examples
5. Add to Best Practices, Common Patterns, or Anti-Patterns sections
6. Update this README if adding new workflows
7. Test the plugin structure follows Claude Code requirements
8. Submit a pull request

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