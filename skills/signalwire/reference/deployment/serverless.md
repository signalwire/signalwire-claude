# Serverless Deployment Reference

Deploy SignalWire AI Agents in serverless environments including AWS Lambda, Google Cloud Functions, Azure Functions, and CGI.

## Import

```python
from signalwire_agents import AgentBase, SwaigFunctionResult
```

## Automatic Environment Detection

The SDK automatically detects the execution environment and handles request/response formats:

| Environment | Detection Method |
|-------------|------------------|
| AWS Lambda | `AWS_LAMBDA_FUNCTION_NAME`, `LAMBDA_TASK_ROOT` env vars |
| Google Cloud Functions | `FUNCTION_TARGET`, `K_SERVICE`, `GOOGLE_CLOUD_PROJECT` env vars |
| Azure Functions | `AZURE_FUNCTIONS_ENVIRONMENT`, `FUNCTIONS_WORKER_RUNTIME` env vars |
| CGI | `GATEWAY_INTERFACE` env var |
| HTTP Server | Default (no env vars) |

## Platform Comparison

| Platform | Entry Point | Max Timeout | Recommended Memory |
|----------|-------------|-------------|-------------------|
| AWS Lambda | `lambda_handler(event, context)` | 15 min | 512 MB+ |
| Google Cloud Functions | `main(request)` | 60 min (Gen 2) | 512 MB+ |
| Azure Functions | `main(req: func.HttpRequest)` | 10 min | 512 MB+ |

---

## AWS Lambda

### Handler Pattern

```python
#!/usr/bin/env python3
"""AWS Lambda handler for SignalWire agent."""

import os
from signalwire_agents import AgentBase, SwaigFunctionResult


class MyAgent(AgentBase):
    """My agent for AWS Lambda deployment."""

    def __init__(self):
        super().__init__(name="my-lambda-agent")

        self._configure_prompts()
        self.add_language("English", "en-US", "rime.spore")
        self._setup_functions()

    def _configure_prompts(self):
        self.prompt_add_section(
            "Role",
            "You are a helpful assistant deployed on AWS Lambda."
        )

        self.prompt_add_section(
            "Guidelines",
            bullets=[
                "Be concise and helpful",
                "Use available functions when appropriate"
            ]
        )

    def _setup_functions(self):
        @self.tool(
            description="Look up an order by ID",
            parameters={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID to look up"
                    }
                },
                "required": ["order_id"]
            }
        )
        def lookup_order(args, raw_data):
            order_id = args.get("order_id")
            # Query DynamoDB or other backend
            return SwaigFunctionResult(f"Order {order_id}: Shipped, arriving Friday")

        @self.tool(description="Get platform runtime information")
        def get_platform_info(args, raw_data):
            region = os.getenv("AWS_REGION", "unknown")
            function_name = os.getenv("AWS_LAMBDA_FUNCTION_NAME", "unknown")
            memory = os.getenv("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", "unknown")
            return SwaigFunctionResult(
                f"Running on AWS Lambda. Function: {function_name}, "
                f"Region: {region}, Memory: {memory}MB."
            )


# CRITICAL: Create agent instance OUTSIDE handler for cold start optimization
agent = MyAgent()


def lambda_handler(event, context):
    """AWS Lambda entry point.

    Args:
        event: Lambda event (API Gateway request)
        context: Lambda context with runtime info

    Returns:
        API Gateway response dict
    """
    return agent.run(event, context)
```

### requirements.txt

```
signalwire-agents>=1.0.10
h11>=0.13,<0.15
fastapi
mangum
uvicorn
```

### Lambda Response Format

The SDK returns Lambda-compatible responses:

```python
{
    "statusCode": 200,
    "headers": {"Content-Type": "application/json"},
    "body": "..."  # JSON string
}
```

### API Gateway Setup

- Use HTTP API (recommended) or REST API
- Create routes for `GET /`, `POST /`, `POST /swaig`, and `ANY /{proxy+}`
- Enable auto-deploy for the `$default` stage
- Set Lambda timeout to 30s+ for voice calls

### Environment Variables

