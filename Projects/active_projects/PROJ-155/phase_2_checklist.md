# Phase 2: Merge Unique Tests Then Delete

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-155 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** For each file with partial overlap, migrate unique tests to the primary file, then delete the source.
**Priority:** High

---

## Tasks

### Task 2.1: Merge layer restriction rule refactor [Simple]
**Source:** `tests/unit/simulation/test_layer_restriction_rule_refactor.py` (204 lines)
**Target:** `tests/unit/simulation/validation/test_ship_validator_rules.py`
**Tests:** `pytest tests/unit/simulation/validation/ -q`

- [ ] Read source file, locate `test_combined_block_and_allow_rules` test
- [ ] Read target file, identify appropriate insertion point
- [ ] Copy the test (with any needed imports/fixtures) to target file
- [ ] Run target file tests to verify the migrated test passes
- [ ] Delete source file
- [ ] Run tests to verify no regressions

**Notes:**

### Task 2.2: Merge json utils edge cases [Medium]
**Source:** `tests/unit/core/test_json_utils_edge_cases.py` (~127 lines)
**Target:** `tests/unit/core/test_json_utils.py`
**Tests:** `pytest tests/unit/core/test_json_utils*.py -v`

- [ ] Read source file, identify 4 unique tests:
  - `test_load_json_io_error_returns_default`
  - `test_load_json_custom_default`
  - `test_save_json_io_error_returns_false`
  - `test_save_json_type_error_returns_false`
- [ ] Read target file, identify appropriate insertion point and any needed imports
- [ ] Copy the 4 tests with their imports to target file
- [ ] Run target file tests to verify migrated tests pass
- [ ] Delete source file
- [ ] Run tests to verify no regressions

**Notes:**

### Task 2.3: Merge validation edge cases [Medium]
**Source:** `tests/unit/core/test_validation_edge_cases.py` (~165 lines)
**Target:** `tests/unit/core/test_validation.py`
**Tests:** `pytest tests/unit/core/test_validation*.py -v`

- [ ] Read source file, identify 7 unique tests:
  - `test_init_with_none_errors_defaults_to_list`
  - `test_init_with_none_warnings_defaults_to_list`
  - `test_add_error_with_error_code_enum`
  - `test_add_error_with_string_code`
  - `test_add_error_no_code_leaves_none`
  - `test_create_with_errors_list`
  - `test_create_empty_message_in_errors`
- [ ] Read target file, identify appropriate insertion point
- [ ] Copy the 7 tests with any needed imports to target file
- [ ] Run target file tests to verify
- [ ] Delete source file
- [ ] Run tests to verify no regressions

**Notes:**

### Task 2.4: Merge logger events [Simple]
**Source:** `tests/unit/core/logger/test_events.py` (~104 lines)
**Target:** `tests/unit/core/logger/test_logger.py`
**Tests:** `pytest tests/unit/core/logger/ -v`

- [ ] Read source file, identify 3 unique tests (skip existence checks):
  - `test_set_event_handler_replaces_previous`
  - `test_log_event_with_no_kwargs`
  - `test_log_event_with_many_kwargs`
- [ ] Read target file, identify appropriate insertion point
- [ ] Copy the 3 tests to target file
- [ ] Run target file tests to verify
- [ ] Delete source file
- [ ] Run tests to verify no regressions

**Notes:**

### Task 2.5: Merge logger singleton [Medium]
**Source:** `tests/unit/core/logger/test_singleton.py` (~175 lines)
**Target:** `tests/unit/core/logger/test_logger.py`
**Tests:** `pytest tests/unit/core/logger/ -v`

- [ ] Read source file, identify 6 unique tests:
  - `test_double_checked_locking` (threading test — CRITICAL to preserve)
  - `test_log_with_none_message`
  - `test_log_with_empty_string`
  - `test_log_with_complex_objects`
  - `test_log_unicode_characters`
  - `test_log_very_long_message`
