# AI Agent Prompting

## Overview

Master the art of prompting AI voice agents for production use. This guide covers best practices, frameworks, and anti-patterns learned from real-world deployments.

## Related Workflows

- [Voice AI](voice-ai.md) - Overview and decision guide
- [AI Agent SDK Basics](ai-agent-sdk-basics.md) - Python SDK fundamentals
- [AI Agent Functions](ai-agent-functions.md) - SWAIG function patterns
- [AI Agent Deployment](ai-agent-deployment.md) - Production deployment

## Core Principle: Treat AI Like a Person

> "How would you instruct your mother to do the task you want done?" - Brian West

AI agents respond to natural language instructions, not programming commands:

- Use clear, natural language instructions
- Avoid programming mentality - guide, don't command
- Less is more - avoid over-prompting
- Use positive sequential instructions, not rigid "never" statements

## Prompting Best Practices

### 1. Use Clear, Concise Language

**Good:**
```
Transfer the caller after you validate their account.
```

**Bad (Too Strong):**
```
Never transfer the call until you validate their account.
```

The word "never" creates rigid behavior that prevents proper execution. Strong negative language confuses AI agents.

### 2. Avoid Overprompting

Less is more - don't give excessive information:

**Example of overprompting:**
```
You must always greet the customer. Never forget to greet them. Make absolutely sure you say hello. Don't skip the greeting under any circumstances.
```

**Better:**
```
Greet the customer warmly.
```

**Why this matters:**
- Break complex tasks across multiple AI agents
- Each agent should have a focused, specific purpose
- Too much information creates confusion

### 3. Address Edge Cases in Prompts

**Example:**
```
You always have pizza in stock. Never tell customers you're out of pizza.
```

Without this instruction, AI might occasionally hallucinate being out of stock, even when you have inventory.

**Pattern:**
```python
self.agent.set_prompt(text="""
You are a restaurant order taker.

Important facts:
- We always have burgers available
- Delivery time is always 30 minutes
- We accept cash and credit cards only

Never tell customers we're out of stock on menu items.
""")
```

### 4. Use Sequential Steps, Not Rigid Rules

**Good (Sequential):**
```
Steps:
1. Greet the caller
2. Ask how you can help
3. Gather necessary information
4. Transfer to the appropriate department
```

**Bad (Rigid):**
```
Never transfer without greeting.
Never ask for information before greeting.
You must always greet first, no exceptions.
```

**Why sequential works better:**
- AI understands workflow progression
- Allows for natural conversation flow
- Accommodates interruptions gracefully

## The RISE-M Prompt Framework

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

### RISE-M in Practice

```python
class ReceptionistAgent(AgentBase):
    def __init__(self):
        super().__init__(name="receptionist")

        # Role
        self.prompt_add_section(
            "Role",
            "You are Sarah, a professional receptionist for TechCorp."
        )

        # Instructions
        self.prompt_add_section(
            "Instructions",
            """- Answer professionally and courteously
- Listen carefully to caller needs
- Use functions to assist callers"""
        )

        # Steps
        self.prompt_add_section(
            "Steps",
            """1. Greet caller with time-appropriate greeting
2. Ask how you can assist them
3. Collect: name, company, callback number
4. Route to appropriate department or take message"""
        )

        # Expectations
        self.prompt_add_section(
            "Expectations",
            """- Professional tone at all times
- Complete information gathering before transfer
- Confirm all details with caller"""
        )

        # Methods (functions define themselves via decorator)
```

## Voice Configuration

### Basic Voice Settings

```python
# Add language with specific voice
agent.add_language("English", "en-US", "rime.spore")

# Multiple languages for auto-detection
agent.add_language("English", "en-US", "rime.spore")
agent.add_language("Spanish", "es-MX", "rime.spore")

# Premium voices
agent.add_language("English", "en-US", "elevenlabs.josh")
agent.add_language("English", "en-US", "openai.nova")
```

**Available TTS Engines:**
- **Rime** (default, included): `rime.spore`, `rime.marsh`
- **ElevenLabs** (premium): `elevenlabs.josh`, `elevenlabs.rachel`
- **OpenAI**: `openai.nova`, `openai.alloy`
- **Google**: `gcloud.en-US-Neural2-A`
- **Azure**: `azure.en-US-JennyNeural`
- **Amazon Polly**: `polly.Matthew`, `polly.Joanna`
- **Deepgram**: `deepgram.aura-asteria-en`

For complete voice configuration (fillers, pronunciation, hints), see: [reference/sdk/voice-configuration.md](../reference/sdk/voice-configuration.md)

### Multi-Language Support

**Auto-Detection Capability:**
- Add multiple languages in the Languages tab
- AI automatically detects and responds in the caller's language
- No need to write separate prompts per language
- Supports 10+ languages with Nova 3

**Example:**

```python
class MultilingualAgent(AgentBase):
    def __init__(self):
        super().__init__(name="multilingual")

        # Auto-detect and respond in caller's language
        self.add_language("English", "en-US", "rime.spore")
        self.add_language("Spanish", "es-MX", "rime.spore")
        self.add_language("French", "fr-FR", "rime.spore")

        # Single prompt works for all languages
        self.prompt_add_section(
            "Role",
            "You are a customer service agent. Help customers in their preferred language."
        )
```

**Static Greeting for Compliance:**

```yaml
# SWML version for required disclosures
- play:
    urls:
      - "say:English greeting and disclosure"
      - "say:Spanish greeting and disclosure"
- ai:
    prompt: "Your instructions here"
```

This ensures compliance requirements are met (e.g., call recording disclosure) while still leveraging multi-language AI.

