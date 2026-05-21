# Coverage Data — Shard 19

**Coverage source:** heuristic
**File count:** 50 | **LOC estimate:** 9592
**Tiers:** 0=13 1=4 2=20 3=13

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/ai/behaviors.py (Tier 2: TIER_2_PARTIAL, 424 LOC, layer: ai)
- Total symbols: 29 | Heuristically tested: 25
- Candidate test files (3):
  - tests/unit/ai/test_advanced_behaviors.py
  - tests/unit/ai/test_behavior_units.py
  - tests/unit/ai/test_erratic_behavior_seeded.py
- Heuristically untested symbols (4):
  - _flee_direction
  - AIBehavior.__init__
  - AttackRunBehavior.__init__
  - ErraticBehavior.__init__

### game/ai/satellite_controller.py (Tier 2: TIER_2_PARTIAL, 123 LOC, layer: ai)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ai/test_satellite_controller.py
- Heuristically untested symbols (1):
  - SatelliteAIController._find_nearest_enemy

### game/ai/spatial_behaviors/_formation_utils.py (Tier 0: TIER_0_NO_TESTS, 39 LOC, layer: ai)
- Total symbols: 1 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (1):
  - compute_circular_position

### game/core/error_codes.py (Tier 3: TIER_3_APPARENTLY_COVERED, 223 LOC, layer: core)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (15):
  - tests/unit/core/test_error_codes.py
  - tests/unit/core/test_exceptions.py
  - tests/unit/core/test_validation.py
  - tests/unit/core/test_validation_helpers.py
  - tests/unit/services/llm/test_background.py
  - tests/unit/services/llm/test_deepseek.py
  - tests/unit/services/llm/test_factory.py
  - tests/unit/simulation/test_formula_evaluator.py
  - ... and 7 more

### game/core/return_destination.py (Tier 3: TIER_3_APPARENTLY_COVERED, 23 LOC, layer: core)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (4):
  - tests/unit/simulation/test_battle_config.py
  - tests/unit/test_app_delegators.py
  - tests/unit/test_lab/test_visual_run.py
  - tests/unit/ui/test_scene_protocol.py

### game/simulation/battle_runner.py (Tier 2: TIER_2_PARTIAL, 735 LOC, layer: simulation)
- Total symbols: 11 | Heuristically tested: 9
- Candidate test files (8):
  - tests/unit/simulation/battle_controller/test_outcome_emission.py
  - tests/unit/simulation/battle_runner/test_spec_component_validation.py
  - tests/unit/simulation/systems/test_battle_engine_modifier_stack.py
  - tests/unit/simulation/test_battle_outcome_replay_id.py
  - tests/unit/simulation/test_battle_runner.py
  - tests/unit/simulation/test_battle_runner_component_hp.py
  - tests/unit/simulation/test_battle_runner_di.py
  - tests/unit/simulation/test_battle_runner_telemetry.py
- Heuristically untested symbols (2):
  - _attach_telemetry
  - _build_ship_outcome

### game/simulation/combat/boundary.py (Tier 3: TIER_3_APPARENTLY_COVERED, 221 LOC, layer: simulation)
- Total symbols: 21 | Heuristically tested: 21
- Candidate test files (12):
  - tests/unit/combat_lab/test_spec_compiler.py
  - tests/unit/simulation/battle_controller/test_mechanics.py
  - tests/unit/simulation/battle_controller/test_outcome_emission.py
  - tests/unit/simulation/battle_controller/test_start_from_spec.py
  - tests/unit/simulation/battle_controller/test_state.py
  - tests/unit/simulation/combat/test_boundary.py
  - tests/unit/simulation/managers/test_retreat_manager.py
  - tests/unit/simulation/replay/test_serialization.py
  - ... and 4 more

