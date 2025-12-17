# SwaigFunctionResult Reference

`SwaigFunctionResult` is the return type for all SWAIG function handlers. It encapsulates the response text and any actions to execute.

## Import

```python
from signalwire_agents.core.function_result import SwaigFunctionResult
```

## Constructor

```python
SwaigFunctionResult(
    response: str = None,
    post_process: bool = False
)
```

**Parameters:**
- `response` - Text the AI will speak to the user
- `post_process` - If `True`, AI responds before actions execute; if `False`, actions execute immediately

## Basic Usage

### Simple Response

```python
return SwaigFunctionResult("The weather in Seattle is 65°F and cloudy.")
```

### Response with Action

```python
return SwaigFunctionResult("I'll transfer you now.").add_action(
    "transfer", {"dest": "tel:+15551234567"}
)
```

### Multiple Actions

```python
return (SwaigFunctionResult("Let me set that up for you.")
    .add_action("set_global_data", {"customer_verified": True})
    .add_action("toggle_functions", {"active": ["view_balance", "transfer"]}))
```

### Post-Process Mode

When `post_process=True`, the AI delivers the response BEFORE actions execute:

```python
# AI says goodbye, THEN hangs up
return SwaigFunctionResult(
    "Thank you for calling! Goodbye.",
    post_process=True
).add_action("hangup", {})
```

Without `post_process`, actions execute immediately and may interrupt:

```python
# Hangup might occur before AI finishes speaking
return SwaigFunctionResult("Thank you for calling!").add_action("hangup", {})
```

## Methods

### set_response()

Set or update the response text.

```python
result = SwaigFunctionResult()
result.set_response("Here's the information you requested.")
return result
```

### add_action()

Add a single action.

```python
def add_action(self, action_name: str, action_data: dict) -> 'SwaigFunctionResult'
```

Returns self for method chaining.

```python
return (SwaigFunctionResult("Transferring...")
    .add_action("transfer", {"dest": "sip:support@company.com"}))
```

### add_actions()

Add multiple actions at once.

```python
def add_actions(self, actions: list) -> 'SwaigFunctionResult'
```

```python
return SwaigFunctionResult("Setting up your account.").add_actions([
    {"set_global_data": {"account_id": "12345", "verified": True}},
    {"toggle_functions": {"active": ["view_balance"]}}
])
```

### connect() (Convenience Method)

Shorthand for transfer action.

```python
def connect(self, dest: str, final: bool = True) -> 'SwaigFunctionResult'
```

```python
return SwaigFunctionResult("Connecting you to sales.").connect(
    "sip:sales@company.com",
    final=True
)
```

## Action Reference

### transfer

Transfer the call to another destination.

```python
.add_action("transfer", {
    "dest": "tel:+15551234567"  # Phone number
})

.add_action("transfer", {
    "dest": "sip:user@domain.com"  # SIP address
})
```

### hangup

End the call.

```python
.add_action("hangup", {})

.add_action("hangup", {
    "reason": "customer_request"  # Optional reason
})
```

### play

Play an audio file.

```python
# Single file
.add_action("play", {
    "url": "https://example.com/audio.mp3"
})

# Multiple files in sequence
.add_action("play", {
    "urls": [
        "https://example.com/greeting.mp3",
        "https://example.com/menu.mp3"
    ]
})

# Text-to-speech
.add_action("play", {
    "url": "say:Thank you for your patience."
})
```

### set_global_data

Update conversation state accessible to the AI.

```python
.add_action("set_global_data", {
    "customer_id": "12345",
    "customer_name": "John Smith",
    "verified": True,
    "preferences": {
        "contact_method": "email"
    }
})
```

The AI can reference this data in subsequent turns.

### toggle_functions

Enable or disable functions dynamically.

```python
# Activate specific functions
.add_action("toggle_functions", {
    "active": ["transfer_funds", "view_transactions"]
})

# Deactivate specific functions
.add_action("toggle_functions", {
    "inactive": ["delete_account"]
})

# Both at once
.add_action("toggle_functions", {
    "active": ["view_balance"],
    "inactive": ["transfer_funds"]
})
```

### playback_bg

Start background audio (e.g., hold music).

```python
.add_action("playback_bg", {
    "file": "https://example.com/hold-music.mp3",
    "wait": True  # Wait for audio to finish
})
```

### stop_playback_bg

Stop background audio.

```python
.add_action("stop_playback_bg", {})
```

### send_sms

Send an SMS message.

```python
.add_action("send_sms", {
    "to": "+15551234567",
    "from": "+15559876543",
    "body": "Your verification code is 123456"
})
```

### send_mms

Send an MMS message with media.

```python
.add_action("send_mms", {
    "to": "+15551234567",
    "from": "+15559876543",
    "body": "Here's your receipt",
    "media": ["https://example.com/receipt.pdf"]
})
```

### user_input

Request specific input from the user.

```python
.add_action("user_input", {
    "type": "digits",
    "num_digits": 4,
    "speech": "Please enter your 4-digit PIN."
})
```

### context_switch

Switch to a different conversation context.

```python
.add_action("context_switch", {
    "context": "verification",
    "data": {"attempt": 1}
})
```

### swml

Execute arbitrary SWML.

