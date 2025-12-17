#!/usr/bin/env python3
"""
DataMap Agent Example

Demonstrates using DataMap for server-side functions that:
- Call external APIs without custom handlers
- Use expression templates for responses
- Combine with regular @tool functions

DataMap is useful when you just need to call an API and format the response,
without complex logic in your Python code.

Run with: python datamap-agent.py
Test with: swaig-test datamap-agent.py --dump-swml
"""

from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult
from signalwire_agents.core.data_map import DataMap
import os


class DataMapAgent(AgentBase):
    """Agent demonstrating DataMap for server-side API calls."""

    def __init__(self):
        super().__init__(name="datamap-agent", port=3000)

        # Voice configuration
        self.add_language("English", "en-US", "rime.spore")

        # Build prompt
        self.prompt_add_section(
            "Role",
            "You are a helpful assistant that can look up weather, "
            "search Wikipedia, and answer general questions."
        )

        self.prompt_add_section(
            "Guidelines",
            bullets=[
                "Use get_weather to check weather conditions",
                "Use search_wikipedia for general knowledge questions",
                "Use get_random_fact for fun facts",
                "Keep responses conversational and concise"
            ]
        )

        # Configure AI
        self.set_params({
            "end_of_speech_timeout": 1000,
            "attention_timeout": 15000
        })

        # Register DataMap functions
        self._register_datamap_functions()

    def _register_datamap_functions(self):
        """Register server-side DataMap functions."""

        # Weather API (using wttr.in - no API key needed)
        weather_map = (DataMap("get_weather")
            .purpose("Get current weather for a city")
            .parameter("city", "string", "City name", required=True)
            .webhook(
                "GET",
                "https://wttr.in/${lc:args.city}?format=j1"
            )
            .output(SwaigFunctionResult(
                "The weather in ${args.city} is currently "
                "${response.current_condition[0].temp_F} degrees Fahrenheit "
                "with ${response.current_condition[0].weatherDesc[0].value}. "
                "Humidity is ${response.current_condition[0].humidity}%."
            ))
        )
        self.register_swaig_function(weather_map.to_swaig_function())

        # Wikipedia search
        wiki_map = (DataMap("search_wikipedia")
            .purpose("Search Wikipedia for information about a topic")
            .parameter("query", "string", "Search query", required=True)
            .webhook(
                "GET",
                "https://en.wikipedia.org/api/rest_v1/page/summary/${enc:args.query}"
            )
            .output(SwaigFunctionResult(
                "${response.extract}"
            ))
        )
        self.register_swaig_function(wiki_map.to_swaig_function())

        # Random fact (using uselessfacts.jsph.pl)
        fact_map = (DataMap("get_random_fact")
            .purpose("Get a random interesting fact")
            .webhook(
                "GET",
                "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en"
            )
            .output(SwaigFunctionResult(
                "Here's an interesting fact: ${response.text}"
            ))
        )
        self.register_swaig_function(fact_map.to_swaig_function())

        # IP geolocation (using ip-api.com)
        geo_map = (DataMap("get_location_from_ip")
            .purpose("Get geographic location from an IP address")
            .parameter("ip", "string", "IP address to look up", required=True)
            .webhook(
                "GET",
                "http://ip-api.com/json/${args.ip}"
            )
            .output(SwaigFunctionResult(
                "IP address ${args.ip} is located in ${response.city}, "
                "${response.regionName}, ${response.country}. "
                "The ISP is ${response.isp}."
            ))
        )
        self.register_swaig_function(geo_map.to_swaig_function())

    # Mix DataMap with regular @tool functions

    @AgentBase.tool(
        name="calculate",
        description="Perform a mathematical calculation",
        parameters={
            "expression": {
                "type": "string",
                "description": "Mathematical expression (e.g., '2 + 2', '10 * 5')"
            }
        }
    )
    def calculate(self, args, raw_data):
        """Perform safe math calculation."""
        expression = args.get("expression", "")

        # Only allow safe characters
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return SwaigFunctionResult(
                "I can only do basic math with numbers and operators. "
                "Try something like '10 plus 5' or '100 divided by 4'."
            )

        try:
            # Evaluate safely
            result = eval(expression, {"__builtins__": {}}, {})
            return SwaigFunctionResult(
                f"The result of {expression} is {result}."
            )
        except Exception:
            return SwaigFunctionResult(
                "I couldn't calculate that. Could you rephrase it?"
            )

    @AgentBase.tool(
        name="end_call",
        description="End the conversation politely",
        parameters={}
    )
    def end_call(self, args, raw_data):
        """End the call."""
        return SwaigFunctionResult(
            "Thanks for chatting! Have a great day. Goodbye!",
            post_process=True
        ).add_action("hangup", {})


if __name__ == "__main__":
    agent = DataMapAgent()
    print(f"Starting {agent.name} on port {agent.port}...")
    print("\nRegistered functions:")
    print("  - get_weather (DataMap) - Weather from wttr.in")
    print("  - search_wikipedia (DataMap) - Wikipedia summaries")
    print("  - get_random_fact (DataMap) - Random facts")
    print("  - get_location_from_ip (DataMap) - IP geolocation")
    print("  - calculate (@tool) - Math calculations")
    print("  - end_call (@tool) - End conversation")
    agent.run()
