# Phase 2: Merge-Then-Delete

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-157 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Preserve unique tests by merging into canonical files, then delete duplicates.

**CRITICAL RULE:** Always read BOTH source and target files completely before merging. Never assume the validation review's unique test list is still accurate - verify at merge time.

---

## Task 2.1: Merge test_race_validator.py edge cases [Simple]
**Source:** `tests/unit/ui/test_race_validator.py`
**Target:** `tests/unit/ui/screens/test_race_validator.py`
**Tests:** `pytest tests/unit/ui/screens/test_race_validator.py -v`

- [x] Read source file completely
- [x] Read target file completely
- [x] Identify unique edge cases: `test_validate_whitespace_name_returns_invalid`, `test_validate_none_name_returns_invalid`
- [x] Add the 2 unique tests to target file (adapt fixtures as needed)
- [x] Delete source file
- [x] Run tests, verify all pass

**Notes:** Added as TestRaceValidatorEdgeCases class. 19 tests pass.

---

## Task 2.2: Merge AI behaviors unique tests [Medium]
**Source:** `tests/unit/ai/test_ai_behaviors.py`
**Target:** `tests/unit/ai/test_behavior_units.py`
**Tests:** `pytest tests/unit/ai/test_behavior_units.py -v`

- [x] Read both files completely
- [x] Identify unique tests (expected: ~8 including opt_dist_calculation, opt_dist_min_clamp, branching_kite_maintain, target_pos_fixed_rotation, target_pos_relative_rotation, drift_logic_correction, velocity_sync)
- [x] Migrate unique tests to target, adapting mock setup as needed
- [x] Delete source file
- [x] Run tests, verify all pass

**Notes:** Added 3 truly unique tests as TestFormationBehaviorMigrated class (target_pos_relative_rotation, drift_logic_correction, velocity_sync). Other tests were already covered.

---

## Task 2.3: Merge AI target evaluator rules [Medium]
**Source:** `tests/unit/ai/target_evaluator/test_evaluation_rules.py` (599 lines)
**Target:** `tests/unit/ai/target_evaluator/test_target_evaluator_rules.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -v`

- [x] Read both files
- [x] **N/A - Target file does not exist.** Source IS the canonical file.
- [x] Source tests pass (54 tests)

**Notes:** Target file `test_target_evaluator_rules.py` does not exist. Source is canonical and should be KEPT.

---

## Task 2.4: Merge AI evaluation integration tests [Medium]
**Source:** `tests/unit/ai/target_evaluator/test_evaluation_integration.py` (286 lines)
**Target:** `tests/unit/ai/target_evaluator/test_target_evaluator_edge_cases.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -v`

- [x] Read both files
- [x] **N/A - Target file does not exist.** Source IS the canonical file.

**Notes:** Target file does not exist. Source is canonical and should be KEPT.

---

## Task 2.5: Merge controllable adapter tests [Medium]
**Source:** `tests/unit/ai/controllable_interface/test_adapter_basics.py` + `test_adapter_methods.py`
**Target:** `tests/unit/ai/controllable_interface/test_controllable_adapter_edge_cases.py`
**Tests:** `pytest tests/unit/ai/controllable_interface/ -v`

- [x] Read all three files
- [x] **N/A - Target file does not exist.** Sources ARE the canonical files.
- [x] Source tests pass (39 tests)

**Notes:** Target file does not exist. Sources are canonical and should be KEPT.

---

## Task 2.6: Merge core logger tests [Medium]
**Source:** `tests/unit/core/logger/test_events.py` + `tests/unit/core/logger/test_singleton.py`
**Target:** `tests/unit/core/logger/test_logger.py`
**Tests:** `pytest tests/unit/core/logger/ -v`

- [x] Read all three files
- [x] **N/A - Target file does not exist.** Sources ARE the canonical files.

**Notes:** Target file `test_logger.py` does not exist. Sources are canonical and should be KEPT.

---

## Task 2.7: Merge core utility edge cases [Medium]
**Source:** `tests/unit/core/test_json_utils_edge_cases.py` + `tests/unit/core/test_validation_edge_cases.py`
**Target:** `tests/unit/core/test_json_utils.py` + `tests/unit/core/test_validation.py`
**Tests:** `pytest tests/unit/core/ -v`

- [x] Read test_json_utils_edge_cases.py and test_json_utils.py
- [x] Migrate 3 unique tests: test_load_json_io_error_returns_default, test_save_json_io_error_returns_false, test_save_json_type_error_returns_false
- [x] Delete test_json_utils_edge_cases.py
- [x] Read test_validation_edge_cases.py and test_validation.py
- [x] Migrate 5 unique tests: test_init_with_none_errors_defaults_to_list, test_init_with_none_warnings_defaults_to_list, test_add_error_with_error_code_enum, test_add_error_no_code_leaves_none, test_create_empty_message_in_errors
- [x] Delete test_validation_edge_cases.py
- [x] Run tests, verify all pass

**Notes:** 21 json_utils tests, 31 validation tests pass.

---

## Task 2.8: Merge simulation layer restriction test [Simple]
**Source:** `tests/unit/simulation/test_layer_restriction_rule_refactor.py` (204 lines)
**Target:** `tests/unit/simulation/validation/test_ship_validator_rules.py`
**Tests:** `pytest tests/unit/simulation/validation/ -v`

- [x] Read both files
- [x] Migrate 1 unique test: `test_combined_block_and_allow_rules` (block-over-allow precedence)
- [x] Delete source file
- [x] Run tests, verify all pass

**Notes:** Test added to TestLayerRestrictionDefinitionRule class.

---

## Task 2.9: Merge component health manager tests [Simple]
**Source:** `tests/unit/components/test_component_health_manager.py` (144 lines)
**Target:** `tests/unit/simulation/components/test_component_health_edge_cases.py`
**Tests:** `pytest tests/unit/simulation/components/ -v`

- [x] Read both files
- [x] **N/A - Target file does not exist.** Source IS the canonical file.

**Notes:** Target file does not exist. Source is canonical and should be KEPT.

---

## Task 2.10: Delete hex math duplicate [Simple]
**Source:** `tests/unit/strategy/test_hex_math.py` (298 lines)
**Target:** `tests/unit/core/test_hex_math_core.py`
**Tests:** `pytest tests/unit/core/test_hex_math_core.py -v`

- [x] Read both files and verify core is strict superset (validation review confirmed this)
- [x] Delete strategy version
- [x] Run tests, verify all pass

**Notes:** Core version (659 lines) is strict superset with TCG-FND-014, TCG-FND-015, and hex_circle_filled tests.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Record post-phase test count: 12669 tests collected (delta: -92)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
