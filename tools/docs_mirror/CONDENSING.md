# Condensing SignalWire docs for the skill

The skill's `docs/` directory holds condensed copies of SignalWire documentation pages. Claude reads them in the middle of a task when it needs an exact parameter name, default, allowed value, endpoint, or payload field and cannot reach the live docs. The live pages are written for people and spend tokens on explanation. A condensed page keeps every fact and drops the rest.

These instructions are for the agent that maintains `docs/`. The mechanical steps (fetching, hashing, the coverage check, the freshness date) are in `docs_mirror.py`, in the same directory as this file.

Each condensed file lives at the path of its live URL under `skills/signalwire/docs/`: `https://signalwire.com/docs/swml/reference/calling/connect.md` becomes `skills/signalwire/docs/swml/reference/calling/connect.md`. REST resources are the exception (see below).

## The reader

The reader is Claude, partway through writing SWML, a REST call, or a webhook handler. It already knows telephony, HTTP, YAML, and JSON. It needs the one fact it is missing, stated exactly, and it needs to trust that a fact missing from the page is missing from SignalWire.

## Keep

- Every parameter, field, and property, with its type, whether it is required, its default, and its allowed values.
- Every constraint and scoping rule: "rejected without the leading `+`", "SIP targets only", "ignored when `to` starts with `queue:`", "case-sensitive", value ranges, length limits, reserved names.
- Every endpoint: method and path.
- Response fields and status codes, plus any error that is specific to this page.
- Behavior a developer would otherwise get wrong: ordering, what runs when, what happens on failure, what is advisory or best-effort.
- Anything stated as a warning, note, or caution in the source. A recommendation the source makes ("choose a small, fast model") counts as a fact. Keep it and attribute it to the source; don't add your own.

## Drop

- The page preamble (`> This page is for…`, `> Fetch clean Markdown…`).
- Introductory sentences that restate the title or the parameter name.
- The JSON copy of an example that also appears in YAML. Keep the YAML.
- The full Basic Auth explanation on REST pages. State the required API token scope in one line.
- Generic error responses (`422` validation list, `500`) after the first time they appear in a file.
- "Learn more" links whose target adds no fact needed here. Keep a link when it carries a fact, such as "form-encoded requests go to the Compatibility API".
- Request and response JSON examples and SDK code on REST pages, when the schema already shows the same shape.
- Repeated copies of one example in several SDK languages. Keep one language in full (Python), and for each other language give one line with its package, version, and any method names that differ.
- Transitional and marketing prose.

## Never

- Add a fact, default, or example that is not in the source. If the source is ambiguous, keep its wording rather than resolving it.
- Merge two parameters that look alike, or generalize a rule that the source scopes to one case.
- Give advice or opinions. The skill's hand-written files in `skills/signalwire/workflows/` hold those; this layer holds facts.
- Fix something that looks like a mistake in the source, such as an example with broken YAML or a field the page names but never defines. Keep it as written, mark it "(as in source)", and list it in your run report so the docs team can fix the live page.

## Format

Start every file with its source, as a full URL ending in `.md`, so Claude can fetch the live page without building a URL:

```
# connect (SWML method)
Source: https://signalwire.com/docs/swml/reference/calling/connect.md
```

A file condensed from several pages lists each one, and each endpoint block repeats its own source URL.

Write one line per parameter, with its name in backticks and its type, required or default, and allowed values on that same line. The coverage check only counts a parameter as present when its name is inside backticks, and only counts a default when it is on a line that names the parameter in backticks. A default that the source gives on its own line (`**Default:** …`) goes on the parameter's line.

