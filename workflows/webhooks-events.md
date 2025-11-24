# Webhooks & Events

## Overview

SignalWire sends HTTP POST requests to your server when events occur (call state changes, messages received, etc.). Webhooks enable event-driven application architecture.

## Common Webhook Types

1. **Status Callbacks**: Call state changes (queued, ringing, answered, ended)
2. **Message Webhooks**: Incoming SMS/MMS
3. **Video Events**: Room joined, member left, recording complete
4. **Call Events**: SWML fetch, call progress updates

## Call Status Webhooks

### Configuring Status URL

When creating a call via REST API:

```python
response = requests.post(
    f"{space_url}/api/calling/calls",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "command": "dial",
        "params": {
            "from": "+15551234567",
            "to": "+15559876543",
            "url": "https://example.com/swml",
            "status_url": "https://example.com/call-status"  # Status webhook
        }
    }
)
```

### Status Webhook Payload

SignalWire sends POST requests with JSON body:

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

### Call States

- **queued**: Call request received, not yet initiated
- **created**: Call has been created
- **ringing**: Destination is ringing
- **answered**: Call was answered
- **ended**: Call has terminated

### Handling Status Webhooks (Python/Flask)

```python
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

@app.route('/call-status', methods=['POST'])
def handle_call_status():
    data = request.json

    call_id = data.get('call_id')
    status = data.get('call_state')
    from_number = data.get('from')
    to_number = data.get('to')
    timestamp = data.get('timestamp')

    logging.info(f"Call {call_id}: {status}")

    # Handle different states
    if status == 'queued':
        # Call queued, log or update UI
        pass

    elif status == 'ringing':
        # Destination is ringing
        # Update database, notify admin, etc.
        update_call_status(call_id, 'ringing')

    elif status == 'answered':
        # Call answered - start timer, analytics, etc.
        logging.info(f"Call answered at {timestamp}")
        start_call_timer(call_id)

    elif status == 'ended':
        # Call ended - calculate duration, billing, etc.
        logging.info("Call ended")
        finalize_call_record(call_id)

    return jsonify({"status": "received"}), 200

def update_call_status(call_id, status):
    # Update database...
    pass

def start_call_timer(call_id):
    # Start billing timer...
    pass

def finalize_call_record(call_id):
    # Calculate duration, cost, etc.
    pass

if __name__ == '__main__':
    app.run(port=5000)
```

### Handling Status Webhooks (Node.js/Express)

```javascript
const express = require('express');
const app = express();

app.use(express.json());

app.post('/call-status', (req, res) => {
  const { call_id, call_state, from, to, timestamp } = req.body;

  console.log(`Call ${call_id}: ${call_state}`);

  switch (call_state) {
    case 'queued':
      // Handle queued state
      break;

    case 'ringing':
      console.log('Call is ringing');
      updateCallStatus(call_id, 'ringing');
      break;

    case 'answered':
      console.log(`Call answered at ${timestamp}`);
      startCallTimer(call_id);
      break;

    case 'ended':
      console.log('Call ended');
      finalizeCallRecord(call_id);
      break;
  }

  res.json({ status: 'received' });
});

app.listen(5000, () => {
  console.log('Webhook server running on port 5000');
});
```

## Messaging Webhooks

### Configuring Message Webhook

1. **Dashboard**: Phone Numbers → Select number → Messaging Settings
2. Set **When a message comes in**: `https://example.com/incoming-sms`
3. Method: `POST`

### Message Webhook Payload

```json
{
  "message_id": "msg_xxxxxxxx",
  "from": "+15559876543",
  "to": "+15551234567",
  "body": "Hello, SignalWire!",
  "media": [
    "https://example.com/image.jpg"
  ],
  "timestamp": "2025-01-15T10:30:00Z",
  "num_segments": 1,
  "num_media": 1
}
```

### Handling Incoming Messages

```python
@app.route('/incoming-sms', methods=['POST'])
def handle_incoming_sms():
    data = request.json

    from_number = data.get('from')
    to_number = data.get('to')
    body = data.get('body', '').strip()
    media = data.get('media', [])

    logging.info(f"Message from {from_number}: {body}")

    # Process message
    response_text = process_message(from_number, body)

    # Send auto-reply
    if response_text:
        send_sms(to=from_number, from_number=to_number, body=response_text)

    return jsonify({"status": "ok"}), 200

def process_message(from_number, body):
    # Your message processing logic
    if body.upper() == 'HELP':
        return "Available commands: HELP, STATUS, INFO"
    elif body.upper() == 'STATUS':
        return "Your account is active"
    else:
        return None  # No auto-reply
```

