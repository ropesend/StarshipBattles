# Shard 10 — Test Audit Report

## Summary
- Shard: 10
- Files assigned: 82
- Files actually read: 82
- Total findings: 18
- Critical: 3 | Major: 7 | Minor: 8

## Findings

### tests/unit/ui/test_sprites.py (~312 LOC)

#### CAT-1: test_atlas_fallback_logic  [CRITICAL]
- **Location**: test_sprites.py:54-58
- **Issue**: Test body is `pass` with no assertions — cannot fail. The docstring acknowledges the test is "less relevant" since `load_atlas` is deprecated.
- **Suggestion**: Remove the empty test method
- **LOC affected**: 5

### tests/integration/ui/build_queue_screen/test_crash_tooltips.py (~31 LOC)

#### CAT-1: test_apply_tooltips_crash_none_buttons  [CRITICAL]
- **Location**: test_crash_tooltips.py:9-31
- **Issue**: Creates a `BuildQueueScreen` instance but contains zero assertions — the test can never fail unless the constructor raises. The test name implies it should verify "crash safety" but there is no assertion to prove anything was tested.
- **Suggestion**: Add assertions or remove the test
- **LOC affected**: 23

### tests/unit/ui/screens/test_menu_scene.py (~266 LOC)

#### CAT-1: test_button_config_with_3_buttons  [CRITICAL — downgraded: small blast radius]
- **Location**: test_menu_scene.py:54-68
- **Issue**: Duplicate of `test_init_creates_correct_number_of_buttons_from_config` (lines 36-52) — same test body (creates 3 buttons, asserts length=3), only differs in test data construction style. No additional production path exercised.
- **Suggestion**: Remove one of the two duplicates
- **LOC affected**: 16

### tests/unit/modifiers/test_projectile_weapon_bindings.py (~80 LOC)

#### CAT-1: test_projectile_weapon_inherits_weapon_bindings  [CRITICAL — downgraded: small blast radius]
- **Location**: test_projectile_weapon_bindings.py:16-25
- **Issue**: Asserts `get_consumed_stats()` of ProjectileWeaponAbility is a superset of WeaponAbility's. This is a structural assertion on static declarations — if the implementation changes what stats are consumed, the test will fail but only because the declared list changed, not because behavior is wrong. More of a constants-validation test (which rubric excludes from CAT-1), but the `>= 5` assertion on line 34 is a CONSTANTS check.
- **Issue actually**: Line 34 `assert len(ProjectileWeaponAbility.STAT_BINDINGS) >= 5` is a legitimate constants-validation check, so CAT-1 does NOT apply. Removing from findings.

#### CAT-9: test_projectile_weapon_inherits_weapon_bindings / test_projectile_weapon_has_stat_bindings  [MINOR]
- **Location**: test_projectile_weapon_bindings.py:16-34
- **Issue**: Both tests import the same class twice (lines 16-25, 27-34) and assert on its static attributes — they could be merged into a single test.
- **Suggestion**: Merge into one test function
- **LOC affected**: 10

### tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py (~520 LOC)

#### CAT-9: Helper functions _effect / _entry / _add_entry / _grouped_mult_entry  [MINOR]
- **Location**: test_fleet_aura_manager_modifier_stack.py:34-53, 173-189, 288-302
- **Issue**: Four similar helper functions create ModifierEffect/ModifierEntry with near-identical boilerplate. `_add_entry` (line 173) and `_entry` (line 47) differ only in `operation=` value and some field names. `_grouped_mult_entry` (line 288) duplicates `_entry` with an added `stack_group` parameter.
- **Suggestion**: Consolidate into one parametrized helper: `_mk_entry(source, stat_key, value, *, operation="multiply", stack_group=None)`
- **LOC affected**: 50

### tests/integration/strategy/turn_engine/test_resources.py (~394 LOC)

