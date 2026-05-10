# Phase 3: LayerType Import Migration [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-58 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate 24 legacy LayerType imports from `game.simulation.components.component_constants` to canonical `game.core.constants`.

---

## Tasks

### Task 3.1: Migrate LayerType Imports in Test Files [Simple]
**Files:** 24+ files
**Tests:** `pytest tests/ --testmon`

Change `from game.simulation.components.component_constants import LayerType` to `from game.core.constants import LayerType`.

**Test fixtures:**
- [x] `tests/fixtures/components.py:27`
- [x] `tests/fixtures/ships.py:34`

**Repro issues:**
- [x] `tests/repro_issues/test_bug_01_crew_delay.py:5` (also imports `Modifier`)
- [x] `tests/repro_issues/test_bug_05_logistics.py:4,39`
- [x] `tests/repro_issues/test_bug_07_crash.py:9`
- [x] `tests/repro_issues/test_bug_09_endurance.py:8`
- [x] `tests/repro_issues/test_bug_11_hull_update.py:11`
- [x] `tests/repro_issues/test_bug_13_clear_removes_hull.py:11`

**Unit tests - AI:**
- [x] `tests/unit/ai/target_evaluator/test_evaluation_rules.py:429`
- [x] `tests/unit/ai/test_movement_and_ai.py:12`

**Unit tests - Builder:**
- [x] `tests/unit/builder/test_builder_validation.py:7`
- [x] `tests/unit/builder/test_bulk_add.py:3` (also imports `ComponentStatus`)
- [x] `tests/unit/builder/test_requirement_abilities.py:4`

**Unit tests - Combat:**
- [x] `tests/unit/combat/test_combat_endurance.py:8`
- [x] `tests/unit/combat/test_damage_weighted.py:5`
- [x] `tests/unit/combat/test_fighter_launch.py:4`
- [x] `tests/unit/combat/test_multitarget.py:9`

**Unit tests - Entities:**
- [x] `tests/unit/entities/test_hull_layer.py:6`
- [x] `tests/unit/entities/test_ship_caching.py:5`
- [x] `tests/unit/entities/test_ship_component_manager_di.py:64`
- [x] `tests/unit/entities/test_ship_di.py:114,168`
- [x] `tests/unit/entities/test_ship_resources.py:8` (also imports `ComponentStatus`)
- [x] `tests/unit/entities/test_ship_serialization_di.py:77,91,131`
- [x] `tests/unit/entities/test_ship_stats.py:47`
- [x] `tests/unit/entities/test_stacking_integration.py:9`
- [x] `tests/unit/entities/test_stacking_rules.py:4`
- [x] `tests/unit/entities/ship_helpers/conftest.py:11`
- [x] `tests/unit/entities/ship_helpers/test_component_getters.py:15`
- [x] `tests/unit/entities/ship_helpers/test_component_operations.py:13`

**Unit tests - Systems:**
- [x] `tests/unit/systems/test_dynamic_layers.py:6`
- [x] `tests/unit/systems/test_layer_restrictions_refactor.py:5`
- [x] `tests/unit/systems/test_mount_validation.py:18`

**Unit tests - Simulation:**
- [x] `tests/unit/simulation/test_component_decoupling.py:59,154`
- [x] `tests/unit/simulation/test_simulation_design_loader.py:196`
- [x] `tests/unit/simulation/ship_combat_engine/test_combat_ops.py:11`
- [x] `tests/unit/simulation/ship_component_manager/test_creation_and_layers.py:9`
- [x] `tests/unit/simulation/ship_component_manager/test_queries_and_iteration.py:9`

**Unit tests - Other:**
- [x] `tests/unit/fixtures/test_component_fixtures.py:10`
- [x] `tests/unit/fixtures/test_ship_fixtures.py:12`
- [x] `tests/unit/performance/generate_test_data.py:11`
- [x] `tests/unit/regressions/test_bug_regressions_2026_01.py:4` (also imports `ComponentStatus`)
- [x] `tests/unit/services/test_vehicle_design_service.py:12`
- [x] `tests/unit/ui/test_battle_screen_extended.py:9`

**Scripts:**
- [x] `scripts/repro_energy_stats.py:7`
- [x] `scripts/repro_shield.py:7`

**Test framework:**
- [x] `test_framework/scenario.py:99`
- [x] `test_framework/scenarios/gun_accuracy_test.py:3`

- [x] Run tests: `pytest tests/ -x` — 6248 passed
**Notes:** Files importing `ComponentStatus` or `Modifier` alongside LayerType had their imports split: LayerType from `game.core.constants`, other items kept from `component_constants`.

### Task 3.2: Remove LayerType Re-export from component_constants.py [Simple]
**File:** `game/simulation/components/component_constants.py`
**Tests:** `pytest tests/ -x`
- [x] Remove lines 24-26: `from game.core.constants import LayerType` re-export and PROJ-17 comment
- [x] Remove `LayerType` from `__all__`
- [x] Run full test suite: `pytest tests/ -x` — 6248 passed
**Notes:** Clean removal, no remaining callers.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
