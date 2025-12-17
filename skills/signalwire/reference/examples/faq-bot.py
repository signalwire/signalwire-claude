#!/usr/bin/env python3
"""
FAQ Bot Example

Demonstrates an agent that:
- Uses built-in skills (datetime, web_search)
- Has a knowledge base of FAQs
- Transfers to human when needed

Run with: python faq-bot.py
Test with: swaig-test faq-bot.py --dump-swml
"""

from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult
import os

# FAQ knowledge base
FAQS = {
    "hours": {
        "question": "What are your hours?",
        "answer": "We're open Monday through Friday, 9 AM to 5 PM Eastern Time. "
                  "We're closed on weekends and major holidays."
    },
    "returns": {
        "question": "What is your return policy?",
        "answer": "You can return any item within 30 days of purchase for a full refund. "
                  "Items must be in original condition with tags attached. "
                  "We'll provide a prepaid shipping label."
    },
    "shipping": {
        "question": "How long does shipping take?",
        "answer": "Standard shipping takes 5-7 business days. "
                  "Express shipping takes 2-3 business days. "
                  "Free shipping on orders over $50."
    },
    "payment": {
        "question": "What payment methods do you accept?",
        "answer": "We accept all major credit cards including Visa, Mastercard, "
                  "American Express, and Discover. We also accept PayPal and Apple Pay."
    },
    "warranty": {
        "question": "Do your products have a warranty?",
        "answer": "All our products come with a 1-year manufacturer's warranty. "
                  "Electronics have an extended 2-year warranty. "
                  "Contact support for warranty claims."
    },
    "contact": {
        "question": "How can I contact customer service?",
        "answer": "You can reach us by phone at 1-800-555-0123, "
                  "by email at support@example.com, or through live chat on our website. "
                  "Phone support is available during business hours."
    }
}


class FAQBot(AgentBase):
    """FAQ bot with knowledge base and skill integration."""

    def __init__(self):
        super().__init__(name="faq-bot", port=3000)

        # Voice configuration
        self.add_language(
            "English",
            "en-US",
            "rime.spore",
            function_fillers=[
                "Let me check that for you",
                "One moment please"
            ]
        )

        # Add built-in skills
        self.add_skill("datetime", {"timezone": "America/New_York"})

        # Optionally add web search if API keys available
        if os.getenv("GOOGLE_API_KEY") and os.getenv("GOOGLE_SEARCH_ENGINE_ID"):
            self.add_skill("web_search", {
                "api_key": os.environ["GOOGLE_API_KEY"],
                "search_engine_id": os.environ["GOOGLE_SEARCH_ENGINE_ID"]
            })

        # Build the prompt
        self.prompt_add_section(
            "Role",
            "You are a friendly FAQ assistant for Acme Corp. "
            "You help customers with common questions about our products and services."
        )

        self.prompt_add_section(
            "Guidelines",
            body="Follow these guidelines:",
            bullets=[
                "Answer questions using the FAQ lookup function when possible",
                "Be friendly and conversational",
                "Keep responses concise - this is a voice conversation",
                "If you don't know the answer, offer to transfer to a human",
                "Use the datetime skill to tell users the current time or date",
                "Use web_search for questions not in the FAQ (if available)"
            ]
        )

        self.prompt_add_section(
            "Available Topics",
            body="You can answer questions about:",
            bullets=[
                "Business hours",
                "Return policy",
                "Shipping times and costs",
                "Payment methods",
                "Product warranty",
                "Contact information"
            ]
        )

        # Configure AI behavior
        self.set_params({
            "end_of_speech_timeout": 1200,
            "attention_timeout": 15000,
            "inactivity_timeout": 300000
        })

        # Add speech recognition hints
        self.add_hints([
            "FAQ", "hours", "returns", "shipping",
            "warranty", "payment", "refund"
        ])

    @AgentBase.tool(
        name="lookup_faq",
        description="Look up an answer from the FAQ knowledge base",
        parameters={
            "topic": {
                "type": "string",
                "description": "The FAQ topic to look up",
                "enum": ["hours", "returns", "shipping", "payment", "warranty", "contact"]
            }
        }
    )
    def lookup_faq(self, args, raw_data):
        """Look up FAQ answer by topic."""
        topic = args.get("topic", "").lower()

        faq = FAQS.get(topic)
        if faq:
            return SwaigFunctionResult(faq["answer"])
        else:
            return SwaigFunctionResult(
                "I don't have information about that topic. "
                "Would you like me to transfer you to a customer service representative?"
            )

    @AgentBase.tool(
        name="list_faq_topics",
        description="List all available FAQ topics",
        parameters={}
    )
    def list_faq_topics(self, args, raw_data):
        """List all FAQ topics."""
        topics = [faq["question"] for faq in FAQS.values()]
        topic_list = ". ".join(topics)

        return SwaigFunctionResult(
            f"I can help you with the following topics: {topic_list}. "
            "What would you like to know about?"
        )

    @AgentBase.tool(
        name="transfer_to_human",
        description="Transfer to a human customer service representative",
        parameters={
            "reason": {
                "type": "string",
                "description": "Reason for transfer",
                "default": "Customer requested human assistance"
            }
        }
    )
    def transfer_to_human(self, args, raw_data):
        """Transfer to human support."""
        reason = args.get("reason", "Customer requested assistance")

        return (SwaigFunctionResult(
            "I'll connect you with a customer service representative now. "
            "Please hold while I transfer you."
        )
        .add_action("set_global_data", {"transfer_reason": reason})
        .add_action("transfer", {"dest": "sip:support@company.com"}))

    @AgentBase.tool(
        name="end_call",
        description="End the call when the customer is done",
        parameters={}
    )
    def end_call(self, args, raw_data):
        """Politely end the call."""
        return SwaigFunctionResult(
            "Thank you for calling Acme Corp! Have a great day. Goodbye!",
            post_process=True
        ).add_action("hangup", {})


if __name__ == "__main__":
    agent = FAQBot()
    print(f"Starting {agent.name} on port {agent.port}...")
    print(f"FAQ topics available: {list(FAQS.keys())}")

    if agent.has_skill("web_search"):
        print("Web search skill enabled")
    else:
        print("Web search skill disabled (set GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID)")

    agent.run()
