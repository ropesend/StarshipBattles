# Phase 2: Fix Stale Docstrings

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-177 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update 12 docstrings that reference old generic exception types to reflect
the actual domain exceptions being raised.

---

## Tasks

### Task 2.1: Fix system_blueprints_loader.py docstrings [Simple]
**File:** `game/strategy/generation/loaders/system_blueprints_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k blueprints`

- [x] Line 45 (`load()` method): Change `Raises: ValueError` to `Raises: ValidationException`
- [x] Line 121 (`_validate_schema()` method): Change `Raises: ValueError` to `Raises: ValidationException`
- [x] Line 157 (`_validate_blueprint()` method): Change `Raises: ValueError` to `Raises: ValidationException`
- [x] Add import reference in docstring if needed: `game.core.exceptions.ValidationException`

**Notes:** Import already present; 3 docstrings updated

### Task 2.2: Fix astrophysics_loader.py docstrings [Simple]
**File:** `game/strategy/generation/loaders/astrophysics_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k astrophysics`

- [x] Line 49 (`load()` method): Change `Raises: ValueError` to `Raises: ValidationException`
- [x] Line 108 (`_validate_schema()` method): Change `Raises: ValueError` to `Raises: ValidationException`

**Notes:** 2 docstrings updated

### Task 2.3: Fix galaxy_layouts_loader.py docstrings [Simple]
**File:** `game/strategy/generation/loaders/galaxy_layouts_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/ -k galaxy_layouts`

- [x] Line 48 (`load()` method): Change `Raises: ValueError` to `Raises: ResourceException`
- [x] Line 78 (`get_layout_config()` method): Change `Raises: ValueError` to `Raises: ValidationException`

**Notes:** 2 docstrings updated (different exception types for different methods)

### Task 2.4: Fix battle_state.py docstring [Simple]
**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/unit/simulation/ -k battle_state`

- [x] Line 337 (`to_ship()` method): Change `Raises: TypeError` to `Raises: ValidationException`

**Notes:** 1 docstring updated

### Task 2.5: Fix abilities/base.py docstring [Simple]
**File:** `game/simulation/components/abilities/base.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/ -k base`

- [x] Line 88 (`_parse_scope()` method): Change `Raises: ValueError` to `Raises: ValidationException`

**Notes:** 1 docstring updated

### Task 2.6: Fix battle_mode_handler.py docstring [Simple]
**File:** `game/simulation/combat/battle_mode_handler.py`
**Tests:** `pytest tests/unit/simulation/combat/ -k battle_mode`

- [x] Line 279 (`get_handler_for_mode()` function): Change `Raises: ValueError` to `Raises: ValidationException`

**Notes:** 1 docstring updated

### Task 2.7: Fix ship.py docstrings [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/entities/ -k ship`

- [x] Line 782 (`to_dict()` method): Change `Raises: TypeError` to `Raises: ValidationException`
- [x] Lines 806-809 (`from_dict()` method): Change `Raises: KeyError, TypeError, ValueError` to `Raises: ValidationException`

**Notes:** 2 docstrings updated (from_dict consolidated to single ValidationException)

### Task 2.8: Fix ship_factory.py docstring [Simple]
**File:** `game/ui/services/ship_factory.py`
**Tests:** `pytest tests/unit/ui/services/ -k ship_factory`

- [x] Lines 87-88 (`create_ship_from_design()` method): Change `Raises: KeyError, ValueError` to `Raises: ValidationException`

**Notes:** 1 docstring updated

### Task 2.9: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] All 12338 tests pass

**Notes:** 12338 passed, 1 skipped (60.14s)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
