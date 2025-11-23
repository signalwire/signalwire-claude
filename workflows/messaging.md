# Messaging

## Overview

Send and receive SMS and MMS messages using SignalWire REST APIs, Realtime SDK, or SWML.

**IMPORTANT**: Use modern messaging APIs, NOT LAML/CXML compatibility endpoints.

## Sending Messages

### REST API

#### Endpoint

```
POST https://{space}.signalwire.com/api/messaging/messages
```

#### Request Format

```json
{
  "from": "+15551234567",
  "to": "+15559876543",
  "body": "Hello from SignalWire!"
}
```

#### With Media (MMS)

```json
{
  "from": "+15551234567",
  "to": "+15559876543",
  "body": "Check out this image",
  "media": [
    "https://example.com/image.jpg"
  ]
}
```

### Python Example

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
    f"{space_url}/api/messaging/messages",
    auth=HTTPBasicAuth(project_id, api_token),
    headers={"Content-Type": "application/json"},
    json={
        "from": "+15551234567",
        "to": "+15559876543",
        "body": "Hello from Python!"
    }
)

if response.status_code == 201:
    message_id = response.json()['id']
    print(f"Message sent: {message_id}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### Node.js Example

```javascript
const axios = require('axios');

const projectId = process.env.SIGNALWIRE_PROJECT_ID;
const apiToken = process.env.SIGNALWIRE_API_TOKEN;
const spaceUrl = process.env.SIGNALWIRE_SPACE_URL;

async function sendSMS() {
  try {
    const response = await axios.post(
      `${spaceUrl}/api/messaging/messages`,
      {
        from: '+15551234567',
        to: '+15559876543',
        body: 'Hello from Node.js!'
      },
      {
        auth: {
          username: projectId,
          password: apiToken
        },
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );

    console.log(`Message sent: ${response.data.id}`);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

sendSMS();
```

### Sending MMS (Python)

```python
response = requests.post(
    f"{space_url}/api/messaging/messages",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "from": "+15551234567",
        "to": "+15559876543",
        "body": "Here's your receipt",
        "media": [
            "https://example.com/receipt.pdf",
            "https://example.com/logo.png"
        ]
    }
)
```

**Supported media types**: Images (JPG, PNG, GIF), Videos (MP4), PDFs, Audio files

## Receiving Messages

### Configure Webhook

1. **Dashboard**: Go to Phone Numbers → Select number → Messaging Settings
2. Set **When a message comes in**: `https://example.com/incoming-sms`
3. Method: `POST`

### Webhook Payload

SignalWire sends POST request with JSON body:

```json
{
  "message_id": "msg_xxxxxxxx",
  "from": "+15559876543",
  "to": "+15551234567",
  "body": "Hello!",
  "media": [],
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Python (Flask) Webhook Handler

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/incoming-sms', methods=['POST'])
def handle_sms():
    data = request.json

    from_number = data.get('from')
    to_number = data.get('to')
    body = data.get('body')
    media = data.get('media', [])

    print(f"Message from {from_number}: {body}")

    # Process message
    if body.lower() == 'help':
        # Send auto-reply
        send_sms(
            to=from_number,
            from_number=to_number,
            body="Available commands: HELP, STATUS, INFO"
        )

    return jsonify({"status": "received"})

def send_sms(to, from_number, body):
    requests.post(
        f"{space_url}/api/messaging/messages",
        auth=HTTPBasicAuth(project_id, api_token),
        json={
            "from": from_number,
            "to": to,
            "body": body
        }
    )

if __name__ == '__main__':
    app.run(port=5000)
```

### Node.js (Express) Webhook Handler

```javascript
const express = require('express');
const app = express();

app.use(express.json());

app.post('/incoming-sms', async (req, res) => {
  const { from, to, body, media } = req.body;

  console.log(`Message from ${from}: ${body}`);

  // Auto-reply logic
  if (body.toLowerCase() === 'help') {
    await sendSMS(from, to, 'Available commands: HELP, STATUS, INFO');
  }

  res.json({ status: 'received' });
});

async function sendSMS(to, from, body) {
  await axios.post(
    `${process.env.SIGNALWIRE_SPACE_URL}/api/messaging/messages`,
    { from, to, body },
    {
      auth: {
        username: process.env.SIGNALWIRE_PROJECT_ID,
        password: process.env.SIGNALWIRE_API_TOKEN
      }
    }
  );
}

app.listen(5000, () => console.log('Server running on port 5000'));
```

## Sending SMS from SWML (During Calls)

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - say:
        text: "Sending you a confirmation SMS"
    - send_sms:
        to_number: "%{call.from}"
        from_number: "%{call.to}"
        body: "Thank you for calling! Your reference number is 12345"
    - say:
        text: "Message sent. Have a great day!"
    - hangup: {}
```

## Realtime SDK (Python)

```python
from signalwire.realtime import Client

async def main():
    client = Client(
        project=os.getenv('SIGNALWIRE_PROJECT_ID'),
        token=os.getenv('SIGNALWIRE_API_TOKEN')
    )

    # Send message
    result = await client.messaging.send(
        from_number='+15551234567',
        to_number='+15559876543',
        body='Hello from Realtime SDK!'
    )

    print(f"Message ID: {result.message_id}")

    # Listen for incoming messages
    @client.messaging.on('message.received')
    async def on_message(message):
        print(f"Received: {message.body} from {message.from_number}")

        # Auto-reply
        await client.messaging.send(
            from_number=message.to_number,
            to_number=message.from_number,
            body=f"You said: {message.body}"
        )

    await client.connect()
```

## Realtime SDK (JavaScript)

```javascript
const { Messaging } = require('@signalwire/realtime-api');

async function main() {
  const client = new Messaging.Client({
    project: process.env.SIGNALWIRE_PROJECT_ID,
    token: process.env.SIGNALWIRE_API_TOKEN
  });

  // Send message
  const result = await client.send({
    from: '+15551234567',
    to: '+15559876543',
    body: 'Hello from Realtime SDK!'
  });

  console.log(`Message ID: ${result.messageId}`);

  // Listen for incoming
  client.on('message.received', async (message) => {
    console.log(`Received: ${message.body} from ${message.from}`);

    // Auto-reply
    await client.send({
      from: message.to,
      to: message.from,
      body: `You said: ${message.body}`
    });
  });

  await client.connect();
}

main();
```

## Message Status Tracking

### Request Delivery Receipts

```python
response = requests.post(
    f"{space_url}/api/messaging/messages",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "from": "+15551234567",
        "to": "+15559876543",
        "body": "Hello!",
        "status_callback": "https://example.com/message-status"
    }
)
```

### Status Webhook Payload

```json
{
  "message_id": "msg_xxxxxxxx",
  "status": "delivered",
  "timestamp": "2025-01-15T10:30:15Z"
}
```

**Status values**:
- `queued`: Message queued for sending
- `sending`: Currently being sent
- `sent`: Sent to carrier
- `delivered`: Delivered to recipient
- `failed`: Delivery failed
- `undelivered`: Could not deliver

## Common Use Cases

### Two-Factor Authentication (2FA)

```python
import random

