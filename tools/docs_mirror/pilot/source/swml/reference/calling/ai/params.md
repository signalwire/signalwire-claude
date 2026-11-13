> This page is for SWML.

> Fetch clean Markdown by appending `.md` to any page URL under https://signalwire.com/docs or requesting it with the HTTP header `Accept: text/markdown`. The root index at https://signalwire.com/docs/llms.txt lists the available documentation indexes.

# params

> Parameters for AI that can customize the AI agent's behavior.

[functions-fillers]: /docs/swml/reference/calling/ai/swaig/functions

[ai-languages-params]: /docs/swml/reference/calling/ai/languages#paramssimilarity

[ai-languages]: /docs/swml/reference/calling/ai/languages

[ai-multilingual]: /docs/swml/reference/calling/ai/multilingual

[post-prompt-url]: /docs/swml/reference/calling/ai#post_prompt_url

[get-visual-input]: /docs/swml/reference/calling/ai/swaig#internal_fillersget_visual_input

[semantic-gates]: /docs/swml/reference/calling/ai/swaig/functions/gates

[iana-tz]: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

Parameters for AI that can be passed in `ai.params` at the top level of the [`ai` method](/docs/swml/reference/calling/ai).
These parameters control the fundamental behavior and capabilities of the AI agent, including model selection, conversation management, and advanced features like thinking and vision.

## **Properties**

**`ai.params`** `object`

An object that accepts the following properties.

---

**`params.ai_model`** `string` — default: gpt-4o-mini

The AI model that the AI Agent will use during the conversation.

---

**`params.ai_name`** `string` — default: computer

Sets the name the AI agent responds to for wake/activation purposes. When using `enable_pause`, `start_paused`, or `speak_when_spoken_to`, the user must say this name to get the agent's attention. The name matching is case-insensitive.

---

**`params.app_name`** `string` — default: swml app

A custom identifier for the AI application instance. This name is included in webhook payloads (`post_prompt_url`, SWAIG function calls), allowing backend systems to identify which AI configuration made the request.

---

**`params.conscience`** `string`

Sets the prompt which binds the agent to its purpose. This prompt helps reinforce the AI’s behavior after SWAIG function calls.

It is used to reinforce the AI agent’s behavior and guardrails throughout the conversation.

---

**`params.convo`** `object[]`

Injects pre-existing conversation history into the AI session at startup.
This allows you to seed the AI agent with context from a previous conversation or provide example interactions.

---

**`convo[].role`** `string` — required

The role of the message sender. Valid values:

* `user` - A message from the human caller/user interacting with the AI agent.
* `assistant` - A message from the AI agent itself.
* `system` - A system message providing instructions or context to guide the AI's behavior.

---

**`convo[].content`** `string` — required

The text content of the message.

---

**`convo[].lang`** `string` — default: en

The language code for the message. Uses standard ISO language codes such as `en`, `en-US`, `es`, `fr`, `de`, etc.

---

**`params.conversation_id`** `string`

Used by `check_for_input` and `save_conversation` to identify an individual conversation.

---

**`params.conversation_sliding_window`** `integer`

Sets the size of the sliding window for conversation history. This limits how much conversation history is sent to the AI model.

---

**`params.direction`** `string` — default: the natural direction of the call

Forces the direction of the call to the assistant. Valid values are `inbound` and `outbound`.

---

**`params.double_turns`** `boolean` — default: false

