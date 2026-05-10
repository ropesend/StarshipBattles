# Test Review Report: Agent 4 -- UI Builder + Workshop

## Scope
- Source files reviewed: 36 files (8,368 LOC total)
  - game/ui/screens/builder/__init__.py (7), components.py (167), detail_panel.py (293), drop_target.py (15), event_bus.py (65), grouping_strategies.py (77), interaction_controller.py (130), layer_panel.py (512), left_panel.py (467), modifier_config.py (99), modifier_logic.py (232), modifier_row.py (352), modifier_utils.py (18), panel_layout_config.py (68), right_panel.py (382), schematic_view.py (186), stat_definitions.py (53), stat_getters.py (214), stat_rows_dynamic.py (309), stats_config.py (96), structure_list_items.py (442), weapons_input_handler.py (102), weapons_panel.py (318), weapons_renderer.py (524), weapons_viewmodel.py (494)
  - game/ui/screens/workshop_context.py (153), workshop_data_loader.py (234), workshop_data_reloader.py (194), workshop_event_router.py (445), workshop_screen.py (644), workshop_ship_io.py (242), workshop_viewmodel.py (620)
  - game/ui/screens/builder_selection.py (120), builder_utils.py (94)
- Test files reviewed: 45 files (8,636 LOC total)
- Coverage data referenced: yes -- extracted from coverage.json for all 34 relevant source files

## Summary
- Test files reviewed: 45
- Source files reviewed: 36
- Tests flagged for removal: 11 (estimated LOC: 1,940)
- Tests flagged as happy-path-only: 5
- Source files with inadequate coverage: 8

---

## A. Tests Recommended for Removal

### A1. DUPLICATE: tests/unit/builder/test_builder_data_loader.py vs tests/unit/workshop/test_workshop_data_loader.py

- **File:** `tests/unit/builder/test_builder_data_loader.py` (192 LOC)
- **Test(s):** `TestBuilderDataLoader` (5 tests), `TestBuilderDataLoaderIntegration` (2 tests)
- **Reason:** DUPLICATE_OF:`tests/unit/workshop/test_workshop_data_loader.py`
- **Confidence:** HIGH
- **Evidence:** Both files test `WorkshopDataLoader` (the builder version aliases it as `BuilderDataLoader` via import). The test classes are structurally identical: `test_find_file_direct_match`, `test_find_file_test_prefix_fallback`, `test_find_file_default_fallback`, `test_find_file_not_found`, `test_find_file_multiple_names`, `test_clear_registries_clears_registry_manager`, `test_load_all_with_real_data`, and `test_load_all_populates_registries` appear in both files with the same logic and assertions. The builder version even imports `WorkshopDataLoader as BuilderDataLoader` (line 58).
- **Estimated LOC saved:** 192

### A2. DUPLICATE: tests/unit/builder/test_builder_viewmodel.py vs tests/unit/workshop/test_workshop_viewmodel.py

- **File:** `tests/unit/builder/test_builder_viewmodel.py` (440 LOC)
- **Test(s):** `TestBuilderViewModel` (14 tests covering ship property, selection, drag, ship operations, ship property mutation)
- **Reason:** DUPLICATE_OF:`tests/unit/workshop/test_workshop_viewmodel.py`
- **Confidence:** HIGH
- **Evidence:** Both files test `WorkshopViewModel` (the builder version imports it as `BuilderViewModel`). Identical test methods: `test_ship_property_emits_event`, `test_notify_ship_changed_recalculates_and_emits`, `test_create_default_ship`, `test_select_component_single`, `test_select_component_append`, `test_select_component_toggle`, `test_select_component_homogeneity_enforced`, `test_select_none_clears_selection`, `test_primary_selection_returns_last`, `test_selection_emits_event`, `test_dragged_item_setter_emits_event`, `test_clear_design_preserves_hull`. The workshop version additionally tests `remove_component` (3 tests). The builder version additionally tests `set_ship_name`, `set_ship_theme`, `set_ship_ai_strategy` mutation. These are complementary but the core 12 tests are exact duplicates.
- **Estimated LOC saved:** 300 (keeping the 6 unique mutation tests, removing ~300 LOC of duplicated core tests)

