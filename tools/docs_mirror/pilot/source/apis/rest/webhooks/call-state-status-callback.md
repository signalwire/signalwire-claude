> This page is for APIs.

> Fetch clean Markdown by appending `.md` to any page URL under https://signalwire.com/docs or requesting it with the HTTP header `Accept: text/markdown`. The root index at https://signalwire.com/docs/llms.txt lists the available documentation indexes.

# Call state status callback

POST 

Sent to the `status_url` of a [`dial`](/docs/apis/rest/calls/call-commands) command when the call
enters one of the states listed in `status_events` (by default, only `ended`).
`params.call_state` is the state the call has entered.

Status callbacks are advisory, best-effort notifications — delivery can be delayed or fail silently, so don't gate time-critical actions on receiving one. See [Status callback reliability](/docs/platform/webhooks#status-callback-reliability).

Reference: https://signalwire.com/docs/apis/rest/webhooks/call-state-status-callback

## Request

### Payload

- `event_type` (enum, required) — The type of event. Always `calling.call.state` for call state callbacks.
  - Allowed values: `calling.call.state`
- `event_channel` (string, required) — The channel the event was delivered on.
- `timestamp` (double, required) — When the event was sent, as a Unix timestamp in seconds.
- `project_id` (string, required) — Your project ID.
- `space_id` (string, required) — Your Space ID.
- `params` (WebhooksCallingCallStateStatusCallbackPayloadParams, required) — The call and its new state.

## Types

### WebhooksCallingCallStateStatusCallbackPayloadParams

The call and its new state.

- `call_id` (string, required) — ID of the call.
- `node_id` (string, required) — ID of the node the call is on.
- `call_state` (enum, required) — The state the call has entered.
  - Allowed values: `created`, `ringing`, `answered`, `ending`, `ended`
- `direction` (enum, required) — The direction of the call.
  - Allowed values: `inbound`, `outbound`
- `device` (Webhooks.Calling.CallStateDevice, required) — The device on the other end of the call.
- `start_time` (integer, required) — When the call was created, in milliseconds since the Unix epoch. `0` until set.
- `answer_time` (integer, required) — When the call was answered, in milliseconds since the Unix epoch. `0` until the call is answered.
- `end_time` (integer, required) — When the call ended, in milliseconds since the Unix epoch. `0` until the call ends.
- `segment_id` (string, optional) — ID of the call segment. Present when the call has one.
- `tag` (string, optional) — The tag associated with the call. Present only when a tag was set on the call.
- `end_reason` (enum, optional) — Why the call ended. Present once the call has an end reason.
  - Allowed values: `hangup`, `cancel`, `busy`, `noAnswer`, `decline`, `error`, `abandoned`, `maxDuration`, `notFound`
- `end_source` (enum, optional) — Which side ended the call. Present together with `end_reason`.
  - Allowed values: `none`, `inbound`, `outbound`
- `parent` (Webhooks.Calling.InboundCallParent, optional) — The call that created this call. Present only when this call has a parent.
- `peer` (Webhooks.Calling.InboundCallPeer, optional) — The call this call is bridged to. Present only when this call has a peer.
- `dial_winner` (enum, optional) — Set to `"true"` when this call is the leg that answered an outbound dial, including the winning leg of a parallel dial. Omitted otherwise.
  - Allowed values: `true`
- `sip_data` (Webhooks.Calling.InboundCallSipData, optional) — SIP-specific data. Present only for SIP devices.
- `audio_in_mos` (double, optional) — The call's inbound audio quality as a mean opinion score. Present once measured.
- `address_id` (string, optional) — ID of the Resource Address the call was placed to. Present on calls a Subscriber places to an Address.
- `subscriber_id` (string, optional) — ID of the Subscriber who placed the call. Present on calls a Subscriber places from the Browser SDK.
- `subscriber_name` (string, optional) — Name of the Subscriber who placed the call: their display name, or if that's empty their first name, then their email, then `Subscriber`. Present on calls a Subscriber places to an Address.

### Webhooks.Calling.CallStateDevice

The device on one end of the call.

- `type` (enum, required) — The device type.
  - Allowed values: `phone`, `sip`, `webrtc`
- `params` (WebhooksCallingCallStateDeviceParams, required) — The device's addresses. Phone devices report `from_number` and `to_number`; SIP and WebRTC devices report `from` and `to`. Phone and SIP devices also report `headers`, as an empty array when there are none.

### Webhooks.Calling.InboundCallParent

The call that created this call. Present only when this call has a parent — for example, a leg created by a `connect` or transfer.

