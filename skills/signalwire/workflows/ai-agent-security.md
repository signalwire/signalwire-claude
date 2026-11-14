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

The `url` is the full URL SignalWire requested, including any query string. For call requests, basic auth credentials are stripped before signing; for messaging requests they are included as configured. A `data_map` webhook signs the body built from its `params`, form-encoded when the webhook sets `form_param`. A `data_map` webhook with no body, such as a `GET`, signs the URL alone.

| Header | Algorithm | Present on |
|--------|-----------|------------|
| `X-Signalwire-Signature` | HMAC-SHA1, hex | Every signed request |
| `X-Signalwire-SHA256-Signature` | HMAC-SHA256, hex | Call requests only |

Messaging document requests carry the SHA-1 header only. Requests during a call, AI agent requests included, carry both.

### What is signed, and what is not

There is no setting to enable signing.

**Signed:** every POST SignalWire makes to fetch a SWML document from a URL you control — the initial fetch, the fallback fetch, and `execute` or `transfer` operations pointing at external URLs, on both the call and messaging sides.

The same headers are on every request an AI agent makes during a call:

| Request | Notes |
|---------|-------|
| POST to each SWAIG function's `web_hook_url` | Includes a URL set in `SWAIG.defaults` |
| Webhooks in a function's `data_map` | Not retried |
| Function-definition request to each `SWAIG.includes` URL | During the call |
| Summary sent to `post_prompt_url` from the `ai` method | Also the `post_prompt_url` request that loads a stored conversation when `save_conversation` and a `conversation_id` are set |
| Live stream sent to `debug_webhook_url` | Same two headers |
| Function webhooks from `ai_sidecar` and `amazon_bedrock` | Both signed |

**Not signed:**

| Request | Protect it with |
|---------|-----------------|
| The `request` method during a call | HTTP basic auth in the URL, or a shared secret in a custom `X-` header |
| An `amazon_bedrock` agent's summary to `post_prompt_url`, and its `summarize_conversation` request | Basic auth embedded in the URL (`username:password@url`) |

The messaging counterpart of `request` *does* carry the SHA-1 header. The calling one does not. `amazon_bedrock` function webhooks are signed.

In the rare case SignalWire can't compute a signature, it sends the request with no signature headers. Treat a missing signature the same as an invalid one.

Signed AI agent requests do not follow redirects. A `3xx` is a failed request. An unsigned request, such as the `amazon_bedrock` post-prompt summary or a request sent without a signature, does follow a redirect. A SWML document fetch follows a redirect too, but the signature still covers the URL you configured, not the one it landed on. Point `web_hook_url`, `post_prompt_url`, and the agent's other URLs at their final address, including `https://` and any trailing slash.

When an AI agent's POST to a SWAIG `web_hook_url`, to `post_prompt_url`, or to another of its webhook URLs fails to connect, times out, or gets a `5xx`, SignalWire retries it with the same body and the same signature. `data_map` webhooks are not retried. A signature identifies the content of a request, not one delivery, so don't reject a request only because you have seen that signature before. A timeout can deliver the same function call again while the first is still running. Make handlers idempotent.

### Three things builders get wrong

**1. Hash the exact public-facing URL you configured in the Dashboard.** A proxy that rewrites host or scheme changes the hashed string, and a perfectly valid signature then fails to verify. The docs' own troubleshooting section leads with this, because it is the most common cause. For a call request, strip embedded credentials before you hash. When the query string changes per call — the Server SDK's per-call token does this — rebuild the URL from your public base URL plus the path and query string you received. Don't hard-code it.

**2. Keep the raw body.** Verification hashes the bytes, not a re-serialized JSON object. Round-tripping through a JSON parser reorders keys and changes whitespace, and the hash no longer matches. In Express, capture `req.rawBody` *before* the JSON body parser consumes it:

```js
app.use(express.json({
  verify: (req, res, buf) => { req.rawBody = buf.toString('utf8'); }
}));
```

**3. Do not require a signature on every inbound request.** The `request` method during a call is unsigned, and so are an `amazon_bedrock` agent's `post_prompt_url` summary and its `summarize_conversation` request. Rejecting those for a missing signature drops traffic you meant to accept. On the signed requests above, a missing signature is invalid. The rare unsigned send is a failure to sign, not a request to accept.

The docs carry working verification snippets in Node, Python, and Ruby, plus a "confirm your endpoint rejects forgeries" test. Adapt those rather than writing your own HMAC comparison — and use a constant-time compare.

The Server SDK checks this when you give the agent the project's signing key: `signing_key=` in Python, `signingKey` in TypeScript, or `SIGNALWIRE_SIGNING_KEY`. With a key, an unsigned or mis-signed POST to the SWML, SWAIG, or post-prompt endpoint gets `403` and does not reach your code. Without a key, the agent logs a warning at startup and accepts unsigned requests. Behind a proxy or tunnel, set `SWML_PROXY_URL_BASE` to the public base URL so the check uses the URL SignalWire requested.

### Getting and rotating the signing key

Dashboard: **API Credentials → Signing Key → Show**. Each project has its own key.

New signing keys begin with `swpsk_` and are 42 characters. Older keys begin with `PSK_` and are 28 characters. Both sign the same way. Treat the key as opaque: don't parse it, match a pattern, or assume a length.

Rotate via the Dashboard **Reset** button, or the API. Either one promotes the project's next key:

```
POST https://{space}.signalwire.com/api/projects/{id}/signing-key/rotate
```

Docs: `/docs/apis/rest/projects/rotate-signing-key`. **The new key takes 1–2 minutes to become active.** Until then, requests can still arrive signed with the old key, so accept either key during that window, then drop the old one. A project created before the `swpsk_` format can receive a `PSK_` key from its first rotation.

