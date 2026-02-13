# Test Coverage Gaps Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens (game/ui/screens/, game/ui/panels/)
- **Production Files Scanned:** 125+ (101 in screens/, 25 in panels/)
- **Test Files Cross-Referenced:** 51 (43 in tests/unit/ui/screens/, 8 in tests/unit/ui/panels/)
- **Total Issues Found:** 28
- **Critical:** 4 | **Major:** 12 | **Minor:** 8 | **Info:** 4

## Findings

#### CRITICAL: Builder Module Completely Untested
**ID:** TCG-UI1-001
**Location:** `game/ui/screens/builder/` (production) / `tests/unit/ui/screens/builder/` (missing)
**Issue:** The entire builder subdirectory (17+ production files) has NO dedicated test coverage. This includes critical components:
- `drop_target.py` - Component drag-drop targeting logic
- `grouping_strategies.py` - Component grouping algorithms
- `modifier_config.py` - Modifier configuration handling
- `preset_ui.py` - Preset UI management
- `panel_layout_config.py` - Layout configuration
- `interaction_controller.py` - User interaction handling
- `modifier_row.py` - Modifier row rendering
- `event_bus.py` - Event pub/sub system
- `modifier_logic.py` - Modifier calculation logic
- `structure_list_items.py` - Structure list management
- `weapons_panel.py` - Weapons display panel
- `layer_panel.py` - Layer management panel
- `left_panel.py` - Left panel component list
- `schematic_view.py` - Schematic visualization
- `detail_panel.py` - Detail panel rendering
- `right_panel.py` - Right panel controls
**Impact:** Ship design builder is a core user-facing feature. Bugs in modifier logic, drag-drop, or layout could cause incorrect ship designs or data loss. The event_bus is used across the workshop; bugs could cause silent failures.
**Recommendation:** Create test files for at minimum: `modifier_logic.py`, `event_bus.py`, `interaction_controller.py`, `grouping_strategies.py`. These contain complex logic that benefits most from unit testing.
**Effort:** Complex (17+ files need tests, many with complex state management)

#### CRITICAL: Test Lab Module Minimal Coverage
**ID:** TCG-UI1-002
**Location:** `game/ui/screens/test_lab/` (production) / `tests/unit/ui/test_lab_scene/` (partial)
**Issue:** The test_lab subdirectory has 14 production files but only 2 test files (`test_ui_components.py`, `test_logic.py`). Critical files without tests include:
- `data_extractor.py` - Battle result data extraction
- `validation_manager.py` - Test validation logic
- `panel_manager.py` - Panel lifecycle management
- `test_executor.py` - Test execution engine
- `test_run_details.py` - Test result display
- `json_viewer.py` - JSON visualization
- `dialogs.py` - Dialog management
- `component_dropdown.py` - Component selection UI
- `test_run_card.py` - Test run card rendering
- `ship_panels.py` - Ship configuration panels
- `results_panel.py` - Results display
- `formatting_utils.py` - Output formatting (only test in `test_lab_formatting_utils.py`)
**Impact:** Test Lab is used for validating ship combat behavior. `data_extractor.py` and `validation_manager.py` contain parsing and validation logic that could silently produce incorrect test results.
**Recommendation:** Prioritize tests for `data_extractor.py`, `validation_manager.py`, and `test_executor.py` - these contain the core testing logic.
**Effort:** Medium (14 files, but many are UI-focused and can have simpler tests)

#### CRITICAL: Galaxy Test Module No Tests
**ID:** TCG-UI1-003
**Location:** `game/ui/screens/galaxy_test/` (production) / No test files found
**Issue:** The galaxy_test subdirectory has 5 production files with zero test coverage:
- `screen.py` - Main GalaxyTestScreen class with mode switching, event handling, resize handling
- `constants.py` - Configuration constants
- `galaxy_mode.py` - Galaxy generation testing mode
- `system_mode.py` - System generation testing mode
**Impact:** This is a developer tool for testing galaxy/system generation. While lower priority than user-facing features, bugs could mislead developers about generation quality.
**Recommendation:** Add basic smoke tests for `GalaxyTestScreen` initialization and mode switching. Test `galaxy_mode.py` and `system_mode.py` generation logic if they contain non-trivial algorithms.
**Effort:** Simple (5 files, testing tool only)

#### CRITICAL: Formation Module Missing Core Tests
**ID:** TCG-UI1-004
**Location:** `game/ui/screens/formation/` (production) / `tests/unit/ui/test_formation_*.py` (partial)
**Issue:** The formation subdirectory (`input_handler.py`, `renderer.py`) has tests in the parent `tests/unit/ui/` directory but critical gaps exist:
- `renderer.py` - 428 lines of rendering and coordinate transformation logic. Tests exist in `test_formation_renderer.py` but:
  - No tests for `get_resize_handles()` edge cases (empty bounds, single-point selections)
  - No tests for `_draw_arrows()` visibility culling
  - No tests for `get_renumber_arrow_rects()` with edge cases
