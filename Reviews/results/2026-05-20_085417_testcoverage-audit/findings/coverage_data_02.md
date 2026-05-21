# Coverage Data — Shard 02

**Coverage source:** heuristic
**File count:** 48 | **LOC estimate:** 9506
**Tiers:** 0=13 1=3 2=19 3=13

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/core/formula_evaluator.py (Tier 2: TIER_2_PARTIAL, 404 LOC, layer: core)
- Total symbols: 7 | Heuristically tested: 6
- Candidate test files (5):
  - tests/unit/core/test_formula_evaluator.py
  - tests/unit/simulation/test_formula_evaluator.py
  - tests/unit/simulation/test_formula_exceptions.py
  - tests/unit/systems/test_formula_overflow_underflow.py
  - tests/unit/systems/test_formula_system.py
- Heuristically untested symbols (1):
  - _eval_node

### game/services/llm/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 51 LOC, layer: services)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (9):
  - tests/unit/core/test_application_context.py
  - tests/unit/services/llm/conftest.py
  - tests/unit/services/llm/test_background.py
  - tests/unit/services/llm/test_deepseek.py
  - tests/unit/services/llm/test_defaults.py
  - tests/unit/services/llm/test_factory.py
  - tests/unit/services/llm/test_package_imports.py
  - tests/unit/strategy/services/test_race_description_llm_controller.py
  - ... and 1 more

### game/services/llm/provider.py (Tier 3: TIER_3_APPARENTLY_COVERED, 76 LOC, layer: services)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/services/llm/conftest.py
  - tests/unit/services/llm/test_provider_protocol.py

### game/simulation/components/abilities/planetary/shields.py (Tier 0: TIER_0_NO_TESTS, 134 LOC, layer: simulation)
- Total symbols: 8 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (8):
  - PlanetaryShieldAbility
  - PlanetaryShieldAbility.__init__
  - PlanetaryShieldAbility.get_primary_value
  - PlanetaryShieldAbility.get_ui_rows
  - RadiationShieldAbility
  - RadiationShieldAbility.__init__
  - RadiationShieldAbility.get_primary_value
  - RadiationShieldAbility.get_ui_rows

### game/simulation/components/modifier_schema.py (Tier 3: TIER_3_APPARENTLY_COVERED, 251 LOC, layer: simulation)
- Total symbols: 6 | Heuristically tested: 6
- Candidate test files (3):
  - tests/unit/modifiers/test_invalid_operation_handling.py
  - tests/unit/modifiers/test_modifier_json_schema.py
  - tests/unit/simulation/components/test_modifier_schema.py

### game/simulation/designs.py (Tier 3: TIER_3_APPARENTLY_COVERED, 68 LOC, layer: simulation)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/builder/test_designs.py

### game/simulation/entities/ship_combat_manager.py (Tier 0: TIER_0_NO_TESTS, 187 LOC, layer: simulation)
- Total symbols: 7 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (7):
  - ShipCombatManager
  - ShipCombatManager.__init__
  - ShipCombatManager.combat_engine
  - ShipCombatManager.set_event_bus
  - ShipCombatManager.die
  - ShipCombatManager.update
  - ShipCombatManager.update_derelict_status

### game/simulation/entities/ship_physics.py (Tier 3: TIER_3_APPARENTLY_COVERED, 99 LOC, layer: simulation)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/simulation/entities/test_ship_physics.py
  - tests/unit/systems/test_physics.py

### game/simulation/replay/replay_player.py (Tier 2: TIER_2_PARTIAL, 82 LOC, layer: simulation)
- Total symbols: 2 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/test_app_delegators.py
- Heuristically untested symbols (1):
  - run_replay_headless

### game/simulation/replay/replay_verifier.py (Tier 2: TIER_2_PARTIAL, 227 LOC, layer: simulation)
- Total symbols: 6 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/simulation/replay/test_replay_verifier.py
  - tests/unit/strategy/services/test_replay_verification_coordinator.py
- Heuristically untested symbols (2):
  - _record
  - _walk

