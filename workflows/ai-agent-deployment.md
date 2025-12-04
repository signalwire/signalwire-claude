# AI Agent Deployment

## Overview

Deploy SignalWire AI agents to production using traditional servers, serverless platforms, or multi-agent architectures. This guide covers deployment patterns, monitoring, and production tips.

## Related Workflows

- [Voice AI](voice-ai.md) - Overview and decision guide
- [AI Agent SDK Basics](ai-agent-sdk-basics.md) - Python SDK fundamentals
- [AI Agent Prompting](ai-agent-prompting.md) - Best practices for prompts
- [AI Agent Functions](ai-agent-functions.md) - SWAIG function patterns
- [Webhooks & Events](webhooks-events.md) - Monitoring and observability

## Deployment Options

### 1. Traditional Server

Best for:
- Long-running applications
- Multiple agents on one server
- Full control over environment

### 2. Serverless

Best for:
- Auto-scaling requirements
- Pay-per-use pricing
- Minimal infrastructure management

### 3. Multi-Agent Server

Best for:
- Multiple specialized agents
- Shared infrastructure
- Centralized management

## Traditional Server Deployment

### Basic Deployment

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = ["signalwire-agents"]
# ///

import os
from my_agent import MyAgent

if __name__ == "__main__":
    agent = MyAgent()
    agent.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )
```

### Production Server Setup

```python
import os
import logging
from my_agent import MyAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    # Load configuration from environment
    agent = MyAgent(
        name="production-agent",
        port=int(os.getenv('PORT', 5000)),
        host=os.getenv('HOST', '0.0.0.0'),
        basic_auth=(
            os.getenv('SWML_BASIC_AUTH_USER'),
            os.getenv('SWML_BASIC_AUTH_PASSWORD')
        ) if os.getenv('SWML_BASIC_AUTH_USER') else None
    )

    # Run with production settings
    agent.run(debug=False)
```

### Docker Deployment

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run agent
CMD ["python", "agent.py"]
```

**requirements.txt:**

```
signalwire-agents
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  ai-agent:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SIGNALWIRE_SPACE_NAME=${SIGNALWIRE_SPACE_NAME}
      - SIGNALWIRE_PROJECT_ID=${SIGNALWIRE_PROJECT_ID}
      - SIGNALWIRE_TOKEN=${SIGNALWIRE_TOKEN}
      - SWML_PROXY_URL_BASE=https://your-domain.com
      - PORT=5000
    restart: unless-stopped
```

**Deploy:**

```bash
docker-compose up -d
```

### systemd Service (Linux)

**/etc/systemd/system/ai-agent.service:**

```ini
[Unit]
Description=SignalWire AI Agent
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ai-agent
Environment="PORT=5000"
Environment="SIGNALWIRE_SPACE_NAME=myspace"
Environment="SIGNALWIRE_PROJECT_ID=xxxx"
Environment="SIGNALWIRE_TOKEN=xxxx"
ExecStart=/usr/bin/python3 /opt/ai-agent/agent.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl enable ai-agent
sudo systemctl start ai-agent
sudo systemctl status ai-agent
```

## Serverless Deployment

### Key Differences for Serverless

- Agent instantiated **outside** the handler function (cold start optimization)
- Use `@self.tool` inside `_setup_functions()` method (not `@AgentBase.tool` at class level)
- No port binding needed - HTTP trigger handles routing

### AWS Lambda

**lambda_function.py:**

```python
from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult

# CRITICAL: Create agent instance OUTSIDE handler for cold start optimization
class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="lambda-agent")
        self.add_language("English", "en-US", "rime.spore")
        self._setup_functions()

    def _setup_functions(self):
        # Use @self.tool inside method for serverless
        @self.tool(
            name="check_balance",
            description="Check account balance",
            parameters={
                "account_number": {"type": "string", "description": "Account number"}
            }
        )
        def check_balance(args, raw_data):
            account_number = args.get("account_number")
            return SwaigFunctionResult(f"Balance for {account_number}: $1,234.56")

# Instantiate outside handler
agent = MyAgent()

# AWS Lambda handler
def lambda_handler(event, context):
    return agent.run(event, context)
```

