# Phase 3: Test File Splitting (Monoliths)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-48 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Split 50 test files over 500 LOC into smaller, focused files.
**Issues Addressed:** TSR-005

---

## Tasks

### Task 3.1: Split Critical Monoliths (>1000 LOC) [Complex]

#### 3.1.1: Split test_ship_stats_calculator.py (1775 LOC -> 5 files) ✅ COMPLETE
**Source:** `tests/unit/strategy/test_ship_stats_calculator.py` (was test_ship_stats_service.py, renamed in PROJ-46)
**Target:** `tests/unit/strategy/ship_stats/`
**Tests:** `pytest tests/unit/strategy/ship_stats/ -v`

- [x] Create directory `tests/unit/strategy/ship_stats/`
- [x] Create `tests/unit/strategy/ship_stats/__init__.py`
- [x] Read source file and identify test class groupings
- [x] Create `conftest.py` with shared fixtures from original file
- [x] Split into these files:
  - [x] `test_basics.py` - TestShipStatsCalculatorBasics, TestDamageEffectiveness, TestStatAggregation, TestComponentIdMatching, TestIntegrationScenarios
  - [x] `test_warp.py` - TestWarpCapability, TestHasWarpCapability classes
  - [x] `test_resources.py` - TestGenericDictAccumulators, TestTriggerTypes, TestCustomResources classes
  - [x] `test_toggles.py` - TestComponentToggles class
  - [x] `test_modifiers.py` - TestBugDocumentation, TestIntegrationProj08, TestModifierApplication classes
- [x] Update imports in each new file
- [x] Delete original file after verification
- [x] Verify: `pytest tests/unit/strategy/ship_stats/ -v` - all tests pass (70 passed)
- [x] Verify: Same number of tests as before split (70 = 70)

**Notes:** File was renamed to test_ship_stats_calculator.py during PROJ-46. Split into 5 files (test_basics.py, test_warp.py, test_resources.py, test_toggles.py, test_modifiers.py).

---

#### 3.1.2: Split test_ship_instance_proj08.py (1458 LOC -> 3 files) ✅ COMPLETE
**Source:** `tests/unit/strategy/test_ship_instance_proj08.py`
**Target:** `tests/unit/strategy/ship_instance/`
**Tests:** `pytest tests/unit/strategy/ship_instance/ -v`

- [x] Create directory `tests/unit/strategy/ship_instance/`
- [x] Create `__init__.py` and `conftest.py`
- [x] Split into:
  - [x] `test_component_toggles.py` - Component toggle related classes (TestComponentTogglesField, TestSetComponentEnabled, TestIsComponentEnabled, TestCacheInvalidation, TestStatsIntegration)
  - [x] `test_resources.py` - Resource management classes (TestGetResourceCapacity, TestGetCurrentResource, TestConsumeResource, TestGetAllResourceCostsPerHex, TestGetAllResourceCostsPerTurn, TestGetWarpResourceCosts, TestResourceConvenienceMethods, TestResourceMethodInteractions)
  - [x] `test_serialization.py` - Serialization and edge case classes (TestToDictSerialization, TestFromDictSerialization, TestClonePreservation, TestAdditionalCoverage, TestEdgeCases)
- [x] Delete original file after verification
- [x] Verify: All tests pass (71 passed), same count (71 = 71)

**Notes:** Split into 3 files with conftest.py for shared fixture.

---

#### 3.1.3: Split test_battle_controller.py (1425 LOC -> 4 files) ✅ COMPLETE
**Source:** `tests/unit/simulation/test_battle_controller.py`
**Target:** `tests/unit/simulation/battle_controller/`
**Tests:** `pytest tests/unit/simulation/battle_controller/ -v`

- [x] Create directory `tests/unit/simulation/battle_controller/`
- [x] Create `__init__.py` and `conftest.py`
- [x] Split into:
  - [x] `test_initialization.py` - TestBattleControllerInit, TestBattleControllerConfigure
  - [x] `test_execution.py` - TestBattleControllerStart, TestBattleControllerUpdate, TestBattleControllerRunHeadless, TestBattleControllerRunTicks
  - [x] `test_mechanics.py` - TestBattleControllerAddShips, TestBattleControllerAddShipsFromState, TestBattleControllerRetreat, TestBattleControllerReinforcements, TestBattleControllerFindNearestEdge, TestBattleControllerIsAtMapEdge
  - [x] `test_utilities.py` - TestBattleControllerStateSaveLoad, TestBattleControllerQueryMethods, TestBattleControllerCallbacks, TestBattleControllerReset, TestFactoryFunctions, TestBattleControllerGetResults, TestBattleMode, TestBattleConfig, TestRetreatState, TestBattleControllerModeHandlers
