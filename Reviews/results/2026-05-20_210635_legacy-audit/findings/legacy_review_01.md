# Legacy Code Review: Shard 01
## Summary
- Shard: Shard 01
- Files in Scope: 217
- Files Actually Read: 217
- Total Findings: 7
- Critical: 1 | Major: 0 | Minor: 5 | Info: 1

## Module Alias Findings
No module aliases detected by Phase 1 in this shard. Manual review confirms: no undocumented `OldName = NewName` patterns found.

## __init__.py Re-export Shim Findings

#### MINOR: Planetary abilities package re-export shim
**ID:** LEG-01-001
**Location:** game/simulation/components/abilities/planetary/__init__.py:1-59
**Symbol:** Package __init__ re-exports all sub-module classes
**Production call sites:** N/A (legacy import path preserved)
**Issue:** The original 913-LOC `planetary.py` was decomposed into a package by PROJ-382 Phase 5. The `__init__.py` re-exports every ability class so `from game.simulation.components.abilities.planetary import X` continues to work. This is a documented Pattern #36 (Re-Export Shim) — the docstring explicitly states the purpose. The shim references PROJ-382 which is tracked/active. No migration plan for caller consolidation yet.
**Recommendation:** Documented Pattern #36 shim — leave as-is until caller migration project completes. Each sub-module also has a docstring noting the same decomposition.
**LOC affected:** 59

## Deprecation Marker Findings

#### MINOR: Legacy carried_items documentation comment
**ID:** LEG-01-002
**Location:** game/strategy/data/ship_instance.py:170
**Symbol:** `# legacy ``carried_items: List[Dict[str, Any]]`` mixed-shape list.`
**Production call sites:** N/A (comment only)
**Issue:** Documentation marker describing the PROJ-431 → PROJ-436 Phase 9 migration from legacy `carried_items` mixed-shape list to typed `BayInventory`. The comment is informative (documents the migration history) and not a stale TODO. The `carried_items` property was removed in PROJ-436 Phase 9; this comment tours the removed surface.
**Recommendation:** MINOR — the comment is slightly misleading since the property was already deleted. Keep but tighten wording to past tense ("was the legacy"). No code removal needed (comment only).
**LOC affected:** 1

#### MINOR: Legacy carried_items dict-list shape comment
**ID:** LEG-01-003
**Location:** game/strategy/data/ship_instance.py:180
**Symbol:** `# legacy dict-list shape — see ``carried_items`` property.`
**Production call sites:** N/A (comment only)
**Issue:** Same context as LEG-01-002 — documents the `carried_items` property that was removed in PROJ-436 Phase 9. The comment references a property that no longer exists.
**Recommendation:** Update or remove — the referenced `carried_items` property is deleted. Past-tense note or removal.
**LOC affected:** 1

#### MINOR: Legacy carried_items serializer comment
**ID:** LEG-01-004
**Location:** game/strategy/data/ship_instance_serializer.py:62
**Symbol:** `# legacy ``carried_items`` dict-list shape is no longer the`
**Production call sites:** N/A (comment only)
**Issue:** Documents that the serializer no longer emits `carried_items`, instead emitting `bay_inventory`. Informative migration comment — not stale.
**Recommendation:** MINOR — docs quality improvement. Consider adding a removal date or project reference.
**LOC affected:** 1

## Wrapper Delegate Findings