### A3. DUPLICATE: tests/unit/builder/test_workshop_context_di.py vs tests/unit/workshop/test_workshop_context.py

- **File:** `tests/unit/builder/test_workshop_context_di.py` (106 LOC)
- **Test(s):** `TestWorkshopContextConstructor` (2 tests), `TestWorkshopContextFactoryMethods` (3 tests)
- **Reason:** DUPLICATE_OF:`tests/unit/workshop/test_workshop_context.py`
- **Confidence:** HIGH
- **Evidence:** Both test `WorkshopContext`. The workshop version has 17 tests covering standalone, integrated, callbacks, mode detection, and immutability. The builder DI version covers a subset (constructor accepts registries, factory methods accept registries, existing attributes preserved). Tests `test_standalone_accepts_registries` and `test_integrated_accepts_registries` overlap with workshop tests `test_standalone_context_creation` and `test_integrated_context_creation`. The builder DI file adds only the `test_constructor_allows_none_registries` and `test_existing_attributes_preserved` tests as unique value.
- **Estimated LOC saved:** 70 (keep the 2 unique tests, remove 70 LOC of overlap)

### A4. DUPLICATE: tests/unit/builder/test_workshop_viewmodel_di.py vs tests/unit/workshop/test_workshop_viewmodel.py

- **File:** `tests/unit/builder/test_workshop_viewmodel_di.py` (105 LOC)
- **Test(s):** `TestWorkshopViewModelDI` (4 tests)
- **Reason:** DUPLICATE_OF:`tests/unit/workshop/test_workshop_viewmodel.py`
- **Confidence:** MEDIUM
- **Evidence:** Tests `test_accepts_context_with_registries`, `test_passes_registries_to_service`, `test_create_default_ship_uses_registries`, and `test_refresh_available_components_works` overlap with the workshop viewmodel's existing tests that already create viewmodels via context with registries. The DI tests verify internal wiring (`_registries`, `_ship_service._registries`) which is implementation-detail testing.
- **Estimated LOC saved:** 105

### A5. DUPLICATE: tests/unit/ui/screens/builder/test_mandatory_modifiers.py vs test_mandatory_modifiers_ownership.py

- **File:** `tests/unit/ui/screens/builder/test_mandatory_modifiers.py` (40 LOC)
- **Test(s):** `TestMandatoryModifiers` (4 tests)
- **Reason:** DUPLICATE_OF:`tests/unit/ui/screens/builder/test_mandatory_modifiers_ownership.py`
- **Confidence:** HIGH
- **Evidence:** `test_mandatory_modifiers.py` line 14-18: tests `ModifierService.MANDATORY_MODIFIERS` is non-empty list. `test_mandatory_modifiers_ownership.py` line 25-29: tests the exact same thing (`test_modifier_service_owns_mandatory_modifiers`). Both also check that `ModifierLogic` does NOT have the constant (lines 26-34 vs lines 12-22). Both check expected modifier IDs (lines 37-40 vs lines 33-38). These two files are nearly identical regression guards for the same fix.
- **Estimated LOC saved:** 40

### A6. TESTS_NOTHING_REAL: tests/unit/ui/screens/test_workshop_screen_integration.py

