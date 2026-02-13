# Test Coverage Gaps Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens (game/ui/screens/, game/ui/panels/)
- **Production Files Scanned:** 134 (109 in screens/, 25 in panels/)
- **Test Files Cross-Referenced:** 51 (43 in tests/unit/ui/screens/, 8 in tests/unit/ui/panels/)
- **Total Issues Found:** 28
- **Critical:** 2 | **Major:** 15 | **Minor:** 8 | **Info:** 3

> **Review Note (2026-02-13):** Cross-referenced existing tests - BattleScreen HAS tests (test_battle_screen.py, test_battle_screen_extended.py), and BattlePanels HAS tests (test_battle_panels.py). Updated report to remove false positives.

## Findings

### Phase 1: Untested Modules

#### CRITICAL: BattleStateViewer has no unit tests
**ID:** TCG-UI1-001
**Location:** `game/ui/screens/battle_state_viewer.py` (production) / No test file exists
**Issue:** BattleStateViewer (688 lines) implements JSON diff visualization for battle state comparison. The `compute_json_diff()` function and `ScrollableJsonPanel` class have no test coverage despite being algorithmically complex. This contains recursive diff computation, path-based change tracking, and complex UI state management.
**Impact:** JSON diff logic errors could show incorrect change highlighting; scroll/resize handling bugs could cause UI crashes. This is a critical debugging tool for test scenario development.
**Recommendation:** Create `tests/unit/ui/screens/test_battle_state_viewer.py` with:
- `compute_json_diff()` tests for changed, added, removed values across nested structures
- `_mark_all_paths()` recursive path marking
- `DIFF_IGNORE_KEYS` behavior (e.g., 'created_at' should be ignored)
- `ScrollableJsonPanel.set_json_with_diff()` formatting edge cases
- `handle_event()` scroll, drag, keyboard handling
**Effort:** Medium

#### CRITICAL: TestLabValidationManager has no unit tests
**ID:** TCG-UI1-002
**Location:** `game/ui/screens/test_lab/validation_manager.py` (production) / No test file exists
**Issue:** TestLabValidationManager (311 lines) handles critical operations including `validate_all()` for static test validation, `build_context_from_files()` for extracting ship/weapon data, and most critically `apply_metadata_updates()` which WRITES to scenario source files. File-modifying code has zero test coverage.
**Impact:** File-writing code without tests is high risk - could corrupt scenario files or lose test configurations. Validation logic bugs could cause false positives/negatives in test results.
**Recommendation:** Create tests covering:
- `validate_all()` with mock scenarios
- `build_context_from_files()` data extraction
- `apply_metadata_updates()` with mock file I/O (critical - tests file modification)
- Error handling paths
**Effort:** Complex

#### MAJOR: BuilderScreen (legacy) has no unit tests
**ID:** TCG-UI1-005
**Location:** `game/ui/screens/builder/main.py` (production) / No test file exists
**Issue:** BuilderScreen (1122 lines) is the legacy standalone ship builder GUI. While deprecated in favor of DesignWorkshopScreen, it remains functional and untested.
**Impact:** Legacy builder could break without detection if shared dependencies change.
**Recommendation:** Add minimal tests for core selection/modification flows, or mark as deprecated with lower priority.
**Effort:** Complex

#### MAJOR: FormationEditorScreen has incomplete test coverage
**ID:** TCG-UI1-006
**Location:** `game/ui/screens/formation_editor.py` (production) / `tests/unit/ui/screens/test_formation_editor_screen.py` (test)
**Issue:** FormationEditorScreen (935 lines) has test file but many public methods are untested:
- `_handle_left_down()` selection and drag initiation
- `_handle_mouse_motion()` drag/resize/pan state handling
- `generate_shape()` circle/disc/x/line generation
- `save_formation()` / `load_formation()` file I/O
- `FormationCore` model methods (move_arrow, toggle_rotation_mode)
**Impact:** Shape generation, file I/O, and interaction state machine bugs may go undetected.
**Recommendation:** Add tests for FormationCore model methods and interaction flows.
**Effort:** Medium

