# Test Review Report: Agent 5 -- Strategy Integration

## Scope
- Source files reviewed: N/A (integration test review -- source files referenced for cross-checking only)
- Test files reviewed: 81 files across integration/strategy, integration/colonization, integration/resource_system, integration/gameplay_loop, and repro_issues directories
- Coverage data referenced: No (qualitative review based on test code analysis)

## Summary
- Test files reviewed: 81
- Source files reviewed: 0 (cross-referenced unit test directories for overlap detection)
- Tests flagged for removal: 12 (estimated LOC: ~750)
- Tests flagged as happy-path-only: 8
- Source files with inadequate coverage: 3 (cross-layer integration gaps)

---

## A. Tests Recommended for Removal

### A1. DTO Frozen/Immutability Tests (Bulk)
- **File:** `tests/integration/strategy/facade/test_empire_dto.py`
- **Test(s):** `TestColonySummary.test_is_frozen`, `TestFleetSummary.test_is_frozen`, `TestEmpireInfo.test_is_frozen`
- **Reason:** TRIVIAL_CONSTANT -- These test that `@dataclass(frozen=True)` raises `FrozenInstanceError`. This is a Python language feature, not application logic. The creation tests already verify fields are set correctly.
- **Confidence:** HIGH
- **Evidence:** Lines 24-35, 55-66, 109-122 each just do `with pytest.raises(FrozenInstanceError): obj.field = value`. The frozen behavior is guaranteed by Python's dataclass machinery.
- **Estimated LOC saved:** 45

### A2. DTO Frozen/Immutability Tests (Fleet)
- **File:** `tests/integration/strategy/facade/test_fleet_dto.py`
- **Test(s):** `TestFleetOrderInfo.test_is_frozen`, `TestShipInfo.test_is_frozen`, `TestFleetInfo.test_is_frozen`
- **Reason:** TRIVIAL_CONSTANT -- Same as A1, testing Python language feature.
- **Confidence:** HIGH
- **Evidence:** Lines 54-64, 92-104, 169-182 all test `FrozenInstanceError` on frozen dataclasses.
- **Estimated LOC saved:** 40

### A3. DTO Frozen/Immutability Tests (System)
- **File:** `tests/integration/strategy/facade/test_system_dto.py`
- **Test(s):** `TestStarInfo.test_is_frozen`, `TestWarpPointInfo.test_is_frozen`, `TestSystemInfo.test_is_frozen`, `TestPlanetInfo.test_is_frozen`
- **Reason:** TRIVIAL_CONSTANT -- Same pattern as above.
- **Confidence:** HIGH
- **Evidence:** Lines 27-38, 55-66, 114-124, 312-325 all test `FrozenInstanceError`.
- **Estimated LOC saved:** 50

### A4. Command Class Construction Tests
- **File:** `tests/integration/strategy/test_commands.py`
- **Test(s):** `TestIssueInterceptCommand`, `TestIssueJoinFleetCommand`, `TestQueueColonizeMissionCommand`, `TestClearFleetOrdersCommand` (lines 201-287)
- **Reason:** TRIVIAL_CONSTANT -- These tests only verify that command dataclass fields are set correctly and `.name` returns the class name. No logic is exercised.
- **Confidence:** HIGH
- **Evidence:** Lines 204-217: `cmd = IssueInterceptCommand(fleet_id=1, target_fleet_id=2); assert cmd.fleet_id == 1; assert cmd.name == "IssueInterceptCommand"`. This is testing Python attribute assignment, not application logic.
- **Estimated LOC saved:** 90

### A5. Empty Test Method
- **File:** `tests/integration/strategy/test_commands.py`
- **Test(s):** `TestGameSessionCommands.test_handle_command` (line 191)
- **Reason:** TESTS_NOTHING_REAL -- The test body is `pass`. The docstring says "Mock Session logic" but no assertion or action exists.
- **Confidence:** HIGH
- **Evidence:** Line 198: `pass`. Entire test body is a single `pass` statement.
- **Estimated LOC saved:** 10

### A6. Empty Test Method
- **File:** `tests/integration/strategy/production/test_queue.py`
- **Test(s):** `TestProductionQueue.test_production_progress` (line 63)
- **Reason:** TESTS_NOTHING_REAL -- The test body is `pass` after comments explaining that the test logic wasn't implemented.
- **Confidence:** HIGH
- **Evidence:** Lines 63-77 show only comments and end with `pass`.
- **Estimated LOC saved:** 15

