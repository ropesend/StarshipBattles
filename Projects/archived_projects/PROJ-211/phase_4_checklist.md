# Phase 4: UI Services

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-211 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Make UI services follow VehicleClassService strict-DI pattern (require provider, no fallback)
**Priority:** Medium
**Risk:** Low - All services already support the parameter
**Depends on:** None (independent of other phases)

---

## Tasks

### Task 4.1: Fix WorkshopContext.__post_init__() [DI-UI-002, AR-010]
**Files:** `game/ui/screens/workshop_context.py`, `game/app.py`
**Tests:** `pytest tests/unit/builder/`

- [x] Read `workshop_context.py` to understand `__post_init__` fallback
- [x] Update `app.py` methods `start_builder()` and `_create_workshop_context()` to pass `self.registries`
- [x] Update `WorkshopContext.standalone()` and `WorkshopContext.integrated()` to require registries
- [x] Remove `__post_init__` fallback to `get_default_registry_provider()`
- [x] Update test file `test_workshop_context_di.py` (TI-006) - remove backward-compat test
- [x] Verify: all tests pass

### Task 4.2: Fix ComponentService [DI-UI-005, AR-007]
**Files:** `game/ui/services/component_service.py`
**Tests:** `pytest tests/unit/ui/services/`

- [x] Make `registry_provider` required in constructor (match VehicleClassService pattern)
- [x] Remove `_get_provider()` lazy fallback method (kept method but removed fallback logic)
- [x] Remove module-level `get_default_registry_provider` import
- [x] Update all callers to pass provider explicitly (ModifierLogic.init_service())
- [x] Verify: all tests pass

### Task 4.3: Fix ShipFactory [DI-UI-003, AR-008]
**Files:** `game/ui/services/ship_factory.py`
**Tests:** `pytest tests/unit/ui/services/`

- [x] Make `registry_provider` required in constructor
- [x] Remove `_get_registries()` triple-fallback method (kept method but removed fallback logic)
- [x] Update all callers (setup_screen.py, setup_data_io.py) to use lazy init
- [x] Verify: all tests pass

### Task 4.4: Fix DesignLoaderAdapter [DI-UI-004, AR-009]
**Files:** `game/ui/services/design_loader_adapter.py`
**Tests:** `pytest tests/unit/ui/services/`

- [x] Make `registry_provider` required when `design_loader` is None
- [x] Remove module-level `get_default_registry_provider` import
- [x] Update test file `test_design_loader_adapter.py` (TI-007) - remove fallback test
- [x] Update all callers (ship_io.py, strategy_build_queue_manager.py, workshop_screen.py) to pass provider
- [x] Verify: all tests pass

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` - full suite passes (12872 passed, 1 skipped)
- [x] All 4 UI services match VehicleClassService strict-DI pattern
- [x] No `get_default_registry_provider()` calls remain in UI services (lazy init wrappers used)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5

## Notes
- ComponentService now raises ValidationException if registry_provider is None
- ShipFactory now raises ValidationException if registry_provider is None
- DesignLoaderAdapter raises ValidationException if both design_loader and registry_provider are None
- Lazy initialization pattern used for module-level services in setup_screen.py, setup_data_io.py, ship_io.py, strategy_build_queue_manager.py
- ModifierLogic uses class-level init_service() pattern - called from DesignWorkshopScreen.__init__
