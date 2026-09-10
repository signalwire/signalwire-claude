# Inbound Call Handling

## Overview

Handle incoming calls using SWML (SignalWire Markup Language) - a declarative YAML or JSON document that defines call flow and behavior.

## SWML Basics

### What is SWML?

SWML is a markup and scripting language for building communication applications without writing procedural code. It's designed for:
- Voice call handling (IVR systems)
- Conversational AI
- Call routing and transfer
- Recording and transcription
- Integration with external APIs

### Formats

SWML supports both **YAML** and **JSON**:

```yaml
# YAML format (more readable)
version: 1.0.0
sections:
  main:
    - answer: {}
    - play:
        url: "say:Hello from SignalWire"
```

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      { "answer": {} },
      { "play": { "url": "say:Hello from SignalWire" } }
    ]
  }
}
```

### Basic Structure

Every SWML document must have:

1. **Version**: Always `1.0.0` (currently the only supported version)
2. **Sections**: Named blocks of methods (like functions)
3. **Main section**: Required - where execution starts

```yaml
version: 1.0.0
sections:
  main:
    - method1: {}
    - method2:
        param: value

  another_section:
    - method3: {}
```

## Serving SWML

### Option 1: HTTP Endpoint

SignalWire fetches your SWML document via HTTP GET.

```python
# Flask example
from flask import Flask, jsonify
import yaml

app = Flask(__name__)

@app.route('/swml')
def serve_swml():
    swml = {
        "version": "1.0.0",
        "sections": {
            "main": [
                {"answer": {}},
                {"play": {"url": "say:Welcome to our service"}}
            ]
        }
    }
    return jsonify(swml)  # JSON response

# Or serve YAML
@app.route('/swml.yaml')
def serve_swml_yaml():
    swml = """
version: 1.0.0
sections:
  main:
    - answer: {}
    - play:
        url: "say:Welcome to our service"
    """
    return swml, 200, {'Content-Type': 'text/yaml'}
```

Configure this URL in your phone number settings or pass as `url` parameter when making calls.

### Option 2: Relay SDK (Inline SWML)

Send SWML directly via Relay WebSocket:

```python
from signalwire.relay.consumer import Consumer

class MyConsumer(Consumer):
    async def on_incoming_call(self, call):
        swml = {
            "version": "1.0.0",
            "sections": {
                "main": [
                    {"play": {"url": "say:Hello from Relay"}}
                ]
            }
        }
        await call.send_swml(swml)
```

### Option 3: Dashboard (Serverless)

Deploy SWML directly in SignalWire Dashboard:
1. Go to **SWML Scripts** in Dashboard
2. Create new script
3. Paste your SWML
4. Assign to phone number or AI agent

## Core SWML Methods

### answer

Answer an incoming call.

```yaml
- answer: {}
```

**Note**: Usually the first method for inbound calls. Not needed for outbound calls (auto-answered).

### play

Play audio file.

```yaml
- play:
    url: "https://example.com/audio/greeting.mp3"

# Or play multiple files
- play:
    urls:
      - "https://example.com/beep.mp3"
      - "https://example.com/message.mp3"
```

**Supported formats**: MP3, WAV, OGG

### Text-to-speech (say: URLs)

There is no separate `say` method in SWML. Text-to-speech is done with `play` using the `say:` URL prefix.

```yaml
- play:
    url: "say:Welcome to SignalWire"
    say_language: "en-US"
    say_gender: "female"

# With variable substitution
- play:
    url: "say:You called from %{call.from}"
```

**Properties**:
- `url`: `say:<text to speak>`
- `say_voice`: Voice to use (e.g., `gcloud.en-US-Neural2-A`)
- `say_language`: Voice language (e.g., `en-US`)
- `say_gender`: `male` or `female`

**`play` and `prompt` do not share the AI agent's voice default.** They resolve voices through a separate mapping table and land on a different default than `ai`, which uses ElevenLabs "Mark". Set `say_voice` explicitly rather than assuming either default carries over — see [Voice AI](voice-ai.md#voice-selection).

Other playable sound prefixes: `silence:<seconds>` and `ring:[duration:]<country code>`.

### prompt

Play audio/TTS and collect user input.

```yaml
- prompt:
    play: "say:Press 1 for sales, 2 for support"
    max_digits: 1
    terminators: "#"
    digit_timeout: 5.0
