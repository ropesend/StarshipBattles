# Phase 1: Infrastructure — Add Missing Error Codes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-170 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add 3 new error codes needed by the migration. No production behavior changes.
**Estimated Effort:** 30 min

---

## Tasks

### Task 1.1: Add New Error Codes [Simple]
**File:** `game/core/error_codes.py`
**Tests:** `pytest tests/unit/core/ -k error`

- [ ] Add `V002 = "V002"` with docstring `"""Schema or structural validation error (missing fields, invalid data structure)."""` after V001 (line 59)
- [ ] Add `V003 = "V003"` with docstring `"""Referenced entity does not exist."""` after V002
- [ ] Add `C003 = "C003"` with docstring `"""Required dependency injection parameter not provided."""` after C002 (line 137)
- [ ] Update `__all__` if needed (currently only exports `ErrorCode`)
- [ ] Verify: `python -c "from game.core.error_codes import ErrorCode; print(ErrorCode.SCHEMA_VALIDATION_ERROR.value, ErrorCode.MISSING_ENTITY.value, ErrorCode.MISSING_DEPENDENCY.value)"`

**Notes:**

### Task 1.2: Add Error Code Tests [Simple]
**File:** New or existing test file for error codes
**Tests:** `pytest tests/unit/core/ -k error`

- [ ] Verify new codes have unique values (V002, V003, C003)
- [ ] Verify new codes are accessible via `ErrorCode.SCHEMA_VALIDATION_ERROR`, `ErrorCode.MISSING_ENTITY`, `ErrorCode.MISSING_DEPENDENCY`
- [ ] Run existing error code tests to ensure no regression

**Notes:**

### Task 1.3: Update Error Handling Guidelines [Simple]
**File:** `docs/architecture/ERROR_HANDLING_GUIDELINES.md`
**Tests:** N/A (documentation)

- [ ] Add V002 SCHEMA_VALIDATION_ERROR to the Validation Codes table
- [ ] Add V003 MISSING_ENTITY to the Validation Codes table
- [ ] Add C003 MISSING_DEPENDENCY to the Component Codes table
- [ ] Add usage examples for each new code

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `python -c "from game.core.error_codes import ErrorCode; print(len(ErrorCode))"` outputs 22 (19 existing + 3 new)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
