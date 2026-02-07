# Phase 3: LayerType Import Migration [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-58 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate 24 legacy LayerType imports from `game.simulation.components.component_constants` to canonical `game.core.constants`.

---

## Tasks

### Task 3.1: Migrate LayerType Imports in Test Files [Simple]
**Files:** 24+ files
**Tests:** `pytest tests/ --testmon`

Change `from game.simulation.components.component_constants import LayerType` to `from game.core.constants import LayerType`.

**Test fixtures:**
- [ ] `tests/fixtures/components.py:27`
- [ ] `tests/fixtures/ships.py:34`

**Repro issues:**
- [ ] `tests/repro_issues/test_bug_01_crew_delay.py:5` (also imports `Modifier`)
- [ ] `tests/repro_issues/test_bug_05_logistics.py:4,39`
- [ ] `tests/repro_issues/test_bug_07_crash.py:9`
- [ ] `tests/repro_issues/test_bug_09_endurance.py:8`
- [ ] `tests/repro_issues/test_bug_11_hull_update.py:11`
- [ ] `tests/repro_issues/test_bug_13_clear_removes_hull.py:11`

**Unit tests - AI:**
- [ ] `tests/unit/ai/target_evaluator/test_evaluation_rules.py:429`
- [ ] `tests/unit/ai/test_movement_and_ai.py:12`

**Unit tests - Builder:**
- [ ] `tests/unit/builder/test_builder_validation.py:7`
- [ ] `tests/unit/builder/test_bulk_add.py:3` (also imports `ComponentStatus`)
- [ ] `tests/unit/builder/test_requirement_abilities.py:4`

**Unit tests - Combat:**
- [ ] `tests/unit/combat/test_combat_endurance.py:8`
- [ ] `tests/unit/combat/test_damage_weighted.py:5`
- [ ] `tests/unit/combat/test_fighter_launch.py:4`
- [ ] `tests/unit/combat/test_multitarget.py:9`

**Unit tests - Entities:**
- [ ] `tests/unit/entities/test_hull_layer.py:6`
- [ ] `tests/unit/entities/test_ship_caching.py:5`
- [ ] `tests/unit/entities/test_ship_component_manager_di.py:64`
- [ ] `tests/unit/entities/test_ship_di.py:114,168`
- [ ] `tests/unit/entities/test_ship_resources.py:8` (also imports `ComponentStatus`)
- [ ] `tests/unit/entities/test_ship_serialization_di.py:77,91,131`
- [ ] `tests/unit/entities/test_ship_stats.py:47`
- [ ] `tests/unit/entities/test_stacking_integration.py:9`
- [ ] `tests/unit/entities/test_stacking_rules.py:4`
- [ ] `tests/unit/entities/ship_helpers/conftest.py:11`
- [ ] `tests/unit/entities/ship_helpers/test_component_getters.py:15`
- [ ] `tests/unit/entities/ship_helpers/test_component_operations.py:13`

**Unit tests - Systems:**
- [ ] `tests/unit/systems/test_dynamic_layers.py:6`
- [ ] `tests/unit/systems/test_layer_restrictions_refactor.py:5`
- [ ] `tests/unit/systems/test_mount_validation.py:18`

**Unit tests - Simulation:**
- [ ] `tests/unit/simulation/test_component_decoupling.py:59,154`
- [ ] `tests/unit/simulation/test_simulation_design_loader.py:196`
- [ ] `tests/unit/simulation/ship_combat_engine/test_combat_ops.py:11`
- [ ] `tests/unit/simulation/ship_component_manager/test_creation_and_layers.py:9`
- [ ] `tests/unit/simulation/ship_component_manager/test_queries_and_iteration.py:9`

**Unit tests - Other:**
- [ ] `tests/unit/fixtures/test_component_fixtures.py:10`
- [ ] `tests/unit/fixtures/test_ship_fixtures.py:12`
- [ ] `tests/unit/performance/generate_test_data.py:11`
- [ ] `tests/unit/regressions/test_bug_regressions_2026_01.py:4` (also imports `ComponentStatus`)
- [ ] `tests/unit/services/test_vehicle_design_service.py:12`
- [ ] `tests/unit/ui/test_battle_screen_extended.py:9`

**Scripts:**
- [ ] `scripts/repro_energy_stats.py:7`
- [ ] `scripts/repro_shield.py:7`

**Test framework:**
- [ ] `test_framework/scenario.py:99`
- [ ] `test_framework/scenarios/gun_accuracy_test.py:3`

- [ ] Run tests: `pytest tests/ --testmon`
**Notes:** Some files import `ComponentStatus` or `Modifier` alongside LayerType. Keep those imports from `component_constants` if `ComponentStatus`/`Modifier` are NOT available in `game.core.constants`.

### Task 3.2: Remove LayerType Re-export from component_constants.py [Simple]
**File:** `game/simulation/components/component_constants.py`
**Tests:** `pytest tests/ -x`
- [ ] Remove lines 24-26: `from game.core.constants import LayerType` re-export and PROJ-17 comment
- [ ] Run full test suite: `pytest tests/ -x`
**Notes:** Only do this AFTER Task 3.1 is complete.

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
