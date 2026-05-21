# Coverage Data — Shard 01

**Coverage source:** heuristic
**File count:** 48 | **LOC estimate:** 9451
**Tiers:** 0=9 1=3 2=23 3=13

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/core/patterns/layer_iterator.py (Tier 3: TIER_3_APPARENTLY_COVERED, 162 LOC, layer: core)
- Total symbols: 6 | Heuristically tested: 6
- Candidate test files (2):
  - tests/unit/core/patterns/test_layer_iterator.py
  - tests/unit/ui/screens/battle_setup/test_spec_compiler.py

### game/core/validation_helpers.py (Tier 3: TIER_3_APPARENTLY_COVERED, 222 LOC, layer: core)
- Total symbols: 6 | Heuristically tested: 6
- Candidate test files (1):
  - tests/unit/core/test_validation_helpers.py

### game/research/data/tech_node.py (Tier 3: TIER_3_APPARENTLY_COVERED, 158 LOC, layer: research)
- Total symbols: 9 | Heuristically tested: 9
- Candidate test files (8):
  - tests/unit/research/tech_tree/test_cycle_detection.py
  - tests/unit/research/tech_tree/test_loading.py
  - tests/unit/research/tech_tree/test_queries.py
  - tests/unit/research/tech_tree/test_validation.py
  - tests/unit/research/test_research_service.py
  - tests/unit/research/test_research_service_edge_cases.py
  - tests/unit/research/test_tech_node.py
  - tests/unit/research/test_tech_requirement_negation.py

### game/services/llm/factory.py (Tier 3: TIER_3_APPARENTLY_COVERED, 79 LOC, layer: services)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/services/llm/test_deepseek.py
  - tests/unit/services/llm/test_factory.py

### game/services/provider_factory.py (Tier 0: TIER_0_NO_TESTS, 87 LOC, layer: services)
- Total symbols: 1 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (1):
  - resolve_provider

### game/simulation/battle_spec.py (Tier 2: TIER_2_PARTIAL, 257 LOC, layer: simulation)
- Total symbols: 9 | Heuristically tested: 8
- Candidate test files (23):
  - tests/unit/combat_lab/scenarios/test_comparison_scenario.py
  - tests/unit/combat_lab/services/test_ab_battle_runner.py
  - tests/unit/combat_lab/test_spec_compiler.py
  - tests/unit/simulation/battle_controller/test_outcome_emission.py
  - tests/unit/simulation/battle_runner/test_spec_component_validation.py
  - tests/unit/simulation/combat/test_formation_resolver.py
  - tests/unit/simulation/conftest.py
  - tests/unit/simulation/replay/test_replay_player.py
  - ... and 15 more
- Heuristically untested symbols (1):
  - TaskForceSpec.__post_init__

### game/simulation/combat/attack_contract.py (Tier 2: TIER_2_PARTIAL, 207 LOC, layer: simulation)
- Total symbols: 9 | Heuristically tested: 8
- Candidate test files (8):
  - tests/unit/engine/collision_edge_cases/test_beam_ramming.py
  - tests/unit/simulation/combat/test_beam_hit_tracking.py
  - tests/unit/simulation/combat/test_weapon_dispatch_golden.py
  - tests/unit/simulation/combat/test_weapon_family_handlers.py
  - tests/unit/simulation/combat/test_weapon_firing_system.py
  - tests/unit/simulation/combat/test_weapon_registry.py
  - tests/unit/simulation/test_projectile_event_bus_wiring.py
  - tests/unit/ui/test_battle_screen_extended.py
- Heuristically untested symbols (1):
  - WeaponFamilyMetadata

### game/simulation/combat/combat_events.py (Tier 2: TIER_2_PARTIAL, 164 LOC, layer: simulation)
- Total symbols: 10 | Heuristically tested: 9
- Candidate test files (6):
  - tests/unit/simulation/combat/test_combat_events.py
  - tests/unit/simulation/combat/test_damage_calculator_events.py
  - tests/unit/simulation/combat/test_hit_log_modifier_trace.py
  - tests/unit/simulation/combat/test_hit_log_recorder.py
  - tests/unit/simulation/combat/test_ship_stats_aggregator.py
  - tests/unit/simulation/ship_combat_engine/test_combat_ops.py

