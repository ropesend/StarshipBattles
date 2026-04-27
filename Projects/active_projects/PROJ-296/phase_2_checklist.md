# Phase 2: DTOs + Protocol + LLMConfig [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-296 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Define the contract — frozen DTOs (`Message`, `CompletionResult`, `TokenUsage`, `Role`, `FinishReason`), the `LLMProvider` Protocol, and the `LLMConfig` config class. Creates the new `game/services/llm/` package. No concrete provider yet.

---

## Tasks

### Task 2.1: Create `game/services/` package [Simple]
**File:** `game/services/__init__.py` (NEW), `game/services/llm/__init__.py` (NEW, empty for now)
**Tests:** Smoke import test

- [ ] Create directory `game/services/`
- [ ] Create `game/services/__init__.py` with a one-line docstring describing the new layer
- [ ] Create `game/services/llm/__init__.py` (empty for now; populated in Phase 6)
- [ ] Write smoke test in `tests/unit/services/llm/test_package_imports.py`: `from game.services.llm import *` succeeds (will be empty until later phases)
- [ ] Add `tests/unit/services/__init__.py` and `tests/unit/services/llm/__init__.py`

**Notes:**

### Task 2.2: Add `LLMConfig` to `game/core/config.py` [Simple]
**File:** `game/core/config.py`
**Tests:** `pytest tests/unit/core/test_config.py`

- [ ] Write failing tests asserting all `LLMConfig` constants have expected types and values (per design.md)
- [ ] Add `LLMConfig` class after `BattleTuning` in `config.py`. Use the same plain-class style (NOT `@dataclass`) — see Pattern 12:
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
- [ ] Run tests, confirm pass
- [ ] Verify no existing config test breaks

**Notes:**

### Task 2.3: Create `Role`, `FinishReason`, `Message`, `TokenUsage`, `CompletionResult` DTOs [Medium]
**File:** `game/services/llm/types.py` (NEW)
**Tests:** `pytest tests/unit/services/llm/test_types.py`

- [ ] Write failing tests:
  - `Role` enum has exactly: SYSTEM, USER, ASSISTANT, TOOL
  - `FinishReason` enum has exactly: STOP, LENGTH, CANCELLED, ERROR
  - `Message` is frozen — `setattr` raises
  - `Message(role=..., content=...)` constructs correctly
  - `TokenUsage` has 4 fields with `cached_prompt_tokens` defaulting to 0
  - `CompletionResult` is frozen and has all 7 fields
  - All DTOs survive `dataclasses.asdict()` round-trip (sanity check)
- [ ] Implement `game/services/llm/types.py` per design.md spec
  - Use `from enum import Enum` and `class Role(str, Enum):` so values are JSON-friendly
  - Use `@dataclass(frozen=True)` for the 3 dataclasses
- [ ] Run tests, confirm all pass

**Notes:**

### Task 2.4: Create `LLMProvider` Protocol [Medium]
**File:** `game/services/llm/provider.py` (NEW)
**Tests:** `pytest tests/unit/services/llm/test_provider_protocol.py`

- [ ] Write failing tests:
  - `LLMProvider` is `@runtime_checkable`
  - A class with the right `complete()` signature passes `isinstance(obj, LLMProvider)`
  - A class missing `complete()` does NOT pass
  - The protocol's `complete` accepts the documented kwargs (use a `inspect.signature` assertion)
- [ ] Implement per design.md spec. Imports: `Protocol`, `runtime_checkable` from `typing`; `Optional`, `Any` from `typing`; `threading.Event`; `Message` and `CompletionResult` from `.types`
- [ ] Add module docstring referencing PROJ-296 and the design doc
- [ ] Run tests, confirm pass

**Notes:**

### Task 2.5: Update `game/services/llm/__init__.py` exports [Simple]
**File:** `game/services/llm/__init__.py`
**Tests:** `pytest tests/unit/services/llm/test_package_imports.py`

- [ ] Re-export from `__init__.py`:
  ```python
  from game.services.llm.types import (
      Role, FinishReason, Message, TokenUsage, CompletionResult,
  )
  from game.services.llm.provider import LLMProvider

  __all__ = [
      'Role', 'FinishReason', 'Message', 'TokenUsage', 'CompletionResult',
      'LLMProvider',
  ]
  ```
- [ ] Update smoke test to assert all 6 exports are accessible
- [ ] Run all tests in `tests/unit/services/llm/` — all green

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] ~14 new tests added across `test_types.py`, `test_provider_protocol.py`, `test_config.py`
- [ ] `pytest tests/unit/services/llm/ tests/unit/core/test_config.py` — all green
- [ ] No regression in any existing test
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to Phase 3
