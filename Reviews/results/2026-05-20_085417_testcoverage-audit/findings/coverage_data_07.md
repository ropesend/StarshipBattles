# Coverage Data — Shard 07

**Coverage source:** heuristic
**File count:** 47 | **LOC estimate:** 9578
**Tiers:** 0=13 1=1 2=23 3=10

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/ai/combat_utils.py (Tier 3: TIER_3_APPARENTLY_COVERED, 244 LOC, layer: ai)
- Total symbols: 9 | Heuristically tested: 9
- Candidate test files (2):
  - tests/unit/ai/test_combat_utils.py
  - tests/unit/ai/test_target_evaluator_edge_cases.py

### game/ai/spatial_behaviors/__init__.py (Tier 3: TIER_3_APPARENTLY_COVERED, 66 LOC, layer: ai)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py

### game/ai/spatial_behaviors/battle_line.py (Tier 2: TIER_2_PARTIAL, 98 LOC, layer: ai)
- Total symbols: 3 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py
- Heuristically untested symbols (1):
  - BattleLineBehavior.__init__

### game/core/constants.py (Tier 3: TIER_3_APPARENTLY_COVERED, 91 LOC, layer: core)
- Total symbols: 6 | Heuristically tested: 6
- Candidate test files (84):
  - tests/unit/ai/test_ai_protocols.py
  - tests/unit/ai/test_controllable_adapter_edge_cases.py
  - tests/unit/ai/test_movement_and_ai.py
  - tests/unit/ai/test_target_evaluator_edge_cases.py
  - tests/unit/ai/test_target_evaluator_rules.py
  - tests/unit/ai/test_targeting_rules.py
  - tests/unit/builder/test_builder_validation.py
  - tests/unit/builder/test_bulk_add.py
  - ... and 76 more

### game/core/exceptions.py (Tier 3: TIER_3_APPARENTLY_COVERED, 544 LOC, layer: core)
- Total symbols: 38 | Heuristically tested: 38
- Candidate test files (126):
  - tests/unit/abilities/test_ability_layer_scope.py
  - tests/unit/abilities/test_strategic_movement.py
  - tests/unit/abilities/test_warp_jump.py
  - tests/unit/assets/test_asset_manager_resolutions.py
  - tests/unit/builder/test_ship_validator_di.py
  - tests/unit/core/registry/conftest.py
  - tests/unit/core/registry/test_registry_features.py
  - tests/unit/core/registry/test_registry_operations.py
  - ... and 118 more

### game/core/math.py (Tier 2: TIER_2_PARTIAL, 280 LOC, layer: core)
- Total symbols: 33 | Heuristically tested: 24
- Candidate test files (73):
  - tests/unit/ai/spatial_behaviors/test_anti_clumping.py
  - tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py
  - tests/unit/ai/test_ai_controller_edge_cases.py
  - tests/unit/ai/test_ai_controller_unit.py
  - tests/unit/ai/test_ai_protocols.py
  - tests/unit/ai/test_behavior_units.py
  - tests/unit/ai/test_carrier_controller.py
  - tests/unit/ai/test_combat_utils.py
  - ... and 65 more
- Heuristically untested symbols (9):
  - Vector2.__add__
  - Vector2.__radd__
  - Vector2.__sub__
  - Vector2.__rsub__
  - Vector2.__mul__
  - Vector2.__rmul__
  - Vector2.__truediv__
  - Vector2.__neg__
  - Vector2.__iter__

### game/core/protocols/common.py (Tier 0: TIER_0_NO_TESTS, 47 LOC, layer: core)
- Total symbols: 7 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (7):
  - _has_attrs
  - ILocatable
  - ILocatable.location
  - INamed
  - INamed.name
  - IOwnable
  - IOwnable.owner_id

### game/core/registry_cache.py (Tier 3: TIER_3_APPARENTLY_COVERED, 83 LOC, layer: core)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/core/test_registry_cache.py

### game/core/resources.py (Tier 3: TIER_3_APPARENTLY_COVERED, 197 LOC, layer: core)
- Total symbols: 12 | Heuristically tested: 12
- Candidate test files (21):
  - tests/unit/core/resources_registry/test_integration.py
  - tests/unit/core/resources_registry/test_loading.py
  - tests/unit/core/test_constants.py
  - tests/unit/core/test_pure_loaders.py
  - tests/unit/core/test_resource_catalog.py
  - tests/unit/core/test_resource_catalog_mass_per_unit.py
  - tests/unit/core/test_resources.py
  - tests/unit/entities/test_ship_di.py
  - ... and 13 more

