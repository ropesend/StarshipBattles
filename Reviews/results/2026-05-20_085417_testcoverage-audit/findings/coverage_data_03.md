# Coverage Data — Shard 03

**Coverage source:** heuristic
**File count:** 39 | **LOC estimate:** 9762
**Tiers:** 0=5 1=2 2=23 3=9

**Note:** All data below is HEURISTIC — import-based name-grep matching. NOT proof of coverage.

### game/ai/spatial_behaviors/screen.py (Tier 2: TIER_2_PARTIAL, 57 LOC, layer: ai)
- Total symbols: 3 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py
- Heuristically untested symbols (1):
  - ScreenBehavior.__init__

### game/research/data/tech_tree.py (Tier 2: TIER_2_PARTIAL, 264 LOC, layer: research)
- Total symbols: 12 | Heuristically tested: 11
- Candidate test files (7):
  - tests/unit/research/tech_tree/test_cycle_detection.py
  - tests/unit/research/tech_tree/test_loading.py
  - tests/unit/research/tech_tree/test_queries.py
  - tests/unit/research/tech_tree/test_validation.py
  - tests/unit/research/test_research_service.py
  - tests/unit/research/test_research_service_edge_cases.py
  - tests/unit/research/test_tech_requirement_negation.py
- Heuristically untested symbols (1):
  - TechTree.__init__

### game/services/llm/background.py (Tier 3: TIER_3_APPARENTLY_COVERED, 375 LOC, layer: services)
- Total symbols: 12 | Heuristically tested: 12
- Candidate test files (3):
  - tests/unit/services/llm/test_background.py
  - tests/unit/strategy/services/test_race_description_llm_controller.py
  - tests/unit/test_run_loop.py

### game/simulation/combat/families/seeker.py (Tier 3: TIER_3_APPARENTLY_COVERED, 83 LOC, layer: simulation)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/simulation/combat/test_weapon_family_handlers.py

### game/simulation/combat/weapon_firing_system.py (Tier 2: TIER_2_PARTIAL, 248 LOC, layer: simulation)
- Total symbols: 7 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/simulation/combat/test_weapon_dispatch_golden.py
  - tests/unit/simulation/combat/test_weapon_firing_system.py
- Heuristically untested symbols (3):
  - WeaponFiringSystem.set_event_bus
  - WeaponFiringSystem._process_weapon_fire
  - WeaponFiringSystem._create_attack

### game/simulation/components/abilities/planetary/terraforming.py (Tier 0: TIER_0_NO_TESTS, 188 LOC, layer: simulation)
- Total symbols: 16 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (16):
  - AtmosphereModifierAbility
  - AtmosphereModifierAbility.__init__
  - AtmosphereModifierAbility.get_primary_value
  - AtmosphereModifierAbility.get_ui_rows
  - QualityImprovementAbility
  - QualityImprovementAbility.__init__
  - QualityImprovementAbility.get_primary_value
  - QualityImprovementAbility.get_ui_rows
  - GravityModifierAbility
  - GravityModifierAbility.__init__
  - GravityModifierAbility.get_primary_value
  - GravityModifierAbility.get_ui_rows
  - WaterModifierAbility
  - WaterModifierAbility.__init__
  - WaterModifierAbility.get_primary_value
  - ... and 1 more

### game/simulation/entities/ship_design_stats.py (Tier 3: TIER_3_APPARENTLY_COVERED, 113 LOC, layer: simulation)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (3):
  - tests/unit/simulation/systems/test_design_stats_no_fallback.py
  - tests/unit/simulation/systems/test_ship_design_stats.py
  - tests/unit/strategy/services/test_ship_stats_cargo_storage.py

### game/simulation/validation/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 36 LOC, layer: simulation)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (1):
  - tests/unit/strategy/services/test_design_validator.py

### game/strategy/adapters/simulation_adapter.py (Tier 2: TIER_2_PARTIAL, 549 LOC, layer: strategy)
- Total symbols: 10 | Heuristically tested: 7
- Candidate test files (3):
  - tests/unit/strategy/adapters/test_simulation_adapter.py
  - tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py
  - tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
