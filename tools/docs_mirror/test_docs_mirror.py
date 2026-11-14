#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest"]
# ///
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import docs_mirror as dm

SWML_PAGE = """\
> This page is for SWML.

> Fetch clean Markdown by appending `.md` to any page URL under https://signalwire.com/docs or requesting it.

# connect

**`connect.to`** `string` — required

Single destination to dial.

---

**`connect.timeout`** `integer` — default: 60 seconds

---

**`connect.call_state_events`** `string[]` — default: \\['ended']

Allowed event names are `created`, `ringing`, `answered`, and `ended`.

---

**`connect.encryption`** `string` — default: optional

The encryption method. Possible values: `mandatory`, `optional`, `forbidden`.

---

**`connect.codecs`** `string` — default: Based on SignalWire settings

---

**`convo[].role`** `string` — required

The role. Valid values:

* `user` - A human.
* `assistant` - The agent.

```yaml
- connect:
    to: "+15551234567"
```
"""

REST_PAGE = """\
> This page is for APIs.

# Create queue

POST https://%7BYour_Space_Name%7D.signalwire.com/api/relay/rest/queues
Content-Type: application/json

## Request

- `name` (string, required) — The name of the queue.
- `max_size` (integer, optional, nullable) — Maximum callers.

## Response

### 201

## Errors

### 400 Bad Request Error

- `error` (enum, required)
  - Allowed values: `Internal Server Error`
- `direction` (enum, required) — The direction.
  - Allowed values: `inbound`, `outbound`
"""


def test_strip_boilerplate_removes_page_preamble():
    out = dm.strip_boilerplate(SWML_PAGE)
    assert "This page is for" not in out
    assert "Fetch clean Markdown" not in out
    assert out.lstrip().startswith("# connect")


def test_extract_swml_properties_as_leaf_names():
    ids = dm.extract_identifiers(SWML_PAGE)
    assert {"to", "timeout", "call_state_events", "encryption", "role"} <= ids["fields"]


def test_extract_rest_fields():
    ids = dm.extract_identifiers(REST_PAGE)
    assert {"name", "max_size", "direction"} <= ids["fields"]


def test_extract_enum_values_inline_and_bulleted():
    ids = dm.extract_identifiers(SWML_PAGE)
    assert {"created", "ringing", "answered", "ended"} <= ids["values"]
    assert {"mandatory", "optional", "forbidden"} <= ids["values"]
    assert {"user", "assistant"} <= ids["values"]


def test_extract_rest_allowed_values():
    ids = dm.extract_identifiers(REST_PAGE)
    assert {"inbound", "outbound"} <= ids["values"]


def test_multiword_values_are_ignored():
    ids = dm.extract_identifiers(REST_PAGE)
    assert "Internal Server Error" not in ids["values"]


def test_extract_endpoint_paths():
    ids = dm.extract_identifiers(REST_PAGE)
    assert ids["endpoints"] == {"POST /api/relay/rest/queues"}


def test_extract_status_codes():
    ids = dm.extract_identifiers(REST_PAGE)
    assert ids["status"] == {"201", "400"}


def test_coverage_reports_missing_status_code():
    condensed = "POST /api/relay/rest/queues `name` `max_size` `error` `direction` inbound outbound 201\n"
    report = dm.coverage([REST_PAGE], condensed)
    assert report.missing["status"] == {"400"}


def test_code_blocks_are_not_scanned():
    ids = dm.extract_identifiers(SWML_PAGE)
    assert "+15551234567" not in ids["values"]


def test_extract_defaults_keeps_only_concrete_values():
    defaults = dict(dm.extract_defaults(SWML_PAGE))
    assert defaults["timeout"] == "60"
    assert defaults["call_state_events"] == "ended"
    assert defaults["encryption"] == "optional"
    assert "codecs" not in defaults  # "Based on SignalWire settings" is not a value


def test_coverage_passes_when_everything_present():
    condensed = """\
# connect
- `to` string, required
- `timeout` int, default 60
- `call_state_events` string[], default [ended]; values: created, ringing, answered, ended
- `encryption` default optional; mandatory|optional|forbidden
- `codecs` default from settings
- `convo[].role` user|assistant
"""
    report = dm.coverage([SWML_PAGE], condensed)
    assert report.ok, report.render()


