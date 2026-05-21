# Coverage Data — Shard 09

**Coverage source:** heuristic
**File count:** 42 | **LOC estimate:** 9742
**Tiers:** 0=9 1=5 2=18 3=10

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/ai/protocols.py (Tier 3: TIER_3_APPARENTLY_COVERED, 125 LOC, layer: ai)
- Total symbols: 13 | Heuristically tested: 13
- Candidate test files (1):
  - tests/unit/ai/test_ai_protocols.py

### game/screen_router.py (Tier 0: TIER_0_NO_TESTS, 518 LOC, layer: game_root)
- Total symbols: 28 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (28):
  - SceneCallbacks
  - ScreenRouter
  - ScreenRouter.__init__
  - ScreenRouter._switch_scene
  - ScreenRouter.update_resolution
  - ScreenRouter.start_builder
  - ScreenRouter.on_builder_return
  - ScreenRouter.start_battle_setup
  - ScreenRouter.start_strategy_layer
  - ScreenRouter._on_new_game_start
  - ScreenRouter._on_new_game_cancel
  - ScreenRouter._start_quickstart
  - ScreenRouter.start_quickstart_1p
  - ScreenRouter.start_quickstart_2p
  - ScreenRouter.show_load_menu
  - ... and 13 more

### game/simulation/battle_state.py (Tier 3: TIER_3_APPARENTLY_COVERED, 832 LOC, layer: simulation)
- Total symbols: 31 | Heuristically tested: 31
- Candidate test files (5):
  - tests/unit/combat_lab/test_battle_state_capture_no_mode_kwarg.py
  - tests/unit/core/test_serializable_protocol.py
  - tests/unit/simulation/test_battle_state_live_object_bridges.py
  - tests/unit/simulation/test_battle_state_serialization.py
  - tests/unit/simulation/test_battle_state_validation.py

### game/simulation/components/abilities/planetary/resource_modifiers.py (Tier 0: TIER_0_NO_TESTS, 160 LOC, layer: simulation)
- Total symbols: 12 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (12):
  - StrategicResourceGenerationAbility
  - StrategicResourceGenerationAbility.__init__
  - StrategicResourceGenerationAbility.get_primary_value
  - StrategicResourceGenerationAbility.get_ui_rows
  - ResourceHarvestBoosterAbility
  - ResourceHarvestBoosterAbility.__init__
  - ResourceHarvestBoosterAbility.get_primary_value
  - ResourceHarvestBoosterAbility.get_ui_rows
  - BuildRateBoosterAbility
  - BuildRateBoosterAbility.__init__
  - BuildRateBoosterAbility.get_primary_value
  - BuildRateBoosterAbility.get_ui_rows

### game/simulation/components/modifier_manager.py (Tier 2: TIER_2_PARTIAL, 219 LOC, layer: simulation)
- Total symbols: 9 | Heuristically tested: 7
- Candidate test files (1):
  - tests/unit/simulation/components/test_modifier_manager.py
- Heuristically untested symbols (2):
  - ModifierManager.__init__
  - ModifierManager._load_initial_modifiers

### game/simulation/entities/ability_aggregator.py (Tier 3: TIER_3_APPARENTLY_COVERED, 205 LOC, layer: simulation)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/simulation/components/abilities/test_maintenance_abilities.py
  - tests/unit/simulation/entities/test_ability_aggregator.py

### game/simulation/entities/ship.py (Tier 2: TIER_2_PARTIAL, 607 LOC, layer: simulation)
- Total symbols: 63 | Heuristically tested: 49
- Candidate test files (84):
  - tests/unit/ai/test_ai.py
  - tests/unit/ai/test_ai_n_team_targeting.py
  - tests/unit/ai/test_ai_protocols.py
  - tests/unit/ai/test_movement_and_ai.py
  - tests/unit/builder/test_builder_drag_drop_real.py
  - tests/unit/builder/test_builder_improvements.py
  - tests/unit/builder/test_builder_logic.py
  - tests/unit/builder/test_builder_structure_features.py
  - ... and 76 more
