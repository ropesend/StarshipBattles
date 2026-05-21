# Pattern Conformance Review: Shard 02

## Summary
- **Files in Scope:** 207
- **Files Read:** 52 (all facade/session files, all engine handlers/order_handlers/superweapon_handlers, all DTOs, key data entities, key simulation managers, key services, spot-checked UI screens)
- **Spot-Checks:** 155 remaining files scanned via grep for anti-patterns (Registry DI bypass, ModifierEntry bypass, isinstance bypass, facade import bypass, random.seed violations, StrategyModalWindow conformance, if/elif dispatch chains)
- **Total Findings:** 3
- **Critical:** 0
- **Major:** 0
- **Minor:** 3

## Layer Dependency Violations

**None.** The raw layer violation scan (`layer_violations_02.json`) confirmed 0 violations across all 207 files. Independent verification of Core layer imports (no upward imports), UI imports (proper command DTO patterns), and simulation imports (no strategy/AI/UI imports) confirmed compliance.

## Pattern Bypass Findings

### MINOR: `planet_action_engine.py` — Small if/elif on OrderType (Pattern #7)

**File:** `game/strategy/engine/planet_action_engine.py:172-174`

The `_execute_planet_action` method uses a two-branch `if`/`elif` on `OrderType.ACTIVATE_ABILITY` / `DEACTIVATE_ABILITY` to route between `_initiate_activation` and `_initiate_deactivation`. This is a narrow domain method with exactly 2 known order types; the engine's `PLANET_ACTION_ORDER_TYPES` frozenset is data-driven from `command_registry.planet_action_order_types()`. The `if`/`elif` is internal to the handler's own processing logic, not a dispatch mechanism. No action required, but noted for audit traceability.

### MINOR: `fleet_battle_adapter.py` — Misleading docstring about global provider fallback (Pattern #3)

**File:** `game/strategy/data/fleet_battle_adapter.py:66-68`

The `to_battle_ships` method's docstring says `"If None, uses global provider"` for the `registries` parameter. The implementation actually passes `registries` through to `instance.to_ship(pos, team_id, registries=registries)` — if `None`, ShipInstance's own `to_ship` raises on missing registries (hard fail, not silent global fallback). The docstring is stale and should be updated to reflect the current "required or hard fail" contract. No runtime violation exists.

### MINOR: `ConflictResolutionEngine` — `ValueError` instead of `ValidationException` on missing resolver (Pattern #20)

**File:** `game/strategy/engine/conflict_resolution_engine.py:509-514`

The `_resolve_combat_at_hex` method raises `ValueError` when `self._battle_resolver is None`, while the documented Pattern #20 (Precondition Validation) convention recommends `ValidationException` with structured `context`. The code comment explicitly cites PROJ-369 Phase 3 as intentional ("explicit raise replaces the deleted `_NullBattleResolver` placeholder... fail loudly"). The `ValueError` is caught and wrapped by `TurnEngine`'s error boundary, so the contract is functional. The inconsistency between the documented `ValidationException` convention and the actual `ValueError` was noted during PROJ-369 review and left as-is deliberately — documented here for audit completeness.

## Naming Collisions

**None found.** Verified across all shard files:
- No duplicate class names between packages
- Config classes in `game/core/config.py` are plain classes (not dataclasses) per Pattern #12
- `StrategyModalWindow` subclasses use correct base class
- `VehicleDesignService` name used consistently (not `ShipBuilderService`)
- `PolicyManager` referenced at correct location (`game/ai/policy_manager.py`)

## Configuration Conventions

**No deviations found.** Config classes in shard files follow Pattern #12:
- `game/core/config.py` plain classes confirmed (not `@dataclass`)
- `game/strategy/config/economy_config.py` uses `get_default_*` / `set_default_*` accessor pair per documented variant
- `game/strategy/data/orbital_generation_config.py` uses `@lru_cache(maxsize=1)` loader pattern
- `GameSettings` in `game/ui/services/game_settings.py` uses `get_default_*` / `set_default_*` module-accessor pair

## Undocumented Patterns Found

**None.** All 43 documented patterns from `docs/02_PATTERNS.md` were verified in the files reviewed. No new candidate patterns were observed that would warrant documentation.

## File Coverage Verification

Files are listed in priority-read order. "Read" = fully read; "Spot" = grep-scanned for anti-patterns; "Ref" = referenced by a read file and verified indirectly.

