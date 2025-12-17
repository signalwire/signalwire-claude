# SIP Routing Reference

SIP (Session Initiation Protocol) routing allows your agent to automatically handle calls based on SIP usernames. This is useful for routing different SIP endpoints to the same agent or creating multi-tenant deployments.

## Import

```python
from signalwire_agents import AgentBase
```

## Enabling SIP Routing

### enable_sip_routing()

Enable SIP-based routing for the agent.

```python
def enable_sip_routing(
    self,
    auto_map: bool = True,
    path: str = "/sip"
) -> 'AgentBase'
```

**Parameters:**
- `auto_map` - Automatically register common SIP usernames based on agent name/route
- `path` - HTTP endpoint path for SIP routing (default: "/sip")

**Returns:** Self for method chaining

**Example:**

```python
class MySupportAgent(AgentBase):
    def __init__(self):
        super().__init__(name="support-agent", route="/support")

        # Enable SIP routing with auto-mapping
        self.enable_sip_routing(auto_map=True)

        # This will automatically register:
        # - "supportagent" (from name)
        # - "support" (from route)
```

### register_sip_username()

Register a specific SIP username to route to this agent.

```python
def register_sip_username(self, sip_username: str) -> 'AgentBase'
```

**Parameters:**
- `sip_username` - SIP username to register (case-insensitive)

**Returns:** Self for method chaining

**Example:**

```python
agent.register_sip_username("sales")
agent.register_sip_username("billing")
agent.register_sip_username("main-line")
```

### auto_map_sip_usernames()

Automatically register common SIP username variations based on the agent's name and route.

```python
def auto_map_sip_usernames(self) -> 'AgentBase'
```

This method registers:
- Clean version of agent name (lowercase, alphanumeric only)
- Clean version of route path
- Consonant-only version of name (if name is > 3 chars)

**Example:**

```python
class CustomerServiceAgent(AgentBase):
    def __init__(self):
        super().__init__(name="customer-service", route="/cs")

        # This will register: "customerservice", "cs", "cstmrsrvc"
        self.auto_map_sip_usernames()
```

## Complete Example

```python
#!/usr/bin/env python3
from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult


class MultiTenantAgent(AgentBase):
    """Agent that handles multiple SIP endpoints."""

    def __init__(self):
        super().__init__(
            name="multi-tenant",
            route="/agent",
            port=3000
        )

        # Enable SIP routing
        self.enable_sip_routing(auto_map=True)

        # Register additional SIP usernames
        self.register_sip_username("sales")
        self.register_sip_username("support")
        self.register_sip_username("billing")

        # Configure voice
        self.add_language("English", "en-US", "rime.spore")

        # Build prompt
        self.prompt_add_section("Role", "You are a helpful assistant.")


if __name__ == "__main__":
    agent = MultiTenantAgent()
    agent.run()
```

## How SIP Routing Works

1. When `enable_sip_routing()` is called, an endpoint is created at the specified path (default: `/sip`)
2. Incoming SIP requests include a username in the request body
3. The agent extracts the SIP username and checks if it's registered
4. If registered, the agent handles the call; otherwise, routing continues

## Integration with SignalWire

To use SIP routing with SignalWire:

1. Create an External SWML Handler pointing to your agent's SIP endpoint
2. Configure your SignalWire SIP endpoints to route through this handler
3. The agent will automatically route based on the SIP username

## See Also

- [Agent Base Reference](agent-base.md) - Complete AgentBase documentation
- [SignalWire Integration](signalwire-integration.md) - Platform integration details
