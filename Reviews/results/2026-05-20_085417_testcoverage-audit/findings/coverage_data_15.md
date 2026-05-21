# Coverage Data — Shard 15

**Coverage source:** heuristic
**File count:** 45 | **LOC estimate:** 9457
**Tiers:** 0=11 1=1 2=26 3=7

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/ai/target_evaluator.py (Tier 2: TIER_2_PARTIAL, 331 LOC, layer: ai)
- Total symbols: 10 | Heuristically tested: 4
- Candidate test files (6):
  - tests/unit/ai/target_evaluator/test_capabilities_cache.py
  - tests/unit/ai/target_evaluator/test_projectile_candidate_guards.py
  - tests/unit/ai/test_ai_capabilities_cache.py
  - tests/unit/ai/test_target_evaluator_edge_cases.py
  - tests/unit/ai/test_target_evaluator_rules.py
  - tests/unit/ai/test_targeting_rules.py
- Heuristically untested symbols (6):
  - TargetEvaluator._eval_distance_rule
  - TargetEvaluator._eval_mass_rule
  - TargetEvaluator._eval_damage_rule
  - TargetEvaluator._eval_least_armor_rule
  - TargetEvaluator._eval_pdc_arc_rule
  - TargetEvaluator._eval_capability_rule

### game/assets/component_derivatives.py (Tier 2: TIER_2_PARTIAL, 182 LOC, layer: assets)
- Total symbols: 9 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/assets/test_component_derivatives.py
- Heuristically untested symbols (6):
  - ComponentDerivativeResult
  - _read_manifest
  - _write_manifest
  - _source_fast_path_hit
  - _has_expected_size
  - _write_derivative

### game/context.py (Tier 2: TIER_2_PARTIAL, 241 LOC, layer: game_root)
- Total symbols: 7 | Heuristically tested: 5
- Candidate test files (4):
  - tests/unit/core/test_application_context.py
  - tests/unit/strategy/services/test_planet_habitability_service.py
  - tests/unit/test_app_bootstrap_invariants.py
  - tests/unit/test_context_habitability_accessors.py
- Heuristically untested symbols (2):
  - _install_default_habitability_service
  - ApplicationContext.__init__

### game/core/combat_types.py (Tier 3: TIER_3_APPARENTLY_COVERED, 20 LOC, layer: core)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (3):
  - tests/unit/core/test_combat_types.py
  - tests/unit/simulation/combat/test_hit_log_modifier_trace.py
  - tests/unit/simulation/combat/test_hit_log_recorder.py

### game/core/registry.py (Tier 2: TIER_2_PARTIAL, 483 LOC, layer: core)
- Total symbols: 37 | Heuristically tested: 35
- Candidate test files (72):
  - tests/unit/ai/test_ai.py
  - tests/unit/ai/test_ai_protocols.py
  - tests/unit/ai/test_movement_and_ai.py
  - tests/unit/builder/test_builder_logic.py
  - tests/unit/core/registry/conftest.py
  - tests/unit/core/registry/test_registry_features.py
  - tests/unit/core/registry/test_registry_operations.py
  - tests/unit/core/registry/test_singleton_and_thread.py
  - ... and 64 more
- Heuristically untested symbols (2):
  - RegistryManager.unfrozen
  - freeze_registry

### game/simulation/combat/ability_stat_registry.py (Tier 2: TIER_2_PARTIAL, 237 LOC, layer: simulation)
- Total symbols: 4 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/simulation/combat/test_ability_stat_registry.py
  - tests/unit/ui/screens/battle_setup/test_spec_compiler.py
- Heuristically untested symbols (2):
  - _extract_value
  - _route_team_ids

### game/simulation/managers/battle_state_manager.py (Tier 3: TIER_3_APPARENTLY_COVERED, 134 LOC, layer: simulation)
- Total symbols: 5 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/simulation/managers/test_battle_state_manager.py

