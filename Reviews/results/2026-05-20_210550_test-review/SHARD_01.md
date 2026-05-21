# Shard 01 — Test Audit Report

## Summary
- Shard: 01
- Files assigned: 99
- Files actually read: 99
- Total findings: 23
- Critical: 13 | Major: 0 | Minor: 10

## Findings

### tests/unit/ui/screens/test_workshop_screen.py (~634 LOC)

#### CAT-2: test_handle_event_delegates_to_event_router  [CRITICAL]
- **Location**: test_workshop_screen.py:236-247
- **Issue**: Defines a local lambda `screen.handle_event = lambda e: screen.event_router.handle_event(e)`, then calls it. Tests only the locally-defined mock function, never exercises the production `DesignWorkshopScreen.handle_event`.
- **Suggestion**: Construct the screen through real `__init__` or a bypass-init that retains the real method implementations.
- **LOC affected**: 12

#### CAT-2: test_save_ship_delegates_to_ship_io  [CRITICAL]
- **Location**: test_workshop_screen.py:300-309
- **Issue**: Defines `screen._save_ship = lambda: screen.ship_io.save_ship()` locally, never exercises production `_save_ship`.
- **Suggestion**: Remove or rewrite to exercise the real method.
- **LOC affected**: 10

#### CAT-2: test_load_ship_delegates_to_ship_io  [CRITICAL]
- **Location**: test_workshop_screen.py:311-320
- **Issue**: Same pattern — locally-defined lambda replacing production method.
- **Suggestion**: Remove or rewrite to exercise the real method.
- **LOC affected**: 10

#### CAT-2: test_select_target_delegates_to_ship_io  [CRITICAL]
- **Location**: test_workshop_screen.py:322-331
- **Issue**: Same pattern — locally-defined lambda.
- **Suggestion**: Remove or rewrite to exercise the real method.
- **LOC affected**: 10

#### CAT-2: test_ship_property_returns_viewmodel_ship  [CRITICAL]
- **Location**: test_workshop_screen.py:264-272
- **Issue**: Dynamically installs `type(screen).ship = property(lambda self: self.viewmodel.ship)` and tests the locally-installed property descriptor.
- **Suggestion**: Exercise the real `ship` property as defined on the production class.
- **LOC affected**: 9

#### CAT-2: test_selected_components_returns_viewmodel_selection  [CRITICAL]
- **Location**: test_workshop_screen.py:274-281
- **Issue**: Same dynamic-property-install pattern.
- **Suggestion**: Exercise the real property.
- **LOC affected**: 8

#### CAT-2: test_available_components_returns_viewmodel_available  [CRITICAL]
- **Location**: test_workshop_screen.py:283-290
- **Issue**: Same dynamic-property-install pattern.
- **Suggestion**: Exercise the real property.
- **LOC affected**: 8

#### CAT-2: test_selected_component_property_delegates_to_controller  [CRITICAL]
- **Location**: test_workshop_screen.py:396-410
- **Issue**: Same dynamic-property-install pattern.
- **Suggestion**: Exercise the real property.
- **LOC affected**: 15

#### CAT-2: test_dragged_item_property_delegates_to_controller  [CRITICAL]
- **Location**: test_workshop_screen.py:412-425
- **Issue**: Same dynamic-property-install pattern.
- **Suggestion**: Exercise the real property.
- **LOC affected**: 14

#### CAT-2: test_cleanup_clears_ui_manager  [CRITICAL]
- **Location**: test_workshop_screen.py:435-449
- **Issue**: Locally-defined mock `cleanup` method replaces production code.
- **Suggestion**: Call the real `cleanup` method.
- **LOC affected**: 15

#### CAT-2: test_handle_resize_updates_dimensions  [CRITICAL]
- **Location**: test_workshop_screen.py:451-467
- **Issue**: Same locally-defined mock pattern.
- **Suggestion**: Call the real `handle_resize` method.
- **LOC affected**: 17

#### CAT-2: test_clear_design_delegates_to_viewmodel  [CRITICAL]
- **Location**: test_workshop_screen.py:581-594
- **Issue**: Same locally-defined mock pattern.
- **Suggestion**: Call the real `_clear_design` method.
- **LOC affected**: 14

#### CAT-2: test_apply_loaded_ship_updates_viewmodel  [CRITICAL]
- **Location**: test_workshop_screen.py:616-634
- **Issue**: Same locally-defined mock pattern.
- **Suggestion**: Call the real `_apply_loaded_ship` method.
- **LOC affected**: 19

### tests/unit/ui/screens/test_workshop_screen.py (~634 LOC)