- Heuristically untested symbols (4):
  - Ship.stat_querier
  - Ship.validator_helper
  - Ship.get_total_ecm_score
  - Ship.check_validity

### game/simulation/entities/ship_component_manager.py (Tier 0: TIER_0_NO_TESTS, 293 LOC, layer: simulation)
- Total symbols: 15 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (15):
  - ShipComponentManager
  - ShipComponentManager.__init__
  - ShipComponentManager._invalidate_components_cache
  - ShipComponentManager._attach_component
  - ShipComponentManager.add_component
  - ShipComponentManager.add_components_bulk
  - ShipComponentManager.remove_component
  - ShipComponentManager.get_all_components
  - ShipComponentManager.iter_components
  - ShipComponentManager.get_components_by_ability
  - ShipComponentManager.get_weapon_components_cached
  - ShipComponentManager.get_components_by_layer
  - ShipComponentManager.has_components
  - ShipComponentManager.find_component_with_index
  - ShipComponentManager.clear_non_hull_components

### game/simulation/entities/stat_contributors/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 43 LOC, layer: simulation)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (6):
  - tests/unit/simulation/entities/stat_contributors/test_command.py
  - tests/unit/simulation/entities/stat_contributors/test_defense.py
  - tests/unit/simulation/entities/stat_contributors/test_launch.py
  - tests/unit/simulation/entities/stat_contributors/test_movement.py
  - tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py
  - tests/unit/simulation/entities/stat_contributors/test_weapons.py

### game/simulation/replay/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 80 LOC, layer: simulation)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (6):
  - tests/unit/simulation/replay/test_replay_player.py
  - tests/unit/simulation/replay/test_replay_verifier.py
  - tests/unit/simulation/replay/test_serialization.py
  - tests/unit/strategy/services/test_replay_ship_builder_registry_contract.py
  - tests/unit/strategy/services/test_replay_verification_coordinator.py
  - tests/unit/test_app_bootstrap_invariants.py

### game/simulation/replay/replay_capture.py (Tier 2: TIER_2_PARTIAL, 138 LOC, layer: simulation)
- Total symbols: 10 | Heuristically tested: 2
- Candidate test files (3):
  - tests/unit/systems/test_main_integration.py
  - tests/unit/test_app_bootstrap_invariants.py
  - tests/unit/test_app_bootstrap_profiling.py
- Heuristically untested symbols (8):
  - ReplayCaptureContext
  - IReplayCaptureSink
  - IReplayCaptureSink.on_battle_started
  - IReplayCaptureSink.on_battle_ended
  - NullCaptureSink
  - NullCaptureSink.on_battle_started
  - NullCaptureSink.on_battle_ended
  - get_default_capture_sink

### game/simulation/systems/boundary_enforcement.py (Tier 0: TIER_0_NO_TESTS, 122 LOC, layer: simulation)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - enforce_boundary
  - apply_exit_policy
  - bounce_ship

### game/strategy/data/component_activation_state.py (Tier 3: TIER_3_APPARENTLY_COVERED, 144 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 10
- Candidate test files (13):
  - tests/unit/strategy/data/test_component_activation_state.py
  - tests/unit/strategy/data/test_facility_activation.py
  - tests/unit/strategy/data/test_planet_active_abilities.py
  - tests/unit/strategy/engine/test_component_activation_engine.py
  - tests/unit/strategy/engine/test_planet_action_engine.py
  - tests/unit/strategy/engine/test_planet_energy_engine.py
  - tests/unit/strategy/engine/test_planet_modifier_effect_engine.py
  - tests/unit/strategy/services/test_combat_modifier_collector.py
  - ... and 5 more

### game/strategy/data/design_role.py (Tier 3: TIER_3_APPARENTLY_COVERED, 179 LOC, layer: strategy)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/strategy/data/test_design_role.py

### game/strategy/data/task_force.py (Tier 2: TIER_2_PARTIAL, 126 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 7
- Candidate test files (6):
  - tests/unit/strategy/combat/test_spec_compiler_formation.py
  - tests/unit/strategy/data/test_fleet_hierarchy.py
  - tests/unit/strategy/data/test_fleet_hierarchy_integration.py
  - tests/unit/strategy/data/test_group_policies.py
  - tests/unit/strategy/facade/test_fleet_hierarchy_dto.py
  - tests/unit/strategy/fleets/test_task_force_formation.py
