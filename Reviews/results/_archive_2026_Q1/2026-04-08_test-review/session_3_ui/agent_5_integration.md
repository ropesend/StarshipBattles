# Test Review Report: Agent 5 -- UI Integration + Test Lab

## Scope
- Source files reviewed: 16 test_lab files (6091 LOC), battle_ui.py (244 LOC), orchestration/__init__.py (1 LOC) = 6336 LOC total
- Test files reviewed: 19 files (4239 LOC total)
  - tests/unit/ui/test_lab_scene/ (3 files, 1161 LOC)
  - tests/unit/ui/test_lab_formatting_utils.py (152 LOC)
  - tests/unit/ui/interfaces/test_battle_ui.py (352 LOC)
  - tests/unit/ui/mocks/__init__.py (7 LOC)
  - tests/unit/ui/battle_state_viewer/ (3 files, 762 LOC)
  - tests/unit/ui/schematic_view/ (2 files, 682 LOC)
  - tests/unit/ui/left_panel/ (3 files, 590 LOC)
  - tests/integration/ui/conftest.py (59 LOC)
  - tests/unit/ui/test_scene_protocol.py (114 LOC)
  - tests/unit/ui/test_ui_imports.py (81 LOC)
  - tests/unit/ui/test_structure_visibility.py (184 LOC)
- Coverage data referenced: yes -- all 22 test_lab source files plus related UI files

## Summary
- Test files reviewed: 19
- Source files reviewed: 18
- Tests flagged for removal: 12 test classes (estimated LOC: 1823)
- Tests flagged as happy-path-only: 3
- Source files with inadequate coverage: 8

## A. Tests Recommended for Removal

### A1. Dead Mock Module
- **File:** `tests/unit/ui/mocks/__init__.py`
- **Test(s):** entire module
- **Reason:** DEAD_CODE
- **Confidence:** HIGH
- **Evidence:** The file contains only a docstring and `__all__ = []` (7 lines). Grep of the entire `tests/` tree for any import from `tests.unit.ui.mocks` or `from .mocks` returns zero matches. No test in the project imports from this module.
- **Estimated LOC saved:** 7

### A2. Reimplemented Logic Tests -- test_lab_scene/test_logic.py
- **File:** `tests/unit/ui/test_lab_scene/test_logic.py`
- **Test(s):** `TestJSONFormatting`, `TestComponentDropdownSelection`, `TestDropdownOptionIndex`, `TestValueFormatting`, `TestShipExtractionLogic`, `TestComponentIdExtraction`, `TestValidationStatusColors`, `TestValidationSymbols`, `TestPValueInterpretation`, `TestDifferenceCalculation`, `TestBatchExecutionState` (11 classes, 493 LOC)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** This file has ZERO imports from `game.*`. Every test class reimplements the logic locally as a method on the test class (e.g., `self.format_json()`, `self.get_selected_component_id()`, `self.calculate_progress()`), then tests that reimplementation. These tests do not import or call `ComponentDropdown.get_selected_component_id()` (line 98-103 of component_dropdown.py), `format_value()` from formatting_utils.py, or any actual source code. They test standalone pure functions defined inline in the test file. If the real source code changes, these tests continue to pass -- they are untethered from production code entirely.
- **Estimated LOC saved:** 493

### A3. Reimplemented Logic Tests -- test_lab_scene/test_rendering.py
- **File:** `tests/unit/ui/test_lab_scene/test_rendering.py`
- **Test(s):** `TestRenderingCalculations`, `TestColorPalettes`, `TestFontRendering`, `TestScrollbarRendering`, `TestGridRendering`, `TestButtonRendering`, `TestComponentPreviewRendering`, `TestTooltipRendering` (8 classes, 361 LOC)
- **Reason:** TESTS_NOTHING_REAL | TRIVIAL_CONSTANT
- **Confidence:** HIGH
- **Evidence:** Zero imports from `game.*`. Every test class defines its own inline math (e.g., `left_w = left_panel_width - margin * 2; assert left_w == 380`). Tests like `TestColorPalettes.test_valid_rgb_color` assert that hardcoded tuples have values 0-255. `TestButtonRendering.test_button_state_colors` just asserts four inline color tuples are not equal. None of this tests any actual renderer code from `game.ui.screens.test_lab.renderer`. The 3 `TestSurfaceCreation` tests do exercise pygame but only test pygame's own API (SRCALPHA flag, fill color), not project code.
- **Estimated LOC saved:** 361

