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

## Next Steps

- [Call Control](call-control.md) - Transfer, record, conference
- [Voice AI](voice-ai.md) - Add AI agents to calls
- [Webhooks & Events](webhooks-events.md) - Handle call events
- [Outbound Calling](outbound-calling.md) - Make calls with SWML
