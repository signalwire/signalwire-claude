# Error Handling Patterns

Best practices for handling errors in SignalWire AI Agents.

## Core Principle

Never expose technical errors to users. Always provide helpful, conversational fallbacks.

## Basic Try-Except Pattern

```python
@AgentBase.tool(
    name="get_account_info",
    description="Get account information",
    parameters={
        "account_id": {"type": "string", "description": "Account ID"}
    }
)
def get_account_info(self, args, raw_data):
    account_id = args.get("account_id")

    try:
        account = self.api.get_account(account_id)
        return SwaigFunctionResult(
            f"Your account balance is ${account['balance']:.2f}. "
            f"Your next payment is due on {account['due_date']}."
        )

    except AccountNotFoundError:
        return SwaigFunctionResult(
            "I couldn't find that account number. "
            "Could you double-check it and try again?"
        )

    except APIError as e:
        # Log for debugging, but don't expose to user
        self.log.error("api_error", error=str(e), account_id=account_id)
        return SwaigFunctionResult(
            "I'm having trouble accessing account information right now. "
            "Would you like me to transfer you to someone who can help?"
        )

    except Exception as e:
        self.log.error("unexpected_error", error=str(e))
        return SwaigFunctionResult(
            "Something went wrong on my end. "
            "Let me connect you with a representative."
        ).add_action("transfer", {"dest": "sip:support@company.com"})
```

## Validation Errors

Validate inputs and provide clear guidance:

```python
@AgentBase.tool(
    name="schedule_appointment",
    description="Schedule an appointment",
    parameters={
        "date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
        "time": {"type": "string", "description": "Time (HH:MM)"}
    }
)
def schedule_appointment(self, args, raw_data):
    date_str = args.get("date", "")
    time_str = args.get("time", "")

    # Validate date format
    try:
        from datetime import datetime
        apt_datetime = datetime.strptime(
            f"{date_str} {time_str}",
            "%Y-%m-%d %H:%M"
        )
    except ValueError:
        return SwaigFunctionResult(
            "I didn't quite catch that date and time. "
            "Could you say it like 'January 15th at 2 PM'?"
        )

    # Validate not in past
    if apt_datetime < datetime.now():
        return SwaigFunctionResult(
            "That time has already passed. "
            "When would you like to schedule instead?"
        )

    # Validate business hours
    if apt_datetime.hour < 9 or apt_datetime.hour >= 17:
        return SwaigFunctionResult(
            "We're only open from 9 AM to 5 PM. "
            "What time during business hours works for you?"
        )

    # Proceed with booking...
```

## Missing Required Data

Handle missing information conversationally:

```python
@AgentBase.tool(
    name="process_refund",
    description="Process a refund request",
    parameters={
        "order_number": {"type": "string", "description": "Order number"},
        "reason": {"type": "string", "description": "Reason for refund"}
    }
)
def process_refund(self, args, raw_data):
    order_number = args.get("order_number")
    reason = args.get("reason")

    # Check for missing data
    if not order_number:
        return SwaigFunctionResult(
            "I'd be happy to help with that refund. "
            "What's the order number?"
        )

    if not reason:
        return SwaigFunctionResult(
            f"I found order {order_number}. "
            "Could you tell me why you'd like a refund?"
        )

    # Proceed with refund...
```

## External Service Failures

Handle third-party API failures gracefully:

```python
@AgentBase.tool(
    name="get_weather",
    description="Get current weather",
    parameters={
        "city": {"type": "string", "description": "City name"}
    }
)
def get_weather(self, args, raw_data):
    city = args.get("city")

    try:
        weather = self.weather_api.get_current(city)
        return SwaigFunctionResult(
            f"The weather in {city} is currently {weather['temp']}°F "
            f"and {weather['condition']}."
        )

    except requests.Timeout:
        return SwaigFunctionResult(
            "The weather service is taking too long to respond. "
            "Would you like me to try again?"
        )

    except requests.ConnectionError:
        return SwaigFunctionResult(
            "I'm having trouble reaching the weather service right now. "
            "Is there something else I can help you with?"
        )

    except KeyError:
        return SwaigFunctionResult(
            f"I couldn't find weather data for {city}. "
            "Could you check the spelling or try a nearby city?"
        )
```

## Rate Limit Handling

Handle API rate limits gracefully:

```python
@AgentBase.tool(
    name="search_products",
    description="Search product catalog",
    parameters={
        "query": {"type": "string", "description": "Search query"}
    }
)
def search_products(self, args, raw_data):
    query = args.get("query")

    try:
        results = self.catalog_api.search(query)
        # Process results...

    except RateLimitError as e:
        retry_after = e.retry_after or 30
        return SwaigFunctionResult(
            "I'm getting a lot of requests right now. "
            f"Could you give me about {retry_after} seconds and ask again?"
        )
```

## Database Errors

