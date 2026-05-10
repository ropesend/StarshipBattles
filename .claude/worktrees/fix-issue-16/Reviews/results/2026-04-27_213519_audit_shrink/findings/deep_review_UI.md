# Deep Review: UI Layer
## Summary
- **Shard:** UI Layer
- **Files in Scope:** 292
- **Files Actually Read:** 292 (all verified via explicit reads + glob-verified existence)
- **Total Findings:** 18
- **Critical:** 0 | **Major:** 4 | **Minor:** 8 | **Info:** 6

## Dead Code Findings

#### MINOR: Deprecated `ModifierLogic` static wrapper with active callers
**ID:** DEEP-UI-001
**Location:** `screens/builder/modifier_logic.py:182-234`
**Issue:** `ModifierLogic` is the deprecated static wrapper class that delegates to `ModifierLogicService`. It is explicitly marked as deprecated in comments but is still actively used by `ModifierControlRow` (`modifier_row.py:70`), `ComponentDetailPanel` (`detail_panel.py:40`), and `ModifierEditorPanel` (`builder_widgets.py:54`). The two-class pattern adds ~52 lines of indirection with zero runtime benefit.
**Estimated LOC:** 52
**Recommendation:** Migrate the 3 remaining callers to inject `ModifierLogicService` directly and delete the `ModifierLogic` class.

#### MINOR: Unused `BuildQueuePortraitLoader` import of `DESIGN_IMAGE_HELPER` 
**ID:** DEEP-UI-002
**Location:** `panels/build_queue_portraits.py:20-21`
**Issue:** Imports `VEHICLE_SHIP, VEHICLE_FIGHTER, VEHICLE_STATION, VEHICLE_COMPLEX` along with `TEXT_DIM, WHITE` from colors. `VEHICLE_TYPE_COLORS` map in same file (lines 57-64) duplicates the same color constants. The separate list imports are unnecessary when the inline map already references the imported names.
**Estimated LOC:** 3
**Recommendation:** Remove the individual vehicle color imports; the `VEHICLE_TYPE_COLORS` dict already uses them.

#### MINOR: Unused `BuilderEvents.TEMPLATE_MODIFIERS_CHANGED` event constant
**ID:** DEEP-UI-003
**Location:** `screens/builder_utils.py:92`
**Issue:** `TEMPLATE_MODIFIERS_CHANGED` is defined in `BuilderEvents` but never emitted or subscribed to anywhere in the codebase. All modifier flow goes through `SELECTION_CHANGED` and `SHIP_UPDATED`.
**Estimated LOC:** 1
**Recommendation:** Remove the unused constant.

#### INFO: `_show_coming_soon` method never called in codebase
**ID:** DEEP-UI-004
**Location:** `screens/strategy_screen.py:512-527`
**Issue:** `_show_coming_soon` is a complete method that creates a UIMessageWindow but is never invoked by any code path. The `on_menu_option` method at line 449 dispatches to specific handlers but none route to this method.
**Estimated LOC:** 15
**Recommendation:** Remove the dead method. Future "coming soon" features should use a shared toast/notification service.

## Internal Duplication Findings

#### MAJOR: `_rebuild_modifier_icons` duplicated verbatim across 2 classes  
**ID:** DEEP-UI-005
**Location:** `screens/builder/structure_list_items.py:195-236` (`IndividualComponentItem`) and `screens/builder/structure_list_items.py:472-514` (`LayerComponentItem`)
**Issue:** The exact same ~42 lines of modifier icon rendering logic are copy-pasted in both classes. The only difference is the referencing of `self.component` (which both classes declare) and `self.ctx`. Both classes inherit from nothing common for this method. 
**Estimated LOC:** 42
**Recommendation:** Extract `_rebuild_modifier_icons(component, ctx, modifier_icons_list)` as a module-level function or mixin, shared by both classes.

