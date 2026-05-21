# Coverage Data — Shard 04

**Coverage source:** heuristic
**File count:** 45 | **LOC estimate:** 9610
**Tiers:** 0=10 1=4 2=27 3=4

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/ai/ai_factory.py (Tier 2: TIER_2_PARTIAL, 213 LOC, layer: ai)
- Total symbols: 9 | Heuristically tested: 6
- Candidate test files (15):
  - tests/unit/ai/test_ai_n_team_targeting.py
  - tests/unit/ai/test_fighter_controller.py
  - tests/unit/combat_lab/services/test_ab_battle_runner.py
  - tests/unit/simulation/battle_controller/test_outcome_emission.py
  - tests/unit/simulation/factories/test_ai_factory.py
  - tests/unit/simulation/services/test_battle_service.py
  - tests/unit/simulation/systems/test_battle_engine_boundary.py
  - tests/unit/simulation/systems/test_battle_engine_modifier_stack.py
  - ... and 7 more
- Heuristically untested symbols (3):
  - AIControllerFactory.set_engine
  - AIControllerFactory._ship_has_tactical_launch
  - AIControllerFactory._resolve_vehicle_type

### game/research/systems/research_service.py (Tier 3: TIER_3_APPARENTLY_COVERED, 232 LOC, layer: research)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/research/test_research_service.py
  - tests/unit/research/test_research_service_edge_cases.py

### game/simulation/battle_config.py (Tier 2: TIER_2_PARTIAL, 73 LOC, layer: simulation)
- Total symbols: 2 | Heuristically tested: 1
- Candidate test files (8):
  - tests/unit/simulation/battle_controller/conftest.py
  - tests/unit/simulation/battle_controller/test_execution.py
  - tests/unit/simulation/battle_controller/test_initialization.py
  - tests/unit/simulation/battle_controller/test_outcome_emission.py
  - tests/unit/simulation/battle_controller/test_start_from_spec.py
  - tests/unit/simulation/test_battle_config.py
  - tests/unit/test_lab/test_visual_run.py
  - tests/unit/ui/test_scene_protocol.py
- Heuristically untested symbols (1):
  - _default_end_condition

### game/simulation/combat/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 20 LOC, layer: simulation)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (3):
  - tests/unit/simulation/combat/test_ability_stat_registry.py
  - tests/unit/simulation/combat/test_modifier_stack.py
  - tests/unit/simulation/test_projectile_event_bus_wiring.py

### game/simulation/components/abilities/launch.py (Tier 0: TIER_0_NO_TESTS, 176 LOC, layer: simulation)
- Total symbols: 11 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (11):
  - _LaunchAbilityBase
  - _LaunchAbilityBase._parse_attrs
  - _LaunchAbilityBase.recalculate
  - _LaunchAbilityBase.get_primary_value
  - _LaunchAbilityBase.get_ui_rows
  - StrategicMineLayerAbility
  - StrategicFighterLaunchAbility
  - StrategicSatelliteLaunchAbility
  - TacticalMineLayerAbility
  - TacticalFighterLaunchAbility
  - TacticalSatelliteLaunchAbility

### game/simulation/entities/ship_layer_manager.py (Tier 2: TIER_2_PARTIAL, 167 LOC, layer: simulation)
- Total symbols: 5 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/simulation/entities/test_ship_layer_manager.py
- Heuristically untested symbols (1):
  - ShipLayerManager.__init__

### game/simulation/physics_constants.py (Tier 3: TIER_3_APPARENTLY_COVERED, 72 LOC, layer: simulation)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (7):
  - tests/unit/combat_lab/scenarios/test_prop005_mass_affects_turn.py
  - tests/unit/entities/test_ship.py
  - tests/unit/simulation/entities/stat_contributors/test_command.py
  - tests/unit/simulation/entities/test_ship.py
  - tests/unit/simulation/entities/test_ship_physics.py
  - tests/unit/simulation/test_physics_constants.py
  - tests/unit/simulation/test_physics_formulas.py

