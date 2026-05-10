# Test Coverage Gaps Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens (game/ui/screens/ and game/ui/panels/)
- **Production Files Scanned:** 103 (62 in screens/, 17 in screens/builder/, 13 in screens/test_lab/, 4 in screens/formation/, 3 in screens/galaxy_test/, 24 in panels/)
- **Test Files Cross-Referenced:** 47 (39 in tests/unit/ui/screens/, 8 in tests/unit/ui/panels/)
- **Total Issues Found:** 32
- **Critical:** 4 | **Major:** 14 | **Minor:** 10 | **Info:** 4

---

## Findings

### CRITICAL Issues

#### CRITICAL: Entire builder/ subpackage has zero test coverage (1,123-line main.py + 12 modules)
**ID:** TCG-UI1-001
**Location:** `game/ui/screens/builder/` (17 production files) / No test directory exists
**Issue:** The entire `game/ui/screens/builder/` subpackage has NO corresponding test files at all. This includes:
- `main.py` (1,123 lines) - Legacy standalone ship builder GUI
- `state_manager.py` (284 lines) - Builder state management with selection, drag/drop, modifiers
- `weapons_panel.py` (1,037 lines) - Weapons report panel
- `layer_panel.py` (513 lines) - Layer structure panel
- `left_panel.py` (476 lines) - Component palette panel
- `stats_config.py` (625 lines) - Stats configuration
- `structure_list_items.py` (442 lines) - Structure list rendering
- `right_panel.py` (392 lines) - Ship stats panel
- `modifier_row.py` (338 lines) - Modifier control rows
- `detail_panel.py` (296 lines) - Component detail display
- `modifier_editor.py` (196 lines) - Modifier editing
- `schematic_view.py` (194 lines) - Ship schematic rendering
- `modifier_logic.py` (176 lines) - **Pure logic** for modifier validation/calculations
- `interaction_controller.py` (161 lines) - Click/drag interaction handling
- `grouping_strategies.py` (77 lines) - **Pure logic** for component grouping
- `event_bus.py` (56 lines) - **Pure logic** publish/subscribe event bus
- `component_ref.py` (64 lines) - Component reference utilities

**Impact:** 5,450+ lines of production code with zero test coverage. Several modules contain **pure logic** (no Pygame dependencies) that is trivially testable: `event_bus.py`, `grouping_strategies.py`, `modifier_logic.py`, `state_manager.py`. Regressions in builder selection, modifier validation, or event routing would go undetected.
**Recommendation:** Prioritize tests for pure-logic modules first: `event_bus.py` (subscribe/emit/unsubscribe), `grouping_strategies.py` (DefaultGroupingStrategy, TypeGroupingStrategy, FlatGroupingStrategy), `modifier_logic.py` (is_modifier_allowed, get_mandatory_modifiers), `state_manager.py` (selection management, drag state). Then add bypass-init pattern tests for UI-heavy modules.
**Effort:** Medium (pure-logic tests are simple; UI panel tests require mock scaffolding)

---

#### CRITICAL: Entire test_lab/ subpackage has zero test coverage (1,908-line screen.py + 7 modules)
**ID:** TCG-UI1-002
**Location:** `game/ui/screens/test_lab/` (13 production files) / No test directory exists
**Issue:** The entire `game/ui/screens/test_lab/` subpackage has NO test files. Key modules:
- `screen.py` (1,908 lines) - TestLabScreen main orchestrator (largest single file in the shard)
- `test_run_details.py` (893 lines) - Test run detail display
- `test_executor.py` (383 lines) - Test execution logic
- `test_run_card.py` (365 lines) - Test run card rendering
- `validation_manager.py` (310 lines) - **Pure logic** test validation
- `results_panel.py` (256 lines) - Results display
- `data_extractor.py` (210 lines) - **Pure logic** data extraction from test scenarios
- `panel_manager.py` (233 lines) - Panel layout management
- `ship_panels.py` (255 lines) - Ship info display panels
- `component_dropdown.py` (153 lines) - Component selection dropdown
- `json_viewer.py` (122 lines) - JSON display widget
- `formatting_utils.py` (67 lines) - **Pure logic** formatting helpers
- `dialogs.py` (266 lines) - Dialog windows

