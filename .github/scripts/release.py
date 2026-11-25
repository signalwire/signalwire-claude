#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Version helpers for the release workflow.

  release.py current                   print the version in plugin.json
  release.py next LEVEL                print the version after a LEVEL bump
  release.py level < labels.json       print patch, minor, or major for a JSON list of label lists
  release.py releasable < paths.txt    exit 0 if any changed path ships in the plugin
  release.py set VERSION               write VERSION to every version field
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION_FILES = [ROOT / ".claude-plugin/plugin.json", ROOT / ".claude-plugin/marketplace.json"]
# Paths an install receives. Anything else (README, INSTALL, .github) doesn't need a release.
SHIPPED = ("skills/", "commands/", "hooks/", ".claude-plugin/", ".mcp.json")
LEVELS = ("patch", "minor", "major")
VERSION_FIELD = re.compile(r'("version"\s*:\s*")(\d+\.\d+\.\d+)(")')


def bump(version: str, level: str) -> str:
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    if not m:
        raise ValueError(f"not a MAJOR.MINOR.PATCH version: {version!r}")
    major, minor, patch = map(int, m.groups())
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def level_from_labels(label_sets: list[list[str]]) -> str:
    """The biggest release:minor / release:major label across the merged PRs, else patch."""
    found = {label.removeprefix("release:") for labels in label_sets for label in labels}
    return max((lvl for lvl in LEVELS if lvl in found), key=LEVELS.index, default="patch")


def releasable(paths: list[str]) -> bool:
    return any(p == ".mcp.json" or p.startswith(SHIPPED) for p in paths)


def read_version(path: Path) -> str:
    return json.loads(Path(path).read_text())["version"]


def set_version(paths: list[Path], version: str) -> None:
    for path in paths:
        path = Path(path)
        text, n = VERSION_FIELD.subn(rf"\g<1>{version}\g<3>", path.read_text())
        if not n:
            raise ValueError(f"no version field in {path}")
        path.write_text(text)


def main(argv: list[str]) -> int:
    cmd, *args = argv
    if cmd == "current":
        print(read_version(VERSION_FILES[0]))
    elif cmd == "next":
        print(bump(read_version(VERSION_FILES[0]), args[0]))
    elif cmd == "level":
        print(level_from_labels(json.load(sys.stdin)))
    elif cmd == "releasable":
        return 0 if releasable([line.strip() for line in sys.stdin if line.strip()]) else 1
    elif cmd == "set":
        set_version(VERSION_FILES, args[0])
    else:
        print(__doc__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
