# Validator 3: UI Claims Validation Report

**Claims Reviewed:** 40
**Confirmed:** 30
**Downgraded:** 8
**Rejected:** 2

---

## Claim 1: `test_strategy_renderer_animation.py` 3 duplicate elapsed-time tests
**Verdict: CONFIRMED**

The animation file (lines 18-42) tests `_elapsed_time` initialization, single update accumulation, and multi-update accumulation. The canonical `test_strategy_renderer.py` (lines 76-78, 97-106) has `test_init_initializes_elapsed_time`, `test_update_increments_elapsed_time`, and `test_update_accumulates_elapsed_time` which test identical behavior. The animation file's `test_update_handles_large_dt` and `test_update_handles_zero_dt` are trivially obvious edge cases (passing 1.0 and 0.0 to addition). True duplicates.

---

## Claim 2: `test_superweapon_operations.py` init/property tests -- DUPLICATE_OF test_strategy_superweapons.py
**Verdict: CONFIRMED**

Both files test `SuperweaponOperations.__init__` storing scene/facade references and property delegation (camera, hex_size, galaxy). The canonical `test_strategy_superweapons.py` has `TestSuperweaponOperationsInit.test_init_stores_references` (line 66-73) and `TestPropertyAccessors` (lines 76-101) with systems, camera, hex_size, galaxy -- superset of what the operations file tests. The operations file's `TestSuperweaponOperationsInit` (lines 61-87) is fully duplicated.

---

## Claim 3: `test_superweapon_operations.py` 10+ error-path tests -- DUPLICATE_OF test_strategy_superweapons.py, check TestSelfDestruct
**Verdict: DOWNGRADED to MEDIUM**

The error-path tests in `test_superweapon_operations.py` (implode_planet no fleet/no ability/no planet, stellerate no ability/no system, open_warp no ability, close_warp no ability/no warp point, dyson sphere no ability) overlap with `test_strategy_superweapons.py` which tests the same error paths plus success paths. However, `test_superweapon_operations.py` also has unique tests: `TestHelperMethods` (lines 284-337) testing `_get_system_at_hex` delegation and `_get_warp_point_at_hex` with matching/no-system cases, plus `TestConfirmationDialogs` (lines 340-393) testing `_show_confirmation`, `_show_system_picker`, and `_show_ship_picker` delegation. These helper/dialog tests are NOT duplicated in the canonical file. The `TestSelfDestruct` class (lines 239-281) overlaps with `TestSelfDestructWorkflow` in the canonical. Recommendation: remove the duplicate error-path tests but KEEP `TestHelperMethods` and `TestConfirmationDialogs`.

---

## Claim 4: `test_strategy_renderer.py` 2 source-code-text-matching tests using inspect.getsource()
**Verdict: CONFIRMED**

Lines 343-345 check `inspect.getsource(StrategyRenderer._draw_grid)` for the string `'80000'`, and lines 379-381 check `inspect.getsource(StrategyRenderer._draw_warp_lanes)` for `'is_on_screen'`. These test source code text, not runtime behavior. If the constant name changes or code is refactored, the test breaks even if behavior is correct. Classic TESTS_NOTHING_REAL pattern.

---

## Claim 5: `test_strategy_ui_menu.py` 4 source-text-matching tests
**Verdict: CONFIRMED**

`TestMenuButtonAttribute` (lines 90-112) contains 3 tests using `inspect.getsource()`:
- `test_no_btn_save_game_attribute` checks source for absence of `'btn_save_game'`
- `test_has_btn_menu_in_source` checks source for `'btn_menu'`
- `test_has_menu_panel_attribute_in_init` checks `__init__` source for `'menu_panel'`

Plus `TestStrategyMenuPanelImport.test_import_exists` (line 367-371) checks source text for an import statement. All 4 test source text rather than runtime behavior.

---

## Claim 6: `test_planet_selection_window.py` 2 source-text-matching tests (lines 67-86)
**Verdict: CONFIRMED**