### game/simulation/services/battle_service.py (Tier 2: TIER_2_PARTIAL, 399 LOC, layer: simulation)
- Total symbols: 18 | Heuristically tested: 16
- Candidate test files (6):
  - tests/unit/simulation/battle_controller/conftest.py
  - tests/unit/simulation/battle_controller/test_execution.py
  - tests/unit/simulation/battle_controller/test_initialization.py
  - tests/unit/simulation/battle_controller/test_mechanics.py
  - tests/unit/simulation/battle_controller/test_start_from_spec.py
  - tests/unit/simulation/services/test_battle_service.py
- Heuristically untested symbols (2):
  - BattleService.__init__
  - BattleService._require_engine

### game/simulation/services/ship_materializer.py (Tier 3: TIER_3_APPARENTLY_COVERED, 214 LOC, layer: simulation)
- Total symbols: 9 | Heuristically tested: 9
- Candidate test files (2):
  - tests/unit/combat_lab/test_runner_cleanup.py
  - tests/unit/simulation/services/test_ship_materializer.py

### game/strategy/combat/spec_compiler.py (Tier 3: TIER_3_APPARENTLY_COVERED, 100 LOC, layer: strategy)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (5):
  - tests/unit/strategy/combat/test_fighter_group_combat_join.py
  - tests/unit/strategy/combat/test_post_battle_hook.py
  - tests/unit/strategy/combat/test_satellite_group_combat_join.py
  - tests/unit/strategy/combat/test_spec_compiler.py
  - tests/unit/strategy/combat/test_spec_compiler_formation.py

### game/strategy/config/economy_config.py (Tier 3: TIER_3_APPARENTLY_COVERED, 147 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 5
- Candidate test files (8):
  - tests/unit/strategy/config/test_economy_config.py
  - tests/unit/strategy/engine/test_empire_economy_calculator.py
  - tests/unit/strategy/engine/test_happiness_engine.py
  - tests/unit/strategy/engine/test_organics_consumption_engine.py
  - tests/unit/strategy/facade/test_colony_demographic_view.py
  - tests/unit/strategy/services/test_empire_economy_service.py
  - tests/unit/strategy/services/test_planet_economy_projector.py
  - tests/unit/ui/screens/test_food_allocation_editor.py

### game/strategy/data/bay_inventory.py (Tier 2: TIER_2_PARTIAL, 333 LOC, layer: strategy)
- Total symbols: 21 | Heuristically tested: 20
- Candidate test files (32):
  - tests/unit/ai/test_carrier_controller.py
  - tests/unit/strategy/data/test_bay_inventory.py
  - tests/unit/strategy/data/test_bay_inventory_widened.py
  - tests/unit/strategy/data/test_fms_a_audit_fixes.py
  - tests/unit/strategy/data/test_planet_staging_yard_typed_api.py
  - tests/unit/strategy/engine/order_handlers/test_colonize_handler.py
  - tests/unit/strategy/engine/order_handlers/test_launch_fighters_handler.py
  - tests/unit/strategy/engine/order_handlers/test_launch_satellites_handler.py
  - ... and 24 more
- Heuristically untested symbols (1):
  - BayInventory.container_view

### game/strategy/data/habitability_factors.py (Tier 2: TIER_2_PARTIAL, 384 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 5
- Candidate test files (14):
  - tests/unit/strategy/data/test_habitability_factors.py
  - tests/unit/strategy/data/test_homeworld_presets.py
  - tests/unit/strategy/data/test_population_model.py
  - tests/unit/strategy/data/test_race_config.py
  - tests/unit/strategy/data/test_race_point_budget_v2.py
  - tests/unit/strategy/engine/test_game_initializer.py
  - tests/unit/strategy/engine/test_superweapon_order_processor.py
  - tests/unit/strategy/formulas/test_habitability.py
  - ... and 6 more
- Heuristically untested symbols (5):
  - _make_scalar_extractor
  - extract
  - _make_gas_extractor
  - extract
  - _build_gas_factors

