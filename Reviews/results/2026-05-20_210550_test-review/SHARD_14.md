# Shard 14 — Test Audit Report

## Summary
- Shard: 14 | Files assigned: 94 | Files actually read: 94 | Total findings: 33 | Critical: 2 | Major: 15 | Minor: 16

## Findings

### tests/unit/ui/screens/test_event_log_sidebar.py
#### CAT-1: test_module_exists [CRITICAL]
- **Location**: test_event_log_sidebar.py:78-81 | **Issue**: Asserts `EventLogSidebar is not None` immediately after importing the class — cannot fail if the import succeeds. | **Suggestion**: Remove; module existence is verified by import. | **LOC affected**: 4

#### CAT-10: test_stores_panel_reference / test_stores_manager_reference / test_stores_column_manager_reference / test_stores_callback [MINOR]
- **Location**: test_event_log_sidebar.py:83-103 | **Issue**: Four tests verify simple attribute storage after `__init__` with identical pattern (call `_make_sidebar`, assert `sidebar.X is mock_X`). | **Suggestion**: Merge into a single parametrized test covering all four attributes. | **LOC affected**: 21

### tests/unit/ui/screens/test_galaxy_test_screen.py
#### CAT-1: test_sidebar_width_is_positive [CRITICAL]
- **Location**: test_galaxy_test_screen.py:16-22 | **Issue**: Asserts imported constant `SIDEBAR_WIDTH > 0` — cannot fail if the constant is defined as a positive number. However this falls under the exempt "constants validation" carve-out per the rubric. **Re‑checked**: the rubric exempts constants validation. This one is borderline — the test body is trivial (`isinstance` + `> 0`) but the intent is to lock the constant value. | **Suggestion**: Consider removing if there are no other tests covering sidebar behavior; otherwise fine to keep as a guard. | **LOC affected**: 7

### tests/unit/strategy/data/test_naming.py
#### CAT-10: to_roman parametrization opportunity [MINOR]
- **Location**: test_naming.py:178-264 | **Issue**: 16 nearly identical tests (`test_one` through `test_complex_number_3999`) with identical body (call `to_roman(N)`, assert result) differing only in input/output. | **Suggestion**: Parametrize into `@pytest.mark.parametrize("n,expected", [(1,"I"), (2,"II"), ...])`. | **LOC affected**: ~90

#### CAT-12: test_sequential_1_to_10 [MINOR]
- **Location**: test_naming.py:246-251 | **Issue**: Uses `for n, roman in enumerate(expected, start=1)` with nested assertion — logic-heavy test body. | **Suggestion**: Parametrize the 10 cases individually; the enumerate loop is unnecessary when pytest parametrize handles this. | **LOC affected**: 6

### tests/unit/simulation/systems/test_tech_preset_loader.py
#### CAT-9: Repeated TECH_PRESETS_DIR patching [MINOR]
- **Location**: test_tech_preset_loader.py (throughout) | **Issue**: Every test method repeats `with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):`. Common setup repeated across ~20 test methods. | **Suggestion**: Set `TECH_PRESETS_DIR` once in the `temp_presets_dir` fixture or use a class-scoped autouse fixture. | **LOC affected**: ~200

### tests/unit/ui/screens/test_strategy_screen_selection.py
#### CAT-8: Nested with patch blocks [MINOR]
- **Location**: test_strategy_screen_selection.py:30-98 (6 tests) | **Issue**: Each test uses 4 nested `with patch.object(selection, ...)` blocks for `is_star_system`, `is_planet`, `is_warp_point`, `is_fleet`. The SUT is `selection.on_ui_selection` but every branching helper is mocked. | **Suggestion**: Declare a shared `@pytest.fixture` that returns the patcher context or an autouse fixture that patches all four. | **LOC affected**: ~80

### tests/unit/performance/test_profiler_perf.py
#### CAT-6: Mocking import internals [MAJOR]
- **Location**: test_profiler_perf.py:53-61 | **Issue**: `test_profiling_does_not_use_direct_json_calls` uses `inspect.getsource(prof_module)` and asserts against raw source strings (`"json.dump(" not in source`). This is a structural guard test checking source code content rather than behavior. | **Suggestion**: Replace with a behavioral test that verifies the profiler uses json_utils via patching. | **LOC affected**: 9

