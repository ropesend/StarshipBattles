# Phase 4: Partial Cleanups Within Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-155 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove dead code segments from files that have both good and bad content.
**Priority:** Normal

---

## Tasks

### Task 4.1: Remove TestAllowedLayersRemoval [Simple]
**File:** `tests/unit/systems/test_allowed_layers_removal.py`
**Tests:** `pytest tests/unit/systems/ -q`

- [ ] Read the file
- [ ] Remove `TestAllowedLayersRemoval` class (5 tests, ~50 lines) — one-time migration verification
- [ ] Keep `TestBuilderDropValidation` class (3 tests) — ongoing validation value
- [ ] Run tests to verify no regressions

**Notes:**

### Task 4.2: Remove empty stubs from test_bulk_add.py [Simple]
**File:** `tests/unit/builder/test_bulk_add.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [ ] Read the file
- [ ] Remove `test_bulk_add_with_limit` method (setup + `pass` body)
- [ ] Remove `test_bulk_performance_mock` method (`pass` body)
- [ ] Run tests to verify no regressions

**Notes:**

### Task 4.3: Remove empty TestShipExpectedStats [Simple]
**File:** `tests/unit/builder/test_ship_loading.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [ ] Read the file
- [ ] Remove `class TestShipExpectedStats: pass` (docstring + empty class)
- [ ] Run tests to verify no regressions

**Notes:**

### Task 4.4: Remove TestGameSwitchScene [Simple]
**File:** `tests/unit/ui/test_scene_protocol.py`
**Tests:** `pytest tests/unit/ui/test_scene_protocol.py -v`

- [ ] Read the file
- [ ] Remove `TestGameSwitchScene` class (~40 lines) — tests Python attribute assignment on MagicMock
- [ ] Keep `TestISceneProtocolCompliance` and `TestSceneCallback`
- [ ] Run tests to verify no regressions

**Notes:**

### Task 4.5: Remove trivial tests from test_config.py [Medium]
**File:** `tests/unit/ui/test_config.py`
**Tests:** `pytest tests/unit/ui/test_config.py -v`

- [ ] Read the file (213 lines)
- [ ] Identify which tests are pure `assert X > 0` positivity checks (~20 tests)
- [ ] Keep the following valuable tests:
  - `TestUIConfigAllConstantsAreIntegers` (dynamic type checking)
  - `test_font_sizes_hierarchy` (title >= name >= stat)
  - `test_confirm_dialog_larger_than_toast`
  - `test_row_height_large_larger_than_standard`
  - `test_panel_alpha_in_range` (0-255)
  - `test_toast_dimensions_reasonable`
- [ ] Remove all pure `assert X > 0` test classes (~130 lines)
- [ ] Run tests to verify no regressions

**Notes:**

### Task 4.6: Remove duplicate tests from test_battle_screen_edge_cases.py [Medium]
**File:** `tests/unit/ui/screens/test_battle_screen_edge_cases.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_screen_edge_cases.py -v`

- [ ] Read the file (408 lines)
- [ ] Keep 6 unique edge case tests:
  - `test_handle_event_unknown_event_type`
  - `test_handle_mouse_click_none_result` (clears camera target)
  - `test_handle_right_click_no_clear`
  - `test_keydown_f3_toggles_overlay`
  - `test_keydown_comma_respects_minimum` (min speed boundary)
  - `test_keydown_period_respects_maximum` (max speed boundary)
- [ ] Remove 12 duplicate tests + 2 trivial resize tests (~250 lines)
- [ ] Run tests to verify no regressions

**Notes:**

### Task 4.7: Remove mock-property tests from test_strategy_detail_formatter.py [Simple]
**File:** `tests/unit/ui/test_strategy_detail_formatter.py`
**Tests:** `pytest tests/unit/ui/test_strategy_detail_formatter.py -v`

- [ ] Read the file
- [ ] Remove `TestStrategyDetailFormatterWidgetAccessors` class (~60 lines) — tests mock `._mock_name`
- [ ] Remove `TestResizeSupport` class (~40 lines) — tests trivial setters
- [ ] Keep all other test classes
- [ ] Run tests to verify no regressions

**Notes:**

### Task 4.8: Remove trivial tests from test_colors.py [Simple]
**File:** `tests/unit/ui/test_colors.py`
**Tests:** `pytest tests/unit/ui/test_colors.py -v`

- [ ] Read the file (142 lines)
- [ ] Remove `TestBasicColors` class (3 tests, ~18 lines) — WHITE is white, BLACK is black
- [ ] Remove `TestFontConstants` class (3 tests, ~18 lines) — fragile font name matching
- [ ] Keep `TestColorsValidation` (5 tests) — structural RGB validation
- [ ] Keep `TestColorAccessibility` (3 tests) — contrast/dark theme guardrails
- [ ] Run tests to verify no regressions

**Notes:**

### Task 4.9: Remove test_legacy_cleanup [Simple]
**File:** `tests/unit/strategy/test_production_refactor.py`
**Tests:** `pytest tests/unit/strategy/test_production_refactor.py -v`

- [ ] Read the file
- [ ] Remove `test_legacy_cleanup` method (6 lines) — one-time hasattr check for removed methods
- [ ] Keep `test_dynamic_consumption_limiting_resource` and `test_carry_over_capacity`
- [ ] Run tests to verify no regressions

**Notes:**

### Task 4.10: Remove duplicate classes from tech tree test_validation.py [Medium]
**File:** `tests/unit/research/tech_tree/test_validation.py`
**Tests:** `pytest tests/unit/research/tech_tree/ -v`

- [ ] Read the file
- [ ] Verify `TestDetectCycles` duplicates `test_cycle_detection.py` (more comprehensive)
- [ ] Verify `TestDepthCalculation` duplicates `test_queries.py::TestTechTreeDepthCalculation`
- [ ] Remove `TestDetectCycles` class (~60 lines)
- [ ] Remove `TestDepthCalculation` class (~60 lines)
- [ ] Keep `TestValidateRequirements`, `TestValidate`, `TestEdgeCases`
- [ ] Run tests to verify no regressions

**Notes:**

### Task 4.11: Remove layout constants tests [Simple]
**File:** Needs identification — search for `TestLayoutConstants` class
**Tests:** Run tests for the containing file

- [ ] Search for `class TestLayoutConstants` across test suite
- [ ] Read the file, verify tests are trivial `assert X > 0` checks
- [ ] Remove the class (~24 lines)
- [ ] Run tests to verify no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12 -q` — verify no new failures vs baseline
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
