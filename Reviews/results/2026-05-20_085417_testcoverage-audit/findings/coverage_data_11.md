# Coverage Data — Shard 11

**Coverage source:** heuristic
**File count:** 53 | **LOC estimate:** 9820
**Tiers:** 0=11 1=1 2=29 3=12

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/ai/policy_manager.py (Tier 3: TIER_3_APPARENTLY_COVERED, 118 LOC, layer: ai)
- Total symbols: 8 | Heuristically tested: 8
- Candidate test files (7):
  - tests/unit/ai/test_ai.py
  - tests/unit/ai/test_ai_controller_edge_cases.py
  - tests/unit/ai/test_movement_and_ai.py
  - tests/unit/ai/test_policy_manager.py
  - tests/unit/builder/test_builder_ui_sync.py
  - tests/unit/core/test_isolation.py
  - tests/unit/ui/screens/test_battle_setup_logic.py

### game/ai/spatial_behaviors/column.py (Tier 2: TIER_2_PARTIAL, 55 LOC, layer: ai)
- Total symbols: 3 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py
- Heuristically untested symbols (1):
  - ColumnBehavior.__init__

### game/ai/spatial_behaviors/escort.py (Tier 2: TIER_2_PARTIAL, 50 LOC, layer: ai)
- Total symbols: 3 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py
- Heuristically untested symbols (1):
  - EscortBehavior.__init__

### game/core/input_actions.py (Tier 2: TIER_2_PARTIAL, 344 LOC, layer: core)
- Total symbols: 6 | Heuristically tested: 5
- Candidate test files (14):
  - tests/unit/core/test_input_actions.py
  - tests/unit/test_run_loop.py
  - tests/unit/ui/screens/test_build_queue_list_window.py
  - tests/unit/ui/screens/test_fleet_context_menu_dispatch.py
  - tests/unit/ui/screens/test_fleet_menu_items.py
  - tests/unit/ui/screens/test_keybindings_scene.py
  - tests/unit/ui/screens/test_strategy_fleet_command_router.py
  - tests/unit/ui/screens/test_strategy_input_handler_core.py
  - ... and 6 more
- Heuristically untested symbols (1):
  - KeyBinding._key_display_name

### game/core/validation.py (Tier 3: TIER_3_APPARENTLY_COVERED, 209 LOC, layer: core)
- Total symbols: 12 | Heuristically tested: 12
- Candidate test files (25):
  - tests/unit/core/test_bug_reproduction.py
  - tests/unit/core/test_validation.py
  - tests/unit/entities/test_bridge_requirement_removal.py
  - tests/unit/regressions/test_bug_regressions_2026_01.py
  - tests/unit/simulation/services/test_vehicle_design_service.py
  - tests/unit/strategy/engine/handlers/test_movement_handlers.py
  - tests/unit/strategy/engine/test_colonize_mission_handler.py
  - tests/unit/strategy/engine/test_command_registry_thirdparty.py
  - ... and 17 more

### game/research/data/research_tracker.py (Tier 2: TIER_2_PARTIAL, 293 LOC, layer: research)
- Total symbols: 21 | Heuristically tested: 19
- Candidate test files (6):
  - tests/unit/fixtures/test_strategy_entities.py
  - tests/unit/research/conftest.py
  - tests/unit/research/test_research_service.py
  - tests/unit/research/test_research_service_edge_cases.py
  - tests/unit/research/test_research_tracker.py
  - tests/unit/research/test_tech_requirement_negation.py
- Heuristically untested symbols (2):
  - ResearchTracker.__init__
  - ResearchTracker._clamp_allocations_to_budget

### game/simulation/combat/families/_beam_common.py (Tier 3: TIER_3_APPARENTLY_COVERED, 44 LOC, layer: simulation)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/simulation/combat/test_weapon_family_handlers.py

