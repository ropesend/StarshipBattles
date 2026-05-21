# Coverage Data — Shard 17

**Coverage source:** heuristic
**File count:** 50 | **LOC estimate:** 9788
**Tiers:** 0=15 1=3 2=21 3=11

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/core/json_utils.py (Tier 3: TIER_3_APPARENTLY_COVERED, 271 LOC, layer: core)
- Total symbols: 7 | Heuristically tested: 7
- Candidate test files (22):
  - tests/unit/builder/test_ship_loading.py
  - tests/unit/combat_lab/services/conftest.py
  - tests/unit/combat_lab/services/test_scenario_data_service.py
  - tests/unit/core/profiling/test_persistence.py
  - tests/unit/core/test_json_utils.py
  - tests/unit/performance/test_profiler_perf.py
  - tests/unit/quickstart/conftest.py
  - tests/unit/quickstart/test_quickstart_designs.py
  - ... and 14 more

### game/core/patterns/__init__.py (Tier 0: TIER_0_NO_TESTS, 19 LOC, layer: core)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/core/protocols/boundary.py (Tier 0: TIER_0_NO_TESTS, 127 LOC, layer: core)
- Total symbols: 23 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (23):
  - IResourceReader
  - IResourceReader.get_value
  - IResourceReader.get_max_value
  - IResourceReader.get_resource_names
  - IPostBattleShip
  - IPostBattleShip.instance_id
  - IPostBattleShip.name
  - IPostBattleShip.hp
  - IPostBattleShip.max_hp
  - IPostBattleShip.is_alive
  - IPostBattleShip.is_derelict
  - IPostBattleShip.layers
  - IPostBattleShip.resources
  - IResourceHolder
  - IResourceHolder.resources
  - ... and 8 more

### game/core/protocols/combat.py (Tier 0: TIER_0_NO_TESTS, 134 LOC, layer: core)
- Total symbols: 25 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (25):
  - ICombatant
  - ICombatant.team_id
  - ICombatant.is_alive
  - ICombatant.position
  - IDamageable
  - IDamageable.current_hp
  - IDamageable.max_hp
  - IDamageable.is_derelict
  - ICombatShip
  - ICombatShip.name
  - ICombatShip.team_id
  - ICombatShip.is_alive
  - ICombatShip.is_derelict
  - ICombatShip.hp
  - ICombatShip.max_hp
  - ... and 10 more

### game/core/protocols/persistence.py (Tier 0: TIER_0_NO_TESTS, 28 LOC, layer: core)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - ISerializable
  - ISerializable.to_dict
  - ISerializable.from_dict

### game/exit_dialog.py (Tier 0: TIER_0_NO_TESTS, 103 LOC, layer: game_root)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - draw_exit_dialog
  - handle_exit_dialog_click
  - handle_exit_dialog_cancel

### game/research/systems/__init__.py (Tier 0: TIER_0_NO_TESTS, 4 LOC, layer: research)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/simulation/components/abilities/crew.py (Tier 2: TIER_2_PARTIAL, 127 LOC, layer: simulation)
- Total symbols: 8 | Heuristically tested: 7
- Candidate test files (4):
  - tests/unit/modifiers/test_crew_required_mass_scaling.py
  - tests/unit/modifiers/test_crew_resource_bindings.py
  - tests/unit/simulation/components/abilities/test_crew_abilities.py
  - tests/unit/simulation/components/abilities/test_maintenance_abilities.py
- Heuristically untested symbols (1):
  - RequiresMaintenance._parse_attrs

### game/simulation/components/abilities/planetary/_shared.py (Tier 0: TIER_0_NO_TESTS, 17 LOC, layer: simulation)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/simulation/components/abilities/recovery.py (Tier 0: TIER_0_NO_TESTS, 75 LOC, layer: simulation)
- Total symbols: 7 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (7):
  - _RecoveryAbilityBase
  - _RecoveryAbilityBase._parse_attrs
  - _RecoveryAbilityBase.recalculate
  - _RecoveryAbilityBase.get_primary_value
  - _RecoveryAbilityBase.get_ui_rows
  - RecoverFightersAbility
  - RecoverSatellitesAbility

