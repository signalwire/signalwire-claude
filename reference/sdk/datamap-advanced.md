# DataMap Advanced Reference

Complete reference for advanced DataMap features including expressions, webhooks with fallbacks, array processing, and error handling.

## Import

```python
from signalwire_agents import DataMap, create_simple_api_tool, create_expression_tool
from signalwire_agents.core.function_result import SwaigFunctionResult
```

## Basic DataMap Review

DataMap allows you to create server-side SWAIG functions that execute without needing a local webhook handler. The basic pattern:

```python
data_map = (DataMap("function_name")
    .purpose("Description of the function")
    .parameter("param", "string", "Description", required=True)
    .webhook("GET", "https://api.example.com/data?q=${args.param}")
    .output(SwaigFunctionResult("Result: ${response.data}")))

agent.register_swaig_function(data_map.to_swaig_function())
```

## Expressions (Pattern-Based Responses)

Expressions allow you to create functions that respond based on pattern matching without making API calls. This is ideal for control commands or routing logic.

### expression()

Add a pattern-based response to the DataMap.

```python
def expression(
    self,
    test_value: str,
    pattern: Union[str, Pattern],
    output: SwaigFunctionResult,
    nomatch_output: Optional[SwaigFunctionResult] = None
) -> 'DataMap'
```

**Parameters:**
- `test_value` - Template string to test (e.g., `"${args.command}"`)
- `pattern` - Regex pattern to match against
- `output` - SwaigFunctionResult to return when pattern matches
- `nomatch_output` - Optional result when pattern doesn't match

**Example - Playback Control:**

```python
playback_control = (DataMap("control_playback")
    .purpose("Control audio playback - start or stop")
    .parameter("command", "string", "The command: 'start' or 'stop'", required=True)
    .parameter("filename", "string", "Audio file to play", required=False)

    # Match "start" commands
    .expression(
        "${args.command}",
        r"start.*",
        SwaigFunctionResult("Starting playback").add_action(
            "playback_bg", {"file": "${args.filename}"}
        )
    )

    # Match "stop" commands
    .expression(
        "${args.command}",
        r"stop.*",
        SwaigFunctionResult("Stopping playback").add_action(
            "stop_playback_bg", {}
        )
    )
)
```

**Example - Transfer Routing:**

```python
transfer_router = (DataMap("route_call")
    .purpose("Route the call to the appropriate department")
    .parameter("department", "string", "Department name", required=True)

    .expression(
        "${args.department}",
        r"sales|marketing",
        SwaigFunctionResult("Transferring to sales").add_action(
            "transfer", {"dest": "sip:sales@company.com"}
        )
    )

    .expression(
        "${args.department}",
        r"support|help|technical",
        SwaigFunctionResult("Transferring to support").add_action(
            "transfer", {"dest": "sip:support@company.com"}
        )
    )

    .expression(
        "${args.department}",
        r"billing|accounts|payment",
        SwaigFunctionResult("Transferring to billing").add_action(
            "transfer", {"dest": "sip:billing@company.com"}
        )
    )
)
```

## Multiple Webhooks with Fallback

You can chain multiple webhooks that act as fallbacks if earlier ones fail.

```python
search_with_fallback = (DataMap("search")
    .purpose("Search for information with fallback APIs")
    .parameter("query", "string", "Search query", required=True)

    # Primary API
    .webhook("GET", "https://api.primary.com/search?q=${args.query}")
    .output(SwaigFunctionResult("Found: ${response.results[0].title}"))

    # Fallback API (used if primary fails)
    .webhook("GET", "https://api.backup.com/search?q=${args.query}")
    .output(SwaigFunctionResult("Found: ${response.data.title}"))

    # Final fallback output (used if all webhooks fail)
    .fallback_output(SwaigFunctionResult("Sorry, search is temporarily unavailable"))
)
```

## Webhook Configuration

### webhook()

Add a webhook API call to the DataMap.

```python
def webhook(
    self,
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    form_param: Optional[str] = None,
    input_args_as_params: bool = False,
    require_args: Optional[List[str]] = None
) -> 'DataMap'
```

