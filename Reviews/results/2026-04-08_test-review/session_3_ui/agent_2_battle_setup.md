# Test Review Report: Agent 2 -- UI Battle + Setup + Misc Screens

## Scope
- Source files reviewed: 46 files (14,965 LOC total)
  - game/ui/screens/battle_screen.py (632), battle_ui.py (206), battle_results_screen.py (279), battle_results_data.py (147), battle_state_viewer.py (260)
  - game/ui/screens/setup_screen.py (407), setup_data_io.py (255), setup_renderer.py (216), new_game_setup_screen.py (645)
  - game/ui/screens/formation_editor.py (829), formation/input_handler.py (422), formation/renderer.py (435), formation/toolbar_builder.py (290)
  - game/ui/screens/menu_scene.py (109), keybindings_scene.py (582)
  - game/ui/screens/atmosphere_target_editor.py (294), planet_abilities_window.py (228), settings_window.py (109)
  - game/ui/screens/galaxy_test/screen.py (284), galaxy_mode.py (424), system_mode.py (574), constants.py (32)
  - game/ui/screens/save_selection_window.py (397), design_image_helper.py (210), design_selector_window.py (562)
  - game/ui/screens/cargo_quick_dialog.py (290), builder_selection.py (120), builder_utils.py (94)
  - game/ui/screens/build_queue_screen.py (566), build_queue_viewmodel.py (268), build_queue_helpers.py (205), build_queue_list_window.py (129), build_queue_queue_data_source.py (184), build_queue_panel_factory.py (483), build_queue_renderer.py (160), build_queue_selector.py (195)
  - game/ui/screens/race_setup_screen.py (1152), race_validator.py (98), race_asset_loader.py (279), race_browser_dialog.py (303)
  - game/ui/screens/strategy_camera_nav.py (202)
  - game/ui/renderer/camera.py (172), game_renderer.py (169)
  - game/ui/panels/battle_panels.py (561)
  - game/ui/services/battle_factories.py (211), battle_ui_service.py (296)

- Test files reviewed: 52 files (19,735 LOC total)
  - Unit tests (screens): 24 files (8,436 LOC)
  - Unit tests (ui): 16 files (5,555 LOC)
  - Unit tests (services): 5 files (1,520 LOC)
  - Unit tests (battle_state_viewer): 3 files (761 LOC)
  - Integration tests: 12 files (3,463 LOC)

- Coverage data referenced: Yes, extracted from coverage.json

## Summary
- Test files reviewed: 52
- Source files reviewed: 46
- Tests flagged for removal: 8 (estimated LOC: 575)
- Tests flagged as happy-path-only: 6
- Source files with inadequate coverage: 11

---

## A. Tests Recommended for Removal

### A1. Battle State Viewer -- Reimplemented Logic Tests

- **File:** `tests/unit/ui/battle_state_viewer/test_json_diff.py`
- **Test(s):** `TestComputeJsonDiff` (all methods), `TestMarkAllPaths` (all methods), `TestDiffResultConstants`, `TestJsonPathMatching`
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** The entire `TestComputeJsonDiff` class (lines 17-220) reimplements the `compute_json_diff` algorithm as a local method (`self.compute_json_diff`) and then tests that local reimplementation. It never imports or calls the actual `compute_json_diff` from `game.ui.screens.battle_state_viewer`. Same for `TestMarkAllPaths` (lines 226-281) which reimplements `_mark_all_paths` as a local method and tests that. `TestDiffResultConstants` (lines 288-301) asserts that four hardcoded strings are distinct -- a trivial constant test. `TestJsonPathMatching` (lines 307-347) reimplements `path_is_parent_of` and tests it locally.
- **Estimated LOC saved:** 347

### A2. Battle State Viewer -- More Reimplemented Logic

- **File:** `tests/unit/ui/battle_state_viewer/test_ui_logic.py`
- **Test(s):** `TestDiffColorSelection`, `TestScrollOffsetCalculations`, `TestDiffStatistics`
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** All three classes (lines 12-178) reimplement functions locally rather than importing them from the source. `TestDiffColorSelection.get_diff_color()` hardcodes color constants and tests them (lines 19-50). `TestScrollOffsetCalculations.clamp_scroll()` is a local reimplementation (lines 90-93). `TestDiffStatistics.calculate_diff_stats()` is another local reimplementation (lines 131-145). None of these test actual production code.
- **Estimated LOC saved:** 178