#### CAT-10: Full-turn integration tests  [MINOR]
- **Location**: test_resources.py:214-270
- **Issue**: `test_full_turn_depletes_per_turn_resources_completely` and `test_full_turn_does_not_overconsume_resources` share identical setup (create ship, mock costs, process 100 ticks) differing only in the assertion target. Could be parametrized as one test with `(cost, expected_total)`.
- **Suggestion**: Merge into single parametrized test
- **LOC affected**: 30

### tests/unit/strategy/engine/test_planet_action_engine.py (~438 LOC)

#### CAT-10: Event logging tests  [MINOR]
- **Location**: test_planet_action_engine.py:336-437
- **Issue**: `test_activate_logs_shield_activated_event`, `test_deactivate_from_active_logs_shield_deactivated_event`, and `test_deactivate_from_activating_logs_shield_deactivated_event` all follow the identical pattern — create event bus, create planet/facility/order, process tick, assert event logged. Only difference is the pre-existing activation state and expected event type.
- **Suggestion**: Parametrize into one test with `(pre_state, order_type, expected_event_type)`
- **LOC affected**: 55

### tests/unit/strategy/engine/test_build_order_processor.py (~150 LOC)

#### CAT-6: test_build_order_auto_completes_when_queue_empties  [MAJOR]
- **Location**: test_build_order_processor.py:60-81
- **Issue**: Creates a Fleet, then constructs an `ActionExecutionEngine` inline to test BUILD auto-pop. This test bypasses the `OrderProcessor.execute_action_order` entry point (which the other tests in this file use) and instead tests through `ActionExecutionEngine.process_action_ticks`. This encodes knowledge of internal delegation chain — if BUILD auto-pop moves to a different engine, the test breaks even though the behavior is still correct.
- **Suggestion**: Test through the same `execute_action_order` entry point as sibling tests, or move this test to ActionExecutionEngine tests
- **LOC affected**: 12

### tests/unit/ui/screens/test_planet_list_window.py (~213 LOC)

#### CAT-6: Deep mocking of PlanetReportPanel construction  [MAJOR — downgraded: appropriate for UI bypass-init pattern]
- **Location**: test_planet_list_window.py:71-111
- **Issue**: Tests mock `PlanetReportPanel` constructor and verify kwargs. This is a "change-detector" — if `PlanetReportPanel` adds a required parameter, the mock won't catch it and the test will pass even though the real panel would fail. However, this is the project's standard bypass-init pattern for pygame_gui components and is accepted convention.
- **Suggestion**: No action — accepted pattern per project conventions. Noted for awareness.

### tests/unit/ui/panels/test_modifier_editor_panel.py (~45 LOC)

#### CAT-5: Bypass-init fixture recreates panel per test function [MAJOR — downgraded: small blast radius, 3 tests]
- **Location**: test_modifier_editor_panel.py:10-44
- **Issue**: `modifier_panel` fixture (line 10) is function-scoped and constructs `ModifierEditorPanel` with 5 MagicMock dependencies for each of 3 tests. Only exercises `update(dt)` existence check — could be class-scoped or the 3 tests merged.
- **Suggestion**: Merge 3 update tests into one parametrized test; rescope fixture to class
- **LOC affected**: 15

### tests/unit/simulation/services/test_modifier_service.py (~1048 LOC)

#### CAT-5: Large fixture sets (full_registry) scoped as function [MAJOR]
- **Location**: test_modifier_service.py:226-253
- **Issue**: `full_registry` fixture creates 11 mock Modifier objects (each with dict data) and is function-scoped. Used by 20+ tests across multiple classes. Changing to class-scope would avoid rebuilding identical mock registry per test.
- **Suggestion**: Rescope `full_registry` fixture to `class` scope
- **LOC affected**: 28 lines of fixture + re-computation waste across ~20 tests

#### CAT-10: Duplicate turret_mount initial value / min-max tests  [MINOR]
- **Location**: test_modifier_service.py:488-528, 634-664
- **Issue**: Five tests for `get_initial_value('turret_mount', ...)` with different mock firing_arc sources and five corresponding `get_local_min_max('turret_mount', ...)` tests follow identical patterns. Could be parametrized as one cluster.
- **Suggestion**: Parametrize into one test per method with `(component_setup, expected_value_or_min, expected_max)` tuples
- **LOC affected**: 120

