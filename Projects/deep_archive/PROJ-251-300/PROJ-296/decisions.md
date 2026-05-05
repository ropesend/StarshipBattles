# PROJ-296: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | Starting point for LLM Service Foundation |
| 2026-04-26 | **Layer placement: new top-level `game/services/`** | UI and AI both consume LLM (race description, diplomacy). Putting it in either layer inverts the dependency. `game/core/` is "stdlib only" by convention — adding `requests` violates that. New `services/` layer between Engine and Core, deps on Core only, all other layers may import it. |
| 2026-04-26 | **API shape: OpenAI-chat-completion-compatible** (messages with role + content) | De facto standard supported by DeepSeek/OpenAI/Anthropic/Gemini natively and llama.cpp/ollama via shims. Cheapest forward-compat path for swapping providers later. |
| 2026-04-26 | **Streaming: NOT in v1** | First two known consumers (race description, diplomacy "emails") are turn-based, not real-time. Add `complete_stream()` later when a real-time use case appears. |
| 2026-04-26 | **Tool/function calling: NOT in v1** but `Role` enum includes `'tool'` | Forward-compat costs nothing in the type; v1 simply doesn't emit/consume `tool` messages. |
| 2026-04-26 | **Secret storage: env var only (`DEEPSEEK_API_KEY`)** | Single developer, early dev. Keyring/UI deferred until shipping to non-dev users. |
| 2026-04-26 | **First provider: DeepSeek** | User stated cost-effective; capable; will acquire key independently. |
| 2026-04-26 | **HTTP library: `requests`** (not `httpx`) | sync-only is fine for v1; ubiquitous; already transitively present via `google-api-core`. Explicit pin in `requirements.txt` is just clarification, not new tree bloat. |
| 2026-04-26 | **Threading helper INCLUDED in v1** | Future consumers shouldn't reinvent. Contract is small and well-defined. Without it, the first consumer (race description) has to invent the pattern. |
| 2026-04-26 | **Cancellation: logical (callback dropped), not physical (HTTP completes in background)** | Standard pattern for `requests`-based clients. Cost of discarded response is negligible (a few cents at most). The user-facing behavior — callback doesn't fire, UI moves on — is identical to physical cancellation. |
| 2026-04-26 | **`MAX_CONCURRENT_CALLS = 3` (configurable on `LLMConfig`)** | Future overlap of foreground race-description + background diplomacy. Stored on `LLMConfig` so it's tunable without code changes. User explicitly noted "the system should be extensible". |
| 2026-04-26 | **Retry policy: exponential backoff on 5xx only, max 2 retries; never retry 429** | Server errors are transient; rate-limit (429) is a clear back-off signal that auto-retry would worsen. Consumer sees `LLMRateLimited` exception immediately. |
| 2026-04-26 | **`get_default_llm_provider()` returns `None` when unconfigured** | Deferred validation pattern. Consumer checks `if provider:` before showing the UI affordance (e.g., "Generate Description" button). Better UX than raising `LLMConfigError` at app startup. |
| 2026-04-26 | **API key read from `os.environ` per request, never stored on instance** | Defense in depth. Removes a leak vector (instance-var dump in crash logs, `repr()`, exception context). Trivial perf cost. |
| 2026-04-26 | **Naming: `LLMProviderFactory`** (not "registry/selector") | Matches existing convention: `AIControllerFactory`, `ShipFactory`, `PanelFactory` (Pattern Scout finding). |
| 2026-04-26 | **Add `LLMConfig` class to `game/core/config.py`** | Mirrors `PhysicsConfig`/`AIConfig`/`BattleTuning`. Avoids magic numbers scattered through provider/threading code (Pattern Scout finding). |
| 2026-04-26 | **Skip TypeGuard on `LLMProvider`** | No polymorphic dispatch site. TypeGuards are valuable when multiple impls are dispatched in mixed object graphs (`IFleet`, `IStarSystem`); LLM has one provider instance resolved at startup (Pattern Scout finding). |
| 2026-04-26 | **Exceptions live in `game/core/exceptions.py`** (NOT in `game/services/llm/exceptions.py`) | Existing convention; consistent import surface for the codebase (API Reviewer finding). Use `L` error code prefix. |
| 2026-04-26 | **Skip Serializable Protocol for v1** | No persistence of LLM messages or completions in v1. Defer to v2 if conversation history needs saving. |
| 2026-04-26 | **Worker threads are non-daemon; shutdown hook joins with 5s timeout** | Daemon threads can die mid-write. Non-daemon + bounded join means clean shutdown without hanging the game (Risk Assessor finding). |
| 2026-04-26 | **Per-call request_id versioning to handle cancel + immediate-restart races** | Stale results from a cancelled call cannot overwrite the current call's result (Risk Assessor finding). |
| 2026-04-26 | **All `LLMBackgroundCall` shared state guarded by `threading.Lock`** | Multiple frames poll the same call concurrently; lock prevents torn reads (Risk Assessor finding). |
| 2026-04-26 | **Session-scoped autouse pytest fixture monkeypatches `requests.post`** to RAISE | Guarantees no test ever escapes to the real network. Tests must explicitly set up a mock response (Risk Assessor + Test Impact findings). |
| 2026-04-26 | **HTTP mocking: plain `unittest.mock.patch`** (not `responses` or `requests-mock`) | Matches existing codebase style; no new test deps (Test Impact Analyst finding). |
| 2026-04-26 | **Threading helper warrants new Pattern #28 "Background Service Call"** in `docs/02_PATTERNS.md` | Genuinely new pattern not covered by existing 27. Future services with unbounded latency (LLM, future cloud sync, etc.) will reuse it (Pattern Scout finding). |
| 2026-04-26 | **`LLMProvider.complete()` signature: explicit primary kwargs + `**opts` escape hatch** | Type-safe for the OpenAI-compatible knobs every provider supports (model, temp, max_tokens, timeout, cancel_token); `**opts` for provider-specific extras (DeepSeek `top_p`, Anthropic `metadata`) (API Reviewer finding). |
| 2026-04-26 | **`CompletionResult` includes `finish_reason`, `latency_seconds`, `provider`, `request_id`** | Beyond the minimal `text/usage/model`. `finish_reason` lets UI distinguish "done" from "truncated"; `latency_seconds` for observability; `request_id` for support tracing (API Reviewer finding). |
| 2026-04-26 | **Provider's `__repr__` REDACTS the API key entirely** | `repr(provider)` is invoked in many debug contexts (logs, exception printing, REPL); never let the key leak through it (Security Reviewer finding). |
| 2026-04-26 | **Logging guardrails: never log Authorization header, request body, response body, message content** | Each enumerated specifically in design.md. Forbidden in any log line at any level (Security Reviewer finding). |
| 2026-04-26 | **Network: SSL on (default), `timeout=(5, 30)` connect/read, custom User-Agent** | Hardened defaults. SSL never disabled. `User-Agent: starship-battles-llm/1.0` for API citizenship (Security Reviewer finding). |
| 2026-04-26 | **Phase 1-7 ordering with each phase independently testable** | User asked to err on the side of extra phases. Splits foundation/contract/factory/impl/threading/wiring/docs into discrete, sequential pieces. Phase 4 depends on Phase 2 (provider impl needs DTOs); Phase 6 depends on Phases 1-5. |
