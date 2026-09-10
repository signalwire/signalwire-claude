# AI Sidecar (Real-Time Agent Coaching)

## Overview

The SWML `ai_sidecar` method attaches a real-time AI **observer** to a live call. Unlike the `ai` method, the sidecar listens as a third party and **never speaks on the call** — after each customer turn it sends agent-facing advice to your application as webhook/relay callbacks that an agent's UI (or any consumer) can render. Think of it as a coach watching over the agent's shoulder: it runs alongside the call rather than driving it.

**Use cases:** live sales coaching, real-time compliance flagging, intent-based UI navigation, voice-of-customer signal extraction, supervisor-on-shoulder workflows.

**Common pattern:** attach `ai_sidecar` to coach a human agent on a `connect`-bridged call — the customer talks to the human, and the sidecar coaches the human's screen.

Docs: https://signalwire.com/docs/swml/reference/calling/ai-sidecar (subpages: `/params`, `/prompt`, `/swaig`)

## ai_sidecar vs ai vs live_transcribe

| Method | Speaks on call? | Purpose |
|--------|-----------------|---------|
| `ai` | Yes | Conversational AI agent that talks to the caller |
| `ai_sidecar` | No | AI observer that coaches the human agent via callbacks |
| `live_transcribe` | No | Plain transcription, no AI evaluation |

**One transcriber per call:** `ai_sidecar` and `live_transcribe` cannot run on the same call simultaneously — starting one while the other is active is rejected.

## How It Works

Each time the customer finishes speaking, the sidecar evaluates the conversation. This evaluation is a **tick**; every callback carries a `tick_id`. On each tick:

1. Detects **end of customer turn** — a final transcription result followed by brief silence (`idle_timeout_ms`), or the agent starting to speak.
2. Sends the running transcript to the model with your operator prompt and SWAIG tools.
3. The model returns one line of agent-facing advice (an `insight`), or calls the built-in `sidecar_skip` tool to stay silent.
4. Tools the model calls run through your SWAIG functions / MCP servers.
5. Every step fires a structured callback.

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `prompt` | string/object | Operator prompt for coaching behavior. Plain string, POM, or server-side file. Optional but strongly recommended (falls back to minimal default). SignalWire adds built-in sidecar role instructions automatically. |
| `lang` | string | Single BCP-47 tag (e.g. `en-US`). Sets ASR language, shared with model as hint. |
| `model` | string | Model for advice and end-of-call summaries. Suggested: `gpt-4o-mini`, `gpt-4.1-mini`, `gpt-4.1-nano`. |
| `direction` | array | Call legs to observe: `remote-caller`, `local-caller`. Both legs required; defaults to both. Single-leg is rejected. |
| `customer_leg` | string | Which leg is the customer (turn-end trigger source): `remote-caller` or `local-caller`. |
| `url` | string | Webhook URL for callbacks. When unset, callbacks publish only on relay topic `calling.ai.sidecar` (relay always fires; webhook is opt-in). Basic auth embeddable: `username:password@url`. |
| `SWAIG` | object | Functions and MCP servers available to the sidecar (see below). |
| `permissions` | object | SWAIG permission overrides. Defaults to all enabled. |
| `global_data` | object | Initial key-value data. Reference in prompt via `${global_data.key}`; included in tool requests; persists across sessions on the same call leg as `${ai_agents_global_data.key}`. |
| `hints` | array | ASR hints biasing recognition toward terms (product names, jargon, SWAIG enum values). Strongly recommended. Example: `["ACME", "Globex", "FedRAMP", "SOC 2"]`. |
| `params` | object | Tuning options (see Tuning Params below). |
| `action` | object | `action.summarize` generates a one-off conversation summary and returns instead of attaching a sidecar. `summarize.webhook` (defaults to `url`) and `summarize.prompt` (defaults to `ai_summary_prompt`). |

### Permissions

All default to enabled. Setting `params.act_on_channel: false` overrides all of them — actions fire as callbacks but never apply to the call.

