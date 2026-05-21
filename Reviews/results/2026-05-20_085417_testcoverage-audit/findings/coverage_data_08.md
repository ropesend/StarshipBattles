# Coverage Data — Shard 08

**Coverage source:** heuristic
**File count:** 44 | **LOC estimate:** 9593
**Tiers:** 0=13 1=5 2=17 3=9

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/ai/interfaces/controllable.py (Tier 3: TIER_3_APPARENTLY_COVERED, 393 LOC, layer: ai)
- Total symbols: 66 | Heuristically tested: 66
- Candidate test files (9):
  - tests/unit/ai/test_ai.py
  - tests/unit/ai/test_ai_controller_edge_cases.py
  - tests/unit/ai/test_ai_controller_interface.py
  - tests/unit/ai/test_ai_controller_unit.py
  - tests/unit/ai/test_carrier_controller.py
  - tests/unit/ai/test_controllable_adapter.py
  - tests/unit/ai/test_controllable_adapter_edge_cases.py
  - tests/unit/ai/test_movement_and_ai.py
  - ... and 1 more

### game/ai/spatial_behaviors/base.py (Tier 3: TIER_3_APPARENTLY_COVERED, 95 LOC, layer: ai)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/ai/spatial_behaviors/test_anti_clumping.py
  - tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py

### game/ai/spatial_behaviors/free_maneuver.py (Tier 3: TIER_3_APPARENTLY_COVERED, 25 LOC, layer: ai)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py

### game/simulation/battle_controller.py (Tier 2: TIER_2_PARTIAL, 831 LOC, layer: simulation)
- Total symbols: 31 | Heuristically tested: 25
- Candidate test files (7):
  - tests/unit/simulation/battle_controller/conftest.py
  - tests/unit/simulation/battle_controller/test_execution.py
  - tests/unit/simulation/battle_controller/test_initialization.py
  - tests/unit/simulation/battle_controller/test_mechanics.py
  - tests/unit/simulation/battle_controller/test_outcome_emission.py
  - tests/unit/simulation/battle_controller/test_start_from_spec.py
  - tests/unit/simulation/battle_controller/test_state.py
- Heuristically untested symbols (6):
  - BattleController.__init__
  - BattleController._retreat_allowed
  - BattleController._reinforcements_allowed
  - BattleController.get_tick_count
  - BattleController.set_on_ship_escaped
  - BattleController.reset

### game/simulation/components/abilities/container.py (Tier 2: TIER_2_PARTIAL, 216 LOC, layer: simulation)
- Total symbols: 8 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/simulation/components/abilities/test_container_ability.py
- Heuristically untested symbols (3):
  - ContainerAbility._parse_attrs
  - ContainerAbility.recalculate
  - ContainerAbility.get_ui_rows

### game/simulation/entities/stat_contributors/movement.py (Tier 0: TIER_0_NO_TESTS, 73 LOC, layer: simulation)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - contribute_combat_propulsion
  - contribute_strategic_movement
  - contribute_warp_jump
  - contribute_maneuvering_thruster

### game/simulation/entities/stat_contributors/registry.py (Tier 2: TIER_2_PARTIAL, 570 LOC, layer: simulation)
- Total symbols: 28 | Heuristically tested: 15
- Candidate test files (4):
  - tests/unit/simulation/entities/stat_contributors/test_command.py
  - tests/unit/simulation/entities/stat_contributors/test_registry.py
  - tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py
  - tests/unit/simulation/entities/test_stat_contributor_extension.py
- Heuristically untested symbols (13):
  - CrewPriorityEntry
  - StatContributorEntry
  - _StatContributorRegistry
  - _StatContributorRegistry.__init__
  - _StatContributorRegistry.add_default
  - _StatContributorRegistry.add_replacement
  - _StatContributorRegistry.add_appended
  - _StatContributorRegistry.remove_handle
  - _StatContributorRegistry.get
  - _StatContributorRegistry.__contains__
  - _StatContributorRegistry.__len__
  - _next_entry_id
  - _seed_builtin_contributors

### game/simulation/systems/battle_setup.py (Tier 0: TIER_0_NO_TESTS, 141 LOC, layer: simulation)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - initialize_start_state
  - start_teams
  - log_initial_status

### game/strategy/data/planet_serde.py (Tier 0: TIER_0_NO_TESTS, 256 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - _normalize_to_typed
  - planet_to_dict
  - planet_from_dict_kwargs
  - _deserialize_planet_orders

### game/strategy/engine/handlers/fms_shared.py (Tier 0: TIER_0_NO_TESTS, 114 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - check_issuer_invariant
  - count_matching_bay
  - count_matching_yard
  - resolve_requested