**Impact:** 5,021+ lines with zero coverage. The `data_extractor.py`, `validation_manager.py`, and `formatting_utils.py` modules are pure logic with no UI dependencies. The `test_executor.py` orchestrates battle test runs - a failure here would break the Combat Lab entirely.
**Recommendation:** Start with `formatting_utils.py` and `data_extractor.py` (pure logic, zero mocking needed). Then add tests for `validation_manager.py` and `test_executor.py`.
**Effort:** Medium

---

#### CRITICAL: Entire formation/ subpackage has zero test coverage
**ID:** TCG-UI1-003
**Location:** `game/ui/screens/formation/` (4 production files) / No test directory exists
**Issue:** The `game/ui/screens/formation/` subpackage has no tests:
- `input_handler.py` (422 lines) - Mouse/keyboard input handling for formation editor
- `renderer.py` (427 lines) - Formation rendering with grid, arrows, selection

Note: `formation_editor.py` (929 lines, in screens/ root) **does** have a test file (`test_formation_editor_screen.py`, 551 lines, 30 tests). However, the delegated submodules in `formation/` are untested directly.
**Impact:** 849 lines untested. The input handler contains coordinate transformations (world_to_screen, screen_to_world, snap calculations) that are pure math and easily testable. If input handling or rendering breaks, formation editing becomes unusable.
**Recommendation:** Test `input_handler.py` coordinate math functions and `renderer.py` layout calculations. The formation_editor tests may exercise these indirectly, but direct unit tests would catch edge cases.
**Effort:** Simple

---

#### CRITICAL: BattleScreen and BattleUI have zero unit tests
**ID:** TCG-UI1-004
**Location:** `game/ui/screens/battle_screen.py` (660 lines) + `game/ui/screens/battle_ui.py` (285 lines) / No test files
**Issue:** The core battle screen (BattleScreen) and its UI layer (BattleUI) have no unit tests. BattleScreen manages:
- Battle initialization and ship setup (`start()`)
- Simulation stepping (`update()`)
- Battle over detection (`is_battle_over()`, `get_winner()`)
- Speed multiplier control (MIN/MAX constants, pause/resume)
- Event handling and click routing
- Controller pattern for unified battle modes

BattleUI manages panel creation, resize handling, and overlay drawing.
**Impact:** The battle is the core gameplay loop. While simulation tests exercise the underlying engine, the screen-level integration (starting battles, speed control, event routing, overlay toggling) has no tests. Regressions in battle initialization or UI event routing would go undetected.
**Recommendation:** Add bypass-init pattern tests for BattleScreen focusing on: speed multiplier logic, battle start parameter handling, controller get/set, and battle-over state checks. BattleUI resize logic is also testable.
**Effort:** Medium

---

### MAJOR Issues

#### MAJOR: battle_state_viewer.py has zero tests (687 lines of diffable pure logic)
**ID:** TCG-UI1-005
**Location:** `game/ui/screens/battle_state_viewer.py` (687 lines) / No test file
**Issue:** Contains `compute_json_diff()` function and `DiffResult` class - pure logic for computing JSON diffs between initial and final battle states. Also contains `_mark_all_paths()` and rendering logic.
**Impact:** `compute_json_diff()` is a recursive algorithm operating on nested JSON. Bugs in diff computation would produce incorrect battle state comparisons. This is highly testable with zero Pygame dependencies.
**Recommendation:** Write tests for `compute_json_diff()` with various inputs: identical objects, type changes, added/removed keys, nested changes, array changes, DIFF_IGNORE_KEYS filtering.
**Effort:** Simple

---

#### MAJOR: galaxy_test/ subpackage has zero test coverage (3 modules)
**ID:** TCG-UI1-006
**Location:** `game/ui/screens/galaxy_test/` (screen.py 281 lines, galaxy_mode.py 421 lines, system_mode.py 569 lines) / No tests
**Issue:** The galaxy test visualization screens have no tests. `galaxy_mode.py` and `system_mode.py` contain galaxy generation and rendering logic.
**Impact:** 1,271 lines untested. Lower priority since these are development/debug tools, but bugs would hinder galaxy debugging workflow.
**Recommendation:** If these screens are actively used for development, add basic initialization tests.
**Effort:** Medium

