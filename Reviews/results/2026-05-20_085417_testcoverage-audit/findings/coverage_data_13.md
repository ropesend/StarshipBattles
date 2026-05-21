# Coverage Data — Shard 13

**Coverage source:** heuristic
**File count:** 45 | **LOC estimate:** 9466
**Tiers:** 0=6 1=4 2=31 3=4

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/ai/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 109 LOC, layer: ai)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/strategy/test_ui_dto_ai_readers_no_legacy_substrate.py

### game/ai/carrier_controller.py (Tier 2: TIER_2_PARTIAL, 407 LOC, layer: ai)
- Total symbols: 14 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ai/test_carrier_controller.py
- Heuristically untested symbols (11):
  - CarrierAIController._maybe_launch_fighter_wave
  - CarrierAIController._maybe_launch_satellite_wave
  - CarrierAIController._maybe_launch_wave
  - CarrierAIController._sum_launch_rate
  - CarrierAIController._enemy_in_launch_radius
  - CarrierAIController._pop_fighter_cvs
  - CarrierAIController._pop_cvs
  - CarrierAIController._pop_cvs_within_budget
  - CarrierAIController._find_tactical_launch_ability
  - CarrierAIController._unwrap_ship
  - CarrierAIController._ship_is_alive

### game/assets/asset_manager.py (Tier 2: TIER_2_PARTIAL, 374 LOC, layer: assets)
- Total symbols: 19 | Heuristically tested: 16
- Candidate test files (2):
  - tests/unit/assets/test_asset_manager_resolutions.py
  - tests/unit/core/test_asset_manager.py
- Heuristically untested symbols (3):
  - AssetManager.__init__
  - AssetManager._load_star_metadata
  - AssetManager.clear

### game/core/protocols/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 162 LOC, layer: core)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (24):
  - tests/unit/core/test_protocols.py
  - tests/unit/core/test_protocols_boundary.py
  - tests/unit/core/test_protocols_common.py
  - tests/unit/core/test_protocols_public_api.py
  - tests/unit/core/test_registry_provider.py
  - tests/unit/core/test_serializable_protocol.py
  - tests/unit/research/test_research_scene_di.py
  - tests/unit/strategy/facade/test_strategy_session_facade.py
  - ... and 16 more

### game/core/protocols/registry.py (Tier 0: TIER_0_NO_TESTS, 39 LOC, layer: core)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - IRegistryProvider
  - IRegistryProvider.get_components
  - IRegistryProvider.get_modifiers
  - IRegistryProvider.get_vehicle_classes
  - IRegistryProvider.get_resources

### game/core/protocols/ui.py (Tier 0: TIER_0_NO_TESTS, 112 LOC, layer: core)
- Total symbols: 15 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (15):
  - IScene
  - IScene.handle_event
  - IScene.update
  - IScene.draw
  - IScene.handle_resize
  - ICamera
  - ICamera.width
  - ICamera.height
  - ICamera.zoom
  - ICamera.position
  - ICamera.world_to_screen
  - ICamera.screen_to_world
  - ICamera.update
  - ICamera.update_input
  - is_camera

### game/engine/collision.py (Tier 2: TIER_2_PARTIAL, 201 LOC, layer: engine)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (4):
  - tests/unit/engine/collision_edge_cases/conftest.py
  - tests/unit/simulation/combat/test_beam_hit_tracking.py
  - tests/unit/simulation/combat/test_weapon_dispatch_golden.py
  - tests/unit/simulation/systems/test_battle_rng_isolation.py
- Heuristically untested symbols (1):
  - CollisionSystem.process_ramming

### game/simulation/components/abilities/harvester.py (Tier 2: TIER_2_PARTIAL, 181 LOC, layer: simulation)
- Total symbols: 21 | Heuristically tested: 15
- Candidate test files (2):
  - tests/unit/simulation/abilities/test_empire_storage.py
  - tests/unit/simulation/components/abilities/test_colonize_harvester.py
- Heuristically untested symbols (6):
  - ResourceHarvesterAbility._parse_attrs
  - LocalStorageAbility._parse_attrs
  - StagingYardAbility
  - StagingYardAbility._parse_attrs
  - PlanetaryYardAbility
  - SpaceShipyardAbility._parse_attrs