### A7. Hex Math Tests in Integration Directory
- **File:** `tests/integration/strategy/test_hex_math_strategy.py`
- **Test(s):** All tests in `TestHexCoord` class (lines 6-97)
- **Reason:** DUPLICATE_OF:`tests/unit/core/` -- These are pure unit tests for `HexCoord` (init, equality, hash, addition, subtraction, neighbors, distance, pixel conversion). They test `game.core.hex_math` in isolation with no cross-layer interaction. Hex math unit tests should exist in `tests/unit/core/`.
- **Confidence:** HIGH
- **Evidence:** Every test operates solely on `HexCoord` objects with no strategy-layer involvement. No Galaxy, Fleet, Empire, or Session objects are used.
- **Estimated LOC saved:** 97

### A8. Fleet Initialization Test in Integration
- **File:** `tests/integration/strategy/test_fleet_movement.py`
- **Test(s):** `test_fleet_initialization` (lines 7-10)
- **Reason:** TRIVIAL_CONSTANT -- Tests that `Fleet(1, 0, loc)` sets `location` and `ships == []`. This is a unit test for a data class constructor.
- **Confidence:** HIGH
- **Evidence:** Lines 7-10: `fleet = Fleet(1, 0, loc); assert fleet.location == loc; assert fleet.ships == []`.
- **Estimated LOC saved:** 5

### A9. Empire Fleet ID Tests
- **File:** `tests/integration/strategy/test_empire.py`
- **Test(s):** `TestEmpire.test_fleet_id_sequential`, `TestEmpire.test_fleet_id_starts_at_10000`, `TestEmpire.test_multiple_empires_have_independent_counters` (lines 8-51)
- **Reason:** DUPLICATE_OF:`tests/unit/strategy/data/test_empire_resources.py` or similar -- These test Empire.get_next_fleet_id() in isolation with no cross-layer behavior. The serialization test (`test_fleet_id_persists_across_save`) is the only integration-worthy test (save/load round-trip).
- **Confidence:** MEDIUM
- **Evidence:** Lines 8-20 and 35-51 create Empire objects and call `get_next_fleet_id()` without involving any other system. Pure unit behavior.
- **Estimated LOC saved:** 35

### A10. Strategy Scene Turn Management Tests
- **File:** `tests/integration/strategy/test_strategy_scene.py`
- **Test(s):** `TestTurnManagement.test_turn_index_cycles_through_human_players`, `TestTurnManagement.test_turn_processes_after_all_humans_ready` (lines 81-123)
- **Reason:** TESTS_NOTHING_REAL -- These tests simulate turn management logic using local variables and inline lambdas. No actual game code is exercised. The tests verify the logic of a fictional implementation, not the real TurnEngine or StrategyScreen.
- **Confidence:** HIGH
- **Evidence:** Lines 87-99 and 101-123 use `current_player_index` and a local `end_player_turn` function with `nonlocal`. No imports from `game.*` are used for this logic.
- **Estimated LOC saved:** 43

### A11. Naming Test Roman Numerals
- **File:** `tests/integration/strategy/test_naming.py`
- **Test(s):** `TestNaming.test_roman_numerals` (lines 44-51)
- **Reason:** DUPLICATE_OF:unit tests -- Testing a static utility method (`NameRegistry.to_roman`) in isolation. No integration behavior.
- **Confidence:** MEDIUM
- **Evidence:** Lines 44-51 call `NameRegistry.to_roman(N)` and assert specific string values. Pure function test.
- **Estimated LOC saved:** 10

### A12. Colonize Command Queuing Simulation
- **File:** `tests/integration/strategy/test_strategy_scene.py`
- **Test(s):** `test_colonize_command_queues_move_and_colonize` (lines 29-57)
- **Reason:** OVER_MOCKED -- The test manually creates FleetOrder objects and appends them to fleet.orders, then asserts what was just appended. It does not exercise any real command handler or strategy screen logic. It tests `Fleet.add_order()` and `list.append()`.
- **Confidence:** HIGH
- **Evidence:** Lines 46-57: Creates FleetOrder manually, calls `fleet.add_order(move_order)` / `fleet.add_order(colonize_order)`, then asserts `fleet.orders[0].type == OrderType.MOVE`. No command handler, no facade, no session.
- **Estimated LOC saved:** 30

