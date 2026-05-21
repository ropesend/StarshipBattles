# Coverage Data — Shard 05

**Coverage source:** heuristic
**File count:** 32 | **LOC estimate:** 9500
**Tiers:** 0=8 1=0 2=17 3=7

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/core/component_state.py (Tier 2: TIER_2_PARTIAL, 102 LOC, layer: core)
- Total symbols: 7 | Heuristically tested: 6
- Candidate test files (14):
  - tests/unit/core/test_component_state.py
  - tests/unit/simulation/systems/test_fighter_reboard_component_state.py
  - tests/unit/simulation/systems/test_fighter_reboard_overflow_component_state.py
  - tests/unit/simulation/systems/test_ship_design_stats.py
  - tests/unit/strategy/combat/test_post_battle_hook.py
  - tests/unit/strategy/combat/test_spec_compiler.py
  - tests/unit/strategy/fleets/test_ship_instance_components.py
  - tests/unit/strategy/fleets/test_ship_instance_roundtrip.py
  - ... and 6 more
- Heuristically untested symbols (1):
  - ComponentState.__post_init__

### game/core/config.py (Tier 3: TIER_3_APPARENTLY_COVERED, 207 LOC, layer: core)
- Total symbols: 9 | Heuristically tested: 9
- Candidate test files (16):
  - tests/unit/ai/test_ai_controller_interface.py
  - tests/unit/ai/test_ai_controller_unit.py
  - tests/unit/ai/test_behavior_units.py
  - tests/unit/ai/test_erratic_behavior_seeded.py
  - tests/unit/ai/test_fighter_controller.py
  - tests/unit/core/test_config.py
  - tests/unit/core/test_config_edge_cases.py
  - tests/unit/core/test_simulation_constants.py
  - ... and 8 more

### game/core/paths.py (Tier 2: TIER_2_PARTIAL, 202 LOC, layer: core)
- Total symbols: 13 | Heuristically tested: 10
- Candidate test files (26):
  - tests/unit/assets/test_asset_manager_resolutions.py
  - tests/unit/core/test_paths_config.py
  - tests/unit/quickstart/conftest.py
  - tests/unit/quickstart/test_quickstart_builder.py
  - tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py
  - tests/unit/simulation/entities/test_ship_loader.py
  - tests/unit/simulation/entities/test_ship_stats_golden.py
  - tests/unit/simulation/entities/test_stat_contributor_extension.py
  - ... and 18 more
- Heuristically untested symbols (3):
  - _find_project_root
  - Paths.get_planets_v3_dir
  - Paths.get_stars_dir

### game/core/string_utils.py (Tier 3: TIER_3_APPARENTLY_COVERED, 48 LOC, layer: core)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/core/test_string_utils.py
  - tests/unit/strategy/systems/test_race_library.py

### game/engine/__init__.py (Tier 0: TIER_0_NO_TESTS, 36 LOC, layer: engine)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/simulation/battle_outcome.py (Tier 3: TIER_3_APPARENTLY_COVERED, 203 LOC, layer: simulation)
- Total symbols: 9 | Heuristically tested: 9
- Candidate test files (18):
  - tests/unit/simulation/combat/test_hit_log_modifier_trace.py
  - tests/unit/simulation/combat/test_hit_log_recorder.py
  - tests/unit/simulation/combat/test_ship_stats_aggregator.py
  - tests/unit/simulation/combat/test_weapon_summary_aggregator.py
  - tests/unit/simulation/replay/test_replay_player.py
  - tests/unit/simulation/replay/test_serialization.py
  - tests/unit/simulation/test_battle_outcome.py
  - tests/unit/simulation/test_battle_outcome_replay_id.py
  - ... and 10 more

### game/simulation/combat/families/__init__.py (Tier 0: TIER_0_NO_TESTS, 13 LOC, layer: simulation)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/simulation/combat/formation.py (Tier 2: TIER_2_PARTIAL, 416 LOC, layer: simulation)
- Total symbols: 10 | Heuristically tested: 8
- Candidate test files (11):
  - tests/unit/combat_lab/test_spec_compiler_formation.py
  - tests/unit/simulation/combat/test_formation.py
  - tests/unit/simulation/combat/test_formation_defaults.py
  - tests/unit/simulation/combat/test_formation_resolver.py
  - tests/unit/simulation/replay/test_serialization.py
  - tests/unit/simulation/test_battle_spec.py
  - tests/unit/strategy/combat/test_spec_compiler.py
  - tests/unit/strategy/combat/test_spec_compiler_formation.py
  - ... and 3 more
- Heuristically untested symbols (2):
  - _compute_local_positions
  - _symmetric_y

