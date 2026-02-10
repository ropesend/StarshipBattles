# Phase 2: Core → Simulation Violation Fix

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-90 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract `reload_all_from_directory()` from `RegistryManager` (Core layer) to a new module in the Simulation layer, eliminating the only real architectural layer violation.

---

## Tasks

### Task 2.1: Create registry_loader.py in simulation layer [Medium]
**New File:** `game/simulation/services/registry_loader.py`
**Source:** `game/core/registry.py` lines 309-402
**Tests:** `pytest tests/unit/core/test_registry_manager_reload.py -v`

- [ ] Create `game/simulation/services/registry_loader.py` with function `reload_registries_from_directory(registry_manager, data_dir) -> bool`
- [ ] Move full body of `RegistryManager.reload_all_from_directory()` into this free function
- [ ] The 3 simulation imports become legal **top-level imports**:
  - `from game.simulation.components.component import load_modifiers, load_components`
  - `from game.simulation.entities.ship_loader import load_vehicle_classes`
- [ ] First parameter is `registry_manager` (the RegistryManager instance) instead of `self`
- [ ] Keep the `_check_frozen()` call as `registry_manager._check_frozen()` — or use public API if available
- [ ] Verify: `python -c "from game.simulation.services.registry_loader import reload_registries_from_directory; print('OK')"`

**Notes:**

---

### Task 2.2: Remove method from RegistryManager [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/ -v`

- [ ] Remove `reload_all_from_directory()` method (lines 309-402) from `RegistryManager`
- [ ] Verify no other callers exist (only `tests/unit/core/test_registry_manager_reload.py` calls it)
- [ ] Verify: `game/core/registry.py` has zero imports from `game.simulation`

**Notes:**

---

### Task 2.3: Update test file [Simple]
**File:** `tests/unit/core/test_registry_manager_reload.py`
**Tests:** `pytest tests/unit/core/test_registry_manager_reload.py -v`

- [ ] Change import: `from game.simulation.services.registry_loader import reload_registries_from_directory`
- [ ] Change all calls from `manager.reload_all_from_directory(path)` to `reload_registries_from_directory(manager, path)`
- [ ] Verify: `pytest tests/unit/core/test_registry_manager_reload.py -v` — all pass
- [ ] Verify: `pytest tests/ -n 12` — all 7353+ tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `game/core/registry.py` has no imports from `game.simulation`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
