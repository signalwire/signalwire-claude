#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Mechanical half of the docs mirror: fetch, hash, coverage check, freshness stamp.

Condensing is done by an agent following CONDENSING.md. This script does the
parts that must never vary, and the coverage check that catches a condensed
file dropping a parameter, enum value, endpoint, status code, or default.

  docs_mirror.py fetch --out DIR [--manifest FILE] [--urls-file pages.txt] [URL...]
        save pages under DIR and record their hashes (manifest defaults to DIR/manifest.json)
  docs_mirror.py check --manifest FILE [--urls-file pages.txt] [URL...]
        list changed/new/removed pages; a page returning 404 or 410 counts as removed
  docs_mirror.py coverage --condensed FILE SRC... exit 1 if anything is missing
  docs_mirror.py stamp SKILL.md YYYY-MM-DD       update the freshness date
  docs_mirror.py tokens FILE...                  approximate token counts
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlparse

BOILERPLATE = re.compile(r"^> (This page is for|Fetch clean Markdown)\b.*\n?", re.M)
FENCE = re.compile(r"^```.*?^```[^\n]*\n?", re.M | re.S)
SWML_PROP = re.compile(r"\*\*`([^`]+)`\*\*\s+`[^`]+`(.*)$", re.M)
REST_FIELD = re.compile(r"^\s*[-*]\s+`([A-Za-z_][\w\-]*)`\s+\(", re.M)
VALUE_TRIGGER = re.compile(
    r"\b(allowed|possible|supported|valid)\b[^`]*?\b(values?|names?|codecs?)\b", re.I
)
BULLET_VALUE = re.compile(r"^\s*[-*]\s+`([^`]+)`")
DESCRIBED_VALUE = re.compile(r"^\s*[-*]\s+`([^`]+)`\s+[—–:-]\s", re.M)
TABLE_VALUE = re.compile(r"^\|\s*`([^`]+)`\s*\|", re.M)
BOLD_VARIABLE = re.compile(r"\*\*([a-z][a-z0-9_]*):\*\*", re.M)
CODE_SPAN = re.compile(r"`([^`]+)`")
ENDPOINT = re.compile(r"^(GET|POST|PUT|PATCH|DELETE)\s+(\S+)", re.M)
STATUS = re.compile(r"^#{2,4}\s+([1-5]\d\d)\b", re.M)
DEFAULT = re.compile(r"\bdefault:\s*(.+)$")
DEFAULT_LINE = re.compile(r"^\*\*Default:\*\*\s*(.+)$")
FRESHNESS = re.compile(r"(verified against live docs: )(\d{4}-\d{2}-\d{2}|never)")
SINGLE_TOKEN = re.compile(r"^[\w.+\-@:/]+$")


def strip_boilerplate(md: str) -> str:
    return BOILERPLATE.sub("", md).lstrip("\n")


def _prose(md: str) -> str:
    return FENCE.sub("", strip_boilerplate(md))


def _leaf(name: str) -> str:
    return name.split(".")[-1].replace("[]", "")


def _is_value(token: str) -> bool:
    return bool(token) and " " not in token


def extract_identifiers(md: str) -> dict[str, set[str]]:
    text = _prose(md)
    fields = {_leaf(m.group(1)) for m in SWML_PROP.finditer(text)}
    fields |= set(REST_FIELD.findall(text))
    fields |= set(BOLD_VARIABLE.findall(text))

    values: set[str] = set()
    lines = text.splitlines()
    for i, line in enumerate(lines):
        trigger = VALUE_TRIGGER.search(line)
        if not trigger:
            continue
        values |= {v for v in CODE_SPAN.findall(line[trigger.end():]) if _is_value(v)}
        if line.rstrip().endswith(":"):
            for following in lines[i + 1:]:
                if not following.strip():
                    continue
                bullet = BULLET_VALUE.match(following)
                if not bullet:
                    break
                if _is_value(bullet.group(1)):
                    values.add(bullet.group(1))

    values |= {v for v in DESCRIBED_VALUE.findall(text) + TABLE_VALUE.findall(text) if _is_value(v)}

    endpoints = {
        f"{verb} {unquote(urlparse(url).path)}"
        for verb, url in ENDPOINT.findall(text)
        if url.startswith("http")
    }
    status = set(STATUS.findall(text))
    return {"fields": fields, "values": values, "endpoints": endpoints, "status": status}


def _concrete_default(text: str) -> str | None:
    """The literal default value, or None when the default is descriptive."""
    words = text.replace("\\", "").strip().rstrip(".").split()
    if not words:
        return None
    first = words[0].strip("[]'\"`()")
    if not SINGLE_TOKEN.match(first):
        return None
    if len(words) == 1 or re.fullmatch(r"-?\d+(\.\d+)?", first):
        return first
    if len(words) <= 3 and first[0].islower() and all(SINGLE_TOKEN.match(w) for w in words):
        return " ".join(words)
    return None


def extract_defaults(md: str) -> list[tuple[str, str]]:
    """(leaf name, concrete default) pairs. Descriptive defaults are skipped."""
    out = []
    current = None
    for line in _prose(md).splitlines():
        prop = SWML_PROP.match(line)
        if prop:
            current = _leaf(prop.group(1))
            d = DEFAULT.search(prop.group(2))
        else:
            d = DEFAULT_LINE.match(line.strip()) if current else None
        value = _concrete_default(d.group(1)) if d else None
        if value:
            out.append((current, value))
    return out