**Parameters:**
- `method` - HTTP method (GET, POST, PUT, DELETE)
- `url` - API endpoint URL (supports `${args.param}` substitution)
- `headers` - Optional HTTP headers
- `form_param` - Send JSON body as single form parameter
- `input_args_as_params` - Merge function arguments into params
- `require_args` - Only execute if these arguments are present

### body()

Set the request body for POST/PUT webhooks.

```python
def body(self, data: Dict[str, Any]) -> 'DataMap'
```

**Example:**

```python
create_ticket = (DataMap("create_support_ticket")
    .purpose("Create a support ticket")
    .parameter("subject", "string", "Ticket subject", required=True)
    .parameter("description", "string", "Issue description", required=True)
    .parameter("priority", "string", "Priority level", enum=["low", "medium", "high"])

    .webhook("POST", "https://api.helpdesk.com/tickets",
             headers={"Authorization": "Bearer ${env.API_KEY}"})
    .body({
        "subject": "${args.subject}",
        "description": "${args.description}",
        "priority": "${args.priority}",
        "source": "voice_agent"
    })
    .output(SwaigFunctionResult("Ticket created with ID: ${response.ticket_id}"))
)
```

### params()

Set query parameters for the webhook (alias for body in some contexts).

```python
def params(self, data: Dict[str, Any]) -> 'DataMap'
```

## Array Processing with foreach

Process arrays from API responses using the foreach mechanism.

### foreach()

Configure array processing for webhook responses.

```python
def foreach(self, foreach_config: Dict[str, Any]) -> 'DataMap'
```

**Configuration keys:**
- `input_key` - Key in API response containing the array
- `output_key` - Name for the built string variable
- `max` - Maximum number of items to process (optional)
- `append` - Template string to append for each item (uses `${this.field}`)

**Example:**

```python
search_docs = (DataMap("search_documents")
    .purpose("Search documentation and return top results")
    .parameter("query", "string", "Search query", required=True)

    .webhook("POST", "https://api.docs.com/search",
             headers={"Authorization": "Bearer TOKEN"})
    .body({"query": "${args.query}", "limit": 5})

    .foreach({
        "input_key": "results",
        "output_key": "formatted_results",
        "max": 3,
        "append": "- ${this.title}: ${this.summary}\n"
    })

    .output(SwaigFunctionResult("Here's what I found:\n${formatted_results}"))
)
```

## Error Handling

### error_keys()

Specify JSON keys that indicate an error response.

```python
def error_keys(self, keys: List[str]) -> 'DataMap'
```

When any of these keys are present in the API response, the webhook is considered failed.

**Example:**

```python
api_call = (DataMap("get_user")
    .purpose("Get user information")
    .parameter("user_id", "string", "User ID", required=True)

    .webhook("GET", "https://api.example.com/users/${args.user_id}")
    .error_keys(["error", "error_message", "errors"])
    .output(SwaigFunctionResult("User: ${response.name}, Email: ${response.email}"))

    .fallback_output(SwaigFunctionResult("Unable to find user information"))
)
```

### global_error_keys()

Set error keys that apply to all webhooks in the DataMap.

```python
def global_error_keys(self, keys: List[str]) -> 'DataMap'
```

## Post-Webhook Expressions

You can add conditional logic that runs after a webhook completes.

### webhook_expressions()

Add expressions that run after the most recent webhook.

```python
def webhook_expressions(self, expressions: List[Dict[str, Any]]) -> 'DataMap'
```

**Example:**

```python
check_inventory = (DataMap("check_stock")
    .purpose("Check product availability")
    .parameter("product_id", "string", "Product ID", required=True)

    .webhook("GET", "https://api.store.com/inventory/${args.product_id}")
    .webhook_expressions([
        {
            "string": "${response.quantity}",
            "pattern": "^0$",
            "output": {"response": "Sorry, this product is out of stock"}
        },
        {
            "string": "${response.quantity}",
            "pattern": "^[1-9]$",
            "output": {"response": "Limited stock available: ${response.quantity} units"}
        }
    ])
    .output(SwaigFunctionResult("In stock: ${response.quantity} units available"))
)
```

## Helper Functions

### create_simple_api_tool()

Create a simple API tool with minimal configuration.