### game/simulation/components/ability_manager.py (Tier 2: TIER_2_PARTIAL, 285 LOC, layer: simulation)
- Total symbols: 13 | Heuristically tested: 9
- Candidate test files (1):
  - tests/unit/simulation/components/test_ability_manager.py
- Heuristically untested symbols (4):
  - AbilityManager.__init__
  - AbilityManager._build_index
  - AbilityManager._instantiate
  - AbilityManager._get_abilities_polymorphic

### game/simulation/components/component.py (Tier 2: TIER_2_PARTIAL, 406 LOC, layer: simulation)
- Total symbols: 35 | Heuristically tested: 31
- Candidate test files (81):
  - tests/unit/ai/test_ai.py
  - tests/unit/ai/test_ai_protocols.py
  - tests/unit/ai/test_movement_and_ai.py
  - tests/unit/builder/test_builder_logic.py
  - tests/unit/builder/test_builder_structure_features.py
  - tests/unit/builder/test_builder_validation.py
  - tests/unit/builder/test_bulk_add.py
  - tests/unit/builder/test_multi_selection_logic.py
  - ... and 73 more
- Heuristically untested symbols (1):
  - Component.mark_hp_cache_dirty

### game/simulation/components/component_resource_manager.py (Tier 2: TIER_2_PARTIAL, 112 LOC, layer: simulation)
- Total symbols: 6 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/simulation/components/test_component_resource_manager.py
- Heuristically untested symbols (1):
  - ComponentResourceManager.__init__

### game/simulation/components/component_stats_calculator.py (Tier 2: TIER_2_PARTIAL, 360 LOC, layer: simulation)
- Total symbols: 9 | Heuristically tested: 7
- Candidate test files (2):
  - tests/unit/regressions/test_bug_regressions_2026_01.py
  - tests/unit/simulation/components/test_component_stats_calculator.py
- Heuristically untested symbols (2):
  - build_formula_context
  - ComponentStatsCalculator._evaluate_formulas_in_abilities

### game/simulation/entities/ship_validator_helper.py (Tier 2: TIER_2_PARTIAL, 70 LOC, layer: simulation)
- Total symbols: 5 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/simulation/entities/test_ship_validator_helper.py
- Heuristically untested symbols (1):
  - ShipValidatorHelper.__init__

### game/simulation/entities/stat_contributors/defense.py (Tier 0: TIER_0_NO_TESTS, 112 LOC, layer: simulation)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - contribute_armor
  - contribute_shield_projection
  - contribute_shield_regeneration
  - apply_armor_and_repair_scores
  - init_armor_pool

### game/simulation/services/design_loader.py (Tier 2: TIER_2_PARTIAL, 130 LOC, layer: simulation)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/simulation/services/test_simulation_design_loader.py
  - tests/unit/ui/services/test_design_loader_adapter.py
- Heuristically untested symbols (1):
  - SimulationDesignLoader.__init__

### game/strategy/combat/team_spec_builder.py (Tier 2: TIER_2_PARTIAL, 198 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/strategy/combat/test_team_spec_builder.py
- Heuristically untested symbols (2):
  - TeamSpecBuilder.group_fleets_by_owner
  - TeamSpecBuilder.compute_owner_to_team_id

### game/strategy/data/carried_vehicle.py (Tier 2: TIER_2_PARTIAL, 115 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (28):
  - tests/unit/ai/test_carrier_controller.py
  - tests/unit/simulation/components/abilities/test_tactical_fighter_launch.py
  - tests/unit/simulation/components/abilities/test_tactical_satellite_launch.py
  - tests/unit/simulation/systems/test_battle_engine_tick.py
  - tests/unit/simulation/systems/test_fighter_launch_init.py
  - tests/unit/simulation/systems/test_fighter_reboard_component_state.py
  - tests/unit/simulation/systems/test_tactical_mine_resolver.py
  - tests/unit/strategy/data/test_bay_inventory.py
  - ... and 20 more
- Heuristically untested symbols (1):
  - CarriedVehicle.__post_init__

### game/strategy/data/galaxy_state.py (Tier 3: TIER_3_APPARENTLY_COVERED, 69 LOC, layer: strategy)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (3):
  - tests/unit/strategy/data/test_galaxy_entity_registry.py
  - tests/unit/strategy/data/test_galaxy_spatial_index.py
  - tests/unit/strategy/data/test_galaxy_state.py