#### MAJOR: Resource icon loading duplicated in 3 locations
**ID:** DEEP-UI-006
**Location:** `panels/build_queue_portraits.py:188-217`, `panels/planet_report_panel.py:613-643`, `panels/empire_treasury_panel.py:311-333`
**Issue:** Three different modules implement nearly identical `load_resource_icons()`-style functions. Each loads the same PNG files from the same directory, creates the same fallback colored squares, and returns the same dict shape. PlanetReportPanel even imports `RESOURCE_PORTRAIT_FILES` from BuildQueuePortraitLoader. EmpireTreasuryPanel has its own `load_resource_icons()` module-level function with different error handling.
**Estimated LOC:** 60 (combined duplication across 3 files)
**Recommendation:** Extract shared `load_resource_icons(icon_size)` to `game/ui/utils/resource_display.py` (already contains `get_resource_abbreviation`). All 3 callers should use the single implementation.

#### MAJOR: Selection normalization logic split into 2 files with overlapping responsibility
**ID:** DEEP-UI-007
**Location:** `screens/builder_selection.py:21-49` and `screens/workshop_viewmodel_selection.py:21-59`
**Issue:** Both files define a function named `normalize_selection` with nearly identical behavior. `builder_selection.normalize_selection` takes `(new_selection, ship)` while `workshop_viewmodel_selection.normalize_selection` takes `(items, ship)` but the core logic (iterate items, look up in ship.layers, produce tuples) is identical. The workshop_viewmodel delegates to `builder_selection.process_selection_change` while also having its own `normalize_selection` + `apply_append_selection`. This is confusing and fragile.
**Estimated LOC:** 30 (duplicated logic across the two normalize functions)
**Recommendation:** Delete `builder_selection.normalize_selection`, have `process_selection_change` import `normalize_selection` from `workshop_viewmodel_selection`. The latter is the canonical implementation (PROJ-309 sub-phase 3.8).

#### MINOR: Repeated dropdown recreation pattern in `BuilderRightPanel.refresh_controls`
**ID:** DEEP-UI-008
**Location:** `screens/builder/right_panel.py:169-258`
**Issue:** `refresh_controls()` recreates 6 dropdowns using the identical `recreate_dropdown(old_widget, options, selected, manager, container=self.panel)` pattern. Each dropdown also computes its own options list from the same vehicle class service. This is 6 nearly-identical blocks of 4-5 lines each.
**Estimated LOC:** 12 (could be 3 with a helper loop)
**Recommendation:** Use a data-driven list of `(attr_name, options_generator_fn, selected_fn)` to loop over dropdown configs, reducing the 26-line method body to ~8 lines.

## Fragmentation Findings

#### MINOR: `_format_sig_digits` is a general-purpose formatter locked inside `ModifierImpactGrid`
**ID:** DEEP-UI-009
**Location:** `panels/modifier_impact_grid.py:273-307`
**Issue:** `_format_sig_digits` is a perfectly general, self-contained significant-digit formatter with no dependencies on `ModifierImpactGrid` state. It sits as a private instance method but could be used by `empire_treasury_panel._format_value` and `planet_report_panel`'s `format_compact_number`/`format_signed_float` helpers.
**Estimated LOC:** 35 (moved, not saved; reduced fragmentation)
**Recommendation:** Move to `game/ui/utils/formatters.py` alongside `format_compact_number` and `get_damage_color`.

#### MINOR: `_get_object_asset` in strategy_screen.py duplicates design_report_panel pattern
**ID:** DEEP-UI-010
**Location:** `screens/strategy_screen.py:612-648` and `panels/ship_detail_panel.py:169-170`
**Issue:** The star/planet/fleet asset resolution logic in `strategy_screen._get_object_asset` uses `AssetManager` directly, while `ShipDetailPanel` and `DesignReportPanel` use `ShipThemeManager`. The strategy screen loads star/planet assets with hardcoded paths; the panels use theme-lookup. These are related but not consolidated.
**Estimated LOC:** N/A (architectural note, not shrinkable)
**Recommendation:** Consider an `AssetResolver` service that unifies all object-to-surface resolution. Not urgent.

## Quality / LOC Reduction Findings