### Message Delivery Status

Request delivery receipts:

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

### Message Status Webhook Payload

```json
{
  "message_id": "msg_xxxxxxxx",
  "status": "delivered",
  "error_code": null,
  "timestamp": "2025-01-15T10:30:15Z"
}
```

**Status values**:
- `queued`: Queued for sending
- `sending`: Currently being sent
- `sent`: Sent to carrier
- `delivered`: Delivered to recipient
- `failed`: Delivery failed
- `undelivered`: Could not deliver

## SWML Webhooks

### SWML Fetch Webhook

When a call comes in, SignalWire fetches SWML from your configured URL.

**Request from SignalWire**:
```
GET https://example.com/swml?From=+15559876543&To=+15551234567&CallSid=c1234567...
```

**Query Parameters**:
- `From`: Caller's phone number
- `To`: Destination number (your number)
- `CallSid`: Unique call identifier
- `Direction`: `inbound` or `outbound`

**Your Response**:
```python
from flask import Flask, request, jsonify

@app.route('/swml')
def serve_swml():
    from_number = request.args.get('From')
    to_number = request.args.get('To')
    call_sid = request.args.get('CallSid')

    logging.info(f"SWML fetch for call from {from_number}")

    # Generate dynamic SWML based on caller
    if is_vip_customer(from_number):
        swml = generate_vip_swml(from_number)
    else:
        swml = generate_standard_swml(from_number)

    return jsonify(swml)

def generate_vip_swml(from_number):
    return {
        "version": "1.0.0",
        "sections": {
            "main": [
                {"answer": {}},
                {"say": {"text": f"Welcome back, valued customer {from_number}"}},
                {"connect": {"to": "+15551111111"}}  # VIP queue
            ]
        }
    }

def generate_standard_swml(from_number):
    return {
        "version": "1.0.0",
        "sections": {
            "main": [
                {"answer": {}},
                {"say": {"text": "Welcome to our service"}},
                {"transfer": {"dest": "main_menu"}}
            ],
            "main_menu": [
                {"prompt": {
                    "say": "Press 1 for sales, 2 for support",
                    "max_digits": 1
                }}
            ]
        }
    }
```

## Video Room Webhooks

### Configuring Video Webhooks

```python
# Create room with webhooks
response = requests.post(
    f"{space_url}/api/video/rooms",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "name": "my-meeting",
        "event_webhooks": {
            "room.started": "https://example.com/video/room-started",
            "room.ended": "https://example.com/video/room-ended",
            "recording.completed": "https://example.com/video/recording-ready"
        }
    }
)
```

### Video Event Types

- `room.started`: Room session began
- `room.ended`: All participants left
- `member.joined`: Participant joined
- `member.left`: Participant left
- `recording.started`: Recording began
- `recording.completed`: Recording ready for download

### Handling Video Webhooks

```python
@app.route('/video/room-started', methods=['POST'])
def handle_room_started():
    data = request.json

    room_id = data.get('room_id')
    room_name = data.get('room_name')
    timestamp = data.get('timestamp')

    logging.info(f"Room {room_name} started at {timestamp}")

    # Send notifications, update UI, etc.
    notify_admins(f"Meeting {room_name} has started")

    return jsonify({"status": "ok"}), 200

@app.route('/video/recording-ready', methods=['POST'])
def handle_recording_ready():
    data = request.json

    room_id = data.get('room_id')
    recording_url = data.get('recording_url')
    duration = data.get('duration')

    logging.info(f"Recording ready: {recording_url}")

    # Store recording, send to cloud storage, notify users
    save_recording(room_id, recording_url, duration)
    notify_participants(room_id, recording_url)

    return jsonify({"status": "ok"}), 200
```

## Webhook Security

### Verify Webhook Source

#### Option 1: IP Allowlist

```python
SIGNALWIRE_IPS = [
    '1.2.3.4',  # Example SignalWire IP ranges
    '5.6.7.8'
]

@app.before_request
def verify_source_ip():
    client_ip = request.remote_addr

    if request.path.startswith('/webhook/'):
        if client_ip not in SIGNALWIRE_IPS:
            logging.warning(f"Rejected webhook from {client_ip}")
            abort(403)
```

#### Option 2: Shared Secret

Include a secret token in webhook URL:

```python
# When configuring webhook
webhook_url = f"https://example.com/webhook?secret={SECRET_TOKEN}"

# In webhook handler
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    provided_secret = request.args.get('secret')

    if provided_secret != SECRET_TOKEN:
        logging.warning("Invalid webhook secret")
        abort(403)

    # Process webhook...
```