### game/simulation/combat/modifier_stack.py (Tier 3: TIER_3_APPARENTLY_COVERED, 74 LOC, layer: simulation)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (18):
  - tests/unit/combat_lab/services/test_ab_battle_runner.py
  - tests/unit/combat_lab/test_spec_compiler.py
  - tests/unit/simulation/battle_controller/test_outcome_emission.py
  - tests/unit/simulation/combat/test_fleet_aura_extended.py
  - tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py
  - tests/unit/simulation/combat/test_fleet_aura_unknown_stat_key_warning.py
  - tests/unit/simulation/combat/test_hit_log_modifier_trace.py
  - tests/unit/simulation/combat/test_modifier_stack.py
  - ... and 10 more

### game/simulation/combat/ram_target_resolver.py (Tier 2: TIER_2_PARTIAL, 226 LOC, layer: simulation)
- Total symbols: 10 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/simulation/combat/test_ram_target_resolver.py
- Heuristically untested symbols (6):
  - RamTargetResolver.clear_ram_target
  - RamTargetResolver._collect_warheads
  - RamTargetResolver._delivered_damage
  - RamTargetResolver._is_collision
  - RamTargetResolver._apply_damage
  - RamTargetResolver._resolve_collision

### game/simulation/combat/weapon_registry.py (Tier 2: TIER_2_PARTIAL, 95 LOC, layer: simulation)
- Total symbols: 8 | Heuristically tested: 6
- Candidate test files (2):
  - tests/unit/simulation/combat/test_weapon_registry.py
  - tests/unit/simulation/test_projectile_event_bus_wiring.py
- Heuristically untested symbols (2):
  - WeaponRegistry.__init__
  - WeaponRegistry.reset

### game/simulation/components/abilities/cargo.py (Tier 2: TIER_2_PARTIAL, 78 LOC, layer: simulation)
- Total symbols: 6 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/simulation/abilities/test_cargo_storage.py
- Heuristically untested symbols (1):
  - CargoStorage.__init__

### game/simulation/components/abilities/resources.py (Tier 2: TIER_2_PARTIAL, 234 LOC, layer: simulation)
- Total symbols: 23 | Heuristically tested: 22
- Candidate test files (7):
  - tests/unit/entities/test_components.py
  - tests/unit/modifiers/test_crew_resource_bindings.py
  - tests/unit/regressions/test_bug_regressions_2026_01.py
  - tests/unit/simulation/components/abilities/test_resource_consumption.py
  - tests/unit/simulation/validation/test_ship_validator_rules.py
  - tests/unit/ui/screens/builder/test_stat_getters.py
  - tests/unit/ui/screens/builder/test_stat_rows_dynamic.py
- Heuristically untested symbols (1):
  - ResourceConsumption._get_resource_registry

### game/simulation/entities/layer_data.py (Tier 3: TIER_3_APPARENTLY_COVERED, 112 LOC, layer: simulation)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (20):
  - tests/unit/builder/test_builder_drag_drop_real.py
  - tests/unit/builder/test_builder_logic.py
  - tests/unit/builder/test_builder_structure_features.py
  - tests/unit/builder/test_builder_warning_logic.py
  - tests/unit/builder/test_layer_targeted_actions.py
  - tests/unit/core/test_protocols_boundary.py
  - tests/unit/entities/test_bridge_requirement_removal.py
  - tests/unit/simulation/armor_mechanics/test_damage_mechanics.py
  - ... and 12 more

### game/simulation/entities/stat_contributors/accumulator.py (Tier 3: TIER_3_APPARENTLY_COVERED, 89 LOC, layer: simulation)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (4):
  - tests/unit/simulation/entities/stat_contributors/test_defense.py
  - tests/unit/simulation/entities/stat_contributors/test_movement.py
  - tests/unit/simulation/entities/stat_contributors/test_stat_accumulator.py
  - tests/unit/simulation/entities/test_stat_contributor_extension.py

### game/strategy/data/design_role_registry.py (Tier 2: TIER_2_PARTIAL, 98 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (3):
  - tests/unit/strategy/data/test_design_role_registry.py
  - tests/unit/strategy/data/test_design_role_registry_invalidation.py
  - tests/unit/strategy/data/test_design_role_registry_loader.py
- Heuristically untested symbols (1):
  - _build_default

### game/strategy/data/planet_atmosphere.py (Tier 3: TIER_3_APPARENTLY_COVERED, 177 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/strategy/planet_atmosphere/test_calculations.py
  - tests/unit/strategy/planet_atmosphere/test_generation.py