### A4. Reimplemented Logic Tests -- test_lab_scene/test_ui_components.py
- **File:** `tests/unit/ui/test_lab_scene/test_ui_components.py`
- **Test(s):** `TestJSONPopupDimensions`, `TestJSONPopupScrolling`, `TestConfirmationDialogDimensions`, `TestScrollableJSONViewer`, `TestTabbedShipPanelTabs`, `TestTabSelection`, `TestDetailsScrollCalculations`, `TestScrollbarCalculations` (8 classes, 306 LOC)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Zero imports from `game.*`. Each class reimplements arithmetic (e.g., popup dimensions = `int(screen_width * 0.8)`) then asserts the result. None instantiate `JSONPopup`, `ConfirmationDialog`, `TabbedShipPanel`, or `TestRunDetailsPanel`. If the real dialog dimensions change (e.g., from 80% to 70%), these tests would still pass because they test their own copy of the formula.
- **Estimated LOC saved:** 306

### A5. Reimplemented Logic Tests -- battle_state_viewer/test_json_diff.py
- **File:** `tests/unit/ui/battle_state_viewer/test_json_diff.py`
- **Test(s):** `TestComputeJsonDiff`, `TestMarkAllPaths`, `TestDiffResultConstants`, `TestJsonPathMatching` (4 classes, 347 LOC)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Zero imports from `game.*`. `TestComputeJsonDiff` reimplements a complete `compute_json_diff()` function inline (lines 20-58) and tests that. The actual `compute_json_diff` in `game/ui/screens/battle_state_viewer.py` is not imported or exercised. `TestDiffResultConstants` asserts that 4 hardcoded strings are distinct -- pure TRIVIAL_CONSTANT.
- **Estimated LOC saved:** 347

### A6. Reimplemented Logic Tests -- battle_state_viewer/test_ui_logic.py
- **File:** `tests/unit/ui/battle_state_viewer/test_ui_logic.py`
- **Test(s):** `TestDiffColorSelection`, `TestScrollOffsetCalculations`, `TestDiffStatistics` (3 classes, 178 LOC)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Zero imports from `game.*`. All methods are defined inline on the test class. The actual battle_state_viewer rendering code at `game/ui/screens/battle_state_viewer.py` (127 stmts, 29.9% coverage) is not exercised.
- **Estimated LOC saved:** 178

### A7. Reimplemented Logic Tests -- battle_state_viewer/test_viewer_ui.py
- **File:** `tests/unit/ui/battle_state_viewer/test_viewer_ui.py`
- **Test(s):** `TestLineRenderingCalculations`, `TestIndentLevelCalculation`, `TestPanelVisibilityToggle`, `TestDualPanelSync`, `TestKeyboardNavigation` (5 classes, 236 LOC)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Zero imports from `game.*`. `TestPanelVisibilityToggle.test_toggle_visibility` literally tests `visible = not visible` with inline code. `TestDualPanelSync` tests a dict `.get()` call. `TestKeyboardNavigation` reimplements scroll logic inline.
- **Estimated LOC saved:** 236

### A8. Reimplemented Logic Tests -- schematic_view/test_geometry.py
- **File:** `tests/unit/ui/schematic_view/test_geometry.py`
- **Test(s):** `TestMaxRadiusCalculation`, `TestArcAngleCalculations`, `TestArcPolygonPoints`, `TestDisplayRangeCalculation`, `TestLayerRingColors`, `TestLayerRingRadius` (6 classes, 357 LOC)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Zero imports from `game.*`. All geometry functions are reimplemented inline. The actual `game/ui/screens/builder/schematic_view.py` (83.6% coverage) is not imported. Note: This file overlaps with Agent 4's domain (builder/schematic_view), but the finding is the same -- these tests exercise nothing real.
- **Estimated LOC saved:** 357

