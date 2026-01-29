# Phase 2: Registry & Service Extraction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Reduce global state hazards and cross-layer coupling. Enables safer refactoring.

---

## Tasks

### Task 2.1: Create RegistryManager Service [Medium]
**File:** Create `game/core/registry_manager.py`
**Issue:** Risk 5.1 - Global registry mutation, stale references
**Tests:** `pytest tests/unit/core/`

- [ ] Create `RegistryManager` class with:
  - `reload_all_from_directory(data_dir: Path) -> bool`
  - `clear_all() -> None`
  - `get_component_registry() -> Dict`
  - `get_modifier_registry() -> Dict`
  - `get_vehicle_classes() -> Dict`
- [ ] Migrate registry operations from `game/core/registry.py`
- [ ] Add proper error handling and validation
- [ ] Verify: All registry access still works

**Notes:**

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