`TestPlanetSelectionWindowBtnAnyGuard` (lines 64-86) has:
- `test_btn_any_guard_in_source` checks `inspect.getsource(update)` for exact string `"if self.btn_any and self.btn_any.check_pressed()"`
- `test_btn_any_conditional_creation_in_source` checks `inspect.getsource(__init__)` for `"self.btn_any = None"` and `"if show_any_button:"`

These test source text, not behavior. The tests above them (`TestPlanetSelectionWindowParameters`, lines 25-62) test actual `inspect.signature` which is a borderline but defensible way to test API contracts. But the guard tests are pure source matching. Confirmed for lines 67-86 only.

---

## Claim 7: `test_strategy_renderer_animation.py` 2 rotation constant tests (lines 48-57) -- TRIVIAL_CONSTANT
**Verdict: CONFIRMED**

`test_rotation_speed_constant_exists` asserts `WARP_POINT_ROTATION_SPEED == 12.0` and `test_rotation_speed_is_positive` asserts `> 0`. The second is redundant given the first. These are trivial constant assertions that provide near-zero regression protection.

---

## Claim 8: `test_strategy_menu_panel.py` 5 constant tests (lines 43-79) -- TRIVIAL_CONSTANT
**Verdict: DOWNGRADED to LOW**

The constant tests here (lines 43-79) check `BUTTON_COUNT == 6`, `len(MENU_BUTTONS) == 6`, button labels match expected list, option IDs match expected list, panel width/height formulas, and option ID uniqueness. While individual constant checks are trivial, taken together they form a coherent regression guard: if someone adds/removes a menu button, the test catches it. The label and option ID ordering tests are particularly valuable -- they verify the menu structure hasn't accidentally changed. The width/height formula tests are computed from other constants, which validates internal consistency. I'd keep these. Not high value, but not zero value either.

---

## Claim 9: `test_strategy_screen.py` 3 edge case tests (lines 738-799) -- TESTS_NOTHING_REAL
**Verdict: CONFIRMED**

- `test_turn_processing_flag_boundary` (738-751): sets `screen.turn_processing = True`, asserts it's True. Pure set-then-assert.
- `test_detail_zoom_level_boundary_values` (776-786): sets `screen.detail_zoom_level = 0.1`, asserts it's 0.1. Same pattern.
- `test_hex_size_boundary` (788-799): sets `screen.hex_size = 1`, asserts it's 1.

However, `test_cycle_selection_with_single_colony` (753-763) and `test_cycle_selection_negative_direction` (765-774) are NOT set-then-assert -- they call real methods and verify delegation. Only 3 of the 5 tests in this range are TESTS_NOTHING_REAL. The claim says "3 edge case tests" which correctly identifies `test_turn_processing_flag_boundary`, `test_detail_zoom_level_boundary_values`, and `test_hex_size_boundary`. Confirmed.

---

## Claim 10: `test_json_diff.py` -- ALL tests reimplement logic locally, ZERO imports from game.*
**Verdict: CONFIRMED**

I verified: zero `from game.*` or `import game.*` in this file. Every test class defines its own method (`compute_json_diff`, `mark_all_paths`, `path_is_parent_of`) as class methods, then tests those local implementations. `TestDiffResultConstants` tests hardcoded string lists -- not even local reimplementation, just testing Python string equality. None of these tests exercise any production code.

---

## Claim 11: `test_ui_logic.py` -- Same reimplementation pattern
**Verdict: CONFIRMED**

Zero game imports. `TestDiffColorSelection` defines `get_diff_color` locally. `TestScrollOffsetCalculations` defines `clamp_scroll` locally. `TestDiffStatistics` defines `calculate_diff_stats` locally. All tests verify these local implementations only.

---

## Claim 12: `test_viewer_ui.py` -- Same reimplementation pattern
**Verdict: CONFIRMED**

Zero game imports. `TestLineRenderingCalculations` defines `calculate_visible_lines` locally. `TestIndentLevelCalculation` defines `get_indent_level` locally. `TestPanelVisibilityToggle` tests `not visible` (Python boolean logic). `TestDualPanelSync` tests dict.get and variable assignment. `TestKeyboardNavigation` defines `handle_key` locally. None exercise production code.

