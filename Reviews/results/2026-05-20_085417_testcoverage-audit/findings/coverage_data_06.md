# Coverage Data — Shard 06

**Coverage source:** heuristic
**File count:** 38 | **LOC estimate:** 9573
**Tiers:** 0=8 1=2 2=23 3=5

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/ai/interfaces/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 30 LOC, layer: ai)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/simulation/factories/test_ai_factory.py

### game/ai/spatial_behaviors/patrol_zone.py (Tier 2: TIER_2_PARTIAL, 57 LOC, layer: ai)
- Total symbols: 3 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py
- Heuristically untested symbols (1):
  - PatrolZoneBehavior.__init__

### game/app.py (Tier 2: TIER_2_PARTIAL, 531 LOC, layer: game_root)
- Total symbols: 64 | Heuristically tested: 37
- Candidate test files (6):
  - tests/unit/test_app_create_workshop_context.py
  - tests/unit/test_app_delegators.py
  - tests/unit/test_app_public_api.py
  - tests/unit/ui/screens/test_strategy_menu_actions.py
  - tests/unit/ui/screens/test_viewing_empire_anchor.py
  - tests/unit/workshop/test_workshop_ship_io_facade_state.py
- Heuristically untested symbols (21):
  - Game._get_menu_button_config
  - Game._route_get
  - Game._route_set
  - Game.active_scene
  - Game.active_scene
  - Game.builder_scene
  - Game.builder_scene
  - Game.menu_ui_manager
  - Game.show_exit_dialog
  - Game.show_exit_dialog
  - Game.showing_load_menu
  - Game.showing_load_menu
  - Game.showing_race_setup
  - Game.showing_race_setup
  - Game.showing_new_game_setup
  - ... and 6 more

### game/core/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 176 LOC, layer: core)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (12):
  - tests/unit/ai/test_fighter_controller.py
  - tests/unit/core/profiling/test_persistence.py
  - tests/unit/core/test_registry_cache.py
  - tests/unit/core/test_simulation_constants.py
  - tests/unit/core/test_spectrum_math.py
  - tests/unit/strategy/save_game_service/conftest.py
  - tests/unit/strategy/save_game_service/test_error_handling.py
  - tests/unit/strategy/save_game_service/test_load_helpers.py
  - ... and 4 more

### game/engine/spatial.py (Tier 3: TIER_3_APPARENTLY_COVERED, 61 LOC, layer: engine)
- Total symbols: 7 | Heuristically tested: 7
- Candidate test files (10):
  - tests/unit/ai/test_ai.py
  - tests/unit/ai/test_ai_capabilities_cache.py
  - tests/unit/ai/test_capability_cache_pdc.py
  - tests/unit/ai/test_fighter_controller.py
  - tests/unit/engine/test_spatial_exact.py
  - tests/unit/simulation/combat/test_ship_death_at_zero_hp.py
  - tests/unit/simulation/factories/test_ai_factory.py
  - tests/unit/systems/test_spatial.py
  - ... and 2 more

### game/run_loop.py (Tier 2: TIER_2_PARTIAL, 223 LOC, layer: game_root)
- Total symbols: 11 | Heuristically tested: 9
- Candidate test files (1):
  - tests/unit/test_run_loop.py
- Heuristically untested symbols (2):
  - RunLoop.__init__
  - RunLoop._boot_set_resolution

### game/simulation/components/abilities/superweapons.py (Tier 0: TIER_0_NO_TESTS, 116 LOC, layer: simulation)
- Total symbols: 10 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (10):
  - SuperweaponMarker
  - SuperweaponMarker._parse_attrs
  - SuperweaponMarker.get_ui_rows
  - SuperweaponMarker.get_primary_value
  - DestroyPlanet
  - DestroyStar
  - OpenWarpPoint
  - CloseWarpPoint
  - CreateDysonSphere
  - SelfDestruct