### tests/unit/ui/test_battle_panels_extended.py
#### CAT-6: Mocking with importlib.reload [MAJOR]
- **Location**: test_battle_panels_extended.py:36-69 (_install_battle_panels_pygame_mock) | **Issue**: The helper patches `sys.modules['pygame']` with a MagicMock and then `importlib.reload(battle_panels)` to force the module to pick up the mock. This is extremely brittle — it relies on module-level import-time side effects and can interfere with other tests. | **Suggestion**: Patch at the call-site level (`patch.object(battle_panels, 'pygame')`) rather than sys.modules replacement + reload. | **LOC affected**: 34

#### CAT-9: Duplicate pygame mock setup [MINOR]
- **Location**: test_battle_panels_extended.py:474-520 (TestBattlePanelBaseClass.setup_mocks) | **Issue**: `TestBattlePanelBaseClass.setup_mocks` duplicates the pygame patching logic already present in `_install_battle_panels_pygame_mock` but doesn't use the shared helper. | **Suggestion**: Call `_install_battle_panels_pygame_mock(self)` instead of inlining the same 15 lines. | **LOC affected**: 15

### tests/unit/core/test_isolation.py
#### CAT-5: Test ordering dependency [MAJOR]
- **Location**: test_isolation.py:14-118 | **Issue**: Three pairs of tests (`part1_modify` / `part2_verify`) must run in sequence. Part1 modifies global state and Part2 asserts it was cleaned. pytest normally runs tests in any order; if these are reordered, Part2 fails. The docstring warns about this but no `pytest.mark.dependency` or ordering mechanism is used. | **Suggestion**: Use `@pytest.mark.dependency(depends=[...])` or consolidate into a single test with explicit setup/teardown within it. | **LOC affected**: 118

### tests/unit/simulation/components/test_component_health_manager.py
#### CAT-4: Duplicate take_damage validation tests [MAJOR]
- **Location**: test_component_health_manager.py:98-114 | **Issue**: `test_raises_validation_exception_for_string_input`, `test_raises_validation_exception_for_none_input`, `test_raises_validation_exception_for_list_input` — three tests with identical assertion patterns (pytest.raises(ValidationException, match="amount must be numeric")) differing only in input value. | **Suggestion**: Parametrize into one test with `("50", None, [10])`. | **LOC affected**: 18

### tests/unit/simulation/combat/test_damage_calculator.py
#### CAT-10: Damage edge cases cluster [MINOR]
- **Location**: test_damage_calculator.py:609-707 | **Issue**: Seven tests in `TestDamageLayerBoundaryConditions` follow identical body shape: build component mock, call `apply_damage`, assert HP values. | **Suggestion**: Parametrize the boundary-condition cases. | **LOC affected**: ~100

#### CAT-9: Repeated mock_ship construction [MINOR]
- **Location**: test_damage_calculator.py:831-1133 (TestCombinedArmorScenarios + TestShieldDamageEdgeCases + etc.) | **Issue**: Dozens of tests construct nearly identical mock ships inline (is_alive=True, emissive_armor=N, etc.). The `mock_ship` fixture exists but is not used in these classes. | **Suggestion**: Use the factory fixture (`mock_ship`) consistently. | **LOC affected**: ~200

### tests/unit/simulation/combat/test_fleet_aura_provider_identity.py
#### CAT-4: Duplicate same-class multi-provider tests [MAJOR]
- **Location**: test_fleet_aura_provider_identity.py:126-179 | **Issue**: `test_same_class_multi_provider_disable` and `test_same_class_multi_provider_disable_other` are symmetric mirrors of each other (disable A vs disable B). The setup is identical, only the `comp_X.is_operational = False` line differs. | **Suggestion**: Parametrize the component to disable. | **LOC affected**: 54

