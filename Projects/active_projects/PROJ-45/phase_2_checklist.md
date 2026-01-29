# Phase 2: Core Layer - Fix Core Module Error Handling

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-45 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update core modules to use custom exceptions and proper error handling.

---

## Tasks

### Task 2.1: Update json_utils.py Error Handling [Medium]
**File:** `game/core/json_utils.py`
**Tests:** `pytest tests/unit/core/test_json_utils.py`

- [ ] Import custom exceptions from `game.core.exceptions`
- [ ] Replace generic `Exception` catch at line 56 with specific types
- [ ] Add `raise from e` for exception chaining where re-raising
- [ ] Ensure all error paths include context (filepath)
- [ ] Update docstrings to document raised exceptions
- [ ] Verify: Tests pass

**Notes:**

---

### Task 2.2: Update resources.py Error Handling [Medium]
**File:** `game/core/resources.py`
**Tests:** `pytest tests/unit/core/test_resources.py`

- [ ] Fix ERR-05: lines 77-79 - Add logging before fallback
- [ ] Fix ERR-05: lines 111-113 - Add logging before fallback
- [ ] Fix CORE-006: Replace bare `except Exception:` with specific types
- [ ] Import and use `ResourceException` where appropriate
- [ ] Add context to all error messages (resource name, path)
- [ ] Verify: Tests pass

**Notes:**

---

### Task 2.3: Update registry.py Error Handling [Medium]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/test_registry.py`

- [ ] Fix ERR-003: line 175 - Replace `raise Exception()` with `StateException`
- [ ] Fix ERR-005: Standardize to `StateException` for state violations
- [ ] Replace `RuntimeError` with `FrozenStateException` where appropriate (lines 124-127, 241, 296)
- [ ] Add error codes to all raised exceptions
- [ ] Verify: Tests pass

**Notes:**

---

### Task 2.4: Update validation.py with Error Codes [Simple]
**File:** `game/core/validation.py`
**Tests:** `pytest tests/unit/core/test_validation.py`

- [ ] Fix ERR-008: Import `ErrorCode` enum
- [ ] Update `add_error()` to accept `ErrorCode` enum values
- [ ] Add helper method to convert `ErrorCode` to string
- [ ] Update existing usages to use error codes
- [ ] Verify: Tests pass

**Notes:**

---

### Task 2.5: Update screenshot_manager.py Error Handling [Simple]
**File:** `game/core/screenshot_manager.py`
**Tests:** `pytest tests/unit/core/test_screenshot_manager.py`

- [ ] Fix CORE-006: lines 115-116 - Log exception details before fallback
- [ ] Fix CORE-006: lines 216-217 - Log exception details before fallback
- [ ] Replace generic `Exception` catches with specific types
- [ ] Verify: Tests pass

**Notes:**

---

### Task 2.6: Update logger.py Event Handler Error Handling [Simple]
**File:** `game/core/logger.py`
**Tests:** `pytest tests/unit/core/test_logger.py`

- [ ] Add try/catch around event handler invocation in `log_event()`
- [ ] Log handler exceptions rather than propagating
- [ ] Add specific exception types for logging failures
- [ ] Verify: Tests pass

**Notes:**

---

### Task 2.7: Fix paths.py Error Handling [Simple]
**File:** `game/core/paths.py`
**Tests:** `pytest tests/unit/core/test_paths.py`

- [ ] Fix ERR-005: line 25 - Replace generic `Exception` with `ResourceException`
- [ ] Add context (path value) to error message
- [ ] Verify: Tests pass

**Notes:**

---

### Task 2.8: Update Core Module Imports [Simple]
**File:** `game/core/__init__.py`
**Tests:** `pytest tests/unit/core/`

- [ ] Export exceptions from `game.core.exceptions`
- [ ] Export error codes from `game.core.error_codes`
- [ ] Update `__all__` if present
- [ ] Verify: All core tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/unit/core/`
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