---

#### MAJOR: WorkshopViewModel has no direct tests (580 lines, 30 public methods)
**ID:** TCG-UI1-007
**Location:** `game/ui/screens/workshop_viewmodel.py` (580 lines) / No dedicated test file
**Issue:** WorkshopViewModel is the central MVVM ViewModel for the Design Workshop with ~30 public methods including `add_component()`, `remove_component()`, `change_ship_class()`, `validate_design()`, `create_default_ship()`, `add_component_bulk()`, `clear_design()`, `set_ship_name()`. The `test_workshop_screen.py` (27 tests) tests the screen wrapper but does not directly test ViewModel logic.
**Impact:** The ViewModel is the business logic hub for ship design. Untested methods like `add_component_bulk()`, `change_ship_class()` with migration, and `validate_design()` could silently regress.
**Recommendation:** Create `test_workshop_viewmodel.py` with direct tests for each public method. The ViewModel accepts an EventBus and context - easily mockable.
**Effort:** Medium

---

#### MAJOR: FleetReportFilters and FleetReportViewModel have no direct tests
**ID:** TCG-UI1-008
**Location:** `game/ui/screens/fleet_report_filters.py` (263 lines) + `game/ui/screens/fleet_report_view_model.py` (279 lines) / No dedicated test files
**Issue:** `fleet_report_filters.py` contains pure logic functions: `calculate_fleet_stats()`, `filter_ships()`, `sort_ships()`, `get_cell_value()`. `fleet_report_view_model.py` manages filter/sort state. While `test_fleet_report_window.py` exists (37 tests), it mocks the view model entirely and never tests the actual filtering/sorting logic.
**Impact:** Fleet stats calculation, ship filtering by damage/capability, and sorting by column are all untested. These are **pure functions** with no UI dependencies - ideal test targets.
**Recommendation:** Create `test_fleet_report_filters.py` testing `calculate_fleet_stats()` with various ship configurations, `filter_ships()` with different filter combinations, and `sort_ships()` with all column types. Create `test_fleet_report_view_model.py` for state management.
**Effort:** Simple

---

#### MAJOR: ColumnManager has no tests (233 lines, pure data/logic)
**ID:** TCG-UI1-009
**Location:** `game/ui/screens/column_manager.py` (233 lines) / No test file
**Issue:** `ColumnManager` manages column configuration for table displays with methods for toggling visibility, reordering, and getting visible columns. `DEFAULT_FLEET_COLUMNS` and `SPECIAL_CAPABILITY_COLUMNS` are data constants used across fleet report features.
**Impact:** Column visibility and ordering bugs would break fleet report table rendering. Pure logic class, easily testable.
**Recommendation:** Test column toggle, reorder, get_visible_columns with various configurations.
**Effort:** Simple

---

#### MAJOR: setup_data_io.py has no tests (233 lines, file I/O logic)
**ID:** TCG-UI1-010
**Location:** `game/ui/screens/setup_data_io.py` (233 lines) / No test file
**Issue:** Contains functions for scanning ship designs, formations, loading/saving battle setups. Functions: `scan_ship_designs()`, `scan_formations()`, `load_battle_setup()`, `save_battle_setup()`, `load_ship_from_entry()`. Uses ShipFactory and JSON utilities.
**Impact:** Broken setup I/O would prevent battle configuration. File scanning and JSON loading are testable with temp directories.
**Recommendation:** Test `scan_ship_designs()` with mock directories, `load_battle_setup()` with valid/invalid JSON, edge cases like missing files.
**Effort:** Medium

---

#### MAJOR: WorkshopShipIO has no tests (261 lines)
**ID:** TCG-UI1-011
**Location:** `game/ui/screens/workshop_ship_io.py` (261 lines) / No test file
**Issue:** Handles save/load/target workflows for the Design Workshop. Contains logic for integrated vs. standalone save modes, design name prompting, and design library integration.
**Impact:** Broken ship I/O would prevent saving/loading designs in the workshop. Save path selection logic (integrated vs standalone) is testable.
**Recommendation:** Test save/load delegation logic with mocked dependencies, mode-dependent behavior.
**Effort:** Medium

