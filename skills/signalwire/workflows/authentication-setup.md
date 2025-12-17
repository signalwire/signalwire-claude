# Authentication & Setup

## Overview

Before using any SignalWire API or SDK, you need proper authentication credentials and project configuration.

## Required Credentials

### Project ID and API Token

Every SignalWire Space has:
- **Project ID**: Unique identifier for your project (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
- **API Token**: Secret key for authentication
- **Space Name**: Your subdomain (e.g., `mycompany` for `mycompany.signalwire.com`)

### Finding Your Credentials

1. Log in to your SignalWire Dashboard: `https://{space-name}.signalwire.com`
2. Navigate to **API** section
3. Find your Project ID and API Token
4. **IMPORTANT**: Keep API Token secret - never expose in client-side code

## Authentication Methods

### HTTP Basic Authentication (REST APIs)

Most REST API endpoints use HTTP Basic Auth:

```bash
# Format
curl -u <PROJECT_ID>:<API_TOKEN> \
  https://{space}.signalwire.com/api/...

# Or with Authorization header
curl -H "Authorization: Basic $(echo -n 'PROJECT_ID:API_TOKEN' | base64)" \
  https://{space}.signalwire.com/api/...
```

**Python Example:**
```python
import requests
from requests.auth import HTTPBasicAuth

project_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
api_token = "PTxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
space_url = "https://mycompany.signalwire.com"

response = requests.post(
    f"{space_url}/api/calling/calls",
    auth=HTTPBasicAuth(project_id, api_token),
    headers={"Content-Type": "application/json"},
    json={
        "command": "dial",
        "params": {
            "from": "sip:user@example.sip.signalwire.com",
            "to": "sip:dest@example.sip.signalwire.com",
            "url": "https://example.com/swml"
        }
    }
)
```

**Node.js Example:**
```javascript
const axios = require('axios');

const projectId = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx';
const apiToken = 'PTxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';
const spaceUrl = 'https://mycompany.signalwire.com';

const response = await axios.post(
  `${spaceUrl}/api/calling/calls`,
  {
    command: 'dial',
    params: {
      from: 'sip:user@example.sip.signalwire.com',
      to: 'sip:dest@example.sip.signalwire.com',
      url: 'https://example.com/swml'
    }
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
```

### SDK Authentication

#### JavaScript/Node.js Realtime SDK

```javascript
const { SignalWire } = require('@signalwire/realtime-api');

const client = await SignalWire({
  project: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
  token: 'PTxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
});
```

#### Python Realtime SDK

```python
from signalwire.relay.consumer import Consumer

class MyConsumer(Consumer):
    def setup(self):
        self.project = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
        self.token = 'PTxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

    async def on_incoming_call(self, call):
        # Handle incoming calls
        await call.answer()
```

#### Python AI Agents SDK

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = ["signalwire-agents"]
# ///

from signalwire_agents import AgentBase

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__()
        # Authentication handled via environment variables:
        # SIGNALWIRE_PROJECT_ID
        # SIGNALWIRE_API_TOKEN

if __name__ == "__main__":
    agent = MyAgent()
    agent.run()
```

### Environment Variables

Best practice: Store credentials in environment variables, not in code.

```bash
# .env file
SIGNALWIRE_PROJECT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
SIGNALWIRE_API_TOKEN=PTxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SIGNALWIRE_SPACE_URL=https://mycompany.signalwire.com
```

**Python (with python-dotenv):**
```python
import os
from dotenv import load_dotenv

load_dotenv()

project_id = os.getenv('SIGNALWIRE_PROJECT_ID')
api_token = os.getenv('SIGNALWIRE_API_TOKEN')
space_url = os.getenv('SIGNALWIRE_SPACE_URL')
```

**Node.js (with dotenv):**
```javascript
require('dotenv').config();

const projectId = process.env.SIGNALWIRE_PROJECT_ID;
const apiToken = process.env.SIGNALWIRE_API_TOKEN;
const spaceUrl = process.env.SIGNALWIRE_SPACE_URL;
```

## Video Room Tokens

Video API uses **room tokens** instead of API tokens for client-side access.

**Creating a Room Token (server-side):**
```python
import requests
from requests.auth import HTTPBasicAuth

# Server-side only - never expose API token to browser
response = requests.post(
    f"{space_url}/api/video/room_tokens",
    auth=HTTPBasicAuth(project_id, api_token),
    json={
        "room_name": "my-video-room",
        "user_name": "Alice",
        "permissions": ["room.self.audio_mute", "room.self.video_mute"]  # Guest token
    }
)

room_token = response.json()['token']
# Send this token to the browser
```

**Using Room Token (client-side JavaScript):**
```javascript
import { Video } from '@signalwire/js';

const roomSession = new Video.RoomSession({
  token: roomToken,  // Received from your server
  rootElementId: 'video-container'
});

await roomSession.join();
```

## Token Scopes

When creating API tokens in the Dashboard, you can limit scopes:
- **calling**: Voice/telephony APIs
- **messaging**: SMS/MMS APIs
- **video**: Video room APIs
- **fax**: Fax APIs
- **chat**: Chat APIs

## Security Best Practices

1. **Never expose API tokens in client-side code** - Only Project ID and Room Tokens are safe for browsers
2. **Use environment variables** - Don't hardcode credentials
3. **Rotate tokens periodically** - Generate new tokens and revoke old ones
4. **Use minimal scopes** - Only grant permissions your application needs
5. **Validate webhooks** - Verify webhook signatures if available
6. **Use HTTPS only** - All API calls must be over HTTPS

## Common Authentication Errors

### 401 Unauthorized
- **Cause**: Invalid Project ID or API Token
- **Fix**: Verify credentials in Dashboard, check for typos

### 403 Forbidden
- **Cause**: Token doesn't have required scope
- **Fix**: Create token with appropriate permissions

### Invalid Space URL
- **Cause**: Using wrong space name in URL
- **Fix**: Check your Space URL in Dashboard (format: `https://{space-name}.signalwire.com`)

## Testing Authentication

Quick test to verify credentials work:

```bash
# Test authentication by listing call logs
curl -u PROJECT_ID:API_TOKEN \
  https://{space}.signalwire.com/api/calling/calls
```

Successful response = authentication works!

## MFA Implementation Patterns

### Phone-Based Two-Factor Authentication

```python
import random
import time

# MFA code storage (use Redis in production)
mfa_codes = {}

@app.route('/api/send-mfa', methods=['POST'])
def send_mfa_code():
    """Send 6-digit verification code via SMS"""

    data = request.json
    phone_number = data.get('phone')

    # Generate code
    code = str(random.randint(100000, 999999))

    # Store with expiration (5 minutes)
    mfa_codes[phone_number] = {
        'code': code,
        'expires': time.time() + 300,
        'attempts': 0
    }

    # Send via SMS
    requests.post(
        f"{space_url}/api/messaging/messages",
        auth=HTTPBasicAuth(project_id, api_token),
        json={
            "from": "+15551234567",
            "to": phone_number,
            "body": f"Your verification code is: {code}. Expires in 5 minutes."
        }
    )

    return jsonify({"status": "sent"}), 200

@app.route('/api/verify-mfa', methods=['POST'])
def verify_mfa_code():
    """Verify provided code"""

    data = request.json
    phone_number = data.get('phone')
    provided_code = data.get('code')

    # Check if code exists
    if phone_number not in mfa_codes:
        return jsonify({"error": "No code sent"}), 400

    mfa_data = mfa_codes[phone_number]

    # Check expiration
    if time.time() > mfa_data['expires']:
        del mfa_codes[phone_number]
        return jsonify({"error": "Code expired"}), 400

    # Check attempts
    if mfa_data['attempts'] >= 3:
        del mfa_codes[phone_number]
        return jsonify({"error": "Too many attempts"}), 429

    # Verify code
    if provided_code == mfa_data['code']:
        # Success - clean up
        del mfa_codes[phone_number]

        # Generate session token
        session_token = generate_session_token(phone_number)

        return jsonify({
            "verified": True,
            "session_token": session_token
        }), 200
    else:
        # Failed attempt
        mfa_data['attempts'] += 1
        return jsonify({"error": "Invalid code"}), 401
```

### Voice-Based MFA

```yaml
# SWML for voice MFA
version: 1.0.0
sections:
  main:
    - answer: {}
    - say:
        text: "Your verification code is"
    - say:
        text: "{mfa_code}"
        # Speak digits slowly and clearly
    - say:
        text: "I repeat, your code is {mfa_code}"
    - hangup: {}
```

### AI Agent MFA Integration

```yaml
# AI agent that verifies identity
- ai:
    prompt: |
      You are a security verification agent.

      Steps:
      1. Ask the caller to provide their 4-digit PIN
      2. Call verify_pin function with the PIN
      3. If verified, greet them by name and proceed
      4. If not verified, ask them to try again (max 3 attempts)
      5. After 3 failed attempts, disconnect the call

    functions:
      - name: verify_pin
        purpose: "Verify caller's PIN"
        parameters:
          - name: pin
            type: string
            description: "4-digit PIN code"
        data_map:
          webhooks:
            - url: "https://yourserver.com/verify-pin"
              method: POST
              output:
                # Don't tell AI sensitive data - use metadata
                response: "{{verified ? 'Caller verified' : 'Invalid PIN'}}"
                action:
                  - set_meta_data:
                      verified: "{{verified}}"
                      customer_id: "{{customer_id}}"
                      customer_name: "{{customer_name}}"
```

## Metadata for Security (Sensitive Data)

### Keep Sensitive Data Out of LLM

```yaml
# SWAIG function with metadata storage
functions:
  - name: verify_customer
    purpose: "Verify customer identity"
    data_map:
      webhooks:
        - url: "https://yourserver.com/verify"
          method: POST
          output:
            # AI only sees this response
            response: "Customer verified successfully"

            # Sensitive data goes to metadata (not visible to LLM)
            action:
              - set_meta_data:
                  customer_id: "{{response.id}}"
                  account_balance: "{{response.balance}}"
                  credit_card_last4: "{{response.card_last4}}"
                  ssn_last4: "{{response.ssn_last4}}"
                  auth_token: "{{response.token}}"
```

### Accessing Metadata in Functions

```python
@app.route('/swaig/check-balance', methods=['POST'])
def check_balance():
    """Access metadata without exposing to LLM"""

    data = request.json
    metadata = data.get('metadata', {})

    # Retrieve sensitive data from metadata
    account_balance = metadata.get('account_balance')
    customer_id = metadata.get('customer_id')

    # Return response without exposing data
    return jsonify({
        "response": f"Your current balance is ${account_balance}"
    })
```

## Data Protection Patterns

### Payment Data Handling

```yaml
# Collect payment info securely
- ai:
    prompt: |
      Collect payment amount and confirm customer information.
      Then use collect_payment function.

    functions:
      - name: collect_payment
        purpose: "Securely collect credit card information"
        data_map:
          webhooks:
            - url: "https://yourserver.com/process-payment"
              method: POST

# Payment info bypasses LLM completely
- pay:
    payment_method: credit_card
    payment_handler: "https://yourserver.com/payment-processor"
```

**Security Benefits:**
- Payment info never exposed to LLM
- DTMF input required for card numbers
- HTTPS-only connections enforced
- Adaptable to any payment processor

### Encryption for Stored Data

```python
from cryptography.fernet import Fernet

class SecureStorage:
    def __init__(self):
        # Load encryption key from environment
        self.key = os.getenv('ENCRYPTION_KEY').encode()
        self.cipher = Fernet(self.key)

    def encrypt(self, data):
        """Encrypt sensitive data before storage"""
        if isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data).decode()

    def decrypt(self, encrypted_data):
        """Decrypt stored data"""
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        return self.cipher.decrypt(encrypted_data).decode()

# Usage in SWAIG function
storage = SecureStorage()

@app.route('/swaig/store-sensitive', methods=['POST'])
def store_sensitive_data():
    data = request.json
    args = data.get('argument', {})

    sensitive_value = args.get('sensitive_data')

    # Encrypt before storing
    encrypted = storage.encrypt(sensitive_value)

    database.save({
        'customer_id': args.get('customer_id'),
        'encrypted_data': encrypted
    })

    return jsonify({
        "response": "Information stored securely"
    })
```

## Token Management for Video Rooms

### Secure Token Generation

```python
import hashlib
import time

class VideoTokenManager:
    def __init__(self):
        self.token_cache = {}

    def generate_token(self, room_name, user_name, is_moderator=False):
        """Generate video room token with caching"""

        # Check cache
        cache_key = f"{room_name}:{user_name}:{is_moderator}"
        cached = self.token_cache.get(cache_key)

        if cached and cached['expires'] > time.time():
            return cached['token']

        # Generate new token
        response = requests.post(
            f"{space_url}/api/video/room_tokens",
            auth=HTTPBasicAuth(project_id, api_token),
            json={
                "room_name": room_name,
                "user_name": user_name,
                "mod_permissions": is_moderator,
                "permissions": [] if is_moderator else [
                    "room.self.audio_mute",
                    "room.self.video_mute",
                    "room.self.audio_unmute",
                    "room.self.video_unmute"
                ]
            }
        )

        if response.status_code == 200:
            token = response.json()['token']

            # Cache for 1 hour
            self.token_cache[cache_key] = {
                'token': token,
                'expires': time.time() + 3600
            }

            return token

        return None

# Usage
token_manager = VideoTokenManager()

@app.route('/api/join-video', methods=['POST'])
def join_video():
    data = request.json

    token = token_manager.generate_token(
        room_name=data.get('room'),
        user_name=data.get('name'),
        is_moderator=data.get('is_moderator', False)
    )

    if token:
        return jsonify({"token": token})
    else:
        return jsonify({"error": "Token generation failed"}), 500
```

## Next Steps

Once authenticated, proceed to:
- [Outbound Calling](outbound-calling.md) - Make your first call
- [Inbound Call Handling](inbound-call-handling.md) - Receive calls with SWML
- [Video](video.md) - Create video rooms with secure token management
- [Messaging](messaging.md) - Send SMS/MMS with MFA
