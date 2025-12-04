# AgentServer Reference

`AgentServer` enables hosting multiple agents on a single server with optional static file serving.

## Import

```python
from signalwire_agents import AgentBase, AgentServer
```

## Constructor

```python
AgentServer(
    host: str = "0.0.0.0",
    port: int = 3000
)
```

**Parameters:**
- `host` - Host address to bind server
- `port` - Port number for HTTP server

## Basic Usage

### Multiple Agents on One Server

```python
from signalwire_agents import AgentBase, AgentServer

class SupportAgent(AgentBase):
    def __init__(self):
        super().__init__(name="support-agent")
        self.add_language("English", "en-US", "rime.spore")
        self.prompt_add_section("Role", "You are a support agent.")

class SalesAgent(AgentBase):
    def __init__(self):
        super().__init__(name="sales-agent")
        self.add_language("English", "en-US", "rime.spore")
        self.prompt_add_section("Role", "You are a sales agent.")

# Create server and register agents
server = AgentServer(host="0.0.0.0", port=3000)
server.register(SupportAgent(), "/support")
server.register(SalesAgent(), "/sales")
server.run()
```

This creates:
- `http://localhost:3000/support` - Support agent SWML endpoint
- `http://localhost:3000/sales` - Sales agent SWML endpoint

## Methods

### register()

Register an agent at a specific route.

```python
def register(
    self,
    agent: AgentBase,
    route: str
) -> 'AgentServer'
```

**Parameters:**
- `agent` - AgentBase instance to register
- `route` - URL path for this agent (must start with `/`)

**Returns:** Self for method chaining

**Example:**

```python
server = AgentServer()
server.register(SupportAgent(), "/support")
server.register(SalesAgent(), "/sales")
server.register(BillingAgent(), "/billing")
```

### serve_static_files()

Enable static file serving from a directory.

```python
def serve_static_files(
    self,
    directory: str,
    route: str = "/"
) -> 'AgentServer'
```

**Parameters:**
- `directory` - Path to directory containing static files
- `route` - URL prefix for static files (default: `/`)

**Returns:** Self for method chaining

**Example:**

```python
from pathlib import Path

# Serve files from ./web directory at root
web_dir = Path(__file__).parent / "web"
server.serve_static_files(str(web_dir))

# Or serve at a specific path
server.serve_static_files(str(web_dir), "/static")
```

### run()

Start the HTTP server.

```python
def run(self) -> None
```

## Static Files + Agents Pattern

Common pattern for serving a web UI alongside AI agents:

```python
from signalwire_agents import AgentBase, AgentServer
from pathlib import Path
import os

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "3000"))

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="my-agent")
        self.add_language("English", "en-US", "rime.spore")
        self.prompt_add_section("Role", "You are a helpful assistant.")

if __name__ == "__main__":
    # Setup paths
    web_dir = Path(__file__).parent / "web"

    # Create and configure server
    server = AgentServer(host=HOST, port=PORT)
    server.register(MyAgent(), "/agent")
    server.serve_static_files(str(web_dir))

    print(f"Agent endpoint: http://{HOST}:{PORT}/agent")
    print(f"Web UI: http://{HOST}:{PORT}/")
    server.run()
```

**Directory structure:**

```
my_project/
├── agent.py
└── web/
    ├── index.html
    ├── style.css
    └── app.js
```

## WebRTC Web UI Pattern

For browser-based voice interaction with your agent:

**web/index.html:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>AI Agent</title>
    <script src="https://cdn.signalwire.com/libs/swrtc/2.0.0/signalwire.min.js"></script>
</head>
<body>
    <button id="call-btn">Call Agent</button>
    <button id="hangup-btn" disabled>Hang Up</button>

    <script>
        const GUEST_TOKEN = 'YOUR_GUEST_TOKEN';  // From SignalWire Fabric
        const AGENT_ADDRESS = '/public/my-agent';  // Your agent's address

        let client = null;
        let call = null;

        document.getElementById('call-btn').onclick = async () => {
            client = await SignalWire.SignalWire({
                token: GUEST_TOKEN
            });

            call = await client.dial({
                to: AGENT_ADDRESS,
                nodeId: null
            });

            document.getElementById('call-btn').disabled = true;
            document.getElementById('hangup-btn').disabled = false;
        };

        document.getElementById('hangup-btn').onclick = () => {
            if (call) call.hangup();
            document.getElementById('call-btn').disabled = false;
            document.getElementById('hangup-btn').disabled = true;
        };
    </script>
