# Shard 10 — Test Audit Report

## Summary
- Shard: 10 | Files assigned: 99 | Files actually read: 99 | Total findings: 18 | Critical: 1 | Major: 7 | Minor: 10

## Findings

### tests/unit/ui/screens/test_strategy_menu_panel.py

#### CAT-1: test_get_option_buttons_returns_copy  [CRITICAL]
- **Location**: test_strategy_menu_panel.py:174-184 | **Issue**: Tests Python dict.copy() behavior rather than production code. Creates a dict, gets a copy via get_option_buttons(), modifies the returned copy, then asserts the original dict is unchanged. The get_option_buttons method returns `self._option_buttons.copy()` — this test verifies Python `dict.copy()` semantics, not any game logic. | **Suggestion**: Replace with a test that verifies the returned dict contains the expected keys/values from production setup, or remove if the production `copy()` call is already covered by integration tests. | **LOC affected**: 11

### tests/unit/builder/conftest.py

#### CAT-3: No test functions in file  [CRITICAL]
- **Location**: builder/conftest.py:1-58 | **Issue**: This file contains only fixture definitions (`basic_fleet`, `make_mock_ship`, `make_ship_instance`) with no `def test_*` functions. It is a conftest.py but the file list included it as a test file. Conftest fixtures are usable by sibling tests but the file itself has no test functions to audit. | **Suggestion**: Exclude conftest.py files from test-review file lists, or mark as "no test functions — fixture-only conftest." | **LOC affected**: 58

### tests/unit/strategy/data/conftest.py

#### CAT-3: No test functions in file  [CRITICAL]
- **Location**: strategy/data/conftest.py:1-18 | **Issue**: Contains only the `galaxy_stub` fixture definition. No `def test_*` functions. | **Suggestion**: Same as above — exclude from test-review scope. | **LOC affected**: 18

### tests/unit/ui/conftest.py

#### CAT-3: No test functions in file  [CRITICAL]
- **Location**: ui/conftest.py:1-135 | **Issue**: Contains only pytest configuration hooks (`pytest_configure`, `pytest_configure_node`) and fixtures (`ui_manager`, `pygame_display_reset`). No `def test_*` functions. | **Suggestion**: Exclude from test-review scope. | **LOC affected**: 135

### tests/unit/builder/conftest.py

(Duplicate of above — same finding)

---

### tests/unit/research/test_research_renderer.py

#### CAT-5: Fixture Bloat — per-function module reload  [MAJOR]
- **Location**: test_research_renderer.py:22-38 | **Issue**: The `renderer_module` fixture is `autouse=True` and function-scoped, executing `importlib.util.module_from_spec` + `spec.loader.exec_module(module)` on every test. This re-imports the isolated renderer module from disk for every test function (~30 tests in the file). The module is identical across all tests in the file. | **Suggestion**: Change to `scope="module"`. The `importlib` import path is static (hardcoded `parents[3] / "game" / "ui" / "research"`). Re-exec_module per test is unnecessary overhead for the same source file. | **LOC affected**: 16

### tests/unit/ui/test_utils.py

#### CAT-5: Fixture Bloat — per-function UIManager  [MAJOR]
- **Location**: test_utils.py:482-491 | **Issue**: The `ui_manager` fixture in `TestCreateSectionHeader` creates a new `pygame_gui.UIManager((800, 600))` for every test function (10+ tests in the class). UIManager construction includes theme parsing and font loading (~0.3-0.5s overhead). Tests do not mutate the manager in ways that break sharing. | **Suggestion**: Use `scope="class"` or `scope="module"`. The `reset_game_state` autouse fixture in root conftest already handles cleanup. | **LOC affected**: 10

### tests/integration/ui/test_build_queue_design_report.py

