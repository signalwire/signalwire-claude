# Installing the SignalWire Plugin

The plugin works in claude.ai chat (web, desktop, and mobile), in Cowork, and in Claude Code. Install it once per place you use Claude: installs on your claude.ai account also show up in Claude Code, but a Claude Code install from the command line stays on that machine.

## claude.ai and Cowork

1. Go to **Customize > Plugins > Add > Add marketplace**.
2. Enter `signalwire/signalwire-claude`.
3. Install **SignalWire** from that marketplace.

Once the plugin is listed in the Claude directory, you'll also be able to find it under **Customize > Plugins > Discover** without adding the marketplace.

On Team and Enterprise plans, an Owner can make the plugin available to members or install it for everyone.

## Claude Code

From inside a session:

```
/plugin marketplace add signalwire/signalwire-claude
/plugin install signalwire@signalwire
```

Or from a terminal:

```
claude plugin marketplace add signalwire/signalwire-claude
claude plugin install signalwire@signalwire
```

The plugin is active in the next session you start.

## Check that it's working

Ask Claude something SignalWire-specific, such as "Write a SWML IVR that routes to sales or support." Claude should use the SignalWire skill without you naming it.

The plugin also adds three commands. In Claude Code and Cowork, type them directly. In chat, describe what you want and Claude applies the matching one.

| Command | What it does |
|---|---|
| `/signalwire:new-agent` | Builds a voice AI agent from a description |
| `/signalwire:call-flow` | Writes a SWML call flow (IVR, routing, voicemail) |
| `/signalwire:debug` | Diagnoses failed calls, missing webhooks, auth errors, and SWAIG problems |

## Updating

In Claude Code, a marketplace install updates itself. Once a day the plugin checks its marketplace and installs a newer version if one has been published, which takes effect the next time you start Claude Code. It tells you the first time it runs and again whenever it updates itself.

To turn that off, set `SKILL_AUTO_UPDATE=0` in the environment Claude Code starts with, or create an empty `~/.claude/plugins/.no-auto-update` file. To update by hand:

```
/plugin marketplace update signalwire
/plugin update signalwire@signalwire
```

The automatic check doesn't run for installs from claude.ai, from an uploaded zip, or from a local folder.

## Upgrading from `signalwire-builder`

Versions before 1.2.0 were named `signalwire-builder`. The rename means Claude sees the new version as a different plugin, so `/plugin update` won't move you to it. Remove the old one and install the new one:

```
/plugin uninstall signalwire-builder@signalwire
/plugin marketplace update signalwire
/plugin install signalwire@signalwire
```

## Trying a local copy

To test changes to the plugin before they're published:

- **Claude Code:** `claude --plugin-dir /path/to/signalwire-claude` loads the folder for one session.
- **claude.ai:** zip the repository folder and upload it from **Customize > Plugins > Add > Upload plugin**.

Run `claude plugin validate /path/to/signalwire-claude` before either.

## Uninstalling

- **claude.ai and Cowork:** remove it from **Customize > Plugins**.
- **Claude Code:** `/plugin uninstall signalwire@signalwire`

## Getting help

- SignalWire questions: https://signalwire.com/docs and https://signalwire.com/support
- Plugin issues: https://github.com/signalwire/signalwire-claude/issues