### game/strategy/__init__.py (Tier 0: TIER_0_NO_TESTS, 79 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/strategy/data/container.py (Tier 2: TIER_2_PARTIAL, 352 LOC, layer: strategy)
- Total symbols: 22 | Heuristically tested: 19
- Candidate test files (6):
  - tests/unit/simulation/components/abilities/test_container_ability.py
  - tests/unit/strategy/data/test_containable.py
  - tests/unit/strategy/data/test_container.py
  - tests/unit/ui/screens/test_transfer_mass_preview.py
  - tests/unit/ui/screens/test_transfer_mixed_content.py
  - tests/unit/ui/screens/test_transfer_view_model_container.py
- Heuristically untested symbols (3):
  - _get_resource_catalog
  - _resource_mass_per_unit
  - Container.__init__

### game/strategy/data/homeworld_presets.py (Tier 2: TIER_2_PARTIAL, 137 LOC, layer: strategy)
- Total symbols: 7 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/strategy/data/test_homeworld_presets.py
  - tests/unit/strategy/test_race_randomizer.py
- Heuristically untested symbols (3):
  - _get_presets_path
  - get_preset_id_from_name
  - clear_cache

### game/strategy/data/star_generation_config.py (Tier 2: TIER_2_PARTIAL, 200 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/strategy/data/test_star_generation_config.py
- Heuristically untested symbols (3):
  - StarGenerationConfig.__init__
  - StarGenerationConfig._load_from_json
  - StarGenerationConfig._use_defaults

### game/strategy/engine/game_initializer.py (Tier 2: TIER_2_PARTIAL, 446 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 4
- Candidate test files (3):
  - tests/unit/strategy/data/test_galaxy_warp_generator.py
  - tests/unit/strategy/engine/test_game_initializer.py
  - tests/unit/strategy/engine/test_transfer_order.py
- Heuristically untested symbols (6):
  - _PlanetShortageError
  - GameInitializer._wire_fleet_lookups
  - GameInitializer._create_empires
  - GameInitializer._initialize_galaxy
  - GameInitializer._empire_home_indices
  - GameInitializer._setup_initial_scenario

### game/strategy/engine/handlers/construction_queue.py (Tier 2: TIER_2_PARTIAL, 341 LOC, layer: strategy)
- Total symbols: 12 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/strategy/engine/test_set_build_queue_paused_command.py
- Heuristically untested symbols (7):
  - AddToConstructionQueueCommandHandler
  - AddToConstructionQueueCommandHandler._resolve_design_data
  - AddToConstructionQueueCommandHandler._check_design_valid
  - AddToConstructionQueueCommandHandler._load_design_cost
  - RemoveFromConstructionQueueCommandHandler
  - ReorderConstructionQueueCommandHandler
  - register

### game/strategy/engine/handlers/launch_satellites.py (Tier 0: TIER_0_NO_TESTS, 155 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - LaunchSatellitesCommandHandler
  - LaunchSatellitesCommandHandler.execute
  - LaunchSatellitesCommandHandler._execute_fleet
  - LaunchSatellitesCommandHandler._execute_planet
  - register

### game/strategy/engine/handlers/recover_fighters.py (Tier 0: TIER_0_NO_TESTS, 110 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - RecoverFightersCommandHandler
  - RecoverFightersCommandHandler.execute
  - RecoverFightersCommandHandler._execute_fleet
  - RecoverFightersCommandHandler._execute_planet
  - register

### game/strategy/engine/organics_consumption_engine.py (Tier 2: TIER_2_PARTIAL, 126 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/strategy/engine/test_organics_consumption_engine.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
- Heuristically untested symbols (3):
  - OrganicsConsumptionEngine._get_planet_mutator
  - OrganicsConsumptionEngine._validate_tick_inputs
  - OrganicsConsumptionEngine._process_colony

### game/strategy/engine/session/persistence_adapter.py (Tier 3: TIER_3_APPARENTLY_COVERED, 227 LOC, layer: strategy)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/strategy/engine/session/test_persistence_adapter.py
  - tests/unit/strategy/engine/test_restore_path_parity.py

### game/strategy/generation/loaders/galaxy_layouts_loader.py (Tier 2: TIER_2_PARTIAL, 182 LOC, layer: strategy)
- Total symbols: 7 | Heuristically tested: 6
- Candidate test files (1):
  - tests/unit/strategy/generation/density/test_layout_loader.py