```

**Properties**:
- `play`: A playable sound (audio URL, `say:` text, `silence:`, `ring:`) or an array of them
- `max_digits`: Maximum digits to collect
- `terminators`: Digits that end input
- `digit_timeout`: Seconds to wait for the next digit
- `initial_timeout`: Seconds to wait for input to start
- `speech_timeout`, `speech_end_timeout`, `speech_language`, `speech_hints`: setting any of these enables speech recognition

**Accessing result**:

`prompt` sets output variables when it completes:
- `prompt_result`: `failed`, `no_input`, `match_speech`, `match_digits`, or `no_match`
- `prompt_value`: the digits or utterance collected
- `prompt_digit_terminator`: terminator digit collected, if any
- `prompt_speech_confidence`: speech confidence measured, if any

```yaml
- prompt:
    play: "say:Enter your account number"
    max_digits: 6
- execute:
    dest: process_input
    params:
      digits: "%{prompt_value}"
```

Result available in `%{prompt_value}`.

### connect

Connect caller to a phone number or SIP endpoint.

```yaml
- connect:
    to: "+15551234567"
    from: "+15559876543"
    timeout: 30

# Or connect to SIP
- connect:
    to: "sip:user@example.sip.signalwire.com"
```

**Properties**:
- `to`: Destination number or SIP address
- `from`: Caller ID to display
- `timeout`: Ring timeout in seconds

`connect` sets `connect_result` (`connected` or `failed`) and `connect_failed_reason` — branch on these with `cond` or `switch`.

### transfer

Transfer call to another SWML section (permanently).

```yaml
sections:
  main:
    - prompt:
        play: "say:Press 1 for sales, 2 for support"
        max_digits: 1
    - switch:
        variable: prompt_value
        case:
          "1":
            - transfer:
                dest: sales
          "2":
            - transfer:
                dest: support

  sales:
    - play:
        url: "say:Transferring to sales"
    - connect:
        to: "+15551111111"

  support:
    - play:
        url: "say:Transferring to support"
    - connect:
        to: "+15552222222"
```

### execute

Call another section like a function (returns after completion).

```yaml
sections:
  main:
    - execute:
        dest: play_greeting
    - play:
        url: "say:What can I help you with?"

  play_greeting:
    - play:
        url: "https://example.com/greeting.mp3"
    - return: {}  # Return to caller
```

### hangup

End the call.

```yaml
- hangup: {}
```

### record_call

Start recording the call.

```yaml
- record_call:
    stereo: true
    format: "mp3"
```

**Properties**:
- `stereo`: Record each side on separate channel (default: `false`)
- `format`: `mp3`, `wav` (default: `wav`)
- Recording URL sent to webhook when call ends

### send_sms

Send an SMS during the call.

```yaml
- send_sms:
    to_number: "%{call.from}"
    from_number: "+15551234567"
    body: "Thanks for calling! Here's your confirmation code: 12345"
```

## Variable Substitution

Use `%{variable_name}` or `${variable_name}` to access dynamic values. In Calling documents the two forms are interchangeable for plain paths; `${...}` also evaluates JavaScript expressions.

### Call Variables

```yaml
- play:
    url: "say:You called from %{call.from} to %{call.to}"
```

Available variables:
- `%{call.from}` - Caller's number
- `%{call.to}` - Destination number
- `%{call.call_id}` - Unique call ID
- `%{call.direction}` - `inbound` or `outbound`

### Custom Parameters

Pass parameters when creating call:

```json
{
  "command": "dial",
  "params": {
    "from": "+15551234567",
    "to": "+15559876543",
    "url": "https://example.com/swml",
    "custom_param": "value123"
  }
}
```

Access in SWML:
```yaml
- play:
    url: "say:Your reference is %{params.custom_param}"