### game/simulation/components/abilities/base.py (Tier 2: TIER_2_PARTIAL, 535 LOC, layer: simulation)
- Total symbols: 31 | Heuristically tested: 28
- Candidate test files (26):
  - tests/unit/abilities/test_ability_layer_scope.py
  - tests/unit/abilities/test_strategic_movement.py
  - tests/unit/abilities/test_warp_jump.py
  - tests/unit/modifiers/test_ability_introspection.py
  - tests/unit/simulation/abilities/test_cargo_storage.py
  - tests/unit/simulation/combat/test_fleet_aura_cache.py
  - tests/unit/simulation/combat/test_fleet_aura_extended.py
  - tests/unit/simulation/combat/test_fleet_aura_provider_identity.py
  - ... and 18 more
- Heuristically untested symbols (3):
  - Ability._parse_attrs
  - StaticValueAbility._parse_attrs
  - SimpleMultiplierAbility._parse_attrs

### game/simulation/components/abilities/weapons.py (Tier 3: TIER_3_APPARENTLY_COVERED, 386 LOC, layer: simulation)
- Total symbols: 26 | Heuristically tested: 26
- Candidate test files (10):
  - tests/unit/ai/test_combat_utils.py
  - tests/unit/ai/test_targeting_rules.py
  - tests/unit/combat_lab/test_weapon_stats_collection.py
  - tests/unit/modifiers/test_projectile_weapon_bindings.py
  - tests/unit/modifiers/test_seeker_multi_ability.py
  - tests/unit/modifiers/test_seeker_weapon_bindings.py
  - tests/unit/modifiers/test_weapon_ability_bindings.py
  - tests/unit/simulation/combat/test_weapon_summary_aggregator.py
  - ... and 2 more

### game/simulation/entities/stat_contributors/launch.py (Tier 0: TIER_0_NO_TESTS, 118 LOC, layer: simulation)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - contribute_vehicle_launch
  - contribute_tactical_satellite_launch
  - contribute_vehicle_bay

### game/simulation/interfaces/component_protocols.py (Tier 0: TIER_0_NO_TESTS, 226 LOC, layer: simulation)
- Total symbols: 23 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (23):
  - IComponent
  - IComponent.id
  - IComponent.name
  - IComponent.is_active
  - IComponent.current_hp
  - IComponent.max_hp
  - IComponent.status
  - IComponent.ability_instances
  - IComponent.abilities
  - IComponent.modifiers
  - IComponent.stats
  - IComponent.ability_stats
  - IComponent.ship
  - IComponent.layer_assigned
  - IComponent.shots_fired
  - ... and 8 more

### game/simulation/services/vehicle_design_service.py (Tier 3: TIER_3_APPARENTLY_COVERED, 516 LOC, layer: simulation)
- Total symbols: 14 | Heuristically tested: 14
- Candidate test files (4):
  - tests/unit/core/test_service_injection.py
  - tests/unit/simulation/services/test_vehicle_design_service.py
  - tests/unit/ui/screens/test_workshop_viewmodel_pick_up.py
  - tests/unit/workshop/test_move_component.py

### game/simulation/systems/battle_engine.py (Tier 2: TIER_2_PARTIAL, 758 LOC, layer: simulation)
- Total symbols: 33 | Heuristically tested: 19
- Candidate test files (17):
  - tests/unit/ai/test_ai_n_team_targeting.py
  - tests/unit/fixtures/test_battle_fixtures.py
  - tests/unit/simulation/components/abilities/test_tactical_fighter_launch.py
  - tests/unit/simulation/components/abilities/test_tactical_satellite_launch.py
  - tests/unit/simulation/factories/test_ai_factory.py
  - tests/unit/simulation/systems/test_add_ship_mid_battle.py
  - tests/unit/simulation/systems/test_battle_engine_boundary.py
  - tests/unit/simulation/systems/test_battle_engine_end_conditions.py
  - ... and 9 more
- Heuristically untested symbols (14):
  - BattleEngine._initialize_start_state
  - BattleEngine.remove_ship
  - BattleEngine.get_ship_by_name
  - BattleEngine.set_ram_target
  - BattleEngine.clear_ram_target
  - BattleEngine._run_ramming_tick
  - BattleEngine._rebuild_grid
  - BattleEngine._update_ai_and_ships
  - BattleEngine._collect_new_attacks
  - BattleEngine._process_attacks
  - BattleEngine._process_projectile_attack
  - BattleEngine._process_launch_attack
  - BattleEngine.enforce_boundary
  - BattleEngine.shutdown