### game/simulation/components/modifier_effects.py (Tier 3: TIER_3_APPARENTLY_COVERED, 270 LOC, layer: simulation)
- Total symbols: 10 | Heuristically tested: 10
- Candidate test files (17):
  - tests/unit/entities/test_components.py
  - tests/unit/modifiers/test_formula_edge_cases.py
  - tests/unit/modifiers/test_formula_error_handling.py
  - tests/unit/modifiers/test_formula_validation.py
  - tests/unit/modifiers/test_modifier_effect.py
  - tests/unit/modifiers/test_modifier_effect_evaluator.py
  - tests/unit/modifiers/test_multi_ability_effects.py
  - tests/unit/simulation/combat/test_fleet_aura_extended.py
  - ... and 9 more

### game/simulation/entities/ship_serialization.py (Tier 3: TIER_3_APPARENTLY_COVERED, 266 LOC, layer: simulation)
- Total symbols: 6 | Heuristically tested: 6
- Candidate test files (13):
  - tests/unit/combat_lab/services/test_ab_battle_runner.py
  - tests/unit/entities/test_ship.py
  - tests/unit/simulation/battle_controller/test_outcome_emission.py
  - tests/unit/simulation/entities/test_ship_external_stats_serialization_guard.py
  - tests/unit/simulation/entities/test_ship_serialization.py
  - tests/unit/simulation/entities/test_ship_shield_bonus_add.py
  - tests/unit/simulation/systems/test_battle_engine_modifier_stack.py
  - tests/unit/simulation/test_battle_runner_component_hp.py
  - ... and 5 more

### game/simulation/interfaces/entity_protocols.py (Tier 0: TIER_0_NO_TESTS, 487 LOC, layer: simulation)
- Total symbols: 68 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (68):
  - ICombatShip
  - ICombatShip.name
  - ICombatShip.team_id
  - ICombatShip.vehicle_type
  - ICombatShip.angle
  - ICombatShip.position
  - ICombatShip.velocity
  - ICombatShip.radius
  - ICombatShip.mass
  - ICombatShip.hp
  - ICombatShip.max_hp
  - ICombatShip.is_alive
  - ICombatShip.is_derelict
  - ICombatShip.current_shields
  - ICombatShip.max_shields
  - ... and 53 more

### game/simulation/systems/tactical_mine_resolver.py (Tier 2: TIER_2_PARTIAL, 597 LOC, layer: simulation)
- Total symbols: 15 | Heuristically tested: 7
- Candidate test files (2):
  - tests/unit/simulation/systems/test_tactical_mine_resolver.py
  - tests/unit/strategy/combat/test_battle_assembly_third_party_mines.py
- Heuristically untested symbols (8):
  - TacticalMineEvent
  - TacticalMineResolver._evaluate_mine_against_ships
  - TacticalMineResolver._laserhead_per_tick
  - TacticalMineResolver._apply_damage
  - _sum_warhead_damage
  - _extract_laserhead
  - _extract_hull_hp
  - _scatter_in_box

### game/strategy/data/build_context.py (Tier 2: TIER_2_PARTIAL, 62 LOC, layer: strategy)
- Total symbols: 7 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/strategy/data/test_build_context.py
- Heuristically untested symbols (2):
  - BuildContext.construction_queue
  - BuildContext.has_space_shipyard

### game/strategy/data/order_serializer.py (Tier 2: TIER_2_PARTIAL, 243 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/strategy/data/test_order_serializer.py
- Heuristically untested symbols (1):
  - OrderSerializer._deserialize_single_order

### game/strategy/data/planet_gen.py (Tier 2: TIER_2_PARTIAL, 427 LOC, layer: strategy)
- Total symbols: 11 | Heuristically tested: 7
- Candidate test files (2):
  - tests/unit/strategy/data/test_planet_classification_logic.py
  - tests/unit/strategy/data/test_planet_gen.py