### game/simulation/combat/damage_calculator.py (Tier 2: TIER_2_PARTIAL, 244 LOC, layer: simulation)
- Total symbols: 9 | Heuristically tested: 4
- Candidate test files (5):
  - tests/unit/simulation/combat/test_damage_calculator.py
  - tests/unit/simulation/combat/test_damage_calculator_events.py
  - tests/unit/simulation/combat/test_ship_death_at_zero_hp.py
  - tests/unit/simulation/systems/test_battle_rng_isolation.py
  - tests/unit/strategy/engine/test_minefield_resolver.py
- Heuristically untested symbols (5):
  - DamageCalculator._absorb_shields
  - DamageCalculator._reduce_emissive_armor
  - DamageCalculator._absorb_regenerating_armor
  - DamageCalculator._distribute_hull_damage
  - DamageCalculator._finalize_damage

### game/simulation/components/abilities/colonize.py (Tier 2: TIER_2_PARTIAL, 81 LOC, layer: simulation)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/simulation/components/abilities/test_colonize_harvester.py
- Heuristically untested symbols (1):
  - ColonizePlanet._parse_attrs

### game/simulation/components/abilities/defense.py (Tier 2: TIER_2_PARTIAL, 113 LOC, layer: simulation)
- Total symbols: 7 | Heuristically tested: 6
- Candidate test files (7):
  - tests/unit/abilities/test_ability_layer_scope.py
  - tests/unit/modifiers/test_defense_marker_bindings.py
  - tests/unit/simulation/armor_mechanics/test_damage_mechanics.py
  - tests/unit/simulation/components/abilities/test_combat_modifiers.py
  - tests/unit/simulation/components/abilities/test_defense_integration.py
  - tests/unit/simulation/components/abilities/test_defense_isolation.py
  - tests/unit/simulation/components/abilities/test_static_value_ability.py
- Heuristically untested symbols (1):
  - ShieldRegeneratingArmor

### game/simulation/components/abilities/planetary/stat_modifiers.py (Tier 0: TIER_0_NO_TESTS, 233 LOC, layer: simulation)
- Total symbols: 16 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (16):
  - ShieldModifierAbility
  - ShieldModifierAbility.__init__
  - ShieldModifierAbility.get_primary_value
  - ShieldModifierAbility.get_ui_rows
  - DamageModifierAbility
  - DamageModifierAbility.__init__
  - DamageModifierAbility.get_primary_value
  - DamageModifierAbility.get_ui_rows
  - ThrustModifierAbility
  - ThrustModifierAbility.__init__
  - ThrustModifierAbility.get_primary_value
  - ThrustModifierAbility.get_ui_rows
  - StrategicSpeedModifierAbility
  - StrategicSpeedModifierAbility.__init__
  - StrategicSpeedModifierAbility.get_primary_value
  - ... and 1 more

### game/simulation/components/abilities/propulsion.py (Tier 2: TIER_2_PARTIAL, 128 LOC, layer: simulation)
- Total symbols: 8 | Heuristically tested: 7
- Candidate test files (4):
  - tests/unit/abilities/test_strategic_movement.py
  - tests/unit/abilities/test_warp_jump.py
  - tests/unit/combat_lab/test_weapon_stats_collection.py
  - tests/unit/modifiers/test_propulsion_ability_bindings.py
- Heuristically untested symbols (1):
  - WarpJump._parse_attrs

### game/simulation/entities/ship_loader.py (Tier 3: TIER_3_APPARENTLY_COVERED, 173 LOC, layer: simulation)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (30):
  - tests/unit/ai/test_ai.py
  - tests/unit/ai/test_ai_protocols.py
  - tests/unit/ai/test_movement_and_ai.py
  - tests/unit/builder/test_builder_logic.py
  - tests/unit/builder/test_builder_validation.py
  - tests/unit/core/test_pure_loaders.py
  - tests/unit/entities/test_component_di.py
  - tests/unit/entities/test_planetary_complex.py
  - ... and 22 more

### game/simulation/managers/__init__.py (Tier 0: TIER_0_NO_TESTS, 12 LOC, layer: simulation)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/simulation/replay/replay_outcome.py (Tier 0: TIER_0_NO_TESTS, 49 LOC, layer: simulation)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - ReplayOutcome
  - ReplayOutcome.from_battle_outcome
  - ReplayOutcome.to_battle_outcome
  - ReplayOutcome.to_dict
  - ReplayOutcome.from_dict