def test_coverage_reports_missing_field_and_value():
    condensed = "- `to` string\n- `timeout` default 60\n- encryption: optional, mandatory\n"
    report = dm.coverage([SWML_PAGE], condensed)
    assert not report.ok
    assert "call_state_events" in report.missing["fields"]
    assert "forbidden" in report.missing["values"]


def test_coverage_reports_wrong_default():
    condensed = """\
- `to`
- `timeout` default 30
- `call_state_events` default ended; created ringing answered ended
- `encryption` default optional; mandatory forbidden
- `codecs`
- `role` user assistant
"""
    report = dm.coverage([SWML_PAGE], condensed)
    assert ("timeout", "60") in report.bad_defaults
    assert report.missing["fields"] == set()


def test_coverage_matches_whole_words_only():
    condensed = "- `max_size_limit`\n"
    report = dm.coverage([REST_PAGE], condensed)
    assert "max_size" in report.missing["fields"]


def test_coverage_across_multiple_sources():
    other = REST_PAGE.replace("POST", "DELETE").replace("/queues", "/queues/{id}")
    condensed = """\
POST /api/relay/rest/queues ; DELETE /api/relay/rest/queues/{id} ; 201, 400
`name` `max_size` `error` `direction` inbound outbound
"""
    report = dm.coverage([REST_PAGE, other], condensed)
    assert report.ok, report.render()


def test_sha256_is_stable_and_ignores_boilerplate():
    a = dm.content_hash(SWML_PAGE)
    b = dm.content_hash(SWML_PAGE.replace("This page is for SWML.", "This page is for X."))
    assert a == b
    assert a != dm.content_hash(SWML_PAGE + "\nnew line")


def test_changed_pages():
    manifest = {"u1": {"sha256": "aaa"}, "u2": {"sha256": "bbb"}}
    fresh = {"u1": "aaa", "u2": "ccc", "u3": "ddd"}
    assert dm.changed_pages(manifest, fresh) == {"changed": ["u2"], "new": ["u3"], "removed": []}


def test_changed_pages_reports_removed():
    assert dm.changed_pages({"u1": {"sha256": "a"}}, {})["removed"] == ["u1"]


def test_stamp_freshness_replaces_existing_line():
    skill = "# SignalWire\n\nBundled docs verified against live docs: 2026-01-01\n\nmore\n"
    out = dm.stamp_freshness(skill, "2026-11-13")
    assert "verified against live docs: 2026-11-13" in out
    assert "2026-01-01" not in out


def test_stamp_freshness_requires_marker():
    with pytest.raises(ValueError):
        dm.stamp_freshness("# SignalWire\n", "2026-11-13")


PARAMS_PAGE = """\
**`params.direction`** `string` — default: the natural direction of the call

---

**`params.app_name`** `string` — default: swml app

---

**`params.eleven_labs_stability`** `number` — deprecated, default: 0.75

---

**`params.interrupt_prompt`** `string`

Prompt used on interruption.

**Default:** stop

---

**`params.enable_turn_detection`** `string` — default: both

How the turn ends.

* `both` — Use both signals.
* `punct_only` — Punctuation alone.

| Value | Meaning |
|---|---|
| `spell` | Spelled input |
| `veto` | Veto token |
"""


def test_bulleted_and_table_values_without_trigger_phrase():
    ids = dm.extract_identifiers(PARAMS_PAGE)
    assert {"both", "punct_only", "spell", "veto"} <= ids["values"]


def test_table_header_cells_are_not_values():
    ids = dm.extract_identifiers(PARAMS_PAGE)
    assert "Value" not in ids["values"]


def test_deprecated_default_and_separate_default_line():
    defaults = dict(dm.extract_defaults(PARAMS_PAGE))
    assert defaults["eleven_labs_stability"] == "0.75"
    assert defaults["interrupt_prompt"] == "stop"


def test_short_literal_phrase_default_is_checked():
    defaults = dict(dm.extract_defaults(PARAMS_PAGE))
    assert defaults["app_name"] == "swml app"
    assert "direction" not in defaults  # long descriptive default stays manual


def test_field_must_appear_in_code_span():
    condensed = "Calls in that direction are skipped.\n- `app_name` default swml app\n"
    report = dm.coverage([PARAMS_PAGE], condensed)
    assert "direction" in report.missing["fields"]
    assert "app_name" not in report.missing["fields"]


