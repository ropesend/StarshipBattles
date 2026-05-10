# Test Review Report: Agent 1 -- UI Strategy Screens

## Scope
- Source files reviewed: 60 files (18,096 LOC total)
  - Strategy core: strategy_renderer.py (1205), strategy_screen.py (648), strategy_window_manager.py (769), strategy_click_dispatcher.py (628), strategy_panel_manager.py (508), strategy_build_queue_manager.py (271), strategy_camera_nav.py (202), strategy_colonization.py (274), strategy_detail_fmt.py (557), strategy_detail_formatter.py (451), strategy_event_router.py (401), strategy_fleet_command_router.py (307), strategy_fleet_ops.py (216), strategy_game_state_manager.py (104), strategy_input_handler.py (203), strategy_menu_panel.py (103), strategy_superweapons.py (398), strategy_ui.py (406), strategy_ui_action_router.py (115)
  - Fleet: fleet_data_source.py (327), fleet_orders_window.py (8), fleet_report_filters.py (316), fleet_report_sidebar.py (530), fleet_report_view_model.py (182), fleet_report_window.py (370), fleet_selection_window.py (113)
  - Planet: planet_data_source.py (220), planet_list_filter_manager.py (127), planet_list_filters.py (307), planet_list_presets.py (201), planet_list_sidebar.py (255), planet_list_window.py (589), planet_selection_window.py (182), planet_abilities_window.py (228)
  - Star: star_data_source.py (123), star_list_filter_manager.py (85), star_list_filters.py (212), star_list_presets.py (123), star_list_sidebar.py (214), star_list_window.py (473)
  - Empire/Event: empire_build_queue_data_source.py (114), empire_build_queue_filter_manager.py (239), empire_build_queue_formatter.py (189), empire_build_queue_sidebar.py (234), empire_build_queue_viewmodel.py (294), empire_build_queue_window.py (559), empire_panel_window.py (501), event_log_data_source.py (178), event_log_sidebar.py (119), event_log_window.py (384)
  - Other: system_selection_window.py (111), transfer_dialog.py (782), orders_window.py (353)
  - Panels: strategy_widgets.py (189), system_tree_panel.py (576), empire_treasury_panel.py (323)
- Test files reviewed: 55 files (23,756 LOC total)
- Coverage data referenced: yes, from coverage.json

## Summary
- Test files reviewed: 55
- Source files reviewed: 60
- Tests flagged for removal: 14 (estimated LOC: 325)
- Tests flagged as happy-path-only: 8
- Source files with inadequate coverage: 14

---

## A. Tests Recommended for Removal

### A1. Duplicate elapsed-time/animation tests between renderer files
- **File:** `tests/unit/ui/screens/test_strategy_renderer_animation.py`
- **Test(s):** `TestRendererAnimationState.test_renderer_has_elapsed_time_initialized_to_zero`, `test_update_accumulates_delta_time`, `test_update_accumulates_over_multiple_calls`
- **Reason:** DUPLICATE_OF:tests/unit/ui/screens/test_strategy_renderer.py
- **Confidence:** HIGH
- **Evidence:** `test_strategy_renderer.py` lines 77-78 test `_elapsed_time == 0.0`, lines 97-106 test accumulation via `update()`. The animation file's tests at lines 18-32 are exact behavioral duplicates of the renderer init and update tests. The animation file's remaining tests (lines 46-57 constant check, lines 63-98 rotation) are unique and should stay.
- **Estimated LOC saved:** 20

### A2. Duplicate superweapon init/property tests
- **File:** `tests/unit/ui/test_superweapon_operations.py`
- **Test(s):** `TestSuperweaponOperationsInit.test_init_stores_scene_and_facade`, `test_properties_delegate_to_scene`
- **Reason:** DUPLICATE_OF:tests/unit/ui/screens/test_strategy_superweapons.py
- **Confidence:** HIGH
- **Evidence:** `test_strategy_superweapons.py` lines 66-101 test identical init storage and property delegation. Both import from `game.ui.screens.strategy_superweapons.SuperweaponOperations`. The `test_superweapon_operations.py` file tests the same class with the same assertions. Keep the `test_strategy_superweapons.py` version (more complete with fixtures), remove duplicate init/property tests from `test_superweapon_operations.py`.
- **Estimated LOC saved:** 25

