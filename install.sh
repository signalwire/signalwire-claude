#!/bin/bash
# SignalWire Plugin Installer for Claude Code

set -e

PLUGIN_NAME="signalwire-builder"
CLAUDE_PLUGINS_DIR="${HOME}/.claude/plugins"
INSTALL_DIR="${CLAUDE_PLUGINS_DIR}/${PLUGIN_NAME}"

echo "SignalWire Builder Plugin Installer for Claude Code"
echo "===================================================="
echo ""

# Check if plugins directory exists
if [ ! -d "${CLAUDE_PLUGINS_DIR}" ]; then
    echo "Creating Claude plugins directory: ${CLAUDE_PLUGINS_DIR}"
    mkdir -p "${CLAUDE_PLUGINS_DIR}"
fi

# Check if plugin already exists
if [ -d "${INSTALL_DIR}" ]; then
    echo "WARNING: SignalWire Builder plugin already exists at ${INSTALL_DIR}"
    read -p "Do you want to overwrite it? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 1
    fi
    echo "Removing existing installation..."
    rm -rf "${INSTALL_DIR}"
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Copy the plugin files
echo "Installing SignalWire Builder plugin to ${INSTALL_DIR}..."
mkdir -p "${INSTALL_DIR}"

# Copy .claude-plugin directory
if [ -d "${SCRIPT_DIR}/.claude-plugin" ]; then
    cp -r "${SCRIPT_DIR}/.claude-plugin" "${INSTALL_DIR}/"
else
    echo "❌ Error: .claude-plugin directory not found!"
    exit 1
fi

# Copy skills directory
if [ -d "${SCRIPT_DIR}/skills" ]; then
    cp -r "${SCRIPT_DIR}/skills" "${INSTALL_DIR}/"
else
    echo "❌ Error: skills directory not found!"
    exit 1
fi

# Verify installation
if [ -f "${INSTALL_DIR}/.claude-plugin/plugin.json" ] && [ -f "${INSTALL_DIR}/skills/signalwire/SKILL.md" ]; then
    echo ""
    echo "✅ Installation successful!"
    echo ""
    echo "The SignalWire Builder plugin has been installed to:"
    echo "  ${INSTALL_DIR}"
    echo ""
    echo "Plugin structure:"
    echo "  .claude-plugin/plugin.json     - Plugin manifest"
    echo "  .claude-plugin/marketplace.json - Marketplace metadata"
    echo "  skills/signalwire/SKILL.md     - Main skill entry point"
    echo ""
    echo "Included workflows:"
    ls -1 "${INSTALL_DIR}/skills/signalwire/workflows/" 2>/dev/null | sed 's/^/  - /' || echo "  (workflows directory not found)"
    echo ""
    echo "Plugin includes:"
    echo "  - Complete SignalWire REST API, SWML, and SDK documentation"
    echo "  - 110+ Python examples, 24+ JavaScript examples, 44+ SWML examples"
    echo "  - 19 workflow guides (14,800+ lines)"
    echo "  - AI Agents SDK complete reference"
    echo ""
    echo "Usage:"
    echo "  Claude will automatically use this plugin when working on SignalWire projects."
    echo ""
    echo "Documentation:"
    echo "  Main skill: ${INSTALL_DIR}/skills/signalwire/SKILL.md"
    echo "  README: ${INSTALL_DIR}/README.md (if copied)"
    echo ""
    echo "Restart Claude Code to activate the plugin."
    echo ""
else
    echo ""
    echo "❌ Installation failed!"
    echo "Could not find required files after installation."
    echo "Expected:"
    echo "  - ${INSTALL_DIR}/.claude-plugin/plugin.json"
    echo "  - ${INSTALL_DIR}/skills/signalwire/SKILL.md"
    exit 1
fi
