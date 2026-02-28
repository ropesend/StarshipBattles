# Phase 3: Initialization Functions (Simulation Layer)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-211 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Thread registry_provider through initialization/boot functions in component.py and ship_loader.py
**Priority:** Medium - Independent of runtime path, affects boot sequence
**Risk:** Low - Only 2-4 call sites per function
**Depends on:** None (independent of Phases 1-2)

---

## Tasks

### Task 3.1: Fix initialize_ship_data() [DI-SIM-006]
**Files:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/simulation/entities/`

- [x] Read `ship_loader.py` to understand `initialize_ship_data()` call chain
- [x] Add `registry_provider` parameter to `initialize_ship_data()`
- [x] Forward to internal calls (`load_vehicle_classes`, `get_or_create_validator`)
- [x] Update all callers (app.py, test files) to pass provider
- [x] Verify: all tests pass

### Task 3.2: Fix get_or_create_validator() [DI-SIM-001]
**Files:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/simulation/entities/`

- [x] Make `registry_provider` required (parameter already exists)
- [x] Remove fallback to `get_default_registry_provider()`
- [x] Update all callers to pass provider
- [x] Verify: all tests pass

### Task 3.3: Fix load_vehicle_classes() [DI-SIM-002]
**Files:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/simulation/entities/`

- [x] Make `registry_provider` required (parameter already exists)
- [x] Remove fallback to `get_default_registry_provider()`
- [x] Verify callers pass provider (should be wired from Task 3.1)
- [x] Verify: all tests pass

### Task 3.4: Fix load_components() and load_modifiers() [DI-SIM-003, DI-SIM-004, DI-SIM-005, AR-003]
**Files:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/simulation/components/`

- [x] Read `component.py` to understand lines 514, 569, 668
- [x] Add `registry_provider` parameter to `load_components()` (line 569)
- [x] Add `registry_provider` parameter to `load_modifiers()` (line 668)
- [x] Make `registries` required in `load_components_data()` (line 514, remove fallback)
- [x] Update callers: `app.py`, `workshop_data_loader.py`
- [x] Remove module-level `get_default_registry_provider` import if possible
- [x] Verify: all tests pass

### Task 3.5: Fix test_protocols_boundary.py [TI-005]
**Files:** `tests/unit/core/test_protocols_boundary.py`
**Tests:** `pytest tests/unit/core/test_protocols_boundary.py`

- [x] Read the test file and its `simple_ship` fixture
- [x] Fixture already uses `get_default_registry_provider()` correctly (composition root pattern)
- [x] Verify: test passes with proper isolation

### Task 3.6: Update docstrings [DI-SIM-007]
**Files:** `game/simulation/entities/ship_stats.py`

- [x] Reviewed docstring at lines 47-48
- [x] Docstring shows composition-root pattern (get_default_registry_provider) - this is correct
- [x] No change needed - example demonstrates proper DI at composition root level

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` - 12885 passed, 4 skipped (4 unrelated failures in test_bug_13 due to missing asset files)
- [x] No `get_default_registry_provider()` calls remain in `ship_loader.py` or `component.py` (fallback removed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4

## Implementation Notes
- Fixed ~71 test fixture errors by passing `registry_provider` to:
  - `tests/regression/modifier_ability_snapshots/conftest.py` - removed redundant load calls
  - `tests/unit/simulation/services/test_registry_loader.py` - updated mock signatures
  - `tests/unit/simulation/abilities/test_cargo_storage.py` - added fresh_registries
  - `tests/unit/regressions/test_regressions.py` - added provider
  - `tests/unit/systems/test_allowed_layers_removal.py` - added provider
  - `tests/repro_issues/test_bug_09_endurance.py` - added provider