### game/simulation/services/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 16 LOC, layer: simulation)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (6):
  - tests/unit/combat_lab/test_runner_cleanup.py
  - tests/unit/simulation/services/test_ship_materializer.py
  - tests/unit/simulation/test_battle_runner.py
  - tests/unit/simulation/test_battle_runner_di.py
  - tests/unit/ui/services/battle_ui_service/test_state_and_integration.py
  - tests/unit/ui/test_battle_screen_simulation.py

### game/simulation/systems/attack_processor.py (Tier 0: TIER_0_NO_TESTS, 220 LOC, layer: simulation)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - collect_new_attacks
  - process_attacks
  - process_projectile_attack
  - process_launch_attack
  - _spawn_from_carried_vehicle

### game/simulation/systems/battle_end_conditions.py (Tier 2: TIER_2_PARTIAL, 532 LOC, layer: simulation)
- Total symbols: 68 | Heuristically tested: 49
- Candidate test files (30):
  - tests/unit/ai/test_ai_n_team_targeting.py
  - tests/unit/combat_lab/services/test_ab_battle_runner.py
  - tests/unit/combat_lab/test_spec_compiler.py
  - tests/unit/combat_lab/test_test_metadata_end_conditions.py
  - tests/unit/simulation/battle_controller/test_outcome_emission.py
  - tests/unit/simulation/components/abilities/test_tactical_fighter_launch.py
  - tests/unit/simulation/components/abilities/test_tactical_satellite_launch.py
  - tests/unit/simulation/replay/test_replay_player.py
  - ... and 22 more
- Heuristically untested symbols (19):
  - BattleEndCondition
  - BattleEndCondition._serialize_fields
  - TickLimitCondition._serialize_fields
  - TickLimitCondition.__repr__
  - TeamEliminatedCondition._serialize_fields
  - TeamEliminatedCondition.__repr__
  - TeamIncapacitatedCondition._team_has_capability
  - TeamIncapacitatedCondition.__repr__
  - EscapeCondition._serialize_fields
  - EscapeCondition.__repr__
  - ShipDestroyedCondition._serialize_fields
  - ShipDestroyedCondition.__repr__
  - NeverCondition.__repr__
  - MassRatioCondition._serialize_fields
  - MassRatioCondition.__repr__
  - ... and 4 more

### game/simulation/systems/fighter_reboard.py (Tier 2: TIER_2_PARTIAL, 380 LOC, layer: simulation)
- Total symbols: 13 | Heuristically tested: 6
- Candidate test files (4):
  - tests/unit/simulation/systems/test_fighter_reboard.py
  - tests/unit/simulation/systems/test_fighter_reboard_component_state.py
  - tests/unit/simulation/systems/test_fighter_reboard_overflow_component_state.py
  - tests/unit/simulation/systems/test_satellite_reboard.py
- Heuristically untested symbols (7):
  - _ship_is_alive
  - _candidate_alive
  - _resolve_owner_for_team
  - _resolve_sector_hex
  - _ensure_overflow_fighter_group
  - _ensure_overflow_group
  - _mint_overflow_id

### game/simulation/systems/resource_manager.py (Tier 2: TIER_2_PARTIAL, 208 LOC, layer: simulation)
- Total symbols: 22 | Heuristically tested: 20
- Candidate test files (5):
  - tests/unit/core/test_protocols_boundary.py
  - tests/unit/simulation/components/abilities/test_resource_consumption.py
  - tests/unit/simulation/systems/test_resource_manager_edge_cases.py
  - tests/unit/simulation/systems/test_ship_stats_calculator_phases.py
  - tests/unit/simulation/test_component_decoupling.py
- Heuristically untested symbols (2):
  - ResourceState.__init__
  - ResourceRegistry.__init__

