> This page is for SWML.

> Fetch clean Markdown by appending `.md` to any page URL under https://signalwire.com/docs or requesting it with the HTTP header `Accept: text/markdown`. The root index at https://signalwire.com/docs/llms.txt lists the available documentation indexes.

# connect

> Connect to a phone number, SIP URI, Resource Address, queue, or WebSocket stream.

[statuscallbacks]: #statuscallbacks

Connect to a phone number, [SIP URI](/docs/platform/voice/sip), [Resource Address](/docs/platform/addresses), queue, or WebSocket stream.

## **Properties**

**`connect`** `object` — required

Connects the current call to a destination — a phone number, [SIP URI](/docs/platform/voice/sip), [Resource Address](/docs/platform/addresses), queue, or WebSocket stream. The object shape depends on the connection type — select a tab below to see the full property schema for each mode.

---

#### Single

Dial a single destination directly using the `to` property.

**`connect.to`** `string` — required

Single destination to dial.
The value format determines the destination type:

* **Phone number** — E.164 format, including the leading `+` (e.g., `+15552345678`). A number without the `+`, such as `15552345678`, is rejected.
* **SIP URI** — `sip:` or `sips:` prefix (e.g., `sip:alice@example.com`)
* **[Resource Address](/docs/platform/addresses)** — address path (e.g., `/public/test_room`)
* **Queue** — `queue:` prefix (e.g., `queue:support`)
* **Call** — `call:` prefix followed by the ID of a call in progress in the same project (e.g., `call:ba79c846-4834-42b9-9cd3-2f87c30f2972`). Bridges the caller to that call. See [Connect to a call in progress](#connect-to-a-call-in-progress).
* **WebSocket stream** — `stream:wss://` prefix (e.g., `stream:wss://example.com/audio`). An unencrypted `stream:ws://` URL is rejected.

The `queue:`, `call:`, and `stream:` prefixes are case-sensitive and must be lowercase. The `sip:` and `sips:` prefixes are not case-sensitive.

---

**`connect.answer_on_bridge`** `boolean` — default: false

Delay answer until the B-leg answers.

---

**`connect.call_state_events`** `string[]` — default: \['ended']

An array of call state event names to be notified about. Allowed event names are `created`, `ringing`, `answered`, and `ended`. Each item can also be a SWML variable that resolves to one of these names.

---

**`connect.call_state_url`** `string`

Webhook url to send call status change notifications to. Authentication can also be set in the url in the format of `username:password@url`. Learn more about [status callbacks][statuscallbacks].

Applies only to phone, SIP, and Resource Address destinations. When `to` starts with `queue:`, `call:`, or `stream:`, `call_state_url` and `call_state_events` aren't allowed. Queue events go to the `status_url` of [`enter_queue`](/docs/swml/reference/calling/enter-queue), and stream events go to `connect.status_url`.

---

**`connect.codecs`** `string | string[]` — default: Based on SignalWire settings

Codecs to offer, as a comma-separated string (`"PCMU,PCMA"`) or an array of strings (`["PCMU", "PCMA"]`). Supported codecs are `PCMU`, `PCMA`, `OPUS`, `G722`, `G729`, `AMR-WB`, `VP8`, and `H264`. Has no effect on calls to phone numbers.

---

**`connect.confirm`** `string | object[]`

Confirmation to execute when the call is connected. Can be either:

* A URL (string) that returns a SWML document
* An array of SWML methods to execute inline

Only these methods are allowed, including inside `cond` and `switch` branches: `cond`, `switch`, `set`, `unset`, `hangup`, `play`, `prompt`, `record`, `record_call`, `stop_record_call`, `tap`, `stop_tap`, `stream`, `stop_stream`, `transcribe`, `transcribe_stop`, `send_digits`, `send_sms`, `denoise`, `stop_denoise`, and `user_event`.

---

**`connect.confirm_timeout`** `integer` — default: Inherits from timeout

Time, in seconds, allowed for the `confirm` SWML to run on the answered destination, whether it is fetched from a URL or given inline.

---

**`connect.encryption`** `string` — default: optional

The encryption method to use for the call. Possible values: `mandatory`, `optional`, `forbidden`.

---

**`connect.from`** `string` — default: Calling party's caller ID number

Caller ID number. Optional. Must be a phone number in E.164 format with the leading `+`, a SIP URI, or a Resource Address; a `queue:`, `call:`, or `stream:` value is rejected.

---

**`connect.from_name`** `string`

The caller ID name shown to the person you're calling, displayed alongside the `from` number (sometimes called CNAM). Applies to SIP calls only — it has no effect on calls to phone numbers. Use 1 to 70 characters after variable expansion: letters, digits, spaces, and `_`, `.`, `-`, `+`, or `,`. Text and variables can be combined, such as `Support ${vars.dept}`.

---

**`connect.headers`** `object[]`

Custom SIP headers to add to INVITE. Has no effect on calls to phone numbers.

---

**`headers[].name`** `string` — required

The name of the header. Must be a valid SIP header name, 3 to 256 characters long, that either starts with `X-` or is one of `Privacy`, `P-Asserted-Identity`, or `User-to-User`. Names starting with `SignalWire`, `X-SignalWire`, `X-CID`, or `X-SW-Xregion` are reserved and can't be set. A `Privacy` header takes effect only with the value `id`, which hides the caller's number.

---

**`headers[].value`** `string` — required

The value of the header. Can't be empty or contain line breaks.

---

**`connect.max_duration`** `integer` — default: 14400 seconds (4 hours)

Maximum duration, in seconds, allowed for the call.

---

**`connect.password`** `string`

SIP authentication password for the outbound leg. **Only applies to [SIP URI](/docs/platform/voice/sip) targets** — ignored for phone, Resource Address, queue, and stream destinations.

---

**`connect.result`** `object | object[]`

Action to take based on the result of the call. This will run once the peer leg of the call has ended.

Will use the [`switch properties`](/docs/swml/reference/calling/switch#properties) when the `return_value` is a object, and will use the [`cond properties`](/docs/swml/reference/calling/cond#properties) method when the `return_value` is an array.
See [Variables](#variables) for details.

---

**`connect.ringback`** `boolean | string | string[]` — default: A standard ringback tone

Ringback to play to the caller while phone, SIP, and Resource Address destinations ring. Can be:

* A `play` URI, or an array of `play` URIs, to play as the ringback tone
* `false` to turn off SignalWire's ringback tone and pass the destination's early media (for example, its own ringback or announcements) through to the caller
* `true` to keep the default ringback tone

---

**`connect.session_timeout`** `integer` — default: Based on SignalWire settings

Time, in seconds, to set the SIP `Session-Expires` header in INVITE. Must be a positive, non-zero number. Values from 1 to 15000 take effect; a larger value is accepted but ignored, so the default `Session-Expires` value is used. Has no effect on calls to phone numbers.

---

**`connect.status_url`** `string`

HTTP or HTTPS webhook URL to deliver status events. For phone, SIP, and Resource Address destinations, reports the connect operation status (connecting, connected, failed, disconnected). See [Connect Status Callbacks](#connect-status-callbacks). For a `stream:` destination, reports stream status notifications, and `http://` still works, unlike a stream `status_url` set on a destination inside `parallel`, `serial`, or `serial_parallel`. See [Stream Status Callbacks](#stream-status-callbacks).

---

**`connect.status_url_method`** `string` — default: POST

HTTP method for the status webhook. Possible values: `GET`, `POST`. **Stream destinations only.**

---

**`connect.stop_all_on_reject`** `boolean | string[]` — default: false

Stop ringing and disconnect the caller when a destination rejects the call. Can be either:

* `true` to stop when a destination is busy or declines the call
* A non-empty array of the reasons to stop on: `busy`, `decline`, `noAnswer`

When a destination rejects the call with a matching reason, the destinations ringing alongside it stop ringing. If `connect` then fails with that reason, the `result` block runs first, and then the caller is disconnected.

---

**`connect.timeout`** `integer` — default: 60 seconds

Maximum time, in seconds, to wait for an answer.

---

**`connect.execute_after_queue`** `string`

SWML to execute on this call after its bridge with the queued call ends. Only applies when `to` starts with `queue:`.

Can be either:

* A URL (http or https) that returns a SWML document
* An inline SWML document (as a JSON string)

When omitted, the call hangs up when the bridge ends. Either way, the script does not continue past `connect` once a queued call has been bridged.

If no queued call is bridged (for example, the queue is empty or doesn't exist), `connect` fails, `connect_result` is set to `failed`, and `result` runs.

---

**`connect.username`** `string`

SIP authentication username for the outbound leg. **Only applies to [SIP URI](/docs/platform/voice/sip) targets** — ignored for phone, Resource Address, queue, and stream destinations.

---

**`connect.webrtc_media`** `boolean` — default: false

If true, WebRTC media is offered to the SIP endpoint. Has no effect on calls to phone numbers.

---

#### Stream-specific properties

The following properties apply only when `to` starts with `stream:wss://`.

**`connect.authorization_bearer_token`** `string`

Bearer token sent as an `Authorization` header during the WebSocket handshake.

---

**`connect.codec`** `string` — default: PCMU

Audio codec for the stream. Supported values: `PCMU`, `PCMA`, `G722`, `L16`. Codec can include rate and ptime modifiers (e.g., `PCMU@40i`, `L16@24000h@40i`).

---

**`connect.custom_parameters`** `object`

Custom key-value pairs sent in the WebSocket start message.

---

**`connect.name`** `string`

Stream name identifier.

---

**`connect.realtime`** `boolean` — default: false

Enable realtime mode for bidirectional audio.

---

#### Example

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - connect:
        to: "sip:alice@example.com"
        from: "+15551112222"
        username: "sipuser"
        password: "s3cret"
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "connect": {
          "to": "sip:alice@example.com",
          "from": "+15551112222",
          "username": "sipuser",
          "password": "s3cret"
        }
      }
    ]
  }
}
```

#### Parallel

Dial multiple destinations simultaneously — the first to answer is bridged and the rest are cancelled.

**`connect.parallel`** `object[]` — required

Array of destination objects to dial simultaneously. The first destination to answer is bridged and the rest are cancelled.

Must contain at least one destination. A `queue:` or `call:` destination can't be combined with any other destination, and a `stream:` destination can't be combined with a phone, SIP, Resource Address, or queue destination: `connect` fails in either case. If several `stream:` destinations are listed, only the first is used. To connect to a queue, a call, or a stream, use a single `to` instead (see the **Single** tab).

> **20-destination limit**
>
> Up to 20 destinations are dialed. Any destination after the 20th never rings, and `connect` reports no error for it. To reach more, see [Dial more than 20 destinations](#dial-more-than-20-destinations).

---

**`parallel[].to`** `string` — required

Destination to dial. Can be:

* Phone number in E.164 format, including the leading `+` (e.g., `+15552345678`)
* [SIP URI](/docs/platform/voice/sip), with a `sip:` or `sips:` prefix (e.g., `sip:alice@example.com`)
* [Resource Address](/docs/platform/addresses) (e.g., `/public/test_room`)
* Queue (e.g., `queue:support`)
* Call in progress (e.g., `call:ba79c846-4834-42b9-9cd3-2f87c30f2972`)
* WebSocket stream, using `wss://` (e.g., `stream:wss://example.com/audio`)

See the **Single** tab for the format rules of each destination type.

---

**`parallel[].from`** `string`

Caller ID number. Overrides the top-level `from`. Accepts the same formats as the top-level `from`.

---

**`parallel[].from_name`** `string`

The caller ID name shown to this destination. Overrides the top-level `from_name`. Applies to SIP calls only. Use 1 to 70 characters after variable expansion: letters, digits, spaces, and `_`, `.`, `-`, `+`, or `,`.

---

**`parallel[].username`** `string`

SIP authentication username for this destination. **Only applies to SIP URI targets.**

---

**`parallel[].password`** `string`

SIP authentication password for this destination. **Only applies to SIP URI targets.**

---

**`parallel[].timeout`** `integer` — default: Inherits the top-level timeout, then 60 seconds

Maximum time, in seconds, to wait for this destination to answer. Overrides the top-level `timeout`.

---

**`parallel[].call_state_events`** `string[]` — default: Inherits the top-level call_state_events, then \['ended']

An array of call state event names to be notified about. Overrides the top-level `call_state_events`. Each item can also be a SWML variable that resolves to one of these names. Not allowed when `to` starts with `queue:`, `call:`, or `stream:`.

---

**`parallel[].call_state_url`** `string`

Webhook url to send call state change notifications to for this destination. Overrides the top-level `call_state_url`. Not allowed when `to` starts with `queue:`, `call:`, or `stream:`.

---

**`parallel[].confirm`** `string | object[]`

Confirmation script to execute on this destination when answered. Overrides the top-level `confirm`. An inline array is limited to the same methods as the top-level `confirm`.

---

**`parallel[].confirm_timeout`** `integer`

Seconds allowed for the `confirm` SWML to run on this destination. Overrides the top-level `confirm_timeout`. When neither is set, this destination's `timeout` is used.

---

**`parallel[].encryption`** `string`

Media encryption (SRTP) for this destination. Overrides the top-level `encryption`, which is used when this is not set. **Applies to SIP destinations only.**
Possible values: `mandatory`, `optional`, `forbidden`.

---

**`parallel[].headers`** `object[]`

Custom SIP headers to add to INVITE for this destination. Replaces the top-level `headers` for this destination. **Applies to SIP destinations only.**

---

**`parallel[].headers[].name`** `string` — required

The name of the header. Must be a valid SIP header name, 3 to 256 characters long, that either starts with `X-` or is one of `Privacy`, `P-Asserted-Identity`, or `User-to-User`. Names starting with `SignalWire`, `X-SignalWire`, `X-CID`, or `X-SW-Xregion` are reserved and can't be set. A `Privacy` header takes effect only with the value `id`, which hides the caller's number.

---

**`parallel[].headers[].value`** `string` — required

The value of the header. Can't be empty or contain line breaks.

---

**`parallel[].codecs`** `string | string[]`

Codecs to offer to this destination, as a comma-separated string or an array of strings, using the same codec names as the top-level `codecs`. Overrides the top-level `codecs`. **Applies to SIP destinations only.**

---

**`parallel[].webrtc_media`** `boolean`

If true, WebRTC media is offered to this destination. Overrides the top-level `webrtc_media`, which is used when this is not set. **Applies to SIP destinations only.**

---

**`parallel[].session_timeout`** `integer`

Time, in seconds, to set the SIP `Session-Expires` header in INVITE for this destination. Must be a positive, non-zero number. Values from 1 to 15000 take effect; a larger value is accepted but ignored, so the default `Session-Expires` value is used. The top-level `session_timeout` is not used in this mode, so set it on each SIP destination that needs it. **Applies to SIP destinations only.**

---

**`parallel[].name`** `string`

Stream name identifier. **Applies to stream destinations only.**

---

**`parallel[].codec`** `string`

Audio codec for the stream. Takes the same values as `connect.codec` on a single stream destination. **Applies to stream destinations only.**

---

**`parallel[].status_url`** `string`

HTTPS URL to receive status notifications for this stream. Must use `https://`; an `http://` URL is rejected, unlike the top-level `connect.status_url`. See [Stream Status Callbacks](#stream-status-callbacks). **Applies to stream destinations only.**

---

**`parallel[].status_url_method`** `string`

HTTP method for the stream status webhook. Possible values: `GET`, `POST`. **Applies to stream destinations only.**

---

**`parallel[].realtime`** `boolean` — default: false

Enables realtime mode for bidirectional audio on the stream, as with `connect.realtime` on a single stream destination. **Applies to stream destinations only.**

---

**`parallel[].authorization_bearer_token`** `string`

Bearer token for the stream's WebSocket connection, as with `connect.authorization_bearer_token` on a single stream destination. **Applies to stream destinations only.**

---

**`parallel[].custom_parameters`** `object`

Custom key-value pairs for the stream, as with `connect.custom_parameters` on a single stream destination. Every value must be a string. **Applies to stream destinations only.**

---

**`connect.answer_on_bridge`** `boolean` — default: false

Delay answer until the B-leg answers.

---

**`connect.call_state_events`** `string[]` — default: \['ended']

An array of call state event names to be notified about. Allowed event names are `created`, `ringing`, `answered`, and `ended`. Each item can also be a SWML variable that resolves to one of these names. Can be overwritten on each destination.

---

**`connect.call_state_url`** `string`

Webhook url to send call status change notifications to for every phone, SIP, and Resource Address destination. Can be overwritten on each destination. Authentication can also be set in the url in the format of `username:password@url`. Learn more about [status callbacks][statuscallbacks].

It doesn't apply to destinations whose `to` starts with `queue:`, `call:`, or `stream:`, and those destinations can't set their own `call_state_url` or `call_state_events`.

---

**`connect.codecs`** `string | string[]` — default: Based on SignalWire settings

Codecs to offer, as a comma-separated string (`"PCMU,PCMA"`) or an array of strings (`["PCMU", "PCMA"]`). Supported codecs are `PCMU`, `PCMA`, `OPUS`, `G722`, `G729`, `AMR-WB`, `VP8`, and `H264`. Has no effect on calls to phone numbers. Each SIP destination uses these codecs unless it sets its own `codecs`.

---

**`connect.confirm`** `string | object[]`

Confirmation to execute when the call is connected. Can be either:

* A URL (string) that returns a SWML document
* An array of SWML methods to execute inline

Only these methods are allowed, including inside `cond` and `switch` branches: `cond`, `switch`, `set`, `unset`, `hangup`, `play`, `prompt`, `record`, `record_call`, `stop_record_call`, `tap`, `stop_tap`, `stream`, `stop_stream`, `transcribe`, `transcribe_stop`, `send_digits`, `send_sms`, `denoise`, `stop_denoise`, and `user_event`.

---

**`connect.confirm_timeout`** `integer` — default: Inherits from timeout

Time, in seconds, allowed for the `confirm` SWML to run on the answered destination, whether it is fetched from a URL or given inline.

---

**`connect.encryption`** `string` — default: optional

The encryption method to use for the call. Possible values: `mandatory`, `optional`, `forbidden`.

---

**`connect.from`** `string` — default: Calling party's caller ID number

Caller ID number. Optional. Can be overwritten on each destination. Must be a phone number in E.164 format with the leading `+`, a SIP URI, or a Resource Address; a `queue:`, `call:`, or `stream:` value is rejected.

---

**`connect.from_name`** `string`

The caller ID name shown to the person you're calling, displayed alongside the `from` number (sometimes called CNAM). Applies to SIP calls only — it has no effect on calls to phone numbers. Use 1 to 70 characters after variable expansion: letters, digits, spaces, and `_`, `.`, `-`, `+`, or `,`. Text and variables can be combined, such as `Support ${vars.dept}`. Can be overridden on each destination.

---

**`connect.headers`** `object[]`

Custom SIP headers to add to INVITE. Has no effect on calls to phone numbers. Each SIP destination uses these headers unless it sets its own `headers`.

---

**`headers[].name`** `string` — required

The name of the header. Must be a valid SIP header name, 3 to 256 characters long, that either starts with `X-` or is one of `Privacy`, `P-Asserted-Identity`, or `User-to-User`. Names starting with `SignalWire`, `X-SignalWire`, `X-CID`, or `X-SW-Xregion` are reserved and can't be set. A `Privacy` header takes effect only with the value `id`, which hides the caller's number.

---

**`headers[].value`** `string` — required

The value of the header. Can't be empty or contain line breaks.

---

**`connect.max_duration`** `integer` — default: 14400 seconds (4 hours)

Maximum duration, in seconds, allowed for the call.

---

**`connect.result`** `object | object[]`

Action to take based on the result of the call. This will run once the peer leg of the call has ended.

Will use the [`switch properties`](/docs/swml/reference/calling/switch#properties) when the `return_value` is a object, and will use the [`cond properties`](/docs/swml/reference/calling/cond#properties) method when the `return_value` is an array.
See [Variables](#variables) for details.

---

**`connect.ringback`** `boolean | string | string[]` — default: A standard ringback tone

Ringback to play to the caller while phone, SIP, and Resource Address destinations ring. Can be:

* A `play` URI, or an array of `play` URIs, to play as the ringback tone
* `false` to turn off SignalWire's ringback tone and pass the destination's early media (for example, its own ringback or announcements) through to the caller
* `true` to keep the default ringback tone

---

**`connect.session_timeout`** `integer`

SIP `Session-Expires` time, in seconds. Has no effect in this mode: SIP destinations don't use the top-level `session_timeout`, so set `session_timeout` on each SIP destination instead.

---

**`connect.status_url`** `string`

HTTP or HTTPS webhook URL to deliver status events. Reports the connect operation status (connecting, connected, failed, disconnected). See [Connect Status Callbacks](#connect-status-callbacks).

---

**`connect.stop_all_on_reject`** `boolean | string[]` — default: false

Stop ringing and disconnect the caller when a destination rejects the call. Can be either:

* `true` to stop when a destination is busy or declines the call
* A non-empty array of the reasons to stop on: `busy`, `decline`, `noAnswer`

When a destination rejects the call with a matching reason, the destinations ringing alongside it stop ringing. If `connect` then fails with that reason, the `result` block runs first, and then the caller is disconnected.

---

**`connect.timeout`** `integer` — default: 60 seconds

Maximum time, in seconds, to wait for an answer.

---

**`connect.webrtc_media`** `boolean` — default: false

If true, WebRTC media is offered to the SIP endpoint. Has no effect on calls to phone numbers. Can be overwritten on each destination.

---

#### Example

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - connect:
        from: "+15551112222"
        parallel:
          - to: "sip:alice@example.com"
            username: "alice_user"
            password: "alice_pw"
          - to: "sip:bob@example.com"
            username: "bob_user"
            password: "bob_pw"
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "connect": {
          "from": "+15551112222",
          "parallel": [
            {
              "to": "sip:alice@example.com",
              "username": "alice_user",
              "password": "alice_pw"
            },
            {
              "to": "sip:bob@example.com",
              "username": "bob_user",
              "password": "bob_pw"
            }
          ]
        }
      }
    ]
  }
}
```

#### Serial

Dial destinations in sequence — each destination is tried one at a time, moving to the next if the previous fails.

**`connect.serial`** `object[]` — required

Array of destination objects to dial in order. Each destination is tried sequentially — if the first fails, the next is attempted.

Must contain at least one destination. A `queue:` or `call:` destination can't be combined with any other destination, and a `stream:` destination can't be combined with a phone, SIP, Resource Address, or queue destination: `connect` fails in either case. If several `stream:` destinations are listed, only the first is used. To connect to a queue, a call, or a stream, use a single `to` instead (see the **Single** tab).

> **20-destination limit**
>
> Up to 20 destinations are tried. Any destination after the 20th never rings, and `connect` reports no error for it. To reach more, see [Dial more than 20 destinations](#dial-more-than-20-destinations).

---

**`serial[].to`** `string` — required

Destination to dial. Can be:

* Phone number in E.164 format, including the leading `+` (e.g., `+15552345678`)
* [SIP URI](/docs/platform/voice/sip), with a `sip:` or `sips:` prefix (e.g., `sip:alice@example.com`)
* [Resource Address](/docs/platform/addresses) (e.g., `/public/test_room`)
* Queue (e.g., `queue:support`)
* Call in progress (e.g., `call:ba79c846-4834-42b9-9cd3-2f87c30f2972`)
* WebSocket stream, using `wss://` (e.g., `stream:wss://example.com/audio`)

See the **Single** tab for the format rules of each destination type.

---

**`serial[].from`** `string`

Caller ID number. Overrides the top-level `from`. Accepts the same formats as the top-level `from`.

---

**`serial[].from_name`** `string`

The caller ID name shown to this destination. Overrides the top-level `from_name`. Applies to SIP calls only. Use 1 to 70 characters after variable expansion: letters, digits, spaces, and `_`, `.`, `-`, `+`, or `,`.

---

**`serial[].username`** `string`

SIP authentication username for this destination. **Only applies to SIP URI targets.**

---

**`serial[].password`** `string`

SIP authentication password for this destination. **Only applies to SIP URI targets.**

---

**`serial[].timeout`** `integer` — default: Inherits the top-level timeout, then 60 seconds

Maximum time, in seconds, to wait for this destination to answer. Overrides the top-level `timeout`.

---

**`serial[].call_state_events`** `string[]` — default: Inherits the top-level call_state_events, then \['ended']

An array of call state event names to be notified about. Overrides the top-level `call_state_events`. Each item can also be a SWML variable that resolves to one of these names. Not allowed when `to` starts with `queue:`, `call:`, or `stream:`.

---

**`serial[].call_state_url`** `string`

Webhook url to send call state change notifications to for this destination. Overrides the top-level `call_state_url`. Not allowed when `to` starts with `queue:`, `call:`, or `stream:`.

---

**`serial[].confirm`** `string | object[]`

Confirmation script to execute on this destination when answered. Overrides the top-level `confirm`. An inline array is limited to the same methods as the top-level `confirm`.

---

**`serial[].confirm_timeout`** `integer`

Seconds allowed for the `confirm` SWML to run on this destination. Overrides the top-level `confirm_timeout`. When neither is set, this destination's `timeout` is used.

---

**`serial[].encryption`** `string`

Media encryption (SRTP) for this destination. Overrides the top-level `encryption`, which is used when this is not set. **Applies to SIP destinations only.**
Possible values: `mandatory`, `optional`, `forbidden`.

---

**`serial[].headers`** `object[]`

Custom SIP headers to add to INVITE for this destination. Replaces the top-level `headers` for this destination. **Applies to SIP destinations only.**

---

**`serial[].headers[].name`** `string` — required

The name of the header. Must be a valid SIP header name, 3 to 256 characters long, that either starts with `X-` or is one of `Privacy`, `P-Asserted-Identity`, or `User-to-User`. Names starting with `SignalWire`, `X-SignalWire`, `X-CID`, or `X-SW-Xregion` are reserved and can't be set. A `Privacy` header takes effect only with the value `id`, which hides the caller's number.

---

**`serial[].headers[].value`** `string` — required

The value of the header. Can't be empty or contain line breaks.

---

**`serial[].codecs`** `string | string[]`

Codecs to offer to this destination, as a comma-separated string or an array of strings, using the same codec names as the top-level `codecs`. Overrides the top-level `codecs`. **Applies to SIP destinations only.**

---

**`serial[].webrtc_media`** `boolean`

If true, WebRTC media is offered to this destination. Overrides the top-level `webrtc_media`, which is used when this is not set. **Applies to SIP destinations only.**

---

**`serial[].session_timeout`** `integer`

Time, in seconds, to set the SIP `Session-Expires` header in INVITE for this destination. Must be a positive, non-zero number. Values from 1 to 15000 take effect; a larger value is accepted but ignored, so the default `Session-Expires` value is used. The top-level `session_timeout` is not used in this mode, so set it on each SIP destination that needs it. **Applies to SIP destinations only.**

---

**`serial[].name`** `string`

Stream name identifier. **Applies to stream destinations only.**

---

**`serial[].codec`** `string`

Audio codec for the stream. Takes the same values as `connect.codec` on a single stream destination. **Applies to stream destinations only.**

---

**`serial[].status_url`** `string`

HTTPS URL to receive status notifications for this stream. Must use `https://`; an `http://` URL is rejected, unlike the top-level `connect.status_url`. See [Stream Status Callbacks](#stream-status-callbacks). **Applies to stream destinations only.**

---

**`serial[].status_url_method`** `string`

HTTP method for the stream status webhook. Possible values: `GET`, `POST`. **Applies to stream destinations only.**

---

**`serial[].realtime`** `boolean` — default: false

Enables realtime mode for bidirectional audio on the stream, as with `connect.realtime` on a single stream destination. **Applies to stream destinations only.**

---

**`serial[].authorization_bearer_token`** `string`

Bearer token for the stream's WebSocket connection, as with `connect.authorization_bearer_token` on a single stream destination. **Applies to stream destinations only.**

---

**`serial[].custom_parameters`** `object`

Custom key-value pairs for the stream, as with `connect.custom_parameters` on a single stream destination. Every value must be a string. **Applies to stream destinations only.**

---

**`connect.answer_on_bridge`** `boolean` — default: false

Delay answer until the B-leg answers.

---

**`connect.call_state_events`** `string[]` — default: \['ended']

An array of call state event names to be notified about. Allowed event names are `created`, `ringing`, `answered`, and `ended`. Each item can also be a SWML variable that resolves to one of these names. Can be overwritten on each destination.

---

**`connect.call_state_url`** `string`

Webhook url to send call status change notifications to for every phone, SIP, and Resource Address destination. Can be overwritten on each destination. Authentication can also be set in the url in the format of `username:password@url`. Learn more about [status callbacks][statuscallbacks].

It doesn't apply to destinations whose `to` starts with `queue:`, `call:`, or `stream:`, and those destinations can't set their own `call_state_url` or `call_state_events`.

---

**`connect.codecs`** `string | string[]` — default: Based on SignalWire settings

Codecs to offer, as a comma-separated string (`"PCMU,PCMA"`) or an array of strings (`["PCMU", "PCMA"]`). Supported codecs are `PCMU`, `PCMA`, `OPUS`, `G722`, `G729`, `AMR-WB`, `VP8`, and `H264`. Has no effect on calls to phone numbers. Each SIP destination uses these codecs unless it sets its own `codecs`.

---

**`connect.confirm`** `string | object[]`

Confirmation to execute when the call is connected. Can be either:

* A URL (string) that returns a SWML document
* An array of SWML methods to execute inline

Only these methods are allowed, including inside `cond` and `switch` branches: `cond`, `switch`, `set`, `unset`, `hangup`, `play`, `prompt`, `record`, `record_call`, `stop_record_call`, `tap`, `stop_tap`, `stream`, `stop_stream`, `transcribe`, `transcribe_stop`, `send_digits`, `send_sms`, `denoise`, `stop_denoise`, and `user_event`.

---

**`connect.confirm_timeout`** `integer` — default: Inherits from timeout

Time, in seconds, allowed for the `confirm` SWML to run on the answered destination, whether it is fetched from a URL or given inline.

---

**`connect.encryption`** `string` — default: optional

The encryption method to use for the call. Possible values: `mandatory`, `optional`, `forbidden`.

---

**`connect.from`** `string` — default: Calling party's caller ID number

Caller ID number. Optional. Can be overwritten on each destination. Must be a phone number in E.164 format with the leading `+`, a SIP URI, or a Resource Address; a `queue:`, `call:`, or `stream:` value is rejected.

---

**`connect.from_name`** `string`

The caller ID name shown to the person you're calling, displayed alongside the `from` number (sometimes called CNAM). Applies to SIP calls only — it has no effect on calls to phone numbers. Use 1 to 70 characters after variable expansion: letters, digits, spaces, and `_`, `.`, `-`, `+`, or `,`. Text and variables can be combined, such as `Support ${vars.dept}`. Can be overridden on each destination.

---

**`connect.headers`** `object[]`

Custom SIP headers to add to INVITE. Has no effect on calls to phone numbers. Each SIP destination uses these headers unless it sets its own `headers`.

---

**`headers[].name`** `string` — required

The name of the header. Must be a valid SIP header name, 3 to 256 characters long, that either starts with `X-` or is one of `Privacy`, `P-Asserted-Identity`, or `User-to-User`. Names starting with `SignalWire`, `X-SignalWire`, `X-CID`, or `X-SW-Xregion` are reserved and can't be set. A `Privacy` header takes effect only with the value `id`, which hides the caller's number.

---

**`headers[].value`** `string` — required

The value of the header. Can't be empty or contain line breaks.

---

**`connect.max_duration`** `integer` — default: 14400 seconds (4 hours)

Maximum duration, in seconds, allowed for the call.

---

**`connect.result`** `object | object[]`

Action to take based on the result of the call. This will run once the peer leg of the call has ended.

Will use the [`switch properties`](/docs/swml/reference/calling/switch#properties) when the `return_value` is a object, and will use the [`cond properties`](/docs/swml/reference/calling/cond#properties) method when the `return_value` is an array.
See [Variables](#variables) for details.

---

**`connect.ringback`** `boolean | string | string[]` — default: A standard ringback tone

Ringback to play to the caller while phone, SIP, and Resource Address destinations ring. Can be:

* A `play` URI, or an array of `play` URIs, to play as the ringback tone
* `false` to turn off SignalWire's ringback tone and pass the destination's early media (for example, its own ringback or announcements) through to the caller
* `true` to keep the default ringback tone

---

**`connect.session_timeout`** `integer`

SIP `Session-Expires` time, in seconds. Has no effect in this mode: SIP destinations don't use the top-level `session_timeout`, so set `session_timeout` on each SIP destination instead.

---

**`connect.status_url`** `string`

HTTP or HTTPS webhook URL to deliver status events. Reports the connect operation status (connecting, connected, failed, disconnected). See [Connect Status Callbacks](#connect-status-callbacks).

---

**`connect.stop_all_on_reject`** `boolean | string[]` — default: false

Stop ringing and disconnect the caller when a destination rejects the call. Can be either:

* `true` to stop when a destination is busy or declines the call
* A non-empty array of the reasons to stop on: `busy`, `decline`, `noAnswer`

When a destination rejects the call with a matching reason, the destinations ringing alongside it stop ringing. If `connect` then fails with that reason, the `result` block runs first, and then the caller is disconnected.

---

**`connect.timeout`** `integer` — default: 60 seconds

Maximum time, in seconds, to wait for an answer.

---

**`connect.webrtc_media`** `boolean` — default: false

If true, WebRTC media is offered to the SIP endpoint. Has no effect on calls to phone numbers. Can be overwritten on each destination.

---

#### Example

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - connect:
        from: "+15551112222"
        serial:
          - to: "sip:primary@example.com"
            username: "primary_user"
            password: "primary_pw"
          - to: "sip:backup@example.com"
            username: "backup_user"
            password: "backup_pw"
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "connect": {
          "from": "+15551112222",
          "serial": [
            {
              "to": "sip:primary@example.com",
              "username": "primary_user",
              "password": "primary_pw"
            },
            {
              "to": "sip:backup@example.com",
              "username": "backup_user",
              "password": "backup_pw"
            }
          ]
        }
      }
    ]
  }
}
```

#### Serial Parallel

Combine both strategies. The outer array is the **serial** dimension — groups are tried one at a time, in order. Each inner array is the **parallel** dimension — all destinations in that group are dialed simultaneously. If no destination answers in the first group, the next group is attempted.

**`connect.serial_parallel`** `object[][]` — required

Array of arrays combining both strategies. The outer array is the **serial** dimension — each element is a group tried in order. Each inner array is the **parallel** dimension — all destinations in that group are dialed simultaneously. If no destination in the current group answers, the next group is attempted.

In the `[][]` notation below, the first `[]` is the serial (group) index and the second `[]` is the parallel (destination) index within that group.

Must contain at least one destination across all groups: an empty group is skipped, and `connect` fails if every group is empty. A `queue:` or `call:` destination can't be combined with any other destination, and a `stream:` destination can't be combined with a phone, SIP, Resource Address, or queue destination: `connect` fails in either case. If several `stream:` destinations are listed, only the first is used. To connect to a queue, a call, or a stream, use a single `to` instead (see the **Single** tab).

> **20-destination limit**
>
> Up to 20 destinations are dialed in total, counted across all groups rather than per group. With three groups of eight destinations, the first two groups ring in full (16 destinations), the third group rings only its first four, and its last four never ring. `connect` reports no error for skipped destinations. To reach more, see [Dial more than 20 destinations](#dial-more-than-20-destinations).

---

**`serial_parallel[][].to`** `string` — required

Destination to dial. Can be:

* Phone number in E.164 format, including the leading `+` (e.g., `+15552345678`)
* [SIP URI](/docs/platform/voice/sip), with a `sip:` or `sips:` prefix (e.g., `sip:alice@example.com`)
* [Resource Address](/docs/platform/addresses) (e.g., `/public/test_room`)
* Queue (e.g., `queue:support`)
* Call in progress (e.g., `call:ba79c846-4834-42b9-9cd3-2f87c30f2972`)
* WebSocket stream, using `wss://` (e.g., `stream:wss://example.com/audio`)

See the **Single** tab for the format rules of each destination type.

---

**`serial_parallel[][].from`** `string`

Caller ID number. Overrides the top-level `from`. Accepts the same formats as the top-level `from`.

---

**`serial_parallel[][].from_name`** `string`

The caller ID name shown to this destination. Overrides the top-level `from_name`. Applies to SIP calls only. Use 1 to 70 characters after variable expansion: letters, digits, spaces, and `_`, `.`, `-`, `+`, or `,`.

---

**`serial_parallel[][].username`** `string`

SIP authentication username for this destination. **Only applies to SIP URI targets.**

---

**`serial_parallel[][].password`** `string`

SIP authentication password for this destination. **Only applies to SIP URI targets.**

---

**`serial_parallel[][].timeout`** `integer` — default: Inherits the top-level timeout, then 60 seconds

Maximum time, in seconds, to wait for this destination to answer. Overrides the top-level `timeout`.

---

**`serial_parallel[][].call_state_events`** `string[]` — default: Inherits the top-level call_state_events, then \['ended']

An array of call state event names to be notified about. Overrides the top-level `call_state_events`. Each item can also be a SWML variable that resolves to one of these names. Not allowed when `to` starts with `queue:`, `call:`, or `stream:`.

---

**`serial_parallel[][].call_state_url`** `string`

Webhook url to send call state change notifications to for this destination. Overrides the top-level `call_state_url`. Not allowed when `to` starts with `queue:`, `call:`, or `stream:`.

---

**`serial_parallel[][].confirm`** `string | object[]`

Confirmation script to execute on this destination when answered. Overrides the top-level `confirm`. An inline array is limited to the same methods as the top-level `confirm`.

---

**`serial_parallel[][].confirm_timeout`** `integer`

Seconds allowed for the `confirm` SWML to run on this destination. Overrides the top-level `confirm_timeout`. When neither is set, this destination's `timeout` is used.

---

**`serial_parallel[][].encryption`** `string`

Media encryption (SRTP) for this destination. Overrides the top-level `encryption`, which is used when this is not set. **Applies to SIP destinations only.**
Possible values: `mandatory`, `optional`, `forbidden`.

---

**`serial_parallel[][].headers`** `object[]`

Custom SIP headers to add to INVITE for this destination. Replaces the top-level `headers` for this destination. **Applies to SIP destinations only.**

---

**`serial_parallel[][].headers[].name`** `string` — required

The name of the header. Must be a valid SIP header name, 3 to 256 characters long, that either starts with `X-` or is one of `Privacy`, `P-Asserted-Identity`, or `User-to-User`. Names starting with `SignalWire`, `X-SignalWire`, `X-CID`, or `X-SW-Xregion` are reserved and can't be set. A `Privacy` header takes effect only with the value `id`, which hides the caller's number.

---

**`serial_parallel[][].headers[].value`** `string` — required

The value of the header. Can't be empty or contain line breaks.

---

**`serial_parallel[][].codecs`** `string | string[]`

Codecs to offer to this destination, as a comma-separated string or an array of strings, using the same codec names as the top-level `codecs`. Overrides the top-level `codecs`. **Applies to SIP destinations only.**

---

**`serial_parallel[][].webrtc_media`** `boolean`

If true, WebRTC media is offered to this destination. Overrides the top-level `webrtc_media`, which is used when this is not set. **Applies to SIP destinations only.**

---

**`serial_parallel[][].session_timeout`** `integer`

Time, in seconds, to set the SIP `Session-Expires` header in INVITE for this destination. Must be a positive, non-zero number. Values from 1 to 15000 take effect; a larger value is accepted but ignored, so the default `Session-Expires` value is used. The top-level `session_timeout` is not used in this mode, so set it on each SIP destination that needs it. **Applies to SIP destinations only.**

---

**`serial_parallel[][].name`** `string`

Stream name identifier. **Applies to stream destinations only.**

---

**`serial_parallel[][].codec`** `string`

Audio codec for the stream. Takes the same values as `connect.codec` on a single stream destination. **Applies to stream destinations only.**

---

**`serial_parallel[][].status_url`** `string`

HTTPS URL to receive status notifications for this stream. Must use `https://`; an `http://` URL is rejected, unlike the top-level `connect.status_url`. See [Stream Status Callbacks](#stream-status-callbacks). **Applies to stream destinations only.**

---

**`serial_parallel[][].status_url_method`** `string`

HTTP method for the stream status webhook. Possible values: `GET`, `POST`. **Applies to stream destinations only.**

---

**`serial_parallel[][].realtime`** `boolean` — default: false

Enables realtime mode for bidirectional audio on the stream, as with `connect.realtime` on a single stream destination. **Applies to stream destinations only.**

---

**`serial_parallel[][].authorization_bearer_token`** `string`

Bearer token for the stream's WebSocket connection, as with `connect.authorization_bearer_token` on a single stream destination. **Applies to stream destinations only.**

---

**`serial_parallel[][].custom_parameters`** `object`

Custom key-value pairs for the stream, as with `connect.custom_parameters` on a single stream destination. Every value must be a string. **Applies to stream destinations only.**

---

**`connect.answer_on_bridge`** `boolean` — default: false

Delay answer until the B-leg answers.

---

**`connect.call_state_events`** `string[]` — default: \['ended']

An array of call state event names to be notified about. Allowed event names are `created`, `ringing`, `answered`, and `ended`. Each item can also be a SWML variable that resolves to one of these names. Can be overwritten on each destination.

---

**`connect.call_state_url`** `string`

Webhook url to send call status change notifications to for every phone, SIP, and Resource Address destination. Can be overwritten on each destination. Authentication can also be set in the url in the format of `username:password@url`. Learn more about [status callbacks][statuscallbacks].

It doesn't apply to destinations whose `to` starts with `queue:`, `call:`, or `stream:`, and those destinations can't set their own `call_state_url` or `call_state_events`.

---

**`connect.codecs`** `string | string[]` — default: Based on SignalWire settings

Codecs to offer, as a comma-separated string (`"PCMU,PCMA"`) or an array of strings (`["PCMU", "PCMA"]`). Supported codecs are `PCMU`, `PCMA`, `OPUS`, `G722`, `G729`, `AMR-WB`, `VP8`, and `H264`. Has no effect on calls to phone numbers. Each SIP destination uses these codecs unless it sets its own `codecs`.

---

**`connect.confirm`** `string | object[]`

Confirmation to execute when the call is connected. Can be either:

* A URL (string) that returns a SWML document
* An array of SWML methods to execute inline

Only these methods are allowed, including inside `cond` and `switch` branches: `cond`, `switch`, `set`, `unset`, `hangup`, `play`, `prompt`, `record`, `record_call`, `stop_record_call`, `tap`, `stop_tap`, `stream`, `stop_stream`, `transcribe`, `transcribe_stop`, `send_digits`, `send_sms`, `denoise`, `stop_denoise`, and `user_event`.

---

**`connect.confirm_timeout`** `integer` — default: Inherits from timeout

Time, in seconds, allowed for the `confirm` SWML to run on the answered destination, whether it is fetched from a URL or given inline.

---

**`connect.encryption`** `string` — default: optional

The encryption method to use for the call. Possible values: `mandatory`, `optional`, `forbidden`.

---

**`connect.from`** `string` — default: Calling party's caller ID number

Caller ID number. Optional. Can be overwritten on each destination. Must be a phone number in E.164 format with the leading `+`, a SIP URI, or a Resource Address; a `queue:`, `call:`, or `stream:` value is rejected.

---

**`connect.from_name`** `string`

The caller ID name shown to the person you're calling, displayed alongside the `from` number (sometimes called CNAM). Applies to SIP calls only — it has no effect on calls to phone numbers. Use 1 to 70 characters after variable expansion: letters, digits, spaces, and `_`, `.`, `-`, `+`, or `,`. Text and variables can be combined, such as `Support ${vars.dept}`. Can be overridden on each destination.

---

**`connect.headers`** `object[]`

Custom SIP headers to add to INVITE. Has no effect on calls to phone numbers. Each SIP destination uses these headers unless it sets its own `headers`.

---

**`headers[].name`** `string` — required

The name of the header. Must be a valid SIP header name, 3 to 256 characters long, that either starts with `X-` or is one of `Privacy`, `P-Asserted-Identity`, or `User-to-User`. Names starting with `SignalWire`, `X-SignalWire`, `X-CID`, or `X-SW-Xregion` are reserved and can't be set. A `Privacy` header takes effect only with the value `id`, which hides the caller's number.

---

**`headers[].value`** `string` — required

The value of the header. Can't be empty or contain line breaks.

---

**`connect.max_duration`** `integer` — default: 14400 seconds (4 hours)

Maximum duration, in seconds, allowed for the call.

---

**`connect.result`** `object | object[]`

Action to take based on the result of the call. This will run once the peer leg of the call has ended.

Will use the [`switch properties`](/docs/swml/reference/calling/switch#properties) when the `return_value` is a object, and will use the [`cond properties`](/docs/swml/reference/calling/cond#properties) method when the `return_value` is an array.
See [Variables](#variables) for details.

---

**`connect.ringback`** `boolean | string | string[]` — default: A standard ringback tone

Ringback to play to the caller while phone, SIP, and Resource Address destinations ring. Can be:

* A `play` URI, or an array of `play` URIs, to play as the ringback tone
* `false` to turn off SignalWire's ringback tone and pass the destination's early media (for example, its own ringback or announcements) through to the caller
* `true` to keep the default ringback tone

---

**`connect.session_timeout`** `integer`

SIP `Session-Expires` time, in seconds. Has no effect in this mode: SIP destinations don't use the top-level `session_timeout`, so set `session_timeout` on each SIP destination instead.

---

**`connect.status_url`** `string`

HTTP or HTTPS webhook URL to deliver status events. Reports the connect operation status (connecting, connected, failed, disconnected). See [Connect Status Callbacks](#connect-status-callbacks).

---

**`connect.stop_all_on_reject`** `boolean | string[]` — default: false

Stop ringing and disconnect the caller when a destination rejects the call. Can be either:

* `true` to stop when a destination is busy or declines the call
* A non-empty array of the reasons to stop on: `busy`, `decline`, `noAnswer`

When a destination rejects the call with a matching reason, the destinations ringing alongside it stop ringing. If `connect` then fails with that reason, the `result` block runs first, and then the caller is disconnected.

---

**`connect.timeout`** `integer` — default: 60 seconds

Maximum time, in seconds, to wait for an answer.

---

**`connect.webrtc_media`** `boolean` — default: false

If true, WebRTC media is offered to the SIP endpoint. Has no effect on calls to phone numbers. Can be overwritten on each destination.

---

#### Example

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - connect:
        from: "+15551112222"
        serial_parallel:
          - - to: "sip:alice@example.com"
              username: "alice_user"
              password: "alice_pw"
            - to: "sip:bob@example.com"
              username: "bob_user"
              password: "bob_pw"
          - - to: "sip:fallback@example.com"
              username: "fb_user"
              password: "fb_pw"
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "connect": {
          "from": "+15551112222",
          "serial_parallel": [
            [
              {
                "to": "sip:alice@example.com",
                "username": "alice_user",
                "password": "alice_pw"
              },
              {
                "to": "sip:bob@example.com",
                "username": "bob_user",
                "password": "bob_pw"
              }
            ],
            [
              {
                "to": "sip:fallback@example.com",
                "username": "fb_user",
                "password": "fb_pw"
              }
            ]
          ]
        }
      }
    ]
  }
}
```

---

## **Variables**

Set by the method:

* **connect_result:** (out) `connected` | `failed`.
* **connect_failed_reason:** (out) Detailed reason for failure.
* **return_value:** (out) Same value as `connect_result`.

> **Variables belong to one leg**
>
> SWML variables live on the leg that set them, for as long as that leg lasts. A document that runs on the leg `connect` dialed, such as a `confirm` script, starts with an empty `vars` and its own `call` object. On the leg that issued `connect`, every variable survives, and `connect_result` is set when the document resumes. For how legs relate, see [Call legs](/docs/platform/voice/call-legs).

## **StatusCallbacks**

> **Status callbacks are advisory**
>
> Status callbacks are asynchronous, best-effort HTTP notifications: delivery can be delayed or fail silently — if your server is unreachable, the callback simply never arrives. Don't gate time-critical or business-critical actions solely on receiving one. Confirm state via the REST API before acting, or use a transport with visible failure modes — see [Status callback reliability](/docs/platform/webhooks#status-callback-reliability).

A POST request will be sent to `call_state_url` with a JSON payload when the call state changes.
Only call state events listed in `call_state_events` will be sent (default: `ended`).

A call state URL can also receive a `calling.call.connect` event. When the call that runs `connect` has its own call state URL, for example because it was itself dialed with a `call_state_url`, and the `connect` fails, SignalWire also sends that URL a `calling.call.connect` event with `connect_state` set to `failed`, regardless of `call_state_events`. That event has the shape described in [Connect Status Callbacks](#connect-status-callbacks).

The fields below describe the `calling.call.state` payload.

**`event_type`** `string`

The type of event: `calling.call.state` for call state changes.

---

**`event_channel`** `string`

The channel for the event, includes the SWML session ID.

---

**`timestamp`** `number`

Unix timestamp (float) when the event was generated.

---

**`project_id`** `string`

The project ID associated with the call.

---

**`space_id`** `string`

The Space ID associated with the call.

---

**`params`** `object`

An object containing call state parameters.

---

**`params.call_id`** `string`

The call ID.

---

**`params.node_id`** `string`

The node handling the call.

---

**`params.segment_id`** `string`

The segment ID for the call leg. Present when a segment ID has been assigned.

---

**`params.tag`** `string`

The tag associated with the call. Present when a tag has been set.

---

**`params.call_state`** `string`

The current call state. **Valid values:** `created`, `ringing`, `answered`, `ended`.

---

**`params.parent`** `object`

The leg's parent call. Present when the leg has a parent call.

---

**`parent.device_type`** `string`

The device type of the parent call.

---

**`parent.call_id`** `string`

The parent call's ID.

---

**`parent.node_id`** `string`

The node handling the parent call.

---

**`params.peer`** `object`

The leg's peer call. Present when the leg has a peer.

---

**`peer.call_id`** `string`

The peer call's ID.

---

**`peer.node_id`** `string`

The node handling the peer call.

---

**`params.direction`** `string`

The direction of the call leg (e.g., `outbound`).

---

**`params.device`** `object`

Details about the device involved in the call.

---

**`device.type`** `string`

The type of device: `phone`, `sip`, or `webrtc`.

---

**`device.params.from_number`** `string`

The originating phone number. Present for `phone` devices.

---

**`device.params.to_number`** `string`

The destination phone number. Present for `phone` devices.

---

**`device.params.from`** `string`

The originating address. Present for `sip` and `webrtc` devices.

---

**`device.params.to`** `string`

The destination address. Present for `sip` and `webrtc` devices.

---

**`device.params.headers`** `object[]`

SIP headers recorded for the device, each with a `name` and a `value`. Present for some `phone` and `sip` devices.

---

**`params.end_reason`** `string`

The reason the call ended (only present when `call_state` is `ended`). Possible values include `hangup`, `cancel`, `busy`, `noAnswer`, `decline`, `error`, `abandoned`, `maxDuration`, and `notFound`; which ones occur depends on how the call ended.

---

**`params.end_source`** `string`

Which side ended the call: `inbound`, `outbound`, or `none`. Present together with `end_reason`.

---

**`params.dial_winner`** `string`

The string `"true"` when this leg was the destination that answered a dial. Absent otherwise.

---

**`params.sip_data`** `object`

SIP details for the leg. Present for `sip` devices while SIP information is available. Each field is present only when its value is known.

---

**`sip_data.sip_req_user`** `string`

User part of the SIP Request-URI. `sip_data.sip_req_uri` and `sip_data.sip_req_host` hold the full Request-URI and its host.

---

**`sip_data.sip_from_user`** `string`

User part of the SIP `From` header. `sip_data.sip_from_uri` and `sip_data.sip_from_host` hold the full URI and its host.

---

**`sip_data.sip_to_user`** `string`

User part of the SIP `To` header. `sip_data.sip_to_uri` and `sip_data.sip_to_host` hold the full URI and its host.

---

**`sip_data.sip_contact_user`** `string`

User part of the SIP `Contact` header. `sip_data.sip_contact_uri`, `sip_data.sip_contact_host`, and `sip_data.sip_contact_port` hold the full URI, its host, and its port (as a string).

---

**`sip_data.sip_p_asserted_identity`** `string`

The SIP `P-Asserted-Identity` header value.

---

**`sip_data.sip_from_params`** `object`

Parameters of the SIP `From` header, as string key-value pairs. `sip_data.sip_to_params`, `sip_data.sip_contact_params`, and `sip_data.sip_req_params` hold the parameters of the `To` header, the `Contact` header, and the Request-URI.

---

**`params.address_id`** `string`

The ID of the Resource Address involved in the call. Present when known.

---

**`params.subscriber_id`** `string`

The ID of the subscriber involved in the call. Present when known.

---

**`params.subscriber_name`** `string`

The name of the subscriber involved in the call. Present when known.

---

**`params.start_time`** `number`

When the call leg was created, in milliseconds since the Unix epoch. `0` when not available.

---

**`params.answer_time`** `number`

When the call leg was answered, in milliseconds since the Unix epoch. `0` when not available.

---

**`params.end_time`** `number`

When the call leg ended, in milliseconds since the Unix epoch. `0` when not available.

---

**`params.audio_in_mos`** `number`

Estimated audio quality (mean opinion score) of the audio received on the leg. Present when available.

---

### Raw JSON example

```json
{
  "event_type": "calling.call.state",
  "event_channel": "swml:xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "timestamp": 1640000000.123,
  "project_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "space_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "params": {
    "call_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "node_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "call_state": "answered",
    "direction": "outbound",
    "device": {
      "type": "phone",
      "params": {
        "from_number": "+15551231234",
        "to_number": "+15553214321"
      }
    },
    "start_time": 1639999995000,
    "answer_time": 1640000000000,
    "end_time": 0
  }
}
```

---

## **Connect Status Callbacks**

When you provide a top-level `status_url`, SignalWire sends HTTP POST requests reporting the overall status of the connect operation.

**`event_type`** `string`

The type of event. Always `calling.call.connect` for connect status events.

---

**`event_channel`** `string`

The channel for the event, includes the SWML session ID.

---

**`timestamp`** `number`

Unix timestamp (float) when the event was generated.

---

**`project_id`** `string`

The project ID associated with the call.

---

**`space_id`** `string`

The Space ID associated with the call.

---

**`params`** `object`

An object containing connect status parameters.

---

**`params.call_id`** `string`

The call ID.

---

**`params.node_id`** `string`

The node handling the call.

---

**`params.segment_id`** `string`

The segment ID for the call leg. Present when a segment ID has been assigned.

---

**`params.tag`** `string`

The tag associated with the call. Present when a tag has been set.

---

**`params.connect_state`** `string`

The current connect state. Possible values:

* `connecting` — Attempting to connect
* `connected` — Successfully connected
* `failed` — Connection failed
* `disconnected` — Connection ended

---

**`params.failed_reason`** `string`

The reason the connection failed. Only present when `connect_state` is `failed`. Uses the same values as the call state `end_reason`, for example `busy`, `decline`, `noAnswer`, `notFound` (the queue is empty or doesn't exist), or `error`.

---

**`params.peer`** `object`

Details about the peer. Present whenever peer information is available, which includes `connected` events and can include `disconnected` events.

---

**`peer.call_id`** `string`

The peer's call ID.

---

**`peer.tag`** `string`

The tag associated with the peer call. Present when a tag has been set on the peer.

---

**`peer.node_id`** `string`

The node ID of the node handling this call.

---

**`peer.queue_id`** `string`

The queue ID when the peer was connected via a queue. Only present for queue-based connections.

---

**`peer.queue_name`** `string`

The queue name when the peer was connected via a queue. Only present for queue-based connections.

---

**`peer.device`** `object`

Details about the peer's device.

---

### Raw JSON example

```json
{
  "event_type": "calling.call.connect",
  "event_channel": "swml:xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "timestamp": 1640000000.123,
  "project_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "space_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "params": {
    "call_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "node_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "connect_state": "connected",
    "peer": {
      "call_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "node_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "device": {
        "type": "phone",
        "params": {
          "from_number": "+15551231234",
          "to_number": "+15553214321"
        }
      }
    }
  }
}
```

#### Failed state example

```json
{
  "event_type": "calling.call.connect",
  "event_channel": "swml:xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "timestamp": 1640000000.123,
  "project_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "space_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "params": {
    "call_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "node_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "connect_state": "failed",
    "failed_reason": "noAnswer"
  }
}
```

---

## **Stream Status Callbacks**

When connecting to a WebSocket stream destination with a `status_url`, SignalWire sends HTTP requests reporting the stream status.

**`event_type`** `string`

The type of event. Always `calling.call.stream` for stream status events.

---

**`event_channel`** `string`

The channel for the event, includes the SWML session ID.

---

**`timestamp`** `number`

Unix timestamp (float) when the event was generated.

---

**`project_id`** `string`

The project ID associated with the call.

---

**`space_id`** `string`

The Space ID associated with the call.

---

**`params`** `object`

An object containing stream status parameters.

---

**`params.call_id`** `string`

The call ID.

---

**`params.node_id`** `string`

The node handling the call.

---

**`params.segment_id`** `string`

The segment ID for the call leg. Present when a segment ID has been assigned.

---

**`params.tag`** `string`

The tag associated with the call. Present when a tag has been set.

---

**`params.control_id`** `string`

The control identifier for the stream.

---

**`params.state`** `string`

The current stream state. Possible values:

* `streaming` — Stream is active
* `finished` — Stream has ended

---

**`params.url`** `string`

The WebSocket URL of the stream.

---

**`params.name`** `string`

The stream name, if one was provided.

---

### Raw JSON example

```json
{
  "event_type": "calling.call.stream",
  "event_channel": "swml:xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "timestamp": 1640000000.123,
  "project_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "space_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "params": {
    "call_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "node_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "control_id": "xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "state": "streaming",
    "url": "wss://example.com/audio",
    "name": "my-stream"
  }
}
```

---

## **Examples**

### Use `connect` with a Resource Address

Connect to a [Resource](/docs/platform/resources) by using its [Address](/docs/platform/addresses) as the `to` value.

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - play:
        volume: 10
        urls:
          - 'silence:1.0'
          - 'say:Hello, connecting to a fabric Resource that is a room'
    - connect:
        to: /public/test_room
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "answer": {}
      },
      {
        "play": {
          "volume": 10,
          "urls": [
            "silence:1.0",
            "say:Hello, connecting to a fabric Resource that is a room"
          ]
        }
      },
      {
        "connect": {
          "to": "/public/test_room"
        }
      }
    ]
  }
}
```

### Dial a single phone number

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - connect:
        from: "+15553214321"
        to: "+15551231234"
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "connect": {
          "from": "+15553214321",
          "to": "+15551231234"
        }
      }
    ]
  }
}
```

### Play a country ringtone while the destination rings

Set `answer_on_bridge` to `true` so the caller's leg isn't answered until the destination picks up, and use `ringback` to play the UK ringtone in place of the default tone. The ringtone repeats until the call connects. See [playable sounds](/docs/swml/reference/calling/play#playable-sounds) for the other ringtones and sounds you can use.

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - connect:
        answer_on_bridge: true
        ringback:
          - "ring:uk"
        from: "+15553214321"
        to: "+15551231234"
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "connect": {
          "answer_on_bridge": true,
          "ringback": ["ring:uk"],
          "from": "+15553214321",
          "to": "+15551231234"
        }
      }
    ]
  }
}
```

