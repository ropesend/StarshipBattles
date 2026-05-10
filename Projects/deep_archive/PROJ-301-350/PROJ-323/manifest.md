# PROJ-323 File Manifest

<!-- Cleaned 2026-05-04 (PROJ-325 Phase 1 Task 1.4): removed entries for files deleted by upstream PROJ-321. See FND-CC-004 in OpenCode 323-review. -->

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.
>
> **Note (2026-05-04):** 41 entries removed during PROJ-325 Phase 1 Task 1.4 cleanup. The removed entries pointed to test files that no longer exist at the cited path — the bulk were deleted by upstream PROJ-321 (CAT-1/CAT-2/CAT-3 dead-test cleanups), and a smaller number were moved to a different location by PROJ-322 reorg. This manifest reflects the post-cleanup state of files relevant to the now-complete PROJ-323 work.

## Files

| File | Type | Notes |
|------|------|-------|
| tests/integration/fleet_combat/test_combat_resource_consumption.py | Test | 1 item(s): CAT-12(1) |
| tests/integration/gameplay_loop/test_turn_execution.py | Test | 1 item(s): CAT-12(1) |
| tests/integration/research_workflow/test_workflow.py | Test | 1 item(s): CAT-12(1) |
| tests/integration/strategy/test_fleet_navigation_consistency.py | Test | 1 item(s): CAT-12(1) |
| tests/integration/strategy/test_galaxy_gen.py | Test | 1 item(s): CAT-12(1) |
| tests/integration/strategy/test_habitability_on_economy.py | Test | 1 item(s): CAT-12(1) |
| tests/integration/strategy/test_planet_physics.py | Test | 1 item(s): CAT-12(1) |
| tests/integration/strategy/turn_engine/test_resources.py | Test | 1 item(s): CAT-10(1) |
| tests/integration/ui/test_race_setup_ships_smoke.py | Test | 1 item(s): CAT-12(1) |
| tests/regression/test_deprecated_code_removed.py | Test | 1 item(s): CAT-11(1) |
| tests/repro_issues/test_bug_13_weapons_report.py | Test | 1 item(s): CAT-12(1) |
| tests/unit/ai/test_advanced_behaviors.py | Test | 1 item(s): CAT-12(1) |
| tests/unit/ai/test_ai_controller_unit.py | Test | 2 item(s): CAT-8(2) |
| tests/unit/ai/test_combat_utils.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/builder/test_builder_improvements.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/builder/test_builder_validation.py | Test | 1 item(s): CAT-12(1) |
| tests/unit/core/test_combat_types.py | Test | 1 item(s): CAT-11(1) |
| tests/unit/core/test_config_edge_cases.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/core/test_json_utils.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/core/test_protocols.py | Test | 2 item(s): CAT-9(1), CAT-10(1) |
| tests/unit/modifiers/test_defense_marker_bindings.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/modifiers/test_projectile_weapon_bindings.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/research/research_scene/test_callbacks.py | Test | 2 item(s): CAT-8(1), CAT-9(1) |
| tests/unit/research/research_scene/test_initialization.py | Test | 2 item(s): CAT-8(1), CAT-9(1) |
| tests/unit/research/research_scene/test_interaction.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/research/test_tech_node.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/simulation/combat/test_fleet_aura_extended.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/simulation/components/abilities/test_defense_isolation.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/simulation/components/abilities/test_resource_consumption.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/simulation/components/abilities/test_static_value_ability.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/simulation/components/abilities/test_system_stabilizers.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/simulation/services/test_modifier_service.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/simulation/systems/test_battle_end_conditions.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/simulation/systems/test_battle_engine_end_conditions.py | Test | 2 item(s): CAT-9(1), CAT-10(1) |
| tests/unit/simulation/test_battle_runner.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/simulation/test_battle_runner_di.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/simulation/test_physics_formulas.py | Test | 1 item(s): CAT-12(1) |
| tests/unit/strategy/data/test_design_metadata_validation.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/strategy/data/test_fleet_cargo_resources.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/strategy/data/test_planet_gen.py | Test | 1 item(s): CAT-12(1) |
| tests/unit/strategy/data/test_population_model.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/strategy/data/test_superweapon_orders.py | Test | 1 item(s): CAT-11(1) |
| tests/unit/strategy/engine/test_colonize_mission_handler.py | Test | 1 item(s): CAT-11(1) |
| tests/unit/strategy/engine/test_empire_economy_calculator.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/strategy/engine/test_harvesting_engine.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/strategy/engine/test_organics_consumption_engine.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/strategy/engine/test_planet_action_engine.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/strategy/engine/test_planetary_yard_requirement.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/strategy/engine/test_resupply_engine.py | Test | 1 item(s): CAT-12(1) |
| tests/unit/strategy/engine/test_superweapon_command_handlers.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/strategy/engine/test_superweapon_handler_validation.py | Test | 2 item(s): CAT-10(2) |
| tests/unit/strategy/facade/test_facade_dispatch.py | Test | 1 item(s): CAT-11(1) |
| tests/unit/strategy/facade/test_system_dto.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/strategy/fleet_navigation/test_service_edge_cases.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/strategy/formulas/test_colony_output.py | Test | 1 item(s): CAT-12(1) |
| tests/unit/strategy/planet/test_planet_validation.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/strategy/services/ability_sources/test_system_archetype.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/strategy/services/test_fleet_navigation_action_timing.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/strategy/services/test_modifier_resolver.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/strategy/test_command_handlers.py | Test | 2 item(s): CAT-9(1), CAT-10(1) |
| tests/unit/strategy/test_engine_event_emission.py | Test | 2 item(s): CAT-8(1), CAT-9(1) |
| tests/unit/strategy/test_fleet_speed_calculator.py | Test | 2 item(s): CAT-9(1), CAT-10(1) |
| tests/unit/strategy/test_quickstart_builder.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/strategy/validation/test_colonize_validator.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/ui/components/filters/test_tri_state_widget.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/ui/components/table/test_selection.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/ui/components/table/test_virtual_table.py | Test | 2 item(s): CAT-8(2) |
| tests/unit/ui/panels/test_component_modifier_grid_panel.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/ui/panels/test_design_report_panel.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/ui/panels/test_race_identity_panel.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/ui/screens/battle_setup/test_renderer.py | Test | 1 item(s): CAT-11(1) |
| tests/unit/ui/screens/builder/test_modifier_control_row.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/ui/screens/builder/test_modifier_logic_smart_floor.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/ui/screens/test_build_queue_list_window.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/ui/screens/test_cargo_quick_dialog_resolution.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/ui/screens/test_empire_build_queue_sidebar.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/ui/screens/test_empire_build_queue_window.py | Test | 1 item(s): CAT-11(1) |
| tests/unit/ui/screens/test_fleet_data_source.py | Test | 3 item(s): CAT-9(1), CAT-10(2) |
| tests/unit/ui/screens/test_fleet_report_filters.py | Test | 4 item(s): CAT-10(3), CAT-12(1) |
| tests/unit/ui/screens/test_fleet_report_window.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/ui/screens/test_planet_data_source.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/ui/screens/test_planet_list_components.py | Test | 1 item(s): CAT-12(1) |
| tests/unit/ui/screens/test_setup_screen.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/ui/screens/test_strategy_detail_formatter.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/ui/screens/test_strategy_game_state_manager.py | Test | 2 item(s): CAT-12(2) |
| tests/unit/ui/screens/test_strategy_renderer.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/ui/screens/test_strategy_superweapons.py | Test | 2 item(s): CAT-10(2) |
| tests/unit/ui/screens/test_superweapon_input_modes.py | Test | 1 item(s): CAT-10(1) |
| tests/unit/ui/screens/test_workshop_screen.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/ui/test_detail_panel_rendering.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/ui/test_new_game_setup.py | Test | 1 item(s): CAT-11(1) |
| tests/unit/ui/test_race_browser_dialog.py | Test | 1 item(s): CAT-12(1) |
| tests/unit/ui/test_race_flag_gallery.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/ui/test_race_summary_panel.py | Test | 1 item(s): CAT-8(1) |
| tests/unit/ui/utils/test_formatters.py | Test | 1 item(s): CAT-9(1) |
| tests/unit/ui/utils/test_portraits.py | Test | 1 item(s): CAT-9(1) |
