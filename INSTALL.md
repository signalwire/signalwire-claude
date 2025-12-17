# SignalWire Builder Plugin Installation Guide

## Quick Install (Recommended)

### Option 1: Install from Claude Code Marketplace

The easiest way to install:

```bash
/plugin marketplace add signalwire/signalwire-claude
/plugin install signalwire-builder
```

### Option 2: Using the Install Script

```bash
# Extract the archive
tar -xzf signalwire-builder.tar.gz

# Run the installer
cd signalwire-builder
./install.sh
```

The installer will:
- Create `~/.claude/plugins/signalwire-builder/` if it doesn't exist
- Check for existing installation (prompts before overwriting)
- Copy all plugin files to the correct location
- Verify the installation

### Option 3: Manual Installation

```bash
# Extract the archive
tar -xzf signalwire-builder.tar.gz

# Create plugin directory
mkdir -p ~/.claude/plugins/signalwire-builder

# Copy the plugin contents
cp -r signalwire-builder/.claude-plugin ~/.claude/plugins/signalwire-builder/
cp -r signalwire-builder/skills ~/.claude/plugins/signalwire-builder/

# Verify installation
ls ~/.claude/plugins/signalwire-builder/skills/signalwire/SKILL.md
```

## Verification

After installation, verify the plugin is present:

```bash
ls -la ~/.claude/plugins/signalwire-builder/
```

You should see:
```
.claude-plugin/
  ├── plugin.json
  └── marketplace.json
skills/
  └── signalwire/
      ├── SKILL.md
      ├── workflows/
      │   ├── authentication-setup.md
      │   ├── call-control.md
      │   ├── fabric-relay.md
      │   ├── inbound-call-handling.md
      │   ├── messaging.md
      │   ├── number-management.md
      │   ├── outbound-calling.md
      │   ├── video.md
      │   ├── voice-ai.md
      │   ├── webhooks-events.md
      │   └── [9 more AI agent workflow files]
      └── reference/
          ├── sdk/
          ├── deployment/
          └── examples/
```

## Usage

Once installed, Claude Code will automatically use the SignalWire skill when:

- You mention SignalWire in your prompts
- You're working on telephony/messaging/video applications
- You ask about SWML, REST APIs, or SDKs
- You're building AI voice agents

The plugin activates automatically based on context - no manual invocation needed!

## Troubleshooting

### Plugin Not Loading

1. **Check file location**:
   ```bash
   ls ~/.claude/plugins/signalwire-builder/skills/signalwire/SKILL.md
   ```

2. **Verify plugin structure**:
   ```bash
   ls ~/.claude/plugins/signalwire-builder/.claude-plugin/plugin.json
   ```

3. **Restart Claude Code**: Close and reopen Claude Code after installation

4. **Check plugin list**:
   ```bash
   /plugin list
   ```

### Skill Not Triggering

Make sure you're working on SignalWire-related tasks. The skill activates when:
- File names or paths contain "signalwire"
- Your prompts mention SignalWire APIs
- You're working with SWML documents
- You're building voice AI agents

## Updating

To update to a newer version:

```bash
# Using marketplace (easiest)
/plugin update signalwire-builder

# Or manually
rm -rf ~/.claude/plugins/signalwire-builder
tar -xzf signalwire-builder-v2.tar.gz
cd signalwire-builder
./install.sh
```

## Uninstallation

To remove the plugin:

```bash
# Using Claude Code
/plugin uninstall signalwire-builder

# Or manually
rm -rf ~/.claude/plugins/signalwire-builder
```

## What's Included

- **6,056 lines** of comprehensive documentation
- **110+ Python** code examples
- **24+ JavaScript** code examples
- **44+ SWML** (YAML) examples
- **10 workflow guides** covering all SignalWire features

## Requirements

- Claude Code with skills support
- macOS, Linux, or WSL (for install script)
- No other dependencies

## Next Steps

After installation:

1. Open Claude Code
2. Start a new conversation
3. Ask Claude about SignalWire (e.g., "How do I make an outbound call with SignalWire?")
4. Watch Claude automatically use the expert knowledge!

## Getting Help

**For SignalWire questions**:
- https://developer.signalwire.com/
- https://signalwire.com/support

**For Claude Code questions**:
- https://docs.claude.com/

## License

This skill is provided as-is for use with Claude Code.
SignalWire is a trademark of SignalWire, Inc.