### game/strategy/combat/pre_tick_setup/__init__.py (Tier 0: TIER_0_NO_TESTS, 20 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/strategy/combat/pre_tick_setup/reboard_setup.py (Tier 0: TIER_0_NO_TESTS, 46 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - build_fighter_reboard_setup
  - _setup

### game/strategy/data/containable.py (Tier 3: TIER_3_APPARENTLY_COVERED, 134 LOC, layer: strategy)
- Total symbols: 12 | Heuristically tested: 12
- Candidate test files (8):
  - tests/unit/simulation/components/abilities/test_container_ability.py
  - tests/unit/strategy/data/test_containable.py
  - tests/unit/strategy/data/test_container.py
  - tests/unit/strategy/data/test_ship_instance_container_views.py
  - tests/unit/strategy/facade/test_container_snapshots.py
  - tests/unit/ui/screens/test_transfer_mass_preview.py
  - tests/unit/ui/screens/test_transfer_mixed_content.py
  - tests/unit/ui/screens/test_transfer_view_model_container.py

### game/strategy/data/empire.py (Tier 3: TIER_3_APPARENTLY_COVERED, 430 LOC, layer: strategy)
- Total symbols: 19 | Heuristically tested: 19
- Candidate test files (41):
  - tests/unit/core/test_protocols.py
  - tests/unit/strategy/data/test_build_queue_source.py
  - tests/unit/strategy/data/test_empire.py
  - tests/unit/strategy/data/test_empire_deployed_groups.py
  - tests/unit/strategy/data/test_empire_fleet_registration.py
  - tests/unit/strategy/data/test_empire_resources.py
  - tests/unit/strategy/data/test_fleet_display_name.py
  - tests/unit/strategy/data/test_fleet_id_global.py
  - ... and 33 more

### game/strategy/data/galaxy_entity_registry.py (Tier 2: TIER_2_PARTIAL, 169 LOC, layer: strategy)
- Total symbols: 17 | Heuristically tested: 11
- Candidate test files (1):
  - tests/unit/strategy/data/test_galaxy_entity_registry.py
- Heuristically untested symbols (6):
  - GalaxyEntityRegistry.add_system
  - GalaxyEntityRegistry._register_zones_from_system
  - GalaxyEntityRegistry._rebuild_warp_point_index_for
  - GalaxyEntityRegistry.rebuild_all_warp_point_indices
  - GalaxyEntityRegistry._index_planet
  - GalaxyEntityRegistry.get_next_fleet_id

### game/strategy/data/galaxy_protocols.py (Tier 2: TIER_2_PARTIAL, 215 LOC, layer: strategy)
- Total symbols: 20 | Heuristically tested: 8
- Candidate test files (4):
  - tests/unit/strategy/data/test_galaxy_protocols.py
  - tests/unit/strategy/services/test_galaxy_pathfinding_service.py
  - tests/unit/strategy/services/test_planet_habitability_service.py
  - tests/unit/test_context_habitability_accessors.py
- Heuristically untested symbols (12):
  - IGalaxySpatialQuery.get_system_at_location
  - IGalaxySpatialQuery.get_planets_at_global_hex
  - IGalaxySpatialQuery.get_zones_at_global_hex
  - IGalaxySpatialQuery.get_planet_global_hex
  - IStockpileHolder.add_to_stockpile
  - IStockpileHolder.consume_from_stockpile
  - IStockpileHolder.has_stockpile
  - IStockpileHolder.get_stockpile
  - IStagingYardHolder.get_staging_mass
  - IStagingYardHolder.add_to_staging_yard
  - IStagingYardHolder.remove_from_staging_yard
  - IStagingYardHolder.max_staging_mass

### game/strategy/engine/conflict_resolution_engine.py (Tier 3: TIER_3_APPARENTLY_COVERED, 577 LOC, layer: strategy)
- Total symbols: 13 | Heuristically tested: 13
- Candidate test files (10):
  - tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py
  - tests/unit/strategy/conflict_resolution/test_core.py
  - tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py
  - tests/unit/strategy/engine/test_conflict_deployed_group_trigger.py
  - tests/unit/strategy/engine/test_conflict_resolution_event_replay.py
  - tests/unit/strategy/engine/test_conflict_resolution_modifier_logging.py
  - tests/unit/strategy/engine/test_conflict_round_budget.py
  - tests/unit/strategy/engine/test_engine_validation.py
  - ... and 2 more

