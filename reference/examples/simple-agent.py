#!/usr/bin/env python3
"""
Simple SignalWire AI Agent Example

This template demonstrates a basic agent with:
- Voice configuration
- Prompt building
- AI parameters
- A simple SWAIG function

Run with: python simple-agent.py
Test with: swaig-test simple-agent.py --dump-swml
"""

from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult


class SimpleAgent(AgentBase):
    """A simple conversational AI agent."""

    def __init__(self):
        super().__init__(
            name="simple-agent",
            port=3000
        )

        # Configure voice - required for the agent to speak
        self.add_language("English", "en-US", "rime.spore")

        # Build the prompt
        self.prompt_add_section(
            "Role",
            "You are a friendly and helpful AI assistant."
        )

        self.prompt_add_section(
            "Guidelines",
            body="Follow these guidelines when interacting with users:",
            bullets=[
                "Be conversational and natural",
                "Keep responses concise - this is a voice conversation",
                "Ask clarifying questions when needed",
                "Use the get_time function when asked about the current time"
            ]
        )

        # Configure AI behavior
        self.set_params({
            "end_of_speech_timeout": 1000,    # 1 second of silence ends turn
            "attention_timeout": 10000,        # 10 seconds before "are you there?"
            "inactivity_timeout": 300000       # 5 minutes before disconnect
        })

    @AgentBase.tool(
        name="get_time",
        description="Get the current date and time",
        parameters={}
    )
    def get_time(self, args, raw_data):
        """Return the current date and time."""
        from datetime import datetime

        now = datetime.now()
        return SwaigFunctionResult(
            f"The current time is {now.strftime('%I:%M %p')} "
            f"on {now.strftime('%A, %B %d, %Y')}."
        )


if __name__ == "__main__":
    agent = SimpleAgent()
    print(f"Starting {agent.name} on port {agent.port}...")
    agent.run()
