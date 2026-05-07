# Test Review Report: Fleet Orders + Production Cross-Domain Dedup

## Scope
- Source files reviewed: [13 files, 5472 LOC total]
  - `game/strategy/engine/order_processor.py` (779 lines)
  - `game/strategy/engine/action_execution_engine.py` (215 lines)
  - `game/strategy/engine/production_engine.py` (605 lines)
  - `game/strategy/engine/production_spawner.py` (412 lines)
  - `game/strategy/engine/production_math.py` (39 lines)
  - `game/strategy/engine/command_handlers.py` (1062 lines)
  - `game/strategy/engine/commands.py` (416 lines)
  - `game/strategy/engine/fleet_movement_engine.py` (291 lines)
  - `game/strategy/data/order_types.py` (171 lines)
  - `game/strategy/data/order_serializer.py` (235 lines)
  - `game/strategy/engine/empire_economy_calculator.py` (251 lines)
  - `game/ui/panels/planet_report_panel.py` (557 lines)
  - `game/strategy/data/build_queue_source.py` (439 lines)
- Test files reviewed: [29 files, 8623 LOC total]
  - `tests/unit/strategy/test_fleet_order_processor.py` (615 lines)
  - `tests/unit/strategy/test_fleet_orders_logic.py` (140 lines)
  - `tests/unit/strategy/test_advanced_fleet_orders.py` (349 lines)
  - `tests/unit/strategy/engine/test_fleet_order_transfer.py` (389 lines)
  - `tests/unit/strategy/engine/test_transfer_order.py` (495 lines)
  - `tests/unit/strategy/data/test_fleet_order_resolution.py` (414 lines)
  - `tests/unit/strategy/engine/test_build_order_processor.py` (150 lines)
  - `tests/unit/strategy/engine/test_build_order_command_handler.py` (213 lines)
  - `tests/unit/strategy/engine/test_action_execution_engine.py` (520 lines)
  - `tests/unit/strategy/engine/test_movement_build_blocking.py` (123 lines)
  - `tests/integration/strategy/test_resource_transfer.py` (188 lines)
  - `tests/integration/gameplay_loop/test_fleet_operations.py` (263 lines)
  - `tests/integration/strategy/test_fleet_join_redirect.py` (212 lines)
  - `tests/integration/save_load/test_roundtrip_orders.py` (156 lines)
  - `tests/integration/strategy/production/test_fleet_save_load.py` (194 lines)
  - `tests/integration/strategy/production/test_fleet_production_e2e.py` (440 lines)
  - `tests/integration/strategy/production/test_completion.py` (489 lines)
  - `tests/integration/strategy/production/test_queue.py` (194 lines)
  - `tests/integration/strategy/test_production_rates.py` (361 lines)
  - `tests/unit/strategy/engine/test_production_math.py` (88 lines)
  - `tests/unit/strategy/engine/test_production_refactor.py` (511 lines)
  - `tests/unit/strategy/engine/test_production_repro.py` (232 lines)
  - `tests/unit/strategy/engine/test_production_spawner_staging_yard.py` (111 lines)
  - `tests/unit/strategy/data/test_production_rates.py` (54 lines)
  - `tests/unit/ui/panels/test_compute_planet_production.py` (130 lines)
  - `tests/unit/strategy/production_engine/test_tick_consumption.py` (608 lines)
  - `tests/unit/strategy/production_engine/test_spawning.py` (184 lines)
  - `tests/unit/strategy/production_engine/test_resource_costs.py` (122 lines)
  - `tests/unit/strategy/engine/test_empire_economy_calculator.py` (678 lines)
- Coverage data referenced: no

## Summary
- Test files reviewed: 29
- Source files reviewed: 13
- Tests flagged for removal: 7 (estimated LOC: 355)
- Tests flagged as happy-path-only: 2
- Source files with inadequate coverage: 0

## A. Tests Recommended for Removal