def test_field_inside_dotted_code_span_counts():
    report = dm.coverage([SWML_PAGE], "- `convo[].role` user assistant\n")
    assert "role" not in report.missing["fields"]


def test_default_must_be_on_a_line_naming_field_in_code():
    condensed = "- `app_name` string, default swml\nThe app name swml app is used.\n"
    report = dm.coverage([PARAMS_PAGE], condensed)
    assert ("app_name", "swml app") in report.bad_defaults



def test_bold_variable_names_are_fields():
    page = "## Variables\n\n**connect_result:** `connected` or `failed`.\n"
    assert "connect_result" in dm.extract_identifiers(page)["fields"]



def test_code_fences_do_not_break_span_matching():
    condensed = "```yaml\n- connect:\n    to: x\n```\n- `app_name` default swml app\n- `direction`\n- `eleven_labs_stability` default 0.75\n- `interrupt_prompt` default stop\n- `enable_turn_detection` default both\n"
    report = dm.coverage([PARAMS_PAGE], condensed)
    assert report.missing["fields"] == set(), report.render()


def test_field_inside_fenced_block_counts_as_code():
    condensed = "```yaml\napp_name: x\n```\n"
    report = dm.coverage([PARAMS_PAGE], condensed)
    assert "app_name" not in report.missing["fields"]



def test_stamp_freshness_replaces_never():
    skill = "<!-- Bundled docs verified against live docs: never -->\n"
    assert dm.stamp_freshness(skill, "2026-11-20") == "<!-- Bundled docs verified against live docs: 2026-11-20 -->\n"


def test_read_url_list_skips_comments_and_blanks():
    text = "# SWML\nhttps://a.example/x.md\n\n  https://a.example/y.md  \n# skipped below\n"
    assert dm.read_url_list(text) == ["https://a.example/x.md", "https://a.example/y.md"]


def _fake_fetch(monkeypatch, pages):
    monkeypatch.setattr(dm, "fetch", lambda url: pages[url])


def test_fetch_writes_manifest_to_given_path(tmp_path, monkeypatch):
    url = "https://signalwire.com/docs/swml/reference/calling/connect.md"
    _fake_fetch(monkeypatch, {url: SWML_PAGE})
    manifest = tmp_path / "keep" / "manifest.json"
    manifest.parent.mkdir()
    out = tmp_path / "cache"
    assert dm.main(["fetch", "--out", str(out), "--manifest", str(manifest), url]) == 0
    assert (out / "swml/reference/calling/connect.md").read_text() == SWML_PAGE
    assert not (out / "manifest.json").exists()
    entry = json.loads(manifest.read_text())[url]
    assert entry["sha256"] == dm.content_hash(SWML_PAGE)
    assert entry["path"] == "swml/reference/calling/connect.md"


def test_fetch_and_check_read_urls_file(tmp_path, monkeypatch, capsys):
    a, b = "https://signalwire.com/docs/a.md", "https://signalwire.com/docs/b.md"
    _fake_fetch(monkeypatch, {a: "# a\n", b: "# b\n"})
    urls = tmp_path / "pages.txt"
    urls.write_text(f"# group\n{a}\n{b}\n")
    manifest = tmp_path / "manifest.json"
    dm.main(["fetch", "--out", str(tmp_path / "cache"), "--manifest", str(manifest), "--urls-file", str(urls)])
    assert set(json.loads(manifest.read_text())) == {a, b}

    _fake_fetch(monkeypatch, {a: "# a\n", b: "# b changed\n"})
    capsys.readouterr()
    dm.main(["check", "--manifest", str(manifest), "--urls-file", str(urls)])
    assert json.loads(capsys.readouterr().out)["changed"] == [b]



def test_check_reports_404_page_as_removed(tmp_path, monkeypatch, capsys):
    import urllib.error
    gone = "https://signalwire.com/docs/gone.md"

    def fetch(url):
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)

    monkeypatch.setattr(dm, "fetch", fetch)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({gone: {"sha256": "x"}}))
    capsys.readouterr()
    dm.main(["check", "--manifest", str(manifest), gone])
    assert json.loads(capsys.readouterr().out)["removed"] == [gone]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