### game/strategy/data/planetary_facility.py (Tier 2: TIER_2_PARTIAL, 238 LOC, layer: strategy)
- Total symbols: 17 | Heuristically tested: 16
- Candidate test files (28):
  - tests/unit/core/test_protocols.py
  - tests/unit/quickstart/test_quickstart_builder.py
  - tests/unit/strategy/data/test_build_context.py
  - tests/unit/strategy/data/test_build_queue_source.py
  - tests/unit/strategy/data/test_colony_yard_registries.py
  - tests/unit/strategy/data/test_facility_activation.py
  - tests/unit/strategy/data/test_facility_construction_queue.py
  - tests/unit/strategy/data/test_facility_resource_tracking.py
  - ... and 20 more
- Heuristically untested symbols (1):
  - PlanetaryFacility._validate_resource_id

### game/strategy/engine/environmental_hazard_engine.py (Tier 2: TIER_2_PARTIAL, 250 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 6
- Candidate test files (4):
  - tests/unit/strategy/engine/test_engine_validation.py
  - tests/unit/strategy/engine/test_environmental_hazard_engine.py
  - tests/unit/strategy/engine/test_owned_sector_effects_filter.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
- Heuristically untested symbols (2):
  - EnvironmentalHazardEngine.__init__
  - EnvironmentalHazardEngine._get_ship_mutator

### game/strategy/engine/movement_phase_collaborator.py (Tier 2: TIER_2_PARTIAL, 194 LOC, layer: strategy)
- Total symbols: 7 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py
  - tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py
- Heuristically untested symbols (3):
  - MovementPhaseCollaborator._diff_moved_fleets
  - MovementPhaseCollaborator._mark_boosters_dirty
  - MovementPhaseCollaborator._resolve_minefields

### game/strategy/engine/order_handlers/transfer.py (Tier 2: TIER_2_PARTIAL, 252 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (3):
  - tests/unit/strategy/engine/order_handlers/test_transfer_handler.py
  - tests/unit/strategy/engine/test_pod_transfer.py
  - tests/unit/strategy/engine/test_staging_yard_operations.py
- Heuristically untested symbols (1):
  - TransferHandler.supported_order_types

### game/strategy/engine/order_processor.py (Tier 3: TIER_3_APPARENTLY_COVERED, 115 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 5
- Candidate test files (17):
  - tests/unit/strategy/engine/test_build_order_processor.py
  - tests/unit/strategy/engine/test_colonize_population.py
  - tests/unit/strategy/engine/test_engine_validation.py
  - tests/unit/strategy/engine/test_fleet_order_transfer.py
  - tests/unit/strategy/engine/test_fleet_transfer_extended.py
  - tests/unit/strategy/engine/test_issuer_execution_contract.py
  - tests/unit/strategy/engine/test_order_processor_colonize.py
  - tests/unit/strategy/engine/test_order_processor_fleet_merge.py
  - ... and 9 more

### game/strategy/generation/density/primitives/noise.py (Tier 3: TIER_3_APPARENTLY_COVERED, 117 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/strategy/generation/density/conftest.py
  - tests/unit/strategy/generation/density/test_noise.py

### game/strategy/generation/loaders/system_blueprints_loader.py (Tier 2: TIER_2_PARTIAL, 241 LOC, layer: strategy)
- Total symbols: 7 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/strategy/generation/test_system_blueprints.py
- Heuristically untested symbols (3):
  - SystemBlueprintsLoader.__init__
  - SystemBlueprintsLoader._validate_schema
  - SystemBlueprintsLoader._validate_blueprint

### game/strategy/interfaces/engines/components.py (Tier 0: TIER_0_NO_TESTS, 47 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - IComponentActivationEngine
  - IComponentActivationEngine.process_activation_tick