### game/strategy/engine/harvesting_engine.py (Tier 2: TIER_2_PARTIAL, 585 LOC, layer: strategy)
- Total symbols: 27 | Heuristically tested: 10
- Candidate test files (9):
  - tests/unit/strategy/engine/test_engine_validation.py
  - tests/unit/strategy/engine/test_harvesting_engine.py
  - tests/unit/strategy/engine/test_harvesting_engine_caches.py
  - tests/unit/strategy/engine/test_harvesting_engine_habitability.py
  - tests/unit/strategy/engine/test_harvesting_size_scaling.py
  - tests/unit/strategy/production_engine/test_habitability.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
  - tests/unit/ui/panels/test_planet_report_panel.py
  - ... and 1 more
- Heuristically untested symbols (17):
  - _get_ability_info
  - _get_ability_data_from_registry
  - get_harvester_from_registry
  - HarvestingEngine._get_planet_mutator
  - HarvestingEngine._get_empire_mutator
  - HarvestingEngine._refresh_storage_if_needed
  - HarvestingEngine._aggregate_empire_storage
  - HarvestingEngine._collect_staging_capacity
  - HarvestingEngine._get_staging_info
  - HarvestingEngine._collect_storage_from_facility
  - HarvestingEngine._get_storage_info
  - HarvestingEngine._get_storage_from_registry
  - HarvestingEngine._process_empire
  - HarvestingEngine._process_colony
  - HarvestingEngine._process_facility
  - ... and 2 more

### game/strategy/engine/order_handlers/base.py (Tier 2: TIER_2_PARTIAL, 220 LOC, layer: strategy)
- Total symbols: 16 | Heuristically tested: 10
- Candidate test files (2):
  - tests/unit/strategy/engine/order_handlers/test_base.py
  - tests/unit/strategy/engine/test_issuer_execution_contract.py
- Heuristically untested symbols (6):
  - IOrderHandler.execute_action_order
  - BaseOrderHandler.__init__
  - BaseOrderHandler._get_planet_mutator
  - BaseOrderHandler._get_ship_mutator
  - OrderHandlerRegistry.__init__
  - OrderHandlerRegistry.__contains__

### game/strategy/engine/quality_engine.py (Tier 2: TIER_2_PARTIAL, 83 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 3
- Candidate test files (3):
  - tests/unit/strategy/engine/test_engine_validation.py
  - tests/unit/strategy/engine/test_quality_engine.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
- Heuristically untested symbols (2):
  - QualityEngine.__init__
  - QualityEngine._process_colony

### game/strategy/engine/session/graph_restoration.py (Tier 0: TIER_0_NO_TESTS, 79 LOC, layer: strategy)
- Total symbols: 1 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (1):
  - restore_graph_wiring

### game/strategy/engine/superweapon_handlers/create_dyson_sphere.py (Tier 0: TIER_0_NO_TESTS, 124 LOC, layer: strategy)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - process_create_dyson_sphere
  - _precheck
  - _effect

### game/strategy/facade/dto/empire_dto.py (Tier 3: TIER_3_APPARENTLY_COVERED, 120 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 6
- Candidate test files (1):
  - tests/unit/strategy/facade/test_empire_dto.py

### game/strategy/facade/slices/event_slice.py (Tier 0: TIER_0_NO_TESTS, 96 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (8):
  - EventSlice
  - EventSlice.__init__
  - EventSlice.get_human_player_ids
  - EventSlice.get_turn_number
  - EventSlice.get_save_path
  - EventSlice.get_turn_events
  - EventSlice.get_all_events
  - EventSlice.get_events_by_category

### game/strategy/services/ability_sources/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 42 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (10):
  - tests/unit/strategy/data/test_galaxy_warp_generator.py
  - tests/unit/strategy/services/ability_sources/test_facility.py
  - tests/unit/strategy/services/ability_sources/test_fleet.py
  - tests/unit/strategy/services/ability_sources/test_intrinsic_roll.py
  - tests/unit/strategy/services/ability_sources/test_labels.py
  - tests/unit/strategy/services/ability_sources/test_planet_intrinsic.py
  - tests/unit/strategy/services/ability_sources/test_star.py
  - tests/unit/strategy/services/ability_sources/test_storm.py
  - ... and 2 more

### game/strategy/services/fleet_path_projection.py (Tier 0: TIER_0_NO_TESTS, 201 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - project_path_inner
  - consume_ticks
  - get_action_time_for_projection
  - project_action_order
  - resolve_path_for_order

### game/strategy/services/fleet_speed_calculator.py (Tier 3: TIER_3_APPARENTLY_COVERED, 188 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 6
- Candidate test files (1):
  - tests/unit/strategy/test_fleet_speed_calculator.py