### A3. Battle State Viewer -- Panel Logic Reimplementation

- **File:** `tests/unit/ui/battle_state_viewer/test_viewer_ui.py`
- **Test(s):** `TestLineRenderingCalculations`, `TestIndentLevelCalculation`, `TestPanelVisibilityToggle`, `TestDualPanelSync`, `TestKeyboardNavigation`
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Every test class reimplements its own version of the logic (e.g., `calculate_visible_lines` at line 22, `get_indent_level` at line 64, `handle_key` at line 181) and tests that reimplementation. `TestPanelVisibilityToggle` (lines 105-141) creates a local `PanelState` class with show/hide/toggle and tests boolean toggling -- no production code involved. `TestDualPanelSync` (lines 148-170) tests dictionary lookup on a local dict, not production code.
- **Estimated LOC saved:** 236

### A4. Galaxy Test Screen -- Trivial Attribute Tests

- **File:** `tests/unit/ui/screens/test_galaxy_test_screen.py`
- **Test(s):** `TestGalaxyTestScreenInit` (all 5 methods), `TestCameraSetup.test_screen_has_camera`, `TestFPSTracking` (all 2 methods)
- **Reason:** TESTS_NOTHING_REAL / TRIVIAL_CONSTANT
- **Confidence:** HIGH
- **Evidence:** `TestGalaxyTestScreenInit` (lines 81-143) bypasses `__init__` entirely, then manually assigns attributes (`screen.screen_width = 1920`) and asserts the same value back. This tests Python attribute assignment, not any game code. Same for `TestCameraSetup.test_screen_has_camera` (lines 220-231) -- assigns a mock to `screen.camera` and asserts it back. `TestFPSTracking` (lines 258-281) assigns `screen.current_fps = 60.0` and asserts it equals 60.0.
- **Estimated LOC saved:** 80

### A5. Galaxy Test Screen -- Trivial Type/Import Assertions

- **File:** `tests/unit/ui/screens/test_galaxy_test_screen.py`
- **Test(s):** `TestGalaxyTestConstants.test_constants_can_be_imported`, `TestGalaxyTestScreenImport.test_screen_can_be_imported`, `TestGalaxyTestScreenImport.test_screen_has_mode_constants`, `TestModeSwitching` (all 4 methods), `TestGalaxyModeHelper.test_helper_can_be_imported`, `TestSystemModeHelper.test_helper_can_be_imported`
- **Reason:** TRIVIAL_CONSTANT / SCAFFOLD_ONLY
- **Confidence:** MEDIUM
- **Evidence:** `test_constants_can_be_imported` (line 17) only asserts `is not None` after import. `test_screen_can_be_imported` (line 64) same. `TestModeSwitching` (lines 184-212) asserts that mode constants are strings and are distinct -- testing string inequality. `test_helper_can_be_imported` (lines 240, 250) asserts `is not None` after import. These tests provide minimal regression value. However, the constant validation tests (SIDEBAR_WIDTH is positive, HEX_SIZE is positive, PLANET_TYPE_COLORS RGB validation at lines 28-56) are KEPT as they validate invariants.
- **Estimated LOC saved:** 60

### A6. Camera Navigator -- Method Existence Test

- **File:** `tests/unit/ui/screens/test_camera_navigator.py`
- **Test(s):** `TestCenterOnHex.test_center_on_hex_method_exists`
- **Reason:** TRIVIAL_CONSTANT
- **Confidence:** HIGH
- **Evidence:** Line 48-50: `assert hasattr(CameraNavigator, 'center_on_hex')`. This is a pure structural check that adds no value beyond the other two tests in the same class which actually call the method.
- **Estimated LOC saved:** 3

### A7. Keybindings Scene -- GameState Constant Test

- **File:** `tests/unit/ui/screens/test_keybindings_scene.py`
- **Test(s):** `TestAppIntegration.test_game_state_keybindings_exists`
- **Reason:** TRIVIAL_CONSTANT
- **Confidence:** MEDIUM
- **Evidence:** Lines 286-289: Asserts `GameState.KEYBINDINGS == 10`. This tests a hardcoded enum value. However, it documents an API contract between app.py and the keybindings system, so the confidence is MEDIUM rather than HIGH.
- **Estimated LOC saved:** 5

### A8. Menu Scene -- BG_COLOR Constant Test