### game/simulation/interfaces/ability_protocols.py (Tier 3: TIER_3_APPARENTLY_COVERED, 359 LOC, layer: simulation)
- Total symbols: 46 | Heuristically tested: 46
- Candidate test files (1):
  - tests/unit/simulation/interfaces/test_ability_protocols.py

### game/simulation/systems/tick_phase.py (Tier 3: TIER_3_APPARENTLY_COVERED, 201 LOC, layer: simulation)
- Total symbols: 34 | Heuristically tested: 34
- Candidate test files (1):
  - tests/unit/simulation/systems/test_tick_phases.py

### game/simulation/validation/base.py (Tier 3: TIER_3_APPARENTLY_COVERED, 126 LOC, layer: simulation)
- Total symbols: 7 | Heuristically tested: 7
- Candidate test files (3):
  - tests/unit/builder/test_ship_validator_di.py
  - tests/unit/simulation/validation/test_base_rule.py
  - tests/unit/simulation/validation/test_ship_validator_rules.py

### game/strategy/data/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 0 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (8):
  - tests/unit/strategy/data/test_build_queue_source.py
  - tests/unit/strategy/data/test_galaxy_system_generator.py
  - tests/unit/strategy/data/test_order_types_no_duplicated_metadata.py
  - tests/unit/strategy/data/test_ship_cargo_manager_no_legacy_substrate.py
  - tests/unit/strategy/engine/test_game_initializer.py
  - tests/unit/strategy/facade/slices/test_empire_slice.py
  - tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py
  - tests/unit/ui/test_race_summary_panel.py

### game/strategy/data/design_metadata.py (Tier 2: TIER_2_PARTIAL, 305 LOC, layer: strategy)
- Total symbols: 11 | Heuristically tested: 10
- Candidate test files (6):
  - tests/unit/fixtures/test_strategy_entities.py
  - tests/unit/strategy/data/test_design_metadata_mass_valid.py
  - tests/unit/strategy/data/test_design_metadata_validation.py
  - tests/unit/strategy/design_repository/test_repository.py
  - tests/unit/strategy/test_design_metadata.py
  - tests/unit/strategy/test_quickstart_builder.py
- Heuristically untested symbols (1):
  - DesignMetadata._calculate_construction_cost_from_ship

### game/strategy/data/galaxy.py (Tier 2: TIER_2_PARTIAL, 338 LOC, layer: strategy)
- Total symbols: 39 | Heuristically tested: 34
- Candidate test files (15):
  - tests/unit/strategy/data/test_fleet_id_global.py
  - tests/unit/strategy/data/test_galaxy.py
  - tests/unit/strategy/data/test_galaxy_add_warp_point.py
  - tests/unit/strategy/data/test_galaxy_protocols.py
  - tests/unit/strategy/data/test_galaxy_warp_generator.py
  - tests/unit/strategy/data/test_storm.py
  - tests/unit/strategy/engine/session/test_persistence_adapter.py
  - tests/unit/strategy/engine/test_game_initializer.py
  - ... and 7 more
- Heuristically untested symbols (2):
  - Galaxy.fleets_by_id
  - Galaxy.generate_planets

### game/strategy/data/galaxy_spatial_index.py (Tier 3: TIER_3_APPARENTLY_COVERED, 122 LOC, layer: strategy)
- Total symbols: 9 | Heuristically tested: 9
- Candidate test files (1):
  - tests/unit/strategy/data/test_galaxy_spatial_index.py

### game/strategy/data/galaxy_warp_generator.py (Tier 2: TIER_2_PARTIAL, 420 LOC, layer: strategy)
- Total symbols: 12 | Heuristically tested: 9
- Candidate test files (2):
  - tests/unit/strategy/data/test_galaxy_warp_generator.py
  - tests/unit/strategy/data/test_intrinsic_rng_determinism.py
