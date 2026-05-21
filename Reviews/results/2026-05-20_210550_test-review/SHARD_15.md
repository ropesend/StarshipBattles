# Shard 15 — Test Audit Report

## Summary
- Shard: 15 | Files assigned: 93 | Files actually read: 93 | Total findings: 7 | Critical: 3 | Major: 0 | Minor: 4

## Findings

### tests/unit/ui/panels/test_planet_report_panel.py

#### CAT-1: test_resource_grid_items_list_exists [CRITICAL]
- **Location**: test_planet_report_panel.py:88-97 | **Issue**: Creates panel via `__new__`, sets `_resource_grid_items = []`, then asserts `isinstance(panel._resource_grid_items, list)` — assertion cannot fail because it was just assigned to a list. | **Suggestion**: Remove or restructure to test real behavior (e.g. verify `_build_resource_grid` populates the list). | **LOC affected**: 10

### tests/unit/ui/screens/test_keybindings_scene.py

#### CAT-1: test_update_does_not_raise [CRITICAL]
- **Location**: test_keybindings_scene.py:273-275 | **Issue**: Calls `scene.update(0.016)` with no assertions beyond "does not raise" — cannot fail if imports succeed. | **Suggestion**: Add behavior assertion (e.g. verify UI manager updated, elapsed time advanced) or remove. | **LOC affected**: 3

#### CAT-1: test_draw_does_not_raise [CRITICAL]
- **Location**: test_keybindings_scene.py:276-279 | **Issue**: Calls `scene.draw(surface)` with no assertions beyond "does not raise" — cannot fail if imports succeed. | **Suggestion**: Add behavior assertion or remove. | **LOC affected**: 4

### tests/unit/ui/utils/test_portraits.py

#### CAT-10: TestGetShipClassColor — 4 tests with identical body, different data [MINOR]
- **Location**: test_portraits.py:18-28 | **Issue**: `test_known_class_fighter`, `test_known_class_cruiser`, `test_unknown_class_returns_default`, `test_none_returns_default` all call `get_ship_class_color(x)` and assert `== y` — identical logic across 4 test methods. | **Suggestion**: Merge into single `@pytest.mark.parametrize` test: `[("Fighter", SHIP_CLASS_FIGHTER), ("Cruiser", SHIP_CLASS_CRUISER), ("Dreadnought", SHIP_CLASS_DEFAULT), (None, SHIP_CLASS_DEFAULT)]`. | **LOC affected**: ~14

### tests/unit/ui/screens/test_battle_results_screen.py

#### CAT-10: TestHpColor — 6 tests with identical body, different data [MINOR]
- **Location**: test_battle_results_screen.py:18-43 | **Issue**: `test_zero_hp_returns_destroyed`, `test_negative_hp_returns_destroyed`, `test_low_hp_returns_critical`, `test_medium_hp_returns_damaged`, `test_high_hp_returns_healthy`, `test_full_hp_returns_healthy` all call `_hp_color(n)` and assert `== COLOR` — identical logic across 6 test methods. | **Suggestion**: Merge into `@pytest.mark.parametrize`: `[(0, HP_DESTROYED), (-5, HP_DESTROYED), (10, HP_CRITICAL), (30, HP_DAMAGED), (80, HP_HEALTHY), (100, HP_HEALTHY)]`. | **LOC affected**: ~26

### tests/unit/ui/screens/test_event_log_data_source.py

#### CAT-10: TestCategoryIcons — 4 tests with identical body for different categories [MINOR]
- **Location**: test_event_log_data_source.py:96-118 | **Issue**: `test_combat_icon`, `test_production_icon`, `test_colonies_icon`, `test_fleet_operations_icon` all assert `category_key in CATEGORY_ICONS` and check icon text contains a substring — identical logic across 4 tests. | **Suggestion**: Parametrize: `[("combat", "[Combat]"), ("production", "[Prod]"), ("colonies", "[Colony]"), ("fleet_operations", "[FleetOps]")]`. | **LOC affected**: ~23

