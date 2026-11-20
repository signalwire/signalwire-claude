# connect (SWML method)
Source: https://signalwire.com/docs/swml/reference/calling/connect.md

Connects the current call to a phone number, SIP URI, Resource Address, queue, call in progress, or WebSocket stream. `connect` object, required. Shape depends on mode: Single (`to`), `parallel`, `serial`, `serial_parallel`. A stream is a Single `to` with `stream:wss://`.

## Single mode (`connect.to`)

- `to` string, required — single destination; format sets the type:
  - Phone: E.164 with leading `+` (`+15552345678`). Without `+` (`15552345678`): rejected.
  - SIP URI: `sip:` or `sips:` prefix (`sip:alice@example.com`). These prefixes are not case-sensitive.
  - Resource Address: path (`/public/test_room`).
  - Queue: `queue:<name>` (`queue:support`).
  - Call: `call:<call_id>` of a call in progress in the same project; bridges the caller to it. See "Call in progress" below.
  - WebSocket stream: `stream:wss://…` (`stream:wss://example.com/audio`). `stream:ws://` rejected.
  - `queue:`, `call:`, `stream:` prefixes are case-sensitive, must be lowercase.

Top-level properties in Single mode:

- `answer_on_bridge` boolean, default false — delay answer until the B-leg answers.
- `call_state_events` string[], default ['ended'] — allowed event names: `created` | `ringing` | `answered` | `ended`. Each item can also be a SWML variable resolving to one of these.
- `call_state_url` string — webhook for call state changes. Auth allowed as `username:password@url`. Applies only to phone, SIP, Resource Address destinations. When `to` starts with `queue:`, `call:`, or `stream:`, `call_state_url` and `call_state_events` aren't allowed; queue events go to `status_url` of `enter_queue` (https://signalwire.com/docs/swml/reference/calling/enter-queue.md), stream events go to `connect.status_url`.
- `codecs` string | string[], default based on SignalWire settings — comma-separated (`"PCMU,PCMA"`) or array. Supported codecs: `PCMU`, `PCMA`, `OPUS`, `G722`, `G729`, `AMR-WB`, `VP8`, `H264`. No effect on calls to phone numbers.
- `confirm` string | object[] — URL returning SWML, or inline array of SWML methods, run when the call is connected. Only these methods allowed, including inside `cond`/`switch` branches: `cond`, `switch`, `set`, `unset`, `hangup`, `play`, `prompt`, `record`, `record_call`, `stop_record_call`, `tap`, `stop_tap`, `stream`, `stop_stream`, `transcribe`, `transcribe_stop`, `send_digits`, `send_sms`, `denoise`, `stop_denoise`, `user_event`.
- `confirm_timeout` integer, default inherits from `timeout` — seconds allowed for `confirm` SWML to run on the answered destination (URL or inline).
- `encryption` string, default optional — values: `mandatory` | `optional` | `forbidden`.
- `from` string, optional, default calling party's caller ID number — E.164 with leading `+`, SIP URI, or Resource Address; a `queue:`, `call:`, or `stream:` value is rejected.
- `from_name` string — caller ID name (CNAM) shown alongside `from`. SIP calls only; no effect on phone numbers. 1–70 characters after variable expansion: letters, digits, spaces, `_` `.` `-` `+` `,`. Text and variables can combine (`Support ${vars.dept}`).
- `headers` object[] — custom SIP headers added to INVITE. No effect on calls to phone numbers.
  - `headers[].name` string, required — valid SIP header name, 3–256 chars, starting with `X-` or one of `Privacy`, `P-Asserted-Identity`, `User-to-User`. Reserved (can't be set): names starting with `SignalWire`, `X-SignalWire`, `X-CID`, `X-SW-Xregion`. `Privacy` takes effect only with value `id` (hides caller's number).
  - `headers[].value` string, required — can't be empty or contain line breaks.