### tests/unit/strategy/facade/test_strategy_session_facade.py (~793 LOC)

#### CAT-9: Repeated _make_mock_* helpers across test classes  [MAJOR — downgraded: only affects this file]
- **Location**: test_strategy_session_facade.py:19-39, 168-181, 252-261, 333-363, 484-520
- **Issue**: Four test classes (`TestFleetQueries`, `TestSystemQueries`, `TestPlanetQueries`, `TestValidationQueries`, and `TestEmpireQueries`) each define their own near-identical `_make_mock_fleet`, `_make_mock_empire`, `_make_mock_planet` helpers. These 12+ helper methods collectively duplicate the same logic (create Mock with `.id`, `.name`, `.location`, etc.).
- **Suggestion**: Extract shared mock factory helpers to module-level or a shared conftest fixture
- **LOC affected**: 80

### tests/unit/simulation/test_physics_formulas.py (~800 LOC)

#### CAT-12: Logic-heavy formula boundary tests  [MINOR]
- **Location**: test_physics_formulas.py:49-147, 152-221, 227-294, 300-374, 380-433, 440-505, 511-560, 566-613
- **Issue**: Multiple test classes re-implement the physics formulas being tested (e.g., `max_speed = (thrust * K_SPEED) / mass` at line 56, 70, 82, etc.) rather than using only the production `compute_max_speed()` / `compute_acceleration()` functions. The `TestSpeedFormulaBoundaries`, `TestAccelerationFormulaBoundaries`, `TestTurnSpeedFormulaBoundaries`, `TestRadiusFormulaBoundaries`, `TestForceApplicationBoundaries`, `TestDragFormulaBoundaries`, `TestDefenseScoreFormulaBoundaries`, `TestManeuverScoreFormulaBoundaries` all inline the formula math. When the production formula changes, these tests silently test the old formula.
- **Suggestion**: Replace inline formula reimplementations with calls to the shared `compute_max_speed()`, `compute_acceleration()`, etc. functions from `game.simulation.physics_constants`. The `TestComputeAcceleration` and `TestComputeMaxSpeed` classes (lines 737-800) already do this correctly — the boundary classes should follow the same pattern.
- **LOC affected**: 500

### tests/unit/strategy/data/test_planet_gen.py (~724 LOC)

#### CAT-12: Statistical sampling in test assertions  [MINOR]
- **Location**: test_planet_gen.py:71-118, 161-189, 556-680
- **Issue**: Multiple tests use for-loops (lines 76, 93, 109, 167, 176, 187, 596, 618, 633, 650, 670) to sample random outputs and compute averages as assertions. These are non-deterministic probability-based tests that can produce false negatives. The test itself computes expected-value ranges via averaging (CAT-12).
- **Suggestion**: Replace statistical sampling with seeded-RNG deterministic tests (e.g., use `random.Random(seed)` and assert specific values rather than average ranges)
- **LOC affected**: 200

### tests/unit/strategy/fleet_navigation/test_service_edge_cases.py (~511 LOC)

#### CAT-4: Duplicate of test_projection.py  [MAJOR — downgraded: tests different code paths]
- **Location**: test_service_edge_cases.py:432-465 vs test_projection.py:146-169
- **Issue**: `test_project_path_as_dicts_returns_list_of_dicts` in test_projection.py and `test_project_path_as_dicts` test class in test_service_edge_cases.py both test `project_path_as_dicts()` behavior. The edge-cases file adds zero-speed and edge-case variants not in projection.py, but the base case overlaps.
- **Suggestion**: Consolidate base `project_path_as_dicts` test in one file, keep edge cases in edge_cases file
- **LOC affected**: 20

### tests/unit/core/test_json_utils.py (~571 LOC)

