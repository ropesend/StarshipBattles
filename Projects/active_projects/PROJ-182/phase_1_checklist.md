# Phase 1: Dead Code Removal & Docstring Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-182 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete dead primitives.py files and update all stale docstring/documentation examples to use ValidationResult factory methods

---

## Tasks

### Task 1.1: Delete Dead `primitives.py` and Its Tests [Simple]
**Files:**
- `game/strategy/validation/primitives.py` (80 lines — entire file)
- `tests/unit/strategy/validation/test_primitives.py` (entire file)
**Tests:** `pytest tests/ -n 12` (expect 20 fewer tests from deleted file)

- [ ] Delete `game/strategy/validation/primitives.py`
- [ ] Delete `tests/unit/strategy/validation/test_primitives.py`
- [ ] Verify: `game/strategy/validation/__init__.py` does NOT import from primitives (confirmed during review — it doesn't)
- [ ] Run `pytest tests/unit/strategy/validation/ -n 4` — remaining validation tests still pass

**Notes:**

---

### Task 1.2: Update ValidationResult Class Docstring [Simple]
**File:** `game/core/validation.py`
**Tests:** No tests affected (docstring-only change)

- [ ] Line 72: Change `result = ValidationResult(is_valid=False, errors=["Error 1", "Error 2"])` to `result = ValidationResult.with_errors(["Error 1", "Error 2"])`
- [ ] Line 81: Change `result = ValidationResult()` to `result = ValidationResult.success()`
- [ ] Update the surrounding text on line 71 from `Construction:` to `Factory Methods:` to reflect the new pattern

**Notes:**

---

### Task 1.3: Update ValidationRule Class Docstring [Simple]
**File:** `game/simulation/validation/base.py`
**Tests:** No tests affected (docstring-only change)

- [ ] Line 30: Change `result = ValidationResult(True)` to `result = ValidationResult.success()`

**Notes:**

---

### Task 1.4: Update PATTERNS.md ValidationResult Documentation [Simple]
**File:** `docs/architecture/PATTERNS.md`
**Tests:** No tests affected (documentation-only change)

- [ ] Lines 251-255: Update the `ValidationResult` dataclass definition to match the real class (use `is_valid: bool` not `success: bool`, add `error_code: Optional[str] = None`)
- [ ] Line 264: Change `return ValidationResult(True)` to `return ValidationResult.success()`
- [ ] Line 288: Change `return ValidationResult(False, [f"Layer {layer_type} not found"])` to `return ValidationResult.error(f"Layer {layer_type} not found")`
- [ ] Line 291: Change `return ValidationResult(False, [f"Layer {layer_type} at capacity"])` to `return ValidationResult.error(f"Layer {layer_type} at capacity")`
- [ ] Line 293: Change `return ValidationResult(True)` to `return ValidationResult.success()`
- [ ] Line 306: Change `return ValidationResult(False, [f"{component.name} already installed"])` to `return ValidationResult.error(f"{component.name} already installed")`
- [ ] Line 307: Change `return ValidationResult(True)` to `return ValidationResult.success()`

**Notes:**

---

### Task 1.5: Final Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Grep for `ValidationResult(True)` in `.py` and `.md` files — zero results (excluding factory method internals in validation.py)
- [ ] Grep for `ValidationResult(False` in `.py` and `.md` files — zero results (excluding factory method internals in validation.py)
- [ ] Grep for `ValidationResult()` in `.py` and `.md` files — zero results (excluding factory method internals in validation.py)
- [ ] Verify primitives.py no longer exists

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to completion
