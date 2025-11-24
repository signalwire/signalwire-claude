# Call Control

## Overview

Control active calls with transfer, recording, conferencing, and real-time manipulation using SWML methods or Relay SDK.

## Transfer Methods

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
- say:
    text: "Please hold while I transfer you"
- connect:
    to: "+15551234567"
    timeout: 30
  on_failure:
    - say: { text: "Transfer failed. Please try again later" }
    - hangup: {}
```

### Transfer with Screening

```yaml
- say:
    text: "Transferring you now"
- connect:
    to: "+15551234567"
    ringback:
      - play:
          url: "https://example.com/hold-music.mp3"
```

### Section Transfer

Transfer to another SWML section:

```yaml
sections:
  main:
    - prompt:
        say: "Press 1 for sales"
        max_digits: 1
      on_success:
        - transfer: { dest: sales_dept }

  sales_dept:
    - say: { text: "Welcome to sales" }
    - connect: { to: "+15551111111" }
```

## Recording

### Record Entire Call (SWML)

```yaml
- answer: {}
- record_call:
    stereo: true
    format: "mp3"
- say:
    text: "This call is being recorded"
```

**Parameters**:
- `stereo`: `true` = each side on separate channel
- `format`: `mp3` or `wav`

Recording URL sent to webhook when call ends.

### Record Message/Voicemail (SWML)

```yaml
- say:
    text: "Please leave a message after the beep"
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
- say:
    text: "Joining conference room"
- join_room:
    name: "my-conference"
    muted: false
    deaf: false
```

**Parameters**:
- `name`: Conference room name (creates if doesn't exist)
- `muted`: Join with mic muted (default: `false`)
- `deaf`: Can't hear others (default: `false`)

### Conference with PIN (SWML)

```yaml
sections:
  main:
    - answer: {}
    - prompt:
        say: "Please enter your conference PIN"
        max_digits: 4
      on_success:
        - switch:
            variable: "%{args.result}"
            case:
              "1234":
                - transfer: { dest: valid_conference }
              default:
                - say: { text: "Invalid PIN" }
                - hangup: {}

  valid_conference:
    - say: { text: "Joining conference" }
    - join_room:
        name: "secure-meeting"
```

### Moderator vs Participant

```yaml
# Moderator
- join_room:
    name: "meeting-123"
    moderator: true
    start_conference_on_enter: true
    end_conference_on_exit: true

# Participant
- join_room:
    name: "meeting-123"
    moderator: false
    wait_for_moderator: true
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

```yaml
sections:
  main:
    - answer: {}
    - say:
        text: "All agents are busy. Please hold."
    - execute:
        dest: play_hold_music
    - connect:
        to: "+15551234567"
        timeout: 300  # 5 min timeout
      on_failure:
        - transfer: { dest: voicemail }

  play_hold_music:
    - play:
        url: "https://example.com/hold-music.mp3"
    - say:
        text: "Your call is important to us. Please continue holding."
    - execute:
        dest: play_hold_music  # Loop

  voicemail:
    - say: { text: "Please leave a message" }
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
  on_failure:
    - say: { text: "Forwarding to mobile" }
    - connect:
        to: "+15559876543"
        timeout: 20
      on_failure:
        - transfer: { dest: voicemail }
```

### Sequential Forward (Try Multiple Numbers)

```yaml
sections:
  main:
    - answer: {}
    - execute: { dest: try_office }

  try_office:
    - connect:
        to: "+15551111111"
        timeout: 20
      on_failure:
        - execute: { dest: try_mobile }

  try_mobile:
    - connect:
        to: "+15552222222"
        timeout: 20
      on_failure:
        - transfer: { dest: voicemail }

  voicemail:
    - say: { text: "Please leave a message" }
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

## Common Call States

- **created**: Call has been created
- **ringing**: Destination is ringing
- **answered**: Call was answered
- **ended**: Call has terminated
- **busy**: Destination is busy
- **failed**: Call failed to connect
- **no-answer**: Destination didn't answer

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

```yaml
- connect:
    to: "+15551234567"
    caller_id: "%{call.from}"
    answer_on_bridge: true
    whisper:
      say: "This is a sales call from %{call.from}"
```

### Call Screening with Accept/Reject

```yaml
- say:
    text: "Connecting you now"
