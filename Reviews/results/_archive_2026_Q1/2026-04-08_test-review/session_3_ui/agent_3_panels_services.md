# Test Review Report: Agent 3 — UI Panels + Components + Services

## Scope
- **Source files reviewed:** 41 files (7,187 LOC panels + 7,633 LOC components/widgets/services/renderer/filters/utils/research/assets)
- **Test files reviewed:** 54 files
- **Coverage data referenced:** Yes (extracted from coverage.json for all 41 source files)

## Summary
- Test files reviewed: 54
- Source files reviewed: 41
- Tests flagged for removal: 14 (estimated LOC: ~620)
- Tests flagged as happy-path-only: 8
- Source files with inadequate coverage: 10

---

## A. Tests Recommended for Removal

### A1. Dead mock module
- **File:** `tests/unit/ui/mocks/__init__.py`
- **Test(s):** Entire module
- **Reason:** DEAD_CODE
- **Confidence:** HIGH
- **Evidence:** Module contains only `__all__ = []` (8 lines). Grep for `from tests.unit.ui.mocks` finds only a reference in an archived project document (`Projects/deep_archive/PROJ-151-200/PROJ-154/phase_1_checklist.md`), not in any test code. No test imports from this module.
- **Estimated LOC saved:** 8

### A2. Trivial import-only tests
- **File:** `tests/unit/ui/panels/test_component_modifier_grid_panel.py`
- **Test(s):** `TestComponentModifierGridPanelImport::test_panel_can_be_imported`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Line 37-39: asserts `ComponentModifierGridPanel is not None` after import. This is already covered implicitly by every other test in the file which also imports the class.
- **Estimated LOC saved:** 5

- **File:** `tests/unit/ui/panels/test_design_report_panel.py`
- **Test(s):** `TestDesignReportPanelImport::test_panel_can_be_imported`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Line 39-43: same pattern. Every other test in the file imports `DesignReportPanel`.
- **Estimated LOC saved:** 5

- **File:** `tests/unit/ui/panels/test_design_stats_panel.py`
- **Test(s):** `TestDesignStatsPanelInit::test_panel_can_be_imported`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Line 146-150: asserts class `is not None` after import. Redundant with all other tests.
- **Estimated LOC saved:** 5

- **File:** `tests/unit/ui/panels/test_planet_report_panel.py`
- **Test(s):** `TestPlanetReportPanelImport::test_panel_can_be_imported`, `test_compute_production_can_be_imported`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Lines 55-66: both just assert `is not None` after import. The function/class is used extensively in later tests in the same file and in `test_compute_planet_production.py`.
- **Estimated LOC saved:** 12

- **File:** `tests/unit/ui/panels/test_ship_detail_panel.py`
- **Test(s):** `TestShipDetailPanelInit::test_panel_can_be_imported`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Line 132-136: asserts `is not None` after import, redundant.
- **Estimated LOC saved:** 5

- **File:** `tests/unit/ui/test_race_description_panel.py`
- **Test(s):** `TestRaceDescriptionPanelCreation::test_race_description_panel_can_be_imported`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Line 39-42: asserts `is not None` after import.
- **Estimated LOC saved:** 4

- **File:** `tests/unit/ui/test_race_environment_panel.py`
- **Test(s):** `TestRaceEnvironmentPanelCreation::test_race_environment_panel_can_be_imported`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Line 51-55: asserts `is not None` after import.
- **Estimated LOC saved:** 4

- **File:** `tests/unit/ui/test_race_flag_gallery.py`
- **Test(s):** `TestRaceFlagGalleryCreation::test_race_flag_gallery_can_be_imported`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Line 57-60.
- **Estimated LOC saved:** 4

- **File:** `tests/unit/ui/test_race_portrait_gallery.py`
- **Test(s):** `TestRacePortraitGalleryCreation::test_race_portrait_gallery_can_be_imported`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Line 57-60.
- **Estimated LOC saved:** 4

- **File:** `tests/unit/ui/test_race_summary_panel.py`
- **Test(s):** `TestRaceSummaryPanelCreation::test_race_summary_panel_can_be_imported`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Line 128-132.
- **Estimated LOC saved:** 4

- **File:** `tests/unit/ui/test_race_theme_gallery.py`
- **Test(s):** `TestRaceThemeGalleryCreation::test_race_theme_gallery_can_be_imported`
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Line 51-55.
- **Estimated LOC saved:** 4