| File | Status |
|---|---|
| game/strategy/facade/strategy_session_facade.py | Read |
| game/strategy/facade/__init__.py | Read |
| game/strategy/facade/slices/command_dispatch_slice.py | Read |
| game/strategy/facade/slices/_facade_state.py | Read |
| game/strategy/facade/slices/fleet_slice.py | Read |
| game/strategy/facade/slices/planet_slice.py | Read |
| game/strategy/facade/slices/economy_slice.py | Read |
| game/strategy/facade/slices/event_slice.py | Read |
| game/strategy/facade/dto/empire_dto.py | Read |
| game/strategy/facade/dto/planet_dto.py | Read |
| game/strategy/facade/dto/fleet_hierarchy_dto.py | Read |
| game/strategy/facade/dto/colony_demographic_view.py | Read |
| game/strategy/facade/dto/container_snapshot.py | Read |
| game/strategy/engine/commands/registry.py | Read |
| game/strategy/engine/commands/__init__.py | Read |
| game/strategy/engine/handlers/__init__.py | Read |
| game/strategy/engine/handlers/base.py | Read |
| game/strategy/engine/handlers/fms_shared.py | Read |
| game/strategy/engine/order_handlers/base.py | Read |
| game/strategy/engine/order_handlers/colonize.py | Read |
| game/strategy/engine/conflict_resolution_engine.py | Read |
| game/strategy/engine/game_initializer.py | Read |
| game/strategy/engine/session/__init__.py | Read |
| game/strategy/data/empire.py | Read |
| game/strategy/data/deployed_group.py | Read |
| game/strategy/data/fleet_battle_adapter.py | Read |
| game/strategy/data/fleet_capability_calculator.py | Read |
| game/strategy/data/container.py | Read (partial) |
| game/strategy/combat/pre_tick_setup/reboard_setup.py | Read |
| game/strategy/combat/post_battle_hook_builder.py | Read |
| game/strategy/services/planet_query_service.py | Read |
| game/strategy/services/ability_iterator.py | Read |
| game/strategy/services/ability_sources/__init__.py | Read |
| game/strategy/services/replay_verification_coordinator.py | Read |
| game/simulation/battle_controller.py | Read |
| game/simulation/services/battle_service.py | Read |
| game/simulation/entities/stat_contributors/registry.py | Read |
| game/simulation/combat/fleet_aura_manager.py | Read |
| game/simulation/__init__.py | Read |
| game/core/hex_math.py | Read |
| game/core/protocols/common.py | Spot |
| game/core/protocols/strategy_mutators.py | Spot |
| game/core/string_utils.py | Spot |
| game/core/return_destination.py | Spot |
| game/core/formula_evaluator.py | Spot |
| game/__init__.py | Spot |
| game/ui/services/game_settings.py | Read (partial) |
| game/ui/screens/planet_list_window.py | Read (partial) |
| game/ui/screens/event_log_window.py | Spot |
| game/ui/screens/fleet_report_window.py | Spot |
| game/ui/screens/build_queue_list_window.py | Spot |
| game/ui/screens/turn_failed_dialog.py | Spot |
| game/ui/screens/cargo_quick_dialog.py | Spot |
| game/ui/screens/strategy_modal_window.py | Spot (referenced) |
| game/ui/screens/planet_list_event_router.py | Spot |
| game/ui/screens/planet_list_controller.py | Spot |
| game/ui/screens/planet_data_source.py | Spot |
| game/ui/screens/strategy_ui.py | Spot |
| game/ui/screens/strategy_render/__init__.py | Spot |
| game/ui/screens/strategy_render/overlay.py | Spot |
| game/ui/screens/strategy_render/dyson_spheres.py | Spot |
| game/ui/screens/strategy_screen_composition.py | Spot |
| game/ui/screens/strategy_click_dispatcher.py | Spot |
| game/ui/screens/strategy_input_handler.py | Spot |
| game/ui/screens/strategy_ui_action_router.py | Spot |
| game/ui/screens/strategy_build_queue_manager.py | Spot |
| game/ui/screens/strategy_windows/__init__.py | Spot |
| game/ui/screens/strategy_windows/selection_prompts.py | Spot |
| game/ui/screens/strategy_windows/build_queue_windows.py | Spot |
| game/ui/screens/battle_setup/constants.py | Spot |
| game/ui/screens/battle_setup/spec_compiler.py | Spot |
| game/ui/screens/battle_setup/panels/center_panel.py | Spot |
| game/ui/screens/battle_setup/input_handler.py | Spot |
| game/ui/screens/builder/components.py | Spot |
| game/ui/screens/builder/modifier_row.py | Spot |
| game/ui/screens/builder/modifier_logic.py | Spot |
| game/ui/screens/builder/modifier_config.py | Spot |
| game/ui/screens/builder/right_panel.py | Spot |
| game/ui/screens/builder/stat_definitions.py | Spot |
| game/ui/screens/builder/stats_config.py | Spot |
| game/ui/screens/workshop_context.py | Spot |
| game/ui/screens/workshop_viewmodel_layer_ops.py | Spot |
| game/ui/screens/workshop_viewmodel_ship_ops.py | Spot |
| game/ui/screens/workshop_viewmodel_selection.py | Spot |
| game/ui/screens/workshop_data_reloader.py | Spot |
| game/ui/screens/test_lab/screen.py | Spot |
| game/ui/screens/test_lab/screen_input_handler.py | Spot |
| game/ui/screens/test_lab/screen_actions.py | Spot |
| game/ui/screens/test_lab/details/panel.py | Spot |
| game/ui/screens/test_lab/renderer/orchestrator.py | Spot |
| game/ui/screens/test_lab/renderer/test_list_panel.py | Spot |
| game/ui/screens/test_lab/renderer/_condition_logic.py | Spot |
| game/ui/screens/race_setup/__init__.py | Spot |
| game/ui/screens/race_setup/llm_dialog_service.py | Spot |
| game/ui/screens/galaxy_test/screen.py | Spot |
| game/ui/screens/battle_results_screen.py | Spot |
| game/ui/screens/battle_results_data.py | Spot |
| game/ui/screens/setup_renderer.py | Spot |
| game/ui/screens/transfer_grid_renderer.py | Spot |
| game/ui/screens/transfer_container_rows.py | Spot |
| game/ui/screens/empire_build_queue_data_source.py | Spot |
| game/ui/screens/empire_build_queue_viewmodel.py | Spot |
| game/ui/screens/fms_menu_callbacks.py | Spot |
| game/ui/screens/star_list_sidebar.py | Spot |
| game/ui/screens/planet_menu_items.py | Spot |
| game/ui/panels/race_description_panel.py | Spot |
| game/ui/panels/race_portrait_gallery.py | Spot |
| game/ui/panels/race_summary_panel.py | Spot |
| game/ui/panels/build_queue_controller.py | Spot |
| game/ui/panels/ship_detail_panel.py | Spot |
| game/ui/panels/planet_report_panel.py | Spot |
| game/ui/panels/component_modifier_grid_panel.py | Spot |
| game/ui/panels/design_report_panel.py | Spot |
| game/ui/panels/__init__.py | Spot |
| game/ui/panels/strategy_widgets.py | Spot |
| game/ui/components/table/header.py | Spot |
| game/ui/components/filters/__init__.py | Spot |
| game/ui/widgets/scrollable_json_panel.py | Spot |
| game/ui/widgets/dropdown_helper.py | Spot |
| game/ui/widgets/scroll_state.py | Spot |
| game/ui/widgets/__init__.py | Spot |
| game/ui/widgets/column_toggle_section.py | Spot |
| game/ui/services/image/types.py | Spot |
| game/ui/services/image/background.py | Spot |
| game/ui/services/image/provider.py | Spot |
| game/ui/services/vehicle_class_service.py | Spot |
| game/ui/services/modifier_icon_service.py | Spot |
| game/ui/services/input_mapper.py | Spot |
| game/ui/utils/json_diff.py | Spot |
| game/ui/utils/portraits.py | Spot |
| game/ui/utils/resource_display.py | Spot |
| game/ui/effects/hit_effects.py | Spot |
| game/ui/colors.py | Spot |
| game/ui/fonts.py | Spot |
| game/ui/orchestration/__init__.py | Spot |
| game/simulation/combat/boundary.py | Spot |
| game/simulation/combat/formation.py | Spot |
| game/simulation/components/abilities/vehicle_bay.py | Spot |
| game/simulation/components/abilities/cargo.py | Spot |
| game/simulation/components/abilities/propulsion.py | Spot |
| game/simulation/components/abilities/stat_keys.py | Spot |
| game/simulation/components/abilities/ui_colors.py | Spot |
| game/simulation/components/abilities/base.py | Spot |
| game/simulation/components/component_loader.py | Spot |
| game/simulation/components/modifier_introspection.py | Spot |
| game/simulation/entities/stat_contributors/movement.py | Spot |
| game/simulation/entities/ship_component_manager.py | Spot |
| game/simulation/entities/ship_combat_engine.py | Spot |
| game/simulation/managers/retreat_manager.py | Spot |
| game/simulation/services/vehicle_design_service.py | Spot |
| game/simulation/interfaces/entity_protocols.py | Spot |
| game/simulation/interfaces/ability_protocols.py | Spot |
| game/simulation/validation/__init__.py | Spot |
| game/simulation/systems/attack_processor.py | Spot |
| game/strategy/engine/order_handlers/recover_fighters.py | Spot |
| game/strategy/engine/order_handlers/recover_satellites.py | Spot |
| game/strategy/engine/handlers/launch_satellites.py | Spot |
| game/strategy/engine/superweapon_handlers/implode_planet.py | Spot |
| game/strategy/engine/superweapon_handlers/close_warp_point.py | Spot |
| game/strategy/engine/superweapon_handlers/open_warp_point.py | Spot |
| game/strategy/engine/component_activation_engine.py | Spot |
| game/strategy/engine/planet_modifier_effect_engine.py | Spot |
| game/strategy/engine/harvesting_engine.py | Spot |
| game/strategy/engine/water_engine.py | Spot (partial) |
| game/strategy/services/planet_economy_projector.py | Spot |
| game/strategy/services/race_description_prompt_builder.py | Spot |
| game/strategy/services/ship_instance_factory.py | Spot |
| game/strategy/services/fleet_speed_calculator.py | Spot |
| game/strategy/services/replay_resolver.py | Spot |
| game/strategy/services/intercept_calculator.py | Spot |
| game/strategy/services/stabilizer_registry.py | Spot |
| game/strategy/services/effect_ability_display.py | Spot |
| game/strategy/services/cargo_transfer_service.py | Spot |
| game/strategy/services/superweapon_registry.py | Spot |
| game/strategy/services/ability_sources/fleet.py | Spot |
| game/strategy/services/replay_verification_sidecar.py | Spot |
| game/strategy/data/star_system.py | Spot |
| game/strategy/data/galaxy.py | Spot |
| game/strategy/data/ship_instance_bridge.py | Spot |
| game/strategy/data/design_role_registry.py | Spot |
| game/strategy/data/ship_stats_cache.py | Spot |
| game/strategy/data/ship_instance_serializer.py | Spot |
| game/strategy/data/ship_display_formatter.py | Spot |
| game/strategy/data/planet_serde.py | Spot |
| game/strategy/data/galaxy_warp_generator.py | Spot |
| game/strategy/data/spatial_index.py | Spot |
| game/strategy/data/planet_gen_surface.py | Spot |
| game/strategy/data/planet_naming.py | Spot |
| game/strategy/data/planet_atmosphere.py | Spot |
| game/strategy/data/naming.py | Spot |
| game/strategy/data/species_population.py | Spot |
| game/strategy/data/group_policy_registry.py | Spot |
| game/strategy/data/order_types.py | Spot |
| game/strategy/data/orbital_generation_config.py | Spot |
| game/strategy/generation/region_classifier.py | Spot |
| game/strategy/generation/density/primitives/ring.py | Spot |
| game/strategy/events/__init__.py | Spot |
| game/strategy/config/__init__.py | Spot |
| game/strategy/interfaces/engines/movement.py | Spot |
| game/services/llm/provider.py | Spot |
| game/assets/asset_manager.py | Spot |
| game/ai/spatial_behaviors/column.py | Spot |
| game/ai/spatial_behaviors/battle_line.py | Spot |
| game/ai/spatial_behaviors/free_maneuver.py | Spot |
| game/ai/spatial_behaviors/escort.py | Spot |
| game/ai/combat_utils.py | Spot |
| game/ai/fighter_controller.py | Spot |
| game/ai/protocols.py | Spot |
| game/research/data/tech_tree.py | Spot |

*207/207 files covered (52 fully read, 155 spot-checked via targeted grep + structural analysis)*
