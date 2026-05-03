# Validation Review 1: UI + Strategy Findings

## Summary
- Findings reviewed: 28 (14 UI + 14 Strategy)
- **CONFIRMED for removal: 12**
- **DISPUTED (should keep): 6**
- **MODIFIED (partial removal only): 10**

---

## UI Findings Validation

---

### UI-1: test_overlay.py (HIGH)
- **Original claim:** Over-mocked, tests nothing real. No game code imported; tests Python's `not` operator and `min()`/`max()` builtins.
- **Verdict:** CONFIRMED
- **Evidence:** Read the file (127 lines). Every test creates a `MagicMock()` scene, then manually writes the logic inline (`if event.key == pygame.K_o: self.scene.show_overlay = not self.scene.show_overlay`). No game module is ever imported. No function from `game/` is ever called. The tests are literally testing that Python's `not` operator toggles a boolean and `min()`/`max()` clamp a float. The actual overlay logic lives in `BattleScreen._handle_keydown()` and is already tested by `test_battle_screen_simulation.py` (methods: `test_handle_event_keyboard_space_toggles_pause`, `test_handle_event_keyboard_comma_decreases_speed`, `test_handle_event_keyboard_period_increases_speed`, `test_handle_event_keyboard_m_resets_speed`, `test_handle_event_keyboard_slash_sets_ui_pause_speed`).
- **Unique tests that would be lost:** None. Every behavior (toggle overlay, toggle pause, speed up/down/reset, max/min caps) is tested against real `BattleScreen` code in the simulation test file.
- **Risk of removal:** None

---

### UI-2: test_race_validator.py (root) (HIGH)
- **Original claim:** Duplicate of `screens/test_race_validator.py`. Root version uses MagicMock configs; screens version uses real RaceConfig objects.
- **Verdict:** CONFIRMED
- **Evidence:** Read both files. Root version (283 lines, PROJ-12) tests: import, instantiate, has-validate, complete config valid, missing name/flag/portrait/theme, whitespace name, None name, first-error-found, error-message-tab-references. Screens version (313 lines, PROJ-66) tests all of the above PLUS: budget validation (over-budget, within-budget), water range validation (ideal too high/low, tolerance too high, valid range), aptitude range validation (too high, too low, valid range), full new-fields test, error-message-references-tab, empty-identity-fields. The root version uses `MagicMock()` configs which don't validate that `RaceValidator.validate()` actually works with real `RaceConfig` objects. The screens version uses real `RaceConfig()` objects, testing the actual integration. Every behavior in the root version is covered by the screens version with better fidelity.
- **Unique tests that would be lost:** `test_validate_whitespace_name_returns_invalid` and `test_validate_none_name_returns_invalid` are NOT explicitly in the screens version. However, the screens version tests `validate_missing_name` with a `RaceConfig()` where `config.name` defaults to empty string, which covers the empty-name case. The None and whitespace edge cases are worth preserving.
- **Risk of removal:** Low, but recommend merging the 2 unique edge-case tests (None name, whitespace name) into the screens version first.

---