#### Option 3: HTTP Basic Auth

Configure webhooks with authentication:

```python
# In SWML or API call
json={
    "status_url": "https://username:password@example.com/webhook"
}

# Or configure in Dashboard with auth credentials
```

### HTTPS Required

**IMPORTANT**: Always use HTTPS for webhook URLs to protect data in transit.

```python
# Good
"status_url": "https://example.com/webhook"

# Bad - will fail or be rejected
"status_url": "http://example.com/webhook"
```

## Webhook Retry Logic

If your server returns an error (5xx) or times out, SignalWire will retry:

- **Retry attempts**: 3-5 times
- **Backoff**: Exponential (1s, 2s, 4s, 8s)
- **Timeout**: 10 seconds per attempt

### Handling Retries (Idempotency)

```python
processed_events = set()  # Or use database

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    event_id = data.get('call_id') or data.get('message_id')

    # Check if already processed
    if event_id in processed_events:
        logging.info(f"Duplicate event {event_id}, ignoring")
        return jsonify({"status": "duplicate"}), 200

    # Process event
    process_event(data)

    # Mark as processed
    processed_events.add(event_id)

    return jsonify({"status": "ok"}), 200
```

## Local Development & Testing

### Using ngrok

```bash
# Start your local server
python app.py  # Runs on localhost:5000

# Expose with ngrok
ngrok http 5000

# Copy ngrok URL and configure in SignalWire
# Example: https://abc123.ngrok.io/webhook
```

### Testing Webhooks Manually

Use curl to simulate webhook requests:

```bash
curl -X POST https://localhost:5000/call-status \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "test-123",
    "call_state": "answered",
    "from": "+15551234567",
    "to": "+15559876543",
    "timestamp": "2025-01-15T10:30:00Z"
  }'
```

## Error Handling Best Practices

### Always Return 200 OK

```python
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        data = request.json
        process_event(data)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        # Log error but still return 200
        logging.error(f"Webhook processing error: {e}")

        # Store for manual review
        save_failed_webhook(data, str(e))

        # Return 200 to prevent retries
        return jsonify({"status": "error", "message": str(e)}), 200
```

### Async Processing

For long-running tasks, acknowledge immediately and process asynchronously:

```python
from threading import Thread
from queue import Queue

webhook_queue = Queue()

def webhook_processor():
    while True:
        data = webhook_queue.get()
        try:
            process_webhook(data)
        except Exception as e:
            logging.error(f"Processing error: {e}")
        webhook_queue.task_done()

# Start background thread
Thread(target=webhook_processor, daemon=True).start()

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json

    # Queue for processing
    webhook_queue.put(data)

    # Return immediately
    return jsonify({"status": "queued"}), 200
```

## Monitoring & Logging

### Log All Webhooks

```python
import json
from datetime import datetime

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Log raw webhook
    webhook_log = {
        'timestamp': datetime.utcnow().isoformat(),
        'path': request.path,
        'data': request.json,
        'headers': dict(request.headers)
    }

    logging.info(f"Webhook received: {json.dumps(webhook_log)}")

    # Process...
    return jsonify({"status": "ok"}), 200
```

### Dashboard Logs

Check SignalWire Dashboard > Logs for:
- Webhook delivery attempts
- Response status codes
- Retry history
- Errors

## Common Patterns

### Call Analytics

```python
call_analytics = {}

@app.route('/call-status', methods=['POST'])
def track_call_analytics():
    data = request.json

    call_id = data['call_id']
    status = data['call_state']

    if call_id not in call_analytics:
        call_analytics[call_id] = {}

    call_analytics[call_id][status] = datetime.utcnow()

    if status == 'ended':
        # Calculate metrics
        answered_at = call_analytics[call_id].get('answered')
        ended_at = call_analytics[call_id]['ended']

        if answered_at:
            duration = (ended_at - answered_at).total_seconds()
            logging.info(f"Call duration: {duration}s")

    return jsonify({"status": "ok"}), 200
```

### Notification System

```python
@app.route('/incoming-sms', methods=['POST'])
def forward_to_email():
    data = request.json

    from_number = data['from']
    body = data['body']

    # Send email notification
    send_email(
        to='admin@example.com',
        subject=f'New SMS from {from_number}',
        body=body
    )

    return jsonify({"status": "ok"}), 200
```

## Post-Prompt Processing Patterns

### Collect Data After AI Call Ends

Use `post_prompt_url` to gather structured data from conversations:

```yaml
# SWML with post-prompt collection
- ai:
    prompt: |
      Gather customer name, phone, and order details.
      Be conversational and friendly.
    post_prompt_url: "https://yourserver.com/summary"
    post_prompt: |
      Summarize the conversation as a valid JSON object.
      Include: customer_name, customer_phone, customer_order
```

### Server Receives Structured Data

```python
@app.route('/summary', methods=['POST'])
def handle_post_prompt():
    data = request.json

    # Parsed data from AI
    parsed = data.get('post_prompt_data', {}).get('parsed', {})

    customer_name = parsed.get('customer_name')
    customer_phone = parsed.get('customer_phone')
    customer_order = parsed.get('customer_order', [])

    # Full conversation transcript
    conversation = data.get('conversation', [])

    # Call metadata
    call_id = data.get('call_id')
    ai_session_id = data.get('ai_session_id')

    # Store in database
    database.save({
        'customer_name': customer_name,
        'customer_phone': customer_phone,
        'order': customer_order,
        'call_id': call_id,
        'transcript': conversation,
        'timestamp': datetime.now()
    })

    # Create CRM ticket
    crm.create_ticket({
        'name': customer_name,
        'phone': customer_phone,
        'notes': format_transcript(conversation)
    })

    return jsonify({"status": "ok"}), 200
```

### Post-Prompt Analytics

```python
@app.route('/analytics', methods=['POST'])
def handle_analytics():
    data = request.json

    # Extract analytics from post-prompt
    parsed = data.get('post_prompt_data', {}).get('parsed', {})

    analytics = {
        'call_id': data.get('call_id'),
        'intent': parsed.get('intent'),  # "support", "sales", "billing"
        'resolved': parsed.get('resolved'),  # True/False
        'sentiment': parsed.get('sentiment'),  # "positive", "neutral", "negative"
        'topics': parsed.get('topics', []),  # ["refund", "shipping"]
        'action_items': parsed.get('action_items', []),
        'call_duration': calculate_duration(data.get('conversation')),
        'transfer_occurred': 'transfer' in str(data.get('conversation'))
    }

    # Store for reporting
    analytics_db.save(analytics)

    # Alert if negative sentiment
    if analytics['sentiment'] == 'negative' and not analytics['resolved']:
        alert_manager(f"Unresolved negative call: {analytics['call_id']}")

    return jsonify({"status": "ok"}), 200
```

### Post-Prompt Structure

```yaml
ai:
  params:
    post_prompt_url: "https://yourserver.com/analytics"
    post_prompt: |
      Summarize this conversation as JSON:
      {
        "intent": "primary reason for call",
        "resolved": true/false,
        "sentiment": "positive/neutral/negative",
        "topics": ["list", "of", "topics"],
        "action_items": ["follow-up tasks"],
        "customer_satisfied": true/false
      }
```

## Webhook Testing with webhook.site

### Development Pattern

```python
# Use webhook.site for testing SWAIG functions

# 1. Go to webhook.site and get temporary URL
# 2. Configure in SWML:

functions:
  - name: create_ticket
    purpose: "Create support ticket"
    web_hook: "https://webhook.site/unique-id-here"
    parameters:
      - name: title
        type: string
      - name: description
        type: string

# 3. Test AI agent
# 4. View payload in webhook.site
# 5. Iterate on response format
```

### Webhook.site Benefits

- Instant temporary URLs
- View raw payloads
- No server setup needed
- Copy/paste request data
- Test before deploying real endpoint

### Testing Workflow

```python
# After verifying payload structure on webhook.site,
# implement real endpoint:

@app.route('/swaig/create-ticket', methods=['POST'])
def create_ticket():
    data = request.json

    # data structure verified via webhook.site
    function_name = data.get('function')
    args = data.get('argument', {})

    if function_name == 'create_ticket':
        ticket = github.create_issue(
            title=args.get('title'),
            body=args.get('description')
        )

        return jsonify({
            "response": f"Ticket #{ticket.number} created successfully",
            "metadata": {
                "ticket_id": ticket.number,
                "url": ticket.html_url
            }
        })
```

## Monitoring and Observability

### Real-Time Transcription Integration

```yaml
# Enable live transcription
sections:
  main:
    - live_transcribe:
        url: "wss://yourserver.com/transcribe"
    - ai:
        prompt: "Your agent instructions"
```

### WebSocket Transcription Handler