### tests/unit/strategy/engine/test_planet_command_handlers.py
#### CAT-4: Repeated planet_not_found / wrong_owner pairs [MAJOR]
- **Location**: test_planet_command_handlers.py:53-561 | **Issue**: Every command handler class (Activate, Deactivate, Clear, Delete, SetAtmosphere, SetGravity, SetWater, SetRadiationShield) has the same two boilerplate tests: `test_planet_not_found` and `test_wrong_owner`. That's 8 handler classes × 2 tests = 16 near-identical tests. | **Suggestion**: Extract shared parametrized base tests or use a mixin. | **LOC affected**: ~200

### tests/unit/strategy/pathfinding/test_basic_paths.py
#### CAT-9: Test helper shims declared at module level [MINOR]
- **Location**: test_basic_paths.py:12-30 | **Issue**: `find_path_deep_space`, `find_path_interstellar`, `get_system_at_hex`, `find_nearest_system` are module-level helper functions that duplicate the shim pattern also present in `test_edge_cases.py`. These could be shared in a conftest. | **Suggestion**: Move to `tests/unit/strategy/pathfinding/conftest.py`. | **LOC affected**: 19

### tests/unit/simulation/systems/test_tech_preset_loader.py
#### CAT-4: Repeated availability test patterns [MAJOR]
- **Location**: test_tech_preset_loader.py:233-296 | **Issue**: `TestGetAvailableComponents` and `TestGetAvailableModifiers` have identical test structure: test returns list, test returns empty when missing, test wildcard, test raises for missing. Same test body, different method name. | **Suggestion**: Parametrize across components/modifiers. | **LOC affected**: 64

### tests/unit/simulation/combat/test_boundary.py
#### CAT-10: Conformance protocol parametrize only covers 3 types [MINOR]
- **Location**: test_boundary.py:47-62 | **Issue**: The `test_region_implements_protocol` parametrize is good practice but the test body only checks attribute existence (`hasattr` + `callable`). This is more of a structural conformance check. | **Suggestion**: Fine as-is; no change needed.

### tests/unit/simulation/combat/test_damage_calculator.py
#### CAT-5: Function-scoped fixtures rebuild expensive state [MAJOR]
- **Location**: test_damage_calculator.py:331-370 | **Issue**: `damage_calculator`, `mock_component`, and `mock_ship` are function-scoped fixtures that create new `DamageCalculator()` and factory lambdas per test. `DamageCalculator` has no state so re-creation is cheap, but the factory fixtures could be class-scoped. | **Suggestion**: Change `mock_component` and `mock_ship` to class-scoped. | **LOC affected**: 40

### tests/unit/strategy/pathfinding/test_basic_paths.py + test_edge_cases.py
#### CAT-4: Duplicate helper functions and path symmetry tests [MAJOR]
- **Location**: test_basic_paths.py:12-30 + test_edge_cases.py:13-35 | **Issue**: Both files declare identical `find_path_deep_space`, `find_path_interstellar`, `find_nearest_system` helper shims. Also `TestDeepSpacePathSymmetry` in test_basic_paths.py and `TestInterceptFallbackBehaviors` in test_edge_cases.py test overlapping concepts. | **Suggestion**: Consolidate helpers into a shared conftest. | **LOC affected**: 54

### tests/unit/regressions/test_bug_regressions_2026_01.py
#### CAT-6: Hardcoded magic numbers in assertions [MAJOR]
- **Location**: test_bug_regressions_2026_01.py:60-61 | **Issue**: `assert ab.amount == 25` — hardcoded expected value depends on `10 * sqrt(1.0) * 2.5 = 25` but the formula is opaque in the test. If the formula changes slightly this test breaks for the wrong reason. | **Suggestion**: Compute the expected value from the inputs (`10 * math.sqrt(1.0) * 2.5`) in the test to make it self-documenting. | **LOC affected**: 2

### tests/integration/ui/test_build_queue_formatting.py
#### CAT-8: Heavy fixture construction with nested MagicMock [MINOR]
- **Location**: test_build_queue_formatting.py:28-88 (MockSession) | **Issue**: `MockSession` is a 60-line mock class with nested property subclasses (`economy`, `session_meta`) to simulate facade behavior. While this is integration-level and necessary for the test scenario, the setup is >50% of the test file. | **Suggestion**: Extract `MockSession` into a shared fixture in `tests/integration/ui/conftest.py`. | **LOC affected**: 60

