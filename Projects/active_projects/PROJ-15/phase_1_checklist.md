# Phase 1: Pure Alias Files [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete single-line alias files and update their callers

---

## Tasks

### Task 1.1: Delete `builder_viewmodel.py` [Simple]
**Delete:** `game/ui/screens/builder_viewmodel.py`
**Tests:** `pytest tests/unit/builder/test_builder_viewmodel.py tests/repro_issues/test_bug_13_clear_removes_hull.py -v`

- [x] Update `tests/unit/builder/test_builder_viewmodel.py`:
  - Change `from game.ui.screens.builder_viewmodel import BuilderViewModel`
  - To `from game.ui.screens.workshop_viewmodel import WorkshopViewModel`
  - Update class references from `BuilderViewModel` to `WorkshopViewModel`
- [x] Update `tests/repro_issues/test_bug_13_clear_removes_hull.py`:
  - Change `from game.ui.screens.builder_viewmodel import BuilderViewModel` (line ~47)
  - To `from game.ui.screens.workshop_viewmodel import WorkshopViewModel`
  - Update class references
- [x] Delete `game/ui/screens/builder_viewmodel.py`
- [x] Verify: Run tests - should pass

**Notes:** All 13 tests pass. Only changed the ViewModel import in test_bug_13 since it still uses BuilderSceneGUI (Phase 5).

---

### Task 1.2: Delete `builder_data_loader.py` [Simple]
**Delete:** `game/ui/screens/builder_data_loader.py`
**Tests:** `pytest tests/unit/builder/test_builder_data_loader.py -v`

- [x] Update `tests/unit/builder/test_builder_data_loader.py`:
  - Change all 8 imports from `BuilderDataLoader` to `WorkshopDataLoader`
  - Import: `from game.ui.screens.workshop_data_loader import WorkshopDataLoader, LoadResult`
  - Update all class references
- [x] Delete `game/ui/screens/builder_data_loader.py`
- [x] Verify: Run tests - should pass

**Notes:** All 8 tests pass. Updated class names and docstrings.

---

### Task 1.3: Delete `builder_event_router.py` [Simple]
**Delete:** `game/ui/screens/builder_event_router.py`
**Tests:** `pytest tests/unit/builder/ -v`

- [x] Verify no external imports of `BuilderEventRouter` exist (search confirmed none)
- [x] Delete `game/ui/screens/builder_event_router.py`
- [x] Verify: Run tests - should pass

**Notes:** Only reference was in builder_screen.py which imports directly from workshop_event_router.py. All 106 tests pass.

---

### Task 1.4: Delete `ship_builder_service.py` [Simple]
**Delete:** `game/simulation/services/ship_builder_service.py`
**Tests:** `pytest tests/unit/services/ -v`

- [x] Update `game/simulation/services/__init__.py`:
  - Remove line 3: `from .ship_builder_service import ShipBuilderService, ShipBuilderResult`
  - Remove from `__all__`: `'ShipBuilderService'`, `'ShipBuilderResult'`
- [x] Update `game/ui/screens/workshop_viewmodel.py` (line 14):
  - Change `from game.simulation.services import ShipBuilderService, ShipBuilderResult`
  - To `from game.simulation.services.vehicle_design_service import VehicleDesignService, DesignResult`
  - Update all references: `ShipBuilderService` → `VehicleDesignService`, `ShipBuilderResult` → `DesignResult`
- [x] Update `tests/unit/services/test_ship_builder_service.py`:
  - Rename file to `test_vehicle_design_service.py`
  - Update imports to use `VehicleDesignService, DesignResult`
  - Update all class references
- [x] Delete `game/simulation/services/ship_builder_service.py`
- [x] Verify: Run tests - should pass

**Notes:** All 81 service tests pass. Also updated the __init__.py to export VehicleDesignService and DesignResult directly.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/builder/ tests/unit/services/ tests/repro_issues/ -v` - all pass (252 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