```

### Prompt Results

```yaml
- prompt:
    play: "say:Enter your PIN"
    max_digits: 4
- switch:
    variable: prompt_value
    case:
      "1234":
        - play: { url: "say:PIN accepted" }
    default:
      - play: { url: "say:Invalid PIN" }
```

## Control Flow

### switch

Conditional branching based on variable value. `variable` takes the variable name directly (no substitution syntax).

```yaml
- switch:
    variable: prompt_value
    case:
      "1":
        - play: { url: "say:You pressed 1" }
      "2":
        - play: { url: "say:You pressed 2" }
    default:
      - play: { url: "say:Invalid selection" }
```

### cond

Branch on JavaScript conditions. `cond` takes an array of `when`/`then` objects, plus an optional final `else`. Inside `when`, reference variables directly — do not wrap the condition in `${...}`.

SWML methods do not take `on_success`/`on_failure` handlers. Instead, each method sets output variables (`prompt_result`, `connect_result`, `record_result`, etc.) that you branch on with `cond` or `switch`:

```yaml
- prompt:
    play: "say:Press any key"
    max_digits: 1
    digit_timeout: 5.0
- cond:
    - when: "prompt_result == 'no_input'"
      then:
        - play: { url: "say:No input received" }
    - else:
        - play: { url: "say:Thank you" }
```

## Advanced Patterns

### IVR Menu System

Use `label` + `goto` with `max` to cap menu retries.

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - transfer:
        dest: main_menu

  main_menu:
    - label: menu
    - prompt:
        play: "https://example.com/main-menu.mp3"
        max_digits: 1
        digit_timeout: 5.0
    - cond:
        - when: "prompt_result == 'no_input'"
          then:
            - play: { url: "say:Sorry, I didn't catch that" }
            - goto: { label: menu, max: 3 }
    - switch:
        variable: prompt_value
        case:
          "1":
            - transfer: { dest: sales }
          "2":
            - transfer: { dest: support }
          "3":
            - transfer: { dest: billing }
          "9":
            - goto: { label: menu, max: 5 }  # Repeat menu
        default:
          - play: { url: "say:Invalid selection" }
          - goto: { label: menu, max: 3 }
    - play: { url: "say:We were unable to process your selection. Goodbye." }
    - hangup: {}

  sales:
    - play: { url: "say:Connecting you to sales" }
    - connect:
        to: "+15551111111"
        timeout: 30
    - cond:
        - when: "connect_result == 'failed'"
          then:
            - play: { url: "say:Sales is unavailable. Returning to main menu" }
            - transfer: { dest: main_menu }

  support:
    - play: { url: "say:Connecting you to support" }
    - connect: { to: "+15552222222" }

  billing:
    - play: { url: "say:Connecting you to billing" }
    - connect: { to: "+15553333333" }
```

### Voicemail System

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - play:
        url: "say:Please leave a message after the beep"
    - play:
        url: "https://example.com/beep.mp3"
    - record:
        beep: false
        max_length: 120
        end_silence_timeout: 3
    - play:
        url: "say:Thank you for your message"
    - send_sms:
        to_number: "+15551234567"  # Notify admin
        from_number: "%{call.to}"
        body: "New voicemail from %{call.from}"
    - hangup: {}
```

### Call Screening

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - play:
        url: "say:Please say your name after the beep"
    - play: { url: "https://example.com/beep.mp3" }
    - record:
        max_length: 5
        end_silence_timeout: 2
    - play:
        url: "say:Please hold while we connect you"
    - connect:
        to: "+15551234567"
        from: "%{call.from}"
    - cond:
        - when: "connect_result == 'failed'"
          then:
            - transfer: { dest: voicemail }
    - hangup: {}

  voicemail:
    - play: { url: "say:Sorry, that person is unavailable" }
    - hangup: {}
```

