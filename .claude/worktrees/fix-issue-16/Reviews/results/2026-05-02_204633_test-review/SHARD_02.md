# Shard 02 — Test Audit Report

## Summary
- Shard: 02
- Files assigned: 80
- Files actually read: 80
- Total findings: 24
- Critical: 4 | Major: 8 | Minor: 12

## Findings

### tests/unit/services/llm/test_package_imports.py (~46 LOC)

#### CAT-1: test_services_package_importable  [CRITICAL]
- **Location**: test_package_imports.py:4-6
- **Issue**: Test body is only `import game.services` with zero assertions. The only way it fails is if the module fails to load, making it a trivial smoke check.
- **Suggestion**: Remove — package importability is already validated by every other test that imports from game.services. Merge into test_llm_package_exports_phase_2_symbols if needed.
- **LOC affected**: 3

#### CAT-1: test_llm_package_importable  [CRITICAL]
- **Location**: test_package_imports.py:8-9
- **Issue**: Test body is only `import game.services.llm` with zero assertions. Redundant with the explicit export tests in the same file.
- **Suggestion**: Remove.
- **LOC affected**: 2

---

### tests/unit/test_modifier_logic.py (~103 LOC)

#### CAT-2: Entire file — Tests Nothing Real  [CRITICAL]
- **Location**: test_modifier_logic.py:1-103
- **Issue**: Every test method (`test_turret_decrement_90`, `test_turret_decrement_15`, `test_turret_increment_15`, `test_size_decrement`, `test_size_increment`) reimplements `calculate_snap_decrement`, `calculate_snap_increment`, and `calculate_size_decrement` locally in the test class and exercises ONLY those local reimplementations. Zero imports from `game.*`. Provides zero regression protection for any production code path.
- **Suggestion**: Remove entire file. The production `ModifierLogicService.calculate_snap_value` is covered by `tests/unit/ui/screens/builder/test_modifier_logic_service.py:195-218`.
- **LOC affected**: 103

---

### tests/regression/test_deprecated_code_removed.py (~200 LOC)

#### CAT-3: test_fleet_movement_simulator_import_fails  [CRITICAL]
- **Location**: test_deprecated_code_removed.py:13-16
- **Issue**: Uses `pytest.raises(ImportError)` to verify a removed module stays removed. This is a dead code guard — the class being guarded was already deleted. The pattern `pytest.raises(ImportError): from x import DeletedClass` is exactly the CAT-3 signal.
- **Suggestion**: Remove this test. The removed module has been gone long enough that regression risk is negligible. The other `hasattr` guards in the same file (GameState aliases, deprecated registry functions) serve the same purpose more cleanly.
- **LOC affected**: 4

---

### tests/unit/simulation/components/test_modifier_manager.py (~443 LOC)

#### CAT-4: Standalone static method tests duplicate instance method coverage  [MAJOR]
- **Location**: test_modifier_manager.py:140-177
- **Issue**: `TestModifierManagerStandalone` tests `add_modifier_static`, `remove_modifier_static`, and `get_modifier_static` — deprecated methods that are thin wrappers. The same add/remove/query operations are tested on instance methods in the preceding test classes (`TestModifierManagerAddRemove`, `TestModifierManagerQuery`, `TestStatefulModifierManagerAddModifier`, `TestStatefulModifierManagerRemoveModifier`, `TestStatefulModifierManagerQuery`).
- **Suggestion**: Remove `TestModifierManagerStandalone` class. If static methods still have production callers, the instance-method tests already cover the same logic paths since the static methods delegate identically.
- **LOC affected**: 38

---

### tests/unit/ui/test_camera.py (~582 LOC)

#### CAT-5: pygame.init() autouse fixtures repeated across 6 classes  [MAJOR]
- **Location**: test_camera.py:22-26, 48-51, 115-118, 164-167, 237-240, 259-262, 305-308
- **Issue**: Six test classes repeat `@pytest.fixture(autouse=True)` with `pygame.init()` and `os.environ['SDL_VIDEODRIVER'] = 'dummy'`. `pygame.init()` is a heavyweight call that only needs to happen once.
- **Suggestion**: Move pygame init to a single `module`-scoped fixture in a `conftest.py` or at the module level. The dummy driver is already set by the repo's top-level `conftest.py`.
- **LOC affected**: ~50 (7 fixture definitions)

---

### tests/unit/ui/services/test_ship_io.py (~1152 LOC)

