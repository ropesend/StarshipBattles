# Shard 09 — Test Audit Report

## Summary
- Shard: 09
- Files assigned: 74
- Files actually read: 74
- Total findings: 37
- Critical: 6 | Major: 11 | Minor: 20

## Findings

### tests/repro_issues/repro_facade_colonies.py (~93 LOC)

#### CAT-3: Entire file — standalone repro script  [CRITICAL]
- **Location**: repro_facade_colonies.py:1-93
- **Issue**: This is a standalone unittest.TestCase repro script, not a proper pytest test. Standalone repro scripts covered by proper tests elsewhere are dead test code per rubric.
- **Suggestion**: Remove if the behavior is tested by the proper integration tests (e.g., tests/integration/strategy/facade/test_validation_queries.py or similar). Otherwise, migrate to pytest.
- **LOC affected**: 93

### tests/unit/strategy/pathfinding/test_intercept_edge_cases.py (~27 LOC)

#### CAT-1: test_pathfinding_module_exists, test_intercept_function_exists, test_find_path_functions_exist  [CRITICAL]
- **Location**: test_intercept_edge_cases.py:13-27
- **Issue**: Three tests that only check importability (`assert pathfinding is not None`, `assert calculate_intercept_point is not None`). These cannot fail unless the module is deleted — trivial pass tests.
- **Suggestion**: Remove these tests; importability is verified implicitly by any real test in the same file.
- **LOC affected**: 15

### tests/unit/ui/test_race_theme_gallery.py (~274 LOC)

#### CAT-1: test_race_theme_gallery_has_button_list, test_race_theme_gallery_has_scroll_container  [CRITICAL]
- **Location**: test_race_theme_gallery.py:51-70
- **Issue**: Tests manually set attributes (`gallery.asset_buttons = []`) then assert `isinstance(gallery.asset_buttons, list)`. The assertion checks a value the test itself set — trivial pass.
- **Suggestion**: Remove or replace with integration tests that verify real button creation through the full init path.
- **LOC affected**: 20

### tests/integration/strategy/test_production_rates.py (~361 LOC)

#### CAT-2: test_high_metal_cost_creates_multi_turn_build, test_mixed_resources_bottleneck_determines_turns, test_cost_per_tick_* (multiple), test_resource_consumption_* (multiple)  [CRITICAL]
- **Location**: test_production_rates.py:108-145, 180-283
- **Issue**: These tests reimplement the per-resource turn calculation logic locally (`math.ceil`, `max(1, max(...))`, min/max logic) rather than calling production code. The tests exercise copied local logic, not the real `BuildQueueController` or production pipeline. Three test classes (`TestPerResourceTurnCalculation`, `TestCostPerTickCapping`, `TestResourceConsumptionOverTurns`) duplicate algorithm logic inline.
- **Suggestion**: Replace with tests that call actual production methods and assert return values, or extract the algorithm into a pure function tested separately.
- **LOC affected**: ~175

### tests/unit/ui/test_race_asset_loader.py (~546 LOC)

#### CAT-1: test_load_portrait_full_has_correct_signature  [CRITICAL] (downgraded to MAJOR — small blast radius, single test)
- **Location**: test_race_asset_loader.py:85-93
- **Issue**: Tests `assert hasattr(loader, 'load_portrait_full')` and `assert callable(loader.load_portrait_full)` — can never fail if imports succeed.
- **Suggestion**: Remove.
- **LOC affected**: 9

### tests/unit/ui/panels/test_planet_report_panel.py (~987 LOC)

#### CAT-1: test_function_exists  [CRITICAL] (downgraded to MAJOR — small blast radius)
- **Location**: test_planet_report_panel.py:247-251
- **Issue**: `assert callable(compute_planet_production)` — trivial pass.
- **Suggestion**: Remove.
- **LOC affected**: 5

### tests/unit/strategy/test_quickstart_builder.py (~409 LOC)

#### CAT-9: Repeated spawn_initial_complexes setup  [MINOR]
- **Location**: test_quickstart_builder.py:216-409
- **Issue**: Nine `test_spawn_initial_complexes_*` tests each recreate the same empire/session/home_planet MagicMock setup plus the same `with patch('game.strategy.quickstart_builder.DesignLibrary')` block. ~50% of each test body is duplicated setup.
- **Suggestion**: Extract a shared helper or fixture for the setup (empire, session, planet, DesignLibrary mock), then override only the DesignLoadResult per test.
- **LOC affected**: ~150