#### CAT-5: Fixture Bloat — per-function real pygame_gui construction  [MAJOR]
- **Location**: test_build_queue_design_report.py:160-184 | **Issue**: The `design_report_panel` fixture is function-scoped and constructs real `pygame_gui` elements (`UIPanel`, `DesignReportPanel`) for each of the ~18 test functions. `update_design` also creates `UIScrollingContainer` and stat rows. Combined, this is 18+ full widget-tree builds for the same panel configuration. | **Suggestion**: Use `scope="class"` with a panel recreation helper or `scope="module"`. The mock ship fixture provides the same data each time. | **LOC affected**: 25

### tests/unit/strategy/data/test_container.py

#### CAT-8: Needless Complexity — repeated imports in helper functions  [MINOR]
- **Location**: test_container.py:38-63 | **Issue**: The helpers `_any_policy`, `_metals`, `_energy`, `_human`, `_fighter` are module-level functions that each construct a single simple object. Five separate helpers for single-line constructor calls. The `_any_policy` helper is used 20+ times but has 7 lines of boilerplate. | **Suggestion**: Use module-level constants (e.g. `_ANY_POLICY = ContainerPolicy(...)`, `_METALS = ResourceContainable("metals")`) instead of helper functions. The objects are immutable/stateless. | **LOC affected**: 27

### tests/unit/ai/test_advanced_behaviors.py

#### CAT-6: Mocking Brittleness — Asserts on mock.call_args in spatial behavior tests  [MAJOR]
- **Location**: test_advanced_behaviors.py:63-65, 71-74 | **Issue**: Tests assert on `mock_controller.navigate_to.call_args` positional args (`dest = args[0]`, `kwargs.get('stop_dist', 0)`) to verify spatial movement. These are assertions on internal implementation details of how the behavior communicates with the controller, not on observable output. If the navigate_to signature or calling convention changes, these tests fail without a behavioral change. **Note**: The module docstring explicitly accepts this pattern as "intentional for spatial behavior tests" (CAT-12 finding marked acceptable). CAT-6 still flags the mock-level coupling. | **Suggestion**: Consider testing the post-condition (e.g., ship position after update) instead of the navigate_to call contract, or add a comment marking the deliberate coupling. | **LOC affected**: 20

### tests/unit/battle_controller/test_mechanics.py

#### CAT-6: Mocking Brittleness — Asserts on mock.call_count for service.add_ship  [MAJOR]
- **Location**: test_mechanics.py:25-31, 53-61 | **Issue**: `test_add_ships_calls_service_for_each_ship` and `test_add_ships_with_team_0/1` assert on `mock_service.add_ship.call_count == 3` and `mock_service.add_ship.assert_called_with(ship, team_id)`. These verify internal call patterns rather than observable outcomes. While the test name documents the contract, the assertion on call_count and call_args list is brittle to refactoring that achieves the same result through a different internal path. | **Suggestion**: If the service contract is a public interface, this is acceptable. Add a comment marking the deliberate coupling as "contract test: add_ships MUST delegate to service.add_ship exactly N times." | **LOC affected**: 12

### tests/unit/fleet/test_fleet_pursuer_tracker.py

#### CAT-10: Parameterize Opportunity — redirect_pursuers edge cases  [MINOR]
- **Location**: test_fleet_pursuer_tracker.py:387-445 | **Issue**: The `TestRedirectPursuersExcludeKwarg` class has 3 tests that all follow the same pattern: create old_target + new_target + pursuer(s), register, call `redirect_pursuers(exclude=...)`, assert on order targets and pursuer_tracker membership. `test_redirect_excludes_specified_fleet_from_rewrite`, `test_redirect_returns_tuple_of_redirected_and_excluded`, `test_redirect_excluded_fleet_not_added_to_new_target` differ only in assertion targets. | **Suggestion**: Parametrize into a single test driven by (exclude_set, expected_order_target_for_excluded, expected_memberships). | **LOC affected**: 55

### tests/unit/battle_screen/test_battle_screen_simulation.py