#### MAJOR: PlanetReportPanel has no unit tests
**ID:** TCG-UI1-007
**Location:** `game/ui/panels/planet_report_panel.py` (production) / No test file exists
**Issue:** PlanetReportPanel (509 lines) displays planet information including portrait, atmosphere graph, complexes list, and resource grid. `compute_planet_production()` utility function also lacks tests.
**Impact:** Planet detail display and production calculations may be incorrect.
**Recommendation:** Create `tests/unit/ui/panels/test_planet_report_panel.py` covering:
- `update_planet()` state update
- `_format_compact_number()` formatting
- `compute_planet_production()` harvester aggregation
- Resource grid construction
**Effort:** Medium

#### MAJOR: ShipDetailPanel has no unit tests
**ID:** TCG-UI1-008
**Location:** `game/ui/panels/ship_detail_panel.py` (production) / No test file exists
**Issue:** ShipDetailPanel (447 lines) displays ship instance details with damage tracking. `get_damage_color()` and component damage section logic are untested.
**Impact:** Damage color coding and layer collapse state management may regress.
**Recommendation:** Create `tests/unit/ui/panels/test_ship_detail_panel.py` covering:
- `get_damage_color()` threshold behavior
- `update_ship()` display building
- `toggle_layer()` state management
- `_build_damage_section()` component grouping
**Effort:** Medium

#### MAJOR: BaseGallery abstract class has no unit tests
**ID:** TCG-UI1-009
**Location:** `game/ui/panels/base_gallery.py` (production) / No test file exists
**Issue:** BaseGallery (264 lines) is an abstract base class for portrait/flag galleries. Shared code like `_populate_gallery()`, `handle_button_click()`, and `_sanitize_object_id()` are untested.
**Impact:** Gallery implementations (RacePortraitGallery, RaceFlagGallery) could have issues from base class bugs.
**Recommendation:** Create `tests/unit/ui/panels/test_base_gallery.py` with concrete test subclass to verify base behavior.
**Effort:** Simple

#### MAJOR: DesignReportPanel has no unit tests
**ID:** TCG-UI1-010
**Location:** `game/ui/panels/design_report_panel.py` (production) / No test file exists
**Issue:** DesignReportPanel (284 lines) wraps DesignStatsPanel for ship report display. Portrait path construction and fallback generation logic are untested.
**Impact:** Portrait loading and fallback display could fail silently.
**Recommendation:** Create `tests/unit/ui/panels/test_design_report_panel.py` for update_design() and _update_portrait() logic.
**Effort:** Simple

#### MAJOR: Multiple builder submodules have no tests
**ID:** TCG-UI1-011
**Location:** `game/ui/screens/builder/` (multiple files)
**Issue:** The following builder submodules have no corresponding tests:
- `schematic_view.py` (192 lines) - Ship visualization
- `left_panel.py` (476 lines) - Component list and filtering
- `right_panel.py` - Stats display
- `layer_panel.py` - Component layer display
- `weapons_panel.py` - Weapons report
- `detail_panel.py` - Component details
- `interaction_controller.py` - Mouse/keyboard handling
- `modifier_editor.py`, `modifier_config.py`, `modifier_logic.py`, `modifier_row.py` - Modifier system
- `state_manager.py` - Selection and pending actions
- `event_bus.py` - Event system
- `preset_ui.py` - Preset management
**Impact:** Ship builder functionality relies on untested UI code.
**Recommendation:** Prioritize tests for interaction_controller.py and state_manager.py as they contain non-trivial logic.
**Effort:** Complex

#### MAJOR: Multiple test_lab submodules have no tests
**ID:** TCG-UI1-012
**Location:** `game/ui/screens/test_lab/` (multiple files)
**Issue:** The Combat Lab test runner UI has no test coverage:
- `screen.py` - Main test lab screen
- `data_extractor.py` - Battle state extraction
- `validation_manager.py` - Scenario validation
- `panel_manager.py` - Panel coordination
- `test_executor.py` - Test execution orchestration
- `formatting_utils.py` - Display formatting
- `json_viewer.py` - JSON state viewer
- `dialogs.py` - Confirmation dialogs
- `component_dropdown.py` - Component selection
- `test_run_card.py`, `test_run_details.py` - Result display
- `ship_panels.py`, `results_panel.py` - Ship/result panels
**Impact:** Combat Lab UI could break without detection.
**Recommendation:** Prioritize tests for data_extractor.py and test_executor.py as they contain critical logic.
**Effort:** Complex

