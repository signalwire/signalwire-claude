# Outbound Calling

## Overview

Make outbound phone calls using the SignalWire REST API. Calls can be controlled via SWML documents or handled in real-time with SDKs.

## REST API: Creating Calls

### Endpoint

```
POST https://{space}.signalwire.com/api/calling/calls
```

### Authentication

HTTP Basic Auth with Project ID and API Token (see [Authentication](authentication-setup.md))

### Request Format

```json
{
  "command": "dial",
  "params": {
    "from": "sip:user@example.sip.signalwire.com",
    "to": "sip:dest@example.sip.signalwire.com",
    "url": "https://example.com/swml",
    "caller_id": "+1234567890",
    "status_url": "https://example.com/status",
    "fallback_url": "https://example.com/fallback"
  }
}
```

### Required Parameters

- **command**: Always `"dial"` for creating new calls
- **params.from**: Calling number (E.164 format) or SIP address
- **params.to**: Destination number (E.164 format) or SIP address
- **params.url**: SWML document URL to control the call

### Optional Parameters

- **params.caller_id**: Caller ID to display (must be a number you own)
- **params.status_url**: Webhook URL for status updates
- **params.fallback_url**: Fallback SWML if primary URL fails
- **params.timeout**: Ring timeout in seconds
- **params.max_duration**: Maximum call duration in seconds

### Response

```json
{
  "call_id": "c1234567-89ab-cdef-0123-456789abcdef",
  "status": "queued"
}
```

## Complete Examples

### Python

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = ["requests"]
# ///

import os
import requests
from requests.auth import HTTPBasicAuth

project_id = os.getenv('SIGNALWIRE_PROJECT_ID')
api_token = os.getenv('SIGNALWIRE_API_TOKEN')
space_url = os.getenv('SIGNALWIRE_SPACE_URL')

