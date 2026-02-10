# Phase 6: Update Test Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-84 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Convert all test files that construct or access layer dicts directly. This is the largest phase — ~50 test files need mechanical conversion from dict access to LayerData attribute access.

**Conversion patterns:**
- `ship.layers[X] = {'components': [...], 'radius_pct': 0.5, ...}` → `ship.layers[X] = LayerData(components=[...], radius_pct=0.5, ...)`
- `ship.layers[X]['components']` → `ship.layers[X].components`
- `ship.layers[X]['hp_pool']` → `ship.layers[X].hp_pool`
- Add `from game.simulation.entities.layer_data import LayerData` to each file

---

## Tasks

### Task 6.1: Update conftest and fixture files [Medium]
**Files:**
- `tests/unit/simulation/armor_mechanics/conftest.py`
- `tests/unit/ui/services/battle_ui_service/conftest.py`
**Tests:** `pytest tests/unit/simulation/armor_mechanics/ tests/unit/ui/services/battle_ui_service/ -x`

- [ ] Replace dict literals with `LayerData(...)` construction in conftest fixtures
- [ ] Update any dict key access to attribute access
- [ ] Add LayerData import
- [ ] Verify: tests pass

**Notes:**

---

### Task 6.2: Update combat and damage test files [Medium]
**Files:**
- `tests/unit/combat/test_combat.py`
- `tests/unit/combat/test_shields.py`
- `tests/unit/combat/test_battle_engine_core.py`
- `tests/unit/combat/test_damage_weighted.py`
- `tests/unit/combat/test_battle_state_di.py`
- `tests/unit/combat/test_pdc.py`
- `tests/unit/simulation/armor_mechanics/test_damage_mechanics.py`
- `tests/unit/simulation/armor_mechanics/test_damage_reduction.py`
- `tests/unit/simulation/combat/test_damage_calculator.py`
- `tests/unit/simulation/ship_combat_engine/test_combat_ops.py`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/armor_mechanics/ tests/unit/simulation/combat/ tests/unit/simulation/ship_combat_engine/ -x`

- [ ] Replace all `ship.layers[X] = {dict}` with `ship.layers[X] = LayerData(...)`
- [ ] Replace all `ship.layers[X]['key']` with `ship.layers[X].key`
- [ ] Add LayerData import to each file
- [ ] Verify: tests pass

**Notes:**

---

### Task 6.3: Update entity and ship test files [Medium]
**Files:**
- `tests/unit/entities/test_ship.py`
- `tests/unit/entities/test_ship_stats.py`
- `tests/unit/entities/test_bridge_requirement_removal.py`
- `tests/unit/entities/test_hull_layer.py`
- `tests/unit/entities/test_emissive_armor.py`
- `tests/unit/entities/test_crystalline_armor.py`
- `tests/unit/entities/test_ship_resources.py`
- `tests/unit/entities/ship_helpers/test_component_operations.py`
- `tests/unit/simulation/ship_component_manager/test_creation_and_layers.py`
- `tests/unit/simulation/ship_component_manager/test_queries_and_iteration.py`
**Tests:** `pytest tests/unit/entities/ tests/unit/simulation/ship_component_manager/ -x`

- [ ] Replace all dict-style layer access with attribute access
- [ ] Add LayerData import to each file
- [ ] Verify: tests pass

**Notes:**

---

### Task 6.4: Update builder/UI test files [Medium]
**Files:**
- `tests/unit/builder/test_builder_drag_drop_real.py`
- `tests/unit/builder/test_builder_state_manager.py`
- `tests/unit/builder/test_builder_structure_features.py`
- `tests/unit/builder/test_builder_warning_logic.py`
- `tests/unit/builder/test_layer_targeted_actions.py`
- `tests/unit/builder/test_multi_selection_logic.py`
- `tests/unit/builder/test_builder_improvements.py`
- `tests/unit/builder/test_selection_refinements.py`
- `tests/unit/builder/test_builder_logic.py`
- `tests/unit/builder/test_builder_viewmodel.py`
- `tests/unit/builder/test_builder_validation.py`
- `tests/unit/workshop/test_workshop_viewmodel.py`
- `tests/unit/ui/services/battle_ui_service/test_conversion.py`
- `tests/unit/ui/services/battle_ui_service/test_state_and_integration.py`
- `tests/unit/ui/test_rendering_logic.py`
**Tests:** `pytest tests/unit/builder/ tests/unit/workshop/ tests/unit/ui/ -x`

- [ ] Replace all dict-style layer access with attribute access
- [ ] Add LayerData import to each file
- [ ] Verify: tests pass

**Notes:**

---

### Task 6.5: Update repro/bug test files [Medium]
**Files:**
- `tests/repro_issues/test_bug_04_display.py`
- `tests/repro_issues/test_bug_05_deep_repro.py`
- `tests/repro_issues/test_bug_05_logistics.py`
- `tests/repro_issues/test_bug_05_rejected_fix.py`
- `tests/repro_issues/test_bug_06_combat_propulsion.py`
- `tests/repro_issues/test_bug_07_crash.py`
- `tests/repro_issues/test_bug_10_logistics_update.py`
- `tests/repro_issues/test_bug_11_hull_update.py`
- `tests/repro_issues/test_bug_12_energy_gen.py`
- `tests/repro_issues/test_bug_13_clear_removes_hull.py`
**Tests:** `pytest tests/repro_issues/ -x`

- [ ] Replace all dict-style layer access with attribute access
- [ ] Add LayerData import to each file
- [ ] Verify: tests pass

**Notes:**

---

### Task 6.6: Update remaining test files [Medium]
**Files:**
- `tests/unit/simulation/test_layer_restriction_rule_refactor.py`
- `tests/unit/systems/test_layer_restrictions_refactor.py`
- `tests/unit/systems/test_mount_validation.py`
- `tests/unit/simulation/systems/test_ship_stats_calculator_phases.py`
- `tests/unit/simulation_tests/test_resource_scenarios.py`
- `tests/unit/test_targeting_rules.py`
- `tests/unit/ai/controllable_interface/test_adapter_methods.py`
- `tests/integration/ui/test_build_queue_design_report.py`
- `tests/unit/builder/test_fleet_composition.py`
**Tests:** `pytest tests/unit/simulation/ tests/unit/systems/ tests/unit/ai/ tests/integration/ -x`

- [ ] Replace all dict-style layer access with attribute access
- [ ] Add LayerData import to each file
- [ ] Verify: tests pass

**Notes:**

---

### Task 6.7: Full test suite run [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run complete test suite with parallelism
- [ ] Fix any remaining failures
- [ ] Verify all 7353+ tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
