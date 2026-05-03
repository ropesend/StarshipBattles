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
| game/ui/screens/strategy_click_dispatcher.py | Production | Phase 4 — convert 5 superweapon click handlers (lines 283-354) to a table-driven dispatch (DUP-X-02) |
| game/ui/screens/strategy_superweapons.py | Production | Phase 4 — extract `_resolve_superweapon_target` helper from designation handlers (lines 119-310) (DUP-X-02) |
| game/strategy/engine/superweapon_command_handlers.py | Production | Phase 4 — extract `SuperweaponOrderHandler` base class (lines 73-372 across 10 handlers) (DUP-X-02) |
| game/ui/screens/planet_list_window.py | Production | Phase 4 — refactor onto `DataListWindow` base (DUP-X-03) |
| game/ui/screens/star_list_window.py | Production | Phase 4 — refactor onto `DataListWindow` base (DUP-X-03) |
| game/ui/screens/planet_list_sidebar.py | Production | Phase 4 — replace inline `add_range` with shared `build_range_slider_row` (lines 198-239) (DUP-X-03, DUP-X-07) |
| game/ui/screens/star_list_sidebar.py | Production | Phase 4 — replace inline `add_range` with shared `build_range_slider_row` (lines 93-134) (DUP-X-03, DUP-X-07) |
| game/ui/screens/planet_data_source.py | Production | Phase 4 — refactor onto base `ListDataSource` (lines 81-102) (DUP-X-03, DUP-X-14) |
| game/ui/screens/star_data_source.py | Production | Phase 4 — refactor onto base `ListDataSource` (lines 46-58) (DUP-X-03, DUP-X-14) |
| game/ui/screens/planet_list_filters.py | Production | Phase 4 — share sort-key utility with star_list_filters (part of DUP-X-03 list-window refactor) |
| game/ui/screens/star_list_filters.py | Production | Phase 4 — share sort-key utility with planet_list_filters (part of DUP-X-03 list-window refactor) |
| game/ui/screens/atmosphere_target_editor.py | Production | Phase 4 — adopt `RaceConfigResolverMixin` and `PlanetTargetEditor` base (DUP-X-04, DUP-X-05) |
| game/ui/screens/gravity_target_editor.py | Production | Phase 4 — adopt `RaceConfigResolverMixin` and `PlanetTargetEditor` base (DUP-X-04, DUP-X-05) |
| game/ui/screens/radiation_shield_editor.py | Production | Phase 4 — adopt `RaceConfigResolverMixin` and `PlanetTargetEditor` base (DUP-X-04, DUP-X-05) |
| game/ui/screens/water_target_editor.py | Production | Phase 4 — adopt `RaceConfigResolverMixin` and `PlanetTargetEditor` base (DUP-X-04, DUP-X-05) |
| game/ui/screens/species_selector_mixin.py | Production | Phase 4 — host new `RaceConfigResolverMixin` alongside existing `load_race_config` (line 111) (DUP-X-04) |
| game/ui/screens/strategy_event_router.py | Production | Phase 4 — extract `_open_planet_target_editor` (lines 213-269) (DUP-X-06) |
| game/ui/widgets/range_slider_builder.py | Production (NEW) | Phase 4 — host `build_range_slider_row(label, key, min_limit, max_limit, y_off, width, manager, container)` (DUP-X-07) |
| game/ui/screens/event_log_sidebar.py | Production | Phase 4 — replace `_build_column_section` (lines 57-92) with shared helper (DUP-X-08) |
| game/ui/screens/fleet_report_sidebar.py | Production | Phase 4 — replace `_build_column_section` (lines 315-343) with shared helper (DUP-X-08) |
| game/strategy/validation/superweapon_validator.py | Production | Phase 4 — extract `_validate_star_targeted_superweapon` (lines 99-125, 213-239) (DUP-X-09) |
| game/ui/screens/workshop_viewmodel_ship_ops.py | Production | Phase 4 — adopt `_with_ship` helper for guard+notify+log (lines 88-176) (DUP-X-10) |
| game/ui/screens/workshop_viewmodel_layer_ops.py | Production | Phase 4 — adopt `_with_ship` helper for guard+notify+log (lines 195-220) (DUP-X-10) |
| game/strategy/data/galaxy_system_generator.py | Production | Phase 4 — extract `_lazy_load_json_cache` (lines 223-237, 275-289, 324-334) and `_apply_intrinsic_abilities` (lines 240-268, 292-317) (DUP-X-11, DUP-X-12) |
| game/ai/spatial_behaviors/_formation_utils.py | Production (NEW) | Phase 4 — host `_compute_circular_position(anchor_x, anchor_y, distance, slot_index, total)` (DUP-X-13) |
| game/ai/spatial_behaviors/escort.py | Production | Phase 4 — call `_compute_circular_position` in `compute_target_position` (lines 26-52) (DUP-X-13) |
| game/ai/spatial_behaviors/screen.py | Production | Phase 4 — call `_compute_circular_position` in `compute_target_position` (lines 33-59) (DUP-X-13) |
