# Pilot questions

Answer each question using ONLY the files you were given. Quote exact parameter names and values. If the files do not say, answer "not stated".

## SWML ai params (file: swml/reference/calling/ai/params.md)
1. What is the default value of `ai_model`?
2. What happens when `enable_turn_detection` is set to `off`, and what is the default silence the agent then waits for?
3. What values are allowed for `inactivity_timeout`, and what is its default?
4. If `thinking_model` is not set, which model is used for thinking?

## SWML connect (file: swml/reference/calling/connect.md)
5. How many destinations does a `parallel` connect dial, and what happens to destinations beyond that limit?
6. With `serial_parallel` and three groups of eight destinations each, which destinations ring?
7. Can `call_state_url` be used when `to` is `queue:support`? If not, where do queue events go?
8. What happens if `to` is a phone number written without the leading `+`?

## REST queues (file: apis/rest/queues.md, or the five apis/rest/queues/*.md pages)
9. Can you delete a queue that has callers waiting? What does a successful delete return?
10. Using the update endpoint, how do you remove a queue's maximum size?
11. What are the uniqueness rules for queue names, and can a deleted queue's name be reused?
12. What HTTP method and path create a queue, and which API token scope is required?

## Call state status callback (file: apis/rest/webhooks/call-state-status-callback.md)
13. Which call states trigger the callback by default?
14. Where in the payload is the call's new state, and what is the top-level `event_type`?
15. What are the from/to field names for a phone device, and how do they differ for SIP or WebRTC devices?
16. What does `dial_winner` indicate, and what is its value when present?

## Deploying SWML (file: swml/guides/deployment.md)
17. When a number uses an external URL for SWML, what HTTP method does SignalWire use, and what does the request body contain?
18. What are `vars` and `params` on a new inbound call, and when are they populated?
19. How do you run SWML from a Relay application (Python)? Name the client, the context/topic, and the call method.
20. Where in the Dashboard is a number's call handler set to a Relay Application?