### A3. Tests that test nothing real (set-attribute-then-assert-attribute)
- **File:** `tests/unit/ui/panels/test_design_report_panel.py`
- **Test(s):** `TestDesignReportPanelInit::test_panel_stores_manager`, `test_panel_stores_rect`, `test_panel_stores_container`, `test_panel_initial_ship_is_none`, `test_panel_stats_panel_initially_none`, `test_panel_rows_map_is_dict`; `TestShowPlaceholder::test_show_placeholder_logic_clears_ship`, `test_show_placeholder_logic_kills_stats`, `test_show_placeholder_logic_clears_rows`, `test_label_set_text_clears`, `test_placeholder_text_kills_old`; `TestWidthRequired::test_width_is_integer`
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Lines 51-118 (init tests): These patch out `__init__`, then manually set `panel.manager = manager` and assert `panel.manager is manager`. This tests Python attribute assignment, not the class. Lines 126-203 (placeholder tests): These duplicate the source code logic inline — they set `panel.current_ship = None` and then assert it's None, or run `if panel._stats_panel is not None: panel._stats_panel.kill()` which is testing their own test code rather than calling `show_placeholder()`. Line 479-480: `test_width_is_integer` asserts `isinstance(width, int)` — redundant with `test_width_returns_750` which already demonstrates an int return.
- **Estimated LOC saved:** ~150

- **File:** `tests/unit/ui/panels/test_planet_report_panel.py`
- **Test(s):** `TestPlanetReportPanelInit::test_panel_stores_manager`, `test_panel_stores_rect`, `test_panel_stores_planet`, `test_panel_stores_production_rates`, `test_panel_production_rates_default_empty`; `TestUpdatePlanet::test_update_planet_sets_planet`, `test_update_planet_sets_production_rates`, `test_detail_text_has_rebuild_method`; `TestComplexesList::test_complexes_container_none_check`, `test_complex_items_is_list`; `TestResourceGrid::test_resource_grid_items_list_exists`; `TestHeightRequired::test_height_is_integer`
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Same pattern as above. Init tests set attributes on `__new__`-constructed objects and assert they exist. `test_update_planet_sets_planet` (line 145-161) just does `panel.planet = new_planet; assert panel.planet is new_planet`. `test_complexes_container_none_check` (line 211-227) tests a Python `if not` pattern by running it inline in the test, not the actual method.
- **Estimated LOC saved:** ~120

### A4. Duplicate test logic
- **File:** `tests/unit/ui/panels/test_design_stats_panel.py`
- **Test(s):** `TestDesignStatsPanelStatCalculation::test_mass_calculation`, `test_speed_calculation`, `test_thrust_calculation`; `TestDesignStatsPanelFormatting::test_mass_formatting_integer`, `test_mass_formatting_decimal`, `test_percentage_formatting`
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Lines 191-243: These tests create a mock ship, set `ship.mass = 175.5`, then assert `ship.mass == 175.5`. They test MagicMock attribute assignment, not DesignStatsPanel. The formatting tests (lines 218-243) test inline f-string formatting — `f"{ship.mass:.0f}"` — which is a Python language feature, not project code. None of these call any method on `DesignStatsPanel`.
- **Estimated LOC saved:** ~55

- **File:** `tests/unit/ui/panels/test_design_stats_panel.py`
- **Test(s):** `TestDesignStatsPanelRowsMap::test_rows_map_is_dict`, `test_rows_map_stores_stat_rows`; `TestDesignStatsPanelLayerStatus::test_layer_rows_list_exists`, `test_current_logistics_keys_is_set`
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Lines 246-299: Identical `__new__` + manual attribute set + assert pattern. Tests Python data structure creation.
- **Estimated LOC saved:** ~55

### A5. Trivial constant assertion tests
- **File:** `tests/unit/ui/panels/test_ship_stats_renderer.py`
- **Test(s):** `TestResourceColors::test_fuel_color_is_orange`, `test_energy_color_is_blue`, `test_ammo_color_is_yellowish`; `TestResourceOrderPriority::test_fuel_has_highest_priority`, `test_energy_has_second_priority`, `test_ammo_has_third_priority`
- **Reason:** TRIVIAL_CONSTANT
- **Confidence:** MEDIUM
- **Evidence:** Lines 305-348: Assert specific RGB tuples and priority integers for 6 constants. These are mapping table values that would break many things visually if changed, but the tests don't guard against regressions — they just document current values. The functional tests above already exercise these constants indirectly.
- **Estimated LOC saved:** ~45

