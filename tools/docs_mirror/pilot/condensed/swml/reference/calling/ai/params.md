# ai.params (SWML ai method)
Source: https://signalwire.com/docs/swml/reference/calling/ai/params.md

`ai.params` object, set at the top level of the `ai` method (https://signalwire.com/docs/swml/reference/calling/ai.md). All properties below are under `params.`.

## General

- `ai_model` string, default gpt-4o-mini — model used during the conversation
- `ai_name` string, default computer — name the agent responds to for wake/activation; with `enable_pause`, `start_paused`, or `speak_when_spoken_to` the user must say it to get the agent's attention. Matching is case-insensitive.
- `app_name` string, default swml app — identifier included in webhook payloads (`post_prompt_url`, SWAIG function calls)
- `conscience` string — prompt that binds the agent to its purpose; reinforces behavior and guardrails after SWAIG function calls and throughout the conversation
- `convo` object[] — conversation history injected at startup (seed context or example interactions)
  - `convo[].role` string, required — values: user | assistant | system
  - `convo[].content` string, required — message text
  - `convo[].lang` string, default en — ISO language code (`en`, `en-US`, `es`, `fr`, `de`, …)
- `conversation_id` string — identifies a conversation for `check_for_input` and `save_conversation`
- `conversation_sliding_window` integer — size of the sliding window limiting how much history is sent to the model
- `direction` string, default the natural direction of the call — forces call direction; values: inbound | outbound
- `double_turns` boolean, default false — before each reply a smaller planning model reviews the conversation and available functions and gives the agent a short directive. The reply waits for the plan: adds latency to every turn. Planning model is `utility_model` if set, otherwise `ai_model`. Billed separately from the agent's per-minute rate. To cover the wait, set `double_turn_fillers` on each `languages` entry (https://signalwire.com/docs/swml/reference/calling/ai/languages.md).
- `enable_inner_dialog` boolean, default false — runs a separate background AI process that analyzes the conversation and feeds real-time insights to the main agent
- `enable_pause` boolean, default false — auto-adds a `pause_conversation` function the AI calls when the user says "hold on"/"wait"/"pause"; while paused the agent stays silent until the user speaks `ai_name`. Cannot be used with `speak_when_spoken_to`.
- `enable_thinking` boolean, default false — enables thinking; may add latency (uses an extra turn to think)
- `enable_turn_detection` string | boolean, default both — how the agent decides the caller finished speaking, from two signals: sentence-ending punctuation in the partial transcript, and an acoustic read of intonation. Also accepted as `turn_detection`. Values:
  - `both` (alias `true`) — punctuation ends the turn; acoustic signal can hold the turn open for another word when the caller sounds mid-sentence, or end it when the caller trails off without punctuation
  - `punct_only` — punctuation alone ends the turn
  - `acoustic_only` — acoustic signal alone ends the turn
  - `off` (alias `false`) — neither signal; agent waits out `end_of_speech_timeout` silence
  - `both` and `punct_only` are tuned by `turn_detection_min_length` and `turn_detection_timeout`; `acoustic_only` uses neither.
- `enable_vision` boolean, default false — visual input processing; image comes from the user's camera if video is available, via `get_visual_input` (internal_fillers, https://signalwire.com/docs/swml/reference/calling/ai/swaig.md)
- `languages_enabled` boolean — has no effect, can be omitted. A `languages` array (https://signalwire.com/docs/swml/reference/calling/ai/languages.md) takes effect because it is set, so `false` does not disable one. The `multilingual` object (https://signalwire.com/docs/swml/reference/calling/ai/multilingual.md) is likewise switched on by being set.
- `local_tz` string, default US/Central — IANA TZ ID (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
- `redact_prompt` string — plain-language description of sensitive content to redact from everything the platform records or transmits: logs, events, webhook payloads, call timeline, post-conversation `call_log` and `raw_call_log`. E.g. `"credit card numbers, social security numbers, and full names"`. Redacted content becomes `----`. Set to enable; omit to leave redaction off. The caller still hears content in full and **the AI still receives the real text** — protects what is recorded/transmitted, not what the AI processes. Redaction can occasionally miss content; a safeguard, not an absolute guarantee.
- `save_conversation` boolean, default false — send a conversation summary after the call ends. Requires `post_prompt_url` (https://signalwire.com/docs/swml/reference/calling/ai.md) and `conversation_id`. Eliminates need for a `post_prompt` in the `ai` parameters. Separately, an agent that starts with a `conversation_id` asks `post_prompt_url` for the summary stored for that ID and resumes the conversation with it; reply format: "responding to post prompt requests" in https://signalwire.com/docs/swml/reference/calling/ai.md
- `summary_mode` string — values: "string" | "original"
- `thinking_model` string, default Value of ai_model parameter — model used for thinking
- `utility_model` string, default Value of ai_model parameter — model for lightweight background tasks such as redaction (`redact_prompt`) and transcription cleanup (`auto_correct`); these run while the caller waits, so choose a small fast model (e.g. `gpt-4o-mini`, `gpt-4.1-mini`, `gpt-4.1-nano`). An unrecognized model value is ignored and the main model is used.
- `transfer_summary` boolean, default false — pass a conversation summary from one AI agent to another (e.g. between support agents in two departments)
- `vision_model` string, default Value of ai_model parameter — model used for vision
- `visual_input` boolean | integer, default 1 — how many of the caller's newest video frames `get_visual_input` sends, oldest first, at most one per second: `true` = `1`, or a whole number `1`–`5`; any other value keeps the default. Does not affect the `visual_input` of a semantic gate (https://signalwire.com/docs/swml/reference/calling/ai/swaig/functions/gates.md) or SWAIG function (https://signalwire.com/docs/swml/reference/calling/ai/swaig/functions.md), which set their own.
- `wait_for_user` boolean, default false — false: agent starts dialogue after call setup; true: agent waits for the user to speak first

## Speech recognition

- `asr_diarize` boolean, default false — speaker diarization; transcript split into chunks each with an identity (speaker1, speaker2, …) and text
- `asr_smart_format` boolean, default false — better formatting of numbers, dates, times, and other entities in the transcript
- `auto_correct` boolean, default false — cleans up the caller's transcription before the AI reads it (spoken numbers to digits, formats addresses and phone numbers, fixes obvious mishearings) without changing meaning. Cannot be used with `enable_text_normalization`, which is on by default: set `enable_text_normalization` to `"off"` or `auto_correct` has no effect. With `redact_prompt`, cleanup and redaction run together in a single step.
- `enable_text_normalization` string, default both — converts numbers, currency, dates, etc. between written and spoken forms (caller "twenty three dollars" → `$23`; AI `$23` → spoken "twenty three dollars"). Values:
  - `heard` — caller input only: speech → written form before the AI reads it
  - `spoken` — AI responses only: written → spoken form before TTS
  - `both` — both directions (default)
  - `false` / `off` / `none` — off
  - `true` / `on` — same as `both`
  - Applied per language; adapts automatically if the conversation switches languages. Note: if normalization isn't available for the spoken language, that direction is skipped and the conversation continues. Some languages support only one direction; `both` then applies whichever is available.
- `asr_speaker_affinity` boolean, default false — agent responds only to the speaker who responds to it first; others ignored
- `end_of_speech_timeout` integer, default 700 — ms of silence at end of utterance to detect end of speech; `0`–`10,000`
- `energy_level` number, default 52 — energy (dB) needed for the bot to hear you; `0.0`–`100.0`
- `first_word_timeout` integer, default 1000 — ms to wait for the first word after speech is detected; `0`–`10,000`
- `llm_diarize_aware` boolean, default false — agent participates in diarization; users can state who they are at the start and the agent identifies them later
- `openai_asr_engine` string, default deepgram:nova-3 — ASR engine; common values include `deepgram:nova-2`, `deepgram:nova-3`, and other supported engines

## Speech synthesis

- `ai_volume` integer, default 0 — AI volume; `-50`–`50`
- `max_emotion` integer — has no effect, can be omitted; does not change the voice
- `speech_gen_quick_stops` integer, default 3 — number of quick stops for speech generation; `0`–`10`
- `tts_number_format` string, default e164 — how the AI references phone numbers; values: `e164` (+12345678901) | `international` (+1 234-567-8901) | `national` ((234) 567-8901)
- `video_blank_image` string — what the caller sees on a video call without avatar clips (no `video_talking_file`): an `http://` or `https://` URL to a PNG shown as a still. Up to 4 MB and 3840 x 2160 pixels; scaled to fit within 1280 x 720. Any other value is ignored. Without it the still is black. The still shows when the call captures caller video frames (via `enable_vision`, or the `visual_input` of a semantic gate or SWAIG function) or when this param is set. Set it whenever you capture frames on a video call without avatar clips, so the caller doesn't see a black screen.
- `video_idle_file` string — video URL played when AI is idle; video-capable calls only
- `video_listening_file` string — video URL played while AI listens to the user; video-capable calls only
- `video_talking_file` string — video URL played while AI talks; video-capable calls only
- `eleven_labs_similarity` number, deprecated, default 0.75 — how closely AI adheres to the original voice; `0.0`–`1.0`. Use `languages[].params.similarity` instead (https://signalwire.com/docs/swml/reference/calling/ai/languages.md).
- `eleven_labs_stability` number, deprecated, default 0.50 — voice stability/randomness between generations; lower = broader emotional range; `0.0`–`1.0`. Use `languages[].params.stability` instead.

## Interruption & barge

- `acknowledge_interruptions` boolean | integer, default false — agent acknowledges crosstalk and confirms user input when the user speaks over it. `true` = up to one interruption; positive integer = max interruptions to acknowledge.
- `barge_functions` boolean, default false — allow functions during barging; when `false`, functions don't execute while the user is speaking
- `barge_match_string` string — string or regular expression defining barge behavior (e.g. stop when the word "hippopotamus" is input)
- `barge_min_words` integer — words that must be input before barge triggers; `1`–`99`
- `enable_barge` string — when the user can interrupt; values: "complete" | "partial" | "all" | boolean. `false` disables barging.
- `interrupt_on_noise` boolean, default false — barges the agent on any sound longer than 1 second; threshold can't be changed
- `interrupt_prompt` string — prompt to help the agent respond to interruptions. Default: "The user didn't wait for you to finish responding and started talking over you. As part of your next response, make a comment about how you were both talking at the same time and verify you properly understand what the user said."
- `transparent_barge` boolean, default true — agent doesn't respond while the user speaks over it; waits for the user to finish. Any attempt the LLM makes to barge is ignored and scraped from conversation logs.
- `transparent_barge_max_time` integer, default 3000 — max duration of transparent barge mode; `0`–`60,000` ms

## Timeouts & delays

- `attention_timeout` integer, default 5000 — ms before prompting the user to respond; `0` (disable) or `1,000`–`600,000`
- `attention_timeout_prompt` string, default The user has not responded, try to get their attention. Stay in the same language. — prompt fed to the AI when `attention_timeout` is reached
- `digit_timeout` integer, default 3000 — ms at end of digit input to detect end of input; `1`–`29,999`; any other value keeps the default
- `hard_stop_prompt` string — final prompt fed to the AI when `hard_stop_time` is reached
- `hard_stop_time` string — max time the agent stays active. Once passed, the next time the agent is waiting for the caller it receives `hard_stop_prompt` as a final instruction for its last reply; the conversation then ends and the next SWML instruction runs. Not exact; does not cut off speech in progress. Format: `HH:MM:SS`, `MM:SS`, or a whole number of seconds (`"30:00"` and `"1800"` are both 30 minutes); in colon forms minutes and seconds go up to `59`. Unit suffixes are not converted: letters are ignored, so `30m` = 30-second limit (same for `1h`). Use colon form or seconds.
- `inactivity_timeout` integer, default 600000 — ms before exiting the app due to inactivity; `0` (disable) or `10,000`–`3,600,000`
- `initial_sleep_ms` integer, default 0 — ms to wait before the agent starts processing; `0`–`300,000`
- `outbound_attention_timeout` integer, default 120000 — time for the outbound call recipient to respond before timeout; `10,000`–`600,000` ms
- `speech_event_timeout` integer, default 0 — timeout for speech event processing; `0`–`10,000` ms. `0` or unset lets speech recognition set this timing itself.
- `speech_timeout` integer — has no effect, can be omitted; does not change speech timing

## Audio & media

- `background_file` string — URL of audio played in the background while AI plays in foreground
- `background_file_loops` integer, default undefined — max times to loop the background file
- `background_file_volume` integer, default 0 — `background_file` volume; `-50`–`50`
- `hold_music` string — hold music URL; accepts WAV, mp3, and FreeSWITCH `tone_stream` (https://developer.signalwire.com/freeswitch/media-and-codecs/audio-files/#mod_tone_stream-and-the-tgml-generator)
- `hold_on_process` boolean, default false — hold music during SWAIG processing
- `static_greeting` string — greeting played when the call is answered; always plays at the beginning of the call
- `static_greeting_no_barge` boolean, default false — `true`: greeting can't be interrupted by the user speaking over it; `false`: it can

## SWAIG functions

- `function_wait_for_talking` boolean, default false — `true`: wait for any filler (https://signalwire.com/docs/swml/reference/calling/ai/swaig/functions.md) to finish before executing a function; `false`: execute asynchronously while the filler plays
- `functions_on_no_response` boolean, default false — execute functions when the user doesn't respond (on attention timeout)
- `swaig_allow_settings` boolean, default true — SWAIG functions may change model settings via the `settings` action (https://signalwire.com/docs/swml/reference/calling/ai/swaig/functions/data-map.md, list of valid actions). Only settings the selected model supports are applied.
- `swaig_allow_swml` boolean, default true — SWAIG may return SWML to execute
- `swaig_post_conversation` boolean, default false — post entire conversation to any SWAIG call
- `swaig_set_global_data` boolean, default true — SWAIG functions may change `global_data` via `set_global_data` / `unset_global_data` actions (data-map page above). Changes last for the rest of the AI session and don't carry over to other calls; to keep `global_data` for a later AI session on the same call see `persist_global_data`.
- `semantic_gates_enabled` boolean, default true — whether the call checks semantic gates (https://signalwire.com/docs/swml/reference/calling/ai/swaig/functions/gates.md) on SWAIG functions; `false` turns checks off and gated functions run unchecked
- `semantic_gate_timeout_ms` integer, default 2500 — total ms one semantic gate check may take; a check that runs out of time blocks the function; `500`–`10000`
- `semantic_gate_history` integer, default 20 — recent conversation entries a gate check reads; `0`–`100`
- For `semantic_gate_timeout_ms` and `semantic_gate_history`: out-of-range values are clamped; a number's fraction is dropped; a string is read as a whole number (`"3000"`); a non-integer string (`"3000ms"`, `"2.5"`), a boolean, or `null` keeps the default.

## Input & DTMF

- `digit_terminators` string — DTMF digit, as a string, signaling end of input (e.g. "#")
- `input_poll_freq` integer, default 2000 — check-for-input poll interval (`check_for_input`); `1,000`–`10,000` ms. Use case: feeding an inbound SMS to the AI on a voice call (e.g. collecting an email address).

## Debug & development

- `audible_debug` boolean, default false — AI announces the function being executed
- `audible_latency` boolean, default false — announce latency info during the call
- `cache_mode` boolean, default false — response caching for repeated queries
- `debug` boolean | integer, default false — `true` or positive integer logs extra debug info, which may be included in webhook payloads; higher integers increase verbosity
- `debug_webhook_level` integer, default 1 — how much the debug stream carries; `0`–`2`. Level 2 adds `conversation_add`, `llm_request`, `llm_response` (together far higher volume than everything else combined). Setting `debug_webhook_url` turns the stream on; lowering the level thins it, doesn't stop it.
- `debug_webhook_url` string — each interaction posted in real time to this URL; auth can be embedded as `username:password@url`. See callback below.
- `enable_accounting` boolean, default false — usage accounting/tracking for billing and analytics
- `verbose_logs` boolean — has no effect, can be omitted

## Inner dialog

- `inner_dialog_model` string — model for inner dialog; if unset, `ai_model` is used
- `inner_dialog_prompt` string, default The assistant is intelligent and straightforward, does its job well and is not excessively polite. — system prompt for the inner dialog AI
- `inner_dialog_synced` boolean — has no effect, can be omitted

## Pause & wake

- `speak_when_spoken_to` boolean, default false — agent stays silent until addressed by name (`ai_name`); "push-to-talk" style
- `start_paused` boolean, default false — agent starts paused; doesn't respond until the user speaks `ai_name`
- `wake_prefix` string — extra prefix required with the name to wake (e.g. `ai_name` "assistant" + `wake_prefix` "hey" → user says "hey assistant")

## Advanced

- `max_response_tokens` integer — has no effect, can be omitted; does not limit response length
- `persist_global_data` boolean, default true — `global_data` persists across multiple AI agent invocations within the same call
- `pom_format` string, default markdown — format for structured prompts sent to the model; values: markdown | xml
- `swaig_post_swml_vars` boolean | array, default false — include SWML variables in SWAIG webhook payloads: `true` = all; array of strings = only those variable names
- `turn_detection_min_length` integer, default 0 — min transcript characters before punctuation alone can end the caller's turn (raise so a back-channel like "Uh-huh." with a full stop doesn't end an unfinished turn); `0`–`1000`, `0` = any length. In `both` mode the acoustic signal overrides this (when it reads the caller as finished the turn ends regardless of length, so "Yes." still works), so it filters only the punctuation path. No effect when `enable_turn_detection` is `off` or `acoustic_only`.
- `turn_detection_timeout` integer, default Value of end_of_speech_timeout — ms the agent waits after deciding the turn ended before finalizing the transcript. A partial transcript arriving inside the window cancels the decision, so this is a ceiling on how long a turn can hang, not latency added to every turn; a caller who has finished usually commits well inside it. Lowering it doesn't make the agent answer faster; values below `500` degrade transcription accuracy on words the recognizer needs extra audio to disambiguate. `0`–`10000`, `0` uses the default. No effect when `enable_turn_detection` is `off` or `acoustic_only`.
- `turn_filler_every_n` integer, default 1 — play a backchannel on every Nth opportunity. Count advances only on opportunities that would otherwise have produced one, and resets when the caller starts a new turn (first opportunity of each turn always plays). A turn chaining several waits shares one count, so raising this widens spacing across the whole stretch.
- `turn_filler_min_ms` integer, default 0 — ms a wait must already have run before a backchannel plays. Off by default: waits open the moment the agent decides to hold, and `spell`/`number` are meant to be answered right then. A positive `<token>:<ms>` suffix in `turn_filler_sources` replaces this for that token, but `:0` does not clear it. To answer one source immediately while delaying others, leave this at `0` and put suffixes on the others.
- `turn_filler_sources` string, default spell,number — comma-separated tokens naming which deliberate waits earn a backchannel from `languages[].turn_fillers` (https://signalwire.com/docs/swml/reference/calling/ai/languages.md), or `multilingual.turn_fillers` (https://signalwire.com/docs/swml/reference/calling/ai/multilingual.md) in multilingual mode. A wait = agent holds off answering because the caller isn't finished; the token names why. Tokens:
  - `spell` — caller is spelling something out
  - `number` — caller is reading out digits
  - `text` — wording suggests caller is mid-sentence
  - `acoustic` — audio suggests caller is mid-sentence
  - `veto` — any of the above
  - Default answers only `spell` and `number` (pauses are expected and can't be shortened). A backchannel during `text` or `acoustic` usually talks over a caller still going, so give either its own delay with a `<token>:<ms>` suffix rather than listing it bare, e.g. `spell,number,text:1200`. Tokens matched whole and case-insensitively; a space after a comma is fine. Unknown tokens match no wait and nothing is validated: a misspelling silently leaves the agent with no backchannels at all.
- `vad_config` string — Silero VAD settings; format `threshold` or `threshold:frame_ms`. threshold `0`–`100` (sensitivity); optional frame_ms `16`–`40` (analysis frame duration, ms).

## debug_webhook_url callback

Diagnostic feed for an in-progress call: every agent step (speech recognized, model called, tool invoked, context switched, error hit) is posted to `debug_webhook_url` as it happens. Usable for post-hoc diagnosis or reacting live (e.g. paging a supervisor).

Each request carries `call_info` plus one or more event properties, where the property name is the event. One moment can produce several: evaluating a `data_map` webhook (https://signalwire.com/docs/swml/reference/calling/ai/swaig/functions/data-map.md) sends `webhook`, `input`, `output`, `error_keys`, and `match` together. Handle the properties you recognize and ignore the rest; the set grows over time.

Full field reference: https://signalwire.com/docs/apis/rest/webhooks/ai-debug-webhook.md. When to use the debug stream vs. the post-prompt report: https://signalwire.com/docs/platform/ai/analytics.md