### A1. Transfer Order - Duplicate Load/Unload Tests (Mock vs Real)
- **File:** `tests/unit/strategy/engine/test_fleet_order_transfer.py`
- **Test(s):** `TestExecuteLoad` (5 tests, lines 201-284), `TestExecuteUnload` (5 tests, lines 294-362)
- **Reason:** DUPLICATE_OF:`tests/unit/strategy/engine/test_transfer_order.py::TestOrderProcessorTransfer`
- **Confidence:** HIGH
- **Evidence:** `test_fleet_order_transfer.py::TestExecuteLoad::test_load_passengers_from_colony` (line 204) tests the same behavior as `test_transfer_order.py::TestOrderProcessorTransfer::test_process_transfer_load_passengers_from_colony` (line 167). The former uses fully mocked fleet.resources (mock returns canned values), the latter uses real Fleet/Ship objects with actual cargo calculation. The real-object tests in `test_transfer_order.py` are strictly more thorough and exercise real code paths. The mock-only tests in `test_fleet_order_transfer.py` duplicate: load cap by capacity (lines 221-235 vs 234-262), load cap by population (lines 237-252 vs 234-262), unload cap by cargo (lines 308-317 vs 205-231), unload-all (lines 319-327 vs 264-292), load with species (lines 253-270 vs 337-376), unload with species (lines 345-362 vs 378-415). All 10 tests have exact behavioral equivalents in the real-object file.
- **Estimated LOC saved:** 162

### A2. Transfer Validation Duplicates (Mock vs Real)
- **File:** `tests/unit/strategy/engine/test_fleet_order_transfer.py`
- **Test(s):** `TestProcessTransfer::test_transfer_no_order_returns_failure`, `test_transfer_wrong_order_type_returns_failure`, `test_transfer_invalid_params_returns_failure`; `TestTransferValidation::test_transfer_validates_direction`, `test_transfer_load_passengers`, `test_transfer_unload_passengers` (lines 93-195)
- **Reason:** DUPLICATE_OF:`tests/unit/strategy/engine/test_transfer_order.py::TestOrderProcessorTransfer`
- **Confidence:** MEDIUM
- **Evidence:** `test_fleet_order_transfer.py` lines 93-99 test "no order returns failure" by calling `processor.process_transfer()` with mock fleet returning None order. `test_transfer_order.py` line 167 tests the full load flow with real objects. The validation tests at lines 124-138 (direction validation) are very thin mocked assertions that are implicitly covered by the real-object tests' success/failure paths. However, the 3 negative-path tests (no order, wrong type, invalid params at lines 93-118) are NOT duplicated elsewhere and should be kept. The 3 validation/execution tests at lines 140-195 are duplicates.
- **Estimated LOC saved:** 56

### A3. TransferResult/JoinFleetResult/ColonizeResult Dataclass Tests
- **File:** `tests/unit/strategy/test_fleet_order_processor.py`
- **Test(s):** `TestOrderResult::test_join_fleet_result_has_required_fields`, `test_colonize_result_has_required_fields`, `test_colonize_result_defaults` (lines 459-487)
- **Reason:** TRIVIAL_CONSTANT
- **Confidence:** HIGH
- **Evidence:** These tests instantiate dataclasses and assert their fields match the constructor args (line 467: `result = JoinFleetResult(merged=True, cancelled=False); assert result.merged is True`). Dataclass field access is guaranteed by Python. These 3 tests verify no logic -- just that `@dataclass` works. The `TransferResult` tests at `test_fleet_order_transfer.py` lines 369-389 are the same pattern.
- **Estimated LOC saved:** 35

### A4. OrderProcessor Creation Test
- **File:** `tests/unit/strategy/test_fleet_order_processor.py`
- **Test(s):** `TestOrderProcessorCreation::test_order_processor_can_be_created` (lines 60-69)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Line 67: `processor = OrderProcessor()` then `assert processor is not None`. This is a scaffold test that verifies only that a class can be instantiated. Every other test in the file already does this.
- **Estimated LOC saved:** 10

### A5. BUILD Order Movement Blocking - Duplicate in E2E
- **File:** `tests/integration/strategy/production/test_fleet_production_e2e.py`
- **Test(s):** `TestFleetProductionE2E::test_e2e_fleet_with_build_order_cannot_move`, `test_e2e_fleet_without_build_order_can_move` (lines 210-260)
- **Reason:** DUPLICATE_OF:`tests/unit/strategy/engine/test_movement_build_blocking.py`
- **Confidence:** MEDIUM
- **Evidence:** `test_fleet_production_e2e.py` lines 210-235 test "fleet with BUILD order not in movements" by calling `movement_engine.collect_movements()` and checking fleet not in results. `test_movement_build_blocking.py` lines 47-57 test identical behavior with identical assertions. The E2E file even uses the same `FleetMovementEngine()` directly rather than going through TurnEngine, so it is not actually testing a higher abstraction layer. The unit test file additionally tests mixed fleets (lines 93-107) and BUILD-then-MOVE queuing (lines 78-91). The two E2E tests add no coverage beyond the 4 unit tests.
- **Estimated LOC saved:** 51