#### MAJOR: GalaxyTest screen module has no tests
**ID:** TCG-UI1-013
**Location:** `game/ui/screens/galaxy_test/` (production) / No test files
**Issue:** Galaxy test visualization screens (galaxy_mode.py, system_mode.py, screen.py, constants.py) have no test coverage.
**Impact:** Galaxy visualization testing tool could regress.
**Recommendation:** Add basic tests for mode switching and constants validation.
**Effort:** Simple

#### MAJOR: Formation submodules have no tests
**ID:** TCG-UI1-014
**Location:** `game/ui/screens/formation/` (input_handler.py, renderer.py)
**Issue:** Formation editor input handling (input_handler.py, ~200 lines) and rendering (renderer.py, ~300 lines) lack tests despite containing coordinate transformation and state machine logic.
**Impact:** Formation editing interactions may have bugs.
**Recommendation:** Test `FormationInputHandler` state transitions and coordinate math.
**Effort:** Medium

#### MAJOR: Workshop helper modules have thin coverage
**ID:** TCG-UI1-015
**Location:** `game/ui/screens/workshop_*.py` (multiple files)
**Issue:** Workshop screen has test file but helper modules are untested:
- `workshop_context.py` - Mode configuration
- `workshop_viewmodel.py` - MVVM state management
- `workshop_event_router.py` - Event delegation
- `workshop_data_loader.py` - Data loading
- `workshop_data_reloader.py` - Hot reload
- `workshop_ship_io.py` - Save/load operations
**Impact:** Workshop functionality depends on untested helper code.
**Recommendation:** Add unit tests for viewmodel state management and context mode logic.
**Effort:** Medium

#### MAJOR: Multiple race panel modules lack tests
**ID:** TCG-UI1-016
**Location:** `game/ui/panels/race_*.py` (multiple files)
**Issue:** Race setup UI panels have minimal coverage:
- `race_description_panel.py` - No tests
- `race_environment_panel.py` - No tests
- `race_flag_gallery.py` - No tests (base class in base_gallery.py)
- `race_portrait_gallery.py` - No tests
- `race_summary_panel.py` - No tests
- `race_theme_gallery.py` - No tests
- `race_aptitudes_panel.py` - Has tests
- `race_identity_panel.py` - Has tests
**Impact:** Race setup screens have inconsistent test coverage.
**Recommendation:** Add tests for summary_panel and description_panel at minimum.
**Effort:** Medium

### Phase 2: Undertested Public APIs

#### MAJOR: StrategyRenderer draw methods test only at mock level
**ID:** TCG-UI1-017
**Location:** `tests/unit/ui/screens/test_strategy_renderer.py`
**Issue:** StrategyRenderer tests use extensive mocking that tests "draw was called" but never verifies actual drawing behavior. For example:
- `test_draw_calls_draw_warp_lanes` only checks if method was called
- `test_draw_warp_lanes_viewport_culling_logic` uses source inspection (assert '80000' in source) instead of actual testing
**Impact:** Tests pass even if draw methods are broken; regression risk.
**Recommendation:** Add integration tests that verify rendered output or at minimum test internal logic with real data.
**Effort:** Medium

#### MAJOR: DesignStatsPanel tests use bypass-init pattern excessively
**ID:** TCG-UI1-018
**Location:** `tests/unit/ui/panels/test_design_stats_panel.py`
**Issue:** Most tests bypass `__init__` and manually set attributes. Tests like `test_mass_calculation` only assert `ship.mass == 175.5` (the mock value), testing nothing real:
```python
def test_mass_calculation(self):
    ship = _make_mock_ship()
    ship.mass = 175.5
    assert ship.mass == 175.5  # This tests the mock, not the panel
```
**Impact:** Tests verify mock behavior, not production code behavior.
**Recommendation:** Refactor to test actual panel methods with controlled inputs.
**Effort:** Medium

