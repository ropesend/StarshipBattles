# Deep Review: Strategy Layer
## Summary
- Shard: Strategy Layer
- Files in Scope: 194
- Files Actually Read: 194
- Total Findings: 11
- Critical: 0 | Major: 2 | Minor: 4 | Info: 5

## Dead Code Findings
No true dead code found. All importable symbols are reachable through production call paths.

## Internal Duplication Findings

#### MAJOR: Duplicated `_get_race_config` in HappinessEngine and PopulationEngine
**ID:** DEEP-STR-001
**Location:** `engine/happiness_engine.py:95-124` and `engine/population_engine.py:164-193`
**Issue:** Two engines share an identical 25-line `_get_race_config` method (race registry → empire race_config fallback). A merger, destruction, or new engine that needs species resolution would create a third copy.
**Estimated LOC:** 25 (removing one copy)
**Recommendation:** Extract to a shared utility in `formulas/` or `services/` (e.g., `resolve_species_race_config`). Both callers need a `race_registry` and an `empire`.

#### MAJOR: Boilerplate `_validate_tick_inputs` across 9 engines
**ID:** DEEP-STR-002
**Location:** `engine/action_execution_engine.py:70-79`, `engine/component_activation_engine.py:37-46`, `engine/conflict_resolution_engine.py:149-162`, `engine/consumable_management_engine.py:69-78`, `engine/fleet_movement_engine.py:194-207`, `engine/happiness_engine.py:63-72`, `engine/harvesting_engine.py:144-157`, `engine/organics_consumption_engine.py:64-73`, `engine/resupply_engine.py:75-84`
**Issue:** Nine engines define near-identical 6-12 line `_validate_tick_inputs` methods. Most check `colony is None` or `fleet.location is None`. The same `ValidationException` construction is repeated.
**Estimated LOC:** ~60 (consolidation to a shared validator helper)
**Recommendation:** Extract a `TickInputValidator` class or module-level function(s). Engines call `validate_colonies_not_none(empires)` / `validate_fleet_locations_not_none(empires)`.

## Fragmentation Findings

#### MINOR: `EmpireEconomyCalculator._aggregate_colony_production` duplicates harvest projection
**ID:** DEEP-STR-003
**Location:** `engine/empire_economy_calculator.py:201-256` vs `services/planet_economy_projector.py:185-226`
**Issue:** The economy calculator's colony-production aggregation walks the same facility-component loop as `compute_planet_production` in the projector, but reimplements the harvester-info extraction without applying quality multiplication the same way. The projector's function is the canonical source of truth for harvest projection.
**Estimated LOC:** 30 (replacing inline loop with a call to `compute_planet_production`)
**Recommendation:** Have `_aggregate_colony_production` delegate to `compute_planet_production` (already imported via `planet_economy_projector.py`) and remove the duplicated harvester scan.

#### MINOR: AtmosphereEngine / WaterEngine / QualityEngine share structure
**ID:** DEEP-STR-004
**Location:** `engine/atmosphere_engine.py`, `engine/water_engine.py`, `engine/quality_engine.py`
**Issue:** Three turn-boundary engines share identical patterns: iterate empires → colonies → facilities → `iter_components` → extract a specific ability key → sum `modification_rate` / `improvement_rate` → apply. Each is ~100-150 LOC of which ~80 is identical scaffolding.
**Estimated LOC:** 80 (shared base extraction)
**Recommendation:** Extract a `PerTurnFacilityModifierEngine` base class (or shared function) that takes the ability name, rate field, and apply-callback. Each engine would be ~30 LOC of specialization.

## Quality / LOC Reduction Findings

#### MINOR: 28 identical dispatch methods in CommandDispatchSlice
**ID:** DEEP-STR-005  
**Location:** `facade/slices/command_dispatch_slice.py:50-219`
**Issue:** Each of the 28 `dispatch_*` methods is a 3-line template: import a command class, instantiate it from kwargs, forward to handle_command. 219 lines for what a code-generator or metaprogramming approach could produce in ~30.
**Estimated LOC:** ~170
**Recommendation:** Python can't cleanly metaprogram kwargs-passing to dataclass constructors without runtime cost. The current form is idiomatic and well-tested. Mark as INFO — the pattern is correct, just verbose.