---

## Claim 13: `test_galaxy_test_screen.py` init tests -- bypass __init__, set attr, assert attr
**Verdict: CONFIRMED**

`TestGalaxyTestScreenInit` (lines 80-143) patches `__init__`, then does:
- `screen.screen_width = 1920; assert screen.screen_width == 1920`
- `screen.on_close_callback = callback; assert screen.on_close_callback is callback`
- `screen.mode = GalaxyTestScreen.MODE_MENU; assert screen.mode == GalaxyTestScreen.MODE_MENU`

Pure set-then-assert, testing Python attribute assignment.

Also: `TestCameraSetup` (217-231), `TestFPSTracking` (257-281) -- same pattern. All confirmed.

---

## Claim 14: `test_galaxy_test_screen.py` import/constant tests -- TRIVIAL_CONSTANT/SCAFFOLD
**Verdict: CONFIRMED**

`TestGalaxyTestConstants` (14-57): tests `SIDEBAR_WIDTH is not None`, `isinstance(SIDEBAR_WIDTH, (int, float))`, `SIDEBAR_WIDTH > 0` -- trivially obvious for any constant. `TestGalaxyTestScreenImport` (61-77): `assert GalaxyTestScreen is not None`. `TestModeSwitching` (182-213): `assert isinstance(GalaxyTestScreen.MODE_MENU, str)`, `len(set(modes)) == 3`. `TestGalaxyModeHelper`/`TestSystemModeHelper` (236-253): `assert GalaxyModeHelper is not None`.

However, the `TestClearUI` class (147-177) tests `_clear_ui()` which actually calls the real method and verifies `kill()` is called on elements and the list is emptied. This is a real behavioral test. Recommendation: remove the scaffold/constant tests but KEEP `TestClearUI`.

---

## Claim 15: `test_camera_navigator.py` test_center_on_hex_method_exists -- TRIVIAL_CONSTANT
**Verdict: CONFIRMED**

Line 48-50: `assert hasattr(CameraNavigator, 'center_on_hex')`. This is a pure existence check. The other two tests in the class (`test_center_on_hex_sets_camera_position` and `test_center_on_hex_origin`) are real behavioral tests that should be kept. Only the existence check is trivial.

---

## Claim 16: `test_keybindings_scene.py` test_game_state_keybindings_exists -- TRIVIAL_CONSTANT
**Verdict: CONFIRMED**

Lines 285-289: `assert hasattr(GameState, 'KEYBINDINGS'); assert GameState.KEYBINDINGS == 10`. Tests that a constant exists and has a specific value. If someone changes the enum value, this would break, but it's testing a magic number, not behavior. However, the rest of the file (test_scene_creates_without_error, test_scene_has_iscene_methods, etc.) appears to have substantial behavioral tests. Only this one test is trivial.

---

## Claim 17: `test_menu_scene.py` test_bg_color_constant -- TRIVIAL_CONSTANT
**Verdict: CONFIRMED**

Line 252-256: `assert hasattr(MenuScene, 'BG_COLOR'); assert MenuScene.BG_COLOR == (20, 20, 30)`. Trivial constant assertion. The rest of the file has real behavioral tests.

---

## Claim 18: `tests/unit/ui/mocks/__init__.py` -- DEAD_CODE (empty module)
**Verdict: CONFIRMED**

File contains only a docstring and `__all__ = []`. No classes, no functions, no imports. No other file imports from this module. Dead code.

---

## Claim 19: 11 import-only scaffold tests across 11 files -- SCAFFOLD_ONLY
**Verdict: DOWNGRADED -- need individual verification**

