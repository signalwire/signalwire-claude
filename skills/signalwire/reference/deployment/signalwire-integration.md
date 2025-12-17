# SignalWire Platform Integration Reference

Guide to connecting your AI Agent to the SignalWire platform for phone calls, WebRTC, and the Fabric API.

## Overview

SignalWire AI Agents can be reached via:
1. **Phone calls** - Traditional PSTN calling
2. **SIP** - VoIP connections
3. **WebRTC** - Browser-based voice/video

All methods require registering your agent with SignalWire's Fabric platform.

## Prerequisites

### SignalWire Account

1. Create account at [signalwire.com](https://signalwire.com)
2. Get credentials from your Space settings:
   - Space Name (e.g., `myspace.signalwire.com`)
   - Project ID
   - API Token

### Environment Setup

```bash
export SIGNALWIRE_SPACE_NAME="myspace"
export SIGNALWIRE_PROJECT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export SIGNALWIRE_TOKEN="PTxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## Fabric API Integration

The Fabric API lets you create "addresses" that route calls to your agent.

### Creating an External SWML Handler

An external SWML handler tells SignalWire where to fetch your agent's SWML:

```bash
# Create handler via API
curl -X POST "https://${SIGNALWIRE_SPACE_NAME}.signalwire.com/api/fabric/resources/external_swml_handler" \
  -u "${SIGNALWIRE_PROJECT_ID}:${SIGNALWIRE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My AI Agent",
    "request_url": "https://your-agent.com/agent",
    "request_method": "POST"
  }'
```

Response:
```json
{
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "name": "My AI Agent",
    "request_url": "https://your-agent.com/agent",
    "request_method": "POST"
}
```

### Creating a Subscriber (Address)

A subscriber creates a callable address for your agent:

```bash
curl -X POST "https://${SIGNALWIRE_SPACE_NAME}.signalwire.com/api/fabric/subscribers" \
  -u "${SIGNALWIRE_PROJECT_ID}:${SIGNALWIRE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-agent",
    "external_swml_handler": {
        "id": "HANDLER_ID_FROM_ABOVE"
    }
  }'
```

Response includes your agent's address:
```json
{
    "id": "subscriber-id",
    "name": "my-agent",
    "address": "/public/my-agent"
}
```

### Using Basic Auth with Fabric

If your agent requires authentication, include credentials in the URL:

```bash
curl -X POST "https://${SIGNALWIRE_SPACE_NAME}.signalwire.com/api/fabric/resources/external_swml_handler" \
  -u "${SIGNALWIRE_PROJECT_ID}:${SIGNALWIRE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Secure Agent",
    "request_url": "https://username:password@your-agent.com/agent",
    "request_method": "POST"
  }'
```

## WebRTC Integration

### Guest Tokens

Guest tokens allow browser clients to connect without full SignalWire credentials:

```bash
# Create guest token
curl -X POST "https://${SIGNALWIRE_SPACE_NAME}.signalwire.com/api/fabric/subscribers/tokens" \
  -u "${SIGNALWIRE_PROJECT_ID}:${SIGNALWIRE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "reference_id": "guest-user-123",
    "ttl": 3600
  }'
```

Response:
```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
    "expires_at": "2024-01-15T12:00:00Z"
}
```

### Browser Client

Use the SignalWire JavaScript SDK to connect:

```html
<!DOCTYPE html>
<html>
<head>
    <title>AI Agent Call</title>
    <script src="https://cdn.signalwire.com/libs/swrtc/2.0.0/signalwire.min.js"></script>
</head>
<body>
    <button id="call">Call Agent</button>
    <button id="hangup" disabled>Hang Up</button>

    <script>
        const GUEST_TOKEN = 'YOUR_GUEST_TOKEN';
        const AGENT_ADDRESS = '/public/my-agent';

        let client = null;
        let call = null;

        document.getElementById('call').onclick = async () => {
            // Connect to SignalWire
            client = await SignalWire.SignalWire({
                token: GUEST_TOKEN
            });

            // Dial the agent
            call = await client.dial({
                to: AGENT_ADDRESS,
                nodeId: null  // Let SignalWire choose
            });

            // Handle call events
            call.on('destroy', () => {
                document.getElementById('call').disabled = false;
                document.getElementById('hangup').disabled = true;
            });

            document.getElementById('call').disabled = true;
            document.getElementById('hangup').disabled = false;
        };

        document.getElementById('hangup').onclick = () => {
            if (call) call.hangup();
        };
    </script>
