# AI Agent Turn Taking

How an AI agent decides the caller has finished speaking. This governs whether the agent interrupts people or leaves dead air, and it is the first thing to reach for when an agent "feels wrong" on a call. Callers cut the agent off, or backchannels stop it? [Interruptions (barge-in)](#interruptions-barge-in).

> **This file documents behavior that the public docs do not fully reflect.**
>
> `/docs/swml/reference/calling/ai/params` describes `enable_turn_detection` as a `boolean` that "monitors partial speech transcripts for sentence-ending punctuation." That is half of the older behavior, and it omits the acoustic model entirely. The parameter is a string with four values, and the punctuation check is one of two fused signals.
>
> The end-of-turn behavior below, through What Not to Promise, was verified against the running platform. Do not "correct" it back toward that docs page. The docs are being fixed separately; when they are, this file can be re-checked against them.

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

`params.turn_detection`, alias `params.enable_turn_detection`. Takes a string:

| Value | Behavior |
|-------|----------|
| `both` | **Default.** Punctuation and acoustic fused. Punctuation declares end-of-speech; the acoustic signal can gate it (hold for another word) or override it (declare end-of-speech with no punctuation). |
| `punct_only` | Punctuation only. Acoustic model ignored. |
| `acoustic_only` | Acoustic model only. Punctuation ignored. |
| `off` | No predictive fire. Falls back to the silence timer. Legacy behavior. |

Booleans are accepted as an alias — `true`/`1` maps to `both`, `false`/`0` maps to `off`. That alias is why the current documentation calls the parameter a boolean. `punctuation_only` is accepted as a synonym for `punct_only`.

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

Not on the docs site apart from `turn_detection_timeout`.

These are forwarded to the recognizer only when `turn_detection` is not `off`, and only when set to a non-default value. An unset knob is deliberately not sent, so the recognizer applies its own tuned default.

**Setting a knob to its apparent default is therefore not a no-op.** Writing `250` into `turn_detection_timeout` sends `250`; leaving it unset lets the recognizer choose, and the two can differ.

| Param | Recognizer default when unsent | Meaning |
|-------|-------------------------------|---------|
| `turn_detection_timeout` | 250 ms | Hedge: after fusion decides to fire, wait this long for a new partial to cancel the fire. A ceiling, not the latency driver — a new partial cancels it early. |
| `turn_detection_min_length` | 0 | Minimum transcript length before fusion will fire. Suppresses firing on a stray first word. |
| `acoustic_eot_gate_prob` | 0.40 | Acoustic reading at or below which the model is treated as reporting mid-thought, and can hold the turn. |
| `acoustic_eot_trust_prob` | 0.95 | Acoustic reading above which the model can declare end-of-turn with no punctuation. |
| `speech_event_timeout` | derived: `max(2 × silence, 3500)` ms | Word-silence bound, as opposed to audio-silence. Normally leave unset. |
| `asr_params` | — | Escape hatch, an object. Any key is forwarded to the recognizer verbatim. |

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

## Interruptions (barge-in)

Barge-in is decided by the platform from the speech events, before the model sees anything, while playback is still going out. A prompt line like "if the user interrupts, stop talking" cannot stop that audio. Tune it with `ai` params, not the prompt. Set them on SWML `params`, with Python `set_params` or `set_param`, or with TypeScript `setParams`. The public params page omits or overstates several of these interactions.

`barge_min_words` is the number of words that must be input before barge triggers. `barge_match_string` is a regex the transcript must match to barge. Setting it turns `transparent_barge` off, so the rollup and removal behavior in [Transparent Barge](ai-agent-prompting.md#transparent-barge) no longer applies. `acknowledge_interruptions` and `interrupt_prompt` only take effect in that mode. With both set, an utterance barges if it has at least `barge_min_words` words or matches the regex. To ignore short backchannels, set only `barge_min_words` (2 or more).

`enable_barge` defaults to complete and partial. `false` disables barging. `barge_functions` defaults to false. While a function runs, barge is vetoed unless it is true, and enabling it declares that those functions are re-runnable.

`interrupt_on_noise` (default off) stops playback after about one second of detected speech and skips `barge_min_words`, `barge_match_string` and `static_greeting_no_barge`. Leave it off if you rely on those. `end_of_speech_timeout` is the silence that ends the caller's utterance.

`static_greeting_no_barge: true` stops speech from interrupting the static greeting; DTMF still does. Without it, any speech over a static greeting interrupts it, ignoring `barge_min_words` and `barge_match_string`. A greeting the model generates follows the normal barge filters.

Cut in with one word, then three, then a full sentence. Talk over the greeting. Say "mm-hm" while the agent reads a list. Change one setting at a time and listen to the recordings.

## Related

- [Voice AI](voice-ai.md) — agent overview and voice selection
- [AI Agent Prompting](ai-agent-prompting.md) — prompt structure
- [reference/sdk/agent-base.md](../reference/sdk/agent-base.md) — full `params` list for the SDK
