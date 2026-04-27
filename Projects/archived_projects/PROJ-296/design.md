# PROJ-296: LLM Service Foundation — Design

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to [decisions.md](decisions.md).

---

## Architectural Rationale

### Layer placement: new top-level `game/services/`

This project introduces the **first member** of a new top-level `services/` layer. The layer sits **between Engine and Core** in the dependency hierarchy: it depends only on Core, and every other layer (Engine, Simulation, Research, Strategy, AI, UI) may depend on it.

**Why a new layer rather than tucking under existing ones:**

| Option | Why not |
|--------|---------|
| `game/core/llm/` | Core is "standard library only" by convention. Adding `requests` to Core violates that. |
| `game/llm/` outside hierarchy (like `context.py`) | `context.py` is the DI container itself; services are the *things being injected*. Conflating roles obscures intent. |
| Tuck under UI / Strategy / AI | Multiple layers consume LLM (UI for race description, AI for diplomacy). Putting it inside one inverts the dependency. |
| New top-level `game/services/` (chosen) | Cross-cutting infrastructure with clean dep rule (Core only); future services follow the same template. |

### Dependency hierarchy (post-PROJ-296)

```
┌──────────────────────────────────────────────────────────────┐
│  UI Layer          game/ui/, game/app.py                     │
├──────────────────────────────────────────────────────────────┤
│  AI Layer          game/ai/                                  │
├──────────────────────────────────────────────────────────────┤
│  Strategy Layer    game/strategy/                            │
├──────────────────────────────────────────────────────────────┤
│  Research Layer    game/research/                            │
├──────────────────────────────────────────────────────────────┤
│  Simulation Layer  game/simulation/                          │
├──────────────────────────────────────────────────────────────┤
│  Engine Layer      game/engine/                              │
├──────────────────────────────────────────────────────────────┤
│  Services Layer    game/services/   [NEW IN PROJ-296]        │
│  Cross-cutting infrastructure (LLM today)                    │
├──────────────────────────────────────────────────────────────┤
│  Core Layer        game/core/                                │
└──────────────────────────────────────────────────────────────┘
```

### What belongs in `game/services/`?

To prevent the new layer becoming a junk drawer, every service must satisfy ALL three:

1. **Depends only on `game/core/`** (and stdlib + third-party). Never imports from a domain layer.
2. **Used by 2+ other layers** (or has clear roadmap to be). Otherwise it belongs in the consuming layer.
3. **Has a documented protocol + at least one testable implementation.** No bare functions; no implicit globals.

A service that's only used by one layer belongs in that layer's own `services/` subpackage (e.g. `game/strategy/services/`, `game/ui/services/`).

---

## API Surface (final after Phase B review)

### `LLMProvider` Protocol

```python
@runtime_checkable
class LLMProvider(Protocol):
    """Pluggable LLM provider interface. Synchronous; threading is the caller's
    responsibility (see LLMBackgroundCall in background.py)."""

    def complete(
        self,
        messages: list[Message],
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout_seconds: Optional[float] = None,
        cancel_token: Optional[threading.Event] = None,
        **opts: Any,
    ) -> CompletionResult:
        """Send messages, get completion. Raises LLMException on failure."""
        ...
```

Notes:
- Explicit primary kwargs cover the OpenAI-compatible knobs that every provider supports.
- `**opts` is the escape hatch for provider-specific knobs (e.g. DeepSeek's `top_p` or Anthropic's `metadata`).
- `cancel_token` lives on the protocol because future providers may support actual interruption (HTTP/2 streaming, async transports). For now it's checked between retries only.
- All `Optional[...] = None` so callers fall back to `LLMConfig` defaults via the provider impl.

### DTOs

All frozen dataclasses in `game/services/llm/types.py`:

```python
class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"   # included for forward compat; v1 doesn't emit/consume

@dataclass(frozen=True)
class Message:
    role: Role
    content: str

@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cached_prompt_tokens: int = 0  # set when provider reports it

class FinishReason(str, Enum):
    STOP = "stop"
    LENGTH = "length"
    CANCELLED = "cancelled"
    ERROR = "error"

@dataclass(frozen=True)
class CompletionResult:
    text: str
    usage: TokenUsage
    model: str
    finish_reason: FinishReason
    latency_seconds: float
    provider: str            # e.g. "deepseek"
    request_id: Optional[str] # provider's request id if returned
```

### `LLMConfig` (in `game/core/config.py`)