- Heuristically untested symbols (3):
  - SimulationBattleResolver._run_simulated_battle
  - SimulationBattleResolver._build_assembly
  - SimulationBattleResolver._build_capture_context

### game/strategy/combat/post_battle_hook.py (Tier 2: TIER_2_PARTIAL, 251 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/strategy/combat/test_post_battle_hook.py
- Heuristically untested symbols (3):
  - _find_instance_by_id
  - _apply_single_outcome
  - _remove_ship

### game/strategy/combat/post_battle_hook_builder.py (Tier 2: TIER_2_PARTIAL, 152 LOC, layer: strategy)
- Total symbols: 3 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/strategy/combat/test_battle_assembly.py
  - tests/unit/strategy/combat/test_post_battle_hook_builder.py
- Heuristically untested symbols (1):
  - _mine_group_has_inventory

### game/strategy/combat/strategy_modifier_stack_builder.py (Tier 2: TIER_2_PARTIAL, 220 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 4
- Candidate test files (2):
  - tests/unit/strategy/combat/test_spec_compiler.py
  - tests/unit/strategy/combat/test_strategy_modifier_stack_builder.py
- Heuristically untested symbols (1):
  - StrategyModifierStackBuilder._emit_team_scoped

### game/strategy/data/physics.py (Tier 2: TIER_2_PARTIAL, 76 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/core/test_protocols.py
  - tests/unit/strategy/data/test_radiation_physics.py
- Heuristically untested symbols (1):
  - SectorEnvironment.__init__

### game/strategy/data/planet_gen_surface.py (Tier 2: TIER_2_PARTIAL, 236 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/strategy/data/test_planet_classification_logic.py
  - tests/unit/strategy/data/test_planet_gen.py
- Heuristically untested symbols (1):
  - _get_planetary_ids

### game/strategy/data/storm.py (Tier 3: TIER_3_APPARENTLY_COVERED, 144 LOC, layer: strategy)
- Total symbols: 4 | Heuristically tested: 4
- Candidate test files (8):
  - tests/unit/fixtures/test_strategy_entities.py
  - tests/unit/strategy/data/test_storm.py
  - tests/unit/strategy/facade/slices/test_system_slice.py
  - tests/unit/strategy/facade/test_strategy_session_facade.py
  - tests/unit/strategy/generation/test_storm_generator.py
  - tests/unit/strategy/services/ability_sources/test_storm.py
  - tests/unit/strategy/services/test_ability_iterator.py
  - tests/unit/strategy/services/test_system_effects_collector.py

### game/strategy/engine/handlers/__init__.py (Tier 1: TIER_1_NO_SYMBOLS_TESTED, 72 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files (8):
  - tests/unit/strategy/engine/test_base_command_handler.py
  - tests/unit/strategy/engine/test_build_order_command_handler.py
  - tests/unit/strategy/engine/test_colonize_mission_handler.py
  - tests/unit/strategy/engine/test_command_handlers_public_api.py
  - tests/unit/strategy/engine/test_command_ownership.py
  - tests/unit/strategy/engine/test_command_registry_seeding.py
  - tests/unit/strategy/engine/test_superweapon_command_handlers.py
  - tests/unit/strategy/test_command_handlers.py

### game/strategy/engine/handlers/build.py (Tier 0: TIER_0_NO_TESTS, 97 LOC, layer: strategy)
- Total symbols: 5 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (5):
  - BuildOrderCommandHandler
  - BuildOrderCommandHandler.execute
  - RemoveBuildOrderCommandHandler
  - RemoveBuildOrderCommandHandler.execute
  - register

### game/strategy/engine/order_handlers/recover_fighters.py (Tier 2: TIER_2_PARTIAL, 296 LOC, layer: strategy)
- Total symbols: 9 | Heuristically tested: 5
- Candidate test files (2):
  - tests/unit/strategy/engine/order_handlers/test_recover_fighters_handler.py
  - tests/unit/strategy/engine/test_issuer_execution_contract.py