### game/strategy/engine/order_handlers/lay_mines.py (Tier 2: TIER_2_PARTIAL, 380 LOC, layer: strategy)
- Total symbols: 14 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/strategy/engine/order_handlers/test_lay_mines_handler.py
  - tests/unit/strategy/engine/test_issuer_execution_contract.py
- Heuristically untested symbols (9):
  - _stable_scatter_seed
  - _scatter_positions
  - _cos
  - _sin
  - LayMinesOrderHandler._run_with_issuer
  - LayMinesOrderHandler._find_ship
  - LayMinesOrderHandler._extract_turn
  - LayMinesOrderHandler._create_mine_group
  - LayMinesOrderHandler._mint_deployed_group_id

### game/strategy/engine/superweapon_handlers/stellerate_star.py (Tier 0: TIER_0_NO_TESTS, 79 LOC, layer: strategy)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - process_stellerate_star
  - _precheck
  - _effect

### game/strategy/formulas/colony_output.py (Tier 3: TIER_3_APPARENTLY_COVERED, 164 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (5):
  - tests/unit/strategy/data/test_planet_habitability_cache.py
  - tests/unit/strategy/engine/test_harvesting_engine_habitability.py
  - tests/unit/strategy/formulas/test_colony_output.py
  - tests/unit/strategy/production_engine/test_habitability.py
  - tests/unit/strategy/services/test_planet_economy_projector.py

### game/strategy/generation/density/primitives/density_primitive.py (Tier 2: TIER_2_PARTIAL, 45 LOC, layer: strategy)
- Total symbols: 3 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/strategy/generation/density/test_density_primitive.py
- Heuristically untested symbols (2):
  - DensityPrimitive
  - DensityPrimitive.evaluate

### game/strategy/interfaces/engines/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 96 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (10):
  - tests/unit/strategy/interfaces/test_engines_leaf_path_discipline.py
  - tests/unit/strategy/mocks/mock_engines.py
  - tests/unit/strategy/turn_engine/test_default_tick_phase_list.py
  - tests/unit/strategy/turn_engine/test_dependency_injection.py
  - tests/unit/strategy/turn_engine/test_turn_end_of_turn_engine_rollback.py
  - tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py
  - tests/unit/strategy/turn_engine/test_turn_engine_init_precedence.py
  - tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py
  - ... and 2 more

### game/strategy/interfaces/engines/logistics.py (Tier 0: TIER_0_NO_TESTS, 153 LOC, layer: strategy)
- Total symbols: 7 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (7):
  - IConsumableEngine
  - IConsumableEngine.process_per_turn_consumption
  - IResupplyEngine
  - IResupplyEngine.process_fuel_generation
  - IResupplyEngine.process_fleet_resupply
  - IHarvestingEngine
  - IHarvestingEngine.process_harvesting_tick

### game/strategy/services/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 5 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (12):
  - tests/unit/strategy/data/test_design_role.py
  - tests/unit/strategy/engine/test_conflict_resolution_modifier_logging.py
  - tests/unit/strategy/fleet_navigation/test_navigation_pure.py
  - tests/unit/strategy/services/test_action_time_resolver.py
  - tests/unit/strategy/services/test_combat_modifier_collector.py
  - tests/unit/strategy/services/test_component_layers.py
  - tests/unit/strategy/services/test_empire_economy_service.py
  - tests/unit/strategy/services/test_replay_verification_coordinator.py
  - ... and 4 more

### game/strategy/services/ability_sources/facility.py (Tier 0: TIER_0_NO_TESTS, 87 LOC, layer: strategy)
- Total symbols: 9 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (9):
  - FacilityAbilitySource
  - FacilityAbilitySource.source_kind
  - FacilityAbilitySource.source_label
  - FacilityAbilitySource.source_id
  - FacilityAbilitySource.owner_id
  - FacilityAbilitySource.get_abilities
  - FacilityAbilitySource.affects_hex
  - FacilityAbilitySource.affects_system
  - FacilityAbilitySource.get_activation_state