### game/strategy/data/deployed_group.py (Tier 2: TIER_2_PARTIAL, 424 LOC, layer: strategy)
- Total symbols: 26 | Heuristically tested: 14
- Candidate test files (22):
  - tests/unit/simulation/systems/test_fighter_reboard.py
  - tests/unit/simulation/systems/test_fighter_reboard_overflow_component_state.py
  - tests/unit/simulation/systems/test_satellite_reboard.py
  - tests/unit/simulation/systems/test_tactical_mine_resolver.py
  - tests/unit/strategy/combat/test_battle_assembly.py
  - tests/unit/strategy/combat/test_battle_assembly_third_party_mines.py
  - tests/unit/strategy/combat/test_fighter_group_combat_join.py
  - tests/unit/strategy/combat/test_satellite_group_combat_join.py
  - ... and 14 more
- Heuristically untested symbols (12):
  - _register_type
  - deco
  - DeployedGroup._from_dict_payload
  - DeployedGroup._decode_location
  - DeployedGroup.__eq__
  - DeployedGroup.__hash__
  - DeployedGroup.__repr__
  - MineGroup._from_dict_payload
  - _ShipBearingDeployedGroup
  - _ShipBearingDeployedGroup.remove_ship
  - FighterWing._from_dict_payload
  - SatelliteConstellation._from_dict_payload

### game/strategy/engine/population_engine.py (Tier 2: TIER_2_PARTIAL, 177 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 6
- Candidate test files (4):
  - tests/unit/strategy/engine/test_engine_validation.py
  - tests/unit/strategy/engine/test_population_engine.py
  - tests/unit/strategy/formulas/test_colony_output.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
- Heuristically untested symbols (2):
  - PopulationEngine._process_empire
  - PopulationEngine._process_colony

### game/strategy/engine/production_spawner.py (Tier 2: TIER_2_PARTIAL, 667 LOC, layer: strategy)
- Total symbols: 15 | Heuristically tested: 11
- Candidate test files (3):
  - tests/unit/strategy/engine/test_production_normalisation.py
  - tests/unit/strategy/engine/test_production_spawner.py
  - tests/unit/strategy/engine/test_production_spawner_staging_yard.py
- Heuristically untested symbols (4):
  - ProductionSpawner.__init__
  - ProductionSpawner._get_catalog
  - ProductionSpawner._get_planet_mutator
  - ProductionSpawner._spawn_fleet_carried_vehicle

### game/strategy/facade/slices/economy_slice.py (Tier 0: TIER_0_NO_TESTS, 188 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - EconomySlice
  - EconomySlice.__init__
  - EconomySlice.get_race_registry
  - EconomySlice.resolve_economy_config
  - EconomySlice.get_colony_demographic_view

### game/strategy/generation/loaders/__init__.py (Tier 0: TIER_0_NO_TESTS, 7 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/strategy/quickstart_builder.py (Tier 3: TIER_3_APPARENTLY_COVERED, 333 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 6
- Candidate test files (3):
  - tests/unit/quickstart/test_quickstart_builder.py
  - tests/unit/strategy/engine/test_population_seeding.py
  - tests/unit/strategy/test_quickstart_builder.py

### game/strategy/services/superweapon_registry.py (Tier 3: TIER_3_APPARENTLY_COVERED, 131 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (4):
  - tests/unit/strategy/engine/order_handlers/test_superweapon_dispatch.py
  - tests/unit/strategy/services/test_ability_metadata_contracts.py
  - tests/unit/strategy/services/test_ability_metadata_registry.py
  - tests/unit/strategy/services/test_superweapon_registry_contract.py

### game/ui/panels/modifier_impact_grid.py (Tier 2: TIER_2_PARTIAL, 514 LOC, layer: ui)
- Total symbols: 16 | Heuristically tested: 14
- Candidate test files (1):
  - tests/unit/ui/test_modifier_impact_grid.py
- Heuristically untested symbols (2):
  - ModifierImpactGrid._get_component_consumed_stats
  - ModifierImpactGrid._get_rotated_header

### game/ui/screens/builder/modifier_row.py (Tier 2: TIER_2_PARTIAL, 355 LOC, layer: ui)
- Total symbols: 10 | Heuristically tested: 8
- Candidate test files (3):
  - tests/unit/repro_issues/test_slider_increment.py
  - tests/unit/ui/screens/builder/test_modifier_control_row.py
  - tests/unit/ui/screens/builder/test_modifier_row.py
- Heuristically untested symbols (2):
  - ModifierControlRow._build_linear_controls
  - ModifierControlRow._clear_ui

### game/ui/screens/fleet_menu_items.py (Tier 2: TIER_2_PARTIAL, 274 LOC, layer: ui)
- Total symbols: 11 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/ui/screens/test_fleet_context_menu_dispatch.py
  - tests/unit/ui/screens/test_fleet_menu_items.py
- Heuristically untested symbols (8):
  - _MapperLike
  - _has
  - _can_warp
  - _can_strategic_move
  - _has_self_destruct_ships
  - _at_colonisable_hex
  - _fleet_has_carried_vehicle
  - _matching_deployed_group_at_fleet_hex

