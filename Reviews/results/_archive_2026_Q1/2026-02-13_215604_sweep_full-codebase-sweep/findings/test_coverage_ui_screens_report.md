# Test Coverage Gaps Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens (game/ui/screens/, game/ui/panels/)
- **Production Files Scanned:** 95+ screen/panel modules
- **Test Files Cross-Referenced:** 53 test files (45 screens, 8 panels)
- **Total Issues Found:** 24
- **Critical:** 3 | **Major:** 10 | **Minor:** 8 | **Info:** 3

## Findings

### Untested Modules (Phase 1)

#### CRITICAL: BattleStateViewer Has No Tests
**ID:** TCG-UI1-001
**Location:** `game/ui/screens/battle_state_viewer.py` (production) / No test file exists
**Issue:** BattleStateViewer contains critical JSON diff logic (`compute_json_diff`, `_mark_all_paths`) with complex recursive comparison for displaying battle state changes. The `ScrollableJsonPanel` class has extensive event handling and rendering logic with zero test coverage.
**Impact:** The JSON diff algorithm (40+ lines) could have edge case bugs with nested structures, type changes, or list handling that would go undetected. The scrollbar interaction logic could fail silently.
**Recommendation:** Write unit tests for `compute_json_diff()` with various JSON structures (nested dicts, lists, type changes, added/removed keys). Test `_get_diff_colors()` color logic.
**Effort:** Medium

#### CRITICAL: TestLab Submodules Completely Untested
**ID:** TCG-UI1-002
**Location:** `game/ui/screens/test_lab/*.py` (8 modules) / No corresponding test files
**Issue:** The entire test_lab subdirectory containing TestLabScreen and its supporting modules (panel_manager.py, test_executor.py, validation_manager.py, data_extractor.py, results_panel.py, ship_panels.py, json_viewer.py, dialogs.py) has no test coverage. These modules manage combat lab test execution, validation, and results display.
**Impact:** Test infrastructure bugs could cause false positives/negatives in combat testing. Test execution logic (TestLabExecutor) could fail without detection.
**Recommendation:** Prioritize tests for TestLabExecutor.execute_test(), ValidationManager validation logic, and DataExtractor ship/component extraction.
**Effort:** Complex

#### CRITICAL: Builder Submodule Interaction Controller Untested
**ID:** TCG-UI1-003
**Location:** `game/ui/screens/builder/interaction_controller.py` (production) / No test file
**Issue:** InteractionController manages drag-and-drop, selection, and drop target registration for the ship builder. This critical input handling code has no tests.
**Impact:** Ship builder drag-drop could silently break. Drop target registration could fail to register targets, causing component placement bugs.
**Recommendation:** Test drag initiation/completion, drop target hit detection, selection rectangle calculation, and hover detection.
**Effort:** Medium

---

### Major Coverage Gaps (Phase 1)

#### MAJOR: Galaxy Test Screen Has No Tests
**ID:** TCG-UI1-004
**Location:** `game/ui/screens/galaxy_test/*.py` (4 files) / No test files
**Issue:** Galaxy test screen including galaxy_mode.py and system_mode.py for visualizing galaxy/system state has no test coverage.
**Impact:** Galaxy visualization debugging tools could fail without detection.
**Recommendation:** Test galaxy_mode and system_mode rendering paths and coordinate transformations.
**Effort:** Medium

#### MAJOR: Ship Stats Renderer Undertested
**ID:** TCG-UI1-005
**Location:** `game/ui/panels/ship_stats_renderer.py` (production) / `tests/unit/ui/panels/test_ship_stats_renderer.py`
**Issue:** While test file exists with 26 tests, key rendering functions are not tested: `draw_ship_weapons()`, `draw_ship_components()`, `draw_weapon_entry()`, `draw_component_entry()`. These iterate over ship layers and render component status.
**Impact:** Component rendering bugs in battle UI could go undetected. Layer iteration logic untested.
**Recommendation:** Add tests verifying weapon/component rendering handles empty lists, None components, and status display.
**Effort:** Simple

#### MAJOR: Column Manager Missing Tests
**ID:** TCG-UI1-006
**Location:** `game/ui/screens/column_manager.py` (production) / No test file
**Issue:** ColumnManager extracted from FleetReportWindow for testability but has no tests. Contains column visibility, ordering, and value extraction logic.
**Impact:** Fleet report columns could display incorrectly or be reordered incorrectly.
**Recommendation:** Test get_visible_columns(), toggle_visibility(), get_value() extraction for various ship properties.
**Effort:** Simple

#### MAJOR: Race Browser Dialog Untested
**ID:** TCG-UI1-007
**Location:** `game/ui/screens/race_browser_dialog.py` (production) / No test file
**Issue:** RaceBrowserDialog handles race selection with asset preview. Selection callbacks, row highlighting, and asset loading untested.
**Impact:** Race loading from library could fail silently. Preview rendering bugs undetected.
**Recommendation:** Test race list population, selection callbacks, and asset loading fallbacks.
**Effort:** Medium

