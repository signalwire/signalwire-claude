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

## Best Practices from Production

### The Fundamental Mindset

**Critical Insight**: Treat the AI agent like a person, not a program.

> "How would you instruct your mother to do the task you want done?" - Brian West

This mindset shift changes everything about how you write prompts and design AI interactions.

### Prompting Best Practices

#### 1. Use Clear, Concise Language

**Good:**
```
Transfer the caller after you validate their account.
```

**Bad (Too Strong):**
```
Never transfer the call until you validate their account.
```

The word "never" creates rigid behavior that prevents proper execution. Strong negative language confuses AI agents.

#### 2. Avoid Overprompting

- Less is more - don't give excessive information
- Break complex tasks across multiple AI agents
- Each agent should have a focused, specific purpose

**Example of overprompting:**
```
You must always greet the customer. Never forget to greet them. Make absolutely sure you say hello. Don't skip the greeting under any circumstances.
```

**Better:**
```
Greet the customer warmly.
```

#### 3. Address Edge Cases in Prompts

**Example:**
```
You always have pizza in stock. Never tell customers you're out of pizza.
```

Without this instruction, AI might occasionally hallucinate being out of stock, even when you have inventory.

#### 4. Use the RISE-M Prompt Framework

The RISE-M framework provides structured prompting:
- **R**ole: Define the agent's role
- **I**nstructions: Clear step-by-step guidance
- **S**teps: Numbered workflow
- **E**xpectations: Desired outcomes
- **M**ethods: Tools and functions available

**Example:**
```python
self.agent.set_prompt(text="""
Role: You are Tina, a professional receptionist for Spacely Sprockets.

Instructions:
- Answer the phone professionally
- Gather caller information before transferring
- Use available functions to help callers

Steps:
1. Greet the caller based on time of day
2. Ask how you can assist them
3. Get their name, company name, and phone number
4. Transfer to the appropriate department if needed
5. If you've helped the customer, thank them and hang up

Expectations:
- Be polite and professional at all times
- Never share confidential company information
- Transfer calls only after gathering required information

Methods:
- Use transfer_to_sales for sales inquiries
- Use transfer_to_support for technical issues
""")
```

### AI Agent Configuration Patterns

#### Conversation Flow Setup (UI Method)

Use the SignalWire Dashboard for simple agents:

```
Name: Tina
Description: You work for Spacely Sprockets. You answer the phone
and take notes on what the caller needs and can optionally transfer
elsewhere in the company.

Language: US English
Gender: Female
Voice: Neural
Personality: Professional
Time Zone: US/Central

Hours of Operation:
- Monday-Friday: 9 AM - 5 PM

Skills and Behaviors:
- Transfer Calls
  - Sales: +15551234567
  - Support: +15551234568

Conversation Flow:
Step 1: Greet the caller based on time of day and ask how you can assist them.
Step 2: Get their name, company name, and phone number before you transfer.
Step 3: If you've helped customer and there is nothing else to do, thank the caller and hang up.
```

#### Advanced Configuration (SWML Method)

Use SWML for:
- Custom function integration
- Multi-language support
- Complex conditional logic
- Post-prompt processing

### Multi-Language Support

**Auto-Detection Capability:**
- Add multiple languages in the Languages tab
- AI automatically detects and responds in the caller's language
- No need to write separate prompts per language
- Supports 10+ languages with Nova 3

**Static Greeting for Compliance:**
```yaml
- play:
    urls:
      - "say:English greeting"
      - "say:Spanish greeting"
- ai:
    prompt: "Your instructions here"
```

This ensures compliance requirements are met (e.g., call recording disclosure) while still leveraging multi-language AI.

### Voice Cloning and Premium Voices

**Available TTS Providers:**
- Google (default, included)
- 11 Labs (premium, clone your own voice)
- OpenAI TTS
- PlayHT (for emotions)

**Voice Cloning Benefits:**
- Clone your voice with 11 Labs
- Speak 29 languages in your own voice
- Maintains consistency across languages
- Preserves brand voice

### Latency Optimization

#### Filler Strategies

**1. Speech Fillers:**
```yaml
fillers:
  - "Let me look that up for you"
  - "One moment please"
  - "Just checking on that"
```

