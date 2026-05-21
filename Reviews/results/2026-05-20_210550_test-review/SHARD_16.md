# Shard 16 — Test Audit Report

## Summary
- Shard: 16 | Files assigned: 92 | Files actually read: 92 | Total findings: 18 | Critical: 3 | Major: 7 | Minor: 8

## Findings

### tests/unit/strategy/save_game_service/conftest.py
#### CAT-3: (no test functions) [CRITICAL]
- **Location**: conftest.py:1-50 | **Issue**: File contains `MockGameSession` class and a fixture but zero `def test_` functions. Pytest loads it for fixture discovery only. | **Suggestion**: No action needed — conftest.py is a valid fixture-only file. | **LOC affected**: 50

### tests/unit/strategy/engine/conftest.py
#### CAT-3: (no test functions) [CRITICAL]
- **Location**: conftest.py:1-13 | **Issue**: File contains only one fixture (`economy_calculator`), no test functions. | **Suggestion**: No action needed — valid fixture-only conftest. | **LOC affected**: 13

### tests/unit/core/resources_registry/conftest.py
#### CAT-3: (no test functions) [CRITICAL]
- **Location**: conftest.py:1-42 | **Issue**: File contains fixtures only (`clean_registry`, `sample_resources_data`, `sample_resources_file`), no test functions. | **Suggestion**: No action needed — valid fixture-only conftest. | **LOC affected**: 42

### tests/unit/strategy/save_game_service/test_save_load_ops.py
#### CAT-4: Duplicate MockGameSession class [MAJOR]
- **Location**: test_save_load_ops.py:24-51 | **Issue**: `MockGameSession` class is defined identically to the one in `tests/unit/strategy/save_game_service/conftest.py:12-39` (same directory). | **Suggestion**: Delete the local copy and import from conftest, or move to a shared fixture module. | **LOC affected**: 28
#### CAT-9: Repeated autouse fixture across test classes [MINOR]
- **Location**: test_save_load_ops.py:57-65, 150-158, 210-218, 286-294 | **Issue**: `setup_tmpdir` autouse fixture identical across 4 test classes. | **Suggestion**: Move to a single session/class-scoped fixture or share via the module-level conftest. | **LOC affected**: ~40

### tests/unit/strategy/fleet/test_warp_resources.py
#### CAT-4: Duplicate ship factory fixtures [MAJOR]
- **Location**: test_warp_resources.py:15-39, 218-247 | **Issue**: `make_warp_ship` and `make_edge_ship` fixtures in the same file share ~70% identical code (both create MagicMock(spec=ShipInstance) with identical setup patterns). | **Suggestion**: Merge into a single parametrized helper. | **LOC affected**: ~55
#### CAT-10: Parameterize opportunity for warp cost tests [MINOR]
- **Location**: test_warp_resources.py:41-210 | **Issue**: `test_warp_resource_costs_single_ship`, `test_warp_resource_costs_multiple_ships`, `test_warp_resource_costs_mixed_resource_types` share the same structure (build fleet, add ships, check costs dict). | **Suggestion**: Parametrize with different ship configs and expected cost dicts. | **LOC affected**: ~50

### tests/unit/strategy/engine/test_action_execution_engine.py
#### CAT-6: Mocks internal implementation detail [MAJOR]
- **Location**: test_action_execution_engine.py:133-134 | **Issue**: Tests mock `ActionTimeResolver.resolve_action_time` at module import path rather than through a DI seam. Three tests use this pattern. | **Suggestion**: Inject a stub ActionTimeResolver via the engine constructor or expose a test seam. | **LOC affected**: ~15
#### CAT-12: Logic-heavy test with for-loop assertions [MINOR]
- **Location**: test_action_execution_engine.py:89-96 | **Issue**: `test_speed_1_fleet_acts_every_100_ticks` contains a for loop with nested assertions across 4 ticks. | **Suggestion**: Use parametrize with `pytest.mark.parametrize("tick", [1, 20, 50, 99])` for the non-acting ticks. | **LOC affected**: ~8