The claim bundles 11 files but doesn't name them all. I cannot verify "each has other tests that import the class" without knowing the full list. From what I've seen, many files have import-only tests (e.g., `test_panel_can_be_imported` in design_report_panel.py, planet_report_panel.py, design_stats_panel.py, galaxy_test_screen.py). These ARE scaffold tests and individually removable. However, blanket confirmation of "11 files" without seeing the full list is irresponsible. Downgraded -- the pattern is real but needs individual file verification.

---

## Claim 20: `test_design_report_panel.py` ~12 set-then-assert tests -- TESTS_NOTHING_REAL
**Verdict: CONFIRMED**

`TestDesignReportPanelInit` (lines 48-118): Every test patches `__init__`, then sets an attribute and asserts it (`panel.manager = manager; assert panel.manager is manager`). This is testing Python attribute assignment, not panel behavior.

`TestShowPlaceholder` (lines 122-203): Most tests are set-then-assert. `test_show_placeholder_logic_clears_ship` literally does `panel.current_ship = None; assert panel.current_ship is None`. `test_show_placeholder_logic_kills_stats` reimplements the logic inline rather than calling the method.

However, `TestUpdateDesign` (lines 206-413) calls the REAL `panel.update_design(ship)` method and verifies its side effects. These are legitimate behavioral tests. `TestUpdatePortrait` (416-452) calls the real `_update_portrait` method. `TestPanelKill` (484-531) calls the real `kill()` method. `TestWidthRequired` (457-480) calls real `get_width_required()`.

Recommendation: ~12 set-then-assert tests from Init/ShowPlaceholder are removable. The update_design, portrait, kill, and width tests should be KEPT. Confirmed for the set-then-assert subset.

---

## Claim 21: `test_planet_report_panel.py` ~11 set-then-assert tests -- TESTS_NOTHING_REAL
**Verdict: CONFIRMED**

`TestPlanetReportPanelInit` (lines 77-137): 5 tests all patch __init__, set attribute, assert attribute. `TestUpdatePlanet` (lines 142-190): `test_update_planet_sets_planet` sets `panel.planet = new_planet; assert panel.planet is new_planet`. `test_update_planet_sets_production_rates` same pattern. `test_detail_text_has_rebuild_method` calls `MagicMock().rebuild()` and asserts it was called -- testing mock behavior.

`TestComplexesList` (194-237): `test_complexes_container_none_check` writes inline `if not panel.complexes_container: result = "early_return"` and asserts result -- reimplemented logic. `test_complex_items_is_list` is set-then-assert.

However, the file also has legitimate tests: `TestComputePlanetProduction` (421-451) calls real `compute_planet_production()`. `TestGetHarvesterInfo` (456-496) calls real `_get_harvester_info()`. `TestNumberFormatting` (242-268) calls real `format_compact_number()`. `TestPortrait` (301-333) calls real `_update_portrait()`. `TestHeightRequired` (338-364) calls real `get_height_required()`. `TestPanelKill` (369-416) calls real `kill()`. `_update_complexes_list` (198-209) calls the real method and correctly handles None. `_update_resource_grid` (287-298) calls real method.

Confirmed for the set-then-assert subset (~11 tests). The real behavioral tests should be kept.

---

## Claim 22: `test_design_stats_panel.py` stat calculation + formatting tests -- test MagicMock attrs not real panel
**Verdict: CONFIRMED**

`TestDesignStatsPanelStatCalculation` (lines 188-212): Creates a mock ship, sets `ship.mass = 175.5`, then asserts `ship.mass == 175.5`. This tests MagicMock attribute storage, not any panel logic.

`TestDesignStatsPanelFormatting` (215-243): Tests Python f-string formatting (`f"{ship.mass:.0f}"`) on mock attributes. This tests Python string formatting, not the panel.

---

## Claim 23: `test_design_stats_panel.py` rows_map + layer_status tests -- set-then-assert pattern
**Verdict: CONFIRMED**

`TestDesignStatsPanelRowsMap` (246-273): patches __init__, sets `panel.rows_map = {}`, asserts it's a dict. Sets `panel.rows_map["mass"] = row`, asserts it's there.