### game/strategy/services/ability_sources/warp_point.py (Tier 0: TIER_0_NO_TESTS, 64 LOC, layer: strategy)
- Total symbols: 9 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (9):
  - WarpPointAbilitySource
  - WarpPointAbilitySource.source_kind
  - WarpPointAbilitySource.source_label
  - WarpPointAbilitySource.source_id
  - WarpPointAbilitySource.owner_id
  - WarpPointAbilitySource.get_abilities
  - WarpPointAbilitySource.affects_hex
  - WarpPointAbilitySource.affects_system
  - WarpPointAbilitySource.get_activation_state

### game/strategy/services/deployment_zone_calculator.py (Tier 3: TIER_3_APPARENTLY_COVERED, 107 LOC, layer: strategy)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/strategy/services/test_deployment_zone_calculator.py

### game/strategy/services/planet_write_service.py (Tier 2: TIER_2_PARTIAL, 184 LOC, layer: strategy)
- Total symbols: 26 | Heuristically tested: 20
- Candidate test files (3):
  - tests/unit/strategy/engine/session/test_bootstrap.py
  - tests/unit/strategy/engine/test_game_session_from_dict.py
  - tests/unit/strategy/services/test_planet_write_service.py
- Heuristically untested symbols (6):
  - PlanetWriteService.add_staging_item
  - PlanetWriteService.pop_staging_item
  - PlanetWriteService.insert_order
  - PlanetWriteService.set_atmosphere_target
  - PlanetWriteService.set_gravity_target
  - PlanetWriteService.set_water_target

### game/strategy/services/task_group_suggester.py (Tier 3: TIER_3_APPARENTLY_COVERED, 125 LOC, layer: strategy)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/strategy/services/test_task_group_suggester.py

### game/strategy/validation/superweapon_validator.py (Tier 0: TIER_0_NO_TESTS, 270 LOC, layer: strategy)
- Total symbols: 11 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (11):
  - SuperweaponValidator
  - SuperweaponValidator.find_ship_with_ability
  - SuperweaponValidator._require_ability
  - SuperweaponValidator._require_at_star_system
  - SuperweaponValidator.validate_implode_planet
  - SuperweaponValidator._validate_star_targeted_superweapon
  - SuperweaponValidator.validate_stellerate_star
  - SuperweaponValidator.validate_open_warp_point
  - SuperweaponValidator.validate_close_warp_point
  - SuperweaponValidator.validate_create_dyson_sphere
  - SuperweaponValidator.validate_self_destruct

### game/ui/panels/design_report_panel.py (Tier 2: TIER_2_PARTIAL, 200 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 6
- Candidate test files (1):
  - tests/unit/ui/panels/test_design_report_panel.py
- Heuristically untested symbols (1):
  - DesignReportPanel.show_placeholder

### game/ui/panels/race_environment_panel.py (Tier 2: TIER_2_PARTIAL, 337 LOC, layer: ui)
- Total symbols: 15 | Heuristically tested: 11
- Candidate test files (2):
  - tests/unit/ui/screens/test_race_setup_screen.py
  - tests/unit/ui/test_race_environment_panel.py
- Heuristically untested symbols (4):
  - RaceEnvironmentPanel._create_content
  - RaceEnvironmentPanel._create_repro_and_happiness
  - RaceEnvironmentPanel._create_factor_rows
  - RaceEnvironmentPanel._on_row_change

### game/ui/screens/builder/layer_panel.py (Tier 2: TIER_2_PARTIAL, 536 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/test_structure_visibility.py
- Heuristically untested symbols (10):
  - LayerPanel.__init__
  - LayerPanel.handle_item_action
  - LayerPanel.handle_event
  - LayerPanel.update
  - LayerPanel.suppress_toggle
  - LayerPanel.draw
  - LayerPanel.can_accept_drop
  - LayerPanel.accept_drop
  - LayerPanel.get_target_layer_at
  - LayerPanel.get_range_selection

