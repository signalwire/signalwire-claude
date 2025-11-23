# Voice AI

## Overview

Build conversational AI agents for phone calls using SignalWire's AI platform, including SWAIG functions, AI Agents SDK, and Prompt Object Model (POM).

## AI Architecture Options

### 1. SWML AI (Simplest)

Declarative AI configuration in SWML documents.

### 2. SWAIG Functions

Add server-side functions your AI can call during conversations.

### 3. AI Agents SDK (Most Powerful)

Full Python SDK for building stateful, complex AI agents.

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

### SWAIG with Function Metadata

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

## AI Agents SDK (Python)

### Installation

```bash
pip install signalwire-agents
# or with uv:
# uv pip install signalwire-agents
```

### Basic Agent

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = ["signalwire-agents"]
# ///

from signalwire_agents import AgentBase

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__()

        # Set agent personality via POM
        self.agent.set_prompt(
            text="You are a friendly customer service agent for Acme Corp."
        )

    def check_balance(self, account_number):
        """Check account balance"""
        # Database lookup...
        return f"Account {account_number} has a balance of $1,234.56"

    def transfer_funds(self, from_account, to_account, amount):
        """Transfer funds between accounts"""
        # Process transfer...
        return f"Transferred ${amount} from {from_account} to {to_account}"

if __name__ == "__main__":
    agent = MyAgent()
    agent.run()
```

The SDK automatically:
- Discovers methods as SWAIG functions
- Generates function metadata from docstrings
- Handles HTTP server setup
- Manages SWML generation

### Prompt Object Model (POM)

Structure your AI's prompt for better control:

```python
from signalwire_agents import AgentBase

class CustomerServiceAgent(AgentBase):
    def __init__(self):
        super().__init__()

        # Set system prompt
        self.agent.set_prompt(
            text="""You are a customer service agent for Acme Corp.

Guidelines:
- Be polite and professional
- Ask clarifying questions if needed
- Use available functions to help customers
- If you can't help, offer to transfer to a human agent
"""
        )

        # Add pronunciation hints
        self.agent.add_pronunciation(
            "Acme", "ACK-mee"
        )

        # Set language and voice
        self.agent.set_language("en-US")
        self.agent.set_voice("female")

    def get_order_status(self, order_number):
        """Check the status of a customer's order"""
        # API call to order system...
        return f"Order {order_number} was shipped on Jan 10 and will arrive Jan 15"
```

### State Management

Track conversation state across function calls:

```python
class StatefulAgent(AgentBase):
    def __init__(self):
        super().__init__()
        self.user_data = {}  # Persistent across function calls

    def verify_identity(self, account_number, last_four_ssn):
        """Verify customer identity"""
        # Check credentials...
        if self.verify_credentials(account_number, last_four_ssn):
            self.user_data['verified'] = True
            self.user_data['account'] = account_number
            return "Identity verified. How can I help you today?"
        else:
            return "Sorry, I couldn't verify your identity. Please try again."

    def check_balance(self):
        """Check balance for verified user"""
        if not self.user_data.get('verified'):
            return "Please verify your identity first."

        account = self.user_data.get('account')
        # Look up balance...
        return f"Your balance is $1,234.56"
```

### Multi-Step Workflows

Guide the AI through specific workflows:

```python
class OrderAgent(AgentBase):
    def __init__(self):
        super().__init__()

        self.agent.set_prompt(
            text="""You are an order-taking agent for a restaurant.

Process:
1. Greet the customer
2. Take their order (use add_item function)
3. Confirm the order
4. Collect payment (use process_payment function)
5. Provide estimated time
"""
        )

        self.order_items = []
        self.order_total = 0.0

    def add_item(self, item_name, quantity=1):
        """Add an item to the order"""
        # Look up price...
        price = self.get_item_price(item_name)

        self.order_items.append({
            'item': item_name,
            'quantity': quantity,
            'price': price
        })

        self.order_total += price * quantity

        return f"Added {quantity}x {item_name}. Current total: ${self.order_total:.2f}"

    def confirm_order(self):
        """Confirm the current order"""
        if not self.order_items:
            return "Your order is empty."

        items_list = ", ".join([
            f"{item['quantity']}x {item['item']}"
            for item in self.order_items
        ])

        return f"Your order: {items_list}. Total: ${self.order_total:.2f}. Proceed to payment?"

    def process_payment(self, card_number):
        """Process payment for the order"""
        # Payment processing...
        return f"Payment of ${self.order_total:.2f} processed. Estimated time: 20 minutes."

    def get_item_price(self, item_name):
        menu = {
            'burger': 8.99,
            'fries': 3.99,
            'soda': 1.99
        }
        return menu.get(item_name.lower(), 0)