### game/simulation/systems/tech_preset_loader.py (Tier 3: TIER_3_APPARENTLY_COVERED, 203 LOC, layer: simulation)
- Total symbols: 7 | Heuristically tested: 7
- Candidate test files (1):
  - tests/unit/simulation/systems/test_tech_preset_loader.py

### game/strategy/combat/battle_assembly.py (Tier 2: TIER_2_PARTIAL, 353 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/strategy/combat/test_battle_assembly.py
  - tests/unit/strategy/combat/test_battle_assembly_third_party_mines.py
- Heuristically untested symbols (3):
  - _boundary_to_box
  - StrategyBattleAssembler.__init__
  - StrategyBattleAssembler.assemble

### game/strategy/data/carried_vehicle_deploy.py (Tier 0: TIER_0_NO_TESTS, 116 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - carried_vehicle_to_ship_instance
  - carried_vehicle_to_ship_instance_safe

### game/strategy/data/orbital_generation_config.py (Tier 2: TIER_2_PARTIAL, 195 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/strategy/data/test_orbital_generation_config.py
- Heuristically untested symbols (3):
  - OrbitalGenerationConfig.__init__
  - OrbitalGenerationConfig._load_from_json
  - OrbitalGenerationConfig._use_defaults

### game/strategy/data/ship_display_formatter.py (Tier 2: TIER_2_PARTIAL, 131 LOC, layer: strategy)
- Total symbols: 7 | Heuristically tested: 6
- Candidate test files (1):
  - tests/unit/strategy/test_ship_display_formatter.py
- Heuristically untested symbols (1):
  - ShipDisplayFormatter.__init__

### game/strategy/data/squadron.py (Tier 2: TIER_2_PARTIAL, 102 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 7
- Candidate test files (6):
  - tests/unit/strategy/data/test_fleet_hierarchy.py
  - tests/unit/strategy/data/test_fleet_hierarchy_integration.py
  - tests/unit/strategy/data/test_group_policies.py
  - tests/unit/strategy/data/test_squadron_characterization.py
  - tests/unit/strategy/facade/test_fleet_hierarchy_dto.py
  - tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py
- Heuristically untested symbols (1):
  - Squadron.__init__

### game/strategy/engine/handlers/movement.py (Tier 2: TIER_2_PARTIAL, 284 LOC, layer: strategy)
- Total symbols: 11 | Heuristically tested: 10
- Candidate test files (1):
  - tests/unit/strategy/engine/handlers/test_movement_handlers.py
- Heuristically untested symbols (1):
  - register

### game/strategy/engine/happiness_engine.py (Tier 2: TIER_2_PARTIAL, 141 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/strategy/engine/test_happiness_engine.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
- Heuristically untested symbols (2):
  - HappinessEngine._validate_tick_inputs
  - HappinessEngine._process_colony

### game/strategy/facade/__init__.py (Tier 0: TIER_0_NO_TESTS, 8 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/strategy/facade/dto/build_queue_dto.py (Tier 3: TIER_3_APPARENTLY_COVERED, 42 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/strategy/facade/dto/test_build_queue_dto.py

### game/strategy/facade/dto/fleet_dto.py (Tier 2: TIER_2_PARTIAL, 332 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 5
- Candidate test files (5):
  - tests/unit/strategy/facade/test_fleet_dto.py
  - tests/unit/strategy/facade/test_fleet_dto_build.py
  - tests/unit/strategy/facade/test_fleet_dto_capabilities.py
  - tests/unit/strategy/facade/test_population_dtos.py
  - tests/unit/strategy/services/test_cargo_transfer_service.py
- Heuristically untested symbols (3):
  - FleetInfo._aggregate_carried_vehicles_by_type
  - FleetInfo._sum_vehicle_bay_used
  - FleetInfo._sum_vehicle_bay_max

### game/strategy/facade/grouped_namespaces.py (Tier 2: TIER_2_PARTIAL, 406 LOC, layer: strategy)
- Total symbols: 53 | Heuristically tested: 8
- Candidate test files (1):
  - tests/unit/strategy/facade/test_container_snapshots.py
