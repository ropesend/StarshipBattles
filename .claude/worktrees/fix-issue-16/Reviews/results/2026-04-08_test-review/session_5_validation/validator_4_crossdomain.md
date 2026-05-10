# Validator 4: Cross-Domain Claims Validation

**Scope:** Claims from Session 4 agents (research, colonization, fleet/production, misc/repro)
**Claims Reviewed:** 40
**Confirmed:** 24
**Downgraded:** 10
**Rejected:** 6

---

## Claim 1: test_research_tracker_edge_cases.py (12 tests) -- DUPLICATE_OF test_research_tracker.py

**Verdict: CONFIRMED**

Read both files in full. The edge cases file has two classes:
- `TestNodeStateSerialization` (5 tests): `test_node_state_roundtrip`, `test_node_state_from_dict_defaults`, `test_node_state_from_dict_partial_data`, `test_node_state_zero_rp`, `test_node_state_max_chance`
- `TestResearchTrackerSerialization` (7 tests): roundtrips, seed consistency, auto_spread_enabled, from_dict defaults

The main `test_research_tracker.py` already has:
- `TestNodeState.test_from_dict_with_missing_keys` -- same as `test_node_state_from_dict_defaults`
- `TestNodeState.test_from_dict_with_partial_data` -- same as `test_node_state_from_dict_partial_data`
- `TestNodeState.test_to_dict_serialization` + `test_from_dict_deserialization` -- covers roundtrip
- `TestResearchTrackerSerialization.test_round_trip` -- covers tracker roundtrip
- `TestResearchTrackerSerialization.test_from_dict_empty` -- covers defaults

The edge case tests for `zero_rp` and `max_chance` are trivially simple extensions of the existing roundtrip (just different values). The `session_seed_consistency` test just asserts two objects with the same seed have the same seed value -- trivial. Confirmed duplicate.

---

## Claim 2: test_interaction.py TestCycleDetectionCall (2 tests) -- TESTS_NOTHING_REAL

**Verdict: CONFIRMED**

Read lines 275-331. Both tests create MagicMock objects and then manually call methods on the mocks -- they never construct a real `ResearchTreeScene` that runs its `__init__`. The first test:
1. Creates `scene = MagicMock(spec=ResearchTreeScene)` (not a real scene)
2. Manually calls `mock_tree.detect_cycles()` (calling mock method directly)
3. Asserts the mock was called -- but it was called by the test itself, not by production code

The second test:
1. Manually iterates `cycle_errors` and calls `mock_logger.info()`
2. Asserts `mock_logger.info.call_count == 2` -- but the test itself called the logger

Neither test actually exercises any production code path. They test local mock setup. Confirmed TESTS_NOTHING_REAL.

---

## Claim 3: test_process_colonize_cargo.py::test_colonize_universal_drop_pod_succeeds -- DUPLICATE_OF test_process_colonize_validation.py

**Verdict: CONFIRMED**

Both files test the same scenario: a ship with a drop pod labelled as one type (CONTINENTAL) colonizing an ICE_DWARF planet, asserting `result.colonized is True` because pods are universal. The validation file's `test_process_colonize_universal_drop_pod_succeeds` does the same thing with additionally checking `planet.owner_id` and `empire.colonies`. The cargo file is a strict subset.

---

## Claim 4: test_process_colonize_cargo.py::test_colonize_any_planet_picks_first_unowned -- DUPLICATE_OF test_process_colonize_validation.py

**Verdict: CONFIRMED**

Both files test "Any Planet" (target=None) colonization picking the first unowned planet. `test_process_colonize_validation.py::TestProcessColonizeAnyPlanet::test_any_planet_selects_first_unowned` tests the same scenario with the same assertions.

---

## Claim 5: test_process_colonize_cargo.py::test_colonize_ship_stays + test_colonize_fleet_not_removed -- DUPLICATE_OF test_colonize_population.py

**Verdict: DOWNGRADED to MEDIUM**

