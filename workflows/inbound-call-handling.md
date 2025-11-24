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
    - say:
        text: "Hello from SignalWire"
```

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      { "answer": {} },
      { "say": { "text": "Hello from SignalWire" } }
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
                {"say": {"text": "Welcome to our service"}}
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
    - say:
        text: Welcome to our service
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
                    {"say": {"text": "Hello from Relay"}}
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

### say

Text-to-speech (TTS).

```yaml
- say:
    text: "Welcome to SignalWire"
    language: "en-US"
    gender: "female"

# With variable substitution
- say:
    text: "You called from %{call.from}"
```

**Parameters**:
- `text`: What to say
- `language`: Voice language (default: `en-US`)
- `gender`: `male`, `female`, or specific voice name

### prompt

Play audio/TTS and collect user input.

```yaml
- prompt:
    play: "Press 1 for sales, 2 for support"
    max_digits: 1
    terminators: "#"
    digit_timeout: 5.0
```

**Parameters**:
- `play`: Audio URL or TTS text
- `say`: Alternative to `play` for TTS
- `max_digits`: Maximum digits to collect
- `terminators`: Keys that end input (default: `#`)
- `digit_timeout`: Seconds to wait for digit

**Accessing result**:
```yaml
- prompt:
    play: "Enter your account number"
    max_digits: 6
  on_success:
    - execute:
        dest: process_input
        params:
          digits: "%{args.result}"
```

Result available in `%{args.result}`.

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

**Parameters**:
- `to`: Destination number or SIP address
- `from`: Caller ID to display
- `timeout`: Ring timeout in seconds

### transfer

Transfer call to another SWML section (permanently).

```yaml
sections:
  main:
    - prompt:
        play: "Press 1 for sales, 2 for support"
        max_digits: 1
      on_success:
        - switch:
            variable: "%{args.result}"
            case:
              "1":
                - transfer:
                    dest: sales
              "2":
                - transfer:
                    dest: support

  sales:
    - say:
        text: "Transferring to sales"
    - connect:
        to: "+15551111111"

  support:
    - say:
        text: "Transferring to support"
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
    - say:
        text: "What can I help you with?"

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

**Parameters**:
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

Use `%{variable_name}` to access dynamic values:

### Call Variables

```yaml
- say:
    text: "You called from %{call.from} to %{call.to}"
```

Available variables:
- `%{call.from}` - Caller's number
- `%{call.to}` - Destination number
- `%{call.id}` - Unique call ID
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
- say:
    text: "Your reference is %{params.custom_param}"
```

### Prompt Results

```yaml
- prompt:
    play: "Enter your PIN"
    max_digits: 4
  on_success:
    - switch:
        variable: "%{args.result}"
        case:
          "1234":
            - say: { text: "PIN accepted" }
          default:
            - say: { text: "Invalid PIN" }
```

## Control Flow

### switch

Conditional branching based on variable value.

```yaml
- switch:
    variable: "%{args.result}"
    case:
      "1":
        - say: { text: "You pressed 1" }
      "2":
        - say: { text: "You pressed 2" }
      default:
        - say: { text: "Invalid selection" }
```

### Callbacks (on_success, on_failure)

Methods can have success/failure handlers:

```yaml
- prompt:
    play: "Press any key"
    max_digits: 1
    digit_timeout: 5.0
  on_success:
    - say: { text: "Thank you" }
  on_failure:
    - say: { text: "No input received" }
```

## Advanced Patterns