### game/engine/physics.py (Tier 2: TIER_2_PARTIAL, 109 LOC, layer: engine)
- Total symbols: 9 | Heuristically tested: 7
- Candidate test files (3):
  - tests/unit/simulation/entities/test_ship_physics.py
  - tests/unit/systems/test_physics.py
  - tests/unit/systems/test_physics_edge_cases.py

### game/simulation/components/abilities/__init__.py (Tier 3: TIER_3_APPARENTLY_COVERED, 393 LOC, layer: simulation)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (16):
  - tests/unit/abilities/test_strategic_movement.py
  - tests/unit/abilities/test_warp_jump.py
  - tests/unit/entities/test_abilities.py
  - tests/unit/entities/test_ability_interface.py
  - tests/unit/entities/test_ship_stat_querier.py
  - tests/unit/modifiers/test_pipeline_unification.py
  - tests/unit/regressions/test_bug_regressions_2026_01.py
  - tests/unit/simulation/abilities/test_cargo_storage.py
  - ... and 8 more

### game/simulation/components/abilities/markers.py (Tier 2: TIER_2_PARTIAL, 172 LOC, layer: simulation)
- Total symbols: 24 | Heuristically tested: 21
- Candidate test files (1):
  - tests/unit/simulation/components/abilities/test_markers.py
- Heuristically untested symbols (3):
  - MultiplexTrackingAbility._parse_attrs
  - VehicleStorageAbility._parse_attrs
  - PodStorageAbility._parse_attrs

### game/simulation/components/abilities/planetary/stabilizers.py (Tier 0: TIER_0_NO_TESTS, 180 LOC, layer: simulation)
- Total symbols: 12 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (12):
  - GeologicStabilizerAbility
  - GeologicStabilizerAbility.__init__
  - GeologicStabilizerAbility.get_primary_value
  - GeologicStabilizerAbility.get_ui_rows
  - StellarStabilizerAbility
  - StellarStabilizerAbility.__init__
  - StellarStabilizerAbility.get_primary_value
  - StellarStabilizerAbility.get_ui_rows
  - WarpFieldStabilizerAbility
  - WarpFieldStabilizerAbility.__init__
  - WarpFieldStabilizerAbility.get_primary_value
  - WarpFieldStabilizerAbility.get_ui_rows

### game/simulation/components/abilities/vehicle_bay.py (Tier 2: TIER_2_PARTIAL, 89 LOC, layer: simulation)
- Total symbols: 6 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/strategy/data/test_vehicle_bay.py
- Heuristically untested symbols (4):
  - VehicleBayAbility._parse_attrs
  - VehicleBayAbility.recalculate
  - VehicleBayAbility.get_primary_value
  - VehicleBayAbility.get_ui_rows

### game/simulation/components/modifier_introspection.py (Tier 3: TIER_3_APPARENTLY_COVERED, 311 LOC, layer: simulation)
- Total symbols: 6 | Heuristically tested: 6
- Candidate test files (2):
  - tests/unit/modifiers/test_modifier_introspection.py
  - tests/unit/simulation/components/test_modifier_introspection.py

### game/strategy/combat/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 6 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (2):
  - tests/unit/strategy/combat/test_battle_assembly.py
  - tests/unit/strategy/services/test_combat_modifier_collector.py

### game/strategy/data/fleet_capability_calculator.py (Tier 2: TIER_2_PARTIAL, 268 LOC, layer: strategy)
- Total symbols: 13 | Heuristically tested: 11
- Candidate test files (4):
  - tests/unit/strategy/data/test_fleet_capability_calculator.py
  - tests/unit/strategy/data/test_fms_a_audit_fixes.py
  - tests/unit/strategy/test_fleet_capability_calculator.py
  - tests/unit/strategy/test_fleet_capability_calculator_di.py
- Heuristically untested symbols (2):
  - _get_ship_component_registry
  - FleetCapabilityCalculator._get_registry