```bash
# Authentication
SWML_BASIC_AUTH_USER=admin
SWML_BASIC_AUTH_PASSWORD=your-secure-password

# Proxy URL (required for SWAIG callbacks)
SWML_PROXY_URL_BASE=https://your-api-id.execute-api.us-east-1.amazonaws.com

# SignalWire credentials (if using Fabric API)
SIGNALWIRE_SPACE_NAME=your-space
SIGNALWIRE_PROJECT_ID=your-project-id
SIGNALWIRE_TOKEN=your-token
```

### Deploy Script Example

```bash
#!/bin/bash
# Deploy to AWS Lambda

FUNCTION_NAME="${1:-signalwire-agent}"
REGION="${2:-us-east-1}"
RUNTIME="python3.11"
HANDLER="handler.lambda_handler"
MEMORY_SIZE=512
TIMEOUT=30

# Build with Docker for correct architecture
docker run --rm \
    --platform linux/amd64 \
    -v "$(pwd):/var/task:ro" \
    -v "$PACKAGE_DIR:/var/output" \
    -w /var/task \
    public.ecr.aws/lambda/python:3.11 \
    bash -c "pip install -r requirements.txt -t /var/output --quiet && cp handler.py /var/output/"

# Create deployment package
cd "$PACKAGE_DIR" && zip -r function.zip . -q

# Deploy
aws lambda create-function \
    --function-name "$FUNCTION_NAME" \
    --runtime "$RUNTIME" \
    --handler "$HANDLER" \
    --zip-file "fileb://function.zip" \
    --memory-size "$MEMORY_SIZE" \
    --timeout "$TIMEOUT" \
    --region "$REGION" \
    --environment "Variables={SWML_BASIC_AUTH_USER=admin,SWML_BASIC_AUTH_PASSWORD=secret}"
```

---

## Google Cloud Functions

### Handler Pattern

```python
#!/usr/bin/env python3
"""Google Cloud Functions handler for SignalWire agent."""

import os
from signalwire_agents import AgentBase, SwaigFunctionResult


class MyAgent(AgentBase):
    """My agent for Google Cloud Functions deployment."""

    def __init__(self):
        super().__init__(name="my-gcloud-agent")

        self._configure_prompts()
        self.add_language("English", "en-US", "rime.spore")
        self._setup_functions()

    def _configure_prompts(self):
        self.prompt_add_section(
            "Role",
            "You are a helpful assistant deployed on Google Cloud Functions."
        )

    def _setup_functions(self):
        @self.tool(
            description="Say hello to a user",
            parameters={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the person to greet"
                    }
                },
                "required": ["name"]
            }
        )
        def say_hello(args, raw_data):
            name = args.get("name", "World")
            return SwaigFunctionResult(f"Hello {name}!")

        @self.tool(description="Get platform runtime information")
        def get_platform_info(args, raw_data):
            import urllib.request

            # Gen 2 Cloud Functions run on Cloud Run
            service = os.getenv("K_SERVICE", "unknown")
            revision = os.getenv("K_REVISION", "unknown")

            # Query metadata server for project ID
            project = os.getenv("GOOGLE_CLOUD_PROJECT", "unknown")
            if project == "unknown":
                try:
                    req = urllib.request.Request(
                        "http://metadata.google.internal/computeMetadata/v1/project/project-id",
                        headers={"Metadata-Flavor": "Google"}
                    )
                    with urllib.request.urlopen(req, timeout=2) as resp:
                        project = resp.read().decode()
                except Exception:
                    pass

            return SwaigFunctionResult(
                f"Running on Google Cloud Functions Gen 2. "
                f"Service: {service}, Revision: {revision}, Project: {project}."
            )


# Create agent instance outside handler for warm starts
agent = MyAgent()


def main(request):
    """Google Cloud Functions entry point.

    Args:
        request: Flask request object

    Returns:
        Flask response
    """
    return agent.run(request)
```

### requirements.txt

```
signalwire-agents>=1.0.10
functions-framework>=3.0.0
```

### Deployment

```bash
gcloud functions deploy my-agent \
    --gen2 \
    --runtime python311 \
    --trigger-http \
    --allow-unauthenticated \
    --entry-point main \
    --region us-central1 \
    --memory 512MB \
    --timeout 60s \
    --min-instances 0 \
    --max-instances 10
```