- **File:** `tests/unit/ui/test_fonts.py`
- **Test(s):** `TestFontConstants::test_font_main_is_arial`, `test_font_mono_is_consolas`
- **Reason:** TRIVIAL_CONSTANT
- **Confidence:** MEDIUM
- **Evidence:** Lines 120-126: Asserts `FONT_MAIN == "Arial"` and `FONT_MONO == "Consolas"`. These are configuration constants, not behavioral invariants.
- **Estimated LOC saved:** 8

### A6. Duplicate test coverage
- **File:** `tests/unit/ui/test_rendering_logic.py`
- **Test(s):** `TestRenderingLogic::test_draw_ship_culling`; `TestDrawShipBehavior::test_draw_ship_dead_ship_returns_early`; `TestLayerColors::test_layer_colors_constant_mapping`, `test_layer_colors_values`
- **Reason:** DUPLICATE_OF:tests/unit/ui/renderer/test_game_renderer.py
- **Confidence:** MEDIUM
- **Evidence:** `test_draw_ship_culling` (line 53-59) duplicates `TestDrawShipCulling::test_ship_culled_when_off_screen_left` from test_game_renderer.py. `test_draw_ship_dead_ship_returns_early` duplicates `TestDrawShipCulling::test_dead_ship_not_drawn`. `TestLayerColors` (lines 234-249) duplicate `TestLayerColors` from test_game_renderer.py with identical assertions. The `test_layer_colors_values` test additionally asserts specific RGB values (harder-coded than the renderer test), making it more fragile.
- **Estimated LOC saved:** ~50

---

## B. Tests That Are Happy-Path-Only

### B1. BuildQueuePortraitLoader
- **File:** `tests/unit/ui/panels/test_build_queue_portraits.py`
- **Test(s):** `TestResourceIconLoading`, `TestResourcePortraitConstants`
- **What's tested:** Icon loading, constant dictionaries
- **What's missing:** What happens when `icon_size < 0`? What about loading icons with corrupted image files (not just missing)? What about `icon_size=0`?
- **Source method(s) affected:** `game/ui/panels/build_queue_portraits.py:load_resource_icons` (line ~50-80)
- **Priority:** LOW

### B2. ComponentModifierGridPanel
- **File:** `tests/unit/ui/panels/test_component_modifier_grid_panel.py`
- **Test(s):** `TestOnSelectionChanged`, `TestUpdateComponent`
- **What's tested:** Normal selection flow, component update
- **What's missing:** What if `_on_selection_changed` is called with a tuple of wrong length (e.g., 2 elements or 4)? What if `modifier_grid` is None when `_on_ship_updated` is called? Error recovery paths.
- **Source method(s) affected:** `game/ui/panels/component_modifier_grid_panel.py:_on_selection_changed` (lines ~50-80)
- **Priority:** LOW

### B3. DesignLoaderAdapter
- **File:** `tests/unit/ui/services/test_design_loader_adapter.py`
- **Test(s):** All tests
- **What's tested:** Delegation to loader, None returns, ValidationException on None provider
- **What's missing:** What happens when `load_ship_from_design_data` raises unexpected exceptions (e.g., `KeyError`, `TypeError` from bad design data)? Does the adapter propagate or catch them?
- **Source method(s) affected:** `game/ui/services/design_loader_adapter.py:load_ship_from_design_data` (line ~40-55)
- **Priority:** MEDIUM

### B4. ValidationService
- **File:** `tests/unit/ui/services/test_validation_service.py`
- **Test(s):** All tests (5 tests)
- **What's tested:** Delegation to validator, valid/invalid results
- **What's missing:** No test for `validate_addition` with None ship, None component, None layer. No test for `validate_design` with None ship. No test for exception handling if the validator itself throws.
- **Source method(s) affected:** `game/ui/services/validation_service.py` (79 LOC, 100% coverage by line but not by branch)
- **Priority:** MEDIUM

### B5. ShipIOAdapter
- **File:** `tests/unit/ui/services/test_ship_io_adapter.py`
- **Test(s):** `TestShipIOAdapterErrorPaths`
- **What's tested:** Various error message strings from mock
- **What's missing:** These tests only verify that the adapter passes through error messages — they don't test that the adapter *itself* handles its own error paths (e.g., what if `mock_ship_io_class.save_ship` raises an unhandled exception instead of returning a tuple?).
- **Source method(s) affected:** `game/ui/services/ship_io_adapter.py:save_ship`, `load_ship`
- **Priority:** LOW (thin adapter)

