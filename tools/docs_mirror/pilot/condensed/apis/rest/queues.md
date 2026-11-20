# Queues (REST API)
Sources:
- https://signalwire.com/docs/apis/rest/queues/create-queue.md
- https://signalwire.com/docs/apis/rest/queues/get-queue.md
- https://signalwire.com/docs/apis/rest/queues/list-queues.md
- https://signalwire.com/docs/apis/rest/queues/update-queue.md
- https://signalwire.com/docs/apis/rest/queues/delete-queue.md

Base: `https://{Your_Space_Name}.signalwire.com/api/relay/rest/queues`. Auth: Basic (`project_id:api_token`). All endpoints require API token scope _Voice_.

Voice call queues in the project. The call workflow is responsible for placing callers into the queue. Queue-member positions and wait times are read through the Queue Members endpoints (https://signalwire.com/docs/apis/rest/queue-members/list-queue-members.md). The Compatibility API exposes the same queues through SID-based routes.

## Queue object
- `id` string, required — unique identifier of the queue
- `project_id` string, required — project the queue belongs to
- `friendly_name` string, required — the queue's name (set via request field `name`)
- `max_size` integer, required, nullable — max callers allowed; `null` when no maximum is set
- `current_size` integer, optional — current number of callers in the queue
- `average_wait_time` integer, optional — average wait time in seconds
- `uri` string, optional — URL of this queue, e.g. `/api/relay/rest/queues/<id>`
- `date_created` datetime, optional
- `date_updated` datetime, optional — last updated

## Create queue
`POST /api/relay/rest/queues` — Content-Type: application/json
Source: https://signalwire.com/docs/apis/rest/queues/create-queue.md
- `name` string, required — must be unique among the project's active queues; a deleted queue's name can be reused
- `max_size` integer, optional, nullable — integer > 0; omit or send `null` for no maximum

Returns 201 with the queue object. Use Compatibility Create queue (https://signalwire.com/docs/compatibility-api/rest/queues/create-queue.md) for form-encoded requests.

## Get queue
`GET /api/relay/rest/queues/{id}`
Source: https://signalwire.com/docs/apis/rest/queues/get-queue.md
- `id` path string, required — unique ID of the queue

Returns 200 with the queue object.

## List queues
`GET /api/relay/rest/queues`
Source: https://signalwire.com/docs/apis/rest/queues/list-queues.md
No request parameters documented. Compatibility equivalent: https://signalwire.com/docs/compatibility-api/rest/queues/list-queues.md

Returns 200:
- `links` PaginationLinks, optional
  - `links.self` string, required — current page
  - `links.first` string, required — first page
  - `links.next` string, optional — only present when there are more results
  - `links.prev` string, optional — only present when not on the first page
- `data` list of Queue, optional — queue objects

## Update queue
`PUT /api/relay/rest/queues/{id}` — Content-Type: application/json
Source: https://signalwire.com/docs/apis/rest/queues/update-queue.md
- `id` path string, required — unique ID of the queue
- `name` string, optional — new name must be unique among the project's active queues
- `max_size` integer, optional, nullable — integer > 0; send `null` to remove the maximum

Returns 200 with the queue object. Compatibility API updates the same queues through its SID-based route.

## Delete queue
`DELETE /api/relay/rest/queues/{id}`
Source: https://signalwire.com/docs/apis/rest/queues/delete-queue.md
- `id` path string, required — unique ID of the queue

The queue must be empty; a queue with waiting callers returns a validation error. Returns 204, no body. Removes the same queue the Compatibility Delete queue (https://signalwire.com/docs/compatibility-api/rest/queues/delete-queue.md) manages.

## Errors
- `400` `{"error": "Bad Request"}` — update and delete only
- `422` `{"errors": [...]}` — create, get, list, update (not listed for delete). Each item: `detail` string, `status` string (HTTP status code), `title` string (short summary), `code` string (error code); all required
- `500` `{"error": "Internal Server Error"}` — all endpoints
