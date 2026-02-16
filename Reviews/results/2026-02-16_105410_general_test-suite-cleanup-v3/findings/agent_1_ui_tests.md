# Agent 1: UI Tests Analysis

## Summary
- Files analyzed: 138 (all test files in tests/unit/ui/)
- Removal candidates found: 14
- HIGH confidence: 5
- MEDIUM confidence: 5
- LOW confidence: 4

---

## HIGH Confidence Removal Candidates
(Tests almost certainly safe to remove)

### 1. test_overlay.py -- Over-mocked / Tests nothing real
- **Location:** `tests/unit/ui/test_overlay.py`
- **Category:** Over-mocked / Tests nothing real
- **Reason:** This file tests "BattleOverlayControls" but never imports or calls any actual game module. Every test creates a `MagicMock()` scene and then manually toggles attributes with inline `if event.key == pygame.K_o:` logic. It is literally testing Python's `not` operator and `min()/max()` builtins, not any game code. The actual overlay keyboard handling is in `BattleScreen.handle_event()` / `BattleScreen._handle_keydown()`, which is already thoroughly tested by `test_battle_screen_simulation.py` and `screens/test_battle_screen_edge_cases.py`. No game code is imported; no game function is called.
- **Lines:** ~127 lines that could be removed

### 2. test_race_validator.py (root) -- Duplicate of screens/ version
- **Location:** `tests/unit/ui/test_race_validator.py`
- **Category:** Duplicate
- **Reason:** This is the PROJ-12 Phase 4 scaffold version that uses `MagicMock()` configs. The newer `tests/unit/ui/screens/test_race_validator.py` (PROJ-66 Phase 7) uses real `RaceConfig` objects and covers additional validation including budget checks, water ranges, and aptitude ranges. Every behavior tested in the root file (missing name, missing flag, missing portrait, missing theme, error messages) is also tested in the screens/ version with better coverage. The root file adds zero unique coverage.
- **Lines:** ~283 lines that could be removed

### 3. mock_battle_ui_service.py -- Unused test mock
- **Location:** `tests/unit/ui/mocks/mock_battle_ui_service.py`
- **Category:** Dead code
- **Reason:** This `MockBattleUIService` class is never imported by any test file in the entire test suite. A grep for `MockBattleUIService` across all of `tests/` returns hits only in the mock file itself and its `__init__.py` re-export. All actual BattleUIService tests use `unittest.mock.Mock/MagicMock` instead. The 256-line mock class was created in PROJ-43 Phase 12 but was never adopted.
- **Lines:** ~256 lines (including `__init__.py` re-export)

### 4. test_slider_snap_logic.py -- Tests local helper methods, not game code
- **Location:** `tests/unit/ui/test_slider_snap_logic.py`
- **Category:** Tests nothing real (no game code imported)
- **Reason:** The `TestModifierLogic` class defines `calculate_snap_decrement`, `calculate_snap_increment`, and `calculate_size_decrement` as *methods on the test class itself*, then tests those local methods. No game module is imported. No game function is called. These appear to be prototype/scratch tests for logic that was later implemented in `game/ui/screens/builder/modifier_logic.py`, but the tests never reference that module.
- **Lines:** ~96 lines that could be removed

### 5. test_config.py -- Trivially obvious constant validation
- **Location:** `tests/unit/ui/test_config.py`
- **Category:** Trivially obvious / Low value
- **Reason:** Every test in this file asserts that a UIConfig constant is positive (e.g., `assert UIConfig.PANEL_PADDING > 0`, `assert UIConfig.TOAST_WIDTH > 0`, `assert UIConfig.BAR_HEIGHT > 0`). There are 30+ tests that each assert a single integer constant is `> 0` or within a range. These constants are compile-time literals that would never silently become negative or zero. The one structural test (`test_all_constants_are_integers`) could be valuable but is trivially true given the class definition. The `test_font_sizes_hierarchy` and `test_confirm_dialog_larger_than_toast` tests verify relationships between constants, but these are also trivially obvious design constraints. Total: 213 lines of tests that validate static integer literals.
- **Lines:** ~213 lines that could be removed

