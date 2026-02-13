# Phase 1: Error Code Standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-107 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Standardize all error codes to use the ErrorCode enum. Add missing AI category. Fix invalid codes in documentation.

**Findings:** CON-FND-001, CON-FND-005, CON-FND-007

---

## Tasks

### Task 1.1: Add AI Error Code Category to ErrorCode Enum [Simple]
**File:** `game/core/error_codes.py`
**Tests:** `pytest tests/unit/core/test_error_codes.py -v`

- [x] Add AI category section after Component codes (line ~137):
  ```python
  # AI Codes (A001-A099)
  AI_STATE_ERROR = "A001"
  """AI system state error (e.g., singleton violation)."""
  ```
- [x] Verify: New code follows X### format convention (A001)
- [x] Verify: `pytest tests/unit/core/test_error_codes.py` passes

**Notes:** Also added missing Formula codes F001, F002, F004 that were referenced in modifier_effects.py.

---

### Task 1.2: Fix StrategyManager Error Code [Simple]
**File:** `game/ai/strategy_manager.py`
**Tests:** `pytest tests/unit/ai/ -v -k strategy_manager`

- [x] Line 48: Replace raw string `"AI001"` with `ErrorCode.AI_STATE_ERROR.value`
- [x] Add import: `from game.core.error_codes import ErrorCode` at top of file
- [x] Verify: `pytest tests/unit/ai/ -v` passes

**Notes:** Updated test in test_ai_exceptions.py to expect "A001" instead of "AI001".

---

### Task 1.3: Fix Exception Module Docstring Error Codes [Simple]
**File:** `game/core/exceptions.py`
**Tests:** `pytest tests/unit/core/ -v`

- [x] Line 18: Change `code="V002"` in docstring example to `code=ErrorCode.VALIDATION_FAILED.value` (or just `code="V001"` since V002 doesn't exist in enum - verify first)
- [x] Line 29: Change `code="P003"` in docstring to `code=ErrorCode.CORRUPT_DATA.value` (P003 IS valid - just update to show enum usage pattern)
- [x] Line 38: Change `if e.code == "C002":` to `if e.code == ErrorCode.COMPONENT_INVALID.value:`
- [x] Verify: All docstring examples use ErrorCode enum values, not raw strings
- [x] Verify: `pytest tests/unit/core/` passes

**Notes:** Documentation-only changes. All three docstring examples now show ErrorCode enum pattern.

---

### Task 1.4: Fix ValidationResult Docstring Invalid Error Code [Simple]
**File:** `game/core/validation.py`
**Tests:** `pytest tests/unit/core/ -v`

- [x] Line 89: Change `code="E001"` to `code=ErrorCode.VALIDATION_FAILED.value` in the docstring example
- [x] Verify: The code value used exists in ErrorCode enum
- [x] Verify: `pytest tests/unit/core/` passes

**Notes:** Documentation-only change. Fixed invalid "E001" to use proper ErrorCode.VALIDATION_FAILED.value.

---

### Task 1.5: Verify No Other Raw Error Code Strings Remain [Simple]
**Tests:** Run grep across codebase

- [x] Search for `code="[A-Z]\d{3}"` pattern in game/**/*.py (excluding test files)
- [x] For each found occurrence, verify it either:
  - Uses `ErrorCode.X.value` pattern, OR
  - Is a valid ErrorCode enum value string
- [x] Document any remaining violations for future cleanup

**Notes:** Found 12 raw string usages across 4 files. All are valid ErrorCode enum values:
- battle_controller.py: S001 (STATE_FROZEN) - 2 uses
- projectile.py: V003 (MISSING_REQUIRED) - 3 uses
- modifier_effects.py: F001, F002, F003, F004 - 4 uses (added missing F001, F002, F004 to enum)
- game_session.py: P001, P002, P003 - 3 uses
These use raw strings but match enum values. Converting to ErrorCode.X.value pattern is out of scope for Phase 1 (focused on fixing invalid codes and adding missing enum values).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run full test suite: `pytest tests/ -n 12` → 8185 passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