`TestDesignStatsPanelLayerStatus` (276-299): patches __init__, sets `panel.layer_rows = []`, asserts it's a list. Sets `panel.current_logistics_keys = set()`, asserts it's a set.

`TestDesignStatsPanelInit` (143-186): patches __init__, sets attributes, asserts them.

However, `TestStatRow` (59-139) tests REAL StatRow methods (update, set_visible) with proper caching behavior. These are legitimate. Keep StatRow tests, remove the set-then-assert init/rowsmap/layer tests.

---

## Claim 24: `test_ship_stats_renderer.py` 6 color/priority constant tests -- TRIVIAL_CONSTANT
**Verdict: DOWNGRADED to LOW**

`TestResourceColors` (305-324): Asserts `RESOURCE_COLORS["fuel"] == (255, 165, 0)` etc. -- 3 tests.
`TestResourceOrderPriority` (329-348): Asserts `RESOURCE_ORDER_PRIORITY["fuel"] == 0` etc. -- 3 tests.

These are trivial constant assertions. However, the rest of the file has substantial real tests: `TestDrawStatBar` tests actual drawing function with various percentages, `TestGetHpBarColor` tests real color logic with thresholds, `TestGetComponentStatusDisplay` tests real status display function, `TestDrawShipResources` tests real drawing function, `TestDrawShipCombatStatsDTO` is a legitimate regression test. The 6 constant tests could be removed but the file overall is valuable. Downgraded because removing just 6 constant tests from an otherwise healthy file is low priority.

---

## Claim 25: `test_fonts.py` 2 font constant tests -- TRIVIAL_CONSTANT
**Verdict: REJECTED**

`TestFontConstants` (lines 117-127) asserts `FONT_MAIN == "Arial"` and `FONT_MONO == "Consolas"`. While these look trivial, they guard against accidental changes to font names that would break rendering across the entire UI. Font name strings are used throughout the codebase for `pygame.font.SysFont` calls. If someone changes `FONT_MAIN` from "Arial" to something else, it could cause silent rendering issues on systems without that font. This is a legitimate regression guard. The rest of the file tests real caching behavior. REJECTED -- keep these.

---

## Claim 26: `test_rendering_logic.py` 4 tests -- DUPLICATE_OF test_game_renderer.py
**Verdict: DOWNGRADED to MEDIUM**

`test_rendering_logic.py` imports and tests `draw_ship` and `LAYER_COLORS` from `game.ui.renderer.game_renderer`. The canonical `test_game_renderer.py` has `TestLayerColors`, `TestDrawShipCulling`, `TestDrawShipRendering`, and `TestDrawShipOverlay` classes.

`TestRenderingLogic.test_draw_ship_culling` overlaps with `TestDrawShipCulling` in the canonical file.
`TestLayerColors.test_layer_colors_constant_mapping` and `test_layer_colors_values` overlap with `TestLayerColors` in the canonical file.
`TestDrawShipBehavior` has tests for dead ship, theme image, no theme image, zoom, and boundary -- some of these overlap with canonical tests.

However, `test_component_color_coding` tests a specific overlay behavior (weapon/engine color coding) that may not be duplicated in the canonical file. Downgraded because partial overlap exists but full duplication needs more careful comparison.

---

## Claim 27: `test_builder_data_loader.py` -- DUPLICATE_OF test_workshop_data_loader.py
**Verdict: CONFIRMED**

Both files test `WorkshopDataLoader` (the builder file imports it as `BuilderDataLoader` via alias). Same class under test. The workshop version is the canonical name. Both test file discovery, data loading with temp directories. The builder version is a leftover from a rename.

---

## Claim 28: `test_builder_viewmodel.py` -- DUPLICATE_OF test_workshop_viewmodel.py
**Verdict: CONFIRMED**

Both files test `WorkshopViewModel` (the builder file imports it as `BuilderViewModel`). Same class, same mock event bus pattern, same DI context setup. The workshop version is canonical. The builder version is the pre-rename duplicate.

---

## Claim 29: `test_workshop_context_di.py` -- DUPLICATE_OF test_workshop_context.py
**Verdict: DOWNGRADED to MEDIUM**

