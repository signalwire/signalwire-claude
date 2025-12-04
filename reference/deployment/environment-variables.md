# Environment Variables Reference

Complete reference for environment variables used by SignalWire AI Agents SDK.

## SignalWire Authentication

Required for SignalWire platform features (Fabric API, calling, SMS).

| Variable | Description |
|----------|-------------|
| `SIGNALWIRE_SPACE_NAME` | Your SignalWire space (e.g., `myspace.signalwire.com` or just `myspace`) |
| `SIGNALWIRE_PROJECT_ID` | Project ID from SignalWire dashboard |
| `SIGNALWIRE_TOKEN` | API token from SignalWire dashboard |

**Example:**

```bash
export SIGNALWIRE_SPACE_NAME="myspace"
export SIGNALWIRE_PROJECT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export SIGNALWIRE_TOKEN="PTxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## Server Configuration

### SWML Proxy Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `SWML_PROXY_URL_BASE` | None | Base URL for SWML callbacks (required for SignalWire to reach your agent) |
| `SWML_SSL_ENABLED` | `false` | Enable HTTPS for callback URLs |

**Example:**

```bash
# Local development with ngrok
export SWML_PROXY_URL_BASE="https://abc123.ngrok.io"

# Production
export SWML_PROXY_URL_BASE="https://agent.mycompany.com"
export SWML_SSL_ENABLED="true"
```

### Basic Authentication

| Variable | Default | Description |
|----------|---------|-------------|
| `SWML_BASIC_AUTH_USER` | None | HTTP Basic Auth username |
| `SWML_BASIC_AUTH_PASSWORD` | None | HTTP Basic Auth password |

When set, all agent endpoints require authentication:

```bash
export SWML_BASIC_AUTH_USER="admin"
export SWML_BASIC_AUTH_PASSWORD="secretpassword"
```

URLs with embedded credentials:
```
https://admin:secretpassword@abc123.ngrok.io/agent
```

## Debug Webhooks

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG_WEBHOOK_URL` | None | URL to receive debug events |
| `DEBUG_WEBHOOK_LEVEL` | `0` | Debug verbosity (0=off, 1=basic, 2=verbose) |

**Debug Levels:**
- `0` - Disabled (default)
- `1` - Basic events (function calls, errors)
- `2` - Verbose (includes full transcripts, all events)

**Example:**

```bash
export DEBUG_WEBHOOK_URL="https://webhook.site/abc123"
export DEBUG_WEBHOOK_LEVEL="1"
```

## Skill Configuration

### OpenAI Skills

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | API key for OpenAI-powered skills |

### Google Search Skill

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Google API key for search |
| `GOOGLE_SEARCH_ENGINE_ID` | Custom Search Engine ID |

### Datasphere Skill

| Variable | Description |
|----------|-------------|
| `DATASPHERE_DEFAULT_SPACE_NAME` | SignalWire space for Datasphere |
| `DATASPHERE_DEFAULT_PROJECT_ID` | Project ID for Datasphere |
| `DATASPHERE_DEFAULT_TOKEN` | Token for Datasphere |

**Example:**

```bash
# Web search skill
export GOOGLE_API_KEY="AIza..."
export GOOGLE_SEARCH_ENGINE_ID="017..."

# OpenAI skills
export OPENAI_API_KEY="sk-..."
```

## Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `SWML_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `SWML_LOG_FORMAT` | `text` | Log format (`text` or `json`) |

**Example:**

```bash
# Verbose logging for development
export SWML_LOG_LEVEL="DEBUG"

# JSON logs for production (easier to parse)
export SWML_LOG_FORMAT="json"
```

## Serverless Deployment

### AWS Lambda

| Variable | Description |
|----------|-------------|
| `AWS_LAMBDA_FUNCTION_NAME` | Auto-set by AWS Lambda |
| `_HANDLER` | Lambda handler path |

### Google Cloud Functions

| Variable | Description |
|----------|-------------|
| `FUNCTION_TARGET` | Cloud Function entry point |
| `K_SERVICE` | Cloud Run service name |

### Azure Functions

| Variable | Description |
|----------|-------------|
| `FUNCTIONS_WORKER_RUNTIME` | Set to `python` |

The SDK auto-detects serverless environments and adjusts behavior accordingly.

## Development Environment

Example `.env` file for local development:

```bash
# SignalWire credentials
SIGNALWIRE_SPACE_NAME=myspace
SIGNALWIRE_PROJECT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
SIGNALWIRE_TOKEN=PTxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Proxy URL (use ngrok for local dev)
SWML_PROXY_URL_BASE=https://abc123.ngrok.io

# Optional: Basic auth
SWML_BASIC_AUTH_USER=admin
SWML_BASIC_AUTH_PASSWORD=dev123

# Debugging
DEBUG_WEBHOOK_URL=https://webhook.site/your-unique-id
DEBUG_WEBHOOK_LEVEL=1

# Logging
SWML_LOG_LEVEL=DEBUG

# Skills (as needed)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
GOOGLE_SEARCH_ENGINE_ID=017...
```

Load with python-dotenv:

```python
from dotenv import load_dotenv
load_dotenv()

from signalwire_agents import AgentBase
# ... rest of agent code
```

## Production Environment

Recommended production settings:

```bash
# Core credentials
SIGNALWIRE_SPACE_NAME=production-space
SIGNALWIRE_PROJECT_ID=prod-project-id
SIGNALWIRE_TOKEN=prod-token

# Production URL
SWML_PROXY_URL_BASE=https://agent.mycompany.com
SWML_SSL_ENABLED=true

# Security
SWML_BASIC_AUTH_USER=api
SWML_BASIC_AUTH_PASSWORD=<strong-random-password>

# Minimal logging
SWML_LOG_LEVEL=WARNING
SWML_LOG_FORMAT=json

# Debug off in production
DEBUG_WEBHOOK_LEVEL=0
```

## Docker Compose Example

```yaml
version: '3.8'
services:
  agent:
    build: .
    ports:
      - "3000:3000"
    environment:
      - SIGNALWIRE_SPACE_NAME=${SIGNALWIRE_SPACE_NAME}
      - SIGNALWIRE_PROJECT_ID=${SIGNALWIRE_PROJECT_ID}
      - SIGNALWIRE_TOKEN=${SIGNALWIRE_TOKEN}
      - SWML_PROXY_URL_BASE=${SWML_PROXY_URL_BASE}
      - SWML_BASIC_AUTH_USER=${SWML_BASIC_AUTH_USER}
      - SWML_BASIC_AUTH_PASSWORD=${SWML_BASIC_AUTH_PASSWORD}
      - DEBUG_WEBHOOK_LEVEL=0
```

## Environment Variable Precedence

1. **Constructor parameters** - Highest priority
2. **Environment variables** - Second priority
3. **Defaults** - Lowest priority

```python
# Constructor overrides env var
agent = AgentBase(
    name="my-agent",
    basic_auth=("user", "pass")  # Overrides SWML_BASIC_AUTH_*
)
```

## Checking Configuration

Verify your environment at runtime:

```python
import os

required_vars = [
    "SIGNALWIRE_SPACE_NAME",
    "SIGNALWIRE_PROJECT_ID",
    "SIGNALWIRE_TOKEN",
    "SWML_PROXY_URL_BASE"
]

missing = [v for v in required_vars if not os.getenv(v)]
if missing:
    print(f"Missing required env vars: {missing}")
```
