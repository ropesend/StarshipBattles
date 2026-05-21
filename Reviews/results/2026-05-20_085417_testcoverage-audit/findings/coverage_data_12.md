# Coverage Data — Shard 12

**Coverage source:** heuristic
**File count:** 44 | **LOC estimate:** 9506
**Tiers:** 0=8 1=3 2=26 3=7

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/core/spectrum_math.py (Tier 3: TIER_3_APPARENTLY_COVERED, 155 LOC, layer: core)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/core/test_spectrum_math.py
  - tests/unit/strategy/data/test_stars.py

### game/services/__init__.py (Tier 0: TIER_0_NO_TESTS, 13 LOC, layer: services)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/simulation/components/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 5 LOC, layer: simulation)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/test_app_bootstrap_invariants.py

### game/simulation/components/abilities/stat_keys.py (Tier 2: TIER_2_PARTIAL, 201 LOC, layer: simulation)
- Total symbols: 8 | Heuristically tested: 7
- Candidate test files (20):
  - tests/unit/modifiers/test_ability_introspection.py
  - tests/unit/modifiers/test_ability_stat_binding.py
  - tests/unit/modifiers/test_crew_required_mass_scaling.py
  - tests/unit/modifiers/test_crew_resource_bindings.py
  - tests/unit/modifiers/test_defense_marker_bindings.py
  - tests/unit/modifiers/test_pipeline_unification.py
  - tests/unit/modifiers/test_propulsion_ability_bindings.py
  - tests/unit/modifiers/test_seeker_weapon_bindings.py
  - ... and 12 more
- Heuristically untested symbols (1):
  - AbilityStatBinding.__post_init__

### game/simulation/components/component_loader.py (Tier 2: TIER_2_PARTIAL, 323 LOC, layer: simulation)
- Total symbols: 10 | Heuristically tested: 9
- Candidate test files (9):
  - tests/unit/core/test_isolation.py
  - tests/unit/data/test_mine_design.py
  - tests/unit/entities/test_component_cache.py
  - tests/unit/simulation/components/abilities/test_warhead.py
  - tests/unit/simulation/components/test_component_loader.py
  - tests/unit/simulation/components/test_create_ability_formula_skip.py
  - tests/unit/strategy/data/test_fms_a_audit_fixes.py
  - tests/unit/strategy/data/test_ship_cargo_manager_per_bay.py
  - ... and 1 more
- Heuristically untested symbols (1):
  - ComponentCacheManager.__init__

### game/simulation/components/modifiers.py (Tier 3: TIER_3_APPARENTLY_COVERED, 149 LOC, layer: simulation)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/modifiers/test_invalid_operation_handling.py
  - tests/unit/simulation/components/test_modifiers.py

### game/simulation/entities/projectile.py (Tier 2: TIER_2_PARTIAL, 212 LOC, layer: simulation)
- Total symbols: 6 | Heuristically tested: 5
- Candidate test files (7):
  - tests/unit/ai/test_ai_protocols.py
  - tests/unit/simulation/combat/test_weapon_dispatch_golden.py
  - tests/unit/simulation/entities/test_projectile.py
  - tests/unit/simulation/projectile_guidance/conftest.py
  - tests/unit/simulation/projectile_guidance/test_guidance_behavior.py
  - tests/unit/simulation/projectile_guidance/test_guidance_core.py
  - tests/unit/simulation/test_projectile_manager.py
- Heuristically untested symbols (1):
  - _default_event_logger

### game/simulation/managers/retreat_manager.py (Tier 2: TIER_2_PARTIAL, 280 LOC, layer: simulation)
- Total symbols: 14 | Heuristically tested: 12
- Candidate test files (2):
  - tests/unit/simulation/battle_controller/test_mechanics.py
  - tests/unit/simulation/managers/test_retreat_manager.py
- Heuristically untested symbols (2):
  - RetreatManager.__init__
  - RetreatManager._handle_ship_escaped

### game/strategy/data/fleet_pursuer_tracker.py (Tier 2: TIER_2_PARTIAL, 145 LOC, layer: strategy)
- Total symbols: 9 | Heuristically tested: 7
- Candidate test files (2):
  - tests/unit/strategy/data/test_fleet_order_removal.py
  - tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py
- Heuristically untested symbols (2):
  - FleetPursuerTracker.__init__
  - FleetPursuerTracker._remove_orders_targeting_fleet

### game/strategy/data/order_types.py (Tier 3: TIER_3_APPARENTLY_COVERED, 167 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 6
- Candidate test files (105):
  - tests/unit/fixtures/test_strategy_entities.py
  - tests/unit/strategy/conflict_resolution/test_core.py
  - tests/unit/strategy/data/test_empire_fleet_registration.py
  - tests/unit/strategy/data/test_fleet_order_removal.py
  - tests/unit/strategy/data/test_fleet_order_resolution.py
  - tests/unit/strategy/data/test_order_serializer.py
  - tests/unit/strategy/data/test_order_types_characterization.py
  - tests/unit/strategy/data/test_superweapon_orders.py
  - ... and 97 more

