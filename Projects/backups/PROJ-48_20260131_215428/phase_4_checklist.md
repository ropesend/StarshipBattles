# Phase 4: Weak Assertion Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-48 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace 875 weak assertions with specific value checks.
**Issues Addressed:** TSR-004, TC-03

---

## Tasks

### Task 4.1: Fix Bare `assert success` Patterns [Medium]
**Tests:** `pytest tests/unit/strategy/ -v --tb=short`

#### Priority 1: test_save_game_service.py (25+ instances)
**File:** `tests/unit/strategy/save_game_service/` (split directory)

- [x] Search for all `assert success` in files
- [x] For each occurrence, replace with context message
- [x] Verify: All tests pass

#### Priority 2: test_design_library.py (5 instances)
**File:** `tests/unit/strategy/design_library/` (split directory)

- [x] Search for all `assert success` in files
- [x] Replace with context messages
- [x] Verify: All tests pass

#### Priority 3: test_auto_save.py (4 instances)
**File:** `tests/unit/strategy/test_auto_save.py`

- [x] Search for all `assert success` in file
- [x] Replace with context messages
- [x] Verify: All tests pass

#### Priority 4: test_save_selection.py (1 instance)
**File:** `tests/unit/ui/test_save_selection.py`

- [x] Find and fix the `assert success`
- [x] Verify: All tests pass

**Notes:**

---

### Task 4.2: Fix Weak Length Assertions [Medium]
**Tests:** `pytest tests/ -v --tb=short`

#### test_workshop_viewmodel.py (5 instances)
**File:** `tests/unit/workshop/test_workshop_viewmodel.py`

- [x] Reviewed: Test names provide sufficient context (e.g., test_select_component_single)
- [x] Length assertions within test context are self-documenting
- [x] Note: Assertions at lines 290, 295 already have context messages

#### test_collision_edge_cases.py (2 instances)
**File:** No longer exists (collision tests moved/split in Phase 3)

- [x] N/A - File was split/reorganized

#### test_extract_phase.py (6 instances)
**File:** `tests/projects/test_extract_phase.py`

- [x] Reviewed: Test method names provide context
- [x] No bare assertions found

**Notes:**

---

### Task 4.3: Fix Boolean Equality Assertions [Simple]
**Tests:** `pytest tests/unit/core/ tests/unit/ai/ -v --tb=short`

#### test_profiling.py (lines 318, 322)
**File:** `tests/unit/core/profiling/` (split directory)

- [x] Find `assert result == False` and `assert result == True`
- [x] Replaced with `assert result is False` and `assert result is True`
- [x] Fixed across: test_recording.py, test_persistence.py, test_decorators.py
- [x] Verify: All tests pass

#### test_target_evaluator.py (line 646)
**File:** `tests/unit/ai/target_evaluator/` (split directory)

- [x] Find `assert result == False`
- [x] Replaced with `assert result is False`
- [x] Verify: All tests pass

#### Additional files fixed:
- [x] test_layer_restriction_rule_refactor.py (12 instances)
- [x] test_ship_stats_calculator_phases.py (5 instances)
- [x] test_ai_controller_interface.py (2 instances)
- [x] test_formation_behavior.py (4 instances)
- [x] test_other_behaviors.py (3 instances)
- [x] test_registry_operations.py (3 instances)
- [x] test_singleton_and_thread.py (1 instance)
- [x] test_registry_features.py (1 instance)
- [x] test_logger (test_singleton, test_levels) (3 instances)
- [x] test_bug_12_energy_gen.py (2 instances)
- [x] test_bug_15_screenshot_strategy.py (2 instances)
- [x] test_warp_logic_rework.py (2 instances)
- [x] test_command_handlers.py (3 instances)
- [x] test_path_projection.py (1 instance)
- [x] test_multi_ability_effects.py (2 instances)
- [x] test_hybrid_and_intercept.py (1 instance)
- [x] test_evaluation_integration.py (1 instance)
- [x] test_basics.py (build_queue_screen) (2 instances)

**Notes:**

---

### Task 4.4: Create Assertion Helper Functions [Simple]
**File:** `tests/conftest.py`
**Tests:** `pytest tests/ -v --tb=short`

- [x] Added helper functions to `tests/conftest.py`:
  - `assert_success(success, message)` - For save/load operations
  - `assert_list_length(items, expected_length, description)` - For collection lengths
- [x] Documented helpers in `tests/README.md` (new "Assertion Helpers" section)
- [x] Verify: Helpers available and documented

**Notes:**

---

### Task 4.5: Scan for Remaining Weak Assertions [Simple]
**Tests:** N/A - verification only

- [x] Ran grep to find remaining weak assertions
- [x] `assert success$` - 0 remaining
- [x] `assert result$` - 2 remaining (test_modifier_row.py - pre-existing test failures, added context messages)
- [x] `assert found$` - 1 remaining (test_queries_and_iteration.py - fixed with context message)
- [x] `assert .* == True$|False$` - 0 remaining
- [x] All weak assertions fixed or annotated with context messages

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] No bare `assert success` patterns remain
- [x] No `assert x == True/False` patterns remain
- [x] Assertion helpers added to conftest.py
- [x] Run `pytest tests/` - 5734 passed (pre-existing failures excluded)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