### Multi-Language Support

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - prompt:
        play: "say:Press 1 for English, presione 2 para Español"
        max_digits: 1
    - switch:
        variable: prompt_value
        case:
          "1":
            - transfer: { dest: english_menu }
          "2":
            - transfer: { dest: spanish_menu }

  english_menu:
    - play:
        url: "say:Welcome to our service"
        say_language: "en-US"
    - prompt:
        play: "say:Press 1 for sales, 2 for support"
        max_digits: 1

  spanish_menu:
    - play:
        url: "say:Bienvenido a nuestro servicio"
        say_language: "es-MX"
    - prompt:
        play: "say:Presione 1 para ventas, 2 para soporte"
        say_language: "es-MX"
        max_digits: 1
```

## Configuring Phone Numbers

### Dashboard Configuration

1. Go to **Phone Numbers** in Dashboard
2. Select your number
3. Under **Voice Settings**:
   - Set **When a call comes in**: "Request a SWML document from a webhook"
   - Enter your SWML URL: `https://example.com/swml`
4. Save

### Via REST API

```python
import requests
from requests.auth import HTTPBasicAuth

# Update phone number with SWML URL
response = requests.put(
    f"{space_url}/api/laml/2010-04-01/Accounts/{project_id}/IncomingPhoneNumbers/{phone_sid}",
    auth=HTTPBasicAuth(project_id, api_token),
    data={
        "VoiceUrl": "https://example.com/swml",
        "VoiceMethod": "GET"
    }
)
```

## Testing SWML

### Local Development with ngrok

```bash
# Start your local server
python app.py  # Runs on localhost:5000

# In another terminal, expose with ngrok
ngrok http 5000

# Use the ngrok URL in your phone number configuration
# Example: https://abc123.ngrok.io/swml
```

### Test Call Flow

1. Call your SignalWire number
2. Follow the prompts
3. Check SignalWire Dashboard > Logs for debugging
4. Look for SWML fetch logs and execution traces

### Debug with Logging

```python
@app.route('/swml')
def serve_swml():
    # Log incoming request
    print(f"SWML request from: {request.args.get('From')}")
    print(f"To: {request.args.get('To')}")
    print(f"CallSid: {request.args.get('CallSid')}")

    swml = {
        "version": "1.0.0",
        "sections": {
            "main": [
                {"answer": {}},
                {"play": {"url": f"say:Debug: Call from {request.args.get('From')}"}}
            ]
        }
    }
    return jsonify(swml)
```

## Common Errors

### Invalid SWML Structure

**Error**: "Invalid SWML version" or "Missing main section"

**Fix**:
- Ensure `version: 1.0.0` is present
- Verify `main` section exists
- Check YAML/JSON syntax

### Variable Not Found

**Error**: Variable `%{undefined.var}` returns empty string

**Fix**:
- Check variable name spelling
- Ensure variable exists in context
- Use default values when possible

### Timeout Errors

**Error**: Call disconnects unexpectedly

**Fix**:
- Check `timeout` values in `prompt` and `connect`
- Increase `digit_timeout` for slower input
- Branch on result variables (e.g., `prompt_result`, `connect_result`) with `cond` to handle failures

## Performance Best Practices

1. **Cache audio files**: Host on CDN for faster playback
2. **Minimize HTTP requests**: Inline SWML when possible
3. **Use YAML for readability**: Convert to JSON for production if needed
4. **Pre-record prompts**: Better quality than TTS
5. **Handle failures gracefully**: Always provide fallback options

## Best Practices from Production

### SWML Editor Validation

**Always use the SWML Editor for validation:**
- Located in Dashboard > Relay > SWML tab
- Provides real-time validation
- Catches syntax errors before deployment
- Shows errors in red boxes with clear descriptions
- Test your SWML before pointing phone numbers to it

### Keep SWML Simple and Focused

**Good Practice:**
- Use clear, concise instructions
- Avoid overly complex nested structures
- Break complex flows into multiple SWML documents
- Use sections to organize logical workflows