```javascript
const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  console.log('Transcription connection established');

  ws.on('message', (data) => {
    const message = JSON.parse(data);

    if (message.event === 'transcription') {
      console.log('User said:', message.transcription.text);

      // Real-time processing
      analyzeIntent(message.transcription.text);

      // Store for records
      saveTranscript(message.transcription.text);

      // Update live dashboard
      broadcastToAgents({
        type: 'live_transcript',
        text: message.transcription.text,
        timestamp: Date.now()
      });
    }
  });
});
```

### Call Audio Streaming

Stream call audio for real-time transcription or recording:

```yaml
# SWML with audio streaming
- stream:
    url: "wss://yourserver.com/stream"
    track: "both"  # inbound, outbound, or both
- ai:
    prompt: "Your instructions"
```

### WebSocket Stream Handler

```javascript
wss.on('connection', (ws) => {
  let audioBuffer = [];

  ws.on('message', (data) => {
    const message = JSON.parse(data);

    if (message.event === 'media') {
      // Base64-encoded audio payload
      const audioChunk = Buffer.from(message.media.payload, 'base64');

      // Send to DeepGram, AssemblyAI, etc.
      transcriptionService.process(audioChunk);

      // Save to WAV file
      audioBuffer.push(audioChunk);
    }

    if (message.event === 'stop') {
      // Stream ended, save complete audio
      const wavFile = createWav(audioBuffer);
      saveToStorage(wavFile, `call-${message.call_id}.wav`);
    }
  });
});
```

### Use Cases

- Live transcription with DeepGram or AssemblyAI
- Local audio storage in WAV format
- Real-time speech analytics
- Custom call recording implementations
- Compliance monitoring

## Status Callback Handling

### Complete Status Event Tracking

```python
from enum import Enum
from datetime import datetime

class CallState(Enum):
    QUEUED = "queued"
    CREATED = "created"
    RINGING = "ringing"
    ANSWERED = "answered"
    ENDED = "ended"

# Track all call states
call_states = {}

@app.route('/call-status', methods=['POST'])
def track_call_lifecycle():
    data = request.json

    call_id = data.get('call_id')
    state = data.get('call_state')
    timestamp = data.get('timestamp')

    # Initialize tracking
    if call_id not in call_states:
        call_states[call_id] = {
            'from': data.get('from'),
            'to': data.get('to'),
            'direction': data.get('direction'),
            'states': {}
        }

    # Record state transition
    call_states[call_id]['states'][state] = timestamp

    # Handle specific states
    if state == CallState.QUEUED.value:
        log_call_queued(call_id)

    elif state == CallState.RINGING.value:
        # Calculate queue time
        queued_time = call_states[call_id]['states'].get('queued')
        if queued_time:
            queue_duration = (datetime.fromisoformat(timestamp) -
                            datetime.fromisoformat(queued_time)).total_seconds()
            metrics.record('queue_time', queue_duration)

    elif state == CallState.ANSWERED.value:
        # Calculate ring time
        ringing_time = call_states[call_id]['states'].get('ringing')
        if ringing_time:
            ring_duration = (datetime.fromisoformat(timestamp) -
                           datetime.fromisoformat(ringing_time)).total_seconds()
            metrics.record('ring_time', ring_duration)

        # Start billing
        start_billing(call_id)

    elif state == CallState.ENDED.value:
        # Calculate call duration
        answered_time = call_states[call_id]['states'].get('answered')
        if answered_time:
            duration = (datetime.fromisoformat(timestamp) -
                       datetime.fromisoformat(answered_time)).total_seconds()

            # Record metrics
            metrics.record('call_duration', duration)

            # Calculate cost
            cost = calculate_cost(duration)
            billing.record(call_id, cost)

        # Cleanup
        finalize_call(call_id)

    return jsonify({"status": "ok"}), 200
```

### Dashboard Metrics

```python
def generate_call_metrics():
    """Generate real-time call center metrics"""

    return {
        'active_calls': count_active_calls(),
        'average_wait_time': metrics.average('queue_time'),
        'average_call_duration': metrics.average('call_duration'),
        'calls_per_hour': metrics.rate('calls', hours=1),
        'answer_rate': (metrics.count('answered') / metrics.count('ringing')) * 100,
        'abandonment_rate': (metrics.count('abandoned') / metrics.count('queued')) * 100
    }
```

## Next Steps

- [Fabric & Relay](fabric-relay.md) - Alternative to webhooks using WebSocket
- [Outbound Calling](outbound-calling.md) - Configure status callbacks
- [Messaging](messaging.md) - Configure message webhooks and delivery tracking
- [Video](video.md) - Configure video event webhooks
- [Voice AI](voice-ai.md) - Post-prompt processing for AI conversations