### A3. Duplicate superweapon error-path tests
- **File:** `tests/unit/ui/test_superweapon_operations.py`
- **Test(s):** `TestImplodePlanetDesignation` (all 3 tests), `TestStellerateStarDesignation` (both tests), `TestOpenWarpDesignation.test_returns_error_if_fleet_lacks_ability`, `TestCloseWarpDesignation` (both tests), `TestDysonSphereDesignation.test_returns_error_if_fleet_lacks_ability`
- **Reason:** DUPLICATE_OF:tests/unit/ui/screens/test_strategy_superweapons.py
- **Confidence:** HIGH
- **Evidence:** `test_strategy_superweapons.py` lines 108-358 test all the same error paths with the same assertions (fleet lacks ability, no planet/system/warp at hex). The `test_strategy_superweapons.py` version also covers success paths (confirmation dialog, system picker) which the `test_superweapon_operations.py` version does not. The only unique tests in `test_superweapon_operations.py` are `TestSelfDestruct` (lines 239-280) -- these should be preserved.
- **Estimated LOC saved:** 120

### A4. Source-code-text-matching tests (brittle)
- **File:** `tests/unit/ui/screens/test_strategy_renderer.py`
- **Test(s):** `TestDrawGrid.test_draw_grid_skips_massive_hex_counts` (line 335), `TestDrawWarpLanes.test_draw_warp_lanes_viewport_culling_logic` (line 375)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** These tests use `inspect.getsource()` to assert that a string like `'80000'` or `'is_on_screen'` appears in source code. They don't exercise any behavior -- they just grep source text. If the implementation changes the variable name or threshold value, these tests break without any actual bug. Lines 343-345 and 378-381.
- **Estimated LOC saved:** 15

### A5. Source-code-text-matching tests (UI menu)
- **File:** `tests/unit/ui/screens/test_strategy_ui_menu.py`
- **Test(s):** `TestMenuButtonAttribute.test_no_btn_save_game_attribute` (line 93), `test_has_btn_menu_in_source` (line 99), `test_has_menu_panel_attribute_in_init` (line 106), `TestStrategyMenuPanelImport.test_import_exists` (line 367)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** These tests use `inspect.getsource()` to check that strings like `'btn_save_game'` don't exist or `'btn_menu'` does exist in source code. They test source text, not behavior. The actual functionality is already tested by the behavioral tests in the same file (e.g., toggle_menu_panel, btn_menu click handler). Lines 93-111 and 367-371.
- **Estimated LOC saved:** 30

### A6. Source-code-text-matching tests (planet selection)
- **File:** `tests/unit/ui/screens/test_planet_selection_window.py`
- **Test(s):** `TestPlanetSelectionWindowBtnAnyGuard.test_btn_any_guard_in_source` (line 67), `test_btn_any_conditional_creation_in_source` (line 77)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** These tests use `inspect.getsource()` to assert strings like `"if self.btn_any and self.btn_any.check_pressed()"` exist in source code. They verify source text patterns, not behavior. If the guard logic is refactored (e.g., to use `getattr` or extract a method), tests break despite correct behavior. Lines 67-86.
- **Estimated LOC saved:** 20