- [x] Delete original file after verification
- [x] Verify: All tests pass (110 passed), same count (110 = 110)

**Notes:** Split into 4 files with conftest.py for shared fixtures.

---

#### 3.1.4: Split test_fleet.py (1103 LOC -> 3 files) ✅ COMPLETE
**Source:** `tests/unit/strategy/test_fleet.py`
**Target:** `tests/unit/strategy/fleet/`
**Tests:** `pytest tests/unit/strategy/fleet/ -v`

- [x] Create directory `tests/unit/strategy/fleet/`
- [x] Create `__init__.py` and `conftest.py`
- [x] Split into:
  - [x] `test_basics.py` - Fleet creation, orders, merge, equality (TestFleetOrder, TestFleet, TestFleetOrders, TestFleetMerge, TestFleetEquality)
  - [x] `test_resources.py` - Movement resources, warp resources (TestMovementResourceMethods, TestWarpResourceMethods, TestBackwardCompatibility, TestEdgeCases)
  - [x] `test_serialization.py` - Serialization (TestFleetSerialization)
- [x] Delete original file after verification
- [x] Verify: All tests pass (70 passed), same count (70 = 70)

**Notes:** Split into 3 files with conftest.py containing shared fixtures (basic_fleet, make_mock_ship, make_ship_instance).

---

### Task 3.2: Split Severe Monoliths (700-1000 LOC) [Complex]

**For each file below, follow the same pattern:**
1. Create subdirectory with `__init__.py` and `conftest.py`
2. Split by test class groupings
3. Verify all tests pass

- [x] `test_pathfinding.py` (996 LOC) -> 3 files (55 tests)
- [x] `test_registry.py` (973 LOC) -> 3 files (69 tests)
- [x] `test_research_scene.py` (954 LOC) -> 3 files (30 tests)
- [x] `test_collision_edge_cases.py` (949 LOC) -> 3 files (32 tests)
- [x] `test_turn_engine_strategy.py` (932 LOC) -> 3 files (27 tests)
- [x] `test_modifier_ability_snapshots.py` (907 LOC) -> 2 files (70 tests)
- [x] `test_fleet_navigation_service.py` (852 LOC) -> 2 files (36 tests)
- [x] `test_resources_registry.py` (838 LOC) -> 2 files (39 tests)
- [x] `test_gameplay_loop.py` (824 LOC) -> 3 files (27 tests)
- [x] `test_test_lab_scene.py` (789 LOC) -> 2 files (57 tests)
- [x] `test_controllable_interface.py` (788 LOC) -> 2 files (96 tests)
- [x] `test_projectile_guidance.py` (780 LOC) -> 2 files (27 tests)
- [ ] `test_target_evaluator.py` (765 LOC) -> 2 files
- [ ] `test_turn_engine.py` (746 LOC) -> 2 files
- [ ] `test_battle_state_viewer.py` (739 LOC) -> 2 files
- [ ] `test_resource_system.py` (725 LOC) -> 2 files
- [ ] `test_planet_atmosphere.py` (716 LOC) -> 2 files
- [ ] `test_fleet_combat.py` (714 LOC) -> 2 files
- [ ] `test_conflict_resolution_engine.py` (708 LOC) -> 2 files
- [ ] `test_formation_prediction.py` (682 LOC) -> 2 files

**Notes:**

---

### Task 3.3: Split Moderate Monoliths (500-700 LOC) [Medium]

**Files to split (26 files between 500-700 LOC):**

Split into 2 files each based on test class groupings:
- [ ] Files 41-50 from the 50 file list (see design.md)

**Notes:** This task may be split across multiple sessions. Track progress by checking off completed files.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No test file exceeds 500 LOC: `find tests/ -name "test_*.py" -exec wc -l {} \; | awk '$1 > 500 {print}'`
- [ ] All new directories have `__init__.py` and `conftest.py`
- [ ] Run `pytest tests/ -v --tb=short` - all tests pass
- [ ] Same total test count as baseline
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
