# Call state status callback (webhook)
Source: https://signalwire.com/docs/apis/rest/webhooks/call-state-status-callback.md

POST to the `status_url` of a `dial` command (https://signalwire.com/docs/apis/rest/calls/call-commands.md) when the call enters a state listed in `status_events` (default: only `ended`). `params.call_state` is the state entered.

Advisory, best-effort: delivery can be delayed or fail silently; don't gate time-critical actions on receiving one. See "Status callback reliability" in https://signalwire.com/docs/platform/webhooks.md.

## Payload
- `event_type` enum, required — values: `calling.call.state` (always)
- `event_channel` string, required — channel the event was delivered on
- `timestamp` double, required — when sent, Unix seconds
- `project_id` string, required
- `space_id` string, required
- `params` object, required — the call and its new state:
  - `params.call_id` string, required
  - `params.node_id` string, required — node the call is on
  - `params.call_state` enum, required — values: `created` | `ringing` | `answered` | `ending` | `ended`
  - `params.direction` enum, required — values: `inbound` | `outbound`
  - `params.device` object, required — device on the other end (see Device)
  - `params.start_time` integer, required — call created, ms since epoch; `0` until set
  - `params.answer_time` integer, required — ms since epoch; `0` until answered
  - `params.end_time` integer, required — ms since epoch; `0` until the call ends
  - `params.segment_id` string, optional — present when the call has a segment
  - `params.tag` string, optional — present only when a tag was set on the call
  - `params.end_reason` enum, optional — present once the call has an end reason — values: `hangup` | `cancel` | `busy` | `noAnswer` | `decline` | `error` | `abandoned` | `maxDuration` | `notFound`
  - `params.end_source` enum, optional — which side ended the call; present together with `end_reason` — values: `none` | `inbound` | `outbound`
  - `params.parent` object, optional — call that created this call; present only when this call has a parent (see Parent)
  - `params.peer` object, optional — call this call is bridged to; present only when this call has a peer (see Peer)
  - `params.dial_winner` enum (string), optional — values: `true`. Set to `"true"` when this call is the leg that answered an outbound dial, including the winning leg of a parallel dial; omitted otherwise
  - `params.sip_data` object, optional — present only for SIP devices (see SIP data)
  - `params.audio_in_mos` double, optional — inbound audio quality as mean opinion score; present once measured
  - `params.address_id` string, optional — Resource Address the call was placed to; present on calls a Subscriber places to an Address
  - `params.subscriber_id` string, optional — Subscriber who placed the call; present on calls a Subscriber places from the Browser SDK
  - `params.subscriber_name` string, optional — display name, or if empty first name, then email, then `Subscriber`; present on calls a Subscriber places to an Address

## Device (`params.device`)
- `type` enum, required — values: `phone` | `sip` | `webrtc`
- `params` object, required — the device's addresses. Phone reports `from_number`/`to_number`; SIP and WebRTC report `from`/`to`. Phone and SIP also report `headers` (empty array when none).
  - `params.from_number` string, optional — number that initiated the call; phone only
  - `params.to_number` string, optional — number the call was placed to; phone only
  - `params.from` string, optional — address that initiated the call; SIP and WebRTC only
  - `params.to` string, optional — address the call was placed to; SIP and WebRTC only
  - `params.headers[]` list, optional — phone and SIP only; empty array when none
    - `headers[].name` string, required
    - `headers[].value` string, required

## Parent (`params.parent`)
Present only when this call has a parent, e.g. a leg created by a `connect` or transfer.
- `call_id` string, required — parent call ID
- `node_id` string, required — same value as this call's own `node_id`, not the parent call's node
- `device_type` enum, optional — parent's device type; present only when this call was created by a `connect` (SWML `connect` method or Relay `connect` command); omitted for any other parent — values: `sip` | `phone` | `webrtc`

## Peer (`params.peer`)
Present only when this call has a peer.
- `call_id` string, required — peer call ID
- `node_id` string, required — same value as this call's own `node_id`, not the peer call's node

## SIP data (`params.sip_data`)
Only present when `call.type` is `sip` (source wording). Every key is optional and included only when the call's SIP signaling carries a value for it, so a key missing on one call can be present on another. All strings unless marked object.
- `sip_req_host` — host of the SIP request URI
- `sip_req_uri` — full SIP request URI
- `sip_req_user` — user of the SIP request URI
- `sip_from_host` — host of the From header
- `sip_from_uri` — full URI from the From header
- `sip_from_user` — user of the From header
- `sip_to_host` — host of the To header
- `sip_to_uri` — full URI from the To header
- `sip_to_user` — user of the To header
- `sip_contact_user` — user of the Contact header
- `sip_contact_port` — port from the Contact header
- `sip_contact_uri` — full URI from the Contact header
- `sip_contact_host` — host of the Contact header
- `sip_from_params` object — URI parameters of the From header
- `sip_to_params` object — URI parameters of the To header
- `sip_contact_params` object — URI parameters of the Contact header
- `sip_req_params` object — URI parameters of the request URI
- `sip_p_asserted_identity` — P-Asserted-Identity header of the incoming request. Only the first P-Asserted-Identity header is read, and only when its URI has a user part.

The four `*_params` objects are key/value pairs, present only when that URI carries parameters; a parameter without a value is left out, so the object can be empty.
