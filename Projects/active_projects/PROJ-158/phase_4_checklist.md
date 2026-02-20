# Phase 4: Rewrite Integration Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-158 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rewrite integration tests that tested valuable end-to-end behavior (completion → spawning, shipyard gating, queue ordering) to use the live tick-based API.

**Key Pattern for Rewriting:**
1. Replace `engine.process_production([empire], save_path=dir)` with either:
   - `for tick in range(1, 101): engine.production_engine.process_construction_tick(tick, [empire], galaxy, save_path=dir)` (one turn of ticks)
   - OR use a `TurnEngine` and call `engine.process_turn([empire], galaxy)` (full turn including all phases)
2. All queue items must have `total_cost` and `resources_consumed` fields
3. Empire must have sufficient resources in `resource_pool`
4. For items that should complete in 1 turn: set `total_cost` low enough (e.g., `{"Metals": 100}` completes in 5 ticks at 20/tick rate)

---

## Tasks

### Task 4.1: Rewrite `test_complex_workflow.py` [Medium]
**File:** `tests/integration/test_complex_workflow.py`
**Tests:** `pytest tests/integration/test_complex_workflow.py -q`

- [ ] Update `empire_with_colony` fixture: give empire starting resources (e.g., `{"Metals": 100000, "Organics": 100000}`)
- [ ] Create helper `_process_one_turn(engine, empires, galaxy=None, save_path=None)` that loops 100 ticks of `process_construction_tick()`
- [ ] `test_full_build_workflow`: Replace `planet.add_production()` with direct queue item (with `total_cost`). Use turn helper. Item with `turns_remaining=2` should have `total_cost` requiring ~200 ticks (e.g., `{"Metals": 4000}` at 20/tick = 200 ticks = 2 turns). Assert after turn 1: item still in queue, `resources_consumed > 0`. After turn 2: queue empty, facility built.
- [ ] `test_shipyard_enables_ship_building`: Build shipyard via tick processing (1-turn item). Then add ship to facility queue with proper fields. Process ticks.
- [ ] `test_multiple_complexes_on_planet`: Queue 3 items that each complete in 1 turn. Process 3 turns.
- [ ] `test_shipyard_detection_with_multiple_facilities`: Same pattern — build facilities via tick processing.
- [ ] `test_non_operational_shipyard_not_detected`: Build shipyard via tick processing, then damage it.
- [ ] Verify all tests pass (both previously passing and rewritten)

**Notes:** These tests currently use `TurnEngine()` directly. The tick processing is on `ProductionEngine`, which `TurnEngine` holds as `self.production_engine`. Either access it directly or use `process_turn()` for full integration.

### Task 4.2: Rewrite `test_completion.py` integration tests [Medium]
**File:** `tests/integration/strategy/production/test_completion.py`
**Tests:** `pytest tests/integration/strategy/production/test_completion.py -q`

Update the `conftest.py` fixture first:
- [ ] Read `tests/integration/strategy/production/conftest.py` and update `production_setup` fixture to give empire resources

Then rewrite each failing test class:
- [ ] `TestProductionCompletion::test_production_completion`: Ship in facility queue → process ticks → spawns fleet. Queue item needs `total_cost`.
- [ ] `TestComplexSpawning::test_build_complex_adds_to_facilities`: Complex in base queue → ticks → PlanetaryFacility.
- [ ] `TestComplexSpawning::test_spawn_complex_loads_design_data`: Same + verify design_data populated.
- [ ] `TestComplexSpawning::test_spawn_complex_creates_facility_instance`: Same + verify UUID instance_id.
- [ ] `TestComplexSpawning::test_complex_builds_in_1_turn`: Item with small `total_cost` → 1 turn of ticks → completed.
- [ ] `TestShipSpawning` (5 tests): All add ship to shipyard facility queue → process ticks → verify spawn.
- [ ] `TestParallelShipyardE2E::test_two_shipyards_process_and_complete_independently`: Two yards with different queue items → verify independent processing.
- [ ] `TestFacilityQueueSaveLoadE2E::test_save_load_preserves_facility_queues_and_processes`: Save/load then process ticks.
- [ ] Replace all `engine.process_production()` calls with tick loop
- [ ] Verify all 10 previously failing + existing passing tests pass

**Notes:**

### Task 4.3: Rewrite `test_queue.py` integration tests [Simple]
**File:** `tests/integration/strategy/production/test_queue.py`
**Tests:** `pytest tests/integration/strategy/production/test_queue.py -q`

- [ ] `test_ship_build_stops_when_shipyard_removed`: Add `total_cost` to queue item, process ticks, then remove shipyard facility. Queue item should stop processing.
- [ ] `test_ship_build_starts_with_new_shipyard`: Add shipyard + queue item with `total_cost`, process ticks, verify progress.
- [ ] `test_complex_builds_without_shipyard`: Complex with `total_cost` in base queue, process ticks, verify completion.
- [ ] Verify all 5 tests pass (2 already passing + 3 rewritten)

**Notes:**

### Task 4.4: Rewrite `test_fleet_production_e2e.py` tests [Medium]
**File:** `tests/integration/strategy/production/test_fleet_production_e2e.py`
**Tests:** `pytest tests/integration/strategy/production/test_fleet_production_e2e.py -q`

- [ ] `test_e2e_fleet_with_yard_builds_ship_that_spawns_in_fleet`: Replace `process_fleet_production()` with `process_construction_tick()` loop. Add `total_cost`/`resources_consumed` to item. Fleet mock needs `space_shipyard_count` attribute.
- [ ] `test_e2e_fleet_at_planet_builds_complex_that_appears_on_planet`: Same pattern.
- [ ] `test_e2e_complex_pauses_when_fleet_moves_away_from_planet`: Process ticks at planet → move fleet → process ticks away (paused) → move back → process ticks (resumes).
- [ ] `test_queue_items_processed_in_order`: Add `total_cost` to all items. Process ticks. Verify FIFO ordering.
- [ ] Verify all tests pass (passing save/load + movement tests + 4 rewritten)

**Notes:** Fleet needs `space_shipyard_count` property/attribute for rate calculation in the dynamic system.

### Task 4.5: Rewrite `test_turn_execution.py` production test [Simple]
**File:** `tests/integration/gameplay_loop/test_turn_execution.py`
**Tests:** `pytest tests/integration/gameplay_loop/test_turn_execution.py::TestMultipleTurns::test_production_completes_across_turns`

- [ ] Replace `colony.add_production("test_complex", turns=3, vehicle_type="complex")` with direct queue item: `{"design_id": "test_complex", "type": "complex", "turns_remaining": 3, "total_cost": {"Metals": 6000}, "resources_consumed": {"Metals": 0.0}}`
  - 6000 Metals / 20 per tick = 300 ticks = 3 turns
- [ ] Give empire resources: set `colony` owner empire's `resource_pool["Metals"] = 100000`
- [ ] Replace `turn_engine.process_production()` calls with `turn_engine.process_turn()`
- [ ] Adjust assertions: after 1 turn, verify item still in queue with `resources_consumed > 0`; after 2 turns, still in queue; after 3 turns, queue empty
- [ ] Verify test passes

**Notes:** This test lives in the gameplay_loop integration tests, so using full `process_turn()` is appropriate.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/integration/strategy/production/ -q` — all pass
- [ ] `pytest tests/integration/test_complex_workflow.py -q` — all pass
- [ ] `pytest tests/integration/gameplay_loop/test_turn_execution.py -q` — production test passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