#### MAJOR: Save Selection Window Untested
**ID:** TCG-UI1-008
**Location:** `game/ui/screens/save_selection_window.py` (production) / No test file
**Issue:** SaveSelectionWindow for browsing/loading saves has no tests. Contains turn history expansion, save deletion, and item mapping logic.
**Impact:** Save/load UI bugs could corrupt save handling. Turn history display could fail.
**Recommendation:** Test save list population, turn history expansion, and load callbacks.
**Effort:** Medium

#### MAJOR: Planet Report Panel Untested
**ID:** TCG-UI1-009
**Location:** `game/ui/panels/planet_report_panel.py` (production) / No test file
**Issue:** PlanetReportPanel displays planet information with atmosphere graph, portrait, and complexes list. Has 200+ lines with complex layout logic but no tests.
**Impact:** Planet information display bugs in strategy UI undetected.
**Recommendation:** Test panel initialization, format_planet_info() integration, and resource grid layout.
**Effort:** Medium

#### MAJOR: System Tree Panel Untested
**ID:** TCG-UI1-010
**Location:** `game/ui/panels/system_tree_panel.py` (production) / No test file
**Issue:** SystemTreePanel provides tree navigation UI for star systems with expand/collapse, icons, and positioning. No test coverage.
**Impact:** System navigation tree could have expand/collapse bugs or positioning errors.
**Recommendation:** Test tree item creation, expand/collapse state, and position calculations.
**Effort:** Medium

#### MAJOR: Builder Left Panel Untested
**ID:** TCG-UI1-011
**Location:** `game/ui/screens/builder/left_panel.py` (production) / No test file in builder subdir
**Issue:** BuilderLeftPanel manages component list, bulk add UI (count entry, increment buttons), and filtering. Critical builder functionality untested.
**Impact:** Component list could fail to update. Bulk add count calculation could be wrong.
**Recommendation:** Test component list population, bulk count adjustment, and hover detection.
**Effort:** Medium

#### MAJOR: Schematic View Untested
**ID:** TCG-UI1-012
**Location:** `game/ui/screens/builder/schematic_view.py` (production) / No test file
**Issue:** SchematicView renders ship schematic with layers, components, and firing arcs. Contains scale calculations and arc caching. No tests.
**Impact:** Ship display could render incorrectly. Scale calculations for different ship classes untested.
**Recommendation:** Test _calculate_max_r() for various ship classes, arc cache invalidation.
**Effort:** Medium

#### MAJOR: Workshop Data Reloader Untested
**ID:** TCG-UI1-013
**Location:** `game/ui/screens/workshop_data_reloader.py` (production) / No test file
**Issue:** WorkshopDataReloader orchestrates component/ship data reloading. Complex callback chains untested.
**Impact:** Data reload could fail to update all panels. Partial reload states undetected.
**Recommendation:** Test reload orchestration and callback invocation order.
**Effort:** Medium

---

### Minor Coverage Gaps (Phase 2)

#### MINOR: BattleUI Missing draw() Test
**ID:** TCG-UI1-014
**Location:** `game/ui/screens/battle_ui.py` (production) / `tests/unit/ui/test_battle_panels.py`
**Issue:** BattleUI.draw() method and draw_debug_overlay() have no dedicated tests. Debug overlay draws weapon ranges, aim points, and firing arcs.
**Impact:** Debug visualization could fail silently in battle screen.
**Recommendation:** Test draw_debug_overlay() with various ship configurations.
**Effort:** Simple

#### MINOR: FormationRenderer Missing Tests
**ID:** TCG-UI1-015
**Location:** `game/ui/screens/formation/renderer.py` (production) / `tests/unit/ui/test_formation_renderer.py`
**Issue:** Test file exists but FormationRenderer.draw() and coordinate transformation are not fully tested. Only 2 tests focused on renderer.
**Impact:** Formation editor rendering could have visual bugs.
**Recommendation:** Add tests for draw() with various arrow configurations.
**Effort:** Simple

#### MINOR: Strategy Panel Manager Untested
**ID:** TCG-UI1-016
**Location:** `game/ui/screens/strategy_panel_manager.py` (production) / No test file
**Issue:** StrategyPanelManager coordinates strategy UI panels. Panel creation and lifecycle untested.
**Impact:** Panel state management bugs could cause UI inconsistencies.
**Recommendation:** Test panel creation, visibility toggling, and cleanup.
**Effort:** Simple

#### MINOR: Empire Panel Window Undertested
**ID:** TCG-UI1-017
**Location:** `game/ui/screens/empire_panel_window.py` (production) / No dedicated test file
**Issue:** EmpirePanelWindow showing empire statistics has no dedicated tests.
**Impact:** Empire statistics display bugs undetected.
**Recommendation:** Test panel initialization with various empire states.
**Effort:** Simple

#### MINOR: Fleet Orders Window Undertested
**ID:** TCG-UI1-018
**Location:** `game/ui/screens/fleet_orders_window.py` (production) / No test file
**Issue:** FleetOrdersWindow for displaying/editing fleet orders has no tests.
**Impact:** Fleet order display and editing could fail silently.
**Recommendation:** Test order list display and edit callbacks.
**Effort:** Simple