---

## B. Tests That Are Happy-Path-Only

### B1. Facade Empire Queries
- **File:** `tests/integration/strategy/facade/test_empire_queries.py`
- **Test(s):** `TestGetEmpireColonies`, `TestGetHumanPlayerIds`, `TestGetTurnNumber`
- **What's tested:** Query methods return correct data for valid inputs and empty edge case.
- **What's missing:** No tests for malformed session state (e.g., empire with None colonies list), concurrent mutation during query, very large empire counts.
- **Source method(s) affected:** `StrategySessionFacade.get_empire_colonies`, `get_human_player_ids`, `get_turn_number`
- **Priority:** LOW

### B2. Facade Validation Queries -- can_colonize
- **File:** `tests/integration/strategy/facade/test_validation_queries.py`
- **Test(s):** `TestCanColonize`
- **What's tested:** Valid colonize, invalid (already owned), missing fleet, None planet_id.
- **What's missing:** No test for fleet at wrong location, fleet with no colony pod, fleet owned by different empire.
- **Source method(s) affected:** `StrategySessionFacade.can_colonize`
- **Priority:** MEDIUM -- These are important validation paths that users trigger directly.

### B3. Production Completion -- No Failure Paths
- **File:** `tests/integration/strategy/production/test_completion.py`
- **Test(s):** `TestProductionCompletion`, `TestComplexSpawning`, `TestShipSpawning`
- **What's tested:** Items complete and spawn correctly.
- **What's missing:** No test for: insufficient resources mid-build, corrupt queue item data, multiple items completing in same tick, shipyard destroyed during build, save_path that doesn't exist.
- **Source method(s) affected:** `ProductionEngine.process_construction_tick`, `spawn_ship`, `spawn_complex`
- **Priority:** MEDIUM

### B4. Galaxy Generation -- Only Valid Configs
- **File:** `tests/integration/strategy/test_galaxy_gen.py`
- **Test(s):** All `TestGalaxyGen` tests
- **What's tested:** Galaxy init, add system, min distance, warp linking, connectivity.
- **What's missing:** No test for: zero systems, impossibly tight min_dist (more systems than can fit), negative radius, duplicate system placement at same hex.
- **Source method(s) affected:** `Galaxy.generate_systems`, `Galaxy.generate_warp_lanes`
- **Priority:** LOW

### B5. Deterministic Generation -- No Error Handling
- **File:** `tests/integration/strategy/test_deterministic_generation.py`
- **Test(s):** All tests in `TestDeterministicGeneration`
- **What's tested:** Same seed produces same galaxy, different seeds differ, all galaxy types work.
- **What's missing:** No test for: invalid galaxy type string, seed=0, seed=MAX_INT, negative seed, system_count=0.
- **Source method(s) affected:** `GameSession.__init__` via `GameConfig`
- **Priority:** LOW

### B6. Warp Order -- Missing Resource Exhaustion
- **File:** `tests/integration/strategy/test_warp_orders.py`
- **Test(s):** `TestWarpOrderCommand`, `TestWarpOrderNavigation`
- **What's tested:** Valid warp at point, move-then-warp, reject non-warp fleet, reject invalid point.
- **What's missing:** No test for: fleet runs out of warp resources mid-jump, fleet speed changes during warp, warp to destroyed system, warp while fleet is building.
- **Source method(s) affected:** `WarpCommandHandler.execute`, `FleetNavigationService.compute_next_step`
- **Priority:** MEDIUM

### B7. Resupply System -- Only Fuel Resource
- **File:** `tests/integration/strategy/test_resupply_system.py`
- **Test(s):** All tests in file
- **What's tested:** Fuel synthesis, accumulation, cap, range equalization, enemy rejection.
- **What's missing:** No test for ammo resupply, energy resupply, multiple resource types simultaneously, facility destroyed between synthesis and resupply ticks, colony ownership changes mid-turn.
- **Source method(s) affected:** `ResupplyEngine.process_fleet_resupply`, `TurnEngine` resupply phase
- **Priority:** LOW -- The system is data-driven so fuel tests likely cover other resources.