```python
from signalwire_agents import create_simple_api_tool

weather_tool = create_simple_api_tool(
    name="get_weather",
    url="https://api.weather.com/current?q=${args.city}&key=API_KEY",
    response_template="Weather in ${args.city}: ${response.condition}, ${response.temp}°F",
    parameters={
        "city": {
            "type": "string",
            "description": "City name",
            "required": True
        }
    }
)

agent.register_swaig_function(weather_tool.to_swaig_function())
```

### create_expression_tool()

Create an expression-based tool for pattern matching.

```python
from signalwire_agents import create_expression_tool

control_tool = create_expression_tool(
    name="volume_control",
    patterns={
        "${args.command}": ("up|increase|louder", SwaigFunctionResult("Volume increased")),
        "${args.command}": ("down|decrease|quieter", SwaigFunctionResult("Volume decreased")),
        "${args.command}": ("mute|silent", SwaigFunctionResult("Audio muted"))
    },
    parameters={
        "command": {
            "type": "string",
            "description": "Volume command",
            "required": True
        }
    }
)

agent.register_swaig_function(control_tool.to_swaig_function())
```

## Variable Substitution

DataMap supports variable substitution in URLs, bodies, and outputs:

| Pattern | Description |
|---------|-------------|
| `${args.param}` | Function argument value |
| `${response.field}` | API response field |
| `${response.nested.field}` | Nested response field |
| `${response.array[0].field}` | Array element field |
| `${env.VAR_NAME}` | Environment variable |
| `${this.field}` | Current item in foreach loop |
| `${formatted_results}` | Output from foreach processing |

## Complete Complex Example

```python
#!/usr/bin/env python3
from signalwire_agents import AgentBase, DataMap
from signalwire_agents.core.function_result import SwaigFunctionResult


class DataMapDemoAgent(AgentBase):
    def __init__(self):
        super().__init__(name="datamap-demo", port=3000)

        self.add_language("English", "en-US", "rime.spore")
        self.prompt_add_section("Role", "You are a helpful assistant with access to various tools.")

        # Register DataMap functions
        self._register_datamap_functions()

    def _register_datamap_functions(self):
        # Expression-based playback control
        playback = (DataMap("control_audio")
            .purpose("Control background audio playback")
            .parameter("action", "string", "Action: start, stop, or pause", required=True)
            .parameter("file_url", "string", "Audio file URL for start action")
            .expression("${args.action}", r"start",
                SwaigFunctionResult("Starting audio").add_action("playback_bg", {"file": "${args.file_url}"}))
            .expression("${args.action}", r"stop|pause",
                SwaigFunctionResult("Stopping audio").add_action("stop_playback_bg", {})))

        # API call with error handling and fallback
        lookup = (DataMap("lookup_order")
            .purpose("Look up order status by order number")
            .parameter("order_number", "string", "The order number", required=True)
            .webhook("GET", "https://api.orders.com/v1/orders/${args.order_number}",
                     headers={"Authorization": "Bearer ${env.ORDERS_API_KEY}"})
            .error_keys(["error", "not_found"])
            .output(SwaigFunctionResult(
                "Order ${args.order_number}: Status is ${response.status}. "
                "Shipped on ${response.ship_date}. "
                "Tracking: ${response.tracking_number}"
            ))
            .fallback_output(SwaigFunctionResult(
                "I couldn't find order ${args.order_number}. Please verify the number."
            )))

        # Array processing for search results
        search = (DataMap("search_products")
            .purpose("Search product catalog")
            .parameter("query", "string", "Search keywords", required=True)
            .webhook("GET", "https://api.store.com/products/search?q=${args.query}&limit=5")
            .foreach({
                "input_key": "products",
                "output_key": "product_list",
                "max": 3,
                "append": "- ${this.name} ($${this.price}): ${this.description}\n"
            })
            .output(SwaigFunctionResult("Found these products:\n${product_list}")))

        # Register all functions
        self.register_swaig_function(playback.to_swaig_function())
        self.register_swaig_function(lookup.to_swaig_function())
        self.register_swaig_function(search.to_swaig_function())


if __name__ == "__main__":
    agent = DataMapDemoAgent()
    agent.run()
```

## See Also

- [SWAIG Functions Reference](swaig-functions.md) - Function definition patterns
- [Function Result Reference](function-result.md) - SwaigFunctionResult actions
- [Common Patterns](../patterns/common-patterns.md) - Best practices