### A6. Fleet Save/Load - Duplicated Between Two Files
- **File:** `tests/integration/strategy/production/test_fleet_production_e2e.py`
- **Test(s):** `TestFleetProductionE2E::test_e2e_save_load_preserves_build_state` (lines 262-292)
- **Reason:** DUPLICATE_OF:`tests/integration/strategy/production/test_fleet_save_load.py::TestFleetConstructionQueueSaveLoad::test_roundtrip_preserves_full_fleet_state`
- **Confidence:** HIGH
- **Evidence:** Both tests serialize a Fleet with BUILD order + construction_queue, deserialize, and assert queue/orders are preserved. `test_fleet_production_e2e.py` line 267 creates `Fleet("test_fleet", 0, HexCoord(10, -5))`, adds BUILD order and 2 queue items, serializes, deserializes, checks `restored_fleet.is_building is True` and queue length == 2. `test_fleet_save_load.py` line 130 does the exact same thing with 3 queue items + 2 ships, checking the same properties. The dedicated save/load file is more thorough (6 tests covering empty queue, is_building, etc.).
- **Estimated LOC saved:** 31

### A7. Production Rates JSON - Duplicate Testing
- **File:** `tests/unit/strategy/data/test_production_rates.py`
- **Test(s):** `TestProductionRatesJson` (all 7 tests, lines 1-54)
- **Reason:** DUPLICATE_OF:`tests/integration/strategy/test_production_rates.py::TestProductionRatesFromJSON`
- **Confidence:** MEDIUM
- **Evidence:** `test_production_rates.py` (unit) lines 19-54 load `production_rates.json` and assert: both yard types present, all 5 resources, planetary_yard rate == 2000, space_shipyard rate == 30000, all positive. `test_production_rates.py` (integration) lines 290-318 call `get_default_production_rates()` and assert: planetary_yard has all 5 resources at 2000, space_shipyard at 30000, unknown returns empty. The integration file tests the same data through the actual API function. The unit file tests raw JSON loading, which is a valid but thin layer -- the integration tests effectively supersede them since any JSON loading failure would also fail the integration tests. However, the unit tests provide slightly faster failure isolation, so removal is optional.
- **Estimated LOC saved:** 10 (if removed)

## B. Tests That Are Happy-Path-Only
(N/A for dedup agent -- noting observations made during analysis)

### B1. Transfer Order Validation Gaps
- **File:** `tests/unit/strategy/engine/test_fleet_order_transfer.py`
- **Observation:** `TestTransferValidation` only tests invalid direction (1 test). Does not test: invalid cargo_type, negative amount, planet not at fleet location, planet owned by different empire, fleet with no cargo capacity. The real-object tests in `test_transfer_order.py` cover partial amount and species-specific cases but also miss invalid cargo type and cross-empire validation.

### B2. Build Order Processing - No Negative Tests
- **File:** `tests/unit/strategy/engine/test_build_order_processor.py`
- **Observation:** All 7 tests verify correct behavior (queue persists, auto-completes, queued orders remain). No test verifies behavior when construction_queue is malformed, when fleet has no shipyard capability, or when resources are exhausted mid-build at the OrderProcessor level (these are tested in `test_production_refactor.py` and `test_tick_consumption.py`, but the build order processor layer itself lacks negative-path coverage).

## C. Source Code with Inadequate Coverage
(N/A for dedup agent)

## D. Cross-Domain Observations

### D1. Transfer Tests Are Split Across 3 Files With Different Abstraction Levels
The transfer order system has tests in:
1. `tests/unit/strategy/engine/test_fleet_order_transfer.py` -- Mock-heavy unit tests of OrderProcessor._execute_load/_execute_unload (PROJ-119)
2. `tests/unit/strategy/engine/test_transfer_order.py` -- Real-object tests of OrderProcessor.process_transfer + command dispatch (PROJ-68)
3. `tests/integration/strategy/test_resource_transfer.py` -- Integration tests for resource load/unload with real Fleet/Planet (Phase 7)

