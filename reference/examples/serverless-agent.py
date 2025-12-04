#!/usr/bin/env python3
"""Serverless agent example for AWS Lambda, Google Cloud Functions, or Azure.

This example demonstrates deploying a SignalWire AI Agent to serverless
platforms with SWAIG functions.

Environment variables:
    SWML_BASIC_AUTH_USER: Basic auth username (optional)
    SWML_BASIC_AUTH_PASSWORD: Basic auth password (optional)

AWS Lambda requirements.txt:
    signalwire-agents>=1.0.10
    h11>=0.13,<0.15
    fastapi
    mangum
    uvicorn

Google Cloud Functions requirements.txt:
    signalwire-agents>=1.0.10
    functions-framework>=3.0.0

Azure Functions requirements.txt:
    azure-functions>=1.17.0
    signalwire-agents>=1.0.10
"""

import os
from signalwire_agents import AgentBase, SwaigFunctionResult


class CustomerServiceAgent(AgentBase):
    """Customer service agent for serverless deployment."""

    def __init__(self):
        super().__init__(name="customer-service-serverless")

        self._configure_prompts()
        self.add_language("English", "en-US", "rime.spore")
        self._setup_functions()

        # Optional: Add skills
        self.add_skill("datetime", {"timezone": "America/New_York"})

    def _configure_prompts(self):
        self.prompt_add_section(
            "Role",
            "You are a helpful customer service agent deployed on a serverless platform."
        )

        self.prompt_add_section(
            "Guidelines",
            bullets=[
                "Be friendly and professional",
                "Use lookup_order when customers ask about their orders",
                "Provide accurate information",
                "Transfer to human support when needed"
            ]
        )

    def _setup_functions(self):
        @self.tool(
            description="Look up an order by order number",
            parameters={
                "type": "object",
                "properties": {
                    "order_number": {
                        "type": "string",
                        "description": "The order number to look up"
                    }
                },
                "required": ["order_number"]
            },
            fillers=["Let me check that order for you", "One moment please"]
        )
        def lookup_order(args, raw_data):
            order_num = args.get("order_number", "")
            # In production, query your database here
            # Example: DynamoDB, Cloud SQL, Cosmos DB, etc.
            return SwaigFunctionResult(
                f"Order {order_num} was shipped on Monday and will arrive by Friday."
            )

        @self.tool(
            description="Transfer the call to human support",
            parameters={
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Reason for the transfer"
                    }
                }
            }
        )
        def transfer_to_support(args, raw_data):
            reason = args.get("reason", "customer request")
            return (
                SwaigFunctionResult(f"Transferring you to a specialist for: {reason}")
                .add_action("transfer", {"dest": "sip:support@example.com"})
            )

        @self.tool(description="Get the current platform runtime information")
        def get_runtime_info(args, raw_data):
            # Detect which platform we're running on
            if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
                platform = "AWS Lambda"
                details = f"Function: {os.getenv('AWS_LAMBDA_FUNCTION_NAME')}, Region: {os.getenv('AWS_REGION')}"
            elif os.getenv("K_SERVICE"):
                platform = "Google Cloud Functions"
                details = f"Service: {os.getenv('K_SERVICE')}, Revision: {os.getenv('K_REVISION')}"
            elif os.getenv("FUNCTIONS_WORKER_RUNTIME"):
                platform = "Azure Functions"
                details = f"App: {os.getenv('WEBSITE_SITE_NAME')}, Region: {os.getenv('REGION_NAME')}"
            else:
                platform = "Local/Unknown"
                details = "Running locally or in unknown environment"

            return SwaigFunctionResult(f"Running on {platform}. {details}")


# CRITICAL: Create agent instance OUTSIDE handler for cold start optimization
# This ensures the agent is only initialized once per container instance
agent = CustomerServiceAgent()


# ============================================================
# AWS Lambda Handler
# ============================================================
def lambda_handler(event, context):
    """AWS Lambda entry point.

    Configure API Gateway with:
    - Routes: GET /, POST /, POST /swaig, ANY /{proxy+}
    - Integration: Lambda proxy (AWS_PROXY)

    Args:
        event: API Gateway event
        context: Lambda context

    Returns:
        API Gateway response dict
    """
    return agent.run(event, context)


# ============================================================
# Google Cloud Functions Handler
# ============================================================
def main(request):
    """Google Cloud Functions entry point.

    Deploy with:
        gcloud functions deploy customer-service \
            --gen2 \
            --runtime python311 \
            --trigger-http \
            --allow-unauthenticated \
            --entry-point main

    Args:
        request: Flask request object

    Returns:
        Flask response
    """
    return agent.run(request)


# ============================================================
# Azure Functions Handler
# ============================================================
# Uncomment and add to __init__.py in your function app:
#
# import azure.functions as func
#
# def main(req: func.HttpRequest) -> func.HttpResponse:
#     """Azure Functions entry point.
#
#     Configure function.json with:
#         {
#             "bindings": [{
#                 "authLevel": "anonymous",
#                 "type": "httpTrigger",
#                 "direction": "in",
#                 "name": "req",
#                 "methods": ["get", "post"],
#                 "route": "{*path}"
#             }, {
#                 "type": "http",
#                 "direction": "out",
#                 "name": "$return"
#             }]
#         }
#
#     Args:
#         req: Azure HTTP request
#
#     Returns:
#         Azure HTTP response
#     """
#     return agent.run(req)