- Heuristically untested symbols (3):
  - GalaxyWarpGenerator._build_edge_candidates
  - GalaxyWarpGenerator._should_add_density_edge
  - GalaxyWarpGenerator._add_density_edges

### game/strategy/data/planet_naming.py (Tier 3: TIER_3_APPARENTLY_COVERED, 63 LOC, layer: strategy)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/strategy/data/test_planet_naming.py

### game/strategy/data/planet_physics.py (Tier 3: TIER_3_APPARENTLY_COVERED, 212 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 6
- Candidate test files (5):
  - tests/unit/strategy/data/test_planet_gen.py
  - tests/unit/strategy/data/test_planet_physics.py
  - tests/unit/strategy/planet_atmosphere/conftest.py
  - tests/unit/strategy/planet_atmosphere/test_calculations.py
  - tests/unit/strategy/planet_atmosphere/test_generation.py

### game/strategy/data/race_caption_loader.py (Tier 2: TIER_2_PARTIAL, 116 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/strategy/data/test_race_caption_loader.py
- Heuristically untested symbols (2):
  - RaceCaptionLoader.__init__
  - RaceCaptionLoader._load

### game/strategy/engine/commands/order_metadata_view.py (Tier 3: TIER_3_APPARENTLY_COVERED, 133 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 8
- Candidate test files (8):
  - tests/unit/strategy/engine/commands/test_order_metadata_view.py
  - tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py
  - tests/unit/strategy/engine/test_command_registry_contract.py
  - tests/unit/strategy/engine/test_command_specs_contract.py
  - tests/unit/strategy/engine/test_order_persistence_from_metadata.py
  - tests/unit/strategy/fleet_movement_engine/test_characterization.py
  - tests/unit/strategy/services/test_action_time_resolver.py
  - tests/unit/strategy/test_fleet_order_processor.py

### game/strategy/engine/handlers/launch_fighters.py (Tier 0: TIER_0_NO_TESTS, 155 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - LaunchFightersCommandHandler
  - LaunchFightersCommandHandler.execute
  - LaunchFightersCommandHandler._execute_fleet
  - LaunchFightersCommandHandler._execute_planet
  - register

### game/strategy/engine/order_handlers/recover_satellites.py (Tier 2: TIER_2_PARTIAL, 274 LOC, layer: strategy)
- Total symbols: 9 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/strategy/engine/order_handlers/test_recover_satellites_handler.py
  - tests/unit/strategy/engine/test_issuer_execution_contract.py
- Heuristically untested symbols (4):
  - RecoverSatellitesOrderHandler._run_with_issuer
  - RecoverSatellitesOrderHandler._find_ship
  - RecoverSatellitesOrderHandler._find_satellite_constellation
  - RecoverSatellitesOrderHandler._satellite_ship_to_carried_vehicle

### game/strategy/engine/planet_modifier_effect_engine.py (Tier 2: TIER_2_PARTIAL, 108 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/strategy/engine/test_planet_modifier_effect_engine.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
- Heuristically untested symbols (6):
  - PlanetModifierEffectEngine.__init__
  - PlanetModifierEffectEngine._get_planet_mutator
  - PlanetModifierEffectEngine._process_planet
  - PlanetModifierEffectEngine._process_gravity
  - PlanetModifierEffectEngine._process_radiation
  - PlanetModifierEffectEngine._has_active_ability

### game/strategy/events/event_log.py (Tier 2: TIER_2_PARTIAL, 188 LOC, layer: strategy)
- Total symbols: 13 | Heuristically tested: 11
- Candidate test files (3):
  - tests/unit/fixtures/test_strategy_entities.py
  - tests/unit/strategy/events/test_event_log.py
  - tests/unit/strategy/events/test_event_validation.py
- Heuristically untested symbols (2):
  - EventLog.__init__
  - EventLog._matches_empire

### game/strategy/facade/slices/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 7 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py

