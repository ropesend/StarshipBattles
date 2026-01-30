# Phase 2: Registry & Service Extraction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress (Task 2.1 Complete)
**Objective:** Reduce global state hazards and cross-layer coupling. Enables safer refactoring.

---

## Tasks

### Task 2.1: Create RegistryManager Service [Medium]
**File:** `game/core/registry.py` (RegistryManager already exists)
**Issue:** Risk 5.1 - Global registry mutation, stale references
**Tests:** `pytest tests/unit/core/test_registry_manager_reload.py`

- [x] Add `reload_all_from_directory(data_dir: Path) -> bool` method
  - Clears all registries and reloads from directory
  - Supports test_* prefixed files for test data directories
  - Returns False for invalid directories
  - Raises RuntimeError if frozen
- [x] RegistryManager already has:
  - `clear()` for clearing registries
  - `.components`, `.modifiers`, `.vehicle_classes` accessors
- [x] Add proper error handling and logging
- [x] Created 12 tests for reload_all_from_directory

**Notes:** RegistryManager already existed. Added reload_all_from_directory() method.

---

### Task 2.2: Refactor BuilderSceneGUI Registry Access [Medium]
**File:** `game/ui/screens/builder/main.py`
**Issue:** AR-03 lines 859-1002 - Direct registry manipulation
**Tests:** `pytest tests/unit/builder/`

- [ ] Import `RegistryManager` instead of individual registries
- [ ] Replace lines 859-869 (direct registry clears) with `registry_manager.reload_all_from_directory()`
- [ ] Remove imports of `COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`, `VEHICLE_CLASSES`
- [ ] Verify: Data reload in builder still works

**Notes:**

---

### Task 2.3: Create ShipFactory Service [Simple]
**File:** Create `game/simulation/services/ship_factory.py`
**Issue:** Lines 90-91, 972 in BuilderSceneGUI - Direct ship creation
**Tests:** `pytest tests/unit/simulation/`

- [ ] Create `ShipFactory` with:
  - `create_default_ship(name, x, y, color, ship_class=None, registries=None) -> Ship`
  - `create_from_template(template_path, x, y) -> Ship`
- [ ] Refactor BuilderSceneGUI lines 90-91 to use factory
- [ ] Refactor BuilderSceneGUI line 972 to use factory
- [ ] Verify: Ship creation in builder works

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