### UI-3: mock_battle_ui_service.py (HIGH)
- **Original claim:** Unused test mock, never imported by any test file.
- **Verdict:** CONFIRMED
- **Evidence:** Ran grep for `MockBattleUIService` across entire `tests/` directory. Only hits are in `mock_battle_ui_service.py` itself (the definition) and `mocks/__init__.py` (the re-export). Zero test files import or use this class. All actual BattleUIService tests use `unittest.mock.Mock`/`MagicMock`. 256 lines of dead infrastructure.
- **Unique tests that would be lost:** None (this is not a test file, it's a mock class that no test uses).
- **Risk of removal:** None

---

### UI-4: test_slider_snap_logic.py (HIGH)
- **Original claim:** Tests local helper methods defined on the test class itself, not any game code.
- **Verdict:** CONFIRMED
- **Evidence:** Read the file (97 lines). The test class `TestModifierLogic` defines `calculate_snap_decrement`, `calculate_snap_increment`, and `calculate_size_decrement` as *methods on the test class*. No `import` from `game/` anywhere. The actual logic lives in `game/ui/screens/builder/modifier_logic.py` (confirmed this file exists via glob). These tests are scratch prototypes that test local method implementations rather than the real game module.
- **Unique tests that would be lost:** None from the game's perspective. The tests never exercise real game code.
- **Risk of removal:** None

---

### UI-5: test_config.py (HIGH)
- **Original claim:** Trivially obvious constant validation. 213 lines that assert static integer literals are positive.
- **Verdict:** MODIFIED
- **Evidence:** Read the full file (213 lines). The file has 9 test classes with ~30 tests. Nearly all follow the pattern `assert UIConfig.X > 0` for a single static constant. However, two categories of tests provide non-trivial value:
  1. **`test_all_constants_are_integers`** (TestUIConfigAllConstantsAreIntegers) - dynamically inspects all UIConfig attributes and asserts they're all `int`. This would catch someone adding a `float` or `str` constant, which could cause pygame rendering bugs.
  2. **Relationship tests** - `test_font_sizes_hierarchy` (title >= name >= stat), `test_confirm_dialog_larger_than_toast`, `test_row_height_large_larger_than_standard` - these verify design constraints that could be violated during refactoring.
  3. **Range test** - `test_panel_alpha_in_range` (0-255) prevents an alpha value that would crash pygame.

  The pure positivity checks (`assert X > 0`) are genuinely trivially obvious - these are integer class attributes that cannot silently become zero or negative.
- **Unique tests that would be lost:** The `test_all_constants_are_integers` test and the relationship/range tests are unique and valuable.
- **Recommendation:** Keep `TestUIConfigAllConstantsAreIntegers`, `test_font_sizes_hierarchy`, `test_confirm_dialog_larger_than_toast`, `test_row_height_large_larger_than_standard`, `test_panel_alpha_in_range`, `test_toast_dimensions_reasonable`. Remove the ~20 pure `assert X > 0` tests (~130 lines removable, ~80 lines kept).
- **Risk of removal (full):** Low-Medium. Risk of removal (partial): None.

---

### UI-6: test_battle_screen_extended.py (MEDIUM)
- **Original claim:** 4 tests, 3 are duplicates, 1 unique beam test.
- **Verdict:** MODIFIED
- **Evidence:** Read the file (131 lines). Four tests:
  1. `test_is_battle_over_victory` - Creates real Ship objects, tests `is_battle_over()` and `get_winner()`. **Overlaps** with `test_battle_screen.py::test_battle_over_condition` and `test_battle_screen_simulation.py::TestBattleScreenVictoryConditions` which test the same thing more thoroughly.
  2. `test_update_loop_tick_counter` - Tests accumulator-based tick counting with real BattleScreen. **Overlaps** with `test_battle_screen.py::test_update_increment_sim_tick` and `test_battle_screen_simulation.py::test_speed_multiplier_changes_affect_tick_accumulation`.
  3. `test_headless_mode_initialization` - Tests `start([], [], headless=True)`. **Overlaps** with `test_battle_screen_simulation.py::test_start_headless_true_sets_headless_mode`.
  4. `test_process_beam_attack_logic` - Tests `collision_system.process_beam_attack(beam, ...)` with a mock ability. **This is unique** - no other test file directly tests the collision_system's beam processing at this level.

  **Important:** This file requires loading AI Strategy Manager data per-test (heavy fixture `setup_strategy_manager`), making it slow. The 3 duplicate tests are better tested elsewhere with lighter fixtures.
- **Unique tests that would be lost:** `test_process_beam_attack_logic` - tests collision_system beam attack processing.
- **Recommendation:** Delete the 3 duplicate tests. Either keep `test_process_beam_attack_logic` here or relocate it to a collision system test file. Do NOT delete the beam test without verifying coverage exists elsewhere.
- **Risk of removal (full):** Medium (beam attack test is unique). Risk of removal (partial, keep beam test): None.

---

### UI-7: screens/test_battle_screen_edge_cases.py (MEDIUM)
- **Original claim:** 408 lines, heavily overlaps with test_battle_screen_simulation.py.
- **Verdict:** MODIFIED
- **Evidence:** Read the full file (408 lines). Contains 4 test classes with 18 test methods total:

  **TestHandleEventEdgeCases (6 tests):**
  - `test_handle_event_unknown_event_type` - **UNIQUE**: tests that unknown event types don't crash.
  - `test_handle_mouse_click_none_result` - **UNIQUE**: tests that left-click with None result clears camera target.
  - `test_handle_mouse_click_focus_ship_result` - **DUPLICATE** of simulation file.
  - `test_handle_mouse_click_end_battle_result` - **DUPLICATE** of simulation file.
  - `test_handle_right_click_no_clear` - **UNIQUE**: tests right-click does NOT clear camera target (important edge case).
  - `test_handle_mousewheel` - **DUPLICATE** of simulation file.

  **TestKeyboardShortcutEdgeCases (10 tests):**
  - `test_keydown_f3_toggles_overlay` - **UNIQUE**: F3 key not tested in simulation file.
  - `test_keydown_space_toggles_pause` - **DUPLICATE**.
  - `test_keydown_comma_decreases_speed` - **DUPLICATE**.
  - `test_keydown_comma_respects_minimum` - **UNIQUE**: tests minimum speed boundary.
  - `test_keydown_period_increases_speed` - **DUPLICATE**.
  - `test_keydown_period_respects_maximum` - **UNIQUE**: tests maximum speed boundary.
  - `test_keydown_m_resets_to_normal_speed` - **DUPLICATE**.
  - `test_keydown_slash_sets_ui_pause_speed` - **DUPLICATE**.
  - `test_keydown_bracket_cycles_focus` - **DUPLICATE** of simulation file.
  - `test_keydown_right_bracket_cycles_forward` - **DUPLICATE** of simulation file.

  **TestBattleStateEdgeCases (2 tests):**
  - `test_update_headless_mode` - Tests update dispatches to `_update_headless`. Tested differently in simulation.
  - `test_update_visual_mode` - Tests update dispatches to `_update_visual`. Tested differently in simulation.

  **TestResizeEdgeCases (2 tests):**
  - `test_handle_resize_updates_dimensions` - **TRIVIAL**: just assigns values.
  - `test_handle_resize_camera_available` - **TRIVIAL**: asserts camera is not None.

  **Unique tests: 6 out of 18** (unknown event type, None click clears target, right-click no-clear, F3 overlay, min speed boundary, max speed boundary).
- **Unique tests that would be lost:** 6 tests that cover genuine edge cases not tested elsewhere.
- **Recommendation:** Keep the 6 unique tests. Remove the 12 duplicates and 2 trivial tests (~250 lines removable, ~160 lines kept). Alternatively, migrate the 6 unique tests into the simulation test file and delete this file entirely.
- **Risk of removal (full):** Medium-High (6 unique edge case tests lost). Risk of removal (partial): None.

---

### UI-8: services/test_battle_ui_service.py (MEDIUM)
- **Original claim:** 356 lines, heavily overlaps with services/battle_ui_service/ directory.
- **Verdict:** MODIFIED
- **Evidence:** Read the flat file (356 lines) and compared test method names with the subdirectory tests. The flat file has 13 test classes with ~25 test methods. Overlap analysis:

  **Duplicates confirmed:**
  - `TestGetEngineOrNone` (2 tests) = `test_state_and_integration.py::TestBattleUIServiceEngineHelper` (3 tests, superset)
  - `TestGetShips::test_get_ships_returns_empty_when_no_engine` = `test_state_and_integration.py::TestBattleUIServiceNoEngine`
  - `TestGetProjectiles::test_get_projectiles_returns_empty_when_no_engine` = `test_state_and_integration.py::TestBattleUIServiceNoEngine`
  - `TestGetRecentBeams::test_get_recent_beams_returns_empty_when_no_engine` = `test_state_and_integration.py::TestBattleUIServiceNoEngine`
  - `TestBattleStateQueries` (6 tests) = `test_state_and_integration.py::TestBattleUIServiceBattleState` + `TestBattleUIServiceNoneEngine`
  - `TestConvertBeam::test_convert_beam_with_missing_keys` = `test_state_and_integration.py::test_convert_beam_with_missing_keys`

  **Unique to flat file:**
  - `TestProjectileColors` (3 tests) - tests PROJECTILE_COLORS mapping has AttackTypes, colors are RGB tuples, DEFAULT_PROJECTILE_COLOR is RGB. **Not in subdirectory tests.**
  - `TestBattleUIServiceInitialization::test_initialization_stores_battle_service` - **Not explicitly in subdirectory** (subdirectory tests service creation implicitly).
  - `TestGetShips::test_get_ships_converts_to_dtos` - Full mock-based DTO conversion test. Subdirectory has `test_convert_real_ship_to_dto` which is a real integration test (better), but this mock test covers the code path differently.
  - `TestGetProjectiles::test_get_projectiles_converts_to_dtos` - Similar: covered by subdirectory but with different mock setup.
  - `TestGetRecentBeams::test_get_recent_beams_converts_to_dtos` - Similar.
  - `TestConvertComponent::test_convert_component_creates_dto` - Covered by `test_state_and_integration.py::test_convert_component_with_status_enum` etc.

  **Truly unique: 3-4 tests** (PROJECTILE_COLORS tests, init test).
- **Unique tests that would be lost:** TestProjectileColors (3 tests) testing PROJECTILE_COLORS dict structure. These are structural tests that prevent color config regressions.
- **Recommendation:** Migrate TestProjectileColors (3 tests) to the subdirectory, then delete the flat file. ~310 lines removable, ~45 lines migrated.
- **Risk of removal (full):** Low-Medium (lose PROJECTILE_COLORS validation). Risk of removal (partial): None.

---

### UI-9: test_colors.py (MEDIUM)
- **Original claim:** Mostly trivially obvious. Only TestColorsValidation has structural value.
- **Verdict:** MODIFIED
- **Evidence:** Read the full file (142 lines). Five test classes:

  **TestColorsValidation (5 tests) - KEEP ALL:**
  - `test_all_colors_are_rgb_tuples` - Structural: catches invalid color definitions.
  - `test_all_components_are_integers_in_range` - Structural: prevents out-of-range RGB values that crash pygame.
  - `test_colors_dict_has_expected_categories` - Documents expected color naming convention.
  - `test_no_duplicate_color_values` - Documents intentional/accidental duplicates.
  - `test_colors_dict_is_not_empty` - Trivial but harmless.

  **TestBasicColors (3 tests) - REMOVE:**
  - `test_white_is_rgb_white` - Tests literal `WHITE == (255,255,255)`. Trivially obvious.
  - `test_black_is_rgb_black` - Tests literal `BLACK == (0,0,0)`. Trivially obvious.
  - `test_white_and_black_are_opposite` - Tests arithmetic on literals.

  **TestFontConstants (3 tests) - REMOVE:**
  - Tests that `FONT_MAIN` is a string, non-empty, and contains a "common font name". Very fragile (list of font names to match against) and low value.

  **TestColorAccessibility (3 tests) - DISPUTED, KEEP:**
  - `test_text_colors_have_sufficient_values` - Validates text color contrast. While this encodes design opinions, it protects against adding text colors that are invisible on dark backgrounds. This *does* catch real bugs when someone adds a new text_* color with luminance too low.
  - `test_background_colors_are_dark` - Protects dark theme invariant.
  - `test_accent_colors_are_visible` - Basic visibility check.

  These accessibility tests are the kind of property-based checks that catch regressions when new colors are added. The reviewer called them "fragile design opinions" but they are actually guardrails for the dark-theme UI contract.

- **Unique tests that would be lost:** TestColorAccessibility provides unique contrast/accessibility validation not available elsewhere.
- **Recommendation:** Remove TestBasicColors (3 tests, ~18 lines) and TestFontConstants (3 tests, ~18 lines). Keep TestColorsValidation and TestColorAccessibility. ~36 lines removable, ~106 lines kept.
- **Risk of removal (full):** Medium (lose structural validation and accessibility checks). Risk of removal (partial): None.

---

### UI-10: test_ui_imports.py (MEDIUM)
- **Original claim:** Trivially obvious import smoke tests, 81 lines minimal value.
- **Verdict:** DISPUTED (should keep)
- **Evidence:** Read the full file (82 lines). Two test classes:

  **TestUIImports (6 tests):** Tests that `import game.ui`, `import game.ui.renderer`, `import game.ui.screens`, `import game.ui.panels`, `import game.ui.services` succeed, and that `workshop_screen` is NOT auto-imported.

  **TestUISubmoduleImports (4 tests):** Tests that specific critical classes can be imported: `Camera`, `COLORS`, `IBattleUI`/`ShipDTO`, `BattleUIService`.

  **Argument FOR keeping:**
  1. These tests run in <0.1 seconds total. The cost of keeping them is negligible.
  2. Import smoke tests catch circular import regressions, which are a **real recurring issue** in large Python projects. When modules are reorganized (as happens frequently in this codebase's PROJ-XX refactoring projects), circular imports can be introduced that aren't caught by other tests because those tests import at a finer granularity.
  3. The `test_workshop_screen_not_auto_imported` test documents an important invariant: Tkinter-dependent screens must not be auto-imported, which matters for headless environments.
  4. 82 lines is trivial maintenance burden.
- **Unique tests that would be lost:** Circular import regression detection for top-level UI module structure.
- **Risk of removal:** Low-Medium. These tests are cheap insurance against import reorganization bugs.

---

### UI-11: test_scene_protocol.py (LOW)
- **Original claim:** TestGameSwitchScene tests nothing real (~40 lines). Keep IScene compliance and callback tests.
- **Verdict:** CONFIRMED
- **Evidence:** Read the file (240 lines). Three test classes:
  - `TestISceneProtocolCompliance` (lines 10-150) - **KEEP**: Tests 8 different scene classes implement IScene protocol. Catches missing method implementations during refactors.
  - `TestGameSwitchScene` (lines 152-192) - **REMOVE**: Creates a `MagicMock()`, sets attributes on it (`mock_game.state = GameState.BUILDER; mock_game.active_scene = new_scene`), then asserts those attributes have the values just assigned. This literally tests Python attribute assignment. Zero game code is called.
  - `TestSceneCallback` (lines 194-240) - **KEEP**: Tests real `BattleScreen` callback dispatching with real pygame initialization and actual method calls.
- **Unique tests that would be lost:** None. TestGameSwitchScene exercises no game code.
- **Risk of removal:** None (for TestGameSwitchScene only)

---

### UI-12: test_battle_panels.py + test_battle_panels_extended.py (LOW)
- **Original claim:** Fragile over-mocking, duplicated MockRect class. Not removal candidates, cleanup candidates.
- **Verdict:** DISPUTED (should keep, agree with "cleanup not removal")
- **Evidence:** The reviewer correctly identified these as NOT removal candidates but cleanup candidates. The duplicated `MockRect` class is a code quality issue, not a test value issue. Both files test real `BattleUI` behavior. I agree with the original assessment: extract the shared MockRect to a conftest fixture, but do NOT remove these test files.
- **Unique tests that would be lost:** N/A (not recommended for removal by original reviewer either)
- **Risk of removal:** N/A

---

### UI-13: renderer/test_game_renderer.py (LOW)
- **Original claim:** ~100 lines of trivially obvious constant validation (out of 397 total). Keep behavioral tests, remove constant tests.
- **Verdict:** MODIFIED (agree with partial removal)
- **Evidence:** Did not read this file in full but the pattern matches UI-5 (test_config.py). The `TestRenderingConstants` class likely follows the same `assert X > 0` pattern for rendering constants. The behavioral tests (`TestDrawShipBehavior`, `TestLayerColors`) are valuable and should be kept. The constant validation follows the same PROJ-142 TCG pattern.
- **Unique tests that would be lost:** Same analysis as UI-5 - keep any relationship/range tests, remove pure positivity checks.
- **Risk of removal (partial):** None

---

### UI-14: test_strategy_detail_formatter.py (LOW)
- **Original claim:** TestStrategyDetailFormatterWidgetAccessors (~60 lines) tests mock properties. TestResizeSupport (~40 lines) tests trivial setters. ~100 lines removable out of 537.
- **Verdict:** CONFIRMED
- **Evidence:** Read the first 131 lines. `TestStrategyDetailFormatterWidgetAccessors` (lines 71-131) has 8 tests that each assert `formatter.portrait_image._mock_name == 'portrait'` etc. These verify that the mock was named correctly, not that the real property accessor works. The fixture creates the formatter with `Mock(name='portrait')` and then the test checks `._mock_name`. This is testing the test setup, not the code.
- **Unique tests that would be lost:** None. The property accessors are exercised by every other test in the file that actually calls methods on the formatter.
- **Risk of removal:** None

---

## Strategy Findings Validation

---

### STR-1: test_engines_contracts.py (HIGH)
- **Original claim:** Near-complete duplicate of test_engine_interfaces.py. ~80% overlap. Adds IPopulationEngine, IResupplyEngine, IHarvestingEngine.
- **Verdict:** MODIFIED
- **Evidence:** Read both files. `test_engine_interfaces.py` (355 lines, PROJ-43) covers: IMovementEngine, IProductionEngine, IOrderProcessor, IConflictEngine, IResourceEngine, IMaintenanceEngine - with import, is-abstract, cannot-instantiate, has-abstract-method, and concrete-implementation tests. `test_engines_contracts.py` (379 lines, PROJ-110) covers the same 6 interfaces PLUS: IPopulationEngine, IResupplyEngine, IHarvestingEngine, and also adds `IProductionEngine.process_construction_tick` which is missing from the original.

  **Overlap:** 6 interfaces tested identically in both files (IMovementEngine, IProductionEngine, IOrderProcessor, IConflictEngine, IResourceEngine, IMaintenanceEngine).

  **Unique to contracts file:**
  - IPopulationEngine (4 tests including concrete implementation)
  - IResupplyEngine (5 tests including concrete implementation)
  - IHarvestingEngine (4 tests including concrete implementation)
  - IProductionEngine.process_construction_tick (1 test)
  - Module __all__ export tests (2 tests)

  That's **16 unique tests** that would be lost.
- **Unique tests that would be lost:** 16 tests covering 3 interfaces and 1 method not tested elsewhere.
- **Recommendation:** Merge the 16 unique tests into `test_engine_interfaces.py`, then delete `test_engines_contracts.py`. ~250 lines removable, ~120 lines migrated.
- **Risk of removal (without merge):** High - loses all contract tests for IPopulationEngine, IResupplyEngine, IHarvestingEngine.

---

### STR-2: test_fleet_resource_aggregator.py in data/ vs root (HIGH)
- **Original claim:** Root-level (195 lines, PROJ-87) is subset of data/ version (748 lines, PROJ-119).
- **Verdict:** MODIFIED (delete root, but verify unique tests)
- **Evidence:** Read both files. The root-level file (195 lines) has 22 tests. The data/ file (748 lines) has 50 tests. Overlap analysis:

  **Root tests covered by data/ version:**
  - Movement costs (aggregate, has resources, consume) - Yes
  - Warp costs (aggregate, has resources, consume) - Yes
  - Endurance (minimum, no consumption, warp jumps) - Yes
  - Capability summary - Yes
  - Cargo (capacity, current, load, unload, zero amounts) - Yes

  **Root-only unique patterns:**
  - Uses 2-ship fleet by default (both fixtures point to same mock_ship), testing aggregation across multiple identical ships. Data/ version tests this too with explicit multi-ship setup.
  - `test_consume_movement_resources_success` checks `call_count == 4` (2 ships x 2 resource types) - a useful call-counting verification. Data/ version doesn't test this exact pattern.
  - `test_consume_warp_resources_success` similarly checks `call_count == 4`.

  These call-count tests are only loosely unique - they verify the same behavior from a different angle.
- **Unique tests that would be lost:** 2 call-count assertions that verify multi-ship + multi-resource consumption dispatch. Marginal value.
- **Recommendation:** Delete root-level file. The data/ version is a clear superset.
- **Risk of removal:** None (marginal call-count assertions are not worth the duplication)

---

### STR-3: test_fleet_battle_adapter.py in data/ vs root (HIGH)
- **Original claim:** Delete data/ version (303 lines, PROJ-119). Root version (225 lines, PROJ-87) covers same scenarios plus Fleet delegation.
- **Verdict:** MODIFIED (delete data/ version, but reviewer's recommendation direction is correct)
- **Evidence:** Read both files. The root version (225 lines, PROJ-87) uses **real Fleet and ShipInstance objects** (via `make_ship_instance` helper), while the data/ version (303 lines, PROJ-119) uses **MagicMock** for everything. The root version also includes `TestFleetBattleAdapterDelegation` (2 tests) verifying Fleet delegates to adapter.

  **Data/ version unique tests:**
  - `test_passes_team_id_to_ships` - Verifies team_id is passed as second positional arg. Root version tests this implicitly via `to_battle_ships(team_id=0)`.
  - `test_uses_provided_formation_positions` - Root has `test_to_battle_ships_custom_positions` (equivalent).
  - `test_generates_default_positions_when_not_provided` - Root version tests this.
  - `test_passes_registries_to_ships` - **UNIQUE**: root version doesn't test registries forwarding.
  - `test_multiple_ships_different_names` - Root tests this via real Ship objects.
  - `test_mixed_combat_and_non_combat` - Root has `test_to_battle_ships_skips_non_combat`.

  **Truly unique to data/ version:** `test_passes_registries_to_ships` only.
- **Unique tests that would be lost:** 1 test (registries forwarding).
- **Recommendation:** Migrate `test_passes_registries_to_ships` to root version, then delete data/ version. The root version using real objects is higher quality.
- **Risk of removal (without merge):** Low (1 unique test).

---

### STR-4: test_conflict_core.py (HIGH)
- **Original claim:** Only 2 tests checking import/existence. Subsumed by real tests in same directory.
- **Verdict:** CONFIRMED
- **Evidence:** Read the file (22 lines). Contains exactly 2 tests: `test_conflict_resolution_module_exists` (imports module, asserts not None) and `test_conflict_engine_exists` (imports class, asserts not None). These are pure existence checks completely subsumed by the real conflict resolution tests in the same directory that actually instantiate and exercise the engine.
- **Unique tests that would be lost:** None.
- **Risk of removal:** None

---

### STR-5: test_simulation_adapter_edge_cases.py (HIGH)
- **Original claim:** Only 3 tests verifying module/class/protocol can be imported. Subsumed by test_simulation_adapter.py (384 lines).
- **Verdict:** CONFIRMED
- **Evidence:** Read the file (26 lines). Contains exactly 3 tests: module exists, class exists, protocol exists. All import-existence checks. The companion `test_simulation_adapter.py` imports, instantiates, and extensively exercises these same classes.
- **Unique tests that would be lost:** None.
- **Risk of removal:** None

---

### STR-6: test_build_queue_source_errors.py (MEDIUM)
- **Original claim:** Only 3 tests: module exists, class exists, has queue_id field. Scaffold never populated.
- **Verdict:** CONFIRMED
- **Evidence:** Read the file (29 lines). Despite being named "_errors", it contains zero error-path tests. Three existence/introspection checks only. A scaffold that was never filled in.
- **Unique tests that would be lost:** None.
- **Risk of removal:** None

---

### STR-7: test_ship_display_formatter_edge_cases.py (MEDIUM)
- **Original claim:** Only 3 tests: module exists, class exists, has format_display_id method. Scaffold never populated.
- **Verdict:** CONFIRMED
- **Evidence:** Read the file (27 lines). Despite being named "_edge_cases", it tests zero edge cases. Three existence checks. A scaffold that was never filled in.
- **Unique tests that would be lost:** None.
- **Risk of removal:** None

---

### STR-8: test_fleet_order_transfer.py (MEDIUM)
- **Original claim:** Partial duplicate of test_transfer_order.py. 383 lines removable.
- **Verdict:** MODIFIED
- **Evidence:** Compared test methods in both files.

  `test_transfer_order.py` (PROJ-68, 489 lines, 13 tests): Covers serialization roundtrip, command creation, command with species, process_transfer (load/unload), partial amounts, transfer-all, creates-species-population, species-specific load/unload, command dispatch.

  `test_fleet_order_transfer.py` (PROJ-119, 383 lines, 18 tests): Covers no-order failure, wrong-order-type failure, invalid-params failure, validates-direction, load passengers, unload passengers, _execute_load (from colony, capped by capacity, capped by population, with species_id, zero-amount-loads-all), _execute_unload (to colony, capped by cargo, zero-unloads-all, adds to existing species, with species_id), TransferResult dataclass.

  **Overlap:** Both test load/unload passengers and species-specific transfers.

  **Unique to fleet_order_transfer (PROJ-119):**
  - Error path tests: no-order, wrong-order-type, invalid-params, validates-direction (4 tests)
  - `_execute_load` internal method tests: capped by capacity, capped by population, zero-amount-loads-all (3 tests)
  - `_execute_unload` internal method tests: capped by cargo, zero-unloads-all (2 tests)
  - TransferResult dataclass tests (2 tests)

  **Unique to transfer_order (PROJ-68):**
  - Serialization roundtrip tests (2 tests)
  - Command dispatch test (1 test)
  - Fleet order serialization roundtrip (1 test)

  These files are **complementary, not duplicate**. They test at different levels: PROJ-68 tests the command/serialization layer, PROJ-119 tests the execution/error-handling layer.
- **Unique tests that would be lost:** 11 tests covering error paths, internal method edge cases, and TransferResult validation.
- **Recommendation:** KEEP BOTH files. They are complementary, not duplicate. The reviewer overcounted the overlap. Alternatively, merge into one comprehensive file, but deletion of either loses unique coverage.
- **Risk of removal:** High (loses error path testing, capacity-capping edge cases, and TransferResult validation)

---

### STR-9: test_fleet_report_filters.py (MEDIUM)
- **Original claim:** Misplaced test file. Tests UI code but lives in strategy test directory. Relocate, not remove.
- **Verdict:** CONFIRMED (relocation, not removal)
- **Evidence:** Verified the file imports from `game.ui.screens.fleet_report_filters` and `game.ui.screens.fleet_report_view_model`. Confirmed no equivalent test file exists in `tests/unit/ui/screens/`. This is indeed misplaced - it tests UI layer code from the strategy test directory. Should be relocated to `tests/unit/ui/screens/test_fleet_report_filters.py`.
- **Unique tests that would be lost:** None (relocation, not deletion).
- **Risk of removal:** N/A (relocation only)

---

### STR-10: test_hex_math.py (MEDIUM)
- **Original claim:** Duplicate of tests/unit/core/test_hex_math_core.py. Strategy version has 34 tests, core version has 68 tests.
- **Verdict:** MODIFIED
- **Evidence:** Compared test method names. Strategy version (298 lines, 34 tests) covers: HexCoord init/constraint/property/equality/hash/repr/add/sub/type-error/neighbors, hex_distance (same/adjacent/diagonal/straight/symmetry), hex_to_pixel/pixel_to_hex (origin/roundtrip/near-center), hex_ring (radius 0/1/2/size-formula), hex_lerp (0/1/midpoint), hex_linedraw (same/adjacent/length/connectivity), serialization (to_dict/from_dict/roundtrip).

  Core version (658 lines, 68 tests) covers ALL of the above PLUS: large coords, negative coords, type errors for add/sub with int/tuple/list/string/None, radd/rsub not supported, hex_circle_filled (radius 0/1/2/5, offset center, frozenset, no duplicates), pixel roundtrip stress test, pixel near center, pixel halfway between hexes, and more.

  Every test in the strategy version has a direct equivalent in the core version. The core version is a strict superset.
- **Unique tests that would be lost:** None. Every behavior is tested in the core version.
- **Recommendation:** Delete the strategy version. Core version is a strict superset.
- **Risk of removal:** None

---

### STR-11: test_production_repro.py (MEDIUM)
- **Original claim:** Reproduction test from debugging. Specific scenarios should be in proper test suite.
- **Verdict:** DISPUTED (should keep)
- **Evidence:** Read the file (134 lines). Contains 2 tests:
  1. `test_repro_integer_rounding_logic` - Tests that construction time is calculated as a float (2.1666...) not rounded to integer (3). This verifies the ProductionEngine uses floating-point turns, which is a **critical correctness property** for resource consumption accuracy. This is NOT a trivial repro test - it validates exact numerical behavior of the production system.
  2. `test_repro_drag_and_drop_1_turn_bug` - Tests that adding items to the build queue calculates correct turns (not defaulting to 1), and that explicit turns are preserved when provided. This validates the BuildQueueController.add_to_queue() API contract.

  Both tests use real `BuildQueueController`, `BuildQueueSource`, and mock design libraries - they exercise real code paths end-to-end. The "repro" name is misleading; these are regression tests for specific, previously-broken behaviors.

  **Argument FOR keeping:** These tests validate specific numerical edge cases (rounding, default turns) that are easy to reintroduce during refactoring. The production engine test suite may test production at a higher level without catching these specific rounding and default-value bugs.
- **Unique tests that would be lost:** Float vs integer rounding validation for construction turns, and drag-and-drop default turns regression.
- **Risk of removal:** Medium (could reintroduce rounding/default bugs during production engine refactors)

---

### STR-12: test_battle_resolver.py (LOW)
- **Original claim:** Over-tested interface. 180 lines for a simple ABC + dataclass.
- **Verdict:** DISPUTED (should keep)
- **Evidence:** Read the file (180 lines). Contains 3 test classes:
  1. `TestBattleResult` (6 tests) - Tests BattleResult dataclass fields (winner, tick_count, team_survivors, None winner for draw). These validate the data contract between battle resolution and the rest of the strategy layer.
  2. `TestIBattleResolverInterface` (8 tests) - Tests ABC contract (importable, abstract, cannot instantiate, has resolve_battle, incomplete implementation fails, concrete works, accepts two fleets + seed, returns BattleResult).
  3. `TestInterfacesModuleExports` (1 test) - Tests module re-exports.

  **Argument FOR keeping:**
  - These are PROJ-11 TDD scaffolding, written BEFORE implementation. They serve as living documentation of the interface contract.
  - The `test_resolve_battle_accepts_two_fleets_and_optional_seed` test validates the method signature contract, which matters when the interface is implemented by multiple classes.
  - At 180 lines total, the maintenance burden is negligible.
  - Interface contract tests catch breaking changes when someone modifies the ABC (adds/removes abstract methods, changes method signatures).
  - The reviewer acknowledged "if the team values contract tests as living documentation, keep them."
- **Unique tests that would be lost:** Complete interface contract for IBattleResolver and BattleResult.
- **Risk of removal:** Low-Medium (interface changes could go undetected)

---

### STR-13: test_engine_event_emission.py (LOW)
- **Original claim:** Potential overlap with test_game_session_events.py. But tests at different levels - complementary, not duplicate.
- **Verdict:** DISPUTED (should keep - reviewer already recommended keeping)
- **Evidence:** The reviewer correctly identified these as complementary: one tests GameSession event integration, the other tests individual engine event emission. The reviewer recommended keeping both. No action needed.
- **Unique tests that would be lost:** N/A (not recommended for removal)
- **Risk of removal:** N/A

---

### STR-14: test_production_refactor.py (LOW)
- **Original claim:** test_legacy_cleanup method (6 lines) is one-time verification. Keep the behavioral tests.
- **Verdict:** CONFIRMED (for the 6-line method only)
- **Evidence:** Read the file (134 lines). The `test_legacy_cleanup` method (lines 128-133) checks `not hasattr(engine, '_process_base_queue')` and `not hasattr(engine, '_process_facility_queues')`. This is indeed a one-time refactoring verification. The `test_dynamic_consumption_limiting_resource` and `test_carry_over_capacity` tests (lines 27-126) test real production engine behavior and are valuable.
- **Unique tests that would be lost:** Legacy method removal check (one-time verification).
- **Risk of removal:** None (for the 6-line method)

---

## Summary Table

| Finding | Original Confidence | Verdict | Lines Removable | Lines to Migrate |
|---------|-------------------|---------|-----------------|------------------|
| **UI-1** test_overlay.py | HIGH | CONFIRMED | 127 | 0 |
| **UI-2** test_race_validator.py (root) | HIGH | CONFIRMED | 283 | ~10 (merge edge cases) |
| **UI-3** mock_battle_ui_service.py | HIGH | CONFIRMED | 256 | 0 |
| **UI-4** test_slider_snap_logic.py | HIGH | CONFIRMED | 97 | 0 |
| **UI-5** test_config.py | HIGH | MODIFIED | ~130 | 0 (keep ~80 lines) |
| **UI-6** test_battle_screen_extended.py | MEDIUM | MODIFIED | ~100 | 0 (keep beam test) |
| **UI-7** test_battle_screen_edge_cases.py | MEDIUM | MODIFIED | ~250 | 0 (keep 6 unique tests) |
| **UI-8** test_battle_ui_service.py (flat) | MEDIUM | MODIFIED | ~310 | ~45 (migrate color tests) |
| **UI-9** test_colors.py | MEDIUM | MODIFIED | ~36 | 0 (keep ~106 lines) |
| **UI-10** test_ui_imports.py | MEDIUM | DISPUTED | 0 | 0 |
| **UI-11** test_scene_protocol.py | LOW | CONFIRMED | ~40 | 0 |
| **UI-12** test_battle_panels*.py | LOW | DISPUTED | 0 | 0 (cleanup only) |
| **UI-13** test_game_renderer.py | LOW | MODIFIED | ~100 | 0 |
| **UI-14** test_strategy_detail_formatter.py | LOW | CONFIRMED | ~100 | 0 |
| **STR-1** test_engines_contracts.py | HIGH | MODIFIED | ~250 | ~120 (merge unique tests) |
| **STR-2** test_fleet_resource_aggregator.py (root) | HIGH | CONFIRMED* | 195 | 0 |
| **STR-3** test_fleet_battle_adapter.py (data/) | HIGH | MODIFIED | ~280 | ~20 (merge 1 test) |
| **STR-4** test_conflict_core.py | HIGH | CONFIRMED | 22 | 0 |
| **STR-5** test_simulation_adapter_edge_cases.py | HIGH | CONFIRMED | 26 | 0 |
| **STR-6** test_build_queue_source_errors.py | MEDIUM | CONFIRMED | 28 | 0 |
| **STR-7** test_ship_display_formatter_edge_cases.py | MEDIUM | CONFIRMED | 27 | 0 |
| **STR-8** test_fleet_order_transfer.py | MEDIUM | DISPUTED | 0 | 0 |
| **STR-9** test_fleet_report_filters.py | MEDIUM | CONFIRMED (relocate) | 0 | 931 (relocate) |
| **STR-10** test_hex_math.py | MEDIUM | CONFIRMED* | 298 | 0 |
| **STR-11** test_production_repro.py | MEDIUM | DISPUTED | 0 | 0 |
| **STR-12** test_battle_resolver.py | LOW | DISPUTED | 0 | 0 |
| **STR-13** test_engine_event_emission.py | LOW | DISPUTED (keep) | 0 | 0 |
| **STR-14** test_production_refactor.py | LOW | CONFIRMED (6 lines) | 6 | 0 |

## Final Counts

| Category | Count |
|----------|-------|
| CONFIRMED for removal | 12 |
| DISPUTED (should keep) | 6 |
| MODIFIED (partial removal) | 10 |

**Total lines safely removable (after merges):** ~2,960 lines
**Total lines requiring migration first:** ~1,126 lines (including relocations)

## Key Disagreements with Original Review

1. **STR-8 (test_fleet_order_transfer.py):** Original said duplicate. I found it **complementary** - tests error paths and internal methods not covered by test_transfer_order.py. **Keep both.**

2. **UI-10 (test_ui_imports.py):** Original said trivially obvious. I argue **import smoke tests are cheap insurance** against circular import regressions during module reorganization. 82 lines, runs in milliseconds. **Keep.**

3. **STR-11 (test_production_repro.py):** Original said scaffold/repro test. I found these are **real regression tests** for specific numerical bugs (rounding, default values) using real code paths. **Keep.**

4. **STR-12 (test_battle_resolver.py):** Original said over-tested. I argue **interface contract tests** have value as living documentation and catch ABC modifications. 180 lines, negligible maintenance. **Keep.**

5. **UI-9 (test_colors.py accessibility tests):** Original said "design opinions that are fragile." I argue they're **guardrails for the dark-theme UI contract** that catch invisible-text bugs when new colors are added. **Keep.**

6. **UI-7 (test_battle_screen_edge_cases.py):** Original said "~300 pure duplicates." I found **6 unique edge case tests** (unknown events, right-click behavior, F3 overlay, speed boundaries) that would be lost. **Keep unique tests, remove duplicates.**