- Heuristically untested symbols (1):
  - GalaxyLayoutsLoader._scale_primitive

### game/strategy/interfaces/engines/population.py (Tier 0: TIER_0_NO_TESTS, 134 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (6):
  - IPopulationEngine
  - IPopulationEngine.process_population_growth
  - IOrganicsConsumptionEngine
  - IOrganicsConsumptionEngine.process_consumption
  - IHappinessEngine
  - IHappinessEngine.process_happiness

### game/strategy/services/intercept_calculator.py (Tier 2: TIER_2_PARTIAL, 189 LOC, layer: strategy)
- Total symbols: 12 | Heuristically tested: 5
- Candidate test files (4):
  - tests/unit/strategy/pathfinding/test_edge_cases.py
  - tests/unit/strategy/pathfinding/test_hybrid_and_intercept.py
  - tests/unit/strategy/pathfinding/test_intercept_recursion.py
  - tests/unit/strategy/test_advanced_fleet_orders.py
- Heuristically untested symbols (7):
  - _ChaserProxyCapabilities
  - _ChaserProxyCapabilities.__init__
  - _ChaserProxy
  - _ChaserProxy.__init__
  - _extract_chaser_info
  - InterceptCalculator.__init__
  - InterceptCalculator._evaluate_intercept_candidates

### game/strategy/services/replay_verification_coordinator.py (Tier 2: TIER_2_PARTIAL, 441 LOC, layer: strategy)
- Total symbols: 13 | Heuristically tested: 11
- Candidate test files (4):
  - tests/unit/strategy/services/test_replay_verification_coordinator.py
  - tests/unit/systems/test_main_integration.py
  - tests/unit/test_app_bootstrap_invariants.py
  - tests/unit/test_app_bootstrap_profiling.py
- Heuristically untested symbols (2):
  - ReplayVerificationCoordinator._worker_loop
  - ReplayVerificationCoordinator._write_sidecar

### game/strategy/services/ship_instance_factory.py (Tier 3: TIER_3_APPARENTLY_COVERED, 173 LOC, layer: strategy)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/strategy/services/test_ship_instance_factory.py
  - tests/unit/strategy/test_ship_instance_damage.py

### game/strategy/services/strategic_ability_scanner.py (Tier 2: TIER_2_PARTIAL, 423 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/strategy/services/test_strategic_ability_scanner.py
- Heuristically untested symbols (3):
  - find_harvest_boosters_for_colony
  - _is_component_functionally_active
  - _extract_ability

### game/strategy/services/system_effects_collector.py (Tier 2: TIER_2_PARTIAL, 411 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 9
- Candidate test files (3):
  - tests/unit/strategy/services/test_system_effects_collector.py
  - tests/unit/strategy/services/test_system_effects_collector_aggregate_characterization.py
  - tests/unit/strategy/services/test_system_effects_collector_decomposition.py
- Heuristically untested symbols (1):
  - _build_provider

### game/ui/colors.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 421 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (14):
  - tests/unit/strategy/test_ship_instance_damage.py
  - tests/unit/ui/panels/test_planet_report_panel.py
  - tests/unit/ui/panels/test_planet_report_panel_characterization.py
  - tests/unit/ui/panels/test_ship_detail_panel.py
  - tests/unit/ui/panels/test_ship_stats_renderer.py
  - tests/unit/ui/panels/test_strategy_widgets.py
  - tests/unit/ui/screens/strategy_render/test_dyson_spheres.py
  - tests/unit/ui/screens/strategy_render/test_grid_and_storms.py
  - ... and 6 more

### game/ui/screens/builder/interaction_controller.py (Tier 2: TIER_2_PARTIAL, 132 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/builder/test_builder_interaction.py
- Heuristically untested symbols (2):
  - InteractionController.handle_event
  - InteractionController.update