### A9. Reimplemented Logic Tests -- schematic_view/test_rendering_logic.py
- **File:** `tests/unit/ui/schematic_view/test_rendering_logic.py`
- **Test(s):** `TestWeaponArcColorSelection`, `TestCacheKeyGeneration`, `TestRectCenterCalculation`, `TestImageScalingCalculation`, `TestScaledImageDimensions`, `TestGetComponentAt` (6 classes, 324 LOC)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Zero imports from `game.*`. `TestGetComponentAt` tests a function that always returns None (lines 309-319). `TestCacheKeyGeneration` tests that creating a tuple produces a tuple. `TestRectCenterCalculation` tests `x + width // 2`.
- **Estimated LOC saved:** 324

### A10. Reimplemented Logic Tests -- left_panel/test_bulk_add.py
- **File:** `tests/unit/ui/left_panel/test_bulk_add.py`
- **Test(s):** `TestBulkAddCounterLogic`, `TestButtonIncrementLogic` (2 classes, 165 LOC)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Zero imports from `game.*`. Each test method redefines `get_add_count()` as a local function, then asserts clamping behavior. The actual left_panel code at `game/ui/screens/builder/left_panel.py` (43.1% coverage) is not imported or tested. Note: This file overlaps with Agent 4's domain.
- **Estimated LOC saved:** 165

### A11. Reimplemented Logic Tests -- left_panel/test_selection_hover.py
- **File:** `tests/unit/ui/left_panel/test_selection_hover.py`
- **Test(s):** `TestSelectionStateLogic`, `TestDropdownStateLogic`, `TestHoverDetectionLogic`, `TestGetHoveredComponentLogic` (4 classes, 144 LOC)
- **Reason:** TESTS_NOTHING_REAL | OVER_MOCKED
- **Confidence:** HIGH
- **Evidence:** Zero imports from `game.*`. Tests define local functions that mimic hover logic. `TestHoverDetectionLogic` creates local functions with Mock objects that test the mock's return values, not real code. The actual left_panel hover detection code is untested.
- **Estimated LOC saved:** 144

### A12. Reimplemented Logic Tests -- left_panel/test_sorting_filtering.py
- **File:** `tests/unit/ui/left_panel/test_sorting_filtering.py`
- **Test(s):** `TestSortingLogic`, `TestFilteringLogic`, `TestTypeFilterOptions`, `TestComponentOrderMap`, `TestRegistryReloadLogic` (5 classes, 280 LOC)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Zero imports from `game.*`. Tests use Python's built-in `sorted()` with Mock objects, testing Python stdlib behavior rather than actual left_panel sorting/filtering code. Example: `sorted(components, key=lambda c: c.name)` is tested, but `LeftPanel._sort_components()` is not imported.
- **Estimated LOC saved:** 280

**Total estimated LOC for removal: ~3198 lines across 12 items.**
**Pattern note:** Items A2-A12 all follow the same anti-pattern: reimplementing source logic inline in the test file rather than importing and testing the real code. This is a systematic issue suggesting these were bulk-generated without being connected to actual source modules.

## B. Tests That Are Happy-Path-Only

### B1. test_lab_formatting_utils.py
- **File:** `tests/unit/ui/test_lab_formatting_utils.py`
- **Test(s):** `TestFormatValueNoneAndBasicTypes`, `TestFormatValueFloatFull`, `TestFormatValueFloatCompact`, `TestFormatValueEdgeCases`
- **What's tested:** The `format_value()` function from `game.ui.screens.test_lab.formatting_utils` with valid inputs and expected edge cases. This is the ONLY test in the test_lab_scene area that actually imports and tests real source code.
- **What's missing:** No tests for list/dict inputs, deeply nested objects, extremely large floats (inf), NaN, negative zero, or very long strings. However, the function is simple enough that the current tests are reasonable.
- **Source method(s) affected:** `game/ui/screens/test_lab/formatting_utils.py:8` (`format_value`)
- **Priority:** LOW -- the function is small (67 LOC) and at 100% coverage already

### B2. test_battle_ui.py
- **File:** `tests/unit/ui/interfaces/test_battle_ui.py`
- **Test(s):** `TestResourceDTO`, `TestComponentDTO`, `TestShipDTO`, `TestProjectileDTO`, `TestBeamDTO`, `TestIBattleUIProtocol`
- **What's tested:** DTO creation, frozen immutability, protocol structural typing. Good contract tests.
- **What's missing:** No tests for DTO equality, hashing, or repr behavior. No edge cases for DTOs with None fields where Optional is allowed. `test_invalid_implementation_fails_check` only tests a class missing 5 of 6 methods -- does not test missing just 1 method.
- **Source method(s) affected:** `game/ui/interfaces/battle_ui.py:16-244`
- **Priority:** LOW -- source is at 100% coverage and DTOs are simple frozen dataclasses