```python
class LLMConfig:
    """Tunable defaults for the LLM service. All fields can be overridden
    per-call via complete()'s explicit kwargs."""

    DEFAULT_TIMEOUT_SECONDS: float = 60.0
    CONNECT_TIMEOUT_SECONDS: float = 5.0
    DEFAULT_MAX_TOKENS: int = 4096
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MODEL: str = "deepseek-chat"
    MAX_RETRIES_5XX: int = 2
    RETRY_BACKOFF_BASE_SECONDS: float = 1.0
    MAX_CONCURRENT_CALLS: int = 3
    USER_AGENT: str = "starship-battles-llm/1.0"
```

### Exception hierarchy (added to `game/core/exceptions.py`)

```
GameException
    └── LLMException
            ├── LLMConfigError       (L001 — no key / unknown provider)
            ├── LLMNetworkError      (L002 — connection / DNS / SSL / timeout)
            ├── LLMResponseError     (L003 — non-2xx response, malformed body)
            ├── LLMRateLimited       (L004 — 429 from provider)
            ├── LLMTimeoutError      (L005 — timeout)
            └── LLMCancelled         (L006 — cancelled via cancel_token)
```

Error codes use the `L` prefix (next free letter).

---

## Threading Model

### `LLMBackgroundCall`

A small wrapper that runs a provider's `complete()` on a `threading.Thread` and exposes status to the polling caller (typically a pygame screen's `update()` method).

```python
class CallStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"

class LLMBackgroundCall:
    def __init__(
        self,
        provider: LLMProvider,
        messages: list[Message],
        **complete_kwargs: Any,
    ) -> None: ...

    def start(self) -> None:
        """Spawn the worker thread. Idempotent."""

    def cancel(self) -> None:
        """Set the cancel event. Worker will be marked CANCELLED on completion;
        in-flight HTTP request will complete in background and be discarded."""

    @property
    def status(self) -> CallStatus: ...

    @property
    def result(self) -> Optional[CompletionResult]:
        """None until status == DONE."""

    @property
    def error(self) -> Optional[LLMException]:
        """None unless status == ERROR."""

    @property
    def elapsed_seconds(self) -> float:
        """Wall time since start(). Useful for "show retry dialog after 30s"
        consumer UX."""
```

### Concurrency safeguards

- All shared state guarded by an internal `threading.Lock`.
- A module-level **counter** of in-flight calls. `LLMBackgroundCall.start()` raises `LLMConfigError` if creating it would exceed `LLMConfig.MAX_CONCURRENT_CALLS`. Counter decrements on done/error/cancelled.
- Each call gets a monotonic `request_id` so that "cancel + new request" can't see stale results overwrite (the polling consumer compares the active id).
- Worker threads are spawned **non-daemon**. A shutdown hook in `game/app.py` joins all in-flight workers with a 5-second timeout before `pygame.quit()`. If the timeout elapses, log a warning and proceed (better than hanging the game on shutdown).

### Cancellation semantics