**Deploy with SAM:**

**template.yaml:**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  AIAgentFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: lambda_function.lambda_handler
      Runtime: python3.11
      CodeUri: .
      MemorySize: 512
      Timeout: 30
      Environment:
        Variables:
          SIGNALWIRE_SPACE_NAME: !Ref SignalWireSpaceName
          SIGNALWIRE_PROJECT_ID: !Ref SignalWireProjectID
          SIGNALWIRE_TOKEN: !Ref SignalWireToken
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /swml
            Method: POST

Parameters:
  SignalWireSpaceName:
    Type: String
  SignalWireProjectID:
    Type: String
  SignalWireToken:
    Type: String
    NoEcho: true
```

**Deploy:**

```bash
sam build
sam deploy --guided
```

### Google Cloud Functions

**main.py:**

```python
from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="gcf-agent")
        self.add_language("English", "en-US", "rime.spore")
        self._setup_functions()

    def _setup_functions(self):
        @self.tool(
            name="check_weather",
            description="Get weather information",
            parameters={
                "city": {"type": "string", "description": "City name"}
            }
        )
        def check_weather(args, raw_data):
            city = args.get("city")
            return SwaigFunctionResult(f"The weather in {city} is sunny and 72°F")

# Instantiate outside handler
agent = MyAgent()

# Google Cloud Functions entry point
def main(request):
    return agent.run(request)
```

**requirements.txt:**

```
signalwire-agents
```

**Deploy:**

```bash
gcloud functions deploy ai-agent \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point main \
  --set-env-vars SIGNALWIRE_SPACE_NAME=myspace,SIGNALWIRE_PROJECT_ID=xxx,SIGNALWIRE_TOKEN=xxx
```

### Azure Functions

**__init__.py:**

```python
import azure.functions as func
from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult

class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="azure-agent")
        self.add_language("English", "en-US", "rime.spore")
        self._setup_functions()

    def _setup_functions(self):
        @self.tool(
            name="lookup_user",
            description="Look up user information",
            parameters={
                "user_id": {"type": "string", "description": "User ID"}
            }
        )
        def lookup_user(args, raw_data):
            user_id = args.get("user_id")
            return SwaigFunctionResult(f"User {user_id} found: John Doe")

# Instantiate outside handler
agent = MyAgent()

def main(req: func.HttpRequest) -> func.HttpResponse:
    return agent.run(req)
```

**Deploy:**

```bash
func azure functionapp publish <APP_NAME>
```

For complete serverless deployment guide, see: [reference/deployment/serverless.md](../reference/deployment/serverless.md)

## Multi-Agent Server

Deploy multiple agents on one server with AgentServer:

```python
from signalwire_agents import AgentServer
from agents.support import SupportAgent
from agents.sales import SalesAgent
from agents.faq import FAQAgent

# Create server
server = AgentServer(host="0.0.0.0", port=3000)

# Register agents at different paths
server.register(SupportAgent(), "/support")
server.register(SalesAgent(), "/sales")
server.register(FAQAgent(), "/faq")

# Optionally serve static files (web UI)
server.serve_static_files("./web")

# Run server
server.run()
```

**Each agent gets its own endpoint:**
- `https://yourdomain.com/support/swml` - Support agent
- `https://yourdomain.com/sales/swml` - Sales agent
- `https://yourdomain.com/faq/swml` - FAQ agent

**Benefits:**
- Shared infrastructure
- Centralized logging
- Resource efficiency
- Easier management

For complete multi-agent patterns, see: [reference/sdk/agent-server.md](../reference/sdk/agent-server.md)

## Production Tips

### 1. Start Simple, Iterate Constantly

- Begin with minimal functionality
- Add features incrementally
- Test after each addition
- Track what works in version control

### 2. Environment Configuration

**Use environment variables for all configuration:**

```python
import os

class ProductionAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name=os.getenv('AGENT_NAME', 'default-agent'),
            port=int(os.getenv('PORT', 5000)),
            basic_auth=(
                os.getenv('SWML_BASIC_AUTH_USER'),
                os.getenv('SWML_BASIC_AUTH_PASSWORD')
            ) if os.getenv('SWML_BASIC_AUTH_USER') else None
        )

        # API keys from environment
        self.api_key = os.getenv('EXTERNAL_API_KEY')
        self.database_url = os.getenv('DATABASE_URL')
```

