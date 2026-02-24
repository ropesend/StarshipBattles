# Phase 3: Migrate Remaining Builtin Raises

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-177 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Convert 4 remaining builtin exception raise sites to domain exceptions.

---

## Tasks

### Task 3.1: Migrate component_health_manager.py [Simple]
**File:** `game/simulation/components/component_health_manager.py`
**Tests:** `pytest tests/unit/simulation/components/ -k health_manager`

- [ ] Line 52: Change `raise TypeError(...)` to `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={...})`
- [ ] Add imports: `from game.core.exceptions import ValidationException` and `from game.core.error_codes import ErrorCode`
- [ ] Update docstring if present

**Notes:**

### Task 3.2: Migrate astrophysics_loader.py raise sites [Simple]
**File:** `game/strategy/generation/loaders/astrophysics_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k astrophysics`

- [ ] Line 68: Change `raise KeyError(...)` to `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={"category": category})`
- [ ] Line 84: Change `raise KeyError(...)` to `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={"zone": zone})`
- [ ] Update imports if not already present

**Notes:**

### Task 3.3: Migrate system_blueprints_loader.py raise site [Simple]
**File:** `game/strategy/generation/loaders/system_blueprints_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k blueprints`

- [ ] Line 67: Change `raise KeyError(...)` to `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={"blueprint_name": name})`
- [ ] Update imports if not already present

**Notes:**

### Task 3.4: Migrate event_bus.py raise site [Simple]
**File:** `game/ui/screens/builder/event_bus.py`
**Tests:** `pytest tests/unit/ui/ -k event_bus`

- [ ] Line 24: Change `raise TypeError(...)` to `raise ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={"callback": str(callback)})`
- [ ] Add imports: `from game.core.exceptions import ValidationException` and `from game.core.error_codes import ErrorCode`

**Notes:**

### Task 3.5: Update callers that catch migrated exceptions [Medium]
**Tests:** `pytest tests/ -n 12`

- [ ] Search for `except KeyError` blocks in callers of functions from Tasks 3.2-3.3
- [ ] Search for `except TypeError` blocks in callers of functions from Tasks 3.1, 3.4
- [ ] Update catch sites to catch `ValidationException` instead (or in addition)
- [ ] If no callers catch these specifically, document "no callers affected"

**Notes:**

### Task 3.6: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All 12338 tests pass
- [ ] No new warnings

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