### game/strategy/data/ship_instance.py (Tier 2: TIER_2_PARTIAL, 789 LOC, layer: strategy)
- Total symbols: 48 | Heuristically tested: 43
- Candidate test files (61):
  - tests/unit/core/test_protocols.py
  - tests/unit/simulation/systems/test_fighter_reboard.py
  - tests/unit/simulation/systems/test_fighter_reboard_component_state.py
  - tests/unit/simulation/systems/test_fighter_reboard_overflow_component_state.py
  - tests/unit/simulation/systems/test_satellite_reboard.py
  - tests/unit/strategy/combat/test_fighter_group_combat_join.py
  - tests/unit/strategy/combat/test_satellite_group_combat_join.py
  - tests/unit/strategy/combat/test_team_spec_builder.py
  - ... and 53 more
- Heuristically untested symbols (5):
  - ShipInstance.__post_init__
  - ShipInstance.__hash__
  - ShipInstance.__eq__
  - ShipInstance.get_resource_percentage
  - ShipInstance.__repr__

### game/strategy/engine/consumable_management_engine.py (Tier 2: TIER_2_PARTIAL, 164 LOC, layer: strategy)
- Total symbols: 6 | Heuristically tested: 5
- Candidate test files (7):
  - tests/unit/strategy/consumable_management_engine/test_auto_disable.py
  - tests/unit/strategy/consumable_management_engine/test_characterization.py
  - tests/unit/strategy/consumable_management_engine/test_consumption.py
  - tests/unit/strategy/consumable_management_engine/test_initialization.py
  - tests/unit/strategy/engine/test_engine_validation.py
  - tests/unit/strategy/turn_engine/test_dependency_injection.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
- Heuristically untested symbols (1):
  - ConsumableManagementEngine.__init__

### game/strategy/engine/production_math.py (Tier 3: TIER_3_APPARENTLY_COVERED, 39 LOC, layer: strategy)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/strategy/engine/test_production_math.py

### game/strategy/generation/loaders/astrophysics_loader.py (Tier 2: TIER_2_PARTIAL, 152 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/strategy/data/test_planet_classification_logic.py
  - tests/unit/strategy/generation/test_astrophysics.py
- Heuristically untested symbols (2):
  - AstrophysicsLoader.__init__
  - AstrophysicsLoader._validate_schema

### game/strategy/generation/planet_image_registry.py (Tier 2: TIER_2_PARTIAL, 129 LOC, layer: strategy)
- Total symbols: 7 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/strategy/data/test_planet_classification_logic.py
  - tests/unit/strategy/generation/test_planet_image_registry.py
- Heuristically untested symbols (2):
  - PlanetImageRegistry.__init__
  - PlanetImageRegistry._load_classifications

### game/strategy/services/ability_sources/system_archetype.py (Tier 0: TIER_0_NO_TESTS, 53 LOC, layer: strategy)
- Total symbols: 9 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (9):
  - SystemAbilitySource
  - SystemAbilitySource.source_kind
  - SystemAbilitySource.source_label
  - SystemAbilitySource.source_id
  - SystemAbilitySource.owner_id
  - SystemAbilitySource.get_abilities
  - SystemAbilitySource.affects_hex
  - SystemAbilitySource.affects_system
  - SystemAbilitySource.get_activation_state

### game/strategy/services/planet_habitability_service.py (Tier 3: TIER_3_APPARENTLY_COVERED, 65 LOC, layer: strategy)
- Total symbols: 3 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/strategy/services/test_planet_habitability_service.py

### game/strategy/services/race_description_prompt_builder.py (Tier 2: TIER_2_PARTIAL, 258 LOC, layer: strategy)
- Total symbols: 8 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/strategy/services/test_race_description_prompt_builder.py
- Heuristically untested symbols (6):
  - _aptitude_display_names
  - _render_user_payload
  - _render_identity
  - _render_aptitudes
  - _render_preferences
  - _render_caption_or_note

### game/ui/assets/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 4 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (5):
  - tests/unit/regressions/test_regressions.py
  - tests/unit/ui/assets/test_ship_theme_manager.py
  - tests/unit/ui/screens/test_design_image_helper.py
  - tests/unit/ui/test_ship_theme_logic.py
  - tests/unit/ui/test_theme_discovery.py

### game/ui/filters/__init__.py (Tier 0: TIER_0_NO_TESTS, 4 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/ui/renderer/sprites.py (Tier 2: TIER_2_PARTIAL, 125 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 6
- Candidate test files (3):
  - tests/unit/ui/conftest.py
  - tests/unit/ui/test_sprite_loading.py
  - tests/unit/ui/test_sprites.py
