# Coverage Data — Shard 14

**Coverage source:** heuristic
**File count:** 45 | **LOC estimate:** 9469
**Tiers:** 0=13 1=7 2=19 3=6

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/__init__.py (Tier 0: TIER_0_NO_TESTS, 0 LOC, layer: game_root)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/ai/group_target_coordinator.py (Tier 2: TIER_2_PARTIAL, 144 LOC, layer: ai)
- Total symbols: 8 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/ai/test_group_target_coordinator.py
- Heuristically untested symbols (3):
  - GroupTargetCoordinator._max_hp_capacity
  - GroupTargetCoordinator._bounded_hp
  - GroupTargetCoordinator._hp_ratio

### game/core/hex_math.py (Tier 2: TIER_2_PARTIAL, 394 LOC, layer: core)
- Total symbols: 22 | Heuristically tested: 21
- Candidate test files (245):
  - tests/unit/core/test_hex_math_core.py
  - tests/unit/core/test_hex_math_strategy.py
  - tests/unit/core/test_protocols.py
  - tests/unit/fixtures/test_strategy_entities.py
  - tests/unit/simulation/systems/test_fighter_reboard.py
  - tests/unit/simulation/systems/test_fighter_reboard_component_state.py
  - tests/unit/simulation/systems/test_fighter_reboard_overflow_component_state.py
  - tests/unit/simulation/systems/test_satellite_reboard.py
  - ... and 237 more
- Heuristically untested symbols (1):
  - _hex_round

### game/core/protocols/strategy_entities.py (Tier 0: TIER_0_NO_TESTS, 457 LOC, layer: core)
- Total symbols: 87 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (87):
  - IStarSystem
  - IStarSystem.stars
  - IStarSystem.planets
  - IStarSystem.warp_points
  - IStarSystem.global_location
  - IStarSystem.name
  - IStarSystem.storms
  - IStar
  - IStar.color
  - IStar.mass
  - IStar.temperature
  - IStar.luminosity
  - IStar.star_type
  - IStar.name
  - IPlanet
  - ... and 72 more

### game/core/protocols/strategy_mutators.py (Tier 0: TIER_0_NO_TESTS, 219 LOC, layer: core)
- Total symbols: 65 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (65):
  - IFleetMutator
  - IFleetMutator.set_location
  - IFleetMutator.set_path
  - IFleetMutator.append_order
  - IFleetMutator.insert_order
  - IFleetMutator.pop_order
  - IFleetMutator.clear_orders
  - IFleetMutator.swap_orders
  - IFleetMutator.add_ship
  - IFleetMutator.remove_ship
  - IFleetMutator.set_display_name
  - IFleetMutator.set_fleet_policy
  - IFleetMutator.append_construction_item
  - IFleetMutator.pop_construction_item
  - IFleetMutator.set_construction_queue_paused
  - ... and 50 more

### game/simulation/combat/families/beam.py (Tier 0: TIER_0_NO_TESTS, 32 LOC, layer: simulation)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - BeamHandler
  - BeamHandler.fire

### game/simulation/combat/fleet_aura_manager.py (Tier 2: TIER_2_PARTIAL, 515 LOC, layer: simulation)
- Total symbols: 19 | Heuristically tested: 15
- Candidate test files (9):
  - tests/unit/simulation/combat/test_fleet_aura_cache.py
  - tests/unit/simulation/combat/test_fleet_aura_extended.py
  - tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py
  - tests/unit/simulation/combat/test_fleet_aura_provider_identity.py
  - tests/unit/simulation/combat/test_fleet_aura_register.py
  - tests/unit/simulation/combat/test_fleet_aura_unknown_stat_key_warning.py
  - tests/unit/simulation/combat/test_fleet_aura_unregister.py
  - tests/unit/simulation/components/abilities/test_fleet_components.py
  - ... and 1 more
- Heuristically untested symbols (4):
  - ExternalModifier
  - FleetAuraManager.__init__
  - FleetAuraManager._append_external_from_entry
  - FleetAuraManager._log_unknown_stat_key_once

### game/simulation/components/abilities/planetary/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 59 LOC, layer: simulation)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (6):
  - tests/unit/simulation/components/abilities/test_combat_modifiers.py
  - tests/unit/simulation/components/abilities/test_planet_modifiers.py
  - tests/unit/simulation/components/abilities/test_planetary_abilities.py
  - tests/unit/simulation/components/abilities/test_strategic_abilities.py
  - tests/unit/simulation/components/abilities/test_system_stabilizers.py
  - tests/unit/simulation/components/abilities/test_terraforming_abilities.py