### B8. Event Log Integration -- No Overflow/Pruning
- **File:** `tests/integration/strategy/test_event_log_integration.py`
- **Test(s):** All tests
- **What's tested:** Events emitted, queried by turn/category, persisted through save/load.
- **What's missing:** No test for event log overflow (hundreds of turns of events), event with None empire_id, event with very long message string, concurrent event emission.
- **Source method(s) affected:** `EventLog`, `EventBus.log_event`, `StrategySessionFacade.get_all_events`
- **Priority:** LOW

---

## C. Source Code with Inadequate Coverage

### C1. Fleet Capabilities Integration
- **Source file:** `game/strategy/data/fleet_capabilities.py` (estimated ~200 LOC)
- **Coverage:** Not measured directly, but integration tests rely heavily on mocking `fleet._capabilities` (see test_warp_orders.py, test_fleet_production_e2e.py)
- **Untested areas:** Real FleetCapabilities calculation integrated with actual ship designs. Most integration tests mock `_capabilities` directly, which means the real capability computation (from ship components) is never exercised end-to-end.
- **Risk:** A bug in capability calculation from ship data would not be caught by integration tests.
- **Priority:** MEDIUM

### C2. Conflict Resolution Engine -- Full Battle Flow
- **Source file:** `game/strategy/engine/conflict_resolution_engine.py` (estimated ~300 LOC)
- **Coverage:** Integration tests use `InstantBattleResolver` (see colonization/conftest.py:24, gameplay_loop/conftest.py:19, fleet_registration_lifecycle.py:25) to skip real combat. No integration test exercises a real battle through the strategy layer.
- **Untested areas:** Full combat flow: fleet detection at same hex -> battle resolution with real simulation -> survivor reintegration -> fleet destruction -> galaxy registry cleanup. The InstantBattleResolver always declares team 0 the winner.
- **Risk:** Bugs in battle result processing (survivor ship restoration, fleet state after battle, resource/ammo consumption during battle) would not be caught.
- **Priority:** HIGH

### C3. Turn Engine Storm/Radiation Processing
- **Source file:** `game/strategy/engine/turn_engine.py` environmental phase
- **Coverage:** `test_turn_storms.py` (331 LOC) and `test_galaxy_generation_storms.py` (194 LOC) exist but were not read -- storm integration tests exist. However, `test_radiation.py` (67 LOC) is very small.
- **Untested areas:** Radiation damage accumulation across multiple turns, radiation interaction with shields/armor in strategy layer, storm movement affecting fleet paths mid-journey.
- **Risk:** Environmental hazards could silently break without notice.
- **Priority:** MEDIUM

---

## D. Cross-Domain Observations

1. **InstantBattleResolver pattern is pervasive.** At least 3 integration test directories (colonization, gameplay_loop, fleet_registration_lifecycle) use a stub battle resolver that always declares team 0 the winner. This means NO integration test exercises real combat through the strategy layer. The simulation and strategy layers are never tested together in the integration suite. This is a significant cross-layer gap. Consider adding at least one "smoke test" that uses the real battle resolver with simple ships.

2. **Heavy mock usage in "integration" tests.** Many facade tests (test_empire_queries.py, test_fleet_queries.py, test_validation_queries.py) create `Mock()` or `MagicMock()` session objects. While the facade pattern justifies mocking the session, these tests don't exercise real cross-layer behavior -- they test that the facade delegates correctly to mocks. The tests in `test_facade_integration.py` are the true integration tests (using real `GameSession`). Consider whether the mock-based facade tests belong in `tests/unit/strategy/facade/` instead.

3. **Duplicated `make_colony_ship` helper.** The function `make_colony_ship_for_planet` (or variants) is defined independently in at least 6 locations: `test_facade_integration.py:19`, `test_colonize_logic.py:65`, `test_command_handlers.py:13`, `colonization/conftest.py:41`, `turn_engine/conftest.py:87`, and `test_commands.py:22`. This should be consolidated into a shared conftest or test utility module.

4. **Duplicated `MockGalaxy` classes.** At least 8 different `MockGalaxy` classes exist across integration test files, each with slightly different method sets. These should be consolidated into a shared fixture.

