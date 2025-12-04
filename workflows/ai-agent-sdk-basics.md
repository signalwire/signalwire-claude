# AI Agent SDK Basics

## Overview

Build Python-based AI voice agents using the SignalWire AI Agents SDK. This guide covers installation, basic structure, and local development.

## Related Workflows

- [Voice AI](voice-ai.md) - Overview and decision guide
- [AI Agent Prompting](ai-agent-prompting.md) - Best practices for prompts
- [AI Agent Functions](ai-agent-functions.md) - SWAIG function patterns
- [AI Agent Deployment](ai-agent-deployment.md) - Production deployment

## When to Use the SDK

Use the AI Agents SDK instead of SWML when you need:
- Complex multi-step workflows
- Advanced state management
- Multi-agent deployments
- Serverless deployments (Lambda, GCF, Azure)
- Integration with Python ML/AI libraries
- Custom business logic integration

For simple conversational IVR, SWML AI is sufficient.

## Installation

```bash
pip install signalwire-agents
# or with uv:
# uv pip install signalwire-agents
```

## Basic Agent Structure

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = ["signalwire-agents"]
# ///

from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="my-agent", port=3000)

        # Configure voice
        self.add_language("English", "en-US", "rime.spore")

        # Set agent personality via POM
        self.prompt_add_section(
            "Role",
            "You are a friendly customer service agent for Acme Corp."
        )

    @AgentBase.tool(
        name="check_balance",
        description="Check account balance for a customer",
        parameters={
            "account_number": {
                "type": "string",
                "description": "The customer's account number"
            }
        }
    )
    def check_balance(self, args, raw_data):
        """Check account balance"""
        account_number = args.get("account_number")
        # Database lookup...
        return SwaigFunctionResult(f"Account {account_number} has a balance of $1,234.56")

if __name__ == "__main__":
    agent = MyAgent()
    agent.run()
```

## AgentBase Constructor Parameters

The SDK automatically handles:
- HTTP server setup
- SWML generation
- Function discovery from `@AgentBase.tool` decorators
- Webhook routing

**Key Constructor Parameters:**
- `name` (required): Agent identifier
- `port` (default: 3000): HTTP server port
- `host` (default: "0.0.0.0"): Server bind address
- `basic_auth` (optional): Tuple of (username, password) for HTTP auth
- `auto_answer` (default: True): Automatically answer calls
- `record_call` (default: False): Enable call recording

**Example with all parameters:**

```python
agent = MyAgent(
    name="customer-service",
    port=5000,
    host="0.0.0.0",
    basic_auth=("agent", "secret123"),
    auto_answer=True,
    record_call=True
)
```

For complete AgentBase API reference, see: [reference/sdk/agent-base.md](../reference/sdk/agent-base.md)

## Tool Decorator Pattern

The `@AgentBase.tool` decorator automatically registers functions as SWAIG endpoints:

```python
@AgentBase.tool(
    name="function_name",
    description="What this function does (AI uses this)",
    parameters={
        "param1": {
            "type": "string",
            "description": "Parameter description"
        },
        "param2": {
            "type": "number",
            "description": "Numeric parameter",
            "required": False  # Optional parameters
        }
    }
)
def function_name(self, args, raw_data):
    """Docstring also helps AI understand function"""
    param1 = args.get("param1")
    param2 = args.get("param2", 0)  # Default for optional param

    # Your logic here...

    return SwaigFunctionResult("Response text the AI will speak")
```

**Parameter Types:**
- `string` - Text values
- `number` - Numeric values (int or float)
- `boolean` - True/False
- `array` - List of values
- `object` - Nested structure

**The decorator generates:**
- Function metadata for the AI
- HTTP endpoint routing
- Automatic argument parsing
- Error handling

## SwaigFunctionResult

Return values from tools use `SwaigFunctionResult`:

```python
# Simple response
return SwaigFunctionResult("I found your order. It shipped yesterday.")

# Response with additional SWML actions
from signalwire_agents.core.function_result import SwaigFunctionResult

result = SwaigFunctionResult("Transferring you now")
result.add_action("play", {"url": "say:Please hold"})
result.add_action("transfer", {"dest": "tel:+15551234567"})
return result

# Chain actions fluently
return (SwaigFunctionResult("Processing your payment")
    .add_action("play", {"url": "https://example.com/processing.mp3"})
    .add_action("hangup", {}))