### Set Environment Variables

```bash
gcloud functions deploy my-agent \
    --region us-central1 \
    --gen2 \
    --update-env-vars SWML_BASIC_AUTH_USER=myuser,SWML_BASIC_AUTH_PASSWORD=mypass
```

---

## Azure Functions

### Handler Pattern

```python
#!/usr/bin/env python3
"""Azure Functions handler for SignalWire agent."""

import os
import azure.functions as func
from signalwire_agents import AgentBase, SwaigFunctionResult


class MyAgent(AgentBase):
    """My agent for Azure Functions deployment."""

    def __init__(self):
        super().__init__(name="my-azure-agent")

        self._configure_prompts()
        self.add_language("English", "en-US", "rime.spore")
        self._setup_functions()

    def _configure_prompts(self):
        self.prompt_add_section(
            "Role",
            "You are a helpful assistant deployed on Azure Functions."
        )

    def _setup_functions(self):
        @self.tool(
            description="Say hello to a user",
            parameters={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the person to greet"
                    }
                },
                "required": ["name"]
            }
        )
        def say_hello(args, raw_data):
            name = args.get("name", "World")
            return SwaigFunctionResult(f"Hello {name}!")

        @self.tool(description="Get Azure deployment information")
        def get_platform_info(args, raw_data):
            function_name = os.getenv("WEBSITE_SITE_NAME", "unknown")
            region = os.getenv("REGION_NAME", "unknown")
            runtime = os.getenv("FUNCTIONS_WORKER_RUNTIME", "unknown")
            version = os.getenv("FUNCTIONS_EXTENSION_VERSION", "unknown")

            return SwaigFunctionResult(
                f"Running on Azure Functions. "
                f"App: {function_name}, Region: {region}, "
                f"Runtime: {runtime}, Version: {version}."
            )


# Create agent instance outside handler for warm starts
agent = MyAgent()


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions entry point.

    Args:
        req: Azure Functions HTTP request object

    Returns:
        Azure Functions HTTP response
    """
    return agent.run(req)
```

### function.json

```json
{
    "scriptFile": "__init__.py",
    "bindings": [
        {
            "authLevel": "anonymous",
            "type": "httpTrigger",
            "direction": "in",
            "name": "req",
            "methods": ["get", "post"],
            "route": "{*path}"
        },
        {
            "type": "http",
            "direction": "out",
            "name": "$return"
        }
    ]
}
```

### host.json

```json
{
    "version": "2.0",
    "extensionBundle": {
        "id": "Microsoft.Azure.Functions.ExtensionBundle",
        "version": "[4.*, 5.0.0)"
    }
}
```

### requirements.txt

```
azure-functions>=1.17.0
signalwire-agents>=1.0.10
```

### Deployment

```bash
# Create function app
az functionapp create \
    --name my-signalwire-agent \
    --resource-group my-resource-group \
    --consumption-plan-location eastus \
    --runtime python \
    --runtime-version 3.11 \
    --functions-version 4 \
    --storage-account mystorageaccount

# Deploy code
func azure functionapp publish my-signalwire-agent

# Set environment variables
az functionapp config appsettings set \
    --name my-signalwire-agent \
    --resource-group my-resource-group \
    --settings SWML_BASIC_AUTH_USER=user SWML_BASIC_AUTH_PASSWORD=pass
```

---

## CGI Mode

For traditional CGI deployments (Apache, nginx with FastCGI):

```python
#!/usr/bin/env python3
from signalwire_agents import AgentBase, SwaigFunctionResult


class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="cgi-agent")
        self.add_language("English", "en-US", "rime.spore")
        self.prompt_add_section("Role", "You are a helpful assistant.")


if __name__ == "__main__":
    agent = MyAgent()
    agent.run(force_mode="cgi")
```

### CGI Configuration (Apache)

```apache
ScriptAlias /agent /var/www/cgi-bin/agent.py
<Directory /var/www/cgi-bin>
    Options +ExecCGI
    AddHandler cgi-script .py
</Directory>
```

---

## Force Mode Override