- Heuristically untested symbols (1):
  - SpriteManager.__init__

### game/ui/screens/battle_setup/panels/left_panel.py (Tier 0: TIER_0_NO_TESTS, 181 LOC, layer: ui)
- Total symbols: 1 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (1):
  - build

### game/ui/screens/battle_setup/panels/right_panel.py (Tier 0: TIER_0_NO_TESTS, 35 LOC, layer: ui)
- Total symbols: 1 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (1):
  - build

### game/ui/screens/battle_setup/view_model.py (Tier 3: TIER_3_APPARENTLY_COVERED, 60 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (4):
  - tests/unit/ui/screens/battle_setup/test_controller.py
  - tests/unit/ui/screens/battle_setup/test_input_handler.py
  - tests/unit/ui/screens/battle_setup/test_view_model.py
  - tests/unit/ui/screens/test_battle_setup_state.py

### game/ui/screens/builder/panel_layout_config.py (Tier 2: TIER_2_PARTIAL, 71 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/builder/test_builder_structure_features.py
  - tests/unit/ui/test_modifier_icons.py
- Heuristically untested symbols (2):
  - ComponentItemContext.__post_init__
  - StructurePanelLayoutConfig.__post_init__

### game/ui/screens/builder/stat_rows_dynamic.py (Tier 0: TIER_0_NO_TESTS, 580 LOC, layer: ui)
- Total symbols: 31 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (31):
  - _label_for
  - _get_constant_consumption
  - _get_max_endurance
  - _discover_resources
  - sort_key
  - _build_resource_rows
  - get_logistics_rows
  - get_construction_rows
  - res_getter
  - _get_strategic_abilities
  - get_strategic_rows
  - rate_getter
  - cap_getter
  - yard_getter
  - shipyard_getter
  - ... and 16 more

### game/ui/screens/event_log_sidebar.py (Tier 2: TIER_2_PARTIAL, 91 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/screens/test_event_log_sidebar.py
- Heuristically untested symbols (3):
  - EventLogSidebar.__init__
  - EventLogSidebar._build_widgets
  - EventLogSidebar._build_column_section

### game/ui/screens/food_allocation_editor.py (Tier 2: TIER_2_PARTIAL, 394 LOC, layer: ui)
- Total symbols: 16 | Heuristically tested: 10
- Candidate test files (1):
  - tests/unit/ui/screens/test_food_allocation_editor.py
- Heuristically untested symbols (6):
  - FoodAllocationRowData
  - FoodAllocationEditorUiBuilder
  - FoodAllocationEditorUiBuilder.build
  - FoodAllocationEditorUiBuilder._build_row
  - FoodAllocationEditor.update
  - FoodAllocationEditor.process_event

### game/ui/screens/galaxy_test/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 9 LOC, layer: ui)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/ui/test_scene_protocol.py

### game/ui/screens/list_data_source_base.py (Tier 2: TIER_2_PARTIAL, 104 LOC, layer: ui)
- Total symbols: 11 | Heuristically tested: 8
- Candidate test files (1):
  - tests/unit/ui/screens/test_list_data_source_base.py
- Heuristically untested symbols (3):
  - ListDataSource._entity_at
  - ListDataSource._get_column
  - ListDataSource._extract_value

### game/ui/screens/strategy_detail_fmt.py (Tier 3: TIER_3_APPARENTLY_COVERED, 726 LOC, layer: ui)
- Total symbols: 15 | Heuristically tested: 15
- Candidate test files (2):
  - tests/unit/ui/screens/test_fleet_detail_fmt.py
  - tests/unit/ui/screens/test_strategy_detail_fmt.py

### game/ui/screens/strategy_event_router.py (Tier 2: TIER_2_PARTIAL, 555 LOC, layer: ui)
- Total symbols: 18 | Heuristically tested: 8
- Candidate test files (9):
  - tests/unit/ui/screens/test_click_gate_integration.py
  - tests/unit/ui/screens/test_event_log_window.py
  - tests/unit/ui/screens/test_fleet_context_menu_dispatch.py
  - tests/unit/ui/screens/test_strategy_event_router.py
  - tests/unit/ui/screens/test_strategy_event_router_esc_modal.py
  - tests/unit/ui/screens/test_strategy_event_router_load_dialog_modal_tracking.py
  - tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py
  - tests/unit/ui/screens/test_strategy_ui_menu.py
  - ... and 1 more