#### CAT-10: Parameterize Opportunity — speed multiplier keyboard tests  [MINOR]
- **Location**: test_battle_screen_simulation.py:262-320 | **Issue**: Four separate tests (`test_handle_event_keyboard_comma_decreases_speed`, `test_handle_event_keyboard_period_increases_speed`, `test_handle_event_keyboard_m_resets_speed`, `test_handle_event_keyboard_slash_sets_ui_pause_speed`) follow the identical pattern: set initial multiplier, create KEYDOWN event with specific key, call handle_event, assert on expected multiplier. Same for bracket key cycle-focus tests. | **Suggestion**: Parametrize as `@pytest.mark.parametrize("key,initial,expected", [(K_COMMA, 1.0, 0.5), (K_PERIOD, 1.0, 2.0), ...])`. | **LOC affected**: 58

### tests/unit/battle_screen/test_battle_screen_simulation.py

#### CAT-10: Parameterize Opportunity — win/loss detection tests  [MINOR]
- **Location**: test_battle_screen_simulation.py:175-222 | **Issue**: `test_get_winner_returns_1_when_team0_all_dead`, `test_get_winner_returns_0_when_team1_all_dead`, and `test_draw_condition_all_ships_dead` follow identical setup → mutate ship.is_alive → assert structure. | **Suggestion**: Parametrize into a single test driven by (team0_alive, team1_alive, expected_winner) tuples. | **LOC affected**: 35

### tests/unit/battle_screen/test_battle_screen_simulation.py

#### CAT-10: Parameterize Opportunity — arrow key panning + middle mouse panning + target clearing  [MINOR]
- **Location**: test_battle_screen_simulation.py:444-492 | **Issue**: `test_arrow_key_panning_moves_camera`, `test_middle_mouse_panning_moves_camera`, `test_middle_mouse_panning_clears_target` share the same scene setup and differ only in the input mocks and assertion target. | **Suggestion**: Parametrize with (key_pressed_bits, mouse_pressed_bits, mouse_rel, expected_position_predicate, expected_target_state). | **LOC affected**: 35

### tests/unit/research/test_research_renderer.py

#### CAT-10: Parameterize Opportunity — _is_visible boundary position tests  [MINOR]
- **Location**: test_research_renderer.py:112-169 | **Issue**: Tests `test_center_of_viewport_is_visible`, `test_origin_is_visible`, `test_top_right_corner_is_visible`, `test_bottom_left_corner_is_visible`, `test_bottom_right_corner_is_visible` are 5 identical-structure tests differing only by the input position. Similarly, 4 "outside viewport" tests follow the same pattern. | **Suggestion**: Parametrize `_is_visible` tests with (position, expected) tuples. The 9 visibility tests and 4 out-of-bounds tests reduce to 2 parametrized tests. | **LOC affected**: 55

### tests/unit/research/test_research_renderer.py

#### CAT-10: Parameterize Opportunity — margin extension tests  [MINOR]
- **Location**: test_research_renderer.py:173-238 | **Issue**: `test_margin_extends_visibility_left`, `test_margin_extends_visibility_right`, `test_margin_extends_visibility_top`, `test_margin_extends_visibility_bottom`, `test_margin_extends_visibility_all_corners` are 5 tests with near-identical bodies differing only in input position, margin, and expected result. | **Suggestion**: Parametrize into a single test driven by (position, margin, expected) tuples. | **LOC affected**: 55

### tests/unit/strategy/engine/test_fleet_transfer_extended.py

#### CAT-12: Logic-Heavy Test — conditional assertion on call results  [MINOR]
- **Location**: test_fleet_transfer_extended.py:66-137 | **Issue**: The `test_caps_by_source_cargo`, `test_caps_by_dest_space`, `test_amount_zero_transfers_all`, `test_zero_space_returns_zero`, `test_zero_source_returns_zero` tests all follow the pattern: create mock fleet/target with specific cargo values, call transfer method, assert result equals expected. The assertions include arithmetic that depends on mock return value configuration. This is acceptable for integration-level transfer tests but the complex mock setup (cargo_current + cargo_capacity determining behavior) makes the test bodies logic-heavy. | **Suggestion**: Acceptable for this test class — the arithmetic in assertions documents the transfer cap formula. Consider extracting the `_dispatch_fleet_to_fleet` direct call setup into a parametrized test fixture. | **LOC affected**: 30