- `swaig_allow_swml` — whether tools may run SWML on the call
- `swaig_allow_settings` — whether tools may change sidecar settings (e.g. model)
- `swaig_set_global_data` — whether tools may set global data

### Tuning Params (`params`)

All optional.

**Reaction:**

| Param | Range | Description |
|-------|-------|-------------|
| `idle_timeout_ms` | 50–5000 | Silence (ms) after customer finishes before evaluation. Lower = faster reaction. If the agent speaks while the customer's turn is pending, evaluation runs immediately. |
| `min_interval_ms` | 0–60000 | Minimum time between evaluations — throttle for busy calls. |
| `max_iters_per_tick` | 1–20 | Max tool calls chained in one evaluation before advice must be produced. |
| `max_history_tokens` | 1000–200000 | Token budget for running history; oldest messages dropped past it. |
| `act_on_channel` | boolean | Whether tool actions (transfer, hangup, etc.) take effect on the call or are report-only. |

**Summaries:**

| Param | Description |
|-------|-------------|
| `final_summary` | Generate a closing summary of the sidecar's session at call end (included in `final` callback). |
| `ai_summary` | Generate an end-of-call summary of the conversation itself (distinct from `final_summary`). |
| `ai_summary_prompt` | Custom prompt for the end-of-call conversation summary. |
| `summary_model` | Model for the end-of-call summary (distinct from the sidecar's `model`). |

**Transcription:**

| Param | Description |
|-------|-------------|
| `live_events` | Emit a callback per utterance the recognizer produces. |
| `verbose_utterances` | Include full ASR detail (word timings, alternatives) per utterance. Increases callback size. |
| `speech_engine` | `deepgram` (default) or `google`. Turn-end detection is calibrated for Deepgram. |
| `speech_timeout` | ms the recognizer waits before finalizing speech. |
| `vad_silence_ms` | Silence (ms) used to detect end of speech. |
| `vad_thresh` | Speech-detection sensitivity. |
| `transcribe_prompt` | Bias prompt passed to the ASR for expected terms (distinct from operator `prompt`). |

**Debug:** `debug_level` (speech-engine verbosity, 0–100), `debug` (verbose sidecar logging).

## Prompt Forms

Three forms (markdown-formatted prompts recommended). If both `file` and `pom`/`text` are set, `file` wins.

```yaml
# Text (bare string, or {text: "..."})
prompt: "You are a real-time sales copilot. After each customer turn, give the agent one concise piece of advice, or call sidecar_skip if no advice is needed."

# POM — structured sections rendered to markdown
prompt:
  pom:
    - title: Personality
      body: "You are a real-time sales copilot."
    - title: Instructions
      bullets:
        - "Watch for buying signals."
        - "Call lookup_competitor when a competitor is mentioned."

# File — server-side file path whose contents become the prompt
prompt:
  file: "/path/to/prompt.md"
```

POM sections support `title`, `body`, `bullets`, nested `subsections`, `numbered`, `numberedBullets`.

**Variable expansion** works in any form: `${global_data.*}`, `${ai_agents_global_data.*}`, plus call variables for caller number, destination number, customer leg, local date/time/timezone, and call session ID.

**Always instruct the model to call `sidecar_skip` when there's nothing useful to say** — otherwise it fills silence with low-quality advice.

## SWAIG (Functions and MCP Servers)

```yaml
SWAIG:
  defaults:
    web_hook_url: "https://your-app.example.com/sidecar/swaig"  # basic auth embeddable
    # web_hook_auth_user / web_hook_auth_password also supported
  functions:
    - function: lookup_competitor        # only required field
      description: "Look up a competitor by name."
      parameters:                        # JSON Schema; omit for no-arg functions
        type: object
        properties:
          competitor:
            type: string
            description: "Competitor name."
        required: [competitor]
      # per-function web_hook_url / auth override defaults
  mcp_servers:
    - url: "https://crm.example.com/mcp"
      headers:                           # auth goes in headers; supports variable expansion
        Authorization: "Bearer ${global_data.crm_token}"
      resources: true                    # fetch server resources into global_data
      resource_vars:
        customer_id: "${global_data.customer_id}"
```

**Parameter schema restriction:** each property allows only `type`, `description`, `enum`, `default`. Validation keywords (`pattern`, `minimum`, `maximum`) are rejected — express constraints in the description and validate server-side.

**Reserved name:** `sidecar_skip` is auto-registered as a built-in; do not declare it. When the model calls it, the tick ends silently (no `insight`) and a `skip` callback fires with the model's reason.

MCP server tools are discovered at startup and registered as callable functions alongside your SWAIG functions.

### Tool Webhook Contract

Platform POSTs JSON to the function's `web_hook_url` (smaller field set than the `ai` method's SWAIG webhook; caller details grouped under `channel_data`). Your response:

