# Legacy Code Review: Shard 02
## Summary
- Shard: Shard 02
- Files in Scope: 177
- Files Actually Read: 177
- Total Findings: 5
- Critical: 0 | Major: 1 | Minor: 4 | Info: 0

## Module Alias Findings
No findings — deterministic scan returned zero module aliases in this shard.

## Init Re-export Findings
No findings from deterministic scan. Two re-export shims were identified during manual review (see Re-Export Shim Findings and Additional Legacy Indicators sections below).

## Deprecation Marker Findings
No findings — deterministic scan returned zero deprecation markers in this shard.

## Wrapper Delegate Findings
No findings — deterministic scan returned zero wrapper delegates in this shard.

## Name Pair Drift Findings
No findings — deterministic scan returned zero name-pair-drift entries in this shard.

## Save Migration Code Findings
No findings — deterministic scan returned zero save-migration code in this shard.

## Superseded Pattern Uses
#### MAJOR: Pattern 30 (Registrar Close-Callback) — stale slot cleanup in _handle_window_close
**ID:** LEG-02-001
**Location:** game/ui/screens/strategy_event_router.py:427-460
**Symbol:** `_handle_window_close` method
**Pattern:** #30 (Registrar Close-Callback), superseded by #31 (StrategyModalWindow)
**Production call sites:** 0 new call sites needed; the method fires on `UI_WINDOW_CLOSE` events
**Issue:** The `_handle_window_close` method (lines 427-460) manually clears 14 window reference slots on strategy_window_manager when `pygame_gui.UI_WINDOW_CLOSE` fires. At least 6 of these slots (`planet_list_window`, `star_list_window`, `fleet_report_window`, `empire_build_queue_window`, `event_log_window`, `empire_panel_window`) are StrategyModalWindow subclasses that already auto-deregister via Pattern #31. The slot-nulling is redundant for modal tracking but serves as caller-convenience pointer cleanup. The patterns doc (§30) permits "Legacy slot fields remain as caller-convenience pointers; they no longer provide modal tracking." However, 8 non-modal slots (`fleet_orders_window`, `transfer_dialog`, `build_queue_list_window`, `move_choice_window`, `cargo_quick_dialog`, `planet_selection_window`, `system_selection_window`, `fleet_selection_window`) are not covered by Pattern #31 and their close-callback cleanup remains the primary mechanism. This is a **MAJOR** finding: the close-callback pattern is active and relied upon for non-modal windows; the migration is incomplete for these 8 slots.
**Recommendation:** Migrate the 8 non-modal window slots to a consistent cleanup mechanism (either wrap them in StrategyModalWindow or add a dedicated non-modal slot-cleanup contract). Delete the 6 redundant StrategyModalWindow slot-clears from this method (they're already handled by Pattern #31 deregistration).
**LOC affected:** 34

## Re-Export Shim Findings
#### MINOR: stars.py — PROJ-372 backward-compat re-exports
**ID:** LEG-02-002
**Location:** game/strategy/data/stars.py:31-38
**Symbol:** `Spectrum`, `SOLAR_LUMINOSITY_W`, `SOLAR_MASS_KG`, `SOLAR_RADIUS_M`, `SOLAR_TEMP_K`, `WIEN_DISPLACEMENT_CONSTANT` (re-exported from `game.core.spectrum_math` and `game.strategy.data.spectrum`)
**Pattern:** #36 (Re-Export Shim) — documented and tracked
**Production call sites:** 15+ import sites per module docstring
**Issue:** PROJ-372 Phase 1 split spectral math to `game/core/spectrum_math` and Spectrum to `game/strategy/data/spectrum`. This module re-exports them for backward compatibility. The `__all__` entry for `StarGenerator` (line 45) references a class that IS NOT imported in this file — it was moved to `game/strategy/generation/star_generator.py`. Anyone doing `from game.strategy.data.stars import StarGenerator` will get `ImportError`.
**Recommendation:** (a) Remove `StarGenerator` from `__all__` immediately (it is a stale entry with no corresponding import). (b) Track migration of the 15+ call sites importing from this legacy path to import from `game.core.spectrum_math` directly, then delete the shim lines.
**LOC affected:** 12

#### MINOR: planet.py — extracted-class backward-compat re-exports
**ID:** LEG-02-003
**Location:** game/strategy/data/planet.py:22-25
**Symbol:** `PlanetaryFacility`, `SpeciesPopulation`, `ColonySpeciesConfig` (re-exported with `# noqa: F401`)
**Pattern:** #36 (Re-Export Shim) — documented PROJ-210 / PROJ-284
**Production call sites:** Unknown — the comment says "external readers using `from planet import ...` continue to resolve them"
**Issue:** PROJ-210 extracted `PlanetaryFacility` and `SpeciesPopulation` to their own modules; PROJ-284 added `ColonySpeciesConfig`. The re-exports preserve legacy import paths. Comment at line 19-21 documents the intent.
**Recommendation:** Audit `game/` for call sites importing these names from `game.strategy.data.planet` rather than from their canonical modules (`game.strategy.data.planetary_facility`, `game.strategy.data.species_population`, `game.strategy.data.colony_species_config`). When zero callers remain, delete the re-exports.
**LOC affected:** 7

## TYPE_CHECKING-Only Re-export Findings
No findings — deterministic scan returned zero TYPE_CHECKING-only re-exports in this shard.

## Optional Protocol Method Findings
No findings — deterministic scan returned zero optional protocol methods in this shard.

## Additional Legacy Indicators (Phase 1 did not catch)
#### MINOR: module-level mutable caches using `global` keyword
**ID:** LEG-02-004
**Location:** Multiple files
**Symbols:** `_production_rates_cache` (build_queue_source.py:34), `_ship_factory` (setup_data_io.py:30), `_cached_registries` (strategy_build_queue_manager.py:40, ship_io.py:39), `_PORTRAIT_THUMBNAIL_CACHE` (race_portrait_gallery.py:31), `_replay_store` (save_game_service.py:30)
**Production call sites:** N/A (module-internal state)
**Issue:** Six files use the `global` keyword for module-level mutable caches with lazy-init-on-first-access patterns. Four of these (`_cached_registries` ×2, `_ship_factory`, `_cached_registries`) duplicate the same `get_default_registry_provider() -> GameRegistries` lazy-init pattern. The PROJ-258 DI pattern (ApplicationContext) provides a canonical alternative, but these remain as localized lazy-init caches. This is a state management concern rather than a pure legacy issue — the `global` keyword is a code smell flagging opportunistic module-level mutation rather than structured DI. MINOR because the pattern is functional and bounded to single-module scope.
**Recommendation:** Consolidate the 4 duplicate `_cached_registries` / `_ship_factory` lazy-init blocks into a shared `_lazy_registries()` helper under `game/ui/services/` to reduce duplication. Consider migrating `_production_rates_cache` and `_replay_store` to the `get_default_*` / `set_default_*` pattern already documented in Pattern #1.
**LOC affected:** ~30 across 6 files

#### MINOR: stale PROJ-XX placeholder in paths.py comment
**ID:** LEG-02-005
**Location:** game/core/paths.py:98
**Symbol:** Comment `# PROJ-XX Star Expansion` on STAR_DIR definitions
**Production call sites:** N/A (comment only)
**Issue:** The comment references `PROJ-XX` as a placeholder project number that was never filled in. The star asset paths are actively used (star_list_filters.py, star_data_source.py import from these paths). This is stale documentation referencing a now-resolved or never-formally-tracked project.
**Recommendation:** Replace `PROJ-XX` with the actual PROJ number (likely PROJ-231 Star List Panel) or remove the marker if the feature was delivered outside the formal project system.
**LOC affected:** 1

## Verification Coverage
- Critical findings verified: 0/0 (no critical findings to verify)
- Major findings sampled: 1/1 (LEG-02-001 verified against strategy_event_router.py source)

## File Coverage Verification
| File | Status |
|------|--------|
| game/__init__.py | Read ✓ |
| game/ai/__init__.py | Read ✓ |
| game/ai/policy_manager.py | Read ✓ |
| game/ai/spatial_behaviors/base.py | Read ✓ |
| game/core/exceptions.py | Read ✓ |
| game/core/formula_evaluator.py | Read ✓ |
| game/core/paths.py | Read ✓ |
| game/core/patterns/layer_iterator.py | Read ✓ |
| game/core/profiling.py | Read ✓ |
| game/core/protocols/__init__.py | Read ✓ |
| game/core/roles.py | Read ✓ |
| game/core/spectrum_math.py | Read ✓ |
| game/core/validation_helpers.py | Read ✓ |
| game/engine/collision.py | Read ✓ |
| game/engine/physics.py | Read ✓ |
| game/research/data/__init__.py | Read ✓ |
| game/research/systems/__init__.py | Read ✓ |
| game/run_loop.py | Read ✓ |
| game/services/llm/deepseek.py | Read ✓ |
| game/simulation/__init__.py | Read ✓ |
| game/simulation/combat/combat_events.py | Read ✓ |
| game/simulation/combat/telemetry.py | Read ✓ |
| game/simulation/combat/weapon_firing_system.py | Read ✓ |
| game/simulation/components/abilities/colonize.py | Read ✓ |
| game/simulation/components/abilities/defense.py | Read ✓ |
| game/simulation/components/abilities/markers.py | Read ✓ |
| game/simulation/components/abilities/planetary/stabilizers.py | Read ✓ |
| game/simulation/components/abilities/planetary/terraforming.py | Read ✓ |
| game/simulation/components/abilities/propulsion.py | Read ✓ |
| game/simulation/components/abilities/superweapons.py | Read ✓ |
| game/simulation/components/abilities/ui_colors.py | Read ✓ |
| game/simulation/components/component_health_manager.py | Read ✓ |
| game/simulation/components/component_loader.py | Read ✓ |
| game/simulation/components/component_resource_manager.py | Read ✓ |
| game/simulation/components/modifier_effects.py | Read ✓ |
| game/simulation/components/modifier_introspection.py | Read ✓ |
| game/simulation/entities/ability_aggregator.py | Read ✓ |
| game/simulation/entities/combat_endurance.py | Read ✓ |
| game/simulation/entities/ship_combat_manager.py | Read ✓ |
| game/simulation/entities/ship_loader.py | Read ✓ |
| game/simulation/entities/stat_contributors/accumulator.py | Read ✓ |
| game/simulation/entities/stat_contributors/launch.py | Read ✓ |
| game/simulation/interfaces/__init__.py | Read ✓ |
| game/simulation/managers/__init__.py | Read ✓ |
| game/simulation/managers/battle_state_manager.py | Read ✓ |
| game/simulation/managers/retreat_manager.py | Read ✓ |
| game/simulation/projectile_manager.py | Read ✓ |
| game/simulation/replay/replay_capture.py | Read ✓ |
| game/simulation/replay/replay_serialization.py | Read ✓ |
| game/simulation/services/battle_service.py | Read ✓ |
| game/simulation/services/design_loader.py | Read ✓ |
| game/simulation/services/registry_loader.py | Read ✓ |
| game/simulation/systems/battle_setup.py | Read ✓ |
| game/simulation/systems/boundary_enforcement.py | Read ✓ |
| game/strategy/config/economy_config.py | Read ✓ |
| game/strategy/data/__init__.py | Read ✓ |
| game/strategy/data/build_queue_source.py | Read ✓ |
| game/strategy/data/design_metadata.py | Read ✓ |
| game/strategy/data/environmental_preference.py | Read ✓ |
| game/strategy/data/fleet.py | Read ✓ |
| game/strategy/data/fleet_pursuer_tracker.py | Read ✓ |
| game/strategy/data/galaxy_spatial_index.py | Read ✓ |
| game/strategy/data/galaxy_system_generator.py | Read ✓ |
| game/strategy/data/planet.py | Read ✓ |
| game/strategy/data/race_caption_loader.py | Read ✓ |
| game/strategy/data/resource_generation_config.py | Read ✓ |
| game/strategy/data/spatial_index.py | Read ✓ |
| game/strategy/data/squadron.py | Read ✓ |
| game/strategy/data/star_generation_config.py | Read ✓ |
| game/strategy/data/stars.py | Read ✓ |
| game/strategy/engine/commands/__init__.py | Read ✓ |
| game/strategy/engine/commands/registry.py | Read ✓ |
| game/strategy/engine/consumable_management_engine.py | Read ✓ |
| game/strategy/engine/empire_economy_calculator.py | Read ✓ |
| game/strategy/engine/handlers/build.py | Read ✓ |
| game/strategy/engine/handlers/movement.py | Read ✓ |
| game/strategy/engine/happiness_engine.py | Read ✓ |
| game/strategy/engine/harvesting_engine.py | Read ✓ |
| game/strategy/engine/order_handlers/__init__.py | Read ✓ |
| game/strategy/engine/order_handlers/join_fleet.py | Read ✓ |
| game/strategy/engine/production_engine.py | Read ✓ |
| game/strategy/engine/superweapon_handlers/close_warp_point.py | Read ✓ |
| game/strategy/engine/superweapon_handlers/stellerate_star.py | Read ✓ |
| game/strategy/engine/turn_state_snapshot.py | Read ✓ |
| game/strategy/engine/water_engine.py | Read ✓ |
| game/strategy/events/event_log.py | Read ✓ |
| game/strategy/events/event_types.py | Read ✓ |
| game/strategy/facade/dto/colony_demographic_view.py | Read ✓ |
| game/strategy/facade/dto/fleet_dto.py | Read ✓ |
| game/strategy/generation/density/primitives/geometric.py | Read ✓ |
| game/strategy/generation/density/primitives/radial.py | Read ✓ |
| game/strategy/generation/density/primitives/ring.py | Read ✓ |
| game/strategy/generation/loaders/astrophysics_loader.py | Read ✓ |
| game/strategy/generation/loaders/system_blueprints_loader.py | Read ✓ |
| game/strategy/interfaces/__init__.py | Read ✓ |
| game/strategy/services/ability_sources/planet_intrinsic.py | Read ✓ |
| game/strategy/services/ability_sources/system_archetype.py | Read ✓ |
| game/strategy/services/action_time_resolver.py | Read ✓ |
| game/strategy/services/empire_write_service.py | Read ✓ |
| game/strategy/services/fleet_navigation_service.py | Read ✓ |
| game/strategy/services/fleet_speed_calculator.py | Read ✓ |
| game/strategy/services/galaxy_pathfinding_service.py | Read ✓ |
| game/strategy/services/intercept_calculator.py | Read ✓ |
| game/strategy/services/replay_verification_coordinator.py | Read ✓ |
| game/strategy/services/superweapon_registry.py | Read ✓ |
| game/strategy/services/task_group_suggester.py | Read ✓ |
| game/strategy/systems/save_game_service.py | Read ✓ |
| game/strategy/validation/superweapon_validator.py | Read ✓ |
| game/strategy/validation/transfer_validator.py | Read ✓ |
| game/ui/components/table/data_source.py | Read ✓ |
| game/ui/components/table/selection.py | Read ✓ |
| game/ui/panels/build_queue_controller.py | Read ✓ |
| game/ui/panels/design_report_panel.py | Read ✓ |
| game/ui/panels/race_identity_panel.py | Read ✓ |
| game/ui/panels/race_portrait_gallery.py | Read ✓ |
| game/ui/panels/ship_detail_panel.py | Read ✓ |
| game/ui/panels/ship_stats_renderer.py | Read ✓ |
| game/ui/renderer/__init__.py | Read ✓ |
| game/ui/renderer/sprites.py | Read ✓ |
| game/ui/research/research_controls.py | Read ✓ |
| game/ui/research/research_scene.py | Read ✓ |
| game/ui/screens/__init__.py | Read ✓ |
| game/ui/screens/battle_results_data.py | Read ✓ |
| game/ui/screens/battle_setup/panels/__init__.py | Read ✓ |
| game/ui/screens/battle_state_viewer.py | Read ✓ |
| game/ui/screens/builder/__init__.py | Read ✓ |
| game/ui/screens/builder/modifier_config.py | Read ✓ |
| game/ui/screens/builder/stat_getters.py | Read ✓ |
| game/ui/screens/builder/structure_list_items.py | Read ✓ |
| game/ui/screens/builder/weapons_renderer.py | Read ✓ |
| game/ui/screens/design_image_helper.py | Read ✓ |
| game/ui/screens/empire_build_queue_sidebar.py | Read ✓ |
| game/ui/screens/empire_build_queue_window.py | Read ✓ |
| game/ui/screens/fleet_report_sidebar.py | Read ✓ |
| game/ui/screens/galaxy_test/galaxy_mode.py | Read ✓ |
| game/ui/screens/menu_scene.py | Read ✓ |
| game/ui/screens/planet_list_controller.py | Read ✓ |
| game/ui/screens/planet_list_filters.py | Read ✓ |
| game/ui/screens/planet_list_window.py | Read ✓ |
| game/ui/screens/race_setup/renderer.py | Read ✓ |
| game/ui/screens/race_setup/screen.py | Read ✓ |
| game/ui/screens/setup_data_io.py | Read ✓ |
| game/ui/screens/star_data_source.py | Read ✓ |
| game/ui/screens/star_list_filter_manager.py | Read ✓ |
| game/ui/screens/star_list_filters.py | Read ✓ |
| game/ui/screens/star_list_presets.py | Read ✓ |
| game/ui/screens/strategy_build_queue_manager.py | Read ✓ |
| game/ui/screens/strategy_click_dispatcher.py | Read ✓ |
| game/ui/screens/strategy_colonization.py | Read ✓ |
| game/ui/screens/strategy_detail_fmt.py | Read ✓ |
| game/ui/screens/strategy_event_router.py | Read ✓ |
| game/ui/screens/strategy_menu_panel.py | Read ✓ |
| game/ui/screens/strategy_modal_window.py | Read ✓ |
| game/ui/screens/strategy_panel_manager.py | Read ✓ |
| game/ui/screens/strategy_render/context.py | Read ✓ |
| game/ui/screens/strategy_render/hex_outlines.py | Read ✓ |
| game/ui/screens/strategy_render/planets.py | Read ✓ |
| game/ui/screens/strategy_renderer.py | Read ✓ |
| game/ui/screens/strategy_screen.py | Read ✓ |
| game/ui/screens/strategy_windows/__init__.py | Read ✓ |
| game/ui/screens/strategy_windows/build_queue_windows.py | Read ✓ |
| game/ui/screens/strategy_windows/fleet_report_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/list_windows.py | Read ✓ |
| game/ui/screens/test_lab/details/chrome.py | Read ✓ |
| game/ui/screens/test_lab/renderer/orchestrator.py | Read ✓ |
| game/ui/screens/test_lab/screen.py | Read ✓ |
| game/ui/screens/test_lab/test_executor.py | Read ✓ |
| game/ui/screens/test_lab/test_run_card.py | Read ✓ |
| game/ui/screens/transfer_grid_renderer.py | Read ✓ |
| game/ui/screens/water_target_editor.py | Read ✓ |
| game/ui/screens/workshop_data_reloader.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_ship_ops.py | Read ✓ |
| game/ui/services/image/defaults.py | Read ✓ |
| game/ui/services/ship_io.py | Read ✓ |
| game/ui/utils/formatters.py | Read ✓ |
| game/ui/utils/pygame_utils.py | Read ✓ |
| game/ui/widgets/scroll_state.py | Read ✓ |