- Heuristically untested symbols (1):
  - TaskForce.__init__

### game/strategy/engine/commands/__init__.py (Tier 2: TIER_2_PARTIAL, 629 LOC, layer: strategy)
- Total symbols: 47 | Heuristically tested: 40
- Candidate test files (27):
  - tests/unit/strategy/data/test_superweapon_orders.py
  - tests/unit/strategy/engine/handlers/test_movement_handlers.py
  - tests/unit/strategy/engine/handlers/test_order_queue_handlers.py
  - tests/unit/strategy/engine/test_build_order_command_handler.py
  - tests/unit/strategy/engine/test_command_handlers_public_api.py
  - tests/unit/strategy/engine/test_command_ownership.py
  - tests/unit/strategy/engine/test_command_registry_contract.py
  - tests/unit/strategy/engine/test_command_registry_seeding.py
  - ... and 19 more
- Heuristically untested symbols (7):
  - TransferDirection
  - RemoveFromConstructionQueueCommand
  - ReorderConstructionQueueCommand
  - SetAtmosphereTargetCommand
  - SetGravityTargetCommand
  - SetWaterTargetCommand
  - SetRadiationShieldTargetCommand

### game/strategy/engine/commands/registry.py (Tier 2: TIER_2_PARTIAL, 494 LOC, layer: strategy)
- Total symbols: 23 | Heuristically tested: 19
- Candidate test files (11):
  - tests/unit/strategy/engine/commands/test_order_metadata_view.py
  - tests/unit/strategy/engine/test_command_registry_contract.py
  - tests/unit/strategy/engine/test_command_registry_seeding.py
  - tests/unit/strategy/engine/test_command_registry_thirdparty.py
  - tests/unit/strategy/engine/test_command_specs_contract.py
  - tests/unit/strategy/engine/test_order_persistence_from_metadata.py
  - tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py
  - tests/unit/strategy/facade/test_strategy_session_facade_public_api.py
  - ... and 3 more
- Heuristically untested symbols (4):
  - CommandRegistry.unregister
  - CommandRegistry.__len__
  - CommandRegistry.__contains__
  - _wrap

### game/strategy/engine/construction_forecast.py (Tier 2: TIER_2_PARTIAL, 100 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/strategy/engine/test_construction_forecast.py
- Heuristically untested symbols (1):
  - _get_planetary_ids

### game/strategy/engine/issuer_adapter.py (Tier 2: TIER_2_PARTIAL, 372 LOC, layer: strategy)
- Total symbols: 31 | Heuristically tested: 28
- Candidate test files (1):
  - tests/unit/strategy/engine/test_issuer_adapter.py
- Heuristically untested symbols (3):
  - _matches
  - _cv_matches
  - FleetShipIssuerAdapter.ship

### game/strategy/engine/order_handlers/launch_satellites.py (Tier 2: TIER_2_PARTIAL, 274 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/strategy/engine/order_handlers/test_launch_satellites_handler.py
  - tests/unit/strategy/engine/test_issuer_execution_contract.py
- Heuristically untested symbols (5):
  - LaunchSatellitesOrderHandler._run_with_issuer
  - LaunchSatellitesOrderHandler._find_ship
  - LaunchSatellitesOrderHandler._create_satellite_group
  - LaunchSatellitesOrderHandler._mint_group_id
  - LaunchSatellitesOrderHandler._carried_vehicle_to_ship_instance

### game/strategy/events/event_types.py (Tier 3: TIER_3_APPARENTLY_COVERED, 38 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (14):
  - tests/unit/strategy/engine/order_handlers/test_colonize_handler.py
  - tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py
  - tests/unit/strategy/engine/order_handlers/test_self_destruct_handler.py
  - tests/unit/strategy/engine/test_order_processor_colonize.py
  - tests/unit/strategy/engine/test_order_processor_instant.py
  - tests/unit/strategy/engine/test_planet_action_engine.py
  - tests/unit/strategy/engine/test_planet_energy_engine.py
  - tests/unit/strategy/engine/test_production_engine_consumption.py
  - ... and 6 more

