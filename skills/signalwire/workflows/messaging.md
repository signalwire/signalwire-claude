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

## Campaign Registry Requirements

**CRITICAL:** All A2P (Application-to-Person) messaging to US numbers requires registration.

### Required For

- Long codes (10-digit local numbers)
- Toll-free numbers
- Short codes
- Any outbound SMS/MMS

### Registration Process

#### 1. Create Brand

Navigate to: **Messaging Campaigns** > **Brands** > **New**

Required information:
- Legal business name
- EIN/Tax ID
- Business type
- Contact information
- Business address

```python
# Creating a brand via API
response = requests.post(
    f"{space_url}/api/messaging/brands",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "legal_name": "Acme Corporation",
        "ein": "12-3456789",
        "business_type": "corporation",
        "email": "compliance@acme.com",
        "phone": "+15551234567",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "postal_code": "90210",
            "country": "US"
        }
    }
)

brand_id = response.json()['id']
```

#### 2. Create Campaign

Navigate to: **Messaging Campaigns** > **Campaigns** > **New**

Campaign details:
- Brand selection
- Use case description (e.g., "Appointment reminders", "Marketing")
- Message samples (provide 2-3 example messages)
- Volume estimates (messages per day/month)
- Opt-in/opt-out processes

```python
# Creating a campaign via API
response = requests.post(
    f"{space_url}/api/messaging/campaigns",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "brand_id": brand_id,
        "use_case": "appointment_reminders",
        "description": "Automated appointment confirmation and reminder messages",
        "sample_messages": [
            "Hi {name}, your appointment is confirmed for {date} at {time}. Reply STOP to opt out.",
            "Reminder: You have an appointment tomorrow at {time}. Reply C to confirm or R to reschedule."
        ],
        "message_volume": "1000",
        "opt_in_workflow": "Customers opt-in during account creation",
        "opt_out_keywords": ["STOP", "UNSUBSCRIBE", "CANCEL"]
    }
)

campaign_id = response.json()['id']
```

#### 3. Associate Phone Number

Navigate to: **Phone Numbers** > Select Number > **Edit**

Link number to campaign and save:

```python
# Associate number with campaign
response = requests.put(
    f"{space_url}/api/relay/rest/phone_numbers/{number_sid}",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "messaging_campaign_id": campaign_id
    }
)
```

**Processing Time:** Campaign approval can take 1-2 weeks

## Message Templates and Best Practices

### Template Patterns

```python
# Define reusable message templates
templates = {
    "appointment_confirm": lambda name, datetime:
        f"Hi {name}, your appointment is confirmed for {datetime}. Reply STOP to opt out.",

    "appointment_reminder": lambda name, datetime:
        f"Reminder: You have an appointment tomorrow at {datetime}. Reply C to confirm or R to reschedule.",

    "opt_out": lambda:
        "You have been unsubscribed. Reply START to opt back in.",

    "opt_in_confirm": lambda:
        "Thank you for subscribing! You'll receive appointment reminders. Reply STOP to unsubscribe.",
}

# Use templates
message_body = templates["appointment_confirm"]("John Doe", "Jan 15, 2025 at 2:00 PM")
```

### Best Practices

1. **Always Include Opt-Out Language**
   ```python
   message = f"{content} Reply STOP to opt out."
   ```

2. **Keep Messages Concise**
   - SMS limit: 160 characters (standard)
   - Unicode/emoji: 70 characters per segment
   - Long messages auto-split into multiple segments

3. **Personalize When Possible**
   ```python
   message = f"Hi {customer_name}, {content}"
   ```

4. **Include Sender Identification**
   ```python
   message = f"From Acme Healthcare: {content}"
   ```

5. **Respect Quiet Hours**
   ```python
   from datetime import datetime

   def should_send_message(timezone='America/New_York'):
       hour = datetime.now(tz=timezone).hour
       # Don't send between 9 PM and 8 AM
       if hour >= 21 or hour < 8:
           return False
       return True
   ```

## Opt-In/Opt-Out Handling

### Inbound Message Handler with Opt-Out

