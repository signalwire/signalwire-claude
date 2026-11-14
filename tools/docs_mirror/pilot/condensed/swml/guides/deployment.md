# Deploy SWML from web servers and Relay applications (guide)
Source: https://signalwire.com/docs/swml/guides/deployment.md

Examples use Calling SWML (https://signalwire.com/docs/swml/reference/calling.md). The same deployment patterns apply to Messaging SWML (https://signalwire.com/docs/swml/reference/messaging.md) for inbound SMS/MMS; only differences: webhook payload has `message` instead of `call`, and a different set of available methods.
Variables, Call Object, and all variable scopes: https://signalwire.com/docs/swml/reference/variables.md

## From a web server
Detailed guide: https://signalwire.com/docs/swml/guides/remote-server.md

1. In the phone number settings, check "Use External URL for SWML Script handler?" and set the Web URL that serves the SWML script.
2. Every time a call comes in (or some other designated event occurs), SignalWire sends a POST to that URL in the standard document-fetching webhook format (https://signalwire.com/docs/swml/reference/calling.md, section "Document-fetching webhook", has the full body structure).

POST body: `call` object, `vars`, `params`, `envs`.
- `vars` and `params` are empty for a new call.
- When the remote script is run via `execute` (https://signalwire.com/docs/swml/reference/calling/execute.md) or `transfer` (https://signalwire.com/docs/swml/reference/calling/transfer.md): `vars` lists the variables declared in the script so far; `params` holds the parameters explicitly set by that `execute`/`transfer`.

`call` and `params` properties can be referenced during execution with `%{...}` substitution, e.g. `url: 'say:%{call.from}'`.

Constraint: a script referencing `params.*` (e.g. `url: '%{params.file}'` in `play`) causes an error if invoked as the response to a phone call, because `params` is empty. It works when hosted on a server and called with `execute` or `transfer`, which pass `params` in.

Invoking a hosted script with params (as shown in source):
```yaml
version: 1.0.0
sections:
  main:
    execute:
      dest: https://example.com/swml.yaml
      params:
        file: https://cdn.signalwire.com/swml/audio.mp3
```
Target script `https://example.com/swml.yaml`:
```yaml
version: 1.0.0
sections:
  main:
    - play:
        url: '%{params.file}'
    - return: 1
```

## From a Relay application
Uses the Relay client in the Server SDKs (https://signalwire.com/docs/server-sdks.md).

```python
# Install: python -m pip install signalwire-sdk==3.4.1
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

client = RelayClient(project="<YOUR_PROJECT_ID>", token="<YOUR_API_TOKEN>", contexts=["swml"])

@client.on_call
async def handle_call(call):
    await call.transfer(SCRIPT)

client.run()
```
TypeScript (`npm install @signalwire/sdk@2.0.5`; also runs as JavaScript `.mjs`): `import { RelayClient } from "@signalwire/sdk"`; `new RelayClient({ project, token, contexts: ["swml"] })`; `client.onCall(async (call) => { await call.transfer(script); })`; `await client.run()`.

- The handler subscribes to topic `swml`, so it receives every call to a phone number whose call handler is a Relay Application (https://signalwire.com/docs/platform/glossary.md, "Relay Application") with that topic.
- Set a number's handler under **Inbound Call Settings** on the number's page in the SignalWire Dashboard.
- On call arrival the handler transfers the call to the SWML document, which takes over the call.
- The transfer destination can be an inline SWML document or the URL of a server that returns one.

Related: Getting started with SWML https://signalwire.com/docs/swml.md