- connect:
    to: "+15551234567"
    confirm:
      say: "Press 1 to accept this call, 2 to send to voicemail"
      digit: "1"
  on_failure:
    - transfer: { dest: voicemail }
```

## Error Handling

### Timeout Handling

```yaml
- connect:
    to: "+15551234567"
    timeout: 30
  on_failure:
    - say:
        text: "The person you're trying to reach is unavailable"
    - transfer: { dest: voicemail }
```

### Busy Signal Handling

```yaml
- connect:
    to: "+15551234567"
  on_failure:
    - say:
        text: "The line is busy. Please try again later"
    - hangup: {}
```

## Performance Tips

1. **Use timeouts**: Always set reasonable timeout values
2. **Provide feedback**: Tell callers what's happening ("Transferring you now...")
3. **Handle failures**: Always have `on_failure` handlers
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
    prompt: |
      Gather: customer name, phone, issue description
      After gathering, call send_to_agent function
    functions:
      - name: send_to_agent
        web_hook: "https://yourserver.com/context-transfer"
        parameters:
          - name: customer_name
          - name: customer_phone
          - name: issue_summary

# Then transfer
- connect:
    to: "agent@yourspace.signalwire.com"
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

**Pass data through the call:**

```yaml
- ai:
    prompt: "Verify customer identity"
    functions:
      - name: verify_identity
        web_hook: "https://yourserver.com/verify"

# After verification, set variables
- set:
    caller_verified: true
    account_id: "12345"
    issue_type: "technical"
    customer_tier: "premium"

# Available in subsequent steps
- condition:
    if: "{{caller_verified}} == true"
    then:
      - connect:
          to: "{{customer_tier}}-support@yourspace.signalwire.com"
          headers:
            X-Account-ID: "{{account_id}}"
            X-Issue-Type: "{{issue_type}}"
            X-Customer-Tier: "{{customer_tier}}"
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
    caller_id: "{{call.from}}"
    answer_on_bridge: true
    whisper:
      say: "Incoming call from {{caller_name}}, account {{account_id}}, issue type: {{issue_type}}"
```

### Call Screening with Accept/Reject

```yaml
- say:
    text: "Please hold while we locate an agent"
- connect:
    to: "+15551234567"
    confirm:
      say: "You have an incoming call from {{caller_name}}. Press 1 to accept, 2 to send to voicemail, 3 to send to another agent"
      digit: "1"
  on_failure:
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
    bargeable: false  # Force caller to hear it
- prompt:
    type: digits
    say: "Press 1 to consent to recording, or hang up if you do not wish to be recorded"
    max_digits: 1
  on_success:
    - condition:
        if: "{{args.result}} == '1'"
        then:
          - record_call: { stereo: true, format: "mp3" }
          - transfer: { dest: main_menu }
        else:
          - hangup: {}
  on_failure:
    - hangup: {}
```

### Recording Notifications

**Send recording URL via webhook:**

```yaml
- record_call:
    stereo: true
    format: "mp3"
    status_callback: "https://yourserver.com/recording-complete"
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
        say: "Enter your PIN followed by the pound sign"
        max_digits: 6
        terminators: "#"
      on_success:
        - switch:
            variable: "{{args.result}}"
            case:
              "1234":
                - transfer: { dest: moderator_conference }
              "5678":
                - transfer: { dest: participant_conference }
              default:
                - say: { text: "Invalid PIN" }
                - hangup: {}

  moderator_conference:
    - say: { text: "Welcome moderator. You may start the conference." }
    - join_room:
        name: "meeting-{{call.to}}"
        moderator: true
        start_conference_on_enter: true
        end_conference_on_exit: true
        muted: false

  participant_conference:
    - say: { text: "Welcome to the conference. Waiting for the moderator." }
    - join_room:
        name: "meeting-{{call.to}}"
        moderator: false
        wait_for_moderator: true
        muted: false
        start_muted: false
```

### Dynamic Conference Naming

**Use caller-specific conference rooms:**

```yaml
# Create unique room per account
- join_room:
    name: "support-{{account_id}}"
    moderator: false

# Or use timestamp for one-time conferences
- join_room:
    name: "meeting-{{call.timestamp}}"