- Heuristically untested symbols (45):
  - FacadeCommands
  - FacadeCommands.__init__
  - FacadeCommands.__getattr__
  - FacadeCommands.__dir__
  - FacadeFleetQueries.__init__
  - FacadeFleetQueries.get
  - FacadeFleetQueries.at_hex
  - FacadeFleetQueries.path_preview
  - FacadeFleetQueries.path_projection
  - FacadeFleetQueries.remaining_pods
  - FacadePlanetQueries.__init__
  - FacadePlanetQueries.get
  - FacadePlanetQueries.at_hex
  - FacadeSystemQueries
  - FacadeSystemQueries.__init__
  - ... and 30 more

### game/strategy/facade/slices/empire_slice.py (Tier 2: TIER_2_PARTIAL, 97 LOC, layer: strategy)
- Total symbols: 9 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/strategy/facade/slices/test_empire_slice.py
- Heuristically untested symbols (5):
  - EmpireSlice.__init__
  - EmpireSlice.get_all_empires
  - EmpireSlice.get_empire
  - EmpireSlice.get_empire_colonies
  - EmpireSlice.get_empire_fleets

### game/strategy/generation/density/density_map.py (Tier 2: TIER_2_PARTIAL, 241 LOC, layer: strategy)
- Total symbols: 7 | Heuristically tested: 6
- Candidate test files (4):
  - tests/unit/strategy/generation/density/conftest.py
  - tests/unit/strategy/generation/density/test_density_map.py
  - tests/unit/strategy/generation/density/test_layout_loader.py
  - tests/unit/strategy/generation/test_placement_strategies.py
- Heuristically untested symbols (1):
  - DensityMap.__len__

### game/strategy/generation/density/primitives/linear.py (Tier 3: TIER_3_APPARENTLY_COVERED, 86 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/strategy/generation/density/conftest.py
  - tests/unit/strategy/generation/density/test_linear.py

### game/strategy/services/action_time_resolver.py (Tier 2: TIER_2_PARTIAL, 243 LOC, layer: strategy)
- Total symbols: 7 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/strategy/services/test_action_time_resolver.py
- Heuristically untested symbols (4):
  - _activate_time_field
  - ActionTimeResolver._find_fleet_ability_time
  - ActionTimeResolver._find_planet_ability_time
  - _get_abilities

### game/strategy/services/component_abilities.py (Tier 2: TIER_2_PARTIAL, 403 LOC, layer: strategy)
- Total symbols: 13 | Heuristically tested: 10
- Candidate test files (2):
  - tests/unit/strategy/services/test_component_abilities.py
  - tests/unit/ui/screens/test_fleet_report_filters.py
- Heuristically untested symbols (3):
  - _get_component_registry
  - get_component_type
  - get_component_threshold

### game/ui/screens/battle_results_screen.py (Tier 2: TIER_2_PARTIAL, 291 LOC, layer: ui)
- Total symbols: 13 | Heuristically tested: 9
- Candidate test files (1):
  - tests/unit/ui/screens/test_battle_results_screen.py
- Heuristically untested symbols (4):
  - BattleResultsScreen.__init__
  - BattleResultsScreen._draw_header
  - BattleResultsScreen._draw_team_column
  - BattleResultsScreen._draw_footer

### game/ui/screens/battle_setup/renderer.py (Tier 2: TIER_2_PARTIAL, 86 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/screens/battle_setup/test_renderer.py
- Heuristically untested symbols (1):
  - BattleSetupRenderer._build_bottom_bar

### game/ui/screens/builder/modifier_utils.py (Tier 3: TIER_3_APPARENTLY_COVERED, 20 LOC, layer: ui)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/ui/screens/builder/test_modifier_utils.py

### game/ui/screens/empire_build_queue_data_source.py (Tier 2: TIER_2_PARTIAL, 114 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/ui/screens/test_build_queue_data_source.py
- Heuristically untested symbols (2):
  - BuildQueueDataSource.__init__
  - BuildQueueDataSource._get_column_value