### B3. test_scene_protocol.py
- **File:** `tests/unit/ui/test_scene_protocol.py`
- **Test(s):** `TestISceneProtocolCompliance`, `TestSceneCallback`
- **What's tested:** All 9 scene classes structurally implement IScene; BattleScreen callback routing
- **What's missing:** Tests only verify structural compliance (hasattr), never call handle_event/update/draw with actual events. `TestSceneCallback` only tests one callback routing path (return_to_destination). Does not test error handling in callbacks or invalid action strings.
- **Source method(s) affected:** All scene classes' IScene implementations
- **Priority:** MEDIUM -- these are important API contract tests but should exercise actual method calls

## C. Source Code with Inadequate Coverage

### C1. test_run_details.py -- CRITICAL GAP
- **Source file:** `game/ui/screens/test_lab/test_run_details.py` (957 LOC)
- **Coverage:** 5.2% (32/610 stmts) -- MASSIVE gap, the single largest coverage gap in the entire UI
- **Untested areas:**
  - `_draw_header_and_status()` (lines 176-195)
  - `_draw_metadata()` (lines 197-215)
  - `_draw_action_buttons()` -- 3 button rendering paths (lines 217-307)
  - `_draw_metrics()` (lines 309-332)
  - `_draw_validation_results()` (lines 334-392) -- phase grouping logic
  - `_draw_single_validation()` (lines 394-485) -- expected/actual/p-value display
  - `_draw_numeric_difference()` (lines 487-530) -- percentage diff, boolean skip, exact match
  - `_draw_propulsion_outcomes()` (lines 776-815) -- turn/motion/stationary branching
  - `_draw_resource_outcomes()` (lines 542-581) -- fuel/energy/ammo branching
  - `_draw_fuel_outcomes()`, `_draw_energy_outcomes()`, `_draw_ammo_outcomes()` (lines 583-774)
  - `handle_event()` -- button click handling with 3 button types (lines 90-123)
  - `_calculate_scroll()` -- scroll calculation (lines 68-88)
- **Risk:** This is the detailed test results panel -- the primary way developers see test pass/fail details. Changes to validation result display, numeric difference formatting, or resource outcome rendering have zero test coverage. Boolean skip logic in `_draw_numeric_difference()` (line 496) prevents false diffs but has no test. The phase grouping logic (data/precondition/outcome) is tested nowhere.
- **Priority:** HIGH

### C2. renderer.py -- CRITICAL GAP
- **Source file:** `game/ui/screens/test_lab/renderer.py` (1193 LOC)
- **Coverage:** 6.8% (45/663 stmts) -- second largest coverage gap
- **Untested areas:**
  - `draw()` main method and all 3 column renders (lines 55-113)
  - `_draw_header_seed_controls()` -- seed mode button rendering (lines 128-227)
  - `_draw_category_sidebar()` -- group tree with expand/collapse (lines 229-325)
  - `_draw_tag_filters()` -- tag filter buttons with 3-state cycle (lines 327-429)
  - `_draw_test_list()` -- scrollable test list with flags (lines 431-546)
  - `_draw_metadata_panel()` -- test details with conditions, validation (lines 577-713)
  - `_draw_validation_section()` -- phase-grouped validation display (lines 902-1020)
  - `_draw_validation_check_compact()` -- per-check rendering (lines 1022-1092)
  - `_format_check_pair()` -- value alignment formatting (lines 1094-1130) -- this is a pure function that COULD be tested without pygame
  - `_is_condition_verified()` -- condition-to-validation mapping (lines 783-864) -- complex regex parsing logic with no tests
  - `_draw_validation_flag()` -- pass/fail/warn circle (lines 1132-1185)
- **Risk:** The renderer is the visual entry point for the entire Combat Lab. The `_is_condition_verified()` method at lines 783-864 contains complex regex parsing and a large mapping dictionary that could silently break. The `_format_check_pair()` static method (lines 1094-1130) is a pure function with formatting logic that should have unit tests.
- **Priority:** HIGH -- especially `_format_check_pair()` and `_is_condition_verified()` which are pure logic extractable from pygame