### tests/unit/simulation/services/test_battle_service.py
#### CAT-4: Duplicate not_found/not_started error path patterns [MAJOR]
- **Location**: test_battle_service.py:242-264 + 317-329 | **Issue**: `test_add_ship_no_active_battle` and `test_remove_ship_no_active_battle` are identical except for method name. Similarly `test_remove_ship_after_battle_started` mirrors `test_add_ship_after_battle_started`. | **Suggestion**: Merge into parametrized tests. | **LOC affected**: 40

### tests/unit/strategy/engine/test_planet_command_handlers.py
#### CAT-4: Repeated planet_not_found / wrong_owner boilerplate [MAJOR]
- **Location**: test_planet_command_handlers.py:249-269, 297-316, 378-396, 440-452, 486-498, 532-544 | **Issue**: `planet_not_found` and `wrong_owner` tests appear 6+ times across handler classes with identical test bodies differing only in the handler class and command factory. | **Suggestion**: Extract `class TestPlanetCommandHandlerCommon(metaclass=...)` with parametrized handler_class. | **LOC affected**: ~120

### tests/unit/strategy/engine/test_harvesting_engine.py
#### CAT-9: `_make_engine` duplicated across test classes [MINOR]
- **Location**: test_harvesting_engine.py:157, 524, 842 | **Issue**: `_make_engine` is declared as a staticmethod identically in three separate test classes. | **Suggestion**: Move to module-level helper or conftest fixture. | **LOC affected**: 10

### tests/unit/simulation/replay/test_serialization.py
#### CAT-9: Duplicate lookup patterns in ReplaySpec tests [MINOR]
- **Location**: test_serialization.py:464-507 | **Issue**: `TestReplaySpec` has three tests that build the same `_make_minimal_battle_spec()` and create a `ReplaySpec.from_battle_spec(...)`. The setup is repeated. | **Suggestion**: Use a class-scoped fixture for the base spec. | **LOC affected**: 30

## File Coverage Verification