</body>
</html>
```

### Complete WebRTC Agent Example

```python
#!/usr/bin/env python3
"""Agent with WebRTC web interface."""

from signalwire_agents import AgentBase, AgentServer
from pathlib import Path
import os

class WebAgent(AgentBase):
    def __init__(self):
        super().__init__(name="web-agent")
        self.add_language("English", "en-US", "rime.spore")
        self.prompt_add_section(
            "Role",
            "You are a helpful AI assistant accessible via web browser."
        )

if __name__ == "__main__":
    # Server setup
    server = AgentServer(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "3000"))
    )

    # Register agent
    server.register(WebAgent(), "/agent")

    # Serve web UI
    web_dir = Path(__file__).parent / "web"
    server.serve_static_files(str(web_dir))

    print("Agent: http://localhost:3000/agent")
    print("Web UI: http://localhost:3000/")
    server.run()
```

## Phone Number Integration

### Purchasing a Number

```bash
# Search available numbers
curl "https://${SIGNALWIRE_SPACE_NAME}.signalwire.com/api/relay/rest/phone_numbers/search?area_code=206" \
  -u "${SIGNALWIRE_PROJECT_ID}:${SIGNALWIRE_TOKEN}"

# Purchase a number
curl -X POST "https://${SIGNALWIRE_SPACE_NAME}.signalwire.com/api/relay/rest/phone_numbers" \
  -u "${SIGNALWIRE_PROJECT_ID}:${SIGNALWIRE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"number": "+12065551234"}'
```

### Routing to Your Agent

Configure the number to point to your agent's address:

1. Go to SignalWire Dashboard > Phone Numbers
2. Select your number
3. Set "Handle Calls Using" to "A SWML Script"
4. Set "When a call comes in" to your agent's Fabric address

Or via API:

```bash
curl -X PUT "https://${SIGNALWIRE_SPACE_NAME}.signalwire.com/api/relay/rest/phone_numbers/NUMBER_ID" \
  -u "${SIGNALWIRE_PROJECT_ID}:${SIGNALWIRE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "call_handler": "swml_app",
    "call_request_url": "https://your-agent.com/agent"
  }'
```

## SIP Integration

### SIP Endpoint

Create a SIP endpoint to receive calls from your PBX:

```bash
curl -X POST "https://${SIGNALWIRE_SPACE_NAME}.signalwire.com/api/relay/rest/endpoints/sip" \
  -u "${SIGNALWIRE_PROJECT_ID}:${SIGNALWIRE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ai-agent",
    "password": "secure-password",
    "caller_id": "+12065551234"
  }'
```

Route the SIP endpoint to your agent similarly to phone numbers.

## Complete Integration Example

This example creates a full deployment with phone + WebRTC:

```python
#!/usr/bin/env python3
"""
Full SignalWire integration example.

Prerequisites:
1. SignalWire account with credentials in environment
2. ngrok or public URL for your agent
3. Phone number purchased (optional, for PSTN)
"""

from signalwire_agents import AgentBase, AgentServer
from signalwire_agents.core.function_result import SwaigFunctionResult
from pathlib import Path
import os
import requests

# Environment
SPACE = os.environ["SIGNALWIRE_SPACE_NAME"]
PROJECT = os.environ["SIGNALWIRE_PROJECT_ID"]
TOKEN = os.environ["SIGNALWIRE_TOKEN"]
AGENT_URL = os.environ["SWML_PROXY_URL_BASE"]


