# Phase 1: Exceptions + Error Codes [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-296 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Establish the `LLMException` branch and `L001`–`L006` error codes that the rest of the project will raise. Pure additive change to `game/core/`. No behavior yet — just the vocabulary.

---

## Tasks

### Task 1.1: Add `L001`–`L006` codes to `error_codes.py` [Simple]
**File:** `game/core/error_codes.py`
**Tests:** `pytest tests/unit/core/test_error_codes.py`

- [x] Write failing test in `tests/unit/core/test_error_codes.py` asserting `ErrorCode.LLM_CONFIG_MISSING.value == "L001"` (and the other 5 codes)
- [x] Run the test, confirm it fails for the right reason ("no such enum member")
- [x] Add the following entries to the `ErrorCode` enum:
  - `LLM_CONFIG_MISSING = "L001"`, `LLM_NETWORK_ERROR = "L002"`, `LLM_BAD_RESPONSE = "L003"`, `LLM_RATE_LIMITED = "L004"`, `LLM_TIMEOUT = "L005"`, `LLM_CANCELLED = "L006"`
- [x] Run the test again, confirm it passes
- [x] Add a test (`TestLLMErrorCodes.test_llm_codes_start_with_l`) that iterates enum and asserts L prefix on all LLM_* codes

**Notes:** Added 7 new tests in `tests/unit/core/test_error_codes.py` (6 minimum-set + 1 prefix). Existing `test_all_codes_are_unique` already covers uniqueness. 22 codes test passes.

### Task 1.2: Add `LLMException` branch to `exceptions.py` [Simple]
**File:** `game/core/exceptions.py`
**Tests:** `pytest tests/unit/core/test_exceptions.py`

- [x] Write failing tests for each new exception class (TestLLMExceptions class with 6 tests covering inheritance, code/context, chaining, catchability)
- [x] Run tests, confirm they fail (ImportError, classes don't exist)
- [x] Add the new exception classes after `FormulaException` in `exceptions.py` with proper docstrings (security guidance baked into `LLMException` docstring)
- [x] Run tests, confirm pass
- [x] Verify no existing test breaks (`pytest tests/unit/core/` → 947 passing)

**Notes:** Added security guidance to `LLMException` docstring — never log API key, body, headers, or message contents in `context`. Total 7 new exception tests added; full core suite stays green.

### Task 1.3: Update package `__all__` exports [Simple]
**File:** `game/core/__init__.py`
**Tests:** `pytest tests/unit/core/`

- [x] Add the 7 new exception classes to imports + `__all__` (kept alongside existing PROJ-45 entries with a separator comment)
- [x] Update module docstring to list new LLM exception names
- [x] Verify imports work: `python -c "from game.core import LLMException, LLMConfigError, LLMRateLimited"` succeeds
- [x] Run `pytest tests/unit/core/` to confirm nothing broke (947 passing)

**Notes:** Followed existing comment-block pattern in `__all__`. No reordering of existing entries.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Tests added: 7 new in `test_error_codes.py` + 6 new in `test_exceptions.py` = 13 total
- [x] `pytest tests/unit/core/` — all 947 green
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to point to Phase 2
