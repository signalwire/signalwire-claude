# SignalWire Builder Plugin - Distribution Guide

## Overview

The SignalWire Builder plugin provides comprehensive expert knowledge for building SignalWire applications in Claude Code. It includes complete API documentation, 19 workflow guides, and 170+ working code examples.

## Distribution Methods

### Method 1: Claude Marketplace (Recommended)

Users can install directly from the marketplace:

```bash
/plugin install signalwire-builder@signalwire
```

**Requirements:**
- Plugin registered in Claude marketplace registry
- `marketplace.json` submitted to marketplace
- GitHub releases configured with tarball downloads

### Method 2: GitHub Releases

Users download and install from GitHub:

```bash
# Download latest release
curl -L https://github.com/signalwire/signalwire-claude/releases/latest/download/signalwire-builder.tar.gz | tar -xz

# Install
cd signalwire-builder
./install.sh
```

### Method 3: Direct Git Clone

Users clone and install manually:

```bash
git clone https://github.com/signalwire/signalwire-claude.git
cd signalwire-claude/skills/signalwire
./install.sh
```

## Creating a Release

### 1. Create Tarball

From the `signalwire-claude/skills/signalwire` directory:

```bash
# Create distribution tarball (exclude git directory)
tar -czf signalwire-builder.tar.gz \
    --exclude='.git' \
    --exclude='*.tar.gz' \
    plugin.json \
    marketplace.json \
    SKILL.md \
    README.md \
    DISTRIBUTION.md \
    INSTALL.md \
    LICENSE \
    install.sh \
    workflows/ \
    reference/

# Verify tarball contents
tar -tzf signalwire-builder.tar.gz | head -20
```

### 2. Create GitHub Release

From the `signalwire-claude` repository root:

```bash
# Tag the release
git tag -a v1.0.0 -m "SignalWire Builder Plugin v1.0.0"
git push origin v1.0.0

# Create release with tarball
cd skills/signalwire
gh release create v1.0.0 \
    signalwire-builder.tar.gz \
    --title "SignalWire Builder Plugin v1.0.0" \
    --notes "## SignalWire Builder - Claude Code Plugin

Transform Claude into an expert SignalWire developer with comprehensive API documentation and production-tested patterns.

### What's Included

- **Complete API Coverage**: REST APIs, SWML, Relay SDK, AI Agents SDK, Video API
- **19 Workflow Guides**: 14,800+ lines of documentation
- **170+ Code Examples**: 110+ Python, 24+ JavaScript, 44+ SWML
- **Production Knowledge**: Best practices from real-world deployments
- **AI Agents**: Complete SDK reference with SWAIG patterns

### Features

✅ Modern SignalWire APIs (excludes deprecated LAML/CXML)
✅ Workflow-organized documentation (calling, messaging, video, AI)
✅ Production-ready code with error handling and security
✅ Real-world patterns: IVR, AI agents, video conferencing, MFA
✅ Practical knowledge from 89 SignalWire training videos

### Installation

#### Marketplace (Recommended)
\`\`\`bash
/plugin install signalwire-builder@signalwire
\`\`\`

#### Manual Installation
\`\`\`bash
curl -L https://github.com/signalwire/signalwire-claude/releases/download/v1.0.0/signalwire-builder.tar.gz | tar -xz
cd signalwire-builder
./install.sh
\`\`\`

### What Makes This Different

**Technical Knowledge** (what APIs do):
- REST API endpoints and parameters
- SWML method reference
- SDK function signatures

**Practical Knowledge** (how to use them):
- Best practices from production deployments
- Common patterns and real-world examples
- Anti-patterns and mistakes to avoid
- Testing, debugging, and security strategies

### Documentation

- Main guide: \`SKILL.md\`
- User documentation: \`README.md\`
- Installation help: \`INSTALL.md\`
- Distribution info: \`DISTRIBUTION.md\`

### Support

- Documentation: https://developer.signalwire.com/
- GitHub Issues: https://github.com/signalwire/signalwire-claude/issues
- SignalWire Support: https://signalwire.com/support
"
```

### 3. Submit to Marketplace

Submit `marketplace.json` to the Claude Code plugin marketplace registry:

```json
{
  "marketplace": "signalwire",
  "plugins": [
    {
      "id": "signalwire-builder",
      "name": "SignalWire Builder",
      "description": "Expert knowledge for building SignalWire applications...",
      "version": "1.0.0",
      "author": "SignalWire",
      "repository": "https://github.com/signalwire/signalwire-claude",
      "install_url": "https://github.com/signalwire/signalwire-claude/releases/latest/download/signalwire-builder.tar.gz"
    }
  ]
}
```

## What Users Get

Once installed at `~/.claude/plugins/signalwire-builder/`, Claude becomes an expert in:

### Core Technologies
✅ **REST APIs** - All modern JSON endpoints (`/api/calling/`, `/api/messaging/`, `/api/video/`)
✅ **SWML** - Complete YAML/JSON markup reference with 44+ examples
✅ **Relay SDK** - Real-time WebSocket control (JavaScript/Python)
✅ **AI Agents SDK** - Complete Python SDK with SWAIG patterns
✅ **Call Fabric** - Subscribers, resources, routing architecture
✅ **Video API** - WebRTC, room management, Browser SDK

