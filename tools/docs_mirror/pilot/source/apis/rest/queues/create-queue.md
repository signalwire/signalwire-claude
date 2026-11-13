> This page is for APIs.

> Fetch clean Markdown by appending `.md` to any page URL under https://signalwire.com/docs or requesting it with the HTTP header `Accept: text/markdown`. The root index at https://signalwire.com/docs/llms.txt lists the available documentation indexes.

# Create queue

POST https://%7BYour_Space_Name%7D.signalwire.com/api/relay/rest/queues
Content-Type: application/json

Creates a voice call queue in the project for calls that need to wait for later handling. Queue names must be unique among active queues; a deleted queue's name can be reused. The call workflow is responsible for placing callers into the queue. Use Compatibility [Create queue](/docs/compatibility-api/rest/queues/create-queue) for form-encoded requests.

#### Permissions

The API token used to authenticate must have the following scope(s) enabled to make a successful request: _Voice_.

[Learn more about API scopes](/docs/platform/your-signalwire-api-space).

Reference: https://signalwire.com/docs/apis/rest/queues/create-queue

## Authentication

- `Authorization` header (basic auth, required) — SignalWire Basic Authentication using Project ID and API Token. The client sends HTTP requests with the Authorization header containing the word Basic followed by a space and a base64-encoded string of project_id:token. The project ID will be used as the username and the API token as the password. Example: ``` Authorization: Basic base64(project_id:token) ```

## Request

### Body (application/json)

This endpoint expects a CreateQueueRequest.

- `name` (string, required) — The name of the queue. Must be unique among the project's active queues.
- `max_size` (integer, optional, nullable) — The maximum number of callers allowed in the queue. Must be an integer greater than 0. Omit it or send `null` for no maximum.

## Response

### 201

The request has succeeded and a new resource has been created as a result.

- `id` (string, required) — The unique identifier of the queue.
- `project_id` (string, required) — The project ID associated with this queue.
- `friendly_name` (string, required) — The friendly name of the queue.
- `max_size` (integer, required, nullable) — The maximum number of callers allowed in the queue, or `null` when no maximum is set.
- `current_size` (integer, optional) — The current number of callers in the queue.
- `average_wait_time` (integer, optional) — The average wait time in seconds.
- `uri` (string, optional) — The URL of this queue.
- `date_created` (datetime, optional) — Timestamp when the queue was created.
- `date_updated` (datetime, optional) — Timestamp when the queue was last updated.

## Errors

### 422 Unprocessable Entity Error

The request failed validation. See errors for details.

- `errors` (list of Types.StatusCodes.SpaceApiErrorItem, required) — List of validation errors.

### 500 Internal Server Error

An internal server error occurred.

- `error` (enum, required)
  - Allowed values: `Internal Server Error`

## Types

### Types.StatusCodes.SpaceApiErrorItem

Details about a specific validation error.

- `detail` (string, required) — A description of what caused the error.
- `status` (string, required) — The HTTP status code.
- `title` (string, required) — A short summary of the error type.
- `code` (string, required) — The error code.

## Examples

**Request**

```json
{
  "name": "Name 2"
}
```

**Response**

```json
{
  "id": "aae131db-214c-46f5-88b6-92004f8467cf",
  "project_id": "c6c4679b-716a-456a-9e41-a03821005005",
  "friendly_name": "test",
  "max_size": 5,
  "current_size": 0,
  "average_wait_time": 0,
  "uri": "/api/relay/rest/queues/aae131db-214c-46f5-88b6-92004f8467cf",
  "date_created": "2024-01-15T09:30:00Z",
  "date_updated": "2024-01-15T09:30:00Z"
}
```

**SDK Code**

```python
import requests

url = "https://{your_space_name}.signalwire.com/api/relay/rest/queues"

payload = { "name": "Name 2" }
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers, auth=("<project_id>", "<api_token>"))

print(response.json())
```

```javascript
const url = 'https://{your_space_name}.signalwire.com/api/relay/rest/queues';
const credentials = btoa("<project_id>:<api_token>");

const options = {
  method: 'POST',
  headers: {
    Authorization: `Basic ${credentials}`,
    'Content-Type': 'application/json'
  },
  body: '{"name":"Name 2"}'
};

try {
  const response = await fetch(url, options);
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error(error);
}
```

```go
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://{your_space_name}.signalwire.com/api/relay/rest/queues"

	payload := strings.NewReader("{\n  \"name\": \"Name 2\"\n}")

	req, _ := http.NewRequest("POST", url, payload)

	req.SetBasicAuth("<project_id>", "<api_token>")
	req.Header.Add("Content-Type", "application/json")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://{your_space_name}.signalwire.com/api/relay/rest/queues")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Post.new(url)
request.basic_auth("<project_id>", "<api_token>")
request["Content-Type"] = 'application/json'
request.body = "{\n  \"name\": \"Name 2\"\n}"

response = http.request(request)
puts response.read_body
```

```java
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://{your_space_name}.signalwire.com/api/relay/rest/queues")
  .basicAuth("<project_id>", "<api_token>")
  .header("Content-Type", "application/json")
  .body("{\n  \"name\": \"Name 2\"\n}")
  .asString();
```

```php
<?php
require_once('vendor/autoload.php');

$client = new \GuzzleHttp\Client();

$response = $client->request('POST', 'https://{your_space_name}.signalwire.com/api/relay/rest/queues', [
  'body' => '{
  "name": "Name 2"
}',
  'headers' => [
    'Content-Type' => 'application/json',
  ],
    'auth' => ['<project_id>', '<api_token>'],
]);

echo $response->getBody();
```

```csharp
using RestSharp;
using RestSharp.Authenticators;

var client = new RestClient("https://{your_space_name}.signalwire.com/api/relay/rest/queues");
client.Authenticator = new HttpBasicAuthenticator("<project_id>", "<api_token>");
var request = new RestRequest(Method.POST);

request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"name\": \"Name 2\"\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let credentials = Data("<project_id>:<api_token>".utf8).base64EncodedString()

let headers = [
  "Authorization": "Basic \(credentials)",
  "Content-Type": "application/json"
]
let parameters = ["name": "Name 2"] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://{your_space_name}.signalwire.com/api/relay/rest/queues")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "POST"
request.allHTTPHeaderFields = headers
request.httpBody = postData as Data

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```