---

## MEDIUM Confidence Removal Candidates
(Tests that have significant overlap or low value, but removing requires more care)

### 6. test_battle_screen_extended.py -- Mostly duplicated by test_battle_screen_simulation.py
- **Location:** `tests/unit/ui/test_battle_screen_extended.py`
- **Category:** Duplicate / Overlap
- **Reason:** This 130-line file has 4 test methods: `test_is_battle_over_victory`, `test_update_loop_tick_counter`, `test_headless_mode_initialization`, and `test_process_beam_attack_logic`. The first three are direct duplicates of tests in `test_battle_screen.py` (`test_battle_over_condition`, `test_update_increment_sim_tick`) and `test_battle_screen_simulation.py` (`TestBattleScreenSimulationLifecycle.test_start_headless_true_sets_headless_mode`). The beam attack test is the only unique one, but it tests an internal implementation detail (`collision_system.process_beam_attack`). This file also requires loading AI Strategy Manager data per-test (heavy fixture), making it slower than the equivalent tests elsewhere.
- **Lines:** ~130 lines that could be removed (after verifying beam attack test coverage)

### 7. screens/test_battle_screen_edge_cases.py -- Heavily overlaps with test_battle_screen_simulation.py
- **Location:** `tests/unit/ui/screens/test_battle_screen_edge_cases.py`
- **Category:** Duplicate / Overlap
- **Reason:** This 408-line file duplicates many tests from `test_battle_screen_simulation.py`. Specific overlaps:
  - `test_handle_mouse_click_focus_ship_result` = `TestBattleScreenEventHandling.test_handle_event_focus_ship_from_ui_click`
  - `test_handle_mouse_click_end_battle_result` = `TestBattleScreenEventHandling.test_handle_event_end_battle_from_ui_click`
  - `test_keydown_space_toggles_pause` = `TestBattleScreenEventHandling.test_handle_event_keyboard_space_toggles_pause`
  - `test_keydown_comma_decreases_speed` = `TestBattleScreenEventHandling.test_handle_event_keyboard_comma_decreases_speed`
  - `test_keydown_period_increases_speed` = `TestBattleScreenEventHandling.test_handle_event_keyboard_period_increases_speed`
  - `test_keydown_m_resets_to_normal_speed` = `TestBattleScreenEventHandling.test_handle_event_keyboard_m_resets_speed`
  - `test_keydown_slash_sets_ui_pause_speed` = `TestBattleScreenEventHandling.test_handle_event_keyboard_slash_sets_ui_pause_speed`
  - `test_update_headless_mode` / `test_update_visual_mode` = `TestBattleScreenSimulationLifecycle.test_start_headless_true_sets_headless_mode`

  The edge_cases file uses `__new__` + lambda init bypass pattern while simulation uses proper BattleScreen initialization. Both approaches are valid but maintaining both is unnecessary.
- **Lines:** ~408 lines, likely ~300 are pure duplicates

### 8. services/test_battle_ui_service.py -- Heavily overlaps with services/battle_ui_service/ directory
- **Location:** `tests/unit/ui/services/test_battle_ui_service.py`
- **Category:** Duplicate / Overlap
- **Reason:** This 356-line file duplicates many tests from `services/battle_ui_service/test_state_and_integration.py` (698 lines) and `services/battle_ui_service/test_conversion.py` (163 lines). Specific overlaps:
  - `TestGetEngineOrNone` = `TestBattleUIServiceEngineHelper` in test_state_and_integration.py
  - `TestGetShips.test_get_ships_returns_empty_when_no_engine` = `TestBattleUIServiceNoEngine.test_get_ships_returns_empty_when_no_engine`
  - `TestGetProjectiles.test_get_projectiles_returns_empty_when_no_engine` = `TestBattleUIServiceNoEngine.test_get_projectiles_returns_empty_when_no_engine`
  - `TestGetRecentBeams.test_get_recent_beams_returns_empty_when_no_engine` = `TestBattleUIServiceNoEngine.test_get_recent_beams_returns_empty_when_no_engine`
  - `TestBattleStateQueries` methods = `TestBattleUIServiceBattleState` and `TestBattleUIServiceNoneEngine`
  - `TestConvertBeam.test_convert_beam_with_missing_keys` = `TestBattleUIServiceConversionEdgeCases.test_convert_beam_with_missing_keys`

  The subdirectory tests are more comprehensive and include real domain object integration tests. The flat file appears to be the PROJ-142 TCG version that was superseded by the PROJ-43 audit expansion.