def send_2fa_code(phone_number):
    code = random.randint(100000, 999999)

    # Store code in database with expiration
    # ... database logic ...

    # Send SMS
    requests.post(
        f"{space_url}/api/messaging/messages",
        auth=HTTPBasicAuth(project_id, api_token),
        json={
            "from": "+15551234567",
            "to": phone_number,
            "body": f"Your verification code is: {code}. Expires in 5 minutes."
        }
    )

    return code
```

### Appointment Reminders

```python
def send_reminder(appointment):
    body = f"""
Hi {appointment.patient_name},

This is a reminder of your appointment:
Date: {appointment.date}
Time: {appointment.time}
Provider: {appointment.doctor}

Reply CONFIRM to confirm or CANCEL to cancel.
    """.strip()

    requests.post(
        f"{space_url}/api/messaging/messages",
        auth=HTTPBasicAuth(project_id, api_token),
        json={
            "from": "+15551234567",
            "to": appointment.phone,
            "body": body
        }
    )
```

### SMS Chatbot

```python
@app.route('/incoming-sms', methods=['POST'])
def chatbot():
    data = request.json
    from_number = data.get('from')
    body = data.get('body', '').strip().upper()

    # Command routing
    commands = {
        'BALANCE': get_balance,
        'HOURS': get_hours,
        'LOCATION': get_location,
        'HELP': get_help
    }

    handler = commands.get(body, handle_unknown)
    response_text = handler(from_number)

    # Send response
    send_sms(to=from_number, body=response_text)

    return jsonify({"status": "ok"})

