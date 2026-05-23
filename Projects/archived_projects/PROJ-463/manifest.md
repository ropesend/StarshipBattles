# PROJ-463 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/simulation/combat/families/seeker.py | Production | Add seeker_ab None-guard (Phase 1.1) |
| game/strategy/engine/game_session.py | Production | Annotate 10 mutator props; type handle_command (Phase 1.2, 2.6) |
| game/simulation/combat/targeting_system.py | Production | Add None-guards (Phase 2.1) |
| game/simulation/components/component_resource_manager.py | Production | Narrow ResourceConsumption subtype (Phase 2.2) |
| game/simulation/components/abilities/base.py | Production | Narrow get_effective_stat (Phase 2.3) |
| game/simulation/interfaces/entity_protocols.py | Production | Narrow ICombatShip/IProjectile Any (Phase 2.3) |
| game/simulation/interfaces/ai_controller.py | Production | Narrow IAIController.ship (Phase 2.3) |
| game/simulation/components/component_stats_calculator.py | Production | Narrow evaluate_recursive; implicit Optional (Phase 2.3, 2.9) |
| game/ai/interfaces/controllable.py | Production | Narrow adapter ship + 16 methods (Phase 2.4) |
| game/strategy/engine/atmosphere_engine.py | Production | Narrow _get_planet_mutator (Phase 2.5) |
| game/strategy/engine/harvesting_engine.py | Production | Narrow mutator getters (Phase 2.5) |
| game/strategy/engine/planet_modifier_effect_engine.py | Production | Narrow _get_planet_mutator (Phase 2.5) |
| game/strategy/engine/production_spawner.py | Production | Narrow _get_planet_mutator (Phase 2.5) |
| game/strategy/engine/superweapon_order_processor.py | Production | Narrow _get_empire_mutator (Phase 2.5) |
| game/strategy/engine/environmental_hazard_engine.py | Production | Narrow _get_ship_mutator (Phase 2.5) |
| game/strategy/engine/order_handlers/base.py | Production | Narrow mutator getters (Phase 2.5) |
| game/strategy/engine/turn_engine.py | Production | Narrow _time_phase (Phase 2.6) |
| game/strategy/engine/handlers/base.py | Production | Narrow resolve helpers; implicit Optional (Phase 2.6, 2.9) |
| game/strategy/systems/design_catalog.py | Production | Add load_design_data return type (Phase 2.7) |
| game/strategy/engine/superweapon_handlers/create_dyson_sphere.py | Production | Add _precheck/_effect returns (Phase 2.7) |
| game/strategy/engine/superweapon_handlers/close_warp_point.py | Production | Add _precheck/_effect returns (Phase 2.7) |
| game/strategy/engine/superweapon_handlers/open_warp_point.py | Production | Add _precheck/_effect returns (Phase 2.7) |
| game/strategy/engine/superweapon_handlers/implode_planet.py | Production | Add _effect return (Phase 2.7) |
| game/strategy/engine/superweapon_handlers/stellerate_star.py | Production | Add _precheck/_effect returns (Phase 2.7) |
| game/simulation/entities/stat_contributors/registry.py | Production | Add iter_for return type (Phase 2.7) |
| game/strategy/data/star_system.py | Production | Add primary_star return type (Phase 2.7) |
| game/strategy/engine/game_initializer.py | Production | Add generator return types (Phase 2.7) |
| game/strategy/services/ability_sources/fleet.py | Production | Add generator return type (Phase 2.7) |
| game/strategy/engine/handlers/construction_queue.py | Production | Add _resolve_design_data return (Phase 2.7) |
| game/simulation/battle_runner.py | Production | Declare replay_id; remove ignores (Phase 2.8) |
| game/simulation/systems/attack_processor.py | Production | Declare launched_in_battle_id; remove ignore (Phase 2.8) |
| game/strategy/systems/save_game_service.py | Production | Add protocol methods; remove ignores (Phase 2.8) |
| game/strategy/adapters/simulation_adapter.py | Production | Remove no-redef ignore; annotate _lookup (Phase 2.8) |
| game/strategy/combat/battle_assembly.py | Production | Remove unjustified return-value ignore (Phase 2.8) |
| game/strategy/engine/issuer_adapter.py | Production | Narrow getattr fallback; remove ignore (Phase 2.8) |
| game/simulation/components/abilities/weapons.py | Production | Fix implicit Optional (Phase 2.9) |
| game/strategy/generation/loaders/galaxy_layouts_loader.py | Production | Fix implicit Optional (Phase 2.9) |
| game/strategy/generation/star_generator.py | Production | Fix implicit Optional (Phase 2.9) |
| game/simulation/combat/damage_calculator.py | Production | Fix implicit Optional (Phase 2.9) |
| game/strategy/validation/transfer_validator.py | Production | Fix implicit Optional (Phase 2.9) |
| game/simulation/systems/battle_logger.py | Production | Fix implicit Optional (Phase 2.9) |
| game/ai/ (mypy config) | Production | Adopt --strict (Phase 3.1) |
| game/simulation/ (mypy config) | Production | Adopt --strict; Ship mixin attrs (Phase 3.2) |
| game/strategy/ (mypy config) | Production | Adopt --strict (Phase 3.3) |