**2. Sound File Fillers:**
```yaml
functions:
  - name: lookup_order
    wait_file: "https://cdn.example.com/typing-sounds.mp3"
```

Creates natural conversation flow by playing ambient sounds (typing, paper rustling) during processing.

**3. Per-Function Fillers:**
```yaml
functions:
  - name: generate_image
    purpose: "Create custom bouquet image"
    fillers:
      - "Let me arrange those flowers for you"
      - "Creating your custom bouquet"
    wait_file: "https://cdn.example.com/packaging-sounds.mp3"
```

#### Silence Management

```yaml
- play:
    url: "silence:1.0"  # 1 second of silence
```

Strategic silence can make conversations feel more natural.

### Handling Interruptions

**Transparent Barge:**
- AI removes last response when interrupted
- Rolls up multiple interruptions into one query
- Provides more pertinent answers
- Two logs available: raw and processed

**Barge Acknowledgment:**
Configure AI to acknowledge excessive interruptions:
```
If the caller interrupts you repeatedly, politely ask them to let you finish speaking.
```

## Common Patterns from Production

### Pattern 1: Restaurant Reservation System

```python
class RestaurantAgent(AgentBase):
    def __init__(self):
        super().__init__()

        self.agent.set_prompt(text="""
You are a reservation agent for a busy restaurant.

Steps:
1. Ask for the date and time they'd like to dine
2. Ask for party size
3. Check availability using check_availability function
4. Book the reservation using book_reservation function
5. Confirm details and thank them

Always have pizza in stock. Never tell customers we're out of pizza.
""")

    def check_availability(self, date, time, party_size):
        """Check if restaurant has availability"""
        # Database lookup...
        return f"We have tables available at {time} for {party_size} guests"

    def book_reservation(self, name, phone, date, time, party_size):
        """Book the reservation"""
        # Store in database...
        return f"Reservation confirmed for {name} on {date} at {time} for {party_size} guests"
```

### Pattern 2: Multi-Factor Authentication

```yaml
functions:
  - name: send_mfa_code
    purpose: "Send 6-digit verification code"
    data_map:
      webhooks:
        - url: "https://api.signalwire.com/api/mfa/send"
          method: POST
          body:
            to: "{{call.from}}"

  - name: verify_mfa_code
    purpose: "Verify the code provided by user"
    parameters:
      - name: code
        type: string
    data_map:
      webhooks:
        - url: "https://api.signalwire.com/api/mfa/verify"
```

**Best Practices:**
- Store session data in metadata
- Never echo codes back to user
- Limit verification attempts
- Expire codes after time limit

### Pattern 3: Healthcare/Nursing Home Assistant

```yaml
- ai:
    prompt: |
      You are Adam, a nursing home digital assistant.
      Conduct a weekly health assessment.

      Steps:
      1. Verify patient identity with PIN
      2. Ask standard health questions
      3. Provide guidance if needed
      4. Store summary for caregiver
    functions:
      - name: verify_patient
        web_hook: "https://yourserver.com/verify"
      - name: get_health_info
        web_hook: "https://yourserver.com/datasphere"
      - name: store_summary
        web_hook: "https://yourserver.com/save"
      - name: send_caregiver_sms
        web_hook: "https://yourserver.com/notify"
```

### Pattern 4: Context Switching Without Ending Session

**Dynamic Context Switching** - SignalWire's unique capability:

```yaml
- ai:
    prompt: "You are now a sales agent"
    params:
      post_prompt_url: "https://yourserver.com/context-switch"
```

The agent can morph from one role to another without ending the session, reducing call legs and costs.

## SWAIG Function Techniques

### Progressive Knowledge Building

Use metadata to build knowledge across function calls:

```javascript
// In SWAIG function
const ticketNumbers = tickets.map(t => t.number);

// Return with metadata
res.json({
  response: "Here are your open tickets: " + ticketNumbers.join(', '),
  metadata: {
    open_tickets: ticketNumbers
  }
});

// Later function can access
if (metadata.open_tickets.includes(ticketNumber)) {
  // Allow operation
}
```

**Use cases:**
- Session state
- Authentication tokens
- Previous interactions
- Conditional permissions

### Testing Functions with webhook.site