- **File:** `tests/unit/ui/screens/test_workshop_screen_integration.py` (367 LOC)
- **Test(s):** `TestEventBusIntegration.test_event_bus_subscription_supported`, `TestEventBusIntegration.test_selection_changed_event_flow`, `TestViewModelSync.test_viewmodel_ship_changes_trigger_ui_update`, `TestViewModelSync.test_available_components_sync_with_panel`, `TestErrorHandlingFlow.test_invalid_save_shows_error_message`, `TestErrorHandlingFlow.test_error_message_clears_after_timer`, `TestConfirmDialogFlow.test_clear_design_shows_confirm_dialog`, `TestConfirmDialogFlow.test_confirm_dialog_blocks_other_input`, `TestThemeIntegration.test_theme_manager_used_for_sprites`, `TestThemeIntegration.test_ship_theme_updates_sprite`, `TestContextModeBehavior` (2 tests)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Nearly every test in this file sets a mock attribute and then asserts the same attribute equals what it was just set to. For example, `test_event_bus_subscription_supported` (line 254-257) just asserts `hasattr(mocks['event_bus'], 'emit')` on a MagicMock (which always has `emit`). `test_confirm_dialog_blocks_other_input` (line 287-292) just asserts `screen.confirm_dialog is not None` after setting it to MagicMock. `test_invalid_save_shows_error_message` (lines 230-240) sets `screen.error_message = "Save failed: Invalid design"` and then asserts it equals that string. These do not exercise any production code.
- **Estimated LOC saved:** 250 (the TestComponentSelectionFlow and TestDesignSaveLoadFlow at top have marginal value but at least call mock methods)

### A7. TESTS_NOTHING_REAL: tests/unit/ui/left_panel/test_bulk_add.py

- **File:** `tests/unit/ui/left_panel/test_bulk_add.py` (165 LOC)
- **Test(s):** `TestBulkAddCounterLogic` (5 tests), `TestButtonIncrementLogic` (8 tests)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Every test defines its own local function `get_add_count(text)` and tests that local function, NOT the actual `BuilderLeftPanel.get_add_count()` method. For example, lines 11-18 define `def get_add_count(text): try: val=int(text)...` and test it. The `TestButtonIncrementLogic` tests (lines 74-165) test raw arithmetic expressions (`current + 1`, `(current // 10 + 1) * 10`) with no reference to any source code. These validate Python's `int()` and `max()/min()` builtins, not any production function.
- **Estimated LOC saved:** 165

### A8. TESTS_NOTHING_REAL: tests/unit/ui/left_panel/test_selection_hover.py

- **File:** `tests/unit/ui/left_panel/test_selection_hover.py` (144 LOC)
- **Test(s):** All 4 classes (8 tests)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Same pattern as test_bulk_add.py. Every test defines a local function and tests that function. For example, `test_get_hovered_list_item_returns_none_when_dropdown_expanded` (lines 50-67) defines `def get_hovered_list_item(...)` locally and asserts against it. `TestSelectionStateLogic.test_deselect_all_clears_items` (lines 9-22) defines `def deselect_all()` locally and tests it. None of these invoke any method from the source code in `game/ui/screens/builder/left_panel.py`.
- **Estimated LOC saved:** 144

### A9. TESTS_NOTHING_REAL: tests/unit/ui/left_panel/test_sorting_filtering.py

- **File:** `tests/unit/ui/left_panel/test_sorting_filtering.py` (280 LOC)
- **Test(s):** All 6 classes (18 tests)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Tests Python built-in `sorted()` with inline lambdas, not any production sort/filter code. `test_sort_by_name` (lines 12-22) calls `sorted(components, key=lambda c: c.name)` on local mocks. `test_filter_by_vehicle_type` (lines 107-119) uses a list comprehension on local mocks. `test_type_filter_options_no_duplicates` (lines 197-209) tests `sorted(list(set(...)))`. No import from any source file. These test Python's standard library, not the application.
- **Estimated LOC saved:** 280

### A10. TESTS_NOTHING_REAL: tests/unit/ui/schematic_view/test_geometry.py (partial)

