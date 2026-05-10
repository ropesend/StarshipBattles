# Phase 1: Infrastructure — Add Missing Error Codes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-170 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add 3 new error codes needed by the migration. No production behavior changes.
**Estimated Effort:** 30 min

---

## Tasks

### Task 1.1: Add New Error Codes [Simple]
**File:** `game/core/error_codes.py`
**Tests:** `pytest tests/unit/core/ -k error`

- [x] Add `V002 = "V002"` with docstring `"""Schema or structural validation error (missing fields, invalid data structure)."""` after V001 (line 59)
- [x] Add `V003 = "V003"` with docstring `"""Referenced entity does not exist."""` after V002
- [x] Add `C003 = "C003"` with docstring `"""Required dependency injection parameter not provided."""` after C002 (line 137)
- [x] Update `__all__` if needed (currently only exports `ErrorCode`) — No change needed
- [x] Verify: `python -c "from game.core.error_codes import ErrorCode; print(ErrorCode.SCHEMA_VALIDATION_ERROR.value, ErrorCode.MISSING_ENTITY.value, ErrorCode.MISSING_DEPENDENCY.value)"`

**Notes:**

### Task 1.2: Add Error Code Tests [Simple]
**File:** New or existing test file for error codes
**Tests:** `pytest tests/unit/core/ -k error`

- [x] Verify new codes have unique values (V002, V003, C003)
- [x] Verify new codes are accessible via `ErrorCode.SCHEMA_VALIDATION_ERROR`, `ErrorCode.MISSING_ENTITY`, `ErrorCode.MISSING_DEPENDENCY`
- [x] Run existing error code tests to ensure no regression

**Notes:**

### Task 1.3: Update Error Handling Guidelines [Simple]
**File:** `docs/architecture/ERROR_HANDLING_GUIDELINES.md`
**Tests:** N/A (documentation)

- [x] Add V002 SCHEMA_VALIDATION_ERROR to the Validation Codes table
- [x] Add V003 MISSING_ENTITY to the Validation Codes table
- [x] Add C003 MISSING_DEPENDENCY to the Component Codes table
- [x] Add usage examples for each new code

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `python -c "from game.core.error_codes import ErrorCode; print(len(ErrorCode))"` outputs 24 (21 existing + 3 new)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