### game/simulation/components/abilities/ui_colors.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 84 LOC, layer: simulation)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (9):
  - tests/unit/entities/test_abilities.py
  - tests/unit/simulation/abilities/test_cargo_storage.py
  - tests/unit/simulation/components/abilities/test_colonize_harvester.py
  - tests/unit/simulation/components/abilities/test_crew_abilities.py
  - tests/unit/simulation/components/abilities/test_defense_isolation.py
  - tests/unit/simulation/components/abilities/test_resource_consumption.py
  - tests/unit/simulation/components/abilities/test_static_value_ability.py
  - tests/unit/simulation/components/abilities/test_superweapons.py
  - ... and 1 more

### game/simulation/components/abilities/warhead.py (Tier 0: TIER_0_NO_TESTS, 123 LOC, layer: simulation)
- Total symbols: 8 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (8):
  - WarheadAbility
  - WarheadAbility._parse_attrs
  - WarheadAbility.recalculate
  - WarheadAbility.get_primary_value
  - WarheadAbility.get_ui_rows
  - LaserheadAbility
  - LaserheadAbility.__init__
  - LaserheadAbility.sync_data

### game/simulation/entities/ship_combat_engine.py (Tier 2: TIER_2_PARTIAL, 252 LOC, layer: simulation)
- Total symbols: 9 | Heuristically tested: 8
- Candidate test files (6):
  - tests/unit/combat/test_combat.py
  - tests/unit/simulation/armor_mechanics/test_damage_mechanics.py
  - tests/unit/simulation/armor_mechanics/test_damage_reduction.py
  - tests/unit/simulation/entities/test_ship_combat_manager.py
  - tests/unit/simulation/ship_combat_engine/test_combat_ops.py
  - tests/unit/simulation/ship_combat_engine/test_cooldowns.py
- Heuristically untested symbols (1):
  - ShipCombatEngine.__init__

### game/simulation/entities/ship_stats.py (Tier 2: TIER_2_PARTIAL, 559 LOC, layer: simulation)
- Total symbols: 16 | Heuristically tested: 6
- Candidate test files (4):
  - tests/unit/builder/test_requirement_abilities.py
  - tests/unit/simulation/entities/test_ship_resource_manager.py
  - tests/unit/simulation/entities/test_ship_stats.py
  - tests/unit/simulation/systems/test_ship_stats_calculator_phases.py
- Heuristically untested symbols (10):
  - _get_planetary_resource_ids
  - ShipStatsCalculator.__init__
  - ShipStatsCalculator._reset_base_state
  - ShipStatsCalculator._phase_damage_check_and_supply
  - ShipStatsCalculator._aggregate_resource_abilities
  - ShipStatsCalculator._aggregate_cargo_and_pod_abilities
  - ShipStatsCalculator._apply_aggregated_stats
  - ShipStatsCalculator._phase_physics_and_limits
  - ShipStatsCalculator._check_mass_limits
  - ShipStatsCalculator._phase_sensor_defense_scores

### game/simulation/interfaces/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 128 LOC, layer: simulation)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (2):
  - tests/unit/simulation/entities/test_combat_endurance.py
  - tests/unit/simulation/interfaces/test_ai_controller_interface.py

### game/simulation/interfaces/ai_controller.py (Tier 2: TIER_2_PARTIAL, 140 LOC, layer: simulation)
- Total symbols: 7 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/simulation/interfaces/test_ai_controller_interface.py
- Heuristically untested symbols (4):
  - IAIControllerFactory
  - IAIControllerFactory.set_grid
  - IAIControllerFactory.create_for_ship
  - IAIControllerFactory.create_for_ships

### game/strategy/config/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 0 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (2):
  - tests/unit/strategy/config/test_economy_config.py
  - tests/unit/strategy/engine/test_organics_consumption_engine.py

### game/strategy/data/environmental_preference.py (Tier 3: TIER_3_APPARENTLY_COVERED, 89 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 5
- Candidate test files (15):
  - tests/unit/strategy/data/test_environmental_preference.py
  - tests/unit/strategy/data/test_habitability_factors.py
  - tests/unit/strategy/data/test_population_model.py
  - tests/unit/strategy/data/test_race_config.py
  - tests/unit/strategy/data/test_race_point_budget_v2.py
  - tests/unit/strategy/engine/test_game_initializer.py
  - tests/unit/strategy/engine/test_superweapon_order_processor.py
  - tests/unit/strategy/formulas/test_habitability.py
  - ... and 7 more