### tests/unit/ui/test_save_selection.py (~466 LOC)

#### CAT-5: Repeated autouse setup_tmpdir fixtures  [MAJOR]
- **Location**: test_save_selection.py:47-55, 148-156, 217-225
- **Issue**: Three test classes (`TestSaveSelectionTurnList`, `TestSaveSelectionListSaves`, `TestSaveSelectionEmpireInfo`) each define the exact same `autouse setup_tmpdir` fixture that creates a tempdir, patches `SAVES_DIR`, yields, and removes.
- **Suggestion**: Move to a conftest.py in the same directory or make the first occurrence a class-scoped fixture.
- **LOC affected**: ~30

#### CAT-6: test_buttons_enable_after_selection — internal implementation coupling  [MAJOR]
- **Location**: test_save_selection.py:274-327
- **Issue**: Test requires full `pygame.init()`, `pygame_gui.UIManager`, and display setup. It mutates a dict element from `window.saves_listbox.item_list` by setting `first_item["selected"] = True`, then calls `window._handle_selection_change()` — this is tightly coupled to pygame_gui's internal dict representation.
- **Suggestion**: Test at the view model or controller level instead of through the UI widget tree.
- **LOC affected**: 55

#### CAT-7: time.sleep in test  [MAJOR]
- **Location**: test_save_selection.py:204
- **Issue**: `time.sleep(0.1)` to ensure different timestamps between saves. Arbitrary sleep makes tests slow and flaky.
- **Suggestion**: Mock `time.time()` or patch the timestamp source to return deterministic values.
- **LOC affected**: 1

### tests/unit/core/test_protocols.py (~547 LOC)

#### CAT-9: Repeated imports in every test method  [MINOR]
- **Location**: test_protocols.py:14-220
- **Issue**: Every test body imports the same classes locally (`from game.core.protocols import IFleet`, `from game.strategy.data.fleet import Fleet`, etc.) rather than using module-level imports.
- **Suggestion**: Move all imports to module level.
- **LOC affected**: ~40 duplicate import lines

#### CAT-10: TypeGuard test cluster — parameterize opportunity  [MINOR]
- **Location**: test_protocols.py:101-220
- **Issue**: `TestTypeGuardFunctions` has 10 tests with identical structure: import typeguard, create real object, assert True; then create non-object, assert False. Each could be `@pytest.mark.parametrize` with (typeguard_fn, real_class, false_test_objects).
- **Suggestion**: Parametrize the typeguard test cluster.
- **LOC affected**: ~120 → ~30

### tests/unit/core/resources_registry/test_loading.py (~311 LOC)

#### CAT-10: Edge case test cluster — parameterize opportunity  [MINOR]
- **Location**: test_loading.py:159-239
- **Issue**: `TestEdgeCases` has 9 tests with identical pattern: write a JSON file with a specific edge case (empty array, missing key, null value, non-array, missing id, null id, empty id, duplicate ids, duplicate no-warning), load it, assert catalog state. All 9 could be a single `@pytest.mark.parametrize`.
- **Suggestion**: Parametrize the edge case tests.
- **LOC affected**: ~80 → ~25

### tests/unit/ui/utils/test_formatters.py (~159 LOC)

#### CAT-9: Repeated local imports  [MINOR]
- **Location**: test_formatters.py:9-57
- **Issue**: Every test in `TestFormatCompactNumber` repeats `from game.ui.utils.formatters import format_compact_number` at the top of the body instead of a single module-level import.
- **Suggestion**: Move the import to module level.
- **LOC affected**: ~12

### tests/unit/research/test_tech_node.py (~672 LOC)

#### CAT-10: Price curve test cluster — partial parameterize  [MINOR]
- **Location**: test_tech_node.py:315-373
- **Issue**: `TestTechNodePriceCurves` has 9 tests checking price curves (flat, linear, quadratic, exponential, logarithmic, sqrt, unknown, multiplier) — each is structurally identical (create node, call get_effective_price, assert). Already partially parameterized in `TestGetEffectivePriceParametrized` below, but the 9 tests above are non-parametrized duplicates of the parametrized versions.
- **Suggestion**: Remove the non-parametrized class; the parametrized version (`TestGetEffectivePriceParametrized`) already covers all the same curves with more level values. Consolidate into one parametrized class.
- **LOC affected**: ~60

### tests/unit/entities/test_ship.py (~510 LOC)