## File Coverage Verification

| File | LOC (est.) | Read | Tests | Quality Notes |
|------|-----------|------|-------|---------------|
| tests/unit/ui/panels/test_design_stats_panel.py | 550 | Yes | 17 | Good coverage of panel lifecycle |
| tests/unit/simulation/battle_controller/test_outcome_emission.py | 324 | Yes | 10 | Strong contracts, real run_battle integration |
| tests/static_guards/test_no_planet_legacy_kwarg_wrapper.py | 100 | Yes | 3 | Solid deletion guards |
| tests/unit/ui/utils/test_portraits.py | 49 | Yes | 7 | CAT-10: parametrize opportunity |
| tests/unit/strategy/engine/test_command_registry_seeding.py | 183 | Yes | 7 | Strong registry contract tests |
| tests/unit/strategy/facade/test_facade_grouped_namespaces.py | 258 | Yes | 16 | Good namespace parity coverage |
| tests/repro_issues/test_bug_27_ordertype.py | 112 | Yes | 3 | Targeted regression test |
| tests/unit/strategy/services/test_system_effects_collector.py | 828 | Yes | 33 | Comprehensive system effects coverage |
| tests/unit/strategy/test_auto_save.py | 153 | Yes | 5 | Good save lifecycle coverage |
| tests/unit/strategy/engine/order_handlers/test_self_destruct_handler.py | 132 | Yes | 8 | Clean handler contract tests |
| tests/unit/entities/test_component_cache.py | 44 | Yes | 4 | Good cache manager coverage |
| tests/unit/research/conftest.py | 55 | Yes | 0 | Fixtures only (expected) |
| tests/unit/strategy/consumable_management_engine/test_auto_disable.py | 374 | Yes | 12 | Thorough edge case coverage |
| tests/unit/strategy/engine/session/test_bootstrap.py | 180 | Yes | 10 | Strong anti-drift tests |
| tests/integration/strategy/turn_engine/test_resupply.py | 295 | Yes | 5 | Good resupply integration |
| tests/unit/strategy/services/test_superweapon_registry_contract.py | 192 | Yes | 12 | Excellent registry contract |
| tests/unit/strategy/test_quickstart_builder.py | 338 | Yes | 17 | Comprehensive builder coverage |
| tests/unit/simulation/components/abilities/test_planetary_abilities.py | 153 | Yes | 14 | Good ability construction tests |
| tests/unit/core/test_input_actions.py | 223 | Yes | 22 | Thorough enum/dataclass coverage |
| tests/unit/builder/test_builder_interaction.py | 66 | Yes | 2 | Sparse but focused |
| tests/unit/strategy/engine/test_turn_engine_settings.py | 54 | Yes | 6 | Good clamp/fallback coverage |
| tests/unit/entities/test_ship_di.py | 187 | Yes | 9 | Solid DI enforcement tests |
| tests/unit/simulation/entities/test_ship_external_stats_serialization_guard.py | 93 | Yes | 3 | Strong serialization guards |
| tests/unit/core/test_combat_types.py | 31 | Yes | 4 | Good dataclass coverage |
| tests/unit/strategy/fleet_movement_engine/test_basics.py | 183 | Yes | 8 | Good movement engine coverage |
| tests/unit/ui/screens/test_strategy_window_manager.py | 866 | Yes | 44 | Thorough window lifecycle |
| tests/unit/research/research_controls/conftest.py | 88 | Yes | 0 | Fixtures only (expected) |
| tests/unit/ui/assets/test_ship_theme_manager.py | 636 | Yes | 30 | Comprehensive theme manager |
| tests/unit/strategy/engine/test_minefield_resolver_no_legacy_substrate.py | 86 | Yes | 2 | AST-regression guard |
| tests/unit/strategy/test_fleet_order_processor.py | 570 | Yes | 20 | Good order processing coverage |
| tests/unit/ui/test_ui_stats.py | 83 | Yes | 3 | Exercises real ship + registry |
| tests/projects/test_extract_phase.py | 402 | Yes | 17 | Good phase extraction coverage |
| tests/unit/simulation/combat/test_fleet_aura_unknown_stat_key_warning.py | 140 | Yes | 5 | Good warning-path coverage |
| tests/unit/ui/screens/test_fleet_context_menu_dispatch.py | 295 | Yes | 16 | Good integration + e2e |
| tests/unit/ui/test_race_description_panel.py | 602 | Yes | 23 | Comprehensive panel coverage |
| tests/unit/ui/services/test_design_loader_adapter.py | 131 | Yes | 10 | Good adapter contract |
| tests/unit/ui/panels/test_planet_report_panel.py | 991 | Yes | 46 | CAT-1: trivial pass found; extensive but some weak |
| tests/unit/ui/screens/test_strategy_renderer_animation.py | 79 | Yes | 6 | Good animation state tests |
| tests/unit/ui/screens/test_keybindings_scene.py | 281 | Yes | 25 | CAT-1: 2 trivial passes |
| tests/integration/ui/test_fleet_build_button.py | 232 | Yes | 11 | Good UI integration tests |
| tests/unit/ui/widgets/test_ui_element_registry.py | 100 | Yes | 6 | Clean registry tests |
| tests/unit/ui/panels/test_race_identity_panel.py | 487 | Yes | 24 | Thorough panel coverage |
| tests/unit/ui/screens/test_strategy_panel_manager.py | 193 | Yes | 7 | Good resize/tooltip tests |
| tests/unit/ui/screens/test_event_log_data_source.py | 676 | Yes | 52 | CAT-10: parametrize for category icons; otherwise thorough |
| tests/unit/ai/test_capability_cache_pdc.py | 145 | Yes | 6 | Good tag-based PDC regression |
| tests/performance/test_panel_loadtime_benchmark.py | 153 | Yes | 2 | Performance benchmark (expected pattern) |
| tests/integration/save_load/test_roundtrip_config.py | 92 | Yes | 7 | Good config serialization |
| tests/unit/strategy/data/test_bay_inventory_widened.py | 272 | Yes | 21 | Thorough four-slot coverage |
| tests/unit/core/test_component_state.py | 169 | Yes | 14 | Good state coverage |
| tests/integration/research_workflow/test_persistence.py | 240 | Yes | 13 | Good persistence coverage |
| tests/unit/ui/screens/test_battle_screen_edge_cases.py | 168 | Yes | 6 | Good edge case coverage |
| tests/unit/strategy/generation/test_star_image_registry.py | 83 | Yes | 8 | Clean registry tests |
| tests/unit/simulation/projectile_guidance/test_guidance_core.py | 319 | Yes | 16 | Thorough guidance mechanics |
| tests/unit/strategy/galaxy/test_galaxy_validation.py | 131 | Yes | 9 | Good validation coverage |
| tests/unit/simulation/entities/stat_contributors/test_defense.py | 246 | Yes | 14 | Thorough defense aggregation |
| tests/unit/ui/screens/test_battle_results_screen.py | 220 | Yes | 17 | CAT-10: parametrize for hp_color; good scroll/nav |
| tests/unit/strategy/validation/test_transfer_validator_robustness.py | 102 | Yes | 3 | Targeted robustness tests |
| tests/unit/simulation/systems/test_ship_design_stats.py | 190 | Yes | 15 | Good design stats coverage |
| tests/static_guards/test_no_design_library_class.py | 110 | Yes | 3 | AST + runtime guard |
| tests/unit/ai/target_evaluator/test_projectile_candidate_guards.py | 129 | Yes | 5 | Good crash-prevention guards |
| tests/unit/agent_coordination/test_interagent_discussion_v26_contract.py | 94 | Yes | 4 | Document-contract tests |
| tests/unit/strategy/facade/test_facade_state_proj411_caches.py | 88 | Yes | 9 | Good cache lifecycle coverage |
| tests/unit/modifiers/test_modifier_introspection.py | 342 | Yes | 16 | Good introspection coverage |
| tests/unit/simulation/combat/test_ram_target_resolver.py | 254 | Yes | 14 | Excellent ramming model coverage |
| tests/unit/simulation/combat/test_formation.py | 216 | Yes | 16 | Thorough formation coverage |
| tests/unit/modifiers/test_formula_edge_cases.py | 318 | Yes | 18 | Good formula edge case coverage |
| tests/unit/ui/services/test_component_service.py | 257 | Yes | 15 | Good modifier restriction coverage |
| tests/unit/strategy/engine/order_handlers/test_transfer_handler.py | 827 | Yes | 25 | Comprehensive transfer handler |
| tests/unit/simulation/test_physics_formulas.py | 800 | Yes | 45 | Extremely thorough physics tests |
| tests/unit/strategy/generation/test_astrophysics.py | 239 | Yes | 22 | Good astrophysics coverage |
| tests/repro_issues/test_bug_09_hull_in_palette.py | 53 | Yes | 1 | Targeted regression test |
| tests/unit/core/registry/test_registry_operations.py | 428 | Yes | 25 | Thorough registry op coverage |
| tests/unit/ui/screens/test_build_queue_data_source.py | 296 | Yes | 22 | Good data source coverage |
| tests/unit/builder/test_layer_targeted_actions.py | 148 | Yes | 6 | Good layer-targeting tests |
| tests/unit/strategy/facade/test_colony_demographic_view.py | 482 | Yes | 18 | Excellent demographic view coverage |
| tests/unit/simulation/combat/test_formation_defaults.py | 95 | Yes | 7 | Clean default formation tests |
| tests/unit/simulation/components/abilities/test_crew_abilities.py | 555 | Yes | 40 | Comprehensive crew ability tests |
| tests/unit/simulation/combat/test_ship_stats_aggregator.py | 220 | Yes | 13 | Good stats aggregation |
| tests/unit/strategy/engine/test_conflict_resolution_event_replay.py | 101 | Yes | 3 | Clean replay_id threading |
| tests/unit/strategy/data/test_design_role_registry_loader.py | 250 | Yes | 18 | Good layered loading coverage |
| tests/unit/ui/screens/test_event_log_replay_button.py | 429 | Yes | 19 | Good replay button coverage |
| tests/unit/workshop/test_stat_getters.py | 167 | Yes | 19 | Good stat getter coverage |
| tests/unit/ui/test_race_flag_gallery.py | 352 | Yes | 17 | Good gallery coverage + thumbnail cache |
| tests/unit/strategy/test_ship_instance_damage.py | 841 | Yes | 27 | Comprehensive damage + layer coverage |
| tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py | 74 | Yes | 4 | Golden-phase characterization |
| tests/unit/core/test_role_registry.py | 411 | Yes | 32 | Thorough registry coverage |
| tests/unit/strategy/engine/test_planet_energy_cache.py | 79 | Yes | 3 | Good cache invalidation tests |
| tests/unit/ui/screens/builder/test_mandatory_modifiers_ownership.py | 41 | Yes | 3 | Clean ownership contract |
| tests/unit/strategy/turn_engine/test_default_tick_phase_list.py | 266 | Yes | 7 | Golden-phase + invariants |
| tests/regression/modifier_ability_snapshots/conftest.py | 237 | Yes | 0 | Helper/snapshot functions only |
| tests/unit/engine/collision_edge_cases/conftest.py | 62 | Yes | 0 | Fixtures only (expected) |
| tests/unit/simulation/components/abilities/test_simple_multiplier_ability.py | 260 | Yes | 20 | Good multiplier ability coverage |
| tests/unit/simulation/services/test_simulation_design_loader.py | 216 | Yes | 9 | Good loader coverage |

## Context Usage Estimate
~85K tokens input (93 files × ~24362 LOC read), ~3K tokens output (report).