### game/simulation/components/component_health_manager.py (Tier 2: TIER_2_PARTIAL, 102 LOC, layer: simulation)
- Total symbols: 5 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/simulation/components/test_component_health_manager.py
- Heuristically untested symbols (1):
  - ComponentHealthManager.__init__

### game/simulation/entities/combat_endurance.py (Tier 3: TIER_3_APPARENTLY_COVERED, 155 LOC, layer: simulation)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/simulation/entities/test_combat_endurance.py

### game/simulation/entities/ship_stat_querier.py (Tier 2: TIER_2_PARTIAL, 145 LOC, layer: simulation)
- Total symbols: 7 | Heuristically tested: 6
- Candidate test files (1):
  - tests/unit/entities/test_ship_stat_querier.py
- Heuristically untested symbols (1):
  - ShipStatQuerier.__init__

### game/simulation/entities/stat_contributors/command.py (Tier 0: TIER_0_NO_TESTS, 116 LOC, layer: simulation)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - contribute_multiplex_tracking
  - allocate_crew_and_life_support

### game/simulation/entities/stat_contributors/weapons.py (Tier 0: TIER_0_NO_TESTS, 56 LOC, layer: simulation)
- Total symbols: 1 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (1):
  - aggregate_targeting_scores

### game/strategy/combat/pre_tick_setup/mine_setup.py (Tier 0: TIER_0_NO_TESTS, 62 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - build_mine_resolver_setup
  - _setup

### game/strategy/combat/pre_tick_setup_registry.py (Tier 2: TIER_2_PARTIAL, 118 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/strategy/combat/test_pre_tick_setup_registry.py
- Heuristically untested symbols (2):
  - PreTickBattleSetupRegistry.__init__
  - PreTickBattleSetupRegistry.__len__

### game/strategy/data/colony_species_config.py (Tier 3: TIER_3_APPARENTLY_COVERED, 118 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 6
- Candidate test files (7):
  - tests/unit/strategy/data/test_colony_species_config.py
  - tests/unit/strategy/data/test_planet_species_configs.py
  - tests/unit/strategy/engine/test_happiness_engine.py
  - tests/unit/strategy/facade/test_colony_demographic_view.py
  - tests/unit/strategy/formulas/test_colony_output.py
  - tests/unit/strategy/services/test_planet_economy_projector.py
  - tests/unit/ui/screens/test_food_allocation_editor.py

### game/strategy/data/fleet.py (Tier 2: TIER_2_PARTIAL, 632 LOC, layer: strategy)
- Total symbols: 43 | Heuristically tested: 39
- Candidate test files (128):
  - tests/unit/core/test_protocols.py
  - tests/unit/simulation/systems/test_fighter_reboard.py
  - tests/unit/simulation/systems/test_fighter_reboard_component_state.py
  - tests/unit/simulation/systems/test_fighter_reboard_overflow_component_state.py
  - tests/unit/simulation/systems/test_satellite_reboard.py
  - tests/unit/strategy/combat/test_fighter_group_combat_join.py
  - tests/unit/strategy/combat/test_post_battle_hook.py
  - tests/unit/strategy/combat/test_satellite_group_combat_join.py
  - ... and 120 more
- Heuristically untested symbols (4):
  - Fleet.get_combat_capable_ships
  - Fleet._unregister_from_target
  - Fleet.__eq__
  - Fleet.__hash__

### game/strategy/data/race_config.py (Tier 2: TIER_2_PARTIAL, 372 LOC, layer: strategy)
- Total symbols: 15 | Heuristically tested: 8
- Candidate test files (29):
  - tests/unit/fixtures/test_strategy_entities.py
  - tests/unit/quickstart/test_quickstart_races.py
  - tests/unit/strategy/data/test_homeworld_presets.py
  - tests/unit/strategy/data/test_population_model.py
  - tests/unit/strategy/data/test_race_config.py
  - tests/unit/strategy/data/test_race_point_budget_v2.py
  - tests/unit/strategy/engine/test_game_initializer.py
  - tests/unit/strategy/engine/test_happiness_engine.py
  - ... and 21 more