### game/ui/screens/event_log_window.py (Tier 2: TIER_2_PARTIAL, 735 LOC, layer: ui)
- Total symbols: 23 | Heuristically tested: 18
- Candidate test files (7):
  - tests/unit/ui/screens/test_event_log_no_copy.py
  - tests/unit/ui/screens/test_event_log_replay_button.py
  - tests/unit/ui/screens/test_event_log_row_pool_visibility.py
  - tests/unit/ui/screens/test_event_log_window.py
  - tests/unit/ui/screens/test_event_log_window_reuse.py
  - tests/unit/ui/screens/test_strategy_modal_esc_close.py
  - tests/unit/ui/screens/test_strategy_modal_hidden_input.py
- Heuristically untested symbols (5):
  - EventLogUiBuilder
  - EventLogWindow._init_layout
  - EventLogWindow._create_filter_buttons
  - EventLogWindow._update_filter_buttons
  - EventLogWindow.update_events_only

### game/ui/screens/fleet_data_source.py (Tier 2: TIER_2_PARTIAL, 332 LOC, layer: ui)
- Total symbols: 24 | Heuristically tested: 6
- Candidate test files (1):
  - tests/unit/ui/screens/test_fleet_data_source.py
- Heuristically untested symbols (18):
  - FleetDataSource.__init__
  - FleetDataSource._get_column_handlers
  - FleetDataSource._get_column_value
  - FleetDataSource._format_status
  - FleetDataSource._format_resources
  - FleetDataSource._format_serial
  - FleetDataSource._format_design
  - FleetDataSource._format_name
  - FleetDataSource._format_hp_pct
  - FleetDataSource._format_tonnage
  - FleetDataSource._format_speed
  - FleetDataSource._format_warp
  - FleetDataSource._format_spaceyard
  - FleetDataSource._format_transport
  - FleetDataSource._format_cargo
  - ... and 3 more

### game/ui/screens/per_player_ui_state.py (Tier 2: TIER_2_PARTIAL, 57 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/ui/screens/test_per_player_ui_state.py
  - tests/unit/ui/screens/test_strategy_game_state_manager.py
- Heuristically untested symbols (1):
  - PerPlayerUiState.__init__

### game/ui/screens/planet_abilities_controller.py (Tier 2: TIER_2_PARTIAL, 257 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/ui/screens/test_planet_abilities_controller_scanner.py
- Heuristically untested symbols (4):
  - PlanetAbilitiesController.__init__
  - PlanetAbilitiesController.get_component_status
  - PlanetAbilitiesController.is_component_active
  - PlanetAbilitiesController.toggle_ability

### game/ui/screens/planet_data_source.py (Tier 2: TIER_2_PARTIAL, 100 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/screens/test_planet_data_source.py
- Heuristically untested symbols (5):
  - PlanetDataSource.__init__
  - PlanetDataSource._planets
  - PlanetDataSource._render_icon
  - PlanetDataSource._get_planet_icon
  - PlanetDataSource._get_blank_icon

### game/ui/screens/planet_list_event_router.py (Tier 2: TIER_2_PARTIAL, 301 LOC, layer: ui)
- Total symbols: 10 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/ui/screens/test_planet_list_components.py
  - tests/unit/ui/screens/test_planet_list_window.py
- Heuristically untested symbols (5):
  - PlanetListEventRouter.process_event
  - PlanetListEventRouter._set_all_filters
  - PlanetListEventRouter._set_all_effects
  - PlanetListEventRouter._toggle_filter
  - PlanetListEventRouter._navigate_to_selected

### game/ui/screens/race_setup/renderer.py (Tier 2: TIER_2_PARTIAL, 234 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 6
- Candidate test files (2):
  - tests/unit/ui/screens/test_race_setup_delegate_factory.py
  - tests/unit/ui/screens/test_race_setup_screen.py
- Heuristically untested symbols (3):
  - RaceSetupRenderer.close_save_update_dialog
  - RaceSetupRenderer.close_llm_dialog
  - RaceSetupRenderer.close_llm_error_popup

### game/ui/screens/race_validator.py (Tier 2: TIER_2_PARTIAL, 96 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/screens/test_race_validator.py
- Heuristically untested symbols (1):
  - RaceValidator.__init__

