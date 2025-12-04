# SWAIG Functions Reference

SWAIG (SignalWire AI Gateway) functions are tools the AI can call during conversation. This reference covers all aspects of defining and implementing SWAIG functions.

## Overview

SWAIG functions allow your agent to:
- Look up external data (orders, accounts, weather)
- Perform actions (transfer calls, send SMS, update records)
- Control conversation flow (end call, change context)
- Integrate with external APIs and services

## Definition Methods

### Method 1: @AgentBase.tool Decorator (Recommended)

The decorator approach is cleaner and keeps the function definition with its implementation.

```python
from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult


class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="my-agent")
        self.add_language("English", "en-US", "rime.spore")

    @AgentBase.tool(
        name="get_weather",
        description="Get the current weather for a city",
        parameters={
            "city": {
                "type": "string",
                "description": "The city name"
            },
            "units": {
                "type": "string",
                "description": "Temperature units",
                "enum": ["fahrenheit", "celsius"],
                "default": "fahrenheit"
            }
        }
    )
    def get_weather(self, args, raw_data):
        city = args.get("city")
        units = args.get("units", "fahrenheit")
        # Implementation here
        return SwaigFunctionResult(f"Weather in {city}: 72°F and sunny")
```

### Method 2: define_tool() (Imperative)

Use this when you need to dynamically define functions or separate definition from implementation.

```python
class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="my-agent")
        self.add_language("English", "en-US", "rime.spore")

        self.define_tool(
            name="get_weather",
            description="Get the current weather for a city",
            parameters={
                "city": {
                    "type": "string",
                    "description": "The city name"
                }
            },
            handler=self.handle_weather
        )

    def handle_weather(self, args, raw_data):
        city = args.get("city")
        return SwaigFunctionResult(f"Weather in {city}: 72°F")
```

### Method 3: DataMap (Server-Side)

For functions that simply call an external API without custom logic.

```python
from signalwire_agents.core.data_map import DataMap

weather_map = (DataMap("get_weather")
    .purpose("Get current weather for a location")
    .parameter("city", "string", "City name", required=True)
    .webhook("GET", "https://api.weather.com/v1/current?q=${args.city}&key=API_KEY")
    .output(SwaigFunctionResult("Weather in ${args.city}: ${response.temp}°F"))
)

agent.register_swaig_function(weather_map.to_swaig_function())
```

## Handler Signature

All function handlers must follow this signature:

```python
def handler(self, args: dict, raw_data: dict) -> SwaigFunctionResult:
    pass
```

### The `args` Parameter

Contains the parameters the AI passed to the function:

```python
def handle_order_lookup(self, args, raw_data):
    order_id = args.get("order_id")           # Required param
    include_items = args.get("include_items", False)  # Optional with default
```

### The `raw_data` Parameter

Contains the full request context:

```python
{
    "call_id": "unique-call-identifier",
    "call": {
        "from": "+15551234567",
        "to": "+15559876543",
        "direction": "inbound"
    },
    "vars": {
        # Global data and conversation state
    },
    "conversation_id": "conv-123",
    "function": "function_name",
    "argument": {
        "parsed": [...],  # Parsed arguments
        "raw": "..."      # Raw argument string
    }
}
```

**Accessing call information:**

```python
def handle_function(self, args, raw_data):
    call_id = raw_data.get("call_id")
    caller = raw_data.get("call", {}).get("from", "unknown")
    global_vars = raw_data.get("vars", {})
```

## Parameter Schema

Parameters use JSON Schema format:

### Basic Types

```python
parameters={
    "name": {
        "type": "string",
        "description": "Customer name"
    },
    "age": {
        "type": "integer",
        "description": "Customer age"
    },
    "amount": {
        "type": "number",
        "description": "Transaction amount"
    },
    "confirmed": {
        "type": "boolean",
        "description": "Whether the action is confirmed"
    }
}
```

### Required vs Optional

```python
parameters={
    "order_id": {
        "type": "string",
        "description": "Order ID (required)"
        # No default = required
    },
    "include_items": {
        "type": "boolean",
        "description": "Include line items",
        "default": False  # Has default = optional
    }
}
```

### Enum (Fixed Options)

```python
parameters={
    "department": {
        "type": "string",
        "description": "Department to transfer to",
        "enum": ["sales", "support", "billing", "technical"]
    },
    "priority": {
        "type": "string",
        "description": "Ticket priority",
        "enum": ["low", "medium", "high", "urgent"],
        "default": "medium"
    }
}
```