- **File:** `tests/unit/ui/screens/test_menu_scene.py`
- **Test(s):** `TestMenuSceneConstants.test_bg_color_constant`
- **Reason:** TRIVIAL_CONSTANT
- **Confidence:** HIGH
- **Evidence:** Lines 252-256: `assert MenuScene.BG_COLOR == (20, 20, 30)`. Tests that a color constant equals a specific RGB value. No behavioral significance.
- **Estimated LOC saved:** 5

---

## B. Tests That Are Happy-Path-Only

### B1. Battle Screen Edge Cases -- Missing Error Paths

- **File:** `tests/unit/ui/screens/test_battle_screen_edge_cases.py`
- **Test(s):** `TestHandleEventEdgeCases`, `TestKeyboardShortcutEdgeCases`
- **What's tested:** Unknown event type ignored, mouse click with None result, right click preservation, focus ship with unknown ID, F3 overlay toggle, speed limits
- **What's missing:** No tests for handle_event when battle is not started (scene has no engine). No tests for key events during headless mode. No tests for multiple simultaneous key presses. No tests for focus_ship with a valid ship ID where the ship dies mid-lookup.
- **Source method(s) affected:** `game/ui/screens/battle_screen.py:handle_event` (~line 200+), `_handle_keydown` (~line 250+)
- **Priority:** LOW (edge cases already covered at medium level; the missing scenarios are unlikely in practice)

### B2. Battle Panels -- No Draw/Render Tests

- **File:** `tests/unit/ui/test_battle_panels.py`, `tests/unit/ui/test_battle_panels_extended.py`
- **Test(s):** All classes in both files
- **What's tested:** Click handling, expansion toggling, DTO integration, scroll offset, seeker state, ID-based tracking
- **What's missing:** No tests verify draw() output (panel rendering). Coverage is 39% (130/333 stmts). The draw methods contain complex layout logic with conditional branches for shields display, component lists, team headers, derelict marking, resource bars -- none tested. No tests for dead ship display styling. No tests for overflow/truncation of long ship names.
- **Source method(s) affected:** `game/ui/panels/battle_panels.py:ShipStatsPanel.draw` (~line 100+), `SeekerMonitorPanel.draw` (~line 300+), `BattleControlPanel.draw` (~line 400+)
- **Priority:** MEDIUM (draw bugs would be visible but not crash-inducing)

### B3. Setup Screen -- No Rendering or Scroll Tests

- **File:** `tests/unit/ui/screens/test_setup_screen.py`
- **Test(s):** All classes
- **What's tested:** Init, team add/remove, callback invocation, save/load, formation groups, dropdown
- **What's missing:** No tests for the actual rendering path (draw method at setup_renderer.py -- 10% coverage). No tests for scroll behavior with many ships. No tests for handling more than ~20 ships in a team list (overflow). No tests for keyboard shortcuts (Ctrl+S save, Ctrl+L load). No error path tests for what happens when scan_ship_designs returns corrupt data at runtime.
- **Source method(s) affected:** `game/ui/screens/setup_renderer.py` (10% coverage, 100 stmts), `game/ui/screens/setup_screen.py:draw` (~line 300+)
- **Priority:** MEDIUM

### B4. Race Setup Screen -- No Tab Rendering Tests

- **File:** `tests/unit/ui/screens/test_race_setup_screen.py`
- **Test(s):** All classes (711 LOC)
- **What's tested:** Tab navigation, validation delegation, complete/cancel callbacks, editing mode, aptitude changes
- **What's missing:** Coverage is only 29.2% (149/511 stmts). No tests for draw/rendering of any of the 7 tabs. No tests for mouse event handling within tab panels. No tests for keyboard shortcuts. No tests for the budget display updating in real-time as aptitudes change. No error handling tests for corrupt race library data.
- **Source method(s) affected:** `game/ui/screens/race_setup_screen.py` (29.2% coverage)
- **Priority:** MEDIUM

### B5. Design Selector Window -- No Error/Edge Cases

- **File:** `tests/unit/ui/screens/test_design_selector_window.py`
- **Test(s):** All classes (610 LOC)
- **What's tested:** Filtering by name/class/type, selection callbacks, obsolete marking, mode differences
- **What's missing:** Coverage is 57.4% (117/204 stmts). No tests for window resize behavior. No tests for empty design library. No tests for concurrent modifications (design deleted while selector is open). No tests for the image thumbnail loading path within the selector.
- **Source method(s) affected:** `game/ui/screens/design_selector_window.py` (57.4% coverage)
- **Priority:** LOW