### game/strategy/data/fleet_battle_adapter.py (Tier 2: TIER_2_PARTIAL, 193 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/strategy/test_fleet_battle_adapter.py
- Heuristically untested symbols (3):
  - FleetBattleAdapter.__init__
  - FleetBattleAdapter._resolve_ship_policies
  - FleetBattleAdapter._apply_policy_override

### game/strategy/engine/handlers/base.py (Tier 2: TIER_2_PARTIAL, 465 LOC, layer: strategy)
- Total symbols: 19 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/strategy/data/test_fleet_group_kind.py
  - tests/unit/strategy/engine/test_command_registry_thirdparty.py
- Heuristically untested symbols (15):
  - add_move_order_if_needed
  - ICommandHandler
  - BaseCommandHandler._resolve_fleet
  - BaseCommandHandler._resolve_player_fleet
  - BaseCommandHandler._resolve_fleet_required
  - BaseCommandHandler._resolve_player_planet
  - BaseCommandHandler._resolve_planet
  - BaseCommandHandler._resolve_planet_optional
  - BaseCommandHandler._emit_validated_order
  - BaseCommandHandler._resolve_build_entity
  - BaseCommandHandler._resolve_queue
  - BaseCommandHandler._resolve_queue_owner
  - BaseCommandHandler._build_colonize_target
  - CommandHandlerRegistry
  - CommandHandlerRegistry.__init__

### game/strategy/engine/handlers/registry_factory.py (Tier 3: TIER_3_APPARENTLY_COVERED, 44 LOC, layer: strategy)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (3):
  - tests/unit/strategy/engine/test_command_registry_contract.py
  - tests/unit/strategy/engine/test_command_registry_thirdparty.py
  - tests/unit/strategy/engine/test_command_specs_contract.py

### game/strategy/engine/minefield_resolver.py (Tier 2: TIER_2_PARTIAL, 706 LOC, layer: strategy)
- Total symbols: 24 | Heuristically tested: 7
- Candidate test files (2):
  - tests/unit/simulation/systems/test_tactical_mine_resolver.py
  - tests/unit/strategy/engine/test_minefield_resolver.py
- Heuristically untested symbols (17):
  - MineDetonationEvent
  - MinefieldResolutionResult
  - MinefieldResolutionResult.total_damage_applied
  - _compute_size_score
  - _compute_maneuver_score
  - _get_ship_scores
  - _sigmoid
  - _iter_mines
  - _pop_mine_at
  - _mine_has_warhead
  - _get_warhead_damage
  - _mine_has_laserhead
  - _get_laserhead_attrs
  - MinefieldResolver._compute_p_trigger_from_scores
  - MinefieldResolver._resolve_warhead_pass
  - ... and 2 more

### game/strategy/engine/order_handlers/join_fleet.py (Tier 2: TIER_2_PARTIAL, 283 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py
- Heuristically untested symbols (4):
  - JoinFleetHandler.supported_order_types
  - JoinFleetHandler._validate_tick_inputs
  - JoinFleetHandler._execute_fleet_merge
  - JoinFleetHandler._emit_join_cancelled

### game/strategy/engine/planet_action_engine.py (Tier 2: TIER_2_PARTIAL, 395 LOC, layer: strategy)
- Total symbols: 15 | Heuristically tested: 5
- Candidate test files (3):
  - tests/unit/strategy/engine/test_engine_validation.py
  - tests/unit/strategy/engine/test_planet_action_engine.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
- Heuristically untested symbols (10):
  - PlanetActionTickResult
  - PlanetActionEngine.__init__
  - PlanetActionEngine._process_planet_tick
  - PlanetActionEngine._execute_order
  - PlanetActionEngine._initiate_activation
  - PlanetActionEngine._initiate_deactivation
  - PlanetActionEngine._resolve_component_key
  - PlanetActionEngine._get_energy_drain_rate
  - PlanetActionEngine._get_deactivation_time
  - PlanetActionEngine._find_ability_component_id

### game/strategy/engine/superweapon_command_handlers.py (Tier 2: TIER_2_PARTIAL, 460 LOC, layer: strategy)
- Total symbols: 26 | Heuristically tested: 18
- Candidate test files (3):
  - tests/unit/strategy/engine/test_superweapon_command_handlers.py
  - tests/unit/strategy/engine/test_superweapon_edge_cases.py
  - tests/unit/strategy/engine/test_superweapon_handler_validation.py