#### MINOR: StrategyScreen tests have incomplete method coverage
**ID:** TCG-UI1-019
**Location:** `tests/unit/ui/screens/test_strategy_screen.py`
**Issue:** Test file exists but many public methods lack tests: `handle_resize()`, `cleanup()`, empire iteration, battle initiation. Only initialization and basic turn advancement are tested.
**Impact:** Core strategy screen functionality has gaps.
**Recommendation:** Add tests for missing public methods.
**Effort:** Medium

### Phase 3: Critical Path Coverage

#### MINOR: Screen transition handling untested
**ID:** TCG-UI1-020
**Location:** Multiple screens (battle_screen.py, strategy_screen.py, setup_screen.py)
**Issue:** Scene callback mechanisms for screen transitions (`_trigger_return_to_setup`, `_trigger_return_to_test_lab`, `scene_callback`) have no dedicated tests.
**Impact:** Screen navigation bugs could cause game crashes or stuck states.
**Recommendation:** Add tests verifying callback invocation on expected events.
**Effort:** Simple

#### MINOR: Input handling edge cases untested
**ID:** TCG-UI1-021
**Location:** `game/ui/screens/strategy_input_handler.py`, `game/ui/screens/battle_screen.py`
**Issue:** Tests exist for hotkeys but edge cases are missing:
- Rapid repeated key presses
- Conflicting modifier keys
- Focus loss during input
**Impact:** Input handling bugs in edge cases.
**Recommendation:** Add edge case tests for input handlers.
**Effort:** Simple

### Phase 4: Test Quality Issues

#### MINOR: Source code inspection used instead of behavior testing
**ID:** TCG-UI1-022
**Location:** `tests/unit/ui/screens/test_strategy_renderer.py` lines 343-349
**Issue:** Test uses `inspect.getsource()` to check if a constant exists:
```python
def test_draw_grid_skips_massive_hex_counts(self, renderer, mock_scene):
    from game.ui.screens.strategy_renderer import StrategyRenderer
    import inspect
    source = inspect.getsource(StrategyRenderer._draw_grid)
    assert '80000' in source  # The threshold constant exists
```
This is fragile and doesn't test behavior.
**Impact:** Source changes (renaming variable, changing constant value) break test even if behavior is correct.
**Recommendation:** Replace with behavior-based test using actual hex count threshold.
**Effort:** Simple

#### MINOR: Mock verification without assertions on behavior
**ID:** TCG-UI1-023
**Location:** `tests/unit/ui/screens/test_strategy_renderer.py`
**Issue:** Multiple tests only verify that methods were called without asserting any output:
```python
def test_draw_warp_lanes_iterates_systems(self, renderer, mock_scene):
    renderer._draw_warp_lanes(screen)
    # Verify iteration happened (no exception)
```
This is essentially "didn't crash" testing.
**Impact:** Tests pass even if methods do nothing correct.
**Recommendation:** Add specific assertions about state changes or output.
**Effort:** Simple

#### MINOR: Test helper function tests its own mock
**ID:** TCG-UI1-024
**Location:** `tests/unit/ui/panels/test_design_stats_panel.py` lines 188-212
**Issue:** `TestDesignStatsPanelStatCalculation` class tests mock objects, not production code:
```python
def test_mass_calculation(self):
    ship = _make_mock_ship()
    ship.mass = 175.5
    assert ship.mass == 175.5  # Tests the mock!
```
**Impact:** No production code exercised; false confidence in coverage.
**Recommendation:** Rewrite to test actual DesignStatsPanel behavior with ship input.
**Effort:** Simple

#### MINOR: Missing parameterized edge case tests
**ID:** TCG-UI1-025
**Location:** Various test files
**Issue:** Many test functions test single happy path without edge cases:
- Empty collections
- None values
- Boundary values (0, -1, max values)
- Invalid inputs
**Impact:** Edge case bugs undetected.
**Recommendation:** Add pytest.mark.parametrize for edge cases.
**Effort:** Simple