### game/strategy/services/ability_sources/star.py (Tier 0: TIER_0_NO_TESTS, 98 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (10):
  - StarAbilitySource
  - StarAbilitySource.source_kind
  - StarAbilitySource.source_label
  - StarAbilitySource.source_id
  - StarAbilitySource.owner_id
  - StarAbilitySource.get_abilities
  - StarAbilitySource.affects_hex
  - StarAbilitySource._has_system_scope_ability
  - StarAbilitySource.affects_system
  - StarAbilitySource.get_activation_state

### game/strategy/services/ability_sources/storm.py (Tier 0: TIER_0_NO_TESTS, 77 LOC, layer: strategy)
- Total symbols: 9 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (9):
  - StormAbilitySource
  - StormAbilitySource.source_kind
  - StormAbilitySource.source_label
  - StormAbilitySource.source_id
  - StormAbilitySource.owner_id
  - StormAbilitySource.get_abilities
  - StormAbilitySource.affects_hex
  - StormAbilitySource.affects_system
  - StormAbilitySource.get_activation_state

### game/ui/config.py (Tier 3: TIER_3_APPARENTLY_COVERED, 68 LOC, layer: ui)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (5):
  - tests/unit/ui/screens/test_orders_window.py
  - tests/unit/ui/screens/test_star_list_window.py
  - tests/unit/ui/screens/test_strategy_screen.py
  - tests/unit/ui/test_config.py
  - tests/unit/ui/test_ui_config.py

### game/ui/filters/filter_state.py (Tier 3: TIER_3_APPARENTLY_COVERED, 10 LOC, layer: ui)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (13):
  - tests/unit/ui/components/filters/test_tri_state_widget.py
  - tests/unit/ui/filters/test_filter_state.py
  - tests/unit/ui/filters/test_filter_state_manager.py
  - tests/unit/ui/screens/test_empire_build_queue_filter_manager.py
  - tests/unit/ui/screens/test_empire_build_queue_sidebar.py
  - tests/unit/ui/screens/test_empire_build_queue_viewmodel.py
  - tests/unit/ui/screens/test_empire_build_queue_window.py
  - tests/unit/ui/screens/test_fleet_report_filters.py
  - ... and 5 more

### game/ui/panels/build_queue_drag_handler.py (Tier 3: TIER_3_APPARENTLY_COVERED, 361 LOC, layer: ui)
- Total symbols: 8 | Heuristically tested: 8
- Candidate test files (3):
  - tests/unit/ui/panels/test_build_queue_catalog_threading.py
  - tests/unit/ui/panels/test_build_queue_drag_handler.py
  - tests/unit/ui/screens/test_build_queue_screen_lifecycle.py

### game/ui/panels/race_theme_gallery.py (Tier 2: TIER_2_PARTIAL, 211 LOC, layer: ui)
- Total symbols: 14 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/ui/test_race_theme_gallery.py
- Heuristically untested symbols (9):
  - RaceThemeGallery._get_label_text
  - RaceThemeGallery._get_thumb_size
  - RaceThemeGallery._get_preview_size
  - RaceThemeGallery._get_object_id_prefix
  - RaceThemeGallery._get_preview_panel_object_id
  - RaceThemeGallery._get_current_selection
  - RaceThemeGallery._set_selection
  - RaceThemeGallery._update_preview
  - RaceThemeGallery._populate_gallery

### game/ui/screens/battle_setup_state.py (Tier 2: TIER_2_PARTIAL, 265 LOC, layer: ui)
- Total symbols: 19 | Heuristically tested: 14
- Candidate test files (4):
  - tests/unit/ui/screens/battle_setup/test_controller.py
  - tests/unit/ui/screens/battle_setup/test_spec_compiler.py
  - tests/unit/ui/screens/battle_setup/test_spec_compiler_formation.py
  - tests/unit/ui/screens/test_battle_setup_state.py
