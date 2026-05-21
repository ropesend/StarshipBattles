# Shard 11 -- Test Audit Report

## Summary
- Shard: 11 | Files assigned: 85 | Files actually read: 85 | Total findings: 28 | Critical: 11 | Major: 10 | Minor: 7

## Findings

### tests/unit/workshop/test_workshop_viewmodel_public_api.py

#### CAT-1: test_ship_is_property (and 8 additional property-check tests) [CRITICAL]
- **Location**: test_workshop_viewmodel_public_api.py:111-135 | **Issue**: Nine tests assert isinstance(X, property). Cannot fail if imports succeed. | **Suggestion**: Merge into a single parametrized test. | **LOC affected**: 25

#### CAT-1: test_select_component_is_callable [CRITICAL]
- **Location**: test_workshop_viewmodel_public_api.py:107-108 | **Issue**: Asserts callable(X). Cannot fail unless class is removed. | **Suggestion**: Fold into API-presence parametrized test. | **LOC affected**: 2

### tests/unit/ui/screens/test_strategy_renderer_public_api.py

#### CAT-1: Entire file -- 8 trivial pass tests [CRITICAL]
- **Location**: test_strategy_renderer_public_api.py:16-91 | **Issue**: All 8 tests assert attribute existence via hasattr/isinstance/inspect. No logic tested. | **Suggestion**: Fold into single parametrized test or remove. | **LOC affected**: 76

### tests/unit/core/test_role.py

#### CAT-1: Four trivial structural tests [CRITICAL]
- **Location**: test_role.py:45-80 | **Issue**: Tests assert Python dataclass built-in behavior (frozen, eq) and import path identity. | **Suggestion**: Remove import-path test. Merge frozen/equality tests. | **LOC affected**: 24

### tests/unit/strategy/data/test_colony_yard_registries.py

#### CAT-1: test_game_registries_has_components_attribute [CRITICAL]
- **Location**: test_colony_yard_registries.py:81-84 | **Issue**: Asserts hasattr(fresh_registries, 'components'). Trivial pass against a fixture. | **Suggestion**: Remove or fold into first test that uses .components. | **LOC affected**: 3

### tests/unit/ui/screens/test_strategy_game_state_manager.py

#### CAT-6: Multiple tests patch private methods of SUT [MAJOR]
- **Location**: test_strategy_game_state_manager.py:521-648 | **Issue**: Tests patch object(manager, "_apply_turn_start_state") / "_capture_outgoing_player_state" / "_sync_active_empire" -- mocking internal private methods. Breaks on internal refactor. | **Suggestion**: Assert observable outcomes (screen state, rotation index) rather than delegation. | **LOC affected**: 130

#### CAT-4: Duplicate else-branch / rollover-branch tests [MAJOR]
- **Location**: test_strategy_game_state_manager.py:510-687 | **Issue**: Else-branch and rollover-branch tests have identical structure with only player-count difference. | **Suggestion**: Parametrize on human_player_ids and current_player_index. | **LOC affected**: 150

#### CAT-6: test_capture_writes_each_live_windows_snapshot_to_outgoing_slot mocks private internal state [MAJOR]
- **Location**: test_strategy_game_state_manager.py:1189-1231 | **Issue**: Reads internal manager._per_player_ui_state.load(). Tightly coupled to capture implementation details. | **Suggestion**: Assert on window manager interface calls. | **LOC affected**: 40

#### CAT-8: Excessively long helper function [MINOR]
- **Location**: test_strategy_game_state_manager.py:10-64, 821-870 | **Issue**: Two near-duplicate 45-55 line mock factory helpers exceed 100 lines of infrastructure. | **Suggestion**: Extract shared factory accepting player count. | **LOC affected**: 100

### tests/unit/simulation/entities/test_ship_serialization.py

#### CAT-10: Five identical-structure roundtrip tests [MINOR]
- **Location**: test_ship_serialization.py:328-419 | **Issue**: Five tests (preserves_name/_ship_class/_theme_id/_team_id/_color) follow identical to_dict/from_dict/assert pattern. | **Suggestion**: Parametrize on field name using getattr. | **LOC affected**: 20

