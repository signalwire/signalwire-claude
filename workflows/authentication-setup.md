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

## Next Steps

Once authenticated, proceed to:
- [Outbound Calling](outbound-calling.md) - Make your first call
- [Inbound Call Handling](inbound-call-handling.md) - Receive calls with SWML
- [Video](video.md) - Create video rooms
- [Messaging](messaging.md) - Send SMS/MMS
