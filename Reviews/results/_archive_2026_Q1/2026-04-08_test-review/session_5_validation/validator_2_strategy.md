# Validator 2: Strategy Claims Validation Report

Skeptical validation of 29 claims from Session 2 (Strategy). Each claim independently verified by reading actual test files and production source code.

---

## Claim 1: `test_ship_pod_storage.py` -- OVER_MOCKED

**Verdict: CONFIRMED**

The claim is correct. The `_make_ship_with_pod_capacity()` helper (lines 9-21) creates a `MagicMock(spec=ShipInstance)` and then manually re-implements the three methods as lambdas:

```python
ship.get_pod_storage_capacity = lambda: float(ship.get_calculated_stats().get('pod_storage_mass', 0))
ship.get_pod_storage_used = lambda: sum(item.get('mass', 0.0) for item in ship.carried_items)
ship.can_carry_pod = lambda mass: (...)
```

I verified the actual `ShipInstance` class at `game/strategy/data/ship_instance.py` lines 376-390 -- these are real methods with the same logic. The tests are testing the lambda re-implementations, NOT the actual ShipInstance methods. If someone changes the real methods, these tests would still pass because they never call the real code. This is textbook OVER_MOCKED.

---

## Claim 2: `test_production_rates.py` TestProductionRatesJson -- TRIVIAL_CONSTANT

**Verdict: DOWNGRADED to LOW**