**Example of good structure:**
```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - execute: { dest: greeting }
    - execute: { dest: main_menu }

  greeting:
    - play: { url: "https://example.com/greeting.mp3" }
    - return: {}

  main_menu:
    - prompt:
        play: "say:Press 1 for sales, 2 for support"
        max_digits: 1
```

### Loop Protection Pattern

**Problem:** Input-collection loops can repeat infinitely if the caller never responds.

**Solution:** Use `label` + `goto` with `max` — `goto` stops jumping after `max` attempts (1-100), so the script falls through to your exit path.

```yaml
sections:
  main:
    - answer: {}
    - transfer: { dest: get_input }

  get_input:
    - label: menu
    - prompt:
        play: "say:Press 1 for sales, 2 for support"
        max_digits: 1
    - cond:
        - when: "prompt_result == 'no_input'"
          then:
            - play: { url: "say:We didn't receive any input" }
            - goto: { label: menu, max: 2 }
    - switch:
        variable: prompt_value
        case:
          "1":
            - transfer: { dest: sales }
          "2":
            - transfer: { dest: support }
        default:
          - play: { url: "say:That was not a valid option" }
          - goto: { label: menu, max: 2 }
    - play: { url: "say:We're having trouble understanding your input. Goodbye." }
    - hangup: {}

  sales:
    - connect: { to: "+15551111111" }

  support:
    - connect: { to: "+15552222222" }
```

**Implementation per input-collection point:**
- Use unique label names (`menu1`, `menu2`) for multiple input-collection points
- Set `max` to the maximum retries (typically 2-3)
- Provide helpful feedback before looping
- Always end with hangup after max attempts (the methods after `goto` run once the jump limit is reached)

### Variable Management Best Practices

**Using Variables Effectively:**

```yaml
sections:
  main:
    - answer: {}
    # Set variables for reuse
    - set:
        movie1: "Mean Girls plays at 12:45, 2:15, and 5:00"
        movie2: "Godfather plays at 1:45, 3:25, and 6:00"
        movie3: "Batman plays at 12:30, 1:30, and 5:45"
        business_phone: "+15551234567"

    - prompt:
        play: "say:Press 1 for Mean Girls, 2 for Godfather, 3 for Batman"
        max_digits: 1
    - switch:
        variable: prompt_value
        case:
          "1":
            - execute:
                dest: announce_times
                params:
                  movie_info: "%{movie1}"
          "2":
            - execute:
                dest: announce_times
                params:
                  movie_info: "%{movie2}"
          "3":
            - execute:
                dest: announce_times
                params:
                  movie_info: "%{movie3}"

  announce_times:
    - play:
        url: "say:%{params.movie_info}"
    - play:
        url: "silence:1.0"
    - prompt:
        play: "say:Press 1 to receive showtimes via SMS, or press star to return to the menu"
        max_digits: 1
    - switch:
        variable: prompt_value
        case:
          "1":
            - send_sms:
                to_number: "%{call.from}"
                from_number: "%{business_phone}"
                body: "%{params.movie_info}"
            - play: { url: "say:Showtimes have been sent to your phone" }
          "*":
            - transfer: { dest: main }
```

**Benefits:**
- Update in one place
- Reuse across nodes
- Maintain consistency
- Easier to modify

### Accessing Caller Information

**Built-in Call Variables:**

```yaml
# Access caller phone number
- play:
    url: "say:You called from %{call.from}"

# Access destination number
- play:
    url: "say:You called %{call.to}"

# Use in SMS node
- send_sms:
    to_number: "%{call.from}"
    from_number: "%{call.to}"
    body: "Thanks for calling! Your reference number is %{call.call_id}"

# Access call metadata
- cond:
    - when: "call.direction == 'inbound'"
      then:
        - play: { url: "say:This is an inbound call" }
```

### Handling Unknown/No Input