`test_workshop_context_di.py` in `tests/unit/builder/` tests constructor injection and factory method registries pass-through. `test_workshop_context.py` in `tests/unit/workshop/` tests standalone/integrated factory methods and their defaults. The DI file focuses specifically on the DI path (constructor registries, factory registries pass-through) while the canonical file focuses on mode behavior. There IS overlap on `registries` parameter testing, but the DI file has a narrower, complementary focus. Not a pure duplicate -- downgraded.

---

## Claim 30: `test_workshop_viewmodel_di.py` -- DUPLICATE_OF test_workshop_viewmodel.py
**Verdict: DOWNGRADED to MEDIUM**

The DI file focuses on context registries injection path and registries pass-through to VehicleDesignService. The canonical file tests broader ViewModel behavior. Similar reasoning as claim 29 -- complementary focus, not pure duplication. Downgraded.

---

## Claim 31: `test_mandatory_modifiers.py` -- DUPLICATE_OF test_mandatory_modifiers_ownership.py
**Verdict: CONFIRMED**

Both files test the same thing: ModifierService owns MANDATORY_MODIFIERS and ModifierLogic doesn't have its own copy.

`test_mandatory_modifiers.py` has:
- `test_modifier_service_has_mandatory_modifiers` -- duplicated by ownership file's `test_modifier_service_owns_mandatory_modifiers`
- `test_mandatory_modifiers_are_strings` -- unique but trivial
- `test_modifier_logic_no_duplicate_constant` -- duplicated by ownership file's `test_modifier_logic_has_no_own_mandatory_modifiers_constant`

The ownership file is more focused and has better assertion messages. The first file is redundant.

---

## Claim 32: `test_workshop_screen_integration.py` -- TESTS_NOTHING_REAL
**Verdict: CONFIRMED**

Every test in this file patches `__init__`, creates mock attributes, then either:
- Sets a mock attribute and asserts it: `screen.viewmodel.ship = new_ship; assert screen.viewmodel.ship.name == "New Ship"` (line 197-200)
- Calls a method on a mock and asserts it was called: `screen._ship_io_adapter.save_design(ship); screen._ship_io_adapter.save_design.assert_called_once()` (line 117-119)
- Sets a string and asserts it: `screen.error_message = "Save failed: Invalid design"; assert screen.error_message == "Save failed: Invalid design"` (lines 236-239)
- Checks mock existence: `assert screen.event_bus is not None` (line 173)

No test calls a real method of `DesignWorkshopScreen`. All test MagicMock behavior.

---

## Claim 33: `test_bulk_add.py` -- reimplements logic locally, zero game.* imports
**Verdict: CONFIRMED**

Zero `from game.*` imports. Every test class defines its own local function (`get_add_count`, inline arithmetic) and tests that. `TestBulkAddCounterLogic` redefines the clamping logic 5 times (once per test method). `TestButtonIncrementLogic` does inline arithmetic with `max(1, min(1000, new_val))`. None of these exercise production code.

---

## Claim 34: `test_selection_hover.py` -- reimplements logic locally
**Verdict: CONFIRMED**

Zero `from game.*` imports. Every test defines its own local function:
- `deselect_all` (lines 15-18)
- `is_dropdown_expanded` (lines 31-32, 38-39)
- `get_hovered_list_item` (lines 57-63, 74-80, 97-103)
- `get_hovered_component` (lines 123-127, 137-141)

All test these local reimplementations, not production code.

---

## Claim 35: `test_sorting_filtering.py` -- tests Python sorted() on local mocks
**Verdict: CONFIRMED**

Zero `from game.*` imports. Every test uses Python's built-in `sorted()` on local Mock/SimpleNamespace objects. `TestSortingLogic` tests `sorted(components, key=lambda c: c.name)`. `TestFilteringLogic` tests list comprehensions. `TestTypeFilterOptions` tests `sorted(list(set(...)))`. `TestComponentOrderMap` tests dict comprehension. `TestRegistryReloadLogic` tests `if x not in list` logic. All test Python builtins, not production code.

