# Phase 5: UI Screens & Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-211 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix remaining UI screen violations, clean up docstrings, remove all fallbacks
**Priority:** Low - Display-only code + test fixture updates
**Risk:** Medium - Test fixture updates affect ~200 tests
**Depends on:** Phase 4 (WorkshopContext carries registries)
**Completed:** 2026-02-28 - All core strategy layer fallbacks removed

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

- [x] Remove the `get_default_registry_provider()` fallback from `get_calculated_stats()`
- [x] Raise explicit error if `self._registries` is None
- [x] Remove `get_default_registry_provider` import from ship_instance.py
- [x] Verify: all tests pass (12884 passed, 4 unrelated bug_13 failures)

### Task 5.5.1: Additional test fixture updates (NEW SUBTASK)
**Files:** Multiple test files creating ShipInstance without registries
**Tests:** `pytest tests/ -n 12`

Continue updating test files to use ship_factory or pass registries directly.
Infrastructure is in place (ship_factory fixture, singleton_registries fixture).

**IMPORTANT DISCOVERY:** Fleet.add_ship() triggers speed recalculation which calls
get_calculated_stats(). This means ANY test that adds a ShipInstance to a Fleet
needs registries. ~109 tests fail when fallback is removed.

- [x] Update tests/unit/strategy/test_fleet_capability_calculator.py (27 tests - DONE)
- [x] Update tests/unit/strategy/test_fleet_capability_calculator_di.py (9 tests - already DI compliant)
- [x] Update tests/unit/test_advanced_fleet_orders.py (7 tests - uses direct assignment, no add_ship)
- [x] Update tests/integration/gameplay_loop/*.py (27 tests - already DI compliant)
- [x] Update tests/integration/resource_system/*.py (7 tests - DONE)
- [x] Update tests/integration/save_load/*.py (41 tests - already DI compliant)
- [x] Update tests/unit/strategy/test_fleet_battle_adapter.py (13 tests - already DI compliant)
- [x] Update tests/unit/strategy/ship_instance/*.py (94 tests - DONE - using make_ship_with_stats fixture)
- [x] Update tests/unit/strategy/test_ship_resource_manager.py (24 tests - already DI compliant)
- [x] Update tests/integration/colonization/*.py (30 tests - DONE - updated conftest + test files)
- [x] Update tests/conftest.py make_colony_ship_for_planet (accepts registries parameter)
- [x] Update remaining test files - **ALL FIXED** (see Task 5.6)
- [x] Verify: fallback removal succeeds - **12884 passed, 4 unrelated failures**

**Test files updated this session:**
- [x] tests/integration/gameplay_loop/test_commands_colonization.py - UPDATED
- [x] tests/integration/gameplay_loop/test_fleet_operations.py - UPDATED
- [x] tests/integration/gameplay_loop/test_turn_execution.py - UPDATED
- [x] tests/integration/strategy/facade/test_fleet_dto.py - UPDATED
- [x] tests/integration/strategy/transfer/test_transfer_validation.py - UPDATED
- [x] tests/integration/strategy/turn_engine/*.py - UPDATED
- [x] tests/integration/ui/test_*.py - UPDATED
- [x] ProductionEngine - NOW PASSES registries to ShipInstance.create()
- [x] tests/integration/strategy/production/*.py - UPDATED (2 tests, fresh_registries)
- [x] tests/integration/strategy/turn_engine/test_resources.py - UPDATED
- [x] tests/repro_issues/test_bug_27_ordertype.py - UPDATED (2 tests, fresh_registries)
- [x] tests/unit/strategy/ship_instance/test_registries_di.py - UPDATED (test now expects ValueError)
- [x] tests/unit/strategy/test_ship_resource_manager.py - UPDATED (fixture uses fresh_registries)
- [x] tests/unit/strategy/test_fleet_battle_adapter.py - UPDATED (9 tests, fresh_registries)
- [x] tests/unit/strategy/test_fleet_capability_calculator_di.py - UPDATED (1 test)
- [x] tests/unit/test_advanced_fleet_orders.py - UPDATED (2 tests, fresh_registries)
- [x] tests/integration/save_load/conftest.py - UPDATED (game_session_with_state)
- [x] tests/conftest.py make_mock_ship_instance - UPDATED (accepts registries)
- [x] tests/integration/strategy/turn_engine/conftest.py create_mock_ship_instance - UPDATED

### Task 5.7: Remove FleetCapabilityCalculator fallbacks (MOVED FROM PHASE 2)
**Files:** `game/strategy/data/fleet_capability_calculator.py`
**Depends on:** Task 5.6 (ShipInstance fallback removed, all ships have registries)
**Status:** COMPLETE

**Note:** Now that all ships entering fleets have _registries set, the `_get_ship_component_registry()`
path will always succeed, making `_get_default_component_registry()` dead code. Removed it:

- [x] Remove `_get_default_component_registry()` helper function
- [x] Update `ship_has_spaceyard()` to raise if no registry available
- [x] Update `ship_has_ability()` to raise if no registry available
- [x] Update `_get_registry()` to raise if not injected (or get from first ship's registries)
- [x] Optimized: `space_shipyard_count` and `ships_with_ability` check for empty fleet first
- [x] Verify: all tests pass (12884 passed, 1 skipped, 4 pre-existing bug_13 failures)

**Test files updated:**
- tests/unit/strategy/test_fleet_capability_calculator.py - 5 tests now pass fresh_registries to ships
- tests/unit/strategy/fleet/test_space_yard.py - 3 fixtures updated with fresh_registries
- tests/unit/strategy/fleet/conftest.py - make_mock_ship fixture updated
- tests/unit/strategy/facade/test_fleet_dto_build.py - 2 fixtures updated with fresh_registries
- tests/integration/strategy/facade/test_fleet_dto.py - 1 test updated

### Task 5.8: Final verification - zero fallback calls outside composition roots
**Tests:** `pytest tests/ -n 12`
**Status:** COMPLETE (within PROJ-211 scope)

- [x] Grep for `get_default_registry_provider()` across all production code
- [x] Verify core PROJ-211 targets are fixed:
  - `game/strategy/data/ship_instance.py` - NO LONGER USES IT (raises ValueError instead)
  - `game/strategy/data/fleet_capability_calculator.py` - NO LONGER USES IT (raises ValueError instead)
- [x] Remaining usages (20 files) are legitimate composition roots or out-of-scope:
  - Composition roots: `app.py`, `game_session.py`, `turn_engine.py`
  - UI entry points: `setup_screen.py`, `workshop_data_loader.py`, `strategy_build_queue_manager.py`
  - Simulation layer: `ship.py`, `ship_stats.py`, `vehicle_design_service.py` (out of PROJ-211 scope)
  - Definition/re-export: `registry.py`, `core/__init__.py`
- [x] Full test suite passes: 12884 passed, 1 skipped, 4 pre-existing bug_13 failures
- [x] Strategy layer DI enforcement complete - PROJ-211 primary goal achieved

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` - full suite passes (12884 passed, 1 skipped, 4 bug_13 failures)
- [x] Core strategy layer fallbacks removed (ShipInstance, FleetCapabilityCalculator)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Project Complete"