### IVR Menu System

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - execute:
        dest: main_menu

  main_menu:
    - prompt:
        play: "https://example.com/main-menu.mp3"
        max_digits: 1
        digit_timeout: 5.0
      on_success:
        - switch:
            variable: "%{args.result}"
            case:
              "1":
                - transfer: { dest: sales }
              "2":
                - transfer: { dest: support }
              "3":
                - transfer: { dest: billing }
              "9":
                - execute: { dest: main_menu }  # Repeat menu
              default:
                - say: { text: "Invalid selection" }
                - execute: { dest: main_menu }
      on_failure:
        - say: { text: "Sorry, I didn't catch that" }
        - execute: { dest: main_menu }

  sales:
    - say: { text: "Connecting you to sales" }
    - connect:
        to: "+15551111111"
        timeout: 30
      on_failure:
        - say: { text: "Sales is unavailable. Returning to main menu" }
        - execute: { dest: main_menu }

  support:
    - say: { text: "Connecting you to support" }
    - connect: { to: "+15552222222" }

  billing:
    - say: { text: "Connecting you to billing" }
    - connect: { to: "+15553333333" }
```

### Voicemail System

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - say:
        text: "Please leave a message after the beep"
    - play:
        url: "https://example.com/beep.mp3"
    - record:
        beep: false
        max_length: 120
        end_silence_timeout: 3
    - say:
        text: "Thank you for your message"
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
    - say:
        text: "Please say your name after the beep"
    - play: { url: "https://example.com/beep.mp3" }
    - record:
        max_length: 5
        end_silence_timeout: 2
    - say:
        text: "Please hold while we connect you"
    - connect:
        to: "+15551234567"
        caller_id: "%{call.from}"
      on_success:
        - hangup: {}
      on_failure:
        - transfer: { dest: voicemail }

  voicemail:
    - say: { text: "Sorry, that person is unavailable" }
    - hangup: {}
```

### Multi-Language Support

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - prompt:
        play: "Press 1 for English, presione 2 para Español"
        max_digits: 1
      on_success:
        - switch:
            variable: "%{args.result}"
            case:
              "1":
                - transfer: { dest: english_menu }
              "2":
                - transfer: { dest: spanish_menu }

  english_menu:
    - say:
        text: "Welcome to our service"
        language: "en-US"
    - prompt:
        say: "Press 1 for sales, 2 for support"
        max_digits: 1

  spanish_menu:
    - say:
        text: "Bienvenido a nuestro servicio"
        language: "es-MX"
    - prompt:
        say: "Presione 1 para ventas, 2 para soporte"
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
                {"say": {"text": f"Debug: Call from {request.args.get('From')}"}}
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
- Add `on_failure` handlers

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
        say: "Press 1 for sales, 2 for support"
        max_digits: 1
```

### Loop Protection Pattern

**Problem:** Gather input nodes can loop infinitely if caller doesn't respond.

**Solution:**

```yaml
sections:
  main:
    - answer: {}
    - execute: { dest: get_input }

  get_input:
    # Create loop counter
    - set:
        loop: "{{loop | default(0) | int + 1}}"

    # Check loop count
    - condition:
        if: "{{loop}} > 2"
        then:
          - say: { text: "We're having trouble understanding your input. Goodbye." }
          - hangup: {}
        else:
          - prompt:
              say: "Press 1 for sales, 2 for support"
              max_digits: 1
            on_success:
              - switch:
                  variable: "{{args.result}}"
                  case:
                    "1":
                      - transfer: { dest: sales }
                    "2":
                      - transfer: { dest: support }
                  default:
                    - say: { text: "That was not a valid option" }
                    - execute: { dest: get_input }
            on_failure:
              - say: { text: "We didn't receive any input" }
              - execute: { dest: get_input }

  sales:
    - connect: { to: "+15551111111" }

  support:
    - connect: { to: "+15552222222" }