- Heuristically untested symbols (10):
  - StrategyEventRouter.on_ui_selection
  - StrategyEventRouter._open_atmosphere_editor
  - StrategyEventRouter._open_planet_target_editor
  - StrategyEventRouter._open_gravity_editor
  - StrategyEventRouter._open_water_editor
  - StrategyEventRouter._open_radiation_shield_editor
  - StrategyEventRouter._open_food_allocation_editor
  - StrategyEventRouter._get_race_config
  - StrategyEventRouter._handle_colonize_button
  - StrategyEventRouter.process_custom_events

### game/ui/screens/strategy_panel_manager.py (Tier 3: TIER_3_APPARENTLY_COVERED, 507 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/ui/screens/test_strategy_panel_manager.py
  - tests/unit/ui/screens/test_strategy_ui_button_wiring.py

### game/ui/screens/strategy_render/planets.py (Tier 0: TIER_0_NO_TESTS, 78 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - draw_planet_sprite
  - load_planet_v3_image

### game/ui/screens/strategy_windows/build_queue_windows.py (Tier 0: TIER_0_NO_TESTS, 91 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (9):
  - BuildQueueListRegistrar
  - BuildQueueListRegistrar.__init__
  - BuildQueueListRegistrar.open
  - BuildQueueListRegistrar._on_closed
  - EmpireBuildQueueRegistrar
  - EmpireBuildQueueRegistrar.__init__
  - EmpireBuildQueueRegistrar.open
  - EmpireBuildQueueRegistrar.close
  - EmpireBuildQueueRegistrar._on_closed

### game/ui/screens/strategy_windows/event_log_window_ctrl.py (Tier 0: TIER_0_NO_TESTS, 208 LOC, layer: ui)
- Total symbols: 10 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (10):
  - EventLogRegistrar
  - EventLogRegistrar.__init__
  - EventLogRegistrar.open_all
  - EventLogRegistrar.open_with_events
  - EventLogRegistrar.sync_for_empire
  - EventLogRegistrar._open_with
  - EventLogRegistrar._build_replay_resolver
  - EventLogRegistrar._on_launch_replay
  - EventLogRegistrar._on_navigate
  - EventLogRegistrar._on_closed

### game/ui/screens/test_lab/panel_manager.py (Tier 2: TIER_2_PARTIAL, 233 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/test_lab/test_panel_manager.py
- Heuristically untested symbols (3):
  - TestLabPanelManager.__init__
  - TestLabPanelManager.create_results_panel
  - TestLabPanelManager.create_ui_buttons

### game/ui/screens/test_lab/renderer/_condition_logic.py (Tier 0: TIER_0_NO_TESTS, 136 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - is_condition_verified
  - format_check_pair

### game/ui/screens/test_lab/renderer/header_panel.py (Tier 0: TIER_0_NO_TESTS, 152 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - HeaderPanel
  - HeaderPanel.__init__
  - HeaderPanel.draw
  - HeaderPanel._draw_seed_controls

### game/ui/screens/turn_failed_dialog.py (Tier 0: TIER_0_NO_TESTS, 137 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (4):
  - _format_body
  - TurnFailedDialog
  - TurnFailedDialog.__init__
  - TurnFailedDialog.process_event

### game/ui/services/image/types.py (Tier 3: TIER_3_APPARENTLY_COVERED, 43 LOC, layer: ui)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/ui/services/image/test_background.py

### game/ui/services/ship_io.py (Tier 2: TIER_2_PARTIAL, 177 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 3
- Candidate test files (3):
  - tests/unit/builder/test_io_interactive.py
  - tests/unit/ui/services/test_ship_io.py
  - tests/unit/ui/services/test_ship_io_adapter.py
- Heuristically untested symbols (2):
  - ShipIO._ensure_ships_folder
  - ShipIO._get_design_loader