#### CAT-5: Ship-creation fixtures are function-scoped but used across multiple test classes  [MAJOR]
- **Location**: test_ship_io.py:27-55
- **Issue**: `mock_ship`, `mock_ship_with_special_chars`, and `minimal_ship` fixtures call `create_test_ship()` with `add_bridge=True, registries=fresh_registries` — creating real Ship objects with full component instantiation. These are function-scoped (default) and used across 13 test classes. Each test that uses them re-creates the same Ship from scratch.
- **Suggestion**: Rescope to `class` or `module` level — the ships are not mutated between tests (round-trip tests serialize/deserialize via json, not modify the original).
- **LOC affected**: 30 (fixture definitions)

---

### tests/unit/ui/screens/builder/test_modifier_logic_service.py (~252 LOC)

#### CAT-6: Tests call private _get_base_firing_arc method  [MAJOR]
- **Location**: test_modifier_logic_service.py:47, 57, 67, 73, 84
- **Issue**: Five tests in `TestGetBaseFiringArc` directly call `service._get_base_firing_arc(comp)`, a private method. The tests are tightly coupled to internal implementation rather than testing through the public interface (`get_initial_value` with `turret_mount` or `get_local_min_max`).
- **Suggestion**: Test `_get_base_firing_arc` behavior indirectly through `get_initial_value('turret_mount', comp)` and `get_local_min_max('turret_mount', comp)`. If `_get_base_firing_arc` is independently critical, promote it to a public static helper.
- **LOC affected**: 42

---

### tests/unit/simulation/systems/test_battle_engine_init_ship.py (~92 LOC)

#### CAT-6: Tests call private _initialize_ship method  [MAJOR]
- **Location**: test_battle_engine_init_ship.py:65-93
- **Issue**: All four tests call `battle_engine._initialize_ship(ship)` directly — a private helper method. The test asserts on internal effects (event bus wiring, component update calls, stat recalculation). This is testing implementation details rather than the contract of battle engine initialization.
- **Suggestion**: Test through `engine.start(...)` or `engine.start_teams(...)` public APIs, verifying observable outcomes (e.g., ship is in `engine.ships`, has correct team_id, etc.). If the private helper must be unit-tested, refactor it to a public standalone function.
- **LOC affected**: 31

---

### tests/unit/ui/screens/test_strategy_screen.py (~885 LOC)

#### CAT-6: Mocks internal sub-object delegates  [MAJOR]
- **Location**: test_strategy_screen.py:66-74 (setup), used across ~50 tests
- **Issue**: The test helper `_make_strategy_screen()` injects MagicMock replacements for all internal sub-objects (`_renderer`, `_camera_nav`, `_fleet_ops`, `_colonization`, `_superweapons`, `_build_queue`, `_game_state`, `_input`). Tests then assert these mocks were called with specific arguments, encoding the exact delegation chain. If delegation changes (e.g., `_build_queue` is renamed or split), all tests break even if behavior is unchanged.
- **Suggestion**: Reduce to testing the public API surface (update, draw, handle_event, handle_resize, handle_click) with observable outcomes. Sub-object delegation is an implementation detail.
- **LOC affected**: ~400 (tests relying on mock assertions)

---

### tests/unit/ai/test_ai_controller_unit.py (~809 LOC)

#### CAT-8: Nesting + nonlocal capture for single assertion  [MAJOR]
- **Location**: test_ai_controller_unit.py:284-362
- **Issue**: `test_behavior_context_includes_movement_policy` and `test_behavior_context_uses_movement_policy_values` use 5+ levels of `with patch()` nesting, plus `nonlocal` variable capture and `patch.object` side-effect to intercept behavior calls — all to assert one key-value pair in the context dict. Setup is ~50%+ of test body.
- **Suggestion**: Simplify by calling `controller._build_behavior_context(policy={...})` if that becomes a public method, or restructure the controller so context construction is separable and testable independently.
- **LOC affected**: 78

---

### tests/unit/strategy/test_fleet_speed_calculator.py (~411 LOC)

#### CAT-9: Repeated mock construction across 7 ship-speed tests  [MINOR]
- **Location**: test_fleet_speed_calculator.py:13-131
- **Issue**: Every test in `TestFleetSpeedCalculatorShipSpeed` duplicates the same pattern: create MagicMock ship, set design_data, set get_calculated_stats.return_value, call calculate_ship_speed, assert result. A helper fixture or factory function would eliminate ~50 lines.
- **Suggestion**: Extract a `_make_mock_ship_with_stats(mass, speed)` helper.
- **LOC affected**: 50