**Always handle these paths:**
- Unmatched input: caller input doesn't match any `switch` case (use `default`)
- No input: caller doesn't respond (`prompt_result == 'no_input'`)

**Best Practice Example:**

```yaml
- label: menu
- prompt:
    play: "say:Press 1 for sales, 2 for support, or 0 to speak with an operator"
    max_digits: 1
    digit_timeout: 5.0
- cond:
    - when: "prompt_result == 'no_input'"
      then:
        - play: { url: "say:We didn't receive your input. Let me repeat the options." }
        - goto: { label: menu, max: 3 }
- switch:
    variable: prompt_value
    case:
      "1":
        - transfer: { dest: sales }
      "2":
        - transfer: { dest: support }
      "0":
        - transfer: { dest: operator }
    default:
      - play: { url: "say:That's not a valid option. Let me repeat the menu." }
      - goto: { label: menu, max: 3 }
```

## Common SWML Patterns from Production

### Pattern 1: Call Flow Builder IVR

**Use Case:** Visual, drag-and-drop IVR creation without code

**What It Is:**
- Located in SignalWire Dashboard > Call Flow Builder
- No-code IVR creation
- Visual node-based design
- Automatically generates SWML

**Key Node Types:**
1. **Answer Call** - Required first step
2. **Play Audio/TTS** - Communicate with caller
3. **Gather Input** - Collect DTMF or speech
4. **Forward to Phone** - Transfer to another number
5. **Voicemail Recording** - Capture messages
6. **Send SMS** - Send text messages
7. **AI Agent** - Connect to AI resources
8. **Request** - Call external APIs
9. **Condition** - Branching logic
10. **Set Variable** - Store data
11. **Hang Up** - End the call

**When to Use:**
- Simple IVR flows
- Non-technical team members
- Rapid prototyping
- Business logic changes frequently

### Pattern 2: After-Hours Routing

**Use Case:** Different behavior during business hours

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    # Call external time API
    - request:
        url: "https://timeapi.io/api/Time/current/zone?timeZone=America/Chicago"
        method: GET
        save_variables: true
    - cond:
        - when: "request_response.hour >= 9 && request_response.hour < 17"
          then:
            - transfer: { dest: business_hours }
        - else:
            - transfer: { dest: after_hours }

  business_hours:
    - play: { url: "say:Our office is open. Connecting you now." }
    - connect:
        to: "+15551234567"
        timeout: 30
    - cond:
        - when: "connect_result == 'failed'"
          then:
            - transfer: { dest: voicemail }
    - hangup: {}

  after_hours:
    - play:
        url: "say:Our office is currently closed. We're open Monday through Friday, 9 AM to 5 PM Central Time."
    - transfer: { dest: voicemail }

  voicemail:
    - play: { url: "say:Please leave a message after the beep" }
    - record:
        max_length: 120
        end_silence_timeout: 3
    - play: { url: "say:Thank you. We'll return your call soon." }
    - hangup: {}
```

### Pattern 3: Multi-Destination Call Routing

**Use Case:** Try multiple numbers sequentially

The `connect` method's `serial` mode tries destinations one at a time, moving to the next if the previous fails:

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - play: { url: "say:Please hold while we locate an available representative" }
    - connect:
        serial:
          - to: "+15551111111"
            timeout: 20
          - to: "+15552222222"
            timeout: 20
          - to: "+15553333333"
            timeout: 20
    - cond:
        - when: "connect_result == 'failed'"
          then:
            - transfer: { dest: voicemail }
    - hangup: {}

  voicemail:
    - play: { url: "say:All representatives are unavailable. Please leave a message." }
    - record: { max_length: 120 }
    - hangup: {}
```

If you need an announcement between attempts, use one `connect` per section and chain with `cond` on `connect_result`:

```yaml
  try_office:
    - connect:
        to: "+15551111111"
        timeout: 20
    - cond:
        - when: "connect_result == 'failed'"
          then:
            - play: { url: "say:Trying alternate number" }
            - transfer: { dest: try_mobile }
    - hangup: {}
```