Files 1 and 2 overlap significantly (see A1, A2 above). File 3 tests resources (metals, fuel) rather than passengers, providing unique coverage. Recommendation: consolidate files 1 and 2 into a single file, keeping the real-object tests from file 2 and the 3 negative-path validation tests from file 1.

### D2. JOIN_FLEET Tested in 4 Different Places
JOIN_FLEET merge behavior is verified in:
1. `test_fleet_order_processor.py::TestJoinFleetProcessing` (4 mock tests)
2. `test_fleet_order_processor.py::TestInstantOrderProcessing` (4 mock tests)
3. `test_advanced_fleet_orders.py::TestAdvancedFleetOrders::test_join_fleet_execution` (1 real-object test)
4. `tests/integration/gameplay_loop/test_fleet_operations.py::TestFleetMerge` (2 integration tests)
5. `tests/integration/strategy/test_fleet_join_redirect.py` (full redirect/cancel lifecycle)

These are NOT duplicates -- they test genuinely different concerns:
- File 1 tests OrderProcessor.process_join_fleet() with mocks (unit)
- File 2 tests OrderProcessor.process_instant_orders() with mocks (unit)
- File 3 tests with real Fleet/Empire objects via process_instant_orders (higher fidelity)
- File 4 tests through TurnEngine.process_turn() (full integration)
- File 5 tests pursuer tracking redirect/cancel on merge/destruction

However, files 1 and 3 both test "co-located merge succeeds" and "non-co-located merge fails" -- the real-object tests in file 3 are redundant with the mock tests in file 1 for these two behaviors. The mock tests run faster and isolate the unit; the real-object tests add marginal confidence. Not flagged for removal due to low LOC cost (~25 lines).

### D3. Production Engine Tests Well-Layered But _make_shipyard Duplicated
The helper function `_make_shipyard()` is defined independently in 5 different test files:
- `tests/integration/strategy/production/test_completion.py` line 28
- `tests/integration/strategy/production/test_queue.py` line 29
- `tests/unit/strategy/production_engine/test_tick_consumption.py` line 79
- `tests/unit/strategy/production_engine/test_spawning.py` line 14
- `tests/integration/strategy/production/test_fleet_production_e2e.py` (inline)

