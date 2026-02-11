# Phase 1: Error Code Standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-107 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Standardize all error codes to use the ErrorCode enum. Add missing AI category. Fix invalid codes in documentation.

**Findings:** CON-FND-001, CON-FND-005, CON-FND-007

---

## Tasks

### Task 1.1: Add AI Error Code Category to ErrorCode Enum [Simple]
**File:** `game/core/error_codes.py`
**Tests:** `pytest tests/unit/core/test_error_codes.py -v`

- [ ] Add AI category section after Component codes (line ~137):
  ```python
  # AI Codes (A001-A099)
  AI_STATE_ERROR = "A001"
  """AI system state error (e.g., singleton violation)."""
  ```
- [ ] Verify: New code follows X### format convention (A001)
- [ ] Verify: `pytest tests/unit/core/test_error_codes.py` passes

**Notes:**

---

### Task 1.2: Fix StrategyManager Error Code [Simple]
**File:** `game/ai/strategy_manager.py`
**Tests:** `pytest tests/unit/ai/ -v -k strategy_manager`

- [ ] Line 48: Replace raw string `"AI001"` with `ErrorCode.AI_STATE_ERROR.value`
- [ ] Add import: `from game.core.error_codes import ErrorCode` at top of file
- [ ] Verify: `pytest tests/unit/ai/ -v` passes

**Notes:**

---

### Task 1.3: Fix Exception Module Docstring Error Codes [Simple]
**File:** `game/core/exceptions.py`
**Tests:** `pytest tests/unit/core/ -v`

- [ ] Line 18: Change `code="V002"` in docstring example to `code=ErrorCode.VALIDATION_FAILED.value` (or just `code="V001"` since V002 doesn't exist in enum - verify first)
- [ ] Line 29: Change `code="P003"` in docstring to `code=ErrorCode.CORRUPT_DATA.value` (P003 IS valid - just update to show enum usage pattern)
- [ ] Line 38: Change `if e.code == "C002":` to `if e.code == ErrorCode.COMPONENT_INVALID.value:`
- [ ] Verify: All docstring examples use ErrorCode enum values, not raw strings
- [ ] Verify: `pytest tests/unit/core/` passes

**Notes:** These are documentation-only changes (docstring examples). No runtime behavior changes.

---

### Task 1.4: Fix ValidationResult Docstring Invalid Error Code [Simple]
**File:** `game/core/validation.py`
**Tests:** `pytest tests/unit/core/ -v`

- [ ] Line 89: Change `code="E001"` to `code=ErrorCode.VALIDATION_FAILED.value` in the docstring example
- [ ] Verify: The code value used exists in ErrorCode enum
- [ ] Verify: `pytest tests/unit/core/` passes

**Notes:** Documentation-only change. "E001" doesn't exist in any category.

---

### Task 1.5: Verify No Other Raw Error Code Strings Remain [Simple]
**Tests:** Run grep across codebase

- [ ] Search for `code="[A-Z]\d{3}"` pattern in game/**/*.py (excluding test files)
- [ ] For each found occurrence, verify it either:
  - Uses `ErrorCode.X.value` pattern, OR
  - Is a valid ErrorCode enum value string
- [ ] Document any remaining violations for future cleanup

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