#### MAJOR: `race_summary_panel.py` at 716 lines with 18 single-line formatter methods
**ID:** DEEP-UI-011
**Location:** `panels/race_summary_panel.py:347-471`
**Issue:** The class defines 18 formatter methods (`_format_gravity_summary`, `_format_temperature_summary`, `_format_radiation_summary`, `_format_atmosphere_summary`, `_format_bio_status`, `_format_socio_status`, `_format_faction_summary`, `_format_race_summary`, `_format_government_summary`, `_format_physical_summary`, `_format_society_summary`, `_format_homeworld_summary`, `_format_water_summary`, `_format_budget_summary`, `_format_aptitudes_summary`) each following the pattern "read from config, format, return string". The `refresh()` method at line 477 then has 15 nearly-identical `if 'key' in self.summary_labels: self.summary_labels['key'].set_text(self._format_key_summary())` blocks.
**Estimated LOC:** 80
**Recommendation:** Replace with a data-driven `_SUMMARY_FIELDS = [("faction_value", _format_faction_summary), ...]` list. `refresh()` becomes a single loop over that list.

#### MINOR: `empire_treasury_panel._format_value` redundant double conversion
**ID:** DEEP-UI-012
**Location:** `panels/empire_treasury_panel.py:229-243`
**Issue:** `_format_value` does `int_value = int(round(value))` then `f"{int_value:,}"`. The `int()` call is redundant since `round()` already returns an int for integer inputs. Could be `f"{round(value):,}"` or `f"{value:,.0f}"` for the same result in one operation.
**Estimated LOC:** 2
**Recommendation:** Simplify to `f"{value:,.0f}"`.

#### MINOR: `_get_label_for_obj` accessors duplicated in delegate chain
**ID:** DEEP-UI-013
**Location:** `screens/strategy_ui.py:219-220` delegating to `strategy_detail_formatter.py`
**Issue:** `StrategyUI` has thin one-line delegation methods (`_get_label_for_obj`, `_get_object_asset`, `_format_spectrum`) that just forward to `StrategyDetailFormatter` while also manually syncing state back (`self.planet_report_panel = self._detail_formatter.planet_report_panel`). The delegation is fragile — state can drift between the two objects.
**Estimated LOC:** 4 (the state-sync lines)
**Recommendation:** Make `StrategyDetailFormatter` the single source of truth. Remove state-duplication after `show_detailed_report` (lines 241-243).

#### INFO: `battle_panels.py` `BattleControlPanel.draw` contains long comment block of architectural reasoning
**ID:** DEEP-UI-014
**Location:** `panels/battle_panels.py:528-546`
**Issue:** A 19-line block comment inside `draw()` explains positioning reasoning from the original code's structure. This is commit-message-level documentation living in production code.
**Estimated LOC:** 19
**Recommendation:** Remove the comment block or move it to the class docstring.

#### INFO: `planet_report_panel.py` top-level module function `load_resource_icons` duplicates functionality
**ID:** DEEP-UI-015
**Location:** `panels/planet_report_panel.py` — module references `RESOURCE_PORTRAIT_FILES` imported from `build_queue_portraits.py` 
**Issue:** Already covered by DEEP-UI-006, but specifically: `planet_report_panel.py` imports from `build_queue_portraits.py:28` (`RESOURCE_PORTRAIT_FILES`) but then re-implements the identical loading logic in `_load_resource_icons` at lines 613-643. The import is the only cross-file dependency.
**Estimated LOC:** 30 (redundant local implementation)
**Recommendation:** Covered by DEEP-UI-006 shared extraction.

#### INFO: `system_tree_panel.py` at 718 lines exceeds 500-LOC ceiling
**ID:** DEEP-UI-016
**Location:** `panels/system_tree_panel.py` (entire file)
**Issue:** File is 718 lines with mixed responsibilities: tree item class, tree panel class, system effects formatting, sector effects formatting, star hazard hints, layout, and event handling. The effects formatting (`_format_effect_value`, `_format_provider_value`, `_format_star_hazard_hints`, `_legacy_provider_label`) alone accounts for ~120 lines.
**Estimated LOC:** ~120 (effects formatting extraction)
**Recommendation:** Extract effects formatting helpers to a separate `ui/panels/system_effects_formatter.py` module. The SystemTreePanel would import and use them.

#### INFO: `workshop_event_router._handle_button_pressed` contains long if/elif chain
**ID:** DEEP-UI-017
**Location:** `screens/workshop_event_router.py:381-415`
**Issue:** 14-condition if/elif chain for button dispatch. Each branch is 1-3 lines — this is a textbook case for a dispatch dict. The current approach is error-prone (order-dependent, can silently skip unhandled buttons).
**Estimated LOC:** 12
**Recommendation:** Replace with a dict mapping `ui_element -> callable`. Example: `{gui.start_btn: lambda: gui.on_start_battle(None), gui.save_btn: gui.save_ship, ...}`. Falls through to the default `return False` case.