- Heuristically untested symbols (4):
  - RecoverFightersOrderHandler._run_with_issuer
  - RecoverFightersOrderHandler._find_ship
  - RecoverFightersOrderHandler._find_fighter_wing
  - RecoverFightersOrderHandler._fighter_ship_to_carried_vehicle

### game/strategy/engine/order_handlers/registry_factory.py (Tier 3: TIER_3_APPARENTLY_COVERED, 105 LOC, layer: strategy)
- Total symbols: 1 | Heuristically tested: 1
- Candidate test files (1):
  - tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py

### game/strategy/engine/production_engine.py (Tier 2: TIER_2_PARTIAL, 830 LOC, layer: strategy)
- Total symbols: 25 | Heuristically tested: 24
- Candidate test files (16):
  - tests/unit/strategy/engine/test_engine_validation.py
  - tests/unit/strategy/engine/test_planetary_yard_requirement.py
  - tests/unit/strategy/engine/test_production_engine_consumption.py
  - tests/unit/strategy/engine/test_production_engine_queue.py
  - tests/unit/strategy/engine/test_production_refactor.py
  - tests/unit/strategy/engine/test_production_repro.py
  - tests/unit/strategy/engine/test_production_resource_source_contract.py
  - tests/unit/strategy/production_engine/conftest.py
  - ... and 8 more
- Heuristically untested symbols (1):
  - ProductionEngine._log_zero_consume_shortage

### game/strategy/formulas/__init__.py (Tier 0: TIER_0_NO_TESTS, 11 LOC, layer: strategy)
- Total symbols: 0 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)

### game/strategy/generation/density/primitives/spiral_arm.py (Tier 3: TIER_3_APPARENTLY_COVERED, 103 LOC, layer: strategy)
- Total symbols: 2 | Heuristically tested: 2
- Candidate test files (2):
  - tests/unit/strategy/generation/density/conftest.py
  - tests/unit/strategy/generation/density/test_spiral_arm.py

### game/strategy/systems/race_library.py (Tier 2: TIER_2_PARTIAL, 300 LOC, layer: strategy)
- Total symbols: 14 | Heuristically tested: 11
- Candidate test files (1):
  - tests/unit/strategy/systems/test_race_library.py
- Heuristically untested symbols (3):
  - RaceLibrary.__init__
  - RaceLibrary._ensure_folder_exists
  - CachedRaceRegistry.__init__

### game/ui/interfaces/battle_ui.py (Tier 3: TIER_3_APPARENTLY_COVERED, 244 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 12
- Candidate test files (5):
  - tests/unit/ui/interfaces/test_battle_ui.py
  - tests/unit/ui/services/battle_ui_service/test_conversion.py
  - tests/unit/ui/services/battle_ui_service/test_state_and_integration.py
  - tests/unit/ui/services/test_battle_ui_service.py
  - tests/unit/ui/test_battle_screen.py

### game/ui/panels/build_queue_portraits.py (Tier 2: TIER_2_PARTIAL, 220 LOC, layer: ui)
- Total symbols: 7 | Heuristically tested: 3
- Candidate test files (2):
  - tests/unit/ui/panels/test_build_queue_catalog_threading.py
  - tests/unit/ui/panels/test_build_queue_portraits.py
- Heuristically untested symbols (4):
  - BuildQueuePortraitLoader.__init__
  - BuildQueuePortraitLoader.load_queue_item_portrait
  - BuildQueuePortraitLoader._create_placeholder
  - BuildQueuePortraitLoader._create_type_placeholder

### game/ui/panels/builder_widgets.py (Tier 2: TIER_2_PARTIAL, 292 LOC, layer: ui)
- Total symbols: 13 | Heuristically tested: 6
- Candidate test files (3):
  - tests/unit/ui/conftest.py
  - tests/unit/ui/panels/test_builder_widgets.py
  - tests/unit/ui/panels/test_modifier_editor_panel.py