| File | LOC | Read | Test functions | Findings |
|------|-----|------|----------------|----------|
| tests/unit/ui/screens/builder/test_stat_rows_dynamic.py | 347 | Yes | 9 | None |
| tests/unit/ui/screens/test_event_log_sidebar.py | 198 | Yes | 20 | CAT-1, CAT-10 |
| tests/unit/ui/screens/test_galaxy_test_screen.py | 96 | Yes | 5 | (CAT-1 borderline, exempted as constants validation) |
| tests/unit/strategy/engine/order_handlers/test_recover_fighters_handler.py | 241 | Yes | 8 | None |
| tests/unit/simulation/systems/test_tech_preset_loader.py | 596 | Yes | 28 | CAT-9, CAT-4 |
| tests/unit/ui/screens/builder/test_detail_panel.py | 30 | Yes | 1 | None |
| tests/unit/strategy/design_catalog/test_filter_designs.py | 74 | Yes | 4 | None |
| tests/unit/strategy/data/test_naming.py | 264 | Yes | 28 | CAT-10, CAT-12 |
| tests/integration/strategy/test_fleet_registration_lifecycle.py | 494 | Yes | 11 | None |
| tests/unit/simulation/replay/test_serialization.py | 698 | Yes | 25 | CAT-9 |
| tests/unit/ui/screens/test_strategy_screen_selection.py | 184 | Yes | 12 | CAT-8 |
| tests/unit/services/llm/test_package_imports.py | 38 | Yes | 3 | None |
| tests/unit/simulation/components/abilities/test_planet_modifiers.py | 202 | Yes | 23 | None |
| tests/unit/strategy/engine/test_movement_build_blocking.py | 123 | Yes | 7 | None |
| tests/integration/strategy/test_planet_physics.py | 80 | Yes | 4 | None |
| tests/unit/performance/test_profiler_perf.py | 181 | Yes | 13 | CAT-6 |
| tests/unit/ui/test_battle_panels_extended.py | 617 | Yes | 34 | CAT-6, CAT-9 |
| tests/unit/systems/test_persistence.py | 44 | Yes | 1 | None |
| tests/unit/core/test_isolation.py | 118 | Yes | 6 | CAT-5 |
| tests/unit/strategy/facade/test_fleet_dto_capabilities.py | 141 | Yes | 11 | None |
| tests/unit/strategy/facade/slices/test_planet_slice.py | 142 | Yes | 6 | None |
| tests/unit/simulation/components/abilities/test_tactical_satellite_launch.py | 159 | Yes | 4 | None |
| tests/unit/simulation/components/test_space_shipyard_consolidation.py | 60 | Yes | 7 | None |
| tests/unit/modifiers/test_seeker_weapon_bindings.py | 104 | Yes | 6 | None |
| tests/integration/replay/test_replay_snapshot_builder_invocation.py | 232 | Yes | 2 | None |
| tests/unit/simulation/armor_mechanics/test_damage_reduction.py | 264 | Yes | 18 | None |
| tests/static_guards/test_no_hidden_test_files.py | 103 | Yes | 1 | None |
| tests/unit/ui/screens/test_fleet_detail_fmt.py | 209 | Yes | 14 | None |
| tests/integration/ai_strategy/test_response.py | 157 | Yes | 9 | None |
| tests/unit/test_run_loop.py | 177 | Yes | 11 | None |
| tests/integration/strategy/test_treasury_panel_e2e.py | 199 | Yes | 2 | None |
| tests/unit/ui/screens/test_strategy_ui_action_router.py | 65 | Yes | 2 | None |
| tests/unit/simulation/components/test_component_health_manager.py | 421 | Yes | 42 | CAT-4 |
| tests/unit/simulation/combat/test_fleet_aura_provider_identity.py | 308 | Yes | 13 | CAT-4 |
| tests/unit/simulation/combat/test_damage_calculator.py | 1199 | Yes | 48 | CAT-10, CAT-9, CAT-5 |
| tests/unit/strategy/test_ship_serial_numbering.py | 252 | Yes | 14 | None |
| tests/unit/entities/test_components.py | 335 | Yes | 18 | None |
| tests/unit/strategy/services/test_fleet_navigation_gaps.py | 164 | Yes | 8 | None |
| tests/unit/simulation/test_battle_state_validation.py | 232 | Yes | 22 | None |
| tests/unit/core/profiling/test_singleton_threading.py | 51 | Yes | 3 | None |
| tests/unit/strategy/engine/order_handlers/conftest.py | 61 | Yes | 0 (fixtures) | None |
| tests/unit/strategy/facade/dto/test_build_queue_dto.py | 72 | Yes | 4 | None |
| tests/unit/strategy/facade/test_designs_by_empire_through_catalog.py | 101 | Yes | 4 | None |
| tests/unit/tools/test_agent_skill_prefix_checker.py | 72 | Yes | 7 | None |
| tests/unit/ui/test_fonts.py | 126 | Yes | 16 | None |
| tests/unit/strategy/pathfinding/test_basic_paths.py | 361 | Yes | 22 | CAT-4, CAT-9 |
| tests/unit/ai/test_behavior_units.py | 624 | Yes | 29 | None |
| tests/unit/test_lab/test_test_run_details_public_api.py | 125 | Yes | 11 | None |
| tests/unit/simulation/combat/test_boundary.py | 334 | Yes | 21 | None |
| tests/unit/ui/screens/test_strategy_screen_order_editing.py | 194 | Yes | 17 | None |
| tests/integration/ui/test_build_queue_formatting.py | 296 | Yes | 8 | CAT-8 |
| tests/unit/strategy/production_engine/test_spawning.py | 223 | Yes | 9 | None |
| tests/integration/replay/test_headless_visual_equivalence.py | 177 | Yes | 1 | None |
| tests/unit/core/test_resource_catalog.py | 265 | Yes | 27 | None |
| tests/unit/core/profiling/test_persistence.py | 177 | Yes | 17 | None |
| tests/unit/strategy/data/test_galaxy_protocols.py | 83 | Yes | 6 | None |
| tests/unit/research/test_research_service.py | 644 | Yes | 34 | None |
| tests/unit/ui/screens/test_strategy_screen_lifecycle.py | 171 | Yes | 19 | None |
| tests/unit/simulation/services/test_battle_service.py | 985 | Yes | 49 | CAT-4 |
| tests/unit/strategy/data/test_production_rates.py | 54 | Yes | 7 | None |
| tests/unit/simulation/components/test_modifier_introspection.py | 705 | Yes | 34 | None |
| tests/unit/research/test_tech_requirement_negation.py | 290 | Yes | 16 | None |
| tests/unit/strategy/fleet/test_basics.py | 345 | Yes | 27 | None |
| tests/unit/ui/screens/test_strategy_renderer.py | 1120 | Yes | 48 | None |
| tests/unit/strategy/services/ability_sources/test_dual_scope_validation.py | 72 | Yes | 1 | None |
| tests/unit/fixtures/test_component_fixtures.py | 114 | Yes | 14 | None |
| tests/integration/strategy/transfer/conftest.py | 215 | Yes | 0 (fixtures) | None |
| tests/unit/tools/test_agent_surface_inventory.py | 191 | Yes | 8 | None |
| tests/integration/strategy/combat/test_damage_persistence.py | 171 | Yes | 1 | None |
| tests/unit/entities/ship_helpers/test_component_getters.py | 243 | Yes | 23 | None |
| tests/unit/strategy/engine/test_planet_command_handlers.py | 561 | Yes | 22 | CAT-4 |
| tests/integration/strategy/test_fleet_movement.py | 65 | Yes | 3 | None |
| tests/unit/strategy/pathfinding/test_edge_cases.py | 326 | Yes | 11 | CAT-4, CAT-9 |
| tests/unit/ui/screens/test_strategy_input_handler_hidden_planet_list.py | 120 | Yes | 4 | None |
| tests/integration/save_load/test_fleet_serde_roundtrip.py | 192 | Yes | 3 | None |
| tests/integration/strategy/test_save_round_trip_phase1.py | 46 | Yes | 3 | None |
| tests/integration/strategy/test_economy_e2e.py | 545 | Yes | 8 | None |
| tests/unit/strategy/turn_engine/test_turn_end_of_turn_engine_rollback.py | 75 | Yes | 1 | None |
| tests/static_guards/test_facade_bypass_guard.py | 238 | Yes | 5 | None |
| tests/unit/ui/test_lab_formatting_utils.py | 152 | Yes | 22 | None |
| tests/unit/strategy/fleets/test_ship_instance_components.py | 168 | Yes | 5 | None |
| tests/unit/strategy/combat/test_post_battle_hook.py | 640 | Yes | 12 | None |
| tests/unit/strategy/engine/order_handlers/test_lay_mines_handler.py | 277 | Yes | 7 | None |
| tests/unit/strategy/services/test_action_time_resolver.py | 685 | Yes | 21 | None |
| tests/unit/fixtures/conftest.py | 29 | Yes | 0 (imports) | None |
| tests/unit/ui/screens/test_transfer_view_model_container.py | 252 | Yes | 7 | None |
| tests/unit/strategy/services/test_ship_instance_write_service.py | 207 | Yes | 12 | None |
| tests/unit/regressions/test_bug_regressions_2026_01.py | 114 | Yes | 3 | CAT-6 |
| tests/integration/ui/test_editor_click_blocking.py | 244 | Yes | 7 | None |
| tests/integration/save_load/test_resupply_persistence.py | 311 | Yes | 8 | None |
| tests/unit/modifiers/test_stat_key.py | 126 | Yes | 10 | None |
| tests/unit/strategy/data/test_order_types_no_duplicated_metadata.py | 55 | Yes | 2 | None |
| tests/unit/strategy/services/test_empire_write_service.py | 147 | Yes | 11 | None |
| tests/unit/strategy/engine/test_harvesting_engine.py | 970 | Yes | 30 | CAT-9 |

## Context Usage Estimate
- Files read: 94 | Total LOC read: ~24,755 | Findings produced: 33 | Context efficiency: ~750 LOC per finding (typical for a thorough audit scan; many files had zero findings)