### game/ui/screens/star_data_source.py (Tier 0: TIER_0_NO_TESTS, 71 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (7):
  - StarDataSource
  - StarDataSource.__init__
  - StarDataSource.get_star_at_index
  - StarDataSource._stars
  - StarDataSource._render_icon
  - StarDataSource._get_star_icon
  - StarDataSource._make_circle_icon

### game/ui/screens/strategy_colonization.py (Tier 2: TIER_2_PARTIAL, 273 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 7
- Candidate test files (2):
  - tests/unit/ui/screens/test_strategy_colonization.py
  - tests/unit/ui/screens/test_strategy_screen_composition.py
- Heuristically untested symbols (5):
  - ColonizationSystem.__init__
  - ColonizationSystem.issue_colonize_order
  - ColonizationSystem.queue_colonize_mission
  - ColonizationSystem.request_colonize_order
  - ColonizationSystem._resolve_planet_global_hex

### game/ui/screens/strategy_render/__init__.py (Tier 0: TIER_0_NO_TESTS, 9 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/ui/screens/strategy_render/grid.py (Tier 2: TIER_2_PARTIAL, 175 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/ui/screens/strategy_render/test_grid_and_storms.py
  - tests/unit/ui/screens/strategy_render/test_grid_cache.py
- Heuristically untested symbols (2):
  - GridLayer.__init__
  - GridLayer._ensure_surface

### game/ui/screens/strategy_ui.py (Tier 2: TIER_2_PARTIAL, 567 LOC, layer: ui)
- Total symbols: 56 | Heuristically tested: 12
- Candidate test files (4):
  - tests/unit/ui/screens/test_event_log_window.py
  - tests/unit/ui/screens/test_open_warp_user_error_surfacing.py
  - tests/unit/ui/screens/test_strategy_ui_menu.py
  - tests/unit/ui/screens/test_strategy_ui_tooltips.py
- Heuristically untested symbols (44):
  - _get_planetary_ids
  - StrategyUI.__getattr__
  - StrategyUI._apply_hotkey_tooltips
  - StrategyUI.open_fleet_context_menu
  - StrategyUI.close_fleet_context_menu
  - StrategyUI.open_planet_context_menu
  - StrategyUI.close_planet_context_menu
  - StrategyUI._build_planet_menu_callbacks
  - StrategyUI._build_fleet_menu_callbacks
  - StrategyUI._on_fleet_context_menu_action
  - StrategyUI.hide_ui
  - StrategyUI.show_ui
  - StrategyUI.handle_resize
  - StrategyUI.show_system_info
  - StrategyUI.show_sector_info
  - ... and 29 more

### game/ui/screens/test_lab/details/resource_outcomes.py (Tier 0: TIER_0_NO_TESTS, 294 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - is_resource_test
  - draw_resource_outcomes
  - _draw_fuel_outcomes
  - _draw_energy_outcomes
  - _draw_ammo_outcomes

### game/ui/screens/transfer_mass_preview.py (Tier 0: TIER_0_NO_TESTS, 209 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (6):
  - MassPreview
  - compute_mass_preview
  - _resolve_pending_qty
  - _mass_per_unit_for_cargo_key
  - _qty_for_cargo_key
  - _get_catalog

### game/ui/services/image/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 62 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (7):
  - tests/unit/core/test_application_context.py
  - tests/unit/tools/test_regenerate_ship_portraits.py
  - tests/unit/ui/services/image/test_defaults.py
  - tests/unit/ui/services/image/test_factory.py
  - tests/unit/ui/services/image/test_null_provider.py
  - tests/unit/ui/services/image/test_openai_provider.py
  - tests/unit/ui/services/image/test_provider.py

### game/ui/services/image/null_provider.py (Tier 0: TIER_0_NO_TESTS, 62 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - NullImageProvider
  - NullImageProvider.__init__
  - NullImageProvider.__repr__
  - NullImageProvider.__str__
  - NullImageProvider.generate_image

### game/ui/services/modifier_icon_service.py (Tier 2: TIER_2_PARTIAL, 87 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/ui/services/test_modifier_icon_service.py
  - tests/unit/ui/test_modifier_icons.py
- Heuristically untested symbols (1):
  - ModifierIconService.__init__

### game/ui/utils/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 57 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/ui/test_utils.py
