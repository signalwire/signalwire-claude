# Security Patterns

Best practices for securing SignalWire AI Agents.

## Request Signing

Verifying that SignalWire, and not someone else, sent you a request. This is the mechanism — the metadata and basic-auth patterns further down this file are complements to it, not substitutes.

Docs: `/docs/swml/guides/webhook-security`

*(Not to be confused with `/docs/apis/rest/webhooks/swaig-signature-request`, which is about SWAIG's `get_signature` function-discovery call — a different meaning of "signature" entirely. See [SWAIG Includes](ai-agent-functions.md#swaig-includes--remote-function-discovery).)*

### The mechanics

```
signature = hex( HMAC( signing_key, url + raw_body ) )
```

The `url` is the full path including query string. For call requests, basic auth credentials are stripped before signing; for messaging requests they are included as configured.

| Header | Algorithm | Present on |
|--------|-----------|------------|
| `X-Signalwire-Signature` | HMAC-SHA1, hex | Every signed request |
| `X-Signalwire-SHA256-Signature` | HMAC-SHA256, hex | Call requests only |

Messaging document requests carry the SHA-1 header only.

### What is signed, and what is not

**Signed:** every POST SignalWire makes to fetch a SWML document from a URL you control — the initial fetch, and `execute` or `transfer` operations pointing at external URLs, on both the call and messaging sides.

**Not signed:**

| Request | Protect it with |
|---------|-----------------|
| POST to a SWAIG function's `web_hook_url` | HTTP basic auth in the URL, or a shared secret in a custom `X-` header |
| The conversation summary sent to `post_prompt_url` (when you serve your own SWML) | Same |
| The `request` method during a call | Same |

The messaging counterpart of `request` *does* carry the SHA-1 header. The calling one does not.

### Three things builders get wrong

**1. Hash the exact public-facing URL you configured in the Dashboard.** A proxy that rewrites host or scheme changes the hashed string, and a perfectly valid signature then fails to verify. The docs' own troubleshooting section leads with this, because it is the most common cause.

**2. Keep the raw body.** Verification hashes the bytes, not a re-serialized JSON object. Round-tripping through a JSON parser reorders keys and changes whitespace, and the hash no longer matches. In Express, capture `req.rawBody` *before* the JSON body parser consumes it:

```js
app.use(express.json({
  verify: (req, res, buf) => { req.rawBody = buf.toString('utf8'); }
}));
```

**3. Do not require a signature on every inbound request.** Signatures cover requests *for a SWML document*, not everything a document sends you. An endpoint that rejects unsigned traffic will reject SWAIG function webhooks, `status_url` callbacks, and `request` verb targets — traffic you meant to accept. Gate on signature only where a signature is actually sent.

The docs carry working verification snippets in Node, Python, and Ruby, plus a "confirm your endpoint rejects forgeries" test. Adapt those rather than writing your own HMAC comparison — and use a constant-time compare.

### Getting and rotating the signing key

Dashboard: **API Credentials → Signing Key → Show**. Each project has its own key.

Rotate via the Dashboard reset button, or the API:

```
POST https://{space}.signalwire.com/api/projects/{id}/signing-key/rotate
```

Docs: `/docs/apis/rest/projects/rotate-signing-key`. **The previous key takes about 1–2 minutes to stop working**, so rotation has a short overlap window rather than being instantaneous — deploy the new key within it, and expect a brief period where both verify.

## Content Redaction

Three related params in `ai.params`. Docs: `/docs/swml/reference/calling/ai/params` and `/docs/platform/ai/content-redaction`.

| Param | Type | Default | What it does |
|-------|------|---------|--------------|
| `redact_prompt` | **string** | — | A plain-language description of sensitive content to redact from what the platform records and transmits |
| `auto_correct` | boolean | `false` | Cleans up the caller's transcription before the AI reads it — spoken numbers to digits, address and phone formatting, obvious mishearings — without changing meaning |
| `enable_text_normalization` | **string** | `both` | Converts numbers, currency and dates between written and spoken forms, so the AI understands callers better and speaks more naturally |

**`redact_prompt` is a string, not a switch.** You describe what to redact in plain language — "credit card numbers, CVVs, social security numbers" — and the platform masks matching text with `----`.

```yaml
- ai:
    prompt:
      text: "You are a payments assistant."
    params:
      redact_prompt: "credit card numbers, CVV codes, and social security numbers"
      auto_correct: true
      utility_model: gpt-4.1-mini
```

Both `redact_prompt` and `auto_correct` run on the [`utility_model`](voice-ai.md#utility_model), not the main model.

### What redaction does *not* cover

The name suggests more protection than it gives. **Redaction is applied to the record, not to the call.**

| Masked | Not masked |
|--------|------------|
| Conversation text in completed-turn AI events | The live conversation — both parties hear the real content |
| Webhook payloads | The model's input — the agent processes real words each turn |
| Post-conversation call logs (`call_log`, `raw_call_log`) | Structured fields: entity values, tool results |
| The call timeline | SWAIG handler arguments — your functions receive unmasked data |
| | Audio recordings |

The docs are explicit that this is best-effort and AI-driven, that values can slip through, and that it is "a strong safeguard for your logs and integrations rather than a guarantee."

**So do not use `redact_prompt` as your only control on a card number.** It keeps secrets out of your log pipeline and your webhook payloads. It does not keep them out of the model, out of your SWAIG endpoint, or off the recording. For payment data that must never reach the LLM, use the [`pay`](swml-methods.md#pay) method, which bypasses the model entirely.

Caller content is also redacted from logs at visible log levels.

## Authentication

### Basic Auth for Agent Endpoints

Always protect production agents with authentication:

```python
class SecureAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="secure-agent",
            basic_auth=("username", "strong-password-here")
        )
```

Or via environment variables:

```bash
export SWML_BASIC_AUTH_USER="agent"
export SWML_BASIC_AUTH_PASSWORD="$(openssl rand -base64 32)"
```

### Token-Based Function Security

Mark sensitive functions as secure:

```python
@AgentBase.tool(
    name="delete_account",
    description="Permanently delete customer account",
    parameters={
        "account_id": {"type": "string", "description": "Account ID"}
    },
    secure=True  # Requires token validation
)
def delete_account(self, args, raw_data):
    # Token is automatically validated by the framework
    account_id = args.get("account_id")
    # Perform deletion...
```

## Identity Verification

### PIN Verification Pattern

Verify caller identity before exposing sensitive operations:

```python
class BankingAgent(AgentBase):
    def __init__(self):
        super().__init__(name="banking-agent")
        self.add_language("English", "en-US", "rime.spore")

        self.prompt_add_section(
            "Security",
            "Always verify customer identity before discussing account details. "
            "Use the verify_pin function first."
        )

    @AgentBase.tool(
        name="verify_pin",
        description="Verify customer identity with PIN",
        parameters={
            "pin": {"type": "string", "description": "4-digit PIN"}
        }
    )
    def verify_pin(self, args, raw_data):
        pin = args.get("pin")
        caller = raw_data.get("call", {}).get("from")

        # Implement rate limiting
        attempts = raw_data.get("vars", {}).get("pin_attempts", 0)
        if attempts >= 3:
            return (FunctionResult(
                "Too many incorrect attempts. For your security, "
                "I'll connect you with a representative."
            )
            .add_action("transfer", {"dest": "sip:security@company.com"}))

        if self.validate_pin(caller, pin):
            return (FunctionResult(
                "Identity verified. How can I help you today?"
            )
            .add_action("set_global_data", {"verified": True})
            .add_action("toggle_functions", {
                "active": ["get_balance", "transfer_funds"]
            }))
        else:
            return (FunctionResult(
                f"That PIN doesn't match. You have {2 - attempts} attempts left."
            )
            .add_action("set_global_data", {"pin_attempts": attempts + 1}))

    @AgentBase.tool(
        name="get_balance",
        description="Get account balance (requires verification)",
        parameters={}
    )
    def get_balance(self, args, raw_data):
        # Double-check verification status
        if not raw_data.get("vars", {}).get("verified"):
            return FunctionResult(
                "I need to verify your identity first. What's your PIN?"
            )
        # Return balance...
```

### Knowledge-Based Verification

Verify with personal information:

```python
@AgentBase.tool(
    name="verify_identity",
    description="Verify identity with security questions",
    parameters={
        "last_four_ssn": {"type": "string", "description": "Last 4 of SSN"},
        "zip_code": {"type": "string", "description": "Billing zip code"}
    }
)
def verify_identity(self, args, raw_data):
    caller = raw_data.get("call", {}).get("from")
    ssn_last4 = args.get("last_four_ssn")
    zip_code = args.get("zip_code")

    customer = self.lookup_customer(caller)
    if not customer:
        return FunctionResult(
            "I couldn't find an account with this phone number. "
            "Would you like me to transfer you to customer service?"
        )

    if (customer["ssn_last4"] == ssn_last4 and
        customer["zip"] == zip_code):
        return (FunctionResult(
            f"Thank you, {customer['name']}. How can I help you?"
        )
        .add_action("set_global_data", {
            "verified": True,
            "customer_id": customer["id"]
        }))
    else:
        return FunctionResult(
            "That information doesn't match our records. "
            "Let me connect you with a representative."
        ).add_action("transfer", {"dest": "sip:verify@company.com"})
```

## Input Validation

### Sanitize All Inputs

Never trust user-provided data:

```python
import re

@AgentBase.tool(
    name="lookup_order",
    description="Look up order by number",
    parameters={
        "order_number": {"type": "string", "description": "Order number"}
    }
)
def lookup_order(self, args, raw_data):
    order_number = args.get("order_number", "")

    # Validate format (e.g., ORD-12345)
    if not re.match(r'^ORD-\d{5,10}$', order_number):
        return FunctionResult(
            "That doesn't look like a valid order number. "
            "Order numbers start with ORD- followed by digits."
        )

    # Safe to query
    order = self.db.get_order(order_number)
    # ...
```

### Prevent SQL Injection

Always use parameterized queries:

```python
# WRONG - SQL injection vulnerability
def lookup_customer_bad(self, name):
    query = f"SELECT * FROM customers WHERE name = '{name}'"
    return self.db.execute(query)

# CORRECT - Parameterized query
def lookup_customer_good(self, name):
    query = "SELECT * FROM customers WHERE name = %s"
    return self.db.execute(query, (name,))
```

### Validate Phone Numbers

```python
import re

def is_valid_phone(phone: str) -> bool:
    """Validate E.164 phone number format."""
    return bool(re.match(r'^\+1\d{10}$', phone))

@AgentBase.tool(
    name="send_confirmation",
    description="Send SMS confirmation",
    parameters={
        "phone": {"type": "string", "description": "Phone number"}
    }
)
def send_confirmation(self, args, raw_data):
    phone = args.get("phone", "")

    if not is_valid_phone(phone):
        return FunctionResult(
            "I need a valid US phone number to send the confirmation."
        )

    # Safe to send
    # ...
```

## Data Protection

### Never Log Sensitive Data

```python
import logging

logger = logging.getLogger(__name__)

@AgentBase.tool(
    name="process_payment",
    description="Process a payment",
    parameters={
        "card_number": {"type": "string", "description": "Card number"},
        "amount": {"type": "number", "description": "Amount"}
    }
)
def process_payment(self, args, raw_data):
    card_number = args.get("card_number")
    amount = args.get("amount")

    # WRONG - logs sensitive data
    # logger.info(f"Processing payment: card={card_number}, amount={amount}")

    # CORRECT - mask sensitive data
    masked_card = f"****{card_number[-4:]}" if card_number else "unknown"
    logger.info(f"Processing payment: card={masked_card}, amount={amount}")

    # Process payment...
```

### Secure Global Data

Don't store sensitive info in global_data (it's visible in logs):

```python
# WRONG - sensitive data in global_data
return FunctionResult("Verified!").add_action(
    "set_global_data", {"ssn": "123-45-6789"}
)

# CORRECT - only store non-sensitive identifiers
return FunctionResult("Verified!").add_action(
    "set_global_data", {"verified": True, "customer_id": "cust_abc123"}
)
```

## Environment Security

### Use Environment Variables for Secrets

```python
import os

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="my-agent",
            basic_auth=(
                os.environ["AGENT_USERNAME"],
                os.environ["AGENT_PASSWORD"]
            )
        )

        # API keys from environment
        self.api_key = os.environ["EXTERNAL_API_KEY"]
```

### Never Hardcode Credentials

```python
# WRONG
class BadAgent(AgentBase):
    def __init__(self):
        super().__init__(name="bad-agent")
        self.api_key = "sk-1234567890abcdef"  # NEVER do this

# CORRECT
class GoodAgent(AgentBase):
    def __init__(self):
        super().__init__(name="good-agent")
        self.api_key = os.environ.get("API_KEY")
        if not self.api_key:
            raise ValueError("API_KEY environment variable required")
```

## Rate Limiting

### Prevent Abuse

```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimitedAgent(AgentBase):
    def __init__(self):
        super().__init__(name="rate-limited")
        self._request_times = defaultdict(list)
        self._max_requests = 10  # per minute

    def _check_rate_limit(self, caller: str) -> bool:
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)

        # Clean old entries
        self._request_times[caller] = [
            t for t in self._request_times[caller]
            if t > minute_ago
        ]

        # Check limit
        if len(self._request_times[caller]) >= self._max_requests:
            return False

        self._request_times[caller].append(now)
        return True

    @AgentBase.tool(
        name="expensive_operation",
        description="Perform expensive operation",
        parameters={}
    )
    def expensive_operation(self, args, raw_data):
        caller = raw_data.get("call", {}).get("from", "unknown")

        if not self._check_rate_limit(caller):
            return FunctionResult(
                "You've made too many requests. "
                "Please wait a minute and try again."
            )

        # Proceed with operation...
```

## Secure Transfers

### Validate Transfer Destinations

```python
ALLOWED_DESTINATIONS = {
    "support": "sip:support@company.com",
    "sales": "sip:sales@company.com",
    "billing": "tel:+15551234567"
}

@AgentBase.tool(
    name="transfer",
    description="Transfer to department",
    parameters={
        "department": {
            "type": "string",
            "description": "Department name",
            "enum": ["support", "sales", "billing"]
        }
    }
)
def transfer(self, args, raw_data):
    department = args.get("department")

    # Only allow predefined destinations
    dest = ALLOWED_DESTINATIONS.get(department)
    if not dest:
        return FunctionResult(
            "I can only transfer to support, sales, or billing."
        )

    return FunctionResult(
        f"Transferring you to {department}..."
    ).add_action("transfer", {"dest": dest})
```

## Security Checklist

- [ ] **Authentication**: Agent endpoints require auth
- [ ] **Secrets**: All credentials in environment variables
- [ ] **Validation**: All inputs validated and sanitized
- [ ] **Verification**: Sensitive operations require identity verification
- [ ] **Rate Limiting**: Abuse prevention in place
- [ ] **Logging**: No sensitive data in logs
- [ ] **Transfers**: Only allowed destinations
- [ ] **HTTPS**: Production uses SSL/TLS
- [ ] **Secure Functions**: Destructive operations marked secure
- [ ] **Data Protection**: Minimal data in global_data