### game/strategy/formulas/habitability.py (Tier 3: TIER_3_APPARENTLY_COVERED, 92 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/strategy/engine/test_happiness_engine.py
  - tests/unit/strategy/formulas/test_habitability.py

### game/strategy/generation/density/primitives/__init__.py (Tier 0: TIER_0_NO_TESTS, 23 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/strategy/services/empire_write_service.py (Tier 3: TIER_3_APPARENTLY_COVERED, 167 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 10
- Candidate test files (3):
  - tests/unit/strategy/engine/session/test_bootstrap.py
  - tests/unit/strategy/engine/test_game_session_from_dict.py
  - tests/unit/strategy/services/test_empire_write_service.py

### game/strategy/services/fleet_navigation_service.py (Tier 2: TIER_2_PARTIAL, 515 LOC, layer: strategy)
- Total symbols: 22 | Heuristically tested: 21
- Candidate test files (16):
  - tests/unit/strategy/engine/handlers/test_movement_handlers.py
  - tests/unit/strategy/engine/handlers/test_order_queue_handlers.py
  - tests/unit/strategy/engine/test_set_build_queue_paused_command.py
  - tests/unit/strategy/fleet_navigation/test_data_structures.py
  - tests/unit/strategy/fleet_navigation/test_destination_path.py
  - tests/unit/strategy/fleet_navigation/test_navigation_pure.py
  - tests/unit/strategy/fleet_navigation/test_projection.py
  - tests/unit/strategy/fleet_navigation/test_service_edge_cases.py
  - ... and 8 more
- Heuristically untested symbols (1):
  - FleetNavigationService._project_path_inner

### game/strategy/services/race_description_llm_controller.py (Tier 2: TIER_2_PARTIAL, 312 LOC, layer: strategy)
- Total symbols: 25 | Heuristically tested: 18
- Candidate test files (2):
  - tests/unit/strategy/services/test_race_description_llm_controller.py
  - tests/unit/ui/test_race_description_panel.py
- Heuristically untested symbols (7):
  - _FieldState
  - RaceDescriptionLLMController._start_field
  - RaceDescriptionLLMController._cancel_field
  - RaceDescriptionLLMController._gather_captions
  - RaceDescriptionLLMController._poll_field
  - RaceDescriptionLLMController._apply_field_transition
  - RaceDescriptionLLMController._fire_on_change

### game/strategy/validation/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 22 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (4):
  - tests/unit/strategy/engine/test_typed_planet_intents.py
  - tests/unit/strategy/validation/test_colonize_validator.py
  - tests/unit/strategy/validation/test_superweapon_validator.py
  - tests/unit/strategy/validation/test_validators_no_legacy_substrate.py

### game/strategy/validation/transfer_validator.py (Tier 2: TIER_2_PARTIAL, 443 LOC, layer: strategy)
- Total symbols: 9 | Heuristically tested: 3
- Candidate test files (3):
  - tests/unit/strategy/data/test_fms_a_audit_fixes.py
  - tests/unit/strategy/validation/test_transfer_drop_pod.py
  - tests/unit/strategy/validation/test_transfer_validator_robustness.py
- Heuristically untested symbols (6):
  - _get_resource_catalog
  - _is_known_cargo_type
  - TransferValidator._validate_fleet_transfer
  - TransferValidator._validate_unload
  - TransferValidator._validate_vehicle_load
  - TransferValidator._validate_vehicle_unload

### game/ui/panels/race_aptitudes_panel.py (Tier 2: TIER_2_PARTIAL, 280 LOC, layer: ui)
- Total symbols: 13 | Heuristically tested: 6
- Candidate test files (2):
  - tests/unit/ui/panels/test_race_aptitudes_panel.py
  - tests/unit/ui/screens/test_race_setup_screen.py
- Heuristically untested symbols (7):
  - RaceAptitudesPanel._create_content
  - RaceAptitudesPanel._create_budget_section
  - RaceAptitudesPanel._create_aptitude_section
  - RaceAptitudesPanel._create_cost_breakdown_section
  - RaceAptitudesPanel._get_aptitude_value
  - RaceAptitudesPanel._set_aptitude_value
  - RaceAptitudesPanel._format_cost

