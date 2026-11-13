# Condensed-docs pilot, 2026-11-13

The question: can SignalWire's live docs pages be condensed for an LLM reader without losing facts, and how much does that save?

Five page types were condensed by agents following `../CONDENSING.md`, checked with `../docs_mirror.py coverage`, re-read by hand against the source, and then tested with 20 questions answered once from the condensed files and once from the source pages.

## Token reduction

Approximate tokens (characters / 4).

| Page type | Source | Source tokens | Condensed tokens | Saved |
|---|---|---:|---:|---:|
| Large SWML parameter reference | `swml/reference/calling/ai/params` | 9,289 | 5,881 | 37% |
| SWML method with modes and examples | `swml/reference/calling/connect` | 18,490 | 5,170 | 72% |
| REST resource (5 endpoint pages into 1 file) | `apis/rest/queues/*` | 8,369 | 1,012 | 88% |
| Webhook payload | `apis/rest/webhooks/call-state-status-callback` | 2,481 | 1,507 | 39% |
| Procedural guide | `swml/guides/deployment` | 1,651 | 951 | 42% |
| **Total** | | **40,280** | **14,521** | **64%** |

Savings depend on the page type. Pages that are mostly parameter rules (`ai/params`, webhook payloads) shrink by about 40%, because nearly every sentence is a fact. Pages with repeated examples, repeated mode tabs, or YAML and JSON copies of each example shrink by about 70%. REST resources shrink the most, because their five endpoint pages repeat the same auth text, object schema, and error blocks.

## Answer accuracy

Both readers used Sonnet (`questions.md`, answer key in `answers.md`). The questions mix simple lookups (defaults, field names) with behavior rules the coverage check can't see (the 20-destination limit, what happens to a queue with waiting callers, which fields are not allowed with `queue:`).

| Reader | Correct | Tokens read |
|---|---:|---:|
| Condensed files only | 20 / 20 | ~14,700 |
| Source pages only | 20 / 20 | ~40,500 |

## Coverage check

The condensing agents probed the check by deleting facts from copies of their output. It was strengthened to catch what they found. It now fails on a missing:

- field name, which must appear inside backticks
- allowed value
- endpoint
- status code
- short literal default, including deprecated defaults and defaults given on their own line

It still can't see behavior rules, descriptive or prose-only defaults, whether a value is listed under the right field, or differences between modes that share a parameter name. CONDENSING.md has the condensing agent check those by hand.

## Possible problems in the live docs, found while condensing

- `swml/guides/deployment`: the `execute` example writes `main:` as a mapping instead of a list.
- `apis/rest/webhooks/call-state-status-callback`: the SIP data section says it is present when "`call.type` is `sip`", but this payload has `device.type`, not `call.type`.
- `swml/reference/calling/connect`: `result` says it uses `switch` "when the `return_value` is a object" and `cond` "when the `return_value` is an array". It probably means the type of `result`.
- `swml/reference/calling/connect`: `peer.device` is shown in an example but never defined.
- `apis/rest/queues/delete-queue`: a non-empty queue "returns a validation error", but the page lists only `400` and `500`, not `422`.