```python
.add_action("swml", {
    "sections": {
        "main": [
            {"play": {"url": "https://example.com/audio.mp3"}},
            {"hangup": {}}
        ]
    }
})
```

## Common Patterns

### Lookup and Respond

```python
@AgentBase.tool(
    name="get_balance",
    description="Get account balance",
    parameters={"account_id": {"type": "string", "description": "Account ID"}}
)
def get_balance(self, args, raw_data):
    account_id = args.get("account_id")
    balance = self.db.get_balance(account_id)

    return SwaigFunctionResult(
        f"Your current balance is ${balance:.2f}. "
        "Would you like to make a payment?"
    )
```

### Transfer with Context

```python
@AgentBase.tool(
    name="escalate",
    description="Transfer to human agent",
    parameters={
        "reason": {"type": "string", "description": "Reason for transfer"}
    }
)
def escalate(self, args, raw_data):
    reason = args.get("reason", "Customer requested transfer")

    # Store context for the human agent
    return (SwaigFunctionResult(
        "I'll connect you with a specialist who can help. "
        "Please hold for a moment."
    )
    .add_action("set_global_data", {"transfer_reason": reason})
    .add_action("transfer", {"dest": "sip:support@company.com"}))
```

### Conditional Actions

```python
@AgentBase.tool(
    name="process_request",
    description="Process customer request",
    parameters={
        "request_type": {"type": "string", "description": "Type of request"}
    }
)
def process_request(self, args, raw_data):
    request_type = args.get("request_type")

    result = SwaigFunctionResult()

    if request_type == "cancel":
        result.set_response("Your service has been cancelled.")
        result.add_action("send_sms", {
            "to": raw_data.get("call", {}).get("from"),
            "body": "Your cancellation has been confirmed."
        })

    elif request_type == "upgrade":
        result.set_response("Let me connect you with our sales team.")
        result.add_action("transfer", {"dest": "sip:sales@company.com"})

    else:
        result.set_response("I've noted your request. Is there anything else?")

    return result
```

### Multi-Step Verification

```python
@AgentBase.tool(
    name="verify_pin",
    description="Verify customer PIN",
    parameters={"pin": {"type": "string", "description": "4-digit PIN"}}
)
def verify_pin(self, args, raw_data):
    pin = args.get("pin")
    caller = raw_data.get("call", {}).get("from")

    if self.verify_customer_pin(caller, pin):
        return (SwaigFunctionResult(
            "Thank you, your identity has been verified. "
            "How can I help you today?"
        )
        .add_action("set_global_data", {"verified": True})
        .add_action("toggle_functions", {
            "active": ["view_balance", "transfer_funds", "view_transactions"]
        }))
    else:
        attempts = raw_data.get("vars", {}).get("pin_attempts", 0) + 1

        if attempts >= 3:
            return (SwaigFunctionResult(
                "Too many incorrect attempts. "
                "For your security, I'll connect you with an agent."
            )
            .add_action("transfer", {"dest": "sip:security@company.com"}))

        return (SwaigFunctionResult(
            f"That PIN doesn't match. You have {3 - attempts} attempts remaining. "
            "Please try again."
        )
        .add_action("set_global_data", {"pin_attempts": attempts}))
```

### Graceful Call Ending

```python
@AgentBase.tool(
    name="end_call",
    description="End the conversation politely",
    parameters={}
)
def end_call(self, args, raw_data):
    return SwaigFunctionResult(
        "Thank you for calling! Have a great day. Goodbye!",
        post_process=True  # Let AI finish speaking before hangup
    ).add_action("hangup", {})
```

### Background Music During Processing

```python
@AgentBase.tool(
    name="long_operation",
    description="Perform a long-running operation",
    parameters={"data": {"type": "string", "description": "Data to process"}}
)
def long_operation(self, args, raw_data):
    # Start hold music
    result = SwaigFunctionResult("Please hold while I process that.")
    result.add_action("playback_bg", {
        "file": "https://example.com/hold-music.mp3"
    })

    # Do the work (in real implementation, this would be async)
    processed = self.process_data(args.get("data"))

    # Stop music and respond
    result.add_action("stop_playback_bg", {})
    result.set_response(f"All done! {processed}")

    return result
```

## Serialization

`SwaigFunctionResult` serializes to JSON for the SWAIG protocol:

```python
result = (SwaigFunctionResult("Hello!")
    .add_action("set_global_data", {"greeted": True}))

# Serializes to:
{
    "response": "Hello!",
    "action": [
        {"set_global_data": {"greeted": True}}
    ]
}
```

With post_process:

```python
result = SwaigFunctionResult("Goodbye!", post_process=True).add_action("hangup", {})

# Serializes to:
{
    "response": "Goodbye!",
    "action": [
        {"SWML": {"sections": {"main": [{"ai": {"post_prompt": ...}}]}}},
        {"hangup": {}}
    ]
}
```

## Best Practices

1. **Always provide a response** - Even for action-only results, give the user feedback
2. **Use post_process for goodbyes** - Ensures the AI finishes speaking before hangup
3. **Chain actions logically** - Actions execute in order, plan accordingly
4. **Keep responses conversational** - The response becomes the AI's speech
5. **Handle errors gracefully** - Return helpful error messages, not exceptions