- Heuristically untested symbols (7):
  - RaceConfig._validate_required_fields
  - RaceConfig._validate_aptitudes
  - RaceConfig._validate_identity_enums
  - RaceConfig._validate_homeworld
  - RaceConfig._validate_descriptions
  - RaceConfig._validate_preferences
  - RaceConfig._validate_reproduction_and_happiness

### game/strategy/data/resource_generation_config.py (Tier 2: TIER_2_PARTIAL, 149 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/strategy/data/test_resource_generation_config.py
  - tests/unit/strategy/engine/test_game_initializer.py
- Heuristically untested symbols (3):
  - ResourceGenerationConfig.__init__
  - ResourceGenerationConfig._load_from_json
  - ResourceGenerationConfig._use_defaults

### game/strategy/data/ship_consumable_manager.py (Tier 2: TIER_2_PARTIAL, 181 LOC, layer: strategy)
- Total symbols: 12 | Heuristically tested: 11
- Candidate test files (4):
  - tests/unit/strategy/test_managers_phase_3b.py
  - tests/unit/strategy/test_ship_consumable_manager.py
  - tests/unit/strategy/test_ship_display_formatter.py
  - tests/unit/ui/screens/test_fleet_report_filters.py
- Heuristically untested symbols (1):
  - ShipConsumableManager.__init__

### game/strategy/data/ship_stats_cache.py (Tier 3: TIER_3_APPARENTLY_COVERED, 66 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/strategy/ship_instance/test_ship_stats_cache.py

### game/strategy/data/spectrum.py (Tier 3: TIER_3_APPARENTLY_COVERED, 73 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (13):
  - tests/unit/core/test_protocols.py
  - tests/unit/fixtures/test_strategy_entities.py
  - tests/unit/strategy/data/test_galaxy.py
  - tests/unit/strategy/data/test_radiation_physics.py
  - tests/unit/strategy/data/test_spectrum.py
  - tests/unit/strategy/data/test_stars.py
  - tests/unit/strategy/data/test_storm.py
  - tests/unit/strategy/facade/test_star_info_dto.py
  - ... and 5 more

### game/strategy/engine/empire_economy_calculator.py (Tier 2: TIER_2_PARTIAL, 333 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 4
- Candidate test files (4):
  - tests/unit/strategy/engine/conftest.py
  - tests/unit/strategy/engine/test_empire_economy_calculator.py
  - tests/unit/strategy/services/test_empire_economy_service.py
  - tests/unit/ui/panels/test_empire_treasury_panel.py
- Heuristically untested symbols (4):
  - EmpireEconomyCalculator.__init__
  - EmpireEconomyCalculator._aggregate_population_upkeep
  - EmpireEconomyCalculator._aggregate_colony_production
  - EmpireEconomyCalculator._aggregate_construction_expenses

### game/strategy/engine/game_session.py (Tier 2: TIER_2_PARTIAL, 498 LOC, layer: strategy)
- Total symbols: 28 | Heuristically tested: 19
- Candidate test files (15):
  - tests/unit/strategy/engine/session/test_bootstrap.py
  - tests/unit/strategy/engine/session/test_persistence_adapter.py
  - tests/unit/strategy/engine/session/test_runtime_services.py
  - tests/unit/strategy/engine/test_game_initializer.py
  - tests/unit/strategy/engine/test_game_session_from_dict.py
  - tests/unit/strategy/engine/test_game_session_projection_boundary.py
  - tests/unit/strategy/engine/test_game_session_shape.py
  - tests/unit/strategy/engine/test_population_seeding.py
  - ... and 7 more
- Heuristically untested symbols (9):
  - GameSession._event_log
  - GameSession._fleet_mutator
  - GameSession._planet_mutator
  - GameSession._empire_mutator
  - GameSession._ship_mutator
  - GameSession.process_turn
  - GameSession.preview_fleet_path
  - GameSession.get_fleet_path_projection
  - GameSession._get_planet_by_id

### game/strategy/engine/handlers/order_queue.py (Tier 2: TIER_2_PARTIAL, 267 LOC, layer: strategy)
- Total symbols: 11 | Heuristically tested: 10
- Candidate test files (1):
  - tests/unit/strategy/engine/handlers/test_order_queue_handlers.py
- Heuristically untested symbols (1):
  - register

