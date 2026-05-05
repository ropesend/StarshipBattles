# Phase 2: DTOs + Protocol + LLMConfig [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-296 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Define the contract — frozen DTOs (`Message`, `CompletionResult`, `TokenUsage`, `Role`, `FinishReason`), the `LLMProvider` Protocol, and the `LLMConfig` config class. Creates the new `game/services/llm/` package. No concrete provider yet.

---

## Tasks

### Task 2.1: Create `game/services/` package [Simple]
**File:** `game/services/__init__.py` (NEW), `game/services/llm/__init__.py` (NEW, empty for now)
**Tests:** Smoke import test

- [x] Create directory `game/services/`
- [x] Create `game/services/__init__.py` with a one-line docstring describing the new layer
- [x] Create `game/services/llm/__init__.py` (empty for now; populated in Phase 6)
- [x] Write smoke test in `tests/unit/services/llm/test_package_imports.py`: `from game.services.llm import *` succeeds (will be empty until later phases)
- [x] Add `tests/unit/services/__init__.py` and `tests/unit/services/llm/__init__.py`

**Notes:** Added a third smoke test (`test_llm_package_exports_phase_2_symbols`) once Task 2.5 landed. 3 import-smoke tests pass.

### Task 2.2: Add `LLMConfig` to `game/core/config.py` [Simple]
**File:** `game/core/config.py`
**Tests:** `pytest tests/unit/core/test_config.py`

- [x] Write failing tests asserting all `LLMConfig` constants have expected types and values (per design.md)
- [x] Add `LLMConfig` class after `BattleTuning` in `config.py`. Use the same plain-class style (NOT `@dataclass`) — see Pattern 12:
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
- [x] Run tests, confirm pass
- [x] Verify no existing config test breaks

**Notes:** Added 3 tests in `TestLLMConfig` class — value/type assertions plus `is_dataclass` negative assertion to enforce Pattern 12. 5 config tests pass.

### Task 2.3: Create `Role`, `FinishReason`, `Message`, `TokenUsage`, `CompletionResult` DTOs [Medium]
**File:** `game/services/llm/types.py` (NEW)
**Tests:** `pytest tests/unit/services/llm/test_types.py`

- [x] Write failing tests:
  - `Role` enum has exactly: SYSTEM, USER, ASSISTANT, TOOL
  - `FinishReason` enum has exactly: STOP, LENGTH, CANCELLED, ERROR
  - `Message` is frozen — `setattr` raises
  - `Message(role=..., content=...)` constructs correctly
  - `TokenUsage` has 4 fields with `cached_prompt_tokens` defaulting to 0
  - `CompletionResult` is frozen and has all 7 fields
  - All DTOs survive `dataclasses.asdict()` round-trip (sanity check)
- [x] Implement `game/services/llm/types.py` per design.md spec
  - Use `from enum import Enum` and `class Role(str, Enum):` so values are JSON-friendly
  - Use `@dataclass(frozen=True)` for the 3 dataclasses
- [x] Run tests, confirm all pass

**Notes:** 14 type tests pass. `Role` and `FinishReason` use `(str, Enum)` mixin so values are JSON-friendly. Added a `request_id_can_be_none` test as a sanity check on the Optional default.

### Task 2.4: Create `LLMProvider` Protocol [Medium]
**File:** `game/services/llm/provider.py` (NEW)
**Tests:** `pytest tests/unit/services/llm/test_provider_protocol.py`

- [x] Write failing tests:
  - `LLMProvider` is `@runtime_checkable`
  - A class with the right `complete()` signature passes `isinstance(obj, LLMProvider)`
  - A class missing `complete()` does NOT pass
  - The protocol's `complete` accepts the documented kwargs (use a `inspect.signature` assertion)
- [x] Implement per design.md spec. Imports: `Protocol`, `runtime_checkable` from `typing`; `Optional`, `Any` from `typing`; `threading.Event`; `Message` and `CompletionResult` from `.types`
- [x] Add module docstring referencing PROJ-296 and the design doc
- [x] Run tests, confirm pass

**Notes:** 3 protocol tests pass. The signature-introspection test uses `inspect.Parameter.KEYWORD_ONLY` + default-value checks to enforce the kwargs contract — catches accidental signature drift (e.g. someone changing `cancel_token` to positional).

### Task 2.5: Update `game/services/llm/__init__.py` exports [Simple]
**File:** `game/services/llm/__init__.py`
**Tests:** `pytest tests/unit/services/llm/test_package_imports.py`

- [x] Re-export from `__init__.py`:
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
- [x] Update smoke test to assert all 6 exports are accessible
- [x] Run all tests in `tests/unit/services/llm/` — all green

**Notes:** 6 exports re-exported from `__init__.py`. 10 tests passing across `tests/unit/services/llm/`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] ~14 new tests added across `test_types.py`, `test_provider_protocol.py`, `test_config.py`
- [x] `pytest tests/unit/services/llm/ tests/unit/core/test_config.py` — all green
- [x] No regression in any existing test
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to point to Phase 3