- Heuristically untested symbols (7):
  - ModifierEditorPanel.__init__
  - ModifierEditorPanel._get_modifiers
  - ModifierEditorPanel.set_panel_height
  - ModifierEditorPanel._clear_scroll_container
  - ModifierEditorPanel._clear_all_rows
  - ModifierEditorPanel._ensure_row
  - ModifierEditorPanel._clear_extra_ui

### game/ui/panels/design_stats_panel.py (Tier 2: TIER_2_PARTIAL, 516 LOC, layer: ui)
- Total symbols: 15 | Heuristically tested: 13
- Candidate test files (1):
  - tests/unit/ui/panels/test_design_stats_panel.py
- Heuristically untested symbols (2):
  - DesignStatsPanel._build_section
  - DesignStatsPanel._update_requirements

### game/ui/panels/ship_detail_panel.py (Tier 2: TIER_2_PARTIAL, 685 LOC, layer: ui)
- Total symbols: 23 | Heuristically tested: 14
- Candidate test files (2):
  - tests/unit/strategy/test_ship_instance_damage.py
  - tests/unit/ui/panels/test_ship_detail_panel.py
- Heuristically untested symbols (9):
  - InstanceDamage
  - ComponentGroup
  - ShipDetailPanel._compute_initial_expand_state
  - ShipDetailPanel._add_section_header
  - ShipDetailPanel._build_component_section
  - ShipDetailPanel._build_layer_block
  - ShipDetailPanel._build_group_block
  - ShipDetailPanel._build_instance_row
  - ShipDetailPanel._apply_strikethrough

### game/ui/panels/ship_stats_renderer.py (Tier 2: TIER_2_PARTIAL, 440 LOC, layer: ui)
- Total symbols: 12 | Heuristically tested: 5
- Candidate test files (1):
  - tests/unit/ui/panels/test_ship_stats_renderer.py
- Heuristically untested symbols (7):
  - draw_weapon_entry
  - draw_component_entry
  - draw_ship_info_header
  - draw_ship_vitals
  - draw_fleet_bonuses
  - draw_ship_weapons
  - draw_ship_components

### game/ui/screens/atmosphere_target_editor.py (Tier 0: TIER_0_NO_TESTS, 273 LOC, layer: ui)
- Total symbols: 9 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (9):
  - AtmosphereTargetEditor
  - AtmosphereTargetEditor.__init__
  - AtmosphereTargetEditor._build_ui
  - AtmosphereTargetEditor.update
  - AtmosphereTargetEditor._button_handlers
  - AtmosphereTargetEditor._on_apply
  - AtmosphereTargetEditor._set_species_ideal
  - AtmosphereTargetEditor._set_match_current
  - AtmosphereTargetEditor._clear_target

### game/ui/screens/builder_utils.py (Tier 2: TIER_2_PARTIAL, 94 LOC, layer: ui)
- Total symbols: 6 | Heuristically tested: 1
- Candidate test files (2):
  - tests/unit/ui/screens/test_workshop_data_reloader.py
  - tests/unit/ui/screens/test_workshop_viewmodel_pick_up.py
- Heuristically untested symbols (5):
  - PanelWidths
  - PanelHeights
  - calculate_center_width
  - calculate_dynamic_layer_width
  - calculate_bottom_panel_height

### game/ui/screens/cargo_quick_dialog.py (Tier 2: TIER_2_PARTIAL, 330 LOC, layer: ui)
- Total symbols: 11 | Heuristically tested: 5
- Candidate test files (4):
  - tests/unit/ui/screens/test_cargo_quick_dialog.py
  - tests/unit/ui/screens/test_cargo_quick_dialog_issuance.py
  - tests/unit/ui/screens/test_cargo_quick_dialog_kills_on_dispatch_failure.py
  - tests/unit/ui/screens/test_cargo_quick_dialog_resolution.py