### game/strategy/facade/slices/fleet_slice.py (Tier 2: TIER_2_PARTIAL, 191 LOC, layer: strategy)
- Total symbols: 12 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/strategy/facade/test_container_snapshots.py
- Heuristically untested symbols (9):
  - FleetSlice.__init__
  - FleetSlice.build_fleet_hex_index
  - FleetSlice.get_fleet
  - FleetSlice.get_fleets_at_hex
  - FleetSlice.get_fleet_path_preview
  - FleetSlice.get_fleet_path_projection
  - FleetSlice.can_move_to
  - FleetSlice.get_fleet_remaining_pods
  - _ship_container_snapshot

### game/strategy/generation/density/__init__.py (Tier 0: TIER_0_NO_TESTS, 27 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/strategy/generation/density/primitives/ring.py (Tier 3: TIER_3_APPARENTLY_COVERED, 63 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (3):
  - tests/unit/strategy/generation/density/conftest.py
  - tests/unit/strategy/generation/density/test_density_map.py
  - tests/unit/strategy/generation/density/test_ring.py

### game/strategy/services/ship_instance_write_service.py (Tier 2: TIER_2_PARTIAL, 163 LOC, layer: strategy)
- Total symbols: 14 | Heuristically tested: 11
- Candidate test files (3):
  - tests/unit/strategy/engine/session/test_bootstrap.py
  - tests/unit/strategy/engine/test_game_session_from_dict.py
  - tests/unit/strategy/services/test_ship_instance_write_service.py
- Heuristically untested symbols (3):
  - ShipInstanceWriteService.set_consumable_level
  - ShipInstanceWriteService.set_component_toggle
  - ShipInstanceWriteService.set_activation_state

### game/strategy/services/stabilizer_registry.py (Tier 3: TIER_3_APPARENTLY_COVERED, 119 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (4):
  - tests/unit/strategy/engine/test_superweapon_stabilizers.py
  - tests/unit/strategy/services/test_ability_metadata_contracts.py
  - tests/unit/strategy/services/test_ability_metadata_registry.py
  - tests/unit/strategy/services/test_stabilizer_registry.py

### game/ui/effects/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 1 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/ui/effects/test_hit_effects.py

### game/ui/panels/component_modifier_grid_panel.py (Tier 3: TIER_3_APPARENTLY_COVERED, 151 LOC, layer: ui)
- Total symbols: 10 | Heuristically tested: 10
- Candidate test files (1):
  - tests/unit/ui/panels/test_component_modifier_grid_panel.py

### game/ui/renderer/camera.py (Tier 3: TIER_3_APPARENTLY_COVERED, 195 LOC, layer: ui)
- Total symbols: 8 | Heuristically tested: 8
- Candidate test files (3):
  - tests/unit/core/test_protocols.py
  - tests/unit/ui/conftest.py
  - tests/unit/ui/test_camera.py

### game/ui/screens/battle_setup/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 16 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/ui/screens/battle_setup/test_spec_compiler.py

### game/ui/screens/battle_setup/constants.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 54 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/ui/screens/battle_setup/test_controller.py

### game/ui/screens/builder/modifier_logic.py (Tier 2: TIER_2_PARTIAL, 173 LOC, layer: ui)
- Total symbols: 10 | Heuristically tested: 6
- Candidate test files (4):
  - tests/unit/ui/screens/builder/test_mandatory_modifiers_ownership.py
  - tests/unit/ui/screens/builder/test_modifier_config_size_mount.py
  - tests/unit/ui/screens/builder/test_modifier_logic_service.py
  - tests/unit/ui/screens/builder/test_modifier_logic_smart_floor.py
- Heuristically untested symbols (4):
  - ModifierLogicService.__init__
  - ModifierLogicService.is_modifier_allowed
  - ModifierLogicService.get_mandatory_modifiers
  - ModifierLogicService.ensure_mandatory_modifiers