```

### Advanced: External API Integration

```python
import requests

class WeatherAgent(AgentBase):
    def __init__(self):
        super().__init__()

        self.agent.set_prompt(
            text="You are a weather information assistant. Use the get_weather function to provide current weather information."
        )

    def get_weather(self, city, state=None):
        """Get current weather for a city"""
        # Call weather API
        location = f"{city}, {state}" if state else city

        # Example using weather API
        response = requests.get(
            f"https://api.weather.gov/...",  # Actual API endpoint
            params={'location': location}
        )

        if response.status_code == 200:
            data = response.json()
            temp = data.get('temperature')
            condition = data.get('condition')
            return f"The weather in {location} is {condition} with a temperature of {temp}°F"
        else:
            return f"Sorry, I couldn't fetch weather for {location}"
```

### Testing Locally

```python
# test_agent.py
from my_agent import MyAgent

if __name__ == "__main__":
    agent = MyAgent()

    # Start development server
    agent.run(debug=True)

    # Server runs on http://localhost:5000
    # Point your SWML to http://localhost:5000/swml
```

Use ngrok for testing with actual phone calls:

```bash
ngrok http 5000
# Use ngrok URL in your phone number configuration
```

### Deployment

The AI Agents SDK supports multiple deployment methods:

```python
# Serverless (AWS Lambda, etc.)
def lambda_handler(event, context):
    agent = MyAgent()
    return agent.handle_request(event)

# Traditional server
if __name__ == "__main__":
    agent = MyAgent()
    agent.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
```

## Advanced AI Patterns

### Conversation Context

```python
class ContextAwareAgent(AgentBase):
    def __init__(self):
        super().__init__()
        self.conversation_history = []

    def remember_preference(self, preference_type, value):
        """Remember user preferences"""
        self.conversation_history.append({
            'type': preference_type,
            'value': value
        })
        return f"I'll remember that you prefer {value}"

    def recall_preference(self, preference_type):
        """Recall a user preference"""
        for item in reversed(self.conversation_history):
            if item['type'] == preference_type:
                return f"You said you prefer {item['value']}"
        return f"I don't have a {preference_type} preference on record"
```

### Sentiment Analysis

```python
class SentimentAgent(AgentBase):
    def __init__(self):
        super().__init__()
        self.sentiment_score = 0

    def analyze_sentiment(self, customer_message):
        """Analyze customer sentiment (mock implementation)"""
        # Use sentiment analysis API or library
        # For example, TextBlob, VADER, or external API

        negative_words = ['angry', 'frustrated', 'terrible', 'awful']
        positive_words = ['happy', 'great', 'wonderful', 'excellent']

        message_lower = customer_message.lower()

        if any(word in message_lower for word in negative_words):
            self.sentiment_score -= 1
            if self.sentiment_score < -2:
                return "escalate_to_human"
        elif any(word in message_lower for word in positive_words):
            self.sentiment_score += 1

        return "continue"
```

### Call Transfer Integration

```python
class TransferAgent(AgentBase):
    def __init__(self):
        super().__init__()

    def transfer_to_human(self, department=None):
        """Transfer call to human agent"""
        dept_numbers = {
            'sales': '+15551111111',
            'support': '+15552222222',
            'billing': '+15553333333'
        }

        number = dept_numbers.get(department, '+15550000000')

        # Return SWML action to transfer
        return {
            "response": f"Transferring you to {department or 'a representative'}",
            "action": [
                {
                    "say": f"Please hold while I transfer you to {department or 'our team'}",
                    "connect": {
                        "to": number
                    }
                }
            ]
        }