```

**Common Actions:**
- `play` - Play audio
- `transfer` - Transfer call
- `hangup` - End call
- `set_meta_data` - Store metadata
- `toggle_functions` - Enable/disable functions

For complete action reference, see: [reference/sdk/function-result.md](../reference/sdk/function-result.md)

## Environment Variables

Configure agents via environment variables:

```bash
# SignalWire credentials (required for Fabric API)
export SIGNALWIRE_SPACE_NAME="myspace"
export SIGNALWIRE_PROJECT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export SIGNALWIRE_TOKEN="PTxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Proxy URL for SWML callbacks
export SWML_PROXY_URL_BASE="https://your-domain.com"

# Basic auth
export SWML_BASIC_AUTH_USER="agent"
export SWML_BASIC_AUTH_PASSWORD="secret"

# Debug webhooks
export DEBUG_WEBHOOK_URL="https://webhook.site/your-id"
export DEBUG_WEBHOOK_LEVEL="1"  # 0=off, 1=basic, 2=verbose

# Logging
export SWML_LOG_LEVEL="DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

**In your agent:**

```python
import os

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="my-agent",
            port=int(os.getenv('PORT', 3000)),
            basic_auth=(
                os.getenv('SWML_BASIC_AUTH_USER'),
                os.getenv('SWML_BASIC_AUTH_PASSWORD')
            ) if os.getenv('SWML_BASIC_AUTH_USER') else None
        )
```

For complete environment variable reference, see: [reference/deployment/environment-variables.md](../reference/deployment/environment-variables.md)

## Running Locally

### Development Server

```python
# my_agent.py
from my_agent import MyAgent

if __name__ == "__main__":
    agent = MyAgent()
    agent.run(debug=True)

    # Server runs on http://localhost:3000
    # SWML endpoint: http://localhost:3000/swml
```

### Testing with ngrok

For testing with actual phone calls:

```bash
# Start your agent
python my_agent.py

# In another terminal, expose with ngrok
ngrok http 3000

# Copy ngrok URL (e.g., https://abc123.ngrok.io)
# Configure in SignalWire Dashboard:
# - Phone number -> When a call comes in -> https://abc123.ngrok.io/swml
```

### Testing with swaig-test CLI

The SDK includes a CLI tool for testing without phone calls:

```bash
# Verify SWML output
swaig-test my_agent.py --dump-swml

# List registered functions
swaig-test my_agent.py --list-tools

# Execute a function directly
swaig-test my_agent.py --exec check_balance --account_number "12345"

# Test specific class in multi-class file
swaig-test my_agent.py --agent-class MyAgent

# Interactive testing
swaig-test my_agent.py --interactive
```

**Interactive Mode:**
```bash
swaig-test my_agent.py --interactive

# Test function calls interactively
> call check_balance account_number="12345"
> call transfer_funds from_account="123" to_account="456" amount=100
```

For complete testing patterns with pytest and integration tests, see: [AI Agent Testing](ai-agent-testing.md)

## Simple Examples

### Example 1: Banking Agent

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = ["signalwire-agents"]
# ///

from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult

class BankingAgent(AgentBase):
    def __init__(self):
        super().__init__(name="banking-agent", port=3000)
        self.add_language("English", "en-US", "rime.spore")

        self.prompt_add_section(
            "Role",
            "You are a helpful banking assistant for Acme Bank."
        )

    @AgentBase.tool(
        name="check_balance",
        description="Check the balance of a customer's account",
        parameters={
            "account_number": {
                "type": "string",
                "description": "The customer's account number"
            }
        }
    )
    def check_balance(self, args, raw_data):
        """Check account balance"""
        account_number = args.get("account_number")
        # Database lookup...
        balance = 1234.56  # Example
        return SwaigFunctionResult(f"The balance for account {account_number} is ${balance:.2f}")

    @AgentBase.tool(
        name="transfer_funds",
        description="Transfer funds between two accounts",
        parameters={
            "from_account": {"type": "string", "description": "Source account"},
            "to_account": {"type": "string", "description": "Destination account"},
            "amount": {"type": "number", "description": "Amount to transfer"}
        }
    )
    def transfer_funds(self, args, raw_data):
        """Transfer funds between accounts"""
        from_account = args.get("from_account")
        to_account = args.get("to_account")
        amount = args.get("amount")
        # Process transfer...
        return SwaigFunctionResult(f"Transferred ${amount} from {from_account} to {to_account}")

if __name__ == "__main__":
    agent = BankingAgent()
    agent.run()