### Dial numbers in parallel

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - connect:
        parallel:
          - to: "+15551231234"
          - to: "+15553214321"
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "connect": {
          "parallel": [
            {
              "to": "+15551231234"
            },
            {
              "to": "+15553214321"
            }
          ]
        }
      }
    ]
  }
}
```

### Dial more than 20 destinations

To reach more than 20 destinations, split them into batches of up to 20 and start the next batch from the `result` block when `connect_result` is `failed`. The batches ring one after another: the second batch starts only after the first batch's `timeout` expires with no answer. Put the destinations most likely to answer in the first batch.

This example shows two destinations per batch to keep it short. Each `parallel` array can hold up to 20.

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - connect:
        timeout: 20
        parallel:
          - to: "+15551110001"
          - to: "+15551110002"
        result:
          case:
            failed:
              - connect:
                  timeout: 20
                  parallel:
                    - to: "+15551110021"
                    - to: "+15551110022"
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "connect": {
          "timeout": 20,
          "parallel": [
            {
              "to": "+15551110001"
            },
            {
              "to": "+15551110002"
            }
          ],
          "result": {
            "case": {
              "failed": [
                {
                  "connect": {
                    "timeout": 20,
                    "parallel": [
                      {
                        "to": "+15551110021"
                      },
                      {
                        "to": "+15551110022"
                      }
                    ]
                  }
                }
              ]
            }
          }
        }
      }
    ]
  }
}
```

