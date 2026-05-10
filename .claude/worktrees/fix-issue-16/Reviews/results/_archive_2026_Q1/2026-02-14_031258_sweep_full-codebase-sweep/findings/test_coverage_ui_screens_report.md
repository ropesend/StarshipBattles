# Test Coverage Gaps Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens (game/ui/screens/, game/ui/panels/)
- **Production Files Scanned:** 118 (screens: 93, panels: 25)
- **Test Files Cross-Referenced:** 62
- **Total Issues Found:** 24
- **Critical:** 4 | **Major:** 10 | **Minor:** 8 | **Info:** 2

## Findings

#### CRITICAL: BattleScreen has minimal functional tests - no visual battle simulation tests
**ID:** TCG-UI1-001
**Location:** `game/ui/screens/battle_screen.py` (production) / `tests/unit/ui/screens/test_battle_screen_edge_cases.py` (only edge case tests exist)
**Issue:** BattleScreen (645 lines) handles critical battle simulation including tick execution, headless mode, test scenario integration, and visual rendering. Current tests only cover edge cases (keyboard shortcuts, mouse clicks) via bypass-init pattern. No tests verify:
- Battle tick execution via `_run_single_tick()`
- Test scenario completion flow
- Headless vs visual mode switching
- BattleController integration via `start_with_controller()`
- Battle outcome detection and winner determination
**Impact:** Core battle simulation logic is untested. Regressions in tick processing, battle endings, or test mode could go undetected.
**Recommendation:** Add tests for `start()`, `update()`, `_run_single_tick()`, `is_battle_over()`, and controller integration. Test both headless and visual modes.
**Effort:** Complex

#### CRITICAL: BattleUI panel rendering has no test file
**ID:** TCG-UI1-002
**Location:** `game/ui/screens/battle_ui.py` (production) / NO TEST FILE
**Issue:** BattleUI (292 lines) handles all battle UI rendering including ship stats panel, seeker monitor, control panel, debug overlay, grid drawing, and "Return to Combat Lab" button logic. No test file exists for this module.
**Impact:** UI rendering bugs and click handling issues could be introduced without detection. The debug overlay drawing and firing arc visualization are complex and untested.
**Recommendation:** Create `tests/unit/ui/screens/test_battle_ui.py` with tests for handle_click, handle_resize, draw methods, and _get_return_button_rect.
**Effort:** Medium

#### CRITICAL: battle_panels.py (ShipStatsPanel, SeekerMonitorPanel, BattleControlPanel) has no tests
**ID:** TCG-UI1-003
**Location:** `game/ui/panels/battle_panels.py` (production) / NO TEST FILE
**Issue:** battle_panels.py defines three critical panels used during combat: ShipStatsPanel, SeekerMonitorPanel, and BattleControlPanel. These panels render ship statistics, missile tracking, and battle controls. The ShipStatsPanel has complex expansion tracking logic via `_get_ship_id()` and `_is_expanded()`. No tests exist.
**Impact:** Ship stats display bugs, seeker monitor rendering issues, or control panel click handling failures would go undetected.
**Recommendation:** Create `tests/unit/ui/panels/test_battle_panels.py` covering panel initialization, draw methods, handle_click, and scroll handling.
**Effort:** Medium

#### CRITICAL: InteractionController (drag-drop for ship builder) has no tests
**ID:** TCG-UI1-004
**Location:** `game/ui/screens/builder/interaction_controller.py` (production) / NO TEST FILE
**Issue:** InteractionController manages all drag-drop interactions in the ship builder UI including component selection, clone operations (Alt+click), multi-placement mode (Shift+drop), and drop target registration. This is core ship design functionality with no tests.
**Impact:** Ship builder drag-drop bugs would break core gameplay functionality without test detection.
**Recommendation:** Create `tests/unit/ui/screens/builder/test_interaction_controller.py` testing handle_event for all mouse interactions, drop target registration, and selection state management.
**Effort:** Medium