### game/ui/screens/galaxy_test/system_mode.py (Tier 0: TIER_0_NO_TESTS, 576 LOC, layer: ui)
- Total symbols: 13 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (13):
  - SystemModeHelper
  - SystemModeHelper.__init__
  - SystemModeHelper.create_ui
  - SystemModeHelper._get_blueprint_options
  - SystemModeHelper.generate
  - SystemModeHelper._center_camera
  - SystemModeHelper.handle_click
  - SystemModeHelper._update_inspector_panel
  - SystemModeHelper._format_star_info
  - SystemModeHelper._format_planet_info
  - SystemModeHelper._get_classification_reason
  - SystemModeHelper.draw
  - SystemModeHelper.update_fps_display

### game/ui/screens/orders_window.py (Tier 2: TIER_2_PARTIAL, 463 LOC, layer: ui)
- Total symbols: 20 | Heuristically tested: 11
- Candidate test files (3):
  - tests/unit/ui/screens/test_fleet_orders_refresh.py
  - tests/unit/ui/screens/test_orders_window.py
  - tests/unit/ui/screens/test_sub_window_hotkeys.py
- Heuristically untested symbols (9):
  - OrdersListRenderer
  - OrdersListRenderer.render
  - OrdersWindowUiBuilder
  - OrdersWindowUiBuilder.build
  - OrdersWindow.rebuild_list
  - OrdersWindow.process_event
  - OrdersWindow.move_order
  - OrdersWindow.edit_order
  - OrdersWindow.delete_order

### game/ui/screens/planet_list_window.py (Tier 2: TIER_2_PARTIAL, 453 LOC, layer: ui)
- Total symbols: 24 | Heuristically tested: 13
- Candidate test files (7):
  - tests/unit/ui/screens/test_event_log_row_pool_visibility.py
  - tests/unit/ui/screens/test_planet_list_components.py
  - tests/unit/ui/screens/test_planet_list_filter_snapshot.py
  - tests/unit/ui/screens/test_planet_list_window.py
  - tests/unit/ui/screens/test_planet_list_window_reuse.py
  - tests/unit/ui/screens/test_strategy_modal_esc_close.py
  - tests/unit/ui/screens/test_strategy_modal_hidden_input.py
- Heuristically untested symbols (9):
  - PlanetListWindow.filter_effects
  - PlanetListWindow.filter_effects
  - PlanetListWindow.filter_ranges
  - PlanetListWindow.filter_ranges
  - PlanetListWindow._capture_current_state
  - PlanetListWindow._apply_state
  - PlanetListWindow.process_event
  - PlanetListWindow._super_process_event
  - PlanetListWindow.set_dimensions

### game/ui/screens/race_setup/ui_builder.py (Tier 0: TIER_0_NO_TESTS, 42 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - RaceSetupUiBuilder
  - RaceSetupUiBuilder.build

### game/ui/screens/radiation_shield_editor.py (Tier 0: TIER_0_NO_TESTS, 231 LOC, layer: ui)
- Total symbols: 8 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (8):
  - RadiationShieldEditor
  - RadiationShieldEditor.__init__
  - RadiationShieldEditor._build_ui
  - RadiationShieldEditor.update
  - RadiationShieldEditor._button_handlers
  - RadiationShieldEditor._on_apply
  - RadiationShieldEditor._set_auto
  - RadiationShieldEditor._clear_target

### game/ui/screens/star_list_presets.py (Tier 2: TIER_2_PARTIAL, 127 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/ui/screens/test_star_list_window.py
- Heuristically untested symbols (2):
  - capture_star_list_state
  - apply_star_list_state

### game/ui/screens/strategy_camera_nav.py (Tier 2: TIER_2_PARTIAL, 232 LOC, layer: ui)
- Total symbols: 13 | Heuristically tested: 12
- Candidate test files (2):
  - tests/unit/ui/screens/test_camera_navigator.py
  - tests/unit/ui/screens/test_strategy_screen_composition.py