```json
{
  "response": "ACME charges $99/seat. We're $79.",
  "action": [
    { "user_event": { "topic": "sidecar.alert", "level": "info" } },
    { "set_global_data": { "last_lookup": "ACME" } }
  ]
}
```

- `response` — the tool result the model reads on its next step
- `action` — optional; one action object or array, each keyed by action name

### Supported SWAIG Actions

| Action | Effect |
|--------|--------|
| `user_event` | Emits your topic + payload — the primary way to surface UI alerts and intent navigation. |
| `set_global_data` / `unset_global_data` | Merge into / remove from `global_data`. Fires `global_data_change`; persists across sessions on the leg. |
| `set_session_metadata` / `unset_session_metadata` | Session metadata changes. |
| `transfer` | Transfer call to phone number, SIP URI, or SWML URL. Ends sidecar and transcription. Optional summary on transfer. |
| `hangup` | Terminate the call. Ends sidecar and transcription. |
| `stop` | Stop the sidecar only; transcription continues. |
| `say` / TTS | Report-only — sidecar has no voice. Fires an `action` callback with `spoken: false`, `reason: "no_tts_in_sidecar"`. |
| `toggle_functions` | Enable/disable functions mid-conversation (`function` name + active state). |
| `set_model` | Change model settings. Gated by `swaig_allow_settings`. |
| `SWML` | Run a SWML document on the call. Gated by `swaig_allow_swml`; `transfer: true` variant ends the sidecar. |
| `inject_message` | Inject a message and trigger a new evaluation — send the sidecar a question/instruction mid-call. |
| `tool_chaining_control` | `true` or `"forever"` — whether/how the model may chain tool calls. |
| `webhook_detail` | Control webhook payload verbosity. |

With `act_on_channel: false`, all actions are report-only.

## Callbacks

Two delivery paths, same payload:

- **Relay topic `calling.ai.sidecar`** — always fires (consume via RELAY or browser SDK)
- **Webhook** — only when `url` is set; HTTP POST with the event wrapped under `sidecar_event`

```json
{
  "call_info": {
    "project_id": "...", "space_id": "...", "call_id": "...",
    "content_type": "text/json", "content_disposition": "post_data",
    "conversation_type": "voice"
  },
  "sidecar_event": {
    "type": "insight",
    "ts": 1745870400123456,
    "tick_id": 7,
    "channel_data": { },
    "raw": "Confirm the customer's address.",
    "iter": 0,
    "total_iters": 1
  }
}
```

Unwrap `sidecar_event` before reading `type`. Every callback carries `type`, `ts` (microsecond timestamp), `tick_id`, and `channel_data` (`call_id` plus `caller_id_name`/`caller_id_number`/`destination_number` when available).

### Callback Types

