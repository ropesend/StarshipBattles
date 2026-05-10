# Phase 1: Dead Code Removal & Docstring Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-182 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete dead primitives.py files and update all stale docstring/documentation examples to use ValidationResult factory methods

---

## Tasks

### Task 1.1: Delete Dead `primitives.py` and Its Tests [Simple]
**Files:**
- `game/strategy/validation/primitives.py` (80 lines — entire file)
- `tests/unit/strategy/validation/test_primitives.py` (entire file)
**Tests:** `pytest tests/ -n 12` (expect 20 fewer tests from deleted file)

- [x] Delete `game/strategy/validation/primitives.py`
- [x] Delete `tests/unit/strategy/validation/test_primitives.py`
- [x] Verify: `game/strategy/validation/__init__.py` does NOT import from primitives (confirmed during review — it doesn't)
- [x] Run `pytest tests/unit/strategy/validation/ -n 4` — remaining validation tests still pass (72 passed)

**Notes:**

---

### Task 1.2: Update ValidationResult Class Docstring [Simple]
**File:** `game/core/validation.py`
**Tests:** No tests affected (docstring-only change)

- [x] Line 72: Change `result = ValidationResult(is_valid=False, errors=["Error 1", "Error 2"])` to `result = ValidationResult.with_errors(["Error 1", "Error 2"])`
- [x] Line 81: Change `result = ValidationResult()` to `result = ValidationResult.success()`
- [x] Update the surrounding text on line 71 from `Construction:` to `Factory Methods:` to reflect the new pattern

**Notes:**

---

### Task 1.3: Update ValidationRule Class Docstring [Simple]
**File:** `game/simulation/validation/base.py`
**Tests:** No tests affected (docstring-only change)

- [x] Line 30: Change `result = ValidationResult(True)` to `result = ValidationResult.success()`

**Notes:**

---

### Task 1.4: Update PATTERNS.md ValidationResult Documentation [Simple]
**File:** `docs/architecture/PATTERNS.md`
**Tests:** No tests affected (documentation-only change)

- [x] Lines 251-255: Update the `ValidationResult` dataclass definition to match the real class (use `is_valid: bool` not `success: bool`, add `error_code: Optional[str] = None`)
- [x] Line 264: Change `return ValidationResult(True)` to `return ValidationResult.success()`
- [x] Line 288: Change `return ValidationResult(False, [f"Layer {layer_type} not found"])` to `return ValidationResult.error(f"Layer {layer_type} not found")`
- [x] Line 291: Change `return ValidationResult(False, [f"Layer {layer_type} at capacity"])` to `return ValidationResult.error(f"Layer {layer_type} at capacity")`
- [x] Line 293: Change `return ValidationResult(True)` to `return ValidationResult.success()`
- [x] Line 306: Change `return ValidationResult(False, [f"{component.name} already installed"])` to `return ValidationResult.error(f"{component.name} already installed")`
- [x] Line 307: Change `return ValidationResult(True)` to `return ValidationResult.success()`

**Notes:**

---

### Task 1.5: Final Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12` — 12366 passed, 1 skipped
- [x] Grep for `ValidationResult(True)` in `.py` and `.md` files — zero results
- [x] Grep for `ValidationResult(False` in `.py` and `.md` files — zero results
- [x] Grep for `ValidationResult()` in `.py` and `.md` files — zero results
- [x] Verify primitives.py no longer exists

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to completion

**Notes:** Also updated tests/unit/simulation/validation/test_base_rule.py to use factory methods instead of deprecated constructor patterns.