- Heuristically untested symbols (8):
  - MissionCommandHandler
  - MissionCommandHandler._validate_mission
  - ImplodePlanetMissionCommandHandler._validate_mission
  - StellerateStarMissionCommandHandler._validate_mission
  - OpenWarpPointMissionCommandHandler._validate_mission
  - CloseWarpPointMissionCommandHandler._validate_mission
  - CreateDysonSphereMissionCommandHandler._validate_mission
  - register

### game/strategy/engine/superweapon_handlers/implode_planet.py (Tier 0: TIER_0_NO_TESTS, 60 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - process_implode_planet
  - _effect

### game/strategy/engine/superweapon_handlers/open_warp_point.py (Tier 0: TIER_0_NO_TESTS, 106 LOC, layer: strategy)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - process_open_warp_point
  - _precheck
  - _effect

### game/strategy/facade/dto/planet_dto.py (Tier 2: TIER_2_PARTIAL, 168 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 2
- Candidate test files (4):
  - tests/unit/strategy/facade/test_population_dtos.py
  - tests/unit/strategy/facade/test_system_dto.py
  - tests/unit/strategy/services/test_cargo_transfer_service.py
  - tests/unit/ui/screens/test_cargo_quick_dialog_issuance.py
- Heuristically untested symbols (3):
  - _is_any_planetary_shield_active
  - _dict_to_tuple
  - _resource_dict_to_catalog_tuple

### game/strategy/facade/slices/command_dispatch_slice.py (Tier 3: TIER_3_APPARENTLY_COVERED, 125 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/strategy/engine/test_command_registry_contract.py
  - tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py

### game/strategy/interfaces/engines/orders.py (Tier 0: TIER_0_NO_TESTS, 136 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - IOrderProcessor
  - IOrderProcessor.process_instant_orders
  - IOrderProcessor.execute_action_order
  - IActionExecutionEngine
  - IActionExecutionEngine.process_action_ticks

### game/strategy/services/fleet_cargo_projector.py (Tier 3: TIER_3_APPARENTLY_COVERED, 64 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/strategy/services/test_fleet_cargo_projector.py

### game/strategy/services/mine_group_service.py (Tier 3: TIER_3_APPARENTLY_COVERED, 151 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/strategy/services/test_mine_group_service.py

### game/strategy/services/planet_economy_projector.py (Tier 2: TIER_2_PARTIAL, 244 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 6
- Candidate test files (3):
  - tests/unit/strategy/services/test_planet_economy_projector.py
  - tests/unit/ui/panels/test_compute_planet_production.py
  - tests/unit/ui/panels/test_planet_report_panel.py
- Heuristically untested symbols (2):
  - PlanetEconomyProjector._project_harvest
  - PlanetEconomyProjector._project_upkeep

### game/strategy/systems/design_catalog.py (Tier 2: TIER_2_PARTIAL, 330 LOC, layer: strategy)
- Total symbols: 23 | Heuristically tested: 16
- Candidate test files (11):
  - tests/unit/strategy/design_catalog/test_cache_invalidation.py
  - tests/unit/strategy/design_catalog/test_catalog.py
  - tests/unit/strategy/design_catalog/test_filter_designs.py
  - tests/unit/strategy/design_catalog/test_pending_built_count_flush.py
  - tests/unit/strategy/design_catalog/test_search_designs.py
  - tests/unit/strategy/engine/session/test_bootstrap.py
  - tests/unit/strategy/engine/test_production_spawner.py
  - tests/unit/strategy/facade/test_designs_by_empire_through_catalog.py
  - ... and 3 more
- Heuristically untested symbols (7):
  - DesignCatalog.lookup_data
  - DesignCatalog.has_design
  - DesignCatalog.upsert_design
  - DesignCatalog.remove_design
  - DesignCatalog.get_design_path
  - DesignCatalog.has_design
  - DesignCatalog.mark_obsolete

### game/ui/components/table/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 37 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (2):
  - tests/unit/ui/screens/test_event_log_replay_button.py
  - tests/unit/ui/screens/test_fleet_report_window_multi_select.py

### game/ui/orchestration/__init__.py (Tier 0: TIER_0_NO_TESTS, 1 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/ui/panels/race_flag_gallery.py (Tier 2: TIER_2_PARTIAL, 196 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/ui/test_race_flag_gallery.py
- Heuristically untested symbols (8):
  - RaceFlagGallery._get_label_text
  - RaceFlagGallery._get_thumb_size
  - RaceFlagGallery._get_preview_size
  - RaceFlagGallery._get_object_id_prefix
  - RaceFlagGallery._get_preview_panel_object_id
  - RaceFlagGallery._get_current_selection
  - RaceFlagGallery._set_selection
  - RaceFlagGallery._update_preview

