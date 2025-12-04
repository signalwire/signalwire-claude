# Dynamic Configuration Reference

Dynamic configuration allows you to customize agent behavior per-request based on query parameters, headers, or request body data. This is essential for multi-tenant applications, personalization, and request-specific customization.

## Import

```python
from signalwire_agents import AgentBase
```

## Dynamic Config Callback

### set_dynamic_config_callback()

Set a callback function that's called for each request to dynamically configure the agent.

```python
def set_dynamic_config_callback(
    self,
    callback: Callable[[dict, dict, dict, 'AgentBase'], None]
) -> 'AgentBase'
```

**Parameters:**
- `callback` - Function with signature `(query_params, body_params, headers, agent)`

**Callback Arguments:**
- `query_params` - Dictionary of URL query parameters
- `body_params` - Dictionary of request body parameters
- `headers` - Dictionary of HTTP headers
- `agent` - The agent instance to configure

**Example:**

```python
def my_config(query_params, body_params, headers, agent):
    tier = query_params.get('tier', 'standard')

    if tier == 'premium':
        agent.add_skill("advanced_search")
        agent.add_language("English", "en-US", "elevenlabs.josh:eleven_turbo_v2_5")
        agent.set_params({"end_of_speech_timeout": 500})
        agent.prompt_add_section("Premium", "This is a premium customer. Provide extra attention.")

    agent.set_global_data({"tier": tier})

agent = MyAgent()
agent.set_dynamic_config_callback(my_config)
```

### What You Can Configure

The callback receives the actual agent instance, so you can call any AgentBase method:

```python
def dynamic_config(query_params, body_params, headers, agent):
    # Add skills based on request
    if query_params.get('enable_search'):
        agent.add_skill("web_search", {"api_key": "..."})

    # Modify language/voice based on caller
    language = headers.get('Accept-Language', 'en-US')
    if language.startswith('es'):
        agent.add_language("Spanish", "es-MX", "gcloud.es-MX-Neural2-A")
    else:
        agent.add_language("English", "en-US", "rime.spore")

    # Customize prompt based on tenant
    tenant_id = query_params.get('tenant')
    if tenant_id:
        agent.prompt_add_section("Tenant", f"You represent tenant {tenant_id}.")

    # Set parameters dynamically
    agent.set_params({
        "local_tz": query_params.get('timezone', 'America/New_York')
    })

    # Add global data
    agent.set_global_data({
        "tenant_id": tenant_id,
        "request_id": headers.get('X-Request-ID')
    })

    # Define tools dynamically
    agent.define_tool(
        name="custom_lookup",
        description="Look up tenant-specific data",
        handler=lambda args, raw: SwaigFunctionResult(f"Data for {tenant_id}")
    )
```

## Preserving Query Parameters

When using dynamic configuration, you may need to preserve query parameters for SWAIG callbacks.

### add_swaig_query_params()

Add query parameters that will be included in all SWAIG webhook URLs.

```python
def add_swaig_query_params(self, params: Dict[str, str]) -> 'AgentBase'
```

**Example:**

```python
def dynamic_config(query_params, body_params, headers, agent):
    tier = query_params.get('tier')

    if tier == 'premium':
        agent.add_skill('advanced_search')
        # Preserve tier param so SWAIG callbacks receive it too
        agent.add_swaig_query_params({'tier': tier})
```

### clear_swaig_query_params()

Clear all SWAIG query parameters.

```python
agent.clear_swaig_query_params()
```

## Routing Callbacks

### register_routing_callback()

Register a callback to determine request routing based on POST data.

```python
def register_routing_callback(
    self,
    callback_fn: Callable[[Request, Dict[str, Any]], Optional[str]],
    path: str = "/sip"
) -> None
```

**Parameters:**
- `callback_fn` - Function that returns a route string or None
- `path` - HTTP path for this routing endpoint

**Callback Return Values:**
- Return a route string to redirect to a different endpoint
- Return `None` to continue normal processing

**Example:**

```python
def route_by_caller(request, body):
    caller = body.get('call', {}).get('from', '')

    # Route VIP callers to premium agent
    if caller in VIP_NUMBERS:
        return '/premium'

    # Route by area code
    if caller.startswith('+1212'):
        return '/nyc-agent'

    # Continue normal processing
    return None

agent.register_routing_callback(route_by_caller, path="/route")
```

## Per-Request SWML Customization

### on_swml_request()

Override this method for per-request customization before SWML is generated.

```python
def on_swml_request(
    self,
    request_data: dict = None,
    callback_path: str = None,
    request = None
) -> Optional[dict]
```

**Parameters:**
- `request_data` - Request body data
- `callback_path` - The callback path being processed
- `request` - FastAPI Request object