### A7. Trivial constant assertions
- **File:** `tests/unit/ui/screens/test_strategy_renderer_animation.py`
- **Test(s):** `TestWarpPointRotationConstant.test_rotation_speed_constant_exists` (line 48), `test_rotation_speed_is_positive` (line 53)
- **Reason:** TRIVIAL_CONSTANT
- **Confidence:** MEDIUM
- **Evidence:** Lines 48-57 assert `WARP_POINT_ROTATION_SPEED == 12.0` and `> 0`. The exact value 12.0 is an implementation detail with no invariant. The positivity check is slightly more useful but still trivial. If the designer changes the rotation speed to 15.0, the test fails for no real reason.
- **Estimated LOC saved:** 10

### A8. Trivial constant assertions in menu panel
- **File:** `tests/unit/ui/screens/test_strategy_menu_panel.py`
- **Test(s):** `TestMenuPanelConstants.test_button_count` (line 43), `test_menu_buttons_length` (line 46), `test_menu_buttons_labels` (line 49), `test_menu_buttons_option_ids` (line 55), `test_option_id_strings_are_unique` (line 78)
- **Reason:** TRIVIAL_CONSTANT
- **Confidence:** MEDIUM
- **Evidence:** Lines 43-79. These assert `BUTTON_COUNT == 6`, `len(MENU_BUTTONS) == 6`, and check exact label strings. If a 7th menu option is added, these tests all fail. The uniqueness test (line 78) has some value as an invariant guard. The panel width/height tests (lines 62-75) are more useful as they verify arithmetic consistency. Consider keeping uniqueness + panel sizing, removing exact count/label checks.
- **Estimated LOC saved:** 25

### A9. Trivial property delegation tests in renderer
- **File:** `tests/unit/ui/screens/test_strategy_renderer.py`
- **Test(s):** `TestPropertyAccessors` class (lines 113-148): `test_camera_property`, `test_galaxy_property`, `test_systems_property`, `test_empires_property`, `test_hex_size_property`, `test_screen_width_property`, `test_screen_height_property`, `test_empire_assets_property`
- **Reason:** OVER_MOCKED
- **Confidence:** LOW
- **Evidence:** These 8 tests each assert that `renderer.property is mock_scene.property`. Since the renderer stores `self.scene` and these are all `@property` returning `self.scene.X`, these tests only verify Python property syntax works. However, they do document the API contract, so this is a borderline call.
- **Estimated LOC saved:** 35

### A10. Strategy screen edge case tests with no real logic
- **File:** `tests/unit/ui/screens/test_strategy_screen.py`
- **Test(s):** `TestEdgeCases.test_detail_zoom_level_boundary_values` (line 776), `test_hex_size_boundary` (line 789), `test_turn_processing_flag_boundary` (line 738)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** These tests set a plain attribute and assert it was set (e.g., `screen.hex_size = 1; assert screen.hex_size == 1`). They test Python attribute assignment, not game logic. There is no validation, no clamping, no side effects. Lines 738-799.
- **Estimated LOC saved:** 25

---

## B. Tests That Are Happy-Path-Only

### B1. Build queue manager -- only success paths for open/close
- **File:** `tests/unit/ui/screens/test_strategy_build_queue_manager.py`
- **Test(s):** `TestOnBuildYardClick`, `TestOnFleetBuildClick`, `TestOnNavigateToHexBuild`
- **What's tested:** Opening build queue for owned planet, fleet with shipyard, valid source
- **What's missing:** Enemy planet (not owner_id match), fleet without shipyard, planet with no build yard facility, concurrent build queue open attempts, exception handling from BuildQueueScreen constructor
- **Source method(s) affected:** `game/ui/screens/strategy_build_queue_manager.py:on_build_yard_click` (line ~50-90), `on_fleet_build_click` (line ~95-130)
- **Priority:** LOW

### B2. Strategy colonization -- only success and empty-result paths
- **File:** `tests/unit/ui/screens/test_strategy_colonization.py`
- **Test(s):** `TestColonizationSystemZone`
- **What's tested:** Finding Dyson Sphere via zone, empty zone result
- **What's missing:** Multiple candidate planets requiring prompt, validation failure (can_colonize returns invalid), fleet with no colonization pods, planet already colonized, exception from facade
- **Source method(s) affected:** `game/ui/screens/strategy_colonization.py:on_colonize_click` (lines 50-110)
- **Priority:** MEDIUM (colonization is a critical game action)