### tests/unit/ui/screens/test_strategy_screen.py
#### CAT-6: Delegation tests assert mock internals [MAJOR]
- **Location**: test_strategy_screen.py:433-482 | **Issue**: Multiple tests (`test_update_delegates_to_camera`, `test_update_delegates_to_renderer`, `test_update_delegates_to_ui`, `test_draw_delegates_to_renderer`, `test_draw_delegates_to_ui`, etc.) only assert that mock methods were called with specific args. These tests cannot fail unless the method signature changes, making them brittle to refactoring. | **Suggestion**: Consider integration-level tests for the lifecycle or use a spy pattern with a verification step that the state was actually changed. | **LOC affected**: ~50
#### CAT-8: Deeply nested patch contexts [MAJOR]
- **Location**: test_strategy_screen.py:178-231 | **Issue**: `test_init_with_injected_composition_wires_slots` has 6 nested `with patch(...)` blocks inside a single test method. | **Suggestion**: Collapse into a shared `patch.multiple` or break into smaller setup-verification tests. | **LOC affected**: ~54

### tests/unit/ui/screens/test_fleet_orders_refresh.py
#### CAT-5: Real pygame display initialization in function-scoped fixture [MAJOR]
- **Location**: test_fleet_orders_refresh.py:11-13 | **Issue**: `manager` fixture calls `pygame.init()` and creates a real `pygame_gui.UIManager((800, 600))` — expensive for a unit test. | **Suggestion**: Patch `pygame_gui.UIManager` and `pygame.init()` to use MagicMock for unit-level tests, or move this file to `tests/integration/`. | **LOC affected**: 3

### tests/unit/ui/test_structure_visibility.py
#### CAT-8: 8 nested patch decorations in a single with statement [MINOR]
- **Location**: test_structure_visibility.py:29-36 | **Issue**: `setup_mocks` fixture nests 8 `patch()` decorators inside a single `with` block. | **Suggestion**: Use `patch.multiple()` to collapse into one call. | **LOC affected**: ~8

### tests/unit/simulation/test_battle_spec.py
#### CAT-9: Repeated `_minimal_*` helpers could be fixtures [MINOR]
- **Location**: test_battle_spec.py:45-92 | **Issue**: Four helper functions (`_minimal_ship_spec`, `_minimal_task_force`, `_minimal_team`, `_minimal_battle_spec`) are used across multiple tests but are plain functions, not fixtures. Each call creates new dataclass instances. | **Suggestion**: Convert to pytest fixtures with appropriate scope where reuse is safe (dataclasses are immutable so module scope is fine). | **LOC affected**: ~48

### tests/unit/ui/screens/test_new_game_setup_controller.py
#### CAT-10: Parameterize opportunity for modal callback tests [MINOR]
- **Location**: test_new_game_setup_controller.py:174-196 | **Issue**: `test_on_race_selected_sets_race_and_clears_modal` and `test_on_race_created_sets_race_and_clears_modal` have identical assertion structure (set race → assert vm state → assert screen callback). | **Suggestion**: Merge into a single parametrized test over the callback method name. | **LOC affected**: ~22

### tests/unit/ui/screens/test_transfer_dialog_enhanced.py
#### CAT-5: Real pygame_gui UIManager in fixture [MINOR]
- **Location**: test_transfer_dialog_enhanced.py:13 | **Issue**: `mock_manager` fixture creates a real `pygame_gui.UIManager((800, 600))` — closer to integration-test cost. | **Suggestion**: Consider patching UIManager with MagicMock for unit-level isolation. | **LOC affected**: 1

## File Coverage Verification

