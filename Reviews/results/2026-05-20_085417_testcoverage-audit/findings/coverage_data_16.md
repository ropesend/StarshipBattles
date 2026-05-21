# Coverage Data — Shard 16

**Coverage source:** heuristic
**File count:** 42 | **LOC estimate:** 9608
**Tiers:** 0=9 1=1 2=20 3=12

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/ai/fighter_controller.py (Tier 2: TIER_2_PARTIAL, 140 LOC, layer: ai)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ai/test_fighter_controller.py
- Heuristically untested symbols (1):
  - FighterAIController._find_nearest_enemy

### game/app_bootstrap.py (Tier 0: TIER_0_NO_TESTS, 343 LOC, layer: game_root)
- Total symbols: 7 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (7):
  - configure_logging
  - parse_args
  - BootstrapResult
  - _detect_resolution
  - _timed_phase
  - bootstrap
  - _replay_combat_lab_fallback

### game/core/event_logging.py (Tier 3: TIER_3_APPARENTLY_COVERED, 61 LOC, layer: core)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (10):
  - tests/unit/core/event_logging/test_event_bus.py
  - tests/unit/simulation/test_projectile_event_bus_wiring.py
  - tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py
  - tests/unit/strategy/engine/session/test_bootstrap.py
  - tests/unit/strategy/engine/test_conflict_resolution_event_replay.py
  - tests/unit/strategy/engine/test_production_refactor.py
  - tests/unit/strategy/engine/test_superweapon_event_payloads.py
  - tests/unit/strategy/engine/test_superweapon_order_processor.py
  - ... and 2 more

### game/research/data/__init__.py (Tier 0: TIER_0_NO_TESTS, 6 LOC, layer: research)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/services/llm/types.py (Tier 3: TIER_3_APPARENTLY_COVERED, 95 LOC, layer: services)
- Total symbols: 5 | Heuristically tested: 5
- Candidate test files (7):
  - tests/unit/services/llm/conftest.py
  - tests/unit/services/llm/test_background.py
  - tests/unit/services/llm/test_deepseek.py
  - tests/unit/services/llm/test_provider_protocol.py
  - tests/unit/services/llm/test_types.py
  - tests/unit/strategy/services/test_race_description_llm_controller.py
  - tests/unit/strategy/services/test_race_description_prompt_builder.py

### game/simulation/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 130 LOC, layer: simulation)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (4):
  - tests/unit/simulation/battle_controller/test_outcome_emission.py
  - tests/unit/simulation/test_battle_outcome.py
  - tests/unit/simulation/test_battle_spec.py
  - tests/unit/systems/test_physics.py

### game/simulation/combat/families/pdc.py (Tier 3: TIER_3_APPARENTLY_COVERED, 45 LOC, layer: simulation)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/simulation/combat/test_weapon_family_handlers.py

### game/simulation/combat/targeting_system.py (Tier 2: TIER_2_PARTIAL, 325 LOC, layer: simulation)
- Total symbols: 7 | Heuristically tested: 5
- Candidate test files (3):
  - tests/unit/simulation/combat/test_targeting_system.py
  - tests/unit/simulation/combat/test_weapon_dispatch_golden.py
  - tests/unit/simulation/combat/test_weapon_firing_system.py
- Heuristically untested symbols (2):
  - TargetingSystem._get_pdc_valid_targets
  - TargetingSystem._get_pdc_target_type

### game/simulation/components/abilities/planetary/environmental.py (Tier 0: TIER_0_NO_TESTS, 90 LOC, layer: simulation)
- Total symbols: 8 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (8):
  - EnvironmentalDamageAbility
  - EnvironmentalDamageAbility.__init__
  - EnvironmentalDamageAbility.get_primary_value
  - EnvironmentalDamageAbility.get_ui_rows
  - FuelDrainAbility
  - FuelDrainAbility.__init__
  - FuelDrainAbility.get_primary_value
  - FuelDrainAbility.get_ui_rows

### game/simulation/components/component_constants.py (Tier 3: TIER_3_APPARENTLY_COVERED, 69 LOC, layer: simulation)
- Total symbols: 7 | Heuristically tested: 7
- Candidate test files (18):
  - tests/unit/builder/test_builder_structure_features.py
  - tests/unit/builder/test_bulk_add.py
  - tests/unit/core/test_pure_loaders.py
  - tests/unit/modifiers/test_invalid_operation_handling.py
  - tests/unit/modifiers/test_modifier_loader_v2.py
  - tests/unit/modifiers/test_multi_ability_effects.py
  - tests/unit/regressions/test_bug_regressions_2026_01.py
  - tests/unit/simulation/battle_runner/test_spec_component_validation.py
  - ... and 10 more