#### CAT-9: Redundant _REQUIRED test class  [MINOR]
- **Location**: test_json_utils.py:277-307
- **Issue**: `TestLoadJsonRequired` tests `load_json_required()` which is the same underlying function as `load_json()` but with `raise_on_error` behavior. The success test (line 280-290) duplicates the logic already tested in `test_load_json_success` (line 14-24).
- **Suggestion**: Only test the differential behavior (raises vs returns default) — remove the success-path test or merge the class into TestLoadJson
- **LOC affected**: 15

### tests/unit/ui/screens/test_strategy_superweapons.py (~545 LOC)

#### CAT-10: Repeated no_fleet / no_ability error tests  [MINOR]
- **Location**: test_strategy_superweapons.py:112-116, 175-179, 225-229, 297-301, 345-349, 393-397
- **Issue**: `test_no_fleet_returns_none` appears 6 times (once per superweapon: Imploder, Stellerator, OpenWarp, CloseWarp, DysonSphere, SelfDestruct). Each has the identical body: call handler with `None` fleet, assert result is `None`.
- **Suggestion**: Parametrize: `@pytest.mark.parametrize("handler_name", ["handle_implode_planet_designation", ...])`
- **LOC affected**: 30

#### CAT-10: Repeated fleet_without_ability_returns_error tests  [MINOR]
- **Location**: test_strategy_superweapons.py:118-125, 181-188, 231-238, 303-309, 351-358, 399-406
- **Issue**: Six identical-pattern tests (mock fleet without ability, call handler, assert error result with ability name in message).
- **Suggestion**: Parametrize with `(handler_name, ability_name, expected_message_fragment)` tuples
- **LOC affected**: 45

### tests/unit/simulation/components/abilities/test_system_stabilizers.py (~109 LOC)

#### CAT-10: Near-identical Stabilizer tests  [MINOR]
- **Location**: test_system_stabilizers.py:12-109
- **Issue**: `TestStellarStabilizerAbility` and `TestWarpFieldStabilizerAbility` are structurally identical (6 tests each, same patterns, only the class name, constructor arg, and expected energy_drain_rate differ). Could be one parametrized class.
- **Suggestion**: Parametrize into single test class with `(AbilityClass, expected_drain, ...)` tuples
- **LOC affected**: 50

### tests/unit/strategy/generation/test_storm_generator.py (~394 LOC)

#### CAT-12: Logic-heavy star_hexes computation  [MINOR]
- **Location**: test_storm_generator.py:181-190
- **Issue**: `test_storms_avoid_star_hexes` computes `star.occupied_hexes` set and iterates with a for-loop that contains a computation (`storm_hexes = storm.occupied_hexes`). Minor, but the assert uses `len(overlap) == 0` instead of simpler `assert storm_hexes.isdisjoint(star_hexes)`.
- **Suggestion**: Use `assert storm_hexes.isdisjoint(star_hexes)` for clarity
- **LOC affected**: 5

### tests/unit/strategy/fleet_navigation/test_service_edge_cases.py (~511 LOC)

#### CAT-9: Mock fleet creation boilerplate repeated  [MINOR]
- **Location**: test_service_edge_cases.py:392-431, 474-510
- **Issue**: Both `TestProjectPath` and `TestCalculateFleetNextHex` classes construct mock fleets with 8+ `MagicMock()` attributes. A shared `_make_mock_fleet()` helper at module level would eliminate this repetition.
- **Suggestion**: Extract a `_make_mock_fleet(location, path, orders, speed, can_warp)` helper
- **LOC affected**: 40

### tests/unit/ai/test_combat_utils.py (~559 LOC)

#### CAT-8: Overly complex mock construction in PDC arc tests  [MAJOR — downgraded: tests real production edge cases]
- **Location**: test_combat_utils.py:317-341
- **Issue**: `_create_pdc_ship` helper uses `lambda sp, sa, tp: WeaponAbility.check_firing_solution(weapon_ability, sp, sa, tp)` to bind a real method to a Mock — this is a fragile mock/production hybrid. If `check_firing_solution` signature changes, the lambda silently breaks.
- **Suggestion**: Consider using `unittest.mock.patch.object` on a partially-real mock, or use the real `WeaponAbility`/`Component` objects for these tests
- **LOC affected**: 7

