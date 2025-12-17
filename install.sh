#!/bin/bash
# SignalWire Plugin Installer for Claude Code

set -e

PLUGIN_NAME="signalwire-builder"
CLAUDE_PLUGINS_DIR="${HOME}/.claude/plugins"
INSTALL_DIR="${CLAUDE_PLUGINS_DIR}/${PLUGIN_NAME}"

echo "SignalWire Plugin Installer for Claude Code"
echo "==========================================="
echo ""

# Check if plugins directory exists
if [ ! -d "${CLAUDE_PLUGINS_DIR}" ]; then
    echo "Creating Claude plugins directory: ${CLAUDE_PLUGINS_DIR}"
    mkdir -p "${CLAUDE_PLUGINS_DIR}"
fi

# Check if plugin already exists
if [ -d "${INSTALL_DIR}" ]; then
    echo "WARNING: SignalWire plugin already exists at ${INSTALL_DIR}"
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
echo "Installing SignalWire plugin to ${INSTALL_DIR}..."
mkdir -p "${INSTALL_DIR}"
cp -r "${SCRIPT_DIR}"/* "${INSTALL_DIR}/"

# Verify installation
if [ -f "${INSTALL_DIR}/SKILL.md" ] && [ -f "${INSTALL_DIR}/plugin.json" ]; then
    echo ""
    echo "✅ Installation successful!"
    echo ""
    echo "The SignalWire plugin has been installed to:"
    echo "  ${INSTALL_DIR}"
    echo ""
    echo "Included workflows:"
    ls -1 "${INSTALL_DIR}/workflows/" | sed 's/^/  - /'
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
    echo "  Main guide: ${INSTALL_DIR}/SKILL.md"
    echo "  README: ${INSTALL_DIR}/README.md"
    echo ""
    echo "Restart Claude Code to activate the plugin."
    echo ""
else
    echo ""
    echo "❌ Installation failed!"
    echo "Could not find required files after installation."
    exit 1
fi
