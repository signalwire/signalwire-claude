> This page is for SWML.

> Fetch clean Markdown by appending `.md` to any page URL under https://signalwire.com/docs or requesting it with the HTTP header `Accept: text/markdown`. The root index at https://signalwire.com/docs/llms.txt lists the available documentation indexes.

# Deploy SWML from web servers

> Learn how to serve SWML scripts from web servers and Relay applications.

SWML scripts can be served in multiple ways beyond the SignalWire Dashboard. This guide covers serving SWML from web servers and Relay applications.

> **Info**
>
> For complete information about variables, the Call Object, and all variable scopes, see the [**Variables and Expressions**](/docs/swml/reference/variables) reference.

> **Note**
>
> The examples below use [**Calling SWML**](/docs/swml/reference/calling) (the voice-call flavor). The same deployment patterns apply to [**Messaging SWML**](/docs/swml/reference/messaging) for inbound SMS and MMS — the only difference is the webhook payload shape (`message` instead of `call`) and the set of available methods.

## From a web server

> **Tip**
>
> This use case is described in detail in the [Handling Incoming Calls from Code](/docs/swml/guides/remote-server) guide.

In the phone number settings, when you check the "Use External URL for SWML Script handler?" option,
you can set a Web URL that will serve the SWML script.
Every time a call comes in (or some other designated event occurs),
SignalWire sends a POST request to the URL using the standard [document-fetching webhook](/docs/swml/reference/calling#document-fetching-webhook) format.
The request body contains the `call` object, `vars`, `params`, and `envs`. See the [document-fetching webhook reference](/docs/swml/reference/calling#document-fetching-webhook) for the full request body structure.

### Understanding the POST Request

The `vars` object and the `params` object will be empty for a new call.
If you're executing a remote SWML script using the [`execute`](/docs/swml/reference/calling/execute) or [`transfer`](/docs/swml/reference/calling/transfer) methods,
the `vars` parameter has a list of the variables declared in the script so far.
And the `params` object has the list of parameters explicitly set by the [`execute`](/docs/swml/reference/calling/execute) or [`transfer`](/docs/swml/reference/calling/transfer) methods.

You can also reference the properties of `call` and `params` objects during the script execution using the variable subtitution bracket like so:

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - play:
        url: 'say:%{call.from}'
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "play": {
          "url": "say:%{call.from}"
        }
      }
    ]
  }
}
```

Further, consider the following SWML script:

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    - play:
        url: '%{params.file}'
    - return: 1
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": [
      {
        "play": {
          "url": "%{params.file}"
        }
      },
      {
        "return": 1
      }
    ]
  }
}
```

It references `params.file` in its [`play`](/docs/swml/reference/calling/play) method.
If this SWML was invoked as a response to a phone call, it would cause an error as the `params` object is empty.
But if it was hosted on a server and called with the [`execute`](/docs/swml/reference/calling/execute) or the [`transfer`](/docs/swml/reference/calling/transfer) method,
the `params` object is passed into the SWML.

The SWML above can be invoked as follows:

#### YAML

```yaml
version: 1.0.0
sections:
  main:
    execute:
      dest: https://example.com/swml.yaml
      params:
        file: https://cdn.signalwire.com/swml/audio.mp3
```

#### JSON

```json
{
  "version": "1.0.0",
  "sections": {
    "main": {
      "execute": {
        "dest": "https://example.com/swml.yaml",
        "params": {
          "file": "https://cdn.signalwire.com/swml/audio.mp3"
        }
      }
    }
  }
}
```

## From a Relay application

You can also execute SWML from a Relay application.
The following handler uses the Relay client in the [Server SDKs](/docs/server-sdks).

#### Python — Relay client

```python
# Install: python -m pip install signalwire-sdk==3.4.1
# Save as swml_relay.py and run: python swml_relay.py
from signalwire.relay import RelayClient

SCRIPT = """
version: 1.0.0
sections:
  main:
    - answer: {}
    - execute:
        dest: play_music
        params:
          to_play: 'https://cdn.signalwire.com/swml/April_Kisses.mp3'
  play_music:
    - play:
        url: '%{params.to_play}'
"""

client = RelayClient(
    project="<YOUR_PROJECT_ID>",
    token="<YOUR_API_TOKEN>",
    contexts=["swml"],
)

@client.on_call
async def handle_call(call):
    await call.transfer(SCRIPT)

client.run()
```

#### TypeScript — Relay client

```typescript
// Install: npm install @signalwire/sdk@2.0.5
// This sample also runs as JavaScript: save as swml-relay.mjs,
// then run: node swml-relay.mjs
import { RelayClient } from "@signalwire/sdk";

const script = `
version: 1.0.0
sections:
  main:
    - answer: {}
    - execute:
        dest: play_music
        params:
          to_play: 'https://cdn.signalwire.com/swml/April_Kisses.mp3'
  play_music:
    - play:
        url: '%{params.to_play}'
`;

const client = new RelayClient({
  project: "<YOUR_PROJECT_ID>",
  token: "<YOUR_API_TOKEN>",
  contexts: ["swml"],
});

client.onCall(async (call) => {
  await call.transfer(script);
});

await client.run();
```

The handler subscribes to the topic `swml`, so it receives every call to a phone number whose call handler is a [Relay Application](/docs/platform/glossary#relay-application) with that topic.
You set a number's handler under **Inbound Call Settings** on the number's page in the SignalWire Dashboard.
When a call arrives, the handler transfers it to the SWML document, which takes over the call.
The transfer destination can be an inline SWML document, as here, or the URL of a server that returns one.

## Next steps

* **[Variables and Expressions](/docs/swml/reference/variables)**: Complete reference for SWML variables and the Call Object

* **[Handle incoming calls from code](/docs/swml/guides/remote-server)**: Complete guide to serving SWML from web servers

* **[Calling SWML reference](/docs/swml/reference/calling)**: Methods available for voice calls

* **[Messaging SWML reference](/docs/swml/reference/messaging)**: Methods available for inbound SMS and MMS

* **[Getting started with SWML](/docs/swml)**: Learn the fundamentals