#### CAT-5: equipped_ship fixture is function-scoped with expensive construction [MINOR]
- **Location**: test_ship_serialization.py:49-82 | **Issue**: Creates Cruiser with 4 real components, recalculate_stats(). Used by 20+ read-only tests. | **Suggestion**: Change to scope="class" for non-mutating test classes. | **LOC affected**: N/A

### tests/integration/research_workflow/test_workflow.py

#### CAT-12: test_process_turn_accumulates_chance -- conditional assertion [MINOR]
- **Location**: test_workflow.py:36-50 | **Issue**: if/else branches in test body forking on breakthrough occurrence. | **Suggestion**: Split into two deterministic tests using seeded RNG. | **LOC affected**: 15

#### CAT-12: test_chance_accumulates_over_turns -- conditional assertion [MINOR]
- **Location**: test_workflow.py:111-129 | **Issue**: Guard assertion behind data-driven len(chances) >= 3 check. Passes silently otherwise. | **Suggestion**: Seed RNG or assert minimum len(chances) before testing. | **LOC affected**: 19

### tests/integration/gameplay_loop/test_commands_colonization.py

#### CAT-12: test_order_cleared_on_completion -- for-loop with conditional break [MINOR]
- **Location**: test_commands_colonization.py:127-147 | **Issue**: for _ in range(5) with if-break retry loop masking as a unit test. | **Suggestion**: Use known-speed fleet + short move guaranteed in one tick. | **LOC affected**: 21

### tests/integration/test_complex_workflow.py

#### CAT-12: test_multiple_complexes_on_planet -- repeated conditional checks [MINOR]
- **Location**: test_complex_workflow.py:315-361 | **Issue**: Repeats if len(queue)>0 3 times -- manual retry loop. | **Suggestion**: Use while loop or compute exact turns needed upfront. | **LOC affected**: 12

### tests/unit/ui/screens/builder/test_weapons_renderer.py

#### CAT-11: test_weapons_renderer_verbose_tooltip_renders_detailed_lines -- fragile exact-list assertion [MAJOR]
- **Location**: test_weapons_renderer.py:81-120 | **Issue**: Asserts entire rendered line list against exact 9-string hardcoded list. Formatting change breaks test. | **Suggestion**: Assert presence of key substrings rather than exact ordered list. | **LOC affected**: 29

### tests/unit/ui/screens/strategy_windows/test_list_windows.py

#### CAT-11: test_star_list_open_creates_centered_window -- fragile rect assertion [MAJOR]
- **Location**: test_list_windows.py:48-63 | **Issue**: Asserts exact rect topleft=(50,40), size=(900,720). Any layout change breaks test. | **Suggestion**: Assert window center is within reasonable region, not exact pixels. | **LOC affected**: 8

### tests/unit/ui/screens/test_new_game_setup_extended.py

#### CAT-8: test_create_ui_uses_controller_default_save_name -- complex patch nesting [MINOR]
- **Location**: test_new_game_setup_extended.py:407-440 | **Issue**: Uses with patch(...) as elements, patch.object(...) as gen: with 5 lambda side_effect assignments. 4+ nested mock layers. | **Suggestion**: Extract patching into helper context manager. | **LOC affected**: 34

### tests/unit/strategy/facade/test_strategy_session_facade_public_api.py

#### CAT-5: fresh_facade fixture is function-scoped when it could be module-scoped [MINOR]
- **Location**: test_strategy_session_facade_public_api.py:202-210 | **Issue**: fresh_facade is never mutated; all tests are read-only contract checks. | **Suggestion**: Change to scope="module". | **LOC affected**: N/A

---

## File Coverage Verification