### game/simulation/validation/ship_validator.py (Tier 2: TIER_2_PARTIAL, 450 LOC, layer: simulation)
- Total symbols: 27 | Heuristically tested: 15
- Candidate test files (12):
  - tests/unit/builder/test_builder_validation.py
  - tests/unit/builder/test_requirement_abilities.py
  - tests/unit/builder/test_ship_validator_di.py
  - tests/unit/entities/test_bridge_requirement_removal.py
  - tests/unit/regressions/test_bug_regressions_2026_01.py
  - tests/unit/simulation/validation/test_maintenance_validator_rules.py
  - tests/unit/simulation/validation/test_ship_validator_rules.py
  - tests/unit/systems/test_layer_refinements.py
  - ... and 4 more
- Heuristically untested symbols (12):
  - LayerConstraintRule._do_validate
  - UniqueComponentRule._should_validate
  - UniqueComponentRule._do_validate
  - ExclusiveGroupRule._should_validate
  - ExclusiveGroupRule._do_validate
  - MountDependencyRule._do_validate
  - LayerRestrictionDefinitionRule._do_validate
  - LayerRestrictionDefinitionRule._check_block_rules
  - LayerRestrictionDefinitionRule._check_allow_rules
  - MassBudgetRule._do_validate
  - ClassRequirementsRule._do_validate
  - ResourceDependencyRule._do_validate

### game/strategy/adapters/__init__.py (Tier 0: TIER_0_NO_TESTS, 10 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/strategy/data/build_queue_source.py (Tier 2: TIER_2_PARTIAL, 463 LOC, layer: strategy)
- Total symbols: 13 | Heuristically tested: 10
- Candidate test files (9):
  - tests/unit/strategy/data/test_build_queue_source.py
  - tests/unit/strategy/data/test_colony_yard_registries.py
  - tests/unit/strategy/engine/test_planetary_yard_requirement.py
  - tests/unit/strategy/engine/test_production_refactor.py
  - tests/unit/strategy/engine/test_production_repro.py
  - tests/unit/ui/panels/test_build_queue_controller.py
  - tests/unit/ui/screens/test_build_queue_screen_lifecycle.py
  - tests/unit/ui/screens/test_empire_build_queue_viewmodel.py
  - ... and 1 more
- Heuristically untested symbols (3):
  - _load_production_rates
  - _get_facility_production_rates
  - _get_planetary_yard_size_multiplier

### game/strategy/data/classification_config.py (Tier 2: TIER_2_PARTIAL, 173 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/strategy/data/test_classification_config.py
- Heuristically untested symbols (3):
  - ClassificationConfig.__init__
  - ClassificationConfig._load_from_json
  - ClassificationConfig._use_defaults

### game/strategy/data/planet.py (Tier 2: TIER_2_PARTIAL, 504 LOC, layer: strategy)
- Total symbols: 40 | Heuristically tested: 35
- Candidate test files (73):
  - tests/unit/core/test_protocols.py
  - tests/unit/strategy/data/test_build_context.py
  - tests/unit/strategy/data/test_build_queue_source.py
  - tests/unit/strategy/data/test_construction_queue_paused_persistence.py
  - tests/unit/strategy/data/test_facility_construction_queue.py
  - tests/unit/strategy/data/test_facility_resource_tracking.py
  - tests/unit/strategy/data/test_fleet_order_resolution.py
  - tests/unit/strategy/data/test_galaxy.py
  - ... and 65 more
- Heuristically untested symbols (5):
  - _is_carried_vehicle_dict
  - _staging_yard_carried_vehicle
  - Planet.total_pressure_atm
  - Planet.get_staging_mass
  - Planet.add_production

### game/strategy/data/ship_instance_bridge.py (Tier 2: TIER_2_PARTIAL, 173 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/strategy/ship_instance/test_ship_instance_bridge.py
- Heuristically untested symbols (1):
  - ShipInstanceBridge.__init__

### game/strategy/data/ship_instance_serializer.py (Tier 3: TIER_3_APPARENTLY_COVERED, 211 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 6
- Candidate test files (2):
  - tests/unit/strategy/data/test_fms_a_audit_fixes.py
  - tests/unit/strategy/ship_instance/test_ship_instance_serializer.py

### game/strategy/engine/action_execution_engine.py (Tier 2: TIER_2_PARTIAL, 329 LOC, layer: strategy)
- Total symbols: 9 | Heuristically tested: 5
- Candidate test files (7):
  - tests/unit/strategy/engine/test_action_execution_engine.py
  - tests/unit/strategy/engine/test_action_execution_engine_gaps.py
  - tests/unit/strategy/engine/test_build_order_processor.py
  - tests/unit/strategy/engine/test_engine_validation.py
  - tests/unit/strategy/turn_engine/test_dependency_injection.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
  - tests/unit/strategy/turn_engine/test_turn_processing.py