### game/strategy/data/fleet_hierarchy.py (Tier 2: TIER_2_PARTIAL, 185 LOC, layer: strategy)
- Total symbols: 15 | Heuristically tested: 14
- Candidate test files (10):
  - tests/unit/strategy/data/test_fleet_hierarchy.py
  - tests/unit/strategy/data/test_fleet_hierarchy_integration.py
  - tests/unit/strategy/data/test_group_policies.py
  - tests/unit/strategy/data/test_group_policy_registry_characterization.py
  - tests/unit/strategy/data/test_squadron_characterization.py
  - tests/unit/strategy/facade/test_fleet_hierarchy_dto.py
  - tests/unit/strategy/services/test_deployment_zone_calculator.py
  - tests/unit/strategy/services/test_fleet_write_service.py
  - ... and 2 more
- Heuristically untested symbols (1):
  - FleetHierarchyNode.__init__

### game/strategy/engine/atmosphere_engine.py (Tier 2: TIER_2_PARTIAL, 143 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 3
- Candidate test files (3):
  - tests/unit/strategy/engine/test_atmosphere_engine.py
  - tests/unit/strategy/engine/test_engine_validation.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
- Heuristically untested symbols (3):
  - AtmosphereEngine.__init__
  - AtmosphereEngine._get_planet_mutator
  - AtmosphereEngine._process_colony

### game/strategy/engine/handlers/transfer.py (Tier 2: TIER_2_PARTIAL, 142 LOC, layer: strategy)
- Total symbols: 3 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/strategy/engine/test_transfer_handler_fleet_to_fleet.py
- Heuristically untested symbols (1):
  - register

### game/strategy/engine/order_handlers/colonize.py (Tier 2: TIER_2_PARTIAL, 210 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/strategy/engine/order_handlers/test_colonize_handler.py
- Heuristically untested symbols (1):
  - ColonizeHandler.supported_order_types

### game/strategy/engine/session/bootstrap.py (Tier 2: TIER_2_PARTIAL, 322 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/strategy/engine/session/test_bootstrap.py
- Heuristically untested symbols (2):
  - build_event_handler
  - handler

### game/strategy/engine/superweapon_handlers/close_warp_point.py (Tier 0: TIER_0_NO_TESTS, 117 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - _parse_close_target
  - process_close_warp_point
  - _precheck
  - _effect

### game/strategy/generation/star_generator.py (Tier 0: TIER_0_NO_TESTS, 471 LOC, layer: strategy)
- Total symbols: 15 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (15):
  - StarGenerator
  - StarGenerator.__init__
  - StarGenerator._get_image_id
  - StarGenerator._generate_mass
  - StarGenerator._determine_type_and_radius
  - StarGenerator._compute_stefan_boltzmann_type
  - StarGenerator._roll_star_type
  - StarGenerator._kelvin_to_rgb
  - StarGenerator._map_solar_radius_to_hex_radius
  - StarGenerator._generate_spectrum
  - StarGenerator.generate_system_stars
  - StarGenerator._generate_companions
  - StarGenerator.generate_from_blueprint
  - StarGenerator._generate_random_stars
  - StarGenerator._generate_mass_constrained

### game/strategy/interfaces/engines/terraforming.py (Tier 0: TIER_0_NO_TESTS, 72 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (6):
  - IQualityEngine
  - IQualityEngine.process_quality_improvement
  - IAtmosphereEngine
  - IAtmosphereEngine.process_atmosphere
  - IWaterEngine
  - IWaterEngine.process_water_modification

### game/strategy/services/ability_sources/planet_intrinsic.py (Tier 0: TIER_0_NO_TESTS, 91 LOC, layer: strategy)
- Total symbols: 9 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (9):
  - PlanetIntrinsicAbilitySource
  - PlanetIntrinsicAbilitySource.source_kind
  - PlanetIntrinsicAbilitySource.source_label
  - PlanetIntrinsicAbilitySource.source_id
  - PlanetIntrinsicAbilitySource.owner_id
  - PlanetIntrinsicAbilitySource.get_abilities
  - PlanetIntrinsicAbilitySource.affects_hex
  - PlanetIntrinsicAbilitySource.affects_system
  - PlanetIntrinsicAbilitySource.get_activation_state

### game/strategy/services/empire_economy_service.py (Tier 2: TIER_2_PARTIAL, 96 LOC, layer: strategy)
- Total symbols: 3 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/strategy/services/test_empire_economy_caching.py
  - tests/unit/strategy/services/test_empire_economy_service.py