- Heuristically untested symbols (6):
  - CargoQuickDialogUiBuilder
  - CargoQuickDialogUiBuilder.build
  - CargoQuickDialogUiBuilder._setup_ui
  - CargoQuickDialogUiBuilder._apply_tooltips
  - CargoQuickDialogUiBuilder._add_cargo_row
  - CargoQuickDialog._handle_keydown

### game/ui/screens/planet_list_controller.py (Tier 2: TIER_2_PARTIAL, 48 LOC, layer: ui)
- Total symbols: 4 | Heuristically tested: 2
- Candidate test files (1):
  - tests/unit/ui/screens/test_planet_list_window.py
- Heuristically untested symbols (2):
  - PlanetListController.resolve_demographic_view
  - PlanetListController.navigate_to

### game/ui/screens/race_asset_loader.py (Tier 3: TIER_3_APPARENTLY_COVERED, 269 LOC, layer: ui)
- Total symbols: 10 | Heuristically tested: 10
- Candidate test files (3):
  - tests/unit/ui/screens/test_empire_panel_window.py
  - tests/unit/ui/test_race_asset_loader.py
  - tests/unit/ui/test_race_browser_dialog.py

### game/ui/screens/save_selection_window.py (Tier 2: TIER_2_PARTIAL, 473 LOC, layer: ui)
- Total symbols: 14 | Heuristically tested: 9
- Candidate test files (3):
  - tests/unit/ui/screens/test_save_selection_window.py
  - tests/unit/ui/screens/test_strategy_event_router_load_dialog_modal_tracking.py
  - tests/unit/ui/test_save_selection.py
- Heuristically untested symbols (5):
  - SaveSelectionUiBuilder
  - SaveSelectionUiBuilder.build
  - SaveSelectionWindow._on_expand_clicked
  - SaveSelectionWindow._on_delete_clicked
  - SaveSelectionWindow._on_cancel_clicked

### game/ui/screens/strategy_render/fleets.py (Tier 0: TIER_0_NO_TESTS, 120 LOC, layer: ui)
- Total symbols: 2 | Heuristically tested: 0
- Candidate test files: NONE (Tier 0)
- Heuristically untested symbols (2):
  - draw_fleets
  - draw_fleet_path

### game/ui/screens/strategy_screen.py (Tier 2: TIER_2_PARTIAL, 539 LOC, layer: ui)
- Total symbols: 50 | Heuristically tested: 39
- Candidate test files (6):
  - tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py
  - tests/unit/ui/screens/test_strategy_menu_actions.py
  - tests/unit/ui/screens/test_strategy_screen.py
  - tests/unit/ui/screens/test_viewing_empire_anchor.py
  - tests/unit/ui/test_empire_asset_loading.py
  - tests/unit/ui/test_scene_protocol.py
- Heuristically untested symbols (9):
  - StrategyScreen._on_colonize_planet_selected
  - StrategyScreen.request_colonize_order
  - StrategyScreen.on_edit_order
  - StrategyScreen._start_edit_move
  - StrategyScreen.complete_edit_move
  - StrategyScreen._start_edit_transfer
  - StrategyScreen.calculate_hybrid_path
  - StrategyScreen._get_system_at_hex
  - StrategyScreen._find_nearest_system

### game/ui/screens/strategy_windows/planet_abilities_ctrl.py (Tier 2: TIER_2_PARTIAL, 83 LOC, layer: ui)
- Total symbols: 5 | Heuristically tested: 3
- Candidate test files (1):
  - tests/unit/ui/screens/test_planet_abilities_window_lifecycle.py
- Heuristically untested symbols (2):
  - PlanetAbilitiesRegistrar._on_closed
  - PlanetAbilitiesRegistrar.open_editor

### game/ui/screens/workshop_viewmodel_ship_ops.py (Tier 3: TIER_3_APPARENTLY_COVERED, 330 LOC, layer: ui)
- Total symbols: 18 | Heuristically tested: 18
- Candidate test files (1):
  - tests/unit/ui/screens/test_workshop_viewmodel_ship_ops.py