```

**Implementation per gather node:**
- Use unique variable names (`loop1`, `loop2`) for multiple gather points
- Set maximum iterations (typically 2-3)
- Provide helpful feedback before looping
- Always end with hangup after max attempts

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
        say: "Press 1 for Mean Girls, 2 for Godfather, 3 for Batman"
        max_digits: 1
      on_success:
        - switch:
            variable: "{{args.result}}"
            case:
              "1":
                - execute:
                    dest: announce_times
                    params:
                      movie_info: "{{movie1}}"
              "2":
                - execute:
                    dest: announce_times
                    params:
                      movie_info: "{{movie2}}"
              "3":
                - execute:
                    dest: announce_times
                    params:
                      movie_info: "{{movie3}}"

  announce_times:
    - say:
        text: "{{movie_info}}"
    - play:
        url: "silence:1.0"
    - prompt:
        say: "Press 1 to receive showtimes via SMS, or press star to return to the menu"
        max_digits: 1
      on_success:
        - switch:
            variable: "{{args.result}}"
            case:
              "1":
                - send_sms:
                    to_number: "{{call.from}}"
                    from_number: "{{business_phone}}"
                    body: "{{movie_info}}"
                - say: { text: "Showtimes have been sent to your phone" }
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
- say:
    text: "You called from {{call.from}}"

# Access destination number
- say:
    text: "You called {{call.to}}"

# Use in SMS node
- send_sms:
    to: "{{call.from}}"
    from: "{{call.to}}"
    body: "Thanks for calling! Your reference number is {{call.id}}"

# Access call metadata
- condition:
    if: "{{call.direction}} == 'inbound'"
    then:
      - say: { text: "This is an inbound call" }
```

### Handling Unknown/No Input

**Always handle these paths:**
- `unknown`: Caller input doesn't match options
- `no_input`: Caller doesn't respond

**Best Practice Example:**

```yaml
- prompt:
    say: "Press 1 for sales, 2 for support, or 0 to speak with an operator"
    max_digits: 1
    digit_timeout: 5.0
  on_success:
    - switch:
        variable: "{{args.result}}"
        case:
          "1":
            - transfer: { dest: sales }
          "2":
            - transfer: { dest: support }
          "0":
            - transfer: { dest: operator }
          default:
            - say: { text: "That's not a valid option. Let me repeat the menu." }
            - execute: { dest: main_menu }
  on_failure:
    - say: { text: "We didn't receive your input. Let me repeat the options." }
    - execute: { dest: main_menu }
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
    - condition:
        if: "{{request.response.hour}} >= 9 && {{request.response.hour}} < 17"
        then:
          - transfer: { dest: business_hours }
        else:
          - transfer: { dest: after_hours }

  business_hours:
    - say: { text: "Our office is open. Connecting you now." }
    - connect:
        to: "+15551234567"
        timeout: 30
      on_failure:
        - transfer: { dest: voicemail }

  after_hours:
    - say:
        text: "Our office is currently closed. We're open Monday through Friday, 9 AM to 5 PM Central Time."
    - transfer: { dest: voicemail }

  voicemail:
    - say: { text: "Please leave a message after the beep" }
    - record:
        max_length: 120
        end_silence_timeout: 3
    - say: { text: "Thank you. We'll return your call soon." }
    - hangup: {}
```

### Pattern 3: Multi-Destination Call Routing

**Use Case:** Try multiple numbers sequentially

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - say: { text: "Please hold while we locate an available representative" }
    - execute: { dest: try_office }

  try_office:
    - connect:
        to: "+15551111111"
        timeout: 20
      on_success:
        - hangup: {}
      on_failure:
        - execute: { dest: try_mobile }

  try_mobile:
    - say: { text: "Trying alternate number" }
    - connect:
        to: "+15552222222"
        timeout: 20
      on_success:
        - hangup: {}
      on_failure:
        - execute: { dest: try_backup }

  try_backup:
    - say: { text: "Trying final contact method" }
    - connect:
        to: "+15553333333"
        timeout: 20
      on_success:
        - hangup: {}
      on_failure:
        - transfer: { dest: voicemail }

  voicemail:
    - say: { text: "All representatives are unavailable. Please leave a message." }
    - record: { max_length: 120 }
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
        say: "All agents are currently busy. Press 1 to hold, or press 2 to receive a callback when an agent is available"
        max_digits: 1
      on_success:
        - switch:
            variable: "{{args.result}}"
            case:
              "1":
                - transfer: { dest: hold_queue }
              "2":
                - transfer: { dest: schedule_callback }

  hold_queue:
    - play:
        url: "https://example.com/hold-music.mp3"
    - say: { text: "Your call is important to us. Please continue holding." }
    - execute: { dest: hold_queue }  # Loop hold music

  schedule_callback:
    - say: { text: "We'll call you back at this number when an agent is available" }
    # Make API call to queue system
    - request:
        url: "https://yourserver.com/api/callback-queue"
        method: POST
        body:
          phone: "{{call.from}}"
          timestamp: "{{call.timestamp}}"
    - say: { text: "You've been added to our callback queue. We'll call you back shortly." }
    - hangup: {}