- Heuristically untested symbols (4):
  - PlanetGenerator.__init__
  - PlanetGenerator._collect_star_exclusion_zones
  - PlanetGenerator._create_planet_objects
  - PlanetGenerator._create_single_planet

### game/strategy/engine/handlers/lay_mines.py (Tier 0: TIER_0_NO_TESTS, 168 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - LayMinesCommandHandler
  - LayMinesCommandHandler.execute
  - LayMinesCommandHandler._execute_fleet
  - LayMinesCommandHandler._execute_planet
  - register

### game/strategy/facade/slices/_facade_state.py (Tier 2: TIER_2_PARTIAL, 188 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 8
- Candidate test files (7):
  - tests/unit/strategy/engine/test_game_session_projection_boundary.py
  - tests/unit/strategy/facade/slices/test_facade_state.py
  - tests/unit/strategy/facade/test_designs_by_empire_through_catalog.py
  - tests/unit/strategy/facade/test_facade_state_proj411_caches.py
  - tests/unit/strategy/services/test_empire_economy_caching.py
  - tests/unit/ui/screens/test_gather_planets_caching.py
  - tests/unit/workshop/test_workshop_ship_io_facade_state.py
- Heuristically untested symbols (2):
  - FacadeSessionState.seed_planet_index
  - FacadeSessionState.seed_race_registry

### game/strategy/services/ability_iterator.py (Tier 2: TIER_2_PARTIAL, 339 LOC, layer: strategy)
- Total symbols: 15 | Heuristically tested: 7
- Candidate test files (1):
  - tests/unit/strategy/services/test_ability_iterator.py
- Heuristically untested symbols (8):
  - _iter_hex_filtered_sources
  - _facility_provider
  - _storm_provider
  - _star_provider
  - _planet_intrinsic_provider
  - _fleet_provider
  - _system_archetype_provider
  - _warp_point_provider

### game/strategy/services/combat_modifier_collector.py (Tier 2: TIER_2_PARTIAL, 195 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/strategy/combat/test_spec_compiler.py
  - tests/unit/strategy/services/test_combat_modifier_collector.py
- Heuristically untested symbols (1):
  - _entry_scope

### game/strategy/services/replay_verification_sidecar.py (Tier 3: TIER_3_APPARENTLY_COVERED, 173 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 8
- Candidate test files (2):
  - tests/unit/strategy/services/test_replay_verification_coordinator.py
  - tests/unit/strategy/services/test_replay_verification_sidecar.py

### game/strategy/validation/colonize_validator.py (Tier 2: TIER_2_PARTIAL, 166 LOC, layer: strategy)
- Total symbols: 7 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/strategy/engine/test_multi_pod_colonization.py
- Heuristically untested symbols (4):
  - ColonizeValidator.validate
  - ColonizeValidator.fleet_has_drop_pod
  - ColonizeValidator._validate_drop_pod_availability
  - ColonizeValidator.find_ship_with_drop_pod

### game/strategy/validation/planet_order_validator.py (Tier 3: TIER_3_APPARENTLY_COVERED, 124 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/strategy/engine/test_planet_command_handlers.py
  - tests/unit/strategy/validation/test_planet_order_validator.py

### game/ui/assets/ship_theme_manager.py (Tier 2: TIER_2_PARTIAL, 453 LOC, layer: ui)
- Total symbols: 20 | Heuristically tested: 17
- Candidate test files (2):
  - tests/unit/ui/assets/test_ship_theme_manager.py
  - tests/unit/ui/test_race_asset_loader.py
- Heuristically untested symbols (3):
  - ShipThemeManager.__init__
  - ShipThemeManager._validate_image_size
  - ShipThemeManager.get_theme_description

