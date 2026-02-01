# Phase 2: Core Layer - Fix Core Module Error Handling

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-45 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update core modules to use custom exceptions and proper error handling.

---

## Tasks

### Task 2.1: Update json_utils.py Error Handling [Medium]
**File:** `game/core/json_utils.py`
**Tests:** `pytest tests/unit/core/test_json_utils.py`

- [x] Import custom exceptions from `game.core.exceptions`
- [x] Replace generic `Exception` catch at line 56 with specific types
- [x] Add `raise from e` for exception chaining where re-raising
- [x] Ensure all error paths include context (filepath)
- [x] Update docstrings to document raised exceptions
- [x] Verify: Tests pass (18/18)

**Notes:** json_utils.py already had proper specific exception handling (FileNotFoundError, JSONDecodeError, IOError). Updated module docstring to document exceptions.

---

### Task 2.2: Update resources.py Error Handling [Medium]
**File:** `game/core/resources.py`
**Tests:** `pytest tests/unit/core/test_resources_registry.py`

- [x] Fix ERR-05: lines 77-79 - Add logging before fallback
- [x] Fix ERR-05: lines 111-113 - Add logging before fallback
- [x] Fix CORE-006: Replace bare `except Exception:` with specific types
- [x] Import and use `ResourceException` where appropriate
- [x] Add context to all error messages (resource name, path)
- [x] Verify: Tests pass (39/39)

**Notes:** Replaced bare `except Exception` with specific types (FileNotFoundError, JSONDecodeError, PermissionError, OSError, TypeError, AttributeError). Added logging for each exception path.

---

### Task 2.3: Update registry.py Error Handling [Medium]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/test_registry.py`

- [x] Fix ERR-003: line 175 - Replace `raise Exception()` with `StateException`
- [x] Fix ERR-005: Standardize to `StateException` for state violations
- [x] Replace `RuntimeError` with `FrozenStateException` where appropriate (lines 124-127, 241, 296)
- [x] Add error codes to all raised exceptions
- [x] Verify: Tests pass (69/69)

**Notes:**
- Changed `get_default_registries()` to raise `StateException` instead of `RuntimeError`
- Changed all frozen state errors to raise `FrozenStateException` with error codes
- Updated 7 fallback patterns in other files to also catch `StateException`
- Updated test expectations accordingly

---

### Task 2.4: Update validation.py with Error Codes [Simple]
**File:** `game/core/validation.py`
**Tests:** `pytest tests/unit/core/test_validation.py`

- [x] Fix ERR-008: Import `ErrorCode` enum
- [x] Update `add_error()` to accept `ErrorCode` enum values
- [x] Add helper method to convert `ErrorCode` to string
- [x] Update existing usages to use error codes
- [x] Verify: Tests pass (26/26)

**Notes:** Updated `add_error()` to accept both `str` and `ErrorCode` enum values. Enum values are automatically converted to their string value.

---

### Task 2.5: Update screenshot_manager.py Error Handling [Simple]
**File:** `game/core/screenshot_manager.py`
**Tests:** `pytest tests/unit/core/test_screenshot_manager.py`

- [x] Fix CORE-006: lines 115-116 - Log exception details before fallback
- [x] Fix CORE-006: lines 216-217 - Log exception details before fallback
- [x] Replace generic `Exception` catches with specific types
- [x] Verify: Tests pass (no dedicated tests, import works)

**Notes:** Replaced `except Exception` with specific types: `pygame.error`, `IOError`, `OSError`, `AttributeError`. Added filepath context to error messages.

---

### Task 2.6: Update logger.py Event Handler Error Handling [Simple]
**File:** `game/core/logger.py`
**Tests:** `pytest tests/unit/core/test_logger.py`

- [x] Add try/catch around event handler invocation in `log_event()`
- [x] Log handler exceptions rather than propagating
- [x] Add specific exception types for logging failures
- [x] Verify: Tests pass (39/39)

**Notes:** Added try/catch in `log_event()` to catch and log handler exceptions without propagating. Updated test expectations to match new behavior (handlers don't crash callers).

---

### Task 2.7: Fix paths.py Error Handling [Simple]
**File:** `game/core/paths.py`
**Tests:** `pytest tests/unit/core/test_paths.py`

- [x] Fix ERR-005: line 25 - Replace generic `Exception` with `ResourceException`
- [x] Add context (path value) to error message
- [x] Verify: Tests pass (no dedicated tests, import works)

**Notes:** Replaced `RuntimeError` with `ResourceException` with error code and context.

---

### Task 2.8: Update Core Module Imports [Simple]
**File:** `game/core/__init__.py`
**Tests:** `pytest tests/unit/core/`

- [x] Export exceptions from `game.core.exceptions`
- [x] Export error codes from `game.core.error_codes`
- [x] Update `__all__` if present
- [x] Verify: All core tests pass (516/516)

**Notes:** Added all 10 exception classes and ErrorCode enum to core exports.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/unit/core/` (516 passed)
- [x] No regressions: `pytest tests/` (5740 passed, 3 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
