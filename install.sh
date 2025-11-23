#!/bin/bash
# SignalWire Skill Installer for Claude Code

set -e

SKILL_NAME="signalwire"
CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"
INSTALL_DIR="${CLAUDE_SKILLS_DIR}/${SKILL_NAME}"

echo "SignalWire Skill Installer for Claude Code"
echo "=========================================="
echo ""

# Check if skills directory exists
if [ ! -d "${CLAUDE_SKILLS_DIR}" ]; then
    echo "Creating Claude skills directory: ${CLAUDE_SKILLS_DIR}"
    mkdir -p "${CLAUDE_SKILLS_DIR}"
fi

# Check if skill already exists
if [ -d "${INSTALL_DIR}" ]; then
    echo "WARNING: SignalWire skill already exists at ${INSTALL_DIR}"
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

# Copy the skill files
echo "Installing SignalWire skill to ${INSTALL_DIR}..."
cp -r "${SCRIPT_DIR}" "${INSTALL_DIR}"

# Verify installation
if [ -f "${INSTALL_DIR}/SKILL.md" ]; then
    echo ""
    echo "✅ Installation successful!"
    echo ""
    echo "The SignalWire skill has been installed to:"
    echo "  ${INSTALL_DIR}"
    echo ""
    echo "Included workflows:"
    ls -1 "${INSTALL_DIR}/workflows/" | sed 's/^/  - /'
    echo ""
    echo "Usage:"
    echo "  Claude will automatically use this skill when working on SignalWire projects."
    echo "  You can also invoke it with: /signalwire"
    echo ""
    echo "Documentation:"
    echo "  Main guide: ${INSTALL_DIR}/SKILL.md"
    echo "  README: ${INSTALL_DIR}/README.md"
    echo ""
else
    echo ""
    echo "❌ Installation failed!"
    echo "Could not find SKILL.md after installation."
    exit 1
fi
