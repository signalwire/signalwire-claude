# Prefab Agents Reference

Prefab agents are ready-to-use agent templates for common use cases. They provide pre-configured prompts, tools, and workflows that you can use directly or customize.

## Import

```python
from signalwire_agents.prefabs import (
    InfoGathererAgent,
    FAQBotAgent,
    ConciergeAgent,
    SurveyAgent,
    ReceptionistAgent
)
```

## Available Prefab Agents

| Prefab | Use Case |
|--------|----------|
| `InfoGathererAgent` | Collect answers to a series of questions |
| `FAQBotAgent` | Answer frequently asked questions |
| `ConciergeAgent` | Virtual concierge services |
| `SurveyAgent` | Conduct automated surveys |
| `ReceptionistAgent` | Screen calls and route to departments |

---

## InfoGathererAgent

Collects answers to a predefined series of questions, with optional confirmation for each answer.

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `questions` | list | None | List of question dictionaries |
| `name` | str | "info_gatherer" | Agent name |
| `route` | str | "/info_gatherer" | HTTP route |
| **kwargs | | | Additional AgentBase parameters |

### Question Dictionary Format

```python
{
    "key_name": "unique_identifier",    # Required: Used to store the answer
    "question_text": "What is your name?",  # Required: The question to ask
    "confirm": True  # Optional: Require user confirmation (default: False)
}
```

### Basic Example

```python
from signalwire_agents.prefabs import InfoGathererAgent

agent = InfoGathererAgent(
    questions=[
        {"key_name": "full_name", "question_text": "What is your full name?"},
        {"key_name": "email", "question_text": "What is your email address?", "confirm": True},
        {"key_name": "phone", "question_text": "What is your phone number?", "confirm": True},
        {"key_name": "reason", "question_text": "What is the purpose of your inquiry?"}
    ],
    port=3000
)

agent.add_language("English", "en-US", "rime.spore")
agent.run()
```

### Dynamic Questions Example

For questions that vary based on request parameters:

```python
from signalwire_agents.prefabs import InfoGathererAgent

agent = InfoGathererAgent(name="dynamic-intake", port=3000)

def get_questions(query_params, body_params, headers):
    form_type = query_params.get('type', 'default')

    if form_type == 'support':
        return [
            {"key_name": "name", "question_text": "What is your name?"},
            {"key_name": "issue", "question_text": "What issue are you experiencing?"},
            {"key_name": "urgency", "question_text": "How urgent is this issue?"}
        ]
    else:
        return [
            {"key_name": "name", "question_text": "What is your name?"},
            {"key_name": "message", "question_text": "How can I help you today?"}
        ]

agent.set_question_callback(get_questions)
agent.add_language("English", "en-US", "rime.spore")
agent.run()
```

### Built-in Tools

- `start_questions` - Begin the question sequence
- `submit_answer` - Submit an answer and proceed to the next question

---

## SurveyAgent

Conducts automated surveys with various question types and response validation.

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `survey_name` | str | **required** | Name of the survey |
| `questions` | list | **required** | List of question dictionaries |
| `introduction` | str | None | Custom introduction message |
| `conclusion` | str | None | Custom conclusion message |
| `brand_name` | str | None | Brand/company name |
| `max_retries` | int | 2 | Max retries for invalid answers |
| `name` | str | "survey" | Agent name |
| `route` | str | "/survey" | HTTP route |

### Question Types

| Type | Description | Required Fields |
|------|-------------|-----------------|
| `rating` | Numeric rating (1-N scale) | `scale` (default: 5) |
| `multiple_choice` | Select from options | `options` (list) |
| `yes_no` | Yes or no answer | None |
| `open_ended` | Free-form text | None |

### Question Dictionary Format

```python
{
    "id": "unique_id",           # Required: Unique identifier
    "text": "Question text?",    # Required: The question to ask
    "type": "rating",            # Required: rating, multiple_choice, yes_no, open_ended
    "scale": 5,                  # For rating type: 1-N scale
    "options": ["A", "B", "C"],  # For multiple_choice: available options
    "required": True             # Optional: whether answer is required (default: True)
}
```

### Example

```python
from signalwire_agents.prefabs import SurveyAgent

agent = SurveyAgent(
    survey_name="Customer Satisfaction Survey",
    brand_name="Acme Corp",
    introduction="Thank you for taking our quick customer satisfaction survey.",
    conclusion="Thank you for your feedback! It helps us serve you better.",
    questions=[
        {
            "id": "overall",
            "text": "How would you rate your overall experience?",
            "type": "rating",
            "scale": 5
        },
        {
            "id": "recommend",
            "text": "Would you recommend us to a friend?",
            "type": "yes_no"
        },
        {
            "id": "service_type",
            "text": "Which service did you use?",
            "type": "multiple_choice",
            "options": ["Phone Support", "Email Support", "Chat Support", "In-Person"]
        },
        {
            "id": "comments",
            "text": "Do you have any additional comments?",
            "type": "open_ended",
            "required": False
        }
    ],
    port=3000
)

agent.add_language("English", "en-US", "rime.spore")
agent.run()
```

### Built-in Tools

- `validate_response` - Validate a response for a question
- `log_response` - Log a validated response

### Processing Results

Override `on_summary` to process survey results:

```python
class MySurveyAgent(SurveyAgent):
    def on_summary(self, summary, raw_data=None):
        if summary:
            # Store in database, send to webhook, etc.
            print(f"Survey completed: {summary}")
```