This is code duplication in test infrastructure, not test duplication. Recommendation: extract `_make_shipyard()` into `tests/integration/strategy/production/conftest.py` (which already exists and has `create_shipyard()` at line 120, but tests don't use it).

### D4. compute_planet_production Tested in 2 Places
- `tests/unit/ui/panels/test_compute_planet_production.py` (5 tests, 130 lines) -- Tests the `compute_planet_production()` function
- `tests/unit/strategy/engine/test_empire_economy_calculator.py` (12+ tests, 678 lines) -- Tests `EmpireEconomyCalculator.calculate()` which internally calls production aggregation

These are NOT duplicates. `compute_planet_production` is a UI utility for displaying per-planet production rates. `EmpireEconomyCalculator` is a strategy-layer aggregator that computes empire-wide production, expenses, and net resources. They share the same underlying harvester-scanning logic but serve different consumers. Both files also test registry fallback (BUG-86/87) independently -- the calculator file at line 357 and the compute file at line 54. The registry fallback tests are borderline duplicates but test through different entry points.

## E. Dedup Map

### E1. Transfer Load/Unload (Passengers)
- **Behavior:** Loading passengers from colony to fleet; unloading passengers to colony
- **Test locations:**
  - `test_fleet_order_transfer.py:TestExecuteLoad:test_load_passengers_from_colony` (line 204) -- mock-only
  - `test_fleet_order_transfer.py:TestExecuteUnload:test_unload_passengers_to_colony` (line 294) -- mock-only
  - `test_transfer_order.py:TestOrderProcessorTransfer:test_process_transfer_load_passengers_from_colony` (line 167) -- real objects
  - `test_transfer_order.py:TestOrderProcessorTransfer:test_process_transfer_unload_passengers_to_colony` (line 200) -- real objects
- **Recommendation:** Remove mock-only tests in `test_fleet_order_transfer.py` (TestExecuteLoad, TestExecuteUnload). Keep real-object tests in `test_transfer_order.py`.

### E2. Transfer Capacity Capping
- **Behavior:** Transfer amount capped by fleet cargo capacity / colony population
- **Test locations:**
  - `test_fleet_order_transfer.py:TestExecuteLoad:test_load_capped_by_capacity` (line 221)
  - `test_fleet_order_transfer.py:TestExecuteLoad:test_load_capped_by_colony_population` (line 237)
  - `test_transfer_order.py:TestOrderProcessorTransfer:test_transfer_partial_amount` (line 234)
- **Recommendation:** Remove mock tests. Real-object test covers both caps.

### E3. Transfer All (amount=0)
- **Behavior:** Amount=0 means transfer all available
- **Test locations:**
  - `test_fleet_order_transfer.py:TestExecuteLoad:test_load_zero_amount_loads_all_capacity` (line 272)
  - `test_fleet_order_transfer.py:TestExecuteUnload:test_unload_zero_amount_unloads_all` (line 319)
  - `test_transfer_order.py:TestOrderProcessorTransfer:test_transfer_all_when_amount_zero` (line 264)
- **Recommendation:** Remove mock tests. Real-object test covers both directions.

### E4. Transfer Species-Specific
- **Behavior:** Load/unload specific species
- **Test locations:**
  - `test_fleet_order_transfer.py:TestExecuteLoad:test_load_with_species_id` (line 253)
  - `test_fleet_order_transfer.py:TestExecuteUnload:test_unload_with_species_id` (line 345)
  - `test_transfer_order.py:TestOrderProcessorTransfer:test_process_transfer_species_specific_load` (line 337)
  - `test_transfer_order.py:TestOrderProcessorTransfer:test_process_transfer_species_specific_unload` (line 378)
- **Recommendation:** Remove mock tests. Real-object tests cover both load and unload with species.

### E5. JOIN_FLEET Co-Located Merge
- **Behavior:** JOIN_FLEET merges when fleets at same location
- **Test locations:**
  - `test_fleet_order_processor.py:TestJoinFleetProcessing:test_process_join_fleet_merges_at_same_location` (line 80) -- mock
  - `test_fleet_order_processor.py:TestInstantOrderProcessing:test_process_instant_join_fleet_at_location` (line 356) -- mock
  - `test_advanced_fleet_orders.py:TestAdvancedFleetOrders:test_join_fleet_execution` (line 239) -- real objects
  - `test_fleet_operations.py:TestFleetMerge:test_join_fleet_merges_ships` (line 99) -- integration
- **Recommendation:** Genuinely different concerns. `test_process_join_fleet_merges_at_same_location` tests `process_join_fleet()`. `test_process_instant_join_fleet_at_location` tests `process_instant_orders()`. `test_join_fleet_execution` tests with real Fleet/Empire objects. `test_join_fleet_merges_ships` tests through TurnEngine. Keep all -- different layers.

### E6. JOIN_FLEET Non-Co-Located Wait
- **Behavior:** JOIN_FLEET waits when not at target location
- **Test locations:**
  - `test_fleet_order_processor.py:TestJoinFleetProcessing:test_process_join_fleet_fails_at_different_location` (line 100)
  - `test_fleet_order_processor.py:TestInstantOrderProcessing:test_process_instant_join_fleet_not_at_location` (line 383)
  - `test_fleet_order_processor.py:TestInstantOrderProcessing:test_process_instant_join_fleet_preserves_order_when_not_colocated` (line 409)
  - `test_advanced_fleet_orders.py:TestAdvancedFleetOrders:test_join_fleet_waits_when_not_colocated` (line 276)
  - `test_fleet_operations.py:TestFleetMerge:test_join_fleet_requires_same_location` (line 132)
- **Recommendation:** Genuinely different concerns. Different methods tested at different layers. Keep all.

### E7. BUILD Order Movement Blocking
- **Behavior:** Fleet with BUILD order cannot move
- **Test locations:**
  - `test_movement_build_blocking.py:TestMovementBlockingForBuildOrder:test_fleet_with_build_order_not_in_movement_collection` (line 47)
  - `test_movement_build_blocking.py:TestMovementBlockingForBuildOrder:test_fleet_with_build_then_move_does_not_move` (line 78)
  - `test_movement_build_blocking.py:TestMovementBlockingForBuildOrder:test_mixed_fleets_only_non_building_move` (line 93)
  - `test_fleet_production_e2e.py:TestFleetProductionE2E:test_e2e_fleet_with_build_order_cannot_move` (line 210)
  - `test_fleet_production_e2e.py:TestFleetProductionE2E:test_e2e_fleet_without_build_order_can_move` (line 237)
- **Recommendation:** Remove the 2 E2E tests (A5 above). They call the same `FleetMovementEngine()` directly -- not a higher abstraction -- and are pure duplicates of the unit tests.

### E8. Fleet Construction Queue Save/Load
- **Behavior:** Fleet with BUILD order + construction_queue survives serialization round-trip
- **Test locations:**
  - `test_fleet_production_e2e.py:TestFleetProductionE2E:test_e2e_save_load_preserves_build_state` (line 262)
  - `test_fleet_save_load.py:TestFleetConstructionQueueSaveLoad:test_roundtrip_preserves_full_fleet_state` (line 130)
  - `test_fleet_save_load.py:TestFleetConstructionQueueSaveLoad:test_save_game_with_build_order_and_load_restores` (line 103)
  - `test_fleet_save_load.py:TestFleetConstructionQueueSaveLoad:test_is_building_preserved_after_roundtrip` (line 162)
- **Recommendation:** Remove the E2E duplicate (A6 above). The dedicated save/load file has 6 tests covering all edge cases.

### E9. Production Rates JSON Data
- **Behavior:** production_rates.json has correct structure and values
- **Test locations:**
  - `tests/unit/strategy/data/test_production_rates.py:TestProductionRatesJson` (7 tests, lines 1-54) -- raw JSON
  - `tests/integration/strategy/test_production_rates.py:TestProductionRatesFromJSON` (3 tests, lines 290-318) -- via API
- **Recommendation:** Borderline. Unit tests validate raw JSON schema, integration tests validate through `get_default_production_rates()`. If forced to choose, keep integration tests. But 54 LOC is low cost for additional isolation.

### E10. Production Ship Spawning
- **Behavior:** Completed ship production creates a new fleet
- **Test locations:**
  - `tests/unit/strategy/production_engine/test_spawning.py:TestShipSpawning:test_spawn_ship_creates_fleet` (line 47) -- unit with mocks
  - `tests/integration/strategy/production/test_completion.py:TestProductionCompletion:test_production_completion` (line 49) -- integration via TurnEngine
  - `tests/integration/strategy/production/test_completion.py:TestShipSpawning:test_process_production_ship_spawns` (line 202) -- integration via TurnEngine
  - `tests/integration/strategy/production/test_fleet_production_e2e.py:TestFleetProductionE2E:test_e2e_fleet_with_yard_builds_ship_that_spawns_in_fleet` (line 124) -- fleet E2E
- **Recommendation:** Genuinely different concerns. Unit tests mock DesignLibrary/ShipInstance to test spawner in isolation. Integration tests verify full pipeline through TurnEngine (100-tick processing). Fleet E2E tests fleet-specific construction (cargo-based). Keep all.

### E11. Production Resource Consumption Per Tick
- **Behavior:** Each tick deducts resources from stockpile at production rate
- **Test locations:**
  - `tests/unit/strategy/production_engine/test_tick_consumption.py:TestTickConsumption` (12 tests) -- unit
  - `tests/unit/strategy/engine/test_production_refactor.py:TestProductionEngineRefactor` (2 tests) -- unit
- **Recommendation:** Genuinely different concerns. `test_tick_consumption.py` tests the public `process_construction_tick()` API with real stockpile deduction. `test_production_refactor.py` tests the internal `_process_queue_tick_dynamic()` with mock colonies, focusing on dynamic limiting-resource logic and carry-over capacity. Different methods, different concerns. Keep all.

### E12. Registry Fallback for Harvester Production
- **Behavior:** Components without inline abilities resolve via registry lookup
- **Test locations:**
  - `tests/unit/ui/panels/test_compute_planet_production.py:TestComputePlanetProduction:test_planet_with_registry_lookup` (line 54) -- UI utility
  - `tests/unit/strategy/engine/test_empire_economy_calculator.py:TestEmpireEconomyCalculator:test_registry_fallback_for_colony_production` (line 351) -- economy aggregator
- **Recommendation:** Genuinely different concerns. Same underlying logic but tested through different entry points serving different consumers (UI panel vs economy calculator). Keep both.