- **Lines:** ~356 lines, likely ~280 are duplicates

### 9. test_colors.py -- Mostly trivially obvious
- **Location:** `tests/unit/ui/test_colors.py`
- **Category:** Trivially obvious / Low value
- **Reason:** While `TestColorsValidation` (all RGB tuples, in range 0-255) has some structural value, the rest is largely trivial:
  - `TestBasicColors` tests that `WHITE == (255,255,255)` and `BLACK == (0,0,0)` and `WHITE + BLACK = 255` -- this verifies Python literals.
  - `TestFontConstants` tests that `FONT_MAIN` is a non-empty string containing a common font name -- very low value.
  - `TestColorAccessibility` tests that text colors have luminance > 80 and background colors have luminance < 100 -- these are design opinions that are fragile and don't prevent bugs.
  The `TestColorsValidation.test_all_colors_are_rgb_tuples` and `test_all_components_are_integers_in_range` tests are the only ones with structural value, preventing someone from adding an invalid color. The other ~80 lines are trivial.
- **Lines:** ~141 total, ~80 lines trivial, ~60 lines marginally useful

### 10. test_ui_imports.py -- Trivially obvious import smoke tests
- **Location:** `tests/unit/ui/test_ui_imports.py`
- **Category:** Trivially obvious / Low value
- **Reason:** Tests that `import game.ui` succeeds, `import game.ui.renderer` succeeds, etc. These are pure smoke tests that would only fail if a module had a syntax error or broken dependency, which would be caught immediately by any other test importing that module. The `test_workshop_screen_not_auto_imported` test has a good intent (documenting that Tkinter-dependent screens shouldn't auto-import) but the test doesn't actually verify the behavior -- it just re-imports game.ui and checks that `'game.ui'` is in `sys.modules`, which is trivially true.
- **Lines:** ~81 lines that provide minimal value

---

## LOW Confidence Removal Candidates
(Tests with some issues but may still provide value worth keeping)

### 11. test_scene_protocol.py -- TestGameSwitchScene tests nothing real
- **Location:** `tests/unit/ui/test_scene_protocol.py`
- **Category:** Partially over-mocked
- **Reason:** The `TestISceneProtocolCompliance` class (lines 10-150) is valuable -- it tests that all scene classes implement the `IScene` protocol. However, `TestGameSwitchScene` (lines 152-192) tests nothing real: it creates a `MagicMock()` and sets attributes on it, verifying that Python attribute assignment works. `TestSceneCallback` (lines 194-240) is also valuable. Recommend keeping IScene compliance and callback tests but removing `TestGameSwitchScene` (~40 lines).
- **Lines:** ~40 lines in TestGameSwitchScene are zero-value

### 12. test_battle_panels.py + test_battle_panels_extended.py -- Mock pygame at sys.modules level
- **Location:** `tests/unit/ui/test_battle_panels.py` and `tests/unit/ui/test_battle_panels_extended.py`
- **Category:** Fragile over-mocking
- **Reason:** Both files use `patch.dict(sys.modules, {'pygame': mock_pygame})` to replace pygame entirely at the module level, and implement a custom `MockRect` class. This fragile approach can break when import order changes or when the code under test uses different pygame features. The tests do test real `BattleUI` behavior (panel rendering, collision detection), so they have value. However, the duplicated `MockRect` class between the two files (30+ identical lines each) should at least be extracted to a shared fixture. Not removal candidates, but significant cleanup candidates.
- **Lines:** ~60 lines of duplicated MockRect across both files

### 13. renderer/test_game_renderer.py -- Many trivially obvious constant tests
- **Location:** `tests/unit/ui/renderer/test_game_renderer.py`
- **Category:** Partially trivially obvious
- **Reason:** The `TestRenderingConstants` class validates that rendering constants are positive integers (similar pattern to `test_config.py`). Tests like `assert CULLING_MAX_RADIUS > 0` and `assert COMPONENT_DOT_RADIUS > 0` are trivially obvious. However, the file also contains tests for actual rendering behavior (`TestDrawShipBehavior`, `TestLayerColors`) which are valuable. Recommend removing the ~100 lines of constant validation while keeping the behavioral tests.
- **Lines:** ~100 lines of trivially obvious constant validation (out of 397 total)

### 14. test_strategy_detail_formatter.py -- TestStrategyDetailFormatterWidgetAccessors tests nothing real
- **Location:** `tests/unit/ui/screens/test_strategy_detail_formatter.py`
- **Category:** Partially over-mocked / trivially obvious
- **Reason:** The `TestStrategyDetailFormatterWidgetAccessors` class (lines 71-131) tests that mock properties return the same mock name. Tests like `assert formatter.portrait_image._mock_name == 'portrait'` verify that the mock was set up correctly, not that the real code works. These 8 tests could be removed (~60 lines). The `TestResizeSupport` class (lines 425-468) tests trivial setter methods (`update_screen_size`, `update_graph_rect`, `update_graphs`) that just store values -- also trivially obvious (~40 lines). The rest of the file (init, show_detailed_report, compute_planet_production, show_raw_data_popup) is valuable.
- **Lines:** ~100 lines of low-value tests (out of 537 total)

---

## Summary of Removable Lines

| Confidence | Files | Lines Removable |
|-----------|-------|----------------|
| HIGH | 5 files | ~975 lines |
| MEDIUM | 5 files | ~1,145 lines |
| LOW | 4 files | ~300 lines |
| **Total** | **14 files** | **~2,420 lines** |

## Key Patterns Found

### Pattern 1: Duplicate test files at different paths
The most impactful finding is multiple test files testing the same class from different project phases (PROJ-12 vs PROJ-66, PROJ-142 vs PROJ-43). When a later project expanded testing for a class, the earlier tests were not removed.

### Pattern 2: Tests that test nothing real (over-mocked)
Several test files create `MagicMock()` objects and test Python builtin behavior (attribute assignment, boolean toggling, min/max clamping) without ever importing or calling actual game code. These tests can never catch a regression.

### Pattern 3: Trivially obvious constant validation
A PROJ-142 pattern of testing that every integer constant is positive (`assert X > 0`) was applied across `test_config.py`, `test_colors.py`, and `renderer/test_game_renderer.py`. These test static literals that cannot change at runtime.

### Pattern 4: Unused test infrastructure
`MockBattleUIService` (256 lines) was built as test infrastructure but never used by any test.

## Files NOT flagged (confirmed good)
- `test_camera.py` -- Tests real Camera class with meaningful coordinate transform and zoom tests
- `test_battle_screen.py` -- Core BattleScreen tests, no duplication
- `test_sprites.py` -- Tests real SpriteManager with meaningful singleton/thread-safety/parsing tests
- `test_utils.py` -- Tests real utility functions with edge cases
- `test_structure_visibility.py` -- Tests real LayerPanel with meaningful ship component visibility tests
- `test_rendering_logic.py` -- Tests real `draw_ship` function behavior
- All `screens/` tests for strategy, workshop, fleet, planet, etc. -- Generally well-structured and test real behavior
- All `panels/` tests -- Test real panel classes
- All `services/` tests in `battle_ui_service/` subdirectory -- Comprehensive with real domain integration
- `battle_state_viewer/`, `schematic_view/`, `left_panel/` -- All test real classes with meaningful assertions
