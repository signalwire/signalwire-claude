# AI Agent Functions

## Overview

Build powerful SWAIG (SignalWire AI Gateway) functions that extend your AI agents with external data, business logic, and call control. This guide covers function patterns, metadata usage, and advanced techniques.

## Related Workflows

- [Voice AI](voice-ai.md) - Overview and decision guide
- [AI Agent SDK Basics](ai-agent-sdk-basics.md) - Python SDK fundamentals
- [AI Agent Prompting](ai-agent-prompting.md) - Best practices for prompts
- [AI Agent Deployment](ai-agent-deployment.md) - Production deployment
- [Webhooks & Events](webhooks-events.md) - Testing with webhook.site

## SWAIG Basics

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

## Function Definition Patterns

### Pattern 1: SDK Tool Decorator

```python
from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult

class MyAgent(AgentBase):
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
```

### Pattern 2: SWML Function Metadata

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

### Pattern 3: Flask SWAIG Endpoint

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

## SwaigFunctionResult Actions

Return SWML actions from functions to control the call:

### Basic Response

```python
return SwaigFunctionResult("The weather in Seattle is sunny and 72°F")
```

### Response with Play Action

```python
result = SwaigFunctionResult("Please hold while I transfer you")
result.add_action("play", {"url": "https://example.com/hold-music.mp3"})
return result
```

### Response with Transfer

```python
result = SwaigFunctionResult("Transferring you to sales now")
result.add_action("play", {"url": "say:Please hold"})
result.add_action("transfer", {"dest": "tel:+15551234567"})
return result
```

### Chained Actions (Fluent API)

```python
return (SwaigFunctionResult("Processing your payment")
    .add_action("play", {"url": "https://example.com/processing.mp3"})
    .add_action("hangup", {}))
```

### Common Actions

**play** - Play audio:
```python
result.add_action("play", {"url": "say:Please wait"})
result.add_action("play", {"url": "https://example.com/audio.mp3"})
result.add_action("play", {"url": "silence:2.0"})  # 2 seconds of silence
```

**transfer** - Transfer call:
```python
result.add_action("transfer", {"dest": "tel:+15551234567"})
result.add_action("transfer", {"dest": "sip:agent@example.com"})
```

**hangup** - End call:
```python
result.add_action("hangup", {})
```

**set_meta_data** - Store metadata:
```python
result.add_action("set_meta_data", {
    "customer_verified": True,
    "account_id": "12345"
})
```

**toggle_functions** - Enable/disable functions:
```python
# Disable after use
result.add_action("toggle_functions", {
    "active": False,
    "functions": ["send_verification_code"]
})

# Enable functions
result.add_action("toggle_functions", {
    "active": True,
    "functions": ["process_payment"]
})
```

For complete action reference, see: [reference/sdk/function-result.md](../reference/sdk/function-result.md)

## Progressive Knowledge Building

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

**Python SDK version:**

```python
class SupportAgent(AgentBase):
    def __init__(self):
        super().__init__(name="support")
        self.session_data = {}

    @AgentBase.tool(
        name="list_tickets",
        description="List open support tickets",
        parameters={}
    )
    def list_tickets(self, args, raw_data):
        # Get tickets from database
        tickets = database.get_tickets(user_id=self.session_data.get('user_id'))
        ticket_numbers = [t['number'] for t in tickets]

        # Store in session for later use
        self.session_data['open_tickets'] = ticket_numbers

        return (SwaigFunctionResult(f"You have {len(tickets)} open tickets: {', '.join(ticket_numbers)}")
            .add_action("set_meta_data", {"open_tickets": ticket_numbers}))

    @AgentBase.tool(
        name="close_ticket",
        description="Close a support ticket",
        parameters={
            "ticket_number": {"type": "string", "description": "Ticket number to close"}
        }
    )
    def close_ticket(self, args, raw_data):
        ticket_number = args.get("ticket_number")

        # Verify ticket exists in session
        if ticket_number not in self.session_data.get('open_tickets', []):
            return SwaigFunctionResult("That ticket number doesn't exist or is already closed.")

        # Close ticket
        database.close_ticket(ticket_number)

        return SwaigFunctionResult(f"Ticket {ticket_number} has been closed.")
```

**Use cases:**
- Session state
- Authentication tokens
- Previous interactions
- Conditional permissions