- Heuristically untested symbols (1):
  - EmpireEconomyService.__init__

### game/strategy/systems/design_repository.py (Tier 2: TIER_2_PARTIAL, 509 LOC, layer: strategy)
- Total symbols: 21 | Heuristically tested: 16
- Candidate test files (16):
  - tests/unit/strategy/design_catalog/test_cache_invalidation.py
  - tests/unit/strategy/design_catalog/test_catalog.py
  - tests/unit/strategy/design_catalog/test_filter_designs.py
  - tests/unit/strategy/design_catalog/test_search_designs.py
  - tests/unit/strategy/design_repository/test_load_design_data.py
  - tests/unit/strategy/design_repository/test_repository.py
  - tests/unit/strategy/design_repository/test_save_design.py
  - tests/unit/strategy/design_repository/test_scan_designs.py
  - ... and 8 more
- Heuristically untested symbols (5):
  - DesignLoadResult.invalid_schema
  - DesignLoadResult.permission_denied
  - DesignLoadResult.io_error
  - DesignRepository.has_design
  - DesignRepository._sanitize_design_id

### game/ui/components/filters/__init__.py (Tier 0: TIER_0_NO_TESTS, 3 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/ui/panels/build_queue_controller.py (Tier 2: TIER_2_PARTIAL, 723 LOC, layer: ui)
- Total symbols: 23 | Heuristically tested: 18
- Candidate test files (3):
  - tests/unit/strategy/engine/test_production_repro.py
  - tests/unit/ui/panels/test_build_queue_catalog_threading.py
  - tests/unit/ui/panels/test_build_queue_controller.py
- Heuristically untested symbols (5):
  - BuildQueueController._get_target_planet_id
  - BuildQueueController._add_to_single_queue
  - BuildQueueController._add_item_with_target_planet
  - BuildQueueController._add_to_multiple_queues
  - BuildQueueController._add_to_fallback

### game/ui/panels/empire_treasury_panel.py (Tier 2: TIER_2_PARTIAL, 370 LOC, layer: ui)
- Total symbols: 14 | Heuristically tested: 7
- Candidate test files (1):
  - tests/unit/ui/panels/test_empire_treasury_panel.py
- Heuristically untested symbols (7):
  - _get_planetary_ids
  - EmpireTreasuryPanel.__init__
  - EmpireTreasuryPanel._build_ui
  - EmpireTreasuryPanel._build_section
  - EmpireTreasuryPanel._build_row
  - _clear_resource_icon_cache
  - load_resource_icons

### game/ui/research/__init__.py (Tier 0: TIER_0_NO_TESTS, 8 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/ui/screens/battle_state_viewer.py (Tier 2: TIER_2_PARTIAL, 262 LOC, layer: ui)
- Total symbols: 8 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/ui/screens/test_battle_state_viewer.py
- Heuristically untested symbols (3):
  - BattleStateViewer.show
  - BattleStateViewer.hide
  - BattleStateViewer.handle_resize

### game/ui/screens/builder/event_bus.py (Tier 3: TIER_3_APPARENTLY_COVERED, 78 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 5
- Candidate test files (5):
  - tests/unit/systems/test_event_bus.py
  - tests/unit/ui/builder/test_weapons_viewmodel.py
  - tests/unit/ui/screens/test_build_queue_viewmodel.py
  - tests/unit/ui/screens/test_empire_build_queue_viewmodel.py
  - tests/unit/ui/screens/test_empire_build_queue_window.py

### game/ui/screens/builder/weapons_renderer.py (Tier 2: TIER_2_PARTIAL, 524 LOC, layer: ui)
- Total symbols: 15 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/ui/screens/builder/test_weapons_renderer.py
- Heuristically untested symbols (10):
  - WeaponsRenderer.clear_caches
  - WeaponsRenderer.invalidate_icon_cache
  - WeaponsRenderer.invalidate_name_cache
  - WeaponsRenderer._get_scaled_icon
  - WeaponsRenderer._get_weapon_name_surface
  - WeaponsRenderer._get_accuracy_color
  - WeaponsRenderer.draw_direction_indicator
  - WeaponsRenderer.draw_scale_markers
  - WeaponsRenderer.draw_unified_weapon_bar
  - WeaponsRenderer.draw_weapon_row