---

#### MAJOR: 16 panel files have no tests
**ID:** TCG-UI1-012
**Location:** `game/ui/panels/` - multiple files / No corresponding test files
**Issue:** The following panel files have NO test coverage:
- `battle_panels.py` (566 lines) - ShipStatsPanel, SeekerMonitorPanel, BattleControlPanel
- `system_tree_panel.py` (417 lines) - System/sector tree widget
- `modifier_impact_grid.py` (508 lines) - Modifier effect visualization
- `planet_report_panel.py` (508 lines) - Planet detail display
- `ship_detail_panel.py` (446 lines) - Ship detail with damage tracking
- `design_report_panel.py` (283 lines) - Design specs display
- `race_environment_panel.py` (624 lines) - Environmental preferences
- `race_summary_panel.py` (696 lines) - Race configuration summary
- `race_description_panel.py` (145 lines) - Race description text
- `race_theme_gallery.py` (201 lines) - Ship theme gallery
- `race_portrait_gallery.py` (171 lines) - Portrait gallery
- `race_flag_gallery.py` (183 lines) - Flag gallery
- `base_gallery.py` (263 lines) - Abstract gallery base class
- `builder_widgets.py` (281 lines) - Modifier editor panel
- `strategy_widgets.py` (177 lines) - SpectrumGraph, AtmosphereGraph
- `component_modifier_grid_panel.py` (149 lines) - Modifier grid panel
- `build_queue_drag_handler.py` (329 lines) - Drag-and-drop state machine

Panels **with** tests: `race_aptitudes_panel.py`, `race_identity_panel.py`, `build_queue_portraits.py`, `build_queue_controller.py`, `empire_treasury_panel.py`, `ship_stats_renderer.py`, `design_stats_panel.py`, `planet_report_panel.py` (compute_planet_production only).

**Impact:** 5,947 lines of panel code with no tests. Notable pure-logic opportunities: `ship_detail_panel.get_damage_color()` (color mapping from HP percentage), `strategy_widgets.SpectrumGraph/AtmosphereGraph` (data visualization calculations), `build_queue_drag_handler` (drag state machine logic).
**Recommendation:** Prioritize `get_damage_color()` in ship_detail_panel (5-line pure function), `build_queue_drag_handler` state machine, and `base_gallery.py` abstract methods.
**Effort:** Complex (many files, though individual tests are straightforward)

---

#### MAJOR: WorkshopEventRouter has no tests (496 lines)
**ID:** TCG-UI1-013
**Location:** `game/ui/screens/workshop_event_router.py` (496 lines) / No test file
**Issue:** Routes all events for the Design Workshop screen. Contains `handle_event()` with complex branching for button presses, dropdown changes, confirmation dialogs, and keyboard shortcuts.
**Impact:** Event routing bugs would break Workshop interaction. The bypass-init test pattern used for other screens could apply here.
**Recommendation:** Create tests using the bypass-init pattern verifying event delegation for different event types.
**Effort:** Medium

---

#### MAJOR: WorkshopDataLoader and WorkshopDataReloader have no tests (405 lines combined)
**ID:** TCG-UI1-014
**Location:** `game/ui/screens/workshop_data_loader.py` (213 lines) + `game/ui/screens/workshop_data_reloader.py` (192 lines) / No test files
**Issue:** `WorkshopDataLoader` handles JSON file discovery with priority fallback (direct match -> test_ prefix -> default directory) and data loading. `WorkshopDataReloader` orchestrates reload workflows. The `LoadResult` dataclass could be tested trivially.
**Impact:** Data loading bugs would prevent the Design Workshop from functioning. File discovery priority logic is pure and testable.
**Recommendation:** Test `WorkshopDataLoader` file discovery priority with mock directories, `LoadResult` dataclass, error accumulation.
**Effort:** Simple

---

