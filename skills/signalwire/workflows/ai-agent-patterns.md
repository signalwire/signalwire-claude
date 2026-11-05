# Common Patterns

Frequently used patterns for SignalWire AI Agents.

## Code Runs the Agent

Four layers of control. Only the first one depends on the model cooperating:

| Layer | Mechanism |
|-------|-----------|
| Guidance | Prompts and tool descriptions. Probabilistic. |
| Tool scope | Each step lists its own tools. A tool that is not offered cannot be called. |
| Transition scope | `set_valid_steps([])` removes `next_step`. Leave `set_valid_contexts` unset so `change_context` is not offered; an empty list still offers it. |
| Execution authority | The handler checks real state, then commits. The model can ask. Code decides. |

```python
def scoped(step, text, tools):
    """Task and tools. The model cannot change step on its own."""
    return (step.set_text(text)
            .set_functions(tools)          # [] means no user tools
            .set_valid_steps([]))
```

The only way out of a step is a handler that has checked state and then returns `swml_change_step()` or `swml_change_context()`.

Keep truth in a system of record keyed by `call_id`. A confirm takes the revision number of the proposal the caller just heard: a repeat with that revision returns the same record, and a stale revision is refused. Tool handlers receive `(self, args, raw_data)`, and `self` is shared across calls, so writing per-call facts to it leaks one caller into the next call. Read per-call facts from `raw_data` or your store. Per-request agent configuration goes in an `add_per_call_config()` callback. That callback gets its own copy of the SDK-managed configuration. Subclass attributes are shared, so assign new values rather than mutating them.

`params.static_greeting` speaks a fixed disclosure, word for word, before the model says anything. It repeats on every turn until the caller first speaks, including attention timeouts, so a required disclosure can play more than once. Set `params.static_greeting_no_barge` when the caller must not talk over it. Do not leave a required disclosure to the prompt.

`say()` is an action, so it finishes before the next action. Without `post_process`, actions run immediately, so a notice left to the model can be cut off: `say()` first. With `post_process=True`, let the model speak. Use one, not both. `connect(final=True)` runs inline when the call is not from RELAY.

```python
return (
    FunctionResult(
        tool_result="The call is being transferred.",
        tool_prompt="Say nothing more; the notice is playing.",
    )
    .say("I'll connect you now.")
    .connect(host_number, final=True)
)
```

The same `say()` order ends a call when you are not using `post_process`. The goodbye pattern below lets the model speak, then hangs up.

## Seams

Every boundary in the call (recognition, the model, synthesis, a lookup, a handoff) adds latency and a place to fail. Three habits:

- Prefetch lookups when the call arrives, before anyone is waiting on the answer.
- Carry what the caller already said across a handoff, so they don't repeat it.
- Write the failure behavior on purpose: say what happened and what the caller can do next. Otherwise a broken step is silence or a confident wrong answer.

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
    fillers={"en-US": ["Let me look that up", "One moment please"]}
)
def lookup_order(self, args, raw_data):
    order_num = args.get("order_number")

    # Query your data source
    order = self.db.get_order(order_num)

    if order:
        return FunctionResult(
            f"Order {order_num} was placed on {order['date']}. "
            f"Status: {order['status']}. "
            f"Expected delivery: {order['delivery_date']}. "
            "Is there anything else you'd like to know about this order?"
        )
    else:
        return FunctionResult(
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
        return FunctionResult(
            f"Just to confirm - you want to cancel order {order_num}? "
            "This action cannot be undone. Please confirm."
        )

    # Perform cancellation
    self.db.cancel_order(order_num)

    return FunctionResult(
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

    return (FunctionResult(
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
            return (FunctionResult(
                "Identity verified. How can I help you today?"
            )
            .add_action("set_global_data", {"verified": True})
            .add_action("toggle_functions", {
                "active": ["get_balance", "transfer_funds", "recent_transactions"]
            }))
        else:
            return FunctionResult(
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
            return FunctionResult(
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
    return FunctionResult(
        "Thank you for calling! Have a wonderful day. Goodbye!",
        post_process=True  # AI finishes speaking before hangup
    ).add_action("hangup", {})
```

## Slow Reasoning Behind a Tool

Keep the slow reasoning model off the conversation. The fast model stays on the call and calls a SWAIG tool; the tool calls the large model and waits. The large model never holds the microphone.

The acknowledgment is a prompt requirement. On the agent, add a section that tells the model to say, in one sentence, what it is about to look up before it calls the tool.

Per-language `fillers` cover the start of the call. A filler covers the moment a tool call is issued. It does not cover the wait. For the wait, loop `wait_file` with `wait_file_loops=-1`, which plays until the function returns. Omitting `wait_file_loops` plays the file once. A wait script, a nested list inside the per-language filler array, speaks phrases one at a time across the wait. A wait script will not talk over an open `wait_file`, and realtime agents do not support wait scripts.

Put a timeout on the slow call, and keep it well under the platform's 120 s SWAIG webhook limit. A function that outlasts that limit returns an error and its `set_global_data` is lost. The block below is a fragment. `self.billing` and `ask_reasoning_model` are your helpers. `ask_reasoning_model` raises `TimeoutError` when the call exceeds the timeout you pass, and the `except` branch relies on that. If it times out, apologize and offer a fallback: email the explanation, call back, or transfer to a person.

Ask the large model for two or three sentences someone can follow on the phone, plus the data behind them. `global_data` is posted with every later function call, so save a short summary and an id there and keep the full analysis in your own store under that id. The follow-up tool loads the analysis by that id, so later questions do not take another trip to the slow model.

```python
self.prompt_add_section(
    "Slow questions",
    "Before calling explain_bill_increase, say in one sentence "
    "what you are about to look up."
)

@AgentBase.tool(
    name="explain_bill_increase",
    description="Explain why the caller's bill changed",
    parameters={
        "question": {
            "type": "string",
            "description": "What the caller wants explained"
        }
    },
    fillers={
        "en-US": [
            "Just a moment more",
            "Thanks for your patience",
            "Almost there"
        ]
    },
    wait_file="https://example.com/keyboard.mp3",
    wait_file_loops=-1
)
def explain_bill_increase(self, args, raw_data):
    # self.billing and ask_reasoning_model are your helpers.
    # ask_reasoning_model raises TimeoutError when it exceeds timeout.
    invoices = self.billing.recent_invoices(
        raw_data.get("call", {}).get("from")
    )

    question = args.get("question", "why the bill changed")
    try:
        result = self.ask_reasoning_model(
            "Answer in two or three sentences someone can follow on the phone, "
            f"and return the analysis behind them. Question: {question}",
            invoices,
            timeout=45,
        )
    except TimeoutError:
        return FunctionResult(
            "This is taking longer than it should. I can email you the "
            "explanation, call you back, or transfer you to a person now. "
            "Which would you like?"
        ).add_action("set_global_data", {"analysis_status": "timed_out"})

    analysis_id = self.billing.save_analysis(result["analysis"])
    return (FunctionResult(
        f"{result['spoken_summary']} "
        "Want me to go into any part of that?"
    )
    .add_action("set_global_data", {
        "bill_analysis_id": analysis_id,
        "bill_summary": result["spoken_summary"],
        "analysis_status": "done"
    }))

@AgentBase.tool(
    name="get_bill_detail",
    description="Answer a follow-up from the bill analysis already saved on this call",
    parameters={
        "question": {
            "type": "string",
            "description": "The follow-up question"
        }
    }
)
def get_bill_detail(self, args, raw_data):
    analysis_id = (raw_data.get("global_data") or {}).get("bill_analysis_id")
    if not analysis_id:
        return FunctionResult(
            "I don't have that saved; I'll run the full analysis. "
            "Call explain_bill_increase."
        )

    analysis = self.billing.load_analysis(analysis_id)
    question = args.get("question", "that")
    return FunctionResult(
        f"From the saved analysis, answer this in a sentence or two: {question}. "
        f"Analysis: {analysis}"
    )
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

    return (FunctionResult(
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
    return (FunctionResult(
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
    return (FunctionResult(
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
        return FunctionResult(
            f"Your account is all set up! Your username is {username}. "
            "You'll receive a confirmation email shortly."
        )
    else:
        return FunctionResult(
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

    return FunctionResult(
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
            return FunctionResult(
                "I've already performed this operation several times. "
                "To avoid delays, let me transfer you to an agent "
                "who can help further."
            ).add_action("transfer", {"dest": "sip:support@company.com"})

        self._call_counts[call_id] = count + 1

        # Do the expensive thing
        result = self.do_expensive_thing()
        return FunctionResult(result)
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
        return FunctionResult(
            f"Sorry, we don't have availability on {date}. "
            f"The next available slots are: {', '.join(alternatives)}. "
            "Would any of those work for you?"
        )

    return (FunctionResult(
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

    return (FunctionResult(
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