#### INFO: create_modifier factory method (Phase 1 false positive)
**ID:** LEG-01-005
**Location:** game/simulation/components/component_constants.py:45
**Symbol:** `Modifier.create_modifier(value=None) -> ApplicationModifier`
**Production call sites:** N/A (Phase 1 flagged as wrapper, but it's a factory method)
**Issue:** Phase 1 deterministic scan flagged `create_modifier` as a "wrapper delegate" because its body is a single `return ApplicationModifier(self, value)` call. However, this is a standard factory method (Pattern #15) on the `Modifier` class — it constructs an `ApplicationModifier` instance. The `Modifier` class is the definition; `ApplicationModifier` is the applied instance. This is NOT a legacy shim/wrapper — it's the canonical construction path.
**Recommendation:** Not a finding. This is the documented Factory pattern. Phase 1 false positive.
**LOC affected:** 2

#### INFO: calc_damage_at_range local closure (Phase 1 false positive)
**ID:** LEG-01-006
**Location:** game/ui/screens/builder/weapons_viewmodel.py:392
**Symbol:** `calc_damage_at_range(r) -> Any` (local function inside `_compute_points_of_interest`)
**Production call sites:** 0 (local scope only, called 6 times within the enclosing method)
**Issue:** Phase 1 deterministic scan flagged this as a "wrapper delegate" because its body is `return ab.get_damage(r)`. However, this is a **local closure** defined inside `_compute_points_of_interest()`, not a module-level or class-level function. It exists solely to provide a consistent call signature for the points-of-interest computation loop alongside `calc_accuracy_at_range`. It is not a public API surface and cannot have external call sites.
**Recommendation:** Not a finding. Local convenience closure — not legacy code. Phase 1 false positive.
**LOC affected:** 2

## Name-Pair Drift Findings
No name-pair drift detected by Phase 1 in this shard. Manual review confirms no undocumented duplicate system pairs.

## Save Migration Code Findings
No save migration code detected. Verified against AGENTS.md Rule 4 — this shard is clean.

## Superseded Pattern Usage Findings

#### MINOR: Registrar Close-Callback slot cleanup (Pattern #30)
**ID:** LEG-01-007
**Location:** game/ui/screens/planet_abilities_window.py:178-231
**Symbol:** `_on_close_callback` parameter + invocation in `kill()`
**Production call sites:** 1 registrar (`StrategyWindowManager` slot cleanup)
**Issue:** `PlanetAbilitiesWindow` accepts an `on_close_callback` and invokes it in `kill()` before `super().kill()`. This is Pattern #30 (Registrar Close-Callback), superseded by Pattern #31 (Strategy Modal Window Base Class). However, **this is the documented "legacy slot cleanup only" use** per `docs/02_PATTERNS.md` line 652: "Legacy window registrars may still own convenience slots on `StrategyWindowManager`." The class already extends `StrategyModalWindow` (Pattern #31) for modal tracking; the `on_close_callback` is for the registrar's slot-clear convenience pointer, not for modal tracking. This matches the documented Pattern #30 exception.
**Recommendation:** MINOR — documented legacy slot cleanup. No action needed unless the slot tracking mechanism is migrated away from convenience pointers.
**LOC affected:** 8

## TYPE_CHECKING Re-export Findings
No TYPE_CHECKING re-exports detected in this shard.

## Partial Protocol Implementer Findings
No partial protocol implementers detected in this shard.

## Additional Legacy Indicators (Phase 1 did not catch)

#### CRITICAL: Backward-compat DamageContext re-export with zero callers
**ID:** LEG-01-008
**Location:** game/simulation/combat/combat_events.py:62
**Symbol:** `from game.core.combat_types import DamageContext  # noqa: F401`
**Production call sites:** 0 (via combat_events import path)
**Issue:** `combat_events.py` re-imports `DamageContext` from `game.core.combat_types` at module level with the comment "Re-exported here for backward compatibility." The `# noqa: F401` confirms it's intentionally unused within this file — it exists solely to preserve the old import path `from game.simulation.combat.combat_events import DamageContext`. A grep across all of `game/` confirms **zero production files** import `DamageContext` from `combat_events.py`. All consumers (collision.py:53, damage_calculator.py:28, projectile_manager.py:148, combat_events.py:82 for type annotation) import directly from `game.core.combat_types`. Even the `combat_events.py` docstring example (line 20) references `DamageContext` from `game.core.combat_types`. This import line can be removed in a single-PR delete.
**Recommendation:** Delete the re-export line. Zero callers against the legacy path. The canonical `game.core.combat_types` import is well-established.
**LOC affected:** 1

#### MINOR: Stale PROJ-58/PROJ-298 comment references
No stale PROJ comment references found in this shard. All PROJ references checked against active/archived project indices.

#### MINOR: test-only set_default_registry_manager
**ID:** LEG-01-009
**Location:** game/core/registry.py:287-301
**Symbol:** `set_default_registry_manager`
**Production call sites:** 1 (`ApplicationContext.create_production()` at game/context.py:175)
**Issue:** `set_default_registry_manager` is called only from `ApplicationContext.create_production()` during bootstrap. It's part of the documented PROJ-258 DI pattern (module-level `_default_manager` reference with getter/setter pair). However, it fits the "unused `set_default_*` shim" pattern — its only caller is the composition root.
**Recommendation:** MINOR — part of the documented DI pattern. Consider consolidating into the bootstrap path directly rather than maintaining a module-level accessor pair.
**LOC affected:** 15

## Verification Coverage
- Critical findings verified: 1/1 (LEG-01-008 verified by grep across all of `game/`)
- Major findings sampled: 0/0 (no MAJOR findings to sample)

## File Coverage Verification
| File | Status |
|------|--------|
| game/__init__.py | Read ✓ |
| game/ai/ai_factory.py | Read ✓ |
| game/ai/combat_utils.py | Read ✓ |
| game/ai/spatial_behaviors/__init__.py | Read ✓ |
| game/ai/spatial_behaviors/escort.py | Read ✓ |
| game/ai/spatial_behaviors/patrol_zone.py | Read ✓ |
| game/core/combat_types.py | Read ✓ |
| game/core/event_logging.py | Read ✓ |
| game/core/formula_evaluator.py | Read ✓ |
| game/core/paths.py | Read ✓ |
| game/core/protocols/boundary.py | Read ✓ |
| game/core/protocols/combat.py | Read ✓ |
| game/core/registry.py | Read ✓ |
| game/core/return_destination.py | Read ✓ |
| game/core/roles.py | Read ✓ |
| game/core/state_machine.py | Read ✓ |
| game/core/validation.py | Read ✓ |
| game/engine/collision.py | Read ✓ |
| game/research/__init__.py | Read ✓ |
| game/research/data/__init__.py | Read ✓ |
| game/research/systems/research_service.py | Read ✓ |
| game/screen_router.py | Read ✓ |
| game/services/__init__.py | Read ✓ |
| game/services/llm/defaults.py | Read ✓ |
| game/services/provider_factory.py | Read ✓ |
| game/simulation/battle_config.py | Read ✓ |
| game/simulation/combat/ability_stat_registry.py | Read ✓ |
| game/simulation/combat/combat_events.py | Read ✓ |
| game/simulation/combat/families/beam.py | Read ✓ |
| game/simulation/combat/modifier_stack.py | Read ✓ |
| game/simulation/combat/weapon_firing_system.py | Read ✓ |
| game/simulation/components/abilities/__init__.py | Read ✓ |
| game/simulation/components/abilities/cargo.py | Read ✓ |
| game/simulation/components/abilities/colonize.py | Read ✓ |
| game/simulation/components/abilities/crew.py | Read ✓ |
| game/simulation/components/abilities/harvester.py | Read ✓ |
| game/simulation/components/abilities/launch.py | Read ✓ |
| game/simulation/components/abilities/planetary/__init__.py | Read ✓ |
| game/simulation/components/abilities/planetary/resource_modifiers.py | Read ✓ |
| game/simulation/components/abilities/planetary/stabilizers.py | Read ✓ |
| game/simulation/components/abilities/planetary/terraforming.py | Read ✓ |
| game/simulation/components/abilities/stat_keys.py | Read ✓ |
| game/simulation/components/abilities/warhead.py | Read ✓ |
| game/simulation/components/component_constants.py | Read ✓ |
| game/simulation/components/component_resource_manager.py | Read ✓ |
| game/simulation/components/modifiers.py | Read ✓ |
| game/simulation/entities/combat_endurance.py | Read ✓ |
| game/simulation/entities/ship_loader.py | Read ✓ |
| game/simulation/entities/ship_resource_manager.py | Read ✓ |
| game/simulation/entities/ship_stats.py | Read ✓ |
| game/simulation/interfaces/__init__.py | Read ✓ |
| game/simulation/interfaces/ability_protocols.py | Read ✓ |
| game/simulation/managers/retreat_manager.py | Read ✓ |
| game/simulation/physics_constants.py | Read ✓ |
| game/simulation/replay/replay_player.py | Read ✓ |
| game/simulation/replay/replay_record.py | Read ✓ |
| game/simulation/replay/replay_spec.py | Read ✓ |
| game/simulation/replay/replay_verifier.py | Read ✓ |
| game/simulation/services/__init__.py | Read ✓ |
| game/simulation/services/vehicle_design_service.py | Read ✓ |
| game/simulation/systems/boundary_enforcement.py | Read ✓ |
| game/simulation/systems/resource_manager.py | Read ✓ |
| game/simulation/validation/ship_validator.py | Read ✓ |
| game/strategy/__init__.py | Read ✓ |
| game/strategy/adapters/__init__.py | Read ✓ |
| game/strategy/data/__init__.py | Read ✓ |
| game/strategy/data/carried_vehicle.py | Read ✓ |
| game/strategy/data/carried_vehicle_deploy.py | Read ✓ |
| game/strategy/data/empire.py | Read ✓ |
| game/strategy/data/fleet_battle_adapter.py | Read ✓ |
| game/strategy/data/galaxy_entity_registry.py | Read ✓ |
| game/strategy/data/galaxy_protocols.py | Read ✓ |
| game/strategy/data/order_serializer.py | Read ✓ |
| game/strategy/data/ship_consumable_manager.py | Read ✓ |
| game/strategy/data/ship_instance.py | Read ✓ |
| game/strategy/data/ship_instance_serializer.py | Read ✓ |
| game/strategy/data/spatial_index.py | Read ✓ |
| game/strategy/data/species_population.py | Read ✓ |
| game/strategy/data/star_generation_config.py | Read ✓ |
| game/strategy/engine/atmosphere_engine.py | Read ✓ |
| game/strategy/engine/conflict_modifier_collection.py | Read ✓ |
| game/strategy/engine/consumable_management_engine.py | Read ✓ |
| game/strategy/engine/game_config.py | Read ✓ |
| game/strategy/engine/handlers/base.py | Read ✓ |
| game/strategy/engine/handlers/build.py | Read ✓ |
| game/strategy/engine/handlers/lay_mines.py | Read ✓ |
| game/strategy/engine/handlers/registry_factory.py | Read ✓ |
| game/strategy/engine/order_handlers/__init__.py | Read ✓ |
| game/strategy/engine/order_handlers/base.py | Read ✓ |
| game/strategy/engine/order_handlers/colonize.py | Read ✓ |
| game/strategy/engine/order_handlers/transfer.py | Read ✓ |
| game/strategy/engine/planet_energy_engine.py | Read ✓ |
| game/strategy/engine/production_spawner.py | Read ✓ |
| game/strategy/engine/superweapon_handlers/__init__.py | Read ✓ |
| game/strategy/engine/superweapon_handlers/close_warp_point.py | Read ✓ |
| game/strategy/engine/superweapon_handlers/stellerate_star.py | Read ✓ |
| game/strategy/facade/dto/build_queue_dto.py | Read ✓ |
| game/strategy/facade/dto/planet_dto.py | Read ✓ |
| game/strategy/facade/slices/_facade_state.py | Read ✓ |
| game/strategy/facade/slices/economy_slice.py | Read ✓ |
| game/strategy/facade/slices/event_slice.py | Read ✓ |
| game/strategy/facade/strategy_session_facade.py | Read ✓ |
| game/strategy/generation/density/__init__.py | Read ✓ |
| game/strategy/generation/density/density_map.py | Read ✓ |
| game/strategy/generation/density/primitives/linear.py | Read ✓ |
| game/strategy/generation/density/primitives/radial.py | Read ✓ |
| game/strategy/generation/loaders/__init__.py | Read ✓ |
| game/strategy/generation/planet_image_registry.py | Read ✓ |
| game/strategy/generation/star_image_registry.py | Read ✓ |
| game/strategy/interfaces/__init__.py | Read ✓ |
| game/strategy/interfaces/engines/population.py | Read ✓ |
| game/strategy/quickstart_builder.py | Read ✓ |
| game/strategy/services/ability_iterator.py | Read ✓ |
| game/strategy/services/ability_sources/__init__.py | Read ✓ |
| game/strategy/services/ability_sources/fleet.py | Read ✓ |
| game/strategy/services/ability_sources/labels.py | Read ✓ |
| game/strategy/services/ability_sources/storm.py | Read ✓ |
| game/strategy/services/cargo_transfer_service.py | Read ✓ |
| game/strategy/services/component_abilities.py | Read ✓ |
| game/strategy/services/effect_ability_display.py | Read ✓ |
| game/strategy/services/empire_economy_service.py | Read ✓ |
| game/strategy/services/fleet_warp_resolution.py | Read ✓ |
| game/strategy/services/intercept_calculator.py | Read ✓ |
| game/strategy/services/planet_query_service.py | Read ✓ |
| game/strategy/services/replay_resolver.py | Read ✓ |
| game/strategy/services/stabilizer_registry.py | Read ✓ |
| game/strategy/services/strategic_ability_scanner.py | Read ✓ |
| game/strategy/services/task_group_suggester.py | Read ✓ |
| game/strategy/systems/race_library.py | Read ✓ |
| game/strategy/systems/save_game_service.py | Read ✓ |
| game/ui/components/filters/tri_state_widget.py | Read ✓ |
| game/ui/components/table/data_source.py | Read ✓ |
| game/ui/components/table/header.py | Read ✓ |
| game/ui/panels/base_gallery.py | Read ✓ |
| game/ui/panels/build_queue_controller.py | Read ✓ |
| game/ui/panels/design_stats_panel.py | Read ✓ |
| game/ui/panels/modifier_impact_grid.py | Read ✓ |
| game/ui/panels/race_environment_panel.py | Read ✓ |
| game/ui/panels/race_flag_gallery.py | Read ✓ |
| game/ui/panels/race_identity_panel.py | Read ✓ |
| game/ui/panels/race_summary_panel.py | Read ✓ |
| game/ui/panels/race_theme_gallery.py | Read ✓ |
| game/ui/renderer/__init__.py | Read ✓ |
| game/ui/research/__init__.py | Read ✓ |
| game/ui/screens/battle_results_data.py | Read ✓ |
| game/ui/screens/battle_results_screen.py | Read ✓ |
| game/ui/screens/battle_setup/input_handler.py | Read ✓ |
| game/ui/screens/battle_setup/panels/__init__.py | Read ✓ |
| game/ui/screens/battle_setup/panels/center_panel.py | Read ✓ |
| game/ui/screens/battle_setup/spec_compiler.py | Read ✓ |
| game/ui/screens/battle_state_viewer.py | Read ✓ |
| game/ui/screens/build_queue_input_router.py | Read ✓ |
| game/ui/screens/builder/detail_panel.py | Read ✓ |
| game/ui/screens/builder/grouping_strategies.py | Read ✓ |
| game/ui/screens/builder/interaction_controller.py | Read ✓ |
| game/ui/screens/builder/layer_panel.py | Read ✓ |
| game/ui/screens/builder/modifier_config.py | Read ✓ |
| game/ui/screens/builder/stat_definitions.py | Read ✓ |
| game/ui/screens/builder/weapons_renderer.py | Read ✓ |
| game/ui/screens/builder/weapons_viewmodel.py | Read ✓ |
| game/ui/screens/defeat_dialog.py | Read ✓ |
| game/ui/screens/design_image_helper.py | Read ✓ |
| game/ui/screens/empire_build_queue_data_source.py | Read ✓ |
| game/ui/screens/empire_build_queue_filter_manager.py | Read ✓ |
| game/ui/screens/empire_build_queue_viewmodel.py | Read ✓ |
| game/ui/screens/empire_build_queue_window.py | Read ✓ |
| game/ui/screens/event_log_window.py | Read ✓ |
| game/ui/screens/fleet_menu_items.py | Read ✓ |
| game/ui/screens/fleet_report_sidebar.py | Read ✓ |
| game/ui/screens/galaxy_test/system_mode.py | Read ✓ |
| game/ui/screens/gravity_target_editor.py | Read ✓ |
| game/ui/screens/keybindings_scene.py | Read ✓ |
| game/ui/screens/list_data_source_base.py | Read ✓ |
| game/ui/screens/new_game_setup_view_model.py | Read ✓ |
| game/ui/screens/planet_abilities_window.py | Read ✓ |
| game/ui/screens/planet_data_source.py | Read ✓ |
| game/ui/screens/planet_target_editor_base.py | Read ✓ |
| game/ui/screens/race_asset_loader.py | Read ✓ |
| game/ui/screens/race_setup/controller.py | Read ✓ |
| game/ui/screens/race_setup/input_handler.py | Read ✓ |
| game/ui/screens/race_setup/llm_dialog_service.py | Read ✓ |
| game/ui/screens/settings_window.py | Read ✓ |
| game/ui/screens/setup_data_io.py | Read ✓ |
| game/ui/screens/strategy_build_queue_manager.py | Read ✓ |
| game/ui/screens/strategy_camera_nav.py | Read ✓ |
| game/ui/screens/strategy_input_handler.py | Read ✓ |
| game/ui/screens/strategy_modal_window.py | Read ✓ |
| game/ui/screens/strategy_render/context.py | Read ✓ |
| game/ui/screens/strategy_render/storms.py | Read ✓ |
| game/ui/screens/strategy_render/systems.py | Read ✓ |
| game/ui/screens/strategy_superweapons.py | Read ✓ |
| game/ui/screens/strategy_windows/build_queue_windows.py | Read ✓ |
| game/ui/screens/strategy_windows/empire_panel_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/fleet_report_ctrl.py | Read ✓ |
| game/ui/screens/test_lab/details/__init__.py | Read ✓ |
| game/ui/screens/test_lab/formatting_utils.py | Read ✓ |
| game/ui/screens/test_lab/renderer/category_panel.py | Read ✓ |
| game/ui/screens/test_lab/renderer/metadata_panel.py | Read ✓ |
| game/ui/screens/test_lab/renderer/orchestrator.py | Read ✓ |
| game/ui/screens/test_lab/screen_actions.py | Read ✓ |
| game/ui/screens/test_lab/test_run_card.py | Read ✓ |
| game/ui/screens/transfer_controller.py | Read ✓ |
| game/ui/screens/transfer_dialog.py | Read ✓ |
| game/ui/screens/transfer_mass_preview.py | Read ✓ |
| game/ui/screens/turn_failed_dialog.py | Read ✓ |
| game/ui/screens/water_target_editor.py | Read ✓ |
| game/ui/screens/workshop_data_loader.py | Read ✓ |
| game/ui/screens/workshop_data_reloader.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_ship_ops.py | Read ✓ |
| game/ui/services/component_service.py | Read ✓ |
| game/ui/services/image/types.py | Read ✓ |
| game/ui/services/modifier_icon_service.py | Read ✓ |
| game/ui/services/ship_io_adapter.py | Read ✓ |
| game/ui/services/tkinter_utils.py | Read ✓ |
| game/ui/utils/__init__.py | Read ✓ |
| game/ui/widgets/preference_row.py | Read ✓ |
| game/ui/widgets/scroll_state.py | Read ✓ |

All 217 files in scope have been read and verified.
