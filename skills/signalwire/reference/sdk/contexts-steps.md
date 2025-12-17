# Contexts and Steps Reference

The Contexts and Steps system provides an alternative to traditional prompt-based agents by allowing you to define structured workflows with sequential steps, completion criteria, and navigation rules.

## Import

```python
from signalwire_agents import AgentBase, ContextBuilder, Context, Step, create_simple_context
```

## When to Use Contexts and Steps

Use Contexts and Steps when you need:

- **Sequential workflows** - Step-by-step processes like surveys, intake forms, or guided troubleshooting
- **Controlled navigation** - Restrict which steps/contexts the AI can move to
- **Step-specific prompts** - Different instructions at each stage
- **Function restrictions** - Limit which functions are available at each step
- **Completion criteria** - Define when a step is considered complete

## Core Concepts

### Context
A context is a container for related steps. Think of it as a "mode" or "phase" of the conversation.

### Step
A step is a specific point within a context with its own prompt, completion criteria, and available functions.

### ContextBuilder
The builder class that manages all contexts and validates the configuration.

## Basic Usage

### Single Context (Simple Workflow)

For simple sequential workflows, use a single "default" context:

```python
class SurveyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="survey")

        self.add_language("English", "en-US", "rime.spore")

        # Define contexts instead of using prompt_add_section
        self.define_contexts()

    def define_contexts(self):
        ctx = self.contexts.add_context("default")

        # Step 1: Introduction
        intro = ctx.add_step("introduction")
        intro.set_text("Welcome the user and explain that you'll be asking a few questions.")
        intro.set_step_criteria("User acknowledges they're ready to begin")
        intro.set_valid_steps(["next"])  # Can only go to next step

        # Step 2: Name collection
        name = ctx.add_step("get_name")
        name.set_text("Ask the user for their full name.")
        name.set_step_criteria("User provides their name")
        name.set_functions(["record_name"])  # Only this function available
        name.set_valid_steps(["next"])

        # Step 3: Email collection
        email = ctx.add_step("get_email")
        email.set_text("Ask the user for their email address. Confirm the spelling.")
        email.set_step_criteria("User confirms their email address")
        email.set_functions(["record_email"])
        email.set_valid_steps(["next"])

        # Step 4: Completion
        complete = ctx.add_step("complete")
        complete.set_text("Thank the user and summarize the information collected.")
        complete.set_functions("none")  # No functions at this step
```

### Multiple Contexts (Complex Workflows)

For complex workflows with different modes:

```python
class SupportAgent(AgentBase):
    def __init__(self):
        super().__init__(name="support")

        self.add_language("English", "en-US", "rime.spore")
        self.define_contexts()

    def define_contexts(self):
        # Main context - triage incoming issues
        main = self.contexts.add_context("main")
        main.set_valid_contexts(["technical", "billing", "general"])

        triage = main.add_step("triage")
        triage.set_text("Greet the user and determine the type of support they need.")
        triage.set_step_criteria("User's issue category is identified")
        triage.set_valid_contexts(["technical", "billing", "general"])

        # Technical support context
        tech = self.contexts.add_context("technical")
        tech.set_system_prompt("You are a technical support specialist.")
        tech.set_valid_contexts(["main"])

        tech_gather = tech.add_step("gather_info")
        tech_gather.set_text("Gather technical details about the issue.")
        tech_gather.set_functions(["run_diagnostic", "check_system_status"])
        tech_gather.set_valid_steps(["next"])

        tech_resolve = tech.add_step("resolve")
        tech_resolve.set_text("Provide technical resolution steps.")
        tech_resolve.set_functions(["create_ticket", "transfer_to_engineer"])

        # Billing context
        billing = self.contexts.add_context("billing")
        billing.set_system_prompt("You are a billing specialist.")
        billing.set_valid_contexts(["main"])

        bill_verify = billing.add_step("verify")
        bill_verify.set_text("Verify the customer's account information.")
        bill_verify.set_functions(["lookup_account"])
        bill_verify.set_valid_steps(["next"])

        bill_assist = billing.add_step("assist")
        bill_assist.set_text("Assist with billing inquiries.")
        bill_assist.set_functions(["get_balance", "process_payment", "issue_refund"])

        # General inquiries context
        general = self.contexts.add_context("general")
        general.set_valid_contexts(["main"])

        gen_help = general.add_step("help")
        gen_help.set_text("Answer general questions about our products and services.")
```