### game/strategy/events/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 6 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (6):
  - tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py
  - tests/unit/strategy/engine/session/test_bootstrap.py
  - tests/unit/strategy/engine/test_conflict_resolution_event_replay.py
  - tests/unit/strategy/facade/test_event_queries.py
  - tests/unit/strategy/test_engine_event_emission.py
  - tests/unit/strategy/test_game_session_events.py

### game/strategy/facade/dto/system_dto.py (Tier 3: TIER_3_APPARENTLY_COVERED, 162 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/strategy/facade/test_star_info_dto.py
  - tests/unit/strategy/facade/test_system_dto.py

### game/strategy/interfaces/engines/planet_ops.py (Tier 0: TIER_0_NO_TESTS, 89 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - IPlanetEnergyEngine
  - IPlanetEnergyEngine.process_energy_tick
  - IPlanetActionEngine
  - IPlanetActionEngine.process_planet_actions_tick

### game/strategy/services/component_layers.py (Tier 0: TIER_0_NO_TESTS, 169 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - lookup_design_max_hp
  - iter_components_by_layer
  - damaged_components_by_layer
  - count_damaged_components

### game/strategy/services/replay_resolver.py (Tier 2: TIER_2_PARTIAL, 130 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/screens/test_event_log_replay_button.py
- Heuristically untested symbols (2):
  - ReplayResolver
  - ReplayResolver.from_registries

### game/ui/components/__init__.py (Tier 0: TIER_0_NO_TESTS, 1 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/ui/components/table/data_source.py (Tier 3: TIER_3_APPARENTLY_COVERED, 111 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 7
- Candidate test files (1):
  - tests/unit/ui/components/table/test_data_source.py

### game/ui/panels/base_gallery.py (Tier 3: TIER_3_APPARENTLY_COVERED, 265 LOC, layer: ui)
- Total symbols: 17 | Heuristically tested: 17
- Candidate test files (1):
  - tests/unit/ui/panels/test_base_gallery.py

### game/ui/panels/race_portrait_gallery.py (Tier 2: TIER_2_PARTIAL, 171 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/ui/test_race_portrait_gallery.py
- Heuristically untested symbols (8):
  - RacePortraitGallery._get_label_text
  - RacePortraitGallery._get_thumb_size
  - RacePortraitGallery._get_preview_size
  - RacePortraitGallery._get_object_id_prefix
  - RacePortraitGallery._get_preview_panel_object_id
  - RacePortraitGallery._get_current_selection
  - RacePortraitGallery._set_selection
  - RacePortraitGallery._update_preview

### game/ui/panels/system_tree_panel.py (Tier 2: TIER_2_PARTIAL, 711 LOC, layer: ui)
- Total symbols: 25 | Heuristically tested: 15
- Candidate test files (2):
  - tests/unit/ui/panels/test_system_tree_panel_characterization.py
  - tests/unit/ui/panels/test_system_tree_panel_hazard.py
- Heuristically untested symbols (10):
  - SystemTreeItem.add_child
  - SystemTreeItem.set_expanded
  - SystemTreeItem.set_position
  - SystemTreeItem.show
  - SystemTreeItem.hide
  - SystemTreePanel._get_empire_context
  - SystemTreePanel.layout
  - SystemTreePanel._hide_recursive
  - SystemTreePanel.process_event
  - SystemTreePanel.set_dimensions

### game/ui/screens/battle_setup/fleet_hierarchy_editor.py (Tier 2: TIER_2_PARTIAL, 191 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 8
- Candidate test files (1):
  - tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py
- Heuristically untested symbols (1):
  - _get_registries

### game/ui/screens/battle_setup/spec_compiler.py (Tier 2: TIER_2_PARTIAL, 459 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/ui/screens/battle_setup/test_spec_compiler.py
  - tests/unit/ui/screens/battle_setup/test_spec_compiler_formation.py
- Heuristically untested symbols (4):
  - _build_team_spec
  - _task_force_for_fleet
  - _pick_formation_for_fleet
  - _build_modifier_stack

### game/ui/screens/battle_ui.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 209 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/ui/conftest.py
- Heuristically untested symbols (9):
  - BattleUI
  - BattleUI.__init__
  - BattleUI.track_projectile
  - BattleUI.handle_resize
  - BattleUI.draw
  - BattleUI.handle_click
  - BattleUI.handle_scroll
  - BattleUI.draw_grid
  - BattleUI.draw_debug_overlay