### game/ui/screens/empire_panel_window.py (Tier 2: TIER_2_PARTIAL, 724 LOC, layer: ui)
- Total symbols: 25 | Heuristically tested: 17
- Candidate test files (5):
  - tests/unit/ui/screens/test_empire_panel_lazy_load.py
  - tests/unit/ui/screens/test_empire_panel_window.py
  - tests/unit/ui/screens/test_empire_panel_window_reuse.py
  - tests/unit/ui/screens/test_strategy_modal_esc_close.py
  - tests/unit/ui/screens/test_strategy_modal_hidden_input.py
- Heuristically untested symbols (8):
  - EmpirePanelWindow._create_ui
  - EmpirePanelWindow._create_tab_buttons
  - EmpirePanelWindow._create_tab_panels
  - EmpirePanelWindow._build_treasury_tab
  - EmpirePanelWindow._render_species_card
  - EmpirePanelWindow._render_identity_section
  - EmpirePanelWindow._render_aptitudes_section
  - EmpirePanelWindow._build_placeholder_tab

### game/ui/screens/fleet_selection_window.py (Tier 2: TIER_2_PARTIAL, 157 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/screens/test_fleet_selection_window.py
- Heuristically untested symbols (3):
  - FleetSelectionUiBuilder
  - FleetSelectionUiBuilder.build
  - FleetSelectionWindow.__init__

### game/ui/screens/new_game_setup_view_model.py (Tier 2: TIER_2_PARTIAL, 191 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 11
- Candidate test files (2):
  - tests/unit/ui/screens/test_new_game_setup_controller.py
  - tests/unit/ui/screens/test_new_game_setup_view_model.py
- Heuristically untested symbols (1):
  - NewGameSetupViewModel.__init__

### game/ui/screens/race_setup/screen.py (Tier 2: TIER_2_PARTIAL, 512 LOC, layer: ui)
- Total symbols: 19 | Heuristically tested: 14
- Candidate test files (1):
  - tests/unit/ui/screens/test_race_setup_screen.py
- Heuristically untested symbols (4):
  - RaceSetupScreen._init_widget_refs
  - RaceSetupScreen._create_ui
  - RaceSetupScreen._create_tab_buttons
  - RaceSetupScreen._create_navigation_buttons

### game/ui/screens/strategy_windows/transfer_dialogs.py (Tier 0: TIER_0_NO_TESTS, 79 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - TransferDialogRegistrar
  - TransferDialogRegistrar.__init__
  - TransferDialogRegistrar.open
  - TransferDialogRegistrar.open_quick

### game/ui/screens/system_selection_window.py (Tier 2: TIER_2_PARTIAL, 171 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/screens/test_system_selection_window.py
- Heuristically untested symbols (2):
  - SystemSelectionUiBuilder
  - SystemSelectionUiBuilder.build

### game/ui/screens/test_lab/details/propulsion_outcomes.py (Tier 0: TIER_0_NO_TESTS, 229 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - is_propulsion_test
  - draw_propulsion_outcomes
  - _draw_motion_outcomes
  - _draw_turn_outcomes
  - _draw_stationary_outcomes

### game/ui/screens/test_lab/test_run_card.py (Tier 2: TIER_2_PARTIAL, 370 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 8
- Candidate test files (1):
  - tests/unit/ui/screens/test_lab/test_test_run_card.py
- Heuristically untested symbols (1):
  - TestRunCard.get_height

### game/ui/screens/water_target_editor.py (Tier 0: TIER_0_NO_TESTS, 227 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (9):
  - WaterTargetEditor
  - WaterTargetEditor.__init__
  - WaterTargetEditor._build_ui
  - WaterTargetEditor.update
  - WaterTargetEditor._button_handlers
  - WaterTargetEditor._on_apply
  - WaterTargetEditor._set_species_ideal
  - WaterTargetEditor._set_match_current
  - WaterTargetEditor._clear_target

### game/ui/services/tkinter_utils.py (Tier 0: TIER_0_NO_TESTS, 231 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (7):
  - get_tk_root
  - is_tkinter_available
  - reset_tk_root
  - open_save_dialog
  - open_load_dialog
  - prompt_string
  - copy_to_clipboard
