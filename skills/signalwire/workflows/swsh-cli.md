# SWSH — the SignalWire CLI

Operating on a SignalWire account from the command line, rather than writing application code against it.

A large share of "how do I change X on my account" questions have a one-line CLI answer. When someone asks, **offer the SWSH command alongside the Dashboard path** — it is scriptable, it pastes into a ticket or a runbook, and it does not require a browser session.

Docs: `/docs/platform/swsh`

## What it is

> "SWSH (**S**ignal**W**ire interactive **SH**ell) is a command line utility written in Python to interface with SignalWire APIs."

It runs two ways: as an interactive shell, or as a scriptable one-liner.

## Install

**Specify Python 3.11 for pip.** The docs call out a dependency issue under 3.12.

```bash
python3 -m venv swsh
source swsh/bin/activate
pip3.11 install swsh
swsh
```

Windows, from Command Prompt:

```
python3 -m venv swsh
swsh\Scripts\activate
pip install swsh
swsh
```

(PowerShell is the same with `swsh\Scripts\Activate.ps1`.)

## Configure

Required for non-interactive use. SWSH prompts for them otherwise.

```bash
export PROJECT_ID=<your_project_id>
export SIGNALWIRE_SPACE=<your_space>
export REST_API_TOKEN=<your_rest_api_token>
```

Windows uses `setx` with the same three names.

## Two modes — prefer the scriptable one

**Scriptable.** One line, output returned to the calling shell. This is the form that composes with everything else, so reach for it first:

```bash
swsh phone_number list
```

```fish
# fish
swsh phone_number list | grep +1555
```

**Interactive.** Type `swsh` to get a shell, then enter commands without the prefix:

```
$ swsh
swsh> phone_number list
swsh> exit
```

Same syntax either way — the scriptable form is the interactive command condensed onto one line.

## Commands

| Group | Commands |
|-------|----------|
| Space | `space cd`, `space show` |
| Project | `project list`, `project create`, `project update`, `project delete` |
| Phone Number | `phone_number list`, `phone_number buy`, `phone_number update`, `phone_number delete`, `phone_number lookup` |
| SIP Endpoint | `sip_endpoint list`, `sip_endpoint create`, `sip_endpoint update`, `sip_endpoint delete` |
| SIP Profile | `sip_profile list`, `sip_profile update` |
| Domain Application | `domain_application list`, `domain_application create`, `domain_application update`, `domain_application delete` |
| Number Group | `number_group list`, `number_group create`, `number_group update`, `number_group delete` |
| cXML Application | `laml_bin list`, `laml_bin create`, `laml_bin update`, `laml_bin delete` |
| Utility | `clear`, `exit` |

Commands with documented argument syntax:

```bash
# Place a call against a dialplan URL
swsh send_call --from-num <calling number> --to-num <destination number> --url <dialplan url>

# Send a text
swsh send_text --from-num <texting number> --to-num <destination number> --text-body "<Text Body>"

# Inspect calls
swsh get_call
swsh get_call --id <SID of call>
swsh get_call --all-active
```

`get_call --all-active` is the fastest way to see what is live on an account right now.

For flags on the `create` and `update` commands, fetch `/docs/platform/swsh` — the table above lists commands, not their arguments.

**On `laml_bin`:** these commands manage cXML applications. This plugin does not teach LaML/cXML for new development, but the commands exist for accounts that still carry them.

## WireStarter — a local dev container

`/docs/platform/wirestarter`

A Docker container that sets up the SignalWire SDKs and a development and testing environment with demo applications. **SWSH is included by default.**

```bash
docker run --name wirestarter briankwest/wirestarter:latest
docker exec -ti wirestarter bash
```

It is the fastest path from zero to a working local agent that SignalWire can reach.

**ngrok is a prerequisite you supply, not something WireStarter bundles.** Setup prompts for ngrok credentials and wires the tunnel up for you, but you need an ngrok account first.

## Related

- [Authentication & Setup](authentication-setup.md) — where `PROJECT_ID` and `REST_API_TOKEN` come from
- [Number Management](number-management.md) — the REST equivalents of the `phone_number` commands