### game/strategy/data/star_system.py (Tier 2: TIER_2_PARTIAL, 153 LOC, layer: strategy)
- Total symbols: 11 | Heuristically tested: 10
- Candidate test files (23):
  - tests/unit/core/test_protocols.py
  - tests/unit/fixtures/test_strategy_entities.py
  - tests/unit/strategy/data/test_galaxy.py
  - tests/unit/strategy/data/test_galaxy_add_warp_point.py
  - tests/unit/strategy/data/test_galaxy_cleanup.py
  - tests/unit/strategy/data/test_galaxy_warp_generator.py
  - tests/unit/strategy/data/test_storm.py
  - tests/unit/strategy/engine/test_superweapon_event_payloads.py
  - ... and 15 more
- Heuristically untested symbols (1):
  - StarSystem.__repr__

### game/strategy/data/stars.py (Tier 2: TIER_2_PARTIAL, 165 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 5
- Candidate test files (16):
  - tests/unit/core/test_protocols.py
  - tests/unit/fixtures/test_strategy_entities.py
  - tests/unit/strategy/data/test_galaxy.py
  - tests/unit/strategy/data/test_stars.py
  - tests/unit/strategy/data/test_storm.py
  - tests/unit/strategy/engine/test_superweapon_event_payloads.py
  - tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py
  - tests/unit/strategy/engine/test_superweapon_order_processor.py
  - ... and 8 more
- Heuristically untested symbols (1):
  - __getattr__

### game/strategy/engine/conflict_modifier_collection.py (Tier 0: TIER_0_NO_TESTS, 92 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - lookup_environmental_effects
  - collect_team_modifiers

### game/strategy/engine/game_config.py (Tier 2: TIER_2_PARTIAL, 261 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 8
- Candidate test files (30):
  - tests/unit/fixtures/test_strategy_entities.py
  - tests/unit/quickstart/test_quickstart_builder.py
  - tests/unit/strategy/data/test_galaxy_warp_generator.py
  - tests/unit/strategy/engine/session/test_bootstrap.py
  - tests/unit/strategy/engine/session/test_persistence_adapter.py
  - tests/unit/strategy/engine/session/test_runtime_services.py
  - tests/unit/strategy/engine/test_game_config.py
  - tests/unit/strategy/engine/test_game_initializer.py
  - ... and 22 more
- Heuristically untested symbols (2):
  - _get_default_asset_path
  - _get_default_players

### game/strategy/engine/order_handlers/launch_fighters.py (Tier 2: TIER_2_PARTIAL, 294 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/strategy/engine/order_handlers/test_launch_fighters_handler.py
  - tests/unit/strategy/engine/test_issuer_execution_contract.py
- Heuristically untested symbols (5):
  - LaunchFightersOrderHandler._run_with_issuer
  - LaunchFightersOrderHandler._find_ship
  - LaunchFightersOrderHandler._create_fighter_group
  - LaunchFightersOrderHandler._mint_group_id
  - LaunchFightersOrderHandler._carried_vehicle_to_ship_instance

### game/strategy/engine/planet_command_handlers.py (Tier 2: TIER_2_PARTIAL, 346 LOC, layer: strategy)
- Total symbols: 19 | Heuristically tested: 17
- Candidate test files (2):
  - tests/unit/strategy/engine/test_planet_command_handlers.py
  - tests/unit/strategy/engine/test_typed_planet_intents.py
- Heuristically untested symbols (2):
  - _apply_planet_environmental_target
  - register

### game/strategy/engine/resupply_engine.py (Tier 2: TIER_2_PARTIAL, 294 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 7
- Candidate test files (3):
  - tests/unit/strategy/engine/test_engine_validation.py
  - tests/unit/strategy/engine/test_resupply_engine.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
- Heuristically untested symbols (3):
  - ResupplyEngine.__init__
  - ResupplyEngine._process_facility_generation
  - ResupplyEngine._get_fuel_generation_rate