#### CAT-4: Derelict status logic duplicated with test_combat.py  [MAJOR]
- **Location**: test_ship.py:163-194 vs test_combat.py:98-122
- **Issue**: `test_derelict_status_logic` in test_ship.py and `test_derelict_functional_definition` in test_combat.py test the same production behavior (ship becomes derelict with no weapons/engines, adding a weapon removes derelict status, destroying the weapon makes it derelict again) with near-identical assertions.
- **Suggestion**: Keep one, remove the other. test_ship.py is the more appropriate location since it tests entity behavior directly.
- **LOC affected**: ~30 (in test_combat.py:95-122)

### tests/unit/modifiers/test_seeker_weapon_bindings.py (~193 LOC)

#### CAT-4: Duplicate recalculate tests with test_weapons_isolation.py  [MAJOR]
- **Location**: test_seeker_weapon_bindings.py:100-193 vs test_weapons_isolation.py:1011-1026
- **Issue**: Both files test `SeekerWeaponAbility.recalculate()` applying seeker-specific stat modifiers (endurance_mult, projectile_damage_mult, projectile_hp_mult, projectile_stealth_level). The tests in test_weapons_isolation.py at line 1011 already cover the same modifiers. test_seeker_weapon_bindings.py re-tests them with mock components instead.
- **Suggestion**: Consolidate into one file; `test_weapons_isolation.py` already has the more comprehensive test (uses MagicMock with stats dict), so prefer removing / merging the seeker_weapon_bindings recalculate tests.
- **LOC affected**: ~90 (in test_seeker_weapon_bindings.py:100-193)

### tests/unit/simulation/test_battle_runner_di.py (~271 LOC)

#### CAT-4: Duplicate helpers with test_battle_runner.py  [MAJOR]
- **Location**: test_battle_runner_di.py:52-100 (helpers) vs test_battle_runner.py:46-105
- **Issue**: `_make_ship_spec`, `_make_team`, `_minimal_spec`, and `ship_builder` fixture are all near-exact copies from `test_battle_runner.py`. These are infrastructure helpers, not SUT differences.
- **Suggestion**: Extract shared helpers into a conftest.py or shared fixture file under `tests/unit/simulation/`.
- **LOC affected**: ~55

#### CAT-8: AST-walk test for global lookup check  [MINOR]
- **Location**: test_battle_runner_di.py:218-271
- **Issue**: `test_no_simulation_call_to_get_default_registry_provider` parses the entire `game/simulation/` source tree with `ast.parse()` to verify no reference to a specific symbol exists. Massive 54-line setup for a single boolean assertion. Overly complex — a simple `grep` or `rg` check in CI would be more maintainable.
- **Suggestion**: Replace AST walk with a bash-based `rg` check in CI, or reduce to checking just the known vulnerable modules.
- **LOC affected**: 54

### tests/unit/research/research_controls/test_reset_state.py (~269 LOC)

#### CAT-6: Complex mock panel wiring  [MAJOR]
- **Location**: test_reset_state.py:17-31, 76-188
- **Issue**: `_create_mock_panel` creates a MagicMock panel then binds the real `ResearchControlPanel.reset` method onto it via `lambda`. Tests then assert on order of internal method calls (`clear_selection`, `update_budget_display`, etc.) — this is testing internal implementation sequence, not behavioral contract. Refactoring the reset method's implementation would break these tests.
- **Suggestion**: Test the observable post-reset state (what `_selected_node`, `tracker`, `slider_budget` values are), not the internal call sequence.
- **LOC affected**: ~100

### tests/unit/entities/test_ship_stat_querier.py (~752 LOC)

#### CAT-3: Dead TestShipStatQuerierCachedSummary class  [CRITICAL] (downgraded to MAJOR — small blast radius)
- **Location**: test_ship_stat_querier.py:252-257
- **Issue**: `TestShipStatQuerierCachedSummary` class contains only a comment noting that tests were removed (DUP-SIM-007) with no actual test methods. The empty class is dead test scaffolding.
- **Suggestion**: Remove the empty class.
- **LOC affected**: 6

### tests/unit/simulation/test_projectile_manager.py (~1628 LOC)