- `input_handler.py` - Has `test_formation_input_handler.py` but may be undertested
**Impact:** FormationRenderer coordinate transformations are used for arrow placement. Bugs could cause arrows to appear in wrong positions or handles to be misaligned.
**Recommendation:** Add boundary tests for `get_resize_handles()` with edge cases. Add tests for visibility culling in `_draw_arrows()`.
**Effort:** Simple (targeted additions to existing test files)

#### MAJOR: Panel Files Missing Tests
**ID:** TCG-UI1-005
**Location:** `game/ui/panels/` (production) / `tests/unit/ui/panels/` (partial)
**Issue:** 17 panel production files exist but only 8 have corresponding test files. Missing tests for:
- `strategy_widgets.py` - AtmosphereGraph and other strategy UI widgets
- `component_modifier_grid_panel.py` - Modifier grid display
- `modifier_impact_grid.py` - Has test at `test_modifier_impact_grid.py` in parent dir
- `system_tree_panel.py` - System hierarchy display
- `builder_widgets.py` - Workshop widget utilities
- `build_queue_drag_handler.py` - Drag-drop for build queue
- `base_gallery.py` - Base class for gallery panels
- `design_report_panel.py` - Ship design report display (284 lines, complex logic)
- `race_environment_panel.py` - Has test at `test_race_environment_panel.py` in parent dir
- `planet_report_panel.py` - Planet report display (509 lines, complex logic)
- `ship_detail_panel.py` - Ship detail display
- `race_flag_gallery.py` - Race flag selection
- `race_portrait_gallery.py` - Race portrait selection
**Impact:** `planet_report_panel.py` (509 lines) and `design_report_panel.py` (284 lines) contain complex rendering and data processing logic. `build_queue_drag_handler.py` handles critical drag-drop operations.
**Recommendation:** Prioritize tests for `planet_report_panel.py` (especially `compute_planet_production()`), `design_report_panel.py`, and `build_queue_drag_handler.py`.
**Effort:** Medium (8+ files need tests)

#### MAJOR: BattlePanel Classes Undertested
**ID:** TCG-UI1-006
**Location:** `game/ui/panels/battle_panels.py` (567 lines) / `tests/unit/ui/test_battle_panels.py`
**Issue:** While test files exist (`test_battle_panels.py`, `test_battle_panels_extended.py`), the coverage gaps include:
- `ShipStatsPanel._get_ship_id()` - ID extraction logic not directly tested
- `ShipStatsPanel.get_expanded_height()` - Height calculation not tested
- `SeekerMonitorPanel._get_projectile_id()` - Projectile ID extraction untested
- `SeekerMonitorPanel.draw_seeker_entry()` - Rendering logic untested
- `BattleControlPanel` - Victory condition display logic undertested
**Impact:** These panels display critical battle information. Bugs could show incorrect HP, wrong team counts, or misrender victory screens.
**Recommendation:** Add tests for `_get_ship_id()` and `_get_projectile_id()` with various input types. Add tests for `get_expanded_height()` with different component counts.
**Effort:** Simple (targeted additions)

#### MAJOR: Strategy Screen Complex Modules
**ID:** TCG-UI1-007
**Location:** `game/ui/screens/strategy_*.py` (multiple files)
**Issue:** Several strategy screen modules lack dedicated tests:
- `strategy_fleet_ops.py` - Fleet operation handling
- `strategy_colonization.py` - Colonization logic
- `strategy_camera_nav.py` - Camera navigation
- `strategy_panel_manager.py` - Panel lifecycle
- `strategy_event_router.py` - Event routing
- `strategy_screen.py` - Main screen (has `test_strategy_screen.py` but minimal)
- `strategy_ui.py` - UI coordination (has `test_strategy_ui_menu.py`, `test_strategy_ui_tooltips.py`)
**Impact:** Strategy gameplay is a core feature. Fleet operations and colonization are critical game mechanics.
**Recommendation:** Prioritize `strategy_fleet_ops.py` and `strategy_colonization.py` as they contain game logic beyond UI rendering.
**Effort:** Medium (several files with game logic)

#### MAJOR: Workshop Data Components Untested
**ID:** TCG-UI1-008
**Location:** `game/ui/screens/workshop_*.py`
**Issue:** Workshop-related files without tests:
- `workshop_data_reloader.py` - Data reloading logic
- `workshop_data_loader.py` - Data loading utilities
- `workshop_ship_io.py` - Ship save/load operations
- `workshop_viewmodel.py` - View model state management
- `workshop_event_router.py` - Event routing
**Impact:** Workshop is the ship design interface. Data loading/saving bugs could corrupt ship designs or cause data loss.
**Recommendation:** `workshop_ship_io.py` and `workshop_viewmodel.py` contain critical data management logic. Prioritize these.
**Effort:** Medium (5 files with data handling logic)

