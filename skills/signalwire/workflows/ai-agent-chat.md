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

**`chat` with `config_url` creates the conversation if it does not exist, and never returns `initial_message`.** `create_conversation` returns `initial_message` only when the agent speaks first, and none when `status` is `"exists"`.

**`end_conversation` and `delete` are different.** Ending closes the conversation and posts the summary to `post_prompt_url` if configured; later calls on that ID return -32001. Deleting removes it: nothing is post-processed and no webhook fires.

A conversation ID keeps only letters, digits, `_`, `-`, `.`, and `:`. Any other character is dropped with no error, so `rider~2` is stored as `rider2`. An ended conversation cannot be reopened. A later `chat` that passes `config_url` under that same ID starts a new conversation with no memory of the old one.

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

Check the HTTP status before the body.

- **401** — credentials are wrong, or the token does not have the **Chat** permission. An unverified account also returns 401, with JSON `{"message": "Please validate a phone number to access your account."}`.
- **400** — the body was not valid JSON.
- **502** — the AI chat service timed out or could not be reached. The body is JSON with an `error` string, for example `AI chat service is unavailable`. This is not a JSON-RPC error and carries no code.

Errors from AI chat itself come back as **HTTP 200** with an `error` object instead of `result`:

- `-32001`, Conversation not found — the ID is not a live conversation (misspelled, ended, or idle past `conversation_timeout`).
- `-32002`, Configuration error — the `config_url` fetch failed: a status other than 200, or the request failed. Redirects are not followed.
- `-32005` — too many `summarize` calls on this conversation, which allows one per minute.
- `-32006` — the chat rate limit was exceeded.
- `-32007` — another chat operation is already in progress for this conversation.
- `-32008` — `config_url` was blocked or returned an invalid config: a private or unresolvable host, an empty body, or a response that is not a SWML document with an `ai` section.

Code descriptions are at `/docs/apis/error-codes`.

## Python SDK

Two wrappers, so you do not have to hand-roll JSON-RPC:

| Class | For | Reference |
|-------|-----|-----------|
| `AIChatClient` | Async client. `chat()`, `create_conversation()`, `end()`, `delete()`, `log()`, `summarize()`. | `/docs/server-sdks/reference/python/agents/ai-chat-client` |
| `ChatGateway` | Browser-facing proxy — lets a page chat with an agent **without holding a SignalWire API token**. Credentials stay server-side; the browser gets a gateway URL and a publishable key. | `/docs/server-sdks/reference/python/agents/chat-gateway` |

Use `ChatGateway` for anything a browser touches. Shipping project credentials to the client is the failure mode it exists to prevent.

Localhost is always allowed, so the gateway runs locally with no origin list. Set the origin allowlist to your production site origin (Python `allowed_origins`, TypeScript `allowedOrigins`). A copied publishable key still works from a script that omits the `Origin` header. Cap spend with `max_new_conversations` (TypeScript `maxNewConversations`, default 60 per minute) and `max_turns` (TypeScript `maxTurns`, default 200).

## Reading chat logs

`chat_log` returns the transcript for one conversation. For querying across conversations there is a separate REST surface:

```
GET /api/fabric/resources/ai_agents/:id/conversation_logs
GET /api/fabric/resources/chats
GET /api/fabric/resources/chats/:id/events
```

## Webhooks

Tool calls (`web_hook_url`) and the post-prompt summary (`post_prompt_url`) are the same webhooks as a voice session. Both set `conversation_type` to `chat`. `conversation_id` is your chat ID on both. On the tool webhook, `call_id` is the conversation ID; on the post-prompt callback, `call_id` is a separate UUID.

`chat_log` and the post-prompt `call_log` include the system prompt, `system` messages, and tool entries. Filter to `user` and `assistant` before showing a transcript. The gateway's `log` already does.

## SMS and voice handoff

An inbound message webhook can bridge SMS into AI chat: build a stable conversation ID from the sender (the guide uses `sms.` plus the number without `+`) and return messaging SWML whose `reply` is the agent's text. Guide: https://signalwire.com/docs/platform/ai/chat

A page can move that chat onto a call with `HandoffRouter` mounted beside `ChatGateway`. The browser dials with the chat handle and a nonce in `userVariables`. That path ends the text leg when the call starts. Returning to text continues under a new ID. The default is `<id>.1`, then `<id>.2`, and so on. Pass `next_conversation_id` (TypeScript `nextConversationId`) to choose the next ID.

## Gotchas

- **Chat bills per turn, not per minute.** An idle conversation costs nothing, unlike an idle call, so a conversation left open between messages accrues no charges.

## Related

- [Voice AI](voice-ai.md) — the same agents over a phone call
- [AI Agent Functions](ai-agent-functions.md) — SWAIG functions work identically in chat
