# AI Agent Text Chat

Talk to an AI agent by text instead of by voice. Agents that were reachable only over a phone call can now back a web chat widget, a support inbox, or an automated test harness. Shipped 2026-08-17.

Docs: `/docs/apis/rest/ai-chat/chat-methods`

## It is JSON-RPC, not REST

**One endpoint. Six methods. Not six routes.** A builder who assumes REST will construct URLs that do not exist — there is no `POST /api/ai/chat/conversations`.

```
POST https://{space}.signalwire.com/api/ai/chat
Content-Type: application/json
Authorization: Basic base64(project_id:token)
```

```json
{
  "jsonrpc": "2.0",
  "id": "req-2",
  "method": "chat",
  "params": {
    "id": "conv-123",
    "message": "Where is order A-771?"
  }
}
```

**Two different things are called `id`.** The top-level `id` is the JSON-RPC request identifier, echoed back on the response so you can correlate. The `id` inside `params` is the **conversation** identifier. They are unrelated, and mixing them up is the first mistake to make here.

Every response carries `jsonrpc: "2.0"` and echoes the request `id`.

## Methods

| Method | Required params | Optional params | Returns |
|--------|-----------------|-----------------|---------|
| `create_conversation` | `id`, `config_url` | `user_message`, `conversation_timeout` (default 3600s), `user_meta_data`, `reinit` | `{id, initial_message, status}` — status is `created`, `reinitialized`, or `exists` |
| `chat` | `id`, `message` | `role` (default `user`), `config_url`, `conversation_timeout`, `user_meta_data`, `reinit` | `{response, user_event?}` |
| `chat_log` | `id` | — | `{chat_log[], call_timeline[]?}` |
| `summarize` | `id` | `summary_prompt`, `temperature` (0.3), `top_p` (0.3), `frequency_penalty` (1), `presence_penalty` (1), `max_tokens` (512) | `{summary?, error?}` |
| `end_conversation` | `id` | — | `{id, status}` — `ended` or `not_found` |
| `delete` | `id` | — | `{id, status}` — `deleted` or `not_found` |

`jsonrpc` is required on every call alongside the params above.

**`create_conversation` is idempotent by identifier.** Calling it with an `id` that already exists returns `status: "exists"` rather than erroring or clobbering. Pass `reinit` to force a fresh start under the same id.

**`end_conversation` and `delete` are different.** Ending closes the conversation but leaves it readable via `chat_log`. Deleting removes it.

## Typical flow

```bash
# 1. Start a conversation against an agent's SWML
curl -u "$PROJECT_ID:$API_TOKEN" \
  -X POST "https://$SPACE.signalwire.com/api/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"create_conversation",
       "params":{"id":"conv-123","config_url":"https://myapp.com/agent.swml"}}'

# 2. Exchange messages
curl -u "$PROJECT_ID:$API_TOKEN" \
  -X POST "https://$SPACE.signalwire.com/api/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"2","method":"chat",
       "params":{"id":"conv-123","message":"Where is order A-771?"}}'

# 3. Close it out
curl -u "$PROJECT_ID:$API_TOKEN" \
  -X POST "https://$SPACE.signalwire.com/api/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"3","method":"end_conversation",
       "params":{"id":"conv-123"}}'
```

The agent is defined by the SWML at `config_url` — the same document that would answer a phone call. SWAIG functions, prompts and `global_data` all work the same way.

## Errors

JSON-RPC errors come back in the standard `error` object rather than as HTTP status codes. Codes are listed with the rest of the API errors at `/docs/apis/error-codes`.

## Python SDK

Two wrappers, so you do not have to hand-roll JSON-RPC:

| Class | For | Reference |
|-------|-----|-----------|
| `AIChatClient` | Async client. `chat()`, `create_conversation()`, `end()`, `delete()`, `log()`, `summarize()`. | `/docs/server-sdks/reference/python/agents/ai-chat-client` |
| `ChatGateway` | Browser-facing proxy — lets a page chat with an agent **without holding a SignalWire API token**. Credentials stay server-side; the browser gets a gateway URL and a publishable key. | `/docs/server-sdks/reference/python/agents/chat-gateway` |

Use `ChatGateway` for anything a browser touches. Shipping project credentials to the client is the failure mode it exists to prevent.

## Reading chat logs

`chat_log` returns the transcript for one conversation. For querying across conversations there is a separate REST surface:

```
GET /api/fabric/resources/ai_agents/:id/conversation_logs
GET /api/fabric/resources/chats
GET /api/fabric/resources/chats/:id/events
```

## Billing

**Per turn, not per minute.** This is the significant difference from voice — an idle chat session costs nothing, where an idle call does not. A long-lived conversation left open between messages is not accruing charges.

## Related

- [Voice AI](voice-ai.md) — the same agents over a phone call
- [AI Agent Functions](ai-agent-functions.md) — SWAIG functions work identically in chat
