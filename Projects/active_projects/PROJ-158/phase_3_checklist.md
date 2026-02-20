# Phase 3: Rewrite Tick Consumption Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-158 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix the 11 failing tests in `test_tick_consumption.py` that test the live `process_construction_tick()` but assert on dead fields or wrong consumption rates.

**Key Reference — Dynamic System Math:**
- Planetary yard rate: 2000/turn = 20/tick per resource (from `data/production_rates.json`)
- Shipyard facility rate: 3000/turn = 30/tick per resource
- Fleet yard rate: 3000/turn = 30/tick per resource
- Per-tick consumption = min(rate_per_tick, remaining_cost)
- Item completes when `resources_consumed >= total_cost`
- Limiting resource: the resource with the most ticks remaining determines pace for ALL resources

---

## Tasks

### Task 3.1: Update `_make_queue_item()` helper [Simple]
**File:** `tests/unit/strategy/production_engine/test_tick_consumption.py`

- [ ] Remove `cost_per_tick` parameter and field from `_make_queue_item()`
- [ ] Remove `ticks_in_current_turn` parameter and field from `_make_queue_item()`
- [ ] Resulting queue items have only: `design_id`, `type`, `turns_remaining`, `total_cost`, `resources_consumed`
- [ ] Update all callers that explicitly pass `cost_per_tick=` or `ticks_in_current_turn=` kwargs

**Notes:**

### Task 3.2: Rewrite failing TestTickConsumption tests [Medium]
**File:** `tests/unit/strategy/production_engine/test_tick_consumption.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_tick_consumption.py -q`

For each test, the expected consumption is based on production_rates.json rates, NOT item-level fields:

- [ ] `test_successful_tick_deducts_from_empire`: Item has `total_cost={"Metals": 500}`. Rate = 20/tick. Remaining = 500. Time needed = 25 ticks. 1 tick consumes 20 Metals. Assert `empire.resource_pool["Metals"] == approx(980.0)`.
- [ ] `test_resources_consumed_incremented`: After 2 ticks at 20/tick, `resources_consumed["Metals"]` should be `approx(40.0)`.
- [ ] `test_ticks_in_current_turn_incremented`: **DELETE this test** — `ticks_in_current_turn` is a dead field not tracked by the dynamic system.
- [ ] `test_resume_after_resources_available`: Remove `ticks_in_current_turn` assertions. After adding 100 Metals and processing tick, assert 20 Metals consumed (not 1.0). Assert `empire.resource_pool["Metals"] == approx(80.0)`.
- [ ] `test_turn_decremented_after_100_ticks`: **DELETE this test** — `turns_remaining` is now a float estimate updated each tick, not an integer decremented at tick 100. The concept of "100-tick boundary" doesn't exist in the dynamic system.
- [ ] `test_item_remains_when_turns_remaining_above_zero`: Rewrite to verify item stays in queue when `resources_consumed < total_cost`. Use `total_cost={"Metals": 1000}` (needs 50 ticks at 20/tick). After 1 tick, item still in queue with `resources_consumed ~= 20`.
- [ ] `test_multiple_queue_items_only_first_processes`: Remove `ticks_in_current_turn` assertions. After 1 tick, item1 consumed 20 Metals, item2 consumed 0. Assert `empire.resource_pool["Metals"] == approx(980.0)`.
- [ ] `test_facility_queue_tick_consumption`: Remove `ticks_in_current_turn` assertion. Shipyard rate = 30/tick. Assert `empire.resource_pool["Metals"] == approx(970.0)`.
- [ ] `test_multiple_resources_all_consumed`: Rate = 20/tick for each resource. Item has `total_cost={"Metals": 500, "Organics": 250, "Radioactives": 100}`. Limiting resource = Metals (500/20 = 25 ticks). Per tick: Metals = 20, Organics = 250/25 = 10, Radioactives = 100/25 = 4. Assert accordingly.
- [ ] `test_zero_cost_item_processes_normally`: Item with `total_cost={}` should complete immediately (0 cost = done). Assert queue is empty after 1 tick. Remove `ticks_in_current_turn` assertion. May need to patch `_spawn_complex`.
- [ ] `test_fleet_tick_processing_added`: Remove `ticks_in_current_turn` from item setup. Item is near-complete (`resources_consumed={"Metals": 99.0}`, `total_cost={"Metals": 100}`). Should still complete and spawn.

**Notes:** The limiting resource logic means that in multi-resource items, the slowest resource determines ALL consumption rates proportionally.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/production_engine/test_tick_consumption.py -q` — ALL tests pass
- [ ] `pytest tests/unit/strategy/production_engine/ -q` — all remaining tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