### C3. test_run_card.py
- **Source file:** `game/ui/screens/test_lab/test_run_card.py` (367 LOC)
- **Coverage:** 5.9% (14/237 stmts)
- **Untested areas:**
  - `draw()` and `_draw_header()` -- card rendering (lines 74-214)
  - `_draw_propulsion_metrics()` -- turn/motion/stationary display (lines 216-277)
  - `_draw_resource_metrics()` -- fuel/energy/ammo display (lines 289-367)
  - `handle_click()` -- click detection (lines 62-67)
  - `handle_hover()` -- hover state (lines 69-72)
- **Risk:** Test run cards are the clickable elements in test history. Propulsion and resource metric display has complex branching (is_turn_test, has_motion, fuel vs energy vs ammo) with zero coverage.
- **Priority:** MEDIUM -- rendering code is inherently harder to unit test, but click/hover logic is testable

### C4. results_panel.py
- **Source file:** `game/ui/screens/test_lab/results_panel.py` (265 LOC)
- **Coverage:** 10.3% (16/156 stmts)
- **Untested areas:**
  - `set_test()` -- card creation and auto-selection logic (lines 58-94)
  - `handle_event()` -- clear buttons, card clicks, scroll (lines 112-149)
  - `draw()` -- scroll clipping, card positioning (lines 160-189)
  - `_draw_header()` -- button rendering (lines 191-234)
- **Risk:** The auto-select-latest-run logic (lines 88-94) and card selection state management are business logic with no tests.
- **Priority:** MEDIUM

### C5. component_dropdown.py
- **Source file:** `game/ui/screens/test_lab/component_dropdown.py` (154 LOC)
- **Coverage:** 11.0% (9/82 stmts)
- **Untested areas:**
  - `handle_click()` -- expand/collapse/option selection logic (lines 46-81)
  - `handle_hover()` -- hover index tracking (lines 83-96)
  - `draw()` -- dropdown rendering with arrow, options (lines 105-155)
- **Risk:** Click handling has 4 branches (click header closed, click header open, click option, click outside) -- none tested. The `get_selected_component_id()` method IS tested but only via the reimplemented version in test_logic.py (which does not import the real code).
- **Priority:** MEDIUM

### C6. screen_input_handler.py
- **Source file:** `game/ui/screens/test_lab/screen_input_handler.py` (399 LOC)
- **Coverage:** 11.8% (22/186 stmts)
- **Untested areas:**
  - `handle_event()` -- event dispatch chain (lines 54-84)
  - `_handle_dialog_events()` -- dialog close detection (lines 86-107)
  - `_handle_panel_events()` -- panel event forwarding (lines 109-140)
  - `_handle_scroll_and_mouse()` -- scroll, hover, click dispatch (lines 142-169)
  - `_update_hover_state()` -- hit testing for categories, groups, tests (lines 171-222)
  - `_handle_click()` -- 5-way click dispatch (lines 224-243)
  - `_check_category_clicks()`, `_check_tag_filter_clicks()`, `_check_test_item_click()`, `_check_action_button_clicks()`, `_check_seed_mode_clicks()` (lines 245-399)
- **Risk:** This is the entire input handling for the Combat Lab. Every user interaction flows through these methods. The scroll-adjusted hit testing in `_update_hover_state()` (lines 210-222) involves coordinate math that could have off-by-one errors with zero test coverage.
- **Priority:** HIGH

### C7. dialogs.py
- **Source file:** `game/ui/screens/test_lab/dialogs.py` (271 LOC)
- **Coverage:** 13.4% (19/142 stmts)
- **Untested areas:**
  - `JSONPopup` -- popup lifecycle, scroll, close (lines 16-122)
  - `ConfirmationDialog` -- confirm/cancel callbacks, button lifecycle (lines 124-271)
  - `handle_event()` for both dialogs -- Escape key, button press, scroll (lines 69-83, 203-216)
- **Risk:** Dialog confirm/cancel callback wiring could silently break. The `_kill_buttons()` cleanup (lines 196-201) prevents UI element leaks but is untested.
- **Priority:** MEDIUM

