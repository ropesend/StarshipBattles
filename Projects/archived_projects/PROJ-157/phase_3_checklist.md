# Phase 3: Partial Cleanups

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-157 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove specific dead classes/methods within files that are otherwise valuable.

**RULE:** Read each file completely before editing. The validation reviews describe what to keep and what to remove - but always verify the current state.

---

## Task 3.1: UI test file partial cleanups [Simple]
**Tests:** `pytest tests/unit/ui/ -x -q --tb=short`

### 3.1a: test_config.py - Remove trivial positivity checks
**File:** `tests/unit/ui/test_config.py`
- [x] Read the file
- [x] Remove pure `assert X > 0` tests (e.g., TestUIConfigPositiveWidth, TestUIConfigPositiveHeight, etc.)
- [x] KEEP: `TestUIConfigAllConstantsAreIntegers`, `test_font_sizes_hierarchy`, `test_confirm_dialog_larger_than_toast`, `test_row_height_large_larger_than_standard`, `test_panel_alpha_in_range`, `test_toast_dimensions_reasonable`
- [x] Run tests

### 3.1b: test_colors.py - Remove trivial literal checks
**File:** `tests/unit/ui/test_colors.py`
- [x] Read the file
- [x] Remove `TestBasicColors` class (3 tests: white==255,255,255, black==0,0,0, white+black opposites)
- [x] Remove `TestFontConstants` class (3 tests: font is string, non-empty, contains common name)
- [x] KEEP: `TestColorsValidation` (5 tests) and `TestColorAccessibility` (3 tests)
- [x] Run tests

### 3.1c: test_scene_protocol.py - Remove mock-attribute test
**File:** `tests/unit/ui/screens/test_scene_protocol.py`
- [x] File does not exist - N/A

### 3.1d: test_game_renderer.py - Remove trivial constant tests
**File:** `tests/unit/ui/renderer/test_game_renderer.py`
- [x] Read the file
- [x] Identify and remove `TestRenderingConstants` or similar class with `assert X > 0` pattern
- [x] KEEP: `TestDrawShipBehavior`, `TestLayerColors`, and other behavioral tests
- [x] Run tests

### 3.1e: test_battle_screen_edge_cases.py - Remove 12 duplicates, keep 6 unique
**File:** `tests/unit/ui/screens/test_battle_screen_edge_cases.py`
- [x] Read the file
- [x] KEEP these 6 unique tests:
  - `test_handle_event_unknown_event_type`
  - `test_handle_mouse_click_none_result` (clears camera target)
  - `test_handle_right_click_no_clear`
  - `test_keydown_f3_toggles_overlay`
  - `test_keydown_comma_respects_minimum` (min speed boundary)
  - `test_keydown_period_respects_maximum` (max speed boundary)
- [x] Remove duplicate tests (those already in test_battle_screen_simulation.py)
- [x] Remove trivial tests: test_handle_resize_updates_dimensions, test_handle_resize_camera_available
- [x] Remove TestBattleStateEdgeCases if redundant with simulation tests
- [x] Run tests

### 3.1f: test_battle_screen_extended.py - Remove 3 duplicates, keep beam test
**File:** `tests/unit/ui/screens/test_battle_screen_extended.py`
- [x] File does not exist - N/A

### 3.1g: test_battle_ui_service.py (flat) - Migrate colors, remove rest
**File:** `tests/unit/ui/services/test_battle_ui_service.py`
**Target:** `tests/unit/ui/services/battle_ui_service/` (subdirectory)
- [x] Read the flat file
- [x] Identify `TestProjectileColors` class (3 tests)
- [x] Migrate TestProjectileColors to appropriate file in subdirectory (test_conversion.py)
- [x] Delete flat file (all other tests duplicated in subdirectory)
- [x] Run tests

- [x] Run `pytest tests/unit/ui/ -x -q --tb=short` after all 3.1 tasks

**Notes:** Removed 18 trivial tests from test_config.py, 6 from test_colors.py, 6 from test_game_renderer.py, 19 from test_battle_screen_edge_cases.py, deleted flat test_battle_ui_service.py (migrated 3 tests). 2 pre-existing test failures unrelated to this project.

---

## Task 3.2: Other partial cleanups [Simple]
**Tests:** `pytest tests/unit/builder/ tests/unit/systems/ tests/unit/research/ -x -q`

### 3.2a: test_bulk_add.py - Remove empty stubs
**File:** `tests/unit/builder/test_bulk_add.py`
- [x] Read the file
- [x] Remove `test_bulk_add_with_limit` method (setup + `pass` body)
- [x] Remove `test_bulk_performance_mock` method (entirely `pass`)
- [x] Run tests

### 3.2b: test_ship_loading.py - Remove empty class
**File:** `tests/unit/builder/test_ship_loading.py`
- [x] Read the file
- [x] Remove `class TestShipExpectedStats: pass` (docstring only, zero test methods)
- [x] Run tests

### 3.2c: test_allowed_layers_removal.py - Remove one-time migration check
**File:** `tests/unit/systems/test_allowed_layers_removal.py`
- [x] Read the file
- [x] Remove `TestAllowedLayersRemoval` class (5 tests checking `allowed_layers` was removed - one-time refactoring verification)
- [x] KEEP: `TestBuilderDropValidation` class (3 tests verifying ongoing centralized validator behavior)
- [x] Run tests

### 3.2d: test_validation.py (tech tree) - Remove duplicate classes
**File:** `tests/unit/research/tech_tree/test_validation.py`
- [x] Read the file
- [x] Remove `TestDetectCycles` class (duplicated more comprehensively by `test_cycle_detection.py`)
- [x] Remove `TestDepthCalculation` class (duplicated by `test_queries.py::TestTechTreeDepthCalculation`)
- [x] KEEP: `TestValidateRequirements`, `TestValidate`, `TestEdgeCases`
- [x] Run tests

- [x] Run `pytest tests/unit/builder/ tests/unit/systems/ tests/unit/research/ -x -q` after all 3.2 tasks

**Notes:** 714 passed. Removed 2 empty stubs, 1 empty class, 5 one-time migration tests, 10 duplicate tests.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Record post-phase test count: 12585 tests collected (delta: -84 from 12669)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
