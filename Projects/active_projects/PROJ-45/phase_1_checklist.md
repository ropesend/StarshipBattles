# Phase 1: Foundation - Exception Hierarchy & Error Codes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-45 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the foundational infrastructure for typed exceptions and error codes.

---

## Tasks

### Task 1.1: Create Custom Exception Hierarchy [Medium]
**File:** `game/core/exceptions.py` (NEW)
**Tests:** `pytest tests/unit/core/test_exceptions.py`

- [ ] Create new file `game/core/exceptions.py`
- [ ] Define base `GameException` class with `code` and `context` attributes:
  ```python
  class GameException(Exception):
      def __init__(self, message: str, code: str = None, context: dict = None):
          super().__init__(message)
          self.code = code
          self.context = context or {}
  ```
- [ ] Define `StateException` and `FrozenStateException` for state violations
- [ ] Define `ValidationException` for validation failures
- [ ] Define `ResourceException` and `MissingResourceException` for resource errors
- [ ] Define `PersistenceException` for save/load errors
- [ ] Define `SimulationException`, `ComponentException`, `FormulaException`
- [ ] Add `__all__` exports
- [ ] Verify: Import works from other modules

**Notes:**

---

### Task 1.2: Create Error Code Enumeration [Simple]
**File:** `game/core/error_codes.py` (NEW)
**Tests:** `pytest tests/unit/core/test_error_codes.py`

- [ ] Create new file `game/core/error_codes.py`
- [ ] Define `ErrorCode` enum with categories:
  - Validation: V001-V099
  - State: S001-S099
  - Resource: R001-R099
  - Persistence: P001-P099
  - Formula: F001-F099
  - Component: C001-C099
- [ ] Add `__all__` exports
- [ ] Verify: All codes are unique

**Notes:**

---

### Task 1.3: Create Exception Tests [Simple]
**File:** `tests/unit/core/test_exceptions.py` (NEW)
**Tests:** Self-testing

- [ ] Create test file for exception hierarchy
- [ ] Test base `GameException` instantiation with code and context
- [ ] Test inheritance chain for all exception types
- [ ] Test exception chaining with `raise from`
- [ ] Verify: `pytest tests/unit/core/test_exceptions.py` passes

**Notes:**

---

### Task 1.4: Create Error Code Tests [Simple]
**File:** `tests/unit/core/test_error_codes.py` (NEW)
**Tests:** Self-testing

- [ ] Create test file for error codes
- [ ] Test all error codes are unique
- [ ] Test error code string values follow naming convention (X###)
- [ ] Verify: `pytest tests/unit/core/test_error_codes.py` passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/unit/core/test_exceptions.py tests/unit/core/test_error_codes.py`
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
