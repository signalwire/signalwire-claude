# AgentBase Reference

Complete reference for the `AgentBase` class - the foundation for all SignalWire AI Agents.

## Import

```python
from signalwire_agents import AgentBase
```

## Class Definition

```python
class AgentBase(
    AuthMixin,
    WebMixin,
    SWMLService,
    PromptMixin,
    ToolMixin,
    SkillMixin,
    AIConfigMixin,
    ServerlessMixin,
    StateMixin
)
```

## Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | **required** | Agent identifier, used in logs and URLs |
| `route` | str | `"/"` | HTTP endpoint path for this agent |
| `host` | str | `"0.0.0.0"` | Host address to bind server |
| `port` | int | `3000` | Port number for HTTP server |
| `basic_auth` | tuple | `None` | `(username, password)` for HTTP basic auth |
| `use_pom` | bool | `True` | Enable Prompt Object Model for structured prompts |
| `token_expiry_secs` | int | `3600` | Session token lifetime in seconds |
| `auto_answer` | bool | `True` | Automatically answer incoming calls |
| `record_call` | bool | `False` | Enable call recording |
| `record_format` | str | `"mp4"` | Recording format (mp4, wav, mp3) |
| `record_stereo` | bool | `True` | Record in stereo (separate channels) |
| `default_webhook_url` | str | `None` | Default URL for SWAIG function webhooks |
| `agent_id` | str | `None` | Custom agent ID (auto-generated if not provided) |
| `native_functions` | list | `None` | List of native SWML functions to expose |
| `suppress_logs` | bool | `False` | Disable structured logging output |

## Prompt Methods (from PromptMixin)

### prompt_add_section()

Add a section to the prompt.

```python
def prompt_add_section(
    self,
    title: str,
    body: str = None,
    bullets: List[str] = None
) -> 'AgentBase'
```

**Parameters:**
- `title` - Section header name
- `body` - Paragraph text content
- `bullets` - List of bullet points

**Returns:** Self for method chaining

**Examples:**

```python
# Simple text section
agent.prompt_add_section("Role", "You are a helpful assistant.")

# Section with bullets
agent.prompt_add_section(
    "Guidelines",
    body="Follow these rules:",
    bullets=["Be concise", "Be helpful", "Be accurate"]
)

# Bullets only
agent.prompt_add_section("Tasks", bullets=["Answer questions", "Provide support"])
```

### prompt_add_subsection()

Add a subsection under an existing section.

```python
def prompt_add_subsection(
    self,
    section_title: str,
    subsection_title: str,
    body: str = None,
    bullets: List[str] = None
) -> 'AgentBase'
```

### set_post_prompt()

Set the post-prompt for conversation summarization.

```python
def set_post_prompt(
    self,
    text: str = None,
    json_schema: dict = None
) -> 'AgentBase'
```

**Examples:**

```python
# Text summary
agent.set_post_prompt("Summarize this conversation in 2-3 sentences.")

# Structured JSON output
agent.set_post_prompt(json_schema={
    "type": "object",
    "properties": {
        "resolved": {"type": "boolean"},
        "category": {"type": "string"},
        "summary": {"type": "string"}
    }
})
```

### get_prompt()

Get the current prompt content.

```python
def get_prompt(self) -> Union[str, List[dict]]
```

### get_post_prompt()

Get the current post-prompt content.

```python
def get_post_prompt(self) -> Optional[str]
```

## Tool Methods (from ToolMixin)

### define_tool()

Programmatically define a SWAIG function.

```python
def define_tool(
    self,
    name: str,
    description: str,
    handler: Callable,
    parameters: dict = None,
    secure: bool = False,
    fillers: List[str] = None,
    wait_file: str = None,
    wait_file_loops: int = None
) -> 'AgentBase'
```

**Parameters:**
- `name` - Function identifier
- `description` - Description for AI to understand when to call
- `handler` - Callable with signature `(args, raw_data) -> SwaigFunctionResult`
- `parameters` - JSON Schema for function parameters
- `secure` - Require token validation
- `fillers` - Phrases to say while processing
- `wait_file` - Audio file URL to play while processing
- `wait_file_loops` - Number of times to loop wait_file

**Example:**

```python
self.define_tool(
    name="get_balance",
    description="Get the account balance for a customer",
    parameters={
        "account_id": {
            "type": "string",
            "description": "Customer account ID"
        }
    },
    handler=self.handle_get_balance,
    fillers=["Let me check that for you", "One moment please"]
)
```

### @AgentBase.tool Decorator

Declarative function definition.

```python
@AgentBase.tool(
    name: str = None,           # Defaults to method name
    description: str = None,    # Required
    parameters: dict = None,    # JSON Schema
    secure: bool = False,
    fillers: List[str] = None,
    wait_file: str = None,
    wait_file_loops: int = None
)
```

**Example:**

