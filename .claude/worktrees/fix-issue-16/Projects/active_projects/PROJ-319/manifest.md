# PROJ-319 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/core/constants.py | Production | Phase 1 — remove dead enum member `GameState.FORMATION = 4` (line 29) |
| game/context.py | Production | Phase 1 — remove unused import `_ccm_mod` (line 116) |
| game/strategy/data/galaxy.py | Production | Phase 1 — remove unused parameter `naming_data_path` (line 624) |
| game/strategy/data/stars.py | Production | Phase 1 — remove unused parameter `age_ratio` (line 303) |
| game/strategy/data/planet_gen.py | Production | Phase 1 — remove unused import `MASS_MOON` (line 23) |
| game/strategy/data/design_metadata.py | Production | Phase 1 — remove unused `import warnings` (line 13) |
| game/strategy/engine/planet_action_engine.py | Production | Phase 1 — remove unused import `get_shield_info` (line 25) |
| game/strategy/facade/dto/fleet_dto.py | Production | Phase 1 — remove unused TYPE_CHECKING import `FleetType` (line 11) |
| game/strategy/services/action_time_resolver.py | Production | Phase 1 — remove unreachable `return 1` (line 115) |
| game/ui/panels/modifier_impact_grid.py | Production | Phase 1 — remove unused parameter `sig_digits` (line 273) |
| game/ui/screens/test_lab/screen.py | Production | Phase 1 — remove unused import `ConfirmationDialog` (line 32) |
| game/ui/services/ship_io_adapter.py | Production | Phase 1 — remove unused TYPE_CHECKING import `ShipIOType` (line 19) |
| game/ui/screens/galaxy_test/system_mode.py | Production | Phase 1 — remove unused import `STAR_FALLBACK` (line 17) |
| game/ui/screens/build_queue_selector.py | Production | Phase 1 — remove redundant `y_offset = 0` assignment (audit said line 99; actual redundant pair is lines 97 + 100) |
| game/simulation/battle_runner.py | Production | Phase 2 — delete dead method `_extract_weapon_summaries` (lines 647-671, 25 LOC) |
| game/ui/screens/strategy_detail_fmt.py | Production | Phase 2 — delete dead helper `_planet_has_shield_facility` (lines 316-347, 32 LOC) |
| game/strategy/services/race_resolver.py | Production (NEW) | Phase 4 — host shared `resolve_race_config(race_id, empire, race_registry)` (DUP-X-01, DUP-X-04) |
| game/strategy/engine/happiness_engine.py | Production | Phase 4 — replace local `_get_race_config` (lines 130-159) with `race_resolver.resolve_race_config` (DUP-X-01) |
| game/strategy/engine/population_engine.py | Production | Phase 4 — replace local `_get_race_config` (lines 164-193) with `race_resolver.resolve_race_config` (DUP-X-01) |
| game/ui/screens/strategy_click_dispatcher.py | Production | Phase 4 — convert 5 superweapon click handlers (lines 283-354) to a `_handle_superweapon_click(designation_method)` helper + 5 thin wrappers (DUP-X-02) |
| game/ui/screens/strategy_superweapons.py | Production (UNCHANGED) | Phase 4 — `_resolve_superweapon_target` extraction was DEFERRED. The audit recommended this consolidation but the additional savings (~30 LOC across 2 of 5 designation handlers) didn't justify the complexity given UI divergence (confirmation dialog vs system picker). Listed here for traceability only — `git diff HEAD~1 HEAD -- game/ui/screens/strategy_superweapons.py` shows no actual diff. See decisions.md row 4. |
| game/strategy/engine/superweapon_command_handlers.py | Production | Phase 4 — six direct command handlers refactored to use `_emit_validated_order` helper on `BaseCommandHandler` (DUP-X-02) |
| game/strategy/engine/handlers/base.py | Production | Phase 4 — added `_emit_validated_order(fleet, order_type, target, result, log_label)` static helper on `BaseCommandHandler` to consolidate the validate→add_order→log tail of every superweapon direct command handler (DUP-X-02) |
| game/ui/screens/planet_list_window.py | Production | Phase 4 — refactor onto `DataListWindowMixin`; replace inline `update()` slider-text-sync, `_toggle_column`, and `_save_preset` with mixin methods (DUP-X-03) |
| game/ui/screens/star_list_window.py | Production | Phase 4 — refactor onto `DataListWindowMixin`; same scope as planet variant (DUP-X-03) |
| game/ui/screens/planet_list_sidebar.py | Production | Phase 4 — replace inline `add_range` with shared `build_range_slider_row` (lines 198-239) (DUP-X-03, DUP-X-07) |
| game/ui/screens/star_list_sidebar.py | Production | Phase 4 — replace inline `add_range` with shared `build_range_slider_row` (lines 93-134) (DUP-X-03, DUP-X-07) |
| game/ui/screens/planet_data_source.py | Production | Phase 4 — refactor onto base `ListDataSource`; only `_render_icon` overridden (DUP-X-03, DUP-X-14) |
| game/ui/screens/star_data_source.py | Production | Phase 4 — refactor onto base `ListDataSource`; only `_render_icon` overridden (DUP-X-03, DUP-X-14) |
| game/ui/screens/planet_list_filters.py | Production | Phase 6 — adopt `make_attr_sort_key(col)` factory from `list_filter_utils.py` (DUP-X-17 / OpenCode H3 remediation; the original PROJ-319 Task 4.14 claim that the sort-key was absorbed by DUP-X-03 was incorrect — see phase_6_checklist.md) |
| game/ui/screens/star_list_filters.py | Production | Phase 6 — adopt `make_attr_sort_key(col)` factory from `list_filter_utils.py` (DUP-X-17 / OpenCode H3 remediation) |
| game/ui/screens/atmosphere_target_editor.py | Production | Phase 4 — adopt `RaceConfigResolverMixin` and `PlanetTargetEditor` base (DUP-X-04, DUP-X-05) |
| game/ui/screens/gravity_target_editor.py | Production | Phase 4 — adopt `RaceConfigResolverMixin` and `PlanetTargetEditor` base (DUP-X-04, DUP-X-05) |
| game/ui/screens/radiation_shield_editor.py | Production | Phase 4 — adopt `RaceConfigResolverMixin` and `PlanetTargetEditor` base (DUP-X-04, DUP-X-05) |
| game/ui/screens/water_target_editor.py | Production | Phase 4 — adopt `RaceConfigResolverMixin` and `PlanetTargetEditor` base (DUP-X-04, DUP-X-05) |
| game/ui/screens/species_selector_mixin.py | Production | Phase 4 — host new `RaceConfigResolverMixin` alongside existing `load_race_config` (line 111) (DUP-X-04) |
| game/ui/screens/planet_target_editor_base.py | Production (NEW) | Phase 4 — `PlanetTargetEditor` base class (subclasses `RaceConfigResolverMixin, StrategyModalWindow`) hosting `process_event` button-dispatch + close-callback wiring (DUP-X-05) |
| game/ui/screens/strategy_event_router.py | Production | Phase 4 — extract `_open_planet_target_editor` (lines 213-269) (DUP-X-06) |
| game/ui/widgets/range_slider_builder.py | Production (NEW) | Phase 4 — host `build_range_slider_row(label, key, min_limit, max_limit, y_off, width, manager, container)` (DUP-X-07) |
| game/ui/widgets/column_toggle_section.py | Production (NEW) | Phase 4 — host `build_column_toggle_section(y, column_manager, sidebar_width, manager, container)` (DUP-X-08) |
| game/ui/screens/event_log_sidebar.py | Production | Phase 4 — replace `_build_column_section` (lines 57-92) with shared helper (DUP-X-08) |
| game/ui/screens/fleet_report_sidebar.py | Production | Phase 4 — replace `_build_column_section` (lines 315-343) with shared helper (DUP-X-08) |
| game/strategy/validation/superweapon_validator.py | Production | Phase 4 — extract `_validate_star_targeted_superweapon` (lines 99-125, 213-239) (DUP-X-09) |
| game/ui/screens/workshop_viewmodel.py | Production | Phase 4 — added `_with_ship(op_name, service_call, on_success, on_failure)` helper on `WorkshopViewModel` to consolidate guard + notify + log pattern used by all four ship-op methods (DUP-X-10) |
| game/ui/screens/workshop_viewmodel_ship_ops.py | Production | Phase 4 — adopt `_with_ship` helper for `add_component`, `add_component_instance`, `remove_component` (DUP-X-10) |
| game/ui/screens/workshop_viewmodel_layer_ops.py | Production | Phase 4 — adopt `_with_ship` helper for `move_component` (DUP-X-10) |
| game/strategy/data/galaxy_system_generator.py | Production | Phase 4 — extract `_load_json_or_empty(path_value, dict_key)` and `_apply_intrinsic_abilities(entities, types_data, get_type_key, rng)` helpers (DUP-X-11, DUP-X-12) |
| game/ai/spatial_behaviors/_formation_utils.py | Production (NEW) | Phase 4 — host `compute_circular_position(anchor_x, anchor_y, distance, slot_index, total)` (DUP-X-13). Note: name has no leading underscore — deliberate deviation from the audit's `_compute_circular_position` recommendation since it's a public helper consumed by sibling modules (see phase_4_checklist.md Task 4.7). |
| game/ai/spatial_behaviors/escort.py | Production | Phase 4 — call `compute_circular_position` in `compute_target_position` (lines 26-52) (DUP-X-13) |
| game/ai/spatial_behaviors/screen.py | Production | Phase 4 — call `compute_circular_position` in `compute_target_position` (lines 33-59) (DUP-X-13) |
| game/ui/screens/list_data_source_base.py | Production (NEW) | Phase 4 — `ListDataSource` base class hosting column lookup, value extraction, icon caching, row-count plumbing; subclasses override `_render_icon` (DUP-X-14) |
| game/ui/screens/data_list_window_mixin.py | Production (NEW) | Phase 4 — `DataListWindowMixin` providing `_toggle_column`, `_save_preset`, `_sync_slider_text` for `PlanetListWindow` and `StarListWindow` (DUP-X-03) |
| game/ui/screens/list_filter_utils.py | Production (NEW) | Phase 6 — host `make_attr_sort_key(col)` sort-key factory shared by `planet_list_filters.py:221` and `star_list_filters.py:134` (DUP-X-17 / OpenCode H3 remediation) |
| tests/integration/strategy/test_planet_physics.py | Test | Phase 1 follow-up — re-import `MASS_MOON` from `planet_physics` (definition site) instead of `planet_gen` (re-export hub broken by C4 deletion) |
| tests/unit/ui/screens/test_event_log_sidebar.py | Test | Phase 4 follow-up (DUP-X-08) — patched `UILabel`/`UIButton` mocks to point at `game.ui.widgets.column_toggle_section` after the helper extraction moved the symbols out of the sidebar module |
| tests/unit/ui/screens/test_fleet_report_sidebar.py | Test | Phase 4 follow-up (DUP-X-08) — same patch update for the sidebar fixture |
| tests/unit/ui/screens/test_fleet_report_window_multi_select.py | Test | Phase 4 follow-up (DUP-X-08) — same patch update for the `TestRemoveButtonState.sidebar_with_button` fixture |
| tests/unit/ui/screens/test_planet_list_components.py | Test | Phase 4 follow-up (DUP-X-07) — added patches for `game.ui.widgets.range_slider_builder.{UILabel, UIHorizontalSlider, UITextEntryLine}` after slider widgets moved out of the sidebar module |