### Comprehensive Workflows
1. **Authentication & Setup** - Credentials, MFA, security patterns
2. **Outbound Calling** - REST API, CRM integration, reminders
3. **Inbound Call Handling** - Complete SWML reference, IVR patterns
4. **Call Control** - Transfers, recording, conference management
5. **Messaging** - SMS/MMS, Campaign Registry compliance
6. **Video** - WebRTC integration, room management
7. **Fabric & Relay** - Subscribers, high availability
8. **Webhooks & Events** - Analytics, debugging, testing
9. **Number Management** - Compliance, bulk operations

### AI Voice Agents (10 Workflow Files)
- Voice AI navigation hub
- SDK basics and fundamentals
- Prompting best practices (RISE-M framework)
- SWAIG functions and DataMap
- Deployment (traditional, Docker, serverless)
- Common patterns and flows
- Error handling strategies
- Security and authentication
- Testing with swaig-test
- Debug webhooks and monitoring

### Code Examples
- **110+ Python examples** (with uv shebangs)
- **24+ JavaScript examples**
- **44+ SWML examples**
- All production-ready with error handling

## File Manifest

Distribution tarball includes:

```
signalwire-builder.tar.gz (~150 KB compressed)
│
├── plugin.json                  # Plugin manifest
├── marketplace.json             # Marketplace registration
├── SKILL.md                     # Main entry point (5.5 KB)
├── README.md                    # User documentation (11 KB)
├── DISTRIBUTION.md              # This file
├── INSTALL.md                   # Installation guide (3.4 KB)
├── LICENSE                      # MIT license
├── install.sh                   # Automated installer
│
├── workflows/                   # 19 workflow files (14,800+ lines)
│   ├── authentication-setup.md
│   ├── outbound-calling.md
│   ├── inbound-call-handling.md
│   ├── call-control.md
│   ├── messaging.md
│   ├── video.md
│   ├── fabric-relay.md
│   ├── webhooks-events.md
│   ├── number-management.md
│   ├── voice-ai.md
│   ├── ai-agent-sdk-basics.md
│   ├── ai-agent-prompting.md
│   ├── ai-agent-functions.md
│   ├── ai-agent-deployment.md
│   ├── ai-agent-patterns.md
│   ├── ai-agent-error-handling.md
│   ├── ai-agent-security.md
│   ├── ai-agent-testing.md
│   └── ai-agent-debug-webhooks.md
│
└── reference/                   # AI Agents SDK API docs
    ├── sdk/                     # 12 files: AgentBase, SWAIG, etc.
    ├── deployment/              # 3 files: Serverless, env vars
    └── examples/                # 6 complete agent examples
```

**Total size:** ~450 KB uncompressed, ~150 KB compressed

## Version Management

### Versioning Scheme

Follow semantic versioning:
- `1.0.0` - Major release (breaking changes to workflow structure)
- `1.1.0` - Minor release (new workflows, new examples)
- `1.0.1` - Patch release (bug fixes, typos, example corrections)

### Update Checklist

When releasing a new version:

1. ☐ Update version in `plugin.json`
2. ☐ Update version in `marketplace.json`
3. ☐ Update version in README.md "Version" section
4. ☐ Test all code examples still work
5. ☐ Create tarball with updated files
6. ☐ Create GitHub release with tarball
7. ☐ Update marketplace registry (if needed)

## Support Information

**For installation issues:**
1. Verify `~/.claude/plugins/` directory exists
2. Check permissions: `chmod -R 755 ~/.claude/plugins/signalwire-builder`
3. Restart Claude Code
4. Check `install.sh` output for errors
5. Verify `plugin.json` and `SKILL.md` are present

**For SignalWire API questions:**
- Documentation: https://developer.signalwire.com
- GitHub: https://github.com/signalwire
- Support: https://signalwire.com/support

**For plugin questions:**
- GitHub Issues: https://github.com/signalwire/signalwire-claude/issues
- Claude Code Docs: https://claude.ai/code

## Key Principles Documented

The plugin documents these production-tested principles:

1. **Treat AI Like a Person, Not a Program** - Natural language prompting
2. **Use Metadata for Security** - Keep sensitive data out of LLM context
3. **Test Continuously** - AI behavior is probabilistic
4. **Preserve Context Through Transfers** - 72% of customers expect it
5. **Implement Loop Protection** - Always protect gather/prompt nodes
6. **Avoid Over-Prompting** - Let AI be conversational
7. **Progressive Knowledge Building** - Use SWAIG to provide context incrementally
8. **Never Expose API Tokens** - Backend token generation pattern

## What's Excluded

The plugin explicitly avoids deprecated/compatibility APIs:
- ❌ LAML (compatibility API)
- ❌ CXML (XML-based markup)
- ❌ Any `/laml/` endpoints

Focus is exclusively on modern APIs:
- ✅ REST with JSON
- ✅ SWML (YAML/JSON)
- ✅ Relay SDK v4
- ✅ AI Agents SDK
- ✅ Call Fabric

## Knowledge Sources

- **Technical Documentation**: Official SignalWire REST APIs, SWML, SDKs
- **Practical Wisdom**: Analysis of 89 SignalWire training videos:
  - LiveWire sessions
  - SignalWire in Seconds tutorials
  - ClueCon 2025 workshops
  - Digital Employees examples
  - Production deployment case studies

## License

MIT License - See LICENSE file for details.

SignalWire is a trademark of SignalWire, Inc.

## Links

- **This Plugin**: https://github.com/signalwire/signalwire-claude
- **SignalWire Documentation**: https://developer.signalwire.com
- **SignalWire AI Agents SDK**: https://github.com/signalwire/signalwire-agents
- **Claude Code**: https://claude.ai/code