### Pattern 4: Callback Queue System

**Use Case:** Offer callback instead of waiting on hold

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - prompt:
        play: "say:All agents are currently busy. Press 1 to hold, or press 2 to receive a callback when an agent is available"
        max_digits: 1
    - switch:
        variable: prompt_value
        case:
          "1":
            - transfer: { dest: hold_queue }
          "2":
            - transfer: { dest: schedule_callback }

  hold_queue:
    # Wait in a named queue with hold music until an agent connects
    # (agents dequeue callers with connect to "queue:support")
    - enter_queue:
        queue_name: "support"
        wait_time: 1800
        # Required: SWML to run after the agent bridge ends (URL or inline JSON string)
        transfer_after_bridge: "https://yourserver.com/after-bridge.swml"
    # queue_result: entering|connecting|connected|leaving|timeout|hangup|failed
    - cond:
        - when: "queue_result == 'timeout'"
          then:
            - transfer: { dest: schedule_callback }
    - hangup: {}

  schedule_callback:
    - play: { url: "say:We'll call you back at this number when an agent is available" }
    # Make API call to queue system
    - request:
        url: "https://yourserver.com/api/callback-queue"
        method: POST
        headers:
          Content-Type: application/json
        body:
          phone: "%{call.from}"
          call_id: "%{call.call_id}"
    - play: { url: "say:You've been added to our callback queue. We'll call you back shortly." }
    - hangup: {}
```

### Pattern 5: Survey Collection

**Use Case:** Gather feedback after call

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - play: { url: "say:Thank you for calling. We'd like to ask you a brief survey question." }
    - transfer: { dest: survey }

  survey:
    - prompt:
        play: "say:On a scale of 1 to 5, how satisfied were you with your service today? Press 1 for very dissatisfied, or 5 for very satisfied."
        max_digits: 1
    - cond:
        - when: "prompt_result == 'match_digits'"
          then:
            - request:
                url: "https://yourserver.com/api/survey"
                method: POST
                headers:
                  Content-Type: application/json
                body:
                  rating: "%{prompt_value}"
                  call_id: "%{call.call_id}"
                  phone: "%{call.from}"
            - play:
                url: "say:Thank you for your feedback. Have a great day!"
            - hangup: {}
        - else:
            - play: { url: "say:Thank you for calling" }
            - hangup: {}
```

## Anti-Patterns to Avoid

### 1. Creating Infinite Loops Without Protection

❌ **Wrong:**
```yaml
  get_input:
    - prompt:
        play: "say:Please make a selection"
        max_digits: 1
    - cond:
        - when: "prompt_result == 'no_input'"
          then:
            - transfer: { dest: get_input }  # Infinite loop!
```

✅ **Right:**
```yaml
  get_input:
    - label: menu
    - prompt:
        play: "say:Please make a selection"
        max_digits: 1
    - goto:
        label: menu
        when: "prompt_result == 'no_input'"
        max: 3  # Stops jumping after 3 retries
    - cond:
        - when: "prompt_result == 'no_input'"
          then:
            - play: { url: "say:We didn't receive your input. Goodbye." }
            - hangup: {}
    # ... continue handling prompt_value
```

### 2. Not Handling All Input Paths

❌ **Wrong:**
```yaml
- prompt:
    play: "say:Press 1 or 2"
    max_digits: 1
- switch:
    variable: prompt_value
    case:
      "1":
        - transfer: { dest: option1 }
      "2":
        - transfer: { dest: option2 }
# Missing default case and no_input handling!
```

✅ **Right:**
```yaml
- label: menu
- prompt:
    play: "say:Press 1 or 2"
    max_digits: 1
- cond:
    - when: "prompt_result == 'no_input'"
      then:
        - play: { url: "say:No input received" }
        - goto: { label: menu, max: 3 }
- switch:
    variable: prompt_value
    case:
      "1":
        - transfer: { dest: option1 }
      "2":
        - transfer: { dest: option2 }
    default:
      - play: { url: "say:Invalid option" }
      - goto: { label: menu, max: 3 }
```