#### CAT-8: test_init_standalone_mode_stores_context  [MINOR]
- **Location**: test_workshop_screen.py:185-191
- **Issue**: Uses `__new__` bypass to construct screen with all-mock context; then checks `context.is_standalone()` (a MagicMock return_value) and `context.mode.value` (set by the test helper itself). Assertions validate the test helper's own wiring, not production paths.
- **Suggestion**: Either construct via real `__init__` or delete — no production code path exercised.
- **LOC affected**: 7

#### CAT-8: test_data_reloader_initialized  [MINOR]
- **Location**: test_workshop_screen.py:341-345
- **Issue**: Asserts `screen.data_reloader is not None` where `data_reloader` was assigned as `MagicMock()` in the test helper. Always True.
- **Suggestion**: Remove — tests nothing real.
- **LOC affected**: 5

#### CAT-9: Repeated mock/lambda definitions across TestWorkshopShipIO and TestWorkshopViewModelIntegration  [MINOR]
- **Location**: test_workshop_screen.py:297-331, 260-290
- **Issue**: Each test in these classes re-defines a lambda/property on the screen instance. The helper `_make_workshop_screen` already creates all needed mock objects but the tests override method slots. If the production methods were retained, the boilerplate per-test method-override would be unnecessary.
- **Suggestion**: Restructure to use the real methods (post-CAT-2 fix) — the boilerplate disappears.
- **LOC affected**: ~80

### tests/unit/ui/screens/test_build_queue_helpers.py (~589 LOC)

#### CAT-10: TestFormatEmpireResources — cluster of 5 same-pattern tests  [MINOR]
- **Location**: test_build_queue_helpers.py:42-115
- **Issue**: `test_formats_resources_with_capacity`, `test_formats_resources_without_capacity`, `test_empty_empire_returns_no_resources`, `test_zero_values_not_shown`, `test_truncates_to_integers` all call `format_empire_resources(empire)` with different MagicMock empire setups and assert on the result string. Identical logic, different data.
- **Suggestion**: Parameterize into a single test with `@pytest.mark.parametrize` providing resource_pool/max_storage/expected_substring tuples.
- **LOC affected**: ~75

#### CAT-10: TestFormatResourceCost — cluster of 4 same-pattern tests  [MINOR]
- **Location**: test_build_queue_helpers.py:118-181
- **Issue**: `test_formats_single_resource`, `test_formats_multiple_resources`, `test_skips_zero_cost_resources`, `test_empty_cost_returns_empty_string` — identical structure, different inputs.
- **Suggestion**: Parameterize.
- **LOC affected**: ~60

### tests/unit/ui/screens/test_fleet_report_window_multi_select.py (~341 LOC)

#### CAT-10: TestShipRemoval null-guard cluster  [MINOR]
- **Location**: test_fleet_report_window_multi_select.py:241-265
- **Issue**: `test_remove_does_nothing_without_empire`, `test_remove_does_nothing_without_callback`, `test_remove_does_nothing_with_empty_selection` — identical test body setting a different null condition and asserting callback not called.
- **Suggestion**: Parameterize the null-condition (empire=None, callback=None, empty selection).
- **LOC affected**: ~25

### tests/regression/test_deprecated_code_removed.py (~190 LOC)

#### CAT-10: TestDeprecatedRegistryFunctionsRemoved — 4 identical-structure hasattr checks  [MINOR]
- **Location**: test_deprecated_code_removed.py:12-34
- **Issue**: `test_get_component_registry_removed`, `test_get_modifier_registry_removed`, `test_get_vehicle_classes_removed`, `test_get_resource_registry_removed` — identical pattern: import registry, assert not hasattr.
- **Suggestion**: Parameterize with function name strings.
- **LOC affected**: ~22

#### CAT-10: TestGameStateAliasesRemoved — 4 identical-structure hasattr checks  [MINOR]
- **Location**: test_deprecated_code_removed.py:45-67
- **Issue**: `test_menu_alias_removed`, `test_builder_alias_removed`, `test_battle_alias_removed`, `test_settings_alias_removed` — identical pattern on `game.app` module.
- **Suggestion**: Parameterize with alias name strings.
- **LOC affected**: ~22

### tests/unit/systems/test_event_bus.py (~262 LOC)

#### CAT-10: TestEventBusValidation — cluster of 3 same-pattern tests for invalid subscribe inputs  [MINOR]
- **Location**: test_event_bus.py:43-65
- **Issue**: `test_subscribe_non_callable_raises_validation_exception`, `test_subscribe_none_raises_validation_exception`, `test_subscribe_integer_raises_validation_exception` — identical logic with different invalid values.
- **Suggestion**: Parameterize with `@pytest.mark.parametrize("bad_value", ["not a callback", None, 42])`.
- **LOC affected**: ~22