For complete environment variable reference, see: [reference/deployment/environment-variables.md](../reference/deployment/environment-variables.md)

### 3. Graceful Degradation

```yaml
ai:
  prompt: "Your instructions"
  params:
    ai_model: "gpt-4o-mini"
    fallback_model: "gpt-4.0-mini"
    max_retries: 3
```

**Current Architecture:**
- Primary: OpenAI API
- Fallback: Azure OpenAI
- Automatic failover in development

### 4. Health Checks

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "ai-agent",
        "version": "1.0.0"
    }), 200

@app.route('/ready', methods=['GET'])
def readiness_check():
    # Check dependencies
    try:
        database.ping()
        return jsonify({"status": "ready"}), 200
    except:
        return jsonify({"status": "not ready"}), 503
```

### 5. Structured Logging

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName
        }
        return json.dumps(log_data)

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

## Monitoring and Observability

### Performance Metrics

**Latency Targets:**
- Average response time: ~500ms
- P95 response time: <1s
- Function execution: <2s

**Quality Metrics:**
- Call completion rate
- Function success rate
- Transfer success rate
- Customer satisfaction

**Operational Efficiency:**
- Includes ASR, TTS, and LLM in single service
- No infrastructure to manage or maintain
- Automatic scaling and load balancing

### Dashboard Metrics

```python
def generate_call_metrics():
    """Generate real-time call center metrics"""

    return {
        'active_calls': count_active_calls(),
        'average_wait_time': metrics.average('queue_time'),
        'average_call_duration': metrics.average('call_duration'),
        'calls_per_hour': metrics.rate('calls', hours=1),
        'answer_rate': (metrics.count('answered') / metrics.count('ringing')) * 100,
        'abandonment_rate': (metrics.count('abandoned') / metrics.count('queued')) * 100
    }
```

### Debug Webhooks

Monitor agent behavior in real-time:

```python
agent.set_params({
    "debug_webhook_url": "https://webhook.site/your-unique-id",
    "debug_webhook_level": 2  # 1=basic, 2=verbose
})
```

**Debug Levels:**
- **0**: Off (default)
- **1**: Function calls, errors, state changes
- **2**: Full transcripts and payloads

For complete debugging guide, see: [AI Agent Debug Webhooks](ai-agent-debug-webhooks.md)

### Post-Prompt Analytics

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

**Use this data to:**
- Track success rates
- Identify problem areas
- Tune prompts
- Measure customer satisfaction

For post-prompt processing patterns, see: [Webhooks & Events](webhooks-events.md)

## Security Best Practices

### 1. Use HTTPS

**Always use HTTPS for webhook URLs:**

```python
# Good
"status_url": "https://example.com/webhook"

# Bad - will fail or be rejected
"status_url": "http://example.com/webhook"
```

### 2. HTTP Basic Auth

```python
agent = MyAgent(
    name="secure-agent",
    basic_auth=("agent", os.getenv('AGENT_PASSWORD'))
)
```

### 3. API Key Management

```python
import os

# Never hardcode API keys
API_KEY = os.getenv('EXTERNAL_API_KEY')

# Use secrets management
from azure.keyvault.secrets import SecretClient
secret_client = SecretClient(vault_url=VAULT_URL, credential=credential)
api_key = secret_client.get_secret("api-key").value
```

### 4. Input Validation

```python
@AgentBase.tool(
    name="transfer_funds",
    description="Transfer funds",
    parameters={
        "amount": {"type": "number", "description": "Amount to transfer"}
    }
)
def transfer_funds(self, args, raw_data):
    amount = args.get("amount")

    # Validate input
    if not isinstance(amount, (int, float)):
        return SwaigFunctionResult("Invalid amount format")

    if amount <= 0:
        return SwaigFunctionResult("Amount must be positive")

    if amount > 10000:
        return SwaigFunctionResult("Amount exceeds daily limit")

    # Process transfer...
