# Coverage Data — Shard 18

**Coverage source:** heuristic
**File count:** 46 | **LOC estimate:** 9483
**Tiers:** 0=14 1=4 2=23 3=5

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/ai/controller.py (Tier 2: TIER_2_PARTIAL, 470 LOC, layer: ai)
- Total symbols: 15 | Heuristically tested: 12
- Candidate test files (10):
  - tests/unit/ai/test_ai.py
  - tests/unit/ai/test_ai_capabilities_cache.py
  - tests/unit/ai/test_ai_controller_edge_cases.py
  - tests/unit/ai/test_ai_controller_interface.py
  - tests/unit/ai/test_ai_controller_unit.py
  - tests/unit/ai/test_capability_cache_pdc.py
  - tests/unit/ai/test_fighter_controller.py
  - tests/unit/ai/test_movement_and_ai.py
  - ... and 2 more
- Heuristically untested symbols (3):
  - AIController._acquire_targets
  - AIController._select_behavior
  - AIController._execute_behavior

### game/core/protocols/strategy_domain.py (Tier 0: TIER_0_NO_TESTS, 256 LOC, layer: core)
- Total symbols: 35 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (35):
  - IEmpire
  - IEmpire.id
  - IEmpire.name
  - IEmpire.color
  - IEmpire.flag_id
  - IEmpire.portrait_id
  - IEmpire.empire_theme_id
  - IEmpire.race_config
  - IEmpire.colonies
  - IEmpire.fleets
  - IEmpire.resource_pool
  - IEmpire.max_storage
  - IEmpire.built_ship_designs
  - IFacility
  - IFacility.instance_id
  - ... and 20 more

### game/core/ship_classes.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 59 LOC, layer: core)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (5):
  - tests/unit/core/test_ship_classes.py
  - tests/unit/tools/test_codex_ship_theme_creator_skill.py
  - tests/unit/tools/test_regenerate_ship_portraits.py
  - tests/unit/ui/assets/test_ship_theme_manager.py
  - tests/unit/ui/test_theme_discovery.py

### game/research/__init__.py (Tier 0: TIER_0_NO_TESTS, 8 LOC, layer: research)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/services/llm/deepseek.py (Tier 2: TIER_2_PARTIAL, 354 LOC, layer: services)
- Total symbols: 9 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/services/llm/test_deepseek.py
  - tests/unit/services/llm/test_factory.py
- Heuristically untested symbols (6):
  - DeepSeekProvider.__repr__
  - DeepSeekProvider.__str__
  - DeepSeekProvider._read_api_key
  - DeepSeekProvider._build_body
  - DeepSeekProvider._build_headers
  - DeepSeekProvider._parse_response

### game/services/llm/defaults.py (Tier 0: TIER_0_NO_TESTS, 42 LOC, layer: services)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - get_default_llm_provider
  - set_default_llm_provider

### game/simulation/entities/ship_resource_manager.py (Tier 0: TIER_0_NO_TESTS, 53 LOC, layer: simulation)
- Total symbols: 3 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (3):
  - ShipResourceManager
  - ShipResourceManager.__init__
  - ShipResourceManager.get_resource_stat

### game/simulation/replay/replay_record.py (Tier 0: TIER_0_NO_TESTS, 93 LOC, layer: simulation)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - ReplayRecord
  - ReplayRecord.to_dict
  - ReplayRecord.from_dict
  - ReplayRecord.is_current_schema

### game/simulation/services/modifier_service.py (Tier 2: TIER_2_PARTIAL, 268 LOC, layer: simulation)
- Total symbols: 10 | Heuristically tested: 9
- Candidate test files (3):
  - tests/unit/core/test_service_injection.py
  - tests/unit/simulation/services/test_modifier_service.py
  - tests/unit/ui/screens/builder/test_mandatory_modifiers_ownership.py
- Heuristically untested symbols (1):
  - ModifierService._has_arc_set_effect

### game/simulation/services/registry_loader.py (Tier 2: TIER_2_PARTIAL, 137 LOC, layer: simulation)
- Total symbols: 2 | Heuristically tested: 1
- Candidate test files (2):
  - tests/unit/core/test_registry_manager_reload.py
  - tests/unit/simulation/services/test_registry_loader.py