Handle database connectivity issues:

```python
@AgentBase.tool(
    name="check_inventory",
    description="Check product inventory",
    parameters={
        "product_id": {"type": "string", "description": "Product ID"}
    }
)
def check_inventory(self, args, raw_data):
    product_id = args.get("product_id")

    try:
        inventory = self.db.get_inventory(product_id)
        if inventory > 0:
            return SwaigFunctionResult(
                f"Good news! We have {inventory} in stock."
            )
        else:
            return SwaigFunctionResult(
                "That item is currently out of stock. "
                "Would you like me to notify you when it's available?"
            )

    except DatabaseConnectionError:
        self.log.error("db_connection_failed", product_id=product_id)
        return SwaigFunctionResult(
            "I'm having trouble checking inventory at the moment. "
            "Would you like me to transfer you to someone who can check manually?"
        )

    except DatabaseQueryError as e:
        self.log.error("db_query_error", error=str(e), product_id=product_id)
        return SwaigFunctionResult(
            "I encountered an issue looking that up. "
            "Can you tell me the product name instead of the ID?"
        )
```

## Escalation on Repeated Failures

Automatically escalate after multiple failures:

```python
class ResilientAgent(AgentBase):
    def __init__(self):
        super().__init__(name="resilient-agent")
        self._failure_counts = {}

    def _track_failure(self, call_id: str, operation: str) -> int:
        key = f"{call_id}:{operation}"
        count = self._failure_counts.get(key, 0) + 1
        self._failure_counts[key] = count
        return count

    @AgentBase.tool(
        name="lookup_order",
        description="Look up order details",
        parameters={
            "order_number": {"type": "string", "description": "Order number"}
        }
    )
    def lookup_order(self, args, raw_data):
        call_id = raw_data.get("call_id", "unknown")
        order_number = args.get("order_number")

        try:
            order = self.api.get_order(order_number)
            return SwaigFunctionResult(f"Order {order_number}: {order['status']}")

        except Exception as e:
            failures = self._track_failure(call_id, "lookup_order")

            if failures >= 3:
                return SwaigFunctionResult(
                    "I apologize - I've been unable to look up your order. "
                    "Let me connect you with someone who can help directly."
                ).add_action("transfer", {"dest": "sip:support@company.com"})

            return SwaigFunctionResult(
                "I had trouble with that lookup. "
                "Could you repeat the order number?"
            )
```

## Timeout Handling

Handle long-running operations:

```python
import asyncio
from concurrent.futures import TimeoutError

@AgentBase.tool(
    name="complex_search",
    description="Search across multiple systems",
    parameters={
        "query": {"type": "string", "description": "Search query"}
    },
    fillers=["Let me search our systems", "This might take a moment"]
)
def complex_search(self, args, raw_data):
    query = args.get("query")

    try:
        # Set a timeout for the operation
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Search took too long")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(25)  # 25 second timeout

        try:
            results = self.search_all_systems(query)
            return SwaigFunctionResult(f"Found {len(results)} results: ...")
        finally:
            signal.alarm(0)  # Cancel alarm

    except TimeoutError:
        return SwaigFunctionResult(
            "That search is taking longer than expected. "
            "Would you like me to narrow it down? "
            "For example, you could specify a date range or category."
        )
```

## Logging Best Practices

Always log errors for debugging without exposing to users:

```python
import logging

class LoggingAgent(AgentBase):
    def __init__(self):
        super().__init__(name="logging-agent")
        self.logger = logging.getLogger("agent")

    @AgentBase.tool(
        name="sensitive_operation",
        description="Perform sensitive operation",
        parameters={}
    )
    def sensitive_operation(self, args, raw_data):
        call_id = raw_data.get("call_id")
        caller = raw_data.get("call", {}).get("from", "unknown")

        try:
            result = self.do_sensitive_thing()
            self.logger.info(
                "Operation successful",
                extra={
                    "call_id": call_id,
                    "caller": caller,
                    "operation": "sensitive_operation"
                }
            )
            return SwaigFunctionResult("Done!")

        except Exception as e:
            # Log detailed error for debugging
            self.logger.error(
                "Operation failed",
                extra={
                    "call_id": call_id,
                    "caller": caller,
                    "operation": "sensitive_operation",
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                },
                exc_info=True  # Include stack trace
            )

            # Return friendly message to user
            return SwaigFunctionResult(
                "I ran into an issue. Would you like to try again "
                "or speak with a representative?"
            )
```

## Error Response Guidelines

1. **Never expose technical details** - No stack traces, error codes, or system names
2. **Be conversational** - Sound like a helpful person, not an error message
3. **Offer alternatives** - Give the user a path forward
4. **Log everything** - Capture details for debugging
5. **Know when to escalate** - Transfer to humans when appropriate
6. **Be specific when helpful** - "Check the order number" is better than "try again"