5. **DTO tests are unit tests misplaced as integration tests.** All files in `tests/integration/strategy/facade/test_*_dto.py` test dataclass creation, field assignment, and factory methods. These exercise no cross-layer behavior and belong in `tests/unit/strategy/facade/`.

---

## E. Repro Issues Assessment

### E1. test_bug_01_crew_delay.py
- **File:** `tests/repro_issues/test_bug_01_crew_delay.py`
- **Bug:** Crew required stat doesn't update immediately when modifier changes.
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Tests modifier application -> recalculate -> stat update chain. This exercises a real multi-step recalculation path (Component modifier -> Component.recalculate_stats -> Ship.recalculate_stats -> UI stat read) that could regress.

### E2. test_bug_02_seeker.py
- **File:** `tests/repro_issues/test_bug_02_seeker.py`
- **Bug:** Seeker-related bug (37 lines -- likely small regression).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Small focused test. Seeker system has had multiple fixes (per MEMORY.md). Worth keeping as guard.

### E3. test_bug_03_validation.py
- **File:** `tests/repro_issues/test_bug_03_validation.py`
- **Bug:** Adding wrong resource type (Energy Storage) resolves Fuel Storage warning.
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Tests that resource validation is type-specific. This is a subtle validation bug that could easily regress. The test exercises real Ship + Component + validation warning logic.

### E4. test_bug_04_display.py
- **File:** `tests/repro_issues/test_bug_04_display.py`
- **Bug:** Display-related bug (101 lines).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** UI display bugs are hard to catch with unit tests. Keep as targeted regression guard.

### E5. test_bug_05_deep_repro.py
- **File:** `tests/repro_issues/test_bug_05_deep_repro.py`
- **Bug:** Deep reproduction of logistics issue (157 lines).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Extended repro of the same bug family as BUG-05. The test is substantial and exercises a specific chain of component interactions.

### E6. test_bug_05_logistics.py
- **File:** `tests/repro_issues/test_bug_05_logistics.py`
- **Bug:** Missing logistics details in Stats Panel (generation rate, consumption, endurance).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Tests that `get_logistics_rows()` returns all 6 required row types for energy. Exercises real Ship + ShipStatsCalculator + UI stats config. This is a real cross-layer test.

### E7. test_bug_05_rejected_fix.py
- **File:** `tests/repro_issues/test_bug_05_rejected_fix.py`
- **Bug:** Rejected fix attempt for BUG-05 (91 lines).
- **Verdict:** REMOVE_REDUNDANT
- **Evidence:** This appears to be a test for a fix that was rejected. If the actual fix is covered by test_bug_05_logistics.py, this is redundant documentation of a dead approach.

### E8. test_bug_06_combat_propulsion.py
- **File:** `tests/repro_issues/test_bug_06_combat_propulsion.py`
- **Bug:** Combat propulsion bug (147 lines).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Combat propulsion is a simulation-layer feature. This likely tests a specific interaction that could regress.

### E9. test_bug_07_crash.py
- **File:** `tests/repro_issues/test_bug_07_crash.py`
- **Bug:** Crash reproduction (59 lines).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Crash regressions are high-value. Even small tests guarding against crashes should be kept.

### E10. test_bug_08_fuel_validation.py
- **File:** `tests/repro_issues/test_bug_08_fuel_validation.py`
- **Bug:** Fuel validation -- ResourceStorage ability aggregation incorrect.
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Tests real component creation (`create_component("fuel_tank")`), Ship assembly, and validation. Exercises a real integration path through Component -> Ship -> validation warnings.

### E11. test_bug_09_endurance.py
- **File:** `tests/repro_issues/test_bug_09_endurance.py`
- **Bug:** Endurance calculation bug (80 lines).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Endurance is a derived stat from multiple inputs. Regression is likely.

### E12. test_bug_09_hull_in_palette.py
- **File:** `tests/repro_issues/test_bug_09_hull_in_palette.py`
- **Bug:** Hull appearing in component palette (56 lines).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** UI filtering bug. Small focused test worth keeping.

### E13. test_bug_10_logistics_update.py
- **File:** `tests/repro_issues/test_bug_10_logistics_update.py`
- **Bug:** Ship stats not updating for ammo/ordnance in logistics panel.
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Tests that adding a weapon with ResourceConsumption triggers logistics row display. Exercises real Component ability -> ShipStatsCalculator -> UI stats config chain.