### B3. Strategy game state manager -- no error/exception paths
- **File:** `tests/unit/ui/screens/test_strategy_game_state_manager.py`
- **Test(s):** `TestProcessFullTurn`
- **What's tested:** Normal turn processing, auto-save, event log opening
- **What's missing:** Exception during process_turn (facade throws), auto-save failure (save returns False), concurrent advance_turn calls, turn processing with no empires
- **Source method(s) affected:** `game/ui/screens/strategy_game_state_manager.py:_process_full_turn` (lines 40-90)
- **Priority:** HIGH (turn processing is critical)

### B4. Transfer dialog -- limited resource transfer scenarios
- **File:** `tests/unit/ui/screens/test_transfer_dialog.py`
- **Test(s):** `TestTransferDialog`
- **What's tested:** Init population, source change, grid building, confirm dispatch
- **What's missing:** Transfer exceeding capacity, zero-amount transfers, invalid source/target combinations, source and target same entity, confirm with no pending transfers, cancel behavior, error from facade.handle_command
- **Source method(s) affected:** `game/ui/screens/transfer_dialog.py:_on_confirm` (line ~600), `_on_source_changed` (line ~300)
- **Priority:** HIGH (transfer_dialog.py is 782 LOC with only 75.4% coverage)

### B5. Fleet report window -- no error handling tests
- **File:** `tests/unit/ui/screens/test_fleet_report_window.py`
- **Test(s):** All tests in this file
- **What's tested:** Window creation, ship display, selection, filtering
- **What's missing:** Empty fleet (no ships), fleet with destroyed ships, window resize during operation, concurrent window opens, ship data with missing fields
- **Source method(s) affected:** `game/ui/screens/fleet_report_window.py` (48.0% coverage, 179 stmts)
- **Priority:** MEDIUM

### B6. Event log window -- no edge case tests
- **File:** `tests/unit/ui/screens/test_event_log_window.py`
- **Test(s):** All tests
- **What's tested:** Window creation, event display, filtering
- **What's missing:** Empty event list, events with missing fields, very long event text, scrolling behavior, window resize
- **Source method(s) affected:** `game/ui/screens/event_log_window.py` (53.0% coverage, 151 stmts)
- **Priority:** LOW

### B7. Empire build queue window -- limited state transition tests
- **File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
- **Test(s):** Various window state tests
- **What's tested:** Source list, row rendering, selection, batch operations
- **What's missing:** Rapid source switching, build rate edge cases (zero rate, negative rate), design library failures, concurrent modification of queue during display
- **Source method(s) affected:** `game/ui/screens/empire_build_queue_window.py` (70.2% coverage, 258 stmts)
- **Priority:** MEDIUM

### B8. Strategy detail formatter -- show_detail always with valid objects
- **File:** `tests/unit/ui/screens/test_strategy_detail_formatter.py`
- **Test(s):** `TestShowDetailedReport`
- **What's tested:** Show detail with system, fleet, None
- **What's missing:** Show detail with planet (owned and unowned), star (direct selection), warp point, storm, sector environment; planet with zero population, planet with no facilities, fleet with damaged ships
- **Source method(s) affected:** `game/ui/screens/strategy_detail_formatter.py:show_detailed_report` (67.6% coverage, 238 stmts)
- **Priority:** MEDIUM

---

## C. Source Code with Inadequate Coverage

### C1. planet_abilities_window.py
- **Source file:** `game/ui/screens/planet_abilities_window.py` (228 LOC)
- **Coverage:** 0.0% (0/119 stmts covered)
- **Untested areas:** Entire class: `__init__`, `_build_ui`, `_discover_abilities`, `_create_row`, `process_event` (toggle button handling), `refresh`
- **Risk:** Toggle ability UI could silently break -- user cannot activate/deactivate planetary shields, stellar stabilizers, etc.
- **Priority:** HIGH