#### MAJOR: FleetOrdersWindow has no tests
**ID:** TCG-UI1-005
**Location:** `game/ui/screens/fleet_orders_window.py` (production) / NO TEST FILE
**Issue:** FleetOrdersWindow (200+ lines) manages fleet order management UI including order reordering, deletion with undo history, clearing all orders, and keybinding integration. No tests exist.
**Impact:** Fleet order management bugs could break strategy gameplay. Undo functionality is complex and untested.
**Recommendation:** Create `tests/unit/ui/screens/test_fleet_orders_window.py` covering rebuild_list, delete/undo operations, and keyboard shortcuts.
**Effort:** Medium

#### MAJOR: SaveSelectionWindow has no tests
**ID:** TCG-UI1-006
**Location:** `game/ui/screens/save_selection_window.py` (production) / NO TEST FILE
**Issue:** SaveSelectionWindow handles save game browsing, turn history expansion, and save loading/deletion. No tests exist for this critical game flow.
**Impact:** Save/load functionality bugs could cause data loss or game corruption.
**Recommendation:** Create `tests/unit/ui/screens/test_save_selection_window.py` covering _load_saves, save selection, turn expansion, and delete functionality.
**Effort:** Medium

#### MAJOR: PlanetListWindow has no direct test file
**ID:** TCG-UI1-007
**Location:** `game/ui/screens/planet_list_window.py` (production) / partial coverage via test_planet_list_*.py helpers
**Issue:** PlanetListWindow (300+ lines) is a complex window with filtering, sorting, presets, and planet detail display. Tests exist for helper modules (planet_list_filters.py, planet_list_columns.py) but no tests for the window class itself including UI element creation, filter application, or preset management.
**Impact:** Filter/sort UI integration bugs could go undetected even if helper logic is correct.
**Recommendation:** Create `tests/unit/ui/screens/test_planet_list_window.py` testing window initialization, filter state application, and preset load/save.
**Effort:** Medium

#### MAJOR: EmpirePanelWindow has no tests
**ID:** TCG-UI1-008
**Location:** `game/ui/screens/empire_panel_window.py` (production) / NO TEST FILE
**Issue:** EmpirePanelWindow (150+ lines) is a multi-tab window displaying Treasury, Population, and future tabs. No tests exist for tab switching, population panel rendering, or empire data display.
**Impact:** Empire overview UI bugs would affect strategic decision-making.
**Recommendation:** Create `tests/unit/ui/screens/test_empire_panel_window.py` testing tab switching, data extraction, and panel rendering.
**Effort:** Simple

#### MAJOR: NewGameSetupScreen has no tests
**ID:** TCG-UI1-009
**Location:** `game/ui/screens/new_game_setup_screen.py` (production) / NO TEST FILE
**Issue:** NewGameSetupScreen handles new game configuration including galaxy size, AI players, difficulty, and race selection. No tests exist for this critical game flow entry point.
**Impact:** New game configuration bugs could prevent game starts or create invalid game states.
**Recommendation:** Create `tests/unit/ui/screens/test_new_game_setup_screen.py` covering configuration validation and game start flow.
**Effort:** Medium

#### MAJOR: StrategyEventRouter has no tests
**ID:** TCG-UI1-010
**Location:** `game/ui/screens/strategy_event_router.py` (production) / NO TEST FILE
**Issue:** StrategyEventRouter (274 lines) handles all event routing for StrategyUI including button presses, modal detection, colonize button logic, and window close events. No dedicated tests exist.
**Impact:** Event routing bugs could cause unresponsive UI or incorrect behavior cascades.
**Recommendation:** Create `tests/unit/ui/screens/test_strategy_event_router.py` testing route_event, has_modal_open, and button handlers.
**Effort:** Simple

#### MAJOR: FormationInputHandler only has indirect test coverage
**ID:** TCG-UI1-011
**Location:** `game/ui/screens/formation/input_handler.py` (production) / tested indirectly via test_formation_editor_screen.py
**Issue:** FormationInputHandler (150+ lines) implements a complex state machine (IDLE, DRAGGING_ITEMS, BOX_SELECT, RESIZING_GROUP, PANNING, POTENTIAL_CLICK). Tests mock the handler rather than testing state transitions directly.
**Impact:** State machine edge cases (transition guards, resize aspect ratio locking) are untested.
**Recommendation:** Create `tests/unit/ui/screens/formation/test_input_handler.py` testing all state transitions and calculation methods.
**Effort:** Medium

