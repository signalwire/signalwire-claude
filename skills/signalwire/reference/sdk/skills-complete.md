# Skills Reference

Complete reference for all built-in skills and skill management in the SignalWire AI Agents SDK.

## Import

```python
from signalwire_agents import AgentBase, register_skill, add_skill_directory, list_skills_with_params
```

## Skill Management Methods

### add_skill()

Add a skill to the agent.

```python
agent.add_skill(skill_name, params=None)
```

### remove_skill()

Remove a skill from the agent.

```python
agent.remove_skill(skill_name)  # Returns True if removed
```

### has_skill()

Check if a skill is loaded.

```python
if agent.has_skill("datetime"):
    # Skill is loaded
```

### list_skills()

Get list of loaded skill names.

```python
skills = agent.list_skills()  # Returns ["datetime", "math", ...]
```

---

## Built-in Skills

### datetime

Provides date and time functions.

```python
agent.add_skill("datetime", {
    "timezone": "America/New_York"  # Default timezone
})
```

**Functions provided:**
- `check_time` - Get current date and time

---

### math

Provides mathematical operations.

```python
agent.add_skill("math")
```

**Functions provided:**
- Basic arithmetic operations
- Unit conversions
- Mathematical calculations

---

### web_search

Search the web using Google Custom Search.

```python
agent.add_skill("web_search", {
    "api_key": "your-google-api-key",           # Required
    "search_engine_id": "your-cse-id"           # Required
})
```

**Environment variables:**
- `GOOGLE_SEARCH_API_KEY` - API key
- `GOOGLE_SEARCH_ENGINE_ID` - Search engine ID

**Functions provided:**
- `search_web` - Perform web search

---

### wikipedia_search

Search Wikipedia for information.

```python
agent.add_skill("wikipedia_search")
```

**Functions provided:**
- `search_wikipedia` - Search and retrieve Wikipedia content

---

### weather_api

Get weather information.

```python
agent.add_skill("weather_api", {
    "provider": "openweathermap",  # Provider name
    "api_key": "your-api-key",     # Required
    "units": "imperial"            # "imperial" or "metric"
})
```

**Environment variables:**
- `OPENWEATHERMAP_API_KEY` - API key

**Functions provided:**
- `get_weather` - Get current weather for a location

---

### native_vector_search

Local document search using vector embeddings.

```python
agent.add_skill("native_vector_search", {
    "index_path": "/path/to/search/index",  # Required
    "top_k": 5                               # Number of results
})
```

**Functions provided:**
- `search_documents` - Search local document index