#### MAJOR: StrategyEventRouter, StrategyPanelManager, and StrategyCameraNav have no direct tests
**ID:** TCG-UI1-015
**Location:** `game/ui/screens/strategy_event_router.py` (273 lines) + `game/ui/screens/strategy_panel_manager.py` (476 lines) + `game/ui/screens/strategy_camera_nav.py` (189 lines) / No test files
**Issue:** These modules were extracted from StrategyScreen/StrategyUI during PROJ-86 god class decomposition. While the parent classes have tests (`test_strategy_screen.py` with 77 tests), these extracted delegates have no direct tests. The StrategyEventRouter handles modal detection, button dispatch, click-outside-menu logic. CameraNavigator has coordinate math for center_on operations.
**Impact:** God class decomposition without adding tests to extracted modules means coverage regressed. The parent tests may exercise these indirectly through mocked delegates, but mock-based tests of the parent don't test the actual extracted logic.
**Recommendation:** Add direct tests for `CameraNavigator.center_on()` coordinate math, `StrategyEventRouter.has_modal_open()` logic, and panel factory functions.
**Effort:** Medium

---

### MINOR Issues

#### MINOR: planet_list_presets.py, planet_list_sidebar.py, planet_list_columns.py, planet_list_renderer.py have no direct tests
**ID:** TCG-UI1-016
**Location:** `game/ui/screens/planet_list_presets.py` (183 lines), `planet_list_sidebar.py` (255 lines), `planet_list_columns.py` (200 lines), `planet_list_renderer.py` (226 lines) / No direct test files
**Issue:** These planet list utility modules are only tested indirectly through `test_planet_list_components.py` (745 lines). `planet_list_presets.py` has `PresetManager` with capture/apply state logic that is pure and testable. `planet_list_columns.py` has `ColumnManager` with sort and resize logic.
**Impact:** Indirect coverage through integration-style tests in `test_planet_list_components.py` provides some protection, but PresetManager state capture/apply and ColumnManager sort logic deserve direct unit tests.
**Recommendation:** Extract tests for `PresetManager` and `ColumnManager` logic into dedicated test files.
**Effort:** Simple

---

#### MINOR: builder_selection.py has no tests (110 lines, pure selection logic)
**ID:** TCG-UI1-017
**Location:** `game/ui/screens/builder_selection.py` (110 lines) / No test file
**Issue:** Contains `normalize_selection()` and `process_selection_change()` - pure functions for handling multi-select, append, toggle, and homogeneity enforcement in the ship builder.
**Impact:** Selection bugs would cause confusing behavior in the builder. These are pure functions with no dependencies.
**Recommendation:** Test `normalize_selection()` with tuples, components, and not-found items. Test `process_selection_change()` with append/toggle/replace modes.
**Effort:** Simple

---

#### MINOR: build_queue_helpers.py has no tests (63 lines, pure formatting)
**ID:** TCG-UI1-018
**Location:** `game/ui/screens/build_queue_helpers.py` (63 lines) / No test file
**Issue:** Contains `format_empire_resources()` and `format_resource_cost()` - pure formatting functions with no UI dependencies.
**Impact:** Minor display formatting bugs. These are trivially testable.
**Recommendation:** Add tests for both functions with various resource combinations, zero values, empty dicts.
**Effort:** Simple

---

#### MINOR: save_selection_window.py has no tests (395 lines)
**ID:** TCG-UI1-019
**Location:** `game/ui/screens/save_selection_window.py` (395 lines) / No test file
**Issue:** Save game browser with expand/collapse, turn selection, and delete functionality. Complex UI state management.
**Impact:** Save loading bugs could block game continuation. Lower priority since save/load is typically manually tested.
**Recommendation:** Test list item mapping logic and expand/collapse state transitions with bypass-init pattern.
**Effort:** Medium

---

#### MINOR: new_game_setup_screen.py has no tests (627 lines)
**ID:** TCG-UI1-020
**Location:** `game/ui/screens/new_game_setup_screen.py` (627 lines) / No test file
**Issue:** New game configuration screen with player count selection, race assignment, and galaxy settings. Contains validation logic for save names and player configuration.
**Impact:** Configuration validation bugs could create invalid game sessions. The save name regex validation is testable.
**Recommendation:** Test save name validation regex, player count constraints, and GameConfig construction.
**Effort:** Medium