#### CAT-10: 7 calculate_ship_speed tests are parametrizable  [MINOR]
- **Location**: test_fleet_speed_calculator.py:13-116
- **Issue**: Tests `test_calculate_ship_speed_formula`, `test_calculate_ship_speed_higher_movement`, `test_calculate_ship_speed_clamped_to_max`, `test_calculate_ship_speed_zero_for_fighters`, `test_calculate_ship_speed_zero_for_complexes`, `test_calculate_ship_speed_zero_for_no_movement`, `test_calculate_ship_speed_handles_missing_stats` all follow the identical pattern: define (vehicle_type, mass, strategic_movement, expected_speed), mock, call, assert.
- **Suggestion**: Parametrize to one `@pytest.mark.parametrize` test.
- **LOC affected**: 103

---

### tests/unit/strategy/services/test_modifier_resolver.py (~126 LOC)

#### CAT-10: 4+ tests have identical structure, differ only in input data  [MINOR]
- **Location**: test_modifier_resolver.py:15-69
- **Issue**: Tests `test_component_with_size_mount_0_2`, `test_component_with_size_mount_1_0`, `test_component_without_modifiers`, `test_component_with_empty_modifiers`, `test_component_with_other_modifiers_only`, `test_string_component_entry`, `test_component_with_multiple_modifiers` all create a comp_entry dict and call `resolve_size_multiplier`, asserting a specific float. Only the dict and expected value differ.
- **Suggestion**: Parametrize to one test: `@pytest.mark.parametrize("entry,expected", [...])`.
- **LOC affected**: 55

---

### tests/unit/ui/screens/test_planet_data_source.py (~555 LOC)

#### CAT-10: Attr-value extraction tests are parametrizable  [MINOR]
- **Location**: test_planet_data_source.py:150-208
- **Issue**: `test_attr_simple_attribute`, `test_attr_dotted_path`, `test_attr_missing_returns_question_mark`, `test_attr_dotted_path_missing_intermediate` all follow identical structure: create planet mock, create column, call get_cell_value, assert result. Only the planet mock and expected result differ.
- **Suggestion**: Parametrize to a single test with `@pytest.mark.parametrize`.
- **LOC affected**: 59

---

### tests/regression/test_deprecated_code_removed.py (~200 LOC)

#### CAT-11: Hardcoded EXPECTED_GAME_COUNT magic number  [MINOR]
- **Location**: test_deprecated_code_removed.py:152-153
- **Issue**: `EXPECTED_GAME_COUNT = 0` and `EXPECTED_TESTS_COUNT = 13` are hardcoded file-search counts. Any legitimate use of `RegistryManager.instance()` that gets added requires updating this constant. The test also walks the entire filesystem to count, making it a fragile snapshot rather than a behavioral test.
- **Suggestion**: Remove the count-based tests (lines 155-199) or make them advisory-only (non-blocking warnings). The `hasattr` checks in the rest of the file already guard against reintroduced code.
- **LOC affected**: 48

---

### tests/integration/ui/test_race_setup_ships_smoke.py (~174 LOC)

#### CAT-12: Logic-heavy test with if/else branches  [MINOR]
- **Location**: test_race_setup_ships_smoke.py:124-154
- **Issue**: `test_every_portrait_is_2048x2048_or_in_allowlist` has if/elif/else branches in the test body checking `EXPECTED_PORTRAIT_GAPS` and `EXPECTED_PORTRAIT_SIZE_MISMATCHES`. The test logic includes conditional assertions with different comparison operators (== vs !=).
- **Suggestion**: Split into two tests: one for allowlisted gaps and one for non-allowlisted portraits. This eliminates the branching and gives clearer failure messages.
- **LOC affected**: 31

---

### tests/unit/ai/test_ai_controller_unit.py (~809 LOC)

#### CAT-8: Complex mock chain for avoidance tests  [MINOR]
- **Location**: test_ai_controller_unit.py:448-621
- **Issue**: The `TestCheckAvoidance` class repeats identical mock setup (mock_ship positioning, mock_grid query returns, patch('game.ai.controller.is_combatant', ...)) across 8 tests. Each test has ~10 lines of repeated setup.
- **Suggestion**: Extract mock setup to a helper method: `_setup_avoidance_test(threats, ship_pos=(100,100), ship_radius=10.0)`.
- **LOC affected**: 80

---

### tests/integration/fleet_combat/test_combat_resource_consumption.py (~425 LOC)

#### CAT-12: Logic-heavy tests with loops and conditionals  [MINOR]
- **Location**: test_combat_resource_consumption.py:276-313
- **Issue**: `test_fuel_depletes_during_continuous_movement` and `test_ammo_depletes_during_weapon_firing` contain for-loops with conditional breaks and multi-step calculations before the final assertion. The test body itself encodes production-like simulation logic.
- **Suggestion**: Extract the resource consumption loop into a test helper with a clear contract. Alternatively, test at the ResourceState level directly (already done in `TestResourceStateBasics`), and keep only one integration scenario.
- **LOC affected**: 38