**Note:** Requires building a search index first. See [Search System](#search-system) for details.

---

### swml_transfer

Simplified call transfer capabilities.

```python
agent.add_skill("swml_transfer", {
    "default_dest": "sip:support@company.com"  # Optional default
})
```

**Functions provided:**
- `transfer_call` - Transfer to a destination

---

### datasphere

Integration with SignalWire DataSphere.

```python
agent.add_skill("datasphere", {
    "space_name": "your-space",
    "project_id": "your-project-id",
    "token": "your-token"
})
```

**Environment variables:**
- `SIGNALWIRE_SPACE_NAME`
- `SIGNALWIRE_PROJECT_ID`
- `SIGNALWIRE_TOKEN`

---

### datasphere_serverless

DataSphere integration for serverless deployments.

```python
agent.add_skill("datasphere_serverless", {
    "document_id": "your-document-id"
})
```

---

### api_ninjas_trivia

Trivia questions from API Ninjas.

```python
agent.add_skill("api_ninjas_trivia", {
    "api_key": "your-api-ninjas-key"
})
```

**Functions provided:**
- `get_trivia` - Get a trivia question

---

### joke

Tell jokes.

```python
agent.add_skill("joke")
```

**Functions provided:**
- `tell_joke` - Get a random joke

---

### spider

Web scraping and content extraction.

```python
agent.add_skill("spider", {
    "api_key": "your-spider-api-key"
})
```

**Functions provided:**
- `scrape_url` - Extract content from a URL

---

### play_background_file

Control background audio playback.

```python
agent.add_skill("play_background_file")
```

**Functions provided:**
- `play_background` - Start background audio
- `stop_background` - Stop background audio

---

### mcp_gateway

Integration with Model Context Protocol servers.

```python
agent.add_skill("mcp_gateway", {
    "gateway_url": "http://localhost:8080"  # MCP gateway URL
})
```

---

## Custom Skills

### Creating Custom Skills

Custom skills extend `SkillBase`:

```python
from signalwire_agents.core.skill_base import SkillBase
from signalwire_agents.core.function_result import SwaigFunctionResult


class MyCustomSkill(SkillBase):
    SKILL_NAME = "my_custom_skill"
    SKILL_DESCRIPTION = "My custom skill description"
    SKILL_VERSION = "1.0.0"
    REQUIRED_PACKAGES = []  # List pip packages needed
    REQUIRED_ENV_VARS = []  # List env vars needed
    SUPPORTS_MULTIPLE_INSTANCES = False

    @classmethod
    def get_parameter_schema(cls):
        """Define skill parameters."""
        schema = super().get_parameter_schema()
        schema.update({
            "api_key": {
                "type": "string",
                "description": "API key for the service",
                "required": True,
                "hidden": True,  # Don't log this value
                "env_var": "MY_SKILL_API_KEY"  # Can use env var
            },
            "timeout": {
                "type": "integer",
                "description": "Request timeout in seconds",
                "required": False,
                "default": 30
            }
        })
        return schema

    def setup(self):
        """Called when skill is initialized."""
        self.api_key = self.params.get("api_key")
        self.timeout = self.params.get("timeout", 30)

        # Define tools provided by this skill
        self.define_tool(
            name="my_function",
            description="Do something useful",
            parameters={
                "input": {
                    "type": "string",
                    "description": "Input value"
                }
            },
            handler=self.handle_my_function
        )

    def handle_my_function(self, args, raw_data):
        input_val = args.get("input")
        # Do something with self.api_key and input_val
        return SwaigFunctionResult(f"Processed: {input_val}")
```

### Registering Custom Skills

#### Method 1: register_skill()

Register a skill class directly:

```python
from signalwire_agents import register_skill
from my_skills import MyCustomSkill

register_skill(MyCustomSkill)

# Now use it
agent.add_skill("my_custom_skill", {"api_key": "..."})
```

#### Method 2: add_skill_directory()

Add a directory containing skills:

```python
from signalwire_agents import add_skill_directory

add_skill_directory("/path/to/my/skills")

# Skills must follow directory structure:
# /path/to/my/skills/
#   my_skill/
#     skill.py  # Contains skill class
```

#### Method 3: Entry Points

Register via setup.py for pip-installable skills:

```python
# setup.py
setup(
    name="my-skills-package",
    entry_points={
        'signalwire_agents.skills': [
            'my_skill = my_package.skills:MyCustomSkill',
        ]
    }
)
```

#### Method 4: Environment Variable

Add skill directories via environment:

```bash
export SIGNALWIRE_SKILL_PATHS="/path/to/skills1:/path/to/skills2"
```

### Listing All Skills

#### list_skills_with_params()

Get complete schema for all available skills:

```python
from signalwire_agents import list_skills_with_params

schema = list_skills_with_params()
print(schema)
# {
#     "web_search": {
#         "name": "web_search",
#         "description": "Search the web for information",
#         "version": "1.0.0",
#         "parameters": {
#             "api_key": {
#                 "type": "string",
#                 "required": True,
#                 "hidden": True
#             },
#             ...
#         },
#         "source": "built-in"
#     },
#     ...
# }
```

---

## Search System

The SDK includes a powerful local search system for document retrieval.

### Building a Search Index

Use the CLI to build an index:

```bash
# Index documents
python -m signalwire_agents.search.build_index \
    --input /path/to/documents \
    --output /path/to/index \
    --chunk-size 500 \
    --chunk-overlap 50
```

**Supported document formats:**
- PDF (.pdf)
- Word (.docx)
- Excel (.xlsx)
- PowerPoint (.pptx)
- HTML (.html)
- Markdown (.md)
- Text (.txt)

### Using the Search Skill

```python
agent.add_skill("native_vector_search", {
    "index_path": "/path/to/index",
    "top_k": 5  # Number of results to return
})
```

### Search API

The search system can also run as a standalone HTTP service:

```bash
python -m signalwire_agents.search.server \
    --index /path/to/index \
    --port 8080
```

---

## Complete Example

```python
#!/usr/bin/env python3
from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult
import os


class SkillsShowcaseAgent(AgentBase):
    """Agent demonstrating various skills."""

    def __init__(self):
        super().__init__(name="skills-showcase", port=3000)

        # Configure voice
        self.add_language("English", "en-US", "rime.spore")

        # Add built-in skills
        self.add_skill("datetime", {"timezone": "America/New_York"})
        self.add_skill("math")

        # Add web search if API key available
        if os.environ.get("GOOGLE_SEARCH_API_KEY"):
            self.add_skill("web_search", {
                "api_key": os.environ["GOOGLE_SEARCH_API_KEY"],
                "search_engine_id": os.environ["GOOGLE_SEARCH_ENGINE_ID"]
            })

        # Add weather if API key available
        if os.environ.get("OPENWEATHERMAP_API_KEY"):
            self.add_skill("weather_api", {
                "provider": "openweathermap",
                "api_key": os.environ["OPENWEATHERMAP_API_KEY"],
                "units": "imperial"
            })

        # Add local search if index exists
        if os.path.exists("/data/search_index"):
            self.add_skill("native_vector_search", {
                "index_path": "/data/search_index",
                "top_k": 3
            })

        # Build prompt
        self.prompt_add_section("Role", "You are a helpful assistant with access to various tools.")
        self.prompt_add_section(
            "Available Skills",
            body="You have access to: " + ", ".join(self.list_skills())
        )


if __name__ == "__main__":
    agent = SkillsShowcaseAgent()
    agent.run()
```

## See Also

- [Agent Base Reference](agent-base.md) - Core agent documentation
- [SWAIG Functions Reference](swaig-functions.md) - Function patterns
- [Environment Variables](environment-variables.md) - Configuration