</body>
</html>
```

## Environment Variables

AgentServer respects these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `3000` | Server port |

**Example:**

```bash
HOST=127.0.0.1 PORT=8080 python my_server.py
```

## Multiple Agents with Shared Resources

```python
from signalwire_agents import AgentBase, AgentServer
import os

# Shared database connection
db = DatabaseConnection(os.environ["DATABASE_URL"])

class OrderAgent(AgentBase):
    def __init__(self, database):
        super().__init__(name="order-agent")
        self.db = database
        self.add_language("English", "en-US", "rime.spore")
        self.prompt_add_section("Role", "You help with order inquiries.")

    @AgentBase.tool(
        name="lookup_order",
        description="Look up order status",
        parameters={"order_id": {"type": "string", "description": "Order ID"}}
    )
    def lookup_order(self, args, raw_data):
        order = self.db.get_order(args["order_id"])
        return SwaigFunctionResult(f"Order status: {order.status}")

class AccountAgent(AgentBase):
    def __init__(self, database):
        super().__init__(name="account-agent")
        self.db = database
        self.add_language("English", "en-US", "rime.spore")
        self.prompt_add_section("Role", "You help with account inquiries.")

# Share database across agents
server = AgentServer(port=3000)
server.register(OrderAgent(db), "/orders")
server.register(AccountAgent(db), "/accounts")
server.run()
```

## Basic Auth with AgentServer

Each registered agent can have its own authentication:

```python
class SecureAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="secure-agent",
            basic_auth=("username", "password")
        )
        # ... rest of configuration

server = AgentServer()
server.register(SecureAgent(), "/secure")
server.register(PublicAgent(), "/public")  # No auth
server.run()
```

Or use environment variables per-agent:

```bash
SWML_BASIC_AUTH_USER=admin SWML_BASIC_AUTH_PASSWORD=secret python server.py
```

## Best Practices

1. **Use descriptive routes** - `/support`, `/sales`, `/billing` not `/agent1`, `/agent2`

2. **Separate concerns** - Each agent should have a focused purpose

3. **Share resources wisely** - Pass shared connections/clients to agent constructors

4. **Consider health checks** - Add a simple endpoint for load balancer health checks

5. **Log agent activity** - Each agent logs with its own name for easier debugging

## Complete Example

```python
#!/usr/bin/env python3
"""Multi-agent server with static file serving."""

from signalwire_agents import AgentBase, AgentServer
from signalwire_agents.core.function_result import SwaigFunctionResult
from pathlib import Path
import os

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "3000"))


class SupportAgent(AgentBase):
    """Handles customer support inquiries."""

    def __init__(self):
        super().__init__(name="support-agent")
        self.add_language("English", "en-US", "rime.spore")
        self.prompt_add_section(
            "Role",
            "You are a friendly customer support agent."
        )
        self.prompt_add_section(
            "Guidelines",
            bullets=[
                "Help resolve customer issues",
                "Escalate complex issues to human agents",
                "Always be polite and professional"
            ]
        )

    @AgentBase.tool(
        name="escalate",
        description="Escalate to human support",
        parameters={"reason": {"type": "string", "description": "Reason"}}
    )
    def escalate(self, args, raw_data):
        return (SwaigFunctionResult("Connecting you to a specialist.")
                .add_action("transfer", {"dest": "sip:support@company.com"}))


class SalesAgent(AgentBase):
    """Handles sales inquiries."""

    def __init__(self):
        super().__init__(name="sales-agent")
        self.add_language("English", "en-US", "rime.spore")
        self.prompt_add_section(
            "Role",
            "You are an enthusiastic sales representative."
        )


if __name__ == "__main__":
    # Setup
    web_dir = Path(__file__).parent / "web"

    # Create server
    server = AgentServer(host=HOST, port=PORT)

    # Register agents
    server.register(SupportAgent(), "/support")
    server.register(SalesAgent(), "/sales")

    # Serve static files (web UI)
    if web_dir.exists():
        server.serve_static_files(str(web_dir))
        print(f"Web UI: http://{HOST}:{PORT}/")

    print(f"Support agent: http://{HOST}:{PORT}/support")
    print(f"Sales agent: http://{HOST}:{PORT}/sales")

    server.run()
```