#### MAJOR: builder/ subpackage has no test files at all
**ID:** TCG-UI1-012
**Location:** `game/ui/screens/builder/*.py` (18 files) / NO TEST DIRECTORY
**Issue:** The builder subpackage contains 18 production files totaling ~2000+ lines including drop_target.py, grouping_strategies.py, modifier_config.py, preset_ui.py, panel_layout_config.py, modifier_row.py, event_bus.py, modifier_logic.py, structure_list_items.py, weapons_panel.py, layer_panel.py, left_panel.py, schematic_view.py, detail_panel.py, right_panel.py, stats_config.py. NONE have dedicated test files.
**Impact:** Ship builder UI is a core feature with zero direct test coverage for panel rendering, event handling, or modifier configuration.
**Recommendation:** Create `tests/unit/ui/screens/builder/` directory with test files for critical modules: test_event_bus.py, test_modifier_logic.py, test_layer_panel.py, test_schematic_view.py.
**Effort:** Complex

#### MAJOR: test_lab/ subpackage has minimal direct tests
**ID:** TCG-UI1-013
**Location:** `game/ui/screens/test_lab/*.py` (14 files) / `tests/unit/ui/test_lab_scene/` (3 test files with logic tests only)
**Issue:** test_lab subpackage contains 14 production files including screen.py, ship_panels.py, results_panel.py, test_executor.py, validation_manager.py. Existing tests in test_lab_scene/ focus on data formatting logic, not UI components like ResultsPanel or ShipPanel.
**Impact:** Combat Lab UI rendering and panel interaction bugs would go undetected.
**Recommendation:** Add tests for panel rendering and UI interactions in addition to existing logic tests.
**Effort:** Medium

#### MAJOR: RaceDescriptionPanel, ModifierImpactGrid, BuildQueueDragHandler have no tests
**ID:** TCG-UI1-014
**Location:** `game/ui/panels/race_description_panel.py`, `game/ui/panels/modifier_impact_grid.py`, `game/ui/panels/build_queue_drag_handler.py` / NO TEST FILES
**Issue:** These three panel classes handle race text editing, modifier stat visualization, and build queue drag operations. None have tests.
**Impact:** Race setup, ship builder modifier display, and build queue reordering could have bugs without detection.
**Recommendation:** Create test files for each: test_race_description_panel.py, test_modifier_impact_grid.py, test_build_queue_drag_handler.py.
**Effort:** Medium

#### MINOR: RaceBrowserDialog tests are minimal - only tests constants and selection assignment
**ID:** TCG-UI1-015
**Location:** `tests/unit/ui/test_race_browser_dialog.py` (test file)
**Issue:** Tests only verify import, constants (PREVIEW_SIZE, ROW_HEIGHT), and selection assignment. No tests for _create_ui, _load_races, row selection rendering, or callback invocation.
**Impact:** Race browser visual and interaction bugs could go undetected.
**Recommendation:** Add tests for _load_races, row click handling, and callback triggering.
**Effort:** Simple

#### MINOR: SystemSelectionWindow and PlanetSelectionWindow have no tests
**ID:** TCG-UI1-016
**Location:** `game/ui/screens/system_selection_window.py`, `game/ui/screens/planet_selection_window.py` / NO TEST FILES
**Issue:** These dialog windows handle system and planet selection in strategy mode. No tests exist.
**Impact:** Selection dialog bugs could break colonization and targeting workflows.
**Recommendation:** Create simple test files verifying initialization and selection callbacks.
**Effort:** Simple

#### MINOR: DesignSelectorWindow tests don't cover rendering or selection
**ID:** TCG-UI1-017
**Location:** `tests/unit/ui/screens/test_design_selector_window.py` / partial coverage
**Issue:** Tests exist but focus on construction flow. No tests for design list rendering, filter application, or selection state management.
**Impact:** Design browser UI bugs could affect ship production workflow.
**Recommendation:** Add tests for design list population and selection handling.
**Effort:** Simple