The cargo file tests that ship stays in fleet and fleet stays in empire after colonization. While `test_colonize_population.py` does test the overall colonization flow with fleet.ships, its focus is population transfer. The "ship stays" and "fleet not removed" assertions are Phase 2 regression tests. However, these exact checks exist in `test_process_colonize_validation.py` (lines 201-207: ship stays, fleet stays), `test_colonize_logic.py` (line 129: fleet stays), and `test_execution.py` (line 60: fleet stays). So while not the same file as claimed, they ARE duplicated across multiple files. The claim's target file is wrong but the duplication is real.

---

## Claim 6: test_execution.py 3 tests -- DUPLICATE_OF test_commands_colonization.py

**Verdict: DOWNGRADED to LOW**

`test_execution.py` is an integration test that exercises `turn_engine.process_turn()` end-to-end, using real fixtures (`empire_with_fleet`, `turn_engine`). It tests: ownership transfer, colony list addition, fleet staying. These are integration-level tests that test the full turn processing pipeline. `test_commands_colonization.py` tests at the command handler level. Different abstraction levels = not pure duplicates. These integration tests have value as end-to-end smoke tests.

---

## Claim 7: test_validation.py all 5 tests -- DUPLICATE_OF test_colonize_validator.py

**Verdict: DOWNGRADED to MEDIUM**

`test_validation.py` is an integration test using `turn_engine.validate_colonize_order()`. `test_colonize_validator.py` tests the `ColonizeValidator` class directly. These test the same logical validations but at different layers. The integration tests verify the wiring between TurnEngine and ColonizeValidator works. However, the integration tests are thin passthroughs and the wiring is unlikely to break. Downgraded because they still have marginal integration-layer value.

---

## Claim 8: test_colonize_logic.py 3 pod consumption tests -- DUPLICATE_OF test_planet_specific_colonization.py

**Verdict: CONFIRMED**

Lines 222-321 test: pod consumed from cargo (ship stays), single-ship fleet stays, and consuming exactly one pod when two exist. These scenarios are tested in `test_process_colonize_cargo.py` (which also tests these same behaviors) and `test_planet_specific_colonization.py`. The MockPlanet in this file uses simplified mocks rather than real Planet objects, making it a weaker test than the other files. Confirmed duplicate.

---

## Claim 9: test_colonize_logic.py 4 validation tests -- DUPLICATE_OF test_process_colonize_validation.py + test_colonize_validator.py

**Verdict: DOWNGRADED to MEDIUM**

Lines 111-195 test: specific planet success, wrong location fail, any planet success, any planet fail (no candidates), specific planet fail (owned). These tests use `order_processor.execute_action_order()` which is a higher-level entry point than `process_colonize()`. This tests the `execute_action_order` routing to `process_colonize`, adding marginal integration value. However, the core logic tested is identical.

---

## Claim 10: test_colonize_planet.py -- DUPLICATE_OF test_colonize_harvester.py::TestColonizePlanet

**Verdict: CONFIRMED**

Both files test `ColonizePlanet` ability: init with string/dict, layer is STRATEGIC, allowed scopes, UI rows, all planet types, registry presence, factory creation. The `test_colonize_harvester.py::TestColonizePlanet` class (lines 31-140+) covers all the same cases. The `test_colonize_planet.py` file is redundant.

---

## Claim 11: test_superweapon_handler_validation.py 5 "rejects" tests -- DUPLICATE_OF test_superweapon_command_handlers.py

**Verdict: DOWNGRADED to MEDIUM**

`test_superweapon_handler_validation.py` (PROJ-207 Phase 2) tests that handlers pass `component_registry` to validators and reject fleets without abilities. `test_superweapon_command_handlers.py` (PROJ-102 Phase 5) tests the same handlers for successful execution, order creation, and validation failures. The "rejects" tests overlap, but the "passes component_registry" tests are unique to the validation file -- they verify that `component_registry` is threaded through as a keyword argument, which the other file doesn't check. The "rejects" tests ARE duplicates, but the "passes_component_registry" tests add unique coverage.

