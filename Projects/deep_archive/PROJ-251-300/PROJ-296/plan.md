# PROJ-296: LLM Service Foundation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-296` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-296 [phase]` before stopping
> - Update Current State with specific handoff context

---

## Quick Status

| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Exceptions + Error Codes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. DTOs + Protocol + LLMConfig | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. LLMProviderFactory | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. DeepSeek Implementation | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Threading Helper | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. ApplicationContext Wiring | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Documentation Closeout | Complete | [phase_7_checklist.md](phase_7_checklist.md) |

---

## Current State

**Last Updated:** 2026-04-26 19:00
**Active Phase:** Complete — awaiting user verification
**Last Action:** All 7 phases implemented and tested. Final sharded suite: **15273/15273 passing** (+106 tests over 15167 baseline, 0 regressions). Documentation updated across `docs/01_ARCHITECTURE.md` (new `services/` layer), `docs/02_PATTERNS.md` (Pattern #28 Background Service Call), `docs/04_SERVICES.md` (LLM service entry), `docs/05_ERROR_HANDLING.md` (LLM exception branch + L codes). `tests/regression/test_services_layer_rule.py` enforces the layer rule going forward.
**Next Action:** **USER VERIFICATION** — run Phase 7 Task 7.7 manual smoke (one item with `DEEPSEEK_API_KEY` UNSET to confirm graceful degradation, then optional end-to-end with a real key). After verification, archive via Protocol 03.
**Blockers:** None — implementation done.
**Context for Next Agent:**
- Pre-existing test failures (NOT from PROJ-296): 3 import errors in `tests/unit/ai/test_ai_protocols.py`, `tests/unit/ai/test_behavior_units.py`, `tests/unit/strategy/engine/test_build_order_command_handler.py` (when run via `pytest tests/unit/`). The sharded runner (which is the canonical CI path) doesn't hit them. Verified pre-existing via `git stash`.
- This is the **foundation** project — no existing consumers wired. Race description generation triage at [Projects/Triage/race_description_generation.md](../../Triage/race_description_generation.md) becomes its own PROJ-XX once this is verified. Diplomacy is the second known future consumer.
- Future provider additions: drop `game/services/llm/<name>.py` implementing `LLMProvider`, end with `register_provider("<name>", <Class>)`, add to package `__init__.py` side-effect imports. The dispatch dict `_PROVIDERS` is data-driven — no factory edits needed.
- Security note: API key is read from `os.environ` per-request (never cached on instance). `__repr__` redacts. Logs and exception context omit the key, request body, response body, and message contents. The `_block_real_http` autouse fixture in `tests/conftest.py` guarantees no test escapes to the real network.

---

## Overview

Add an LLM provider abstraction layer to the codebase as a **new top-level `game/services/` layer** (the first member of that layer). Provides:

- A pluggable `LLMProvider` Protocol that hides which model/provider is in use
- A concrete `DeepSeekProvider` implementation as the first provider
- A threading helper for non-blocking calls from the pygame UI
- ApplicationContext integration mirroring existing services
- Foundation for diplomacy AI, race description generation, and any future LLM consumers

---

## Goals

- **Pluggable**: swap DeepSeek for OpenAI / Anthropic / Gemini / local llama.cpp without touching consumer code
- **Non-blocking**: pygame UI never freezes on an LLM call; callers poll a background task and can cancel
- **Safe**: API key is never logged or persisted; tests cannot make real HTTP calls
- **Conventional**: follows existing patterns (ApplicationContext DI, exception hierarchy, error codes, logging)
- **Documented**: new `services/` layer formally added to the architecture docs

---

## Scope

### In Scope (v1)

- Protocol + DTOs (`Message`, `CompletionResult`, `TokenUsage`, `Role` enum)
- DeepSeek concrete provider
- `LLMProviderFactory` reading `LLM_PROVIDER` env var (default `"deepseek"`)
- `LLMBackgroundCall` threading helper with cancel + status + elapsed time
- `LLMConfig` class for tunable defaults (timeout, retries, max concurrent calls)
- `LLMException` branch + `L001`-`L006` error codes in `game/core/`
- ApplicationContext wiring + module-level `get_default_llm_provider()` accessor
- New `game/services/` layer rule documented in `docs/01_ARCHITECTURE.md`
- New Pattern #28 "Background Service Call" entry in `docs/02_PATTERNS.md`
- Autouse pytest fixture preventing real HTTP calls in tests

### Out of Scope (v1)

- Streaming responses
- Tool / function calling (but `Role` enum includes `'tool'` for forward compat)
- In-game Settings UI for the API key (env var only)
- OS keyring / encrypted secret storage
- Cost estimation / token-counting UI
- Local model integration (ollama / llama.cpp) — protocol supports it; no concrete impl
- Specific consumer UIs (race description, diplomacy) — separate projects
- Length limits on completions (consumer concern; varies per use case)

---

## Key Files

### New files (to be created)
| Component | File Path | Phase |
|-----------|-----------|-------|
| LLM Exception branch | `game/core/exceptions.py` (extend) | 1 |
| LLM Error codes | `game/core/error_codes.py` (extend) | 1 |
| LLM DTOs | `game/services/llm/types.py` | 2 |
| LLM Provider protocol | `game/services/llm/provider.py` | 2 |
| LLM Config | `game/core/config.py` (extend) | 2 |
| LLM Provider Factory | `game/services/llm/factory.py` | 3 |
| DeepSeek Provider | `game/services/llm/deepseek.py` | 4 |
| LLM Background Call | `game/services/llm/background.py` | 5 |
| Defaults + accessors | `game/services/llm/__init__.py` | 6 |
| Empty package marker | `game/services/__init__.py` | 2 |

### Modified files
| Component | File Path | Phase |
|-----------|-----------|-------|
| DI container | `game/context.py` | 6 |
| App shutdown hook | `game/app.py` | 5 |
| Test fixture | `tests/conftest.py` | 4 |
| Dependency pin | `requirements.txt` | 4 |
| Architecture docs | `docs/01_ARCHITECTURE.md` | 7 |
| Patterns docs | `docs/02_PATTERNS.md` (new Pattern #28) | 7 |
| Services docs | `docs/04_SERVICES.md` | 7 |
| Error handling docs | `docs/05_ERROR_HANDLING.md` | 7 |

### Triage findings
| Component | File Path |
|-----------|-----------|
| Original triage source | [findings/llm_provider_abstraction.md](findings/llm_provider_abstraction.md) |
| Phase A swarm reports | `.agent_reports/proj_296_phase_a/` (ephemeral) |
| Phase B swarm reports | `.agent_reports/proj_296_phase_b/` (ephemeral) |

---

## Decisions Log (summary; see [decisions.md](decisions.md) for full)

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Layer placement: new top-level `game/services/` | Cross-cutting (UI + AI both need it), `core/` is stdlib-only by convention |
| 2026-04-26 | API shape: OpenAI-chat-completion-compatible | De facto standard; supported by DeepSeek/OpenAI/Anthropic/Gemini/local |
| 2026-04-26 | Streaming: NOT in v1 | Diplomacy is turn-based "emails", not real-time |
| 2026-04-26 | Secret storage: env var only (`DEEPSEEK_API_KEY`) | Single developer, early dev. Keyring deferred. |
| 2026-04-26 | First provider: DeepSeek | Cost-effective, capable; user already plans to acquire key |
| 2026-04-26 | Threading helper INCLUDED in v1 | Future consumers shouldn't reinvent; small contract |
| 2026-04-26 | Cancellation: logical (callback dropped), not physical (HTTP completes in background) | Standard pattern; cost is negligible discarded response |
| 2026-04-26 | `MAX_CONCURRENT_CALLS = 3` (configurable on `LLMConfig`) | Future overlap of foreground race-description + background diplomacy |
| 2026-04-26 | Retry policy: 5xx only, max 2 retries; never retry 429 | Rate-limit is a clear back-off signal; consumer surfaces it |
| 2026-04-26 | `get_default_llm_provider()` returns None when unconfigured | Deferred validation: consumer checks before showing UI affordance |
| 2026-04-26 | API key read from `os.environ` per-request, never stored on instance | Defense in depth; removes a leak vector at trivial cost |
| 2026-04-26 | Naming: `LLMProviderFactory` (not "registry/selector") | Matches `AIControllerFactory`/`ShipFactory`/`PanelFactory` convention |
| 2026-04-26 | Skip TypeGuard on `LLMProvider` | No polymorphic dispatch site; not needed |
| 2026-04-26 | Exceptions live in `game/core/exceptions.py` | Existing convention; consistent import surface |

---

## Phases

### Phase 1: Exceptions + Error Codes [Simple]
**Status:** Complete
**Objective:** Establish the exception branch and error codes the rest of the project will raise. Pure additive change to `game/core/`. No behavior yet.

Tasks: see [phase_1_checklist.md](phase_1_checklist.md).

### Phase 2: DTOs + Protocol + LLMConfig [Medium]
**Status:** Complete
**Objective:** Define the contract — frozen dataclasses (`Message`, `CompletionResult`, `TokenUsage`), the `LLMProvider` Protocol, the `Role` enum, and the `LLMConfig` config class. Creates the new `game/services/llm/` package with empty `__init__.py`.

Tasks: see [phase_2_checklist.md](phase_2_checklist.md).

### Phase 3: LLMProviderFactory [Simple]
**Status:** Complete
**Objective:** Provider selection by env var. With a stub provider for tests. Returns `None` if no provider can be constructed (deferred validation pattern).

Tasks: see [phase_3_checklist.md](phase_3_checklist.md).

### Phase 4: DeepSeek Implementation [Medium]
**Status:** Complete
**Objective:** First concrete provider. HTTP client with hardened defaults (SSL on, timeouts, custom UA, retry on 5xx). Adds `requests>=2.31.0` to `requirements.txt`. Adds session-scoped autouse fixture preventing real HTTP calls in tests.

Tasks: see [phase_4_checklist.md](phase_4_checklist.md).

### Phase 5: Threading Helper [Medium]
**Status:** Complete
**Objective:** `LLMBackgroundCall` class — spawns worker thread, exposes status / result / error / elapsed_seconds, supports cancel, enforces `MAX_CONCURRENT_CALLS`. Adds shutdown-hook to `game/app.py` joining workers with 5s timeout before `pygame.quit()`.

Tasks: see [phase_5_checklist.md](phase_5_checklist.md).

### Phase 6: ApplicationContext Wiring [Simple]
**Status:** Complete
**Objective:** Wire LLM provider into the DI container following the established pattern. Module-level `_default_llm_provider` slot + `get_default_llm_provider()` / `set_default_llm_provider()` accessors. 5 specific edits to `game/context.py`. Update 1 test file.

Tasks: see [phase_6_checklist.md](phase_6_checklist.md).

### Phase 7: Documentation Closeout [Simple]
**Status:** Complete
**Objective:** Add the new `services/` layer to `docs/01_ARCHITECTURE.md` (diagram + dependency rules + package directory map). Add Pattern #28 "Background Service Call" to `docs/02_PATTERNS.md`. Add LLM service entry to `docs/04_SERVICES.md`. Add LLM exception branch + `L` codes to `docs/05_ERROR_HANDLING.md`. Run full sharded suite, confirm baseline + new tests pass.

Tasks: see [phase_7_checklist.md](phase_7_checklist.md).

---

## Verification Checklist

### Project Start (REQUIRED, completed)
- [x] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS, 05_ERROR_HANDLING)
- [x] Run full test suite: `python Tools/test_sharded/test_sharded.py` — 15167/15167 passing in 50.3s

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — affected tests pass
- [ ] Update phase status in this plan
- [ ] Update Current State

### Final Verification
- [ ] All Phase 1-7 tasks checked off
- [ ] Set `DEEPSEEK_API_KEY` env var locally and confirm `get_default_llm_provider()` returns a usable provider (manual smoke; no test should hit real API)
- [ ] With key UNSET: confirm `get_default_llm_provider()` returns `None` cleanly
- [ ] Run full sharded suite: `python Tools/test_sharded/test_sharded.py` — baseline + ~54 new tests pass
- [ ] All `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/04_SERVICES.md`, `docs/05_ERROR_HANDLING.md` updated
- [ ] User verified

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

---

## Completion Checklist
- [ ] All Phase 1-7 tasks checked off
- [ ] All tests passing (15167 + ~54 new = ~15221+)
- [ ] No accidental real HTTP calls in tests
- [ ] API key never logged
- [ ] Docs updated and consistent
- [ ] User verified
