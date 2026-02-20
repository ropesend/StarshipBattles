# Phase 3: Rewrite Tick Consumption Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-158 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Remove `cost_per_tick` parameter and field from `_make_queue_item()`
- [x] Remove `ticks_in_current_turn` parameter and field from `_make_queue_item()`
- [x] Resulting queue items have only: `design_id`, `type`, `turns_remaining`, `total_cost`, `resources_consumed`
- [x] Update all callers that explicitly pass `cost_per_tick=` or `ticks_in_current_turn=` kwargs

**Notes:**

### Task 3.2: Rewrite failing TestTickConsumption tests [Medium]
**File:** `tests/unit/strategy/production_engine/test_tick_consumption.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_tick_consumption.py -q`

For each test, the expected consumption is based on production_rates.json rates, NOT item-level fields:

- [x] `test_successful_tick_deducts_from_empire`: Updated to expect 20/tick consumption (980 remaining after 1 tick).
- [x] `test_resources_consumed_incremented`: Updated to expect 40.0 after 2 ticks.
- [x] `test_ticks_in_current_turn_incremented`: **DELETED** — dead field test.
- [x] `test_resume_after_resources_available`: Removed dead field assertions, fixed consumption rate.
- [x] `test_turn_decremented_after_100_ticks`: **DELETED** — dead concept test.
- [x] `test_item_remains_when_turns_remaining_above_zero`: Renamed to `test_item_remains_when_resources_consumed_below_total`, rewritten for resources_consumed tracking.
- [x] `test_multiple_queue_items_only_first_processes`: Removed dead field assertions, fixed consumption assertions.
- [x] `test_facility_queue_tick_consumption`: Fixed to expect 30/tick shipyard rate.
- [x] `test_multiple_resources_all_consumed`: Fixed - each resource consumes at 20/tick (capped by remaining cost), not proportionally.
- [x] `test_zero_cost_item_processes_normally`: Renamed to `test_zero_cost_item_completes_immediately`, fixed helper to preserve empty dict.
- [x] `test_fleet_tick_processing_added`: Added `space_shipyard_count` attribute, removed dead fields.

**Notes:** The limiting resource logic means that in multi-resource items, the slowest resource determines ALL consumption rates proportionally.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/production_engine/test_tick_consumption.py -q` — 19 passed
- [x] `pytest tests/unit/strategy/production_engine/ -q` — 34 passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4

**Notes:**
- Deleted 2 tests: `test_ticks_in_current_turn_incremented`, `test_turn_decremented_after_100_ticks`
- Renamed 2 tests: `test_item_remains_when_turns_remaining_above_zero` → `test_item_remains_when_resources_consumed_below_total`, `test_zero_cost_item_processes_normally` → `test_zero_cost_item_completes_immediately`
- Fixed helper `_make_queue_item()` to use `is not None` check for empty dict handling
- All TestMidTurnCompletion tests updated to remove dead field references