---

## ConciergeAgent

Acts as a virtual concierge providing information about services, amenities, and making reservations.

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `venue_name` | str | **required** | Name of the venue/business |
| `services` | list | **required** | List of available services |
| `amenities` | dict | **required** | Amenities with details |
| `hours_of_operation` | dict | None | Operating hours by area |
| `special_instructions` | list | None | Additional instructions |
| `welcome_message` | str | None | Custom welcome message |
| `name` | str | "concierge" | Agent name |
| `route` | str | "/concierge" | HTTP route |

### Amenities Dictionary Format

```python
{
    "amenity_name": {
        "hours": "Operating hours",
        "location": "Physical location",
        # Any additional key-value details
    }
}
```

### Example

```python
from signalwire_agents.prefabs import ConciergeAgent

agent = ConciergeAgent(
    venue_name="Grand Plaza Hotel",
    services=[
        "room service",
        "spa bookings",
        "restaurant reservations",
        "airport shuttle",
        "valet parking"
    ],
    amenities={
        "pool": {
            "hours": "7 AM - 10 PM",
            "location": "2nd Floor, East Wing"
        },
        "gym": {
            "hours": "24 hours",
            "location": "3rd Floor"
        },
        "spa": {
            "hours": "9 AM - 9 PM",
            "location": "4th Floor",
            "booking": "Required"
        },
        "restaurant": {
            "hours": "6 AM - 11 PM",
            "location": "Lobby Level",
            "dress_code": "Smart Casual"
        }
    },
    hours_of_operation={
        "front_desk": "24 hours",
        "concierge": "6 AM - 10 PM",
        "business_center": "7 AM - 9 PM"
    },
    special_instructions=[
        "Offer complimentary upgrades to loyalty members when available",
        "Always mention current promotions"
    ],
    welcome_message="Welcome to Grand Plaza Hotel! How may I assist you today?",
    port=3000
)

agent.add_language("English", "en-US", "rime.spore")
agent.run()
```

### Built-in Tools

- `check_availability` - Check availability for a service/date/time
- `get_directions` - Get directions to amenities

---

## FAQBotAgent

Answers frequently asked questions using skills and configured knowledge.

### Basic Usage

```python
from signalwire_agents.prefabs import FAQBotAgent

agent = FAQBotAgent(
    company_name="Acme Corp",
    faqs={
        "hours": "We're open Monday-Friday, 9 AM to 5 PM EST.",
        "location": "We're located at 123 Main Street, Suite 100.",
        "contact": "You can reach us at support@acme.com or 555-123-4567.",
        "returns": "We offer a 30-day return policy on all items."
    },
    port=3000
)

agent.add_language("English", "en-US", "rime.spore")
agent.run()
```

---

## ReceptionistAgent

Screens incoming calls, collects caller information, and routes to appropriate departments.

### Basic Usage

```python
from signalwire_agents.prefabs import ReceptionistAgent

agent = ReceptionistAgent(
    company_name="Acme Corp",
    departments={
        "sales": {
            "description": "New purchases and pricing inquiries",
            "transfer_dest": "sip:sales@company.com"
        },
        "support": {
            "description": "Technical help and troubleshooting",
            "transfer_dest": "sip:support@company.com"
        },
        "billing": {
            "description": "Invoices, payments, and account questions",
            "transfer_dest": "sip:billing@company.com"
        }
    },
    port=3000
)

agent.add_language("English", "en-US", "rime.spore")
agent.run()
```

---

## Customizing Prefab Agents

All prefab agents extend `AgentBase`, so you can customize them:

```python
from signalwire_agents.prefabs import SurveyAgent
from signalwire_agents.core.function_result import SwaigFunctionResult

class CustomSurveyAgent(SurveyAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Add custom configuration
        self.add_language("Spanish", "es-MX", "rime.spore")

        # Add additional tools
        self.define_tool(
            name="escalate_to_human",
            description="Transfer to a human agent",
            handler=self.handle_escalate
        )

    def handle_escalate(self, args, raw_data):
        return SwaigFunctionResult("Transferring you to a human agent").add_action(
            "transfer", {"dest": "sip:support@company.com"}
        )

    def on_summary(self, summary, raw_data=None):
        # Custom summary handling
        if summary:
            # Send to webhook, database, etc.
            pass
```

## Multi-Agent Deployment

Deploy multiple prefab agents together:

```python
from signalwire_agents import AgentServer
from signalwire_agents.prefabs import (
    InfoGathererAgent,
    SurveyAgent,
    ConciergeAgent
)

server = AgentServer(host="0.0.0.0", port=3000)

# Configure and register each agent
intake = InfoGathererAgent(questions=[...])
intake.add_language("English", "en-US", "rime.spore")
server.register(intake, "/intake")

survey = SurveyAgent(survey_name="Feedback", questions=[...])
survey.add_language("English", "en-US", "rime.spore")
server.register(survey, "/survey")

concierge = ConciergeAgent(venue_name="Hotel", services=[...], amenities={...})
concierge.add_language("English", "en-US", "rime.spore")
server.register(concierge, "/concierge")

server.run()
```

## See Also

- [Agent Base Reference](agent-base.md) - Complete AgentBase documentation
- [Contexts and Steps](contexts-steps.md) - Workflow patterns used by prefabs
- [SWAIG Functions Reference](swaig-functions.md) - Function definition patterns