## Metadata for Security

**Critical Pattern:** Keep sensitive data OUT of the LLM context:

### What to Store in Metadata

- Customer information → metadata
- Payment details → metadata + SWML Pay
- Authentication tokens → metadata
- Account balances → metadata

SWAIG functions can access metadata, but AI cannot see it directly.

### Example: Secure Authentication

```python
@AgentBase.tool(
    name="verify_customer",
    description="Verify customer identity",
    parameters={
        "account_number": {"type": "string", "description": "Account number"},
        "pin": {"type": "string", "description": "4-digit PIN"}
    }
)
def verify_customer(self, args, raw_data):
    account_number = args.get("account_number")
    pin = args.get("pin")

    # Verify credentials
    customer = database.verify(account_number, pin)

    if customer:
        # Store sensitive data in metadata (NOT visible to AI)
        return (SwaigFunctionResult("Identity verified. How can I help you?")
            .add_action("set_meta_data", {
                "verified": True,
                "customer_id": customer['id'],
                "account_balance": customer['balance'],
                "customer_tier": customer['tier']
            }))
    else:
        return SwaigFunctionResult("I couldn't verify your identity. Please try again.")

@AgentBase.tool(
    name="get_balance",
    description="Get current account balance",
    parameters={}
)
def get_balance(self, args, raw_data):
    # Access metadata from raw_data
    meta = raw_data.get('meta_data', {})

    if not meta.get('verified'):
        return SwaigFunctionResult("Please verify your identity first.")

    # Balance is in metadata, not passed through AI
    balance = meta.get('account_balance')
    return SwaigFunctionResult(f"Your current balance is ${balance:.2f}")
```

### Metadata Token for Scoped Access

```yaml
functions:
  - name: payment_function
    metadata_token: "payments_only"
  - name: account_lookup
    metadata_token: "general"
```

Functions can only access metadata matching their token.

## DataMap - Server-Side Functions

For functions that don't need local processing, use DataMap to call external APIs directly:

### Weather Lookup via API

```python
from signalwire_agents.core.data_map import DataMap

# Weather lookup via API
weather_func = (DataMap("get_weather")
    .purpose("Get current weather for a city")
    .parameter("city", "string", "City name", required=True)
    .webhook("GET", "https://api.weather.com/v1/current?q=${args.city}&key=API_KEY")
    .output(SwaigFunctionResult(
        "The weather in ${args.city} is ${response.condition} "
        "and ${response.temp_f}°F"
    ))
)

agent.register_swaig_function(weather_func.to_swaig_function())
```

### Pattern-Based Responses with Expressions

```python
# Playback control without API calls
playback_control = (DataMap("control_playback")
    .purpose("Control audio playback - start or stop")
    .parameter("command", "string", "The command: 'start' or 'stop'", required=True)
    .parameter("filename", "string", "Audio file to play", required=False)

    .expression(
        "${args.command}",
        r"start.*",
        SwaigFunctionResult("Starting playback").add_action(
            "playback_bg", {"file": "${args.filename}"}
        )
    )

    .expression(
        "${args.command}",
        r"stop.*",
        SwaigFunctionResult("Stopping playback").add_action(
            "stop_playback_bg", {}
        )
    )
)
```

For advanced DataMap features (array processing, webhooks with fallbacks), see: [reference/sdk/datamap-advanced.md](../reference/sdk/datamap-advanced.md)

## Function Chaining

Execute multiple functions in sequence:

```python
@AgentBase.tool(
    name="book_appointment",
    description="Book an appointment",
    parameters={
        "date": {"type": "string", "description": "Appointment date"},
        "time": {"type": "string", "description": "Appointment time"}
    }
)
def book_appointment(self, args, raw_data):
    date = args.get("date")
    time = args.get("time")

    # Book appointment
    appointment_id = database.create_appointment(date, time)

    # Return response and enable confirmation function
    return (SwaigFunctionResult(f"I've reserved {date} at {time} for you.")
        .add_action("set_meta_data", {"appointment_id": appointment_id})
        .add_action("toggle_functions", {
            "active": True,
            "functions": ["confirm_appointment", "cancel_appointment"]
        }))

@AgentBase.tool(
    name="confirm_appointment",
    description="Confirm the booked appointment",
    parameters={}
)
def confirm_appointment(self, args, raw_data):
    meta = raw_data.get('meta_data', {})
    appointment_id = meta.get('appointment_id')

    database.confirm_appointment(appointment_id)

    # Disable both functions after confirmation
    return (SwaigFunctionResult("Your appointment is confirmed. You'll receive a reminder 24 hours before.")
        .add_action("toggle_functions", {
            "active": False,
            "functions": ["confirm_appointment", "cancel_appointment"]
        }))
```

