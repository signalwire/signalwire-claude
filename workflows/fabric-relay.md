# Fabric & Relay

## Overview

SignalWire Fabric is a unified communication framework using real-time WebSocket connections. Relay is the SDK for building applications that connect to Fabric.

## Key Concepts

### Call Fabric Resources

Everything in Fabric is a "resource":

1. **Subscribers**: Internal users within your application
2. **Relay Applications**: Your apps connected via WebSocket
3. **AI Agents**: Conversational AI endpoints
4. **SWML Scripts**: Call flow documents
5. **Video Rooms**: Video conference spaces
6. **SIP Gateways**: External SIP connections
7. **Fabric Addresses**: Routing identifiers (phone numbers, SIP URIs)

### Subscribers

Subscribers are internal account-holders in your SignalWire application - programmable identities within Call Fabric.

**Key Properties**:
- Always use private context (internal to your app)
- Can receive or initiate calls, messages, video sessions
- Registered endpoints for communication

#### Creating Subscribers (Dashboard)

1. Go to **Call Fabric** > **Resources**
2. Click **+ Add**
3. Select **Subscriber**
4. Fill in:
   - **Name**: Unique identifier (e.g., `alice`)
   - **Display Name**: Human-readable name
   - **Password**: Authentication password
   - **Timezone**: User's timezone
   - **Country/Region**: Geographic location
5. Save

#### Creating Subscribers (REST API)

```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.post(
    f"{space_url}/api/fabric/subscribers",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "name": "alice",
        "display_name": "Alice Smith",
        "password": "secure_password",
        "timezone": "America/New_York",
        "country": "US",
        "region": "east"
    }
)

subscriber = response.json()
print(f"Subscriber created: {subscriber['id']}")
```

#### Subscriber Addresses

Subscribers have Fabric addresses for routing:

```
sip:alice@{space-id}.sip.signalwire.com
```

Use this address to call/message subscribers.

### Relay Applications

Relay Applications are your server or client apps connected to SignalWire via persistent WebSocket connection.

**Benefits**:
- Real-time event handling
- Low latency communication
- Bidirectional control
- Stateful connections

## Relay SDK (Python)

### Installation

```bash
pip install signalwire
# or with uv:
# uv pip install signalwire
```

### Basic Relay Application

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = ["signalwire"]
# ///

import os
from signalwire.relay.consumer import Consumer

class MyRelayApp(Consumer):
    def setup(self):
        self.project = os.getenv('SIGNALWIRE_PROJECT_ID')
        self.token = os.getenv('SIGNALWIRE_API_TOKEN')
        self.contexts = ['office']  # Context to listen on

    async def on_incoming_call(self, call):
        print(f"Incoming call from: {call.from_number}")

        # Answer the call
        await call.answer()

        # Play greeting
        await call.play_tts(text="Welcome to our office!")

        # Collect input
        result = await call.prompt(
            type='digits',
            text='Press 1 for sales, 2 for support',
            max_digits=1
        )

        # Route based on input
        if result.digits == '1':
            await call.connect([['+15551111111']])
        elif result.digits == '2':
            await call.connect([['+15552222222']])
        else:
            await call.play_tts(text="Invalid selection")
            await call.hangup()

    async def on_incoming_message(self, message):
        print(f"Message from {message.from_number}: {message.body}")

        # Auto-reply
        await message.reply(
            text=f"You said: {message.body}"
        )

    async def ready(self):
        print("Relay application is ready!")

if __name__ == '__main__':
    app = MyRelayApp()
    app.run()
```

### Contexts

Contexts are routing namespaces. Relay apps subscribe to specific contexts to receive events.

```python
class MyRelayApp(Consumer):
    def setup(self):
        self.project = os.getenv('SIGNALWIRE_PROJECT_ID')
        self.token = os.getenv('SIGNALWIRE_API_TOKEN')
        self.contexts = ['sales', 'support']  # Listen on multiple contexts
```

Configure phone numbers or subscribers to route to specific contexts in the Dashboard.

### Making Outbound Calls

```python
class OutboundCaller(Consumer):
    async def make_call(self):
        call = await self.client.calling.dial(
            from_number='+15551234567',
            to_number='+15559876543'
        )

        # Wait for answer
        await call.wait_for_answered()

        # Play message
        await call.play_tts(text="This is an automated call")

        # Hangup
        await call.hangup()
