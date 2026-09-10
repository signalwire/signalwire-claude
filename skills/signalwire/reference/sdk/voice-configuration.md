# Voice and TTS Configuration Reference

Complete reference for voice configuration, TTS engines, languages, fillers, and pronunciation rules.

## Import

```python
from signalwire_agents import AgentBase
```

## Language Configuration

### add_language()

Add a language with voice configuration to the agent.

```python
def add_language(
    self,
    name: str,
    code: str,
    voice: str,
    speech_fillers: Optional[List[str]] = None,
    function_fillers: Optional[List[str]] = None,
    engine: Optional[str] = None,
    model: Optional[str] = None
) -> 'AgentBase'
```

**Parameters:**
- `name` - Human-readable language name (e.g., "English", "Spanish")
- `code` - Language code (e.g., "en-US", "es-MX", "fr-FR")
- `voice` - TTS voice identifier (see formats below)
- `speech_fillers` - Phrases for natural speech pauses
- `function_fillers` - Phrases while executing functions
- `engine` - Explicit TTS engine name
- `model` - Explicit TTS model name

**Returns:** Self for method chaining

### Voice Format Options

#### Simple Voice Name
```python
# Resolves against elevenlabs (since 2026-08-13) - NOT the engine you may expect.
# Prefer the combined format below.
agent.add_language("English", "en-US", "mark")
```

#### Combined Format: engine.voice:model
```python
agent.add_language("English", "en-US", "elevenlabs.josh:eleven_turbo_v2_5")
agent.add_language("English", "en-US", "rime.spore:coda")
```

#### Explicit Parameters
```python
agent.add_language(
    "English",
    "en-US",
    "josh",
    engine="elevenlabs",
    model="eleven_turbo_v2_5"
)
```

### set_languages()

Set all language configurations at once.

```python
def set_languages(self, languages: List[Dict[str, Any]]) -> 'AgentBase'
```

**Example:**
```python
agent.set_languages([
    {
        "name": "English",
        "code": "en-US",
        "voice": "spore",
        "engine": "rime",
        "speech_fillers": ["um", "let me think"],
        "function_fillers": ["one moment", "checking"]
    },
    {
        "name": "Spanish",
        "code": "es-MX",
        "voice": "es-MX-Neural2-A",
        "speech_fillers": ["ehm", "déjame pensar"],
        "function_fillers": ["un momento", "verificando"]
    }
])
```

## TTS Engines and Voices

### The Default Voice

An AI agent that sets no `voice` speaks with **ElevenLabs "Mark"** — compiled defaults are engine `elevenlabs`, voice `mark`. Mark is included in the regular AI agent price; it is not a premium add-on.

Two separate changes produced this, and they are easy to conflate:

| Date | Change |
|------|--------|
| 2026-08-13 | A voice string with **no engine prefix** resolves against `elevenlabs` instead of `gcloud`. |
| 2026-09-05 | An agent specifying **no `voice` at all** now gets ElevenLabs "Mark". |

Sources: `/docs/platform/changelog/2026/8/13`, `/docs/platform/changelog/2026/9/5`.

**Always declare the engine explicitly.** The default has moved twice in two months, and an agent that relies on it will change voice without a deploy.

**This default is for AI agents.** The `play` and `prompt` verbs resolve voices through a separate mapping table and land elsewhere — do not carry this answer over to them.

### Available Engines

Voice specs take the form **`engine.voice:model`** — engine and voice required, model optional and not supported by every engine. The format is case-insensitive.

Each engine has its own page carrying its voice list, supported languages, and per-engine parameters. **Fetch that page rather than trusting any voice list written down here** — catalogs change often.

| Identifier | Engine | Page under `/docs/platform/voice/tts/` |
|------------|--------|----------------------------------------|
| `amazon` | Amazon Polly | `amazon-polly` |
| `azure` | Azure | `azure` |
| `cartesia` | Cartesia | `cartesia` |
| `deepgram` | Deepgram | `deepgram` |
| `elevenlabs` | ElevenLabs — **default for AI agents** | `elevenlabs` |
| `fish` | Fish Audio | `fish` |
| `gcloud` | Google Cloud | `gcloud` |
| `grok` | Grok (xAI) | `grok` |
| `groq-tts` | Groq | `groq-tts` |
| `inworld` | Inworld | `inworld` |
| `minimax` | MiniMax | `minimax` |
| `mistral` | Mistral | `mistral` |
| `openai` | OpenAI | `openai` |
| `rime` | Rime | `rime` |
| `smallest` | Smallest.ai | `smallest` |
| `speechify` | Speechify | `speechify` |

**The Amazon identifier is `amazon`, not `polly`.**

### Renames and Deprecations

Older code will hit these (source: `/docs/platform/changelog/2026/8/5`):

- **`playai-turbo` is now `groq-tts`.** Groq retired PlayAI in December 2025 and repointed the engine at Canopy Labs' Orpheus, defaulting to `canopylabs/orpheus-v1-english`. Arabic is available via the `canopylabs/orpheus-arabic-saudi` model, shorthand `arabic`.
- **Rime's `arcana` model is deprecated.** Applications invoking it fall back to `coda`, which shares voice names. `coda` now accepts the same sampling parameters as other Rime models: `repetition_penalty`, `temperature`, `top_p`, `max_tokens`.

