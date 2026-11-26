#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest"]
# ///
"""Tests for release.py. Run: uv run --script .github/scripts/test_release.py"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import release  # noqa: E402


@pytest.mark.parametrize("version,level,expected", [
    ("1.2.0", "patch", "1.2.1"),
    ("1.2.9", "patch", "1.2.10"),
    ("1.2.7", "minor", "1.3.0"),
    ("1.2.7", "major", "2.0.0"),
])
def test_bump(version, level, expected):
    assert release.bump(version, level) == expected


def test_bump_rejects_non_semver():
    with pytest.raises(ValueError):
        release.bump("1.2", "patch")


@pytest.mark.parametrize("label_sets,expected", [
    ([], "patch"),
    ([["type/bug"], []], "patch"),
    ([["release:minor"], ["type/bug"]], "minor"),
    ([["release:minor"], ["release:major"]], "major"),
    ([["major"], ["minor"]], "patch"),
    ([["severity:major"]], "patch"),
])
def test_level_from_labels(label_sets, expected):
    assert release.level_from_labels(label_sets) == expected


@pytest.mark.parametrize("paths,expected", [
    (["README.md", "INSTALL.md", ".github/workflows/release.yml"], False),
    (["README.md", "skills/signalwire/SKILL.md"], True),
    (["commands/debug.md"], True),
    (["hooks/self-update.sh"], True),
    ([".mcp.json"], True),
    ([".claude-plugin/plugin.json"], True),
    ([], False),
])
def test_releasable(paths, expected):
    assert release.releasable(paths) is expected


def test_set_version_updates_every_version_field(tmp_path):
    plugin = tmp_path / "plugin.json"
    market = tmp_path / "marketplace.json"
    plugin.write_text('{\n  "name": "signalwire",\n  "version": "1.2.0",\n  "license": "MIT"\n}\n')
    market.write_text(
        '{\n  "metadata": {\n    "version": "1.2.0"\n  },\n'
        '  "plugins": [\n    {\n      "name": "signalwire",\n      "version": "1.2.0"\n    }\n  ]\n}\n'
    )
    release.set_version([plugin, market], "1.2.1")
    assert json.loads(plugin.read_text())["version"] == "1.2.1"
    m = json.loads(market.read_text())
    assert m["metadata"]["version"] == "1.2.1"
    assert m["plugins"][0]["version"] == "1.2.1"
    # formatting is preserved: only the version strings change
    assert plugin.read_text() == '{\n  "name": "signalwire",\n  "version": "1.2.1",\n  "license": "MIT"\n}\n'


def test_read_version(tmp_path):
    p = tmp_path / "plugin.json"
    p.write_text('{"name": "x", "version": "3.4.5"}')
    assert release.read_version(p) == "3.4.5"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
