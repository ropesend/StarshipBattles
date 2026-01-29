# Phase 3: Test File Splitting (Monoliths)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-48 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Split 50 test files over 500 LOC into smaller, focused files.
**Issues Addressed:** TSR-005

---

## Tasks

### Task 3.1: Split Critical Monoliths (>1000 LOC) [Complex]

#### 3.1.1: Split test_ship_stats_service.py (1756 LOC -> 5 files)
**Source:** `tests/unit/strategy/test_ship_stats_service.py`
**Target:** `tests/unit/strategy/ship_stats/`
**Tests:** `pytest tests/unit/strategy/ship_stats/ -v`

- [ ] Create directory `tests/unit/strategy/ship_stats/`
- [ ] Create `tests/unit/strategy/ship_stats/__init__.py`
- [ ] Read source file and identify test class groupings
- [ ] Create `conftest.py` with shared fixtures from original file
- [ ] Split into these files:
  - [ ] `test_basics.py` - TestShipStatsServiceBasics class
  - [ ] `test_damage.py` - TestDamageEffectiveness class
  - [ ] `test_warp.py` - TestWarpCapability, TestHasWarpCapability classes
  - [ ] `test_resources.py` - TestGenericDictAccumulators, TestTriggerTypes, TestCustomResources classes
  - [ ] `test_modifiers.py` - TestModifierApplication class
- [ ] Update imports in each new file
- [ ] Delete original file after verification
- [ ] Verify: `pytest tests/unit/strategy/ship_stats/ -v` - all tests pass
- [ ] Verify: Same number of tests as before split

**Notes:**

---

#### 3.1.2: Split test_ship_instance_proj08.py (1458 LOC -> 3 files)
**Source:** `tests/unit/strategy/test_ship_instance_proj08.py`
**Target:** `tests/unit/strategy/ship_instance/`
**Tests:** `pytest tests/unit/strategy/ship_instance/ -v`

- [ ] Create directory `tests/unit/strategy/ship_instance/`
- [ ] Create `__init__.py` and `conftest.py`
- [ ] Split into:
  - [ ] `test_component_toggles.py` - Component toggle related classes
  - [ ] `test_resources.py` - Resource management classes
  - [ ] `test_serialization.py` - Serialization and edge case classes
- [ ] Delete original file after verification
- [ ] Verify: All tests pass, same count

**Notes:**

---

#### 3.1.3: Split test_battle_controller.py (1317 LOC -> 4 files)
**Source:** `tests/unit/simulation/test_battle_controller.py`
**Target:** `tests/unit/simulation/battle_controller/`
**Tests:** `pytest tests/unit/simulation/battle_controller/ -v`

- [ ] Create directory `tests/unit/simulation/battle_controller/`
- [ ] Create `__init__.py` and `conftest.py`
- [ ] Split into:
  - [ ] `test_initialization.py` - Init, configure, add ships
  - [ ] `test_execution.py` - Start, update, run_headless, run_ticks
  - [ ] `test_mechanics.py` - Retreat, reinforcements, edge finding
  - [ ] `test_utilities.py` - Queries, callbacks, reset, results
- [ ] Delete original file after verification
- [ ] Verify: All tests pass, same count

**Notes:**

---

#### 3.1.4: Split test_fleet.py (1103 LOC -> 3 files)
**Source:** `tests/unit/strategy/test_fleet.py`
**Target:** `tests/unit/strategy/fleet/`
**Tests:** `pytest tests/unit/strategy/fleet/ -v`

- [ ] Create directory `tests/unit/strategy/fleet/`
- [ ] Create `__init__.py` and `conftest.py`
- [ ] Split into:
  - [ ] `test_basics.py` - Fleet creation, orders, merge, equality
  - [ ] `test_resources.py` - Movement resources, warp resources
  - [ ] `test_serialization.py` - Serialization, backward compat, edge cases
- [ ] Delete original file after verification
- [ ] Verify: All tests pass, same count

**Notes:**

---

### Task 3.2: Split Severe Monoliths (700-1000 LOC) [Complex]

**For each file below, follow the same pattern:**
1. Create subdirectory with `__init__.py` and `conftest.py`
2. Split by test class groupings
3. Verify all tests pass

- [ ] `test_pathfinding.py` (996 LOC) -> 2-3 files
- [ ] `test_registry.py` (973 LOC) -> 2-3 files
- [ ] `test_research_scene.py` (954 LOC) -> 2-3 files
- [ ] `test_collision_edge_cases.py` (949 LOC) -> 2-3 files
- [ ] `test_turn_engine_strategy.py` (932 LOC) -> 2-3 files
- [ ] `test_modifier_ability_snapshots.py` (907 LOC) -> 2 files
- [ ] `test_fleet_navigation_service.py` (852 LOC) -> 2 files
- [ ] `test_resources_registry.py` (838 LOC) -> 2 files
- [ ] `test_gameplay_loop.py` (824 LOC) -> 2-3 files
- [ ] `test_test_lab_scene.py` (789 LOC) -> 2 files
- [ ] `test_controllable_interface.py` (788 LOC) -> 2 files
- [ ] `test_projectile_guidance.py` (780 LOC) -> 2 files
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