### game/ui/screens/planet_selection_window.py (Tier 2: TIER_2_PARTIAL, 262 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/ui/screens/test_planet_selection_window.py
- Heuristically untested symbols (2):
  - PlanetSelectionUiBuilder
  - PlanetSelectionUiBuilder.build

### game/ui/screens/race_setup/ship_preview.py (Tier 0: TIER_0_NO_TESTS, 163 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - ShipPreviewBuilder
  - ShipPreviewBuilder.__init__
  - ShipPreviewBuilder.refresh

### game/ui/screens/star_list_window.py (Tier 2: TIER_2_PARTIAL, 554 LOC, layer: ui)
- Total symbols: 24 | Heuristically tested: 14
- Candidate test files (6):
  - tests/unit/ui/screens/test_event_log_row_pool_visibility.py
  - tests/unit/ui/screens/test_star_list_filter_snapshot.py
  - tests/unit/ui/screens/test_star_list_window.py
  - tests/unit/ui/screens/test_star_list_window_reuse.py
  - tests/unit/ui/screens/test_strategy_modal_esc_close.py
  - tests/unit/ui/screens/test_strategy_modal_hidden_input.py
- Heuristically untested symbols (8):
  - StarListWindowUiBuilder.build
  - StarListWindow.process_event
  - StarListWindow.update
  - StarListWindow._set_all_type_filters
  - StarListWindow._toggle_type_filter
  - StarListWindow._capture_current_state
  - StarListWindow._apply_state
  - StarListWindow.set_dimensions

### game/ui/screens/strategy_renderer.py (Tier 2: TIER_2_PARTIAL, 288 LOC, layer: ui)
- Total symbols: 37 | Heuristically tested: 28
- Candidate test files (4):
  - tests/unit/ui/screens/test_strategy_renderer.py
  - tests/unit/ui/screens/test_strategy_renderer_animation.py
  - tests/unit/ui/screens/test_strategy_renderer_public_api.py
  - tests/unit/ui/screens/test_strategy_screen_composition.py
- Heuristically untested symbols (9):
  - StrategyRenderer._draw_background
  - StrategyRenderer._draw_colony_marker
  - StrategyRenderer._draw_star
  - StrategyRenderer._draw_dyson_spheres
  - StrategyRenderer._draw_storms
  - StrategyRenderer._draw_storms_low_detail
  - StrategyRenderer._draw_planet_sprite
  - StrategyRenderer._draw_fleet_path
  - StrategyRenderer._draw_ghost_hex

### game/ui/screens/strategy_superweapons.py (Tier 2: TIER_2_PARTIAL, 416 LOC, layer: ui)
- Total symbols: 19 | Heuristically tested: 14
- Candidate test files (2):
  - tests/unit/ui/screens/test_strategy_screen_composition.py
  - tests/unit/ui/screens/test_strategy_superweapons.py
- Heuristically untested symbols (5):
  - _check_fleet_ability
  - SuperweaponOperations._queue_implode_planet
  - SuperweaponOperations._show_confirmation
  - SuperweaponOperations._show_system_picker
  - SuperweaponOperations._show_ship_picker

### game/ui/screens/test_lab/renderer/validation_panel.py (Tier 0: TIER_0_NO_TESTS, 230 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - ValidationPanel
  - ValidationPanel.__init__
  - ValidationPanel.draw
  - ValidationPanel._draw_check_compact

### game/ui/screens/transfer_view_model.py (Tier 2: TIER_2_PARTIAL, 325 LOC, layer: ui)
- Total symbols: 21 | Heuristically tested: 18
- Candidate test files (6):
  - tests/unit/ui/screens/test_transfer_controller.py
  - tests/unit/ui/screens/test_transfer_dialog_characterization.py
  - tests/unit/ui/screens/test_transfer_mass_preview.py
  - tests/unit/ui/screens/test_transfer_mixed_content.py
  - tests/unit/ui/screens/test_transfer_view_model.py
  - tests/unit/ui/screens/test_transfer_view_model_container.py
- Heuristically untested symbols (3):
  - _get_resource_catalog
  - _iter_resource_definitions
  - TransferViewModel.get_pending

### game/ui/services/image/openai_provider.py (Tier 2: TIER_2_PARTIAL, 426 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/ui/services/image/test_openai_provider.py
- Heuristically untested symbols (8):
  - OpenAIImageProvider.__init__
  - OpenAIImageProvider.__repr__
  - OpenAIImageProvider.__str__
  - OpenAIImageProvider._read_api_key
  - OpenAIImageProvider._build_headers
  - OpenAIImageProvider._post_generation
  - OpenAIImageProvider._post_edit
  - OpenAIImageProvider._read_edit_file