```python
# Opt-out database (use actual database in production)
opted_out_numbers = set()

@app.route('/incoming-sms', methods=['POST'])
def handle_sms():
    data = request.json
    from_number = data.get('from')
    body = data.get('body', '').strip().upper()

    # Handle STOP/UNSUBSCRIBE
    if body in ['STOP', 'UNSUBSCRIBE', 'CANCEL', 'END', 'QUIT']:
        opted_out_numbers.add(from_number)

        # Send confirmation
        send_sms(
            to=from_number,
            from_number=data.get('to'),
            body="You have been unsubscribed. Reply START to opt back in."
        )

        # Log opt-out
        log_opt_out(from_number)

        return jsonify({"status": "opted_out"}), 200

    # Handle START/SUBSCRIBE
    elif body in ['START', 'SUBSCRIBE', 'YES']:
        if from_number in opted_out_numbers:
            opted_out_numbers.remove(from_number)

        send_sms(
            to=from_number,
            from_number=data.get('to'),
            body="You have been re-subscribed. Reply STOP to unsubscribe."
        )

        log_opt_in(from_number)

        return jsonify({"status": "opted_in"}), 200

    # Handle HELP
    elif body == 'HELP':
        send_sms(
            to=from_number,
            from_number=data.get('to'),
            body="Commands: HELP, STOP. For support, call (555) 123-4567."
        )
        return jsonify({"status": "help_sent"}), 200

    # Check opt-out status before processing
    if from_number in opted_out_numbers:
        return jsonify({"status": "user_opted_out"}), 200

    # Process message normally
    process_message(from_number, body)

    return jsonify({"status": "ok"}), 200

def send_sms(to, from_number, body):
    """Helper to send SMS"""
    requests.post(
        f"{space_url}/api/messaging/messages",
        auth=HTTPBasicAuth(project_id, api_token),
        json={
            "from": from_number,
            "to": to,
            "body": body
        }
    )
```

### Required Opt-Out Keywords

Per CTIA guidelines, support these keywords:
- STOP
- STOPALL
- UNSUBSCRIBE
- CANCEL
- END
- QUIT

### Required Opt-In Keywords

- START
- UNSTOP
- SUBSCRIBE
- YES

## Delivery Status Tracking Patterns

### Track Message Status

```python
import time
from enum import Enum

class MessageStatus(Enum):
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    UNDELIVERED = "undelivered"

# Track message statuses
message_tracking = {}

def send_tracked_message(to, from_number, body):
    """Send message with delivery tracking"""

    response = requests.post(
        f"{space_url}/api/messaging/messages",
        auth=HTTPBasicAuth(project_id, api_token),
        json={
            "from": from_number,
            "to": to,
            "body": body,
            "status_callback": "https://example.com/message-status"
        }
    )

    if response.status_code == 201:
        message_data = response.json()
        message_id = message_data['id']

        # Track message
        message_tracking[message_id] = {
            'to': to,
            'status': MessageStatus.QUEUED,
            'sent_at': time.time(),
            'delivered_at': None,
            'attempts': 1
        }

        return message_id
    else:
        return None

@app.route('/message-status', methods=['POST'])
def handle_message_status():
    """Handle delivery status callbacks"""
    data = request.json

    message_id = data.get('message_id')
    status = data.get('status')

    if message_id in message_tracking:
        message_tracking[message_id]['status'] = MessageStatus(status)

        if status == 'delivered':
            message_tracking[message_id]['delivered_at'] = time.time()

            # Calculate delivery time
            sent_at = message_tracking[message_id]['sent_at']
            delivery_time = time.time() - sent_at

            print(f"Message {message_id} delivered in {delivery_time:.2f}s")

        elif status == 'failed':
            # Handle failed delivery
            handle_failed_message(message_id, message_tracking[message_id])

    return jsonify({"status": "ok"}), 200

def handle_failed_message(message_id, message_data):
    """Retry or log failed message"""
    if message_data['attempts'] < 3:
        # Retry
        message_data['attempts'] += 1
        time.sleep(60)  # Wait before retry

        send_tracked_message(
            to=message_data['to'],
            from_number='+15551234567',
            body="Retry attempt"
        )
    else:
        # Log permanent failure
        print(f"Message {message_id} failed after 3 attempts")
        # Alert admin, log to database, etc.
```

## MMS Support Patterns

### Sending Images

```python
def send_mms_image(to, from_number, body, image_url):
    """Send MMS with image"""
    response = requests.post(
        f"{space_url}/api/messaging/messages",
        auth=HTTPBasicAuth(project_id, api_token),
        json={
            "from": from_number,
            "to": to,
            "body": body,
            "media_urls": [image_url]
        }
    )
    return response.json()

# Usage
send_mms_image(
    to="+15559876543",
    from_number="+15551234567",
    body="Your receipt is attached",
    image_url="https://example.com/receipts/12345.pdf"
)
```

### Supported Media Formats

**Images:**
- JPG, PNG, GIF
- Max size: 5MB per message

**Documents:**
- PDF

**Audio:**
- MP3, WAV

**Video:**
- MP4, 3GP

### Multiple Media Files