### Dial SIP serially with a timeout

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - connect:
        timeout: 20
        serial:
          - from: "sip:chris@example.com"
            to: "sip:alice@example.com"
          - to: "sip:bob@example.com"
            codecs: PCMU
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "connect": {
          "timeout": 20,
          "serial": [
            {
              "from": "sip:chris@example.com",
              "to": "sip:alice@example.com"
            },
            {
              "to": "sip:bob@example.com",
              "codecs": "PCMU"
            }
          ]
        }
      }
    ]
  }
}
```

### Set the caller ID name on SIP legs

Set `from_name` at the top level so every device inherits it, then override it on a single destination. `agent1` sees the caller ID name "Support Team" (inherited); `agent2` sees "Billing Dept" (overridden).

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - connect:
        from: "+15551000001"
        from_name: "Support Team"
        serial:
          - to: "sip:agent1@pbx.example.com"
          - to: "sip:agent2@pbx.example.com"
            from_name: "Billing Dept"
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "connect": {
          "from": "+15551000001",
          "from_name": "Support Team",
          "serial": [
            {
              "to": "sip:agent1@pbx.example.com"
            },
            {
              "to": "sip:agent2@pbx.example.com",
              "from_name": "Billing Dept"
            }
          ]
        }
      }
    ]
  }
}
```