Before each reply, a smaller planning model reviews the conversation and the available functions, then gives the agent a short directive on how to respond. This can improve function use and coherence. The reply waits for the plan, which adds latency to every turn. The planning model is [`utility_model`](#paramsutility_model) if set, otherwise `ai_model`. Billed separately from the agent's per-minute rate. To cover the wait, set [`double_turn_fillers`](/docs/swml/reference/calling/ai/languages#languagesdouble_turn_fillers) on each entry in `languages`.

---

**`params.enable_inner_dialog`** `boolean` — default: false

Enables the inner dialog feature, which runs a separate AI process in the background that analyzes the conversation and provides real-time insights to the main AI agent. This gives the agent a form of "internal thought process" that can help it make better decisions.

---

**`params.enable_pause`** `boolean` — default: false

Enables the pause/resume functionality for the AI agent. When enabled, a `pause_conversation` function is automatically added that the AI can call when the user says things like "hold on", "wait", or "pause". While paused, the agent stops responding until the user speaks the agent's name (set via `ai_name`) to resume. Cannot be used together with `speak_when_spoken_to`.

---

**`params.enable_thinking`** `boolean` — default: false

Enables thinking output for the AI Agent. When set to `true`, the AI Agent will be able to utilize thinking capabilities. This may introduce a little bit of latency as the AI will use an additional turn in the conversation to think about the query.

---

**`params.enable_turn_detection`** `string | boolean` — default: both

How the agent recognizes that the caller has finished speaking. Two signals feed the decision: sentence-ending punctuation in the partial transcript, and an acoustic read of the caller's intonation.

* `both` — Use both signals. Punctuation ends the turn, while the acoustic signal can hold the turn open for another word when the caller sounds mid-sentence, or end it when the caller trails off without punctuation. `true` is an alias.
* `punct_only` — Punctuation alone ends the turn.
* `acoustic_only` — The acoustic signal alone ends the turn.
* `off` — Neither signal is used, and the agent waits out [`end_of_speech_timeout`](#paramsend_of_speech_timeout) silence instead. `false` is an alias.

The `both` and `punct_only` modes are tuned by [`turn_detection_min_length`](#paramsturn_detection_min_length) and [`turn_detection_timeout`](#paramsturn_detection_timeout); `acoustic_only` uses neither. The parameter is also accepted under the name `turn_detection`.

---

**`params.enable_vision`** `boolean` — default: false

Enables visual input processing for the AI Agent. When set to `true`, the AI Agent will be able to utilize visual processing capabilities. The image used for visual processing will be gathered from the user's camera if video is available on the call, leveraging the [`get_visual_input`][get-visual-input] function.

---

**`params.languages_enabled`** `boolean`

Has no effect and can be omitted.

A [`languages`][ai-languages] array takes effect because it is set, not because of this flag, so setting this to `false` does not disable one. The separate [`multilingual`][ai-multilingual] object is likewise switched on by being set.

---

**`params.local_tz`** `string` — default: US/Central

The local timezone setting for the AI. Value should use [IANA TZ ID][iana-tz]

---

**`params.redact_prompt`** `string`

A plain-language description of sensitive content to redact from everything the platform records or transmits about the call — logs, events, webhook payloads, the call timeline, and the post-conversation `call_log` and `raw_call_log`. For example: `"credit card numbers, social security numbers, and full names"`. Redacted content is replaced with `----`. Set this parameter to enable redaction; omit it to leave redaction off.

The caller still hears the content in full, and **the AI still receives the real text** — redaction protects what is recorded and transmitted, not what the AI processes. Redaction can occasionally miss content, so treat it as a safeguard for your logs and integrations rather than an absolute guarantee.

---

**`params.save_conversation`** `boolean` — default: false

Send a summary of the conversation after the call ends. This requires [`post_prompt_url`][post-prompt-url] to be set and the `conversation_id` defined. This eliminates the need for a `post_prompt` in the `ai` parameters. Separately from that end-of-call report, an agent that starts with a `conversation_id` asks `post_prompt_url` for the summary you stored for that ID, and resumes the conversation with it. See [responding to post prompt requests](/docs/swml/reference/calling/ai#responding-to-post-prompt-requests) for the reply format.

---

**`params.summary_mode`** `string`

Summary generation mode. Valid values: `"string"`, `"original"`.

---

**`params.thinking_model`** `string` — default: Value of ai_model parameter

The AI model that the AI Agent will use when utilizing thinking capabilities.

---

**`params.utility_model`** `string` — default: Value of ai_model parameter

The AI model used for lightweight background tasks such as redaction (`redact_prompt`) and transcription cleanup (`auto_correct`). Choose a small, fast model, such as `gpt-4o-mini`, `gpt-4.1-mini`, or `gpt-4.1-nano` — these tasks run while the caller is waiting for a response. A value that is not a recognized model is ignored, and the agent's main model is used instead.

---

**`params.transfer_summary`** `boolean` — default: false

Pass a summary of a conversation from one AI agent to another. For example, transfer a call summary between support agents in two departments.

---

**`params.vision_model`** `string` — default: Value of ai_model parameter

The AI model that the AI Agent will use when utilizing vision capabilities.

---

**`params.visual_input`** `boolean | integer` — default: 1

How many of the caller's newest video frames [`get_visual_input`][get-visual-input] sends, oldest first, taken at most one per second: `true` is `1`, or a whole number from `1` to `5`. Any other value keeps the default. This doesn't affect the `visual_input` of a [semantic gate][semantic-gates] or a [SWAIG function][functions-fillers], which each set their own count.

---

**`params.wait_for_user`** `boolean` — default: false

When false, AI agent will initialize dialogue after call is setup. When true, agent will wait for the user to speak first.

---

### Speech Recognition

Configure how the AI agent processes and understands spoken input, including speaker identification, voice activity detection, and transcription settings.

**`params.asr_diarize`** `boolean` — default: false

If true, enables speaker diarization in ASR (Automatic Speech Recognition). This will break up the transcript into chunks, with each chunk containing a unique identity (e.g speaker1, speaker2, etc.) and the text they spoke.

---

**`params.asr_smart_format`** `boolean` — default: false

Enables smart formatting in ASR (Automatic Speech Recognition). This improves the formatting of numbers, dates, times, and other entities in the transcript.

---

**`params.auto_correct`** `boolean` — default: false

Cleans up the transcription of the caller's speech before the AI reads it — converting spoken numbers to digits, formatting addresses and phone numbers, and fixing obvious mishearings — without changing the meaning. Cannot be used together with `enable_text_normalization`, which is on by default: set `enable_text_normalization` to `"off"` to use `auto_correct`; otherwise `auto_correct` has no effect. When used alongside `redact_prompt`, cleanup and redaction happen together in a single step, which keeps responses fast.

---

**`params.enable_text_normalization`** `string` — default: both

Converts numbers, currency, dates, and similar values between their written and spoken forms so the AI understands callers more accurately and speaks its responses more naturally. For example, a caller who says "twenty three dollars" is understood as `$23`, and the AI's `$23` is spoken back as "twenty three dollars". Applies in both directions by default. See [accepted values](#text-normalization-values) below.

---

**`params.asr_speaker_affinity`** `boolean` — default: false

If true, will force the AI Agent to only respond to the speaker who responds to the AI Agent first. Any other speaker will be ignored.

---

**`params.end_of_speech_timeout`** `integer` — default: 700

Amount of silence, in ms, at the end of an utterance to detect end of speech. Allowed values from `0`-`10,000`.

---

**`params.energy_level`** `number` — default: 52

Amount of energy necessary for bot to hear you (in dB). Allowed values from `0.0`-`100.0`.

---

**`params.first_word_timeout`** `integer` — default: 1000

Amount of time, in ms, to wait for the first word after speech is detected. Allowed values from `0`-`10,000`.

---

**`params.llm_diarize_aware`** `boolean` — default: false

If true, the AI Agent will be involved with the diarization process. Users can state who they are at the start of the conversation and the AI Agent will be able to correctly identify them when they are speaking later in the conversation.

---

**`params.openai_asr_engine`** `string` — default: deepgram:nova-3

The ASR (Automatic Speech Recognition) engine to use. Common values include `deepgram:nova-2`, `deepgram:nova-3`, and other supported ASR engines.

---

#### Values for `enable_text_normalization` \[#text-normalization-values]

| Value                    | Applies to                    | What it does                                                                                                                     |
| ------------------------ | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `heard`                  | Caller input                  | Converts what the caller says into written form before the AI reads it — for example, "twenty three dollars" becomes `$23`.      |
| `spoken`                 | AI responses                  | Converts the AI's written response into spoken form before it is read aloud — for example, `$23` becomes "twenty three dollars". |
| `both`                   | Caller input and AI responses | Applies both conversions. This is the default.                                                                                   |
| `false` / `off` / `none` | —                             | Turns text normalization off.                                                                                                    |
| `true` / `on`            | Caller input and AI responses | Same as `both`.                                                                                                                  |

Text normalization is applied per language and adapts automatically if the conversation switches languages.

> **Note**
>
> If text normalization isn't available for the language being spoken, that direction is simply skipped and the conversation continues uninterrupted. Some languages support only one direction; in that case, `both` applies whichever is available.

### Speech Synthesis

Customize the AI agent's voice output, including volume control, voice characteristics, emotional range, and video avatars for visual interactions.

**`params.ai_volume`** `integer` — default: 0

Adjust the volume of the AI. Allowed values from `-50`-`50`.

---

**`params.max_emotion`** `integer`

Has no effect and can be omitted. Setting it does not change the voice.

---

**`params.speech_gen_quick_stops`** `integer` — default: 3

Number of quick stops for speech generation. Allowed values from `0`-`10`.

---

**`params.tts_number_format`** `string` — default: e164

The format of the number the AI will reference the phone number. Valid values: `e164` (e.g. +12345678901), `international` (e.g. +1 234-567-8901), or `national` (e.g. (234) 567-8901).

---

**`params.video_blank_image`** `string`

What the caller sees on a video call without avatar clips (no `video_talking_file`): an `http://` or `https://` URL to a PNG, shown as a still image. The image can be up to 4 MB and 3840 x 2160 pixels, and is scaled to fit within 1280 x 720. Any other value is ignored. Without it, the still is black.

The still shows when the call captures the caller's video frames, through `enable_vision` or the `visual_input` of a [semantic gate][semantic-gates] or SWAIG function, or when this param is set. Set it whenever you capture frames on a video call without avatar clips, so the caller doesn't see a black screen.

---

**`params.video_idle_file`** `string`

URL of a video file to play when AI is idle. Only works for calls that support video.

---

**`params.video_listening_file`** `string`

URL of a video file to play when AI is listening to the user speak. Only works for calls that support video.

---

**`params.video_talking_file`** `string`

URL of a video file to play when AI is talking. Only works for calls that support video.

---

**`params.eleven_labs_similarity`** `number` — deprecated, default: 0.75

The similarity slider dictates how closely the AI should adhere to the original voice when attempting to replicate it. The higher the similarity, the closer the AI will sound to the original voice. Valid values range from `0.0` to `1.0`. **Deprecated**: Use [`languages[].params.similarity`][ai-languages-params] instead.

---

**`params.eleven_labs_stability`** `number` — deprecated, default: 0.50

The stability slider determines how stable the voice is and the randomness between each generation. Lowering this slider introduces a broader emotional range for the voice. Valid values range from `0.0` to `1.0`. **Deprecated**: Use [`languages[].params.stability`][ai-languages-params] instead.

---

### Interruption & Barge Control

Manage how the AI agent handles interruptions when users speak over it, including when to stop speaking, acknowledge interruptions, or continue regardless.

**`params.acknowledge_interruptions`** `boolean | integer` — default: false

Instructs the agent to acknowledge crosstalk and confirm user input when the user speaks over the agent. `true` acknowledges up to one interruption; a positive integer sets the maximum number of interruptions to acknowledge.

---

**`params.barge_functions`** `boolean` — default: false

Allow functions to be called during barging. When `false`, functions are not executed if the user is speaking.

---

**`params.barge_match_string`** `string`

Takes a string, including a regular expression, defining barge behavior. For example, this param can direct the AI to stop when the word "hippopotamus" is input.

---

**`params.barge_min_words`** `integer`

Defines the number of words that must be input before triggering barge behavior. Allowed values from `1`-`99`.

---

**`params.enable_barge`** `string`

Controls when user can interrupt the AI. Valid values: `"complete"`, `"partial"`, `"all"`, or boolean. Set to `false` to disable barging.

---

**`params.interrupt_on_noise`** `boolean` — default: false

When enabled, barges agent upon any sound interruption longer than 1 second. The 1-second threshold can't be changed.

---

**`params.interrupt_prompt`** `string`

A prompt that is used to help the AI agent respond to interruptions.

**Default:** "The user didn't wait for you to finish responding and started talking over you. As part of your next response, make a comment about how you were both talking at the same time and verify you properly understand what the user said."

---

**`params.transparent_barge`** `boolean` — default: true

When enabled, the AI will not respond to the user's input when the user is speaking over the agent. The agent will wait for the user to finish speaking before responding. Additionally, any attempt the LLM makes to barge will be ignored and scraped from the conversation logs.

---

**`params.transparent_barge_max_time`** `integer` — default: 3000

Maximum duration for transparent barge mode. Allowed values from `0`-`60,000` ms.

---

### Timeouts & Delays

Set various timing parameters that control wait times, response delays, and session limits to optimize the conversation flow and prevent dead air.

**`params.attention_timeout`** `integer` — default: 5000

Amount of time, in ms, to wait before prompting the user to respond. Allowed values: `0` (to disable) or `1,000`-`600,000`.

---

**`params.attention_timeout_prompt`** `string` — default: The user has not responded, try to get their attention. Stay in the same language.

A custom prompt that is fed into the AI when the `attention_timeout` is reached.

---

**`params.digit_timeout`** `integer` — default: 3000

Time, in ms, at the end of digit input to detect end of input. Allowed values from `1`-`29,999`; any other value keeps the default.

---

**`params.hard_stop_prompt`** `string`

A final prompt that is fed into the AI when the `hard_stop_time` is reached.

---

**`params.hard_stop_time`** `string`

The maximum time the AI Agent stays active. Once it has passed, the next time the agent is waiting for the caller it receives [`hard_stop_prompt`](#paramshard_stop_prompt) as a final instruction for its last reply. The conversation then ends and the next SWML instruction runs. The stop is not exact and does not cut off speech in progress.

Time format: a string in `HH:MM:SS` or `MM:SS` form, or a whole number of seconds. For example, `"30:00"` and `"1800"` are both 30 minutes. In the colon forms, minutes and seconds go up to `59`.

> **Unit suffixes are not converted**
>
> Values such as `30m` or `1h` are not read as minutes or hours: the letters are ignored, so `30m` sets a 30-second limit. Use the colon form or a number of seconds instead.

---

**`params.inactivity_timeout`** `integer` — default: 600000

Amount of time, in ms, to wait before exiting the app due to inactivity. Allowed values: `0` (to disable) or `10,000`-`3,600,000`.

---

**`params.initial_sleep_ms`** `integer` — default: 0

Amount of time, in ms, to wait before the AI Agent starts processing. Allowed values from `0`-`300,000`.

---

**`params.outbound_attention_timeout`** `integer` — default: 120000

Sets a time duration for the outbound call recipient to respond to the AI agent before timeout. Allowed values from `10,000`-`600,000` ms.

---

**`params.speech_event_timeout`** `integer` — default: 0

Timeout for speech events processing. Allowed values from `0`-`10,000` ms. `0`, or leaving it unset, lets speech recognition set this timing itself.

---

**`params.speech_timeout`** `integer`

Has no effect and can be omitted. Setting it does not change speech timing on your calls.

---

### Audio & Media

Control background audio, hold music, and greeting messages to enhance the caller experience during different phases of the conversation.

**`params.background_file`** `string`

URL of audio file to play in the background while AI plays in foreground.

---

**`params.background_file_loops`** `integer` — default: undefined

Maximum number of times to loop playing the background file.

---

**`params.background_file_volume`** `integer` — default: 0

Defines `background_file` volume. Allowed values from `-50` to `50`.

---

**`params.hold_music`** `string`

A URL for the hold music to play, accepting WAV, mp3, and FreeSWITCH [`tone_stream`](https://developer.signalwire.com/freeswitch/media-and-codecs/audio-files/#mod_tone_stream-and-the-tgml-generator).

---

**`params.hold_on_process`** `boolean` — default: false

Enables hold music during SWAIG processing.

---

**`params.static_greeting`** `string`

The static greeting to play when the call is answered. This will always play at the beginning of the call.

---

**`params.static_greeting_no_barge`** `boolean` — default: false

If `true`, the static greeting will not be interrupted by the user if they speak over the greeting. If `false`, the static greeting can be interrupted by the user if they speak over the greeting.

---

### SWAIG Functions

Configure SignalWire AI Gateway (SWAIG) function capabilities, including permissions, execution timing, and data persistence across function calls.

**`params.function_wait_for_talking`** `boolean` — default: false

If `true`, the AI will wait for any [`filler`][functions-fillers] to finish playing before executing a function. If `false`, the AI will asynchronously execute a function while playing a filler.

---

**`params.functions_on_no_response`** `boolean` — default: false

Execute functions when the user doesn't respond (on attention timeout).

---

**`params.swaig_allow_settings`** `boolean` — default: true

Allows SWAIG functions to change the AI model's settings with the [`settings` action](/docs/swml/reference/calling/ai/swaig/functions/data-map#list-of-valid-actions) in their response. Only settings the selected model supports are applied.

---

**`params.swaig_allow_swml`** `boolean` — default: true

Allows your SWAIG to return SWML to be executed.

---

**`params.swaig_post_conversation`** `boolean` — default: false

Post entire conversation to any SWAIG call.

---

**`params.swaig_set_global_data`** `boolean` — default: true

Allows SWAIG functions to change `global_data` with the [`set_global_data` and `unset_global_data` actions](/docs/swml/reference/calling/ai/swaig/functions/data-map#list-of-valid-actions). Changes last for the rest of the AI session and don't carry over to other calls. To keep `global_data` for a later AI session on the same call, see [`persist_global_data`](#paramspersist_global_data).

---

**`params.semantic_gates_enabled`** `boolean` — default: true

Whether the call checks the [semantic gates][semantic-gates] on its SWAIG functions. Set it to `false` to turn gate checks off for the call: gated functions then run without being checked.

---

**`params.semantic_gate_timeout_ms`** `integer` — default: 2500

How long one semantic gate check may take in total, in milliseconds. A check that runs out of time blocks the function. Allowed values from `500` to `10000`.

---

**`params.semantic_gate_history`** `integer` — default: 20

How many recent conversation entries a semantic gate check reads. Allowed values from `0` to `100`.

---

A `semantic_gate_timeout_ms` or `semantic_gate_history` value outside its range is clamped to it, and a number's fraction is dropped. A string is read as a whole number (`"3000"`); a string that isn't one (`"3000ms"`, `"2.5"`), a boolean, or `null` keeps the default.

### Input & DTMF

Handle dual-tone multi-frequency (DTMF) input and configure input polling for integrating external data sources during conversations.

**`params.digit_terminators`** `string`

DTMF digit, as a string, to signal the end of input (ex: "#")

---

**`params.input_poll_freq`** `integer` — default: 2000

Check for input function with `check_for_input`. Allowed values from `1,000`-`10,000` ms. Example use case: Feeding an inbound SMS to AI on a voice call, eg., for collecting an email address or other complex information.

---

### Debug & Development

Enable debugging tools, logging, and performance monitoring features to help developers troubleshoot and optimize their AI agent implementations.

**`params.audible_debug`** `boolean` — default: false

If `true`, the AI will announce the function that is being executed on the call.

---

**`params.audible_latency`** `boolean` — default: false

Announce latency information during the call for debugging purposes.

---

**`params.cache_mode`** `boolean` — default: false

Enable response caching to improve performance for repeated queries.

---

**`params.debug`** `boolean | integer` — default: false

Enables debug mode for the AI session. When set to `true` or a positive integer, additional debug information is logged and may be included in webhook payloads. Higher integer values increase verbosity.

---

**`params.debug_webhook_level`** `integer` — default: 1

How much the debug stream carries. Allowed values from `0`-`2`. Level 2 adds `conversation_add`, `llm_request`, and `llm_response`, which together are far higher volume than everything else combined. Setting `debug_webhook_url` is what turns the stream on, so lowering the level thins the stream rather than stopping it. See the [debug_webhook_url callback](#debug_webhook_url-callback) below.

---

**`params.debug_webhook_url`** `string`

Each interaction between the AI and end user is posted in real time to the established URL. Authentication can also be set in the url in the format of `username:password@url`. See the [debug_webhook_url callback](#debug_webhook_url-callback) below.

---

**`params.enable_accounting`** `boolean` — default: false

Enable usage accounting and tracking for billing and analytics purposes.

---

**`params.verbose_logs`** `boolean`

Has no effect and can be omitted.

---

### Inner Dialog

Configure the inner dialog feature, which enables a secondary AI process to analyze conversations in real-time and provide insights to the main AI agent.

**`params.inner_dialog_model`** `string`

Specifies the AI model to use for the inner dialog feature. If not set, the main `ai_model` is used. This allows you to use a different (potentially faster or cheaper) model for background analysis.

---

**`params.inner_dialog_prompt`** `string` — default: The assistant is intelligent and straightforward, does its job well and is not excessively polite.

The system prompt that guides the inner dialog AI's behavior. This prompt shapes how the background AI analyzes the conversation and what kind of insights it provides to the main agent.

---

**`params.inner_dialog_synced`** `boolean`

Has no effect and can be omitted. Setting it does not change how the inner dialog runs.

---

### Pause & Wake

Control the agent's listening behavior, including pause/resume functionality and activation triggers for hands-free scenarios.

**`params.speak_when_spoken_to`** `boolean` — default: false

When enabled, the AI agent remains silent until directly addressed by name (set via `ai_name`). This creates a "push-to-talk" style interaction where the agent only responds when explicitly called upon, useful for scenarios where the agent should listen but not interrupt.

---

**`params.start_paused`** `boolean` — default: false

When enabled, the AI agent starts in a paused state. The agent will not respond to any input until the user speaks the agent's name (set via `ai_name`) to activate it. This is useful for scenarios where you want the agent to wait for explicit activation.

---

**`params.wake_prefix`** `string`

Specifies an additional prefix that must be spoken along with the agent's name to wake the agent. For example, if `ai_name` is "assistant" and `wake_prefix` is "hey", the user would need to say "hey assistant" to activate the agent.

---

### Advanced Configuration

Fine-tune advanced AI behavior settings including response limits, data persistence, prompt formatting, and voice activity detection.

**`params.max_response_tokens`** `integer`

Has no effect and can be omitted. Setting it does not limit the length of the AI's responses.

---

**`params.persist_global_data`** `boolean` — default: true

When enabled, `global_data` persists across multiple AI agent invocations within the same call. This allows data set by SWAIG functions to be retained if the AI agent is invoked multiple times during a single call session.

---

**`params.pom_format`** `string` — default: markdown

Specifies the output format for structured prompts sent to the AI model. Valid values are `markdown` or `xml`. This affects how system prompts and context are formatted when sent to the underlying language model.

---

**`params.swaig_post_swml_vars`** `boolean | array` — default: false

Controls whether SWML variables are included in SWAIG function webhook payloads. When set to `true`, all SWML variables are posted. When set to an array of strings, only the specified variable names are included in the payload.

---

**`params.turn_detection_min_length`** `integer` — default: 0

Minimum number of characters the transcript must contain before punctuation on its own can end the caller's turn. Raise it so a back-channel the recognizer renders with a full stop — "Uh-huh." while the agent is still being answered — doesn't end a turn the caller hasn't finished. Allowed values from `0` to `1000`, where `0` lets a transcript of any length end a turn.

In `both` mode the acoustic signal overrides this: when it reads the caller as finished, the turn ends whatever the length, so short complete replies like "Yes." still work. That leaves this a filter on the punctuation path alone, and it has no effect when [`enable_turn_detection`](#paramsenable_turn_detection) is `off` or `acoustic_only`.

---

**`params.turn_detection_timeout`** `integer` — default: Value of end_of_speech_timeout

Time in milliseconds the agent waits after deciding the caller's turn has ended before it finalizes the transcript. A partial transcript arriving inside the window cancels the decision, so this is a ceiling on how long a turn can hang rather than latency added to every turn. A caller who has finished usually commits well inside it.

Lowering it therefore doesn't make the agent answer faster, and values below `500` degrade transcription accuracy on words the recognizer needs the extra audio to disambiguate. Allowed values from `0` to `10000`, where `0` uses the default. Has no effect when [`enable_turn_detection`](#paramsenable_turn_detection) is `off` or `acoustic_only`.

---

**`params.turn_filler_every_n`** `integer` — default: 1

Play a backchannel on every Nth opportunity rather than all of them. The count advances only on opportunities that would otherwise have produced one, and resets when the caller starts a new turn, so the first opportunity of each turn always plays. A turn that chains several waits shares one count, so raising this widens the spacing across the whole stretch rather than restarting at each wait.

---

**`params.turn_filler_min_ms`** `integer` — default: 0

How long a wait must already have run, in milliseconds, before a backchannel plays. Off by default: waits open the moment the agent decides to hold, and `spell` and `number` are meant to be answered right then. A positive `<token>:<ms>` suffix in `turn_filler_sources` replaces this for that token, but `:0` does not clear it. To answer one source immediately while delaying others, leave this at `0` and put suffixes on the others.

---

**`params.turn_filler_sources`** `string` — default: spell,number

Which deliberate waits earn a backchannel from [`languages[].turn_fillers`](/docs/swml/reference/calling/ai/languages#languagesturn_fillers), or from [`multilingual.turn_fillers`](/docs/swml/reference/calling/ai/multilingual#aimultilingualturn_fillers) when the agent is in multilingual mode, as a comma-separated list of tokens. A wait happens when the agent holds off answering because the caller is not finished, and the token names why.

List a specific hold source, or a whole class of wait:

* `spell` — the caller is spelling something out
* `number` — the caller is reading out digits
* `text` — the wording suggests the caller is mid-sentence
* `acoustic` — the audio suggests the caller is mid-sentence
* `veto` — any of the above

The default answers `spell` and `number` only, because those pauses are expected and cannot be shortened. A backchannel during `text` or `acoustic` usually talks over a caller who is still going, so give either its own delay with a `<token>:<ms>` suffix rather than listing it bare, as in `spell,number,text:1200`.

Tokens are matched whole and case-insensitively, and a space after a comma is fine. A token that is not one of the five above matches no wait, so nothing here is validated and a misspelling silently leaves the agent with no backchannels at all.

---

**`params.vad_config`** `string`

Configures Silero Voice Activity Detection (VAD) settings. Format: `threshold` or `threshold:frame_ms`. The threshold (0-100) sets sensitivity for voice detection, and optional frame_ms (16-40) sets the analysis frame duration in milliseconds.

---

## debug_webhook_url callback

A diagnostic feed for a call that is still in progress. Set `debug_webhook_url` and every step the
agent takes is posted to that URL as it happens: speech recognized, model called, tool invoked,
context switched, error hit. Use it to work out why a call went the way it did — which tool the agent
reached for, what came back, where a turn went wrong — or to react while the call is still live, such
as paging a supervisor.

Each request carries `call_info` plus one or more event properties, where the property name is the
event. One moment can produce several: evaluating a
[`data_map`](/docs/swml/reference/calling/ai/swaig/functions/data-map) webhook sends `webhook`,
`input`, `output`, `error_keys`, and `match` together. Handle the properties you recognize and ignore
the rest, since the set grows over time.

See the [AI debug webhook](/docs/apis/rest/webhooks/ai-debug-webhook) webhook page for the full
field reference. [Conversation analytics](/docs/platform/ai/analytics#choose-the-right-source) explains when
to use the debug stream and when to use the post-prompt report.