## Common Function Patterns

### Pattern 1: Multi-Factor Authentication

```python
@AgentBase.tool(
    name="send_verification_code",
    description="Send a verification code to the customer",
    parameters={}
)
def send_verification_code(self, args, raw_data):
    meta = raw_data.get('meta_data', {})
    phone = meta.get('from')

    # Generate and send code
    code = generate_code()
    send_sms(phone, f"Your verification code is {code}")

    # Store code in session (not metadata - AI doesn't need it)
    self.session_data['verification_code'] = code
    self.session_data['code_expiry'] = time.time() + 300  # 5 minutes

    # Disable this function, enable verify function
    return (SwaigFunctionResult("I've sent a verification code to your phone.")
        .add_action("toggle_functions", {
            "active": False,
            "functions": ["send_verification_code"]
        })
        .add_action("toggle_functions", {
            "active": True,
            "functions": ["verify_code"]
        }))

@AgentBase.tool(
    name="verify_code",
    description="Verify the code provided by the customer",
    parameters={
        "code": {"type": "string", "description": "6-digit verification code"}
    }
)
def verify_code(self, args, raw_data):
    provided_code = args.get("code")
    stored_code = self.session_data.get('verification_code')
    expiry = self.session_data.get('code_expiry', 0)

    # Check expiration
    if time.time() > expiry:
        return SwaigFunctionResult("The code has expired. Please request a new one.")

    # Verify code
    if provided_code == stored_code:
        return (SwaigFunctionResult("Verification successful.")
            .add_action("set_meta_data", {"verified": True})
            .add_action("toggle_functions", {
                "active": False,
                "functions": ["verify_code"]
            }))
    else:
        return SwaigFunctionResult("That code is incorrect. Please try again.")
```

**Best Practices:**
- Store session data in instance variables
- Never echo codes back to user
- Limit verification attempts
- Expire codes after time limit

### Pattern 2: Call Transfer with Context

```python
@AgentBase.tool(
    name="transfer_to_human",
    description="Transfer the call to a human agent in a specific department",
    parameters={
        "department": {
            "type": "string",
            "description": "Department to transfer to",
            "enum": ["sales", "support", "billing"]
        }
    }
)
def transfer_to_human(self, args, raw_data):
    """Transfer call to human agent"""
    department = args.get("department")
    meta = raw_data.get('meta_data', {})

    dept_numbers = {
        'sales': '+15551111111',
        'support': '+15552222222',
        'billing': '+15553333333'
    }

    number = dept_numbers.get(department, '+15550000000')

    # Build context for screen pop
    context = {
        'customer_name': meta.get('customer_name'),
        'issue': meta.get('issue_summary'),
        'call_id': meta.get('call_id')
    }

    # Send context to CRM/screen pop system
    crm.send_screen_pop(number, context)

    # Return SWML action to transfer
    return (SwaigFunctionResult(f"Transferring you to {department or 'a representative'}")
        .add_action("play", {"url": f"say:Please hold while I transfer you to {department or 'our team'}"})
        .add_action("transfer", {"dest": f"tel:{number}"}))
```

**Preserve Context Through Transfers:**
- 72% of customers expect agents to know who they are
- Use SWAIG functions to collect information
- Pass context through metadata and variables
- Implement screen pop for human agents
- Never make customers repeat themselves

### Pattern 3: Database Integration