#### CAT-9: Repeated MagicMock projectile construction  [MINOR]
- **Location**: test_projectile_manager.py:1511-1520, 1831-1840, 1997-2007 (and ~20+ other locations)
- **Issue**: Throughout the file, mock projectiles are constructed with the same 10+ attribute assignments on MagicMock (`proj.position = Vector2(...)`, `proj.velocity = Vector2(...)`, `proj.is_alive = True`, `proj.team_id = 0`, `proj.type = AttackType.PROJECTILE`, etc.). A helper function `_make_mock_proj(x, y, vx, vy, **kwargs)` would eliminate 100+ lines of repeated boilerplate.
- **Suggestion**: Extract a `_make_mock_proj(x, y, vx, vy, team=0, damage=20, **kwargs)` helper.
- **LOC affected**: ~200 could be eliminated

### tests/unit/strategy/pathfinding/test_edge_cases.py (~170 LOC)

#### CAT-12: test_all_path_steps_are_adjacent — logic-heavy  [MINOR]
- **Location**: test_edge_cases.py:148-157
- **Issue**: Contains `for i in range(len(path) - 1)` with `hex_distance()` computation inside the loop. The expected assertion is that each consecutive pair is adjacent, but the test computes the expected value at runtime.
- **Suggestion**: Acceptable for a property-based test of path adjacency, but noted.

### tests/unit/strategy/engine/test_engine_validation.py (~312 LOC)

#### CAT-10: Engine validation test cluster  [MINOR]
- **Location**: test_engine_validation.py:39-312
- **Issue**: 15+ test classes with identical structure (`test_valid_empires_pass`, `test_colony_none_raises`/`test_fleet_none_*_raises`). Each class creates a specific engine and tests the same two scenarios. Could be parametrized across engine classes.
- **Suggestion**: Parametrize with `@pytest.mark.parametrize("engine_cls,kwargs,invalid_field_path", [...])` to reduce 15 classes to one parametrized test.
- **LOC affected**: ~250 → ~50

### tests/integration/strategy/test_commands.py (~287 LOC)

#### CAT-3: test_handle_command — empty test  [CRITICAL] (downgraded to MAJOR — small blast radius)
- **Location**: test_commands.py:191-198
- **Issue**: `test_handle_command` in `TestGameSessionCommands` contains only `pass` with a comment about mock complexity. This is a placeholder with zero assertions.
- **Suggestion**: Either implement or remove.
- **LOC affected**: 8

### tests/unit/simulation/test_battle_runner.py (~490 LOC)

#### CAT-10: Battle runner smoke tests — parameterize opportunity  [MINOR]
- **Location**: test_battle_runner.py:254-390
- **Issue**: `test_run_battle_returns_battle_outcome`, `test_run_battle_hits_tick_limit`, `test_run_battle_team_ids_preserved_in_order`, `test_run_battle_every_ship_spec_has_matching_ship_outcome`, `test_run_battle_seed_is_echoed` — each creates a BattleSpec with nearly identical structure (minimal 2-team spec, TickLimitCondition), differing only in what they assert. All 5 call `run_battle` with the same boilerplate.
- **Suggestion**: Extract a helper `_run_minimal_battle(ticks, seed)` returning `(spec, outcome)`, then assert specific properties.
- **LOC affected**: ~120 → ~40

### tests/unit/combat/test_combat.py (~342 LOC)

#### CAT-12: test_firing_solution_lead — complex computation  [MINOR]
- **Location**: test_combat.py:213-235
- **Issue**: Test contains its own physics/lead calculation logic (`expected collision: P = Vp * t = 20t, T = P0 + Vt * t = 100 + 10t...`) with expected result derived from the same math the SUT uses. The expected value `10.0` is computed from the algorithm, not independently verified.
- **Suggestion**: Use hardcoded expected values from independent sources or a fixture with known-good I/O pairs.
- **LOC affected**: 23

### tests/unit/systems/test_physics.py (~315 LOC)

#### CAT-12: test_mass_dampening — logic-heavy  [MINOR]
- **Location**: test_physics.py:261-281
- **Issue**: Test runs the ship thrust + update cycle twice with different mass values, compares speeds, and asserts `fast_speed > slow_speed`. The test asserts a property (higher mass = lower speed) rather than a specific numeric value, which is a reasonable approach, but the form of calling thrust_forward/update_physics_movement twice and comparing is logic-heavy.
- **Suggestion**: This is a valid approach for testing mass-dampening direction. Fine as-is but noted.

### tests/unit/ui/screens/builder/test_modifier_logic_smart_floor.py (~44 LOC)