## Step Class Reference

### set_text()

Set the step's prompt text directly.

```python
step.set_text("Ask the user for their name and confirm the spelling.")
```

### add_section() / add_bullets()

Use POM-style sections for rich prompts (cannot mix with set_text).

```python
step.add_section("Task", "Collect the user's contact information.")
step.add_bullets("Requirements", [
    "Get full legal name",
    "Get email address",
    "Confirm all information"
])
```

### set_step_criteria()

Define when this step is considered complete.

```python
step.set_step_criteria("User provides and confirms their email address")
```

### set_functions()

Restrict which functions are available in this step.

```python
# Specific functions only
step.set_functions(["save_name", "validate_email"])

# No functions
step.set_functions("none")
```

### set_valid_steps()

Define which steps can be navigated to from this step.

```python
# Only sequential navigation
step.set_valid_steps(["next"])

# Specific steps
step.set_valid_steps(["confirm", "retry", "cancel"])

# Any step (no restriction)
# Don't call set_valid_steps()
```

### set_valid_contexts()

Define which contexts can be navigated to from this step.

```python
step.set_valid_contexts(["billing", "technical"])
```

### Reset Behavior (Context Switching)

Configure what happens when switching from this step to a new context:

```python
step.set_reset_system_prompt("You are now in billing mode.")
step.set_reset_user_prompt("Let's discuss your billing question.")
step.set_reset_consolidate(True)  # Summarize previous conversation
step.set_reset_full_reset(True)   # Complete system prompt replacement
```

## Context Class Reference

### add_step()

Add a new step to the context.

```python
step = context.add_step("step_name")
```

### set_valid_contexts()

Define which contexts can be navigated to from this context.

```python
context.set_valid_contexts(["support", "sales", "main"])
```

### set_system_prompt()

Set a system prompt that applies when entering this context.

```python
context.set_system_prompt("You are a billing specialist helping with account questions.")
```

### add_system_section() / add_system_bullets()

Use POM-style sections for context system prompts.

```python
context.add_system_section("Role", "You are a technical support engineer.")
context.add_system_bullets("Expertise", [
    "Network troubleshooting",
    "Software configuration",
    "Hardware diagnostics"
])
```

### set_prompt() / add_section() / add_bullets()

Set the context's main prompt (separate from system_prompt).

```python
context.set_prompt("Help the user with their technical issue.")
# OR
context.add_section("Objective", "Resolve technical issues efficiently.")
```

### Context Entry Parameters

Configure behavior when entering this context:

```python
context.set_consolidate(True)      # Summarize conversation on entry
context.set_full_reset(True)       # Replace system prompt entirely
context.set_user_prompt("Let's continue with your billing question.")
context.set_isolated(True)         # Truncate conversation history
```

### set_post_prompt()

Override the post-prompt for this context.

```python
context.set_post_prompt("Summarize the technical issue and resolution.")
```

### Context Fillers

Set phrases the AI says when entering/exiting contexts:

```python
context.set_enter_fillers({
    "en-US": ["Let me transfer you to billing...", "Connecting you to billing..."],
    "default": ["Transferring to billing..."]
})

context.set_exit_fillers({
    "en-US": ["Thank you for using billing support."],
    "default": ["Goodbye from billing."]
})

# Or add individually
context.add_enter_filler("en-US", ["Welcome to technical support..."])
context.add_exit_filler("es", ["Gracias por contactar soporte técnico."])
```

## ContextBuilder Reference

Access the ContextBuilder through `self.contexts`:

```python
class MyAgent(AgentBase):
    def define_contexts(self):
        # Add contexts
        ctx = self.contexts.add_context("default")

        # The builder validates automatically when generating SWML
```

### Validation Rules

The ContextBuilder enforces these rules:

1. **Single context must be named "default"** - If you have only one context, it must be named "default"
2. **Each context must have at least one step**
3. **valid_steps references must exist** - Steps referenced in `set_valid_steps()` must exist in the same context
4. **valid_contexts references must exist** - Contexts referenced in `set_valid_contexts()` must exist

## Helper Function

### create_simple_context()

Create a simple context without an agent:

```python
from signalwire_agents import create_simple_context

context = create_simple_context("default")
step = context.add_step("greet")
step.set_text("Greet the user.")
```

## Complete Example