### game/strategy/services/replay_ship_builder.py (Tier 2: TIER_2_PARTIAL, 87 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/strategy/services/test_replay_ship_builder_registry_contract.py
- Heuristically untested symbols (1):
  - _builder

### game/strategy/systems/race_randomizer.py (Tier 3: TIER_3_APPARENTLY_COVERED, 446 LOC, layer: strategy)
- Total symbols: 12 | Heuristically tested: 12
- Candidate test files (2):
  - tests/unit/strategy/systems/test_race_randomizer_helpers.py
  - tests/unit/strategy/test_race_randomizer.py

### game/ui/components/table/header.py (Tier 2: TIER_2_PARTIAL, 146 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/ui/components/table/test_header.py
- Heuristically untested symbols (1):
  - TableHeader.__init__

### game/ui/components/table/selection.py (Tier 3: TIER_3_APPARENTLY_COVERED, 138 LOC, layer: ui)
- Total symbols: 22 | Heuristically tested: 22
- Candidate test files (2):
  - tests/unit/ui/components/table/test_selection.py
  - tests/unit/ui/components/table/test_virtual_table.py

### game/ui/filters/filter_state_manager.py (Tier 2: TIER_2_PARTIAL, 54 LOC, layer: ui)
- Total symbols: 8 | Heuristically tested: 7
- Candidate test files (2):
  - tests/unit/ui/filters/test_filter_state_manager.py
  - tests/unit/ui/screens/test_planet_list_filter_manager.py
- Heuristically untested symbols (1):
  - FilterStateManager.__init__

### game/ui/panels/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 0 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (12):
  - tests/unit/ui/panels/test_base_gallery.py
  - tests/unit/ui/panels/test_builder_widgets.py
  - tests/unit/ui/panels/test_component_modifier_grid_panel.py
  - tests/unit/ui/panels/test_design_report_panel.py
  - tests/unit/ui/test_battle_panels.py
  - tests/unit/ui/test_battle_panels_characterization.py
  - tests/unit/ui/test_battle_panels_extended.py
  - tests/unit/ui/test_race_environment_panel.py
  - ... and 4 more

### game/ui/panels/battle_panels.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 564 LOC, layer: ui)
- Total symbols: 35 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/ui/conftest.py
- Heuristically untested symbols (35):
  - BattlePanel
  - BattlePanel.__init__
  - BattlePanel.draw
  - BattlePanel.handle_click
  - BattlePanel.draw_stat_bar
  - BattlePanel._get_ships
  - ExpandableIdPanel
  - ExpandableIdPanel.__init__
  - ExpandableIdPanel._is_id_expanded
  - ExpandableIdPanel._toggle_id_expanded
  - ShipStatsPanel
  - ShipStatsPanel.__init__
  - ShipStatsPanel._get_ship_id
  - ShipStatsPanel._is_expanded
  - ShipStatsPanel._toggle_expanded
  - ... and 20 more

### game/ui/screens/battle_results_data.py (Tier 2: TIER_2_PARTIAL, 181 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/ui/screens/test_battle_results_screen.py
  - tests/unit/ui/test_battle_results_data.py
- Heuristically untested symbols (2):
  - _build_team_summary
  - _derive_winner

### game/ui/screens/builder/schematic_view.py (Tier 2: TIER_2_PARTIAL, 189 LOC, layer: ui)
- Total symbols: 10 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/builder/test_schematic_cache_key.py
  - tests/unit/ui/screens/builder/test_schematic_view.py
- Heuristically untested symbols (6):
  - SchematicView.__init__
  - SchematicView.update_rect
  - SchematicView.draw
  - SchematicView.draw_all_firing_arcs
  - SchematicView.draw_component_firing_arc
  - SchematicView.draw_weapon_arc

### game/ui/screens/builder/stat_getters.py (Tier 2: TIER_2_PARTIAL, 461 LOC, layer: ui)
- Total symbols: 49 | Heuristically tested: 17
- Candidate test files (1):
  - tests/unit/workshop/test_stat_getters.py
- Heuristically untested symbols (32):
  - fmt_time
  - fmt_multiply
  - fmt_decimal
  - fmt_score
  - fmt_targeting
  - get_total_crew_requirement
  - mass_validator
  - crew_validator
  - life_support_validator
  - get_mass_display
  - get_crew_capacity
  - get_life_support
  - get_max_targets
  - get_armor_hp
  - get_maneuver_points
  - ... and 17 more

### game/ui/screens/fleet_report_window.py (Tier 2: TIER_2_PARTIAL, 565 LOC, layer: ui)
- Total symbols: 23 | Heuristically tested: 8
- Candidate test files (2):
  - tests/unit/ui/screens/test_fleet_report_window.py
  - tests/unit/ui/screens/test_fleet_report_window_multi_select.py