### B6. Cargo Quick Dialog -- Missing Cancel/Error Paths

- **File:** `tests/unit/ui/screens/test_cargo_quick_dialog.py`, `test_cargo_quick_dialog_issuance.py`, `test_cargo_quick_dialog_resolution.py`
- **Test(s):** Combined 498 LOC across 3 files
- **What's tested:** Init for unload/load directions, item population, button behavior, transfer command dispatch
- **What's missing:** Coverage is 79.2% (95/120 stmts). No tests for invalid transfer amounts (negative, exceeding max). No tests for concurrent dialog instances. No tests for what happens when the fleet moves away from the colony during dialog interaction.
- **Source method(s) affected:** `game/ui/screens/cargo_quick_dialog.py` (79.2% coverage)
- **Priority:** LOW

---

## C. Source Code with Inadequate Coverage

### C1. atmosphere_target_editor.py -- 0% Coverage

- **Source file:** `game/ui/screens/atmosphere_target_editor.py` (294 LOC, 131 stmts)
- **Coverage:** 0.0% -- completely untested
- **Untested areas:** Entire file: initialization, event handling, draw, target selection logic, atmosphere calculation display, all UI interactions
- **Risk:** Any bug in atmosphere targeting UI would go undetected. This is a specialized editor that likely has complex coordinate math for targeting.
- **Priority:** MEDIUM (specialized feature, but no safety net at all)

### C2. battle_results_screen.py -- 0% Coverage

- **Source file:** `game/ui/screens/battle_results_screen.py` (279 LOC, 167 stmts)
- **Coverage:** 0.0% -- completely untested
- **Untested areas:** Entire file: results display layout, team summary rendering, weapon accuracy charts, return navigation, ship result listing. Note: `battle_results_data.py` (the data extraction) IS well-tested at 100%, but the screen that displays that data has zero coverage.
- **Risk:** Post-battle results screen could silently break. Users see this after every battle, so visibility is high.
- **Priority:** HIGH (user-facing screen shown after every battle)

### C3. planet_abilities_window.py -- 0% Coverage

- **Source file:** `game/ui/screens/planet_abilities_window.py` (228 LOC, 119 stmts)
- **Coverage:** 0.0% -- completely untested
- **Untested areas:** Entire file: window creation, ability listing, ability effect display, selection handling
- **Risk:** Planet abilities UI could break without detection. Strategy layer interaction point.
- **Priority:** MEDIUM

### C4. settings_window.py -- 0% Coverage

- **Source file:** `game/ui/screens/settings_window.py` (109 LOC, 45 stmts)
- **Coverage:** 0.0% -- completely untested
- **Untested areas:** Entire file: settings display, value editing, save/apply logic
- **Risk:** Settings changes could silently fail. Small file, but user-critical functionality.
- **Priority:** MEDIUM

### C5. setup_renderer.py -- 10% Coverage

- **Source file:** `game/ui/screens/setup_renderer.py` (216 LOC, 100 stmts)
- **Coverage:** 10.0% (10/100 stmts)
- **Untested areas:** All rendering methods: team column drawing, ship entry rendering, formation group display, AI strategy dropdown rendering, button drawing. Only basic imports and constants are covered.
- **Risk:** Battle setup screen visual layout bugs would go undetected.
- **Priority:** LOW (visual-only code, functional behavior tested via setup_screen.py)

### C6. galaxy_test/system_mode.py -- 9.3% Coverage

- **Source file:** `game/ui/screens/galaxy_test/system_mode.py` (574 LOC, 270 stmts)
- **Coverage:** 9.3% (25/270 stmts)
- **Untested areas:** System generation logic, planet placement rendering, orbit drawing, sidebar info display, click handling for system view, planet type distribution
- **Risk:** System generation test tool could silently break. Development tool, not player-facing.
- **Priority:** LOW (developer tool)

### C7. galaxy_test/galaxy_mode.py -- 10.4% Coverage

- **Source file:** `game/ui/screens/galaxy_test/galaxy_mode.py` (424 LOC, 192 stmts)
- **Coverage:** 10.4% (20/192 stmts)
- **Untested areas:** Galaxy generation display, hex grid rendering, system placement visualization, warp lane drawing, sidebar info display
- **Risk:** Galaxy generation test tool could silently break. Development tool, not player-facing.
- **Priority:** LOW (developer tool)

### C8. galaxy_test/screen.py -- 21.3% Coverage

