# Voice AI

## Overview

Build conversational AI agents for phone calls using SignalWire's AI platform. This guide helps you choose the right approach and navigate to focused workflow documentation.

## Quick Navigation

**New to Voice AI? Start here:**
- [AI Architecture Options](#ai-architecture-options) - Choose your approach
- [SWML AI Basics](#swml-ai-basics) - Simplest declarative AI
- [Example: Complete Drive-Thru Agent](#example-complete-drive-thru-agent) - Full working example

**Building with Python SDK? Go to:**
- [AI Agent SDK Basics](ai-agent-sdk-basics.md) - Installation and fundamentals
- [AI Agent Prompting](ai-agent-prompting.md) - Prompting best practices
- [AI Agent Functions](ai-agent-functions.md) - SWAIG function patterns
- [AI Agent Deployment](ai-agent-deployment.md) - Production deployment

**Looking for specific topics:**
- [SWAIG Functions](#swaig-signalwire-ai-gateway) - Add server-side functions to SWML AI
- [When to Pull Additional Documentation](#when-to-pull-additional-documentation) - Reference guide

## AI Architecture Options

### 1. SWML AI (Simplest)

Declarative AI configuration in SWML documents. Best for:
- Simple conversational IVR
- Quick prototypes
- No-code or low-code deployments

**→ Continue reading this page for SWML AI basics**

### 2. SWAIG Functions

Add server-side functions your AI can call during conversations. Best for:
- Database lookups
- External API integration
- Business logic integration
- State management

**→ See [SWAIG Functions](#swaig-signalwire-ai-gateway) below or [AI Agent Functions](ai-agent-functions.md)**

### 3. AI Agents SDK (Most Powerful)

Full Python SDK for building stateful, complex AI agents. Best for:
- Complex multi-step workflows
- Advanced state management
- Multi-agent deployments
- Serverless deployments (Lambda, GCF, Azure)
- Integration with Python ML/AI libraries

**→ Go to [AI Agent SDK Basics](ai-agent-sdk-basics.md)**

### Quick Decision Tree

```
Need database/API access? → Use SWAIG or SDK
Need complex state management? → Use SDK
Need multi-agent architecture? → Use SDK
Need serverless deployment? → Use SDK
Want simplest approach? → Use SWML AI
```

## SWML AI Basics

### Simple AI Agent (SWML)

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - ai:
        prompt: "You are a helpful customer service agent for Acme Corp. Answer questions about our products and services politely."
        post_prompt_url: "https://example.com/swaig"
        post_prompt_auth_user: "username"
        post_prompt_auth_password: "password"
        language: "en-US"
        voice: "female"
```

### AI Parameters

- **prompt**: System instruction for the AI (personality, role, guidelines)
- **post_prompt_url**: SWAIG endpoint for function calls (optional)
- **post_prompt_auth_user/password**: HTTP Basic Auth for SWAIG (optional)
- **language**: Voice language (default: `en-US`)
- **voice**: Voice gender or specific voice name
- **temperature**: Creativity level 0.0-1.0 (default: 0.7)

### Multi-Language Support

Add multiple languages for automatic detection:

```yaml
- ai:
    prompt: "You are a customer service agent."
    languages:
      - name: "English"
        code: "en-US"
        voice: "rime.spore"
      - name: "Spanish"
        code: "es-MX"
        voice: "rime.spore"
```

The AI automatically detects and responds in the caller's language.

## SWAIG (SignalWire AI Gateway)

SWAIG allows your AI agent to call server-side functions via HTTP POST.

### How SWAIG Works

1. AI decides it needs to call a function (e.g., "check_balance")
2. SignalWire sends HTTP POST to your SWAIG endpoint
3. Your server processes the request and returns JSON
4. AI receives the response and continues the conversation

### SWAIG Request Format

```json
{
  "function": "check_balance",
  "args": {
    "account_number": "12345"
  },
  "meta_data": {
    "call_id": "c1234567-89ab-cdef-0123-456789abcdef",
    "from": "+15559876543",
    "to": "+15551234567"
  }
}
```

### SWAIG Response Format

```json
{
  "response": "The account balance for account 12345 is $1,234.56",
  "action": []
}
```

### SWAIG Endpoint (Python/Flask)

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/swaig', methods=['POST'])
def handle_swaig():
    data = request.json

    function = data.get('function')
    args = data.get('args', {})
    meta = data.get('meta_data', {})

    # Route to appropriate function
    handlers = {
        'check_balance': check_balance,
        'transfer_funds': transfer_funds,
        'get_recent_transactions': get_recent_transactions
    }

    handler = handlers.get(function)
    if not handler:
        return jsonify({
            "response": f"Unknown function: {function}",
            "action": []
        })

    # Call handler
    result = handler(args, meta)

    return jsonify({
        "response": result,
        "action": []
    })

def check_balance(args, meta):
    account_number = args.get('account_number')
    # Database lookup...
    balance = 1234.56  # Example
    return f"The balance for account {account_number} is ${balance:.2f}"

def transfer_funds(args, meta):
    from_account = args.get('from_account')
    to_account = args.get('to_account')
    amount = args.get('amount')
    # Process transfer...
    return f"Transferred ${amount} from {from_account} to {to_account}"

def get_recent_transactions(args, meta):
    account_number = args.get('account_number')
    # Database query...
    return "Your last 3 transactions: $50 on Jan 1, $100 on Jan 5, $25 on Jan 10"

if __name__ == '__main__':
    app.run(port=5000)
```

### SWML with Function Metadata

Help the AI understand available functions by including metadata:

```yaml
version: 1.0.0
sections:
  main:
    - answer: {}
    - ai:
        prompt: "You are a banking assistant. Help customers check balances and transfer funds."
        post_prompt_url: "https://example.com/swaig"
        functions:
          - name: "check_balance"
            purpose: "Check the balance of a customer's account"
            arguments:
              - name: "account_number"
                type: "string"
                description: "The customer's account number"
          - name: "transfer_funds"
            purpose: "Transfer funds between accounts"
            arguments:
              - name: "from_account"
                type: "string"
                description: "Source account number"
              - name: "to_account"
                type: "string"
                description: "Destination account number"
              - name: "amount"
                type: "number"
                description: "Amount to transfer in dollars"
```

**For advanced SWAIG patterns, see: [AI Agent Functions](ai-agent-functions.md)**

## Example: Complete Drive-Thru Agent

Based on the HolyGuacamole example using the Python SDK:

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = ["signalwire-agents"]
# ///

from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult

class DriveThruAgent(AgentBase):
    def __init__(self):
        super().__init__(name="drive-thru", port=3000)

        # Configure voice
        self.add_language("English", "en-US", "rime.spore")

        # Set agent personality
        self.prompt_add_section("Role", """
You are a friendly drive-thru order taker for HolyGuacamole.

Process:
1. Greet customer warmly
2. Take their order using add_item function
3. Ask if they want to add anything else
4. Confirm the order
5. Give them the total and estimated time
""")

        # Order state
        self.order = []
        self.menu = {
            'burrito': 8.99,
            'taco': 3.99,
            'chips': 2.99,
            'guacamole': 1.99,
            'soda': 1.99
        }

    @AgentBase.tool(
        name="add_item",
        description="Add an item to the order",
        parameters={
            "item_name": {"type": "string", "description": "Name of the item"},
            "quantity": {"type": "number", "description": "Quantity to order", "required": False},
            "customizations": {"type": "string", "description": "Special requests", "required": False}
        }
    )
    def add_item(self, args, raw_data):
        """Add an item to the order"""
        item_name = args.get("item_name", "").lower()
        quantity = args.get("quantity", 1)
        customizations = args.get("customizations")

        if item_name not in self.menu:
            return SwaigFunctionResult(f"Sorry, we don't have {item_name}. Would you like something else?")

        price = self.menu[item_name]
        self.order.append({
            'item': item_name,
            'quantity': quantity,
            'price': price,
            'customizations': customizations
        })

        total = sum(item['price'] * item['quantity'] for item in self.order)

        return SwaigFunctionResult(f"Added {quantity} {item_name}. Anything else? Your current total is ${total:.2f}")

    @AgentBase.tool(
        name="confirm_order",
        description="Confirm and finalize the order",
        parameters={}
    )
    def confirm_order(self, args, raw_data):
        """Confirm and finalize the order"""
        if not self.order:
            return SwaigFunctionResult("You haven't ordered anything yet. What would you like?")

        items = ", ".join([
            f"{item['quantity']} {item['item']}"
            for item in self.order
        ])

        total = sum(item['price'] * item['quantity'] for item in self.order)

        return SwaigFunctionResult(f"Your order: {items}. Total: ${total:.2f}. Please pull forward to the window. Thank you!")

if __name__ == "__main__":
    agent = DriveThruAgent()
    agent.run()
```

**To learn more about building SDK-based agents, see: [AI Agent SDK Basics](ai-agent-sdk-basics.md)**

## Best Practices Quick Reference

### Prompting
- Treat AI like a person, not a program
- Use clear, natural language
- Avoid over-prompting and "never" statements
- Use the RISE-M framework (Role, Instructions, Steps, Expectations, Methods)

**→ Full guide: [AI Agent Prompting](ai-agent-prompting.md)**

### Functions
- Use SWAIG functions for all data retrieval
- Store sensitive data in metadata, not in prompts
- Provide clear function descriptions
- Use progressive knowledge building

**→ Full guide: [AI Agent Functions](ai-agent-functions.md)**

### Deployment
- Start simple, iterate constantly
- Use environment variables for configuration
- Monitor post-prompt data
- Test continuously with real phone calls

**→ Full guide: [AI Agent Deployment](ai-agent-deployment.md)**

## When to Pull Additional Documentation

**Most tasks can be completed using the focused workflow guides above.** Pull additional reference documentation only when you need:

### ✅ DO Pull References When:

**User asks for specific API details:**
- "What are all the parameters for AgentBase constructor?" → [AgentBase API](../reference/sdk/agent-base.md)
- "What actions can SwaigFunctionResult return?" → [SwaigFunctionResult](../reference/sdk/function-result.md)
- "How do I configure environment variables?" → [Environment Variables](../reference/deployment/environment-variables.md)

**User needs advanced features not shown in examples:**
- Complex workflow with state transitions → [Contexts & Steps](../reference/sdk/contexts-steps.md)
- Pre-built agent templates → [Prefabs](../reference/sdk/prefabs.md)
- Advanced DataMap with array processing → [DataMap Advanced](../reference/sdk/datamap-advanced.md)
- Amazon Bedrock integration → [Bedrock Integration](../reference/sdk/bedrock-agent.md)

**User is deploying to specific platform:**
- AWS Lambda, Google Cloud Functions, Azure → [Serverless Deployment](../reference/deployment/serverless.md)
- WebRTC browser integration → [SignalWire Integration](../reference/deployment/signalwire-integration.md)
- Multi-agent server setup → [AgentServer](../reference/sdk/agent-server.md)

**User is debugging production issues:**
- Real-time monitoring needs → [AI Agent Debug Webhooks](ai-agent-debug-webhooks.md)
- Testing strategies → [AI Agent Testing](ai-agent-testing.md)
- Security hardening → [AI Agent Security](ai-agent-security.md)

### ❌ DON'T Pull References When:

**User wants basic examples:**
- "How do I create a simple AI agent?" → Use examples in the workflow guides
- "How do I add a SWAIG function?" → See [AI Agent SDK Basics](ai-agent-sdk-basics.md) or this page
- "What's the best way to prompt?" → See [AI Agent Prompting](ai-agent-prompting.md)

**User asks general "how do I" questions:**
- "How do I handle transfers?" → See [AI Agent Functions](ai-agent-functions.md)
- "How do I add voice configuration?" → See [AI Agent SDK Basics](ai-agent-sdk-basics.md)
- "How do I test my agent?" → See [AI Agent SDK Basics](ai-agent-sdk-basics.md)

**You can answer from the workflow guides:**
- If the pattern exists in the focused workflow files
- If the best practice is covered in [AI Agent Prompting](ai-agent-prompting.md)
- If the deployment pattern is in [AI Agent Deployment](ai-agent-deployment.md)

### Quick Reference Map

**When building basic agents:**
- This file + [AI Agent SDK Basics](ai-agent-sdk-basics.md) + [AI Agent Prompting](ai-agent-prompting.md)

**When deploying to production:**
- This file + [AI Agent Deployment](ai-agent-deployment.md) + [AI Agent Error Handling](ai-agent-error-handling.md) + [AI Agent Security](ai-agent-security.md)

**When deploying serverless:**
- This file + [AI Agent Deployment](ai-agent-deployment.md) + [Serverless Deployment](../reference/deployment/serverless.md)

**When building complex workflows:**
- This file + [AI Agent Functions](ai-agent-functions.md) + [Contexts & Steps](../reference/sdk/contexts-steps.md)

**When user needs complete API reference:**
- [AgentBase API](../reference/sdk/agent-base.md) for constructor/method details
- [SwaigFunctionResult](../reference/sdk/function-result.md) for action catalog
- [Skills System](../reference/sdk/skills-complete.md) for built-in skills reference

**When looking for working code examples:**
- [Working Examples](../reference/examples/) directory has 6 complete implementations

## Next Steps

**Choose your path:**

1. **Simple SWML AI** - Continue with this page, add SWAIG functions as needed
2. **Python SDK** - Go to [AI Agent SDK Basics](ai-agent-sdk-basics.md)
3. **Production Deployment** - See [AI Agent Deployment](ai-agent-deployment.md)
4. **Learn Prompting** - Read [AI Agent Prompting](ai-agent-prompting.md)
5. **Build Functions** - Explore [AI Agent Functions](ai-agent-functions.md)

**Other related workflows:**
- [Fabric & Relay](fabric-relay.md) - Real-time agent control
- [Webhooks & Events](webhooks-events.md) - Track AI interactions and debugging
- [Call Control](call-control.md) - Integrate AI with call features