### game/strategy/engine/fleet_movement_engine.py (Tier 2: TIER_2_PARTIAL, 383 LOC, layer: strategy)
- Total symbols: 11 | Heuristically tested: 9
- Candidate test files (9):
  - tests/unit/strategy/engine/test_engine_validation.py
  - tests/unit/strategy/engine/test_fleet_movement_engine_calculate_next_hex.py
  - tests/unit/strategy/engine/test_movement_build_blocking.py
  - tests/unit/strategy/fleet_movement_engine/test_basics.py
  - tests/unit/strategy/fleet_movement_engine/test_batch.py
  - tests/unit/strategy/fleet_movement_engine/test_characterization.py
  - tests/unit/strategy/fleet_movement_engine/test_warp.py
  - tests/unit/strategy/turn_engine/test_dependency_injection.py
  - ... and 1 more
- Heuristically untested symbols (2):
  - FleetMovementEngine.__init__
  - FleetMovementEngine._get_fleet_mutator

### game/strategy/engine/handlers/recover_satellites.py (Tier 0: TIER_0_NO_TESTS, 111 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - RecoverSatellitesCommandHandler
  - RecoverSatellitesCommandHandler.execute
  - RecoverSatellitesCommandHandler._execute_fleet
  - RecoverSatellitesCommandHandler._execute_planet
  - register

### game/strategy/engine/order_handlers/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 45 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/strategy/engine/order_handlers/test_colonize_transfer_no_legacy_substrate.py

### game/strategy/engine/planet_energy_engine.py (Tier 2: TIER_2_PARTIAL, 325 LOC, layer: strategy)
- Total symbols: 14 | Heuristically tested: 8
- Candidate test files (4):
  - tests/unit/strategy/engine/test_engine_validation.py
  - tests/unit/strategy/engine/test_planet_energy_cache.py
  - tests/unit/strategy/engine/test_planet_energy_engine.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
- Heuristically untested symbols (6):
  - _extract_abilities
  - PlanetEnergyEngine.__init__
  - PlanetEnergyEngine._get_planet_mutator
  - PlanetEnergyEngine._get_facility_fingerprint
  - PlanetEnergyEngine._compute_activation_drain
  - PlanetEnergyEngine._cancel_all_draining_components

### game/strategy/engine/water_engine.py (Tier 2: TIER_2_PARTIAL, 73 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/strategy/engine/test_water_engine.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
- Heuristically untested symbols (2):
  - WaterEngine.__init__
  - WaterEngine._process_colony

### game/strategy/generation/__init__.py (Tier 0: TIER_0_NO_TESTS, 23 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/strategy/generation/density/primitives/geometric.py (Tier 3: TIER_3_APPARENTLY_COVERED, 101 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/strategy/generation/density/conftest.py
  - tests/unit/strategy/generation/density/test_geometric.py

### game/strategy/generation/placement_strategies.py (Tier 2: TIER_2_PARTIAL, 210 LOC, layer: strategy)
- Total symbols: 7 | Heuristically tested: 6
- Candidate test files (1):
  - tests/unit/strategy/generation/test_placement_strategies.py
- Heuristically untested symbols (1):
  - DensityBasedPlacementStrategy.__init__

### game/strategy/generation/star_image_registry.py (Tier 2: TIER_2_PARTIAL, 111 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/strategy/generation/test_star_image_registry.py
- Heuristically untested symbols (2):
  - StarImageRegistry.__init__
  - StarImageRegistry._load_from_manifest

### game/strategy/interfaces/battle_resolver.py (Tier 3: TIER_3_APPARENTLY_COVERED, 109 LOC, layer: strategy)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (9):
  - tests/unit/strategy/adapters/test_simulation_adapter.py
  - tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py
  - tests/unit/strategy/conflict_resolution/test_core.py
  - tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py
  - tests/unit/strategy/engine/test_conflict_deployed_group_trigger.py
  - tests/unit/strategy/engine/test_conflict_resolution_event_replay.py
  - tests/unit/strategy/interfaces/test_battle_resolver.py
  - tests/unit/strategy/interfaces/test_battle_resolver_replay_id.py
  - ... and 1 more

### game/strategy/interfaces/engines/movement.py (Tier 0: TIER_0_NO_TESTS, 96 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - IMovementEngine
  - IMovementEngine.collect_movements
  - IMovementEngine.apply_movements
  - IMovementEngine.calculate_next_hex