### game/ui/screens/builder/right_panel.py (Tier 2: TIER_2_PARTIAL, 437 LOC, layer: ui)
- Total symbols: 16 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/builder/test_builder_ui_sync.py
- Heuristically untested symbols (13):
  - BuilderRightPanel.__init__
  - BuilderRightPanel.on_registry_reloaded
  - BuilderRightPanel.on_ship_updated
  - BuilderRightPanel.setup_controls
  - BuilderRightPanel.setup_stats
  - BuilderRightPanel._sync_from_stats_panel
  - BuilderRightPanel.rebuild_stats
  - BuilderRightPanel.update_class_dropdown
  - BuilderRightPanel.update_vehicle_type_dropdown
  - BuilderRightPanel.update_role_dropdown
  - BuilderRightPanel._get_role_dropdown_data
  - BuilderRightPanel.update_dropdowns_for_data_reload
  - BuilderRightPanel.update_stats_display

### game/ui/screens/builder_selection.py (Tier 2: TIER_2_PARTIAL, 123 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/screens/test_builder_selection.py
- Heuristically untested symbols (1):
  - _is_component_like

### game/ui/screens/design_image_helper.py (Tier 2: TIER_2_PARTIAL, 218 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/screens/test_design_image_helper.py
- Heuristically untested symbols (2):
  - _load_portrait_thumbnail_uncached
  - _load_topdown_thumbnail_uncached

### game/ui/screens/fleet_report_view_model.py (Tier 2: TIER_2_PARTIAL, 182 LOC, layer: ui)
- Total symbols: 14 | Heuristically tested: 12
- Candidate test files (2):
  - tests/unit/ui/screens/test_fleet_report_filters.py
  - tests/unit/ui/test_fleet_list_view_model.py
- Heuristically untested symbols (2):
  - FleetListViewModel.__init__
  - FleetListViewModel._refresh

### game/ui/screens/fms_menu_callbacks.py (Tier 0: TIER_0_NO_TESTS, 136 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - build_planet_fms_callbacks
  - _dispatch
  - _first_ship_id_with
  - build_fleet_fms_callbacks
  - _dispatch

### game/ui/screens/galaxy_test/constants.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 32 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/ui/screens/test_galaxy_test_screen.py

### game/ui/screens/planet_list_presets.py (Tier 2: TIER_2_PARTIAL, 242 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 9
- Candidate test files (2):
  - tests/unit/ui/screens/test_planet_list_components.py
  - tests/unit/ui/screens/test_planet_list_filter_manager.py
- Heuristically untested symbols (3):
  - PresetManager.__init__
  - PresetManager.save_to_disk
  - PresetManager.get_all_presets

### game/ui/screens/setup_data_io.py (Tier 2: TIER_2_PARTIAL, 220 LOC, layer: ui)
- Total symbols: 8 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/builder/test_fleet_composition.py
  - tests/unit/ui/screens/test_setup_data_io.py
- Heuristically untested symbols (3):
  - serialize_team
  - find_design
  - load_team

### game/ui/screens/strategy_input_handler.py (Tier 2: TIER_2_PARTIAL, 216 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 8
- Candidate test files (7):
  - tests/unit/ui/screens/test_strategy_input_handler_core.py
  - tests/unit/ui/screens/test_strategy_input_handler_hidden_planet_list.py
  - tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py
  - tests/unit/ui/screens/test_strategy_input_handler_transfer.py
  - tests/unit/ui/screens/test_strategy_screen_composition.py
  - tests/unit/ui/screens/test_superweapon_input_modes.py
  - tests/unit/ui/screens/test_warp_hotkey.py
- Heuristically untested symbols (1):
  - StrategyInputHandler._handle_keydown

### game/ui/screens/strategy_modal_window.py (Tier 3: TIER_3_APPARENTLY_COVERED, 292 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 9
- Candidate test files (4):
  - tests/unit/ui/screens/test_event_log_row_pool_visibility.py
  - tests/unit/ui/screens/test_strategy_modal_esc_close.py
  - tests/unit/ui/screens/test_strategy_modal_hidden_input.py
  - tests/unit/ui/screens/test_strategy_modal_window.py

### game/ui/screens/strategy_screen_assets.py (Tier 0: TIER_0_NO_TESTS, 88 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - focus_on_player_home
  - load_assets
  - get_object_asset

### game/ui/screens/strategy_screen_order_editing.py (Tier 0: TIER_0_NO_TESTS, 93 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - on_edit_order
  - start_edit_move
  - complete_edit_move
  - start_edit_transfer

