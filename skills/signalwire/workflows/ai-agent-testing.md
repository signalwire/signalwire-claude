# Testing Patterns

Guide to testing SignalWire AI Agents using swaig-test and other techniques.

## swaig-test CLI

The `swaig-test` CLI tool validates agents without making real calls.

### Basic Usage

```bash
# Dump SWML configuration
swaig-test my_agent.py --dump-swml

# List all registered tools
swaig-test my_agent.py --list-tools

# Execute a specific function
swaig-test my_agent.py --exec function_name --args '{"param": "value"}'

# Test specific agent class in multi-class file
swaig-test my_agent.py --agent-class MyAgent --dump-swml
```

### Verifying SWML Output

```bash
$ swaig-test my_agent.py --dump-swml
```

Check the output for:
- `ai.prompt.text` - Your prompt is complete
- `ai.languages` - Voice is configured
- `ai.SWAIG.functions` - Functions are registered
- `ai.params` - AI parameters are set

Example expected output structure:
```json
{
  "sections": {
    "main": [
      {
        "ai": {
          "prompt": {
            "text": "## Role\n\nYou are a helpful assistant..."
          },
          "languages": [
            {
              "name": "English",
              "code": "en-US",
              "voice": "rime.spore"
            }
          ],
          "SWAIG": {
            "functions": [
              {
                "function": "get_time",
                "description": "Get the current time",
                "parameters": {}
              }
            ]
          }
        }
      }
    ]
  }
}
```

### Testing Functions

```bash
# Simple function with no parameters
$ swaig-test my_agent.py --exec get_time

# Function with parameters
$ swaig-test my_agent.py --exec lookup_order --args '{"order_number": "ORD-12345"}'

# Function with multiple parameters
$ swaig-test my_agent.py --exec schedule_appointment --args '{"date": "2024-01-15", "time": "14:00"}'
```

### Testing with Call Context

Simulate incoming call data:

```bash
$ swaig-test my_agent.py --exec verify_identity \
    --args '{"pin": "1234"}' \
    --call-data '{"from": "+15551234567", "to": "+15559876543"}'
```

## Unit Testing with pytest

### Basic Agent Test

```python
# test_my_agent.py
import pytest
from my_agent import MyAgent

class TestMyAgent:
    @pytest.fixture
    def agent(self):
        return MyAgent()

    def test_agent_has_name(self, agent):
        assert agent.name == "my-agent"

    def test_agent_has_language(self, agent):
        swml = agent.render_swml()
        assert "languages" in str(swml)
        assert "en-US" in str(swml)

    def test_prompt_contains_role(self, agent):
        prompt = agent.get_prompt()
        assert "Role" in prompt or "role" in prompt.lower()

    def test_function_registered(self, agent):
        swml = agent.render_swml()
        assert "get_time" in str(swml)
```

### Testing Function Handlers

```python
import pytest
from my_agent import MyAgent

class TestFunctions:
    @pytest.fixture
    def agent(self):
        return MyAgent()

    def test_lookup_order_found(self, agent, mocker):
        # Mock database call
        mocker.patch.object(
            agent, 'db',
            get_order=lambda x: {"status": "shipped", "date": "2024-01-10"}
        )

        args = {"order_number": "ORD-12345"}
        raw_data = {"call_id": "test-call"}

        result = agent.lookup_order(args, raw_data)

        assert "shipped" in result.response
        assert "ORD-12345" in result.response

    def test_lookup_order_not_found(self, agent, mocker):
        mocker.patch.object(
            agent, 'db',
            get_order=lambda x: None
        )

        args = {"order_number": "INVALID"}
        raw_data = {"call_id": "test-call"}

        result = agent.lookup_order(args, raw_data)

        assert "couldn't find" in result.response.lower()

    def test_transfer_has_action(self, agent):
        args = {"department": "support"}
        raw_data = {"call_id": "test-call"}

        result = agent.transfer_to_agent(args, raw_data)

        # Check that transfer action is included
        actions = result.to_dict().get("action", [])
        transfer_actions = [a for a in actions if "transfer" in a]
        assert len(transfer_actions) > 0
```

### Testing SwaigFunctionResult