### Phase 5: Integration Test Gaps

#### MINOR: No end-to-end battle UI flow tests
**ID:** TCG-UI1-026
**Location:** Integration test gap
**Issue:** No tests verify the complete flow: SetupScreen -> BattleScreen -> test completion -> return to setup. Components are unit tested in isolation but integration is not.
**Impact:** Integration bugs between screens.
**Recommendation:** Add integration test for battle round-trip.
**Effort:** Medium

#### MINOR: Strategy screen + build queue integration untested
**ID:** TCG-UI1-027
**Location:** Integration test gap
**Issue:** StrategyScreen interacts with BuildQueueScreen, EmpireBuildQueueWindow, and BuildQueueListWindow. No tests verify this multi-component interaction.
**Impact:** Build queue integration bugs.
**Recommendation:** Add tests for build queue screen lifecycle from strategy.
**Effort:** Medium

#### MINOR: Workshop + ship I/O roundtrip untested
**ID:** TCG-UI1-028
**Location:** Integration test gap
**Issue:** DesignWorkshopScreen uses WorkshopShipIO for save/load but the complete roundtrip (create ship -> save -> reload -> verify) is not integration tested.
**Impact:** Ship save/load data corruption could go undetected.
**Recommendation:** Add workshop ship I/O roundtrip test.
**Effort:** Medium

### Phase 6: Missing Test Categories

#### MINOR: No resize handling tests
**ID:** TCG-UI1-029
**Location:** Multiple screens with `handle_resize()` methods
**Issue:** `handle_resize()` methods exist in:
- BattleScreen, BattleUI
- FormationEditorScreen
- StrategyScreen
- Multiple panels

None have tests for window resize behavior.
**Impact:** Resize bugs (layout breaks, crashes) undetected.
**Recommendation:** Add parametrized resize tests with various dimensions.
**Effort:** Simple

#### INFO: No error recovery tests for UI screens
**ID:** TCG-UI1-030
**Location:** All screens
**Issue:** UI screens have no tests for error recovery scenarios:
- What happens if ship loading fails mid-battle?
- What if asset loading fails?
- What if session state is corrupt?
**Impact:** Error scenarios cause crashes instead of graceful handling.
**Recommendation:** Consider adding error injection tests for critical flows.
**Effort:** Complex

#### INFO: No performance/stress tests for panels with dynamic content
**ID:** TCG-UI1-031
**Location:** `game/ui/panels/battle_panels.py`, `game/ui/screens/builder/left_panel.py`
**Issue:** Panels that display dynamic lists (ships, components, seekers) are not tested with large datasets:
- 100+ ships in battle
- 500+ components in list
- 50+ tracked seekers
**Impact:** Performance issues with large data.
**Recommendation:** Add benchmark tests with large datasets (lower priority).
**Effort:** Medium

#### INFO: UI panels lack null/empty data tests
**ID:** TCG-UI1-032
**Location:** Various panels
**Issue:** Panels that display entity data (PlanetReportPanel, ShipDetailPanel, DesignReportPanel) are not tested with:
- None values
- Empty collections
- Missing optional fields
**Impact:** NoneType errors or empty display bugs.
**Recommendation:** Add null/empty defensive tests.
**Effort:** Simple

## Top 5 Priority Issues

1. **TCG-UI1-002 (CRITICAL):** TestLabValidationManager writes to scenario files with zero test coverage - highest risk for data corruption in test infrastructure.

2. **TCG-UI1-001 (CRITICAL):** BattleStateViewer JSON diff logic untested - critical debugging tool could produce incorrect results showing false changes or missing real ones.

3. **TCG-UI1-011 (MAJOR):** Builder submodules (19 files including interaction_controller, state_manager, modifier_logic) have no tests - ship design workflow at risk.

4. **TCG-UI1-012 (MAJOR):** Combat Lab (test_lab) UI components (14 files) have only 1 test file - testing tool itself is mostly untested.

5. **TCG-UI1-018 (MAJOR):** DesignStatsPanel tests use bypass-init pattern that tests mocks instead of production code - provides false confidence in coverage.