"Cancel" is **logical** (the consumer's callback never fires; the result is discarded) but **NOT physical** (the underlying HTTP call may complete in the background). This is the standard pattern for `requests`-based clients. The cost of a discarded response is at most a few cents.

---

## Security Model (per Security Reviewer findings)

### API key handling

- Key is read from `os.environ["DEEPSEEK_API_KEY"]` **on every request**, never cached on the provider instance.
- Provider's `__repr__` and `__str__` REDACT the key entirely.
- Exception `context` dicts may contain `model`, `endpoint`, `status_code`, `error_code`, `request_duration_ms` — but NEVER `request_body`, `response_body`, headers (including `Authorization`), or the key itself.
- The response body excerpt included in `LLMResponseError` is truncated to the first 200 chars and post-processed to scrub anything that looks like a token.

### Logging guardrails

| Level | What to log |
|-------|-------------|
| DEBUG | endpoint, model name, message count, prompt token count |
| INFO  | success: status, latency_ms, total tokens |
| WARNING | retryable failure (5xx) before retry |
| ERROR | terminal failure: status, error_code, latency_ms (NO body, NO content) |

Forbidden in any log line: the API key value, full request body, full response body, message contents, system prompts.

### Network hardening

- SSL verification ON (default; never `verify=False`)
- `timeout=(5, 30)` (connect, read) on every request
- Custom `User-Agent: starship-battles-llm/1.0` header
- Stateless `requests.post()` for v1 (sessions add complexity without measurable win at our request rate)

---

## Test Strategy

### Test directory layout (mirrors source, per `docs/03_CONVENTIONS.md` §4.1)

```
tests/unit/services/
└── llm/
    ├── conftest.py
    ├── test_types.py
    ├── test_provider_protocol.py
    ├── test_factory.py
    ├── test_deepseek.py
    ├── test_background.py
    └── test_config.py
```

Plus existing files extended:
- `tests/unit/core/test_exceptions.py` — add LLM branch tests
- `tests/unit/core/test_error_codes.py` — add `L*` code tests
- `tests/unit/core/test_application_context.py` — add LLM provider field test
- `tests/conftest.py` — add session-scoped autouse `_block_real_http` fixture

### Critical test fixtures

- **`_block_real_http` (autouse, session scope)** — monkeypatches `requests.post` and `requests.get` to raise `RuntimeError("real HTTP forbidden in tests; use mock_llm_response")`. Ensures no test ever escapes to the real network.
- **`mock_llm_response`** — accepts a dict shaped like DeepSeek's response, returns a `MagicMock` that the test injects as the `requests.post` side effect.
- **`mock_llm_provider`** — returns a fake `LLMProvider` whose `complete()` returns a configurable `CompletionResult`. For consumer tests.
- **`reset_llm_default_provider`** — clears the module-level `_default_llm_provider` before/after each test that touches it. Prevents shard-level cross-pollination.

### HTTP mocking strategy

Plain `unittest.mock.patch` on `requests.post`. Matches existing codebase style (no new test deps). Each Phase 4 test sets up the mock response, calls `provider.complete()`, asserts the call shape and parsed result.

### Estimated test count

| Phase | Tests | Notes |
|-------|-------|-------|
| 1     | ~12   | Exception branch, error code uniqueness, raise+context behavior |
| 2     | ~14   | DTO frozen-ness, Role enum, FinishReason enum, LLMConfig fields, Protocol satisfaction |
| 3     | ~6    | Factory env-var dispatch, fallback to None, unknown provider raises |
| 4     | ~12   | DeepSeek POST shape, parse success, parse error, retry on 5xx, no-retry on 429, timeout, key redaction in repr |
| 5     | ~13   | Status transitions, cancel semantics, concurrent-call limit, lock safety, elapsed_seconds, shutdown-hook |
| 6     | ~3    | ApplicationContext.create_production sets default; create_test override; get_default returns None when no key |
| 7     | 0     | Docs only; full sharded suite verification |
| **Total** | **~60** | Slight bump from the 54 estimated by Test Impact Analyst (added a few security-specific tests) |

Estimated test wall time impact: under 1 second on the 50.3s baseline.

---

## Future Extension Notes

### Adding a new provider (e.g. OpenAI, Anthropic, Gemini)

1. Create `game/services/llm/<provider>.py` implementing `LLMProvider`
2. Register it in `LLMProviderFactory._PROVIDERS` (a dict, not a hardcoded if/elif chain — see `docs/03_CONVENTIONS.md` §6.5)
3. Document the provider's specific `**opts` keys in its docstring
4. Add tests in `tests/unit/services/llm/test_<provider>.py`

### Adding a new consumer (e.g. diplomacy)

1. Inject `LLMProvider` via `ApplicationContext` or `get_default_llm_provider()`
2. Build a `list[Message]` for the prompt
3. Foreground UX (race description): wrap in `LLMBackgroundCall`, poll `status`/`elapsed_seconds` from the screen's `update()`, show "still working..." dialog after `LLMConfig.MAX_FOREGROUND_WAIT_SECONDS` (default 30s, consumer can override)
4. Background UX (diplomacy turn): call `provider.complete()` directly on a worker thread; no UI interaction

### When to swap to a streaming-capable provider design

If/when a real-time use case appears (live narration, interactive diplomacy chat), the `LLMProvider.complete()` signature is sync-only and would need a sibling `complete_stream()` method. Add it then; don't pre-emptively complicate the v1 API.

### When to upgrade secret storage

The env-var approach is fine for a single-developer game. Triggers to revisit:
- Multi-user shared install (unlikely for this game)
- Moving to a UI-driven workflow where typing the key in-game is preferable to setting an env var
- Ever shipping a build to a non-developer

For any of those, swap to the OS keyring via the `keyring` package + a thin adapter inside `DeepSeekProvider`. The change is local to the provider; consumers are unaffected.