#### CAT-9: CAT-1 adjacent — test_snap_down_by_1_from_1_stays_at_min  [MINOR]
- **Location**: test_modifier_logic_smart_floor.py:37-44
- **Issue**: `assert result >= 0.1` — the assertion only checks a lower bound, not an exact value. The test comment says "should clamp at 0.1" but the assertion only checks `>=`. This is not a regression guard.
- **Suggestion**: Assert `result == pytest.approx(0.1, abs=0.01)` to match the test's description.
- **LOC affected**: 5

### tests/unit/strategy/fleet/test_space_yard.py (~328 LOC)

#### CAT-4: Duplicate make_ship_with_yard fixture  [MAJOR] (downgraded — small blast radius)
- **Location**: test_space_yard.py:91-123 vs 195-226
- **Issue**: `make_ship_with_yard` factory fixture is defined identically in both `TestFleetHasSpaceShipyard` and `TestFleetCanBuildType` classes (same logic, same imports). The second definition at line 195 could reuse the first.
- **Suggestion**: Move to a module-level fixture.
- **LOC affected**: ~35

### tests/unit/ui/test_new_game_setup.py (~425 LOC)

#### CAT-11: test_build_game_config_signature_default_matches_dataclass — fragile  [MINOR]
- **Location**: test_new_game_setup.py:103-117
- **Issue**: Uses `inspect.signature()` and `inspect.getsource()` to verify a function parameter's default matches a constant. This is a fragile assertion on function signature rather than behavior. If someone reorganizes the parameter list or uses a different default mechanism, this test breaks even though behavior is unchanged.
- **Suggestion**: Test observable behavior (what config object is produced) rather than implementation detail (signature metadata).
- **LOC affected**: 16

#### CAT-12: test_curve_low_end_fine_grained — logic-heavy  [MINOR]
- **Location**: test_new_game_setup.py:146-157
- **Issue**: Contains `for t in range(0, 100)` with `max()` computation. The test iterates to verify property of a curve function.
- **Suggestion**: This is a legitimate property-based test of a curve. Acceptable but noted.

### tests/unit/modifiers/test_seeker_weapon_bindings.py (~193 LOC)

#### CAT-6: Recalculate tests with MockComponent classes defined inline  [MAJOR]
- **Location**: test_seeker_weapon_bindings.py:103-193
- **Issue**: Four test methods each define a `class MockComponent` inline with `__init__`, `self.stats = {...}`, `self.ability_stats = {}`, `self.data = {}`. This is a local reimplementation of what MagicMock with attribute settings could achieve in one line.
- **Suggestion**: Use `MagicMock(stats={...}, ability_stats={}, data={})` instead of defining a class per test.
- **LOC affected**: ~60