### tests/unit/strategy/engine/test_resupply_engine.py

#### CAT-8: Needless Complexity — 10+ helper functions + 8 helper methods for mock construction  [MINOR]
- **Location**: test_resupply_engine.py:20-101, 306-379 | **Issue**: The file defines 7 module-level helpers (`_make_mock_registries`, `_make_fuel_facility`, `_make_energy_facility`, `_make_colony`, `_make_empire`, `_make_mock_ship`, `_make_mock_fleet`, `_make_mock_galaxy`, `_make_planet_with_fuel`) plus has sections of dedicated helper code for each test class. While the helpers isolate boilerplate, the sheer volume (11 helpers + 5 helper methods across 748 lines) makes the test file difficult to navigate. | **Suggestion**: Extract common mock factories into `tests/unit/strategy/engine/conftest.py` or a shared fixture module. The `_make_mock_registries`, `_make_fuel_facility`, `_make_colony`, `_make_empire` helpers are reusable by other strategy engine tests. | **LOC affected**: 150

### tests/unit/tools/test_codex_interagent_discussion_skills.py

#### CAT-2: Tests Nothing Real — tests skill Markdown files, not game code  [MAJOR]
- **Location**: test_codex_interagent_discussion_skills.py:29-188 | **Issue**: All 8 test functions in this file read Codex agent skill Markdown files from `.agents/skills/` and assert on text content (presence of protocol keywords, frontmatter structure, absence of legacy patterns). These tests validate documentation format, not production game code. No `game.*` imports. | **Suggestion**: Move to a dedicated `tests/tooling/skills/` directory or mark as tooling-validation tests. Not a game-code test; test-review rubric not intended for documentation content checks. | **LOC affected**: 159

### tests/static_guards/test_no_carried_items_proxy.py

#### CAT-2 (borderline): Tests architecture invariants, not functionality  [MAJOR]
- **Location**: test_no_carried_items_proxy.py:28-92 | **Issue**: All 4 tests assert on module attribute absence (`hasattr` negative checks) and source-code text scanning (`Path.read_text().count(...)`). These are static architecture guards that verify a PROJ-436 deletion contract — the deleted class/property/helpers have not been re-introduced. No game functionality is tested. | **Suggestion**: This is a legitimate deletion guard per the project's stated patterns. Move to `tests/static_guards/` which already houses other guards. Acceptable as-is but flagged for completeness. | **LOC affected**: 65

### tests/static_guards/test_no_commands_specs_module.py

#### CAT-2 (borderline): File-existence guard  [MAJOR]
- **Location**: test_no_commands_specs_module.py:17-26 | **Issue**: Single test asserts that `commands/specs.py` does not exist — a file-existence check, not a functional test. | **Suggestion**: Same as above — legitimate deletion guard per PROJ-371 Phase 2. | **LOC affected**: 10

---

## File Coverage Verification