### Inline Expression Tags Differ by Engine

**These are not interchangeable.** Using the wrong syntax puts literal bracket text into the audio.

| Engine | Syntax | Notes |
|--------|--------|-------|
| ElevenLabs (`eleven_v3`) | `[square]` | Open vocabulary — emotions, reactions, delivery, even accents |
| Fish | `[square]` and `(paren)` | Square for free-form direction, parens for paralanguage: `(break)`, `(laugh)`, `(sigh)` |
| Inworld | `[square]` | One turn-initial emotion tag plus inline sounds. English only, marked experimental |
| Groq | `<angle>` | `<laugh>`, `<sigh>`, `<cough>` … |
| Cartesia | `[laughter]`, `[laughs]` | Broader emotion is a parameter, not a tag |
| Rime | **none**, except `spell()` | No SSML, no `<break>`, no emotion tags |
| Azure | SSML | |
| MiniMax | — | Has an `emotion` parameter instead |
| All others | — | No inline markup |

Per-language ElevenLabs parameters can be set in the `languages` block — worked example at `/docs/swml/reference/calling/ai/languages`.

### Voice Format Examples

| Engine | Example spec |
|--------|--------------|
| `elevenlabs` | `elevenlabs.mark`, `elevenlabs.josh:eleven_turbo_v2_5` |
| `rime` | `rime.spore`, `rime.spore:coda` |
| `gcloud` | `gcloud.en-US-Neural2-A` |
| `azure` | `azure.en-US-JennyNeural` |
| `amazon` | `amazon.Matthew`, `amazon.Joanna` |
| `cartesia` | `cartesia.default` |
| `deepgram` | `deepgram.aura-asteria-en` |
| `openai` | `openai.nova`, `openai.alloy` |

### Rime Voices

```python
agent.add_language("English", "en-US", "rime.spore")
agent.add_language("English", "en-US", "rime.marsh")

# With model specification
agent.add_language("English", "en-US", "rime.spore:coda")
```

### ElevenLabs Voices (Default Engine)

```python
# Mark is the default voice - naming it explicitly pins it against future changes
agent.add_language("English", "en-US", "elevenlabs.mark")

# ElevenLabs with model
agent.add_language("English", "en-US", "elevenlabs.josh:eleven_turbo_v2_5")
agent.add_language("English", "en-US", "elevenlabs.rachel:eleven_multilingual_v2")

# Or explicit parameters
agent.add_language(
    "English", "en-US", "josh",
    engine="elevenlabs",
    model="eleven_turbo_v2_5"
)
```

### Google Cloud Voices

```python
agent.add_language("English", "en-US", "gcloud.en-US-Neural2-F")
agent.add_language("English", "en-US", "gcloud.en-US-Wavenet-A")
```

### Azure Voices

```python
agent.add_language("English", "en-US", "azure.en-US-JennyNeural")
agent.add_language("English", "en-US", "azure.en-US-GuyNeural")
```

### Amazon Polly Voices

```python
agent.add_language("English", "en-US", "amazon.Matthew")
agent.add_language("English", "en-US", "amazon.Joanna")
```

### OpenAI Voices

```python
agent.add_language("English", "en-US", "openai.nova")
agent.add_language("English", "en-US", "openai.alloy")
agent.add_language("English", "en-US", "openai.echo")
```

## Fillers Configuration

Fillers are phrases the AI says during pauses or while processing.

### Speech Fillers vs Function Fillers

- **Speech fillers**: Used during natural speech pauses ("um", "let me think")
- **Function fillers**: Used while executing SWAIG functions ("one moment", "checking")

```python
agent.add_language(
    "English",
    "en-US",
    "rime.spore",
    speech_fillers=["um", "well", "let me think about that"],
    function_fillers=["one moment please", "let me check that", "just a second"]
)
```

### Internal Fillers (Per-Function)

Set fillers for specific internal/native functions:

```python
# Set all internal fillers at once
agent.set_internal_fillers({
    "next_step": {
        "en-US": ["Moving to the next step...", "Great, let's continue..."],
        "es": ["Pasando al siguiente paso...", "Excelente, continuemos..."]
    },
    "check_time": {
        "en-US": ["Let me check the time...", "Getting the current time..."]
    }
})

# Or add individual fillers
agent.add_internal_filler("next_step", "en-US", ["Moving on...", "Let's continue..."])
agent.add_internal_filler("check_time", "fr", ["Laissez-moi vérifier l'heure..."])
```

### Tool-Specific Fillers

When defining tools, you can specify fillers:

```python
@AgentBase.tool(
    name="lookup_order",
    description="Look up an order status",
    parameters={"order_id": {"type": "string", "description": "Order ID"}},
    fillers=["Let me look that up", "Checking on that order"]
)
def lookup_order(self, args, raw_data):
    # ...
```

Or with `define_tool()`:

```python
self.define_tool(
    name="search_database",
    description="Search the database",
    parameters={"query": {"type": "string"}},
    handler=self.handle_search,
    fillers=["Searching...", "Let me find that"],
    wait_file="https://example.com/searching.mp3",
    wait_file_loops=3
)
```

## Pronunciation Rules

### add_pronunciation()

Add rules to help the AI pronounce words correctly.

```python
def add_pronunciation(
    self,
    replace: str,
    with_text: str,
    ignore_case: bool = False
) -> 'AgentBase'
```

**Parameters:**
- `replace` - The expression to replace
- `with_text` - The phonetic spelling to use
- `ignore_case` - Whether to ignore case when matching

**Example:**
```python
agent.add_pronunciation("API", "A P I")
agent.add_pronunciation("SQL", "sequel")
agent.add_pronunciation("GIF", "jiff")
agent.add_pronunciation("SWML", "swim-el")
agent.add_pronunciation("SignalWire", "Signal Wire", ignore_case=True)
```

### set_pronunciations()

Set all pronunciation rules at once:

```python
agent.set_pronunciations([
    {"replace": "API", "with": "A P I"},
    {"replace": "SQL", "with": "sequel"},
    {"replace": "CLI", "with": "C L I", "ignore_case": True}
])
```

## Speech Recognition Hints

### add_hints()

Add hints to improve speech recognition accuracy.

```python
agent.add_hints(["SignalWire", "SWML", "SWAIG", "WebRTC"])
agent.add_hints(["account number", "routing number", "checking", "savings"])
```

### add_pattern_hint()

Add complex hints with pattern matching:

```python
def add_pattern_hint(
    self,
    hint: str,
    pattern: str,
    replace: str,
    ignore_case: bool = False
) -> 'AgentBase'
```

**Example:**
```python
agent.add_pattern_hint(
    hint="order number",
    pattern=r"order\s*#?\s*(\d+)",
    replace="order number $1",
    ignore_case=True
)
```

## LLM Parameters

### set_prompt_llm_params()

Set LLM parameters for the main conversation.

```python
agent.set_prompt_llm_params(
    model="gpt-4o-mini",      # AI model to use
    temperature=0.7,          # Randomness (0-2)
    top_p=0.9,                # Nucleus sampling
    barge_confidence=0.6,     # Interruption confidence threshold
    presence_penalty=0.0,     # Topic diversity
    frequency_penalty=0.0     # Repetition reduction
)
```

**Available Models:**
- `gpt-4o-mini` (default)
- `gpt-4.1-mini`
- `gpt-4.1-nano`
- `nova-micro` (Amazon)
- `nova-lite` (Amazon)
- `qwen3-235b-A22b-instruct`

### set_post_prompt_llm_params()

Set LLM parameters for the post-prompt (summary generation).

```python
agent.set_post_prompt_llm_params(
    model="gpt-4o-mini",
    temperature=0.5,  # Lower for more deterministic summaries
    top_p=0.9
)
```

## Complete Example

```python
#!/usr/bin/env python3
from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult


class MultilingualAgent(AgentBase):
    """Agent with advanced voice configuration."""

    def __init__(self):
        super().__init__(name="multilingual", port=3000)

        # Primary language with ElevenLabs
        self.add_language(
            "English",
            "en-US",
            "elevenlabs.josh:eleven_turbo_v2_5",
            speech_fillers=["um", "well", "let me think"],
            function_fillers=["one moment", "let me check"]
        )

        # Secondary language with Google
        self.add_language(
            "Spanish",
            "es-MX",
            "gcloud.es-MX-Neural2-A",
            speech_fillers=["ehm", "bueno", "déjame pensar"],
            function_fillers=["un momento", "verificando"]
        )

        # Pronunciation rules
        self.add_pronunciation("API", "A P I")
        self.add_pronunciation("SignalWire", "Signal Wire")
        self.add_pronunciation("SWML", "swim-el")

        # Speech recognition hints
        self.add_hints(["SignalWire", "account number", "order status"])

        # Internal fillers for native functions
        self.add_internal_filler("check_time", "en-US", ["Let me check the time..."])
        self.add_internal_filler("check_time", "es-MX", ["Déjame ver la hora..."])

        # LLM parameters
        self.set_prompt_llm_params(
            model="gpt-4o-mini",
            temperature=0.7,
            barge_confidence=0.6
        )

        # Build prompt
        self.prompt_add_section("Role", "You are a helpful multilingual assistant.")

    @AgentBase.tool(
        name="lookup_info",
        description="Look up information",
        parameters={"query": {"type": "string", "description": "What to look up"}},
        fillers=["Let me look that up for you", "Searching now"]
    )
    def lookup_info(self, args, raw_data):
        return SwaigFunctionResult(f"Found information for: {args.get('query')}")


if __name__ == "__main__":
    agent = MultilingualAgent()
    agent.run()
```

## See Also

- [Agent Base Reference](agent-base.md) - Complete AgentBase documentation
- [AI Parameters](agent-base.md#ai-configuration-methods-from-aiconfigmixin) - Speech timeout settings
- [SWAIG Functions Reference](swaig-functions.md) - Function fillers and wait files