- [ ] Read target file, identify appropriate insertion point
- [ ] Copy all 6 tests with threading imports to target file
- [ ] Run target file tests to verify (especially the threading test)
- [ ] Delete source file
- [ ] Run tests to verify no regressions

**Notes:**

### Task 2.6: Merge engines contracts [Medium]
**Source:** `tests/unit/strategy/interfaces/test_engines_contracts.py` (~379 lines)
**Target:** `tests/unit/strategy/interfaces/test_engine_interfaces.py`
**Tests:** `pytest tests/unit/strategy/interfaces/ -v`

- [ ] Read source file, identify 16 unique tests:
  - IPopulationEngine (4 tests including concrete implementation)
  - IResupplyEngine (5 tests including concrete implementation)
  - IHarvestingEngine (4 tests including concrete implementation)
  - IProductionEngine.process_construction_tick (1 test)
  - Module __all__ export tests (2 tests)
- [ ] Read target file, identify appropriate insertion point
- [ ] Copy all unique tests with imports to target file
- [ ] Run target file tests to verify
- [ ] Delete source file
- [ ] Run tests to verify no regressions

**Notes:**

### Task 2.7: Merge fleet battle adapter data/ [Simple]
**Source:** `tests/unit/strategy/data/test_fleet_battle_adapter.py` (303 lines)
**Target:** `tests/unit/strategy/test_fleet_battle_adapter.py`
**Tests:** `pytest tests/unit/strategy/ -q`

- [ ] Read source file, locate `test_passes_registries_to_ships` test
- [ ] Read target file, identify appropriate insertion point
- [ ] Copy the test to target file
- [ ] Run target file tests to verify
- [ ] Delete source file
- [ ] Run tests to verify no regressions

**Notes:**

### Task 2.8: Merge AI behaviors [Medium]
**Source:** `tests/unit/ai/formation_prediction/test_ai_behaviors.py` (~340 lines)
**Target:** `tests/unit/ai/formation_prediction/test_behavior_units.py`
**Tests:** `pytest tests/unit/ai/formation_prediction/ -v`

- [ ] Read source file, identify 8 unique tests:
  - `test_opt_dist_calculation`
  - `test_opt_dist_min_clamp`
  - `test_branching_kite_maintain`
  - `test_target_pos_fixed_rotation`
  - `test_target_pos_relative_rotation`
  - `test_drift_logic_correction`
  - `test_velocity_sync`
  - RamBehavior navigate_to params test (verify uniqueness)
- [ ] Read target file, identify appropriate insertion points
- [ ] Copy unique tests with any needed imports/fixtures to target file
- [ ] Run target file tests to verify
- [ ] Delete source file
- [ ] Run tests to verify no regressions

**Notes:**

### Task 2.9: Merge target evaluator rules [Complex]
**Source:** `tests/unit/ai/target_evaluator/test_evaluation_rules.py` (~599 lines)
**Target:** `tests/unit/ai/target_evaluator/test_target_evaluator_rules.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -v`

- [ ] Read source file, identify ~11 unique tests including:
  - `test_nearest_zero_distance`
  - `test_largest_same_as_mass`
  - `test_missing_mass_uses_default`
  - `test_missing_velocity_uses_zero`
  - `TestStrengthRules` class (2 tests)
  - `TestSpeedRulesFactorBased` class (6 tests — documents known bug!)
  - Edge case tests (missing weight, factor, zero distance, negative weight, large distance)
- [ ] Read target file, identify appropriate insertion points
- [ ] Copy all unique tests preserving the bug documentation comments
- [ ] Run target file tests to verify
- [ ] Delete source file
- [ ] Run tests to verify no regressions

**Notes:** The TestSpeedRulesFactorBased class documents a KNOWN BUG (double negation in slowest-with-factor). Preserve all comments.

### Task 2.10: Merge evaluation integration [Medium]
**Source:** `tests/unit/ai/target_evaluator/test_evaluation_integration.py` (~286 lines)
**Target:** `tests/unit/ai/target_evaluator/test_target_evaluator_edge_cases.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -v`