### game/ui/screens/builder/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 7 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (4):
  - tests/unit/ui/screens/builder/test_components.py
  - tests/unit/ui/screens/builder/test_modifier_row.py
  - tests/unit/ui/screens/builder/test_stat_getters.py
  - tests/unit/ui/screens/builder/test_stat_rows_dynamic.py

### game/ui/screens/builder/drop_target.py (Tier 3: TIER_3_APPARENTLY_COVERED, 15 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/builder/test_builder_interaction.py

### game/ui/screens/defeat_dialog.py (Tier 0: TIER_0_NO_TESTS, 121 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - _format_body
  - DefeatDialog
  - DefeatDialog.__init__
  - DefeatDialog.process_event

### game/ui/screens/empire_build_queue_formatter.py (Tier 2: TIER_2_PARTIAL, 189 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 8
- Candidate test files (1):
  - tests/unit/ui/screens/test_empire_build_queue_formatter.py
- Heuristically untested symbols (1):
  - format_turns_remaining

### game/ui/screens/planet_list_sidebar.py (Tier 2: TIER_2_PARTIAL, 286 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/ui/screens/test_planet_list_components.py
- Heuristically untested symbols (1):
  - add_range

### game/ui/screens/strategy_click_dispatcher.py (Tier 2: TIER_2_PARTIAL, 634 LOC, layer: ui)
- Total symbols: 26 | Heuristically tested: 12
- Candidate test files (3):
  - tests/unit/ui/screens/test_open_warp_user_error_surfacing.py
  - tests/unit/ui/screens/test_strategy_click_dispatcher.py
  - tests/unit/ui/screens/test_strategy_click_dispatcher_rmb.py
- Heuristically untested symbols (13):
  - ClickModeDispatcher._handle_move_mode_click
  - ClickModeDispatcher._handle_join_mode_click
  - ClickModeDispatcher._handle_colonize_mode_click
  - ClickModeDispatcher._handle_transfer_mode_click
  - ClickModeDispatcher._handle_edit_move_click
  - ClickModeDispatcher._handle_drop_cargo_mode_click
  - ClickModeDispatcher._handle_load_cargo_mode_click
  - ClickModeDispatcher._handle_warp_target_click
  - ClickModeDispatcher._handle_implode_planet_click
  - ClickModeDispatcher._handle_stellerate_star_click
  - ClickModeDispatcher._handle_open_warp_click
  - ClickModeDispatcher._handle_close_warp_click
  - ClickModeDispatcher._handle_dyson_sphere_click

### game/ui/screens/strategy_screen_composition.py (Tier 3: TIER_3_APPARENTLY_COVERED, 114 LOC, layer: ui)
- Total symbols: 18 | Heuristically tested: 18
- Candidate test files (1):
  - tests/unit/ui/screens/test_strategy_screen_composition.py

### game/ui/screens/test_lab/details/chrome.py (Tier 0: TIER_0_NO_TESTS, 244 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (6):
  - ActionButtonRects
  - draw_header_and_status
  - draw_metadata
  - draw_action_buttons
  - draw_metrics
  - draw_scrollbar

### game/ui/screens/test_lab/formatting_utils.py (Tier 2: TIER_2_PARTIAL, 67 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/ui/test_lab_formatting_utils.py
- Heuristically untested symbols (1):
  - _format_float

### game/ui/services/battle_ui_service.py (Tier 2: TIER_2_PARTIAL, 321 LOC, layer: ui)
- Total symbols: 14 | Heuristically tested: 10
- Candidate test files (5):
  - tests/unit/ui/services/battle_ui_service/test_conversion.py
  - tests/unit/ui/services/battle_ui_service/test_state_and_integration.py
  - tests/unit/ui/services/test_battle_ui_service.py
  - tests/unit/ui/test_battle_screen.py
  - tests/unit/ui/test_battle_screen_simulation.py
- Heuristically untested symbols (4):
  - _target_display_name
  - BattleUIService.__init__
  - BattleUIService._convert_component
  - BattleUIService._convert_beam