- Heuristically untested symbols (1):
  - find_file

### game/strategy/data/fleet_serde.py (Tier 0: TIER_0_NO_TESTS, 168 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - fleet_to_dict
  - fleet_from_dict_kwargs
  - _deserialize_fleet_ships
  - _deserialize_fleet_orders

### game/strategy/data/group_policy_registry.py (Tier 2: TIER_2_PARTIAL, 108 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 9
- Candidate test files (2):
  - tests/unit/strategy/data/test_group_policies.py
  - tests/unit/strategy/data/test_group_policy_registry_characterization.py
- Heuristically untested symbols (1):
  - GroupPolicyRegistry.__init__

### game/strategy/data/naming.py (Tier 2: TIER_2_PARTIAL, 93 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 4
- Candidate test files (1):
  - tests/unit/strategy/data/test_naming.py
- Heuristically untested symbols (1):
  - NameRegistry.__init__

### game/strategy/engine/order_handlers/self_destruct.py (Tier 2: TIER_2_PARTIAL, 111 LOC, layer: strategy)
- Total symbols: 3 | Heuristically tested: 2
- Candidate test files (5):
  - tests/unit/strategy/engine/order_handlers/test_self_destruct_handler.py
  - tests/unit/strategy/engine/test_superweapon_edge_cases.py
  - tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py
  - tests/unit/strategy/engine/test_superweapon_order_processor.py
  - tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py
- Heuristically untested symbols (1):
  - SelfDestructHandler.supported_order_types

### game/strategy/engine/order_handlers/transfer_branches.py (Tier 0: TIER_0_NO_TESTS, 604 LOC, layer: strategy)
- Total symbols: 12 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (12):
  - _TransferDispatchMixin
  - _TransferDispatchMixin._dispatch_load_planet_resource
  - _TransferDispatchMixin._dispatch_load_planet_passengers
  - _TransferDispatchMixin._dispatch_drop_pod_load
  - _TransferDispatchMixin._dispatch_unload_planet_resource
  - _TransferDispatchMixin._dispatch_unload_planet_passengers
  - _TransferDispatchMixin._dispatch_carried_vehicle_load
  - _TransferDispatchMixin._dispatch_carried_vehicle_unload
  - _TransferDispatchMixin._dispatch_drop_pod_unload
  - _TransferDispatchMixin._dispatch_fleet_to_fleet
  - _TransferDispatchMixin._dispatch_fleet_to_fleet_drop_pod
  - _TransferDispatchMixin._dispatch_fleet_to_fleet_vehicle

### game/strategy/engine/session/__init__.py (Tier 0: TIER_0_NO_TESTS, 26 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/strategy/engine/session/runtime_services.py (Tier 3: TIER_3_APPARENTLY_COVERED, 103 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (3):
  - tests/unit/strategy/engine/session/test_bootstrap.py
  - tests/unit/strategy/engine/session/test_persistence_adapter.py
  - tests/unit/strategy/engine/session/test_runtime_services.py

### game/strategy/engine/turn_engine_config.py (Tier 3: TIER_3_APPARENTLY_COVERED, 263 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/strategy/engine/test_turn_engine_config.py
  - tests/unit/strategy/turn_engine/test_no_lazy_fallback_init.py

### game/strategy/facade/dto/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 32 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (13):
  - tests/unit/strategy/facade/slices/test_empire_slice.py
  - tests/unit/strategy/facade/slices/test_planet_slice.py
  - tests/unit/strategy/facade/slices/test_system_slice.py
  - tests/unit/strategy/facade/test_container_snapshots.py
  - tests/unit/strategy/test_ui_dto_ai_readers_no_legacy_substrate.py
  - tests/unit/ui/screens/test_cargo_quick_dialog.py
  - tests/unit/ui/screens/test_cargo_quick_dialog_resolution.py
  - tests/unit/ui/screens/test_transfer_dialog.py
  - ... and 5 more

### game/strategy/facade/slices/system_slice.py (Tier 2: TIER_2_PARTIAL, 132 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 7
- Candidate test files (1):
  - tests/unit/strategy/facade/slices/test_system_slice.py
