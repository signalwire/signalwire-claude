# BedrockAgent Reference

BedrockAgent extends AgentBase to support Amazon Bedrock's voice-to-voice model while maintaining full compatibility with SignalWire agent features.

## Import

```python
from signalwire_agents import BedrockAgent
```

## Overview

BedrockAgent provides:
- Amazon Bedrock voice-to-voice integration
- Full compatibility with all AgentBase features
- Skills and SWAIG function support
- POM-style prompts
- Post-prompt functionality
- Dynamic configuration

The main difference from `AgentBase` is that it generates SWML with the `amazon_bedrock` verb instead of `ai`.

## Constructor Parameters

```python
BedrockAgent(
    name: str = "bedrock_agent",
    route: str = "/bedrock",
    system_prompt: Optional[str] = None,
    voice_id: str = "matthew",
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_tokens: int = 1024,
    **kwargs
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | "bedrock_agent" | Agent name |
| `route` | str | "/bedrock" | HTTP endpoint path |
| `system_prompt` | str | None | Initial system prompt |
| `voice_id` | str | "matthew" | Bedrock voice ID |
| `temperature` | float | 0.7 | Generation temperature (0-1) |
| `top_p` | float | 0.9 | Nucleus sampling parameter (0-1) |
| `max_tokens` | int | 1024 | Maximum tokens to generate |
| **kwargs | | | Additional AgentBase parameters |

## Bedrock-Specific Methods

### set_voice()

Set the Bedrock voice ID.

```python
def set_voice(self, voice_id: str) -> None
```

**Available voices:**
- `matthew` (default)
- `joanna`
- Other Bedrock-supported voices

**Example:**
```python
agent.set_voice("joanna")
```

### set_inference_params()

Update Bedrock inference parameters.

```python
def set_inference_params(
    self,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> None
```

**Parameters:**
- `temperature` - Generation temperature (0-1). Higher = more random.
- `top_p` - Nucleus sampling (0-1). Lower = more focused.
- `max_tokens` - Maximum tokens to generate.

**Example:**
```python
agent.set_inference_params(
    temperature=0.5,
    top_p=0.9,
    max_tokens=2048
)
```

## Inherited Features

BedrockAgent inherits all AgentBase features:

### Prompt Building

```python
# Text-based prompt
agent.set_prompt_text("You are a helpful assistant.")

# POM-style prompts
agent.prompt_add_section("Role", "You are a helpful assistant.")
agent.prompt_add_section("Guidelines", bullets=["Be concise", "Be helpful"])
```

### Skills

```python
agent.add_skill("datetime", {"timezone": "America/New_York"})
agent.add_skill("math")
```

### SWAIG Functions

```python
@BedrockAgent.tool(
    name="lookup_info",
    description="Look up information",
    parameters={"query": {"type": "string", "description": "Query"}}
)
def lookup_info(self, args, raw_data):
    return SwaigFunctionResult(f"Found: {args.get('query')}")
```

### Post-Prompt

```python
agent.set_post_prompt("Summarize this conversation.")

# Or with JSON schema
agent.set_post_prompt(json_schema={
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "resolved": {"type": "boolean"}
    }
})
```

### Global Data

```python
agent.set_global_data({
    "company_name": "Acme Corp",
    "support_hours": "9-5 EST"
})
```

## Methods Not Applicable

These methods log warnings when called on BedrockAgent:

| Method | Reason |
|--------|--------|
| `set_llm_model()` | Bedrock uses fixed voice-to-voice model |
| `set_prompt_llm_params()` | Use `set_inference_params()` instead |
| `set_post_prompt_llm_params()` | Configured in backend |

## Complete Example

```python
#!/usr/bin/env python3
from signalwire_agents import BedrockAgent
from signalwire_agents.core.function_result import SwaigFunctionResult


class CustomerServiceBedrockAgent(BedrockAgent):
    """Customer service agent using Amazon Bedrock."""

    def __init__(self):
        super().__init__(
            name="bedrock-support",
            route="/support",
            voice_id="matthew",
            temperature=0.7,
            top_p=0.9,
            port=3000
        )

        # Build prompt
        self.prompt_add_section(
            "Role",
            "You are a friendly customer service agent for Acme Corp."
        )
        self.prompt_add_section(
            "Guidelines",
            bullets=[
                "Be helpful and professional",
                "Keep responses concise",
                "Use the lookup_order function for order inquiries"
            ]
        )

        # Add skills
        self.add_skill("datetime", {"timezone": "America/New_York"})

        # Set global context
        self.set_global_data({
            "company": "Acme Corp",
            "hours": "9 AM - 5 PM EST"
        })

        # Configure post-prompt
        self.set_post_prompt(json_schema={
            "type": "object",
            "properties": {
                "resolved": {"type": "boolean"},
                "category": {"type": "string"},
                "summary": {"type": "string"}
            }
        })

    @BedrockAgent.tool(
        name="lookup_order",
        description="Look up an order by order number",
        parameters={
            "order_number": {
                "type": "string",
                "description": "The order number to look up"
            }
        }
    )
    def lookup_order(self, args, raw_data):
        order_num = args.get("order_number")
        # In real implementation, query database
        return SwaigFunctionResult(
            f"Order {order_num} shipped Monday, arriving Friday."
        )

    @BedrockAgent.tool(
        name="transfer_to_human",
        description="Transfer to a human agent",
        parameters={}
    )
    def transfer_to_human(self, args, raw_data):
        return (SwaigFunctionResult("Transferring to a specialist.")
                .add_action("transfer", {"dest": "sip:support@acme.com"}))

    def on_summary(self, summary=None, raw_data=None):
        if summary:
            print(f"Call completed: {summary}")


if __name__ == "__main__":
    agent = CustomerServiceBedrockAgent()
    agent.run()
```

## Multi-Agent Deployment

Deploy Bedrock and standard agents together:

```python
from signalwire_agents import AgentServer, AgentBase, BedrockAgent

server = AgentServer(host="0.0.0.0", port=3000)

# Standard agent
standard = MyStandardAgent()
server.register(standard, "/standard")

# Bedrock agent
bedrock = CustomerServiceBedrockAgent()
server.register(bedrock, "/bedrock")

server.run()
```

## AWS Configuration

BedrockAgent uses AWS Bedrock, which requires appropriate AWS credentials and permissions. Ensure your environment has:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

Or configure via AWS IAM roles when running in AWS.

## See Also

- [Agent Base Reference](agent-base.md) - Base class documentation
- [SWAIG Functions Reference](swaig-functions.md) - Function patterns
- [Skills Reference](skills-complete.md) - Available skills