```

## Best Practices

### 1. Clear Prompts

```python
# Good prompt
self.agent.set_prompt(text="""
You are a technical support agent.

Role: Help customers troubleshoot their devices
Tone: Patient and helpful
Process:
1. Ask what device they're using
2. Ask what problem they're experiencing
3. Provide step-by-step solutions
4. If unresolved, offer to create a support ticket

Do NOT: Make promises about timelines or refunds
""")

# Avoid vague prompts
# Bad: "You help customers"
```

### 2. Function Documentation

```python
def check_inventory(self, product_id, location="warehouse"):
    """
    Check product inventory levels

    Args:
        product_id: Unique product identifier (e.g., "PROD-12345")
        location: Storage location to check (default: "warehouse")

    Returns:
        Current inventory count and location
    """
    # Implementation...
```

The SDK uses docstrings to help the AI understand when to call functions.

### 3. Error Handling

```python
def lookup_order(self, order_number):
    """Look up order status"""
    try:
        order = self.database.get_order(order_number)
        if order:
            return f"Order {order_number} is {order.status}"
        else:
            return f"I couldn't find order {order_number}. Could you double-check the order number?"
    except Exception as e:
        # Log error but don't expose to user
        self.log_error(e)
        return "I'm having trouble accessing the order system. Let me transfer you to someone who can help."
```

### 4. Conversational Responses

```python
# Good: Natural, helpful
"I found your order! It was shipped on January 10th and should arrive by January 15th."

# Avoid: Robotic, technical
"Order status: SHIPPED. Ship date: 2025-01-10. ETA: 2025-01-15."
```

## Testing & Debugging

### Local Testing with swaig-test CLI

```bash
# Install AI Agents SDK
pip install signalwire-agents

# Test your agent
swaig-test my_agent.py

# Interactive testing mode
swaig-test my_agent.py --interactive
```

### Logging

```python
import logging

class DebuggableAgent(AgentBase):
    def __init__(self):
        super().__init__()

        # Enable logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    def some_function(self, param):
        self.logger.debug(f"Function called with: {param}")
        # Your logic...
        self.logger.info("Function completed successfully")
```

### Dashboard Logs

Check SignalWire Dashboard > Logs for:
- AI conversation transcripts
- SWAIG function calls and responses
- Errors and warnings

## Example: Complete Drive-Thru Agent

Based on the HolyGuacamole example:

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = ["signalwire-agents"]
# ///

from signalwire_agents import AgentBase

class DriveThruAgent(AgentBase):
    def __init__(self):
        super().__init__()

        self.agent.set_prompt(text="""
You are a friendly drive-thru order taker for HolyGuacamole.

Process:
1. Greet customer warmly
2. Take their order using add_item function
3. Ask if they want to add anything else
4. Confirm the order
5. Give them the total and estimated time
""")

        self.order = []
        self.menu = {
            'burrito': 8.99,
            'taco': 3.99,
            'chips': 2.99,
            'guacamole': 1.99,
            'soda': 1.99
        }

    def add_item(self, item_name, quantity=1, customizations=None):
        """Add an item to the order"""
        item_name = item_name.lower()

        if item_name not in self.menu:
            return f"Sorry, we don't have {item_name}. Would you like something else?"

        price = self.menu[item_name]
        self.order.append({
            'item': item_name,
            'quantity': quantity,
            'price': price,
            'customizations': customizations or []
        })

        total = sum(item['price'] * item['quantity'] for item in self.order)

        return f"Added {quantity} {item_name}. Anything else? Your current total is ${total:.2f}"

    def confirm_order(self):
        """Confirm and finalize the order"""
        if not self.order:
            return "You haven't ordered anything yet. What would you like?"

        items = ", ".join([
            f"{item['quantity']} {item['item']}"
            for item in self.order
        ])

        total = sum(item['price'] * item['quantity'] for item in self.order)

        return f"Your order: {items}. Total: ${total:.2f}. Please pull forward to the window. Thank you!"

if __name__ == "__main__":
    agent = DriveThruAgent()
    agent.run()
```

## Next Steps

- [Fabric & Relay](fabric-relay.md) - Real-time agent control
- [Webhooks & Events](webhooks-events.md) - Track AI interactions
- [Call Control](call-control.md) - Integrate AI with call features