---

### tests/unit/builder/test_multi_selection_logic.py (~113 LOC)

#### CAT-6: Autouse fixture uses self for state sharing  [MINOR]
- **Location**: test_multi_selection_logic.py:10-50
- **Issue**: The `setup` fixture sets attributes on `self` (old-style unittest pattern) instead of returning test objects. This couples all tests to the class instance and makes test isolation fragile if tests run in parallel.
- **Suggestion**: Convert to standard pytest fixtures that return values or use `fixture`-injection like `self.builder` via `@pytest.fixture` and `self.attr = ...` patterns, or use a helper function instead of autouse.
- **LOC affected**: 40

---

### tests/repro_issues/repro_load_cargo_bug.py (~244 LOC)

#### CAT-3: Standalone repro script covered by proper tests elsewhere  [MINOR]
- **Location**: repro_load_cargo_bug.py:1-244
- **Issue**: This is a standalone diagnostic repro script using `unittest.TestCase` (not pytest), with `print()` diagnostics. It exercises the same `TransferCommandHandler` and `TransferValidator` paths covered by proper unit tests in `tests/unit/strategy/` and `tests/integration/strategy/`.
- **Suggestion**: Review whether the bug this reproduces is still present. If fixed, remove the file. If still present, convert to a focused pytest test in the appropriate integration test dir.
- **LOC affected**: 244

---

### tests/unit/strategy/services/ability_sources/test_system_archetype.py (~68 LOC)

#### CAT-9: Repeated _MockSystem construction  [MINOR]
- **Location**: test_system_archetype.py:16, 21, 26, 32, 41, 46
- **Issue**: Six tests construct `_MockSystem(name=..., archetype=..., intrinsic_abilities=...)` inline. A module-level fixture with parameterization would remove 20 lines of duplication.
- **Suggestion**: Create a `@pytest.fixture` for `_MockSystem` and parametrize the archetype/abilities.
- **LOC affected**: 20

---