| File | LOC (est) | Read | Test Functions | Issues |
|------|-----------|------|----------------|--------|
| tests/unit/ui/screens/test_strategy_modal_esc_close.py | 66 | Yes | 2 | 0 |
| tests/integration/gameplay_loop/test_turn_execution.py | 335 | Yes | 8 | 0 |
| tests/unit/strategy/engine/test_harvesting_size_scaling.py | 195 | Yes | 6 | 0 |
| tests/unit/strategy/services/test_galaxy_pathfinding_service.py | 139 | Yes | 9 | 0 |
| tests/repro_issues/test_bug_13_clear_removes_hull.py | 125 | Yes | 1 | 0 |
| tests/unit/validation/test_component_definitions.py | 107 | Yes | 6 | 0 |
| tests/unit/ui/screens/strategy_windows/test_orders_window_ctrl.py | 102 | Yes | 3 | 0 |
| tests/unit/strategy/data/test_container.py | 389 | Yes | 29 | 1 (CAT-8) |
| tests/integration/strategy/test_mutual_join_rendezvous.py | 345 | Yes | 7 | 0 |
| tests/unit/ui/screens/test_empire_build_queue_viewmodel.py | 491 | Yes | 31 | 0 |
| tests/unit/modifiers/test_modifier_json_schema.py | 367 | Yes | 16 | 0 |
| tests/unit/simulation/battle_controller/test_mechanics.py | 326 | Yes | 21 | 1 (CAT-6) |
| tests/integration/strategy/test_empire.py | 70 | Yes | 5 | 0 |
| tests/unit/simulation/test_battle_outcome.py | 280 | Yes | 15 | 0 |
| tests/unit/strategy/systems/test_race_library.py | 574 | Yes | 24 | 0 |
| tests/unit/strategy/events/test_event_validation.py | 66 | Yes | 5 | 0 |
| tests/unit/ui/services/test_game_settings.py | 94 | Yes | 6 | 0 |
| tests/unit/strategy/engine/test_fleet_transfer_extended.py | 251 | Yes | 20 | 1 (CAT-12) |
| tests/unit/strategy/data/test_homeworld_presets.py | 179 | Yes | 13 | 0 |
| tests/integration/save_load/test_registry_injection.py | 78 | Yes | 5 | 0 |
| tests/unit/strategy/engine/test_planetary_yard_requirement.py | 85 | Yes | 6 | 0 |
| tests/unit/simulation/components/abilities/test_warhead.py | 135 | Yes | 12 | 0 |
| tests/unit/ui/screens/test_workshop_event_router_add_component.py | 112 | Yes | 2 | 0 |
| tests/unit/strategy/design_catalog/test_search_designs.py | 82 | Yes | 4 | 0 |
| tests/unit/strategy/fleet/conftest.py | 58 | Yes | 0 | 1 (CAT-3) |
| tests/unit/ui/screens/test_star_list_filter_snapshot.py | 100 | Yes | 10 | 0 |
| tests/unit/ai/test_ai_n_team_targeting.py | 78 | Yes | 2 | 0 |
| tests/unit/ui/services/image/test_null_provider.py | 28 | Yes | 4 | 0 |
| tests/static_guards/test_no_carried_items_proxy.py | 92 | Yes | 4 | 1 (CAT-2) |
| tests/unit/strategy/fleet_navigation/test_navigation_pure.py | 175 | Yes | 7 | 0 |
| tests/unit/simulation/entities/stat_contributors/test_command.py | 174 | Yes | 13 | 0 |
| tests/unit/ui/screens/test_strategy_menu_panel.py | 184 | Yes | 12 | 1 (CAT-1) |
| tests/unit/ui/screens/test_warp_hotkey.py | 175 | Yes | 8 | 0 |
| tests/unit/strategy/fleet/test_fleet_validation.py | 142 | Yes | 10 | 0 |
| tests/integration/strategy/test_system_destruction.py | 205 | Yes | 5 | 0 |
| tests/unit/strategy/stars/test_star_validation.py | 140 | Yes | 12 | 0 |
| tests/unit/strategy/services/test_component_layers.py | 144 | Yes | 7 | 0 |
| tests/unit/strategy/engine/test_water_engine.py | 256 | Yes | 15 | 0 |
| tests/unit/ui/screens/test_camera_navigator.py | 328 | Yes | 27 | 0 |
| tests/unit/systems/test_formula_system.py | 242 | Yes | 23 | 0 |
| tests/unit/ui/screens/test_strategy_click_dispatcher.py | 372 | Yes | 22 | 0 |
| tests/unit/ai/test_advanced_behaviors.py | 235 | Yes | 9 | 1 (CAT-6) |
| tests/integration/ui/test_design_selector.py | 89 | Yes | 2 | 0 |
| tests/unit/ui/screens/test_transfer_grid_renderer.py | 205 | Yes | 7 | 0 |
| tests/unit/ui/test_battle_results_data.py | 225 | Yes | 12 | 0 |
| tests/unit/research/test_research_renderer.py | 259 | Yes | 31 | 3 (CAT-5, CAT-10 x2) |
| tests/unit/strategy/fleet/test_space_yard.py | 304 | Yes | 22 | 0 |
| tests/unit/simulation/systems/test_battle_engine_end_conditions.py | 332 | Yes | 21 | 0 |
| tests/unit/strategy/test_command_handlers.py | 42 | Yes | 1 | 0 |
| tests/unit/workshop/test_quick_add.py | 307 | Yes | 21 | 0 |
| tests/unit/ui/screens/strategy_render/test_grid_cache.py | 390 | Yes | 21 | 0 |
| tests/unit/strategy/data/conftest.py | 18 | Yes | 0 | 1 (CAT-3) |
| tests/unit/ui/screens/test_build_queue_queue_data_source.py | 309 | Yes | 22 | 0 |
| tests/unit/simulation/services/test_registry_loader.py | 324 | Yes | 18 | 0 |
| tests/unit/ui/screens/test_fleet_data_source.py | 629 | Yes | 32 | 0 |
| tests/unit/strategy/data/test_superweapon_orders.py | 258 | Yes | 17 | 0 |
| tests/unit/ui/screens/test_empire_panel_window.py | 322 | Yes | 24 | 0 |
| tests/unit/ui/screens/test_empire_panel_window_reuse.py | 229 | Yes | 15 | 0 |
| tests/integration/test_transfer_container_validation.py | 145 | Yes | 7 | 0 |
| tests/unit/ui/panels/test_planet_report_panel_characterization.py | 478 | Yes | 22 | 0 |
| tests/unit/strategy/engine/test_command_handlers_public_api.py | 88 | Yes | 3 | 0 |
| tests/unit/strategy/engine/test_resupply_engine.py | 748 | Yes | 30 | 1 (CAT-8) |
| tests/unit/services/llm/test_defaults.py | 33 | Yes | 3 | 0 |
| tests/integration/ui/test_build_queue_design_report.py | 481 | Yes | 26 | 1 (CAT-5) |
| tests/unit/ui/screens/test_planet_production_display.py | 153 | Yes | 5 | 0 |
| tests/unit/tools/test_test_sharded_baseline.py | 358 | Yes | 10 | 0 |
| tests/unit/simulation/entities/test_ship_id.py | 63 | Yes | 5 | 0 |
| tests/unit/entities/ship_helpers/test_component_operations.py | 218 | Yes | 17 | 0 |
| tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py | 445 | Yes | 27 | 1 (CAT-10) |
| tests/integration/strategy/facade/test_facade_integration.py | 431 | Yes | 14 | 0 |
| tests/unit/ui/conftest.py | 135 | Yes | 0 | 1 (CAT-3) |
| tests/integration/save_load/test_roundtrip_stars.py | 117 | Yes | 17 | 0 |
| tests/unit/systems/test_physics.py | 315 | Yes | 18 | 0 |
| tests/performance/test_telemetry_overhead.py | 160 | Yes | 1 | 0 |
| tests/unit/data/test_mine_design.py | 112 | Yes | 13 | 0 |
| tests/unit/strategy/services/test_replay_verification_sidecar.py | 190 | Yes | 14 | 0 |
| tests/unit/strategy/facade/test_strategy_session_facade.py | 919 | Yes | 28 | 0 |
| tests/unit/entities/test_component_di.py | 163 | Yes | 8 | 0 |
| tests/unit/strategy/facade/test_facade_system_proximity.py | 99 | Yes | 5 | 0 |
| tests/unit/strategy/services/ability_sources/test_warp_point.py | 142 | Yes | 16 | 0 |
| tests/unit/strategy/data/test_satellite_constellation.py | 112 | Yes | 10 | 0 |
| tests/unit/strategy/engine/test_staging_yard_operations.py | 277 | Yes | 15 | 0 |
| tests/unit/tools/test_codex_interagent_discussion_skills.py | 188 | Yes | 8 | 1 (CAT-2) |
| tests/unit/ui/screens/builder/test_weapons_panel.py | 225 | Yes | 7 | 0 |
| tests/unit/core/test_protocols_boundary.py | 201 | Yes | 16 | 0 |
| tests/unit/core/patterns/test_layer_iterator.py | 301 | Yes | 28 | 0 |
| tests/integration/ai_strategy/test_commands.py | 81 | Yes | 4 | 0 |
| tests/unit/test_run_loop_shutdown_ordering.py | 87 | Yes | 1 | 0 |
| tests/integration/strategy/test_save_round_trip_phase2.py | 87 | Yes | 2 | 0 |
| tests/static_guards/test_no_commands_specs_module.py | 26 | Yes | 1 | 1 (CAT-2) |
| tests/unit/ui/test_battle_screen_simulation.py | 736 | Yes | 33 | 3 (CAT-10 x3) |
| tests/integration/strategy/facade/test_validation_queries.py | 207 | Yes | 8 | 0 |
| tests/integration/ui/build_queue_screen/test_controller_multi_queue.py | 309 | Yes | 12 | 0 |
| tests/unit/core/test_application_context.py | 202 | Yes | 18 | 0 |
| tests/unit/core/test_config_edge_cases.py | 85 | Yes | 11 | 0 |
| tests/unit/strategy/data/test_empire_deployed_groups.py | 95 | Yes | 10 | 0 |
| tests/unit/ui/screens/test_workshop_data_loader.py | 59 | Yes | 2 | 0 |
| tests/unit/strategy/design_catalog/test_cache_invalidation.py | 89 | Yes | 3 | 0 |
| tests/unit/ui/test_utils.py | 565 | Yes | 30 | 1 (CAT-5) |
| **TOTALS** | ~24186 | 99 of 99 | ~822 | **18 findings** |