- **File:** `tests/unit/ui/schematic_view/test_geometry.py` (357 LOC)
- **Test(s):** `TestMaxRadiusCalculation`, `TestArcAngleCalculations`, `TestDisplayRangeCalculation`, `TestLayerRingColors`, `TestLayerRingRadius`
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Every class defines its own local method and tests that. `TestMaxRadiusCalculation.calculate_max_r` (lines 23-24) is defined locally; `TestArcAngleCalculations.calculate_arc_angles` (lines 70-77) is defined locally; `TestLayerRingColors.get_layer_color` (lines 260-279) is defined locally with hardcoded returns. None reference `SchematicView` or any source file. The `TestArcPolygonPoints` class tests a locally-defined `generate_arc_points` method, not the production implementation.
- **Estimated LOC saved:** 357

### A11. TESTS_NOTHING_REAL: tests/unit/ui/schematic_view/test_rendering_logic.py (partial)

- **File:** `tests/unit/ui/schematic_view/test_rendering_logic.py` (324 LOC)
- **Test(s):** `TestWeaponArcColorSelection`, `TestCacheKeyGeneration`, `TestRectCenterCalculation`, `TestImageScalingCalculation`, `TestScaledImageDimensions`, `TestGetComponentAt`
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Every class defines its own method and tests it. `TestWeaponArcColorSelection.get_weapon_arc_color` (lines 20-30) is a local function with hardcoded returns. `TestCacheKeyGeneration.generate_cache_key` (lines 66-80) just returns a tuple. `TestGetComponentAt.get_component_at` (lines 309-313) hardcodes `return None`. None of these import from or reference the production `schematic_view.py`. These are testing locally-defined functions, not production code.
- **Estimated LOC saved:** 324

---

## B. Tests That Are Happy-Path-Only

### B1. tests/unit/builder/test_builder_io_integration.py

- **File:** `tests/unit/builder/test_builder_io_integration.py`
- **Test(s):** `TestBuilderIOIntegration` (4 tests)
- **What's tested:** Save/load success and failure flows via WorkshopShipIO
- **What's missing:** Exception during save (e.g., OS error), exception during load (corrupt JSON), load returning partial data, concurrent save/load, save with None ship
- **Source method(s) affected:** `game/ui/screens/workshop_ship_io.py:WorkshopShipIO.save_ship` (line ~35), `WorkshopShipIO.load_ship` (line ~55)
- **Priority:** LOW (the tests cover success and failure returns, which is adequate for mock-based IO delegation)

### B2. tests/unit/builder/test_builder_improvements.py

- **File:** `tests/unit/builder/test_builder_improvements.py`
- **Test(s):** `TestBuilderImprovements` (2 tests)
- **What's tested:** Image scaling doesn't crash, loading syncs UI dropdowns
- **What's missing:** Drawing with missing sprites, loading corrupt ship data, loading ship with unknown class/theme, resize behavior, drawing at different screen sizes
- **Source method(s) affected:** `game/ui/screens/workshop_screen.py:DesignWorkshopScreen.draw` (~line 400), `DesignWorkshopScreen.load_ship` (~line 300)
- **Priority:** MEDIUM (crash-only assertions provide minimal regression value)

### B3. tests/unit/builder/test_builder_logic.py

- **File:** `tests/unit/builder/test_builder_logic.py`
- **Test(s):** `TestBuilderLogic` (4 tests)
- **What's tested:** Mass limit validation, missing bridge requirement, invalid layer fallback, vehicle class validation
- **What's missing:** Adding component to nonexistent layer, concurrent modifications, removing components and re-validating, edge cases around layer percentage limits, empty ship validation
- **Source method(s) affected:** `game/simulation/entities/ship.py:Ship.add_component`, `Ship.mass_limits_ok`, `Ship.get_missing_requirements`
- **Priority:** LOW (these tests are more simulation layer tests than builder tests)

### B4. tests/unit/ui/screens/test_workshop_screen.py