### B6. PanelFactory
- **File:** `tests/unit/ui/widgets/test_panel_factory.py`
- **Test(s):** All tests
- **What's tested:** Normal tuple creation, correct params, label positioning
- **What's missing:** No test for invalid rect (zero width/height), no test for very long title text that might overflow.
- **Source method(s) affected:** `game/ui/widgets/panel_factory.py:create_titled_panel`
- **Priority:** LOW

### B7. ModifierEditorPanel
- **File:** `tests/unit/ui/panels/test_modifier_editor_panel.py`
- **Test(s):** `TestModifierEditorPanelUpdate`
- **What's tested:** `update(dt)` exists and doesn't raise
- **What's missing:** Only 3 tests for a real panel class. No tests for event handling, modifier display, modifier editing, or callback invocation. The panel has 42.6% coverage (builder_widgets.py, 333 stmts).
- **Source method(s) affected:** `game/ui/panels/builder_widgets.py` (292 LOC)
- **Priority:** HIGH (42.6% coverage on a complex widget)

### B8. game_renderer draw_ship overlay
- **File:** `tests/unit/ui/renderer/test_game_renderer.py`
- **Test(s):** `TestDrawShipOverlay`
- **What's tested:** Circles drawn when overlay enabled, direction line drawn
- **What's missing:** No tests for overlay with disabled/destroyed components, no test for component-specific color coding (weapon=red, engine=green, etc.) in the renderer test file (only tested in the duplicate `test_rendering_logic.py`), no tests for the `_draw_component_overlay` sub-function error paths.
- **Source method(s) affected:** `game/ui/renderer/game_renderer.py:draw_ship` (169 LOC, 98.8% coverage)
- **Priority:** LOW (98.8% coverage, mostly cosmetic)

---

## C. Source Code with Inadequate Coverage

### C1. scrollable_json_panel.py
- **Source file:** `game/ui/widgets/scrollable_json_panel.py` (410 LOC)
- **Coverage:** 24.2% (223 stmts, 54 covered)
- **Untested areas:** Nearly all rendering logic, scroll handling, JSON tree expansion/collapse, text wrapping, click-to-copy, event handling
- **Risk:** This is the Combat Lab test details viewer. Rendering bugs in JSON display would affect test debugging workflow.
- **Priority:** MEDIUM

### C2. research_controls.py
- **Source file:** `game/ui/research/research_controls.py` (473 LOC)
- **Coverage:** 19.4% (206 stmts, 40 covered)
- **Untested areas:** Button creation, event handling, research queue management, priority controls, tech tree navigation
- **Risk:** Research UI controls could silently break. No dedicated test file exists for this module.
- **Priority:** HIGH

### C3. research_renderer.py
- **Source file:** `game/ui/research/research_renderer.py` (322 LOC)
- **Coverage:** 25.2% (143 stmts, 36 covered)
- **Untested areas:** Tech tree rendering, node positioning, connection line drawing, tooltip display, highlight/selection rendering
- **Risk:** Research tree visual rendering could regress without detection. No dedicated test file exists.
- **Priority:** MEDIUM

### C4. hit_effects.py
- **Source file:** `game/ui/effects/hit_effects.py` (233 LOC)
- **Coverage:** 29.2% (120 stmts, 35 covered)
- **Untested areas:** Particle creation, animation update loop, effect lifecycle management, shield hit visualization, hull hit visualization
- **Risk:** Visual combat effects could break silently. No dedicated test file exists.
- **Priority:** LOW (purely visual effects)

### C5. json_diff.py
- **Source file:** `game/ui/utils/json_diff.py` (111 LOC)
- **Coverage:** 19.1% (47 stmts, 9 covered)
- **Untested areas:** Diff computation between JSON trees, addition/removal/modification detection, nested object comparison, array diffing
- **Risk:** JSON diff is used in the Combat Lab to show expected vs actual test results. Bugs would produce misleading diff output.
- **Priority:** HIGH

### C6. builder_widgets.py (ModifierEditorPanel)
- **Source file:** `game/ui/panels/builder_widgets.py` (292 LOC)
- **Coverage:** 42.6% (141 stmts, 60 covered)
- **Untested areas:** Modifier list display, modifier editing UI, modifier validation, event handling, dropdown management
- **Risk:** Ship builder modifier editing could silently break.
- **Priority:** MEDIUM

### C7. base_gallery.py
- **Source file:** `game/ui/panels/base_gallery.py` (263 LOC)
- **Coverage:** 54.3% (92 stmts, 50 covered)
- **Untested areas:** Gallery layout calculation, scroll container management, thumbnail grid creation, asset discovery and loading
- **Risk:** Base class for 4 gallery subclasses (flag, portrait, theme, potentially more). Bugs here cascade.
- **Priority:** MEDIUM