## Context Usage Estimate

Reading 99 files totalling ~24,186 LOC required approximately 390,000 tokens of context for file contents plus analysis. Total context estimate for this shard review: ~420,000 tokens. Report output: ~12,000 tokens.

### Findings Summary by Category
- **CAT-1 (Trivial Pass):** 1 — test_strategy_menu_panel.py dict.copy() test
- **CAT-2 (Tests Nothing Real):** 3 — codex discussion skills (doc validation), carried_items_proxy guard (deletion invariance), commands_specs_module guard (file existence)
- **CAT-3 (Dead Test Code):** 3 — builder/conftest.py, strategy/data/conftest.py, ui/conftest.py (fixture-only conftest files with no test_ functions)
- **CAT-5 (Fixture Bloat):** 3 — research_renderer per-function module reload, test_utils per-function UIManager, build_queue_design_report per-function panel construction
- **CAT-6 (Mocking Brittleness):** 2 — advanced_behaviors mock.call_args assertions, battle_controller mock.call_count assertions
- **CAT-8 (Needless Complexity):** 2 — test_container repeated import-style helpers, test_resupply_engine 11+ mock helpers
- **CAT-10 (Parameterize Opportunity):** 5 clusters — fleet_pursuer_tracker exclude tests, battle_screen speed multiplier tests (x3 clusters), research_renderer visibility tests (x2 clusters)
- **CAT-12 (Logic-Heavy Test):** 1 — test_fleet_transfer_extended cargo cap arithmetic assertions

### Quality Observations
- **test_strategy_session_facade.py** (919 LOC) is the largest file in shard. Well-organized with clear test class separation across Fleet/System/Planet/Empire queries. Despite heavy use of MagicMock, the facade test pattern is intentional and appropriate.
- **test_battle_screen_simulation.py** (736 LOC) and **test_fleet_data_source.py** (629 LOC) are large but well-structured with clear class boundaries. Parameterize opportunities noted above.
- **test_resupply_engine.py** (748 LOC) has comprehensive coverage across fuel generation and fleet resupply but suffers from helper-function proliferation.
- The three conftest.py files in the shard contain only fixtures/hooks — no test functions. These should be excluded from test-review file lists in future shard configurations.