---

#### MINOR: empire_panel_window.py has no tests (526 lines)
**ID:** TCG-UI1-021
**Location:** `game/ui/screens/empire_panel_window.py` (526 lines) / No test file
**Issue:** Multi-tab empire information window (Treasury, Population, More). Wraps `EmpireTreasuryPanel` (which does have tests) but the window's tab switching logic and population tab rendering are untested.
**Impact:** Tab switching or population display bugs would affect empire management UI.
**Recommendation:** Test tab switching state management with bypass-init pattern.
**Effort:** Medium

---

#### MINOR: race_browser_dialog.py has no tests (290 lines)
**ID:** TCG-UI1-022
**Location:** `game/ui/screens/race_browser_dialog.py` (290 lines) / No test file
**Issue:** Dialog for browsing and loading race configurations from the race library.
**Impact:** Unable to load existing races if broken. Lower priority as it's a utility dialog.
**Recommendation:** Test race list population and selection logic.
**Effort:** Medium

---

#### MINOR: build_queue_list_window.py and build_queue_selector.py have no tests (318 lines combined)
**ID:** TCG-UI1-023
**Location:** `game/ui/screens/build_queue_list_window.py` (129 lines) + `game/ui/screens/build_queue_selector.py` (189 lines) / No test files
**Issue:** Build queue list browsing and queue source selection logic. Part of the multi-queue system.
**Impact:** Multi-queue navigation bugs would affect build management workflow.
**Recommendation:** Test queue selector state management and list population.
**Effort:** Simple

---

#### MINOR: race_asset_loader.py has no tests (276 lines)
**ID:** TCG-UI1-024
**Location:** `game/ui/screens/race_asset_loader.py` (276 lines) / No test file
**Issue:** Handles loading flag/portrait/theme images for races. Contains path resolution and fallback logic.
**Impact:** Missing or broken asset loading would show blank portraits/flags. Path resolution logic is testable.
**Recommendation:** Test path resolution and fallback behavior with mocked filesystem.
**Effort:** Medium

---

#### MINOR: workshop_context.py has no tests (158 lines)
**ID:** TCG-UI1-025
**Location:** `game/ui/screens/workshop_context.py` (158 lines) / No test file
**Issue:** `WorkshopContext` dataclass and `WorkshopMode` enum defining launch modes for the Design Workshop. Contains `is_standalone()`, `is_integrated()` convenience methods.
**Impact:** Context mode checks are used everywhere in the Workshop. Pure data class, trivially testable.
**Recommendation:** Test WorkshopMode enum values, is_standalone/is_integrated checks, context construction.
**Effort:** Simple

---

### INFO Issues

#### INFO: Tests using inspect.getsource() verify source code text, not behavior
**ID:** TCG-UI1-026
**Location:** `tests/unit/ui/screens/test_planet_selection_window.py` (lines 72, 82), `test_strategy_renderer.py` (lines 348, 384), `test_strategy_ui_menu.py` (lines 89, 96, 103, 362)
**Issue:** Multiple tests use `inspect.getsource()` to check that specific strings exist in source code. For example, `test_btn_any_guard_in_source` asserts that `"if self.btn_any and self.btn_any.check_pressed()"` exists in the source text. These tests verify implementation details rather than behavior and are fragile to refactoring (e.g., adding a comment, changing whitespace, extracting a method would break them).
**Impact:** These tests provide false confidence - they verify code text presence, not correctness. A developer could change the logic while keeping the string, and the test would still pass.
**Recommendation:** Replace source-text assertions with behavioral tests. For example, test `PlanetSelectionWindow.update()` behavior when `btn_any` is None by constructing a window with `show_any_button=False` and calling `update()`.
**Effort:** Medium

---