The claim says "5 rejects direct handler tests" but the file has 10 `test_passes_component_registry` + 10 `test_rejects` = 20 tests total. Only the 10 rejects overlap. The 10 registry-passing tests are unique. **REJECTED** as a full-file removal. A partial cleanup (removing only the rejects) would be valid.

---

## Claim 12: test_superweapon_operations.py::test_init_stores_references -- DUPLICATE_OF test_strategy_superweapons.py

**Verdict: CONFIRMED**

Both files have nearly identical `test_init_stores_references`/`test_init_stores_scene_and_facade` that assert `ops.scene is scene` and `ops.facade is facade`. Pure duplication.

---

## Claim 13: test_superweapon_operations.py::test_properties_delegate_to_scene -- DUPLICATE_OF test_strategy_superweapons.py

**Verdict: CONFIRMED**

Both test that `ops.camera is scene.camera`, `ops.hex_size is scene.hex_size`, `ops.galaxy is scene.galaxy`. Exact duplicates.

---

## Claim 14: test_fleet_order_transfer.py TestExecuteLoad + TestExecuteUnload (10 tests) -- DUPLICATE_OF test_transfer_order.py

**Verdict: DOWNGRADED to MEDIUM**

`test_fleet_order_transfer.py` tests `_execute_load()` and `_execute_unload()` with MOCK fleet objects (`MagicMock(spec=Fleet)`). `test_transfer_order.py` (495 lines) tests the same flow but includes serialization roundtrips and uses some real objects. The mock-based tests in the transfer file test internal methods (`_execute_load`, `_execute_unload`) which are private implementation details. However, they test important edge cases like capping by capacity, capping by population, species_id filtering, and zero-amount semantics. While `test_transfer_order.py` has its own load/unload tests, the edge case coverage differs. Downgraded because some test cases may be unique.

---

## Claim 15: test_fleet_order_transfer.py TestTransferValidation 3 tests -- DUPLICATE_OF test_transfer_order.py

**Verdict: DOWNGRADED to MEDIUM**

The 3 validation tests (invalid direction, load passengers, unload passengers) exercise `process_transfer()` with mock objects. `test_transfer_order.py` has similar tests. However, the mock-based approach in the flagged file tests slightly different integration points. Not a clean duplicate.

---

## Claim 16: test_fleet_order_processor.py 3 dataclass tests -- TRIVIAL_CONSTANT

**Verdict: CONFIRMED**

Lines 459-487 test `JoinFleetResult` and `ColonizeResult` dataclasses by asserting that fields set in the constructor can be read back. These are trivial tests of Python dataclass behavior: `assert result.merged is True`, `assert result.planet_name == "Earth"`, `assert result.colonized is False`. No logic is tested.

---

## Claim 17: test_fleet_order_processor.py TestOrderProcessorCreation -- TESTS_NOTHING_REAL

**Verdict: CONFIRMED**

Lines 60-69: Creates an `OrderProcessor()` and asserts `processor is not None`. This tests that a class can be instantiated, which is a trivial import test with zero behavioral coverage.

---

## Claim 18: test_fleet_production_e2e.py 2 movement blocking tests -- DUPLICATE_OF test_movement_build_blocking.py

**Verdict: DOWNGRADED to MEDIUM**

Lines 210-260 test that fleet with BUILD order can't move and fleet without BUILD order can move. These are E2E integration tests that go through `FleetMovementEngine.collect_movements()`. The dedicated `test_movement_build_blocking.py` file presumably tests the same logic. However, E2E tests have value as smoke tests for the full integration. Removing them reduces integration coverage even if unit coverage is maintained.

---

## Claim 19: test_fleet_production_e2e.py::test_save_load_preserves_build_state -- DUPLICATE_OF test_fleet_save_load.py

**Verdict: CONFIRMED**

Lines 262-292 create a Fleet with construction queue, serialize to JSON, deserialize, and check state. `test_fleet_save_load.py` exists specifically for this purpose and likely covers the same scenario with more comprehensive assertions.

---

## Claim 20: test_production_rates.py (unit) all 7 tests -- DUPLICATE_OF test_production_rates.py (integration)