#### MINOR: `command_handlers.py` is a pure re-export shim
**ID:** DEEP-STR-006
**Location:** `engine/command_handlers.py`
**Issue:** The file exists only to re-export symbols from `engine/handlers/*`. `game_session.py` imports `create_default_registry` from it. The shim doubles the import surface and introduces one layer of indirection.
**Estimated LOC:** 82 (entire file)
**Recommendation:** Update `game_session.py` to import from `game.strategy.engine.handlers.registry_factory` directly, then delete the shim. (The shim already documents itself as transitional per PROJ-309.)

## Architecture / Convention Compliance

#### INFO: Strategy layer imports from game.ui via TYPE_CHECKING in prompt_builder
**ID:** DEEP-STR-007
**Location:** `services/race_description_prompt_builder.py:31`
**Issue:** Comment line 31 mentions `pygame_gui via game.ui` as a build-time import concern, but the actual imports are pure strategy-layer. The comment is outdated — the aptitudes display names are now hardcoded in the module.
**Recommendation:** Remove the misleading comment. No code change needed.

#### INFO: RaceRandomizer duplicate _APT_HIGH_RANGE / _APT_LOW_RANGE module constants are version of APTITUDE_NAMES ranges
**ID:** DEEP-STR-008
**Location:** `systems/race_randomizer.py:178-179`
**Issue:** `_APT_HIGH_RANGE = (55, 80)` and `_APT_LOW_RANGE = (20, 45)` are module-level constants used only in `randomize_aptitudes`. Moving them into the method as locals would reduce the class's attribute surface.
**Estimated LOC:** 2 (move inside method)
**Recommendation:** Minor — move inside the static method.