- Heuristically untested symbols (1):
  - CameraNavigator._resolve_global_hex

### game/ui/screens/strategy_menu_panel.py (Tier 3: TIER_3_APPARENTLY_COVERED, 103 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/ui/screens/test_strategy_menu_panel.py

### game/ui/screens/strategy_screen_lifecycle.py (Tier 0: TIER_0_NO_TESTS, 175 LOC, layer: ui)
- Total symbols: 8 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (8):
  - on_design_click
  - on_menu_option
  - show_load_game_dialog
  - on_load_selected
  - confirm_quit_to_menu
  - handle_quit_confirmed
  - show_coming_soon
  - on_save_game_click

### game/ui/screens/strategy_windows/move_choice_dialog.py (Tier 0: TIER_0_NO_TESTS, 94 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - MoveChoiceWindow
  - MoveChoiceDialog
  - MoveChoiceDialog.__init__
  - MoveChoiceDialog.show

### game/ui/screens/test_lab/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 22 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (6):
  - tests/unit/test_lab/test_data_paths.py
  - tests/unit/test_lab/test_visual_run.py
  - tests/unit/ui/screens/test_lab/renderer/test_metadata_panel.py
  - tests/unit/ui/screens/test_lab/renderer/test_tag_filter_panel.py
  - tests/unit/ui/screens/test_lab/test_dialogs.py
  - tests/unit/ui/test_scene_protocol.py

### game/ui/screens/test_lab/component_dropdown.py (Tier 0: TIER_0_NO_TESTS, 157 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (6):
  - ComponentDropdown
  - ComponentDropdown.__init__
  - ComponentDropdown.handle_click
  - ComponentDropdown.handle_hover
  - ComponentDropdown.get_selected_component_id
  - ComponentDropdown.draw

### game/ui/screens/test_lab/details/validation.py (Tier 0: TIER_0_NO_TESTS, 253 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - _phase_color
  - draw_validation_results
  - draw_single_validation
  - draw_numeric_difference

### game/ui/screens/test_lab/renderer/_draw_helpers.py (Tier 0: TIER_0_NO_TESTS, 222 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (6):
  - draw_section
  - draw_section_wrapped
  - draw_bullet_list
  - draw_wrapped_text
  - draw_validation_flag
  - draw_output_log

### game/ui/screens/test_lab/viewmodel.py (Tier 2: TIER_2_PARTIAL, 389 LOC, layer: ui)
- Total symbols: 47 | Heuristically tested: 30
- Candidate test files (2):
  - tests/unit/test_lab/test_data_paths.py
  - tests/unit/test_lab/test_viewmodel.py
- Heuristically untested symbols (12):
  - TestLabViewModel.run_baseline_btn_rect
  - TestLabViewModel.run_baseline_btn_rect
  - TestLabViewModel.tag_filter_rects
  - TestLabViewModel.tag_filter_rects
  - TestLabViewModel.tag_clear_rect
  - TestLabViewModel.tag_clear_rect
  - TestLabViewModel.seed_mode_rects
  - TestLabViewModel.seed_mode_rects
  - TestLabViewModel.seed_input_rect
  - TestLabViewModel.seed_input_rect
  - TestLabViewModel.test_list_panel_rect
  - TestLabViewModel.test_list_panel_rect

### game/ui/screens/transfer_container_rows.py (Tier 0: TIER_0_NO_TESTS, 142 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - build_row_data_from_containers
  - _aggregate_quantities_by_cargo_key

### game/ui/screens/workshop_viewmodel_layer_ops.py (Tier 2: TIER_2_PARTIAL, 254 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 6
- Candidate test files (1):
  - tests/unit/ui/screens/test_workshop_viewmodel_layer_ops.py
- Heuristically untested symbols (1):
  - WorkshopLayerOps.quick_add_component
