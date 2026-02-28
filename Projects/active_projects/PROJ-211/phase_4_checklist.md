# Phase 4: UI Services

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-211 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make UI services follow VehicleClassService strict-DI pattern (require provider, no fallback)
**Priority:** Medium
**Risk:** Low - All services already support the parameter
**Depends on:** None (independent of other phases)

---

## Tasks

### Task 4.1: Fix WorkshopContext.__post_init__() [DI-UI-002, AR-010]
**Files:** `game/ui/screens/workshop_context.py`, `game/app.py`
**Tests:** `pytest tests/unit/builder/`

- [ ] Read `workshop_context.py` to understand `__post_init__` fallback
- [ ] Update `app.py` methods `start_builder()` and `_create_workshop_context()` to pass `self.registries`
- [ ] Update `WorkshopContext.standalone()` and `WorkshopContext.integrated()` to require registries
- [ ] Remove `__post_init__` fallback to `get_default_registry_provider()`
- [ ] Update test file `test_workshop_context_di.py` (TI-006) - remove backward-compat test
- [ ] Verify: all tests pass

### Task 4.2: Fix ComponentService [DI-UI-005, AR-007]
**Files:** `game/ui/services/component_service.py`
**Tests:** `pytest tests/unit/ui/services/`

- [ ] Make `registry_provider` required in constructor (match VehicleClassService pattern)
- [ ] Remove `_get_provider()` lazy fallback method
- [ ] Remove module-level `get_default_registry_provider` import
- [ ] Update all callers to pass provider explicitly
- [ ] Verify: all tests pass

### Task 4.3: Fix ShipFactory [DI-UI-003, AR-008]
**Files:** `game/ui/services/ship_factory.py`
**Tests:** `pytest tests/unit/ui/services/`

- [ ] Make `registry_provider` required in constructor
- [ ] Remove `_get_registries()` triple-fallback method
- [ ] Update all callers (battle setup, formation editor, test lab) to pass provider
- [ ] Verify: all tests pass

### Task 4.4: Fix DesignLoaderAdapter [DI-UI-004, AR-009]
**Files:** `game/ui/services/design_loader_adapter.py`
**Tests:** `pytest tests/unit/ui/services/`

- [ ] Make `registry_provider` required when `design_loader` is None
- [ ] Remove module-level `get_default_registry_provider` import
- [ ] Update test file `test_design_loader_adapter.py` (TI-007) - remove fallback test
- [ ] Update all callers to pass provider
- [ ] Verify: all tests pass

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` - full suite passes
- [ ] All 4 UI services match VehicleClassService strict-DI pattern
- [ ] No `get_default_registry_provider()` calls remain in UI services
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