response = requests.post(
    f"{space_url}/api/calling/calls",
    auth=HTTPBasicAuth(project_id, api_token),
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json"
    },
    json={
        "command": "dial",
        "params": {
            "from": "+15551234567",
            "to": "+15559876543",
            "caller_id": "+15551234567",
            "url": "https://example.com/swml",
            "status_url": "https://example.com/status"
        }
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Call initiated: {data['call_id']}")
    print(f"Status: {data['status']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

### Node.js

```javascript
const axios = require('axios');

const projectId = process.env.SIGNALWIRE_PROJECT_ID;
const apiToken = process.env.SIGNALWIRE_API_TOKEN;
const spaceUrl = process.env.SIGNALWIRE_SPACE_URL;

async function makeCall() {
  try {
    const response = await axios.post(
      `${spaceUrl}/api/calling/calls`,
      {
        command: 'dial',
        params: {
          from: '+15551234567',
          to: '+15559876543',
          caller_id: '+15551234567',
          url: 'https://example.com/swml',
          status_url: 'https://example.com/status'
        }
      },
      {
        auth: {
          username: projectId,
          password: apiToken
        },
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      }
    );

    console.log(`Call initiated: ${response.data.call_id}`);
    console.log(`Status: ${response.data.status}`);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

makeCall();
```

### cURL

```bash
curl -L 'https://kalsey.signalwire.com/api/calling/calls' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H 'Authorization: Basic <base64_creds>' \
  --data-raw '{
    "command": "dial",
    "params": {
      "from": "sip:from-sip@example-112233445566.sip.signalwire.com",
      "to": "sip:to-sip@example-112233445567.sip.signalwire.com",
      "caller_id": "+1234567890",
      "fallback_url": "https://example.com/fallback",
      "url": "https://example.com/swml",
      "status_url": "https://example.com/status"
    }
  }'
```

## Status Callbacks (status_url)

The `status_url` parameter is **DOCUMENTED** and receives webhooks for call state changes.

### Status Events

SignalWire sends HTTP POST requests to your status_url with these states:

- **queued**: Call request received
- **created**: Call has been created
- **ringing**: Destination is ringing
- **answered**: Call was answered
- **ended**: Call has terminated

### Status Webhook Format

```json
{
  "call_id": "c1234567-89ab-cdef-0123-456789abcdef",
  "call_state": "answered",
  "from": "+15551234567",
  "to": "+15559876543",
  "direction": "outbound",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Handling Status Webhooks (Python/Flask)

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/status', methods=['POST'])
def handle_status():
    data = request.json
    call_id = data.get('call_id')
    status = data.get('call_state')

    print(f"Call {call_id}: {status}")

    # Update your database, send notifications, etc.
    if status == 'answered':
        print(f"Call answered at {data.get('timestamp')}")
    elif status == 'ended':
        print("Call ended")

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(port=5000)
```

## Phone Number Formats

### E.164 Format (Phone Numbers)

Use E.164 format for phone numbers:
```
+15551234567  # US number
+442012345678 # UK number
+81312345678  # Japan number
```

**Always include:**
- `+` prefix
- Country code
- No spaces, dashes, or parentheses

### SIP Addresses

For SIP endpoints:
```
sip:username@domain.sip.signalwire.com
```

## SWML Document for Call Control

The `url` parameter points to a SWML document that controls the call behavior.

### Simple SWML Example (served at params.url)

```yaml
version: 1.0.0
sections:
  main:
    - play:
        url: "https://example.com/audio/greeting.mp3"
    - say:
        text: "Thanks for calling. Connecting you now."
    - connect:
        to: "+15551111111"
```

Or in JSON:
```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "play": {
          "url": "https://example.com/audio/greeting.mp3"
        }
      },
      {
        "say": {
          "text": "Thanks for calling. Connecting you now."
        }
      },
      {
        "connect": {
          "to": "+15551111111"
        }
      }
    ]
  }
}
```

See [Inbound Call Handling](inbound-call-handling.md) for comprehensive SWML documentation.

## Using Relay SDK Instead

For real-time call control without SWML, use the Relay SDK:

### Python Relay Example

```python
from signalwire.relay.consumer import Consumer

class OutboundCaller(Consumer):
    def setup(self):
        self.project = os.getenv('SIGNALWIRE_PROJECT_ID')
        self.token = os.getenv('SIGNALWIRE_API_TOKEN')

    async def make_outbound_call(self):
        call = await self.client.calling.dial(
            from_number='+15551234567',
            to_number='+15559876543'
        )

        await call.wait_for_answered()
        await call.play_tts(text="Hello from SignalWire!")
        await call.hangup()
```

### JavaScript/Node.js Relay Example

```javascript
const { SignalWire } = require('@signalwire/realtime-api');

async function makeCall() {
  const client = await SignalWire({
    project: process.env.SIGNALWIRE_PROJECT_ID,
    token: process.env.SIGNALWIRE_API_TOKEN
  });

  const call = await client.voice.dialPhone({
    from: '+15551234567',
    to: '+15559876543'
  });

  await call.waitFor('answered');
  await call.playTTS({ text: 'Hello from SignalWire!' });
  await call.hangup();
}
```

## Common Use Cases

### 1. Click-to-Call from Website

```javascript
// Frontend button triggers call via your backend API
async function initiateCall(fromNumber, toNumber) {
  const response = await fetch('/api/make-call', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ from: fromNumber, to: toNumber })
  });

  const data = await response.json();
  console.log(`Call initiated: ${data.call_id}`);
}
```

```python
# Backend API endpoint
@app.route('/api/make-call', methods=['POST'])
def make_call():
    data = request.json

    response = requests.post(
        f"{space_url}/api/calling/calls",
        auth=HTTPBasicAuth(project_id, api_token),
        json={
            "command": "dial",
            "params": {
                "from": data['from'],
                "to": data['to'],
                "url": "https://myserver.com/swml"
            }
        }
    )

    return jsonify(response.json())
```

### 2. Scheduled Reminder Calls

```python
# Using APScheduler or similar
from apscheduler.schedulers.background import BackgroundScheduler

def send_reminder_call(phone_number, message):
    # Create SWML with the reminder message
    swml_url = f"https://myserver.com/swml/reminder?message={message}"

    requests.post(
        f"{space_url}/api/calling/calls",
        auth=HTTPBasicAuth(project_id, api_token),
        json={
            "command": "dial",
            "params": {
                "from": "+15551234567",
                "to": phone_number,
                "url": swml_url
            }
        }
    )

scheduler = BackgroundScheduler()
scheduler.add_job(
    send_reminder_call,
    'date',
    run_date='2025-01-20 09:00:00',
    args=['+15559876543', 'Your appointment is today']
)
scheduler.start()
```

### 3. Outbound Survey Calls

```python
# Make call with SWML that collects survey responses
response = requests.post(
    f"{space_url}/api/calling/calls",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "command": "dial",
        "params": {
            "from": "+15551234567",
            "to": "+15559876543",
            "url": "https://myserver.com/swml/survey",
            "status_url": "https://myserver.com/survey/status"
        }
    }
)
```

## Error Handling

### Common Errors

**400 Bad Request**
- Invalid phone number format
- Missing required parameters
- Invalid SIP address

**401 Unauthorized**
- Invalid Project ID or API Token

**403 Forbidden**
- Calling not enabled for your space
- Insufficient permissions

**422 Unprocessable Entity**
- Invalid caller_id (not a number you own)
- Blocked destination number

### Example with Error Handling

```python
try:
    response = requests.post(
        f"{space_url}/api/calling/calls",
        auth=HTTPBasicAuth(project_id, api_token),
        json=call_data,
        timeout=10
    )
    response.raise_for_status()

    call_id = response.json()['call_id']
    print(f"Success: {call_id}")

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Authentication failed - check credentials")
    elif e.response.status_code == 422:
        print(f"Invalid request: {e.response.json()}")
    else:
        print(f"HTTP error: {e}")

except requests.exceptions.Timeout:
    print("Request timed out")

except Exception as e:
    print(f"Unexpected error: {e}")
```

## Testing

### Test with cURL First

```bash
# Quick test call
curl -u $SIGNALWIRE_PROJECT_ID:$SIGNALWIRE_API_TOKEN \
  -H 'Content-Type: application/json' \
  $SIGNALWIRE_SPACE_URL/api/calling/calls \
  -d '{
    "command": "dial",
    "params": {
      "from": "+15551234567",
      "to": "+15559876543",
      "url": "https://example.com/test.yaml"
    }
  }'
```

### Use Simple SWML for Testing

```yaml
# test.yaml - Simple test SWML
version: 1.0.0
sections:
  main:
    - say:
        text: "This is a test call from SignalWire"
    - hangup: {}
```

## Outbound Dialer Patterns with CRM

### Automated Patient/Customer Outreach

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = ["requests", "sqlalchemy"]
# ///

import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

project_id = os.getenv('SIGNALWIRE_PROJECT_ID')
api_token = os.getenv('SIGNALWIRE_API_TOKEN')
space_url = os.getenv('SIGNALWIRE_SPACE_URL')

def dial_patients_for_checkup():
    """Automated outbound calling for patient check-ins"""

    # Get patients needing follow-up
    patients = database.query("""
        SELECT * FROM patients
        WHERE last_checkup < NOW() - INTERVAL '6 months'
        AND opt_in_calls = TRUE
    """)

    for patient in patients:
        # Create call with patient-specific SWML
        response = requests.post(
            f"{space_url}/api/calling/calls",
            auth=HTTPBasicAuth(project_id, api_token),
            json={
                "command": "dial",
                "params": {
                    "from": "+15551234567",
                    "to": patient.phone,
                    "url": f"https://yourserver.com/health-assessment/{patient.id}",
                    "status_url": f"https://yourserver.com/call-status/{patient.id}"
                }
            }
        )

        if response.status_code == 200:
            call_id = response.json()['call_id']

            # Log outreach attempt
            database.log_call_attempt({
                'patient_id': patient.id,
                'call_id': call_id,
                'purpose': 'health_checkup',
                'timestamp': datetime.now()
            })
```

### Appointment Reminder Pattern

```python
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()

def schedule_appointment_reminders():
    """Send reminder calls for upcoming appointments"""

    # Get appointments for next 24 hours
    tomorrow = datetime.now() + timedelta(days=1)
    appointments = database.query("""
        SELECT * FROM appointments
        WHERE appointment_time BETWEEN NOW() AND %s
        AND reminder_sent = FALSE
    """, (tomorrow,))

    for appt in appointments:
        # Schedule reminder call
        reminder_time = appt.appointment_time - timedelta(hours=24)

        scheduler.add_job(
            send_reminder_call,
            'date',
            run_date=reminder_time,
            args=[appt.patient_phone, appt.appointment_time, appt.doctor_name]
        )

def send_reminder_call(phone, appt_time, doctor):
    """Make reminder call"""

    # Create SWML for reminder
    swml_url = create_reminder_swml(appt_time, doctor)

    response = requests.post(
        f"{space_url}/api/calling/calls",
        auth=HTTPBasicAuth(project_id, api_token),
        json={
            "command": "dial",
            "params": {
                "from": "+15551234567",
                "to": phone,
                "url": swml_url,
                "status_url": "https://yourserver.com/reminder-status"
            }
        }
    )

scheduler.start()
```

### Voice Appointment Reminders

```yaml
# SWML for appointment reminder
version: 1.0.0
sections:
  main:
    - answer: {}
    - say:
        text: "Hello, this is a reminder from {clinic_name}."
    - say:
        text: "You have an appointment tomorrow at {appointment_time} with Dr. {doctor_name}."
    - prompt:
        say: "Press 1 to confirm, 2 to reschedule, or 3 to cancel."
        max_digits: 1
    - switch:
        variable: "%{digits}"
        case:
          "1":
            - say:
                text: "Thank you, your appointment is confirmed."
            - request:
                url: "https://yourserver.com/confirm-appointment"
                method: POST
            - hangup: {}
          "2":
            - say:
                text: "Please call our office to reschedule."
            - hangup: {}
          "3":
            - say:
                text: "Your appointment has been cancelled."
            - request:
                url: "https://yourserver.com/cancel-appointment"
                method: POST
            - hangup: {}
```

### Healthcare Assessment Workflow

```yaml
# AI-powered health assessment call
version: 1.0.0
sections:
  main:
    - answer: {}
    - ai:
        prompt: |
          You are Adam, a nursing home digital assistant conducting a weekly health assessment.

          Steps:
          1. Greet {patient_name} by name
          2. Verify identity with 4-digit PIN
          3. Ask standard health questions:
             - How are you feeling today?
             - Any pain or discomfort?
             - Taking all medications as prescribed?
             - Any concerns you want to discuss?
          4. Provide guidance if needed
          5. Thank them and end call

          If patient reports serious symptoms, call transfer_to_nurse function.
          Store summary using record_assessment function.

        functions:
          - name: verify_patient_pin
            purpose: "Verify patient identity with PIN"
            web_hook: "https://yourserver.com/verify-pin"

          - name: get_patient_history
            purpose: "Retrieve patient medical history"
            web_hook: "https://yourserver.com/patient-history"

          - name: transfer_to_nurse
            purpose: "Transfer to live nurse for serious issues"
            web_hook: "https://yourserver.com/transfer-nurse"

          - name: record_assessment
            purpose: "Store health assessment summary"
            web_hook: "https://yourserver.com/save-assessment"

          - name: send_caregiver_sms
            purpose: "Notify caregiver of assessment results"
            web_hook: "https://yourserver.com/notify-caregiver"

        post_prompt_url: "https://yourserver.com/assessment-summary"
        post_prompt: |
          Summarize the health assessment as JSON:
          {
            "patient_name": "name",
            "overall_status": "good/fair/concerning",
            "symptoms_reported": ["list"],
            "medication_compliance": true/false,
            "concerns": ["list"],
            "action_required": true/false
          }
```

### CRM Integration Pattern

```python
@app.route('/assessment-summary', methods=['POST'])
def handle_assessment():
    data = request.json

    # Extract assessment data
    parsed = data.get('post_prompt_data', {}).get('parsed', {})

    patient_name = parsed.get('patient_name')
    status = parsed.get('overall_status')
    action_required = parsed.get('action_required')

    # Update CRM/EHR
    ehr_system.update_patient_record({
        'patient': patient_name,
        'assessment_date': datetime.now(),
        'status': status,
        'notes': format_transcript(data.get('conversation'))
    })

    # Alert if action needed
    if action_required or status == 'concerning':
        # Notify care team
        send_alert_to_team({
            'patient': patient_name,
            'urgency': 'high' if status == 'concerning' else 'medium',
            'summary': parsed.get('concerns')
        })

    # Send SMS to caregiver
    if status in ['fair', 'concerning']:
        send_sms(
            to=get_caregiver_phone(patient_name),
            body=f"Health check completed for {patient_name}. Status: {status}. "
                 f"Call office for details."
        )

    return jsonify({"status": "ok"}), 200
```

### Bulk Outbound Campaign

```python
def run_outbound_campaign(campaign_id):
    """Execute bulk outbound calling campaign"""

    campaign = database.get_campaign(campaign_id)
    recipients = database.get_campaign_recipients(campaign_id)

    # Rate limiting (e.g., 10 calls per second)
    from time import sleep
    delay = 0.1  # 100ms between calls

    for recipient in recipients:
        # Check opt-out status
        if is_opted_out(recipient.phone):
            continue

        # Make call
        try:
            response = requests.post(
                f"{space_url}/api/calling/calls",
                auth=HTTPBasicAuth(project_id, api_token),
                json={
                    "command": "dial",
                    "params": {
                        "from": campaign.caller_id,
                        "to": recipient.phone,
                        "url": campaign.swml_url,
                        "status_url": f"https://yourserver.com/campaign/{campaign_id}/status"
                    }
                },
                timeout=5
            )

            if response.status_code == 200:
                database.log_call({
                    'campaign_id': campaign_id,
                    'recipient_id': recipient.id,
                    'call_id': response.json()['call_id'],
                    'status': 'initiated'
                })

        except Exception as e:
            log_error(f"Failed to call {recipient.phone}: {e}")

        # Rate limit
        sleep(delay)
```

## Next Steps

- [Inbound Call Handling](inbound-call-handling.md) - Create SWML to control calls
- [Call Control](call-control.md) - Transfer, record, conference
- [Webhooks & Events](webhooks-events.md) - Handle status callbacks and post-prompt data
- [Voice AI](voice-ai.md) - Add AI agents to outbound calls
- [Messaging](messaging.md) - Follow up calls with SMS