- Heuristically untested symbols (1):
  - SystemSlice.__init__

### game/strategy/facade/strategy_session_facade.py (Tier 2: TIER_2_PARTIAL, 283 LOC, layer: strategy)
- Total symbols: 19 | Heuristically tested: 17
- Candidate test files (12):
  - tests/unit/strategy/engine/test_typed_planet_intents.py
  - tests/unit/strategy/facade/test_colony_demographic_view.py
  - tests/unit/strategy/facade/test_event_queries.py
  - tests/unit/strategy/facade/test_facade_dispatch.py
  - tests/unit/strategy/facade/test_facade_grouped_namespaces.py
  - tests/unit/strategy/facade/test_facade_indices.py
  - tests/unit/strategy/facade/test_facade_robust_resolution.py
  - tests/unit/strategy/facade/test_facade_system_proximity.py
  - ... and 4 more
- Heuristically untested symbols (2):
  - StrategySessionFacade._build_planet_index
  - StrategySessionFacade._build_fleet_hex_index

### game/strategy/generation/density/primitives/radial.py (Tier 3: TIER_3_APPARENTLY_COVERED, 61 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (4):
  - tests/unit/strategy/generation/density/conftest.py
  - tests/unit/strategy/generation/density/test_density_map.py
  - tests/unit/strategy/generation/density/test_radial.py
  - tests/unit/strategy/generation/test_placement_strategies.py

### game/strategy/generation/region_classifier.py (Tier 2: TIER_2_PARTIAL, 275 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 8
- Candidate test files (1):
  - tests/unit/strategy/generation/test_region_classifier.py
- Heuristically untested symbols (2):
  - RegionClassifier.__init__
  - RegionClassifier._build_regions

### game/strategy/services/ability_sources/fleet.py (Tier 0: TIER_0_NO_TESTS, 148 LOC, layer: strategy)
- Total symbols: 12 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (12):
  - FleetAbilitySource
  - FleetAbilitySource.source_kind
  - FleetAbilitySource.source_label
  - FleetAbilitySource.source_id
  - FleetAbilitySource.owner_id
  - FleetAbilitySource.get_abilities
  - FleetAbilitySource.affects_hex
  - FleetAbilitySource.affects_system
  - FleetAbilitySource.get_activation_state
  - _is_combat_capable
  - _is_hidden
  - _walk_strategic_abilities

### game/strategy/services/ability_sources/intrinsic_roll.py (Tier 0: TIER_0_NO_TESTS, 79 LOC, layer: strategy)
- Total symbols: 1 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (1):
  - roll_intrinsic_abilities

### game/strategy/services/ability_sources/labels.py (Tier 0: TIER_0_NO_TESTS, 23 LOC, layer: strategy)
- Total symbols: 1 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (1):
  - format_intrinsic_source_label

### game/strategy/services/cargo_transfer_service.py (Tier 2: TIER_2_PARTIAL, 301 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 7
- Candidate test files (1):
  - tests/unit/strategy/services/test_cargo_transfer_service.py
- Heuristically untested symbols (1):
  - _extract_population_items

### game/ui/panels/race_summary_panel.py (Tier 2: TIER_2_PARTIAL, 732 LOC, layer: ui)
- Total symbols: 25 | Heuristically tested: 13
- Candidate test files (1):
  - tests/unit/ui/test_race_summary_panel.py
- Heuristically untested symbols (12):
  - RaceSummaryPanel._create_left_column_content
  - RaceSummaryPanel._create_environment_column
  - RaceSummaryPanel._create_ship_theme_strip
  - RaceSummaryPanel._format_race_summary
  - RaceSummaryPanel._format_physical_summary
  - RaceSummaryPanel._format_society_summary
  - RaceSummaryPanel._format_homeworld_summary
  - RaceSummaryPanel._render_section_header
  - RaceSummaryPanel._render_env_row
  - RaceSummaryPanel._render_aptitude_rows
  - RaceSummaryPanel._refresh_flag_preview
  - RaceSummaryPanel._refresh_portrait_preview