### C8. ship_panels.py
- **Source file:** `game/ui/screens/test_lab/ship_panels.py` (257 LOC)
- **Coverage:** 18.1% (23/127 stmts)
- **Untested areas:**
  - `TabbedShipPanel` -- tab click handling, tab width calculation, viewer switching (lines 56-184)
  - `ComponentPanel` -- dropdown/viewer coordination on selection change (lines 187-257)
  - `ShipPanel` -- simple delegation (lines 15-53) -- low risk
- **Risk:** `TabbedShipPanel._calculate_tab_rects()` computes layout math. `ComponentPanel.handle_event()` coordinates dropdown selection with JSON viewer update -- this state coordination is untested.
- **Priority:** LOW

## D. Cross-Domain Observations

### D1. Systematic "Reimplemented Logic" Anti-Pattern (CRITICAL)
Items A2 through A12 represent **~3200 LOC of tests that test NOTHING real**. Every single one reimplements source logic as local functions/methods and tests those copies. This pattern was likely generated in bulk. These tests:
- Inflate the test count without providing regression protection
- Will never fail when real source code changes (they are disconnected)
- Create false confidence in coverage of UI logic
- Should be either deleted or rewritten to import actual source modules

The affected directories span three agent domains:
- `tests/unit/ui/test_lab_scene/` (Agent 5 -- this report)
- `tests/unit/ui/battle_state_viewer/` (Agent 5 -- this report)
- `tests/unit/ui/schematic_view/` (overlaps Agent 4)
- `tests/unit/ui/left_panel/` (overlaps Agent 4)

**Recommendation:** Delete all reimplemented-logic tests. For the small subset of pure logic functions (like `_format_check_pair()`, `_is_condition_verified()`, `format_value()`) that CAN be tested without pygame, write real tests that import the actual source code.

### D2. Two Extractable Pure Functions with Zero Coverage
- `TestLabRenderer._format_check_pair()` (lines 1094-1130 of renderer.py) is a `@staticmethod` that formats expected/actual value pairs. It has zero pygame dependency and is trivially testable.
- `TestLabRenderer._is_condition_verified()` (lines 783-864 of renderer.py) does regex parsing and mapping. It only needs the condition text and validation results dicts -- no pygame. Both should be extracted and tested.

### D3. Integration Test conftest.py is Useful Infrastructure (KEEP)
`tests/integration/ui/conftest.py` provides a cached `UIManager` fixture for UI integration tests. It properly handles pygame lifecycle and display surface changes. This is shared infrastructure, not a test, and should be kept.

### D4. test_scene_protocol.py and test_ui_imports.py are Valuable (KEEP)
These test API contracts (IScene protocol compliance) and import stability. They are lightweight structural tests that catch real breakage. `test_structure_visibility.py` is a thorough integration test for hull layer visibility toggle that exercises real `LayerPanel` code with proper mocking -- a model for how the removed test files should have been written.

### D5. Coverage Summary for Test Lab Source Files
| File | Stmts | Coverage | Status |
|------|-------|----------|--------|
| test_run_details.py | 610 | 5.2% | CRITICAL |
| test_run_card.py | 237 | 5.9% | CRITICAL |
| renderer.py | 663 | 6.8% | CRITICAL |
| results_panel.py | 156 | 10.3% | LOW |
| component_dropdown.py | 82 | 11.0% | LOW |
| screen_input_handler.py | 186 | 11.8% | HIGH |
| dialogs.py | 142 | 13.4% | MEDIUM |
| ship_panels.py | 127 | 18.1% | LOW |
| screen.py | 349 | 47.3% | MEDIUM |
| test_executor.py | 235 | 49.4% | MEDIUM |
| data_extractor.py | 70 | 71.4% | OK |
| panel_manager.py | 76 | 73.7% | OK |
| viewmodel.py | 175 | 90.9% | GOOD |
| formatting_utils.py | 27 | 100% | GOOD |
| theme.py | 97 | 100% | GOOD |
| __init__.py | 3 | 100% | GOOD |

**Total: 3235 statements across 16 files. Weighted average coverage: ~28%.**

The top 3 files (test_run_details.py, test_run_card.py, renderer.py) account for 1510 statements at 5-7% coverage. These represent the bulk of the visual Combat Lab UI and are essentially untested. The ~3200 LOC of "reimplemented logic" tests create the illusion that this area has test coverage when in fact zero real source code is being exercised.