### game/strategy/services/fleet_warp_resolution.py (Tier 0: TIER_0_NO_TESTS, 98 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - compute_path_for_warp
  - resolve_warp_exit

### game/strategy/services/galaxy_pathfinding_service.py (Tier 3: TIER_3_APPARENTLY_COVERED, 211 LOC, layer: strategy)
- Total symbols: 7 | Heuristically tested: 7
- Candidate test files (7):
  - tests/unit/strategy/pathfinding/test_basic_paths.py
  - tests/unit/strategy/pathfinding/test_edge_cases.py
  - tests/unit/strategy/pathfinding/test_hybrid_and_intercept.py
  - tests/unit/strategy/pathfinding/test_intercept_recursion.py
  - tests/unit/strategy/pathfinding/test_strip_start_hex.py
  - tests/unit/strategy/services/test_galaxy_pathfinding_service.py
  - tests/unit/strategy/test_advanced_fleet_orders.py

### game/strategy/services/modifier_resolver.py (Tier 3: TIER_3_APPARENTLY_COVERED, 69 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/strategy/services/test_modifier_resolver.py

### game/strategy/services/system_destroyer.py (Tier 2: TIER_2_PARTIAL, 187 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/strategy/services/test_system_destroyer.py
- Heuristically untested symbols (1):
  - SystemDestructionResult

### game/strategy/systems/save_game_service.py (Tier 2: TIER_2_PARTIAL, 588 LOC, layer: strategy)
- Total symbols: 20 | Heuristically tested: 17
- Candidate test files (10):
  - tests/unit/strategy/save_game_service/test_built_count_flush_on_save.py
  - tests/unit/strategy/save_game_service/test_error_handling.py
  - tests/unit/strategy/save_game_service/test_load_helpers.py
  - tests/unit/strategy/save_game_service/test_replay_store_instance.py
  - tests/unit/strategy/save_game_service/test_save_load_ops.py
  - tests/unit/strategy/test_auto_save.py
  - tests/unit/systems/test_main_integration.py
  - tests/unit/test_app_bootstrap_invariants.py
  - ... and 2 more
- Heuristically untested symbols (3):
  - SaveGameService._flush_pending_built_counts
  - SaveGameService._validate_save
  - SaveGameService._is_compatible_version

### game/ui/components/table/virtual_table.py (Tier 2: TIER_2_PARTIAL, 696 LOC, layer: ui)
- Total symbols: 22 | Heuristically tested: 16
- Candidate test files (1):
  - tests/unit/ui/components/table/test_virtual_table.py
- Heuristically untested symbols (5):
  - VirtualTable._build_containers
  - VirtualTable._pool_dims_changed
  - VirtualTable._rebuild_row_pool
  - VirtualTable._update_selection_highlights
  - VirtualTable.scroll_bar

### game/ui/fonts.py (Tier 2: TIER_2_PARTIAL, 92 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/test_fonts.py
- Heuristically untested symbols (1):
  - _ensure_cache_valid

### game/ui/panels/race_description_panel.py (Tier 2: TIER_2_PARTIAL, 418 LOC, layer: ui)
- Total symbols: 11 | Heuristically tested: 10
- Candidate test files (1):
  - tests/unit/ui/test_race_description_panel.py
- Heuristically untested symbols (1):
  - RaceDescriptionPanel._tick_field_label

### game/ui/panels/race_identity_panel.py (Tier 2: TIER_2_PARTIAL, 493 LOC, layer: ui)
- Total symbols: 15 | Heuristically tested: 11
- Candidate test files (2):
  - tests/unit/ui/panels/test_race_identity_panel.py
  - tests/unit/ui/screens/test_race_setup_screen.py
- Heuristically untested symbols (4):
  - RaceIdentityPanel._create_race_section
  - RaceIdentityPanel._create_government_section
  - RaceIdentityPanel._create_faction_section
  - RaceIdentityPanel._recreate_dropdown

### game/ui/pygame_gui_patch.py (Tier 2: TIER_2_PARTIAL, 208 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/ui/test_pygame_gui_patch.py
- Heuristically untested symbols (3):
  - _detect_upstream_bug
  - _to_tuple
  - StarshipUIAppearanceTheme.__init__

### game/ui/screens/builder/modifier_config.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 99 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (2):
  - tests/unit/repro_issues/test_slider_increment.py
  - tests/unit/ui/screens/builder/test_modifier_config_size_mount.py

### game/ui/screens/cargo_quick_dialog_controller.py (Tier 2: TIER_2_PARTIAL, 131 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/screens/test_cargo_quick_dialog_controller_widget_purity.py
- Heuristically untested symbols (4):
  - CargoQuickDialogController.__init__
  - CargoQuickDialogController.get_unload_items
  - CargoQuickDialogController.get_load_items
  - CargoQuickDialogController.get_target_planet_id