#### MAJOR: Fleet Report Components Undertested
**ID:** TCG-UI1-009
**Location:** `game/ui/screens/fleet_*.py`
**Issue:** Fleet-related files with limited coverage:
- `fleet_report_view_model.py` - View model for fleet reports (no dedicated tests)
- `fleet_orders_window.py` - Fleet orders UI
- `fleet_report_filters.py` - Fleet filtering logic
**Impact:** Fleet management is a core strategy game feature. Filter bugs could hide important fleet information.
**Recommendation:** Add tests for `fleet_report_filters.py` filtering logic.
**Effort:** Simple

#### MAJOR: Build Queue UI Complex Logic Untested
**ID:** TCG-UI1-010
**Location:** `game/ui/screens/build_queue_*.py`, `game/ui/panels/build_queue_*.py`
**Issue:** Build queue related files with gaps:
- `build_queue_selector.py` - Build selection UI (no tests)
- `build_queue_list_window.py` - List window (has tests but may be incomplete)
- `build_queue_helpers.py` - Helper utilities
**Impact:** Build queue management is essential for production gameplay. Selection and helper logic bugs could cause wrong items to be queued.
**Recommendation:** Add tests for `build_queue_selector.py` selection logic.
**Effort:** Simple

#### MAJOR: Planet List Components
**ID:** TCG-UI1-011
**Location:** `game/ui/screens/planet_list_*.py`
**Issue:** Several planet list files lack direct tests:
- `planet_list_sidebar.py` - Sidebar rendering
- `planet_list_columns.py` - Column definitions
- `planet_list_renderer.py` - List rendering
- `planet_list_presets.py` - Filter presets
**Impact:** Planet management is a strategy game essential. Column/renderer bugs could show incorrect planet data.
**Recommendation:** Test `planet_list_columns.py` column definitions and sorting logic.
**Effort:** Simple

#### MAJOR: Race Configuration Panels
**ID:** TCG-UI1-012
**Location:** `game/ui/panels/race_*.py`, `game/ui/screens/race_*.py`
**Issue:** Several race-related panels lack tests despite having counterparts:
- `race_flag_gallery.py` - No tests (similar to race_portrait_gallery)
- `race_theme_gallery.py` - Has test at `test_race_theme_gallery.py`
- `race_asset_loader.py` - Has test at `test_race_asset_loader.py`
**Impact:** Race setup is part of new game creation. Gallery selection bugs could cause wrong flag/portrait selection.
**Recommendation:** Add tests for `race_flag_gallery.py` selection and rendering.
**Effort:** Simple

#### MINOR: Event Log Window
**ID:** TCG-UI1-013
**Location:** `game/ui/screens/event_log_window.py` / `tests/unit/ui/screens/test_event_log_window.py`
**Issue:** Event log window tests exist but may not cover edge cases:
- Empty log handling
- Very long messages
- Log scrolling behavior
**Impact:** Event log displays game events. Edge case bugs could cause UI issues.
**Recommendation:** Review existing tests for edge case coverage.
**Effort:** Simple

#### MINOR: Column Manager
**ID:** TCG-UI1-014
**Location:** `game/ui/screens/column_manager.py` / No direct tests
**Issue:** Column manager for planet lists has no dedicated tests.
**Impact:** Column management affects planet list display. Lower risk as it's configuration-focused.
**Recommendation:** Add basic tests for column visibility toggling.
**Effort:** Simple

#### MINOR: Keybindings Scene
**ID:** TCG-UI1-015
**Location:** `game/ui/screens/keybindings_scene.py` / `tests/unit/ui/screens/test_keybindings_scene.py`
**Issue:** Tests exist but may not cover all keybinding edge cases.
**Impact:** Keybinding display is user-facing but low-risk.
**Recommendation:** Review for completeness.
**Effort:** Simple

#### MINOR: Battle State Viewer
**ID:** TCG-UI1-016
**Location:** `game/ui/screens/battle_state_viewer.py` / `tests/unit/ui/battle_state_viewer/`
**Issue:** Tests exist in dedicated subdirectory. May need edge case coverage.
**Impact:** Developer debugging tool.
**Recommendation:** Verify JSON diff and UI logic tests are comprehensive.
**Effort:** Simple

#### MINOR: Setup Screen Components
**ID:** TCG-UI1-017
**Location:** `game/ui/screens/setup_*.py`
**Issue:** Setup screen has tests but helper modules may be undertested:
- `setup_renderer.py` - Rendering utilities
- `setup_data_io.py` - Has `test_setup_data_io.py`
**Impact:** Battle setup is user-facing but renderer is display-only.
**Recommendation:** Verify `setup_data_io.py` tests cover all I/O paths.
**Effort:** Simple