```

### Call Control Methods

```python
async def on_incoming_call(self, call):
    # Answer
    await call.answer()

    # Play audio
    await call.play_audio(url='https://example.com/audio.mp3')

    # Text-to-speech
    await call.play_tts(text="Hello from SignalWire", gender='female')

    # Collect DTMF
    result = await call.prompt(
        type='digits',
        text='Enter your PIN',
        max_digits=4,
        timeout=10
    )
    print(f"User entered: {result.digits}")

    # Record
    recording = await call.record_async(max_length=120)
    await recording.stop()
    print(f"Recording URL: {recording.url}")

    # Connect to number
    await call.connect([['+15551234567']])

    # Hangup
    await call.hangup()
```

### Event Handlers

```python
class EventHandlingApp(Consumer):
    async def on_incoming_call(self, call):
        # Register event handlers
        call.on('state_change', self.on_call_state_change)
        call.on('ended', self.on_call_ended)

        await call.answer()

    async def on_call_state_change(self, call):
        print(f"Call state: {call.state}")

    async def on_call_ended(self, call):
        print(f"Call ended. Duration: {call.duration}s")
```

## Relay SDK (JavaScript/Node.js)

### Installation

```bash
npm install @signalwire/realtime-api
```

### Basic Relay Application

```javascript
const { SignalWire } = require('@signalwire/realtime-api');

async function main() {
  const client = await SignalWire({
    project: process.env.SIGNALWIRE_PROJECT_ID,
    token: process.env.SIGNALWIRE_API_TOKEN,
    topics: ['office']  // Contexts
  });

  // Handle incoming calls
  client.on('call.received', async (call) => {
    console.log(`Incoming call from: ${call.from}`);

    await call.answer();
    await call.playTTS({ text: 'Welcome to our office!' });

    const collect = await call.promptTTS({
      text: 'Press 1 for sales, 2 for support',
      digits: {
        max: 1,
        timeout: 5
      }
    });

    if (collect.digits === '1') {
      await call.connectPhone({ to: '+15551111111' });
    } else if (collect.digits === '2') {
      await call.connectPhone({ to: '+15552222222' });
    } else {
      await call.playTTS({ text: 'Invalid selection' });
      await call.hangup();
    }
  });

  // Handle incoming messages
  client.on('message.received', async (message) => {
    console.log(`Message from ${message.from}: ${message.body}`);

    await client.messaging.send({
      from: message.to,
      to: message.from,
      body: `You said: ${message.body}`
    });
  });

  await client.connect();
  console.log('Relay application connected!');
}

main();
```

### Making Outbound Calls

```javascript
async function makeCall() {
  const client = await SignalWire({ ... });

  const call = await client.voice.dialPhone({
    from: '+15551234567',
    to: '+15559876543'
  });

  await call.waitFor('answered');
  await call.playTTS({ text: 'This is an automated call' });
  await call.hangup();
}
```

## Subscriber-to-Subscriber Communication

### Scenario: Internal Office Phone System

```python
# Create subscribers for employees
employees = {
    'alice': {'extension': '101', 'phone': '+15551111111'},
    'bob': {'extension': '102', 'phone': '+15552222222'},
    'charlie': {'extension': '103', 'phone': '+15553333333'}
}

class OfficePhone(Consumer):
    def setup(self):
        self.project = os.getenv('SIGNALWIRE_PROJECT_ID')
        self.token = os.getenv('SIGNALWIRE_API_TOKEN')
        self.contexts = ['office']

    async def on_incoming_call(self, call):
        await call.answer()

        # Ask for extension
        result = await call.prompt(
            type='digits',
            text='Please enter the extension',
            max_digits=3
        )

        extension = result.digits

        # Find employee by extension
        for name, info in employees.items():
            if info['extension'] == extension:
                await call.play_tts(text=f"Connecting you to {name}")

                # Call subscriber
                subscriber_address = f"sip:{name}@{space_id}.sip.signalwire.com"
                await call.connect([[subscriber_address]])
                return

        await call.play_tts(text="Extension not found")
        await call.hangup()
```

### Subscriber Registration (SIP)

Subscribers can register SIP devices to receive calls:

1. **SIP URI**: `sip:username@{space-id}.sip.signalwire.com`
2. **Username**: Subscriber name
3. **Password**: Subscriber password
4. **Server**: `{space-id}.sip.signalwire.com`
5. **Port**: 5060 (UDP) or 5061 (TLS)

## Advanced Patterns

### Call Queuing System

```python
from collections import deque
import asyncio