### Connect to a queue

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - connect:
        to: "queue:support"
        execute_after_queue: "https://example.com/post-call-swml"
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "connect": {
          "to": "queue:support",
          "execute_after_queue": "https://example.com/post-call-swml"
        }
      }
    ]
  }
}
```

### Connect to a call in progress

Set `to` to `call:` followed by a call ID to bridge the caller to a call that is already in
progress. The call must belong to the same project, can't be the call running `connect`, and can't
be a call controlled by cXML. A `call:` destination must be the only destination, and `call_state_url` and `call_state_events` aren't allowed with it. When the
call can't be bridged, for example because it has already ended, `connect` fails and sets
`connect_result` to `failed`.

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - connect:
        to: "call:ba79c846-4834-42b9-9cd3-2f87c30f2972"
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "connect": {
          "to": "call:ba79c846-4834-42b9-9cd3-2f87c30f2972"
        }
      }
    ]
  }
}
```

### Connect to a WebSocket stream

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - connect:
        to: "stream:wss://example.com/audio"
        codec: PCMU
        realtime: true
        name: my-stream
        status_url: "https://example.com/stream-status"
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "answer": {}
      },
      {
        "connect": {
          "to": "stream:wss://example.com/audio",
          "codec": "PCMU",
          "realtime": true,
          "name": "my-stream",
          "status_url": "https://example.com/stream-status"
        }
      }
    ]
  }
}
```