def get_balance(phone):
    # Look up balance
    return "Your current balance is $42.50"

def get_hours(phone):
    return "We're open Mon-Fri 9am-5pm"

def get_location(phone):
    return "123 Main St, Anytown USA. https://maps.example.com/..."

def get_help(phone):
    return "Commands: BALANCE, HOURS, LOCATION, HELP"

def handle_unknown(phone):
    return "Unknown command. Reply HELP for available commands."
```

### Bulk Messaging

```python
def send_bulk_sms(recipients, message):
    results = []

    for phone_number in recipients:
        try:
            response = requests.post(
                f"{space_url}/api/messaging/messages",
                auth=HTTPBasicAuth(project_id, api_token),
                json={
                    "from": "+15551234567",
                    "to": phone_number,
                    "body": message
                },
                timeout=10
            )

            results.append({
                "phone": phone_number,
                "success": response.status_code == 201,
                "message_id": response.json().get('id')
            })

        except Exception as e:
            results.append({
                "phone": phone_number,
                "success": False,
                "error": str(e)
            })

    return results

# Usage
recipients = ['+15551111111', '+15552222222', '+15553333333']
message = "Sale ends today! Visit example.com for 20% off."
send_bulk_sms(recipients, message)
```

## Character Limits & Segmentation

- **SMS limit**: 160 characters (standard)
- **Unicode (emoji)**: 70 characters per segment
- **Long messages**: Auto-split into multiple segments
- **MMS**: Up to 5MB media per message

## Compliance & Best Practices

1. **Opt-in required**: Get consent before messaging
2. **Opt-out handling**: Honor STOP/UNSUBSCRIBE requests
3. **Rate limiting**: Don't exceed carrier limits
4. **A2P 10DLC**: Register campaigns for business messaging
5. **Time restrictions**: Respect quiet hours (varies by region)

### STOP Handling

```python
@app.route('/incoming-sms', methods=['POST'])
def handle_sms():
    data = request.json
    from_number = data.get('from')
    body = data.get('body', '').strip().upper()

    if body in ['STOP', 'UNSUBSCRIBE', 'CANCEL']:
        # Add to opt-out list
        add_to_optout_list(from_number)

        # Send confirmation
        send_sms(
            to=from_number,
            body="You have been unsubscribed. Reply START to re-subscribe."
        )
    elif body == 'START':
        # Remove from opt-out list
        remove_from_optout_list(from_number)
        send_sms(
            to=from_number,
            body="You have been re-subscribed. Reply STOP to unsubscribe."
        )
    else:
        # Normal message handling
        if is_opted_out(from_number):
            return jsonify({"status": "opted_out"})

        # Process message...

    return jsonify({"status": "ok"})
```

## Error Handling

### Common Errors

**400 Bad Request**
- Invalid phone number format
- Message body too long

**402 Payment Required**
- Insufficient balance

**403 Forbidden**
- Number not enabled for messaging
- Sending to blocked number

**429 Too Many Requests**
- Rate limit exceeded

### Retry Logic

```python
import time
from requests.exceptions import RequestException

def send_sms_with_retry(to, body, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{space_url}/api/messaging/messages",
                auth=HTTPBasicAuth(project_id, api_token),
                json={"from": "+15551234567", "to": to, "body": body},
                timeout=10
            )

            if response.status_code == 201:
                return response.json()

            # Don't retry client errors
            if 400 <= response.status_code < 500:
                raise Exception(f"Client error: {response.text}")

            # Retry server errors
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff

        except RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)

    raise Exception("Max retries exceeded")
```

## Testing

### Using Test Numbers

SignalWire provides test numbers for development:
- Messages sent to test numbers don't actually deliver
- Check Dashboard logs to verify message content

### Local Development

```bash
# Use ngrok for webhook testing
ngrok http 5000

# Update webhook URL in Dashboard to ngrok URL
# https://abc123.ngrok.io/incoming-sms
```

## Next Steps

- [Voice AI](voice-ai.md) - Add AI to messaging conversations
- [Webhooks & Events](webhooks-events.md) - Advanced event handling
- [Number Management](number-management.md) - Configure messaging numbers