### 3. Hardcoding Values That Should Be Variables

❌ **Wrong:**
```yaml
- play: { url: "say:Movie 1 plays at 12:45, 2:15, and 5:00" }
# Later in the code...
- play: { url: "say:Movie 1 plays at 12:45, 2:15, and 5:00" }
# If times change, you must update in multiple places
```

✅ **Right:**
```yaml
- set:
    movie1_times: "Movie 1 plays at 12:45, 2:15, and 5:00"
- play: { url: "say:%{movie1_times}" }
# Later...
- play: { url: "say:%{movie1_times}" }
# Update in one place
```

### 4. Using Complex Nested Structures

❌ **Wrong:**
```yaml
sections:
  main:
    - answer: {}
    - prompt:
        play: "say:Complex menu"
        max_digits: 1
    - switch:
        variable: prompt_value
        case:
          "1":
            - prompt:
                play: "say:Submenu"
                max_digits: 1
            - switch:
                variable: prompt_value
                # Deeply nested, hard to maintain
```

✅ **Right:**
```yaml
sections:
  main:
    - answer: {}
    - transfer: { dest: main_menu }

  main_menu:
    - prompt:
        play: "say:Main menu"
        max_digits: 1
    - switch:
        variable: prompt_value
        case:
          "1":
            - transfer: { dest: submenu }

  submenu:
    - prompt:
        play: "say:Submenu"
        max_digits: 1
    # Separate sections are easier to understand and maintain
```

## Production Tips

### 1. Audio File Best Practices

**Use CDN for audio files:**
- Faster playback
- Reduced latency
- Better reliability
- Geographic distribution

**Optimize audio files:**
- MP3 at 64-128 kbps is sufficient for voice
- 8kHz or 16kHz sample rate
- Mono channel (not stereo) for voice prompts
- Pre-record prompts rather than using TTS for frequently played messages

### 2. Test with Real Phone Calls

**Development workflow:**
1. Write SWML locally
2. Use SWML Editor to validate
3. Deploy to test server with ngrok
4. Call with real phone to test
5. Check Dashboard logs for issues
6. Iterate based on real-world behavior

**Don't rely solely on:**
- Synthetic testing
- Webhook simulators
- API testing tools

Real phone calls reveal issues with:
- Audio quality
- Timing
- User experience
- Network latency

### 3. Use Sections as Functions

**Organize SWML into reusable sections:**

```yaml
sections:
  main:
    - answer: {}
    - execute: { dest: play_greeting }
    - execute: { dest: main_menu }

  play_greeting:
    - play: { url: "https://example.com/greeting.mp3" }
    - return: {}

  main_menu:
    - prompt:
        play: "say:Main menu options"
        max_digits: 1
    # ... menu logic
    - return: {}

  play_hold_music:
    - play: { url: "https://example.com/hold.mp3" }
    - return: {}
```

**Benefits:**
- Reusable components
- Easier to test
- Simpler to modify
- Better organization

### 4. Monitor and Log

**Use Dashboard Logs:**
- Navigate to: Relay > Activity
- Filter by date, status, resource
- Export for external analysis

**Key Metrics to Track:**
- Call success rate
- Average call duration
- DTMF input patterns
- Transfer success rate
- Hang-up points in flow

### 5. Provide Clear Feedback

**Always tell callers what's happening:**

```yaml
# Good - tells user what to expect
- play: { url: "say:Please hold while I transfer you to sales. This may take up to 30 seconds." }
- connect:
    to: "+15551234567"
    timeout: 30

# Bad - silent transfer
- connect: { to: "+15551234567" }
```

## Next Steps

- [Call Control](call-control.md) - Transfer, record, conference
- [Voice AI](voice-ai.md) - Add AI agents to calls
- [Webhooks & Events](webhooks-events.md) - Handle call events
- [Outbound Calling](outbound-calling.md) - Make calls with SWML