```

For complete security patterns, see: [AI Agent Security](ai-agent-security.md)

## Error Handling

### Robust Error Handling

```python
@AgentBase.tool(
    name="api_call",
    description="Call external API",
    parameters={
        "endpoint": {"type": "string", "description": "API endpoint"}
    }
)
def api_call(self, args, raw_data):
    try:
        response = requests.get(
            args.get("endpoint"),
            timeout=5
        )
        response.raise_for_status()
        return SwaigFunctionResult("Success")

    except requests.Timeout:
        logging.error("API timeout")
        return SwaigFunctionResult("The service is taking too long to respond. Please try again.")

    except requests.HTTPError as e:
        logging.error(f"HTTP error: {e}")
        return SwaigFunctionResult("I'm having trouble accessing that information right now.")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return SwaigFunctionResult("An unexpected error occurred. Let me transfer you to someone who can help.")
```

For complete error handling patterns, see: [AI Agent Error Handling](ai-agent-error-handling.md)

## Testing in Production

### Canary Deployments

```python
import random

class CanaryAgent(AgentBase):
    def __init__(self):
        super().__init__(name="canary")

        # 10% of traffic gets new prompt
        if random.random() < 0.1:
            self.prompt_add_section("Role", "New experimental prompt")
        else:
            self.prompt_add_section("Role", "Stable production prompt")
```

### A/B Testing

```python
# Test two prompt variations
# Compare success rates
# Iterate on winner
# Document results
```

### Blue-Green Deployment

```bash
# Deploy new version to green
docker-compose -f docker-compose.green.yml up -d

# Test green deployment
curl https://green.example.com/health

# Switch traffic to green
# Update load balancer or DNS

# Keep blue running as rollback option
```

## Load Balancing

### Nginx Configuration

**/etc/nginx/sites-available/ai-agent:**

```nginx
upstream ai_agents {
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}

server {
    listen 80;
    server_name ai.example.com;

    location / {
        proxy_pass http://ai_agents;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### AWS Application Load Balancer

```yaml
# Target group with health checks
TargetGroup:
  Type: AWS::ElasticLoadBalancingV2::TargetGroup
  Properties:
    HealthCheckEnabled: true
    HealthCheckPath: /health
    HealthCheckProtocol: HTTP
    HealthCheckIntervalSeconds: 30
    HealthyThresholdCount: 2
    UnhealthyThresholdCount: 3
    Port: 5000
    Protocol: HTTP
    VpcId: !Ref VPC
```

## Backup and Recovery

### Database Backups

```python
import subprocess
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"backup_{timestamp}.sql"

    subprocess.run([
        'pg_dump',
        '-h', 'localhost',
        '-U', 'user',
        '-d', 'ai_agent_db',
        '-f', backup_file
    ])

    # Upload to S3
    s3_client.upload_file(backup_file, 'backups-bucket', backup_file)
```

### Configuration Backups

```bash
# Backup environment variables
env | grep -E 'SIGNALWIRE|SWML' > config.backup

# Backup SWML files
tar -czf swml-backup.tar.gz swml/
```

## Scaling Considerations

### Horizontal Scaling

- Use load balancer
- Stateless agent design
- Shared session store (Redis, DynamoDB)
- Database connection pooling

### Vertical Scaling

- Monitor memory usage
- CPU utilization
- Adjust instance size as needed

### Auto-Scaling

**AWS Auto Scaling:**

```yaml
AutoScalingGroup:
  Type: AWS::AutoScaling::AutoScalingGroup
  Properties:
    MinSize: 2
    MaxSize: 10
    DesiredCapacity: 3
    TargetGroupARNs:
      - !Ref TargetGroup
    MetricsCollection:
      - Granularity: 1Minute
```

## Next Steps

- [AI Agent SDK Basics](ai-agent-sdk-basics.md) - Python SDK fundamentals
- [AI Agent Prompting](ai-agent-prompting.md) - Best practices for prompts
- [AI Agent Functions](ai-agent-functions.md) - SWAIG function patterns
- [Webhooks & Events](webhooks-events.md) - Monitoring and testing
- [Voice AI](voice-ai.md) - Complete overview and examples