def _word(token: str) -> re.Pattern:
    return re.compile(rf"(?<![\w\-]){re.escape(token)}(?![\w\-])")


def _code(text: str) -> list[str]:
    """Fenced block bodies plus inline code spans, matched one line at a time."""
    code, in_fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif in_fence:
            code.append(line)
        else:
            code += CODE_SPAN.findall(line)
    return code


def _in_code(name: str, text: str) -> bool:
    pattern = _word(name)
    return any(pattern.search(span) for span in _code(text))


@dataclass
class Coverage:
    missing: dict[str, set[str]] = field(default_factory=dict)
    bad_defaults: list[tuple[str, str]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(self.missing.values()) and not self.bad_defaults

    def render(self) -> str:
        if self.ok:
            return "coverage OK"
        parts = [f"missing {k}: {', '.join(sorted(v))}" for k, v in self.missing.items() if v]
        parts += [f"default for `{n}` should be {v}" for n, v in self.bad_defaults]
        return "\n".join(parts)


def coverage(sources: list[str], condensed: str) -> Coverage:
    wanted: dict[str, set[str]] = {"fields": set(), "values": set(), "endpoints": set(), "status": set()}
    defaults: set[tuple[str, str]] = set()
    for src in sources:
        for k, v in extract_identifiers(src).items():
            wanted[k] |= v
        defaults |= set(extract_defaults(src))

    report = Coverage()
    for kind, tokens in wanted.items():
        if kind == "fields":
            report.missing[kind] = {t for t in tokens if not _in_code(t, condensed)}
        else:
            report.missing[kind] = {t for t in tokens if not _word(t).search(condensed)}

    lines = condensed.splitlines()
    for name, value in sorted(defaults):
        holders = [l for l in lines if _in_code(name, l)]
        if holders and not any(_word(value).search(l) for l in holders):
            report.bad_defaults.append((name, value))
    return report


def content_hash(md: str) -> str:
    return hashlib.sha256(strip_boilerplate(md).strip().encode()).hexdigest()


def changed_pages(manifest: dict, fresh: dict[str, str]) -> dict[str, list[str]]:
    return {
        "changed": sorted(u for u, h in fresh.items() if u in manifest and manifest[u]["sha256"] != h),
        "new": sorted(u for u in fresh if u not in manifest),
        "removed": sorted(u for u in manifest if u not in fresh),
    }


def stamp_freshness(skill_md: str, day: str) -> str:
    if not FRESHNESS.search(skill_md):
        raise ValueError("SKILL.md has no 'verified against live docs: YYYY-MM-DD' (or 'never') line")
    return FRESHNESS.sub(rf"\g<1>{day}", skill_md)


def approx_tokens(text: str) -> int:
    return round(len(text) / 4)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"Accept": "text/markdown", "User-Agent": "signalwire-skill-docs-mirror/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode()


def read_url_list(text: str) -> list[str]:
    """URLs from a pages.txt-style list: one per line, '#' comments and blank lines ignored."""
    return [s for line in text.splitlines() if (s := line.strip()) and not s.startswith("#")]


def fetch_hashes(urls: list[str]) -> dict[str, str]:
    """Current content hash of each URL. Pages that are gone (404/410) are left out, so they show as removed."""
    hashes = {}
    for url in urls:
        try:
            hashes[url] = content_hash(fetch(url))
        except urllib.error.HTTPError as e:
            if e.code not in (404, 410):
                raise
    return hashes


def local_path(url: str) -> str:
    path = urlparse(url).path.removeprefix("/docs/")
    return path if path.endswith(".md") else path + ".md"


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch"); f.add_argument("--out", required=True); f.add_argument("--manifest")
    c = sub.add_parser("check"); c.add_argument("--manifest", required=True)
    for cmd in (f, c):
        cmd.add_argument("--urls-file", help="pages.txt-style list of URLs")
        cmd.add_argument("urls", nargs="*")
    v = sub.add_parser("coverage"); v.add_argument("--condensed", required=True); v.add_argument("sources", nargs="+")
    s = sub.add_parser("stamp"); s.add_argument("skill_md"); s.add_argument("day")
    t = sub.add_parser("tokens"); t.add_argument("files", nargs="+")
    a = p.parse_args(argv)
    if a.cmd in ("fetch", "check") and a.urls_file:
        a.urls += read_url_list(Path(a.urls_file).read_text())

    if a.cmd == "fetch":
        out = Path(a.out)
        manifest_path = Path(a.manifest) if a.manifest else out / "manifest.json"
        manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
        for url in a.urls:
            md = fetch(url)
            dest = out / local_path(url)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(md)
            manifest[url] = {"path": local_path(url), "sha256": content_hash(md), "fetched": date.today().isoformat()}
            print(f"{approx_tokens(md):>7}  {dest}")
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    elif a.cmd == "check":
        manifest = json.loads(Path(a.manifest).read_text())
        print(json.dumps(changed_pages(manifest, fetch_hashes(a.urls)), indent=2))
    elif a.cmd == "coverage":
        report = coverage([Path(s).read_text() for s in a.sources], Path(a.condensed).read_text())
        print(report.render())
        return 0 if report.ok else 1
    elif a.cmd == "stamp":
        path = Path(a.skill_md)
        path.write_text(stamp_freshness(path.read_text(), a.day))
    elif a.cmd == "tokens":
        for name in a.files:
            print(f"{approx_tokens(Path(name).read_text()):>7}  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
