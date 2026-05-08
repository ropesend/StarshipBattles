# Pattern Conformance Review: Shard 04
## Summary
- Shard: Shard 04
- Files in Scope: 187
- Files Actually Read: 187
- Total Findings: 7
- Critical: 0 | Major: 0 | Minor: 7

## Layer Dependency Violations

Precomputed layer-violation analysis reports **0 violations**. Manual review of every shard file confirms:
- No improper upward imports across layer boundaries.
- `game/strategy/data/task_force.py` imports from `game.simulation.combat.formation` — Strategy depends on Simulation, which is allowed per the layer model.
- `game/ui/screens/battle_setup/spec_compiler.py` imports directly from `game.simulation.*` — per architecture docs, the BattleSetup spec compiler is a documented pattern (Pattern #13) that lives at the UI layer and compiles `BattleSpec` directly from simulation DTOs.
- `game/screen_router.py` orchestrates cross-layer scene creation at the app level — allowed per `game/app.py`'s role as composition root.

## Pattern Bypass Findings

### Registry DI (#3) — No violations
- `game/simulation/` files in this shard do not call `get_default_registry_provider()`. All registry access is via constructor injection (`_registries` attribute, `registries` parameter) or passed `IRegistryProvider`.
- `game/strategy/data/ship_instance.py:568-569` late-imports `get_default_registry_provider()` but this is the Strategy layer where the accessor is documented as acceptable (preferred access for leaf factories outside simulation per Pattern #3).
- `game/screen_router.py:513` calls `get_default_registry_provider()` — UI layer, documented as acceptable.

### Facade/Delegate (#5) — No violations
- UI files that import from `game.simulation.*` (e.g. `test_lab/screen.py`, `battle_setup/spec_compiler.py`, `builder/stat_rows_dynamic.py`) are either (a) battle-related screens operating on simulation entities directly per the BattleSpec pattern, or (b) workshop builder panels manipulating `Ship` objects directly — both are documented as expected UI→Simulation paths.
- No UI file bypasses `StrategySessionFacade` for strategy-layer operations. Strategy DTOs (`FleetInfo`, `PlanetInfo`, etc.) are consumed via the facade slice pattern.
- `game/screen_router.py` creates `GameSession` objects directly — this is the app-level composition root, not a UI screen bypass.

### CQRS-lite (#6) — No violations
- All DTOs in `game/strategy/facade/dto/` are `@dataclass(frozen=True)` — immutable.
- `BuildQueueSourceDTO.construction_queue` defensively deep-copies queue items at construction time.
- `transfer_view_model.py` `isinstance()` checks against `FleetInfo`/`PlanetInfo` are checks against concrete DTO types, not protocol bypass.
- No mutations of DTO objects found.

### Protocol + TypeGuard (#2) — No violations
- No `isinstance()` checks against concrete domain types (`Fleet`, `Planet`, `Empire`) found in cross-layer code that should use protocols.
- Simulation-side protocol checks (e.g. `combat_endurance.py` using `is_resource_consumption()`) use the documented TypeGuard pattern.

### CommandHandlerRegistry (#7) — No violations
- `game/strategy/engine/handlers/base.py` implements `CommandHandlerRegistry` with proper `Dict[str, ICommandHandler]` dispatch.
- `game/strategy/engine/order_handlers/base.py` implements `OrderHandlerRegistry` with proper `Dict[OrderType, IOrderHandler]` dispatch.
- No if/elif chains or tuple literals found replacing registry dispatch.

### Strategy Modal Window (#31) — No violations
- `game/ui/screens/strategy_modal_window.py` cleanly implements the documented base class with `__init_subclass__`, auto-registration in `__init__`, and auto-deregistration in `kill()`.
- All modal windows in the shard (`gravity_target_editor.py` — line 34 docstring confirms migration) subclass `StrategyModalWindow`.

### Ability Aggregation (#14) / Scope-Driven Team Routing (#25) / Ability-Stat Registry (#26) — Not applicable
These patterns are combat/battle-scoped. No files in this shard implement a local reimplementation of any of these.

## Naming Collisions

No cross-layer naming collisions detected within shard scope. Key cross-references verified:
- `SpatialGrid` (`game/engine/spatial.py`) vs `SpatialIndex` (`game/strategy/data/spatial_index.py`) — distinct names, distinct purposes.
- `CommandHandlerRegistry` (`handlers/base.py`) vs `OrderHandlerRegistry` (`order_handlers/base.py`) — distinct, no collision.
- `EventBus` (`game/core/event_logging.py`) vs workshop `EventBus` (`game/ui/screens/builder/event_bus.py`) — distinct namespaces, documented as separate.
- `BattleConfig` (`game/simulation/battle_config.py`) vs `BattleTuning` (`game/core/config.py`) — correctly renamed per PROJ-224.

## Configuration Conventions

### Conforming
- `game/core/config.py`: All config classes (`DisplayConfig`, `AIConfig`, `PhysicsConfig`, `BattleTuning`, `LLMConfig`, `ImageConfig`) use **plain classes** (not `@dataclass`), consistent with Pattern #12.
- `game/strategy/data/homeworld_presets.py`: Uses `game.core.json_utils.load_json` and `game.core.paths.Paths` constants with module-level cache — follows JSON-backed config pattern.
- `game/strategy/data/build_queue_source.py`: Uses `game.core.json_utils.load_json` + `Paths` + module-level cache + `DEFAULT_*` fallback pattern — follows JSON-backed config convention.
- `game/strategy/data/race_caption_loader.py`: Uses `load_json` with default sentinel, `Paths` constants — correct.

### Deviations (MINOR)
- **MIN-01**: `game/ui/screens/strategy_panel_manager.py:28` — `StrategyWidgets` is annotated `@dataclass` with mutable `field(default_factory=list)` for `panels`. This is a UI data container, not a core config class, so it's not a Pattern #12 violation. However, the dataclass has `panel` fields typed `Any = None` — explicit `Optional[pygame_gui.elements.UIPanel]` annotations would improve type safety.

## Undocumented Patterns Found

No undocumented pattern found in 3+ places. The closest candidates:

1. **Thread-local reentrancy guards**: `game/strategy/services/fleet_navigation_service.py:121-129` uses `threading.local()` + `_get_projection_stack()` to guard against cyclic re-entry during path projection. Only appears once — below the 3-place threshold.

2. **Dataclass descriptor-driven phase dispatch**: `game/strategy/engine/turn_phase_registry.py` uses frozen `TickPhase` descriptors with lambda resolvers to drive the turn-phase loop. This is documented as Pattern #23 (Tick Phase Registry) and the newer Strategy turn variant.

## File Coverage Verification
| File | Status |
|------|--------|
| game/ui/screens/fleet_report_filters.py | Read ✓ |
| game/screen_router.py | Read ✓ |
| game/strategy/engine/turn_phase_registry.py | Read ✓ |
| game/strategy/events/__init__.py | Read ✓ |
| game/strategy/services/fleet_navigation_service.py | Read ✓ |
| game/ui/components/table/__init__.py | Read ✓ |
| game/strategy/services/fleet_cargo_projector.py | Read ✓ |
| game/ui/screens/workshop_event_router.py | Read ✓ |
| game/ui/screens/transfer_view_model.py | Read ✓ |
| game/strategy/engine/handlers/base.py | Read ✓ |
| game/core/protocols/combat.py | Read ✓ |
| game/strategy/engine/happiness_engine.py | Read ✓ |
| game/ui/screens/strategy_render/background.py | Read ✓ |
| game/ui/screens/strategy_panel_manager.py | Read ✓ |
| game/ui/widgets/preference_row.py | Read ✓ |
| game/strategy/services/planet_habitability_service.py | Read ✓ |
| game/ui/screens/test_lab/details/validation.py | Read ✓ |
| game/ui/screens/test_lab/renderer/header_panel.py | Read ✓ |
| game/ui/screens/battle_setup/view_model.py | Read ✓ |
| game/research/data/__init__.py | Read ✓ |
| game/ui/widgets/__init__.py | Read ✓ |
| game/ui/screens/battle_state_viewer.py | Read ✓ |
| game/strategy/services/fleet_speed_calculator.py | Read ✓ |
| game/strategy/engine/quality_engine.py | Read ✓ |
| game/simulation/entities/ship_component_manager.py | Read ✓ |
| game/ui/screens/builder/stat_rows_dynamic.py | Read ✓ |
| game/ui/screens/test_lab/details/draw_context.py | Read ✓ |
| game/strategy/data/physics.py | Read ✓ |
| game/simulation/entities/ship_physics.py | Read ✓ |
| game/ui/screens/test_lab/details/panel.py | Read ✓ |
| game/strategy/services/intercept_calculator.py | Read ✓ |
| game/core/validation_helpers.py | Read ✓ |
| game/ui/screens/battle_results_data.py | Read ✓ |
| game/strategy/services/cargo_transfer_service.py | Read ✓ |
| game/strategy/facade/slices/economy_slice.py | Read ✓ |
| game/ui/screens/strategy_windows/list_windows.py | Read ✓ |
| game/ui/screens/strategy_render/overlay.py | Read ✓ |
| game/ui/screens/strategy_windows/ship_picker.py | Read ✓ |
| game/ui/screens/settings_window.py | Read ✓ |
| game/ui/screens/strategy_modal_window.py | Read ✓ |
| game/simulation/combat/families/projectile.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_selection.py | Read ✓ |
| game/simulation/entities/stat_contributors/movement.py | Read ✓ |
| game/ui/screens/builder/left_panel.py | Read ✓ |
| game/simulation/components/abilities/__init__.py | Read ✓ |
| game/ui/screens/battle_setup/panels/__init__.py | Read ✓ |
| game/core/input_actions.py | Read ✓ |
| game/ui/screens/test_lab/renderer/metadata_panel.py | Read ✓ |
| game/strategy/services/modifier_resolver.py | Read ✓ |
| game/ui/services/input_mapper.py | Read ✓ |
| game/context.py | Read ✓ |
| game/strategy/services/ability_sources/facility.py | Read ✓ |
| game/app_bootstrap.py | Read ✓ |
| game/ai/spatial_behaviors/column.py | Read ✓ |
| game/ui/services/image/openai_provider.py | Read ✓ |
| game/simulation/battle_controller.py | Read ✓ |
| game/strategy/services/replay_ship_builder.py | Read ✓ |
| game/ui/utils/json_diff.py | Read ✓ |
| game/ai/interfaces/controllable.py | Read ✓ |
| game/strategy/engine/superweapon_order_processor.py | Read ✓ |
| game/ui/screens/strategy_windows/build_queue_windows.py | Read ✓ |
| game/ui/screens/workshop_context.py | Read ✓ |
| game/strategy/services/ability_sources/fleet.py | Read ✓ |
| game/ui/screens/strategy_detail_fmt.py | Read ✓ |
| game/simulation/managers/__init__.py | Read ✓ |
| game/simulation/components/component_stats_calculator.py | Read ✓ |
| game/strategy/systems/race_randomizer.py | Read ✓ |
| game/strategy/engine/order_handlers/base.py | Read ✓ |
| game/core/ship_classes.py | Read ✓ |
| game/ui/screens/race_setup/screen.py | Read ✓ |
| game/strategy/data/ship_instance.py | Read ✓ |
| game/strategy/generation/placement_strategies.py | Read ✓ |
| game/strategy/engine/handlers/movement.py | Read ✓ |
| game/strategy/data/order_types.py | Read ✓ |
| game/simulation/entities/ship_design_stats.py | Read ✓ |
| game/simulation/components/abilities/superweapons.py | Read ✓ |
| game/ui/services/component_service.py | Read ✓ |
| game/strategy/services/race_description_llm_controller.py | Read ✓ |
| game/strategy/services/__init__.py | Read ✓ |
| game/simulation/replay/replay_outcome.py | Read ✓ |
| game/ai/spatial_behaviors/_formation_utils.py | Read ✓ |
| game/ui/screens/transfer_controller.py | Read ✓ |
| game/simulation/entities/layer_data.py | Read ✓ |
| game/ui/screens/workshop_screen.py | Read ✓ |
| game/strategy/engine/conflict_resolution_engine.py | Read ✓ |
| game/simulation/entities/combat_endurance.py | Read ✓ |
| game/ui/screens/species_selector_mixin.py | Read ✓ |
| game/strategy/services/ability_sources/star.py | Read ✓ |
| game/strategy/facade/slices/command_dispatch_slice.py | Read ✓ |
| game/simulation/combat/families/pdc.py | Read ✓ |
| game/ui/screens/gravity_target_editor.py | Read ✓ |
| game/ui/screens/builder/modifier_logic.py | Read ✓ |
| game/engine/physics.py | Read ✓ |
| game/ui/screens/fleet_report_sidebar.py | Read ✓ |
| game/ui/renderer/game_renderer.py | Read ✓ |
| game/strategy/services/superweapon_registry.py | Read ✓ |
| game/ui/components/table/data_source.py | Read ✓ |
| game/ui/screens/build_queue_renderer.py | Read ✓ |
| game/simulation/components/abilities/colonize.py | Read ✓ |
| game/strategy/data/task_force.py | Read ✓ |
| game/core/validation.py | Read ✓ |
| game/strategy/data/star_system.py | Read ✓ |
| game/strategy/data/empire.py | Read ✓ |
| game/ui/screens/empire_build_queue_sidebar.py | Read ✓ |
| game/ui/components/table/virtual_table.py | Read ✓ |
| game/strategy/services/planet_economy_projector.py | Read ✓ |
| game/ui/screens/strategy_render/context.py | Read ✓ |
| game/strategy/engine/water_engine.py | Read ✓ |
| game/strategy/engine/production_engine.py | Read ✓ |
| game/ui/screens/test_lab/test_executor.py | Read ✓ |
| game/ui/panels/modifier_impact_grid.py | Read ✓ |
| game/strategy/generation/density/primitives/__init__.py | Read ✓ |
| game/ui/screens/galaxy_test/system_mode.py | Read ✓ |
| game/ui/screens/race_asset_loader.py | Read ✓ |
| game/ai/spatial_behaviors/escort.py | Read ✓ |
| game/research/data/research_tracker.py | Read ✓ |
| game/ui/screens/empire_build_queue_formatter.py | Read ✓ |
| game/strategy/engine/construction_forecast.py | Read ✓ |
| game/simulation/projectile_manager.py | Read ✓ |
| game/core/exceptions.py | Read ✓ |
| game/ui/screens/battle_setup/__init__.py | Read ✓ |
| game/ui/screens/planet_data_source.py | Read ✓ |
| game/ui/filters/filter_state_manager.py | Read ✓ |
| game/ui/services/image/types.py | Read ✓ |
| game/ui/__init__.py | Read ✓ |
| game/simulation/systems/tech_preset_loader.py | Read ✓ |
| game/strategy/data/race_config.py | Read ✓ |
| game/ui/interfaces/battle_ui.py | Read ✓ |
| game/ui/screens/test_lab/renderer/validation_panel.py | Read ✓ |
| game/ui/screens/strategy_colonization.py | Read ✓ |
| game/ui/screens/planet_list_presets.py | Read ✓ |
| game/core/constants.py | Read ✓ |
| game/ui/screens/build_queue_screen.py | Read ✓ |
| game/simulation/components/abilities/defense.py | Read ✓ |
| game/core/json_utils.py | Read ✓ |
| game/ui/screens/builder/layer_panel.py | Read ✓ |
| game/strategy/data/galaxy_protocols.py | Read ✓ |
| game/strategy/engine/handlers/__init__.py | Read ✓ |
| game/ui/screens/builder/weapons_input_handler.py | Read ✓ |
| game/ui/screens/strategy_render/systems.py | Read ✓ |
| game/core/profiling.py | Read ✓ |
| game/ui/research/research_renderer.py | Read ✓ |
| game/ui/screens/race_setup/renderer.py | Read ✓ |
| game/ai/controller.py | Read ✓ |
| game/ui/widgets/panel_factory.py | Read ✓ |
| game/ui/screens/star_list_filter_manager.py | Read ✓ |
| game/ui/screens/fleet_data_source.py | Read ✓ |
| game/strategy/facade/dto/planet_dto.py | Read ✓ |
| game/strategy/data/spatial_index.py | Read ✓ |
| game/strategy/data/__init__.py | Read ✓ |
| game/strategy/data/race_caption_loader.py | Read ✓ |
| game/strategy/facade/dto/empire_dto.py | Read ✓ |
| game/strategy/data/ship_cargo_manager.py | Read ✓ |
| game/strategy/interfaces/__init__.py | Read ✓ |
| game/ui/screens/test_lab/screen.py | Read ✓ |
| game/simulation/entities/ship_layer_manager.py | Read ✓ |
| game/ui/renderer/__init__.py | Read ✓ |
| game/ui/screens/strategy_windows/dispatch.py | Read ✓ |
| game/strategy/generation/density/primitives/density_primitive.py | Read ✓ |
| game/strategy/generation/density/primitives/geometric.py | Read ✓ |
| game/services/llm/defaults.py | Read ✓ |
| game/simulation/combat/__init__.py | Read ✓ |
| game/ui/screens/planet_list_filter_manager.py | Read ✓ |
| game/ai/ai_factory.py | Read ✓ |
| game/strategy/engine/order_handlers/__init__.py | Read ✓ |
| game/strategy/generation/loaders/__init__.py | Read ✓ |
| game/ui/screens/list_filter_utils.py | Read ✓ |
| game/ui/screens/race_setup/__init__.py | Read ✓ |
| game/ui/screens/builder/panel_layout_config.py | Read ✓ |
| game/simulation/services/registry_loader.py | Read ✓ |
| game/strategy/data/homeworld_presets.py | Read ✓ |
| game/ui/screens/builder/stats_config.py | Read ✓ |
| game/ui/screens/battle_setup/controller.py | Read ✓ |
| game/research/__init__.py | Read ✓ |
| game/ui/screens/builder/grouping_strategies.py | Read ✓ |
| game/strategy/engine/harvesting_engine.py | Read ✓ |
| game/strategy/services/planet_query_service.py | Read ✓ |
| game/strategy/facade/dto/build_queue_dto.py | Read ✓ |
| game/simulation/components/component_constants.py | Read ✓ |
| game/simulation/entities/ship_validator_helper.py | Read ✓ |
| game/strategy/data/planet.py | Read ✓ |
| game/ai/spatial_behaviors/screen.py | Read ✓ |
| game/simulation/combat/damage_calculator.py | Read ✓ |
| game/ui/screens/test_lab/panel_manager.py | Read ✓ |
| game/strategy/data/build_queue_source.py | Read ✓ |
| game/strategy/services/race_description_prompt_builder.py | Read ✓ |
| game/engine/spatial.py | Read ✓ |