The claim says these are "also tested through code paths in test_build_queue_source.py." I searched `test_build_queue_source.py` and found that file uses hardcoded expected rates (`EXPECTED_PLANETARY_RATES`, `EXPECTED_SHIPYARD_RATES`) which implicitly test the same constants. However, `test_production_rates.py` directly validates the JSON data file (`data/production_rates.json`) structure and values. These are legitimate data-file contract tests -- they catch typos, missing resources, wrong values in the data file. The overlap with `test_build_queue_source.py` is partial (the build queue tests don't validate JSON structure). This is a useful data validation test, not truly trivial.

---

## Claim 3: `test_commands.py` TestCommandType (lines 41-48) -- TRIVIAL_CONSTANT

**Verdict: CONFIRMED**

Lines 41-48 test that `CommandType.ISSUE_ORDER` exists (`hasattr`) and that its value is an `int` (from `enum.auto()`). This tests Python's `enum.auto()` mechanism, not any project logic. If `enum.auto()` breaks, Python itself is broken.

---

## Claim 4: `test_commands.py` test_with_origin_hex + test_intercept_self -- TRIVIAL_CONSTANT

**Verdict: DOWNGRADED to LOW (reject for test_intercept_self)**

- `test_with_origin_hex` (line 119-122): Creates a move command with `HexCoord(0,0)` and asserts it equals `HexCoord(0,0)`. This tests nothing meaningful -- CONFIRMED trivial.
- `test_intercept_self` (line 140-142): This actually documents a design decision -- that the command dataclass allows self-interception (validation happens elsewhere). While simple, it serves as documentation of a non-obvious contract. I would **REJECT** removal of `test_intercept_self` -- it's a valid edge case contract test.

---

## Claim 5: `test_build_order_command_handler.py` 4 IssueBuildOrderCommand dataclass tests (lines 18-41) -- DUPLICATE_OF test_commands.py

**Verdict: DOWNGRADED**

I verified: `TestIssueBuildOrderCommand` (lines 18-41) tests `IssueBuildOrderCommand` construction, name, and equality. `test_commands.py` does NOT contain any tests for `IssueBuildOrderCommand` (I searched the whole file -- it imports from commands but only tests other command types). The claim says these are duplicates of test_commands.py, but **there are no corresponding tests in test_commands.py for IssueBuildOrderCommand**. The tests ARE trivial dataclass construction tests, but the "DUPLICATE_OF" label is factually wrong. Should be TRIVIAL_CONSTANT at best, and even then, these tests live alongside the handler tests they contextualize. Keep them.

---

## Claim 6: `test_planet_energy_cache.py` test_cached_values_reused (lines 52-63) -- TESTS_NOTHING_REAL

**Verdict: CONFIRMED**

The test calls `_process_planet` twice (tick 1 and tick 2), then asserts `'capacity' in cache` and `'generation' in cache`. But those same keys were already populated on the first tick -- the test proves nothing about caching behavior. It doesn't verify the scan ran only once, doesn't check performance, doesn't verify the cached values are actually reused. The test name says "reused" but the assertions only check key existence, which was already true after tick 1. The adjacent tests (cache populated, cache invalidated, facility count change) are all fine.

---

## Claim 7: `test_fleet_order_transfer.py` TestTransferResult (lines 369-389) -- TRIVIAL_CONSTANT

**Verdict: CONFIRMED**

Two tests: one creates `TransferResult(success=True, amount_transferred=100, message="OK")` and asserts the fields match; the other creates `TransferResult(success=False)` and checks defaults (0, ""). I verified the source: `TransferResult` is a 3-field `@dataclass` with defaults. These are testing Python's `@dataclass` mechanism. No business logic tested.

---

## Claim 8: `test_engine_interfaces.py` -- SCAFFOLD_ONLY, 476 LOC all ABC mechanics

**Verdict: CONFIRMED**

I read the entire 476-line file. Every test class follows the identical pattern:
1. `test_X_importable` -- asserts import is not None
2. `test_X_is_abstract` -- asserts `issubclass(X, ABC)`
3. `test_X_cannot_instantiate` -- asserts `pytest.raises(TypeError)`
4. `test_X_has_Y_method` -- asserts `hasattr` + `__isabstractmethod__`
5. `test_concrete_X_implementation` -- creates an inline mock subclass

This tests Python's ABC machinery, not project logic. The `TestConcreteImplementations` class (lines 295-398) creates trivial mock implementations that return `[]` or `None`, testing nothing about the real implementations. The `TestInterfacesModuleExports` class tests `__all__` lists.

I searched for `test_engine_inheritance` -- no such file exists. So the claim's suggestion to verify coverage there is moot. But the removal is still valid: these are pure ABC/import scaffolding tests.

---

## Claim 9: `test_simulation_adapter.py` TestSimulationBattleResolverImport (lines 18-29) -- SCAFFOLD_ONLY

**Verdict: CONFIRMED**

Two tests: (1) import from `simulation_adapter` module, assert not None; (2) import from `adapters` package, assert not None. Pure import verification that any other test in this file implicitly exercises.

---

## Claim 10: `test_battle_resolver.py` -- SCAFFOLD_ONLY for import/structural tests

**Verdict: DOWNGRADED**

The file contains both scaffold tests AND substantive contract tests:
- SCAFFOLD (removable): `test_ibattle_resolver_importable`, `test_battle_result_importable`, `test_battle_result_is_dataclass`, `test_ibattle_resolver_is_abstract`, `TestInterfacesModuleExports` -- all test import/type mechanics.
- KEEP: `TestBattleResult` field tests (test the DTO contract), `test_concrete_implementation_must_implement_resolve_battle` (tests ABC enforcement), `test_resolve_battle_accepts_two_fleets_and_optional_seed`, `test_resolve_battle_returns_battle_result`. These test the interface contract. The distinction between "scaffold" and "contract test" matters here.

Recommend: Partial removal only. ~8 of 14 tests are scaffold; the remaining 6 test meaningful contracts.

---

## Claim 11: `test_simulation_adapter.py` TestSimulationBattleResolverImplementation (lines 37-60) -- SCAFFOLD_ONLY

**Verdict: DOWNGRADED**

- `test_implements_ibattle_resolver` (issubclass check) -- scaffold, but catches actual breaking changes if someone removes the base class
- `test_can_instantiate` -- scaffold
- `test_has_resolve_battle_method` -- scaffold, implicitly covered by the behavior tests below

These are lightweight but not harmful. The file also contains substantive behavior tests (TestSimulationBattleResolverBehavior, TestSimulationBattleResolverDependencyInjection) that should absolutely be kept. Removing just the 3 scaffold tests saves 24 lines -- minimal value.

---

## Claim 12: `test_colonize_validator.py` -- ~600 LOC consolidation target, 8.7:1 ratio

**Verdict: DOWNGRADED (partially REJECTED)**

I counted: the file has **1247 lines** and **48 test methods** across 8 test classes. The source (`colonize_validator.py`) is 143 lines. That's an **8.7:1** ratio, matching the claim.

However, I read the test classes carefully. They are NOT duplicates:
- `TestColonizeValidatorBasic` (6 tests): core happy/sad paths
- `TestColonizeValidatorAnyPlanet` (3 tests): "any planet" mode
- `TestColonizeValidatorEdgeCases` (5 tests): race conditions, moved fleet, planet colonized between validate/execute
- `TestColonizeValidatorMessages` (3 tests): error message content
- `TestColonizeValidatorColonyPods` (12 tests): drop pod counting, committed orders, multi-ship pod distribution
- `TestColonizeValidatorZoneColonization` (4 tests): multi-hex Dyson sphere planets
- `TestColonizeValidatorAnyPlanetPods` (6 tests): "any planet" + pod interaction
- `TestColonizeValidatorAdvancedEdgeCases` (9 tests): overcommit, deduplication

The tests cover genuinely different scenarios. The high ratio comes from the extensive mock setup (~15 lines per test for galaxy/fleet/planet fixtures) and the validator being a simple static class. The test-to-source ratio is high but **NOT from semantic duplication** -- it's from thorough edge case coverage of a critical game mechanic (colonization).

Some consolidation is possible (shared fixtures could reduce boilerplate by ~200 lines), but mass deletion would lose meaningful edge case coverage. REJECT the claim as stated ("consolidation target" implying mass removal). Accept that fixture consolidation could trim ~200 LOC without losing coverage.

---

## Claim 13: `test_strategy_session_facade.py` TestEventQueries (lines 614-692) -- DUPLICATE_OF test_event_queries.py

**Verdict: DOWNGRADED**

I searched for `test_event_queries.py` in `tests/unit/strategy` -- **no such file exists**. The claimed duplicate target does not exist. The TestEventQueries class (4 tests) tests facade delegation to `session.event_log.get_events_for_turn`, `.get_all_events`, `.get_events_by_category`. These are legitimate facade delegation tests. The claim's basis (duplicate of a non-existent file) is wrong.

REJECT removal.

---

## Claim 14: Two TestGameStateQueries classes -- Python shadow bug

**Verdict: CONFIRMED**

I found two `class TestGameStateQueries` definitions:
- Line 453: Tests `get_turn_number` and `get_human_player_ids` (2 tests)
- Line 695: Tests `get_save_path` (2 tests, PROJ-208 Phase 4)

In Python, the second class definition shadows the first. The first class's tests (get_turn_number, get_human_player_ids) are **never executed by pytest**. This is a real bug. Fix: rename one class (e.g., `TestGameStateQueriesPhase4`). This is not a "removal" but a "fix" -- the shadowed tests should be recovered, not deleted.

---

## Claim 15: `test_event_types.py` 13 constant-equality tests -- TRIVIAL_CONSTANT

**Verdict: CONFIRMED with caveat**

13 tests like `assert EventType.SHIP_BUILT == "ship_built"`. These test that enum string values match expected strings. While seemingly trivial, these values may be serialized to JSON/save files. If someone changes an enum value, deserialization breaks silently. However, the `test_has_seventeen_members` and `test_has_seven_members` count tests ARE fragile and should be removed (they break every time a new event type is added). The individual value tests serve as a serialization contract. I would keep the value tests but remove the count tests.

---

## Claim 16: `test_geometric.py` test_rotation_affects_shape (line 86) -- `assert d1 != d2 or True` always passes

**Verdict: CONFIRMED**

Line 86: `assert d1 != d2 or True`. This is `assert True` regardless of d1 and d2 values. The test can never fail. The comment says "May be equal by coincidence" but the `or True` makes the entire assertion a no-op. This test provides zero validation.

---

## Claim 17: `test_spiral_arm.py` test_rotation_shifts_pattern (line 78) -- `assert d1 != d2 or True` always passes

**Verdict: CONFIRMED**

Line 78: `assert d1 != d2 or True`. Identical issue to claim 16. The assertion can never fail. Test provides zero validation.

---

## Claim 18: `test_empire_dto.py` -- frozen dataclass tests

**Verdict: DOWNGRADED to MEDIUM (partial REJECT)**

The file has 5 test classes with a mix of tests:
- **Scaffold (removable)**: `test_is_frozen` tests (3 tests, testing Python's `@dataclass(frozen=True)`) -- these test Python, not project logic.
- **KEEP**: Factory method tests (`TestEmpireInfoFactory`, `TestColonySummaryFactory`, `TestFleetSummaryFactory`) -- these test real `from_empire()`, `from_planet()`, `from_fleet()` factory methods with actual domain objects. These exercise real conversion logic and catch regressions.

The claim labels the entire file as "frozen dataclass tests" but ~40% of the tests are meaningful factory tests. Remove only the frozen/construction tests, keep the factory tests.

---

## Claim 19: `test_fleet_dto.py` -- frozen dataclass tests

**Verdict: DOWNGRADED to MEDIUM (partial REJECT)**

Same pattern as claim 18. The file contains:
- **Scaffold**: `test_is_frozen` (3 tests), basic construction tests that just assign and read back fields
- **KEEP**: `TestFleetInfoFactory` tests (7 tests) testing `FleetInfo.from_fleet()` with actual Fleet objects, ship damage calculation, order conversion, join_fleet orders. `test_collection_fields_are_immutable_tuples` and `test_from_fleet_returns_tuples` test a real design decision (tuples for immutability).

Do not remove the entire file. Remove ~5 frozen/basic-construction tests, keep ~12 factory and immutability-contract tests.

---

## Claim 20: `test_system_dto.py` -- frozen dataclass tests

**Verdict: DOWNGRADED to MEDIUM (partial REJECT)**

Same pattern. The file has:
- **Scaffold**: `test_is_frozen` (4 tests), basic construction
- **KEEP**: `TestSystemInfoFactory` (5 tests) testing `from_star_system()` with real domain objects (StarSystem, Star, Planet, warp points), colony counting logic. `TestPlanetInfoFactory` (3 tests) testing `from_planet()` with shipyard detection.

Remove ~6 frozen/construction tests, keep ~8 factory tests.

---

## Claim 21: `test_commands.py` (integration) 4 command class construction tests (lines 201-287) -- TRIVIAL_CONSTANT

**Verdict: CONFIRMED**

Lines 201-287 contain `TestIssueInterceptCommand`, `TestIssueJoinFleetCommand`, `TestQueueColonizeMissionCommand`, `TestClearFleetOrdersCommand`. These are exact duplicates of the unit tests in `tests/unit/strategy/engine/test_commands.py` (same class names, same assertions). The integration directory adds no integration-level testing.

---

## Claim 22: `test_commands.py` (integration) TestGameSessionCommands.test_handle_command (line 191) -- empty `pass` body

**Verdict: CONFIRMED**

Lines 190-198: The test method body is literally `pass` with a multi-line comment explaining they couldn't figure out how to test it. This test asserts nothing. Remove.

---

## Claim 23: `test_queue.py` (integration) test_production_progress (line 63) -- empty `pass` body

**Verdict: CONFIRMED**

Lines 61-76: The test body ends with `pass` after a long comment about needing Galaxy mocking. It asserts nothing. Remove.

---

## Claim 24: `test_hex_math_strategy.py` -- pure unit tests, DUPLICATE_OF core hex tests

**Verdict: CONFIRMED**

I compared the two files:
- `tests/integration/strategy/test_hex_math_strategy.py`: Tests `HexCoord.__init__`, equality, hash, addition, subtraction, neighbors, distance, pixel conversion. 98 lines.
- `tests/unit/core/test_hex_math_core.py`: Comprehensive tests of the exact same functions plus many more (rings, line drawing, serialization, etc.).

Every test in the integration file is a strict subset of the core test file. The integration file tests HexCoord (which is in `game/core/`, not `game/strategy/`). It's misplaced AND duplicated. Remove.

---

## Claim 25: `test_fleet_movement.py` test_fleet_initialization -- TRIVIAL_CONSTANT

**Verdict: CONFIRMED**

Lines 7-10: Creates a `Fleet(1, 0, loc)` and asserts `location == loc` and `ships == []`. This tests default initialization of two fields. The other tests in this file (interstellar pathfinding, no-path) are substantive and should be kept. Only `test_fleet_initialization` should be removed.

---

## Claim 26: `test_empire.py` 3 fleet ID tests -- unit behavior in integration dir

**Verdict: DOWNGRADED to LOW (REJECT removal)**

The file has 4 tests:
1. `test_fleet_id_sequential` -- basic
2. `test_fleet_id_starts_at_10000` -- documents a specific contract
3. `test_fleet_id_persists_across_save` -- **tests serialization round-trip** (to_dict/from_dict). This IS integration-level.
4. `test_multiple_empires_have_independent_counters` -- documents cross-empire isolation

Test 3 is genuinely an integration test (tests serialization + counter continuation). Tests 1/2/4 could be unit tests but they're not duplicated elsewhere. Moving them to unit tests is fine, but removing them outright would lose coverage of the fleet ID contract. REJECT removal; recommend relocation.

---

## Claim 27: `test_strategy_scene.py` TestTurnManagement -- TESTS_NOTHING_REAL, local lambdas

**Verdict: CONFIRMED**

Lines 81-123: Two tests (`test_turn_index_cycles_through_human_players`, `test_turn_processes_after_all_humans_ready`) use purely local variables and lambdas. No game code is imported or called. They test arithmetic on local integer counters:
```python
current_player_index += 1
if current_player_index >= len(human_player_ids):
    current_player_index = 0
```

These test the concept of modular arithmetic, not any production code. Remove.

---

## Claim 28: `test_naming.py` test_roman_numerals -- unit test in integration dir

**Verdict: DOWNGRADED to LOW (REJECT removal)**

`test_roman_numerals` (lines 43-50) tests `NameRegistry.to_roman()`. While this is a pure unit test, it's the ONLY test of `to_roman()` in the entire codebase (I checked). The claim says it should be in a unit test directory, which is true, but removal without relocation would lose coverage. The other tests in the file (load_and_shuffle, unique_names) use temp YAML files and test the full NameRegistry lifecycle -- those are fine as integration tests.

REJECT removal; recommend relocation to unit tests.

---

## Claim 29: `test_strategy_scene.py` test_colonize_command_queues -- OVER_MOCKED

**Verdict: DOWNGRADED to MEDIUM**

The test (`test_colonize_command_queues_move_and_colonize`, lines 29-57) creates real `Fleet` and `FleetOrder` objects, not mocks. It tests the Fleet.add_order API and verifies order queue state. The setup uses `MockPlanet` and `MockSystem` but those are just simple data holders not used in any mock-patching. The test is actually exercising real Fleet order queue mechanics.

However, it doesn't test the actual `_handle_colonize_designation` UI handler -- it just manually constructs orders and adds them to a fleet. So it tests Fleet.add_order (already covered in fleet unit tests) rather than the screen's colonize flow. It's more of a "scenario documentation" test than a real integration test. Not OVER_MOCKED per se, but TESTS_NOTHING_NEW would be more accurate.

---

## Summary Table

| # | File/Test | Original | Verdict | Notes |
|---|-----------|----------|---------|-------|
| 1 | test_ship_pod_storage.py | HIGH | CONFIRMED | Lambda re-implementations, never calls real code |
| 2 | test_production_rates.py | MEDIUM | DOWNGRADED (LOW) | Legitimate data file contract test, partial overlap |
| 3 | TestCommandType | HIGH | CONFIRMED | Tests enum.auto() |
| 4 | test_with_origin_hex + test_intercept_self | MEDIUM | DOWNGRADED (split) | origin_hex trivial; intercept_self is valid contract |
| 5 | IssueBuildOrderCommand 4 tests | MEDIUM | DOWNGRADED (REJECT) | NOT duplicate -- no corresponding tests in test_commands.py |
| 6 | test_cached_values_reused | MEDIUM | CONFIRMED | Asserts same thing as tick-1 test |
| 7 | TestTransferResult | HIGH | CONFIRMED | Tests @dataclass defaults |
| 8 | test_engine_interfaces.py | HIGH | CONFIRMED | 476 LOC of ABC/import scaffolding |
| 9 | TestSimulationBattleResolverImport | HIGH | CONFIRMED | Pure import tests |
| 10 | test_battle_resolver.py | MEDIUM | DOWNGRADED (partial) | ~8 scaffold, ~6 substantive contract tests |
| 11 | TestSimulationBattleResolverImplementation | HIGH | DOWNGRADED (LOW) | Only 24 lines, minimal value in removing |
| 12 | test_colonize_validator.py | HIGH | REJECTED | No semantic duplicates; high ratio from edge cases + fixtures |
| 13 | TestEventQueries | HIGH | REJECTED | Claimed duplicate file does not exist |
| 14 | Two TestGameStateQueries | MEDIUM | CONFIRMED | Shadow bug; fix don't delete |
| 15 | test_event_types.py 13 tests | MEDIUM | CONFIRMED (partial) | Remove count tests; keep value contract tests |
| 16 | test_geometric.py rotation test | HIGH | CONFIRMED | `or True` makes assertion a no-op |
| 17 | test_spiral_arm.py rotation test | HIGH | CONFIRMED | `or True` makes assertion a no-op |
| 18 | test_empire_dto.py | HIGH | DOWNGRADED (MEDIUM) | Remove frozen tests; keep factory tests |
| 19 | test_fleet_dto.py | HIGH | DOWNGRADED (MEDIUM) | Remove frozen tests; keep factory tests |
| 20 | test_system_dto.py | HIGH | DOWNGRADED (MEDIUM) | Remove frozen tests; keep factory tests |
| 21 | integration test_commands.py 4 classes | HIGH | CONFIRMED | Exact duplicates of unit tests |
| 22 | test_handle_command empty pass | HIGH | CONFIRMED | Empty test body |
| 23 | test_production_progress empty pass | HIGH | CONFIRMED | Empty test body |
| 24 | test_hex_math_strategy.py | HIGH | CONFIRMED | Strict subset of core hex tests |
| 25 | test_fleet_initialization | HIGH | CONFIRMED | Trivial 2-field default check |
| 26 | test_empire.py 3 fleet ID tests | MEDIUM | REJECTED | test_fleet_id_persists_across_save is real integration test |
| 27 | TestTurnManagement | HIGH | CONFIRMED | Tests local arithmetic, no game code |
| 28 | test_roman_numerals | MEDIUM | REJECTED | Only coverage of to_roman() in codebase |
| 29 | test_colonize_command_queues | HIGH | DOWNGRADED (MEDIUM) | Uses real Fleet objects, but duplicates Fleet.add_order coverage |

**Totals:**
- CONFIRMED: 15 (claims 1, 3, 6, 7, 8, 9, 14, 16, 17, 21, 22, 23, 24, 25, 27)
- DOWNGRADED: 9 (claims 2, 4, 5, 10, 11, 15, 18, 19, 20, 29)
- REJECTED: 5 (claims 5, 12, 13, 26, 28)

**Critical findings:**
1. Claim 13 is based on a non-existent file -- the reviewer fabricated the duplicate target
2. Claim 12 micharacterizes thorough edge case testing as duplication
3. Claims 18-20 paint entire files when only ~40% of each file is scaffold
4. Claim 14 is real but the fix is rename, not delete