Force a specific execution mode during development or testing:

```python
# Force specific modes
agent.run(force_mode="lambda")
agent.run(force_mode="google_cloud_function")
agent.run(force_mode="azure_function")
agent.run(force_mode="cgi")
```

---

## Multi-Agent Serverless

Deploy multiple agents in a single serverless function using AgentServer:

```python
from signalwire_agents import AgentBase, AgentServer, SwaigFunctionResult


class SalesAgent(AgentBase):
    def __init__(self):
        super().__init__(name="sales", route="/sales")
        self.prompt_add_section("Role", "You are a sales specialist.")
        self.add_language("English", "en-US", "rime.spore")


class SupportAgent(AgentBase):
    def __init__(self):
        super().__init__(name="support", route="/support")
        self.prompt_add_section("Role", "You are a support specialist.")
        self.add_language("English", "en-US", "rime.spore")


# Create server with multiple agents
server = AgentServer()
server.register(SalesAgent(), "/sales")
server.register(SupportAgent(), "/support")


# AWS Lambda
def lambda_handler(event, context):
    return server.run(event, context)


# Google Cloud
def main(request):
    return server.run(request)


# Azure
def main(req):
    return server.run(req)
```

---

## DataMap for Serverless

DataMap enables SWAIG functions that execute on SignalWire servers without requiring webhook callbacks - ideal for reducing serverless complexity:

```python
from signalwire_agents import AgentBase
from signalwire_agents.core.data_map import DataMap
from signalwire_agents.core.function_result import SwaigFunctionResult


class APIAgent(AgentBase):
    def __init__(self):
        super().__init__(name="api-agent")
        self.add_language("English", "en-US", "rime.spore")
        self._setup_datamaps()

    def _setup_datamaps(self):
        # Weather lookup via external API (no local handler needed)
        weather = (
            DataMap("check_weather")
            .purpose("Check weather conditions")
            .parameter("location", "string", "City or zip code", required=True)
            .webhook("GET", "https://api.weather.com/v1/current?q=${enc:args.location}")
            .output(SwaigFunctionResult(
                "Current conditions in ${args.location}: ${response.condition}, ${response.temp}°F"
            ))
            .fallback_output(SwaigFunctionResult("Weather service is currently unavailable"))
        )

        # Order status lookup
        order_status = (
            DataMap("check_order")
            .purpose("Check order status")
            .parameter("order_id", "string", "Order number", required=True)
            .webhook(
                "GET",
                "https://api.orders.com/status/${enc:args.order_id}",
                headers={"Authorization": "Bearer ${env.API_KEY}"}
            )
            .output(SwaigFunctionResult(
                "Order ${args.order_id}: ${response.status}. "
                "Expected delivery: ${response.delivery_date}"
            ))
        )

        # Expression-based control (no API call)
        volume_control = (
            DataMap("set_volume")
            .purpose("Control audio volume")
            .parameter("level", "string", "Volume level", required=True)
            .expression("${args.level}", r"high|loud|up",
                SwaigFunctionResult("Volume increased").add_action("volume", 100))
            .expression("${args.level}", r"low|quiet|down",
                SwaigFunctionResult("Volume decreased").add_action("volume", 30))
            .expression("${args.level}", r"mute|off",
                SwaigFunctionResult("Audio muted").add_action("mute", True))
        )

        # Register all DataMaps
        self.register_swaig_function(weather.to_swaig_function())
        self.register_swaig_function(order_status.to_swaig_function())
        self.register_swaig_function(volume_control.to_swaig_function())


agent = APIAgent()

def lambda_handler(event, context):
    return agent.run(event, context)
```

### DataMap Variable Patterns

```
${args.param}              # Function argument value
${enc:args.param}          # URL-encoded argument
${lc:args.param}           # Lowercase argument
${fmt_ph:args.phone}       # Format as phone number
${response.field}          # API response field
${response.arr[0]}         # Array element
${global_data.key}         # Global session data
${meta_data.key}           # Call metadata
${env.VAR_NAME}            # Environment variable
```

---

## Request Flow