```python
from signalwire_agents.core.function_result import SwaigFunctionResult

def test_simple_result():
    result = SwaigFunctionResult("Hello!")
    data = result.to_dict()

    assert data["response"] == "Hello!"
    assert "action" not in data or data["action"] == []

def test_result_with_action():
    result = SwaigFunctionResult("Transferring...").add_action(
        "transfer", {"dest": "tel:+15551234567"}
    )
    data = result.to_dict()

    assert data["response"] == "Transferring..."
    assert {"transfer": {"dest": "tel:+15551234567"}} in data["action"]

def test_result_with_multiple_actions():
    result = (SwaigFunctionResult("Done!")
        .add_action("set_global_data", {"key": "value"})
        .add_action("hangup", {}))

    data = result.to_dict()
    assert len(data["action"]) == 2

def test_post_process():
    result = SwaigFunctionResult("Goodbye!", post_process=True)
    data = result.to_dict()

    # Post-process adds SWML action
    assert any("SWML" in str(a) for a in data.get("action", []))
```

### Testing on_swml_request Hook

```python
def test_on_swml_request_vip(agent):
    # Simulate VIP caller
    request_data = {
        "call": {
            "from": "+15551234567"  # VIP number
        }
    }

    # Add to VIP list
    agent.vip_numbers = ["+15551234567"]

    # Call the hook
    agent.on_swml_request(request_data=request_data)

    # Check prompt was modified
    prompt = agent.get_prompt()
    assert "VIP" in prompt
```

## Integration Testing

### Local Server Testing

```python
import pytest
import requests
import threading
import time

class TestAgentServer:
    @pytest.fixture
    def running_agent(self):
        from my_agent import MyAgent
        agent = MyAgent()

        # Run in background thread
        thread = threading.Thread(target=agent.run, daemon=True)
        thread.start()
        time.sleep(1)  # Wait for startup

        yield agent

        # Cleanup handled by daemon thread

    def test_swml_endpoint(self, running_agent):
        response = requests.post(
            "http://localhost:3000/",
            json={"call": {"from": "+15551234567"}}
        )

        assert response.status_code == 200
        data = response.json()
        assert "sections" in data

    def test_swaig_endpoint(self, running_agent):
        response = requests.post(
            "http://localhost:3000/swaig",
            json={
                "function": "get_time",
                "argument": {"parsed": [{}]}
            }
        )

        assert response.status_code == 200
```

### Testing with Mock HTTP

```python
import pytest
from unittest.mock import patch, MagicMock

def test_weather_api_integration(agent):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "temp": 72,
        "condition": "sunny"
    }

    with patch('requests.get', return_value=mock_response):
        result = agent.get_weather({"city": "Seattle"}, {})

    assert "72" in result.response
    assert "sunny" in result.response
```

## Test Fixtures

### Common Fixtures

```python
# conftest.py
import pytest

@pytest.fixture
def mock_call_data():
    return {
        "call_id": "test-call-123",
        "call": {
            "from": "+15551234567",
            "to": "+15559876543",
            "direction": "inbound"
        },
        "vars": {}
    }

@pytest.fixture
def mock_verified_call_data(mock_call_data):
    mock_call_data["vars"]["verified"] = True
    return mock_call_data

@pytest.fixture
def agent_with_mocked_db(agent, mocker):
    mock_db = mocker.MagicMock()
    agent.db = mock_db
    return agent, mock_db
```

## Testing Checklist

Before deploying an agent, verify:

- [ ] **SWML Structure**: `swaig-test --dump-swml` produces valid output
- [ ] **Functions Listed**: `swaig-test --list-tools` shows all functions
- [ ] **Functions Execute**: Each function runs without errors
- [ ] **Language Configured**: SWML includes voice configuration
- [ ] **Prompt Complete**: Prompt sections render correctly
- [ ] **Error Handling**: Functions handle missing/invalid inputs
- [ ] **Actions Work**: Transfer, hangup, etc. produce correct SWML
- [ ] **Post-process**: Goodbye flows complete before hangup

## Debugging Tips

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or via environment
# SWML_LOG_LEVEL=DEBUG python my_agent.py
```

### Inspect Function Output

```python
def test_debug_function_output(agent):
    result = agent.some_function({"param": "value"}, {})

    # Print full result for debugging
    import json
    print(json.dumps(result.to_dict(), indent=2))

    assert result.response  # Then make assertions
```

### Compare SWML Snapshots

```python
import json

def test_swml_snapshot(agent, snapshot):
    swml = agent.render_swml()
    # Using pytest-snapshot or similar
    snapshot.assert_match(
        json.dumps(swml, indent=2, sort_keys=True),
        "swml_snapshot.json"
    )
```