### game/ui/renderer/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 0 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/test_app_bootstrap_invariants.py

### game/ui/research/research_renderer.py (Tier 0: TIER_0_NO_TESTS, 324 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (9):
  - ResearchRenderer
  - ResearchRenderer.__init__
  - ResearchRenderer._get_font
  - ResearchRenderer.draw
  - ResearchRenderer._draw_dependency_lines
  - ResearchRenderer._draw_dashed_line
  - ResearchRenderer._draw_nodes
  - ResearchRenderer._draw_node_text
  - ResearchRenderer._is_visible

### game/ui/screens/build_queue_screen.py (Tier 2: TIER_2_PARTIAL, 490 LOC, layer: ui)
- Total symbols: 13 | Heuristically tested: 7
- Candidate test files (2):
  - tests/unit/ui/screens/test_build_queue_screen_lifecycle.py
  - tests/unit/ui/screens/test_sub_window_hotkeys.py
- Heuristically untested symbols (6):
  - BuildQueueScreen._validate_params
  - BuildQueueScreen._construct_collaborators
  - BuildQueueScreen.handle_event
  - BuildQueueScreen.on_active_player_changed
  - BuildQueueScreen.update
  - BuildQueueScreen.draw

### game/ui/screens/build_queue_selector.py (Tier 0: TIER_0_NO_TESTS, 196 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (7):
  - BuildQueueSelector
  - BuildQueueSelector.__init__
  - BuildQueueSelector.refresh
  - BuildQueueSelector.handle_button_click
  - BuildQueueSelector._on_queue_selected
  - BuildQueueSelector._on_queue_toggled
  - BuildQueueSelector.get_selected_sources

### game/ui/screens/builder/stats_config.py (Tier 2: TIER_2_PARTIAL, 246 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 1
- Candidate test files (3):
  - tests/unit/ui/panels/test_design_stats_panel.py
  - tests/unit/ui/test_ui_stats.py
  - tests/unit/workshop/test_stats_visibility.py
- Heuristically untested symbols (2):
  - load_stats_config
  - load_sections_config

### game/ui/screens/empire_build_queue_sidebar.py (Tier 2: TIER_2_PARTIAL, 234 LOC, layer: ui)
- Total symbols: 8 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/ui/screens/test_empire_build_queue_sidebar.py
- Heuristically untested symbols (3):
  - EmpireBuildQueueSidebar.__init__
  - EmpireBuildQueueSidebar._build_column_toggles
  - EmpireBuildQueueSidebar._build_filters

### game/ui/screens/empire_build_queue_viewmodel.py (Tier 2: TIER_2_PARTIAL, 298 LOC, layer: ui)
- Total symbols: 19 | Heuristically tested: 16
- Candidate test files (3):
  - tests/unit/ui/screens/test_build_queue_data_source.py
  - tests/unit/ui/screens/test_empire_build_queue_viewmodel.py
  - tests/unit/ui/screens/test_empire_build_queue_window.py
- Heuristically untested symbols (2):
  - EmpireBuildQueueViewModel._clear_selection
  - EmpireBuildQueueViewModel._refresh

### game/ui/screens/empire_build_queue_window.py (Tier 2: TIER_2_PARTIAL, 734 LOC, layer: ui)
- Total symbols: 47 | Heuristically tested: 36
- Candidate test files (1):
  - tests/unit/ui/screens/test_empire_build_queue_window.py
- Heuristically untested symbols (9):
  - EmpireBuildQueueUiBuilder
  - EmpireBuildQueueWindow._on_filters_applied
  - EmpireBuildQueueWindow._on_selection_changed
  - EmpireBuildQueueWindow._source_can_build_type
  - EmpireBuildQueueWindow._get_system_name
  - EmpireBuildQueueWindow._get_turns_left_text
  - EmpireBuildQueueWindow.on_close_window_button_pressed
  - EmpireBuildQueueWindow.request_close
  - EmpireBuildQueueWindow.open_for_empire