```

## Error Handling Patterns

### Timeout Handling with Escalation

```yaml
- connect:
    to: "+15551234567"
    timeout: 30
  on_failure:
    # Try backup number
    - say: { text: "That agent is unavailable. Trying another agent." }
    - connect:
        to: "+15552222222"
        timeout: 30
      on_failure:
        # Escalate to supervisor
        - say: { text: "Connecting you with a supervisor" }
        - connect:
            to: "+15553333333"
            timeout: 30
          on_failure:
            # Final fallback
            - transfer: { dest: voicemail }
```

### Forward Node Error Handling

**Handle all possible outcomes:**

```yaml
- forward:
    to: "+15551234567"
    timeout: 30
    paths:
      success:
        - hangup: {}
      no_answer:
        - say: { text: "No answer. Leaving voicemail." }
        - transfer: { dest: voicemail }
      busy:
        - say: { text: "Line is busy. Leaving voicemail." }
        - transfer: { dest: voicemail }
      declined:
        - say: { text: "Call was declined. Leaving voicemail." }
        - transfer: { dest: voicemail }
      error:
        - say: { text: "System error. Leaving voicemail." }
        - transfer: { dest: voicemail }
```

## Anti-Patterns to Avoid

### 1. Losing Context on Transfer

❌ **Wrong:**
```yaml
- ai:
    prompt: "Collect customer information"
# Transfer without passing context
- connect: { to: "+15551234567" }
```

✅ **Right:**
```yaml
- ai:
    prompt: "Collect customer information"
    functions:
      - name: prepare_transfer
        web_hook: "https://yourserver.com/send-context"
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
- say: { text: "Please hold while I transfer you to sales. This may take up to 30 seconds." }
- connect:
    to: "+15551234567"
    timeout: 30
  on_failure:
    - say: { text: "I'm sorry, that transfer failed. Let me try another option." }
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
    bargeable: false
- record_call: { stereo: true }
```

### 4. Not Handling Transfer Failures

❌ **Wrong:**
```yaml
- connect: { to: "+15551234567" }
# No on_failure handler - caller hears silence
```

✅ **Right:**
```yaml
- connect:
    to: "+15551234567"
    timeout: 30
  on_success:
    - hangup: {}
  on_failure:
    - say: { text: "Transfer failed. Leaving voicemail." }
    - transfer: { dest: voicemail }
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
        prompt: |
          Collect customer name, account number, and reason for calling.
          Determine if this is: billing, technical support, or sales.
        functions:
          - name: lookup_account
            web_hook: "https://yourserver.com/account"
          - name: determine_routing
            web_hook: "https://yourserver.com/route"

    # Context stored in metadata
    - condition:
        if: "{{metadata.department}} == 'billing'"
        then:
          - transfer: { dest: billing_transfer }
        else:
          - condition:
              if: "{{metadata.department}} == 'technical'"
              then:
                - transfer: { dest: tech_transfer }
              else:
                - transfer: { dest: sales_transfer }

  billing_transfer:
    - say: { text: "Transferring you to billing. They'll have your account information." }
    - connect:
        to: "billing@yourspace.signalwire.com"
        headers:
          X-Account-ID: "{{metadata.account_id}}"
          X-Customer-Name: "{{metadata.customer_name}}"

  tech_transfer:
    - say: { text: "Connecting you with technical support." }
    - connect: { to: "tech@yourspace.signalwire.com" }

  sales_transfer:
    - say: { text: "Connecting you with sales." }
    - connect: { to: "sales@yourspace.signalwire.com" }
```

### Example 2: Recorded Conference with Participants

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - say:
        text: "Welcome to the conference call. This call will be recorded."
    - record_call:
        stereo: true
        format: "mp3"
        status_callback: "https://yourserver.com/recording"

    - prompt:
        say: "Please say your name after the beep"
        record: true
        max_length: 5
      on_success:
        - say: { text: "Thank you. Joining the conference now." }
        - join_room:
            name: "weekly-standup"
            moderator: false
            announce_name: "{{args.recording_url}}"
```

## Next Steps

- [Voice AI](voice-ai.md) - Add AI agents to calls
- [Webhooks & Events](webhooks-events.md) - Track call events
- [Fabric & Relay](fabric-relay.md) - Advanced real-time control