### tests/integration/resource_system/test_resource_pipeline.py (~250 LOC)

#### CAT-8: TestCustomResourceTypeFullPipeline — large fixture setup for narrow assertion  [MINOR]
- **Location**: test_resource_pipeline.py:22-95
- **Issue**: Single test function `test_custom_resource_type_full_pipeline` builds a custom resource JSON file, creates a component, a ship design, a ship instance, and runs consumption — 6 logical steps over 73 lines for what is effectively one integration flow. The test is correctly structured but its monolithic shape masks which step failed.
- **Suggestion**: Split into smaller unit-focused tests or at minimum add intermediate assertions (present day only final asserts exist).
- **LOC affected**: 73

### tests/unit/ui/screens/test_builder_widgets.py (~257 LOC)

#### CAT-2: Tests mock pygame_gui elements entirely — but SUT is real ModifierEditorPanel  [MINOR — downgraded: exercises real production logic through MagicMock widget instances]
- Actual production `ModifierEditorPanel` methods (`layout`, `_on_row_change`, `handle_event`, `rebuild`) are exercised with MagicMock pygame_gui elements. The SUT is real — not CAT-2. No finding.

### tests/unit/builder/conftest.py (~7 LOC)

No findings. Conftest with module docstring only. Normal conftest pattern — not dead code.