### C2. planet_list_sidebar.py
- **Source file:** `game/ui/screens/planet_list_sidebar.py` (255 LOC)
- **Coverage:** 3.3% (3/90 stmts covered)
- **Untested areas:** `build_sidebar()` function body -- all filter widget creation, slider ranges, preset dropdown, type/owner checkboxes
- **Risk:** Planet list filter UI could fail to build or produce incorrect filter ranges
- **Priority:** MEDIUM

### C3. star_list_sidebar.py
- **Source file:** `game/ui/screens/star_list_sidebar.py` (214 LOC)
- **Coverage:** 5.2% (4/77 stmts covered)
- **Untested areas:** `build_sidebar()` function body -- star-specific filter widgets, spectral type checkboxes, mass/temp sliders
- **Risk:** Star list filter UI could fail to initialize
- **Priority:** MEDIUM

### C4. star_list_window.py
- **Source file:** `game/ui/screens/star_list_window.py` (473 LOC)
- **Coverage:** 13.9% (36/259 stmts covered)
- **Untested areas:** `_build_ui`, `_apply_filters`, `_on_sort`, `_on_row_selected`, `_on_preset_changed`, `_export_to_csv`, `handle_resize`
- **Risk:** Star list window could crash on open, sort, filter, or selection
- **Priority:** HIGH

### C5. planet_list_window.py
- **Source file:** `game/ui/screens/planet_list_window.py` (589 LOC)
- **Coverage:** 20.7% (69/333 stmts covered)
- **Untested areas:** `_build_ui`, `_apply_filters`, `_on_sort`, `_on_row_selected`, `_on_preset_changed`, `_on_column_toggle`, `handle_resize`, event handling
- **Risk:** Planet list window could crash on interaction. This is a large, complex file at only 20.7% coverage.
- **Priority:** HIGH

### C6. empire_panel_window.py
- **Source file:** `game/ui/screens/empire_panel_window.py` (501 LOC)
- **Coverage:** 20.9% (36/172 stmts covered)
- **Untested areas:** `_build_ui`, `_populate_data`, `_update_economy_tab`, `_update_military_tab`, `_update_research_tab`, tab switching, data refresh
- **Risk:** Empire overview panel could show stale or incorrect data; tab switching could crash
- **Priority:** HIGH

### C7. star_data_source.py
- **Source file:** `game/ui/screens/star_data_source.py` (123 LOC)
- **Coverage:** 22.7% (17/75 stmts covered)
- **Untested areas:** `get_cell_value`, `get_cell_image`, `_extract_value`, `_get_star_icon`, icon caching
- **Risk:** Star table cells could show wrong values or missing icons
- **Priority:** MEDIUM

### C8. system_tree_panel.py
- **Source file:** `game/ui/panels/system_tree_panel.py` (576 LOC)
- **Coverage:** 26.4% (82/311 stmts covered)
- **Untested areas:** Tree node expansion, planet/fleet node rendering, selection callbacks, right-click context menus, tree rebuild on turn change
- **Risk:** System detail panel tree could fail to expand, show wrong hierarchy, or crash on selection
- **Priority:** MEDIUM

### C9. strategy_camera_nav.py
- **Source file:** `game/ui/screens/strategy_camera_nav.py` (202 LOC)
- **Coverage:** 27.1% (26/96 stmts covered)
- **Untested areas:** `center_on`, `center_on_hex`, `zoom_to_system`, `zoom_to_galaxy`, `cycle_selection` (the actual cycling logic), `_resolve_global_hex`
- **Risk:** Camera navigation could fail to center on objects or zoom to correct levels. cycle_selection logic handles colony/fleet iteration with wrap-around.
- **Priority:** MEDIUM

