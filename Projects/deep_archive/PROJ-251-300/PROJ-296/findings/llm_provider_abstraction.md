# LLM Provider Abstraction Layer

## Context
QA Session 20260426_083959 raised the need for an LLM-generated race
description on the Race Setup screen. Conversation expanded the scope:
LLMs are also planned for diplomacy ("emails between empires per turn")
and possibly other systems later. The user wants an abstraction so the
underlying model can be swapped (DeepSeek today, OpenAI/Anthropic/local
tomorrow) without touching consumer code.

This project is the **foundation** — the consumer-side work for race
descriptions lives in a separate triage doc
(`race_description_generation.md`).

## User Decisions (locked in during triage)

| Decision | Value |
|---|---|
| API shape | OpenAI-chat-completion-compatible (messages: role + content) |
| Streaming | NOT required (turn-based diplomacy, no real-time UX) |
| Tool/function calling | Not required for v1 |
| Secret storage | Environment variable only (`DEEPSEEK_API_KEY`). Single developer, early dev. Keyring/UI deferred. |
| First provider | DeepSeek |
| Future providers | OpenAI, Anthropic, Google Gemini, local (llama.cpp / ollama) |

## Code Investigation Findings
- Greenfield — zero existing LLM integration in the codebase. No
  `anthropic`, `openai`, `api_key`, `llm`, or `gpt` references in
  `game/`. Confirmed via Explore agent on 2026-04-26.
- Settings infrastructure at
  [game/ui/services/game_settings.py](../../game/ui/services/game_settings.py)
  exists but currently stores only `background_brightness`. Not needed
  for v1 (env var only).
- Pygame is single-threaded — any LLM call must run on a worker thread
  with a polling/callback pattern back to the UI.

## Scope (v1)
1. **Provider interface** in `game/services/llm/` (or `game/core/llm/`
   if cross-layer use is needed for diplomacy AI):
   - `LLMProvider` protocol with one method:
     `complete(messages: list[Message], **opts) -> CompletionResult`
   - `Message = {role: 'system'|'user'|'assistant', content: str}`
   - `CompletionResult = {text: str, usage: TokenUsage, model: str}`
   - Synchronous; threading is the caller's responsibility (with a
     thin helper for the common pattern).

2. **DeepSeek implementation** — concrete provider that POSTs to
   DeepSeek's chat completion endpoint, reads `DEEPSEEK_API_KEY` from
   the environment, returns a `CompletionResult`. Uses `requests` (or
   `httpx`).

3. **Provider registry / selection** — module-level
   `get_default_llm_provider()` (mirrors the ApplicationContext pattern
   from PROJ-258). Reads provider name from env (e.g. `LLM_PROVIDER=deepseek`,
   default `"deepseek"`).

4. **Threading helper** — `run_in_background(provider, messages,
   on_complete, on_error)` that wraps a provider call in a thread and
   marshals the result back via a queue the UI polls each frame. Cancel
   support included.

5. **Error handling** — typed exceptions: `LLMConfigError` (no key /
   bad provider), `LLMNetworkError` (timeout / connection),
   `LLMResponseError` (4xx/5xx from provider), `LLMCancelled`. UI
   catches and displays.

6. **Tests** — provider protocol mock; DeepSeek implementation tested
   against a stubbed HTTP transport (no network calls in test); thread
   helper tested for cancellation and ordering.

## Out of Scope (v1)
- Streaming responses
- Tool/function calling
- In-game Settings UI for the API key (env var only)
- OS keyring integration
- Cost estimation / token-counting UI
- Multi-key rotation, rate limiting beyond simple retry
- Local model integration (ollama / llama.cpp) — provider interface
  is designed to support it, but no concrete implementation in v1

## Scope Notes
This is project-sized rather than feature-sized because:
- It introduces a new top-level service category (`llm/`) that
  multiple game systems will depend on
- It crosses the network boundary for the first time in the codebase
  (security, error-handling, threading patterns to be established)
- Decisions made here (API shape, threading model, error taxonomy)
  will be load-bearing for diplomacy and any future LLM consumers
- Worth a phased plan with explicit design doc rather than ad-hoc
  feature work