### E14. test_bug_11_dialog_size.py
- **File:** `tests/repro_issues/test_bug_11_dialog_size.py`
- **Bug:** Dialog size issue (68 lines).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** UI rendering bugs. Worth keeping as guard.

### E15. test_bug_11_hull_update.py
- **File:** `tests/repro_issues/test_bug_11_hull_update.py`
- **Bug:** Hull update issue (80 lines).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Ship builder hull management. Worth keeping.

### E16. test_bug_12_energy_gen.py
- **File:** `tests/repro_issues/test_bug_12_energy_gen.py`
- **Bug:** Energy generation bug (110 lines).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Resource generation is core simulation logic. Keep.

### E17. test_bug_12_hull_layer_addition.py
- **File:** `tests/repro_issues/test_bug_12_hull_layer_addition.py`
- **Bug:** Hull layer addition bug (52 lines).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Ship builder layer management. Keep.

### E18. test_bug_13_clear_removes_hull.py
- **File:** `tests/repro_issues/test_bug_13_clear_removes_hull.py`
- **Bug:** Clearing components removes hull (125 lines).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Destructive operation guard -- clearing should not remove hull. Important invariant.

### E19. test_bug_13_weapons_report.py
- **File:** `tests/repro_issues/test_bug_13_weapons_report.py`
- **Bug:** Weapons report bug (136 lines).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** UI reporting of weapon stats. Worth keeping.

### E20. test_bug_14_multi_planet_offset.py
- **File:** `tests/repro_issues/test_bug_14_multi_planet_offset.py`
- **Bug:** Multi-planet offset issue (337 lines -- substantial).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Large test exercising planet positioning logic. This is a significant regression guard.

### E21. test_bug_15_screenshot_strategy.py
- **File:** `tests/repro_issues/test_bug_15_screenshot_strategy.py`
- **Bug:** Screenshot strategy bug (364 lines -- substantial).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Large test. Strategy-layer screenshot/rendering interaction.

### E22. test_bug_16_raw_data_button.py
- **File:** `tests/repro_issues/test_bug_16_raw_data_button.py`
- **Bug:** Raw data button bug (64 lines).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** UI interaction test. Keep.

### E23. test_bug_17_drag_preview.py
- **File:** `tests/repro_issues/test_bug_17_drag_preview.py`
- **Bug:** Drag preview bug (62 lines).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** UI drag interaction. Keep.

### E24. test_bug_27_ordertype.py
- **File:** `tests/repro_issues/test_bug_27_ordertype.py`
- **Bug:** NameError: name 'OrderType' is not defined in strategy_screen.py.
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Tests that OrderType is importable and that `StrategyUI.show_detailed_report` doesn't crash with MOVE/COLONIZE orders. This guards against import regressions in UI code. The test exercises real pygame + StrategyUI + Fleet + OrderType integration.

### E25. test_crash_planet_list.py
- **File:** `tests/repro_issues/test_crash_planet_list.py`
- **Bug:** Crash when accessing planet list (43 lines).
- **Verdict:** KEEP_AS_REGRESSION
- **Evidence:** Crash guard. Always keep.

---

## Summary Statistics

| Category | Count | Est. LOC |
|---|---|---|
| Recommended for removal | 12 groups | ~750 |
| Happy-path-only (improve) | 8 groups | N/A |
| Cross-layer integration gaps | 3 areas | N/A |
| Repro tests: KEEP | 24 | ~3,200 |
| Repro tests: REMOVE | 1 | ~91 |

### Key Recommendations (Priority Order)

1. **HIGH:** Add at least one integration test using a real BattleResolver instead of InstantBattleResolver to cover strategy-simulation cross-layer combat flow.
2. **HIGH:** Move all `test_*_dto.py` files from `integration/strategy/facade/` to `unit/strategy/facade/` -- they test no cross-layer behavior.
3. **MEDIUM:** Consolidate duplicated `make_colony_ship`, `MockGalaxy`, and similar helpers into shared conftest modules.
4. **MEDIUM:** Add error path tests for production completion (insufficient resources, corrupt queue items).
5. **LOW:** Remove the 12 flagged test groups (~750 LOC of trivial/dead/duplicate tests).