```
┌──────────────┐      ┌─────────────────┐      ┌──────────────────┐
│  SignalWire  │──────│  API Gateway/   │──────│  Cloud Function  │
│   Platform   │      │  HTTP Trigger   │      │  (Your Agent)    │
└──────────────┘      └─────────────────┘      └──────────────────┘
       │                      │                        │
       │   POST /             │                        │
       │─────────────────────>│───────────────────────>│
       │                      │     Returns SWML       │
       │<─────────────────────│<───────────────────────│
       │                      │                        │
       │   POST /swaig        │                        │
       │─────────────────────>│───────────────────────>│
       │                      │  Execute SWAIG func    │
       │<─────────────────────│<───────────────────────│
```

---

## Authentication in Serverless

All serverless modes support HTTP Basic authentication:

```python
# Via environment variables (recommended)
# Set SWML_BASIC_AUTH_USER and SWML_BASIC_AUTH_PASSWORD

# Or via constructor
agent = MyAgent(basic_auth=("username", "password"))
```

Authentication is checked automatically for each request. Failed auth returns 401 with `WWW-Authenticate` header.

---

## Testing Serverless Locally

### Using swaig-test CLI

```bash
# Test AWS Lambda locally
swaig-test handler.py --simulate-serverless lambda --dump-swml

# Test Google Cloud Functions
swaig-test main.py --simulate-serverless cloud_function --dump-swml

# Test Azure Functions
swaig-test function_app/__init__.py --simulate-serverless azure_function --dump-swml

# Test specific function
swaig-test handler.py --exec say_hello --args '{"name": "Alice"}'
```

### Testing Deployed Endpoints

```bash
# Test SWML output
curl -u username:password https://your-endpoint/

# Test SWAIG function
curl -u username:password -X POST https://your-endpoint/swaig \
    -H 'Content-Type: application/json' \
    -d '{
        "function": "say_hello",
        "argument": {
            "parsed": [{"name": "Alice"}]
        }
    }'
```

---

## Best Practices

### 1. Instantiate Agent Outside Handler

```python
# CORRECT - Instantiate once, reuse across invocations
agent = MyAgent()

def lambda_handler(event, context):
    return agent.run(event, context)

# WRONG - Creates new agent on every invocation (slow, wasteful)
def lambda_handler(event, context):
    agent = MyAgent()
    return agent.run(event, context)
```

### 2. Handle Cold Starts

- Minimize initialization code in `__init__`
- Use lazy loading for heavy dependencies
- Keep deployment package size small
- Consider provisioned concurrency for latency-sensitive applications

### 3. Configure Appropriate Timeouts

| Use Case | Recommended Timeout |
|----------|---------------------|
| Simple agent | 30 seconds |
| Complex voice interactions | 60+ seconds |
| External API calls | 60+ seconds |

### 4. Handle Statelessness

Serverless functions are stateless. Don't rely on:
- Local files (use S3, Cloud Storage, or external databases)
- In-memory state between invocations
- Instance variables that persist

Use instead:
- `set_global_data()` for session state
- DataMap for API integrations
- External storage for persistence

### 5. Minimize Dependencies

```
# Keep requirements.txt minimal
signalwire-agents>=1.0.10
# Only add what you actually use
```

### 6. Use Environment Variables

```python
import os

# Get credentials from environment
api_key = os.getenv("MY_API_KEY")
db_connection = os.getenv("DATABASE_URL")
```

---

## Differences from Server-Based Deployment

| Aspect | Server-Based | Serverless |
|--------|--------------|------------|
| Entry Point | `agent.run()` | Platform-specific handler |
| Instantiation | Inside main block | Outside handler |
| Port Binding | Yes (default 3000) | No - HTTP trigger |
| Lifecycle | Persistent | Per-request |
| State | In-memory (persistent) | Lost after execution |
| Timeout | No limit | Platform-specific (10-60 min) |
| Scaling | Manual | Auto-scaling |

---

## See Also

- [Agent Base Reference](agent-base.md) - Core agent documentation
- [DataMap Advanced](datamap-advanced.md) - Server-side function details
- [Environment Variables](environment-variables.md) - Configuration options
- [Dynamic Configuration](dynamic-configuration.md) - Per-request customization