**For Development:**
1. Get temporary URL from webhook.site
2. Set as function web_hook
3. Inspect payloads in real-time
4. Iterate on implementation

This is invaluable for debugging SWAIG function payloads without deploying code.

### Post-Prompt Processing

**Collect data after call ends:**

```yaml
ai:
  prompt: "Gather customer name, phone, and order details"
  post_prompt_url: "https://yourserver.com/summary"
  post_prompt: |
    Summarize the conversation as a valid JSON object.
    Include: customer_name, customer_phone, customer_order
```

**Server receives:**
```json
{
  "post_prompt_data": {
    "parsed": {
      "customer_name": "SpongeBob",
      "customer_phone": "(414) 293-4015",
      "customer_order": [
        {"size": "small", "quantity": 2},
        {"size": "large", "quantity": 2}
      ]
    }
  },
  "conversation": [...],
  "call_id": "...",
  "ai_session_id": "..."
}
```

### Response with Additional SWML

SWAIG functions can return SWML to dynamically control the call:

```json
{
  "response": "Transferring you now",
  "action": [
    {
      "play": {
        "url": "say:Please hold while I transfer you"
      }
    },
    {
      "connect": {
        "to": "+15551234567"
      }
    }
  ]
}
```

### Metadata for Secure Data

**Store sensitive information outside LLM context:**

```yaml
- ai:
    functions:
      - name: verify_customer
        data_map:
          webhooks:
            - url: "https://yourserver.com/verify"
              output:
                response: "Customer verified"
                action:
                  - set_meta_data:
                      customer_id: "{{response.id}}"
                      customer_name: "{{response.name}}"
                      account_balance: "{{response.balance}}"
```

**Benefits:**
- Sensitive data stays out of LLM
- Accessible across all SWAIG functions
- Reduces redundant database lookups
- Improves latency

**Metadata Token** for scoped access:

```yaml
functions:
  - name: payment_function
    metadata_token: "payments_only"
  - name: account_lookup
    metadata_token: "general"
```

## Anti-Patterns to Avoid

### 1. Over-Prompting

❌ **Wrong:**
```
Never, ever transfer calls without permission.
Always ask before doing anything.
Don't forget to verify the customer.
Make absolutely sure you collect all information.
```

✅ **Right:**
```
Transfer calls after verification.
Collect name, phone, and issue before transferring.
```

**Why:** LLMs respond better to clear, concise instructions. Strong negative language creates confusion.

### 2. Treating AI Like Code

❌ **Wrong:** "I will program the AI to do X"

✅ **Right:** "I will guide the AI toward objective X"

**Mindset Shift:**
- Not programming - prompting
- Not commands - instructions
- Not deterministic - probabilistic
- Not rigid - adaptable

### 3. Relying on AI to Remember Facts

❌ **Wrong:**
```python
self.agent.set_prompt(text="""
Our hours are 9 AM to 5 PM Monday through Friday.
We're located at 123 Main St.
Our products include widgets, gadgets, and gizmos priced at $10, $20, and $30.
""")
```

✅ **Right:**
```python
def get_hours(self):
    """Get business hours"""
    return "We're open 9 AM to 5 PM Monday through Friday"

def get_location(self):
    """Get business location"""
    return "We're located at 123 Main St"

def get_products(self):
    """Get product catalog"""
    products = database.query("SELECT * FROM products")
    return format_product_list(products)
```

**Why:** Use functions for all data retrieval. AI can hallucinate or misremember embedded facts.

### 4. Exposing Sensitive Data to LLM

❌ **Wrong:**
```yaml
- ai:
    prompt: "Collect credit card number and repeat it back"
```

✅ **Right:**
```yaml
- pay:
    payment_method: credit_card
    payment_handler: "https://yourserver.com/payment-processor"
# Payment info bypasses LLM completely
```

## Advanced Techniques

### DataSphere Integration (RAG)

**Knowledge Base Access** for AI agents:

```yaml
functions:
  - name: lookup_info
    purpose: "Get information from knowledge base"
    data_map:
      webhooks:
        - url: "https://api.signalwire.com/api/datasphere/search"
          method: POST
          headers:
            Authorization: "Basic {{base64_encoded_creds}}"
          body:
            query: "{{args.question}}"
            document_id: "your-document-id"
          output:
            response: "{{chunk.text}}"
```