## File Coverage Verification
| File | Status | Findings |
|------|--------|----------|
| tests/repro_issues/repro_facade_colonies.py | Read ✓ | 1 |
| tests/unit/abilities/test_warp_jump.py | Read ✓ | 0 |
| tests/unit/ai/test_group_target_coordinator.py | Read ✓ | 0 |
| tests/unit/builder/test_builder_interaction.py | Read ✓ | 0 |
| tests/unit/builder/test_schematic_cache_key.py | Read ✓ | 0 |
| tests/unit/combat/test_combat.py | Read ✓ | 2 |
| tests/unit/core/resources_registry/test_loading.py | Read ✓ | 1 |
| tests/unit/core/test_component_state.py | Read ✓ | 0 |
| tests/unit/core/test_hex_math_strategy.py | Read ✓ | 0 |
| tests/unit/core/test_protocols.py | Read ✓ | 2 |
| tests/unit/entities/test_ship.py | Read ✓ | 1 |
| tests/unit/entities/test_ship_stat_querier.py | Read ✓ | 1 |
| tests/unit/fixtures/test_ship_fixtures.py | Read ✓ | 0 |
| tests/unit/modifiers/test_seeker_weapon_bindings.py | Read ✓ | 2 |
| tests/unit/research/research_controls/test_reset_state.py | Read ✓ | 1 |
| tests/unit/research/test_tech_node.py | Read ✓ | 1 |
| tests/unit/simulation/combat/test_ship_death_at_zero_hp.py | Read ✓ | 0 |
| tests/unit/simulation/components/abilities/test_planetary_fleet_components.py | Read ✓ | 0 |
| tests/unit/simulation/components/abilities/test_weapons_isolation.py | Read ✓ | 1 |
| tests/unit/simulation/components/test_create_ability_formula_skip.py | Read ✓ | 0 |
| tests/unit/simulation/components/test_modifier_effects.py | Read ✓ | 1 |
| tests/unit/simulation/components/test_space_shipyard_consolidation.py | Read ✓ | 0 |
| tests/unit/simulation/systems/test_battle_engine_tick.py | Read ✓ | 0 |
| tests/unit/simulation/test_battle_runner.py | Read ✓ | 1 |
| tests/unit/simulation/test_battle_runner_di.py | Read ✓ | 2 |
| tests/unit/simulation/test_projectile_manager.py | Read ✓ | 1 |
| tests/unit/strategy/adapters/test_simulation_adapter.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_galaxy_entity_registry.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_engine_validation.py | Read ✓ | 1 |
| tests/unit/strategy/engine/test_multi_pod_colonization.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_planet_modifier_effect_engine.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_set_build_queue_paused_command.py | Read ✓ | 0 |
| tests/unit/strategy/events/test_event_log.py | Read ✓ | 0 |
| tests/unit/strategy/fleet/test_space_yard.py | Read ✓ | 1 |
| tests/unit/strategy/fleets/test_ship_instance_roundtrip.py | Read ✓ | 0 |
| tests/unit/strategy/generation/density/test_geometric.py | Read ✓ | 0 |
| tests/unit/strategy/pathfinding/test_edge_cases.py | Read ✓ | 1 |
| tests/unit/strategy/pathfinding/test_intercept_edge_cases.py | Read ✓ | 1 |
| tests/unit/strategy/production_engine/test_spawning.py | Read ✓ | 0 |
| tests/unit/strategy/ship_instance/test_ship_instance_serializer.py | Read ✓ | 0 |
| tests/unit/strategy/test_quickstart_builder.py | Read ✓ | 1 |
| tests/unit/systems/test_arcade_movement.py | Read ✓ | 0 |
| tests/unit/systems/test_physics.py | Read ✓ | 1 |
| tests/unit/test_lab/test_panel_manager.py | Read ✓ | 0 |
| tests/unit/tools/test_agent_skill_prefix_renamer.py | Read ✓ | 0 |
| tests/unit/ui/filters/test_filter_state.py | Read ✓ | 0 |
| tests/unit/ui/panels/test_planet_report_panel.py | Read ✓ | 1 |
| tests/unit/ui/screens/battle_setup/test_controller.py | Read ✓ | 0 |
| tests/unit/ui/screens/builder/test_modifier_logic_smart_floor.py | Read ✓ | 1 |
| tests/unit/ui/screens/test_build_queue_queue_data_source.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_empire_build_queue_filter_manager.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_event_log_sidebar.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_transfer_dialog_enhanced.py | Read ✓ | 0 |
| tests/unit/ui/services/image/test_null_provider.py | Read ✓ | 0 |
| tests/unit/ui/services/test_component_service.py | Read ✓ | 0 |
| tests/unit/ui/test_battle_results_data.py | Read ✓ | 0 |
| tests/unit/ui/test_fleet_list_view_model.py | Read ✓ | 0 |
| tests/unit/ui/test_fonts.py | Read ✓ | 1 |
| tests/unit/ui/test_lab_formatting_utils.py | Read ✓ | 0 |
| tests/unit/ui/test_new_game_setup.py | Read ✓ | 2 |
| tests/unit/ui/test_race_asset_loader.py | Read ✓ | 1 |
| tests/unit/ui/test_race_theme_gallery.py | Read ✓ | 1 |
| tests/unit/ui/test_save_selection.py | Read ✓ | 3 |
| tests/unit/ui/test_theme_discovery.py | Read ✓ | 0 |
| tests/unit/ui/utils/test_formatters.py | Read ✓ | 1 |
| tests/integration/colonization/test_edge_cases.py | Read ✓ | 0 |
| tests/integration/replay/test_capture_pipeline.py | Read ✓ | 0 |
| tests/integration/strategy/facade/test_validation_queries.py | Read ✓ | 0 |
| tests/integration/strategy/test_commands.py | Read ✓ | 1 |
| tests/integration/strategy/test_economy_e2e.py | Read ✓ | 0 |
| tests/integration/strategy/test_production_rates.py | Read ✓ | 1 |
| tests/integration/ui/test_editor_click_blocking.py | Read ✓ | 0 |
| tests/integration/ui/test_move_order_registration.py | Read ✓ | 0 |
| tests/integration/ui/test_stats_render.py | Read ✓ | 0 |

## Context Usage Estimate
- Total LOC read (test files + production code): ~32,000 LOC from test files; minimal production code reads beyond imports.
- Approximate headroom: High (>500K remaining)