```

### Example 2: Support Agent with State

```python
class SupportAgent(AgentBase):
    def __init__(self):
        super().__init__(name="support-agent")
        self.add_language("English", "en-US", "rime.spore")

        # Track state across function calls
        self.user_data = {}

        self.prompt_add_section(
            "Role",
            "You are a technical support agent. Help customers troubleshoot issues."
        )

    @AgentBase.tool(
        name="verify_identity",
        description="Verify customer identity with account number and PIN",
        parameters={
            "account_number": {"type": "string", "description": "Customer account number"},
            "pin": {"type": "string", "description": "4-digit PIN"}
        }
    )
    def verify_identity(self, args, raw_data):
        """Verify customer identity"""
        account_number = args.get("account_number")
        pin = args.get("pin")

        # Check credentials...
        if self.verify_credentials(account_number, pin):
            self.user_data['verified'] = True
            self.user_data['account'] = account_number
            return SwaigFunctionResult("Identity verified. How can I help you today?")
        else:
            return SwaigFunctionResult("Sorry, I couldn't verify your identity. Please try again.")

    @AgentBase.tool(
        name="check_ticket_status",
        description="Check the status of a support ticket",
        parameters={
            "ticket_number": {"type": "string", "description": "Ticket number"}
        }
    )
    def check_ticket_status(self, args, raw_data):
        """Check ticket status for verified user"""
        if not self.user_data.get('verified'):
            return SwaigFunctionResult("Please verify your identity first.")

        ticket_number = args.get('ticket_number')
        # Look up ticket...
        return SwaigFunctionResult(f"Ticket {ticket_number} is in progress and will be resolved by tomorrow.")

    def verify_credentials(self, account_number, pin):
        # Actual verification logic...
        return True  # Example
```

### Example 3: External API Integration

```python
import requests

class WeatherAgent(AgentBase):
    def __init__(self):
        super().__init__(name="weather-agent")
        self.add_language("English", "en-US", "rime.spore")

        self.prompt_add_section(
            "Role",
            "You are a weather information assistant. Use the get_weather function to provide current weather information."
        )

    @AgentBase.tool(
        name="get_weather",
        description="Get current weather for a city",
        parameters={
            "city": {"type": "string", "description": "City name"},
            "state": {"type": "string", "description": "State (optional)", "required": False}
        }
    )
    def get_weather(self, args, raw_data):
        """Get current weather for a city"""
        city = args.get("city")
        state = args.get("state")

        location = f"{city}, {state}" if state else city

        # Call weather API
        response = requests.get(
            f"https://api.weather.gov/...",  # Actual API endpoint
            params={'location': location}
        )

        if response.status_code == 200:
            data = response.json()
            temp = data.get('temperature')
            condition = data.get('condition')
            return SwaigFunctionResult(f"The weather in {location} is {condition} with a temperature of {temp}°F")
        else:
            return SwaigFunctionResult(f"Sorry, I couldn't fetch weather for {location}")

if __name__ == "__main__":
    agent = WeatherAgent()
    agent.run()
```

## SDK vs SWML Decision Guide

**Use SDK when:**
- Need complex state management
- Need to integrate with Python libraries
- Need multi-step conditional logic
- Need database integration
- Deploying to serverless (Lambda/GCF)

**Use SWML when:**
- Simple conversational flow
- No complex business logic
- Quick prototypes
- No-code/low-code approach preferred

**Can combine both:**
- SWML for call flow
- SDK SWAIG functions for complex operations

## Logging and Debugging

```python
import logging

class DebuggableAgent(AgentBase):
    def __init__(self):
        super().__init__(name="debug-agent")

        # Enable logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    @AgentBase.tool(name="some_function", description="Example", parameters={})
    def some_function(self, args, raw_data):
        self.logger.debug(f"Function called with: {args}")
        # Your logic...
        self.logger.info("Function completed successfully")
        return SwaigFunctionResult("Done")
```

**Check logs in:**
- Console output (when running locally)
- SignalWire Dashboard > Logs (for AI conversation transcripts)
- Debug webhooks (see below)

### Debug Webhooks

Monitor agent behavior in real-time:

```python
agent.set_params({
    "debug_webhook_url": "https://webhook.site/your-unique-id",
    "debug_webhook_level": 2  # 1=basic, 2=verbose
})
```

**Debug Levels:**
- **0**: Off (default)
- **1**: Function calls, errors, state changes
- **2**: Full transcripts and payloads

For complete debugging guide, see: [AI Agent Debug Webhooks](ai-agent-debug-webhooks.md)

## Next Steps

- [AI Agent Prompting](ai-agent-prompting.md) - Learn best practices for prompts
- [AI Agent Functions](ai-agent-functions.md) - Advanced SWAIG patterns
- [AI Agent Deployment](ai-agent-deployment.md) - Deploy to production
- [Voice AI](voice-ai.md) - Complete overview and examples