```python
#!/usr/bin/env python3
from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult


class AppointmentScheduler(AgentBase):
    """Agent that schedules appointments using contexts and steps."""

    def __init__(self):
        super().__init__(name="appointment-scheduler", port=3000)

        self.add_language("English", "en-US", "rime.spore")
        self.define_contexts()

    def define_contexts(self):
        # Main scheduling context
        ctx = self.contexts.add_context("default")

        # Step 1: Greeting
        greeting = ctx.add_step("greeting")
        greeting.add_section("Task", "Welcome the caller and offer to help schedule an appointment.")
        greeting.set_step_criteria("Caller confirms they want to schedule an appointment")
        greeting.set_valid_steps(["next"])
        greeting.set_functions("none")

        # Step 2: Get service type
        service = ctx.add_step("get_service")
        service.set_text(
            "Ask what type of appointment they need. "
            "Options are: consultation, follow-up, or new patient visit."
        )
        service.set_step_criteria("Caller specifies the appointment type")
        service.set_functions(["set_appointment_type"])
        service.set_valid_steps(["next", "greeting"])

        # Step 3: Get preferred date/time
        datetime_step = ctx.add_step("get_datetime")
        datetime_step.set_text(
            "Ask for their preferred date and time. "
            "Check availability using the check_availability function."
        )
        datetime_step.set_step_criteria("An available slot is selected")
        datetime_step.set_functions(["check_availability", "suggest_alternative"])
        datetime_step.set_valid_steps(["next", "get_service"])

        # Step 4: Get contact info
        contact = ctx.add_step("get_contact")
        contact.set_text(
            "Collect the caller's name and phone number for confirmation."
        )
        contact.set_step_criteria("Name and phone number are recorded")
        contact.set_functions(["save_contact_info"])
        contact.set_valid_steps(["next"])

        # Step 5: Confirm booking
        confirm = ctx.add_step("confirm")
        confirm.set_text(
            "Summarize the appointment details and ask for confirmation. "
            "If confirmed, book the appointment."
        )
        confirm.set_step_criteria("Appointment is confirmed or caller wants to modify")
        confirm.set_functions(["book_appointment", "send_confirmation"])
        confirm.set_valid_steps(["complete", "get_service", "get_datetime"])

        # Step 6: Complete
        complete = ctx.add_step("complete")
        complete.set_text(
            "Thank the caller and provide any final instructions. "
            "Remind them of the appointment time."
        )
        complete.set_functions("none")

    @AgentBase.tool(
        name="set_appointment_type",
        description="Record the type of appointment requested",
        parameters={
            "type": {
                "type": "string",
                "description": "Appointment type",
                "enum": ["consultation", "follow-up", "new_patient"]
            }
        }
    )
    def set_appointment_type(self, args, raw_data):
        appt_type = args.get("type")
        return SwaigFunctionResult(f"Appointment type set to: {appt_type}").add_action(
            "set_global_data", {"appointment_type": appt_type}
        )

    @AgentBase.tool(
        name="check_availability",
        description="Check availability for a date and time",
        parameters={
            "date": {"type": "string", "description": "Requested date (YYYY-MM-DD)"},
            "time": {"type": "string", "description": "Requested time (HH:MM)"}
        }
    )
    def check_availability(self, args, raw_data):
        date = args.get("date")
        time = args.get("time")
        # In a real implementation, check against a calendar system
        return SwaigFunctionResult(f"The slot on {date} at {time} is available.")

    @AgentBase.tool(
        name="book_appointment",
        description="Book the confirmed appointment",
        parameters={}
    )
    def book_appointment(self, args, raw_data):
        return SwaigFunctionResult("Appointment has been booked successfully.")


if __name__ == "__main__":
    agent = AppointmentScheduler()
    agent.run()
```

## Best Practices

1. **Use meaningful step names** - Names should describe the step's purpose
2. **Define clear step criteria** - Be specific about what completes a step
3. **Restrict functions appropriately** - Only expose functions needed at each step
4. **Use valid_steps for flow control** - Prevent unexpected navigation
5. **Consider using contexts for major mode changes** - Contexts are good for different "phases"
6. **Use fillers for smooth transitions** - Enter/exit fillers make context switches feel natural

## See Also

- [Agent Base Reference](agent-base.md) - Complete AgentBase documentation
- [SWAIG Functions Reference](swaig-functions.md) - Function definition patterns
- [Prefab Agents](prefabs.md) - Pre-built agents that use contexts