### game/ui/screens/build_queue_panel_factory.py (Tier 2: TIER_2_PARTIAL, 586 LOC, layer: ui)
- Total symbols: 14 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/ui/screens/test_build_queue_panel_factory.py
- Heuristically untested symbols (10):
  - _pause_button_label
  - BuildQueuePanels
  - BuildQueuePanelFactory.__init__
  - BuildQueuePanelFactory._create_background
  - BuildQueuePanelFactory._create_queue_selector_panel
  - BuildQueuePanelFactory._create_design_report_panel
  - BuildQueuePanelFactory._create_items_list_panel
  - BuildQueuePanelFactory._create_build_queue_panel
  - BuildQueuePanelFactory._create_filter_panel
  - BuildQueuePanelFactory._create_bottom_bar

### game/ui/screens/builder/structure_list_items.py (Tier 2: TIER_2_PARTIAL, 630 LOC, layer: ui)
- Total symbols: 23 | Heuristically tested: 9
- Candidate test files (3):
  - tests/unit/builder/test_builder_structure_features.py
  - tests/unit/ui/test_modifier_icons.py
  - tests/unit/ui/test_structure_visibility.py
- Heuristically untested symbols (14):
  - _rebuild_modifier_icons_for_item
  - IndividualComponentItem.__init__
  - IndividualComponentItem.update
  - IndividualComponentItem._rebuild_modifier_icons
  - IndividualComponentItem._create_tree_line
  - IndividualComponentItem.get_abs_rect
  - IndividualComponentItem.set_move_buttons_enabled
  - LayerComponentItem.__init__
  - LayerComponentItem.update
  - LayerComponentItem._rebuild_modifier_icons
  - LayerComponentItem.set_move_buttons_enabled
  - LayerComponentItem.get_abs_rect
  - LayerHeaderItem.__init__
  - LayerHeaderItem.update

### game/ui/screens/builder/weapons_panel.py (Tier 2: TIER_2_PARTIAL, 321 LOC, layer: ui)
- Total symbols: 15 | Heuristically tested: 6
- Candidate test files (2):
  - tests/unit/ui/screens/builder/test_weapons_panel.py
  - tests/unit/ui/test_weapons_report_layout.py
- Heuristically untested symbols (8):
  - WeaponsReportPanel._setup_filter_buttons
  - WeaponsReportPanel._update_button_colors
  - WeaponsReportPanel._on_weapons_updated
  - WeaponsReportPanel._on_filter_changed
  - WeaponsReportPanel.hovered_weapon
  - WeaponsReportPanel.set_target
  - WeaponsReportPanel.clear_target
  - WeaponsReportPanel.update

### game/ui/screens/builder/weapons_viewmodel.py (Tier 2: TIER_2_PARTIAL, 494 LOC, layer: ui)
- Total symbols: 20 | Heuristically tested: 17
- Candidate test files (1):
  - tests/unit/ui/builder/test_weapons_viewmodel.py
- Heuristically untested symbols (3):
  - WeaponsViewModel.__init__
  - WeaponsViewModel._get_all_weapons
  - WeaponsViewModel.calculate_tooltip_data

### game/ui/screens/data_list_window_mixin.py (Tier 2: TIER_2_PARTIAL, 130 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/screens/test_planet_list_components.py
- Heuristically untested symbols (3):
  - DataListWindowMixin._toggle_column
  - DataListWindowMixin._save_preset
  - DataListWindowMixin._sync_slider_text

### game/ui/screens/galaxy_test/screen.py (Tier 2: TIER_2_PARTIAL, 288 LOC, layer: ui)
- Total symbols: 16 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/screens/test_galaxy_test_screen.py
- Heuristically untested symbols (13):
  - GalaxyTestScreen._create_menu_ui
  - GalaxyTestScreen._create_galaxy_ui
  - GalaxyTestScreen._create_system_ui
  - GalaxyTestScreen.update
  - GalaxyTestScreen.draw
  - GalaxyTestScreen.handle_event
  - GalaxyTestScreen._handle_button_click
  - GalaxyTestScreen._go_to_menu
  - GalaxyTestScreen._go_to_galaxy_mode
  - GalaxyTestScreen._go_to_system_mode
  - GalaxyTestScreen._on_close
  - GalaxyTestScreen.handle_resize
  - GalaxyTestScreen.update_input

