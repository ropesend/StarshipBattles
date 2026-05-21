# Shard 05 — Test Audit Report

## Summary
- Shard: 05 | Files assigned: 86 | Files actually read: 86 | Total findings: 12 | Critical: 0 | Major: 4 | Minor: 8

## Findings

### tests/unit/simulation/entities/test_ship_fleet_attrs.py
#### CAT-10: test_fleet_attack_bonus_default_is_zero / test_fleet_defense_bonus_default_is_zero [MINOR]
- **Location**: test_ship_fleet_attrs.py:16-54 | **Issue**: 4 tests form two near-identical pairs — `test_fleet_attack_bonus_default_is_zero` + `test_fleet_defense_bonus_default_is_zero` (same body, different attribute), and `test_fleet_attack_bonus_can_be_set_and_read` + `test_fleet_defense_bonus_can_be_set_and_read` (same body, different attribute+value). | **Suggestion**: Parametrize as a single test per pair with `(attr_name, new_value)`, e.g. `@pytest.mark.parametrize("attr,new_val", [("fleet_attack_bonus", 3.5), ("fleet_defense_bonus", 2.7)])`. | **LOC affected**: 38

### tests/unit/simulation/components/test_modifier_manager.py
#### CAT-4: Stateful vs legacy add/remove/query test method duplication [MAJOR]
- **Location**: test_modifier_manager.py:10-335 | **Issue**: `TestModifierManagerAddRemove` (class at line 10) and `TestStatefulModifierManagerAddModifier` (class at line 186) contain near-identical test sequences — `test_add_modifier_success`, `test_add_modifier_replaces_existing`, `test_add_modifier_nonexistent` in both classes, plus `TestModifierManagerQuery` (line 55) and `TestStatefulModifierManagerQuery` (line 312) mirror each other (`test_get_modifier_returns_matching/correct`, `test_get_modifier_returns_none_for_missing`). These test the same `add_modifier`/`get_modifier` contract on two different delegate shapes (component-method vs stateful-manager). The PROJ-44 Phase 4 extraction was verified by the stateful tests; the legacy-class tests no longer add coverage for a separate code path. | **Suggestion**: Delete the `TestModifierManagerAddRemove` / `TestModifierManagerQuery` / `TestModifierManagerEffects` / `TestModifierManagerStatSummary` classes. The stateful `TestStatefulModifierManager*` variants cover the identical production code. | **LOC affected**: ~120

### tests/unit/strategy/engine/test_process_colonize_validation.py
#### CAT-4: Duplicate colonize-success tests differ only in pod type string [MAJOR]
- **Location**: test_process_colonize_validation.py:181-241 | **Issue**: `test_process_colonize_universal_drop_pod_succeeds` (line 181) and `test_process_colonize_correct_pod_type_succeeds` (line 212) are structurally identical — both create a fleet with a drop pod at an ICE_DWARF planet, execute colonization, and assert `result.colonized is True` + `planet.owner_id == 1`. The only difference is the `make_colony_ship(..., "CONTINENTAL")` vs `make_colony_ship(..., "ICE_DWARF")` label. Since Phase 3 made drop pods universal, both test the same code path. | **Suggestion**: Keep one test; re-label as "any drop pod succeeds." Delete the duplicate. Or parametrize with pod type if the Phase 3 universal-doc warrants both labels. | **LOC affected**: 60

### tests/unit/strategy/engine/test_order_processor_fleet_merge.py
#### CAT-6: Mocking internal implementation detail + call_args_list assertion [MAJOR]
- **Location**: test_order_processor_fleet_merge.py:31-62 | **Issue**: `test_fleet_merge_recalculates_target_speed` patches `type(target).trigger_speed_recalculation` (a class-level descriptor patch on an internal dispatch method) and then inspects `mock_recalc.call_args_list` with custom logic (`call.args and call.args[0] is target`). The test comment acknowledges the brittleness ("either flavor counts: bound-method assertion on instance OR call_args check on the patched type-level descriptor"). | **Suggestion**: Replace with a behavior assertion — after `merge_with`, assert `target.speed` reflects the slowest-ship speed (e.g., set both fleet's ships to known speeds and verify the merged fleet's speed is the correct minimum). This tests the contract, not the implementation wiring. | **LOC affected**: 32

### tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py
#### CAT-11: Exact dict equality on event payload [MINOR]
- **Location**: test_join_fleet_handler.py:217-242 | **Issue**: `test_process_instant_orders_emits_fleet_joined_event_payload_exact_match` asserts exact dict equality (`assert payload == {...}`) on a 7-key FLEET_JOINED event payload including `category`, `empire_id`, `message`, `fleet_id`, `target_fleet_id`, `ship_count`. Any added field to the event payload would break this test even if the contract is still satisfied. | **Suggestion**: Assert only the 2-3 structurally required keys (`fleet_id`, `target_fleet_id`, `ship_count`), or use `payload["fleet_id"] == 1` individual assertions. | **LOC affected**: 26

### tests/unit/strategy/fleet_navigation/test_destination_path.py
#### CAT-10: Repeated NavigationState construction in 3 get_destination tests [MINOR]
- **Location**: test_destination_path.py:19-131 | **Issue**: `test_get_destination_move_order_returns_target`, `test_get_destination_colonize_order_returns_none`, `test_get_destination_join_fleet_returns_none` each construct an identical `NavigationState(...)` with the same `location`, `path`, `speed`, `can_warp` — only the `order` differs. | **Suggestion**: Extract `NavigationState(location=HexCoord(0,0), path=(), speed=5.0, can_warp=True)` as a fixture and parametrize over `(order, expected)`. | **LOC affected**: 45

### tests/unit/simulation/systems/test_battle_engine_tick.py
#### CAT-12: For-loop test logic in multiple tick-counting tests [MINOR]
- **Location**: test_battle_engine_tick.py:610-617, 740-748 | **Issue**: `test_multiple_ticks_increment_counter` uses a `for i in range(10)` loop with `engine.update()` inside, then asserts `tick_counter == 10`. `test_rapid_succession_ticks` uses `for _ in range(100)`. These are performing runtime computation inside the test instead of referencing `assert engine.tick_counter == N` after `N` known calls. | **Suggestion**: Use a parametrized test: `@pytest.mark.parametrize("n", [1, 10, 100])` with `for _ in range(n): engine.update()` then `assert engine.tick_counter == n`. Merges both tests into one. | **LOC affected**: 25

### tests/unit/simulation/systems/test_battle_engine_tick.py
#### CAT-12: Call-order tracking test with for-loops and list indexing [MINOR]
- **Location**: test_battle_engine_tick.py:363-388 | **Issue**: `test_ai_updated_before_ships` creates call-order tracking with closures, runs the engine, then computes `max(ai_indices) < min(ship_indices)` — 10+ lines of logic beyond simple assertions. | **Suggestion**: Simplify with `assert call_order.index("ai") < call_order.index("ship")` if the exact first-call position is sufficient, reducing it to 1 line. | **LOC affected**: 26

### tests/repro_issues/test_bug_04_display.py
#### CAT-8: 5+ nested with patch() blocks [MINOR]
- **Location**: test_bug_04_display.py:45-105 | **Issue**: `test_stats_rebuild_leaves_hashes` opens 15 `with patch(...)` blocks nested 4+ deep (lines 45-101). The outermost nested `with` structure spans lines 80-105, with `with patch.object(panel.stats_panel, ...)` nested inside another `with patch.object(panel, ...)` nested inside the outer 15-patch `with` block. This is complex to read and fragile to maintain. | **Suggestion**: Extract the patching into a `@pytest.fixture` or use a dedicated `mock_builder_right_panel` fixture that returns a fully pre-configured panel, reducing the test body to simple calls + assertions. | **LOC affected**: 61

### tests/unit/ui/test_new_game_setup.py
#### CAT-12: For-loop with nested assertions [MINOR]
- **Location**: test_new_game_setup.py:154-165 | **Issue**: `test_curve_low_end_fine_grained` contains a `for t in range(0, 100): v = system_count_slider_curve(t); max_jump = max(max_jump, v - prev); prev = v` loop with a dynamic max computation, then an assertion on `max_jump`. The test computes its own derived statistic before asserting. | **Suggestion**: Replace with a simpler linear scan: `assert all(system_count_slider_curve(t+1) - system_count_slider_curve(t) <= 1 for t in range(0, 99))`. Eliminates the manual loop-max pattern. | **LOC affected**: 12

