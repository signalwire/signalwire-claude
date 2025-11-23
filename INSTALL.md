# SignalWire Skill Installation Guide

## Quick Install (Recommended)

### Option 1: Using the Install Script

```bash
# Extract the archive
tar -xzf signalwire-skill.tar.gz

# Run the installer
cd signalwire
./install.sh
```

The installer will:
- Create `~/.claude/skills/` if it doesn't exist
- Check for existing installation (prompts before overwriting)
- Copy all skill files to the correct location
- Verify the installation

### Option 2: Manual Installation

```bash
# Extract the archive
tar -xzf signalwire-skill.tar.gz

# Create skills directory if needed
mkdir -p ~/.claude/skills

# Copy the skill
cp -r signalwire ~/.claude/skills/

# Verify installation
ls ~/.claude/skills/signalwire/SKILL.md
```

## Verification

After installation, verify the skill is present:

```bash
ls -la ~/.claude/skills/signalwire/
```

You should see:
```
SKILL.md
README.md
install.sh
workflows/
  ├── authentication-setup.md
  ├── call-control.md
  ├── fabric-relay.md
  ├── inbound-call-handling.md
  ├── messaging.md
  ├── number-management.md
  ├── outbound-calling.md
  ├── video.md
  ├── voice-ai.md
  └── webhooks-events.md
```

## Usage

Once installed, Claude Code will automatically use this skill when:

- You mention SignalWire in your prompts
- You're working on telephony/messaging/video applications
- You ask about SWML, REST APIs, or SDKs
- You're building AI voice agents

### Manual Activation

You can also explicitly invoke the skill:

```
/signalwire
```

Or in your prompts:
```
"Using SignalWire, create an IVR system..."
```

## Troubleshooting

### Skill Not Loading

1. **Check file location**:
   ```bash
   ls ~/.claude/skills/signalwire/SKILL.md
   ```

2. **Verify permissions**:
   ```bash
   chmod -R 644 ~/.claude/skills/signalwire/*.md
   chmod 755 ~/.claude/skills/signalwire/workflows/
   ```

3. **Restart Claude Code**: Close and reopen Claude Code after installation

### Skill Not Triggering

Make sure you're working on SignalWire-related tasks. The skill activates when:
- File names or paths contain "signalwire"
- Your prompts mention SignalWire APIs
- You're working with SWML documents
- You explicitly invoke `/signalwire`

## Updating

To update to a newer version:

```bash
# Remove old version
rm -rf ~/.claude/skills/signalwire

# Install new version (using either method above)
tar -xzf signalwire-skill-v2.tar.gz
cd signalwire
./install.sh
```

## Uninstallation

To remove the skill:

```bash
rm -rf ~/.claude/skills/signalwire
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