- [ ] Read source file, identify ~11 unique tests:
  - `TestCustomStatHelpers` (2 tests)
  - `TestDefaultStatHelpers` (3 tests)
  - `TestEdgeCases` unique tests (missing weight, factor, negative weight, large distance)
  - `TestThreatAssessment` (2 realistic scenario tests)
- [ ] Read target file, check for any name conflicts
- [ ] Copy all unique tests to target file
- [ ] Run target file tests to verify
- [ ] Delete source file
- [ ] Run tests to verify no regressions

**Notes:**

### Task 2.11: Merge controllable adapter files [Medium]
**Source:** `tests/unit/ai/controllable_interface/test_adapter_basics.py` + `test_adapter_methods.py` (~496 lines combined)
**Target:** `tests/unit/ai/controllable_interface/test_controllable_adapter_edge_cases.py`
**Tests:** `pytest tests/unit/ai/controllable_interface/ -v`

- [ ] Read both source files, identify 9 unique tests:
  - `test_adapter_get_radius_returns_ship_radius`
  - `test_adapter_get_turn_speed_returns_ship_turn_speed`
  - `test_adapter_get_acceleration_rate_returns_ship_acceleration_rate`
  - `test_adapter_get_is_thrusting_returns_ship_is_thrusting`
  - `test_adapter_get_turn_throttle_returns_ship_turn_throttle`
  - `test_adapter_uses_interface_methods_not_direct_access`
  - `test_direct_attribute_access_raises_error`
  - `test_direct_attribute_assignment_does_not_delegate`
  - `test_adapter_set_formation_master_to_none`
- [ ] Read target file, identify appropriate insertion point
- [ ] Copy all 9 unique tests to target file
- [ ] Run target file tests to verify
- [ ] Delete both source files
- [ ] Run tests to verify no regressions

**Notes:**

### Task 2.12: Merge spatial extended [Simple] (CONDITIONAL)
**Source:** `tests/unit/simulation/test_spatial_extended.py`
**Target:** `tests/unit/simulation/test_spatial.py`
**Tests:** `pytest tests/unit/simulation/test_spatial*.py -v`

- [ ] Check if source file exists. If not, skip this task.
- [ ] Read source file, identify 5 unique tests (empty grid, same cell, different cells, negative coords, cross-cell)
- [ ] Copy unique tests to target file
- [ ] Delete source file
- [ ] Run tests to verify no regressions

**Notes:** This task is conditional — only execute if the source file exists.

### Task 2.13: Merge collision system [Medium] (CONDITIONAL)
**Source:** `tests/unit/simulation/test_collision_system.py`
**Target:** `tests/unit/engine/test_beam_ramming.py`
**Tests:** `pytest tests/unit/simulation/ tests/unit/engine/ -q`

- [ ] Check if source file exists. If not, skip this task.
- [ ] Read source file, identify 6 unique tests (raycasting, tangent hit, behind origin, inside target, ramming logic, no logger)
- [ ] Copy unique tests to target file
- [ ] Delete source file
- [ ] Run tests to verify no regressions

**Notes:** This task is conditional — only execute if the source file exists.

### Task 2.14: Merge component health manager [Simple]
**Source:** `tests/unit/components/test_component_health_manager.py` (144 lines)
**Target:** `tests/unit/simulation/components/test_component_health_edge_cases.py`
**Tests:** `pytest tests/unit/components/ tests/unit/simulation/components/ -q`

- [ ] Read source file, identify 2 unique tests:
  - `test_take_damage_raises_typeerror_for_non_numeric`
  - `test_hp_ratio_returns_cached_ratio`
- [ ] Read target file, identify appropriate insertion point
- [ ] Copy the 2 tests to target file
- [ ] Run target file tests to verify
- [ ] Delete source file
- [ ] Run tests to verify no regressions

**Notes:** This must be done BEFORE Phase 3 Task 3.2 (deleting tests/unit/components/).

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12 -q` — verify no new failures vs baseline
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