```python
send_multiple_media(
    to="+15559876543",
    from_number="+15551234567",
    body="Here are your documents",
    media_urls=[
        "https://example.com/doc1.pdf",
        "https://example.com/image.jpg",
        "https://example.com/video.mp4"
    ]
)
```

### Receiving MMS

```python
@app.route('/incoming-sms', methods=['POST'])
def handle_incoming_mms():
    data = request.json

    from_number = data.get('from')
    body = data.get('body', '')
    media = data.get('media', [])

    if media:
        print(f"Received {len(media)} media files from {from_number}")

        for media_url in media:
            # Download and process media
            process_media(media_url, from_number)

    return jsonify({"status": "ok"}), 200

def process_media(media_url, from_number):
    """Download and process received media"""
    response = requests.get(media_url)

    if response.status_code == 200:
        # Save or process media
        content_type = response.headers.get('Content-Type')

        if content_type.startswith('image/'):
            # Process image
            save_image(response.content, from_number)
        elif content_type == 'application/pdf':
            # Process PDF
            save_pdf(response.content, from_number)
```

## Relay SDK Messaging Patterns

### Modern Messaging Client (Relay v4)

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = ["signalwire"]
# ///

import os
from signalwire.realtime import Client

async def main():
    client = Client(
        project=os.getenv('SIGNALWIRE_PROJECT_ID'),
        token=os.getenv('SIGNALWIRE_API_TOKEN')
    )

    # Event-driven message handling
    @client.messaging.on('message.received')
    async def on_message(message):
        print(f"Received: {message.body} from {message.from_number}")

        # Auto-process common commands
        if message.body.upper() == 'STOP':
            await handle_opt_out(message.from_number)
        elif message.body.upper() == 'START':
            await handle_opt_in(message.from_number)
        else:
            # Route to appropriate handler
            await route_message(message)

    # Send message with delivery tracking
    result = await client.messaging.send(
        from_number='+15551234567',
        to_number='+15559876543',
        body='Hello from Realtime SDK!',
        status_callback='https://example.com/status'
    )

    print(f"Message ID: {result.message_id}")

    await client.connect()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

### Context-Based Routing

```python
# Route messages to different contexts
client = Client(
    project=os.getenv('SIGNALWIRE_PROJECT_ID'),
    token=os.getenv('SIGNALWIRE_API_TOKEN'),
    contexts=['support', 'sales', 'billing']
)

# Send to specific context
await client.messaging.send(
    from_number='+15551234567',
    to_number='+15559876543',
    body='Your support ticket is ready',
    context='support'
)
```

## Production Messaging Tips

### Rate Limiting

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_per_second=10):
        self.max_per_second = max_per_second
        self.timestamps = deque()

    def wait_if_needed(self):
        now = time.time()

        # Remove timestamps older than 1 second
        while self.timestamps and self.timestamps[0] < now - 1:
            self.timestamps.popleft()

        # If at limit, wait
        if len(self.timestamps) >= self.max_per_second:
            sleep_time = 1 - (now - self.timestamps[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.timestamps.append(time.time())

# Usage
rate_limiter = RateLimiter(max_per_second=10)

for recipient in recipients:
    rate_limiter.wait_if_needed()
    send_sms(recipient, message)
```

### Personalization

```python
def personalize_message(template, customer_data):
    """Replace placeholders with customer data"""
    return template.format(**customer_data)

# Template
template = "Hi {name}, your {appointment_type} appointment is on {date} at {time}."

# Customer data
customer = {
    "name": "John Doe",
    "appointment_type": "dental cleaning",
    "date": "January 20",
    "time": "2:00 PM"
}

# Personalized message
message = personalize_message(template, customer)
# "Hi John Doe, your dental cleaning appointment is on January 20 at 2:00 PM."
```

### Error Recovery

```python
def send_with_retry(to, from_number, body, max_retries=3):
    """Send message with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{space_url}/api/messaging/messages",
                auth=HTTPBasicAuth(project_id, api_token),
                json={
                    "from": from_number,
                    "to": to,
                    "body": body
                },
                timeout=10
            )

            if response.status_code == 201:
                return response.json()

            # Don't retry client errors
            if 400 <= response.status_code < 500:
                raise Exception(f"Client error: {response.text}")

            # Retry server errors with backoff
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt  # 1s, 2s, 4s
                time.sleep(sleep_time)

        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)

    raise Exception("Max retries exceeded")
```

## Next Steps

- [Voice AI](voice-ai.md) - Add AI to messaging conversations
- [Webhooks & Events](webhooks-events.md) - Advanced event handling
- [Number Management](number-management.md) - Configure messaging numbers and campaigns