```

### Pattern 5: Survey Collection

**Use Case:** Gather feedback after call

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - say: { text: "Thank you for calling. We'd like to ask you a brief survey question." }
    - execute: { dest: survey }

  survey:
    - prompt:
        say: "On a scale of 1 to 5, how satisfied were you with your service today? Press 1 for very dissatisfied, or 5 for very satisfied."
        max_digits: 1
      on_success:
        - request:
            url: "https://yourserver.com/api/survey"
            method: POST
            body:
              rating: "{{args.result}}"
              call_id: "{{call.id}}"
              phone: "{{call.from}}"
        - say:
            text: "Thank you for your feedback. Have a great day!"
        - hangup: {}
      on_failure:
        - say: { text: "Thank you for calling" }
        - hangup: {}
```

## Anti-Patterns to Avoid

### 1. Creating Infinite Loops Without Protection

❌ **Wrong:**
```yaml
- gather:
    type: digits
    no_input:
      - goto: gather  # Infinite loop!
```

✅ **Right:**
```yaml
- set:
    loop: "{{loop | default(0) | int + 1}}"
- condition:
    if: "{{loop}} > 3"
    then:
      - hangup: {}
    else:
      - gather: {}
```

### 2. Not Handling All Input Paths

❌ **Wrong:**
```yaml
- prompt:
    say: "Press 1 or 2"
    max_digits: 1
  on_success:
    - switch:
        variable: "{{args.result}}"
        case:
          "1":
            - transfer: { dest: option1 }
          "2":
            - transfer: { dest: option2 }
# Missing default and on_failure handlers!
```

✅ **Right:**
```yaml
- prompt:
    say: "Press 1 or 2"
    max_digits: 1
  on_success:
    - switch:
        variable: "{{args.result}}"
        case:
          "1":
            - transfer: { dest: option1 }
          "2":
            - transfer: { dest: option2 }
          default:
            - say: { text: "Invalid option" }
            - execute: { dest: main_menu }
  on_failure:
    - say: { text: "No input received" }
    - execute: { dest: main_menu }
```

### 3. Hardcoding Values That Should Be Variables

❌ **Wrong:**
```yaml
- say: { text: "Movie 1 plays at 12:45, 2:15, and 5:00" }
# Later in the code...
- say: { text: "Movie 1 plays at 12:45, 2:15, and 5:00" }
# If times change, you must update in multiple places
```

✅ **Right:**
```yaml
- set:
    movie1_times: "Movie 1 plays at 12:45, 2:15, and 5:00"
- say: { text: "{{movie1_times}}" }
# Later...
- say: { text: "{{movie1_times}}" }
# Update in one place
```

### 4. Using Complex Nested Structures

❌ **Wrong:**
```yaml
sections:
  main:
    - answer: {}
    - prompt:
        say: "Complex menu"
      on_success:
        - switch:
            case:
              "1":
                - prompt:
                    say: "Submenu"
                  on_success:
                    - switch:
                        # Deeply nested, hard to maintain
```

✅ **Right:**
```yaml
sections:
  main:
    - answer: {}
    - execute: { dest: main_menu }

  main_menu:
    - prompt:
        say: "Main menu"
      on_success:
        - switch:
            case:
              "1":
                - transfer: { dest: submenu }

  submenu:
    - prompt:
        say: "Submenu"
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
    - prompt: { say: "Main menu options" }
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
- say: { text: "Please hold while I transfer you to sales. This may take up to 30 seconds." }
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