### tests/unit/ui/test_new_game_setup.py
#### CAT-12: For-loop with nested assertions (second occurrence) [MINOR]
- **Location**: test_new_game_setup.py:185-191 | **Issue**: `test_curve_is_monotonic_non_decreasing` contains `for t in range(1, 1001): v = system_count_slider_curve(t); assert v >= prev, ...; prev = v`. Similar for-loop-as-test-logic pattern. | **Suggestion**: Use `assert all(curve(t) >= curve(t-1) for t in range(1, 1001))`. | **LOC affected**: 7

## File Coverage Verification

| File | Read | LOC (approx) | Issues |
|------|------|-------------|--------|
| tests/unit/simulation/entities/test_ship_fleet_attrs.py | Yes | 56 | CAT-10 |
| tests/unit/simulation/components/abilities/test_resource_consumption.py | Yes | 1094 | — |
| tests/unit/simulation/combat/test_weapon_summary_aggregator.py | Yes | 191 | — |
| tests/unit/strategy/engine/test_order_processor_fleet_merge.py | Yes | 89 | CAT-6 |
| tests/unit/ui/screens/race_setup/test_panel_factory.py | Yes | 236 | — |
| tests/unit/strategy/engine/test_production_math.py | Yes | 88 | — |
| tests/unit/strategy/combat/test_spec_compiler.py | Yes | 831 | — |
| tests/unit/strategy/stars/test_spectrum_validation.py | Yes | 74 | — |
| tests/unit/strategy/save_game_service/test_replay_store_instance.py | Yes | 117 | — |
| tests/unit/strategy/fleet_navigation/test_destination_path.py | Yes | 330 | CAT-10 |
| tests/integration/strategy/turn_engine/test_harvesting.py | Yes | 251 | — |
| tests/unit/tools/test_lint_test_files.py | Yes | 308 | — |
| tests/unit/ui/test_new_game_setup.py | Yes | 446 | CAT-12 (x2) |
| tests/unit/strategy/data/test_orbital_generation_config.py | Yes | 190 | — |
| tests/unit/strategy/galaxy/test_warp_point_validation.py | Yes | 69 | — |
| tests/unit/workshop/test_workshop_data_loader.py | Yes | 190 | — |
| tests/unit/ai/test_controllable_adapter.py | Yes | 39 | — |
| tests/integration/strategy/test_fleet_command_authorization.py | Yes | 285 | — |
| tests/unit/research/test_tech_node.py | Yes | 649 | — |
| tests/unit/strategy/design_repository/test_load_design_data.py | Yes | 80 | — |
| tests/unit/simulation/components/abilities/test_fleet_components.py | Yes | 275 | — |
| tests/unit/strategy/turn_engine/test_turn_processing.py | Yes | 159 | — |
| tests/unit/strategy/test_game_config.py | Yes | 281 | — |
| tests/unit/ui/screens/test_strategy_ui_menu.py | Yes | 339 | — |
| tests/unit/strategy/ship_instance/test_ship_stats_cache.py | Yes | 138 | — |
| tests/unit/core/test_validation_helpers.py | Yes | 241 | — |
| tests/unit/entities/test_ship.py | Yes | 510 | — |
| tests/unit/assets/test_component_derivatives.py | Yes | 146 | — |
| tests/unit/ui/panels/test_build_queue_controller.py | Yes | 1309 | — |
| tests/unit/simulation/entities/stat_contributors/test_movement.py | Yes | 168 | — |
| tests/unit/simulation/systems/test_battle_engine_tick.py | Yes | 1271 | CAT-12 (x2) |
| tests/unit/builder/test_ship_validator_di.py | Yes | 95 | — |
| tests/unit/strategy/save_game_service/test_built_count_flush_on_save.py | Yes | 82 | — |
| tests/integration/resource_system/test_fleet_operations.py | Yes | 322 | — |
| tests/unit/systems/test_layer_restrictions_refactor.py | Yes | 84 | — |
| tests/unit/ui/test_modifier_icons.py | Yes | 138 | — |
| tests/unit/ui/panels/test_modifier_editor_panel.py | Yes | 51 | — |
| tests/integration/research_workflow/conftest.py | Yes | 69 | — |
| tests/integration/save_load/test_roundtrip_planet.py | Yes | 180 | — |
| tests/unit/strategy/engine/test_no_specs_tuple_literal.py | Yes | 107 | — |
| tests/unit/strategy/services/test_planet_query_service.py | Yes | 108 | — |
| tests/unit/strategy/engine/test_atmosphere_engine.py | Yes | 314 | — |
| tests/unit/ui/screens/race_setup/test_controller.py | Yes | 268 | — |
| tests/unit/simulation/components/test_modifier_manager.py | Yes | 409 | CAT-4 |
| tests/unit/strategy/design_repository/test_repository.py | Yes | 233 | — |
| tests/unit/ui/services/image/test_provider.py | Yes | 67 | — |
| tests/unit/research/tech_tree/test_queries.py | Yes | 240 | — |
| tests/integration/strategy/production/conftest.py | Yes | 149 | — |
| tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py | Yes | 269 | CAT-11 |
| tests/unit/agent_coordination/test_codex_ticket_deprecation.py | Yes | 30 | — |
| tests/unit/ui/screens/test_cargo_quick_dialog_resolution.py | Yes | 103 | — |
| tests/unit/strategy/engine/test_process_colonize_validation.py | Yes | 422 | CAT-4 |
| tests/integration/strategy/test_command_handlers.py | Yes | 532 | — |
| tests/unit/ui/screens/builder/test_components.py | Yes | 182 | — |
| tests/unit/strategy/design_catalog/test_pending_built_count_flush.py | Yes | 82 | — |
| tests/unit/strategy/test_fleet_capability_calculator.py | Yes | 528 | — |
| tests/unit/simulation/validation/test_base_rule.py | Yes | 269 | — |
| tests/unit/strategy/data/test_planet_zones.py | Yes | 213 | — |
| tests/unit/ui/screens/builder/test_modifier_row.py | Yes | 405 | — |
| tests/unit/strategy/engine/handlers/test_movement_handlers.py | Yes | 375 | — |
| tests/integration/strategy/test_warp_logic_rework.py | Yes | 106 | — |
| tests/unit/ui/screens/test_planet_list_filter_snapshot.py | Yes | 117 | — |
| tests/integration/strategy/test_planet_gen.py | Yes | 82 | — |
| tests/unit/simulation/test_projectile_event_bus_wiring.py | Yes | 202 | — |
| tests/unit/simulation/systems/test_resource_manager_edge_cases.py | Yes | 297 | — |
| tests/unit/simulation/entities/test_layer_data.py | Yes | 632 | — |
| tests/unit/ui/panels/test_race_aptitudes_panel.py | Yes | 247 | — |
| tests/integration/test_fms_b_statistical_balance.py | Yes | 225 | — |
| tests/integration/strategy/production/test_completion.py | Yes | 518 | — |
| tests/unit/strategy/data/test_data_layer_boundaries.py | Yes | 67 | — |
| tests/unit/ui/screens/test_planet_list_window_reuse.py | Yes | 124 | — |
| tests/repro_issues/test_bug_04_display.py | Yes | 105 | CAT-8 |
| tests/unit/combat/conftest.py | Yes | 12 | — |
| tests/unit/simulation/test_battle_config.py | Yes | 158 | — |
| tests/integration/strategy/test_strategy_scene.py | Yes | 80 | — |
| tests/unit/entities/test_ship_stat_querier.py | Yes | 745 | — |
| tests/unit/strategy/data/test_habitability_factors.py | Yes | 375 | — |
| tests/unit/ui/screens/test_planet_list_filters.py | Yes | 416 | — |
| tests/unit/strategy/engine/handlers/test_order_queue_handlers.py | Yes | 404 | — |
| tests/unit/ui/screens/test_strategy_modal_window.py | Yes | 491 | — |
| tests/unit/strategy/facade/test_facade_indices.py | Yes | 84 | — |
| tests/unit/ui/screens/test_planet_selection_window.py | Yes | 396 | — |
| tests/unit/simulation/combat/test_hit_log_modifier_trace.py | Yes | 246 | — |
| tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py | Yes | 507 | — |
| tests/unit/strategy/test_fleet_orders_logic.py | Yes | 140 | — |
| tests/unit/ui/screens/test_planet_list_components.py | Yes | 902 | — |

## Context Usage Estimate
Approximately 35K tokens of context consumed across 86 file reads, plus report compilation.