### C8. game_settings.py
- **Source file:** `game/ui/services/game_settings.py` (94 LOC)
- **Coverage:** 67.5% (40 stmts, 27 covered)
- **Untested areas:** Settings persistence (save/load), default value handling, settings validation. No dedicated test file exists.
- **Risk:** Game settings could fail to persist or load correctly.
- **Priority:** MEDIUM

### C9. ship_detail_panel.py
- **Source file:** `game/ui/panels/ship_detail_panel.py` (428 LOC)
- **Coverage:** 36.6% (175 stmts, 64 covered)
- **Untested areas:** `_build_ship_display` (the main rendering method), layer component display, HP bar rendering, status text display, portrait loading
- **Risk:** The ship detail panel is visible in fleet management. Display bugs would be user-facing.
- **Priority:** MEDIUM

### C10. ship_stats_renderer.py
- **Source file:** `game/ui/panels/ship_stats_renderer.py` (439 LOC)
- **Coverage:** 47.8% (186 stmts, 89 covered)
- **Untested areas:** `draw_ship_layer_status` (layer component health bars), `draw_ship_stats_summary` (stat overview), component status coloring for various ComponentStatus states beyond the 4 tested
- **Risk:** Ship stats display could render incorrectly in battle view.
- **Priority:** MEDIUM

---

## D. Cross-Domain Observations

1. **Duplicate rendering test files:** `tests/unit/ui/test_rendering_logic.py` and `tests/unit/ui/renderer/test_game_renderer.py` both test `draw_ship()` and `LAYER_COLORS` from the same source file. The former appears to be the older file. Recommend consolidating into `test_game_renderer.py` and removing `test_rendering_logic.py` (after verifying the `test_component_color_coding` test is preserved, as it tests overlay component coloring which `test_game_renderer.py` does not).

2. **Pervasive `__new__` + patch `__init__` pattern:** Many panel test files (design_report_panel, planet_report_panel, ship_detail_panel, design_stats_panel, race_* panels) use `patch.object(Cls, '__init__', lambda self, *a, **kw: None)` followed by `Cls.__new__(Cls)` to bypass initialization. This creates objects in invalid states and leads to "tests" that set an attribute and assert it was set. While useful for testing individual methods, the init-patching pattern has led to a large volume of tests that exercise nothing. Consider integration-style tests that actually construct the panels (with mocked pygame_gui managers via the existing `ui_manager` fixture) for more valuable coverage.

3. **No test files for several source modules:** The following source files within this agent's scope have no dedicated test files:
   - `game/ui/services/battle_factories.py` (211 LOC, 100% coverage via integration)
   - `game/ui/services/battle_ui_service.py` (296 LOC, 100% coverage via integration)
   - `game/ui/services/game_settings.py` (94 LOC, 67.5% coverage)
   - `game/ui/research/research_controls.py` (473 LOC, 19.4% coverage)
   - `game/ui/research/research_renderer.py` (322 LOC, 25.2% coverage)
   - `game/ui/research/research_scene.py` (399 LOC, 72.1% coverage)
   - `game/ui/effects/hit_effects.py` (233 LOC, 29.2% coverage)
   - `game/ui/utils/json_diff.py` (111 LOC, 19.1% coverage)
   - `game/ui/utils/pygame_utils.py` (260 LOC, 90.8% coverage — tested via other tests)
   - `game/ui/assets/ship_theme_manager.py` (340 LOC, 88.3% coverage — tested via `test_theme_discovery.py`)
   - `game/ui/renderer/camera.py` (172 LOC, 100% coverage via integration)

4. **`test_compute_planet_production.py` duplicates `test_planet_report_panel.py`:** Both files test `compute_planet_production`. The standalone `test_compute_planet_production.py` is more thorough (BUG-86 regression test with registry lookup), while `test_planet_report_panel.py::TestComputePlanetProduction` has weaker versions of the same tests. Consider consolidating.

5. **Race panel tests share identical structural patterns:** The test files for `race_flag_gallery`, `race_portrait_gallery`, `race_theme_gallery`, `race_description_panel`, and `race_environment_panel` all follow a nearly identical template. This suggests they were generated from a template. While not wrong, the repetitive `has_*_attribute` tests (which set an attribute via `__new__` and assert `hasattr`) add no value and could be removed across all of them.