```
- `timeout` int, default 60 — seconds to wait for an answer
- `encryption` string, default optional — values: mandatory | optional | forbidden
- `to` string, required — E.164 with leading `+` (without it: rejected), `sip:`/`sips:` URI, Resource Address path, `queue:<name>`, `call:<call_id>`, or `stream:wss://…` (`ws://` rejected). `queue:`/`call:`/`stream:` must be lowercase.
```

Write nested properties as dotted or `[]` paths (`headers[].name`), or indent them under their parent. Use the same name as the source.

Several fields may share a line when they have the same type, the same required or optional status, the same rule for when they are present, and no default, as with a group of SIP `*_host`, `*_uri` and `*_user` fields. Put each name in its own backticks. Several fields may also share one description written once after the list.

When a page repeats the same properties under several tabs or modes (single, parallel, serial), list them once, say which modes they apply to, and then spell out every difference for each mode. Merge only text that is identical in the source.

Keep examples only when they show something the parameter list does not, such as nesting, the shape of a payload, or how two parameters combine. Keep one example per distinct mode, cut to the lines that matter.

Rewrite every SignalWire docs link as a full URL ending in `.md` (`https://signalwire.com/docs/swml/reference/calling/enter-queue.md`). Do not leave relative or root-relative links (`/docs/...`, `#anchor`); Claude may refuse to follow those. A link to a section becomes the page URL followed by the section's name in text: `https://signalwire.com/docs/swml/reference/calling.md (section "Document-fetching webhook")`. Leave links outside the SignalWire docs as they are.

Write the REST base URL as `https://{Your_Space_Name}.signalwire.com`. The sources percent-encode the braces.

## REST endpoints: one file per resource

Condense every endpoint of one resource (create, get, list, update, delete) into a single file, for example `docs/apis/rest/queues.md`:

1. The resource object schema, once.
2. One block per endpoint: method and path, source URL, API token scope, request parameters, and the response, written as "returns the queue object" when it matches the schema. Spell out only the ways an endpoint differs from the others, such as paging fields on list or which fields update accepts.
3. Errors and status codes, once, noting any endpoint that differs.

## Webhook payload pages

Treat these as a payload schema. Give when the webhook is sent and what triggers it, the top-level fields, then the nested fields as dotted paths, then the delivery notes (for example, that delivery is best effort). There is no endpoint or scope line.

## Guides

Condense a procedural guide to its prerequisites, its steps in order, the request and response contract, and its constraints. Drop the narrative that teaches the concept. The coverage check finds few identifiers in guides, so check them by hand (below).

## Verify before writing

1. Run `docs_mirror.py coverage --condensed <file> <source.md>...`. It fails when the file is missing a field, an allowed value, an endpoint, a status code, or a short literal default named in the source. Fix every failure by restoring the fact, not by working around the check.
2. Then read the source again from top to bottom. The coverage check sees names, values, endpoints, status codes, and short literal defaults. Check these by hand, because it cannot:
   - Every constraint, warning, and behavior sentence, such as "a number without `+` is rejected".
   - Descriptive defaults ("Based on SignalWire settings", "Inherits the top-level timeout, then 60 seconds") and defaults that appear only in prose ("by default, only `ended`").
   - That each allowed value is listed under the right field. The check only confirms a value appears somewhere in the file.
   - Differences between modes or object paths that share a parameter name.
3. Record the token counts before and after (`docs_mirror.py tokens`).

## The routine

Pages in scope are those holding facts an agent needs to act correctly: reference pages, procedural guides, limits, allowlists, and catalogs such as TTS voices. Skip overviews, conceptual explainers, onboarding, and the changelog. Keep the URLs of in-scope pages in `skills/signalwire/docs/pages.txt`, one per line. `docs_mirror.py fetch` records each page's hash in `manifest.json` in its output directory.

- **Daily:** run `docs_mirror.py check --manifest <manifest.json>` with the URLs from `pages.txt`. Re-condense changed pages. Compare the product indexes (the `llms.txt` files) with `pages.txt` to find new pages; condense the ones in scope and add them to `pages.txt`. When a page is removed or moved, flag it for review instead of keeping the old copy.
- **Each run that passes every check:** run `docs_mirror.py stamp skills/signalwire/SKILL.md <today>`. SKILL.md must contain the line `Bundled docs verified against live docs: YYYY-MM-DD`. The date means "last confirmed against the live docs", not "last changed".
- **When a skipped page changes substantially:** check it against the scope rule again, because it may now hold facts.
- **Quarterly:** check every page in the product indexes against the scope rule to catch restructuring.