```python
import sqlite3

class OrderAgent(AgentBase):
    def __init__(self):
        super().__init__(name="order-agent")
        self.db = sqlite3.connect('orders.db')

    @AgentBase.tool(
        name="check_order_status",
        description="Check the status of a customer's order",
        parameters={
            "order_number": {"type": "string", "description": "Order number"}
        }
    )
    def check_order_status(self, args, raw_data):
        order_number = args.get("order_number")

        cursor = self.db.cursor()
        cursor.execute(
            "SELECT status, shipped_date, delivery_date FROM orders WHERE order_number = ?",
            (order_number,)
        )

        result = cursor.fetchone()

        if result:
            status, shipped_date, delivery_date = result
            return SwaigFunctionResult(
                f"Order {order_number} is {status}. "
                f"It shipped on {shipped_date} and will arrive by {delivery_date}."
            )
        else:
            return SwaigFunctionResult(
                f"I couldn't find order {order_number}. Could you double-check the order number?"
            )
```

### Pattern 4: External API Integration

```python
import requests

@AgentBase.tool(
    name="get_stock_price",
    description="Get current stock price",
    parameters={
        "symbol": {"type": "string", "description": "Stock ticker symbol"}
    }
)
def get_stock_price(self, args, raw_data):
    symbol = args.get("symbol").upper()

    try:
        response = requests.get(
            f"https://api.stockmarket.com/v1/quote/{symbol}",
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            price = data['price']
            change = data['change']

            return SwaigFunctionResult(
                f"{symbol} is trading at ${price:.2f}, "
                f"{'up' if change > 0 else 'down'} ${abs(change):.2f} today."
            )
        else:
            return SwaigFunctionResult(f"I couldn't find stock information for {symbol}.")

    except Exception as e:
        logging.error(f"Stock API error: {e}")
        return SwaigFunctionResult("I'm having trouble accessing stock prices right now.")
```

### Pattern 5: Error Handling

```python
@AgentBase.tool(
    name="lookup_order",
    description="Look up order status",
    parameters={
        "order_number": {"type": "string", "description": "Order number"}
    }
)
def lookup_order(self, args, raw_data):
    """Look up order status"""
    try:
        order_number = args.get("order_number")
        order = self.database.get_order(order_number)

        if order:
            return SwaigFunctionResult(f"Order {order_number} is {order.status}")
        else:
            return SwaigFunctionResult(
                f"I couldn't find order {order_number}. Could you double-check the order number?"
            )

    except Exception as e:
        # Log error but don't expose to user
        logging.error(f"Order lookup error: {e}")
        return SwaigFunctionResult(
            "I'm having trouble accessing the order system. "
            "Let me transfer you to someone who can help."
        )
```

## Testing Functions

### Testing with webhook.site

**For Development:**
1. Get temporary URL from webhook.site
2. Set as function web_hook
3. Inspect payloads in real-time
4. Iterate on implementation

```python
# Use webhook.site for testing SWAIG functions

# 1. Go to webhook.site and get temporary URL
# 2. Configure in SWML:

functions:
  - name: create_ticket
    purpose: "Create support ticket"
    web_hook: "https://webhook.site/unique-id-here"
    parameters:
      - name: title
        type: string
      - name: description
        type: string

# 3. Test AI agent
# 4. View payload in webhook.site
# 5. Iterate on response format
```

**After verifying payload structure:**

```python
@app.route('/swaig/create-ticket', methods=['POST'])
def create_ticket():
    data = request.json

    # data structure verified via webhook.site
    function_name = data.get('function')
    args = data.get('argument', {})

    if function_name == 'create_ticket':
        ticket = github.create_issue(
            title=args.get('title'),
            body=args.get('description')
        )

        return jsonify({
            "response": f"Ticket #{ticket.number} created successfully",
            "metadata": {
                "ticket_id": ticket.number,
                "url": ticket.html_url
            }
        })
```

This is invaluable for debugging SWAIG function payloads without deploying code.

For more webhook testing patterns, see: [Webhooks & Events](webhooks-events.md)

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

### Context Switching Without Ending Session

**Dynamic Context Switching** - SignalWire's unique capability:

```yaml
- ai:
    prompt: "You are now a sales agent"
    params:
      post_prompt_url: "https://yourserver.com/context-switch"
```

The agent can morph from one role to another without ending the session, reducing call legs and costs.

## Next Steps

- [AI Agent SDK Basics](ai-agent-sdk-basics.md) - Python SDK fundamentals
- [AI Agent Prompting](ai-agent-prompting.md) - Best practices for prompts
- [AI Agent Deployment](ai-agent-deployment.md) - Deploy to production
- [Webhooks & Events](webhooks-events.md) - Testing and debugging
- [Voice AI](voice-ai.md) - Complete overview and examples
