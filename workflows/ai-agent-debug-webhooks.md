# Webhooks and Debugging Reference

Guide to configuring debug webhooks, post-prompt URLs, and troubleshooting SignalWire AI Agents.

## Debug Webhooks

Debug webhooks send real-time events from your agent to an external URL for monitoring and debugging.

### Configuration

**Via Environment Variables:**

```bash
export DEBUG_WEBHOOK_URL="https://webhook.site/your-unique-id"
export DEBUG_WEBHOOK_LEVEL="1"
```

**Via set_params():**

```python
agent.set_params({
    "debug_webhook_url": "https://webhook.site/your-unique-id",
    "debug_webhook_level": 1
})
```

### Debug Levels

| Level | Name | Events Included |
|-------|------|-----------------|
| `0` | Off | No debug events (default) |
| `1` | Basic | Function calls, errors, state changes |
| `2` | Verbose | All events including transcripts, full payloads |

### Event Types

When `debug_webhook_level >= 1`, you receive:

- **Function calls** - When AI calls a SWAIG function
- **Function results** - Return values from functions
- **Errors** - Any errors during processing
- **State changes** - Global data updates

When `debug_webhook_level == 2`, additionally:

- **Transcripts** - Full speech-to-text output
- **AI responses** - Full AI response text
- **Raw payloads** - Complete request/response data

### Webhook Payload Structure

```json
{
    "event": "function_call",
    "timestamp": "2024-01-15T10:30:00Z",
    "call_id": "abc123",
    "data": {
        "function": "get_weather",
        "arguments": {"city": "Seattle"},
        "result": "Weather in Seattle: 55°F"
    }
}
```

### Recommended Debug Services

- **webhook.site** - Free, instant webhook URL for testing
- **RequestBin** - Inspect webhooks in browser
- **ngrok inspect** - View requests to your ngrok tunnel
- **Your own endpoint** - Log to file, database, or monitoring service

## Post-Prompt URL

Receive a callback when a conversation ends with summary data.

### Configuration

```python
agent.set_post_prompt_url("https://api.example.com/call-complete")
```

Or with environment variable:

```bash
export SWML_POST_PROMPT_URL="https://api.example.com/call-complete"
```

### Post-Prompt Payload

When you configure a post-prompt (text or JSON schema), the result is sent to your URL:

**Text summary post-prompt:**

```python
agent.set_post_prompt("Summarize this conversation in 2-3 sentences.")
```

Webhook receives:
```json
{
    "call_id": "abc123",
    "summary": "Customer called about order #12345. Issue was resolved by providing tracking information.",
    "call": {
        "from": "+15551234567",
        "to": "+15559876543",
        "duration": 180
    }
}
```

**JSON schema post-prompt:**

```python
agent.set_post_prompt(json_schema={
    "type": "object",
    "properties": {
        "resolved": {"type": "boolean"},
        "category": {"type": "string", "enum": ["billing", "support", "sales"]},
        "summary": {"type": "string"},
        "follow_up_required": {"type": "boolean"}
    }
})
```

Webhook receives:
```json
{
    "call_id": "abc123",
    "summary": {
        "resolved": true,
        "category": "support",
        "summary": "Customer needed tracking info for order #12345",
        "follow_up_required": false
    },
    "call": {
        "from": "+15551234567",
        "to": "+15559876543"
    }
}
```

### Handling in on_summary()

You can also handle summaries in your agent code:

```python
class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="my-agent")
        self.set_post_prompt(json_schema={
            "type": "object",
            "properties": {
                "resolved": {"type": "boolean"},
                "summary": {"type": "string"}
            }
        })

    def on_summary(self, summary=None, raw_data=None):
        if summary:
            # Log to database, send notification, etc.
            self.log.info("call_complete", summary=summary)

            if not summary.get("resolved"):
                # Create follow-up ticket
                self.create_ticket(summary, raw_data)
```

## Debugging Techniques

### 1. SWML Dump

Test your agent configuration without making calls:

```bash
swaig-test my_agent.py --dump-swml
```

This outputs the complete SWML configuration, useful for:
- Verifying prompt structure
- Checking function definitions
- Validating parameters

### 2. Function Testing

Test individual functions:

```bash
# List all functions
swaig-test my_agent.py --list-tools

# Call a specific function
swaig-test my_agent.py --exec get_weather --args '{"city": "Seattle"}'
```

### 3. Local Webhook Testing

Use ngrok to expose local endpoints:

```bash
# Terminal 1: Run your agent
python my_agent.py

# Terminal 2: Expose with ngrok
ngrok http 3000
```

Set `DEBUG_WEBHOOK_URL` to your ngrok URL, then view events at `http://localhost:4040`.

### 4. Verbose Logging

Enable debug-level logging:

```bash
SWML_LOG_LEVEL=DEBUG python my_agent.py
```

Or in code:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 5. Request Inspection

Add middleware to log all requests:

```python
class DebugAgent(AgentBase):
    def on_swml_request(self, request_data=None, callback_path=None, request=None):
        print(f"SWML Request: {request_data}")
        print(f"Callback path: {callback_path}")
```

## Common Issues and Solutions

### Functions Not Being Called

**Symptom:** AI doesn't call your functions even when appropriate.

**Solutions:**
1. Check function description - make it clear when to use
2. Verify parameters have good descriptions
3. Add hints to your prompt mentioning the function

```python
self.prompt_add_section(
    "Available Actions",
    bullets=["Use get_order_status to look up order information"]
)
```

### Webhook Not Receiving Events

**Symptom:** Debug webhook URL set but no events received.

**Solutions:**
1. Verify `DEBUG_WEBHOOK_LEVEL` is 1 or 2 (not 0)
2. Check URL is publicly accessible
3. Verify no firewall blocking outbound requests
4. Test URL with curl first

```bash
curl -X POST https://webhook.site/your-id -d '{"test": true}'
```

### Authentication Failures

**Symptom:** 401 Unauthorized errors.

**Solutions:**
1. Check basic auth credentials match
2. Verify credentials in URL are properly encoded
3. Check environment variables are set correctly

```bash
# Test with curl
curl -u user:password https://your-agent.com/agent
```

### Timeout Errors

**Symptom:** Function calls timing out.

**Solutions:**
1. Add fillers to give AI something to say while processing:

```python
@AgentBase.tool(
    name="slow_operation",
    description="Perform slow operation",
    parameters={},
    fillers=["Let me check that for you", "One moment please"]
)
def slow_operation(self, args, raw_data):
    # Long operation
    pass
```

2. Or use wait_file for audio:

```python
@AgentBase.tool(
    name="slow_operation",
    description="Perform slow operation",
    parameters={},
    wait_file="https://example.com/hold-music.mp3",
    wait_file_loops=3
)
```

## Debug Checklist

When troubleshooting an agent:

- [ ] SWML dumps correctly (`swaig-test --dump-swml`)
- [ ] Functions list properly (`swaig-test --list-tools`)
- [ ] Functions execute correctly (`swaig-test --exec`)
- [ ] Agent starts without errors
- [ ] Webhook URL is accessible
- [ ] Debug level is set (1 or 2)
- [ ] SignalWire credentials are valid
- [ ] Proxy URL is reachable from SignalWire
- [ ] Basic auth credentials match (if used)

## Production Monitoring

For production, consider:

1. **Structured logging** - Use JSON format for log aggregation

```bash
SWML_LOG_FORMAT=json python my_agent.py
```

2. **Error alerting** - Send errors to monitoring service

```python
def on_summary(self, summary=None, raw_data=None):
    if raw_data and raw_data.get("error"):
        send_to_pagerduty(raw_data["error"])
```

3. **Metrics collection** - Track call duration, resolution rate, etc.

```python
def on_summary(self, summary=None, raw_data=None):
    statsd.increment("calls.completed")
    if summary and summary.get("resolved"):
        statsd.increment("calls.resolved")
```

4. **Disable verbose debugging** - Use level 0 or 1 in production

```bash
DEBUG_WEBHOOK_LEVEL=0  # or 1 for basic events only
```

## Debug Routes

### enable_debug_routes()

Enable debug endpoints for testing (automatically enabled in development):

```python
agent.enable_debug_routes()
```

This provides endpoints for call inspection and testing.

### setup_graceful_shutdown()

Set up signal handlers for clean shutdown (useful for Kubernetes):

```python
agent.setup_graceful_shutdown()
```

This handles SIGTERM and SIGINT signals for graceful termination.
