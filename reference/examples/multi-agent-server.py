#!/usr/bin/env python3
"""
Multi-Agent Server Example

Demonstrates hosting multiple specialized agents on a single server
with static file serving for a web UI.

Run with: python multi-agent-server.py
Test with: swaig-test multi-agent-server.py --agent-class SupportAgent --dump-swml
"""

from signalwire_agents import AgentBase, AgentServer
from signalwire_agents.core.function_result import SwaigFunctionResult
from pathlib import Path
import os

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "3000"))


class SupportAgent(AgentBase):
    """Handles customer support inquiries."""

    def __init__(self):
        super().__init__(name="support-agent")

        # Voice configuration
        self.add_language("English", "en-US", "rime.spore")

        # Prompt
        self.prompt_add_section(
            "Role",
            "You are a friendly customer support agent for Acme Corp."
        )
        self.prompt_add_section(
            "Guidelines",
            bullets=[
                "Help customers resolve issues",
                "Escalate complex problems to human agents",
                "Always be polite and professional",
                "Use lookup_order to check order status",
                "Use escalate to transfer to a human"
            ]
        )

        # AI behavior
        self.set_params({
            "end_of_speech_timeout": 1000,
            "attention_timeout": 15000
        })

    @AgentBase.tool(
        name="lookup_order",
        description="Look up order status by order number",
        parameters={
            "order_number": {
                "type": "string",
                "description": "The order number (e.g., ORD-12345)"
            }
        },
        fillers=["Let me check that order for you", "One moment please"]
    )
    def lookup_order(self, args, raw_data):
        order_num = args.get("order_number", "unknown")
        # In production, query your database
        return SwaigFunctionResult(
            f"Order {order_num} was shipped on Monday via FedEx. "
            "It should arrive by Friday. Would you like the tracking number?"
        )

    @AgentBase.tool(
        name="escalate",
        description="Transfer to a human support agent",
        parameters={
            "reason": {
                "type": "string",
                "description": "Reason for escalation"
            }
        }
    )
    def escalate(self, args, raw_data):
        reason = args.get("reason", "Customer requested transfer")
        return (SwaigFunctionResult(
            "I'll connect you with a support specialist who can help further. "
            "Please hold while I transfer you."
        )
        .add_action("set_global_data", {"escalation_reason": reason})
        .add_action("transfer", {"dest": "sip:support@company.com"}))


class SalesAgent(AgentBase):
    """Handles sales inquiries and product questions."""

    def __init__(self):
        super().__init__(name="sales-agent")

        self.add_language("English", "en-US", "rime.spore")

        self.prompt_add_section(
            "Role",
            "You are an enthusiastic sales representative for Acme Corp."
        )
        self.prompt_add_section(
            "Guidelines",
            bullets=[
                "Help customers find the right products",
                "Answer questions about pricing and features",
                "Use get_product_info to look up product details",
                "Be enthusiastic but not pushy"
            ]
        )

        self.set_params({
            "end_of_speech_timeout": 1500,
            "attention_timeout": 20000
        })

    @AgentBase.tool(
        name="get_product_info",
        description="Get information about a product",
        parameters={
            "product_name": {
                "type": "string",
                "description": "Name of the product"
            }
        }
    )
    def get_product_info(self, args, raw_data):
        product = args.get("product_name", "")
        # In production, query product database
        return SwaigFunctionResult(
            f"The {product} is one of our most popular items! "
            "It's priced at $99.99 and comes with a 30-day money-back guarantee. "
            "Would you like me to tell you more about its features?"
        )

    @AgentBase.tool(
        name="schedule_demo",
        description="Schedule a product demonstration",
        parameters={
            "product": {"type": "string", "description": "Product for demo"},
            "preferred_time": {"type": "string", "description": "Preferred time"}
        }
    )
    def schedule_demo(self, args, raw_data):
        product = args.get("product", "our products")
        time = args.get("preferred_time", "a convenient time")
        caller = raw_data.get("call", {}).get("from", "unknown")

        return (SwaigFunctionResult(
            f"I've scheduled a demo of {product} for {time}. "
            "You'll receive a confirmation email shortly with the details. "
            "Is there anything else I can help you with?"
        )
        .add_action("set_global_data", {
            "demo_scheduled": True,
            "demo_product": product,
            "customer_phone": caller
        }))


class BillingAgent(AgentBase):
    """Handles billing and payment inquiries."""

    def __init__(self):
        super().__init__(name="billing-agent")

        self.add_language("English", "en-US", "rime.spore")

        self.prompt_add_section(
            "Role",
            "You are a billing specialist for Acme Corp."
        )
        self.prompt_add_section(
            "Guidelines",
            bullets=[
                "Help customers with billing questions",
                "Use get_balance to check account balance",
                "Use process_payment to take payments",
                "Always verify customer identity before discussing account details"
            ]
        )

        # Stricter timeout for billing
        self.set_params({
            "end_of_speech_timeout": 800,
            "inactivity_timeout": 180000  # 3 minutes
        })

    @AgentBase.tool(
        name="get_balance",
        description="Get account balance (requires verification)",
        parameters={
            "account_number": {
                "type": "string",
                "description": "Customer account number"
            }
        }
    )
    def get_balance(self, args, raw_data):
        account = args.get("account_number")
        verified = raw_data.get("vars", {}).get("verified", False)

        if not verified:
            return SwaigFunctionResult(
                "For security, I need to verify your identity first. "
                "Can you please provide the last four digits of your Social Security number?"
            )

        # In production, query billing system
        return SwaigFunctionResult(
            f"Your current balance for account {account} is $156.78. "
            "Your next payment is due on the 15th. "
            "Would you like to make a payment today?"
        )

    @AgentBase.tool(
        name="process_payment",
        description="Process a payment on the account",
        parameters={
            "amount": {"type": "number", "description": "Payment amount"},
            "confirm": {"type": "boolean", "description": "Payment confirmed", "default": False}
        }
    )
    def process_payment(self, args, raw_data):
        amount = args.get("amount", 0)
        confirmed = args.get("confirm", False)

        if not confirmed:
            return SwaigFunctionResult(
                f"I can process a payment of ${amount:.2f}. "
                "This will be charged to your card on file ending in 4242. "
                "Do you confirm this payment?"
            )

        return (SwaigFunctionResult(
            f"Payment of ${amount:.2f} has been processed successfully. "
            "You'll receive a confirmation email shortly. "
            "Is there anything else I can help you with?"
        )
        .add_action("send_sms", {
            "to": raw_data.get("call", {}).get("from"),
            "body": f"Acme Corp: Payment of ${amount:.2f} confirmed. Thank you!"
        }))


if __name__ == "__main__":
    # Create server
    server = AgentServer(host=HOST, port=PORT)

    # Register all agents
    server.register(SupportAgent(), "/support")
    server.register(SalesAgent(), "/sales")
    server.register(BillingAgent(), "/billing")

    # Optionally serve static files
    web_dir = Path(__file__).parent / "web"
    if web_dir.exists():
        server.serve_static_files(str(web_dir))
        print(f"Web UI: http://{HOST}:{PORT}/")

    print(f"Support agent: http://{HOST}:{PORT}/support")
    print(f"Sales agent: http://{HOST}:{PORT}/sales")
    print(f"Billing agent: http://{HOST}:{PORT}/billing")

    server.run()