## File Coverage Verification
| File | Status | Findings |
|------|--------|----------|
| tests/unit/simulation/battle_controller/conftest.py | Read ✓ | 0 |
| tests/integration/test_production_engine_container_unified.py | Read ✓ | 0 |
| tests/unit/strategy/combat/test_strategy_modifier_stack_builder.py | Read ✓ | 0 |
| tests/unit/simulation/combat/test_telemetry.py | Read ✓ | 0 |
| tests/regression/test_deprecated_code_removed.py | Read ✓ | 2 |
| tests/unit/strategy/engine/test_order_processor_instant.py | Read ✓ | 0 |
| tests/unit/simulation/entities/test_ship_shield_bonus_add.py | Read ✓ | 0 |
| tests/unit/tools/test_scalene_profiling_workflow.py | Read ✓ | 0 |
| tests/unit/systems/test_event_bus.py | Read ✓ | 1 |
| tests/unit/strategy/services/test_ability_sources_no_global_registry_access.py | Read ✓ | 0 |
| tests/unit/core/test_profiling_edge_cases.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_empire_economy_calculator.py | Read ✓ | 0 |
| tests/unit/core/test_registry_fixtures.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_system_effects_collector_aggregate_characterization.py | Read ✓ | 0 |
| tests/unit/simulation/systems/test_battle_engine_modifier_stack.py | Read ✓ | 0 |
| tests/unit/simulation/components/test_modifiers.py | Read ✓ | 0 |
| tests/unit/ui/panels/test_builder_widgets.py | Read ✓ | 0 |
| tests/unit/modifiers/test_modifier_effect_evaluator.py | Read ✓ | 0 |
| tests/unit/simulation/components/test_component_constants.py | Read ✓ | 0 |
| tests/unit/modifiers/test_range_mount_cap.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_command_ownership.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_build_queue_helpers.py | Read ✓ | 2 |
| tests/unit/core/test_resources.py | Read ✓ | 0 |
| tests/integration/strategy/test_combat_round_budget.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_commands.py | Read ✓ | 0 |
| tests/unit/strategy/combat/test_team_spec_builder.py | Read ✓ | 0 |
| tests/unit/modifiers/test_multi_ability_effects.py | Read ✓ | 0 |
| tests/repro_issues/test_bug_11_hull_update.py | Read ✓ | 0 |
| tests/projects/phase_workflow/test_git_ops.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_fleet_report_window_multi_select.py | Read ✓ | 1 |
| tests/unit/strategy/data/test_galaxy_state.py | Read ✓ | 0 |
| tests/integration/save_load/test_roundtrip_fleet.py | Read ✓ | 0 |
| tests/integration/resource_system/test_resource_pipeline.py | Read ✓ | 1 |
| tests/unit/ui/services/test_battle_ui_service.py | Read ✓ | 0 |
| tests/unit/services/llm/test_deepseek.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_star_list_filters.py | Read ✓ | 0 |
| tests/unit/strategy/planet_atmosphere/test_calculations.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_design_role_registry.py | Read ✓ | 0 |
| tests/integration/ui/test_ui_dynamic_update.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_star_list_window.py | Read ✓ | 0 |
| tests/unit/simulation/components/abilities/test_system_stabilizers.py | Read ✓ | 0 |
| tests/unit/simulation/systems/test_ship_stats_strategy_attributes.py | Read ✓ | 0 |
| tests/unit/strategy/validation/test_validators_no_legacy_substrate.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_strategy_click_dispatcher_rmb.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_planet_data_source.py | Read ✓ | 0 |
| tests/unit/strategy/engine/order_handlers/test_colonize_transfer_no_legacy_substrate.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_fleet_hierarchy_integration.py | Read ✓ | 0 |
| tests/integration/strategy/test_combat_owned_sector_effect_isolation.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_fleet_selection_window.py | Read ✓ | 0 |
| tests/unit/builder/test_builder_structure_features.py | Read ✓ | 0 |
| tests/unit/builder/test_builder_logic.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_design_validator.py | Read ✓ | 0 |
| tests/unit/engine/collision_edge_cases/test_damage_tracking.py | Read ✓ | 0 |
| tests/unit/simulation/combat/test_modifier_stack.py | Read ✓ | 0 |
| tests/unit/test_lab/test_data_paths.py | Read ✓ | 0 |
| tests/unit/simulation/entities/test_ship_validator_helper.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_strategy_screen_composition.py | Read ✓ | 0 |
| tests/unit/tools/test_regenerate_ship_portraits.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_workshop_screen.py | Read ✓ | 15 |
| tests/unit/strategy/fleets/test_ship_instance_roundtrip.py | Read ✓ | 0 |
| tests/unit/ui/builder/test_weapons_input_handler.py | Read ✓ | 0 |
| tests/unit/strategy/generation/density/test_noise.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_transfer_dialog_characterization.py | Read ✓ | 0 |
| tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_stabilizer_registry.py | Read ✓ | 0 |
| tests/unit/builder/test_builder_warning_logic.py | Read ✓ | 0 |
| tests/static_guards/test_no_activatable_abilities_constant.py | Read ✓ | 0 |
| tests/integration/save_load/test_roundtrip_events.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_lab/test_screen_input_handler.py | Read ✓ | 0 |
| tests/unit/builder/test_schematic_cache_key.py | Read ✓ | 0 |
| tests/unit/builder/conftest.py | Read ✓ | 0 |
| tests/unit/ai/test_controllable_adapter_edge_cases.py | Read ✓ | 0 |
| tests/unit/simulation/managers/test_retreat_manager.py | Read ✓ | 0 |
| tests/integration/test_fms_cd_isolation.py | Read ✓ | 0 |
| tests/unit/simulation/services/test_ship_materializer.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_planet_write_service.py | Read ✓ | 0 |
| tests/unit/strategy/facade/slices/test_system_slice.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_planet_classification_logic.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_multi_pod_colonization.py | Read ✓ | 0 |
| tests/integration/test_fms_b_e2e.py | Read ✓ | 0 |
| tests/unit/ui/panels/test_build_queue_portraits.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_production_engine_consumption.py | Read ✓ | 0 |
| tests/unit/ai/test_erratic_behavior_seeded.py | Read ✓ | 0 |
| tests/projects/phase_workflow/test_reviews.py | Read ✓ | 0 |
| tests/unit/core/test_state_machine.py | Read ✓ | 0 |
| tests/integration/ui/build_queue_screen/test_drag_handler_multi_queue.py | Read ✓ | 0 |
| tests/unit/simulation/validation/test_ship_validator_rules.py | Read ✓ | 0 |
| tests/unit/fixtures/test_ship_fixtures.py | Read ✓ | 0 |
| tests/unit/strategy/ship_instance/test_cost_queries.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_order_processor_transfer.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_fleet_report_window.py | Read ✓ | 0 |
| tests/unit/simulation/systems/test_battle_rng_isolation.py | Read ✓ | 0 |
| tests/unit/modifiers/test_crew_resource_bindings.py | Read ✓ | 0 |
| tests/performance/test_strategy_panel_spans.py | Read ✓ | 0 |
| tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_spatial_index.py | Read ✓ | 0 |
| tests/unit/research/research_scene/test_initialization.py | Read ✓ | 0 |
| tests/unit/simulation/conftest.py | Read ✓ | 0 |
| tests/unit/simulation/projectile_guidance/test_guidance_behavior.py | Read ✓ | 0 |

## Context Usage Estimate
- Total LOC read (test files + production code): ~25,000+
- Approximate headroom: Medium (200-500K)