- `max_duration` integer, default 14400 (4 hours) — max call duration, seconds.
- `password` string — SIP auth password for the outbound leg. SIP URI targets only; ignored for phone, Resource Address, queue, stream.
- `username` string — SIP auth username for the outbound leg. SIP URI targets only; ignored for phone, Resource Address, queue, stream.
- `result` object | object[] — action based on the call result; runs once the peer leg has ended. Source wording: uses `switch` properties (https://signalwire.com/docs/swml/reference/calling/switch.md) "when the `return_value` is a object", `cond` properties (https://signalwire.com/docs/swml/reference/calling/cond.md) "when the `return_value` is an array". See Variables.
- `ringback` boolean | string | string[], default a standard ringback tone — played while phone, SIP, Resource Address destinations ring. A `play` URI or array of `play` URIs; `false` turns off SignalWire's ringback and passes the destination's early media through; `true` keeps the default tone.
- `session_timeout` integer, default based on SignalWire settings — SIP `Session-Expires` in INVITE, seconds. Must be positive, non-zero. 1–15000 take effect; larger is accepted but ignored (default `Session-Expires` used). No effect on calls to phone numbers.
- `status_url` string — HTTP or HTTPS webhook. Phone/SIP/Resource Address destinations: connect operation status (connecting, connected, failed, disconnected), see Connect Status Callbacks. `stream:` destination: stream status, see Stream Status Callbacks; `http://` works here, unlike a stream `status_url` on a destination inside `parallel`/`serial`/`serial_parallel`.
- `status_url_method` string, default POST — values: `GET` | `POST`. Stream destinations only.
- `stop_all_on_reject` boolean | string[], default false — `true`: stop when a destination is busy or declines. Or a non-empty array of reasons: `busy`, `decline`, `noAnswer`. On a matching rejection, destinations ringing alongside it stop ringing; if `connect` then fails with that reason, `result` runs first, then the caller is disconnected.
- `timeout` integer, default 60 — seconds to wait for an answer.
- `execute_after_queue` string — only when `to` starts with `queue:`. URL (http/https) returning SWML, or inline SWML document as a JSON string; runs on this call after its bridge with the queued call ends. Omitted: call hangs up when the bridge ends. Either way the script does not continue past `connect` once a queued call has been bridged. If no queued call is bridged (queue empty or doesn't exist), `connect` fails, `connect_result` = `failed`, and `result` runs.
- `webrtc_media` boolean, default false — offer WebRTC media to the SIP endpoint. No effect on calls to phone numbers.

Stream-specific (only when `to` starts with `stream:wss://`):

- `authorization_bearer_token` string — sent as `Authorization` header in the WebSocket handshake.
- `codec` string, default PCMU — supported values: `PCMU`, `PCMA`, `G722`, `L16`. Rate/ptime modifiers allowed (`PCMU@40i`, `L16@24000h@40i`).
- `custom_parameters` object — key-value pairs sent in the WebSocket start message.
- `name` string — stream name identifier.
- `realtime` boolean, default false — realtime mode for bidirectional audio.

```yaml
- connect:
    to: "sip:alice@example.com"
    from: "+15551112222"
    username: "sipuser"
    password: "s3cret"
```

## Multi-destination modes: `parallel`, `serial`, `serial_parallel`

- `connect.parallel` object[], required — dial all at once; first to answer is bridged, rest cancelled.
- `connect.serial` object[], required — dial in order; if one fails, try the next.
- `connect.serial_parallel` object[][], required — outer array is serial (groups tried in order), inner array is parallel (group dialed simultaneously). If no destination in the current group answers, the next group is tried. In `serial_parallel[][]`, first `[]` = group index, second = destination index.

Rules (all three modes):
- Must contain at least one destination. `serial_parallel`: an empty group is skipped; `connect` fails if every group is empty.
- A `queue:` or `call:` destination can't be combined with any other destination; a `stream:` destination can't be combined with a phone, SIP, Resource Address, or queue destination. `connect` fails in either case. With several `stream:` destinations, only the first is used. For queue, call, or stream, use Single `to`.
- **20-destination limit:** up to 20 destinations are dialed (`parallel`) / tried (`serial`). Any after the 20th never ring and `connect` reports no error. `serial_parallel`: 20 total across all groups, not per group (three groups of eight: groups 1–2 ring fully (16), group 3 rings only its first four, its last four never ring). See "Dial more than 20 destinations".

### Per-destination properties

Identical for `parallel[]`, `serial[]`, and `serial_parallel[][]`:

- `to` string, required — phone (E.164 with `+`), SIP URI (`sip:`/`sips:`), Resource Address, `queue:<name>`, `call:<call_id>`, or `stream:wss://…`. Same format rules as Single `to`.
- `from` string — overrides top-level `from`; same formats.
- `from_name` string — overrides top-level `from_name`. SIP calls only. 1–70 characters after variable expansion: letters, digits, spaces, `_` `.` `-` `+` `,`.
- `username` string — SIP auth username for this destination. SIP URI targets only.
- `password` string — SIP auth password for this destination. SIP URI targets only.
- `timeout` integer, default inherits top-level `timeout`, then 60 — seconds to wait for this destination; overrides top-level.
- `call_state_events` string[], default inherits top-level `call_state_events`, then ['ended'] — overrides top-level. Each item can be a SWML variable resolving to an event name. Not allowed when `to` starts with `queue:`, `call:`, or `stream:`.
- `call_state_url` string — call state webhook for this destination; overrides top-level. Not allowed when `to` starts with `queue:`, `call:`, or `stream:`.
- `confirm` string | object[] — run on this destination when answered; overrides top-level. Inline array limited to the same methods as top-level `confirm`.
- `confirm_timeout` integer — seconds for `confirm` on this destination; overrides top-level `confirm_timeout`. When neither is set, this destination's `timeout` is used.
- `encryption` string — media encryption (SRTP); overrides top-level `encryption` (used when unset). SIP destinations only. Values: `mandatory` | `optional` | `forbidden`.
- `headers` object[] — custom SIP INVITE headers; replaces top-level `headers` for this destination. SIP destinations only. `headers[].name` and `headers[].value` both required, same rules as top-level `headers[]`.
- `codecs` string | string[] — comma-separated or array, same codec names as top-level `codecs`; overrides top-level. SIP destinations only.
- `webrtc_media` boolean — overrides top-level `webrtc_media` (used when unset). SIP destinations only.
- `session_timeout` integer — SIP `Session-Expires` in INVITE for this destination, seconds. Must be positive, non-zero; 1–15000 take effect, larger accepted but ignored (default `Session-Expires` used). Top-level `session_timeout` is not used in these modes; set it on each SIP destination that needs it. SIP destinations only.
- Stream destinations only:
  - `name` string — stream name identifier.
  - `codec` string — same values as single-stream `connect.codec`.
  - `status_url` string — stream status notifications. Must be `https://`; `http://` rejected (unlike top-level `connect.status_url`). See Stream Status Callbacks.
  - `status_url_method` string — values: `GET` | `POST`.
  - `realtime` boolean, default false — realtime bidirectional audio, as single-stream `connect.realtime`.
  - `authorization_bearer_token` string — bearer token for the stream's WebSocket connection.
  - `custom_parameters` object — key-value pairs for the stream; every value must be a string.

### Top-level properties in multi-destination modes

Same as Single mode for `answer_on_bridge`, `call_state_events` (default ['ended']), `codecs`, `confirm`, `confirm_timeout`, `encryption` (default optional), `from`, `from_name`, `headers`, `max_duration` (default 14400), `result`, `ringback`, `stop_all_on_reject` (default false), `timeout` (default 60), `webrtc_media` (default false), with these differences:

- `call_state_url` — applies to every phone, SIP, Resource Address destination; can be overwritten per destination. Doesn't apply to destinations whose `to` starts with `queue:`, `call:`, or `stream:`, and those can't set their own `call_state_url` or `call_state_events`.
- `call_state_events`, `from`, `webrtc_media`, `from_name` — can be overridden per destination.
- `codecs`, `headers` — each SIP destination uses these unless it sets its own.
- `session_timeout` — has no effect in these modes; set it on each SIP destination.
- `status_url` — HTTP or HTTPS; reports the connect operation status (connecting, connected, failed, disconnected). See Connect Status Callbacks.
- Not listed for these modes: top-level `username`, `password`, `execute_after_queue`, `status_url_method`, and the stream-specific properties.

```yaml
- connect:
    from: "+15551112222"
    serial_parallel:
      - - to: "sip:alice@example.com"
          username: "alice_user"
          password: "alice_pw"
        - to: "sip:bob@example.com"
      - - to: "sip:fallback@example.com"
```

`parallel` / `serial` take a flat list: `parallel: [{to: "+15551231234"}, {to: "+15553214321"}]`.

## Variables

Set by the method:
- `connect_result` (out) — `connected` | `failed`.
- `connect_failed_reason` (out) — detailed reason for failure.
- `return_value` (out) — same value as `connect_result`.

Variables belong to one leg, for as long as that leg lasts. A document running on the leg `connect` dialed (e.g. a `confirm` script) starts with an empty `vars` and its own `call` object. On the leg that issued `connect`, every variable survives, and `connect_result` is set when the document resumes. Call legs: https://signalwire.com/docs/platform/voice/call-legs.md

## Status callbacks are advisory

Asynchronous, best-effort HTTP: delivery can be delayed or fail silently (server unreachable: callback never arrives). Don't gate time-critical or business-critical actions solely on one. Confirm state via the REST API before acting, or use a transport with visible failure modes. See "Status callback reliability": https://signalwire.com/docs/platform/webhooks.md

## Call state callbacks (`call_state_url`)

POST with JSON when call state changes; only events in `call_state_events` are sent (default `ended`).

A call state URL can also get a `calling.call.connect` event: when the call running `connect` has its own call state URL (e.g. it was dialed with a `call_state_url`) and `connect` fails, SignalWire sends that URL a `calling.call.connect` event with `connect_state` = `failed`, regardless of `call_state_events`. Shape: see Connect Status Callbacks.

`calling.call.state` payload:
- `event_type` string — `calling.call.state`.
- `event_channel` string — includes the SWML session ID.
- `timestamp` number — Unix timestamp (float).
- `project_id` string; `space_id` string.
- `params` object:
  - `params.call_id` string; `params.node_id` string (node handling the call).
  - `params.segment_id` string — present when assigned.
  - `params.tag` string — present when set.
  - `params.call_state` string — valid values: `created`, `ringing`, `answered`, `ended`.
  - `params.parent` object — present when the leg has a parent call: `parent.device_type`, `parent.call_id`, `parent.node_id` (strings).
  - `params.peer` object — present when the leg has a peer: `peer.call_id`, `peer.node_id`.
  - `params.direction` string — e.g. `outbound`.
  - `params.device` object:
    - `device.type` string — `phone`, `sip`, or `webrtc`.
    - `device.params.from_number`, `device.params.to_number` string — `phone` devices.
    - `device.params.from`, `device.params.to` string — `sip` and `webrtc` devices.
    - `device.params.headers` object[] — SIP headers, each `name` + `value`. Present for some `phone` and `sip` devices.
  - `params.end_reason` string — only when `call_state` is `ended`. Possible values include `hangup`, `cancel`, `busy`, `noAnswer`, `decline`, `error`, `abandoned`, `maxDuration`, `notFound`; which occur depends on how the call ended.
  - `params.end_source` string — `inbound`, `outbound`, or `none`. Present with `end_reason`.
  - `params.dial_winner` string — the string `"true"` when this leg was the destination that answered a dial; absent otherwise.
  - `params.sip_data` object — `sip` devices while SIP info is available; each field present only when known:
    - `sip_data.sip_req_user` (Request-URI user); `sip_data.sip_req_uri`, `sip_data.sip_req_host`.
    - `sip_data.sip_from_user`; `sip_data.sip_from_uri`, `sip_data.sip_from_host`.
    - `sip_data.sip_to_user`; `sip_data.sip_to_uri`, `sip_data.sip_to_host`.
    - `sip_data.sip_contact_user`; `sip_data.sip_contact_uri`, `sip_data.sip_contact_host`, `sip_data.sip_contact_port` (string).
    - `sip_data.sip_p_asserted_identity` string.
    - `sip_data.sip_from_params` object (string key-value pairs); likewise `sip_data.sip_to_params`, `sip_data.sip_contact_params`, `sip_data.sip_req_params`.
  - `params.address_id`, `params.subscriber_id`, `params.subscriber_name` string — Resource Address ID, subscriber ID/name; present when known.
  - `params.start_time`, `params.answer_time`, `params.end_time` number — ms since Unix epoch (created / answered / ended); `0` when not available.
  - `params.audio_in_mos` number — estimated MOS of audio received on the leg; present when available.

## Connect Status Callbacks (top-level `status_url`)

HTTP POST reporting overall status of the connect operation.
- `event_type` string — always `calling.call.connect`.
- `event_channel`, `timestamp`, `project_id`, `space_id` — as in call state payload.
- `params.call_id`, `params.node_id`, `params.segment_id` (when assigned), `params.tag` (when set).
- `params.connect_state` string — possible values: `connecting`, `connected`, `failed`, `disconnected`.
- `params.failed_reason` string — only when `connect_state` is `failed`. Same values as call state `end_reason`, e.g. `busy`, `decline`, `noAnswer`, `notFound` (queue empty or doesn't exist), `error`.
- `params.peer` object — present whenever peer info is available (includes `connected`, can include `disconnected`):
  - `peer.call_id`; `peer.tag` (when set on the peer); `peer.node_id`.
  - `peer.queue_id`, `peer.queue_name` — only for queue-based connections.
  - `peer.device` object — peer's device. Source example: `{type: phone, params: {from_number, to_number}}`.

## Stream Status Callbacks (`status_url` on a stream destination)

HTTP requests reporting stream status.
- `event_type` string — always `calling.call.stream`.
- `event_channel`, `timestamp`, `project_id`, `space_id`; `params.call_id`, `params.node_id`, `params.segment_id` (when assigned), `params.tag` (when set).
- `params.control_id` string — stream control identifier.
- `params.state` string — possible values: `streaming`, `finished`.
- `params.url` string — WebSocket URL of the stream.
- `params.name` string — stream name, if provided.

## Call in progress (`to: "call:<id>"`)

The call must belong to the same project, can't be the call running `connect`, and can't be controlled by cXML. Must be the only destination; `call_state_url` and `call_state_events` not allowed. If it can't be bridged (e.g. already ended), `connect` fails and `connect_result` = `failed`.

## Examples

Ringback with country tone (repeats until connected; other sounds: https://signalwire.com/docs/swml/reference/calling/play.md):
```yaml
- connect:
    answer_on_bridge: true
    ringback: ["ring:uk"]
    from: "+15553214321"
    to: "+15551231234"
```

Dial more than 20 destinations: split into batches of up to 20, start the next from `result` when `connect_result` is `failed`. Next batch starts only after the previous batch's `timeout` expires with no answer.
```yaml
- connect:
    timeout: 20
    parallel:
      - to: "+15551110001"
    result:
      case:
        failed:
          - connect:
              timeout: 20
              parallel:
                - to: "+15551110021"
```

`from_name` at top level is inherited by every device; per-destination overrides it:
```yaml
- connect:
    from: "+15551000001"
    from_name: "Support Team"
    serial:
      - to: "sip:agent1@pbx.example.com"          # sees "Support Team"
      - to: "sip:agent2@pbx.example.com"
        from_name: "Billing Dept"                 # sees "Billing Dept"
```

Queue:
```yaml
- connect:
    to: "queue:support"
    execute_after_queue: "https://example.com/post-call-swml"
```

WebSocket stream:
```yaml
- answer: {}
- connect:
    to: "stream:wss://example.com/audio"
    codec: PCMU
    realtime: true
    name: my-stream
    status_url: "https://example.com/stream-status"
```