### game/ui/screens/strategy_screen_selection.py (Tier 0: TIER_0_NO_TESTS, 99 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - on_ui_selection
  - on_colonize_click
  - on_colonize_planet_selected
  - request_colonize_order

### game/ui/screens/strategy_windows/dispatch.py (Tier 0: TIER_0_NO_TESTS, 129 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (7):
  - UICallbackDispatcher
  - UICallbackDispatcher.__init__
  - UICallbackDispatcher.process
  - ConfirmationDialogController
  - ConfirmationDialogController.__init__
  - ConfirmationDialogController.show
  - ConfirmationDialogController.process_event

### game/ui/screens/strategy_windows/empire_panel_ctrl.py (Tier 0: TIER_0_NO_TESTS, 97 LOC, layer: ui)
- Total symbols: 8 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (8):
  - EmpirePanelRegistrar
  - EmpirePanelRegistrar.__init__
  - EmpirePanelRegistrar.open
  - EmpirePanelRegistrar._on_closed
  - SettingsRegistrar
  - SettingsRegistrar.__init__
  - SettingsRegistrar.open
  - SettingsRegistrar._on_closed

### game/ui/screens/test_lab/dialogs.py (Tier 0: TIER_0_NO_TESTS, 272 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (12):
  - JSONPopup
  - JSONPopup.__init__
  - JSONPopup.close
  - JSONPopup.handle_event
  - JSONPopup.draw
  - ConfirmationDialog
  - ConfirmationDialog.__init__
  - ConfirmationDialog._handle_confirm
  - ConfirmationDialog._handle_cancel
  - ConfirmationDialog._kill_buttons
  - ConfirmationDialog.handle_event
  - ConfirmationDialog.draw

### game/ui/screens/test_lab/results_panel.py (Tier 0: TIER_0_NO_TESTS, 266 LOC, layer: ui)
- Total symbols: 11 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (11):
  - ResultsPanel
  - ResultsPanel.__init__
  - ResultsPanel.set_details_panel
  - ResultsPanel.set_test
  - ResultsPanel._recalculate_scroll
  - ResultsPanel.handle_event
  - ResultsPanel.update
  - ResultsPanel.draw
  - ResultsPanel._draw_header
  - ResultsPanel._is_card_visible
  - ResultsPanel._draw_scrollbar

### game/ui/screens/workshop_data_loader.py (Tier 2: TIER_2_PARTIAL, 229 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 8
- Candidate test files (3):
  - tests/unit/ui/screens/test_workshop_data_loader.py
  - tests/unit/ui/screens/test_workshop_data_reloader.py
  - tests/unit/workshop/test_workshop_data_loader.py
- Heuristically untested symbols (1):
  - WorkshopDataLoader._get_default_class

### game/ui/screens/workshop_screen.py (Tier 2: TIER_2_PARTIAL, 645 LOC, layer: ui)
- Total symbols: 31 | Heuristically tested: 24
- Candidate test files (9):
  - tests/unit/builder/test_builder_drag_drop_real.py
  - tests/unit/builder/test_builder_improvements.py
  - tests/unit/builder/test_builder_structure_features.py
  - tests/unit/builder/test_builder_warning_logic.py
  - tests/unit/builder/test_multi_selection_logic.py
  - tests/unit/builder/test_selection_refinements.py
  - tests/unit/ui/conftest.py
  - tests/unit/ui/screens/test_workshop_screen.py
  - ... and 1 more
- Heuristically untested symbols (3):
  - DesignWorkshopScreen.rebuild_modifier_ui
  - DesignWorkshopScreen.show_clear_confirmation
  - DesignWorkshopScreen.on_select_target_pressed

### game/ui/services/component_service.py (Tier 2: TIER_2_PARTIAL, 132 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/ui/services/test_component_service.py
- Heuristically untested symbols (2):
  - ComponentService.__init__
  - ComponentService._get_provider

### game/ui/services/design_loader_adapter.py (Tier 2: TIER_2_PARTIAL, 99 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/services/test_design_loader_adapter.py
- Heuristically untested symbols (1):
  - DesignLoaderAdapter.__init__