| `type` | When | Key fields |
|--------|------|-----------|
| `start` | Sidecar attached | `model`, `tools`, `global_data` |
| `turn` | Customer finished a turn (evaluation about to run) | `transcript_delta`, `customer_text`, `agent_text` |
| `request` | Sidecar called the model | `model`, `iter`, `messages_count`, `messages_token_count`, `tool_choice` |
| `thought` | Model produced text while still working | `text`, `iter` |
| `insight` | The advice for the agent | `raw` (advice text), `iter`, `total_iters` |
| `skip` | Model called `sidecar_skip` | `reason?` |
| `tool_call` | Model called a tool | `name`, `arguments?`, `iter` |
| `tool_result` | Tool returned | `name`, `response`, `iter` |
| `action` | SWAIG action returned (and executed if enabled) | `action`, `source_function?`, `executed` |
| `global_data_change` | Global data changed | `key`, `old_value?`, `new_value?` |
| `history_pruned` | History trimmed to token budget | `dropped_count`, `kept_count`, `tokens_before`, `tokens_after` |
| `error` | Failure or anti-loop guard | `error_reason`, `detail?` |
| `ask_request` | An `ai_sidecar.ask` call command was queued | `question`, `ask_id` |
| `ask_answer` | Answer to an `ai_sidecar.ask` | `raw`, `iter`, `total_iters`, `ask_id`, `triggered_by` |
| `stop` | Sidecar shutting down | `stop_reason` |
| `final` | Last callback — full session snapshot | `stop_reason`, `summary?`, `history`, `transcript?`, `event_log`, `stats`, `metrics`, `global_data`, `model`, `started_at`, `ended_at`, `duration_ms` |

Within one evaluation (`request`/`thought`/`tool_call`/`tool_result`/`insight`), `iter` counts steps from 0; `total_iters` on the `insight` is the total. Callbacks produced while answering an `ai_sidecar.ask` (REST call command) also carry that `ask_id` and `triggered_by: "ask"`.

### Stop Reasons (`final.stop_reason`)

`transcribe_close` (call ended normally) | `transferred` | `hung_up` | `stop_action` (SWAIG stop; transcription continues) | `api_stop` (stopped programmatically)

### Error Reasons

| `error_reason` | Trigger |
|----------------|---------|
| `tool_loop` | Anti-loop guard: >4 tool calls in a tick, repeated identical calls, or unregistered tool. Sidecar stops calling tools for that tick. |
| `swml_not_allowed` | SWML action requested but `swaig_allow_swml` is false |
| `llm_error` | Model error; `detail` carries provider message |
| `webhook_http_failure` | Tool webhook failed; carries `function`, `http_code`, `curl_code` |
| `event_log_truncated` | Event log hit size limit; older entries dropped |

## Complete Example

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - ai_sidecar:
        prompt: "You are a real-time sales copilot. After each customer turn, give the agent one concise piece of advice or call sidecar_skip if no advice is needed."
        lang: "en-US"
        url: "https://your-app.example.com/sidecar/events"
        hints: ["ACME", "Globex", "FedRAMP", "SOC 2"]
        SWAIG:
          defaults:
            web_hook_url: "https://your-app.example.com/sidecar/swaig"
          functions:
            - function: lookup_account
              description: "Look up an account record."
              parameters:
                type: object
                properties:
                  customer_id:
                    type: string
                required:
                  - customer_id
    - connect:
        from: "+15555550100"
        to: "+15555550199"
        answer_on_bridge: true
    - hangup: {}
```

## Limitations

- One transcriber per call — cannot run with `live_transcribe`
- Both legs required — single-leg `direction` rejected
- Turn detection calibrated for Deepgram (the default engine)
- No voice on the call — `say` reports as a callback instead of speaking
- Stops when the call ends (fires `final` first)
- `sidecar_skip` name reserved
- Tool loops capped (see `tool_loop` error)

## Best Practices

- **Set a prompt** — the default is minimal. Tell the model exactly when to advise and when to `sidecar_skip`.
- **Use `hints`** for product names, competitors, jargon, and SWAIG enum values — ASR accuracy directly drives advice quality.
- **Prefer relay for UIs** — the relay topic always fires; add a webhook `url` only if a server needs the events.
- **Report-only rollout** — start with `params.act_on_channel: false` so transfers/hangups are visible as callbacks without affecting live calls, then enable.
- **Tune reaction** — lower `idle_timeout_ms` for snappier advice; raise `min_interval_ms` on chatty calls to control model costs.
- **Mid-call control** — use the `ai_sidecar.ask` REST call command to ask the sidecar questions, or the `inject_message` action to steer it.