class CustomerAgent(AgentBase):
    """Production-ready customer service agent."""

    def __init__(self):
        super().__init__(
            name="customer-agent",
            basic_auth=(
                os.getenv("SWML_BASIC_AUTH_USER", "agent"),
                os.getenv("SWML_BASIC_AUTH_PASSWORD", "secret")
            )
        )

        self.add_language("English", "en-US", "rime.spore")

        self.prompt_add_section(
            "Role",
            "You are a helpful customer service agent for Acme Corp."
        )

        # Enable debugging in development
        if os.getenv("DEBUG_WEBHOOK_URL"):
            self.set_params({
                "debug_webhook_url": os.environ["DEBUG_WEBHOOK_URL"],
                "debug_webhook_level": int(os.getenv("DEBUG_WEBHOOK_LEVEL", "1"))
            })

    @AgentBase.tool(
        name="end_call",
        description="End the call politely",
        parameters={}
    )
    def end_call(self, args, raw_data):
        return SwaigFunctionResult(
            "Thank you for calling Acme Corp! Goodbye!",
            post_process=True
        ).add_action("hangup", {})


def setup_signalwire():
    """Register agent with SignalWire Fabric."""
    auth = (PROJECT, TOKEN)
    base = f"https://{SPACE}.signalwire.com/api/fabric"

    # Build URL with auth if needed
    user = os.getenv("SWML_BASIC_AUTH_USER")
    password = os.getenv("SWML_BASIC_AUTH_PASSWORD")
    if user and password:
        url_parts = AGENT_URL.replace("https://", "").replace("http://", "")
        request_url = f"https://{user}:{password}@{url_parts}/agent"
    else:
        request_url = f"{AGENT_URL}/agent"

    # Create external SWML handler
    handler_resp = requests.post(
        f"{base}/resources/external_swml_handler",
        auth=auth,
        json={
            "name": "Customer Service Agent",
            "request_url": request_url,
            "request_method": "POST"
        }
    )
    handler = handler_resp.json()
    print(f"Created handler: {handler['id']}")

    # Create subscriber/address
    sub_resp = requests.post(
        f"{base}/subscribers",
        auth=auth,
        json={
            "name": "customer-agent",
            "external_swml_handler": {"id": handler["id"]}
        }
    )
    subscriber = sub_resp.json()
    print(f"Agent address: {subscriber['address']}")

    # Create guest token for WebRTC
    token_resp = requests.post(
        f"{base}/subscribers/tokens",
        auth=auth,
        json={"reference_id": "web-guest", "ttl": 86400}
    )
    guest_token = token_resp.json()
    print(f"Guest token: {guest_token['token'][:50]}...")

    return subscriber["address"], guest_token["token"]


if __name__ == "__main__":
    # Setup SignalWire integration
    address, token = setup_signalwire()

    # Create server
    server = AgentServer(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "3000"))
    )

    # Register agent
    server.register(CustomerAgent(), "/agent")

    # Serve web UI if present
    web_dir = Path(__file__).parent / "web"
    if web_dir.exists():
        server.serve_static_files(str(web_dir))

    print(f"\nAgent running!")
    print(f"SWML endpoint: {AGENT_URL}/agent")
    print(f"SignalWire address: {address}")
    print(f"Web UI: http://localhost:{os.getenv('PORT', '3000')}/")

    server.run()
```

## Troubleshooting

### Agent Not Receiving Calls

1. Verify `SWML_PROXY_URL_BASE` is publicly accessible
2. Check SignalWire handler points to correct URL
3. Test URL manually: `curl -X POST https://your-url/agent`
4. Check SignalWire dashboard for error logs

### WebRTC Not Connecting

1. Verify guest token is valid and not expired
2. Check browser console for errors
3. Ensure HTTPS is used (required for WebRTC)
4. Verify agent address is correct

### Authentication Errors

1. Check credentials are properly URL-encoded
2. Verify `SWML_BASIC_AUTH_*` matches agent configuration
3. Test with curl: `curl -u user:pass https://your-url/agent`

## Security Best Practices

1. **Always use HTTPS** in production
2. **Enable Basic Auth** for production agents
3. **Rotate tokens** regularly
4. **Use environment variables** for credentials
5. **Limit guest token TTL** to minimum needed
6. **Monitor debug webhooks** for suspicious activity