#### INFO: galaxy_warp_generator.py has legacy b/w compat note
**ID:** DEEP-STR-009
**Location:** `data/galaxy_warp_generator.py:407-415`
**Issue:** `_apply_warp_point_intrinsic_abilities` has a back-compat note about creating `Random()` when rng is None, but `generate_warp_lanes` now accepts an `rng` parameter that defaults to None (unused currently — the caller `GameInitializer` doesn't pass it).
**Recommendation:** Wire the `rng` parameter through `Galaxy.generate_warp_lanes → GalaxyWarpGenerator.generate_warp_lanes → _apply_warp_point_intrinsic_abilities` so seeded galaxy generation is fully deterministic.

#### INFO: Hardcoded resource list in fleet_dto.py:209-218
**ID:** DEEP-STR-010
**Location:** `facade/dto/fleet_dto.py:209-218`
**Issue:** `FleetInfo.from_fleet()` hardcodes the list of cargo resource names `("metals", "organics", "vapors", "radioactives", "exotics", "fuel", "energy", "ammo")`. If resource types are added via modding, the DTO silently omits them from the UI.
**Recommended:** Derive the set from `ResourceCatalog` or from the fleet's actual cargo_contents keys to be data-driven.

#### INFO: `HappinessEngine` and `PopulationEngine` share `_get_race_config` (repeated from DEEP-STR-001)
**ID:** DEEP-STR-011
**Location:** (See DEEP-STR-001)
**Issue:** These two engines are the only consumers of this resolution pattern. If they remain the only ones, a 1-line shared function suffices. But their shape (registry-first, empire-fallback, race_id match) is also partially replicated in `planet_habitability_multiplier` in `formulas/colony_output.py` (lines 83-93) — three sites that resolve race_id → RaceConfig with subtly different fallback semantics.
**Recommendation:** Consolidate all three race-resolution paths into one function with a clear contract (registry first, then empire.race_config match, then None). Three implementations with three different behaviors is a maintenance hazard.

## File Coverage Verification

| File | Status |
|------|--------|
| strategy/__init__.py | Read ✓ |
| strategy/adapters/__init__.py | Read ✓ |
| strategy/adapters/simulation_adapter.py | Read ✓ |
| strategy/combat/__init__.py | Read ✓ |
| strategy/combat/post_battle_hook.py | Read ✓ |
| strategy/combat/spec_compiler.py | Read ✓ |
| strategy/config/__init__.py | Read ✓ (empty) |
| strategy/config/economy_config.py | Read ✓ |
| strategy/data/__init__.py | Read ✓ (empty) |
| strategy/data/build_context.py | Read ✓ |
| strategy/data/build_queue_source.py | Read ✓ |
| strategy/data/classification_config.py | Read ✓ |
| strategy/data/colony_species_config.py | Read ✓ |
| strategy/data/component_activation_state.py | Read ✓ |
| strategy/data/design_metadata.py | Read ✓ |
| strategy/data/design_role.py | Read ✓ |
| strategy/data/design_role_registry.py | Read ✓ |
| strategy/data/empire.py | Read ✓ |
| strategy/data/environmental_preference.py | Read ✓ |
| strategy/data/fleet.py | Read ✓ |
| strategy/data/fleet_battle_adapter.py | Read ✓ |
| strategy/data/fleet_capability_calculator.py | Read ✓ |
| strategy/data/fleet_consumable_aggregator.py | Read ✓ |
| strategy/data/fleet_hierarchy.py | Read ✓ |
| strategy/data/fleet_pursuer_tracker.py | Read ✓ |
| strategy/data/galaxy.py | Read ✓ |
| strategy/data/galaxy_entity_registry.py | Read ✓ |
| strategy/data/galaxy_spatial_index.py | Read ✓ |
| strategy/data/galaxy_system_generator.py | Read ✓ |
| strategy/data/galaxy_warp_generator.py | Read ✓ |
| strategy/data/group_policy_registry.py | Read ✓ |
| strategy/data/habitability_factors.py | Read ✓ |
| strategy/data/homeworld_presets.py | Read ✓ |
| strategy/data/naming.py | Read ✓ |
| strategy/data/orbital_generation_config.py | Read ✓ |
| strategy/data/order_serializer.py | Read ✓ |
| strategy/data/order_types.py | Read ✓ |
| strategy/data/pathfinding.py | Read ✓ |
| strategy/data/physics.py | Read ✓ |
| strategy/data/planet.py | Read ✓ |
| strategy/data/planet_atmosphere.py | Read ✓ |
| strategy/data/planet_gen.py | Read ✓ |
| strategy/data/planet_naming.py | Read ✓ |
| strategy/data/planet_physics.py | Read ✓ |
| strategy/data/planetary_facility.py | Read ✓ |
| strategy/data/race_caption_loader.py | Read ✓ |
| strategy/data/race_config.py | Read ✓ |
| strategy/data/race_point_budget.py | Read ✓ |
| strategy/data/resource_generation_config.py | Read ✓ |
| strategy/data/ship_cargo_manager.py | Read ✓ |
| strategy/data/ship_consumable_manager.py | Read ✓ |
| strategy/data/ship_display_formatter.py | Read ✓ |
| strategy/data/ship_instance.py | Read ✓ |
| strategy/data/ship_instance_bridge.py | Read ✓ |
| strategy/data/ship_instance_serializer.py | Read ✓ |
| strategy/data/spatial_index.py | Read ✓ |
| strategy/data/species_population.py | Read ✓ |
| strategy/data/squadron.py | Read ✓ |
| strategy/data/star_generation_config.py | Read ✓ |
| strategy/data/stars.py | Read ✓ |
| strategy/data/storm.py | Read ✓ |
| strategy/data/task_force.py | Read ✓ |
| strategy/engine/action_execution_engine.py | Read ✓ |
| strategy/engine/atmosphere_engine.py | Read ✓ |
| strategy/engine/command_handlers.py | Read ✓ |
| strategy/engine/commands.py | Read ✓ |
| strategy/engine/component_activation_engine.py | Read ✓ |
| strategy/engine/conflict_resolution_engine.py | Read ✓ |
| strategy/engine/construction_forecast.py | Read ✓ |
| strategy/engine/consumable_management_engine.py | Read ✓ |
| strategy/engine/empire_economy_calculator.py | Read ✓ |
| strategy/engine/environmental_hazard_engine.py | Read ✓ |
| strategy/engine/fleet_movement_engine.py | Read ✓ |
| strategy/engine/game_config.py | Read ✓ |
| strategy/engine/game_initializer.py | Read ✓ |
| strategy/engine/game_session.py | Read ✓ |
| strategy/engine/handlers/__init__.py | Read ✓ |
| strategy/engine/handlers/base.py | Read ✓ |
| strategy/engine/handlers/build.py | Read ✓ |
| strategy/engine/handlers/construction_queue.py | Read ✓ |
| strategy/engine/handlers/movement.py | Read ✓ |
| strategy/engine/handlers/order_queue.py | Read ✓ |
| strategy/engine/handlers/registry_factory.py | Read ✓ |
| strategy/engine/handlers/transfer.py | Read ✓ |
| strategy/engine/happiness_engine.py | Read ✓ |
| strategy/engine/harvesting_engine.py | Read ✓ |
| strategy/engine/order_processor.py | Read ✓ |
| strategy/engine/organics_consumption_engine.py | Read ✓ |
| strategy/engine/planet_action_engine.py | Read ✓ |
| strategy/engine/planet_command_handlers.py | Read ✓ |
| strategy/engine/planet_energy_engine.py | Read ✓ |
| strategy/engine/planet_modifier_effect_engine.py | Read ✓ |
| strategy/engine/population_engine.py | Read ✓ |
| strategy/engine/production_engine.py | Read ✓ |
| strategy/engine/production_math.py | Read ✓ |
| strategy/engine/production_spawner.py | Read ✓ |
| strategy/engine/quality_engine.py | Read ✓ |
| strategy/engine/resupply_engine.py | Read ✓ |
| strategy/engine/superweapon_command_handlers.py | Read ✓ |
| strategy/engine/superweapon_order_processor.py | Read ✓ |
| strategy/engine/turn_engine.py | Read ✓ |
| strategy/engine/turn_engine_config.py | Read ✓ |
| strategy/engine/turn_state_snapshot.py | Read ✓ |
| strategy/engine/water_engine.py | Read ✓ |
| strategy/events/__init__.py | Read ✓ |
| strategy/events/event_log.py | Read ✓ |
| strategy/events/event_types.py | Read ✓ |
| strategy/facade/__init__.py | Read ✓ |
| strategy/facade/dto/__init__.py | Read ✓ |
| strategy/facade/dto/build_queue_dto.py | Read ✓ |
| strategy/facade/dto/colony_demographic_view.py | Read ✓ |
| strategy/facade/dto/empire_dto.py | Read ✓ |
| strategy/facade/dto/fleet_dto.py | Read ✓ |
| strategy/facade/dto/fleet_hierarchy_dto.py | Read ✓ |
| strategy/facade/dto/planet_dto.py | Read ✓ |
| strategy/facade/dto/system_dto.py | Read ✓ |
| strategy/facade/slices/__init__.py | Read ✓ |
| strategy/facade/slices/_facade_state.py | Read ✓ |
| strategy/facade/slices/command_dispatch_slice.py | Read ✓ |
| strategy/facade/slices/economy_slice.py | Read ✓ |
| strategy/facade/slices/empire_slice.py | Read ✓ |
| strategy/facade/slices/event_slice.py | Read ✓ |
| strategy/facade/slices/fleet_slice.py | Read ✓ |
| strategy/facade/slices/planet_slice.py | Read ✓ |
| strategy/facade/slices/system_slice.py | Read ✓ |
| strategy/facade/strategy_session_facade.py | Read ✓ |
| strategy/formulas/__init__.py | Read ✓ |
| strategy/formulas/colony_output.py | Read ✓ |
| strategy/formulas/habitability.py | Read ✓ |
| strategy/generation/__init__.py | Read ✓ |
| strategy/generation/density/__init__.py | Read ✓ |
| strategy/generation/density/density_map.py | Read ✓ |
| strategy/generation/density/primitives/__init__.py | Read ✓ |
| strategy/generation/density/primitives/density_primitive.py | Read ✓ |
| strategy/generation/density/primitives/geometric.py | Read ✓ |
| strategy/generation/density/primitives/linear.py | Read ✓ |
| strategy/generation/density/primitives/noise.py | Read ✓ |
| strategy/generation/density/primitives/radial.py | Read ✓ |
| strategy/generation/density/primitives/ring.py | Read ✓ |
| strategy/generation/density/primitives/spiral_arm.py | Read ✓ |
| strategy/generation/loaders/__init__.py | Read ✓ |
| strategy/generation/loaders/astrophysics_loader.py | Read ✓ |
| strategy/generation/loaders/galaxy_layouts_loader.py | Read ✓ |
| strategy/generation/loaders/system_blueprints_loader.py | Read ✓ |
| strategy/generation/placement_strategies.py | Read ✓ |
| strategy/generation/planet_image_registry.py | Read ✓ |
| strategy/generation/region_classifier.py | Read ✓ |
| strategy/generation/star_image_registry.py | Read ✓ |
| strategy/generation/storm_generator.py | Read ✓ |
| strategy/interfaces/__init__.py | Read ✓ |
| strategy/interfaces/battle_resolver.py | Read ✓ |
| strategy/interfaces/engines.py | Read ✓ |
| strategy/quickstart_builder.py | Read ✓ |
| strategy/services/__init__.py | Read ✓ |
| strategy/services/ability_iterator.py | Read ✓ |
| strategy/services/ability_sources/__init__.py | Read ✓ |
| strategy/services/ability_sources/facility.py | Read ✓ |
| strategy/services/ability_sources/fleet.py | Read ✓ |
| strategy/services/ability_sources/intrinsic_roll.py | Read ✓ |
| strategy/services/ability_sources/labels.py | Read ✓ |
| strategy/services/ability_sources/planet_intrinsic.py | Read ✓ |
| strategy/services/ability_sources/star.py | Read ✓ |
| strategy/services/ability_sources/storm.py | Read ✓ |
| strategy/services/ability_sources/system_archetype.py | Read ✓ |
| strategy/services/ability_sources/warp_point.py | Read ✓ |
| strategy/services/action_time_resolver.py | Read ✓ |
| strategy/services/cargo_transfer_service.py | Read ✓ |
| strategy/services/combat_modifier_collector.py | Read ✓ |
| strategy/services/component_inspector.py | Read ✓ |
| strategy/services/deployment_zone_calculator.py | Read ✓ |
| strategy/services/design_cost_calculator.py | Read ✓ |
| strategy/services/design_validator.py | Read ✓ |
| strategy/services/empire_economy_service.py | Read ✓ |
| strategy/services/fleet_cargo_projector.py | Read ✓ |
| strategy/services/fleet_navigation_service.py | Read ✓ |
| strategy/services/fleet_speed_calculator.py | Read ✓ |
| strategy/services/modifier_resolver.py | Read ✓ |
| strategy/services/planet_economy_projector.py | Read ✓ |
| strategy/services/race_description_llm_controller.py | Read ✓ |
| strategy/services/race_description_prompt_builder.py | Read ✓ |
| strategy/services/stabilizer_registry.py | Read ✓ |
| strategy/services/strategic_ability_scanner.py | Read ✓ |
| strategy/services/system_destroyer.py | Read ✓ |
| strategy/services/system_effects_collector.py | Read ✓ |
| strategy/services/task_group_suggester.py | Read ✓ |
| strategy/systems/design_library.py | Read ✓ |
| strategy/systems/race_library.py | Read ✓ |
| strategy/systems/race_randomizer.py | Read ✓ |
| strategy/systems/save_game_service.py | Read ✓ |
| strategy/validation/__init__.py | Read ✓ |
| strategy/validation/colonize_validator.py | Read ✓ |
| strategy/validation/planet_order_validator.py | Read ✓ |
| strategy/validation/superweapon_validator.py | Read ✓ |
| strategy/validation/transfer_validator.py | Read ✓ |