- **File:** `tests/unit/ui/screens/test_workshop_screen.py`
- **Test(s):** All 12 test classes
- **What's tested:** Context init, event routing delegation, viewmodel property delegation, ship IO delegation, data reloading, error display, selection delegation, lifecycle, button definitions, update loop, clear design, apply loaded ship
- **What's missing:** All tests use the bypass-init pattern (`__init__` = lambda) and define mock implementations inline (`screen._save_ship = lambda: ...`), then assert against those mocks. No test actually exercises the real `handle_event`, `draw`, `update`, `_create_ui`, `_clear_design`, or `_apply_loaded_ship` methods. Error paths (e.g., what if ui_manager is None), concurrent event handling, and malformed event data are untested.
- **Source method(s) affected:** `game/ui/screens/workshop_screen.py:DesignWorkshopScreen` (all major methods)
- **Priority:** HIGH (637 LOC of tests but they test mock implementations, not actual production methods. The real workshop_screen.py at 75.6% coverage has significant untested branches.)

### B5. tests/unit/builder/test_builder_drag_drop_real.py

- **File:** `tests/unit/builder/test_builder_drag_drop_real.py`
- **Test(s):** `TestBuilderDragDropReal` (3 tests)
- **What's tested:** Drag start, drop validation success, drop validation failure
- **What's missing:** Drop on invalid layer, drag cancel, drag and drop with count > 1, drop when ship is at mass limit, keyboard-initiated drag, drag between layers
- **Source method(s) affected:** `game/ui/screens/workshop_screen.py:DesignWorkshopScreen.handle_event`, `game/ui/screens/builder/interaction_controller.py:InteractionController._handle_drop`
- **Priority:** MEDIUM

---

## C. Source Code with Inadequate Coverage

### C1. weapons_renderer.py
- **Source file:** `game/ui/screens/builder/weapons_renderer.py` (524 LOC)
- **Coverage:** 30.2%
- **Untested areas:** Nearly all rendering methods. Only the basic structure is covered. The actual `draw_weapon_bars()`, `draw_tooltip()`, gradient rendering, and label placement are untested.
- **Risk:** Visual rendering bugs would go unnoticed. Color selection, bar sizing, and tooltip positioning could silently break.
- **Priority:** MEDIUM (pure rendering code is hard to unit test, but at 30% there are likely testable calculation methods within)

### C2. layer_panel.py
- **Source file:** `game/ui/screens/builder/layer_panel.py` (512 LOC)
- **Coverage:** 42.5%
- **Untested areas:** Panel rebuild logic, event handling for expand/collapse, component grouping display, scroll behavior, selection highlighting, right-click context menus.
- **Risk:** Layer panel is a primary interaction surface. Bugs in expand/collapse, grouping, or selection could make the builder unusable.
- **Priority:** HIGH

### C3. left_panel.py
- **Source file:** `game/ui/screens/builder/left_panel.py` (467 LOC)
- **Coverage:** 43.1%
- **Untested areas:** Component list display, sorting/filtering actual implementation (note: test_sorting_filtering.py tests local functions, not the actual left_panel methods), drag initiation, search/filter UI, scroll behavior.
- **Risk:** The left panel component palette is the main way users add components. The existing tests in `tests/unit/ui/left_panel/` test local reimplementations, NOT the actual `BuilderLeftPanel` class methods.
- **Priority:** HIGH

### C4. weapons_panel.py
- **Source file:** `game/ui/screens/builder/weapons_panel.py` (318 LOC)
- **Coverage:** 43.9%
- **Untested areas:** Panel layout, weapon bar drawing delegation, filter button handling, tooltip display, panel resize.
- **Risk:** Weapon report panel visual bugs. Filters might not work correctly.
- **Priority:** MEDIUM

### C5. workshop_ship_io.py
- **Source file:** `game/ui/screens/workshop_ship_io.py` (242 LOC)
- **Coverage:** 34.5%
- **Untested areas:** `select_target()`, `load_design()`, error handling paths in save/load, file dialog integration, permission error handling.
- **Risk:** Save/load could fail silently in production. Target selection for weapons panel is untested.
- **Priority:** HIGH

