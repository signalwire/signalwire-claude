> This page is for APIs.

> Fetch clean Markdown by appending `.md` to any page URL under https://signalwire.com/docs or requesting it with the HTTP header `Accept: text/markdown`. The root index at https://signalwire.com/docs/llms.txt lists the available documentation indexes.

# Delete queue

DELETE https://%7BYour_Space_Name%7D.signalwire.com/api/relay/rest/queues/{id}

Deletes a voice call queue by ID. The queue must be empty; a queue with waiting callers returns a validation error. This removes the same queue that the Compatibility [Delete queue](/docs/compatibility-api/rest/queues/delete-queue) operation manages.

#### Permissions

The API token used to authenticate must have the following scope(s) enabled to make a successful request: _Voice_.

[Learn more about API scopes](/docs/platform/your-signalwire-api-space).

Reference: https://signalwire.com/docs/apis/rest/queues/delete-queue

## Authentication

- `Authorization` header (basic auth, required) — SignalWire Basic Authentication using Project ID and API Token. The client sends HTTP requests with the Authorization header containing the word Basic followed by a space and a base64-encoded string of project_id:token. The project ID will be used as the username and the API token as the password. Example: ``` Authorization: Basic base64(project_id:token) ```

## Request

### Path parameters

- `id` (string, required) — Unique ID of the queue.

## Response

### 204

There is no content to send for this request, but the headers may be useful.

## Errors

### 400 Bad Request Error

The request is invalid.

- `error` (enum, required)
  - Allowed values: `Bad Request`

### 500 Internal Server Error

An internal server error occurred.

- `error` (enum, required)
  - Allowed values: `Internal Server Error`

## Examples

**SDK Code**

```python
import requests

url = "https://{your_space_name}.signalwire.com/api/relay/rest/queues/id"

response = requests.delete(url, auth=("<project_id>", "<api_token>"))

print(response.json())
```

```javascript
const url = 'https://{your_space_name}.signalwire.com/api/relay/rest/queues/id';
const credentials = btoa("<project_id>:<api_token>");

const options = {method: 'DELETE', headers: {Authorization: `Basic ${credentials}`}};

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
	"net/http"
	"io"
)

func main() {

	url := "https://{your_space_name}.signalwire.com/api/relay/rest/queues/id"

	req, _ := http.NewRequest("DELETE", url, nil)

	req.SetBasicAuth("<project_id>", "<api_token>")

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

url = URI("https://{your_space_name}.signalwire.com/api/relay/rest/queues/id")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Delete.new(url)
request.basic_auth("<project_id>", "<api_token>")

response = http.request(request)
puts response.read_body
```

```java
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.delete("https://{your_space_name}.signalwire.com/api/relay/rest/queues/id")
  .basicAuth("<project_id>", "<api_token>")
  .asString();
```

```php
<?php
require_once('vendor/autoload.php');

$client = new \GuzzleHttp\Client();

$response = $client->request('DELETE', 'https://{your_space_name}.signalwire.com/api/relay/rest/queues/id', [
  'headers' => [
  ],
    'auth' => ['<project_id>', '<api_token>'],
]);

echo $response->getBody();
```

```csharp
using RestSharp;
using RestSharp.Authenticators;

var client = new RestClient("https://{your_space_name}.signalwire.com/api/relay/rest/queues/id");
client.Authenticator = new HttpBasicAuthenticator("<project_id>", "<api_token>");
var request = new RestRequest(Method.DELETE);

IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let credentials = Data("<project_id>:<api_token>".utf8).base64EncodedString()

let headers = ["Authorization": "Basic \(credentials)"]

let request = NSMutableURLRequest(url: NSURL(string: "https://{your_space_name}.signalwire.com/api/relay/rest/queues/id")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "DELETE"
request.allHTTPHeaderFields = headers

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