- Heuristically untested symbols (4):
  - ActionExecutionEngine.__init__
  - ActionExecutionEngine._process_fleet_action_tick
  - ActionExecutionEngine._process_planet_action_tick
  - ActionExecutionEngine._execute_planet_action

### game/strategy/engine/turn_phase_registry.py (Tier 3: TIER_3_APPARENTLY_COVERED, 340 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (5):
  - tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py
  - tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py
  - tests/unit/strategy/turn_engine/test_phase_isolation_with_mock_context.py
  - tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py
  - tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py

### game/strategy/generation/storm_generator.py (Tier 3: TIER_3_APPARENTLY_COVERED, 223 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/strategy/generation/test_storm_generator.py

### game/strategy/services/effect_ability_display.py (Tier 2: TIER_2_PARTIAL, 182 LOC, layer: strategy)
- Total symbols: 7 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/strategy/services/test_effect_ability_display.py
- Heuristically untested symbols (4):
  - _effect_facet
  - _ability_kind
  - _format_status
  - _is_activatable

### game/strategy/services/planet_query_service.py (Tier 3: TIER_3_APPARENTLY_COVERED, 83 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/strategy/services/test_planet_query_service.py

### game/strategy/services/race_resolver.py (Tier 3: TIER_3_APPARENTLY_COVERED, 43 LOC, layer: strategy)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/strategy/services/test_race_resolver.py

### game/strategy/services/replay_store.py (Tier 2: TIER_2_PARTIAL, 495 LOC, layer: strategy)
- Total symbols: 26 | Heuristically tested: 9
- Candidate test files (2):
  - tests/unit/strategy/services/test_replay_store_eviction.py
  - tests/unit/strategy/services/test_replay_verification_coordinator.py
- Heuristically untested symbols (17):
  - load_replay_settings
  - _PendingCapture
  - ReplayStore.__init__
  - ReplayStore.add_on_record_persisted_listener
  - ReplayStore.remove_on_record_persisted_listener
  - ReplayStore._replay_dir
  - ReplayStore._ensure_replay_dir
  - ReplayStore.on_battle_started
  - ReplayStore.on_battle_ended
  - ReplayStore.load
  - ReplayStore.load_or_error
  - ReplayStore.delete
  - ReplayStore._safe_load
  - ReplayStore._iter_replay_files
  - ReplayStore._replay_id_from_path
  - ... and 2 more

### game/ui/panels/planet_report_panel.py (Tier 2: TIER_2_PARTIAL, 674 LOC, layer: ui)
- Total symbols: 17 | Heuristically tested: 13
- Candidate test files (3):
  - tests/unit/ui/panels/test_planet_report_panel.py
  - tests/unit/ui/panels/test_planet_report_panel_characterization.py
  - tests/unit/ui/screens/test_build_queue_screen_lifecycle.py
- Heuristically untested symbols (4):
  - _qty_cell
  - _qual_cell
  - _flow_cell
  - _stockpile_cell

### game/ui/screens/battle_setup/controller.py (Tier 2: TIER_2_PARTIAL, 559 LOC, layer: ui)
- Total symbols: 38 | Heuristically tested: 26
- Candidate test files (1):
  - tests/unit/ui/screens/battle_setup/test_controller.py
- Heuristically untested symbols (12):
  - BattleSetupController.__init__
  - BattleSetupController._get_active_fleet
  - BattleSetupController.duplicate_task_force
  - BattleSetupController.duplicate_squadron
  - BattleSetupController.set_fleet_battle_role
  - BattleSetupController.set_ship_policy
  - BattleSetupController.set_selected_policy
  - BattleSetupController._toggle_dict_for
  - BattleSetupController.save_setup
  - BattleSetupController._save_to_path
  - BattleSetupController.load_setup
  - BattleSetupController._load_from_path

### game/ui/screens/battle_setup/screen.py (Tier 2: TIER_2_PARTIAL, 98 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/ui/screens/battle_setup/test_renderer.py
  - tests/unit/ui/screens/test_battle_setup_state.py
- Heuristically untested symbols (6):
  - FleetBattleSetupScreen.handle_event
  - FleetBattleSetupScreen.update
  - FleetBattleSetupScreen.draw
  - FleetBattleSetupScreen.handle_resize
  - FleetBattleSetupScreen.start
  - FleetBattleSetupScreen._get_toggle

### game/ui/screens/build_queue_helpers.py (Tier 2: TIER_2_PARTIAL, 214 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/ui/screens/test_build_queue_helpers.py
- Heuristically untested symbols (1):
  - _get_planetary_ids

### game/ui/screens/build_queue_renderer.py (Tier 0: TIER_0_NO_TESTS, 247 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (7):
  - BuildQueueRenderer
  - BuildQueueRenderer.__init__
  - BuildQueueRenderer.refresh_items_list
  - BuildQueueRenderer.refresh_queue_display
  - BuildQueueRenderer.refresh_roles_list
  - BuildQueueRenderer.update_queue_header
  - BuildQueueRenderer.refresh_pause_button