| File | Read | LOC | Issues |
|------|------|-----|--------|
| tests/regression/modifier_ability_snapshots/test_utility_modifiers.py | Yes | 259 | 0 |
| tests/unit/simulation/interfaces/test_ai_controller_interface.py | Yes | 101 | 0 |
| tests/unit/ui/screens/test_new_game_setup_extended.py | Yes | 440 | 1 |
| tests/unit/strategy/data/test_planetary_facility_characterization.py | Yes | 198 | 0 |
| tests/integration/research_workflow/test_workflow.py | Yes | 264 | 2 |
| tests/unit/strategy/facade/test_strategy_session_facade_public_api.py | Yes | 344 | 1 |
| tests/unit/strategy/services/ability_sources/test_labels.py | Yes | 27 | 0 |
| tests/unit/strategy/engine/test_command_specs_contract.py | Yes | 279 | 0 |
| tests/unit/ui/screens/test_strategy_event_router_esc_modal.py | Yes | 191 | 0 |
| tests/unit/strategy/engine/order_handlers/test_launch_fighters_handler.py | Yes | 275 | 0 |
| tests/unit/ui/screens/test_strategy_game_state_manager.py | Yes | 1411 | 4 |
| tests/unit/strategy/data/test_colony_yard_registries.py | Yes | 109 | 1 |
| tests/unit/workshop/test_workshop_viewmodel_public_api.py | Yes | 135 | 2 |
| tests/unit/ai/test_targeting_rules.py | Yes | 225 | 0 |
| tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py | Yes | 134 | 0 |
| tests/unit/strategy/pathfinding/test_strip_start_hex.py | Yes | 87 | 0 |
| tests/unit/strategy/systems/test_race_randomizer_helpers.py | Yes | 90 | 0 |
| tests/integration/strategy/test_naming.py | Yes | 50 | 0 |
| tests/unit/simulation/systems/test_ship_stats_calculator_phases.py | Yes | 372 | 0 |
| tests/unit/test_lab/test_viewmodel.py | Yes | 319 | 0 |
| tests/unit/strategy/services/test_cargo_transfer_service.py | Yes | 667 | 0 |
| tests/integration/strategy/test_event_log_empire_filter.py | Yes | 129 | 0 |
| tests/integration/test_fms_d_e2e.py | Yes | 257 | 0 |
| tests/integration/strategy/test_fleet_join_redirect.py | Yes | 384 | 0 |
| tests/unit/core/event_logging/test_event_bus.py | Yes | 60 | 0 |
| tests/unit/strategy/facade/test_empire_dto.py | Yes | 297 | 0 |
| tests/unit/simulation/abilities/test_cargo_storage.py | Yes | 267 | 0 |
| tests/integration/test_app_integration.py | Yes | 184 | 0 |
| tests/unit/strategy/data/test_galaxy_spatial_index.py | Yes | 337 | 0 |
| tests/unit/simulation/test_component_decoupling.py | Yes | 233 | 0 |
| tests/unit/strategy/services/test_empire_economy_service.py | Yes | 117 | 0 |
| tests/unit/simulation/systems/test_fighter_launch_init.py | Yes | 198 | 0 |
| tests/unit/ui/screens/builder/test_weapons_renderer.py | Yes | 120 | 1 |
| tests/integration/test_complex_workflow.py | Yes | 439 | 1 |
| tests/unit/strategy/data/test_build_queue_source.py | Yes | 1049 | 0 |
| tests/unit/entities/test_planetary_complex.py | Yes | 106 | 0 |
| tests/unit/systems/test_allowed_layers_removal.py | Yes | 88 | 0 |
| tests/integration/strategy/turn_engine/test_components.py | Yes | 328 | 0 |
| tests/unit/strategy/engine/test_conflict_round_budget.py | Yes | 145 | 0 |
| tests/unit/strategy/data/test_planet_staging_yard_typed_api.py | Yes | 294 | 0 |
| tests/integration/save_load/test_roundtrip_galaxy.py | Yes | 161 | 0 |
| tests/unit/strategy/production_engine/test_habitability.py | Yes | 294 | 0 |
| tests/static_guards/test_no_ship_instance_legacy_kwarg_wrapper.py | Yes | 85 | 0 |
| tests/unit/strategy/data/test_design_metadata_mass_valid.py | Yes | 100 | 0 |
| tests/unit/engine/collision_edge_cases/test_ccd.py | Yes | 376 | 0 |
| tests/unit/strategy/data/test_stars.py | Yes | 760 | 0 |
| tests/unit/ui/screens/builder/test_grouping_strategies.py | Yes | 127 | 0 |
| tests/unit/workshop/test_move_component.py | Yes | 426 | 0 |
| tests/unit/strategy/facade/test_fleet_dto_build.py | Yes | 170 | 0 |
| tests/unit/simulation/components/abilities/test_colonize_harvester.py | Yes | 626 | 0 |
| tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py | Yes | 88 | 0 |
| tests/unit/ui/screens/test_strategy_ui_button_wiring.py | Yes | 88 | 0 |
| tests/unit/research/research_scene/test_event_routing_and_draw.py | Yes | 308 | 0 |
| tests/unit/strategy/engine/test_superweapon_stabilizers.py | Yes | 95 | 0 |
| tests/integration/test_production_engine_fractional_fleet_cost.py | Yes | 280 | 0 |
| tests/unit/strategy/ship_instance/test_ship_instance_bridge.py | Yes | 285 | 0 |
| tests/integration/test_empire_resource_aggregation.py | Yes | 189 | 0 |
| tests/unit/ui/screens/test_strategy_renderer_public_api.py | Yes | 92 | 1 |
| tests/integration/strategy/facade/test_facade_init.py | Yes | 65 | 0 |
| tests/integration/strategy/test_overlapping_storm_combat.py | Yes | 170 | 0 |
| tests/unit/engine/collision_edge_cases/test_beam_ramming.py | Yes | 813 | 0 |
| tests/unit/core/profiling/test_recording.py | Yes | 132 | 0 |
| tests/unit/ui/screens/builder/test_stat_getters.py | Yes | 336 | 0 |
| tests/unit/tools/test_qa_sound_check.py | Yes | 106 | 0 |
| tests/unit/strategy/data/test_galaxy.py | Yes | 840 | 0 |
| tests/unit/systems/test_formula_overflow_underflow.py | Yes | 282 | 0 |
| tests/unit/strategy/engine/test_superweapon_edge_cases.py | Yes | 772 | 0 |
| tests/integration/gameplay_loop/test_commands_colonization.py | Yes | 296 | 1 |
| tests/integration/strategy/test_planet_serialization.py | Yes | 204 | 0 |
| tests/unit/ui/screens/battle_setup/test_input_handler.py | Yes | 311 | 0 |
| tests/integration/test_ramming_e2e.py | Yes | 201 | 0 |
| tests/unit/core/test_role.py | Yes | 80 | 1 |
| tests/unit/tools/test_skill_usage_tracking.py | Yes | 216 | 0 |
| tests/unit/ui/screens/battle_setup/test_spec_compiler_formation.py | Yes | 111 | 0 |
| tests/unit/simulation/entities/test_projectile.py | Yes | 846 | 0 |
| tests/unit/simulation/entities/test_ship_stats_dirty_flag.py | Yes | 82 | 0 |
| tests/unit/core/test_math_vector2.py | Yes | 250 | 0 |
| tests/unit/simulation/test_formula_evaluator.py | Yes | 395 | 0 |
| tests/unit/simulation/entities/test_ship_serialization.py | Yes | 883 | 2 |
| tests/unit/ui/screens/strategy_windows/test_list_windows.py | Yes | 146 | 1 |
| tests/unit/abilities/test_warp_jump.py | Yes | 214 | 0 |
| tests/unit/strategy/engine/test_harvesting_engine_caches.py | Yes | 82 | 0 |
| tests/unit/simulation/components/abilities/test_weapons_integration.py | Yes | 626 | 0 |
| tests/unit/systems/test_arcade_movement.py | Yes | 133 | 0 |
| tests/integration/ui/conftest.py | Yes | 54 | 0 |

## Context Usage Estimate
- Files read: 85 (100% coverage)
- Approximate tokens consumed: ~180k (reading ~24,000 LOC of test files)
- No delegation agents used -- all reading performed by this shard
- Total findings: 28 (11 Critical, 10 Major, 7 Minor)
