# Common Patterns

Frequently used patterns for SignalWire AI Agents.

## Data Lookup Pattern

Look up information and respond conversationally:

```python
@AgentBase.tool(
    name="lookup_order",
    description="Look up order status by order number",
    parameters={
        "order_number": {
            "type": "string",
            "description": "The order number (e.g., ORD-12345)"
        }
    },
    fillers=["Let me look that up", "One moment please"]
)
def lookup_order(self, args, raw_data):
    order_num = args.get("order_number")

    # Query your data source
    order = self.db.get_order(order_num)

    if order:
        return SwaigFunctionResult(
            f"Order {order_num} was placed on {order['date']}. "
            f"Status: {order['status']}. "
            f"Expected delivery: {order['delivery_date']}. "
            "Is there anything else you'd like to know about this order?"
        )
    else:
        return SwaigFunctionResult(
            f"I couldn't find order {order_num}. "
            "Could you double-check the order number? "
            "It should start with ORD followed by numbers."
        )
```

## Confirmation Pattern

Require explicit confirmation before destructive actions:

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
            "description": "Customer has confirmed cancellation",
            "default": False
        }
    }
)
def cancel_order(self, args, raw_data):
    order_num = args.get("order_number")
    confirmed = args.get("confirmed", False)

    if not confirmed:
        return SwaigFunctionResult(
            f"Just to confirm - you want to cancel order {order_num}? "
            "This action cannot be undone. Please confirm."
        )

    # Perform cancellation
    self.db.cancel_order(order_num)

    return SwaigFunctionResult(
        f"Order {order_num} has been cancelled. "
        "You'll receive a confirmation email shortly. "
        "Is there anything else I can help with?"
    )
```

## Transfer with Context Pattern

Pass conversation context when transferring:

```python
@AgentBase.tool(
    name="transfer_to_agent",
    description="Transfer to a human agent",
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
        "They'll have all the context from our conversation. "
        "Please hold while I connect you."
    )
    .add_action("set_global_data", {
        "transfer_reason": reason,
        "ai_summary": "Customer needs assistance with " + reason
    })
    .add_action("transfer", {"dest": destinations[dept]}))
```

## Progressive Disclosure Pattern

Reveal functions as conversation progresses:

```python
class SecureAgent(AgentBase):
    def __init__(self):
        super().__init__(name="secure-agent")
        self.add_language("English", "en-US", "rime.spore")

        self.prompt_add_section(
            "Role",
            "You are a banking assistant. "
            "Always verify identity before discussing account details."
        )

    @AgentBase.tool(
        name="verify_identity",
        description="Verify customer identity with PIN",
        parameters={
            "pin": {"type": "string", "description": "4-digit PIN"}
        }
    )
    def verify_identity(self, args, raw_data):
        pin = args.get("pin")
        caller = raw_data.get("call", {}).get("from")

        if self.validate_pin(caller, pin):
            return (SwaigFunctionResult(
                "Identity verified. How can I help you today?"
            )
            .add_action("set_global_data", {"verified": True})
            .add_action("toggle_functions", {
                "active": ["get_balance", "transfer_funds", "recent_transactions"]
            }))
        else:
            return SwaigFunctionResult(
                "That PIN doesn't match our records. Please try again."
            )

    @AgentBase.tool(
        name="get_balance",
        description="Get account balance (requires verification)",
        parameters={}
    )
    def get_balance(self, args, raw_data):
        verified = raw_data.get("vars", {}).get("verified", False)
        if not verified:
            return SwaigFunctionResult(
                "I need to verify your identity first. "
                "What's your 4-digit PIN?"
            )
        # Return balance...
```

## Graceful Goodbye Pattern

End calls politely with post_process:

```python
@AgentBase.tool(
    name="end_call",
    description="End the conversation politely when customer is done",
    parameters={}
)
def end_call(self, args, raw_data):
    return SwaigFunctionResult(
        "Thank you for calling! Have a wonderful day. Goodbye!",
        post_process=True  # AI finishes speaking before hangup
    ).add_action("hangup", {})
```

## Hold Music Pattern

Play music during long operations:

```python
@AgentBase.tool(
    name="process_request",
    description="Process a complex request",
    parameters={
        "request_type": {"type": "string", "description": "Type of request"}
    }
)
def process_request(self, args, raw_data):
    request_type = args.get("request_type")

    # Start hold music
    result = SwaigFunctionResult(
        "This will take a moment. Please hold while I process that."
    )
    result.add_action("playback_bg", {
        "file": "https://example.com/hold-music.mp3"
    })

    # Do the work
    outcome = self.do_complex_processing(request_type)

    # Stop music and respond
    result.add_action("stop_playback_bg", {})
    result.set_response(f"All done! {outcome}")

    return result
```

## SMS Follow-up Pattern

Send confirmation via SMS:

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
    caller = raw_data.get("call", {}).get("from")

    # Book the appointment
    confirmation = self.calendar.book(date, time)

    return (SwaigFunctionResult(
        f"Your appointment is confirmed for {date} at {time}. "
        "I'll send you a text message with the details."
    )
    .add_action("send_sms", {
        "to": caller,
        "body": f"Appointment confirmed: {date} at {time}. "
                f"Confirmation #: {confirmation}"
    }))
```

## Multi-Step Flow Pattern

Guide user through a process:

```python
@AgentBase.tool(
    name="start_signup",
    description="Begin the signup process",
    parameters={}
)
def start_signup(self, args, raw_data):
    return (SwaigFunctionResult(
        "Great, let's get you signed up! First, what's your email address?"
    )
    .add_action("set_global_data", {"signup_step": "email"}))

@AgentBase.tool(
    name="collect_email",
    description="Collect email for signup",
    parameters={
        "email": {"type": "string", "description": "Email address"}
    }
)
def collect_email(self, args, raw_data):
    email = args.get("email")
    return (SwaigFunctionResult(
        f"Got it, {email}. Now, what would you like your username to be?"
    )
    .add_action("set_global_data", {
        "signup_step": "username",
        "email": email
    }))

@AgentBase.tool(
    name="collect_username",
    description="Collect username for signup",
    parameters={
        "username": {"type": "string", "description": "Desired username"}
    }
)
def collect_username(self, args, raw_data):
    username = args.get("username")
    email = raw_data.get("vars", {}).get("email")

    # Check availability and create account
    if self.is_username_available(username):
        self.create_account(email, username)
        return SwaigFunctionResult(
            f"Your account is all set up! Your username is {username}. "
            "You'll receive a confirmation email shortly."
        )
    else:
        return SwaigFunctionResult(
            f"Sorry, {username} is already taken. "
            "Can you try a different username?"
        )
```

## Caller Context Pattern

Personalize based on caller information:

```python
def on_swml_request(self, request_data=None, callback_path=None, request=None):
    """Customize agent based on caller."""
    call_data = (request_data or {}).get("call", {})
    caller = call_data.get("from", "")

    # Look up caller in CRM
    customer = self.crm.lookup(caller)

    if customer:
        self.set_global_data({
            "customer_name": customer["name"],
            "customer_tier": customer["tier"],
            "account_id": customer["id"]
        })

        if customer["tier"] == "premium":
            self.prompt_add_section(
                "VIP",
                f"This is {customer['name']}, a premium customer. "
                "Prioritize their requests and offer white-glove service."
            )

        self.prompt_add_section(
            "Customer Context",
            f"Customer name: {customer['name']}\n"
            f"Account ID: {customer['id']}\n"
            f"Last order: {customer.get('last_order', 'None')}"
        )
```

## Fallback Pattern

Handle unrecognized requests gracefully:

```python
@AgentBase.tool(
    name="handle_unknown",
    description="Handle requests the AI cannot fulfill",
    parameters={
        "request_summary": {
            "type": "string",
            "description": "Summary of what the customer asked for"
        }
    }
)
def handle_unknown(self, args, raw_data):
    request = args.get("request_summary", "your request")

    return SwaigFunctionResult(
        f"I'm not able to help with {request} directly, "
        "but I can connect you with someone who can. "
        "Would you like me to transfer you to a specialist?"
    )
```

## Rate Limiting Pattern

Prevent abuse of expensive operations:

```python
class RateLimitedAgent(AgentBase):
    def __init__(self):
        super().__init__(name="rate-limited")
        self._call_counts = {}

    @AgentBase.tool(
        name="expensive_operation",
        description="Perform an expensive operation",
        parameters={}
    )
    def expensive_operation(self, args, raw_data):
        call_id = raw_data.get("call_id")

        # Track calls per conversation
        count = self._call_counts.get(call_id, 0)
        if count >= 3:
            return SwaigFunctionResult(
                "I've already performed this operation several times. "
                "To avoid delays, let me transfer you to an agent "
                "who can help further."
            ).add_action("transfer", {"dest": "sip:support@company.com"})

        self._call_counts[call_id] = count + 1

        # Do the expensive thing
        result = self.do_expensive_thing()
        return SwaigFunctionResult(result)
```

## Appointment Scheduling Pattern

Full appointment booking flow:

```python
@AgentBase.tool(
    name="check_availability",
    description="Check appointment availability",
    parameters={
        "date": {"type": "string", "description": "Requested date"}
    }
)
def check_availability(self, args, raw_data):
    date = args.get("date")
    slots = self.calendar.get_available_slots(date)

    if not slots:
        alternatives = self.calendar.get_next_available()
        return SwaigFunctionResult(
            f"Sorry, we don't have availability on {date}. "
            f"The next available slots are: {', '.join(alternatives)}. "
            "Would any of those work for you?"
        )

    return (SwaigFunctionResult(
        f"We have the following times available on {date}: "
        f"{', '.join(slots)}. Which time works best for you?"
    )
    .add_action("set_global_data", {"requested_date": date}))

@AgentBase.tool(
    name="book_slot",
    description="Book a specific time slot",
    parameters={
        "time": {"type": "string", "description": "Selected time"}
    }
)
def book_slot(self, args, raw_data):
    time = args.get("time")
    date = raw_data.get("vars", {}).get("requested_date")
    caller = raw_data.get("call", {}).get("from")

    confirmation = self.calendar.book(date, time, caller)

    return (SwaigFunctionResult(
        f"You're all set for {date} at {time}. "
        f"Your confirmation number is {confirmation}. "
        "I'll send you a text with the details."
    )
    .add_action("send_sms", {
        "to": caller,
        "body": f"Appointment confirmed: {date} at {time}. "
                f"Confirmation: {confirmation}"
    }))
```