```python
@AgentBase.tool(
    name="transfer_call",
    description="Transfer the call to a support agent",
    parameters={
        "department": {
            "type": "string",
            "description": "Department to transfer to",
            "enum": ["sales", "support", "billing"]
        }
    }
)
def transfer_call(self, args, raw_data):
    dept = args.get("department")
    return SwaigFunctionResult(f"Transferring to {dept}").add_action(
        "transfer", {"dest": f"sip:{dept}@company.com"}
    )
```

### register_swaig_function()

Register a pre-built SWAIG function dictionary.

```python
def register_swaig_function(self, func_dict: dict) -> 'AgentBase'
```

Used primarily with DataMap:

```python
datamap = DataMap("search").purpose("Search").webhook("GET", url)
agent.register_swaig_function(datamap.to_swaig_function())
```

## Skill Methods (from SkillMixin)

### add_skill()

Add a skill to the agent.

```python
def add_skill(
    self,
    skill_name: str,
    params: dict = None
) -> 'AgentBase'
```

**Example:**

```python
agent.add_skill("web_search", {
    "api_key": os.environ["GOOGLE_API_KEY"],
    "search_engine_id": os.environ["GOOGLE_CSE_ID"]
})

agent.add_skill("datetime", {"timezone": "America/Chicago"})
```

### remove_skill()

Remove a skill from the agent.

```python
def remove_skill(self, skill_name: str) -> bool
```

### has_skill()

Check if a skill is loaded.

```python
def has_skill(self, skill_name: str) -> bool
```

### list_skills()

Get list of loaded skill names.

```python
def list_skills(self) -> List[str]
```

## AI Configuration Methods (from AIConfigMixin)

### add_language()

Add a language with voice configuration.

```python
def add_language(
    self,
    name: str,
    code: str,
    voice: str,
    speech_fillers: List[str] = None,
    function_fillers: List[str] = None
) -> 'AgentBase'
```

**Parameters:**
- `name` - Human-readable language name
- `code` - Language code (e.g., "en-US", "es-MX")
- `voice` - TTS voice identifier
- `speech_fillers` - Phrases during speech processing
- `function_fillers` - Phrases during function execution

**Example:**

```python
agent.add_language(
    "English",
    "en-US",
    "rime.spore",
    speech_fillers=["um", "let me think"],
    function_fillers=["one moment", "checking"]
)
```

### add_hints()

Add speech recognition hints.

```python
def add_hints(self, hints: List[str]) -> 'AgentBase'
```

**Example:**

```python
agent.add_hints(["SignalWire", "SWML", "SWAIG", "API", "SDK"])
agent.add_hints(["account number", "routing number"])
```

### set_params()

Set AI behavior parameters.

```python
def set_params(self, params: dict) -> 'AgentBase'
```

**Common Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `end_of_speech_timeout` | int | 3000 | ms of silence to end turn |
| `attention_timeout` | int | 10000 | ms before attention prompt |
| `inactivity_timeout` | int | 600000 | ms before disconnect |
| `barge_match_string` | str | None | Regex for interruption triggers |
| `barge_min_words` | int | 1 | Min words to trigger barge |
| `ai_volume` | int | 0 | Volume adjustment (-50 to 50 dB) |
| `local_tz` | str | None | Timezone for datetime |
| `energy_threshold` | float | 0.05 | Speech detection sensitivity |
| `stt_engine` | str | None | Speech-to-text engine |

**Example:**

```python
agent.set_params({
    "end_of_speech_timeout": 1000,
    "attention_timeout": 15000,
    "inactivity_timeout": 300000,
    "barge_match_string": "stop|cancel|help|agent",
    "barge_min_words": 2,
    "local_tz": "America/New_York"
})
```

### set_global_data()

Set data available to the AI throughout the conversation.

```python
def set_global_data(self, data: dict) -> 'AgentBase'
```

**Example:**

```python
agent.set_global_data({
    "company_name": "Acme Corp",
    "support_hours": "9am-5pm EST",
    "support_email": "help@acme.com"
})
```

### add_pronounce()

Add pronunciation rules.

```python
def add_pronounce(
    self,
    pattern: str,
    replacement: str,
    ignore_case: bool = True
) -> 'AgentBase'
```

**Example:**

```python
agent.add_pronounce("API", "A P I")
agent.add_pronounce("SQL", "sequel")
agent.add_pronounce("GIF", "jiff")
```

## Call Flow Methods

### add_pre_answer_verb()

Add a verb to execute before answering the call.

```python
def add_pre_answer_verb(
    self,
    verb_name: str,
    config: dict
) -> 'AgentBase'
```

**Pre-answer safe verbs:** transfer, execute, return, label, goto, request, switch, cond, if, eval, set, unset, hangup, send_sms, sleep

**Note:** `play` and `connect` verbs require `"auto_answer": False` in config.

**Example:**

```python
# Play ringback tone
agent.add_pre_answer_verb("play", {
    "urls": ["ring:us"],
    "auto_answer": False
})
```