### game/ui/screens/build_queue_viewmodel.py (Tier 2: TIER_2_PARTIAL, 268 LOC, layer: ui)
- Total symbols: 19 | Heuristically tested: 17
- Candidate test files (1):
  - tests/unit/ui/screens/test_build_queue_viewmodel.py
- Heuristically untested symbols (2):
  - BuildQueueScreenViewModel.__init__
  - BuildQueueScreenViewModel.queue_sources

### game/ui/screens/builder/components.py (Tier 2: TIER_2_PARTIAL, 173 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/ui/screens/builder/test_components.py
- Heuristically untested symbols (2):
  - ComponentListItem.set_selected
  - ComponentListItem.set_hovered

### game/ui/screens/builder/weapons_input_handler.py (Tier 3: TIER_3_APPARENTLY_COVERED, 102 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/builder/test_weapons_input_handler.py

### game/ui/screens/fleet_report_sidebar.py (Tier 2: TIER_2_PARTIAL, 512 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/ui/screens/test_fleet_report_sidebar.py
  - tests/unit/ui/screens/test_fleet_report_window_multi_select.py
- Heuristically untested symbols (7):
  - FleetReportSidebar.__init__
  - FleetReportSidebar._build_widgets
  - FleetReportSidebar._build_filter_section
  - FleetReportSidebar._create_status_filter_button
  - FleetReportSidebar._build_column_section
  - FleetReportSidebar._build_actions_section
  - FleetReportSidebar.update_column_button

### game/ui/screens/strategy_fleet_context_menu.py (Tier 2: TIER_2_PARTIAL, 218 LOC, layer: ui)
- Total symbols: 13 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/ui/screens/test_fleet_context_menu_dispatch.py
  - tests/unit/ui/screens/test_fleet_context_menu_position.py
- Heuristically untested symbols (8):
  - FleetContextMenu.__init__
  - FleetContextMenu._create_buttons
  - FleetContextMenu._format_row
  - FleetContextMenu.required_height
  - PlanetContextMenu
  - PlanetContextMenu.__init__
  - PlanetContextMenu._create_buttons
  - PlanetContextMenu.required_height

### game/ui/screens/strategy_render/warp_lanes.py (Tier 0: TIER_0_NO_TESTS, 69 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - draw_warp_lanes
  - is_on_screen

### game/ui/screens/strategy_windows/fleet_report_ctrl.py (Tier 0: TIER_0_NO_TESTS, 73 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - FleetReportRegistrar
  - FleetReportRegistrar.__init__
  - FleetReportRegistrar.open
  - FleetReportRegistrar._on_closed

### game/ui/screens/test_lab/renderer/orchestrator.py (Tier 0: TIER_0_NO_TESTS, 211 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - TestLabRenderer
  - TestLabRenderer._is_condition_verified
  - TestLabRenderer.__init__
  - TestLabRenderer.draw

### game/ui/screens/test_lab/renderer/test_list_panel.py (Tier 0: TIER_0_NO_TESTS, 202 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - TestListPanel
  - TestListPanel.__init__
  - TestListPanel.draw
  - TestListPanel._draw_scrollbar

### game/ui/screens/transfer_controller.py (Tier 2: TIER_2_PARTIAL, 369 LOC, layer: ui)
- Total symbols: 10 | Heuristically tested: 7
- Candidate test files (2):
  - tests/unit/ui/screens/test_transfer_controller.py
  - tests/unit/ui/screens/test_transfer_view_model_container.py
- Heuristically untested symbols (3):
  - TransferController.__init__
  - TransferController._resolve_endpoints
  - TransferController._direction

### game/ui/screens/workshop_viewmodel.py (Tier 2: TIER_2_PARTIAL, 494 LOC, layer: ui)
- Total symbols: 49 | Heuristically tested: 44
- Candidate test files (5):
  - tests/unit/ui/screens/test_workshop_viewmodel_pick_up.py
  - tests/unit/workshop/test_move_component.py
  - tests/unit/workshop/test_quick_add.py
  - tests/unit/workshop/test_workshop_viewmodel.py
  - tests/unit/workshop/test_workshop_viewmodel_public_api.py
- Heuristically untested symbols (1):
  - WorkshopViewModel._with_ship

### game/ui/utils/formatters.py (Tier 3: TIER_3_APPARENTLY_COVERED, 90 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/ui/panels/test_planet_report_panel.py
  - tests/unit/ui/utils/test_formatters.py

### game/ui/widgets/dropdown_helper.py (Tier 3: TIER_3_APPARENTLY_COVERED, 52 LOC, layer: ui)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/ui/widgets/test_dropdown_helper.py
