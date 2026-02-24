# Phase 3: Migrate Remaining Builtin Raises

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-177 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Convert 4 remaining builtin exception raise sites to domain exceptions.

---

## Tasks

### Task 3.1: Migrate component_health_manager.py [Simple]
**File:** `game/simulation/components/component_health_manager.py`
**Tests:** `pytest tests/unit/simulation/components/ -k health_manager`

- [x] Line 52: Change `raise TypeError(...)` to `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={...})`
- [x] Add imports: `from game.core.exceptions import ValidationException` and `from game.core.error_codes import ErrorCode`
- [x] Update docstring if present

**Notes:** Updated docstring to reference ValidationException. Updated 3 tests that caught TypeError.

### Task 3.2: Migrate astrophysics_loader.py raise sites [Simple]
**File:** `game/strategy/generation/loaders/astrophysics_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k astrophysics`

- [x] Line 68: Change `raise KeyError(...)` to `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={"category": category})`
- [x] Line 84: Change `raise KeyError(...)` to `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={"zone": zone})`
- [x] Update imports if not already present

**Notes:** Imports already present from Phase 2. Added available keys to context for better error messages.

### Task 3.3: Migrate system_blueprints_loader.py raise site [Simple]
**File:** `game/strategy/generation/loaders/system_blueprints_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k blueprints`

- [x] Line 67: Change `raise KeyError(...)` to `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={"blueprint_name": name})`
- [x] Update imports if not already present
- [x] Update docstring to reference ValidationException

**Notes:** Imports already present. Updated docstring. Fixed 1 test that caught KeyError.

### Task 3.4: Migrate event_bus.py raise site [Simple]
**File:** `game/ui/screens/builder/event_bus.py`
**Tests:** `pytest tests/unit/ui/ -k event_bus`

- [x] Line 24: Change `raise TypeError(...)` to `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={"callback": str(callback)})`
- [x] Add imports: `from game.core.exceptions import ValidationException` and `from game.core.error_codes import ErrorCode`
- [x] Update docstring to reference ValidationException

**Notes:** Fixed 3 tests in tests/unit/systems/test_event_bus.py that caught TypeError.

### Task 3.5: Update callers that catch migrated exceptions [Medium]
**Tests:** `pytest tests/ -n 12`

- [x] Search for `except KeyError` blocks in callers of functions from Tasks 3.2-3.3
- [x] Search for `except TypeError` blocks in callers of functions from Tasks 3.1, 3.4
- [x] Update catch sites to catch `ValidationException` instead (or in addition)
- [x] If no callers catch these specifically, document "no callers affected"

**Notes:** No external callers catch these exceptions specifically. Only test files needed updating.

### Task 3.6: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] All 12338 tests pass
- [x] No new warnings

**Notes:** 12338 passed, 1 skipped

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