#### MINOR: Design Selector Window Edge Cases
**ID:** TCG-UI1-019
**Location:** `game/ui/screens/design_selector_window.py` (production) / `tests/unit/ui/screens/test_design_selector_window.py`
**Issue:** Tests exist (35 tests) but no tests for empty design list, None values, or very long design names.
**Impact:** Edge case bugs could cause UI crashes with unusual data.
**Recommendation:** Add tests for empty design list, None design_name, and truncation of long names.
**Effort:** Simple

#### MINOR: Base Gallery Panel Missing Tests
**ID:** TCG-UI1-020
**Location:** `game/ui/panels/base_gallery.py` (production) / No test file
**Issue:** BaseGallery provides reusable scrollable gallery functionality. No tests for scroll handling or selection.
**Impact:** Gallery scrolling bugs could affect race setup screens.
**Recommendation:** Test scroll offset calculation, selection callback.
**Effort:** Simple

#### MINOR: Design Report Panel Undertested
**ID:** TCG-UI1-021
**Location:** `game/ui/panels/design_report_panel.py` (production) / No test file
**Issue:** DesignReportPanel for displaying ship design details has no tests.
**Impact:** Design report display bugs undetected.
**Recommendation:** Test report generation with various ship configurations.
**Effort:** Simple

---

### Test Quality Issues (Phase 4)

#### INFO: Heavy Mocking Pattern in Screen Tests
**ID:** TCG-UI1-022
**Location:** `tests/unit/ui/screens/test_workshop_screen.py`, `tests/unit/ui/screens/test_strategy_screen.py`
**Issue:** Tests use bypass-init pattern and mock nearly all dependencies. While this isolates units, some tests mock the method they're testing (e.g., `screen._save_ship = lambda: screen.ship_io.save_ship()` then calling `screen._save_ship()`).
**Impact:** Tests verify delegation patterns but don't catch integration bugs between real implementations.
**Recommendation:** Add some integration tests that exercise real method implementations with minimal mocking.
**Effort:** Medium

#### INFO: Battle Panels Tests Reload Module
**ID:** TCG-UI1-023
**Location:** `tests/unit/ui/test_battle_panels.py`
**Issue:** Tests use `importlib.reload(battle_panels)` which can cause module state inconsistencies across test runs. Tests patch `sys.modules['pygame']` directly.
**Impact:** Tests may pass in isolation but fail when run with other tests.
**Recommendation:** Use more isolated pytest fixtures instead of module reload.
**Effort:** Medium

#### INFO: Missing Serialization Round-Trip Tests
**ID:** TCG-UI1-024
**Location:** Various screen modules
**Issue:** Several screens handle save/load operations (SaveSelectionWindow, SetupDataIO) but lack round-trip serialization tests verifying that saved state can be correctly reloaded.
**Impact:** Save/load bugs could cause data corruption.
**Recommendation:** Add serialization round-trip tests for setup_data_io, save operations.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **TCG-UI1-002 (CRITICAL):** TestLab submodules have zero test coverage. This is test infrastructure testing test infrastructure - meta-level critical. Test execution and validation logic must be verified.

2. **TCG-UI1-001 (CRITICAL):** BattleStateViewer's JSON diff algorithm has no tests. This 40+ line recursive diff algorithm handles complex nested JSON structures and needs comprehensive edge case testing.

3. **TCG-UI1-003 (CRITICAL):** InteractionController handles all ship builder drag-drop. A bug here breaks the core builder workflow.

4. **TCG-UI1-006 (MAJOR):** ColumnManager was explicitly extracted "for testability" per code comment but has no tests. This defeats the purpose of the extraction.

5. **TCG-UI1-009 (MAJOR):** PlanetReportPanel is a frequently-used component in strategy layer with 200+ lines and no tests. Strategy planet inspection relies on this panel.

---

## Module Coverage Matrix

| Production Module | Test File Exists | Estimated Coverage |
|-------------------|------------------|--------------------|
| battle_state_viewer.py | No | 0% |
| battle_screen.py | Yes | 60% |
| battle_ui.py | Partial | 40% |
| builder/*.py (8 files) | No | 0% |
| formation/*.py (3 files) | Partial | 50% |
| galaxy_test/*.py (4 files) | No | 0% |
| test_lab/*.py (8 files) | No | 0% |
| workshop_screen.py | Yes | 70% |
| strategy_screen.py | Yes | 65% |
| setup_screen.py | Yes | 70% |
| race_setup_screen.py | Yes | 60% |
| battle_panels.py | Yes | 70% |
| ship_stats_renderer.py | Yes | 50% |
| planet_report_panel.py | No | 0% |
| system_tree_panel.py | No | 0% |
| design_stats_panel.py | Yes | 60% |

---

## Recommendations Summary

1. **Immediate Priority:** Add tests for `compute_json_diff()` in battle_state_viewer.py
2. **High Priority:** Create test files for test_lab submodules, especially TestLabExecutor
3. **Medium Priority:** Test builder/interaction_controller.py drag-drop logic
4. **Low Priority:** Add edge case tests to existing test files (empty lists, None values)
5. **Technical Debt:** Reduce heavy mocking patterns in screen tests, add some integration tests