## File Coverage Verification
| File | Status | Findings |
|------|--------|----------|
| tests/unit/strategy/planet_atmosphere/test_calculations.py | OK | 0 |
| tests/unit/engine/test_spatial_exact.py | OK | 0 |
| tests/integration/strategy/test_path_projection.py | OK | 0 |
| tests/integration/ui/test_race_setup_ships_smoke.py | CAT-12 | 1 |
| tests/unit/strategy/services/test_modifier_resolver.py | CAT-10 | 1 |
| tests/unit/ui/screens/test_strategy_colonization.py | OK | 0 |
| tests/unit/core/event_logging/test_event_logging.py | OK | 0 |
| tests/integration/replay/test_replay_resolver.py | OK | 0 |
| tests/integration/fleet_combat/test_combat_resource_consumption.py | CAT-12 | 1 |
| tests/unit/ui/screens/builder/test_modifier_logic_service.py | CAT-6 | 1 |
| tests/unit/strategy/test_fleet_speed_calculator.py | CAT-9, CAT-10 | 2 |
| tests/unit/services/llm/test_package_imports.py | CAT-1 (x2) | 2 |
| tests/unit/simulation/systems/test_battle_engine_n_teams.py | OK | 0 |
| tests/unit/ui/screens/test_planet_data_source.py | CAT-10 | 1 |
| tests/unit/builder/test_layer_targeted_actions.py | OK | 0 |
| tests/integration/simulation/test_four_team_battle.py | OK | 0 |
| tests/unit/strategy/services/ability_sources/test_system_archetype.py | CAT-9 | 1 |
| tests/integration/strategy/turn_engine/test_components.py | OK | 0 |
| tests/unit/ui/services/test_ship_io.py | CAT-5 | 1 |
| tests/unit/simulation/components/test_modifier_manager.py | CAT-4 | 1 |
| tests/unit/modifiers/test_formula_edge_cases.py | OK | 0 |
| tests/unit/services/llm/test_types.py | OK | 0 |
| tests/integration/strategy/production/test_fleet_production_e2e.py | OK | 0 |
| tests/unit/ui/screens/test_race_validator.py | OK | 0 |
| tests/unit/tools/test_codex_ship_theme_creator_skill.py | OK | 0 |
| tests/integration/test_make_minimal_spec_smoke.py | OK | 0 |
| tests/integration/strategy/test_fleet_through_unstable_warp_point.py | OK | 0 |
| tests/unit/simulation/systems/test_battle_engine_init_ship.py | CAT-6 | 1 |
| tests/unit/tools/test_scalene_profiling_workflow.py | OK | 0 |
| tests/unit/simulation/entities/test_ship_fleet_attrs.py | OK | 0 |
| tests/unit/ai/test_ai_controller_unit.py | CAT-8 (x2) | 2 |
| tests/unit/strategy/test_component_inspector.py | OK | 0 |
| tests/unit/strategy/ship_instance/test_capacity_levels.py | OK | 0 |
| tests/unit/strategy/generation/test_star_image_registry.py | OK | 0 |
| tests/unit/core/test_bug_reproduction.py | OK | 0 |
| tests/unit/research/test_research_service_edge_cases.py | OK | 0 |
| tests/unit/strategy/data/test_fleet_order_resolution.py | OK | 0 |
| tests/unit/builder/test_multi_selection_logic.py | CAT-6 | 1 |
| tests/unit/ui/test_battle_screen_simulation.py | OK | 0 |
| tests/unit/simulation/systems/test_ship_stats_strategy_attributes.py | OK | 0 |
| tests/unit/strategy/facade/test_event_queries.py | OK | 0 |
| tests/integration/strategy/test_command_handlers.py | OK | 0 |
| tests/unit/ui/test_camera.py | CAT-5 | 1 |
| tests/unit/ui/panels/test_compute_planet_production.py | OK | 0 |
| tests/unit/strategy/services/test_ability_iterator.py | OK | 0 |
| tests/fixtures/test_make_minimal_spec.py | OK | 0 |
| tests/unit/simulation/entities/test_ability_aggregator.py | OK | 0 |
| tests/unit/tools/test_claude_skill_usage_hook.py | OK | 0 |
| tests/unit/simulation/components/abilities/test_colonize_harvester.py | OK | 0 |
| tests/integration/replay/test_replay_store.py | OK | 0 |
| tests/unit/ui/screens/test_strategy_ui_menu.py | OK | 0 |
| tests/unit/ui/screens/test_build_queue_data_source.py | OK | 0 |
| tests/unit/strategy/services/test_system_effects_collector.py | OK | 0 |
| tests/unit/ui/screens/test_battle_results_screen.py | OK | 0 |
| tests/unit/strategy/test_advanced_fleet_orders.py | OK | 0 |
| tests/unit/ui/screens/test_strategy_screen.py | CAT-6 | 1 |
| tests/unit/ui/screens/battle_setup/test_spec_compiler_formation.py | OK | 0 |
| tests/unit/systems/test_persistence.py | OK | 0 |
| tests/unit/strategy/data/test_design_role_registry_invalidation.py | OK | 0 |
| tests/unit/ui/test_modifier_icons.py | OK | 0 |
| tests/unit/ui/screens/test_strategy_input_handler_core.py | OK | 0 |
| tests/unit/strategy/turn_engine/test_dependency_injection.py | OK | 0 |
| tests/unit/test_lab/test_visual_run.py | OK | 0 |
| tests/repro_issues/repro_load_cargo_bug.py | CAT-3 | 1 |
| tests/unit/strategy/generation/density/test_noise.py | OK | 0 |
| tests/unit/ai/test_erratic_behavior_seeded.py | OK | 0 |
| tests/unit/test_modifier_logic.py | CAT-2 | 1 |
| tests/unit/simulation/components/test_modifier_introspection.py | OK | 0 |
| tests/integration/strategy/production/test_completion.py | OK | 0 |
| tests/unit/ui/test_weapons_report_layout.py | OK | 0 |
| tests/regression/test_deprecated_code_removed.py | CAT-3, CAT-11 | 2 |
| tests/unit/simulation/entities/test_ship_physics.py | OK | 0 |
| tests/unit/strategy/engine/test_population_seeding.py | OK | 0 |
| tests/integration/strategy/test_projector_drain_matches_engine.py | OK | 0 |
| tests/unit/core/test_serializable_protocol.py | OK | 0 |
| tests/unit/simulation/components/test_component_stats_calculator.py | OK | 0 |
| tests/unit/ai/target_evaluator/test_projectile_candidate_guards.py | OK | 0 |
| tests/unit/modifiers/test_formula_validation.py | OK | 0 |
| tests/unit/strategy/engine/test_production_refactor.py | OK | 0 |
| tests/unit/strategy/engine/test_superweapon_order_processor.py | OK | 0 |

## Context Usage Estimate
- Total LOC read (test files + production code): ~28,000 (80 test files at ~24,577 + ~3,500 production code scanned for context)
- Approximate headroom: Medium (200-500K)