### Arrays

```python
parameters={
    "items": {
        "type": "array",
        "description": "List of item IDs",
        "items": {
            "type": "string"
        }
    }
}
```

### Nested Objects

```python
parameters={
    "address": {
        "type": "object",
        "description": "Shipping address",
        "properties": {
            "street": {"type": "string"},
            "city": {"type": "string"},
            "state": {"type": "string"},
            "zip": {"type": "string"}
        }
    }
}
```

## Function Options

### Fillers

Phrases the AI says while the function executes:

```python
@AgentBase.tool(
    name="lookup_account",
    description="Look up account information",
    parameters={"account_id": {"type": "string", "description": "Account ID"}},
    fillers=[
        "Let me look that up for you",
        "One moment please",
        "Checking our records"
    ]
)
def lookup_account(self, args, raw_data):
    # Long-running operation
    pass
```

### Wait File

Audio file to play while processing:

```python
@AgentBase.tool(
    name="process_payment",
    description="Process a payment",
    parameters={"amount": {"type": "number", "description": "Amount"}},
    wait_file="https://example.com/hold-music.mp3",
    wait_file_loops=3  # Loop 3 times
)
def process_payment(self, args, raw_data):
    # Long-running payment processing
    pass
```

### Secure Functions

Require token validation for sensitive operations:

```python
@AgentBase.tool(
    name="delete_account",
    description="Delete a customer account (irreversible)",
    parameters={"account_id": {"type": "string", "description": "Account ID"}},
    secure=True
)
def delete_account(self, args, raw_data):
    # Token is automatically validated by the framework
    account_id = args.get("account_id")
    # Perform deletion
    return SwaigFunctionResult(f"Account {account_id} deleted")
```

## Common Patterns

### Simple Data Lookup

```python
@AgentBase.tool(
    name="get_order_status",
    description="Get the status of an order by order number",
    parameters={
        "order_number": {
            "type": "string",
            "description": "The order number (e.g., ORD-12345)"
        }
    }
)
def get_order_status(self, args, raw_data):
    order_num = args.get("order_number")

    # Query your database/API
    status = self.db.get_order_status(order_num)

    if status:
        return SwaigFunctionResult(
            f"Order {order_num} is {status['state']}. "
            f"Expected delivery: {status['delivery_date']}"
        )
    else:
        return SwaigFunctionResult(
            f"I couldn't find order {order_num}. "
            "Please check the number and try again."
        )
```

### Action with Confirmation

```python
@AgentBase.tool(
    name="cancel_order",
    description="Cancel an existing order",
    parameters={
        "order_number": {
            "type": "string",
            "description": "Order number to cancel"
        },
        "confirmed": {
            "type": "boolean",
            "description": "Customer confirmed cancellation",
            "default": False
        }
    }
)
def cancel_order(self, args, raw_data):
    order_num = args.get("order_number")
    confirmed = args.get("confirmed", False)

    if not confirmed:
        return SwaigFunctionResult(
            f"Are you sure you want to cancel order {order_num}? "
            "This cannot be undone. Please confirm."
        )

    # Perform cancellation
    self.db.cancel_order(order_num)
    return SwaigFunctionResult(
        f"Order {order_num} has been cancelled. "
        "You'll receive a confirmation email shortly."
    )
```

### Call Transfer

```python
@AgentBase.tool(
    name="transfer_to_agent",
    description="Transfer the call to a human agent",
    parameters={
        "department": {
            "type": "string",
            "description": "Department to transfer to",
            "enum": ["sales", "support", "billing"]
        },
        "reason": {
            "type": "string",
            "description": "Reason for transfer"
        }
    }
)
def transfer_to_agent(self, args, raw_data):
    dept = args.get("department", "support")
    reason = args.get("reason", "Customer requested transfer")

    destinations = {
        "sales": "sip:sales@company.com",
        "support": "sip:support@company.com",
        "billing": "tel:+15551234567"
    }

    return (SwaigFunctionResult(
        f"I'll transfer you to our {dept} team now. "
        "Please hold while I connect you."
    ).add_action("transfer", {"dest": destinations[dept]}))
```

### Conditional Function Enabling

```python
@AgentBase.tool(
    name="verify_identity",
    description="Verify customer identity with PIN",
    parameters={
        "pin": {
            "type": "string",
            "description": "4-digit PIN"
        }
    }
)
def verify_identity(self, args, raw_data):
    pin = args.get("pin")
    caller = raw_data.get("call", {}).get("from")

    if self.verify_pin(caller, pin):
        # Enable secure functions after verification
        return (SwaigFunctionResult("Identity verified. How can I help you?")
            .add_action("toggle_functions", {
                "active": ["view_balance", "transfer_funds", "update_address"]
            }))
    else:
        return SwaigFunctionResult(
            "That PIN doesn't match our records. Please try again."
        )
```