- Heuristically untested symbols (5):
  - _generate_fleet_id
  - BattleSetupSide.__init__
  - BattleSetupSide.ship_count
  - BattleSetupState.__init__
  - BattleSetupState.get_side

### game/ui/screens/build_queue_input_router.py (Tier 2: TIER_2_PARTIAL, 548 LOC, layer: ui)
- Total symbols: 21 | Heuristically tested: 9
- Candidate test files (2):
  - tests/unit/ui/screens/test_build_queue_screen_lifecycle.py
  - tests/unit/ui/screens/test_sub_window_hotkeys.py
- Heuristically untested symbols (12):
  - BuildQueueInputRouter._dispatch_add_to_queue_command
  - BuildQueueInputRouter._dispatch_remove_from_queue_command
  - BuildQueueInputRouter._dispatch_toggle_pause_command
  - BuildQueueInputRouter._refresh_queue_selector
  - BuildQueueInputRouter.handle_event
  - BuildQueueInputRouter._handle_button_press
  - BuildQueueInputRouter._handle_virtual_table_action
  - BuildQueueInputRouter._handle_remove
  - BuildQueueInputRouter._handle_drag_operations
  - BuildQueueInputRouter._handle_keyboard_input
  - BuildQueueInputRouter._prompt_target_planet
  - BuildQueueInputRouter.on_active_player_changed

### game/ui/screens/builder/detail_panel.py (Tier 2: TIER_2_PARTIAL, 299 LOC, layer: ui)
- Total symbols: 10 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/ui/screens/builder/test_detail_panel.py
  - tests/unit/ui/test_detail_panel_rendering.py
- Heuristically untested symbols (7):
  - ComponentDetailPanel.__init__
  - ComponentDetailPanel.show_details_popup
  - ComponentDetailPanel._clear_display
  - ComponentDetailPanel._update_image
  - ComponentDetailPanel.set_position
  - ComponentDetailPanel.handle_event
  - ComponentDetailPanel.draw

### game/ui/screens/race_setup/panel_factory.py (Tier 0: TIER_0_NO_TESTS, 177 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (7):
  - create_summary_panel
  - create_identity_panel
  - create_visuals_panel
  - create_ships_panel
  - create_environment_panel
  - create_aptitudes_panel
  - create_descriptions_panel

### game/ui/screens/strategy_render/hex_outlines.py (Tier 2: TIER_2_PARTIAL, 133 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/ui/screens/strategy_render/test_hex_outlines.py
- Heuristically untested symbols (2):
  - HexOutlineLayer.__init__
  - draw_inner_hex

### game/ui/screens/test_lab/renderer/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 13 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (2):
  - tests/unit/test_lab/test_renderer_public_api.py
  - tests/unit/ui/screens/test_lab/test_renderer_pure_functions.py

### game/ui/screens/test_lab/screen_input_handler.py (Tier 2: TIER_2_PARTIAL, 399 LOC, layer: ui)
- Total symbols: 13 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/screens/test_lab/test_screen_input_handler.py
- Heuristically untested symbols (11):
  - TestLabInputHandler.__init__
  - TestLabInputHandler._handle_dialog_events
  - TestLabInputHandler._handle_panel_events
  - TestLabInputHandler._handle_scroll_and_mouse
  - TestLabInputHandler._update_hover_state
  - TestLabInputHandler._handle_click
  - TestLabInputHandler._check_category_clicks
  - TestLabInputHandler._check_tag_filter_clicks
  - TestLabInputHandler._check_test_item_click
  - TestLabInputHandler._check_action_button_clicks
  - TestLabInputHandler._check_seed_mode_clicks

### game/ui/services/image/factory.py (Tier 3: TIER_3_APPARENTLY_COVERED, 71 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/services/image/test_factory.py

### game/ui/widgets/range_slider_builder.py (Tier 3: TIER_3_APPARENTLY_COVERED, 85 LOC, layer: ui)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/ui/widgets/test_range_slider_builder.py