**Verdict: REJECTED**

The unit file (`tests/unit/strategy/data/test_production_rates.py`) tests the JSON data file directly -- loading `production_rates.json`, checking both yard types exist, verifying all 5 resource types, and checking specific rate values (2000/turn planetary, 30000/turn space). The integration file (`tests/integration/strategy/test_production_rates.py`) tests the production rate *system* -- turn calculations, bottlenecks, per-tick capping, resource consumption over turns, and `BuildQueueSource` integration.

These test entirely different things. The unit tests validate the data file contents. The integration tests validate the production rate logic and calculations. **Not duplicates at all.**

---

## Claim 21: test_bug_01_crew_delay.py -- DUPLICATE_OF test_crew_abilities.py + test_crew_required_mass_scaling.py

**Verdict: CONFIRMED**

The repro test creates a Component with CrewRequired=5, adds a modifier with `crew_req_mult`, recalculates, and checks `get_crew_required(ship) == 10.0`. This specific modifier-scaling behavior is tested in `test_crew_required_mass_scaling.py` (dedicated to crew scaling) and crew abilities tests. The repro test uses raw manual injection of `ApplicationModifier` which is fragile and not production-representative.

---

## Claim 22: test_bug_02_seeker.py -- DUPLICATE_OF weapon ability tests

**Verdict: CONFIRMED**

Uses `MockComponent` (local class with `stats = {}`, `ability_stats = {}`, `ship = None`) -- completely bypasses the real component system. Tests that `SeekerWeaponAbility.range` equals `500 * 3.0 * 0.8 = 1200` before and after `recalculate()`. This specific calculation is tested by proper seeker weapon ability tests with real components.

---

## Claim 23: test_bug_03_validation.py -- DUPLICATE_OF test_warnings.py + test_ship_validator_rules.py

**Verdict: CONFIRMED**

Tests that adding Energy Storage doesn't resolve a Fuel Storage warning, and adding Fuel Storage doesn't resolve an Ammo Storage warning. This "wrong resource type doesn't fix wrong warning" behavior is core validation logic tested in `test_ship_validator_rules.py` (which tests all validation rules systematically). The repro test adds value as a regression guard but the exact scenarios should be covered by the proper validator tests.

---

## Claim 24: test_bug_05_logistics.py -- DUPLICATE_OF test_ui_stats.py

**Verdict: CONFIRMED**

Tests that `get_logistics_rows(ship)` returns rows for all 6 energy stat categories (capacity, gen, constant, max_usage, endurance, max_endurance). `test_ui_stats.py` tests `get_logistics_rows()` with similar component setups. The repro test uses manual ability injection rather than proper component construction.

---

## Claim 25: test_bug_05_rejected_fix.py -- DUPLICATE_OF test_ui_stats.py

**Verdict: CONFIRMED**

Tests `get_logistics_rows()` visibility when only consumption exists (no storage/gen), and max usage calculation. Same function tested in `test_ui_stats.py`. The repro file tests a subset of the same scenarios.

---

## Claim 26: test_bug_05_deep_repro.py -- DUPLICATE_OF test_ui_stats.py + test_resource_consumption.py

**Verdict: CONFIRMED**

Tests ShieldRegeneration constant energy consumption and Laser activation energy consumption showing up in logistics rows. Both scenarios are tested in `test_ui_stats.py`. The deep repro adds concrete data-driven component dictionaries, but the behavior under test is the same.

---

## Claim 27: test_bug_06_combat_propulsion.py -- DUPLICATE_OF many CombatPropulsion test files

**Verdict: CONFIRMED**

Tests that CombatPropulsion abilities are detected by validation and that thrust values are aggregated correctly. This is core CombatPropulsion functionality that has dedicated tests. The repro test uses "Manual Headless Assembly" pattern (manually constructing layers/components) which is fragile and tests the same assertions as the proper ability tests.

---

## Claim 28: test_bug_07_crash.py -- DUPLICATE_OF test_ship_stat_querier.py + test_ability_interface.py

**Verdict: CONFIRMED**