- Heuristically untested symbols (15):
  - FleetReportLayoutBuilder
  - FleetReportLayoutBuilder.build
  - FleetReportWindow.__init__
  - FleetReportWindow._swap_columns
  - FleetReportWindow.process_event
  - FleetReportWindow._handle_row_click
  - FleetReportWindow.select_ship
  - FleetReportWindow._on_remove_ship
  - FleetReportWindow._post_removal_refresh
  - FleetReportWindow._toggle_filter
  - FleetReportWindow._apply_tri_state_filter
  - FleetReportWindow._toggle_column
  - FleetReportWindow.on_close_window_button_pressed
  - FleetReportWindow.request_close
  - FleetReportWindow.open_for_fleet

### game/ui/screens/galaxy_test/galaxy_mode.py (Tier 0: TIER_0_NO_TESTS, 427 LOC, layer: ui)
- Total symbols: 8 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (8):
  - GalaxyModeHelper
  - GalaxyModeHelper.__init__
  - GalaxyModeHelper.create_ui
  - GalaxyModeHelper.generate
  - GalaxyModeHelper._center_camera
  - GalaxyModeHelper.update_slider_displays
  - GalaxyModeHelper.draw
  - GalaxyModeHelper._draw_warp_lanes

### game/ui/screens/list_filter_utils.py (Tier 0: TIER_0_NO_TESTS, 43 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - make_attr_sort_key
  - _key

### game/ui/screens/new_game_setup_controller.py (Tier 2: TIER_2_PARTIAL, 360 LOC, layer: ui)
- Total symbols: 15 | Heuristically tested: 12
- Candidate test files (3):
  - tests/unit/ui/screens/test_new_game_setup_controller.py
  - tests/unit/ui/screens/test_new_game_setup_extended.py
  - tests/unit/ui/test_new_game_setup.py
- Heuristically untested symbols (3):
  - NewGameSetupController._collect_empire_names
  - NewGameSetupController._centered_modal_rect
  - NewGameSetupController._screen_centered_rect

### game/ui/screens/race_setup/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 27 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (2):
  - tests/unit/ui/screens/race_setup/test_panel_factory.py
  - tests/unit/ui/screens/test_race_setup_screen.py

### game/ui/screens/race_setup/llm_dialog_service.py (Tier 2: TIER_2_PARTIAL, 154 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/ui/screens/test_race_setup_delegate_factory.py
  - tests/unit/ui/screens/test_race_setup_screen.py
- Heuristically untested symbols (2):
  - LLMDialogService.check_dialog_thresholds
  - LLMDialogService.check_error_popups

### game/ui/screens/strategy_render/context.py (Tier 3: TIER_3_APPARENTLY_COVERED, 34 LOC, layer: ui)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/ui/screens/strategy_render/test_context.py

### game/ui/screens/strategy_render/systems.py (Tier 0: TIER_0_NO_TESTS, 307 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - draw_systems
  - load_star_image
  - draw_colony_marker
  - draw_star
  - draw_system_details

### game/ui/screens/test_lab/data_extractor.py (Tier 2: TIER_2_PARTIAL, 227 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/test_lab/test_data_paths.py
- Heuristically untested symbols (4):
  - TestLabDataExtractor.extract_ships
  - TestLabDataExtractor._extract_component_ids
  - TestLabDataExtractor.load_component
  - TestLabDataExtractor.get_components_cache

### game/ui/screens/workshop_viewmodel_selection.py (Tier 0: TIER_0_NO_TESTS, 140 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - normalize_selection
  - apply_append_selection
  - sync_modifiers_to_selection

### game/ui/services/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 29 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (2):
  - tests/unit/systems/test_persistence.py
  - tests/unit/ui/services/test_tkinter_utils.py

### game/ui/services/image/defaults.py (Tier 0: TIER_0_NO_TESTS, 45 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - get_default_image_provider
  - set_default_image_provider

### game/ui/utils/portraits.py (Tier 3: TIER_3_APPARENTLY_COVERED, 105 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/utils/test_portraits.py

### game/ui/widgets/scrollable_json_panel.py (Tier 2: TIER_2_PARTIAL, 412 LOC, layer: ui)
- Total symbols: 15 | Heuristically tested: 10
- Candidate test files (1):
  - tests/unit/ui/widgets/test_scrollable_json_panel.py
- Heuristically untested symbols (5):
  - ScrollableJsonPanel._add_key_value_line_with_diff
  - ScrollableJsonPanel._add_value_line_with_diff
  - ScrollableJsonPanel._get_scrollbar_thumb_rect
  - ScrollableJsonPanel.draw
  - ScrollableJsonPanel._draw_scrollbar