### game/strategy/engine/superweapon_handlers/__init__.py (Tier 0: TIER_0_NO_TESTS, 24 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/strategy/engine/turn_engine.py (Tier 2: TIER_2_PARTIAL, 830 LOC, layer: strategy)
- Total symbols: 31 | Heuristically tested: 28
- Candidate test files (17):
  - tests/unit/strategy/engine/session/test_bootstrap.py
  - tests/unit/strategy/engine/test_population_engine.py
  - tests/unit/strategy/engine/test_turn_engine_progress_callback.py
  - tests/unit/strategy/test_advanced_fleet_orders.py
  - tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py
  - tests/unit/strategy/turn_engine/test_default_tick_phase_list.py
  - tests/unit/strategy/turn_engine/test_dependency_injection.py
  - tests/unit/strategy/turn_engine/test_no_lazy_fallback_init.py
  - ... and 9 more
- Heuristically untested symbols (3):
  - TurnEngine._tick_phase_log_turn_start
  - TurnEngine._tick_phase_log_after_construction
  - TurnEngine._tick_phase_accumulate_env_events

### game/strategy/engine/turn_engine_settings.py (Tier 3: TIER_3_APPARENTLY_COVERED, 77 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/strategy/engine/test_turn_engine_settings.py

### game/strategy/facade/dto/fleet_hierarchy_dto.py (Tier 3: TIER_3_APPARENTLY_COVERED, 104 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 6
- Candidate test files (1):
  - tests/unit/strategy/facade/test_fleet_hierarchy_dto.py

### game/strategy/interfaces/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 58 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/strategy/interfaces/test_engines_package_layout.py

### game/strategy/interfaces/engines/combat.py (Tier 0: TIER_0_NO_TESTS, 112 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - IConflictEngine
  - IConflictEngine.resolve_all_conflicts
  - IEnvironmentalHazardEngine
  - IEnvironmentalHazardEngine.process_environmental_tick

### game/strategy/services/ability_metadata.py (Tier 2: TIER_2_PARTIAL, 566 LOC, layer: strategy)
- Total symbols: 15 | Heuristically tested: 12
- Candidate test files (5):
  - tests/unit/strategy/engine/test_command_registry_contract.py
  - tests/unit/strategy/services/test_ability_metadata_contracts.py
  - tests/unit/strategy/services/test_ability_metadata_effects.py
  - tests/unit/strategy/services/test_ability_metadata_registry.py
  - tests/unit/strategy/services/test_combat_modifier_collector.py
- Heuristically untested symbols (3):
  - _multiplier_effect
  - _rate_effect
  - _energy_drain

### game/strategy/services/fleet_write_service.py (Tier 2: TIER_2_PARTIAL, 136 LOC, layer: strategy)
- Total symbols: 18 | Heuristically tested: 15
- Candidate test files (6):
  - tests/unit/strategy/engine/handlers/test_movement_handlers.py
  - tests/unit/strategy/engine/handlers/test_order_queue_handlers.py
  - tests/unit/strategy/engine/session/test_bootstrap.py
  - tests/unit/strategy/engine/test_game_session_from_dict.py
  - tests/unit/strategy/engine/test_set_build_queue_paused_command.py
  - tests/unit/strategy/services/test_fleet_write_service.py
- Heuristically untested symbols (3):
  - FleetWriteService.swap_orders
  - FleetWriteService.add_task_force
  - FleetWriteService.remove_task_force

### game/ui/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 27 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/conftest.py

### game/ui/effects/hit_effects.py (Tier 2: TIER_2_PARTIAL, 233 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 11
- Candidate test files (1):
  - tests/unit/ui/effects/test_hit_effects.py
- Heuristically untested symbols (1):
  - HitEffect.update

### game/ui/screens/builder/grouping_strategies.py (Tier 2: TIER_2_PARTIAL, 79 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 8
- Candidate test files (3):
  - tests/unit/ui/screens/builder/test_grouping_strategies.py
  - tests/unit/ui/screens/test_workshop_viewmodel_layer_ops.py
  - tests/unit/workshop/test_move_component.py
- Heuristically untested symbols (1):
  - GroupingStrategy

### game/ui/screens/builder/stat_definitions.py (Tier 2: TIER_2_PARTIAL, 77 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 6
- Candidate test files (2):
  - tests/unit/ui/screens/builder/test_stat_definitions.py
  - tests/unit/workshop/test_stats_visibility.py
- Heuristically untested symbols (1):
  - StatDefinition.__init__