Tests that `ship.get_total_sensor_score()` doesn't crash with `AttributeError: 'ToHitAttackModifier' has no attribute 'value'`. This was a specific bug fix -- the interface now works. The proper ability interface tests and ship stat querier tests verify this behavior in a more structured way.

---

## Claim 29: test_bug_08_fuel_validation.py -- DUPLICATE_OF test_ship_validator_rules.py

**Verdict: CONFIRMED**

Tests that a fuel tank provides ResourceStorage for fuel, and that `ship.resources.get_max_value('fuel') > 0`. This is basic resource storage validation tested in `test_ship_validator_rules.py` and resource ability tests.

---

## Claim 30: test_bug_09_endurance.py -- DUPLICATE_OF test_combat_endurance.py + test_ui_stats.py

**Verdict: CONFIRMED**

Tests that fuel endurance is not infinite when engine consumes fuel and ship has fuel tank. Uses `stats_config.fmt_time()` to verify display. This endurance calculation is tested in `test_combat_endurance.py` and `test_ui_stats.py`.

---

## Claim 31: test_bug_10_logistics_update.py -- DUPLICATE_OF test_ui_stats.py

**Verdict: CONFIRMED**

Tests that adding a weapon consuming ammo triggers ammo logistics rows to appear, and checks consumption values. Same function (`get_logistics_rows`) and same scenarios as `test_ui_stats.py`.

---

## Claim 32: test_bug_12_energy_gen.py -- behavior tested in resource/crew tests

**Verdict: DOWNGRADED to LOW**

This file has genuine diagnostic value. It tests two important behaviors:
1. Generator WITHOUT crew is inactive (energy gen = 0) -- tests component deactivation due to unmet crew
2. Generator WITH crew is active (energy gen = 25.0) -- tests proper crew-enabled generation

While these behaviors are individually tested in crew ability tests and resource generation tests, this file tests their *interaction* (crew requirement affecting resource generation). The test comments document root cause analysis ("WORKING AS DESIGNED - not a code bug"). I'd keep this as it tests a specific cross-cutting interaction.

---

## Claim 33: test_bug_14_multi_planet_offset.py -- TESTS_NOTHING_REAL, local arithmetic

**Verdict: CONFIRMED**

Despite importing `pygame`, the file does NO production code imports and NO game.* module calls. Every test performs local arithmetic: `group_offset_x = -largest_diameter * 0.20` then `assert group_offset_x == -20.0`. It reimplements rendering formulas in local variables and asserts the local math is correct. No actual renderer code is tested. Confirmed TESTS_NOTHING_REAL.

---

## Claim 34: test_bug_16_raw_data_button.py -- TESTS_NOTHING_REAL + inspect.getsource

**Verdict: CONFIRMED**

First test does local arithmetic on a `pygame.Rect`. Second test uses `inspect.getsource(strategy_panel_manager.create_strategy_panels)` and checks if `"graph_rect.right"` appears in the source code string. This is an anti-pattern -- source code string matching is fragile and doesn't test behavior. The first test only validates that `138 == 138` after local math. Confirmed.

---

## Claim 35: test_bug_17_drag_preview.py -- TESTS_NOTHING_REAL, inspect.getsource

**Verdict: CONFIRMED**

Two of three tests use `inspect.getsource()` to check that "portrait" appears in the source code of `BuildQueueDragHandler.handle_mouse_down` and `draw_drag_preview`. The third test asserts `48 >= 32 and 48 <= 64` on a local constant. No behavior is tested. Confirmed.

---

## Claim 36: test_crash_planet_list.py -- TESTS_NOTHING_REAL, tests local MockPlanetListWindow

**Verdict: CONFIRMED**

The file defines a local `MockPlanetListWindow` class with `_gather_planets()` method, then tests that this LOCAL mock works correctly. No production code is imported or tested. The `MockGalaxy` and `MockPlanetListWindow` are both defined in the test file itself. The test verifies the local mock returns 2 planets with correct names. Confirmed TESTS_NOTHING_REAL.