### add_post_answer_verb()

Add a verb to execute after answering but before the AI starts.

```python
def add_post_answer_verb(
    self,
    verb_name: str,
    config: dict
) -> 'AgentBase'
```

**Example:**

```python
agent.add_post_answer_verb("play", {
    "url": "say:Thank you for calling. This call may be recorded."
})
agent.add_post_answer_verb("sleep", {"time": 500})
```

### add_post_ai_verb()

Add a verb to execute after the AI conversation ends.

```python
def add_post_ai_verb(
    self,
    verb_name: str,
    config: dict
) -> 'AgentBase'
```

**Example:**

```python
agent.add_post_ai_verb("request", {
    "url": "https://api.example.com/call-complete",
    "method": "POST"
})
agent.add_post_ai_verb("hangup", {})
```

### add_answer_verb()

Configure the answer verb.

```python
def add_answer_verb(self, config: dict = None) -> 'AgentBase'
```

**Example:**

```python
agent.add_answer_verb({"max_duration": 3600})  # 1 hour max
```

### clear_*_verbs()

Remove verbs from insertion points.

```python
agent.clear_pre_answer_verbs()
agent.clear_post_answer_verbs()
agent.clear_post_ai_verbs()
```

## Lifecycle Hooks

### on_swml_request()

Called before SWML is generated for each request.

```python
def on_swml_request(
    self,
    request_data: dict = None,
    callback_path: str = None,
    request = None
) -> None
```

**Example:**

```python
def on_swml_request(self, request_data=None, callback_path=None, request=None):
    call_data = (request_data or {}).get("call", {})
    caller = call_data.get("from", "")

    if caller in self.vip_numbers:
        self.prompt_add_section("VIP", "This is a VIP customer.")
```

### on_summary()

Called when a post-prompt summary is received.

```python
def on_summary(
    self,
    summary: dict = None,
    raw_data: dict = None
) -> None
```

**Example:**

```python
def on_summary(self, summary=None, raw_data=None):
    if summary:
        # Log or store the conversation summary
        print(f"Call summary: {summary}")
```

## Server Methods

### run()

Start the HTTP server.

```python
def run(self) -> None
```

### get_full_url()

Get the full URL for this agent's endpoint.

```python
def get_full_url(self, include_auth: bool = False) -> str
```

## Class Attributes

### PROMPT_SECTIONS

Declarative prompt definition.

```python
class MyAgent(AgentBase):
    PROMPT_SECTIONS = {
        "Role": "You are a helpful assistant.",
        "Guidelines": ["Be concise", "Be accurate"],
        "Personality": {
            "body": "You are friendly.",
            "bullets": ["Use casual language"]
        }
    }
```

## Complete Example

```python
#!/usr/bin/env python3
from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult


class CustomerServiceAgent(AgentBase):
    """A complete customer service agent example."""

    def __init__(self):
        super().__init__(
            name="customer-service",
            route="/support",
            port=3000,
            auto_answer=True,
            record_call=True,
            record_stereo=True
        )

        # Configure voice
        self.add_language("English", "en-US", "rime.spore")

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
                "Use the lookup_order function for order inquiries",
                "Transfer to a human if you cannot help"
            ]
        )

        # Set global context
        self.set_global_data({
            "company": "Acme Corp",
            "hours": "9am-5pm EST"
        })

        # Configure AI behavior
        self.set_params({
            "end_of_speech_timeout": 1000,
            "attention_timeout": 15000,
            "barge_match_string": "agent|human|representative"
        })

        # Add recognition hints
        self.add_hints(["Acme", "order number", "tracking"])

        # Post-call summary
        self.set_post_prompt(json_schema={
            "type": "object",
            "properties": {
                "resolved": {"type": "boolean"},
                "category": {"type": "string"},
                "summary": {"type": "string"}
            }
        })

    @AgentBase.tool(
        name="lookup_order",
        description="Look up an order by order number",
        parameters={
            "order_number": {
                "type": "string",
                "description": "The order number to look up"
            }
        },
        fillers=["Let me look that up", "One moment please"]
    )
    def lookup_order(self, args, raw_data):
        order_num = args.get("order_number")
        # In real implementation, query database
        return SwaigFunctionResult(
            f"Order {order_num} was shipped on Monday and should arrive by Friday."
        )

    @AgentBase.tool(
        name="transfer_to_human",
        description="Transfer the call to a human agent",
        parameters={}
    )
    def transfer_to_human(self, args, raw_data):
        return (SwaigFunctionResult("I'll transfer you to a support specialist.")
                .add_action("transfer", {"dest": "sip:support@acme.com"}))

    def on_summary(self, summary=None, raw_data=None):
        if summary:
            print(f"Call completed: {summary}")


if __name__ == "__main__":
    agent = CustomerServiceAgent()
    agent.run()
```