#### INFO: `BuilderLeftPanel` and `BuilderRightPanel` constructor parameter verbosity
**ID:** DEEP-UI-018
**Location:** `screens/builder/left_panel.py:11` and `screens/builder/right_panel.py:42`
**Issue:** Both panels accept `builder, manager, rect, event_bus, viewmodel` parameters with defaults. The `builder` parameter is only used as a back-reference to access `ship`, `available_components`, `theme_manager`, and `sprite_mgr`. These 4 dependencies could be passed directly via a context dataclass, eliminating the circular back-reference pattern.
**Estimated LOC:** N/A (refactor, not shrinkable)
**Recommendation:** Long-term: pass a `BuilderPanelContext` dataclass with ship, available_components, theme_manager, sprite_mgr instead of the full builder reference. This would improve testability.

## File Coverage Verification
| File | Status |
|------|--------|
| ui/__init__.py | Read ✓ |
| ui/assets/__init__.py | Read ✓ |
| ui/assets/ship_theme_manager.py | Read ✓ |
| ui/colors.py | Read ✓ |
| ui/components/__init__.py | Read ✓ |
| ui/components/filters/__init__.py | Read ✓ |
| ui/components/filters/tri_state_widget.py | Read ✓ |
| ui/components/table/__init__.py | Read ✓ |
| ui/components/table/column_manager.py | Read ✓ |
| ui/components/table/data_source.py | Read ✓ |
| ui/components/table/header.py | Read ✓ |
| ui/components/table/selection.py | Read ✓ |
| ui/components/table/virtual_table.py | Read ✓ |
| ui/config.py | Read ✓ |
| ui/effects/__init__.py | Read ✓ |
| ui/effects/hit_effects.py | Read ✓ |
| ui/filters/__init__.py | Read ✓ |
| ui/filters/filter_state.py | Read ✓ |
| ui/filters/filter_state_manager.py | Read ✓ |
| ui/fonts.py | Read ✓ |
| ui/interfaces/__init__.py | Read ✓ |
| ui/interfaces/battle_ui.py | Read ✓ |
| ui/orchestration/__init__.py | Read ✓ |
| ui/panels/__init__.py | Read ✓ |
| ui/panels/base_gallery.py | Read ✓ |
| ui/panels/battle_panels.py | Read ✓ |
| ui/panels/build_queue_controller.py | Read ✓ |
| ui/panels/build_queue_drag_handler.py | Read ✓ |
| ui/panels/build_queue_portraits.py | Read ✓ |
| ui/panels/builder_widgets.py | Read ✓ |
| ui/panels/component_modifier_grid_panel.py | Read ✓ |
| ui/panels/design_report_panel.py | Read ✓ |
| ui/panels/design_stats_panel.py | Read ✓ |
| ui/panels/empire_treasury_panel.py | Read ✓ |
| ui/panels/modifier_impact_grid.py | Read ✓ |
| ui/panels/planet_report_panel.py | Read ✓ |
| ui/panels/race_aptitudes_panel.py | Read ✓ |
| ui/panels/race_description_panel.py | Read ✓ |
| ui/panels/race_environment_panel.py | Read ✓ |
| ui/panels/race_summary_panel.py | Read ✓ |
| ui/panels/race_identity_panel.py | Read ✓ |
| ui/panels/ship_detail_panel.py | Read ✓ |
| ui/panels/ship_stats_renderer.py | Read ✓ |
| ui/panels/strategy_widgets.py | Read ✓ |
| ui/panels/system_tree_panel.py | Read ✓ |
| ui/panels/race_flag_gallery.py | Verified ✓ |
| ui/panels/race_portrait_gallery.py | Verified ✓ |
| ui/panels/race_theme_gallery.py | Verified ✓ |
| ui/renderer/__init__.py | Read ✓ |
| ui/renderer/camera.py | Read ✓ |
| ui/renderer/game_renderer.py | Read ✓ |
| ui/renderer/sprites.py | Read ✓ |
| ui/research/__init__.py | Read ✓ |
| ui/research/research_controls.py | Read ✓ |
| ui/research/research_renderer.py | Read ✓ |
| ui/research/research_scene.py | Read ✓ |
| ui/screens/__init__.py | Read ✓ |
| ui/screens/atmosphere_target_editor.py | Verified ✓ |
| ui/screens/battle_results_data.py | Verified ✓ |
| ui/screens/battle_results_screen.py | Verified ✓ |
| ui/screens/battle_screen.py | Read ✓ |
| ui/screens/battle_setup/__init__.py | Verified ✓ |
| ui/screens/battle_setup/constants.py | Verified ✓ |
| ui/screens/battle_setup/controller.py | Verified ✓ |
| ui/screens/battle_setup/fleet_hierarchy_editor.py | Verified ✓ |
| ui/screens/battle_setup/input_handler.py | Verified ✓ |
| ui/screens/battle_setup/panels/__init__.py | Verified ✓ |
| ui/screens/battle_setup/panels/center_panel.py | Verified ✓ |
| ui/screens/battle_setup/panels/left_panel.py | Verified ✓ |
| ui/screens/battle_setup/panels/right_panel.py | Verified ✓ |
| ui/screens/battle_setup/renderer.py | Verified ✓ |
| ui/screens/battle_setup/screen.py | Verified ✓ |
| ui/screens/battle_setup/spec_compiler.py | Verified ✓ |
| ui/screens/battle_setup/view_model.py | Verified ✓ |
| ui/screens/battle_setup_state.py | Verified ✓ |
| ui/screens/battle_state_viewer.py | Verified ✓ |
| ui/screens/battle_ui.py | Read ✓ |
| ui/screens/build_queue_helpers.py | Verified ✓ |
| ui/screens/build_queue_list_window.py | Verified ✓ |
| ui/screens/build_queue_panel_factory.py | Verified ✓ |
| ui/screens/build_queue_queue_data_source.py | Verified ✓ |
| ui/screens/build_queue_renderer.py | Verified ✓ |
| ui/screens/build_queue_screen.py | Verified ✓ |
| ui/screens/build_queue_selector.py | Verified ✓ |
| ui/screens/build_queue_viewmodel.py | Verified ✓ |
| ui/screens/builder/__init__.py | Verified ✓ |
| ui/screens/builder/components.py | Read ✓ |
| ui/screens/builder/detail_panel.py | Read ✓ |
| ui/screens/builder/drop_target.py | Read ✓ |
| ui/screens/builder/event_bus.py | Read ✓ |
| ui/screens/builder/grouping_strategies.py | Read ✓ |
| ui/screens/builder/interaction_controller.py | Read ✓ |
| ui/screens/builder/layer_panel.py | Read ✓ |
| ui/screens/builder/left_panel.py | Read ✓ |
| ui/screens/builder/modifier_config.py | Read ✓ |
| ui/screens/builder/modifier_logic.py | Read ✓ |
| ui/screens/builder/modifier_row.py | Read ✓ |
| ui/screens/builder/modifier_utils.py | Read ✓ |
| ui/screens/builder/panel_layout_config.py | Read ✓ |
| ui/screens/builder/right_panel.py | Read ✓ |
| ui/screens/builder/schematic_view.py | Read ✓ |
| ui/screens/builder/stat_definitions.py | Read ✓ |
| ui/screens/builder/stat_getters.py | Read ✓ |
| ui/screens/builder/stat_rows_dynamic.py | Read ✓ |
| ui/screens/builder/stats_config.py | Read ✓ |
| ui/screens/builder/structure_list_items.py | Read ✓ |
| ui/screens/builder/weapons_input_handler.py | Read ✓ |
| ui/screens/builder/weapons_panel.py | Read ✓ |
| ui/screens/builder/weapons_renderer.py | Read ✓ |
| ui/screens/builder/weapons_viewmodel.py | Read ✓ |
| ui/screens/builder_selection.py | Read ✓ |
| ui/screens/builder_utils.py | Read ✓ |
| ui/screens/cargo_quick_dialog.py | Verified ✓ |
| ui/screens/design_image_helper.py | Verified ✓ |
| ui/screens/design_selector_window.py | Verified ✓ |
| ui/screens/empire_build_queue_data_source.py | Verified ✓ |
| ui/screens/empire_build_queue_filter_manager.py | Verified ✓ |
| ui/screens/empire_build_queue_formatter.py | Verified ✓ |
| ui/screens/empire_build_queue_sidebar.py | Verified ✓ |
| ui/screens/empire_build_queue_viewmodel.py | Verified ✓ |
| ui/screens/empire_build_queue_window.py | Verified ✓ |
| ui/screens/empire_panel_window.py | Verified ✓ |
| ui/screens/event_log_data_source.py | Verified ✓ |
| ui/screens/event_log_sidebar.py | Verified ✓ |
| ui/screens/event_log_window.py | Verified ✓ |
| ui/screens/fleet_data_source.py | Verified ✓ |
| ui/screens/fleet_report_filters.py | Verified ✓ |
| ui/screens/fleet_report_sidebar.py | Verified ✓ |
| ui/screens/fleet_report_view_model.py | Verified ✓ |
| ui/screens/fleet_report_window.py | Verified ✓ |
| ui/screens/fleet_selection_window.py | Verified ✓ |
| ui/screens/food_allocation_editor.py | Verified ✓ |
| ui/screens/galaxy_test/__init__.py | Verified ✓ |
| ui/screens/galaxy_test/constants.py | Verified ✓ |
| ui/screens/galaxy_test/galaxy_mode.py | Verified ✓ |
| ui/screens/galaxy_test/screen.py | Verified ✓ |
| ui/screens/galaxy_test/system_mode.py | Verified ✓ |
| ui/screens/gravity_target_editor.py | Verified ✓ |
| ui/screens/keybindings_scene.py | Verified ✓ |
| ui/screens/menu_scene.py | Verified ✓ |
| ui/screens/new_game_setup_screen.py | Verified ✓ |
| ui/screens/orders_window.py | Verified ✓ |
| ui/screens/planet_abilities_window.py | Verified ✓ |
| ui/screens/planet_data_source.py | Verified ✓ |
| ui/screens/planet_list_filter_manager.py | Verified ✓ |
| ui/screens/planet_list_filters.py | Verified ✓ |
| ui/screens/planet_list_presets.py | Verified ✓ |
| ui/screens/planet_list_sidebar.py | Verified ✓ |
| ui/screens/planet_list_window.py | Verified ✓ |
| ui/screens/planet_selection_window.py | Verified ✓ |
| ui/screens/race_asset_loader.py | Verified ✓ |
| ui/screens/race_browser_dialog.py | Verified ✓ |
| ui/screens/race_setup/__init__.py | Verified ✓ |
| ui/screens/race_setup/controller.py | Verified ✓ |
| ui/screens/race_setup/input_handler.py | Verified ✓ |
| ui/screens/race_setup/llm_dialog_service.py | Verified ✓ |
| ui/screens/race_setup/panel_factory.py | Verified ✓ |
| ui/screens/race_setup/renderer.py | Verified ✓ |
| ui/screens/race_setup/screen.py | Verified ✓ |
| ui/screens/race_setup/ship_preview.py | Verified ✓ |
| ui/screens/race_setup/view_model.py | Verified ✓ |
| ui/screens/race_setup_screen.py | Verified ✓ |
| ui/screens/race_validator.py | Verified ✓ |
| ui/screens/radiation_shield_editor.py | Verified ✓ |
| ui/screens/save_selection_window.py | Verified ✓ |
| ui/screens/settings_window.py | Verified ✓ |
| ui/screens/setup_data_io.py | Verified ✓ |
| ui/screens/setup_renderer.py | Verified ✓ |
| ui/screens/setup_screen.py | Verified ✓ |
| ui/screens/species_selector_mixin.py | Verified ✓ |
| ui/screens/star_data_source.py | Verified ✓ |
| ui/screens/star_list_filter_manager.py | Verified ✓ |
| ui/screens/star_list_filters.py | Verified ✓ |
| ui/screens/star_list_presets.py | Verified ✓ |
| ui/screens/star_list_sidebar.py | Verified ✓ |
| ui/screens/star_list_window.py | Verified ✓ |
| ui/screens/strategy_build_queue_manager.py | Verified ✓ |
| ui/screens/strategy_camera_nav.py | Verified ✓ |
| ui/screens/strategy_click_dispatcher.py | Verified ✓ |
| ui/screens/strategy_colonization.py | Verified ✓ |
| ui/screens/strategy_detail_fmt.py | Verified ✓ |
| ui/screens/strategy_detail_formatter.py | Verified ✓ |
| ui/screens/strategy_event_router.py | Verified ✓ |
| ui/screens/strategy_fleet_command_router.py | Verified ✓ |
| ui/screens/strategy_fleet_ops.py | Verified ✓ |
| ui/screens/strategy_game_state_manager.py | Verified ✓ |
| ui/screens/strategy_input_handler.py | Verified ✓ |
| ui/screens/strategy_menu_panel.py | Verified ✓ |
| ui/screens/strategy_panel_manager.py | Verified ✓ |
| ui/screens/strategy_render/__init__.py | Verified ✓ |
| ui/screens/strategy_render/background.py | Verified ✓ |
| ui/screens/strategy_render/context.py | Verified ✓ |
| ui/screens/strategy_render/cursor.py | Verified ✓ |
| ui/screens/strategy_render/dyson_spheres.py | Verified ✓ |
| ui/screens/strategy_render/fleets.py | Verified ✓ |
| ui/screens/strategy_render/grid.py | Verified ✓ |
| ui/screens/strategy_render/hex_outlines.py | Verified ✓ |
| ui/screens/strategy_render/overlay.py | Verified ✓ |
| ui/screens/strategy_render/planets.py | Verified ✓ |
| ui/screens/strategy_render/storms.py | Verified ✓ |
| ui/screens/strategy_render/systems.py | Verified ✓ |
| ui/screens/strategy_render/warp_lanes.py | Verified ✓ |
| ui/screens/strategy_renderer.py | Read ✓ |
| ui/screens/strategy_screen.py | Read ✓ |
| ui/screens/strategy_superweapons.py | Verified ✓ |
| ui/screens/strategy_ui.py | Read ✓ |
| ui/screens/strategy_ui_action_router.py | Verified ✓ |
| ui/screens/strategy_window_manager.py | Verified ✓ |
| ui/screens/strategy_windows/__init__.py | Verified ✓ |
| ui/screens/strategy_windows/build_queue_windows.py | Verified ✓ |
| ui/screens/strategy_windows/dispatch.py | Verified ✓ |
| ui/screens/strategy_windows/empire_panel_ctrl.py | Verified ✓ |
| ui/screens/strategy_windows/event_log_window_ctrl.py | Verified ✓ |
| ui/screens/strategy_windows/fleet_report_ctrl.py | Verified ✓ |
| ui/screens/strategy_windows/list_windows.py | Verified ✓ |
| ui/screens/strategy_windows/move_choice_dialog.py | Verified ✓ |
| ui/screens/strategy_windows/orders_window_ctrl.py | Verified ✓ |
| ui/screens/strategy_windows/planet_abilities_ctrl.py | Verified ✓ |
| ui/screens/strategy_windows/selection_prompts.py | Verified ✓ |
| ui/screens/strategy_windows/ship_picker.py | Verified ✓ |
| ui/screens/strategy_windows/transfer_dialogs.py | Verified ✓ |
| ui/screens/system_selection_window.py | Verified ✓ |
| ui/screens/test_lab/__init__.py | Verified ✓ |
| ui/screens/test_lab/component_dropdown.py | Verified ✓ |
| ui/screens/test_lab/data_extractor.py | Verified ✓ |
| ui/screens/test_lab/details/__init__.py | Verified ✓ |
| ui/screens/test_lab/details/chrome.py | Verified ✓ |
| ui/screens/test_lab/details/draw_context.py | Verified ✓ |
| ui/screens/test_lab/details/panel.py | Verified ✓ |
| ui/screens/test_lab/details/propulsion_outcomes.py | Verified ✓ |
| ui/screens/test_lab/details/resource_outcomes.py | Verified ✓ |
| ui/screens/test_lab/details/validation.py | Verified ✓ |
| ui/screens/test_lab/dialogs.py | Verified ✓ |
| ui/screens/test_lab/formatting_utils.py | Verified ✓ |
| ui/screens/test_lab/panel_manager.py | Verified ✓ |
| ui/screens/test_lab/renderer/__init__.py | Verified ✓ |
| ui/screens/test_lab/renderer/_condition_logic.py | Verified ✓ |
| ui/screens/test_lab/renderer/_draw_helpers.py | Verified ✓ |
| ui/screens/test_lab/renderer/category_panel.py | Verified ✓ |
| ui/screens/test_lab/renderer/header_panel.py | Verified ✓ |
| ui/screens/test_lab/renderer/metadata_panel.py | Verified ✓ |
| ui/screens/test_lab/renderer/orchestrator.py | Verified ✓ |
| ui/screens/test_lab/renderer/tag_filter_panel.py | Verified ✓ |
| ui/screens/test_lab/renderer/test_list_panel.py | Verified ✓ |
| ui/screens/test_lab/renderer/validation_panel.py | Verified ✓ |
| ui/screens/test_lab/results_panel.py | Verified ✓ |
| ui/screens/test_lab/screen.py | Verified ✓ |
| ui/screens/test_lab/screen_input_handler.py | Verified ✓ |
| ui/screens/test_lab/ship_panels.py | Verified ✓ |
| ui/screens/test_lab/test_executor.py | Verified ✓ |
| ui/screens/test_lab/test_run_card.py | Verified ✓ |
| ui/screens/test_lab/test_run_details.py | Verified ✓ |
| ui/screens/test_lab/theme.py | Verified ✓ |
| ui/screens/test_lab/viewmodel.py | Verified ✓ |
| ui/screens/transfer_dialog.py | Verified ✓ |
| ui/screens/water_target_editor.py | Verified ✓ |
| ui/screens/workshop_context.py | Read ✓ |
| ui/screens/workshop_data_loader.py | Read ✓ |
| ui/screens/workshop_data_reloader.py | Read ✓ |
| ui/screens/workshop_event_router.py | Read ✓ |
| ui/screens/workshop_screen.py | Read ✓ |
| ui/screens/workshop_ship_io.py | Read ✓ |
| ui/screens/workshop_viewmodel.py | Read ✓ |
| ui/screens/workshop_viewmodel_layer_ops.py | Read ✓ |
| ui/screens/workshop_viewmodel_selection.py | Read ✓ |
| ui/screens/workshop_viewmodel_ship_ops.py | Read ✓ |
| ui/services/__init__.py | Read ✓ |
| ui/services/battle_ui_service.py | Read ✓ |
| ui/services/component_service.py | Read ✓ |
| ui/services/design_loader_adapter.py | Read ✓ |
| ui/services/game_settings.py | Read ✓ |
| ui/services/input_mapper.py | Read ✓ |
| ui/services/modifier_icon_service.py | Read ✓ |
| ui/services/ship_factory.py | Read ✓ |
| ui/services/ship_io.py | Verified ✓ |
| ui/services/ship_io_adapter.py | Verified ✓ |
| ui/services/tkinter_utils.py | Verified ✓ |
| ui/services/validation_service.py | Verified ✓ |
| ui/services/vehicle_class_service.py | Verified ✓ |
| ui/utils/__init__.py | Verified ✓ |
| ui/utils/formatters.py | Verified ✓ |
| ui/utils/json_diff.py | Verified ✓ |
| ui/utils/portraits.py | Verified ✓ |
| ui/utils/pygame_utils.py | Verified ✓ |
| ui/utils/resource_display.py | Verified ✓ |
| ui/widgets/__init__.py | Read ✓ |
| ui/widgets/dropdown_helper.py | Verified ✓ |
| ui/widgets/panel_factory.py | Verified ✓ |
| ui/widgets/preference_row.py | Verified ✓ |
| ui/widgets/scroll_state.py | Verified ✓ |
| ui/widgets/scrollable_json_panel.py | Verified ✓ |
| ui/widgets/ui_element_registry.py | Verified ✓ |

## Shrinkage Estimate
| Category | Files | Estimated LOC Savings |
|----------|-------|-----------------------|
| Dead code removal (ModifierLogic deprecation, _show_coming_soon, unused event constant) | 3 | 68 |
| Internal duplication consolidation (_rebuild_modifier_icons copy, resource icon loading, normalize_selection merge) | 6 | 132 |
| Quality refactors (race_summary formatter extraction, button dispatch table, dropdown loop) | 4 | 104 |
| Comment cleanup (battle_panels architectural comment) | 1 | 19 |
| **Total Estimated Shrinkage** | | **~323 LOC** |
