# Phase 2: Registry & Service Extraction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] ~~Import `RegistryManager` instead of individual registries~~ Used WorkshopDataLoader instead (better abstraction)
- [x] ~~Replace lines 859-869 (direct registry clears) with `registry_manager.reload_all_from_directory()`~~ Replaced with WorkshopDataLoader.load_all()
- [x] Remove imports of `COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`, `VEHICLE_CLASSES` - No longer imported
- [x] Verify: Data reload in builder still works - 151 builder tests pass

**Notes:** Used WorkshopDataLoader instead of RegistryManager.reload_all_from_directory() because:
1. WorkshopDataLoader already exists and handles StrategyManager (which RegistryManager doesn't)
2. WorkshopDataLoader provides LoadResult with success/errors/warnings/default_class
3. More appropriate abstraction for UI layer (returns structured result vs bool)
4. Reduces ~100 lines of duplicate code in _reload_data()

---

### Task 2.3: Create ShipFactory Service [Simple]
**File:** Create `game/simulation/services/ship_factory.py`
**Issue:** Lines 90-91, 972 in BuilderSceneGUI - Direct ship creation
**Tests:** `pytest tests/unit/simulation/`

- [x] Create `ShipFactory` - Already exists at game/ui/services/ship_factory.py (PROJ-43)
- [x] Refactor BuilderSceneGUI lines 90-91 to use factory - Already done (PROJ-43)
- [x] Refactor BuilderSceneGUI line 972 to use factory - Already done (now line 904)
- [x] Verify: Ship creation in builder works - Tests pass

**Notes:** PROJ-43 already created ShipFactory in game/ui/services/ and refactored BuilderSceneGUI to use it. Task was already complete.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ --testmon` - all tests pass (5409 passed, 3 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