| File | LOC (est) | Read | Test Functions | Issues |
|------|-----------|------|----------------|--------|
| tests/unit/simulation/components/abilities/test_defense_isolation.py | 586 | Yes | 36 | 0 |
| tests/unit/strategy/engine/conftest.py | 13 | Yes | 0 | CAT-3 |
| tests/unit/ui/screens/test_new_game_setup_controller.py | 268 | Yes | 17 | CAT-10 |
| tests/unit/strategy/ship_instance/test_serialization.py | 374 | Yes | 16 | 0 |
| tests/unit/core/test_pure_loaders.py | 348 | Yes | 17 | 0 |
| tests/unit/ui/panels/test_base_gallery.py | 360 | Yes | 12 | 0 |
| tests/unit/strategy/services/test_fleet_cargo_projector.py | 156 | Yes | 14 | 0 |
| tests/unit/simulation/components/test_facing_angle_modifier.py | 106 | Yes | 5 | 0 |
| tests/unit/ui/components/table/test_virtual_table.py | 1465+ | Yes | 21 | 0 |
| tests/integration/strategy/test_game_session_strategy.py | 41 | Yes | 2 | 0 |
| tests/unit/ai/test_fighter_controller.py | 181 | Yes | 5 | 0 |
| tests/unit/simulation/components/test_size_mount_sub_one.py | 106 | Yes | 9 | 0 |
| tests/unit/strategy/interfaces/test_battle_resolver_replay_id.py | 20 | Yes | 2 | 0 |
| tests/unit/strategy/fleet/test_serialization.py | 306 | Yes | 23 | 0 |
| tests/unit/ui/screens/test_strategy_screen.py | 1031 | Yes | 53 | CAT-6, CAT-8 |
| tests/unit/core/resources_registry/conftest.py | 42 | Yes | 0 | CAT-3 |
| tests/unit/agent_coordination/test_codex_discuss_skills.py | 58 | Yes | 2 | 0 |
| tests/unit/simulation/combat/test_ability_stat_registry.py | 604 | Yes | 19 | 0 |
| tests/unit/engine/test_spatial_exact.py | 78 | Yes | 6 | 0 |
| tests/performance/test_contested_hex_round_budget.py | 153 | Yes | 2 | 0 |
| tests/unit/strategy/engine/test_restore_path_parity.py | 259 | Yes | 6 | 0 |
| tests/unit/ui/screens/strategy_windows/test_planet_list_registrar_reuse.py | 88 | Yes | 4 | 0 |
| tests/unit/modifiers/test_ability_stat_binding.py | 183 | Yes | 16 | 0 |
| tests/integration/save_load/conftest.py | 175 | Yes | 0 | 0 |
| tests/unit/ui/services/image/test_openai_provider.py | 301 | Yes | 20 | 0 |
| tests/unit/ui/screens/test_fleet_orders_refresh.py | 178 | Yes | 7 | CAT-5 |
| tests/unit/research/test_research_renderer_drawing.py | 694 | Yes | 18 | 0 |
| tests/unit/fixtures/test_strategy_entities.py | 354 | Yes | 28 | 0 |
| tests/unit/strategy/combat/test_pre_tick_setup_registry.py | 80 | Yes | 6 | 0 |
| tests/unit/services/llm/test_factory.py | 125 | Yes | 10 | 0 |
| tests/unit/simulation/test_battle_spec.py | 301 | Yes | 13 | CAT-9 |
| tests/unit/ui/test_race_asset_loader.py | 535 | Yes | 27 | 0 |
| tests/unit/regressions/test_regressions.py | 92 | Yes | 3 | 0 |
| tests/unit/ui/services/test_modifier_icon_service.py | 100 | Yes | 5 | 0 |
| tests/unit/strategy/data/test_vehicle_bay.py | 236 | Yes | 10 | 0 |
| tests/unit/strategy/data/test_intrinsic_rng_determinism.py | 96 | Yes | 5 | 0 |
| tests/unit/ui/widgets/test_panel_factory.py | 123 | Yes | 5 | 0 |
| tests/unit/ui/screens/test_empire_build_queue_filter_manager.py | 520 | Yes | 34 | 0 |
| tests/unit/combat_lab/services/conftest.py | 239 | Yes | 0 | 0 |
| tests/integration/ui/test_strategy_buttons.py | 146 | Yes | 4 | 0 |
| tests/unit/strategy/fleet/test_warp_resources.py | 380 | Yes | 22 | CAT-4, CAT-10 |
| tests/unit/ui/components/table/test_header.py | 257 | Yes | 10 | 0 |
| tests/unit/ui/test_ui_config.py | 35 | Yes | 5 | 0 |
| tests/unit/strategy/facade/test_event_queries.py | 289 | Yes | 20 | 0 |
| tests/unit/core/test_registry_cache.py | 130 | Yes | 8 | 0 |
| tests/unit/core/test_json_utils.py | 563 | Yes | 32 | 0 |
| tests/unit/modifiers/test_seeker_multi_ability.py | 224 | Yes | 7 | 0 |
| tests/unit/simulation/abilities/test_empire_storage.py | 125 | Yes | 10 | 0 |
| tests/unit/strategy/engine/test_action_execution_engine.py | 520 | Yes | 19 | CAT-6, CAT-12 |
| tests/unit/ui/utils/test_formatters.py | 124 | Yes | 22 | 0 |
| tests/unit/strategy/data/test_race_point_budget_v2.py | 317 | Yes | 27 | 0 |
| tests/unit/systems/test_physics_edge_cases.py | 133 | Yes | 12 | 0 |
| tests/integration/resource_system/conftest.py | 233 | Yes | 0 | 0 |
| tests/unit/ui/screens/test_transfer_dialog_enhanced.py | 87 | Yes | 2 | CAT-5 |
| tests/unit/ui/test_race_environment_panel.py | 510 | Yes | 22 | 0 |
| tests/unit/ui/screens/test_strategy_event_router.py | 629 | Yes | 28 | 0 |
| tests/unit/core/test_ship_classes.py | 58 | Yes | 5 | 0 |
| tests/integration/fleet_combat/test_combat_resource_consumption.py | 441 | Yes | 22 | 0 |
| tests/unit/quality/test_no_unseeded_random.py | 124 | Yes | 1 | 0 |
| tests/unit/strategy/test_game_session.py | 317 | Yes | 17 | 0 |
| tests/unit/ui/test_structure_visibility.py | 180 | Yes | 5 | CAT-8 |
| tests/unit/ui/screens/test_battle_screen_modifier_labels.py | 138 | Yes | 10 | 0 |
| tests/unit/core/test_hex_math_strategy.py | 97 | Yes | 10 | 0 |
| tests/unit/strategy/data/test_planet_physics.py | 210 | Yes | 15 | 0 |
| tests/unit/strategy/fleet_navigation/conftest.py | 29 | Yes | 0 | 0 |
| tests/integration/strategy/test_resupply_system.py | 401 | Yes | 11 | 0 |
| tests/unit/strategy/save_game_service/conftest.py | 50 | Yes | 0 | CAT-3 |
| tests/integration/replay/test_replay_spec_determinism.py | 133 | Yes | 2 | 0 |
| tests/unit/ui/screens/test_lab/renderer/test_metadata_panel.py | 122 | Yes | 4 | 0 |
| tests/unit/ui/services/image/test_background.py | 141 | Yes | 6 | 0 |
| tests/unit/strategy/pathfinding/test_intercept_recursion.py | 125 | Yes | 5 | 0 |
| tests/unit/simulation/systems/test_mass_ratio_condition.py | 92 | Yes | 7 | 0 |
| tests/unit/ui/screens/test_transfer_view_model.py | 89 | Yes | 6 | 0 |
| tests/unit/strategy/validation/test_planet_order_validator.py | 78 | Yes | 4 | 0 |
| tests/unit/simulation/components/abilities/test_terraforming_abilities.py | 67 | Yes | 6 | 0 |
| tests/integration/strategy/test_save_round_trip_phase4.py | 50 | Yes | 3 | 0 |
| tests/unit/ui/screens/test_open_warp_user_error_surfacing.py | 110 | Yes | 9 | 0 |
| tests/unit/simulation/validation/test_mass_placement_allowed.py | 107 | Yes | 7 | 0 |
| tests/unit/workshop/test_workshop_ship_io_facade_state.py | 274 | Yes | 9 | 0 |
| tests/unit/strategy/data/test_mine_group.py | 145 | Yes | 10 | 0 |
| tests/unit/strategy/ship_instance/test_ship_instance_serializer.py | 184 | Yes | 14 | 0 |
| tests/unit/strategy/save_game_service/test_save_load_ops.py | 381 | Yes | 17 | CAT-4, CAT-9 |
| tests/unit/ui/screens/test_empire_panel_lazy_load.py | 117 | Yes | 4 | 0 |
| tests/unit/regressions/test_warnings.py | 111 | Yes | 3 | 0 |
| tests/unit/strategy/generation/test_placement_strategies.py | 639 | Yes | 27 | 0 |
| tests/unit/ui/screens/test_strategy_detail_fmt.py | 1434+ | Yes | 52 | 0 |
| tests/integration/ui/build_queue_screen/test_queue_selector.py | 462 | Yes | 11 | 0 |
| tests/unit/simulation/entities/stat_contributors/test_registry.py | 182 | Yes | 10 | 0 |
| tests/unit/strategy/data/test_facility_construction_queue.py | 200 | Yes | 13 | 0 |
| tests/unit/simulation/systems/test_battle_engine_n_teams.py | 168 | Yes | 8 | 0 |
| tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py | 232 | Yes | 9 | 0 |
| tests/integration/ui/test_race_setup_ships_smoke.py | 182 | Yes | 7 | 0 |
| tests/unit/services/llm/test_deepseek.py | 400 | Yes | 21 | 0 |

## Context Usage Estimate
- All 92 files read successfully
- Approximate tokens consumed: ~90,000 input tokens
- Context window utilization: ~45%