### C10. fleet_selection_window.py
- **Source file:** `game/ui/screens/fleet_selection_window.py` (113 LOC)
- **Coverage:** 30.3% (10/33 stmts covered)
- **Untested areas:** `_build_ui`, `process_event` (selection handling), callback invocation
- **Risk:** Fleet selection dialog could crash or fail to invoke callback on selection
- **Priority:** LOW

### C11. strategy_renderer.py
- **Source file:** `game/ui/screens/strategy_renderer.py` (1205 LOC)
- **Coverage:** 36.0% (247/687 stmts covered)
- **Untested areas:** `_draw_system_details` (planet rendering, orbit rings, name labels), `_draw_fleets` (fleet icon rendering, selection highlight), `_draw_grid` (actual hex drawing), `_draw_move_preview` (path drawing, fuel range), fleet tooltip generation
- **Risk:** At 36% coverage for a 1205-LOC rendering file, many visual rendering paths are untested. However, rendering code is inherently difficult to unit test meaningfully.
- **Priority:** LOW (rendering code -- visual bugs caught by play-testing, not unit tests)

### C12. strategy_event_router.py
- **Source file:** `game/ui/screens/strategy_event_router.py` (401 LOC)
- **Coverage:** 40.3% (85/211 stmts covered)
- **Untested areas:** `handle_click` full dispatch (beyond blocking check), `_dispatch_map_click`, `_handle_sidebar_click`, right-click context menu, double-click handling
- **Risk:** Map clicks could fail to dispatch to correct handlers or produce wrong behavior for sidebar interactions
- **Priority:** MEDIUM

### C13. star_list_filter_manager.py
- **Source file:** `game/ui/screens/star_list_filter_manager.py` (85 LOC)
- **Coverage:** 47.4% (9/19 stmts covered)
- **Untested areas:** `apply_filters`, `reset_filters` -- the actual filtering logic
- **Risk:** Star list filters could silently fail to filter
- **Priority:** LOW

### C14. planet_selection_window.py
- **Source file:** `game/ui/screens/planet_selection_window.py` (182 LOC)
- **Coverage:** 17.8% (13/73 stmts covered)
- **Untested areas:** `_build_ui`, `update` (button press handling), `process_event`, selection callback, "Any" button behavior
- **Risk:** Planet selection dialogs (used for colonization targeting, superweapon targeting) could fail to present options or invoke callbacks
- **Priority:** MEDIUM

---

## D. Cross-Domain Observations

1. **test_superweapon_operations.py vs test_strategy_superweapons.py overlap:** The file `tests/unit/ui/test_superweapon_operations.py` (393 LOC) substantially overlaps with `tests/unit/ui/screens/test_strategy_superweapons.py` (544 LOC). Both test `SuperweaponOperations` from the same source module. The `test_strategy_superweapons.py` file is the more complete version, covering success paths (confirmation dialogs, system pickers). The `test_superweapon_operations.py` file should be consolidated: keep only its unique `TestSelfDestruct` tests (lines 239-280) and merge them into the screens-level file, then delete the duplicate file. Estimated savings: ~300 LOC.

2. **Source-text-grepping antipattern:** Multiple test files use `inspect.getsource()` to assert that specific strings exist in source code (test_strategy_renderer.py, test_strategy_ui_menu.py, test_planet_selection_window.py). This is a brittle testing pattern that tests implementation text rather than behavior. These tests will break on any refactoring even if behavior is preserved. They should be replaced with behavioral tests or removed.

3. **Consistent gap in window lifecycle tests:** Nearly all window classes (planet_list_window, star_list_window, empire_panel_window, fleet_report_window) have tests for creation/init but lack tests for `process_event`, `handle_resize`, and close/cleanup. This is a systematic gap across the UI window subsystem.

4. **planet_abilities_window.py at 0% coverage** is the single highest-risk gap. This is a user-facing feature (ability toggles for planetary shields, stellar stabilizers) with zero test coverage. Even a basic "window creates without crash" test would be valuable.