### game/ui/screens/fleet_report_filters.py (Tier 2: TIER_2_PARTIAL, 319 LOC, layer: ui)
- Total symbols: 10 | Heuristically tested: 8
- Candidate test files (1):
  - tests/unit/ui/screens/test_fleet_report_filters.py
- Heuristically untested symbols (2):
  - _check_tri_state
  - get_sort_key

### game/ui/screens/planet_target_editor_base.py (Tier 0: TIER_0_NO_TESTS, 63 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - PlanetTargetEditor
  - PlanetTargetEditor._button_handlers
  - PlanetTargetEditor.process_event

### game/ui/screens/race_setup/delegate_factory.py (Tier 3: TIER_3_APPARENTLY_COVERED, 87 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/screens/test_race_setup_delegate_factory.py

### game/ui/screens/race_setup/view_model.py (Tier 2: TIER_2_PARTIAL, 88 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/ui/screens/race_setup/test_controller.py
  - tests/unit/ui/screens/test_race_setup_delegate_factory.py
- Heuristically untested symbols (4):
  - RaceSetupViewModel.tab_count
  - RaceSetupViewModel.clamp_step
  - RaceSetupViewModel.show_save_button_on
  - RaceSetupViewModel.show_randomize_button_on

### game/ui/screens/settings_window.py (Tier 0: TIER_0_NO_TESTS, 109 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - SettingsWindow
  - SettingsWindow.__init__
  - SettingsWindow.process_event
  - SettingsWindow.update
  - SettingsWindow.kill

### game/ui/screens/setup_renderer.py (Tier 0: TIER_0_NO_TESTS, 216 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (6):
  - draw_title
  - draw_available_ships
  - draw_load_save_buttons
  - draw_team
  - draw_action_buttons
  - draw_ai_dropdown

### game/ui/screens/star_list_filters.py (Tier 2: TIER_2_PARTIAL, 226 LOC, layer: ui)
- Total symbols: 8 | Heuristically tested: 6
- Candidate test files (2):
  - tests/unit/ui/screens/test_gather_planets_caching.py
  - tests/unit/ui/screens/test_star_list_filters.py
- Heuristically untested symbols (2):
  - matches_filter
  - padded_range

### game/ui/screens/star_list_sidebar.py (Tier 0: TIER_0_NO_TESTS, 180 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - build_sidebar
  - add_range

### game/ui/screens/test_lab/screen.py (Tier 2: TIER_2_PARTIAL, 416 LOC, layer: ui)
- Total symbols: 37 | Heuristically tested: 10
- Candidate test files (3):
  - tests/unit/test_lab/test_handle_resize_forwards_to_viewer.py
  - tests/unit/test_lab/test_render_progress_no_game_handle.py
  - tests/unit/test_lab/test_visual_run.py
- Heuristically untested symbols (27):
  - TestLabScreen.selected_category
  - TestLabScreen.selected_category
  - TestLabScreen.selected_test_id
  - TestLabScreen.selected_test_id
  - TestLabScreen.category_hover
  - TestLabScreen.category_hover
  - TestLabScreen.test_hover
  - TestLabScreen.test_hover
  - TestLabScreen.headless_running
  - TestLabScreen.headless_running
  - TestLabScreen.all_scenarios
  - TestLabScreen.batch_running
  - TestLabScreen.batch_current_index
  - TestLabScreen.batch_total
  - TestLabScreen.ship_panels
  - ... and 12 more

### game/ui/screens/test_lab/theme.py (Tier 0: TIER_0_NO_TESTS, 174 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/ui/services/vehicle_class_service.py (Tier 2: TIER_2_PARTIAL, 134 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 7
- Candidate test files (2):
  - tests/unit/builder/test_builder_ui_sync.py
  - tests/unit/ui/services/test_vehicle_class_service.py
- Heuristically untested symbols (2):
  - VehicleClassService.__init__
  - VehicleClassService._get_provider

### game/ui/widgets/ui_element_registry.py (Tier 2: TIER_2_PARTIAL, 62 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/ui/widgets/test_ui_element_registry.py
- Heuristically untested symbols (3):
  - UIElementRegistry.__init__
  - UIElementRegistry.__len__
  - UIElementRegistry.__iter__