#### INFO: Some tests use .called instead of .assert_called_once()
**ID:** TCG-UI1-027
**Location:** `tests/unit/ui/screens/test_fleet_report_window_multi_select.py` (lines 265, 305, 328, 339, 350-353), `test_design_image_helper.py` (lines 75, 202)
**Issue:** Tests assert `mock.called` (boolean) instead of using `mock.assert_called_once()` or `mock.assert_called()`. While functionally similar for positive checks, `mock.called` for negative checks (`assert not mock.called`) is weaker than `mock.assert_not_called()` because it doesn't include call details in failure messages. Additionally, `.called` doesn't verify call count - it would pass even if called multiple times.
**Impact:** Weak assertions make test failures harder to debug and don't catch unexpected multiple calls.
**Recommendation:** Replace `assert mock.called` with `mock.assert_called()` and `assert not mock.called` with `mock.assert_not_called()`.
**Effort:** Simple

---

#### INFO: Heavy mock usage in screen tests may mask integration bugs
**ID:** TCG-UI1-028
**Location:** Multiple test files using bypass-init pattern: `test_strategy_screen.py`, `test_workshop_screen.py`, `test_fleet_report_window.py`, `test_build_queue_screen.py`
**Issue:** All screen-level tests use the bypass-init pattern (`__init__` patched to no-op, all dependencies mocked). While this enables fast unit testing, it means the actual initialization path - including panel creation, widget wiring, and callback registration - is never tested. For example, `test_strategy_screen.py` has 77 tests but all operate on a StrategyScreen whose `__init__` never ran.
**Impact:** Initialization bugs (wrong widget positions, missing callback registration, incorrect panel creation order) would not be caught. The real `__init__` could fail entirely without any test detecting it.
**Recommendation:** Consider adding at least one "smoke test" per major screen that calls the real `__init__` with minimal valid dependencies (possibly using a Pygame headless/dummy video driver). This would catch initialization crashes.
**Effort:** Complex

---

#### INFO: No tests for StrategyFleetOps or StrategyColonization (extracted delegates)
**ID:** TCG-UI1-029
**Location:** `game/ui/screens/strategy_fleet_ops.py` (199 lines) + `game/ui/screens/strategy_colonization.py` (274 lines) + `game/ui/screens/strategy_superweapons.py` (410 lines, partially tested)
**Issue:** `FleetOperations` and `ColonizationSystem` were extracted from StrategyScreen during PROJ-86 but have no direct unit tests. `strategy_superweapons.py` has `test_strategy_superweapons.py` (570 lines, good coverage), but fleet operations and colonization do not. These contain game logic for move/join/intercept commands and colonization workflows.
**Impact:** Fleet movement and colonization are core strategy gameplay. The parent StrategyScreen tests mock these delegates, so the actual logic in `FleetOperations.execute_move()`, `ColonizationSystem.on_colonize_click()` etc. is untested.
**Recommendation:** Create direct unit tests for `FleetOperations` and `ColonizationSystem` using mock scene/facade patterns.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **TCG-UI1-001 (CRITICAL)**: builder/ subpackage - 5,450+ lines with zero tests. Contains multiple pure-logic modules (`event_bus.py`, `grouping_strategies.py`, `modifier_logic.py`, `state_manager.py`) that require no mocking. Highest ROI for test investment.

2. **TCG-UI1-008 (MAJOR)**: FleetReportFilters and FleetReportViewModel - Pure functions for fleet stats calculation, ship filtering, and sorting with zero tests. Existing fleet report tests mock the view model entirely and never test actual logic. Simple to test, high value.

3. **TCG-UI1-005 (MAJOR)**: battle_state_viewer.py `compute_json_diff()` - Recursive JSON diff algorithm with zero tests. Pure logic, zero dependencies, trivially testable. One of the highest ROI individual functions to test.

4. **TCG-UI1-004 (CRITICAL)**: BattleScreen/BattleUI - Core battle gameplay loop with zero screen-level tests. Speed control, battle initialization, and event routing are all testable with bypass-init pattern.

5. **TCG-UI1-007 (MAJOR)**: WorkshopViewModel - Central MVVM ViewModel with 30 public methods and zero direct tests. Ship design operations (add/remove components, class changes, validation) are the core Workshop functionality.