- **Source file:** `game/ui/screens/galaxy_test/screen.py` (284 LOC, 150 stmts)
- **Coverage:** 21.3% (32/150 stmts)
- **Untested areas:** Mode switching between menu/galaxy/system, button creation, event routing, draw delegation
- **Risk:** Galaxy test screen broken state transitions. Development tool.
- **Priority:** LOW (developer tool)

### C9. battle_ui.py (screens) -- 21.5% Coverage

- **Source file:** `game/ui/screens/battle_ui.py` (206 LOC, 121 stmts)
- **Coverage:** 21.5% (26/121 stmts)
- **Untested areas:** Panel layout management, overlay drawing, UI composition for battle view, panel resize handling, show_overlay toggle rendering
- **Risk:** Battle UI panel layout could break silently. Medium visibility since it composes the battle screen panels.
- **Priority:** MEDIUM

### C10. battle_state_viewer.py -- 29.9% Coverage

- **Source file:** `game/ui/screens/battle_state_viewer.py` (260 LOC, 127 stmts)
- **Coverage:** 29.9% (38/127 stmts)
- **Untested areas:** JSON state diff display, dual-panel rendering, scroll synchronization, keyboard navigation through diff results. NOTE: The test files that exist (test_json_diff.py, test_ui_logic.py, test_viewer_ui.py) do NOT test the actual source code -- they reimplement and test their own local versions of the algorithms (see Section A above).
- **Risk:** Battle state debugging tool broken. Developer tool, but important for debugging battle issues.
- **Priority:** MEDIUM (existing tests provide false confidence since they test reimplemented logic, not the actual code)

### C11. new_game_setup_screen.py -- 30.2% Coverage

- **Source file:** `game/ui/screens/new_game_setup_screen.py` (645 LOC, 281 stmts)
- **Coverage:** 30.2% (85/281 stmts)
- **Untested areas:** Full UI rendering, player name input handling, race setup button integration, start game button enable/disable logic, player count dropdown interaction, empire color assignment UI. The tested portions are static/class methods (validate_save_name, build_game_config) -- the actual screen UI behavior is untested.
- **Risk:** New game creation flow could break. This is a critical user path.
- **Priority:** HIGH (critical user-facing flow for starting new games)

---

## D. Cross-Domain Observations

1. **Battle state viewer tests provide false coverage confidence.** All three test files in `tests/unit/ui/battle_state_viewer/` (761 LOC total) reimplement production logic as local methods and test those reimplementations. They never import from or call `game.ui.screens.battle_state_viewer`. The coverage.json confirms this: battle_state_viewer.py is at 29.9% despite having 761 lines of "tests". These tests should be rewritten to test the actual source code, or deleted. This is the most significant finding in this review.

2. **Battle screen test suite is well-structured despite size.** The 6 battle test files (test_battle_screen.py, test_battle_screen_extended.py, test_battle_screen_simulation.py, test_battle_screen_edge_cases.py, test_battle_panels.py, test_battle_panels_extended.py) have minimal overlap after PROJ-157 cleanup. Each tests distinct aspects: basic init/win-loss, beam processing, lifecycle/events/ticks/camera, edge cases, panel click handling, and DTO integration. No duplicates found.

3. **Integration tests for build_queue are comprehensive.** The 8 integration test files in `tests/integration/ui/build_queue_screen/` and related files (3,463 LOC) provide thorough coverage of the build queue system with real multi-queue scenarios, drag-and-drop, and formatting.

4. **Strategy camera navigator** (`strategy_camera_nav.py`) has only 27.1% coverage (26/96 stmts) with just 3 test methods (50 LOC). The `center_on_system()` and `center_on_fleet()` methods appear untested -- only `center_on_hex()` is tested.

5. **race_browser_dialog.py** has 59.3% coverage (83/140 stmts). The dialog window creation and event handling paths are partially tested, but the actual race browsing/selection UI interactions are gaps.

6. **Pattern concern: bypass-init testing.** Several test files use `patch.object(Screen, '__init__', lambda self, *a, **kw: None)` to bypass initialization, then manually assign attributes. While this avoids expensive setup, it means the actual `__init__` method is never tested, and the manually-assigned state may not match real initialization. This is prevalent in: test_galaxy_test_screen.py, test_race_setup_screen.py, test_design_selector_window.py, test_battle_screen_edge_cases.py. This is an acceptable trade-off for unit tests, but the `__init__` paths should have at least one integration test each.