### game/ui/screens/race_setup/input_handler.py (Tier 2: TIER_2_PARTIAL, 174 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/screens/test_race_setup_delegate_factory.py
- Heuristically untested symbols (1):
  - RaceSetupInputHandler.handle

### game/ui/screens/strategy_render/dyson_spheres.py (Tier 3: TIER_3_APPARENTLY_COVERED, 129 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/screens/strategy_render/test_dyson_spheres.py

### game/ui/screens/strategy_windows/list_windows.py (Tier 2: TIER_2_PARTIAL, 132 LOC, layer: ui)
- Total symbols: 11 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/ui/screens/strategy_windows/test_planet_list_registrar_reuse.py
- Heuristically untested symbols (6):
  - navigate_camera_to
  - PlanetListRegistrar.__init__
  - PlanetListRegistrar._on_navigate
  - StarListRegistrar
  - StarListRegistrar.__init__
  - StarListRegistrar._on_navigate

### game/ui/screens/strategy_windows/orders_window_ctrl.py (Tier 2: TIER_2_PARTIAL, 111 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/screens/strategy_windows/test_orders_window_ctrl.py
- Heuristically untested symbols (1):
  - OrdersRegistrar.__init__

### game/ui/screens/test_lab/screen_actions.py (Tier 2: TIER_2_PARTIAL, 390 LOC, layer: ui)
- Total symbols: 19 | Heuristically tested: 8
- Candidate test files (3):
  - tests/unit/test_lab/test_data_paths.py
  - tests/unit/test_lab/test_render_progress_no_game_handle.py
  - tests/unit/test_lab/test_visual_run.py
- Heuristically untested symbols (11):
  - TestLabScreenActions._require_display_surface
  - TestLabScreenActions._get_engine
  - TestLabScreenActions._ensure_engine
  - TestLabScreenActions._on_view_battle_states
  - TestLabScreenActions._on_use_seed_from_run
  - TestLabScreenActions._on_copy_results
  - TestLabScreenActions._on_run_visual_baseline
  - TestLabScreenActions._on_run_headless
  - TestLabScreenActions._on_run_all_tests
  - TestLabScreenActions._continue_batch_test
  - TestLabScreenActions._prompt_for_custom_seed

### game/ui/screens/workshop_event_router.py (Tier 2: TIER_2_PARTIAL, 592 LOC, layer: ui)
- Total symbols: 25 | Heuristically tested: 5
- Candidate test files (3):
  - tests/unit/builder/test_layer_targeted_actions.py
  - tests/unit/ui/screens/test_workshop_event_router_add_component.py
  - tests/unit/ui/screens/test_workshop_event_router_select_component.py
- Heuristically untested symbols (20):
  - WorkshopEventRouter.__init__
  - WorkshopEventRouter._get_vehicle_classes
  - WorkshopEventRouter.handle_event
  - WorkshopEventRouter._handle_panel_action
  - WorkshopEventRouter._handle_quick_add
  - WorkshopEventRouter._handle_move_individual
  - WorkshopEventRouter._handle_move_group
  - WorkshopEventRouter._handle_select_group
  - WorkshopEventRouter._handle_select_individual
  - WorkshopEventRouter._handle_button_pressed
  - WorkshopEventRouter._handle_dropdown_changed
  - WorkshopEventRouter._apply_confirmation_dropdown
  - WorkshopEventRouter._apply_resolver_dropdown
  - WorkshopEventRouter._handle_class_dropdown
  - WorkshopEventRouter._handle_vehicle_type_dropdown
  - ... and 5 more

### game/ui/screens/workshop_ship_io.py (Tier 2: TIER_2_PARTIAL, 280 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/builder/test_builder_io_integration.py
  - tests/unit/workshop/test_workshop_ship_io_facade_state.py
- Heuristically untested symbols (3):
  - WorkshopShipIO.__init__
  - WorkshopShipIO._design_catalog
  - WorkshopShipIO._prompt_design_name

### game/ui/services/image/background.py (Tier 2: TIER_2_PARTIAL, 288 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 9
- Candidate test files (1):
  - tests/unit/ui/services/image/test_background.py
- Heuristically untested symbols (3):
  - ImageBackgroundCall.elapsed_seconds
  - ImageBackgroundCall._run
  - shutdown_all_image_calls
