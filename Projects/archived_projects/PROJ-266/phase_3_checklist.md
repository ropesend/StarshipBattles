# Phase 3: Combat Lab Pure Function Testing [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-266 3`
> 2. Only proceed if output shows PASSED

**Objective:** Test extractable pure functions from Combat Lab renderer and test_run_details.
**Status:** Not Started

---

## Task 3.1: Test _format_check_pair() [Simple]
**File:** `tests/unit/ui/screens/test_lab/test_renderer_pure_functions.py` (NEW)
**Source:** `game/ui/screens/test_lab/renderer.py` lines 1094-1130
- [ ] `test_format_check_pair_both_none`
- [ ] `test_format_check_pair_both_boolean`
- [ ] `test_format_check_pair_both_large_numeric` (>=10000, 1 decimal)
- [ ] `test_format_check_pair_both_medium_numeric` (>=1, 4 decimals)
- [ ] `test_format_check_pair_both_small_numeric` (<1, 6 decimals)
- [ ] `test_format_check_pair_mixed_types`
- [ ] `test_format_check_pair_both_strings`

## Task 3.2: Test _is_condition_verified() [Medium]
**Source:** `game/ui/screens/test_lab/renderer.py` lines 783-864
- [ ] `test_condition_verified_direct_mapping_pass`
- [ ] `test_condition_verified_direct_mapping_fail`
- [ ] `test_condition_verified_no_matching_validation`
- [ ] `test_condition_verified_range_penalty_regex_pass`
- [ ] `test_condition_verified_range_penalty_regex_fail`
- [ ] `test_condition_verified_empty_results`
- [ ] `test_condition_verified_unknown_condition`

## Task 3.3: Test numeric difference skip logic [Simple]
**File:** `tests/unit/ui/screens/test_lab/test_run_details_logic.py` (NEW)
**Source:** `game/ui/screens/test_lab/test_run_details.py` lines 487-530
- [ ] `test_numeric_diff_skips_non_numeric`
- [ ] `test_numeric_diff_skips_boolean`
- [ ] `test_numeric_diff_skips_none`
- [ ] `test_numeric_diff_exact_match`
- [ ] `test_numeric_diff_percentage_computation`
- [ ] `test_numeric_diff_zero_expected`

## Task 3.4: Test phase grouping logic [Simple]
**Source:** `game/ui/screens/test_lab/test_run_details.py` lines 354-391
- [ ] `test_phase_grouping_sorts_by_phase`
- [ ] `test_phase_grouping_default_phase_is_outcome`
- [ ] `test_phase_grouping_skips_empty_groups`
- [ ] `test_phase_grouping_unrecognized_phase`

## Phase 3 Verification
- [ ] Both new test files pass independently
- [ ] No regressions: `pytest tests/ --testmon`