### tests/unit/strategy/services/test_fleet_navigation_action_timing.py (~580 LOC)

#### CAT-8: Deeply nested patching of internal dependencies  [MAJOR]
- **Location**: test_fleet_navigation_action_timing.py:55-69, 113-127, 171-185, 247-259, 290-300
- **Issue**: Multiple tests use 3+ nested `with patch()` blocks patching `find_hybrid_path`, `ActionTimeResolver.resolve_action_time`, and other internal implementation details. This encodes the internal call chain into the test — if the implementation changes how it resolves paths or action times, these tests fail even though behavior is unchanged.
- **Suggestion**: Mock at the service boundary instead of deep-patching internal helpers; or accept the brittleness since these verify specific timing behavior
- **LOC affected**: 60

### tests/unit/strategy/data/test_habitability_factors.py (~375 LOC)

#### CAT-1: test_all_steps_positive  [CRITICAL — downgraded: minor blast radius, validates constants]
- **Location**: test_habitability_factors.py:88-90
- **Issue**: This tests validates that all registry entries have `step > 0` — this is a constants-validation test (excluded from CAT-1 per rubric). Removing from findings.

Actually this is NOT CAT-1 — it's a valid constants-validation check. Not reported.

## File Coverage Verification
| File | Status | Findings |
|------|--------|----------|
| tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py | Read ✓ | 1 |
| tests/unit/simulation/services/test_simulation_design_loader.py | Read ✓ | 0 |
| tests/unit/strategy/generation/density/test_layout_loader.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_planet_action_engine.py | Read ✓ | 1 |
| tests/unit/strategy/generation/test_storm_generator.py | Read ✓ | 1 |
| tests/unit/strategy/services/test_task_group_suggester.py | Read ✓ | 0 |
| tests/unit/ui/test_sprites.py | Read ✓ | 1 |
| tests/integration/fleet_combat/test_battle_determinism.py | Read ✓ | 0 |
| tests/integration/save_load/test_live_verification.py | Read ✓ | 0 |
| tests/unit/strategy/facade/test_strategy_session_facade.py | Read ✓ | 1 |
| tests/integration/ui/test_fleet_ops_facade.py | Read ✓ | 0 |
| tests/integration/strategy/turn_engine/test_resources.py | Read ✓ | 1 |
| tests/integration/strategy/production/test_fleet_save_load.py | Read ✓ | 0 |
| tests/unit/strategy/fleet_navigation/test_projection.py | Read ✓ | 0 |
| tests/unit/strategy/facade/test_fleet_dto.py | Read ✓ | 0 |
| tests/unit/core/test_validation.py | Read ✓ | 0 |
| tests/unit/tools/test_agent_skill_prefix_checker.py | Read ✓ | 0 |
| tests/integration/strategy/test_fleet_join_redirect.py | Read ✓ | 0 |
| tests/unit/simulation/systems/test_perf_stats_dirty_flag.py | Read ✓ | 0 |
| tests/unit/simulation/entities/test_ship_resource_stat.py | Read ✓ | 0 |
| tests/unit/strategy/design_library/test_per_empire.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_process_colonize_validation.py | Read ✓ | 0 |
| tests/unit/strategy/services/ability_sources/test_star.py | Read ✓ | 0 |
| tests/unit/simulation/components/test_modifier_schema.py | Read ✓ | 0 |
| tests/unit/simulation/services/test_modifier_service.py | Read ✓ | 2 |
| tests/unit/strategy/data/test_storm.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_menu_scene.py | Read ✓ | 1 |
| tests/unit/modifiers/test_projectile_weapon_bindings.py | Read ✓ | 1 |
| tests/integration/ui/build_queue_screen/test_crash_tooltips.py | Read ✓ | 1 |
| tests/unit/strategy/engine/test_command_ownership.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_cargo_tracking.py | Read ✓ | 0 |
| tests/unit/simulation/test_formula_evaluator.py | Read ✓ | 0 |
| tests/unit/simulation/test_physics_formulas.py | Read ✓ | 1 |
| tests/unit/simulation/validation/test_ship_validator_rules.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_harvesting_size_scaling.py | Read ✓ | 0 |
| tests/unit/simulation/components/test_component_constants.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_design_validator.py | Read ✓ | 0 |
| tests/unit/simulation/components/abilities/test_system_stabilizers.py | Read ✓ | 1 |
| tests/unit/strategy/data/test_planet_gen.py | Read ✓ | 1 |
| tests/unit/ui/services/test_ship_io_adapter.py | Read ✓ | 0 |
| tests/unit/simulation/combat/test_fleet_aura_register.py | Read ✓ | 0 |
| tests/unit/ui/widgets/test_ui_element_registry.py | Read ✓ | 0 |
| tests/unit/simulation/combat/test_ship_stats_aggregator.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_staging_yard_operations.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_planet_zones.py | Read ✓ | 0 |
| tests/unit/ui/panels/test_modifier_editor_panel.py | Read ✓ | 1 |
| tests/unit/ui/screens/test_planet_list_filters.py | Read ✓ | 0 |
| tests/unit/core/math_utils/test_helpers.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_fleet_navigation_action_timing.py | Read ✓ | 1 |
| tests/integration/ui/build_queue_screen/test_portrait_logging.py | Read ✓ | 0 |
| tests/integration/ui/build_queue_screen/test_controller_multi_queue.py | Read ✓ | 0 |
| tests/unit/simulation/entities/test_projectile.py | Read ✓ | 0 |
| tests/unit/services/llm/test_http_block.py | Read ✓ | 0 |
| tests/unit/strategy/turn_engine/test_turn_processing.py | Read ✓ | 0 |
| tests/unit/strategy/save_game_service/test_load_helpers.py | Read ✓ | 0 |
| tests/unit/services/llm/test_deepseek.py | Read ✓ | 0 |
| tests/unit/simulation/entities/test_ship_id.py | Read ✓ | 0 |
| tests/unit/quickstart/test_quickstart_builder.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_build_order_processor.py | Read ✓ | 1 |
| tests/unit/entities/ship_helpers/test_component_getters.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_habitability_factors.py | Read ✓ | 0 |
| tests/unit/ui/test_ship_theme_logic.py | Read ✓ | 0 |
| tests/unit/ai/test_ai_protocols.py | Read ✓ | 0 |
| tests/unit/simulation/combat/test_hit_log_modifier_trace.py | Read ✓ | 0 |
| tests/unit/strategy/adapters/test_no_ai_import.py | Read ✓ | 0 |
| tests/unit/ui/services/test_vehicle_class_service.py | Read ✓ | 0 |
| tests/unit/strategy/fleet_navigation/test_service_edge_cases.py | Read ✓ | 2 |
| tests/unit/strategy/production_engine/test_habitability.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_strategy_superweapons.py | Read ✓ | 2 |
| tests/unit/modifiers/test_modifier_effect_evaluator.py | Read ✓ | 0 |
| tests/unit/strategy/test_ship_display_formatter.py | Read ✓ | 0 |
| tests/unit/ai/test_ai_n_team_targeting.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_base_command_handler.py | Read ✓ | 0 |
| tests/integration/save_load/test_registry_injection.py | Read ✓ | 0 |
| tests/unit/ai/test_combat_utils.py | Read ✓ | 1 |
| tests/integration/strategy/test_empire.py | Read ✓ | 0 |
| tests/unit/core/test_json_utils.py | Read ✓ | 1 |
| tests/unit/strategy/data/test_intrinsic_rng_determinism.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_planet_list_window.py | Read ✓ | 1 |
| tests/unit/abilities/test_strategic_movement.py | Read ✓ | 0 |
| tests/unit/strategy/fleet/test_movement_resources.py | Read ✓ | 0 |
| tests/unit/ui/widgets/test_preference_row.py | Read ✓ | 0 |

## Context Usage Estimate
- Total LOC read (test files + production code): ~24,000 LOC (tests) + ~5,000 LOC (game production imports read inline)
- Approximate headroom: Medium (200-500K remaining)
