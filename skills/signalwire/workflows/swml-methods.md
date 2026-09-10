# SWML Method Reference

SWML (SignalWire Markup Language) is a YAML/JSON document format for scripting calls and messages. A document declares `version: 1.0.0` and a `sections` map whose `main` section runs first; each section is an array of method statements executed in order. SWML comes in two flavors: **Calling** documents (voice calls — the full method set below) and **Messaging** documents (inbound SMS/MMS handling — a smaller method set, see [Messaging SWML](#messaging-swml)). This file is a reference for the methods not covered in depth by other workflow docs; the index links each method to where it's documented.

## Method Index (Calling)

| Method | Purpose | Documented in |
|--------|---------|---------------|
| `ai` | Conversational AI agent that speaks with the caller | [voice-ai.md](voice-ai.md) |
| `ai_sidecar` | Real-time AI observer that coaches a human agent via callbacks | [ai-sidecar.md](ai-sidecar.md) |
| `amazon_bedrock` | Amazon Bedrock voice agent interaction | [below](#amazon-bedrock) |
| `answer` | Answer an inbound call | [call-control.md](call-control.md), [inbound-call-handling.md](inbound-call-handling.md) |
| `cond` | Branch on JavaScript conditions | [below](#cond) |
| `connect` | Dial a destination (phone/SIP/stream) and bridge it to the call | [call-control.md](call-control.md), [outbound-calling.md](outbound-calling.md) |
| `denoise` | Start noise reduction | [below](#denoise--stop_denoise) |
| `detect_machine` | Answering machine (AMD) + fax detection | [below](#detect_machine) |
| `enter_queue` | Place the call in a named queue | [below](#enter_queue) |
| `execute` | Call a section or URL as a subroutine | [inbound-call-handling.md](inbound-call-handling.md) |
| `goto` | Jump to a label in the current section | [below](#goto--label) |
| `hangup` | End the call | [call-control.md](call-control.md) |
| `join_conference` | Join an ad-hoc audio conference | [below](#join_conference) |
| `join_room` | Join a RELAY video room session | [below](#join_room) |
| `label` | Mark a jump target for `goto` | [below](#goto--label) |
| `live_transcribe` | Real-time transcription to a webhook | [below](#live_transcribe) |
| `live_translate` | Real-time translation with TTS playback | [below](#live_translate) |
| `pay` | Secure payment collection via DTMF | [below](#pay) |
| `play` | Play audio, TTS, silence, or ringtone | [call-control.md](call-control.md) |
| `prompt` | Play audio and collect digits/speech | [call-control.md](call-control.md), [inbound-call-handling.md](inbound-call-handling.md) |
| `receive_fax` | Receive a fax on this call | [below](#receive_fax) |
| `record` | Foreground recording (blocks until done) | [call-control.md](call-control.md) |
| `record_call` | Background call recording | [inbound-call-handling.md](inbound-call-handling.md), [call-control.md](call-control.md) |
| `request` | Send an HTTP request, optionally save the response as variables | [below](#request) |
| `return` | Return from `execute` or exit the script | [below](#return) |
| `send_digits` | Send DTMF tones | [below](#send_digits) |
| `send_fax` | Send a PDF as a fax | [below](#send_fax) |
| `send_sms` | Send an SMS from the call | [outbound-calling.md](outbound-calling.md) |
| `set` | Set script variables | [inbound-call-handling.md](inbound-call-handling.md), [call-control.md](call-control.md) |
| `sip_refer` | Send a SIP REFER to a SIP call | [below](#sip_refer) |
| `sleep` | Pause execution | [outbound-calling.md](outbound-calling.md) |
| `stop_denoise` | Stop noise reduction | [below](#denoise--stop_denoise) |
| `stop_record_call` | Stop a background recording | [below](#stop_record_call) |
| `stop_stream` | Stop a WebSocket audio stream | [below](#stream--stop_stream) |
| `stop_tap` | Stop a media tap | [below](#tap--stop_tap) |
| `stream` | Stream call audio to a WebSocket endpoint | [below](#stream--stop_stream) |
| `switch` | Branch on a variable's value | [inbound-call-handling.md](inbound-call-handling.md) |
| `tap` | Tap call media to a WebSocket or RTP destination | [below](#tap--stop_tap) |
| `transcribe` | Whole-call background transcription, delivered at call end | [below](#transcribe--transcribe_stop) |
| `transcribe_stop` | Stop a background transcription early | [below](#transcribe--transcribe_stop) |
| `transfer` | Transfer execution to a section, URL, or relay context | [call-control.md](call-control.md) |
| `unset` | Unset variables | [below](#unset) |
| `user_event` | Send a custom event to the connected client | [below](#user_event) |

Docs URL pattern: `https://signalwire.com/docs/swml/reference/calling/<method-slug>` (slug uses hyphens, e.g. `detect-machine`).

## Call Analysis

### detect_machine

Detect whether the far end is a `machine` (fax, voicemail) or a `human`, combining AMD and fax detection. Events go to `status_url` as POSTs (`event_type: calling.call.detect`); the current/final result also lands in `${detect_result}`.

Docs: https://signalwire.com/docs/swml/reference/calling/detect-machine

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `detect_message_end` | boolean, `false` | If `true`, stop detection on beep / end of voicemail greeting |
| `detectors` | string, `amd,fax` | Comma-separated detectors to enable (`amd`, `fax`) |
| `end_silence_timeout` | number, `1.0` | Seconds to wait for voice activity to finish |
| `initial_timeout` | number, `4.5` | Seconds to wait for initial voice activity before giving up |
| `machine_ready_timeout` | number, = `end_silence_timeout` | Seconds of finished voice before firing the READY event |
| `machine_voice_threshold` | number, `1.25` | Seconds of ongoing voice required to classify as MACHINE |
| `machine_words_threshold` | integer, `6` | Min words in one utterance to classify as MACHINE |
| `status_url` | string | HTTP(S) URL for detector events |
| `timeout` | number, `30.0` | Max seconds to run the detector |
| `tone` | `CED` (default) or `CNG` | Fax tone to detect (remote side only) |
| `wait` | boolean, `true` | If `false`, run async (`status_url` required); if `true`, block until detection completes |

**Variables set:** `detect_result` (`machine` \| `human` \| `fax` \| `unknown` \| `detecting` \| `error` — lifecycle events `READY`/`NOT_READY`/`finished` appear only in callbacks, never in this variable), `detect_machine_beep` (`true` if a beep was detected), `detect_ms` (detection time in ms).

```yaml
version: 1.0.0
sections:
  main:
    - detect_machine:
        detectors: "amd,fax"
        wait: true
    - cond:
        - when: detect_result == 'machine'
          then:
            - play: { url: "say: Voicemail detected, goodbye." }
            - hangup: {}
        - else:
            - play: { url: "say: Result was ${detect_result}" }
```

## Queuing

### enter_queue

Place the call in a named queue (auto-created if missing). Callers hear hold music while waiting; an agent connects to the queue with `connect`, bridging caller and agent. After the bridge ends, execution continues with the SWML in `transfer_after_bridge`.

Docs: https://signalwire.com/docs/swml/reference/calling/enter-queue

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `queue_name` | string, required | Queue to enter; auto-created if it doesn't exist |
| `transfer_after_bridge` | string, required | SWML to run after the bridge completes — a URL returning SWML, or an inline SWML document (JSON string) |
| `status_url` | string | HTTP(S) URL for queue status events (`calling.call.queue` with `status`: `enqueue`, `leave`, `dequeue`) |
| `wait_url` | string | URL of hold media (WAV, MP3, AIFF, GSM, μ-law), fetched via GET. Default hold music if unset |
| `wait_time` | integer, `3600` | Max seconds to wait in the queue before timeout |

**Variables set:** `queue_result` (`entering` \| `connecting` \| `connected` \| `leaving` \| `timeout` \| `hangup` \| `failed`), `wait_time` (seconds waited, `-1` if unavailable), `entry_position`, `entry_size` (position/queue size on entry, `-1` if unavailable).

```yaml
version: 1.0.0
sections:
  main:
    - enter_queue:
        queue_name: "sales_queue"
        status_url: "https://example.com/queue-status"
        wait_time: 1800
        transfer_after_bridge: "https://example.com/post-call-swml"
```

## Conferencing

### join_conference

Join an ad-hoc audio conference shared with RELAY and CXML calls.

Docs: https://signalwire.com/docs/swml/reference/calling/join-conference

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `name` | string, required | Conference name |
| `muted` | boolean, `false` | Join muted |
| `beep` | string, `true` | Join/leave beep: `true`, `false`, `onEnter`, `onExit` |
| `start_on_enter` | boolean, `true` | Start the conference when this participant joins |
| `end_on_exit` | boolean, `false` | End the conference when this participant leaves |
| `wait_url` | string | URL fetched (POST, document-fetching webhook body) for SWML to play while waiting for the conference to start. Default hold music if unset |
| `max_participants` | integer, `100000` | Participant cap |
| `record` | string, `do-not-record` | `do-not-record` or `record-from-start` |
| `region` | string | Hosting region: `global`, `us`, `eu`, `ch` |
| `trim` | string, `trim-silence` | `trim-silence` removes leading silence from the recording; `do-not-trim` keeps it |
| `coach` | string | Call SID of an in-progress conference participant to coach |
| `status_callback_event` | string | Space-separated events to report: `start`, `end`, `join`, `leave`, `mute`, `hold`, `modify`, `speaker`, `announcement` |
| `status_callback_event_type` | string | Callback content type: `cxml`, `laml`, `relay` |
| `status_callback` | string | URL for status events |
| `status_callback_method` | string, `POST` | `GET` or `POST` |
| `recording_status_callback` | string | URL for recording status events |
| `recording_status_callback_method` | string, `POST` | `GET` or `POST` |
| `recording_status_callback_event` | string | `in-progress`, `completed`, `absent` |
| `recording_status_callback_event_type` | string | `cxml`, `laml`, `relay` |
| `result` | object | Custom action on conference result — a `switch` object or `cond` array |
| `stream` | object | Attach a bidirectional WebSocket stream to the conference (below) |

`stream` sub-object: `url` (required, `wss://` only), `name`, `codec` (`PCMU`, `PCMA`, `G722`, `L16`, with optional rate/ptime modifiers like `L16@24000h@40i`), `status_url`, `status_url_method` (`POST` default), `realtime` (boolean, `false` — enables audio back into the conference), `authorization_bearer_token`, `custom_parameters` (key-value pairs delivered on connect).

**Variables set:** `join_conference_result` (`completed` \| `answered` \| `no-answer` \| `failed` \| `canceled`), `return_value` (same value).

Status callbacks POST `calling.conference` events; `params.status` identifies the event (`conference-start`, `conference-end`, `participant-join`, `participant-leave`, `participant-mute`/`unmute`, `participant-hold`/`unhold`, `participant-speech-start`/`stop`, `participant-modify`, `record-start`/`pause`/`resume`/`stop`). `conference-end` and `record-stop` include `recording_url`, `recording_duration`, `recording_file_size` when a recording exists.

```yaml
version: 1.0.0
sections:
  main:
    - join_conference:
        name: "team_meeting"
        beep: "onEnter"
        max_participants: 10
        record: "record-from-start"
        stream:
          url: "wss://example.com/conference-audio"
          codec: "PCMU"
          realtime: true
```

### join_room

Join a RELAY video room session; creates the room if it doesn't exist.

Docs: https://signalwire.com/docs/swml/reference/calling/join-room

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `name` | string, required | Room name. Allowed characters: `A-Z a-z 0-9 _ -` |

**Variables set:** `join_room_result` (`joined` \| `failed`).

```yaml
version: 1.0.0
sections:
  main:
    - join_room:
        name: my_room
```

## Transcription & Translation

### live_transcribe

Real-time transcription of the call, delivered to a webhook as it happens. Controlled by a single `action` property: a `start` object, the string `stop`, or a `summarize` object. `stop` and `summarize` are for active calls (via the Call Commands REST API, or SWML run by `transfer`/`execute` mid-call).

Docs: https://signalwire.com/docs/swml/reference/calling/live-transcribe

`action.start` properties:

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `webhook` | string | URL receiving transcription events via POST. Basic auth embeddable: `username:password@url` |
| `lang` | string, required | Language to transcribe |
| `live_events` | boolean, `false` | Send partial results as they occur |
| `ai_summary` | boolean, `false` | Send an AI summary to the webhook when the session ends |
| `speech_timeout` | integer, `60000` | Speech recognition timeout (ms), min 1500 |
| `vad_silence_ms` | integer, `300` (Deepgram) / `500` (Google) | VAD silence time (ms) |
| `vad_thresh` | integer, `400` | VAD threshold, range 0–1800 |
| `debug_level` | integer, `0` | Logging verbosity |
| `direction` | array, required | Legs to transcribe: `remote-caller`, `local-caller` |
| `speech_engine` | string, `deepgram` | `deepgram` or `google` |
| `ai_summary_prompt` | string | Prompt guiding the end-of-session summary |

`action: stop` ends the session. `action.summarize` (`webhook`, `prompt`; both optional) requests an on-demand summary mid-session — versus `ai_summary: true`, which summarizes automatically at session end.

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - live_transcribe:
        action:
          start:
            webhook: 'https://example.com/webhook'
            lang: en
            live_events: true
            direction: [remote-caller, local-caller]
            speech_engine: deepgram
```

Note: `live_transcribe` cannot run alongside `ai_sidecar` — one transcriber per call.

### live_translate

Real-time translation of the call, spoken back via TTS and delivered to a webhook. Same `action` pattern as `live_transcribe` (`start` / `stop` / `summarize`), plus an `inject` action.

Docs: https://signalwire.com/docs/swml/reference/calling/live-translate

`action.start` — everything in `live_transcribe`'s start table (minus `lang`), plus:

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `from_lang` | string, required | Language to translate from |
| `to_lang` | string, required | Language to translate to |
| `from_voice` | string, `elevenlabs.josh` | TTS voice for the source language |
| `to_voice` | string, `elevenlabs.josh` | TTS voice for the target language |
| `filter_from` | string | Tone/style filter for the source direction: `polite`, `rude`, `professional`, `shakespeare`, `gen-z`, or custom via `prompt:` prefix (e.g. `prompt:Use formal business language`) |
| `filter_to` | string | Same, for the target direction |

`action.inject` (`message`, `direction`: `remote-caller`/`local-caller`) inserts a message into the conversation, translated and spoken to the specified party — mid-call only.

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - live_translate:
        action:
          start:
            webhook: 'https://example.com/webhook'
            from_lang: en-US
            to_lang: es-ES
            live_events: true
            direction: [remote-caller, local-caller]
```

### transcribe / transcribe_stop

`transcribe` transcribes the entire call in the background: execution continues immediately, and the transcript is delivered when the call ends. Only one transcription can be active on a call at a time. For real-time delivery use `live_transcribe` instead.

Docs: https://signalwire.com/docs/swml/reference/calling/transcribe and `/transcribe-stop`

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `status_url` | string | URL receiving the transcript when the call ends: `calling.transcript.completed` (with `text`) or `calling.transcript.failed` |

**Variables set:** `transcribe_result` (`success` \| `failed` — whether it started), `transcribe_control_id`.

`transcribe_stop` (no parameters) stops the active background transcription early and sets a success/failure result variable.

```yaml
version: 1.0.0
sections:
  main:
    - transcribe:
        status_url: https://example.com/transcribe-status
    # ... later, to end it early:
    - transcribe_stop: {}
```

## Audio Processing

### denoise / stop_denoise

`denoise` (no parameters) starts noise reduction on the call; `stop_denoise` (no parameters) stops it.

Docs: https://signalwire.com/docs/swml/reference/calling/denoise and `/stop-denoise`

**Variables set:** `denoise_result` — `on` \| `failed` after `denoise`, `off` after `stop_denoise`.

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - denoise: {}
    - play: { url: 'say: Denoising ${denoise_result}' }
    - stop_denoise: {}
```

## Media Streaming & Taps

### stream / stop_stream

`stream` streams call audio to a WebSocket endpoint in the background; execution continues immediately. Runs until `stop_stream` or call end. Multiple simultaneous streams are allowed — give each its own `control_id`.

Docs: https://signalwire.com/docs/swml/reference/calling/stream and `/stop-stream`

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `url` | string, required | Secure WebSocket URI (`wss://`) |
| `control_id` | string, auto-generated | Identifier for this stream (used by `stop_stream`); must be unique among active streams |
| `name` | string | Friendly name, included in status events |
| `track` | string, `inbound_track` | `inbound_track` (what the caller says), `outbound_track` (what the caller hears), `both_tracks` |
| `codec` | string | Freeform, endpoint-specific; common: `PCMU`, `PCMA`, `OPUS` |
| `status_url` | string | URL for `calling.call.stream` status events (`params.state`: `streaming`, `finished`) |
| `status_url_method` | string, `POST` | `GET` or `POST` |
| `authorization_bearer_token` | string | Bearer token sent in the `Authorization` header on WebSocket connect |
| `custom_parameters` | object | Key-value pairs included in the first WebSocket message |

**Variables set:** `stream_result` (`success` \| `failed`), `stream_control_id`.

`stop_stream` takes an optional `control_id` (default: stops the most recently started stream, read from `stream_control_id`) and sets `stop_stream_result` (`success` \| `failed`).

```yaml
version: 1.0.0
sections:
  main:
    - stream:
        url: wss://example.com/audio-stream
        name: live-transcription
        track: both_tracks
        custom_parameters:
          customer_tier: gold
    # ...
    - stop_stream: {}
```

**`stream` is one-way.** Audio leaves the call and nothing comes back. For a bidirectional media stream — the equivalent of Twilio's bidirectional Media Streams — use `connect` with a `stream:` destination instead:

```yaml
- connect:
    to: "stream:wss://example.com/audio"
    codec: PCMU          # PCMU (default), PCMA, G722, L16
    realtime: true       # defaults to false — this is what makes it bidirectional
    authorization_bearer_token: my-token
    custom_parameters:
      user_id: "12345"
```

That form makes the WebSocket a call leg, so audio flows both ways. Shipped January 2026, in both SWML and Relay. **Note `realtime` defaults to `false`** — omitting it gives you a stream leg that does not carry audio back.

Choosing between them: use `stream` to observe (transcription, compliance capture, analytics) while the call continues its SWML; use `connect: stream:` when the far end is a participant that needs to talk back (a voice bot, a translation bridge).

**Concurrency limits** *(not on the docs site)*:

- Reusing a `control_id` that is already active on the call fails with `Duplicate control_id`.
- A **per-call cap on concurrent control-based operations, default 10**, is shared across *all* of them — streams, taps, transcriptions, recordings, detectors. Exceeding it fails with `Too many concurrent operations`. A call already running a recording and two taps has fewer stream slots than you would expect from reading about streams alone.

**Relay form** — the same operation over the [calling commands endpoint](fabric-relay.md#calling-commands-over-http):

```json
{ "command": "calling.stream", "id": "<call-uuid>",
  "params": { "control_id": "stream-control-1", "url": "wss://example.com/stream", "track": "inbound_track" } }

{ "command": "calling.stream.stop", "id": "<call-uuid>",
  "params": { "control_id": "stream-control-1" } }
```

### tap / stop_tap

`tap` starts a background media tap, streaming call audio over WebSocket or RTP to a URI you control.

Docs: https://signalwire.com/docs/swml/reference/calling/tap and `/stop-tap`

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `uri` | string, required | Tap destination: `rtp://IP:port`, `ws://example.com`, or `wss://example.com` |
| `control_id` | string, auto-generated | Identifier for this tap (used by `stop_tap`) |
| `direction` | string, `speak` | `speak` (what the party says), `listen` (what the party hears), `both` |
| `codec` | string, `PCMU` | `PCMU` or `PCMA` |
| `rtp_ptime` | integer, `20` | Packetization time (ms) for `rtp://` URIs |
| `status_url` | string | URL for `calling.call.tap` status events (`params.state`: `tapping`, `finished`) |

**Variables set:** `tap_uri`, `tap_result` (`success` \| `failed`), `tap_control_id`, `tap_rtp_src_addr`, `tap_rtp_src_port` (RTP only), `tap_ptime`, `tap_codec`, `tap_rate`.

`stop_tap` takes an optional `control_id` (default: last tap started, read from `tap_control_id`) and sets `stop_tap_result`.

```yaml
version: 1.0.0
sections:
  main:
    - tap:
        uri: wss://example.com/tap
    # ...
    - stop_tap: {}
```

### stop_record_call

Stop an active background recording started with `record_call`.

Docs: https://signalwire.com/docs/swml/reference/calling/stop-record-call

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `control_id` | string, default: last recording started | Identifier of the recording to stop (reads `record_control_id` when omitted) |

**Variables set:** `stop_record_call_result` (`success` \| `failed`).

```yaml
- stop_record_call:
    control_id: my-recording-id
```

## Fax

### send_fax

Send a PDF as a fax.

Docs: https://signalwire.com/docs/swml/reference/calling/send-fax

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `document` | string, required | URL of the PDF to fax |
| `header_info` | string | Text added to the fax header |
| `identity` | string, default: caller ID number | Station identity to report |
| `status_url` | string | URL for `calling.call.fax` status events (`finished` result plus per-`page` progress events) |

**Variables set:** `send_fax_document`, `send_fax_identity`, `send_fax_remote_identity`, `send_fax_pages`, `send_fax_result_code`, `send_fax_result_text`, `send_fax_result` (`success` \| `failed`).

```yaml
version: 1.0.0
sections:
  main:
    - send_fax:
        document: https://example.com/fax_to_send.pdf
    - execute:
        dest: 'https://example.com/handle_outgoing_fax_result'
```

### receive_fax

Receive a fax being delivered to this call.

Docs: https://signalwire.com/docs/swml/reference/calling/receive-fax

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `status_url` | string | URL for `calling.call.fax` status events (same shape as `send_fax`, direction `receive`) |

**Variables set:** `receive_fax_document` (URL of the received document), `receive_fax_identity`, `receive_fax_remote_identity`, `receive_fax_pages`, `receive_fax_result_code`, `receive_fax_result_text`, `receive_fax_result` (`success` \| `failed`).

```yaml
version: 1.0.0
sections:
  main:
    - receive_fax: {}
    - execute:
        dest: 'https://example.com/handle-fax'  # POSTed with receive_fax_* vars set
```

## SIP

### sip_refer

Send a SIP REFER to a SIP call, asking the recipient to INVITE another SIP URI.

Docs: https://signalwire.com/docs/swml/reference/calling/sip-refer

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `to_uri` | string, required | SIP URI to REFER to |
| `status_url` | string | URL for `calling.call.refer` status events |
| `username` | string | SIP authentication username |
| `password` | string | SIP authentication password |

**Variables set:** `sip_refer_to` (the URI the recipient is to INVITE), `sip_refer_result` (overall result), `return_value` (same value), `sip_refer_response_code` (response to the REFER request), `sip_refer_to_response_code` (INVITE response to the recipient).

```yaml
version: 1.0.0
sections:
  main:
    - sip_refer:
        to_uri: 'sip:alice@example.com'
    - play:
        url: 'say: The SIP refer result is ${sip_refer_result}'
```

## Payments

### pay

Secure payment processing during a call: collects card details from the caller via DTMF, then POSTs them to a `payment_connector_url` you host. Your server charges the card through your processor (Stripe, Braintree, etc.) and returns the result. A positive `charge_amount` runs a **charge**; `charge_amount: "0"` (or omitted) runs **tokenization**, returning a stored-payment token instead.

Docs: https://signalwire.com/docs/swml/reference/calling/pay

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `payment_connector_url` | string, required | URL POSTed with the gathered payment details; must return the transaction result |
| `charge_amount` | string | Amount to charge (float as string, no currency prefix). `0`/omitted = tokenization |
| `currency` | string, `usd` | ISO 4217 currency code |
| `description` | string | Custom payment description passed in the request |
| `input` | string, `dtmf` | Collection method (`dtmf` only). While entering, `#` submits immediately, `*` cancels |
| `language` | string, `en-US` | Prompt language |
| `max_attempts` | integer, `1` | Retries for collecting payment details |
| `min_postal_code_length` | integer, `0` | Minimum postal code length |
| `parameters` | array of `{name, value}` | Custom key-value parameters forwarded to your processor |
| `payment_method` | string | `credit-card` only |
| `postal_code` | boolean\|string, `true` | Prompt for postal code, or supply a known postcode |
| `prompts` | array | Custom prompts per step (below); defaults used for omitted steps |
| `security_code` | boolean, `true` | Whether to prompt for the CVV |
| `status_url` | string | URL POSTed on each status change (`calling.call.pay`) |
| `timeout` | integer, `5` | Seconds to wait for the next digit before validating |
| `token_type` | string, `reusable` | `one-time` or `reusable` |
| `valid_card_types` | string, `visa mastercard amex` | Space-separated allowed card types (`visa`, `mastercard`, `amex`, `maestro`, `discover`, `jcb`, `diners-club`) |
| `voice` | string, `woman` | TTS voice for prompts |

Each `prompts[]` entry: `for` (step: `payment-card-number`, `expiration-date`, `security-code`, `postal-code`, `payment-processing`, `payment-completed`, `payment-failed`, `payment-canceled`), `actions` (array of `{type: Say|Play, phrase}`), plus optional `attempts`, `card_type`, and `error_type` filters (error types include `timeout`, `invalid-card-number`, `invalid-date`, `invalid-security-code`, `card-declined`, etc.).

**Connector contract:** SignalWire POSTs `transaction_id`, `method`, `cardnumber`, `cvv`, `expiry_month`, `expiry_year`, `postal_code`, `chargeAmount`, `currency_code`, `token_type`, `description`. Respond `200` with `{"charge_id": "...", "error_code": null, "error_message": null}` (charge) or `{"token_id": "...", ...}` (tokenization); non-200 with `error_code`/`error_message` set triggers the `payment-failed` prompt.

**Variables set:** `pay_result` (`success` \| `too-many-failed-attempts` \| `payment-connector-error` \| `caller-interrupted-with-star` \| `relay-pay-stop` \| `caller-hung-up` \| `validation-error` \| `internal-error`) and `pay_payment_results` — nested object with `payment_token`, `payment_confirmation_code`, `payment_card_number` (redacted), `payment_card_type`, `payment_card_expiration_date`, `payment_card_security_code` (redacted), `payment_card_postal_code`, `payment_error`, `payment_error_code`, and `connector_error.{code,message}`. Access with dot notation: `${pay_payment_results.payment_token}`.

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - pay:
        charge_amount: '25.00'
        payment_connector_url: "https://example.com/process"
        max_attempts: 3
    - cond:
        - when: "pay_result == 'success'"
          then:
            - play:
                url: 'say: Confirmation code ${pay_payment_results.payment_confirmation_code}.'
        - else:
            - play: { url: 'say: Payment was not completed.' }
```

## DTMF

### send_digits

Send digit presses as DTMF tones.

Docs: https://signalwire.com/docs/swml/reference/calling/send-digits

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `digits` | string, required | Digits to send. Valid: `0123456789*#ABCDWw` — `W` is a 1 s delay, `w` is a 500 ms delay |

**Variables set:** `send_digits_result` (`success` \| `failed`).

```yaml
- send_digits:
    digits: 'Ww1234#'
```

## Events

### user_event

Send custom events to the connected client on the call (commonly consumed by the Browser SDK, which receives them as `user_event` and listens via its `on` method). Useful for triggering client-side UI actions.

Docs: https://signalwire.com/docs/swml/reference/calling/user-event

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `event` | object, required | Any valid JSON object mapping event names to values |

```yaml
version: 1.0.0
sections:
  main:
    - user_event:
        event:
          orderStatus: { count: 42, active: true }
```

## Control Flow

### cond

Execute a sequence of instructions based on JavaScript conditions. Takes an array of `{when, then}` objects, with one optional trailing `{else}`.

Docs: https://signalwire.com/docs/swml/reference/calling/cond

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `when` | string, required | JavaScript condition to evaluate |
| `then` | array, required | SWML methods to run when the condition is `true` |
| `else` | array | SWML methods to run when no `when` matched |

**Warning:** the `when` string already has direct access to all document variables as JavaScript. Do **not** use the `${...}` substitution operator inside it — that can produce inconsistent behavior:

```
❌ when: "${call.type.toLowerCase() == 'sip'}"
❌ when: "${prompt_value} == 1"
✅ when: "call.type.toLowerCase() == 'sip'"
✅ when: "prompt_value == 1"
```

```yaml
version: 1.0.0
sections:
  main:
    - cond:
        - when: call.type.toLowerCase() == 'sip'
          then:
            - play: { url: "say: You're calling from SIP." }
        - when: call.type.toLowerCase() == 'phone'
          then:
            - play: { url: "say: You're calling from a phone." }
        - else:
            - hangup: {}
```

### goto / label

`label` marks a point in a section (`- label: foo`); `goto` jumps to a label **within the same section**, optionally gated by a condition and always capped by `max`.

Docs: https://signalwire.com/docs/swml/reference/calling/goto and `/label`

| Property (`goto`) | Type / Default | Description |
|-------------------|----------------|-------------|
| `label` | string, required | Label in the current section to jump to |
| `when` | string | JavaScript condition; jump only if `true`. Omitted = unconditional |
| `max` | integer, `100` | Max number of jumps (1–100) |

**Retry-cap pattern:** the `max` property is the built-in loop limiter — with `max: 3` the labeled block runs 4 times total (1 initial pass + 3 jumps), then execution falls through. Combine with `when` for a conditional retry loop:

```yaml
version: 1.0.0
sections:
  main:
    - label: menu
    - prompt:
        play: 'say: Press 1 to continue'
        max_digits: 1
    - goto:
        label: menu
        when: prompt_value !== '1'   # plain JS — no ${}
        max: 3                        # cap retries; falls through after 3 jumps
    - play: { url: 'say: Continuing.' }
```

### request

Send a GET, POST, PUT, or DELETE request to a remote URL, optionally saving a parsed JSON response as variables.

Docs: https://signalwire.com/docs/swml/reference/calling/request

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `url` | string, required | Target URL; basic auth embeddable as `username:password@url` |
| `method` | string, required | `GET` \| `POST` \| `PUT` \| `DELETE` |
| `headers` | object | Valid: `Accept`, `Authorization`, `Content-Type`, `Range`, and custom `X-` headers |
| `body` | string \| object | Request body; set `Content-Type` explicitly (else inferred) |
| `connect_timeout` | number, `0` | Max seconds to wait for a connection (0 = none) |
| `timeout` | number, `0` | Max seconds to wait for a response (0 = none) |
| `save_variables` | boolean, `false` | Store parsed JSON response fields as variables |

**Variables set:** `request_url`, `request_result` (`success` \| `failed`), `return_value` (same as result), `request_response_code`, `request_response_headers.<lowercase-name>` (max 64 headers), `request_response_body` (raw, 64 KB limit), and — with `save_variables` — `request_response.<field>` for each JSON field (nested paths work, e.g. `request_response.number.home`).

```yaml
version: 1.0.0
sections:
  main:
    - request:
        url: 'https://api.example.com/todos/1'
        method: GET
        save_variables: true
        timeout: 10
    - play:
        url: 'say: the title is ${request_response.title}'
```

### return

Return from an `execute` subroutine (or exit the script when not in one). The value can be any type and lands in `return_value` in the caller's context; `execute`'s `on_return` runs after the return.

Docs: https://signalwire.com/docs/swml/reference/calling/return

```yaml
version: 1.0.0
sections:
  main:
    - execute:
        dest: fn_that_returns
        on_return:
          - play: { url: 'say: returned ${return_value}' }
  fn_that_returns:
    - return: hello   # or `return: {}` for no value; arrays/objects allowed
```

### unset

Unset variables set by `set` or as a byproduct of other methods (e.g. `record`). Takes a single variable name (string) or an array of names. Referencing an unset variable afterward is an error.

Docs: https://signalwire.com/docs/swml/reference/calling/unset

```yaml
- unset: num_var
# or
- unset:
    - systems
    - name
```

## Amazon Bedrock

### amazon_bedrock

Create an Amazon Bedrock voice agent on the call — the Bedrock counterpart to the `ai` method, with the same overall shape: `prompt` (text or POM, plus tuning params like `temperature`/`top_p` and a Bedrock `voice_id` such as `tiffany`), `post_prompt` and `post_prompt_url` (end-of-session summary callback with the full call log, SWAIG log, and token counts), `SWAIG` (functions, includes, defaults), `params`, and `global_data`.

Docs: https://signalwire.com/docs/swml/reference/calling/amazon-bedrock — for building Bedrock agents with the Agents SDK, see [reference/sdk/bedrock-agent.md](../reference/sdk/bedrock-agent.md).

```yaml
version: 1.0.0
sections:
  main:
    - amazon_bedrock:
        post_prompt_url: https://example.com/my-api
        prompt:
          voice_id: tiffany
          text: |
            You are a helpful assistant. Ask the user for their name,
            then use the appropriate function to answer their question.
        post_prompt:
          text: Summarize the conversation.
        SWAIG:
          defaults:
            web_hook_url: https://example.com/my-webhook
          functions:
            - function: get_weather
              description: Get the current weather for a location.
              parameters:
                type: object
                properties:
                  location: { type: string, description: City name. }
```

## Messaging SWML

The Messaging flavor of SWML handles inbound SMS/MMS. Documents use the same `version`/`sections`/`main` shape, but variables use `%{...}` only, the inbound message is exposed on the `message` scope (`%{message.from}`, `%{message.body}`, `%{message.media[0].url}`), and the method set is:

| Method | Purpose |
|--------|---------|
| `receive` | Accept the inbound message without replying (no-op acknowledgment; no parameters) |
| `reply` | Create and send an outbound message in response (below) |
| `request` | HTTP request to an external URL; failures are soft — they set `request_result` but don't stop execution |
| `transfer` | Tail-call to a new SWML document fetched from a URL (`dest` must be a URL; does not return) |
| `execute` | Call a named section as a subroutine (section names only — no URLs in the messaging context) |
| `return` | Return from a subroutine (value → `return_value`); in `main`, stops execution |
| `goto` | Jump to a `label` in the current section (retry loops; doesn't cross subroutine boundaries) |
| `label` | Mark a jump target; unique within the section |
| `switch` | Branch on a variable's value with optional text transforms — keyword handling |

Docs URL pattern: `https://signalwire.com/docs/swml/reference/messaging/<method>`.

### reply

Sends an outbound message in response to the inbound one. Does **not** end execution — later steps still run after the reply is queued. Accepts three shapes: a bare string (used as the body, sent back to the sender), an object, or an inline `switch`.

Object form:

| Property | Type / Default | Description |
|----------|----------------|-------------|
| `body` | string | Text body. Required when `media` is not set |
| `media` | array | Media URLs to attach (converts to MMS, max 8). Required if no `body` |
| `to` | string | Destination in E.164 format (default: inbound `from`) |
| `from` | string | Sending number/short code — must be owned by your project with messaging capability (default: inbound `to`) |
| `status_url` | string | Delivery status callback URL for the **outbound reply** (fires independently after the document completes) |

Inline `switch` form: `{switch: {variable, transform, case, default}}` — `variable` is a path without the `%{}` wrapper (e.g. `message.body`), `transform` is one of `lowercase`, `uppercase`, `trim`, `lowercase_trim`, `uppercase_trim`, and each `case`/`default` value is either a body string or a full reply object. Don't set `body`/`media`/`to`/`from`/`status_url` alongside an inline `switch` — put them inside the case values. If no case matches and no `default` exists, the step fails and execution stops.

**Variables set:** `reply_result` (`queued` \| `failed`), `reply_message_id` (ID of the outbound message; absent on failure). Both reflect the most recent reply.

### receive

Accepts the inbound message and does nothing else — an explicit no-op. No parameters, no variables.

### Complete example

```yaml
version: 1.0.0
sections:
  main:
    - reply:
        switch:
          variable: message.body
          transform: lowercase_trim
          case:
            help: "Reply STOP to unsubscribe, or visit https://example.com/help."
            stop: "You've been unsubscribed."
            menu:
              body: "Here's our menu."
              media:
                - "https://example.com/menu.pdf"
          default: "Thanks for your message, %{message.from}!"
```

## Variables

Docs: https://signalwire.com/docs/swml/reference/variables

- **Syntax:** wrap a variable path in `${...}` or `%{...}` inside any string value. In **Calling** documents the two are interchangeable; **Messaging** documents accept `%{...}` only. If the placeholder body isn't a plain path (operators, method calls), it's evaluated as a JavaScript expression. Unset-but-valid paths resolve to an empty string.
- **Scopes:** `call` (Calling) / `message` (Messaging) hold the inbound webhook fields (`${call.from}`, `%{message.body}`); `params` holds subroutine/handoff parameters; `vars` holds values you `set` (and method output variables); `envs` (Calling only) holds environment values. Bare output variables like `prompt_value` or `detect_result` are also readable directly.
- **Nested data:** dot notation for objects, zero-based brackets for arrays — `${user.address.city}`, `${employees[0].name}`, `%{message.media[0].url}`.
- **Deployment:** serverless (Dashboard-hosted) documents are substituted at runtime by SignalWire; server-based documents can either return SWML containing placeholders (SignalWire substitutes) or read `call`/`vars`/`envs`/`params` from the webhook POST body and substitute server-side before responding.
- **Not SWML:** mustache-style `{{variable}}` templating is **not** valid SWML syntax — always use `%{...}` or `${...}`.
