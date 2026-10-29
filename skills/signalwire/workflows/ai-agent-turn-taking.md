# AI Agent Turn Taking

How an AI agent decides the caller has finished speaking. This governs whether the agent interrupts people or leaves dead air, and it is the first thing to reach for when an agent "feels wrong" on a call.

`params.enable_turn_detection` (alias `turn_detection`) is a string or boolean. Values: `both` (default), `punct_only`, `acoustic_only`, `off`. `true` is `both`; `false` is `off`. Docs: https://signalwire.com/docs/swml/reference/calling/ai/params

## How End-of-Turn Is Actually Decided

Two independent layers:

**FIRE** — "the turn looks done, commit it." Two signals are fused:

- the recognizer's sentence-terminal punctuation, and
- a local Smart Turn v3 acoustic model that reads prosody.

Plain silence detection (voice activity detection, or VAD) is the fallback when fusion does not fire.

**HOLD** — "wait, more is coming." A veto panel can suppress a fire. Its sources are independent and OR'd together: the turn holds while *any* of them holds.

A turn commits when FIRE fires and no veto holds. Every hold is bounded, so a held turn always commits eventually — a stuck veto cannot strand a caller.

**The veto panel only runs when turn detection is on.** With `turn_detection: off`, the caller owns end-of-turn entirely through the silence timer and none of the hold logic applies.

## What Holds a Turn Open

Worth knowing, because it tells you which problems are already solved and which need tuning:

- **Grammatical incompleteness.** A neural check on the transcript tail holds while the tail is an incomplete thought. "What is the weather in" does not commit.

- **A number still being dictated.** Holds while a digit run is bare and growing, and releases the moment it resolves to a recognized entity — a phone number that validates, an email that assembles to `local@domain.tld`. Real number dictation pauses four to five seconds between groups, which no acoustic model can distinguish from a turn end, so this covers the gaps. The latency cost is near zero, because a validated entity commits fast.

- **A spelled sequence.** Holds while the tail is a run of three or more single letters and number words containing at least one letter. Spelled words, confirmation codes, UUIDs read aloud.

- **Mid-thought prosody.** Holds while the acoustic model reads the audio just past the last word as mid-list or mid-sentence. "One." spoken as a digit in a list sounds very different from "Yeah." spoken as an answer, and this signal is language-agnostic.

Release is confidence-scaled: an ambiguous hold is cut loose quickly, a clearly incomplete tail waits longer. A false hold therefore costs close to nothing.

## `turn_detection` — the mode switch

`params.enable_turn_detection`, also accepted as `params.turn_detection`. String or boolean:

| Value | Behavior |
|-------|----------|
| `both` | **Default.** Punctuation and the acoustic signal. `true` is an alias. |
| `punct_only` | Punctuation alone ends the turn. |
| `acoustic_only` | The acoustic signal alone ends the turn. `turn_detection_min_length` and `turn_detection_timeout` have no effect. |
| `off` | Neither signal. The agent waits out `end_of_speech_timeout` silence. `false` is an alias. |

**Turn detection is on by default.** An agent config that omits the parameter gets `both`.

```yaml
- ai:
    prompt:
      text: "You are a customer service agent."
    params:
      turn_detection: both        # the default; state it if you care
      end_of_speech_timeout: 700
```

## The One Knob to Tune

**`end_of_speech_timeout` is the user-facing knob. Everything else derives from it.**

It measures audio silence, and it means the same thing whether turn detection is on or off. Turn detection does not replace it — it commits *earlier* than the timeout when it is confident. Default 700 ms.

Diagnosing from symptoms:

| Symptom | Do this |
|---------|---------|
| Agent interrupts callers, or cuts them off mid-sentence | Raise `end_of_speech_timeout`. If your callers dictate numbers, addresses, or spellings, first confirm turn detection is **on** — the digit and spelling holds only exist in that path. |
| Agent is slow to respond after the caller stops | Confirm `turn_detection` is not `off`. `both` is what makes it fast; `off` waits out the full silence timer every time. |

**Reach for the advanced knobs last**, and only against a specific measured problem.

## Advanced Knobs

`turn_detection_min_length` and `turn_detection_timeout` tune `both` and `punct_only`. They have no effect when turn detection is `off` or `acoustic_only`.

| Param | Default | Meaning |
|-------|---------|---------|
| `turn_detection_min_length` | `0` (0–1000) | Minimum transcript characters before punctuation alone can end the turn. In `both`, the acoustic signal can still end a short complete reply such as "Yes." |
| `turn_detection_timeout` | value of `end_of_speech_timeout` (0–10000; `0` uses that default) | Milliseconds to wait after deciding the turn ended before finalizing the transcript. A partial inside the window cancels the decision. Values below `500` degrade accuracy. Lowering it does not make the agent answer faster. |

## Choosing a Recognizer

`params.provider` selects the ASR backend:

| Value | Notes |
|-------|-------|
| `deepgram` | Default |
| `grok` | |
| `gladia` | |
| `pulse` | |

`params.openai_asr_engine` selects the Deepgram model. Documented default `deepgram:nova-3`.

Per-agent credential overrides exist for bring-your-own-key setups: `deepgram_key_override` and `deepgram_url_override`. *(Not on the docs site.)*

## What Not to Promise

The neural components of the veto panel depend on model bundles being present on the node handling the call. **When a bundle is absent, the corresponding veto silently never holds** rather than erroring.

So describe veto behavior as what the platform does, not as a guarantee. Do not write an example whose correctness depends on a hold firing — an agent that only collects a phone number correctly because the digit hold caught the pause between groups is an agent that will sometimes fail. Validate the collected value and re-prompt.

## Related

- [Voice AI](voice-ai.md) — agent overview and voice selection
- [AI Agent Prompting](ai-agent-prompting.md) — prompt structure
- [reference/sdk/agent-base.md](../reference/sdk/agent-base.md) — full `params` list for the SDK
