# Phase 2: Merge-Then-Delete

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-157 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Preserve unique tests by merging into canonical files, then delete duplicates.

**CRITICAL RULE:** Always read BOTH source and target files completely before merging. Never assume the validation review's unique test list is still accurate - verify at merge time.

---

## Task 2.1: Merge test_race_validator.py edge cases [Simple]
**Source:** `tests/unit/ui/test_race_validator.py`
**Target:** `tests/unit/ui/screens/test_race_validator.py`
**Tests:** `pytest tests/unit/ui/screens/test_race_validator.py -v`

- [ ] Read source file completely
- [ ] Read target file completely
- [ ] Identify unique edge cases: `test_validate_whitespace_name_returns_invalid`, `test_validate_none_name_returns_invalid`
- [ ] Add the 2 unique tests to target file (adapt fixtures as needed)
- [ ] Delete source file
- [ ] Run tests, verify all pass

**Notes:**

---

## Task 2.2: Merge AI behaviors unique tests [Medium]
**Source:** `tests/unit/ai/test_ai_behaviors.py`
**Target:** `tests/unit/ai/test_behavior_units.py`
**Tests:** `pytest tests/unit/ai/test_behavior_units.py -v`

- [ ] Read both files completely
- [ ] Identify unique tests (expected: ~8 including opt_dist_calculation, opt_dist_min_clamp, branching_kite_maintain, target_pos_fixed_rotation, target_pos_relative_rotation, drift_logic_correction, velocity_sync)
- [ ] Migrate unique tests to target, adapting mock setup as needed
- [ ] Delete source file
- [ ] Run tests, verify all pass

**Notes:**

---

## Task 2.3: Merge AI target evaluator rules [Medium]
**Source:** `tests/unit/ai/target_evaluator/test_evaluation_rules.py` (599 lines)
**Target:** `tests/unit/ai/target_evaluator/test_target_evaluator_rules.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -v`

- [ ] Read both files
- [ ] Identify ~11 unique tests (zero_distance, largest_same_as_mass, missing_mass_uses_default, missing_velocity_uses_zero, TestStrengthRules, TestSpeedRulesFactorBased documenting KNOWN BUG, missing_weight_uses_zero, missing_factor_uses_one, same_position_zero_distance, negative_weight, very_large_distance)
- [ ] Migrate unique tests (especially the speed factor bug documentation tests)
- [ ] Delete source file
- [ ] Run tests, verify all pass

**Notes:**

---

## Task 2.4: Merge AI evaluation integration tests [Medium]
**Source:** `tests/unit/ai/target_evaluator/test_evaluation_integration.py` (286 lines)
**Target:** `tests/unit/ai/target_evaluator/test_target_evaluator_edge_cases.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -v`

- [ ] Read both files
- [ ] Identify ~11 unique tests (TestCustomStatHelpers, TestDefaultStatHelpers testing combat_utils functions, TestThreatAssessment realistic scenarios, TestEdgeCases missing_weight/factor/negative/large)
- [ ] Migrate unique tests
- [ ] Delete source file
- [ ] Run tests, verify all pass

**Notes:**

---

## Task 2.5: Merge controllable adapter tests [Medium]
**Source:** `tests/unit/ai/controllable_interface/test_adapter_basics.py` + `test_adapter_methods.py`
**Target:** `tests/unit/ai/controllable_interface/test_controllable_adapter_edge_cases.py`
**Tests:** `pytest tests/unit/ai/controllable_interface/ -v`

- [ ] Read all three files
- [ ] From test_adapter_basics.py: identify unique `test_adapter_get_radius_returns_ship_radius`
- [ ] From test_adapter_methods.py: identify unique tests (get_turn_speed, get_acceleration_rate, get_is_thrusting, get_turn_throttle, uses_interface_methods_not_direct_access, direct_attribute_access_raises_error, direct_attribute_assignment_does_not_delegate, set_formation_master_to_none)
- [ ] Migrate 9 unique tests to target
- [ ] Delete both source files (keep `test_controllable_adapter.py` - ABC contract tests)
- [ ] Run tests, verify all pass

**Notes:**

---

## Task 2.6: Merge core logger tests [Medium]
**Source:** `tests/unit/core/logger/test_events.py` + `tests/unit/core/logger/test_singleton.py`
**Target:** `tests/unit/core/logger/test_logger.py`
**Tests:** `pytest tests/unit/core/logger/ -v`

- [ ] Read all three files
- [ ] From test_events.py: migrate 3 unique functional tests (test_set_event_handler_replaces_previous, test_log_event_with_no_kwargs, test_log_event_with_many_kwargs)
- [ ] From test_singleton.py: migrate 6 unique tests (test_double_checked_locking, test_log_with_none_message, test_log_with_empty_string, test_log_with_complex_objects, test_log_unicode_characters, test_log_very_long_message)
- [ ] Delete both source files
- [ ] Run tests, verify all pass

**Notes:**

---

## Task 2.7: Merge core utility edge cases [Medium]
**Source:** `tests/unit/core/test_json_utils_edge_cases.py` + `tests/unit/core/test_validation_edge_cases.py`
**Target:** `tests/unit/core/test_json_utils.py` + `tests/unit/core/test_validation.py`
**Tests:** `pytest tests/unit/core/ -v`

- [ ] Read test_json_utils_edge_cases.py and test_json_utils.py
- [ ] Migrate 4 unique tests: test_load_json_io_error_returns_default, test_load_json_custom_default, test_save_json_io_error_returns_false, test_save_json_type_error_returns_false
- [ ] Delete test_json_utils_edge_cases.py
- [ ] Read test_validation_edge_cases.py and test_validation.py
- [ ] Migrate 7 unique tests: test_init_with_none_errors_defaults_to_list, test_init_with_none_warnings_defaults_to_list, test_add_error_with_error_code_enum, test_add_error_with_string_code, test_add_error_no_code_leaves_none, test_create_with_errors_list, test_create_empty_message_in_errors
- [ ] Delete test_validation_edge_cases.py
- [ ] Run tests, verify all pass

**Notes:**

---

## Task 2.8: Merge simulation layer restriction test [Simple]
**Source:** `tests/unit/simulation/test_layer_restriction_rule_refactor.py` (204 lines)
**Target:** `tests/unit/simulation/validation/test_ship_validator_rules.py`
**Tests:** `pytest tests/unit/simulation/validation/ -v`

- [ ] Read both files
- [ ] Migrate 1 unique test: `test_combined_block_and_allow_rules` (block-over-allow precedence)
- [ ] Delete source file
- [ ] Run tests, verify all pass

**Notes:**

---

## Task 2.9: Merge component health manager tests [Simple]
**Source:** `tests/unit/components/test_component_health_manager.py` (144 lines)
**Target:** `tests/unit/simulation/components/test_component_health_edge_cases.py`
**Tests:** `pytest tests/unit/simulation/components/ -v`

- [ ] Read both files
- [ ] Migrate 2 unique tests: `test_take_damage_raises_typeerror_for_non_numeric`, `test_hp_ratio_returns_cached_ratio`
- [ ] Delete source file
- [ ] Run tests, verify all pass

**Notes:**

---

## Task 2.10: Delete hex math duplicate [Simple]
**Source:** `tests/unit/strategy/test_hex_math.py` (298 lines)
**Target:** `tests/unit/core/test_hex_math_core.py`
**Tests:** `pytest tests/unit/core/test_hex_math_core.py -v`

- [ ] Read both files and verify core is strict superset (validation review confirmed this)
- [ ] Delete strategy version
- [ ] Run tests, verify all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Record post-phase test count: _____ tests passed (delta: _____)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