### Setting Conversation State

```python
@AgentBase.tool(
    name="set_customer_context",
    description="Store customer information for the conversation",
    parameters={
        "customer_id": {"type": "string", "description": "Customer ID"},
        "name": {"type": "string", "description": "Customer name"}
    }
)
def set_customer_context(self, args, raw_data):
    customer_id = args.get("customer_id")
    name = args.get("name")

    return (SwaigFunctionResult(f"Hello {name}, how can I help you today?")
        .add_action("set_global_data", {
            "customer_id": customer_id,
            "customer_name": name,
            "verified": True
        }))
```

## Error Handling

### Graceful Error Messages

```python
@AgentBase.tool(
    name="get_account_balance",
    description="Get account balance",
    parameters={"account_id": {"type": "string", "description": "Account ID"}}
)
def get_account_balance(self, args, raw_data):
    account_id = args.get("account_id")

    try:
        balance = self.api.get_balance(account_id)
        return SwaigFunctionResult(f"Your current balance is ${balance:.2f}")

    except AccountNotFoundError:
        return SwaigFunctionResult(
            "I couldn't find that account. "
            "Can you verify the account number?"
        )

    except APIError as e:
        # Log the error internally
        self.log.error("api_error", error=str(e), account_id=account_id)
        # Give user-friendly message
        return SwaigFunctionResult(
            "I'm having trouble accessing account information right now. "
            "Let me transfer you to someone who can help."
        ).add_action("transfer", {"dest": "sip:support@company.com"})
```

### Validation

```python
@AgentBase.tool(
    name="schedule_appointment",
    description="Schedule an appointment",
    parameters={
        "date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
        "time": {"type": "string", "description": "Time (HH:MM)"}
    }
)
def schedule_appointment(self, args, raw_data):
    date_str = args.get("date")
    time_str = args.get("time")

    # Validate date format
    try:
        from datetime import datetime
        apt_date = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        return SwaigFunctionResult(
            "I didn't understand that date and time. "
            "Could you say it like 'January 15th at 2 PM'?"
        )

    # Check if in the past
    if apt_date < datetime.now():
        return SwaigFunctionResult(
            "That time has already passed. "
            "When would you like to reschedule?"
        )

    # Check availability
    if not self.calendar.is_available(apt_date):
        alternatives = self.calendar.get_alternatives(apt_date)
        return SwaigFunctionResult(
            f"That slot isn't available. "
            f"How about {alternatives[0]} or {alternatives[1]}?"
        )

    # Book it
    self.calendar.book(apt_date)
    return SwaigFunctionResult(
        f"I've scheduled your appointment for {apt_date.strftime('%B %d at %I:%M %p')}. "
        "You'll receive a confirmation shortly."
    )
```

## Best Practices

### 1. Clear Descriptions

The description is how the AI knows when to call your function.

**Good:**
```python
description="Look up the status and tracking information for an order using the order number"
```

**Bad:**
```python
description="Get order"
```

### 2. Specific Parameter Descriptions

```python
# Good
"order_number": {
    "type": "string",
    "description": "The order number, typically starting with ORD- followed by numbers"
}

# Bad
"order_number": {
    "type": "string",
    "description": "Order number"
}
```

### 3. Return Conversational Responses

```python
# Good
return SwaigFunctionResult(
    "Your order shipped yesterday via FedEx. "
    "The tracking number is 1234567890. "
    "Would you like me to text you the tracking link?"
)

# Bad
return SwaigFunctionResult("shipped")
```

### 4. Handle Missing Parameters

```python
def handle_function(self, args, raw_data):
    required_param = args.get("required_param")
    if not required_param:
        return SwaigFunctionResult(
            "I need the order number to look that up. "
            "What's your order number?"
        )
```

### 5. Use Appropriate Actions

```python
# End conversation cleanly
return SwaigFunctionResult("Thank you for calling!").add_action("hangup", {})

# Transfer with context
return SwaigFunctionResult("Connecting you now...").add_action(
    "transfer", {"dest": "sip:agent@company.com"}
)

# Update state for future reference
return SwaigFunctionResult("I've noted that.").add_action(
    "set_global_data", {"preference": "email"}
)
```