### game/ui/screens/design_selector_window.py (Tier 2: TIER_2_PARTIAL, 708 LOC, layer: ui)
- Total symbols: 23 | Heuristically tested: 14
- Candidate test files (1):
  - tests/unit/ui/screens/test_design_selector_window.py
- Heuristically untested symbols (9):
  - DesignSelectorUiBuilder
  - DesignSelectorUiBuilder.build
  - DesignSelectorWindow._create_main_list
  - DesignSelectorWindow._create_bottom_buttons
  - DesignSelectorWindow._get_role_filter_options
  - DesignSelectorWindow._get_type_filter_options
  - DesignSelectorWindow._get_class_filter_options
  - DesignSelectorWindow._sanitize_object_id
  - DesignSelectorWindow.update

### game/ui/screens/keybindings_scene.py (Tier 2: TIER_2_PARTIAL, 584 LOC, layer: ui)
- Total symbols: 25 | Heuristically tested: 11
- Candidate test files (1):
  - tests/unit/ui/screens/test_keybindings_scene.py
- Heuristically untested symbols (14):
  - _build_key_name_map
  - KeybindingsScene.__init__
  - KeybindingsScene._build_ui
  - KeybindingsScene._build_action_rows
  - KeybindingsScene._build_action_row
  - KeybindingsScene._build_footer
  - KeybindingsScene._clear_ui
  - KeybindingsScene._apply_binding
  - KeybindingsScene._refresh_action_row
  - KeybindingsScene._draw_capture_overlay
  - KeybindingsScene._handle_button_press
  - KeybindingsScene._handle_dialog_confirmed
  - KeybindingsScene._on_reset_all_clicked
  - KeybindingsScene._refresh_all_rows

### game/ui/screens/new_game_setup_ui_builder.py (Tier 0: TIER_0_NO_TESTS, 41 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - NewGameSetupUiBuilder
  - NewGameSetupUiBuilder.build

### game/ui/screens/planet_list_filter_manager.py (Tier 2: TIER_2_PARTIAL, 148 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 8
- Candidate test files (1):
  - tests/unit/ui/screens/test_planet_list_filter_manager.py
- Heuristically untested symbols (1):
  - PlanetListFilterManager.__init__

### game/ui/screens/setup_screen.py (Tier 2: TIER_2_PARTIAL, 292 LOC, layer: ui)
- Total symbols: 18 | Heuristically tested: 16
- Candidate test files (2):
  - tests/unit/ui/screens/test_setup_screen.py
  - tests/unit/ui/test_scene_protocol.py
- Heuristically untested symbols (2):
  - BattleSetupScreen.get_team_display_groups
  - BattleSetupScreen._handle_action_buttons

### game/ui/screens/species_selector_mixin.py (Tier 0: TIER_0_NO_TESTS, 163 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - build_species_selector
  - get_selected_race_id
  - load_race_config
  - RaceConfigResolverMixin
  - RaceConfigResolverMixin._get_active_race_config

### game/ui/screens/test_lab/details/panel.py (Tier 0: TIER_0_NO_TESTS, 216 LOC, layer: ui)
- Total symbols: 8 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (8):
  - TestRunDetailsPanel
  - TestRunDetailsPanel.__init__
  - TestRunDetailsPanel.set_run
  - TestRunDetailsPanel.clear
  - TestRunDetailsPanel._calculate_scroll
  - TestRunDetailsPanel.handle_event
  - TestRunDetailsPanel._build_ctx
  - TestRunDetailsPanel.draw

### game/ui/screens/test_lab/renderer/metadata_panel.py (Tier 2: TIER_2_PARTIAL, 221 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/screens/test_lab/renderer/test_metadata_panel.py
- Heuristically untested symbols (1):
  - MetadataPanel.__init__

### game/ui/screens/test_lab/test_executor.py (Tier 2: TIER_2_PARTIAL, 393 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/test_lab/test_batch_skip.py
  - tests/unit/test_lab/test_visual_run.py
- Heuristically untested symbols (5):
  - TestLabExecutor.run_visual
  - TestLabExecutor.run_visual_baseline
  - TestLabExecutor._run_scenario_via_run_battle
  - TestLabExecutor.run_all
  - TestLabExecutor.continue_batch

### game/ui/services/ship_io_adapter.py (Tier 2: TIER_2_PARTIAL, 100 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/ui/services/test_ship_io_adapter.py
- Heuristically untested symbols (1):
  - ShipIOAdapter.__init__

### game/ui/utils/json_diff.py (Tier 2: TIER_2_PARTIAL, 113 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/ui/widgets/test_scrollable_json_panel.py
- Heuristically untested symbols (2):
  - compute_json_diff
  - _mark_all_paths
