# Phase 1: Foundation - Exception Hierarchy & Error Codes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-45 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the foundational infrastructure for typed exceptions and error codes.

---

## Tasks

### Task 1.1: Create Custom Exception Hierarchy [Medium]
**File:** `game/core/exceptions.py` (NEW)
**Tests:** `pytest tests/unit/core/test_exceptions.py`

- [x] Create new file `game/core/exceptions.py`
- [x] Define base `GameException` class with `code` and `context` attributes:
  ```python
  class GameException(Exception):
      def __init__(self, message: str, code: str = None, context: dict = None):
          super().__init__(message)
          self.code = code
          self.context = context or {}
  ```
- [x] Define `StateException` and `FrozenStateException` for state violations
- [x] Define `ValidationException` for validation failures
- [x] Define `ResourceException` and `MissingResourceException` for resource errors
- [x] Define `PersistenceException` for save/load errors
- [x] Define `SimulationException`, `ComponentException`, `FormulaException`
- [x] Add `__all__` exports
- [x] Verify: Import works from other modules

**Notes:** All 10 exception classes created with full docstrings. No game.* imports to avoid circular dependencies.

---

### Task 1.2: Create Error Code Enumeration [Simple]
**File:** `game/core/error_codes.py` (NEW)
**Tests:** `pytest tests/unit/core/test_error_codes.py`

- [x] Create new file `game/core/error_codes.py`
- [x] Define `ErrorCode` enum with categories:
  - Validation: V001-V099
  - State: S001-S099
  - Resource: R001-R099
  - Persistence: P001-P099
  - Formula: F001-F099
  - Component: C001-C099
- [x] Add `__all__` exports
- [x] Verify: All codes are unique

**Notes:** 29 error codes defined across 6 categories.

---

### Task 1.3: Create Exception Tests [Simple]
**File:** `tests/unit/core/test_exceptions.py` (NEW)
**Tests:** Self-testing

- [x] Create test file for exception hierarchy
- [x] Test base `GameException` instantiation with code and context
- [x] Test inheritance chain for all exception types
- [x] Test exception chaining with `raise from`
- [x] Verify: `pytest tests/unit/core/test_exceptions.py` passes

**Notes:** 29 tests covering all exception classes, inheritance, and chaining.

---

### Task 1.4: Create Error Code Tests [Simple]
**File:** `tests/unit/core/test_error_codes.py` (NEW)
**Tests:** Self-testing

- [x] Create test file for error codes
- [x] Test all error codes are unique
- [x] Test error code string values follow naming convention (X###)
- [x] Verify: `pytest tests/unit/core/test_error_codes.py` passes

**Notes:** 24 tests covering uniqueness, naming convention, and category organization.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/unit/core/test_exceptions.py tests/unit/core/test_error_codes.py`
- [x] No regressions: `pytest tests/ --testmon`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
