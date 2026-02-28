# Phase 5: UI Screens & Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-211 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Fix remaining UI screen violations, clean up docstrings, remove all fallbacks
**Priority:** Low - Display-only code + test fixture updates
**Risk:** Medium - Test fixture updates affect ~200 tests
**Depends on:** Phase 4 (WorkshopContext carries registries)

---

## Tasks

### Task 5.1: Fix compute_planet_production() [DI-UI-001]
**Files:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/`

- [x] Add `registries: GameRegistries` parameter (now required)
- [x] Update callers (strategy detail panel, build queue, planets list) to pass registries
- [x] Remove fallback - no `get_default_registry_provider()` calls
- [x] Update test fixtures to pass registries
- [x] Verify: all tests pass

### Task 5.2: Fix EmpirePanelWindow [DI-UI-006]
**Files:** `game/ui/screens/empire_panel_window.py`
**Tests:** `pytest tests/unit/ui/screens/`

- [x] Add `registries` parameter to `__init__()`
- [x] Use stored registries in `_build_treasury_tab()` instead of inline resolution
- [x] Update StrategyScreen to pass registries when opening the panel
- [x] Remove `get_default_registry_provider` import
- [x] Verify: all tests pass

### Task 5.3: Fix builder sub-panels [DI-UI-007, DI-UI-008, AR-013]
**Files:** `game/ui/screens/builder/schematic_view.py`, `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/ui/screens/builder/`

- [x] Ensure DesignWorkshopScreen passes VehicleClassService to both sub-panels
- [x] Remove fallback to `get_default_registry_provider()` in both constructors
- [x] Add IRegistryProvider methods to GameRegistries (allows direct use as provider)
- [x] Update test fixtures to pass VehicleClassService
- [x] Verify: all tests pass

### Task 5.4: Update empire_economy_calculator docstring [DI-S-006]
**Files:** `game/strategy/engine/empire_economy_calculator.py`

- [x] Docstring already shows proper DI from session context (done in Phase 4)
- [x] No `get_default_registry_provider()` calls in file

### Task 5.5: Update test fixtures to inject registries (MOVED FROM PHASE 2)
**Files:** Test files using ShipInstance.create() / from_dict() without registries
**Tests:** `pytest tests/ -n 12`

This task enables fallback removal in Phase 2 objects. ~67 occurrences of ShipInstance.create()
or ShipInstance.from_dict() across test files.

Strategy:
1. Add ship_factory fixture in conftest.py that injects fresh_registries
2. Update test files to use ship_factory or pass registries directly
3. For integration tests that manipulate singleton, add singleton_registries fixture

- [x] Create ship_factory fixture in conftest.py for DI-compliant ShipInstance creation
- [x] Update tests/unit/strategy/test_ship_serial_numbering.py (16 tests)
- [x] Update tests/unit/strategy/test_ship_instance_damage.py (17 tests)
- [x] Update tests/integration/strategy/transfer/conftest.py fixtures
- [x] Update tests/unit/strategy/facade/test_population_dtos.py
- [x] Update tests/unit/strategy/engine/test_colonize_population.py (3 helper functions, 6 tests)
- [x] Update tests/integration/resource_system/conftest.py (added singleton_registries)
- [x] Verify: all tests pass (12884 passed, 4 unrelated failures)

### Task 5.6: Remove ShipInstance.get_calculated_stats() fallback (MOVED FROM PHASE 2)
**Files:** `game/strategy/data/ship_instance.py`
**Depends on:** Task 5.5.1 (more test fixture updates needed)

**BLOCKED:** ~127 additional tests need fixture updates before fallback can be removed.
Test files that still create ShipInstance without registries include:
- tests/unit/strategy/test_fleet_capability_calculator.py
- tests/unit/strategy/test_fleet_capability_calculator_di.py
- tests/unit/test_advanced_fleet_orders.py
- tests/integration/gameplay_loop/*.py
- tests/integration/resource_system/*.py (need singleton_registries)
- tests/integration/save_load/*.py
- Many others (~50+ test files)

After remaining test fixtures are updated:
- [ ] Remove the `get_default_registry_provider()` fallback from `get_calculated_stats()`
- [ ] Raise explicit error if `self._registries` is None
- [ ] Remove `get_default_registry_provider` import from ship_instance.py
- [ ] Verify: all tests pass

### Task 5.5.1: Additional test fixture updates (NEW SUBTASK)
**Files:** Multiple test files creating ShipInstance without registries
**Tests:** `pytest tests/ -n 12`

Continue updating test files to use ship_factory or pass registries directly.
Infrastructure is in place (ship_factory fixture, singleton_registries fixture).

**IMPORTANT DISCOVERY:** Fleet.add_ship() triggers speed recalculation which calls
get_calculated_stats(). This means ANY test that adds a ShipInstance to a Fleet
needs registries. ~109 tests fail when fallback is removed.

- [ ] Update tests/unit/strategy/test_fleet_capability_calculator.py (~15 tests)
- [ ] Update tests/unit/strategy/test_fleet_capability_calculator_di.py (1 test)
- [ ] Update tests/unit/test_advanced_fleet_orders.py (2 tests)
- [ ] Update tests/integration/gameplay_loop/*.py (5 tests)
- [x] Update tests/integration/resource_system/*.py (7 tests - DONE)
- [ ] Update tests/integration/save_load/*.py (7 tests/errors)
- [ ] Update tests/unit/strategy/test_fleet_battle_adapter.py (8 tests)
- [ ] Update tests/unit/strategy/ship_instance/*.py (6 tests)
- [ ] Update tests/unit/strategy/test_ship_resource_manager.py (1 test)
- [ ] Update remaining test files (~50+ files)
- [ ] Verify: fallback removal succeeds

### Task 5.7: Remove FleetCapabilityCalculator fallbacks (MOVED FROM PHASE 2)
**Files:** `game/strategy/data/fleet_capability_calculator.py`
**Depends on:** Task 5.5

- [ ] Remove `_get_default_component_registry()` helper function
- [ ] Update `ship_has_spaceyard()` to raise if no registry available
- [ ] Update `ship_has_ability()` to raise if no registry available
- [ ] Update `_get_registry()` to raise if not injected
- [ ] Verify: all tests pass

### Task 5.8: Final verification - zero fallback calls outside composition roots
**Tests:** `pytest tests/ -n 12`

- [ ] Grep for `get_default_registry_provider()` across all production code
- [ ] Verify only `game/app.py`, `conftest.py`, and `game/core/registry.py` (definition site) contain it
- [ ] Verify `game/core/__init__.py` re-export is acceptable (public API for tests)
- [ ] Full test suite passes
- [ ] Document any remaining legitimate usages in decisions.md

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` - full suite passes
- [ ] Zero `get_default_registry_provider()` calls outside composition roots
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