A create-project response includes `signing_key` once. Later requests do not return it, so capture it from that response. The rotate response is the other time the API returns the key.

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

Python takes the pair as `basic_auth=(user, password)`.

If you leave credentials unset, the Python SDK uses the username `signalwire` and generates a new password on every startup, then prints it. In TypeScript, when the password is generated, the user falls back to the agent's `name`. Use that pair only in development. A restart changes the password, and calls already in progress fail their next function call and their post-prompt summary. Set fixed credentials in production.

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

The token is the `__token` query parameter on the function's `web_hook_url`. The agent signs function tokens, and the token on the post-prompt URL, with a secret: `swaig_secret` in Python, `swaigSecret` in TypeScript, or `SIGNALWIRE_SWAIG_SECRET`. If you don't set one, each process generates its own at startup. Tokens from before a restart then fail, and so do tokens another replica issued, so a call in progress fails its next secure function call and its post-prompt summary. Tokens expire one hour after issue (`token_expiry_secs` / `tokenExpirySecs`). Set the lifetime longer than your longest call, and use the same secret on every replica.

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
            .add_action("toggle_functions", [
                {"function": "get_balance", "active": True},
                {"function": "transfer_funds", "active": True},
            ]))
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

### Collect Cards Outside the Model

The model decides it is time to pay. `pay` keeps the digits out of the model's context. A number spoken before the handoff is still heard, so move to the pay step at the start of the payment turn rather than relying on the prompt. Your pricing handler computes the amount and stores it with `FunctionResult.set_metadata()`. The payment function reads that amount from `raw_data["meta_data"]`. It does not take `card_number` or `amount` from the model.

Metadata is scoped to a function's `meta_data_token`. The SDK mints a distinct URL token per function, so give the pricing and payment functions the same token; otherwise the payment function sees an empty `meta_data`.

`post_process=True` lets the model speak the handoff before the SWML runs. Run `pay`, then `set` `ai_response`. `set` expands `${...}` when it runs, so `${pay_result}` is already filled when the model reads the stored text. Build the `set` yourself rather than using `.pay(ai_response=)`, and see [Gotchas](#gotchas) for why.

```python
@AgentBase.tool(
    name="price_order",
    description="Price the order from your catalog. Do not take an amount from the caller.",
    parameters={},
    meta_data_token="order",
)
def price_order(self, args, raw_data):
    total = "25.00"  # computed here, never taken from the model
    return FunctionResult("The total is ready.").set_metadata({
        "order_total": total,
        "order_id": "ord_123",
    })

@AgentBase.tool(
    name="collect_payment",
    description="Hand the call to keypad card entry. Do not collect card numbers.",
    parameters={},
    meta_data_token="order",
)
def collect_payment(self, args, raw_data):
    meta = raw_data.get("meta_data") or {}
    total = meta.get("order_total")
    if total is None:
        return FunctionResult("Let's finish the order before we take payment.")

    return FunctionResult(
        "Tell the caller to enter the card on the keypad. Do not ask for the number.",
        post_process=True,
    ).execute_swml({
        "version": "1.0.0",
        "sections": {
            "main": [
                {
                    "pay": {
                        "payment_connector_url": "https://payments.example.com/connector",
                        "charge_amount": f"{float(total):.2f}",
                        "description": f"Order {meta.get('order_id')}",
                        "max_attempts": "2",
                        "security_code": "true",
                        "postal_code": "true",
                        "token_type": "one-time",
                    }
                },
                {
                    "set": {
                        "ai_response": (
                            "The payment status is ${pay_result}. "
                            "If it is success, confirm the order and give a delivery estimate. "
                            "If not, apologize and offer to try again or pay another way. "
                            "Do not discuss card details."
                        )
                    }
                },
            ]
        },
    })
```

Give the model `${pay_result}`, the status, and nothing more: see [Gotchas](#gotchas).

### Secure Global Data

Don't store sensitive info in global_data (it's visible in logs).

Keep anything two tools might both update in your own store, keyed by `call_id`: see [Gotchas](#gotchas).

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

- [ ] **Transfers**: The model picks a department, and code maps it to an allowed destination
- [ ] **Secure Functions**: Destructive operations marked secure
- [ ] **Data Protection**: Minimal data in `global_data`, and shared counters kept in your own store
- [ ] **Cards**: Digits never enter the conversation (DTMF); the model receives `${pay_result}`
- [ ] **Semantic gates**: Irreversible SWAIG actions (cancel, refund, share account data, move money) sit behind a gate — one question, threshold `0.9` or higher. See [Semantic gates](ai-agent-functions.md#semantic-gates)

## Gotchas

- **`pay` takes `security_code` and `postal_code` as strings.** Pass `"true"`. JSON booleans are rejected.
- **Run `pay` before `set ai_response`.** `set` expands `${pay_result}` when it runs, so it has to come after `pay`. The SDK's `.pay(ai_response=)` helper writes `set` before `pay`, and the model then sees an empty status, or a stale one from an earlier `pay` on the same call.
- **`pay` from a SWAIG function needs `swaig_allow_swml`.** It's on by default. When it's off, the `pay` step is skipped.
- **`${pay_payment_results}` leaves the expiry and postal code unmasked.** Only the card number and CVV are masked, and the object stays on the call until it ends. Keep it out of `ai_response`, post-call summaries, and later functions; `${pay_result}` is all the model needs.
- **`set_global_data` replaces a whole top-level key.** Each tool gets its own copy of `global_data` when it's called, so two tools that read and rewrite the same key lose one update. An increment such as `pin_attempts + 1` is that read-modify-write.
- **The signing key appears only once the project has an API token.** Create a token first if **API Credentials → Signing Key** is empty.