class CallQueue(Consumer):
    def __init__(self):
        super().__init__()
        self.queue = deque()
        self.available_agents = set(['agent1', 'agent2', 'agent3'])

    async def on_incoming_call(self, call):
        await call.answer()
        await call.play_tts(text="Please hold while we connect you to an agent")

        # Add to queue
        self.queue.append(call)

        # Process queue
        await self.process_queue()

    async def process_queue(self):
        while self.queue and self.available_agents:
            call = self.queue.popleft()
            agent = self.available_agents.pop()

            # Connect to agent
            agent_address = f"sip:{agent}@{space_id}.sip.signalwire.com"

            try:
                await call.connect([[agent_address]])
            finally:
                # Agent becomes available again when call ends
                call.on('ended', lambda: self.available_agents.add(agent))
```

### Interactive Voice Response (IVR)

```python
class IVRSystem(Consumer):
    async def on_incoming_call(self, call):
        await call.answer()

        menu_choice = await self.main_menu(call)

        if menu_choice == '1':
            await self.account_balance(call)
        elif menu_choice == '2':
            await self.transfer_to_agent(call)
        elif menu_choice == '3':
            await self.make_payment(call)
        else:
            await call.hangup()

    async def main_menu(self, call):
        result = await call.prompt(
            type='digits',
            text='Press 1 for account balance, 2 for customer service, 3 to make a payment',
            max_digits=1
        )
        return result.digits

    async def account_balance(self, call):
        # Look up balance...
        balance = 1234.56
        await call.play_tts(text=f"Your account balance is ${balance}")
        await call.hangup()

    async def transfer_to_agent(self, call):
        await call.play_tts(text="Connecting you to an agent")
        await call.connect([['+15551234567']])

    async def make_payment(self, call):
        # Collect payment info...
        await call.play_tts(text="Payment processing not available yet")
        await call.hangup()
```

### Multi-Tenant System

```python
class MultiTenant(Consumer):
    def setup(self):
        self.project = os.getenv('SIGNALWIRE_PROJECT_ID')
        self.token = os.getenv('SIGNALWIRE_API_TOKEN')
        self.contexts = ['tenant1', 'tenant2', 'tenant3']

        self.tenant_greetings = {
            'tenant1': "Welcome to Company A",
            'tenant2': "Welcome to Company B",
            'tenant3': "Welcome to Company C"
        }

    async def on_incoming_call(self, call):
        # Determine which tenant based on context
        context = call.context  # 'tenant1', 'tenant2', etc.

        greeting = self.tenant_greetings.get(context, "Welcome")

        await call.answer()
        await call.play_tts(text=greeting)
        # Continue with tenant-specific logic...
```

## Fabric Addresses

### Retrieving Fabric Address

```python
response = requests.get(
    f"{space_url}/api/fabric/addresses",
    auth=HTTPBasicAuth(project_id, api_token)
)

addresses = response.json()
for addr in addresses:
    print(f"Address: {addr['address']} - Type: {addr['type']}")
```

### Address Types

- **phone**: Phone number (+15551234567)
- **sip**: SIP URI (sip:user@domain)
- **subscriber**: Subscriber identifier

## Testing Relay Applications

### Local Development

```python
# Set environment variables
export SIGNALWIRE_PROJECT_ID="your-project-id"
export SIGNALWIRE_API_TOKEN="your-api-token"

# Run your Relay app
python my_relay_app.py
```

### Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)

class DebugRelayApp(Consumer):
    async def on_incoming_call(self, call):
        logging.info(f"Call from: {call.from_number}")
        # Your logic...
```

### Testing Without Phone Calls

Use the Relay SDK to make test calls programmatically:

```python
async def test_call_flow():
    client = await SignalWire({ ... })

    call = await client.voice.dialPhone({
        from: '+15551234567',
        to: '+15559876543'  # Your test number
    })

    # Verify call flow...
```

## Deployment

### Systemd Service (Linux)

```ini
# /etc/systemd/system/relay-app.service
[Unit]
Description=SignalWire Relay Application
After=network.target

[Service]
Type=simple
User=relayuser
WorkingDirectory=/opt/relay-app
Environment="SIGNALWIRE_PROJECT_ID=xxx"
Environment="SIGNALWIRE_API_TOKEN=xxx"
ExecStart=/usr/bin/python3 /opt/relay-app/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "relay_app.py"]
```

## Best Practices

1. **Error Handling**: Wrap call operations in try/except
2. **Reconnection**: Relay SDK auto-reconnects on disconnect
3. **Contexts**: Use contexts for multi-tenant isolation
4. **Logging**: Log all call events for debugging
5. **State Management**: Store session state in database for failover
6. **Scalability**: Run multiple Relay instances for high availability

## Next Steps

- [Call Control](call-control.md) - Advanced call manipulation
- [Voice AI](voice-ai.md) - Add AI to Relay apps
- [Webhooks & Events](webhooks-events.md) - Alternative event handling