---

## Claim 36: `test_geometry.py` -- reimplements logic locally
**Verdict: CONFIRMED**

Zero `from game.*` imports. Every test class defines its own calculation method:
- `calculate_max_r` (line 19-24)
- `calculate_arc_angles` (line 70-78)
- `generate_arc_points` (line 136-156)
- `calculate_display_range` (line 217-222)
- `get_layer_color` (line 260-279)
- `calculate_ring_radius` (line 317-328)

All test these local reimplementations. None exercise production code.

---

## Claim 37: `test_rendering_logic.py` (schematic_view) -- reimplements logic locally
**Verdict: CONFIRMED**

Zero `from game.*` imports. Every test class defines its own method:
- `get_weapon_arc_color` (lines 20-30)
- `generate_cache_key` (lines 66-80) -- literally returns a tuple
- `calculate_center` (lines 143-153) -- integer division
- `calculate_scale_factor` (lines 191-207)
- `calculate_scaled_dimensions` (lines 255-268) -- int multiplication
- `get_component_at` (lines 308-312) -- returns None always

All test local reimplementations. The cache key tests (82-133) are especially egregious -- testing that Python tuples with different values are not equal.

---

## Claim 38: `test_lab_scene/test_logic.py` -- 493 LOC, ZERO imports from game.*
**Verdict: CONFIRMED**

Verified: zero `from game.*` or `import game.*`. Every class defines its own methods:
- `format_json` using `json.dumps`
- `get_selected_component_id` (local logic)
- `calculate_option_index` (local arithmetic)
- `format_value_short` (local formatting)
- `extract_filename_from_condition` (local string parsing)
- `extract_component_ids` (local dict traversal)
- `get_status_color`, `get_status_symbol` (local if-else)
- `get_pvalue_color` (local comparison)
- `calculate_difference` (local arithmetic)
- `calculate_progress` (local division)

493 lines testing only local reimplementations.

---

## Claim 39: `test_lab_scene/test_rendering.py` -- 361 LOC, ZERO imports from game.*
**Verdict: CONFIRMED**

Verified: zero `from game.*` imports. Tests panel rect calculations, coordinate math, and layout calculations -- all as local arithmetic operations, no production code involved.

---

## Claim 40: `test_lab_scene/test_ui_components.py` -- 306 LOC, ZERO imports from game.*
**Verdict: CONFIRMED**

Verified: zero `from game.*` imports. Tests popup dimensions, scroll calculations, tab switching, scrollbar logic -- all as local arithmetic and if-else logic. No production code exercised.

---

## Summary by Category

### CONFIRMED (30 claims)
- **Reimplemented logic / zero game imports** (strongest signal): Claims 10, 11, 12, 33, 34, 35, 36, 37, 38, 39, 40 (11 claims, ~2300+ LOC)
- **Duplicate tests**: Claims 1, 2, 27, 28, 31 (5 claims)
- **Set-then-assert / TESTS_NOTHING_REAL**: Claims 9, 13, 20, 21, 22, 23, 32 (7 claims)
- **Source text matching**: Claims 4, 5, 6 (3 claims)
- **Trivial constant**: Claims 7, 15, 16, 17 (4 claims)
- **Dead code**: Claim 18 (1 claim)
- **Scaffold + constant mix**: Claim 14 (1 claim, but note TestClearUI should be kept)

### DOWNGRADED (8 claims)
- Claim 3: Partial duplicate -- helper/dialog tests are unique
- Claim 8: Menu panel constants have structural regression value
- Claim 19: Blanket 11-file claim needs individual verification
- Claim 24: 6 constants in otherwise valuable file
- Claim 26: Partial overlap, needs careful comparison
- Claim 29: Complementary DI focus, not pure duplicate
- Claim 30: Complementary DI focus, not pure duplicate

### REJECTED (2 claims)
- Claim 25: Font name constants guard against silent rendering breaks across entire UI