### game/ui/screens/gravity_target_editor.py (Tier 0: TIER_0_NO_TESTS, 220 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (9):
  - GravityTargetEditor
  - GravityTargetEditor.__init__
  - GravityTargetEditor._build_ui
  - GravityTargetEditor.update
  - GravityTargetEditor._button_handlers
  - GravityTargetEditor._on_apply
  - GravityTargetEditor._set_species_ideal
  - GravityTargetEditor._set_match_current
  - GravityTargetEditor._clear_target

### game/ui/screens/race_setup/controller.py (Tier 2: TIER_2_PARTIAL, 499 LOC, layer: ui)
- Total symbols: 26 | Heuristically tested: 15
- Candidate test files (2):
  - tests/unit/ui/screens/race_setup/test_controller.py
  - tests/unit/ui/screens/test_race_setup_delegate_factory.py
- Heuristically untested symbols (11):
  - RaceSetupController.on_race_browser_cancelled
  - RaceSetupController.populate_ui_from_config
  - RaceSetupController.on_randomize
  - RaceSetupController.randomize_identity
  - RaceSetupController.randomize_visuals
  - RaceSetupController.randomize_ships
  - RaceSetupController.randomize_environment
  - RaceSetupController.randomize_aptitudes
  - RaceSetupController.randomize_all
  - RaceSetupController.on_overwrite_save
  - RaceSetupController.on_save_dialog_cancel

### game/ui/screens/strategy_render/background.py (Tier 0: TIER_0_NO_TESTS, 58 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - BackgroundLayer
  - BackgroundLayer.__init__
  - BackgroundLayer._load_background
  - BackgroundLayer.draw

### game/ui/screens/strategy_windows/ship_picker.py (Tier 0: TIER_0_NO_TESTS, 43 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - ShipPickerStub
  - ShipPickerStub.__init__
  - ShipPickerStub.show

### game/ui/screens/test_lab/renderer/category_panel.py (Tier 0: TIER_0_NO_TESTS, 157 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - CategoryPanel
  - CategoryPanel.__init__
  - CategoryPanel.draw

### game/ui/screens/workshop_data_reloader.py (Tier 2: TIER_2_PARTIAL, 197 LOC, layer: ui)
- Total symbols: 11 | Heuristically tested: 10
- Candidate test files (1):
  - tests/unit/ui/screens/test_workshop_data_reloader.py
- Heuristically untested symbols (1):
  - WorkshopDataReloader._refresh_ui_after_data_reload

### game/ui/services/game_settings.py (Tier 2: TIER_2_PARTIAL, 94 LOC, layer: ui)
- Total symbols: 11 | Heuristically tested: 7
- Candidate test files (1):
  - tests/unit/ui/services/test_game_settings.py
- Heuristically untested symbols (3):
  - GameSettings.__init__
  - GameSettings._load
  - GameSettings.save

### game/ui/services/image/provider.py (Tier 0: TIER_0_NO_TESTS, 82 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - ImageProvider
  - ImageProvider.generate_image

### game/ui/services/ship_factory.py (Tier 2: TIER_2_PARTIAL, 185 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/ui/services/test_ship_factory.py
- Heuristically untested symbols (3):
  - ShipFactory.__init__
  - ShipFactory._get_registries
  - ShipFactory.setup_formation

### game/ui/widgets/preference_row.py (Tier 2: TIER_2_PARTIAL, 237 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/ui/widgets/test_preference_row.py
- Heuristically untested symbols (5):
  - PreferenceRow.__init__
  - PreferenceRow._build_widgets
  - PreferenceRow.current_preference
  - PreferenceRow.set_preference
  - PreferenceRow.owns_event