### game/ui/research/research_scene.py (Tier 2: TIER_2_PARTIAL, 401 LOC, layer: ui)
- Total symbols: 15 | Heuristically tested: 14
- Candidate test files (8):
  - tests/unit/research/research_controls/conftest.py
  - tests/unit/research/research_scene/conftest.py
  - tests/unit/research/research_scene/test_callbacks.py
  - tests/unit/research/research_scene/test_event_routing_and_draw.py
  - tests/unit/research/research_scene/test_initialization.py
  - tests/unit/research/research_scene/test_interaction.py
  - tests/unit/research/test_research_scene_di.py
  - tests/unit/ui/test_scene_protocol.py
- Heuristically untested symbols (1):
  - ResearchTreeScene._calculate_layout

### game/ui/screens/battle_screen.py (Tier 2: TIER_2_PARTIAL, 669 LOC, layer: ui)
- Total symbols: 36 | Heuristically tested: 22
- Candidate test files (10):
  - tests/unit/ai/test_movement_and_ai.py
  - tests/unit/test_lab/test_visual_run.py
  - tests/unit/ui/conftest.py
  - tests/unit/ui/screens/test_battle_screen_edge_cases.py
  - tests/unit/ui/screens/test_battle_screen_modifier_labels.py
  - tests/unit/ui/screens/test_battle_setup_logic.py
  - tests/unit/ui/test_battle_screen.py
  - tests/unit/ui/test_battle_screen_extended.py
  - ... and 2 more
- Heuristically untested symbols (13):
  - BattleScreen.stats_panel_width
  - BattleScreen._resolve_focus_target
  - BattleScreen._update_headless
  - BattleScreen._update_visual_effects
  - BattleScreen._update_tick_rate
  - BattleScreen._subscribe_combat_events
  - BattleScreen._add_hit_effect
  - BattleScreen._on_shield_hit
  - BattleScreen._on_component_hit
  - BattleScreen._on_component_destroyed
  - BattleScreen._on_ship_destroyed
  - BattleScreen.draw_hud
  - BattleScreen.print_headless_summary

### game/ui/screens/build_queue_queue_data_source.py (Tier 2: TIER_2_PARTIAL, 184 LOC, layer: ui)
- Total symbols: 8 | Heuristically tested: 6
- Candidate test files (1):
  - tests/unit/ui/screens/test_build_queue_queue_data_source.py
- Heuristically untested symbols (2):
  - _format_int
  - BuildQueueQueueDataSource.__init__

### game/ui/screens/menu_scene.py (Tier 2: TIER_2_PARTIAL, 111 LOC, layer: ui)
- Total symbols: 8 | Heuristically tested: 7
- Candidate test files (2):
  - tests/unit/ui/screens/test_menu_scene.py
  - tests/unit/ui/test_scene_protocol.py
- Heuristically untested symbols (1):
  - MenuScene._create_buttons

### game/ui/screens/new_game_setup_screen.py (Tier 2: TIER_2_PARTIAL, 684 LOC, layer: ui)
- Total symbols: 20 | Heuristically tested: 15
- Candidate test files (2):
  - tests/unit/ui/screens/test_new_game_setup_extended.py
  - tests/unit/ui/test_new_game_setup.py
- Heuristically untested symbols (5):
  - system_count_slider_inverse
  - NewGameSetupScreen._init_state
  - NewGameSetupScreen._init_widget_refs
  - NewGameSetupScreen._create_empire_inputs
  - NewGameSetupScreen._on_load_race_clicked

### game/ui/screens/planet_list_helpers.py (Tier 0: TIER_0_NO_TESTS, 215 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (6):
  - _get_planetary_ids
  - _format_population
  - _render_effect_cell
  - build_effect_columns
  - PlanetListUiBuilder
  - PlanetListUiBuilder.build

