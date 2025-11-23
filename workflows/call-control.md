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

## Next Steps

- [Voice AI](voice-ai.md) - Add AI agents to calls
- [Webhooks & Events](webhooks-events.md) - Track call events
- [Fabric & Relay](fabric-relay.md) - Advanced real-time control
