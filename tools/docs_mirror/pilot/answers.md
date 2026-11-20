# Ground truth (from the live source pages)
1. gpt-4o-mini
2. Neither punctuation nor acoustic signal is used; the agent waits out `end_of_speech_timeout` silence, default 700 (ms). (`false` is an alias for `off`.)
3. `0` (disable) or 10,000–3,600,000 ms; default 600000.
4. The value of `ai_model`.
5. Up to 20; later destinations never ring and `connect` reports no error for them.
6. Limit is 20 counted across all groups: first two groups ring in full (16), the third group rings only its first four; its last four never ring; no error.
7. No — `call_state_url`/`call_state_events` aren't allowed with `queue:`, `call:` or `stream:`. Queue events go to the `status_url` of `enter_queue`.
8. It is rejected (E.164 with leading `+` required).
9. No — the queue must be empty; a queue with waiting callers returns a validation error (400). Success returns 204 No Content.
10. Send `max_size: null`.
11. Unique among the project's active queues; a deleted queue's name can be reused.
12. POST /api/relay/rest/queues; scope: Voice.
13. Only `ended` (default `status_events`).
14. `params.call_state`; `event_type` is `calling.call.state`.
15. Phone: `from_number`, `to_number`; SIP/WebRTC: `from`, `to` (under `device.params`).
16. That this leg answered an outbound dial (incl. the winning leg of a parallel dial); value is the string "true"; omitted otherwise.
17. POST; body contains `call`, `vars`, `params`, `envs`.
18. Empty on a new call; populated when the script is invoked via `execute` or `transfer` (vars = variables declared so far, params = parameters set by execute/transfer).
19. `RelayClient` with `contexts=["swml"]`, an `on_call` handler calling `await call.transfer(SCRIPT)` (inline SWML or a URL returning SWML).
20. On the number's page under **Inbound Call Settings**.