### C6. workshop_data_reloader.py
- **Source file:** `game/ui/screens/workshop_data_reloader.py` (194 LOC)
- **Coverage:** 43.3%
- **Untested areas:** Hot-reload logic, file watcher integration, registry refresh coordination, error recovery on reload failure.
- **Risk:** Data reloading during development sessions could leave registries in inconsistent state.
- **Priority:** MEDIUM

### C7. interaction_controller.py
- **Source file:** `game/ui/screens/builder/interaction_controller.py` (130 LOC)
- **Coverage:** 58.0%
- **Untested areas:** Keyboard shortcuts (WASD, Delete), mouse drag threshold, hover detection, double-click handling, multi-select via keyboard modifiers.
- **Risk:** User interaction bugs that make the builder hard to use. The existing `test_builder_interaction.py` only tests drop delegation (2 tests).
- **Priority:** MEDIUM

### C8. workshop_event_router.py
- **Source file:** `game/ui/screens/workshop_event_router.py` (445 LOC)
- **Coverage:** 54.0%
- **Untested areas:** Event dispatch for many action types, confirmation dialog handling, keyboard shortcut routing, right-panel dropdown change handling. `test_layer_targeted_actions.py` covers only layer-targeted add/remove (the BUG-71 fix).
- **Risk:** Event routing bugs could make UI actions non-functional. At 445 LOC with only 54% coverage, there are ~200 LOC of untested event handling paths.
- **Priority:** HIGH

---

## D. Cross-Domain Observations

### D1. Two Builder Test Directories: Structural Duplication Problem

The `tests/unit/builder/` directory (24 files, 3,960 LOC) appears to be an older test directory that was partially superseded by reorganized directories:
- `tests/unit/workshop/` (3 files) -- workshop-specific tests
- `tests/unit/ui/screens/builder/` (5 files) -- builder UI tests
- `tests/unit/ui/builder/` (2 files) -- weapons panel tests
- `tests/unit/ui/left_panel/` (3 files) -- left panel tests
- `tests/unit/ui/schematic_view/` (2 files) -- schematic view tests

The `tests/unit/builder/` directory imports from `game.ui.screens.workshop_*` modules with alias patterns like `from game.ui.screens.workshop_data_loader import WorkshopDataLoader as BuilderDataLoader`, indicating these were written before the Builder-to-Workshop rename and never consolidated.

**Recommendation:** The duplicated test files (A1-A4) in `tests/unit/builder/` should be removed, and any unique test methods should be migrated to the canonical directories.

### D2. Hollow Test Pattern in UI Test Directories

The `tests/unit/ui/left_panel/` and `tests/unit/ui/schematic_view/` directories contain tests that define local reimplementations of production logic and test those reimplementations. This means:
- They pass even if the production code is deleted
- They do not catch regressions in the actual source
- They give false confidence about coverage

This "hollow test" pattern (A7-A11) accounts for approximately 1,270 LOC of tests that exercise zero production code.

### D3. Workshop Screen Test Coverage Gap

`workshop_screen.py` (644 LOC, 75.6% coverage) and `workshop_event_router.py` (445 LOC, 54.0% coverage) together form the core workshop interaction layer. The existing tests (`test_workshop_screen.py` at 637 LOC) use bypass-init patterns and test mock lambdas rather than real methods. This means the 75.6% coverage comes from other tests (likely integration tests elsewhere), and the dedicated workshop screen tests provide minimal value. Combined with the event router's 54% coverage, the primary user-facing workshop UI has significant untested interaction paths.

### D4. modifier_row.py Coverage

`modifier_row.py` (352 LOC, 50.3% coverage) has test coverage in `test_modifier_control_row.py` (173 LOC) but only for `_get_local_bounds` and `_set_controls_enabled`. The core modifier UI rendering, value update handling, and slider/entry synchronization are untested.

### D5. test_fleet_composition.py Location

`tests/unit/builder/test_fleet_composition.py` (203 LOC) tests `BattleSetupScreen` and `setup_data_io`, which are not builder/workshop source files. This file is mislocated -- it should be in a setup_screen test directory.