**Use Cases:**
- Medical information lookup (HIPAA-compliant)
- Product documentation search
- FAQ retrieval
- Policy information

### Thinking Mode (Two-Turn Processing)

**Enable for complex reasoning:**

```yaml
ai:
  params:
    enable_thinking_mode: true
    thinking_model: "gpt-4o-mini"
    response_model: "gpt-4o-nano"
```

**How It Works:**
1. First turn: AI formulates a plan
2. Second turn: AI executes response
3. Results in more detailed, accurate answers

### Outbound Dialer with CRM

**Automated Patient/Customer Outreach:**

```python
from signalwire.relay.calling import Call

@app.route('/dial-patients')
def dial_patients():
    patients = db.query("SELECT * FROM patients WHERE needs_checkup = true")

    for patient in patients:
        call = client.calling.dial(
            to=patient.phone,
            from_=BUSINESS_NUMBER,
            url=f"https://yourserver.com/health-assessment/{patient.id}"
        )
```

**AI Agent with Patient Context:**

```yaml
- ai:
    prompt: |
      You are a health assessment assistant.
      1. Verify patient identity with PIN
      2. Ask standard health questions
      3. Provide guidance if needed
      4. Store summary for caregiver
```

## Testing and Debugging

### Testing Strategies

#### 1. Test Frequently

> "Review your agent regularly - LLM behavior can change with model updates"

**Testing Checklist:**
- Test after every prompt change
- Test with different phrasings
- Test edge cases
- Test failure scenarios
- Test with real phone calls (not just webhooks)

#### 2. Test with Different Voices

**Variables to test:**
- Different accents
- Different speech patterns
- Background noise
- Poor audio quality
- Mumbling/unclear speech

### Common Issues and Solutions

#### Issue: AI Not Calling Functions

**Symptoms:**
- Function never triggers
- AI tries to answer without data

**Solutions:**
1. Make function purpose clearer
2. Explicitly mention function in prompt
3. Reduce prompt complexity
4. Test function independently with webhook.site

#### Issue: AI Hallucinating Information

**Symptoms:**
- AI provides incorrect data
- Makes up information

**Solutions:**
1. Use SWAIG functions for all data lookup
2. Add explicit negating statements:
   ```
   If you don't know something, say "I don't have that information"
   You only know information provided through functions
   ```
3. Use DataSphere for knowledge base
4. Reduce temperature/top_p settings

#### Issue: Loop Detection Triggering Too Soon

**Symptoms:**
- Call ends after valid attempts
- Users disconnected prematurely

**Solutions:**
```yaml
# Increase loop threshold in your SWML
- condition:
    if: "{{loop}} > 5"  # Was 2
```

## Production Tips

### 1. Start Simple, Iterate Constantly

- Begin with minimal functionality
- Add features incrementally
- Test after each addition
- Track what works in version control

### 2. Monitor Post-Prompt Data

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
        "action_items": []
      }
```

Use this data to:
- Track success rates
- Identify problem areas
- Tune prompts
- Measure customer satisfaction

### 3. A/B Testing Prompts

- Test two prompt variations
- Compare success rates
- Iterate on winner
- Document results

### 4. Graceful Degradation

```yaml
ai:
  prompt: "Your instructions"
  params:
    ai_model: "gpt-4o-mini"
    fallback_model: "gpt-4.0-mini"
    max_retries: 3
```

**Current Architecture:**
- Primary: OpenAI API
- Fallback: Azure OpenAI
- Automatic failover in development

## Performance Metrics

**Latency Targets:**
- Average response time: ~500ms
- P95 response time: <1s
- Function execution: <2s

**Quality Metrics:**
- Call completion rate
- Function success rate
- Transfer success rate
- Customer satisfaction

**Operational Efficiency:**
- Includes ASR, TTS, and LLM in single service
- No infrastructure to manage or maintain
- Automatic scaling and load balancing

## Next Steps

- [Fabric & Relay](fabric-relay.md) - Real-time agent control
- [Webhooks & Events](webhooks-events.md) - Track AI interactions
- [Call Control](call-control.md) - Integrate AI with call features
