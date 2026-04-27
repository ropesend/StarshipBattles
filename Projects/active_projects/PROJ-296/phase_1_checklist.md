# Phase 1: Exceptions + Error Codes [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-296 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Establish the `LLMException` branch and `L001`–`L006` error codes that the rest of the project will raise. Pure additive change to `game/core/`. No behavior yet — just the vocabulary.

---

## Tasks

### Task 1.1: Add `L001`–`L006` codes to `error_codes.py` [Simple]
**File:** `game/core/error_codes.py`
**Tests:** `pytest tests/unit/core/test_error_codes.py`

- [ ] Write failing test in `tests/unit/core/test_error_codes.py` asserting `ErrorCode.LLM_CONFIG_MISSING.value == "L001"` (and the other 5 codes)
- [ ] Run the test, confirm it fails for the right reason ("no such enum member")
- [ ] Add the following entries to the `ErrorCode` enum (use the existing prefix pattern):
  ```python
  # LLM Codes (L001-L099)
  LLM_CONFIG_MISSING = "L001"     # No API key / no provider configured
  LLM_NETWORK_ERROR = "L002"      # Connection / DNS / SSL failure
  LLM_BAD_RESPONSE = "L003"       # Non-2xx or malformed response body
  LLM_RATE_LIMITED = "L004"       # 429 from provider
  LLM_TIMEOUT = "L005"            # Request timeout
  LLM_CANCELLED = "L006"          # Cancelled via cancel_token
  ```
- [ ] Run the test again, confirm it passes
- [ ] Add a test that iterates the enum and asserts no two members share a value

**Notes:**

### Task 1.2: Add `LLMException` branch to `exceptions.py` [Simple]
**File:** `game/core/exceptions.py`
**Tests:** `pytest tests/unit/core/test_exceptions.py`

- [ ] Write failing tests for each new exception class:
  - `LLMException` is subclass of `GameException`
  - `LLMConfigError`, `LLMNetworkError`, `LLMResponseError`, `LLMRateLimited`, `LLMTimeoutError`, `LLMCancelled` are subclasses of `LLMException`
  - Each accepts `message`, `code`, `context` kwargs (inherited)
  - Exception chaining via `raise from` preserves `__cause__`
- [ ] Run tests, confirm they fail
- [ ] Add the new exception classes after `FormulaException` in `exceptions.py`. Each should be a thin subclass with no extra body (the constructor is inherited):
  ```python
  class LLMException(GameException):
      """Base class for LLM service errors."""

  class LLMConfigError(LLMException): pass
  class LLMNetworkError(LLMException): pass
  class LLMResponseError(LLMException): pass
  class LLMRateLimited(LLMException): pass
  class LLMTimeoutError(LLMException): pass
  class LLMCancelled(LLMException): pass
  ```
- [ ] Run tests, confirm they pass
- [ ] Verify no existing test breaks: `pytest tests/unit/core/`

**Notes:**

### Task 1.3: Update package `__all__` exports [Simple]
**File:** `game/core/__init__.py`
**Tests:** `pytest tests/unit/core/`

- [ ] Add the 7 new exception classes to `__all__` in alphabetical order with the existing exception entries
- [ ] Verify imports work: in a Python REPL, `from game.core import LLMException, LLMConfigError` should succeed
- [ ] Run `pytest tests/unit/core/` to confirm nothing broke

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Tests added: ~12 new tests in `test_error_codes.py` + `test_exceptions.py`
- [ ] `pytest tests/unit/core/` — all green
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to Phase 2