### game/ui/screens/strategy_fleet_ops.py (Tier 2: TIER_2_PARTIAL, 230 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 10
- Candidate test files (2):
  - tests/unit/ui/screens/test_strategy_fleet_ops.py
  - tests/unit/ui/screens/test_strategy_screen_composition.py
- Heuristically untested symbols (2):
  - _format_result_error
  - FleetOperations.__init__

### game/ui/screens/strategy_ui_action_router.py (Tier 2: TIER_2_PARTIAL, 97 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/screens/test_strategy_ui_action_router.py
- Heuristically untested symbols (1):
  - UIActionRouter.__init__

### game/ui/screens/strategy_window_manager.py (Tier 2: TIER_2_PARTIAL, 450 LOC, layer: ui)
- Total symbols: 41 | Heuristically tested: 35
- Candidate test files (5):
  - tests/unit/ui/screens/test_strategy_event_router_load_dialog_modal_tracking.py
  - tests/unit/ui/screens/test_strategy_modal_window.py
  - tests/unit/ui/screens/test_strategy_window_manager.py
  - tests/unit/ui/screens/test_strategy_window_manager_public_api.py
  - tests/unit/ui/screens/test_sub_window_hotkeys.py
- Heuristically untested symbols (6):
  - StrategyWindowManager.unregister_modal
  - StrategyWindowManager.iter_snapshot_windows
  - StrategyWindowManager._open_planet_editor
  - StrategyWindowManager.show_message_dialog
  - StrategyWindowManager._on_star_list_closed
  - StrategyWindowManager._on_settings_closed

### game/ui/screens/test_lab/details/draw_context.py (Tier 0: TIER_0_NO_TESTS, 62 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - DetailsDrawContext
  - OutcomePalette

### game/ui/screens/test_lab/ship_panels.py (Tier 0: TIER_0_NO_TESTS, 260 LOC, layer: ui)
- Total symbols: 17 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (17):
  - ShipPanel
  - ShipPanel.__init__
  - ShipPanel.handle_event
  - ShipPanel.update
  - ShipPanel.draw
  - TabbedShipPanel
  - TabbedShipPanel.__init__
  - TabbedShipPanel._calculate_tab_rects
  - TabbedShipPanel.handle_event
  - TabbedShipPanel.update
  - TabbedShipPanel.draw
  - TabbedShipPanel.get_selected_ship_info
  - ComponentPanel
  - ComponentPanel.__init__
  - ComponentPanel.handle_event
  - ... and 2 more

### game/ui/screens/transfer_dialog.py (Tier 2: TIER_2_PARTIAL, 418 LOC, layer: ui)
- Total symbols: 19 | Heuristically tested: 10
- Candidate test files (5):
  - tests/unit/ui/screens/test_sub_window_hotkeys.py
  - tests/unit/ui/screens/test_transfer_dialog.py
  - tests/unit/ui/screens/test_transfer_dialog_characterization.py
  - tests/unit/ui/screens/test_transfer_dialog_enhanced.py
  - tests/unit/ui/screens/test_transfer_dialog_keeps_open_on_abort.py
- Heuristically untested symbols (9):
  - TransferDialog._init_widget_refs
  - TransferDialog._on_target_changed
  - TransferDialog._reset_and_build_grid
  - TransferDialog._build_grid
  - TransferDialog._update_pending_label
  - TransferDialog._refresh_mass_preview
  - TransferDialog._on_filter_toggle
  - TransferDialog.process_event
  - TransferDialog.handle_external_selection

### game/ui/widgets/__init__.py (Tier 0: TIER_0_NO_TESTS, 9 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/ui/widgets/column_toggle_section.py (Tier 0: TIER_0_NO_TESTS, 66 LOC, layer: ui)
- Total symbols: 1 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (1):
  - build_column_toggle_section

### game/ui/widgets/panel_factory.py (Tier 3: TIER_3_APPARENTLY_COVERED, 46 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/widgets/test_panel_factory.py