- `call_id` (string, required) — A unique identifier for the parent call.
- `node_id` (string, required) — The same value as this call's own `node_id`, not the parent call's node.
- `device_type` (enum, optional) — The device type of the parent call. Present only when this call was created by a `connect`, from either the SWML `connect` method or the Relay `connect` command; omitted for any other parent call.
  - Allowed values: `sip`, `phone`, `webrtc`

### Webhooks.Calling.InboundCallPeer

The call this call is bridged to. Present only when this call has a peer.

- `call_id` (string, required) — A unique identifier for the peer call.
- `node_id` (string, required) — The same value as this call's own `node_id`, not the peer call's node.

### Webhooks.Calling.InboundCallSipData

SIP-specific data for SIP calls. Only present when `call.type` is `sip`. Every key is optional: each one is included only when the call's SIP signaling carries a value for it, so a key missing from one call can be present on another.

- `sip_req_host` (string, optional) — The host portion of the SIP request URI.
- `sip_req_uri` (string, optional) — The full SIP request URI.
- `sip_req_user` (string, optional) — The user portion of the SIP request URI.
- `sip_from_host` (string, optional) — The host portion of the SIP From header.
- `sip_from_uri` (string, optional) — The full URI from the SIP From header.
- `sip_from_user` (string, optional) — The user portion of the SIP From header.
- `sip_to_host` (string, optional) — The host portion of the SIP To header.
- `sip_to_uri` (string, optional) — The full URI from the SIP To header.
- `sip_to_user` (string, optional) — The user portion of the SIP To header.
- `sip_contact_user` (string, optional) — The user portion of the SIP Contact header.
- `sip_contact_port` (string, optional) — The port from the SIP Contact header.
- `sip_contact_uri` (string, optional) — The full URI from the SIP Contact header.
- `sip_contact_host` (string, optional) — The host portion of the SIP Contact header.
- `sip_from_params` (WebhooksCallingInboundCallSipDataSipFromParams, optional) — The URI parameters of the SIP From header, as key/value pairs. Present only when that URI carries parameters. A parameter without a value is left out, so the object can be empty.
- `sip_to_params` (WebhooksCallingInboundCallSipDataSipToParams, optional) — The URI parameters of the SIP To header, as key/value pairs. Present only when that URI carries parameters. A parameter without a value is left out, so the object can be empty.
- `sip_contact_params` (WebhooksCallingInboundCallSipDataSipContactParams, optional) — The URI parameters of the SIP Contact header, as key/value pairs. Present only when that URI carries parameters. A parameter without a value is left out, so the object can be empty.
- `sip_req_params` (WebhooksCallingInboundCallSipDataSipReqParams, optional) — The URI parameters of the SIP request URI, as key/value pairs. Present only when that URI carries parameters. A parameter without a value is left out, so the object can be empty.
- `sip_p_asserted_identity` (string, optional) — The P-Asserted-Identity header of the incoming SIP request. Only the first P-Asserted-Identity header is read, and only when its URI has a user part.

### WebhooksCallingCallStateDeviceParams

The device's addresses. Phone devices report `from_number` and `to_number`; SIP and WebRTC devices report `from` and `to`. Phone and SIP devices also report `headers`, as an empty array when there are none.

- `from_number` (string, optional) — The number that initiated the call. Phone devices only.
- `to_number` (string, optional) — The number the call was placed to. Phone devices only.
- `from` (string, optional) — The address that initiated the call. SIP and WebRTC devices only.
- `to` (string, optional) — The address the call was placed to. SIP and WebRTC devices only.
- `headers` (list of Webhooks.Calling.InboundCallHeader, optional) — Headers associated with the call. Phone and SIP devices only, as an empty array when there are none.

### WebhooksCallingInboundCallSipDataSipFromParams

The URI parameters of the SIP From header, as key/value pairs. Present only when that URI carries parameters. A parameter without a value is left out, so the object can be empty.

### WebhooksCallingInboundCallSipDataSipToParams

The URI parameters of the SIP To header, as key/value pairs. Present only when that URI carries parameters. A parameter without a value is left out, so the object can be empty.

### WebhooksCallingInboundCallSipDataSipContactParams

The URI parameters of the SIP Contact header, as key/value pairs. Present only when that URI carries parameters. A parameter without a value is left out, so the object can be empty.

### WebhooksCallingInboundCallSipDataSipReqParams

The URI parameters of the SIP request URI, as key/value pairs. Present only when that URI carries parameters. A parameter without a value is left out, so the object can be empty.

### Webhooks.Calling.InboundCallHeader

A single header associated with the call.

- `name` (string, required) — The name of the header.
- `value` (string, required) — The value of the header.