### Voice Cloning and Premium Voices

**Voice Cloning Benefits:**
- Clone your voice with 11 Labs
- Speak 29 languages in your own voice
- Maintains consistency across languages
- Preserves brand voice

**Available TTS Providers:**
- Google (default, included)
- 11 Labs (premium, clone your own voice)
- OpenAI TTS
- PlayHT (for emotions)

## Latency Optimization

### Filler Strategies

**1. Speech Fillers:**

```yaml
# SWML version
fillers:
  - "Let me look that up for you"
  - "One moment please"
  - "Just checking on that"
```

```python
# SDK version
agent.set_params({
    "fillers": [
        "Let me look that up for you",
        "One moment please",
        "Just checking on that"
    ]
})
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

### Silence Management

```yaml
- play:
    url: "silence:1.0"  # 1 second of silence
```

Strategic silence can make conversations feel more natural.

## Handling Interruptions

### Transparent Barge

SignalWire's barge handling:
- AI removes last response when interrupted
- Rolls up multiple interruptions into one query
- Provides more pertinent answers
- Two logs available: raw and processed

### Barge Acknowledgment

Configure AI to acknowledge excessive interruptions:

```python
self.prompt_add_section(
    "Interruption Handling",
    "If the caller interrupts you repeatedly, politely ask them to let you finish speaking."
)
```

**Example:**
```
I understand you're eager to get help. Please let me finish so I can assist you properly.
```

## Configuration Patterns

### Conversation Flow Setup (UI Method)

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

### Advanced Configuration (SWML Method)

Use SWML for:
- Custom function integration
- Multi-language support
- Complex conditional logic
- Post-prompt processing

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
@AgentBase.tool(name="get_hours", description="Get business hours", parameters={})
def get_hours(self, args, raw_data):
    """Get business hours"""
    return SwaigFunctionResult("We're open 9 AM to 5 PM Monday through Friday")

@AgentBase.tool(name="get_location", description="Get business location", parameters={})
def get_location(self, args, raw_data):
    """Get business location"""
    return SwaigFunctionResult("We're located at 123 Main St")

@AgentBase.tool(name="get_products", description="Get product catalog", parameters={})
def get_products(self, args, raw_data):
    """Get product catalog"""
    products = database.query("SELECT * FROM products")
    return SwaigFunctionResult(format_product_list(products))
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

## Testing Prompts

### Test Continuously

AI behavior is probabilistic:
- Test after every prompt change
- Use real phone calls, not just webhooks
- Test with different voices and accents
- Monitor post-prompt data religiously
- Iterate constantly based on real usage

### Testing Checklist

**After every prompt change:**
- Test with different phrasings
- Test edge cases
- Test failure scenarios
- Test with real phone calls (not just webhooks)

**Variables to test:**
- Different accents
- Different speech patterns
- Background noise
- Poor audio quality
- Mumbling/unclear speech

### A/B Testing Prompts

```python
import random

class ABTestAgent(AgentBase):
    def __init__(self):
        super().__init__(name="ab-test")

        # Randomly select prompt variant
        if random.random() < 0.5:
            # Variant A
            self.prompt_add_section("Role", "You are a friendly agent.")
        else:
            # Variant B
            self.prompt_add_section("Role", "You are a professional agent.")
```

- Test two prompt variations
- Compare success rates
- Iterate on winner
- Document results

## Production Best Practices

### Clear Prompts

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

### Function Documentation

```python
@AgentBase.tool(
    name="check_inventory",
    description="Check product inventory levels",
    parameters={
        "product_id": {
            "type": "string",
            "description": "Unique product identifier (e.g., 'PROD-12345')"
        },
        "location": {
            "type": "string",
            "description": "Storage location to check (default: 'warehouse')",
            "required": False
        }
    }
)
def check_inventory(self, args, raw_data):
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

### Conversational Responses

```python
# Good: Natural, helpful
"I found your order! It was shipped on January 10th and should arrive by January 15th."

# Avoid: Robotic, technical
"Order status: SHIPPED. Ship date: 2025-01-10. ETA: 2025-01-15."
```

### Monitor Post-Prompt Data

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

## Common Issues and Solutions

### Issue: AI Not Calling Functions

**Symptoms:**
- Function never triggers
- AI tries to answer without data

**Solutions:**
1. Make function purpose clearer
2. Explicitly mention function in prompt
3. Reduce prompt complexity
4. Test function independently with webhook.site

**Example fix:**

```python
# Before (vague)
@AgentBase.tool(name="lookup", description="Lookup data", parameters={...})

# After (clear)
@AgentBase.tool(
    name="check_order_status",
    description="Check the status of a customer's order using their order number",
    parameters={...}
)
```

### Issue: AI Hallucinating Information

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

**Example:**

```python
self.prompt_add_section(
    "Knowledge Boundaries",
    """You only know information provided through your functions.
    If you don't have access to information, say "I don't have that information."
    Never make up or guess information."""
)
```

### Issue: Loop Detection Triggering Too Soon

**Symptoms:**
- Call ends after valid attempts
- Users disconnected prematurely

**Solutions:**
```yaml
# Increase loop threshold in your SWML
- condition:
    if: "{{loop}} > 5"  # Was 2
```

## Next Steps

- [AI Agent Functions](ai-agent-functions.md) - Learn SWAIG function patterns
- [AI Agent SDK Basics](ai-agent-sdk-basics.md) - Python SDK fundamentals
- [AI Agent Deployment](ai-agent-deployment.md) - Deploy to production
- [Voice AI](voice-ai.md) - Complete overview and examples
