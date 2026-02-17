# Phase 3: Partial Cleanups

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-157 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove specific dead classes/methods within files that are otherwise valuable.

**RULE:** Read each file completely before editing. The validation reviews describe what to keep and what to remove - but always verify the current state.

---

## Task 3.1: UI test file partial cleanups [Simple]
**Tests:** `pytest tests/unit/ui/ -x -q --tb=short`

### 3.1a: test_config.py - Remove trivial positivity checks
**File:** `tests/unit/ui/test_config.py`
- [ ] Read the file
- [ ] Remove pure `assert X > 0` tests (e.g., TestUIConfigPositiveWidth, TestUIConfigPositiveHeight, etc.)
- [ ] KEEP: `TestUIConfigAllConstantsAreIntegers`, `test_font_sizes_hierarchy`, `test_confirm_dialog_larger_than_toast`, `test_row_height_large_larger_than_standard`, `test_panel_alpha_in_range`, `test_toast_dimensions_reasonable`
- [ ] Run tests

### 3.1b: test_colors.py - Remove trivial literal checks
**File:** `tests/unit/ui/test_colors.py`
- [ ] Read the file
- [ ] Remove `TestBasicColors` class (3 tests: white==255,255,255, black==0,0,0, white+black opposites)
- [ ] Remove `TestFontConstants` class (3 tests: font is string, non-empty, contains common name)
- [ ] KEEP: `TestColorsValidation` (5 tests) and `TestColorAccessibility` (3 tests)
- [ ] Run tests

### 3.1c: test_scene_protocol.py - Remove mock-attribute test
**File:** `tests/unit/ui/screens/test_scene_protocol.py`
- [ ] Read the file
- [ ] Remove `TestGameSwitchScene` class (~40 lines) - tests Python attribute assignment on MagicMock
- [ ] KEEP: `TestISceneProtocolCompliance` and `TestSceneCallback`
- [ ] Run tests

### 3.1d: test_game_renderer.py - Remove trivial constant tests
**File:** `tests/unit/ui/renderer/test_game_renderer.py`
- [ ] Read the file
- [ ] Identify and remove `TestRenderingConstants` or similar class with `assert X > 0` pattern
- [ ] KEEP: `TestDrawShipBehavior`, `TestLayerColors`, and other behavioral tests
- [ ] Run tests

### 3.1e: test_battle_screen_edge_cases.py - Remove 12 duplicates, keep 6 unique
**File:** `tests/unit/ui/screens/test_battle_screen_edge_cases.py`
- [ ] Read the file
- [ ] KEEP these 6 unique tests:
  - `test_handle_event_unknown_event_type`
  - `test_handle_mouse_click_none_result` (clears camera target)
  - `test_handle_right_click_no_clear`
  - `test_keydown_f3_toggles_overlay`
  - `test_keydown_comma_respects_minimum` (min speed boundary)
  - `test_keydown_period_respects_maximum` (max speed boundary)
- [ ] Remove duplicate tests (those already in test_battle_screen_simulation.py):
  - test_handle_mouse_click_focus_ship_result, test_handle_mouse_click_end_battle_result, test_handle_mousewheel
  - test_keydown_space_toggles_pause, test_keydown_comma_decreases_speed, test_keydown_period_increases_speed
  - test_keydown_m_resets_to_normal_speed, test_keydown_slash_sets_ui_pause_speed
  - test_keydown_bracket_cycles_focus, test_keydown_right_bracket_cycles_forward
- [ ] Remove trivial tests: test_handle_resize_updates_dimensions, test_handle_resize_camera_available
- [ ] Remove TestBattleStateEdgeCases if redundant with simulation tests
- [ ] Run tests

### 3.1f: test_battle_screen_extended.py - Remove 3 duplicates, keep beam test
**File:** `tests/unit/ui/screens/test_battle_screen_extended.py`
- [ ] Read the file
- [ ] Remove duplicates: test_is_battle_over_victory, test_update_loop_tick_counter, test_headless_mode_initialization
- [ ] KEEP: `test_process_beam_attack_logic` (unique collision system beam test)
- [ ] Run tests

### 3.1g: test_battle_ui_service.py (flat) - Migrate colors, remove rest
**File:** `tests/unit/ui/services/test_battle_ui_service.py`
**Target:** `tests/unit/ui/services/battle_ui_service/` (subdirectory)
- [ ] Read the flat file
- [ ] Identify `TestProjectileColors` class (3 tests)
- [ ] Migrate TestProjectileColors to appropriate file in subdirectory
- [ ] Delete flat file (or remove all classes except colors if keeping in place)
- [ ] Run tests

- [ ] Run `pytest tests/unit/ui/ -x -q --tb=short` after all 3.1 tasks

**Notes:**

---

## Task 3.2: Other partial cleanups [Simple]
**Tests:** `pytest tests/unit/builder/ tests/unit/systems/ tests/unit/research/ -x -q`

### 3.2a: test_bulk_add.py - Remove empty stubs
**File:** `tests/unit/builder/test_bulk_add.py`
- [ ] Read the file
- [ ] Remove `test_bulk_add_with_limit` method (setup + `pass` body)
- [ ] Remove `test_bulk_performance_mock` method (entirely `pass`)
- [ ] Run tests

### 3.2b: test_ship_loading.py - Remove empty class
**File:** `tests/unit/builder/test_ship_loading.py`
- [ ] Read the file
- [ ] Remove `class TestShipExpectedStats: pass` (docstring only, zero test methods)
- [ ] Run tests

### 3.2c: test_allowed_layers_removal.py - Remove one-time migration check
**File:** `tests/unit/systems/test_allowed_layers_removal.py`
- [ ] Read the file
- [ ] Remove `TestAllowedLayersRemoval` class (5 tests checking `allowed_layers` was removed - one-time refactoring verification)
- [ ] KEEP: `TestBuilderDropValidation` class (3 tests verifying ongoing centralized validator behavior)
- [ ] Run tests

### 3.2d: test_validation.py (tech tree) - Remove duplicate classes
**File:** `tests/unit/research/tech_tree/test_validation.py`
- [ ] Read the file
- [ ] Remove `TestDetectCycles` class (duplicated more comprehensively by `test_cycle_detection.py`)
- [ ] Remove `TestDepthCalculation` class (duplicated by `test_queries.py::TestTechTreeDepthCalculation`)
- [ ] KEEP: `TestValidateRequirements`, `TestValidate`, `TestEdgeCases`
- [ ] Run tests

- [ ] Run `pytest tests/unit/builder/ tests/unit/systems/ tests/unit/research/ -x -q` after all 3.2 tasks

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Record post-phase test count: _____ tests passed (delta: _____)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