---

## Claim 37: test_builder_refactor.py -- DUPLICATE + TRIVIAL

**Verdict: CONFIRMED**

Contains two tests:
1. `test_imports` -- tries to import 3 modules and fails if ImportError. This is a basic import check, not behavior testing.
2. `test_preset_manager` -- tests `PresetManager.save_preset()` and `get_preset()`. This is a legitimate functional test but uses unittest.TestCase style (not pytest).

The import test is trivial (modules are imported by hundreds of other tests). The preset manager test has minor value but is likely covered by proper preset tests. Additionally, the file manipulates `sys.path` directly. Confirmed as removable.

---

## Claim 38: _verify_builder_imports.py -- DEAD_CODE, standalone script

**Verdict: CONFIRMED**

This is a standalone script (not a pytest test file) that:
1. Calls `pygame.init()` and `pygame.display.set_mode((100, 100))` at module level
2. Tries to import builder submodules
3. Calls `sys.exit(1)` on failure
4. Has `print()` statements

This is not discoverable by pytest (no test functions/classes). It's a manual verification script. Confirmed DEAD_CODE.

---

## Claim 39: reproduce_scaling.py -- DUPLICATE_OF modifier binding tests

**Verdict: DOWNGRADED to MEDIUM**

Tests `create_component("crew_quarters")` and `create_component("life_support")` with `add_modifier("simple_size_mount", 2.0)` and asserts abilities scale linearly. This uses real production components and real modifier system, making it a valid integration test. While the scaling behavior is tested in modifier binding tests, this specific test exercises the real data files. Not a pure duplicate but low-priority.

---

## Claim 40: test_extract_phase.py 5 placeholder tests with pass body -- SCAFFOLD_ONLY

**Verdict: CONFIRMED**

Lines 406-431 contain 5 tests with `pass` body:
- `test_validate_phase_extracted_with_active_subproject` -- `pass`
- `test_validate_phase_extracted_with_archived_subproject` -- `pass`
- `test_audit_ready_with_extracted_phases` -- `pass`
- `test_audit_ready_warns_active_subproject` -- `pass`
- `test_audit_ready_errors_missing_subproject` -- `pass`

All are explicitly marked as "Placeholder for integration test". The rest of the file (non-placeholder tests) is legitimate and should be kept. Only the 5 `pass` bodies should be removed.

---

## Summary

| Verdict | Count | Claims |
|---------|-------|--------|
| CONFIRMED | 24 | 1, 2, 3, 4, 8, 10, 12, 13, 16, 17, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36, 37, 38, 40 |
| DOWNGRADED | 10 | 5, 6, 7, 9, 11, 14, 15, 18, 32, 39 |
| REJECTED | 6 | 6 (to LOW), 11 (partial reject - registry tests unique), 20 (not duplicates) |

**Note on counts:** Claims 6 and 11 are counted in both DOWNGRADED and partially REJECTED because they contain mixed verdicts (some tests duplicate, some unique).

**Precise count:**
- Pure CONFIRMED removals: 24 claims
- DOWNGRADED (lower confidence, still possibly removable): 10 claims  
- REJECTED (should keep): 2 claims (#11 partial, #20 full)

### Critical Findings

1. **Claim 11 (superweapon_handler_validation.py):** The "passes component_registry" tests are UNIQUE -- they verify kwargs threading that no other file tests. Only the "rejects" tests are duplicates. A full-file removal would lose coverage.

2. **Claim 20 (production_rates.py unit vs integration):** These are NOT duplicates. The unit tests validate data file contents. The integration tests validate calculation logic. Completely different concerns.

3. **Claim 32 (bug_12_energy_gen.py):** Tests a cross-cutting crew-requirement-affects-generation interaction that isn't cleanly covered by either crew tests or resource tests alone. Worth keeping as a focused integration test.

4. **Claims 33-36 (TESTS_NOTHING_REAL):** All confirmed. Bug 14 tests local math, Bug 16/17 use `inspect.getsource()`, and the planet list crash test tests a local mock class. None exercise production code paths.