### game/ui/screens/planet_list_filters.py (Tier 2: TIER_2_PARTIAL, 410 LOC, layer: ui)
- Total symbols: 17 | Heuristically tested: 8
- Candidate test files (3):
  - tests/unit/ui/screens/test_gather_planets_caching.py
  - tests/unit/ui/screens/test_planet_list_components.py
  - tests/unit/ui/screens/test_planet_list_filters.py
- Heuristically untested symbols (8):
  - _name_predicate
  - _type_predicate
  - _owner_predicate
  - _range_predicate
  - get_system_name
  - get_owner_name
  - get_mass_earth
  - get_resource_str

### game/ui/screens/planet_menu_items.py (Tier 2: TIER_2_PARTIAL, 155 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/screens/test_planet_menu_items.py
- Heuristically untested symbols (2):
  - _global_hex
  - _matching_deployed_group_at_hex

### game/ui/screens/strategy_detail_formatter.py (Tier 2: TIER_2_PARTIAL, 454 LOC, layer: ui)
- Total symbols: 25 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/ui/screens/test_planet_production_display.py
  - tests/unit/ui/screens/test_strategy_detail_formatter.py
- Heuristically untested symbols (21):
  - StrategyDetailFormatter.__init__
  - StrategyDetailFormatter.__getattr__
  - StrategyDetailFormatter._get_label_for_obj
  - StrategyDetailFormatter._format_spectrum
  - StrategyDetailFormatter._format_atmosphere_raw
  - StrategyDetailFormatter._format_star_system
  - StrategyDetailFormatter._format_star
  - StrategyDetailFormatter._show_planet_report
  - StrategyDetailFormatter._planet_has_atmosphere_modifier
  - StrategyDetailFormatter._planet_has_gravity_modifier
  - StrategyDetailFormatter._planet_has_water_modifier
  - StrategyDetailFormatter._planet_has_radiation_shield
  - StrategyDetailFormatter._planet_has_ability
  - StrategyDetailFormatter._layout_action_buttons
  - StrategyDetailFormatter._format_sector_environment
  - ... and 6 more

### game/ui/screens/strategy_windows/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 9 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (3):
  - tests/unit/ui/screens/strategy_windows/test_build_queue_windows.py
  - tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py
  - tests/unit/ui/screens/strategy_windows/test_list_windows.py

### game/ui/screens/strategy_windows/selection_prompts.py (Tier 0: TIER_0_NO_TESTS, 90 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - SelectionPromptRegistrar
  - SelectionPromptRegistrar.__init__
  - SelectionPromptRegistrar.prompt_planet
  - SelectionPromptRegistrar.open_system
  - SelectionPromptRegistrar.prompt_fleet

### game/ui/screens/test_lab/renderer/tag_filter_panel.py (Tier 3: TIER_3_APPARENTLY_COVERED, 146 LOC, layer: ui)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/screens/test_lab/renderer/test_tag_filter_panel.py

### game/ui/screens/workshop_context.py (Tier 3: TIER_3_APPARENTLY_COVERED, 175 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 6
- Candidate test files (15):
  - tests/unit/builder/test_builder_drag_drop_real.py
  - tests/unit/builder/test_builder_improvements.py
  - tests/unit/builder/test_builder_io_integration.py
  - tests/unit/builder/test_builder_structure_features.py
  - tests/unit/builder/test_builder_warning_logic.py
  - tests/unit/builder/test_multi_selection_logic.py
  - tests/unit/builder/test_selection_refinements.py
  - tests/unit/test_app_create_workshop_context.py
  - ... and 7 more

### game/ui/services/validation_service.py (Tier 2: TIER_2_PARTIAL, 79 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/services/test_validation_service.py
- Heuristically untested symbols (2):
  - ValidationService.__init__
  - ValidationService._get_validator

### game/ui/utils/resource_display.py (Tier 2: TIER_2_PARTIAL, 58 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/ui/panels/test_empire_treasury_panel.py
- Heuristically untested symbols (1):
  - get_displayed_resource_ids

### game/ui/widgets/scroll_state.py (Tier 2: TIER_2_PARTIAL, 103 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 8
- Candidate test files (1):
  - tests/unit/ui/widgets/test_scroll_state.py
- Heuristically untested symbols (1):
  - ScrollState.__init__