**Returns:** Dictionary with modifications or None

**Example:**

```python
class MyAgent(AgentBase):
    def on_swml_request(self, request_data=None, callback_path=None, request=None):
        call_data = (request_data or {}).get("call", {})
        caller = call_data.get("from", "")

        # Customize based on caller
        if caller in self.vip_numbers:
            self.prompt_add_section("VIP", "This is a VIP customer. Prioritize their needs.")

        # Return None or modifications
        return None
```

## URL and Webhook Overrides

### set_web_hook_url()

Override the default webhook URL for SWAIG functions.

```python
agent.set_web_hook_url("https://custom-domain.com/agent")
```

### set_post_prompt_url()

Override the URL where post-prompt summaries are sent.

```python
agent.set_post_prompt_url("https://api.example.com/summaries")
```

### manual_set_proxy_url()

Manually set the proxy URL base for webhook callbacks.

```python
agent.manual_set_proxy_url("https://my-ngrok-url.ngrok.io")
```

## Function Includes

Include functions from external URLs.

### add_function_include()

```python
def add_function_include(
    self,
    url: str,
    functions: List[str],
    meta_data: Optional[Dict[str, Any]] = None
) -> 'AgentBase'
```

**Example:**

```python
agent.add_function_include(
    url="https://api.example.com/swaig",
    functions=["external_lookup", "external_search"],
    meta_data={"auth_token": "xyz123"}
)
```

### set_function_includes()

Set the complete list of function includes.

```python
agent.set_function_includes([
    {
        "url": "https://api1.example.com/swaig",
        "functions": ["func1", "func2"]
    },
    {
        "url": "https://api2.example.com/swaig",
        "functions": ["func3"]
    }
])
```

## Complete Multi-Tenant Example

```python
#!/usr/bin/env python3
from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult


class MultiTenantAgent(AgentBase):
    """Agent that configures itself based on tenant."""

    TENANT_CONFIGS = {
        "acme": {
            "name": "Acme Corp",
            "voice": "elevenlabs.josh:eleven_turbo_v2_5",
            "skills": ["web_search"],
            "timezone": "America/New_York"
        },
        "globex": {
            "name": "Globex Inc",
            "voice": "rime.spore",
            "skills": ["datetime", "math"],
            "timezone": "America/Los_Angeles"
        }
    }

    def __init__(self):
        super().__init__(name="multi-tenant", port=3000)

        # Set dynamic configuration callback
        self.set_dynamic_config_callback(self.configure_for_tenant)

        # Base configuration (applied to all tenants)
        self.prompt_add_section("Role", "You are a helpful assistant.")

    def configure_for_tenant(self, query_params, body_params, headers, agent):
        tenant_id = query_params.get('tenant', 'default')

        config = self.TENANT_CONFIGS.get(tenant_id, {
            "name": "Default",
            "voice": "rime.spore",
            "skills": [],
            "timezone": "UTC"
        })

        # Configure voice
        agent.add_language("English", "en-US", config["voice"])

        # Add tenant-specific skills
        for skill in config.get("skills", []):
            agent.add_skill(skill)

        # Customize prompt
        agent.prompt_add_section(
            "Company",
            f"You represent {config['name']}. Always refer to the company by name."
        )

        # Set timezone
        agent.set_params({"local_tz": config["timezone"]})

        # Set global data
        agent.set_global_data({
            "tenant_id": tenant_id,
            "company_name": config["name"]
        })

        # Preserve tenant in SWAIG callbacks
        agent.add_swaig_query_params({"tenant": tenant_id})

    @AgentBase.tool(
        name="get_company_info",
        description="Get information about the company",
        parameters={}
    )
    def get_company_info(self, args, raw_data):
        global_data = raw_data.get("global_data", {})
        company = global_data.get("company_name", "our company")
        return SwaigFunctionResult(f"You're speaking with {company}'s virtual assistant.")


if __name__ == "__main__":
    agent = MultiTenantAgent()
    agent.run()
```

**Usage:**
```bash
# Different tenants get different configurations
curl http://localhost:3000/?tenant=acme
curl http://localhost:3000/?tenant=globex
```

## Best Practices

1. **Keep callbacks fast** - The callback runs for every request
2. **Use add_swaig_query_params** - Preserve important params for callbacks
3. **Set defaults** - Always have fallback values
4. **Don't duplicate configuration** - Put common config in `__init__`
5. **Log tenant info** - For debugging multi-tenant issues

## See Also

- [Agent Base Reference](agent-base.md) - Complete AgentBase documentation
- [SIP Routing](sip-routing.md) - Request-based routing
- [Environment Variables](environment-variables.md) - Configuration options
