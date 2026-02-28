# Phase 3: Initialization Functions (Simulation Layer)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-211 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Thread registry_provider through initialization/boot functions in component.py and ship_loader.py
**Priority:** Medium - Independent of runtime path, affects boot sequence
**Risk:** Low - Only 2-4 call sites per function
**Depends on:** None (independent of Phases 1-2)

---

## Tasks

### Task 3.1: Fix initialize_ship_data() [DI-SIM-006]
**Files:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/simulation/entities/`

- [ ] Read `ship_loader.py` to understand `initialize_ship_data()` call chain
- [ ] Add `registry_provider` parameter to `initialize_ship_data()`
- [ ] Forward to internal calls (`load_vehicle_classes`, `get_or_create_validator`)
- [ ] Update all callers (app.py, test files) to pass provider
- [ ] Verify: all tests pass

### Task 3.2: Fix get_or_create_validator() [DI-SIM-001]
**Files:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/simulation/entities/`

- [ ] Make `registry_provider` required (parameter already exists)
- [ ] Remove fallback to `get_default_registry_provider()`
- [ ] Update all callers to pass provider
- [ ] Verify: all tests pass

### Task 3.3: Fix load_vehicle_classes() [DI-SIM-002]
**Files:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/simulation/entities/`

- [ ] Make `registry_provider` required (parameter already exists)
- [ ] Remove fallback to `get_default_registry_provider()`
- [ ] Verify callers pass provider (should be wired from Task 3.1)
- [ ] Verify: all tests pass

### Task 3.4: Fix load_components() and load_modifiers() [DI-SIM-003, DI-SIM-004, DI-SIM-005, AR-003]
**Files:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/simulation/components/`

- [ ] Read `component.py` to understand lines 514, 569, 668
- [ ] Add `registry_provider` parameter to `load_components()` (line 569)
- [ ] Add `registry_provider` parameter to `load_modifiers()` (line 668)
- [ ] Make `registries` required in `load_components_data()` (line 514, remove fallback)
- [ ] Update callers: `app.py`, `workshop_data_loader.py`
- [ ] Remove module-level `get_default_registry_provider` import if possible
- [ ] Verify: all tests pass

### Task 3.5: Fix test_protocols_boundary.py [TI-005]
**Files:** `tests/unit/core/test_protocols_boundary.py`
**Tests:** `pytest tests/unit/core/test_protocols_boundary.py`

- [ ] Read the test file and its `simple_ship` fixture
- [ ] Update fixture to use `fresh_registries` or injected registries instead of global state
- [ ] Verify: test passes with proper isolation

### Task 3.6: Update docstrings [DI-SIM-007]
**Files:** `game/simulation/entities/ship_stats.py`

- [ ] Remove/update docstring that teaches the anti-pattern (lines 47-48)
- [ ] Show proper DI example instead

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` - full suite passes
- [ ] No `get_default_registry_provider()` calls remain in `ship_loader.py` or `component.py`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
