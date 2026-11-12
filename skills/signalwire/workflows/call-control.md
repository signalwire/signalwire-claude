# Call Control

## Overview

Control active calls with transfer, recording, conferencing, and real-time manipulation using SWML methods or Relay.

**Relay call control is reachable over plain HTTP** — `POST /api/calling/calls` with `{"command": "...", "id": "<call-uuid>", "params": {...}}`. No persistent WebSocket is required; the SDK examples below are one way to reach the same commands, not the only way. See [Calling Commands over HTTP](fabric-relay.md#calling-commands-over-http).

## Transfer Methods

**Connect limits.** Phone numbers need a leading `+`. `parallel`, `serial`, and `serial_parallel` dial at most 20 destinations in total (a deployment default); extras never ring and `connect` reports no error. Relay `dial` / `call.connect` skip devices past the same cap and report each as `Too many devices` in `message_data`. A `queue:` or `call:` destination can't be mixed with others, and once a queued call is bridged the script does not continue past `connect` (`connect_result` is `failed` when nothing was bridged). `ringback: false` passes the destination's early media. See [swml-methods.md](swml-methods.md#connect).

### Blind Transfer (SWML)

Transfer call without announcement:

```yaml
- connect:
    to: "+15551234567"
    from: "+15559876543"
```

### Attended Transfer (SWML)

Announce before transferring:

```yaml
- play:
    url: "say:Please hold while I transfer you"
- connect:
    to: "+15551234567"
    timeout: 30
- cond:
    - when: "connect_result == 'failed'"
      then:
        - play: { url: "say:Transfer failed. Please try again later" }
        - hangup: {}
```

### Transfer with Screening

```yaml
- play:
    url: "say:Transferring you now"
- connect:
    to: "+15551234567"
    ringback:
      - "https://example.com/hold-music.mp3"
```

### Section Transfer

Transfer to another SWML section:

```yaml
sections:
  main:
    - prompt:
        play: "say:Press 1 for sales"
        max_digits: 1
    - switch:
        variable: prompt_value
        case:
          "1":
            - transfer: { dest: sales_dept }

  sales_dept:
    - play: { url: "say:Welcome to sales" }
    - connect: { to: "+15551111111" }
```

### In-Session Transfer from a SWAIG Function (Agents SDK)

Inside a live AI session, execute transfers with the SDK's `connect()` helper rather than injecting a document that contains a `connect` verb:

```python
return FunctionResult(
    "Connecting you now.",
    post_process=True
).connect("tel:+15551234567", final=True)
```

An injected document containing `connect` only succeeds when the action carries the `transfer` flag **beside** the SWML document — the shape both `connect()` and `execute_swml(doc, transfer=True)` emit. If the flag ends up *inside* the document (for example, in hand-built action JSON), the platform ignores it, so the nested `connect` fast-fails — `connect_result=failed` within seconds, no B-leg dialed — while the identical document works at the top level of a call.

## Recording

### Record Entire Call (SWML)

```yaml
- answer: {}
- record_call:
    stereo: true
    format: "mp3"
- play:
    url: "say:This call is being recorded"
```

**Parameters**:
- `stereo`: `true` = each side on separate channel
- `format`: `mp3` or `wav`

Recording URL sent to webhook when call ends.

### Record Message/Voicemail (SWML)

```yaml
- play:
    url: "say:Please leave a message after the beep"
- play:
    url: "https://example.com/beep.mp3"
- record:
    max_length: 120
    end_silence_timeout: 3
    beep: false
```

**Parameters**:
- `max_length`: Maximum seconds to record
- `end_silence_timeout`: Stop after N seconds of silence
- `beep`: Play beep before recording (default: `true`)

### Recording with Relay SDK (Python)

```python
from signalwire.relay.consumer import Consumer

class CallRecorder(Consumer):
    async def on_incoming_call(self, call):
        await call.answer()
        await call.play_tts(text="This call will be recorded")

        # Start recording
        recording = await call.record_async(
            stereo=True,
            format='mp3'
        )

        # Continue with call...
        await call.play_tts(text="How can I help you?")

        # Stop recording when done
        await recording.stop()
        recording_url = recording.url
        print(f"Recording saved: {recording_url}")
```

### Recording with Relay SDK (Node.js)

```javascript
const { SignalWire } = require('@signalwire/realtime-api');

client.on('call.received', async (call) => {
  await call.answer();
  await call.playTTS({ text: 'Recording started' });

  const recording = await call.recordAsync({
    stereo: true,
    format: 'mp3'
  });

  // Your call logic here...

  await recording.stop();
  console.log(`Recording URL: ${recording.url}`);
});
```

## Conferencing

### Simple Conference (SWML)

```yaml
- play:
    url: "say:Joining conference room"
- join_conference:
    name: "my-conference"
    muted: false
    beep: true
```

**Parameters**:
- `name`: Conference name (creates if doesn't exist)
- `muted`: Join with mic muted (default: `false`)
- `beep`: Beep on join/leave (`true`, `false`, `onEnter`, `onExit`)

### Conference with PIN (SWML)

```yaml
sections:
  main:
    - answer: {}
    - prompt:
        play: "say:Please enter your conference PIN"
        max_digits: 4
    - switch:
        variable: prompt_value
        case:
          "1234":
            - transfer: { dest: valid_conference }
        default:
          - play: { url: "say:Invalid PIN" }
          - hangup: {}

  valid_conference:
    - play: { url: "say:Joining conference" }
    - join_conference:
        name: "secure-meeting"
```

### Moderator vs Participant

```yaml
# Moderator - with min_participants 1, the conference starts when they join and ends when they leave.
# min_participants is fixed when the conference is created, so the participant join sets it too.
- join_conference:
    name: "meeting-123"
    start_on_enter: true
    end_on_exit: true
    min_participants: 1

# Participant - hears hold music until a start_on_enter participant joins
- join_conference:
    name: "meeting-123"
    start_on_enter: false
    min_participants: 1
```

## Real-Time Call Control with Relay SDK

### Python: Mid-Call Actions

```python
from signalwire.relay.consumer import Consumer

class CallController(Consumer):
    async def on_incoming_call(self, call):
        await call.answer()

        # Play greeting
        await call.play_tts(text="Welcome to our service")

        # Collect input
        result = await call.prompt(
            type='digits',
            text='Press 1 to continue',
            max_digits=1,
            timeout=10
        )

        if result.digits == '1':
            # Transfer to agent
            await call.connect([['+15551234567']])
        else:
            # Play voicemail message
            await call.play_audio('https://example.com/voicemail.mp3')

            # Start recording
            recording = await call.record_async(max_length=120)
            await recording.stop()

            # Send notification
            print(f"Voicemail recorded: {recording.url}")

        await call.hangup()
```

### JavaScript: Call State Management

```javascript
const { SignalWire } = require('@signalwire/realtime-api');

async function handleCall() {
  const client = await SignalWire({
    project: process.env.SIGNALWIRE_PROJECT_ID,
    token: process.env.SIGNALWIRE_API_TOKEN
  });

  client.on('call.received', async (call) => {
    await call.answer();

    // Wait for specific state
    await call.waitFor('answered');

    // Play audio
    await call.playAudio({
      url: 'https://example.com/greeting.mp3'
    });

    // Collect DTMF digits
    const collect = await call.promptTTS({
      text: 'Press 1 for sales, 2 for support',
      digits: {
        max: 1,
        timeout: 5
      }
    });

    switch (collect.digits) {
      case '1':
        await call.connectPhone({ to: '+15551111111' });
        break;
      case '2':
        await call.connectPhone({ to: '+15552222222' });
        break;
      default:
        await call.playTTS({ text: 'Invalid selection' });
        await call.hangup();
    }
  });

  await client.connect();
}
```

## Call Queuing

### Queue Pattern (SWML)

For real hold queues with agents dequeuing callers, use the `enter_queue` method — see [swml-methods.md](swml-methods.md#enter_queue). The pattern below is a lightweight alternative that bridges directly with ring feedback:

```yaml
sections:
  main:
    - answer: {}
    - play:
        url: "say:All agents are busy. Please hold."
    - connect:
        to: "+15551234567"
        timeout: 300  # 5 min timeout
        ringback:  # Hold music while dialing
          - "https://example.com/hold-music.mp3"
          - "say:Your call is important to us. Please continue holding."
    - cond:
        - when: "connect_result == 'failed'"
          then:
            - transfer: { dest: voicemail }

  voicemail:
    - play: { url: "say:Please leave a message" }
    - record: { max_length: 120 }
```

## Call Forwarding

### Unconditional Forward (SWML)

```yaml
- answer: {}
- connect:
    to: "+15559876543"
```

### Conditional Forward (SWML)

```yaml
- answer: {}
- connect:
    to: "+15551234567"
    timeout: 20
- cond:
    - when: "connect_result == 'failed'"
      then:
        - play: { url: "say:Forwarding to mobile" }
        - connect:
            to: "+15559876543"
            timeout: 20
        - cond:
            - when: "connect_result == 'failed'"
              then:
                - transfer: { dest: voicemail }
```

### Sequential Forward (Try Multiple Numbers)

```yaml
sections:
  main:
    - answer: {}
    - connect:
        timeout: 20
        serial:  # Try each destination in order
          - to: "+15551111111"  # Office
          - to: "+15552222222"  # Mobile
    - cond:
        - when: "connect_result == 'failed'"
          then:
            - transfer: { dest: voicemail }

  voicemail:
    - play: { url: "say:Please leave a message" }
    - record: {}
```

## Mute/Unmute

### Relay SDK (Python)

```python
# Mute the call
await call.mute()

# Unmute
await call.unmute()
```

### Relay SDK (JavaScript)

```javascript
// Mute
await call.mute();

// Unmute
await call.unmute();
```

## Call State Monitoring

### Python: Event Handlers

```python
from signalwire.relay.consumer import Consumer

class CallMonitor(Consumer):
    async def on_incoming_call(self, call):
        # Register event handlers
        call.on('state_change', self.on_state_change)
        call.on('ended', self.on_call_ended)

        await call.answer()

    async def on_state_change(self, call):
        print(f"Call state changed to: {call.state}")

    async def on_call_ended(self, call):
        print(f"Call ended. Duration: {call.duration}s")
```

### JavaScript: Event Listeners

```javascript
call.on('state.changed', (call) => {
  console.log(`Call state: ${call.state}`);
});

call.on('ended', (call) => {
  console.log(`Call ended. Duration: ${call.duration}s`);
});
```

### Listing Active Calls (REST)

To enumerate live calls — for example, a cleanup job that ends stale calls — use the **Voice Logs API**. The logs are historical voice activity — calls handled by cXML, SWML, and the Calling API — for usage reporting, billing review, and troubleshooting, not live call control. Finding calls still in progress there is observed behavior. The Compatibility API's `GET /Calls` does NOT return SWML/AI call data.

```
GET https://{space}.signalwire.com/api/voice/logs
```

Each log entry includes the call's `status` (e.g. `in-progress`, `completed`) and an `id` — that `id` is the call ID accepted by the Send Call Commands API (`POST /api/calling/calls`), including `calling.end`.

The endpoint supports only date filters, pagination, and an `include_deleted` flag — no server-side status filter — so filter on `status` client-side.

```python
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta, timezone

auth = HTTPBasicAuth(project_id, api_token)
space_url = "https://your-space.signalwire.com"

# List voice logs; filter client-side (no server-side status filter).
# NOTE: results are paginated (page_size defaults to 50) —
# iterate pages for a complete sweep
logs = requests.get(f"{space_url}/api/voice/logs", auth=auth).json()['data']

# Live = any non-terminal status; stale = live AND older than the
# longest call you consider legitimate. Without the age check this
# would hang up healthy in-progress calls.
TERMINAL = ('completed', 'ended', 'busy', 'failed', 'no-answer', 'canceled')
cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
stale = [log for log in logs
         if log['status'] not in TERMINAL
         and datetime.fromisoformat(log['created_at'].replace('Z', '+00:00')) < cutoff]

# End each stale call using the log's id as the call ID
for log in stale:
    requests.post(
        f"{space_url}/api/calling/calls",
        auth=auth,
        json={
            "command": "calling.end",
            "id": log['id'],
            "params": {"reason": "hangup"}
        }
    )
```

Compatibility entries (`type: laml_call`) carry audio quality stats as top-level fields, each `null` when the call has no measurement for it. `audio_in_mos` is a decimal string from about 1 to 4.5. 4.5 is the best score. A call that received no audio also scores 4.5, so check `audio_in_media_packet_count` too. `audio_rtt_avg`, `audio_rtt_min`, and `audio_rtt_max` are milliseconds, in steps of 10. Inbound jitter (`audio_in_jitter_min`, `audio_in_jitter_max`) is milliseconds squared; outbound jitter (`audio_out_jitter_min`, `audio_out_jitter_max`, `audio_out_jitter_avg`) is milliseconds. Entries also include packet counts and `audio_out_lost` (outbound packets lost). `audio_out_packet_count` is not populated (always `null`); use `audio_out_media_packet_count`. `audio_in_largest_jb_size` is not populated (always `0` when the call has quality statistics).

Relay entries (`relay_pstn_call`, `relay_sip_call`, `relay_webrtc_call`) carry a `qos_metrics` object with only the measured stats, or `null` when the call has no quality measurement. It never includes `audio_in_mos` (kept in its own column), and its keys differ from the Compatibility field names. Use these on completed calls when troubleshooting audio quality; stats for calls still in progress may be `null`.

## Common Call States

A placed call moves through `queued`, `initiated`, `created`, `ringing`, `answered`, `ending`, and `ended`. It can skip some, such as `answered`. `ended` is the final status of every call that was placed, however it ended. The cause is `end_reason` on the `ended` call state callback, for example `busy` or `noAnswer`.

`failed`, `canceled`, and `completed` are outcomes for a call that was never placed. No call state callback is sent for them, whatever `status_events` lists.

- **queued**: Accepted and waiting to be placed
- **initiated**: SignalWire has started placing the call
- **created**: Set up and being placed
- **ringing**: Ringing at the destination
- **answered**: Answered and in progress
- **ending**: Hanging up, on the way to `ended`
- **ended**: Ended, however it ended. Read `end_reason` on the `ended` callback
- **failed**: Could not be placed (destination blocked, call flagged as spam, no registered SIP endpoint, or a temporary error)
- **canceled**: Canceled with the `update` command while still `queued`
- **completed**: Ended with the `update` command while still `queued`

`status: canceled` is valid only while the call is `queued` or `ringing`. Canceling a `ringing` call, or completing a call that has been placed, hangs it up and the status becomes `ended`. A `url` or `swml` redirect is valid only while `answered`. A call whose status is `failed`, `canceled`, or `completed` cannot be updated.

### Disconnect vs. End

Two commands sound alike and behave very differently:

- `calling.disconnect` — **unbridges** connected legs. Nothing hangs up: both legs stay active (and billing) until `max_duration`, a remote hangup, or an explicit end.
- `calling.end` — actually hangs up, with a `reason`. RELAY (Python): `await call.hangup(reason="hangup")`. REST (Python): `client.calling.end(call_id, reason="hangup")`.

Cleanup jobs and reapers must use `calling.end`, never `disconnect`. To enumerate the live SWML/AI calls to end, use the List Voice Logs API — its log `id` is the call ID `calling.end` accepts. (In the raw REST command payload, the call `id` rides at the root of the command object, not in `params` — distinct from the SDK method signatures shown here.)

## Advanced Patterns

### Warm Transfer (Announcement Before Connect)

```python
async def warm_transfer(call, agent_number):
    # Put caller on hold with music
    play_task = call.play_audio('https://example.com/hold.mp3')

    # Call the agent
    agent_call = await client.calling.dial(
        from_number='+15551234567',
        to_number=agent_number
    )

    await agent_call.wait_for_answered()

    # Announce to agent
    await agent_call.play_tts(text="Incoming transfer from customer")

    # Stop hold music
    await play_task.stop()

    # Connect both parties
    await call.connect([agent_call])
```

### Call Whisper (Agent Hears Announcement, Caller Doesn't)

`confirm` runs on the leg `connect` dialed. That document starts with empty `vars` and its own `call` (`call_id`, `from`, `to`, and `direction` for that leg; a B-leg has `parent` and usually `peer` pointing at the A-leg). A-leg `vars` such as `%{vars.caller_name}` are empty there. Use `%{call.from}`, embed the values when you build the A-leg document, or set `confirm` to a URL that looks the caller up by `call.parent` or `call.peer`. The leg that issued `connect` keeps its vars across the bridge. SignalWire clears `call.peer` when that document resumes, so code after `connect` must not rely on it. Docs: https://signalwire.com/docs/platform/voice/call-legs

```yaml
- connect:
    to: "+15551234567"
    from: "%{call.from}"
    answer_on_bridge: true
    confirm:  # Runs on the dialed leg before bridging — caller doesn't hear it
      - play:
          url: "say:This is a sales call from %{call.from}"
```

### Call Screening with Accept/Reject

```yaml
- play:
    url: "say:Connecting you now"
- connect:
    to: "+15551234567"
    confirm:  # Screening script runs on the answered leg
      - prompt:
          play: "say:Press 1 to accept this call"
          max_digits: 1
- cond:
    - when: "connect_result == 'failed'"
      then:
        - transfer: { dest: voicemail }
```

## Error Handling

### Timeout Handling

```yaml
- connect:
    to: "+15551234567"
    timeout: 30
- cond:
    - when: "connect_result == 'failed'"
      then:
        - play:
            url: "say:The person you're trying to reach is unavailable"
        - transfer: { dest: voicemail }
```

### Busy Signal Handling

```yaml
- connect:
    to: "+15551234567"
- cond:
    - when: "connect_failed_reason == 'busy'"
      then:
        - play:
            url: "say:The line is busy. Please try again later"
        - hangup: {}
```

## Performance Tips

1. **Use timeouts**: Always set reasonable timeout values
2. **Provide feedback**: Tell callers what's happening ("Transferring you now...")
3. **Handle failures**: Always check `connect_result` after every `connect`
4. **Optimize hold music**: Use compressed, looping audio files
5. **Monitor call quality**: Track dropped calls and connection failures

## Context Preservation Strategies

### The Problem with Traditional Transfers

Traditional systems lose context during transfers:
1. Caller provides information to IVR
2. Gets transferred to agent
3. Agent has no context - caller repeats everything

**Statistics:**
- 72% of customers expect agents to know who they are
- Customers are 4x more likely to leave after poor transfer experience

### SignalWire's Context-Aware Transfers

**Pattern: Collect and Forward Context**

```yaml
# AI collects information
- ai:
    prompt:
      text: |
        Gather: customer name, phone, issue description
        After gathering, call the send_to_agent function
    SWAIG:
      functions:
        - function: send_to_agent
          purpose: "Send gathered context to the agent dashboard"
          web_hook_url: "https://yourserver.com/context-transfer"
          argument:
            type: object
            properties:
              customer_name:
                type: string
              customer_phone:
                type: string
              issue_summary:
                type: string

# Then transfer
- connect:
    to: "sip:agent@yourspace.signalwire.com"
```

**Server sends context to agent's browser:**

```javascript
// SWAIG function sends data to agent dashboard
app.post('/context-transfer', (req, res) => {
  const { argument: args } = req.body;

  // Send context to agent's WebSocket dashboard
  agentDashboard.send({
    type: 'incoming_call',
    customer_name: args.customer_name,
    customer_phone: args.customer_phone,
    issue: args.issue_summary,
    conversation: req.body.conversation
  });

  // Return to continue call flow
  res.json({
    response: "Transferring you to an agent who can help"
  });
});
```

### Screen Pop Implementation

**WebSocket to Agent Dashboard:**

```javascript
// Agent dashboard receives context before call connects
ws.on('message', (data) => {
  const context = JSON.parse(data);

  // Display before answering
  showCallerContext({
    name: context.customer_name,
    phone: context.customer_phone,
    issue: context.issue_summary,
    aiTranscript: context.conversation
  });
});
```

**Benefits:**
- Agent sees information before answering
- Informed decision to accept/route call
- Immediate context without asking
- Complete AI conversation history

### Call Variables for Context

**Pass data through this leg.** `%{vars.*}` below expands on the leg that issues `connect`. `confirm` on the dialed leg starts with empty `vars`.

```yaml
- ai:
    prompt:
      text: "Verify customer identity"
    SWAIG:
      functions:
        - function: verify_identity
          purpose: "Verify the caller's identity"
          web_hook_url: "https://yourserver.com/verify"

# After verification, set variables
- set:
    caller_verified: true
    account_id: "12345"
    issue_type: "technical"
    customer_tier: "premium"

# Available in subsequent steps
- cond:
    - when: "caller_verified == true"
      then:
        - connect:
            to: "sip:%{vars.customer_tier}-support@yourspace.signalwire.com"
            headers:  # Custom SIP headers (SIP destinations only)
              - name: "X-Account-ID"
                value: "%{vars.account_id}"
              - name: "X-Issue-Type"
                value: "%{vars.issue_type}"
              - name: "X-Customer-Tier"
                value: "%{vars.customer_tier}"
```

## Advanced Transfer Patterns

### Warm Transfer with Context

**Announce to agent before connecting caller:**

```python
async def warm_transfer_with_context(call, agent_number, context):
    # Put caller on hold with music
    play_task = call.play_audio('https://example.com/hold.mp3')

    # Call the agent
    agent_call = await client.calling.dial(
        from_number='+15551234567',
        to_number=agent_number
    )

    await agent_call.wait_for_answered()

    # Announce to agent with context
    await agent_call.play_tts(text=f"""
        Incoming transfer from {context['name']}.
        Account number {context['account']}.
        Issue: {context['issue']}.
        Press 1 to accept, 2 to send to voicemail.
    """)

    # Collect agent's response
    result = await agent_call.prompt(type='digits', max_digits=1)

    if result.digits == '1':
        # Stop hold music
        await play_task.stop()

        # Connect both parties
        await call.connect([agent_call])
    else:
        # Agent declined, send to voicemail
        await agent_call.hangup()
        await play_task.stop()
        await call.transfer_to_voicemail()
```

### Call Whisper (Agent Hears, Caller Doesn't)

```yaml
- connect:
    to: "+15551234567"
    from: "%{call.from}"
    answer_on_bridge: true
    # Dialed leg starts with empty vars. This URL is fetched for that leg;
    # look the caller up from call.parent or call.peer. See Call Whisper above.
    confirm: "https://yourserver.com/agent-whisper"
```

### Call Screening with Accept/Reject

```yaml
- play:
    url: "say:Please hold while we locate an agent"
- connect:
    to: "+15551234567"
    confirm:  # Screening script runs on the answered leg; it does not need A-leg vars
      - prompt:
          play: "say:You have an incoming call. Press 1 to accept"
          max_digits: 1
- cond:
    - when: "connect_result == 'failed'"
      then:
        - transfer: { dest: voicemail }
```

## Recording Best Practices

### When to Use Stereo Recording

**Use stereo recording when:**
- Need to separate caller and agent for analysis
- Performing speech analytics
- Training purposes (isolate agent performance)
- Quality assurance

```yaml
- record_call:
    stereo: true
    format: "mp3"
```

**Result:**
- Left channel: Caller audio
- Right channel: Agent/system audio
- Easier post-processing and analysis

### Recording with Compliance

**Always announce recording:**

```yaml
- play:
    url: "say:This call may be recorded for quality assurance and training purposes"
- prompt:
    play: "say:Press 1 to consent to recording, or hang up if you do not wish to be recorded"
    max_digits: 1
- cond:
    - when: "prompt_value == '1'"
      then:
        - record_call: { stereo: true, format: "mp3" }
        - transfer: { dest: main_menu }
    - else:
        - hangup: {}
```

### Recording Notifications

**Send recording URL via webhook:**

```yaml
- record_call:
    stereo: true
    format: "mp3"
    status_url: "https://yourserver.com/recording-complete"
```

**Server receives:**

```json
{
  "recording_url": "https://example.signalwire.com/recordings/abc123.mp3",
  "recording_duration": "120",
  "call_id": "call-xyz789",
  "from": "+15559876543",
  "to": "+15551234567"
}
```

## Conference Management Patterns

### Moderator-Controlled Conference

```yaml
sections:
  main:
    - answer: {}
    - prompt:
        play: "say:Enter your PIN followed by the pound sign"
        max_digits: 6
        terminators: "#"
    - switch:
        variable: prompt_value
        case:
          "1234":
            - transfer: { dest: moderator_conference }
          "5678":
            - transfer: { dest: participant_conference }
        default:
          - play: { url: "say:Invalid PIN" }
          - hangup: {}

  moderator_conference:
    - play: { url: "say:Welcome moderator. You may start the conference." }
    - join_conference:
        name: "meeting-%{call.to}"
        start_on_enter: true
        end_on_exit: true
        muted: false
        min_participants: 1

  participant_conference:
    - play: { url: "say:Welcome to the conference. Please wait for the moderator." }
    - join_conference:
        name: "meeting-%{call.to}"
        start_on_enter: false
        muted: false
        min_participants: 1
```

### Dynamic Conference Naming

**Use caller-specific conference rooms:**

```yaml
# Create unique conference per account
- join_conference:
    name: "support-%{vars.account_id}"

# Or use the call ID for one-time conferences
- join_conference:
    name: "meeting-%{call.call_id}"
```

## Error Handling Patterns

### Timeout Handling with Escalation

```yaml
sections:
  main:
    - connect:
        to: "+15551234567"
        timeout: 30
    - cond:
        - when: "connect_result == 'failed'"
          then:
            # Try backup number
            - transfer: { dest: try_backup }

  try_backup:
    - play: { url: "say:That agent is unavailable. Trying another agent." }
    - connect:
        to: "+15552222222"
        timeout: 30
    - cond:
        - when: "connect_result == 'failed'"
          then:
            # Escalate to supervisor
            - transfer: { dest: try_supervisor }

  try_supervisor:
    - play: { url: "say:Connecting you with a supervisor" }
    - connect:
        to: "+15553333333"
        timeout: 30
    - cond:
        - when: "connect_result == 'failed'"
          then:
            # Final fallback
            - transfer: { dest: voicemail }
```

### Connect Failure Reason Handling

**Handle all possible outcomes** by branching on `connect_result` and `connect_failed_reason`:

```yaml
- connect:
    to: "+15551234567"
    timeout: 30
- cond:
    - when: "connect_result == 'connected'"
      then:
        - hangup: {}
- switch:
    variable: connect_failed_reason
    case:
      no_answer:
        - play: { url: "say:No answer. Leaving voicemail." }
        - transfer: { dest: voicemail }
      busy:
        - play: { url: "say:Line is busy. Leaving voicemail." }
        - transfer: { dest: voicemail }
      declined:
        - play: { url: "say:Call was declined. Leaving voicemail." }
        - transfer: { dest: voicemail }
    default:
      - play: { url: "say:System error. Leaving voicemail." }
      - transfer: { dest: voicemail }
```

## Anti-Patterns to Avoid

### 1. Losing Context on Transfer

❌ **Wrong:**
```yaml
- ai:
    prompt:
      text: "Collect customer information"
# Transfer without passing context
- connect: { to: "+15551234567" }
```

✅ **Right:**
```yaml
- ai:
    prompt:
      text: "Collect customer information"
    SWAIG:
      functions:
        - function: prepare_transfer
          purpose: "Send collected context to the agent"
          web_hook_url: "https://yourserver.com/send-context"
# Context sent to agent before connection
- connect: { to: "+15551234567" }
```

### 2. Silent Transfers

❌ **Wrong:**
```yaml
- connect: { to: "+15551234567" }
```

✅ **Right:**
```yaml
- play: { url: "say:Please hold while I transfer you to sales. This may take up to 30 seconds." }
- connect:
    to: "+15551234567"
    timeout: 30
- cond:
    - when: "connect_result == 'failed'"
      then:
        - play: { url: "say:I'm sorry, that transfer failed. Let me try another option." }
```

### 3. Recording Without Consent

❌ **Wrong:**
```yaml
- answer: {}
- record_call: { stereo: true }
# Start recording without notification
```

✅ **Right:**
```yaml
- answer: {}
- play:
    url: "say:This call will be recorded"
- record_call: { stereo: true }
```

### 4. Not Handling Transfer Failures

❌ **Wrong:**
```yaml
- connect: { to: "+15551234567" }
# No failure check - caller hears silence
```

✅ **Right:**
```yaml
- connect:
    to: "+15551234567"
    timeout: 30
- cond:
    - when: "connect_result == 'failed'"
      then:
        - play: { url: "say:Transfer failed. Leaving voicemail." }
        - transfer: { dest: voicemail }
    - else:
        - hangup: {}
```

## Production Tips

### 1. Always Set Timeouts

**Specify reasonable timeout values:**

```yaml
# Good - explicit timeout
- connect:
    to: "+15551234567"
    timeout: 30  # 30 seconds

# Bad - no timeout (uses system default, may be too long)
- connect:
    to: "+15551234567"
```

**Recommended timeouts:**
- Internal transfers: 20-30 seconds
- External transfers: 30-45 seconds
- Queue/hold: 5 minutes max

### 2. Provide Hold Music

**Use looping, compressed audio:**

```yaml
- play:
    url: "https://cdn.example.com/hold-music-loop.mp3"
```

**Best practices:**
- Use MP3 at 64-128 kbps
- Create seamless loops (fade in/out)
- Keep file size small (<1MB)
- Host on CDN for reliability

### 3. Monitor Call Quality

**Track key metrics:**
- Dropped call rate
- Transfer success rate
- Average hold time
- Recording failure rate
- Conference connection issues

**Dashboard > Relay > Activity:**
- Filter by call state
- Check for failed transfers
- Identify problematic numbers

### 4. Test Transfer Scenarios

**Test all paths:**
- Successful transfer
- Busy signal
- No answer
- Call declined
- Network error
- Invalid number

**Use test numbers to simulate:**
```
+15005550001 - Generates busy signal
+15005550002 - Generates no answer
+15005550003 - Generates invalid number
```

### 5. Optimize Recording Storage

**Recording management:**
- Set retention policies
- Archive old recordings
- Compress before long-term storage
- Use webhooks to process recordings asynchronously

```javascript
// Webhook handler for recording completion
app.post('/recording-complete', async (req, res) => {
  const { recording_url, call_id } = req.body;

  // Download recording
  const audioFile = await downloadRecording(recording_url);

  // Process (transcribe, analyze, etc.)
  const transcription = await transcribeAudio(audioFile);

  // Store in database with metadata
  await db.recordings.create({
    call_id,
    url: recording_url,
    transcription,
    timestamp: new Date()
  });

  res.sendStatus(200);
});
```

## Real-World Examples

### Example 1: Customer Service with Smart Routing

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - ai:
        prompt:
          text: |
            Collect customer name, account number, and reason for calling.
            Determine if this is: billing, technical support, or sales.
        SWAIG:
          functions:
            - function: lookup_account
              purpose: "Look up the customer's account"
              web_hook_url: "https://yourserver.com/account"
            - function: determine_routing
              purpose: "Record the department to route to"
              web_hook_url: "https://yourserver.com/route"

    # Context stored in variables by the SWAIG functions
    - switch:
        variable: vars.department
        case:
          billing:
            - transfer: { dest: billing_transfer }
          technical:
            - transfer: { dest: tech_transfer }
        default:
          - transfer: { dest: sales_transfer }

  billing_transfer:
    - play: { url: "say:Transferring you to billing. They'll have your account information." }
    - connect:
        to: "sip:billing@yourspace.signalwire.com"
        headers:  # Custom SIP headers (SIP destinations only)
          - name: "X-Account-ID"
            value: "%{vars.account_id}"
          - name: "X-Customer-Name"
            value: "%{vars.customer_name}"

  tech_transfer:
    - play: { url: "say:Connecting you with technical support." }
    - connect: { to: "sip:tech@yourspace.signalwire.com" }

  sales_transfer:
    - play: { url: "say:Connecting you with sales." }
    - connect: { to: "sip:sales@yourspace.signalwire.com" }
```

### Example 2: Recorded Conference with Participants

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - play:
        url: "say:Welcome to the conference call. This call will be recorded."
    - record_call:
        stereo: true
        format: "mp3"
        status_url: "https://yourserver.com/recording"

    - play:
        url: "say:Please say your name after the beep"
    - record:  # Name recording available at %{record_url}
        beep: true
        max_length: 5
        end_silence_timeout: 2
    - play: { url: "say:Thank you. Joining the conference now." }
    - join_conference:
        name: "weekly-standup"
```

## Next Steps

- [Voice AI](voice-ai.md) - Add AI agents to calls
- [Webhooks & Events](webhooks-events.md) - Track call events
- [Fabric & Relay](fabric-relay.md) - Advanced real-time control