#### MINOR: GalaxyTestScreen (galaxy_test/ subpackage) has only basic tests
**ID:** TCG-UI1-018
**Location:** `game/ui/screens/galaxy_test/*.py` (5 files) / `tests/unit/ui/screens/test_galaxy_test_screen.py` (basic tests)
**Issue:** GalaxyTestScreen has tests but galaxy_mode.py and system_mode.py (view mode handlers) have no dedicated tests.
**Impact:** Galaxy/system view mode switching bugs could go undetected.
**Recommendation:** Add tests for mode handlers in galaxy_mode.py and system_mode.py.
**Effort:** Simple

#### MINOR: race_asset_loader.py, workshop_data_loader.py have no direct tests
**ID:** TCG-UI1-019
**Location:** `game/ui/screens/race_asset_loader.py`, `game/ui/screens/workshop_data_loader.py` / NO TEST FILES
**Issue:** These loader classes handle asset loading for races and workshop data. No direct tests, though they may be indirectly tested through higher-level tests.
**Impact:** Asset loading failures could cause visual glitches or crashes.
**Recommendation:** Add tests for error handling and fallback behavior in loaders.
**Effort:** Simple

#### MINOR: column_manager.py and fleet_report_filters.py have no tests
**ID:** TCG-UI1-020
**Location:** `game/ui/screens/column_manager.py`, `game/ui/screens/fleet_report_filters.py` / NO TEST FILES
**Issue:** These utility modules handle column configuration and fleet report filtering. No tests exist.
**Impact:** Column and filter bugs could cause display issues in list views.
**Recommendation:** Create test files for column toggling and filter application logic.
**Effort:** Simple

#### MINOR: workshop_event_router.py, workshop_data_reloader.py have no tests
**ID:** TCG-UI1-021
**Location:** `game/ui/screens/workshop_event_router.py`, `game/ui/screens/workshop_data_reloader.py` / NO TEST FILES
**Issue:** Workshop event routing and data reload logic are untested. These modules handle critical workshop functionality.
**Impact:** Workshop event handling and data refresh bugs could cause inconsistent state.
**Recommendation:** Create test files for event routing and reload triggers.
**Effort:** Simple

#### MINOR: setup_renderer.py has no tests (setup screen rendering)
**ID:** TCG-UI1-022
**Location:** `game/ui/screens/setup_renderer.py` / NO TEST FILE
**Issue:** SetupRenderer handles battle setup screen rendering. No tests exist.
**Impact:** Setup screen visual bugs would go undetected.
**Recommendation:** Create basic render method tests with mocked surfaces.
**Effort:** Simple

#### INFO: Test files use bypass-init pattern consistently
**ID:** TCG-UI1-023
**Location:** Multiple test files
**Issue:** Many test files use the bypass-init pattern (patch __init__, create via __new__) which tests methods in isolation but may miss initialization bugs or dependency injection issues.
**Impact:** Low - this is a valid testing approach, but full integration tests should supplement unit tests.
**Recommendation:** Consider adding a few integration tests that use real initialization for critical screens.
**Effort:** N/A (observation)

#### INFO: Some panels have excellent test coverage
**ID:** TCG-UI1-024
**Location:** `tests/unit/ui/panels/` directory
**Issue:** Positive observation: build_queue_controller.py, empire_treasury_panel.py, design_stats_panel.py, ship_detail_panel.py, planet_report_panel.py all have comprehensive test coverage including edge cases and rendering logic.
**Impact:** These panels serve as good examples for test patterns.
**Recommendation:** Use these as templates when creating new panel tests.
**Effort:** N/A (positive observation)

## Top 5 Priority Issues

1. **TCG-UI1-001 (CRITICAL):** BattleScreen functional tests missing - core battle simulation logic is untested including tick execution, test scenario completion, and controller integration. This is the most critical gap as battles are central to gameplay.

2. **TCG-UI1-003 (CRITICAL):** battle_panels.py (ShipStatsPanel, SeekerMonitorPanel, BattleControlPanel) has no tests - these panels display critical combat information and have complex state management.

3. **TCG-UI1-012 (MAJOR):** builder/ subpackage (18 files) has zero test coverage - ship design is a core feature and the entire builder UI layer is untested.

4. **TCG-UI1-004 (CRITICAL):** InteractionController for drag-drop operations has no tests - this is the core interaction layer for ship building.

5. **TCG-UI1-005 (MAJOR):** FleetOrdersWindow has no tests - fleet order management is essential for strategy gameplay and the undo functionality is complex.