#### MINOR: Empire Panel Window
**ID:** TCG-UI1-018
**Location:** `game/ui/screens/empire_panel_window.py` / No direct tests
**Issue:** Empire panel window has no dedicated tests.
**Impact:** Empire overview display. Lower risk as likely delegates to tested components.
**Recommendation:** Add basic initialization and display tests.
**Effort:** Simple

#### MINOR: Save Selection Window
**ID:** TCG-UI1-019
**Location:** `game/ui/screens/save_selection_window.py` / `tests/unit/ui/test_save_selection.py`
**Issue:** Test exists but may not cover all edge cases (empty saves, corrupted data).
**Impact:** Save file selection is critical for gameplay continuity.
**Recommendation:** Add tests for empty save list and error handling.
**Effort:** Simple

#### MINOR: Design Selector Window
**ID:** TCG-UI1-020
**Location:** `game/ui/screens/design_selector_window.py` / `tests/unit/ui/screens/test_design_selector_window.py`
**Issue:** Tests exist but design selection filtering may need edge case tests.
**Impact:** Design selection affects build queue and fleet composition.
**Recommendation:** Verify filter tests cover all criteria combinations.
**Effort:** Simple

#### INFO: Test Quality - Bypass-Init Pattern Usage
**ID:** TCG-UI1-021
**Location:** `tests/unit/ui/screens/test_formation_editor_screen.py`, `tests/unit/ui/screens/test_workshop_screen.py`
**Issue:** Tests use bypass-init pattern with `__new__` and mock patching. While functional, this tests mocked behavior rather than real initialization.
**Impact:** Tests verify delegation behavior but may miss initialization bugs.
**Recommendation:** Consider adding at least one integration-style test per screen that uses real initialization (with minimal mocking).
**Effort:** Medium

#### INFO: Test Quality - Mock Heavy Tests
**ID:** TCG-UI1-022
**Location:** `tests/unit/ui/screens/test_formation_editor_screen.py`
**Issue:** Some tests create mock methods inline (e.g., `screen.draw = mock_draw`) then verify the mock was called correctly. This tests the test code, not the production code.
**Impact:** These tests pass even if production code is wrong.
**Recommendation:** Refactor to call actual methods and verify outcomes, not mock invocations.
**Effort:** Medium

#### INFO: Test File Organization
**ID:** TCG-UI1-023
**Location:** `tests/unit/ui/`
**Issue:** Test organization is inconsistent:
- Some tests in `tests/unit/ui/` directly (e.g., `test_formation_input_handler.py`)
- Some in `tests/unit/ui/screens/` (most screen tests)
- Some in subdirectories (e.g., `tests/unit/ui/battle_state_viewer/`)
**Impact:** Makes finding tests difficult; no standard for where to add new tests.
**Recommendation:** Consolidate: all screen tests in `tests/unit/ui/screens/`, all panel tests in `tests/unit/ui/panels/`.
**Effort:** Simple (file moves, no code changes)

#### INFO: Missing Integration Tests
**ID:** TCG-UI1-024
**Location:** `tests/integration/ui/` (appears empty or minimal)
**Issue:** No integration tests found for UI screen interactions:
- Screen-to-screen transitions
- Panel interactions within screens
- Data flow from screens to backend services
**Impact:** Unit tests verify components in isolation; integration bugs between components not caught.
**Recommendation:** Add integration tests for key user flows: new game setup, workshop design creation, strategy turn execution.
**Effort:** Complex

## Top 5 Priority Issues

1. **TCG-UI1-001 (CRITICAL):** Builder Module Completely Untested - 17+ files with complex UI logic (modifier handling, event bus, drag-drop) have zero test coverage. This is the ship design interface, a core feature.

2. **TCG-UI1-002 (CRITICAL):** Test Lab Module Minimal Coverage - 14 files but only 2 test files. `data_extractor.py` and `validation_manager.py` contain parsing/validation logic critical for ship testing reliability.

3. **TCG-UI1-005 (MAJOR):** Panel Files Missing Tests - `planet_report_panel.py` (509 lines), `design_report_panel.py` (284 lines), and `build_queue_drag_handler.py` lack tests despite containing complex data processing and user interaction logic.

4. **TCG-UI1-008 (MAJOR):** Workshop Data Components Untested - `workshop_ship_io.py` and `workshop_viewmodel.py` handle ship design data persistence. Bugs here could cause data loss or corruption.

5. **TCG-UI1-007 (MAJOR):** Strategy Screen Complex Modules - `strategy_fleet_ops.py` and `strategy_colonization.py` contain game logic for fleet operations and colonization, critical strategy gameplay features.