### game/ui/screens/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 0 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (14):
  - tests/unit/builder/test_builder_drag_drop_real.py
  - tests/unit/strategy/test_ui_dto_ai_readers_no_legacy_substrate.py
  - tests/unit/systems/test_main_integration.py
  - tests/unit/ui/screens/test_fleet_report_filters.py
  - tests/unit/ui/screens/test_species_selector_mixin.py
  - tests/unit/ui/screens/test_strategy_detail_fmt.py
  - tests/unit/ui/screens/test_strategy_fleet_command_router.py
  - tests/unit/ui/screens/test_strategy_panel_manager.py
  - ... and 6 more

### game/ui/screens/battle_setup/input_handler.py (Tier 2: TIER_2_PARTIAL, 190 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/screens/battle_setup/test_input_handler.py
- Heuristically untested symbols (4):
  - BattleSetupInputHandler.__init__
  - BattleSetupInputHandler._handle_button
  - BattleSetupInputHandler._push_tick_limit_to_controller
  - BattleSetupInputHandler._handle_dropdown

### game/ui/screens/battle_setup/panels/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 15 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/ui/screens/battle_setup/test_renderer.py

### game/ui/screens/battle_setup/panels/center_panel.py (Tier 0: TIER_0_NO_TESTS, 299 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - build
  - _build_policy_controls

### game/ui/screens/builder/left_panel.py (Tier 0: TIER_0_NO_TESTS, 485 LOC, layer: ui)
- Total symbols: 13 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (13):
  - BuilderLeftPanel
  - BuilderLeftPanel.__init__
  - BuilderLeftPanel.on_registry_reloaded
  - BuilderLeftPanel.update
  - BuilderLeftPanel.is_dropdown_expanded
  - BuilderLeftPanel.get_hovered_list_item
  - BuilderLeftPanel.deselect_all
  - BuilderLeftPanel.update_component_list
  - BuilderLeftPanel.draw
  - BuilderLeftPanel.handle_event
  - BuilderLeftPanel.get_add_count
  - BuilderLeftPanel._get_selected_layer
  - BuilderLeftPanel.get_hovered_component

### game/ui/screens/event_log_data_source.py (Tier 2: TIER_2_PARTIAL, 250 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 10
- Candidate test files (3):
  - tests/unit/ui/screens/test_event_log_data_source.py
  - tests/unit/ui/screens/test_event_log_replay_button.py
  - tests/unit/ui/screens/test_event_log_window.py
- Heuristically untested symbols (2):
  - EventLogDataSource._get_cell_detail
  - EventLogDataSource._recompute_filtered

### game/ui/screens/strategy_render/cursor.py (Tier 0: TIER_0_NO_TESTS, 53 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - draw_move_preview
  - draw_ghost_hex
  - draw_hover_hex

### game/ui/screens/strategy_render/storms.py (Tier 3: TIER_3_APPARENTLY_COVERED, 178 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/screens/strategy_render/test_grid_and_storms.py

### game/ui/services/input_mapper.py (Tier 2: TIER_2_PARTIAL, 380 LOC, layer: ui)
- Total symbols: 17 | Heuristically tested: 13
- Candidate test files (9):
  - tests/unit/ui/screens/test_fleet_menu_items.py
  - tests/unit/ui/screens/test_keybindings_scene.py
  - tests/unit/ui/screens/test_strategy_input_handler_core.py
  - tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py
  - tests/unit/ui/screens/test_strategy_input_handler_transfer.py
  - tests/unit/ui/screens/test_strategy_ui_tooltips.py
  - tests/unit/ui/screens/test_sub_window_hotkeys.py
  - tests/unit/ui/screens/test_warp_hotkey.py
  - ... and 1 more
- Heuristically untested symbols (4):
  - InputMapper._load_bindings_from_file
  - InputMapper._build_lookup
  - InputMapper._resolve_pygame_key
  - InputMapper._contexts_overlap

### game/ui/utils/pygame_utils.py (Tier 0: TIER_0_NO_TESTS, 260 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (7):
  - create_centered_rect
  - calculate_ship_image_scale
  - scale_and_rotate_image
  - get_visible_bounding_box
  - scale_image_by_visible_portion
  - create_section_header
  - scale_image_to_fit
