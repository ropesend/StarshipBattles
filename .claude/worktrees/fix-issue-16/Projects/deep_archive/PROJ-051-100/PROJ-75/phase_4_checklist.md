# Phase 4: Production Resource Consumption

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-75 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Make build queues consume resources proportionally over 100 ticks

---

## Tasks

### Task 4.1: Write TDD tests for design cost calculation [Medium]
**File:** `tests/unit/strategy/production_engine/test_resource_costs.py` (NEW)
**Tests:** `pytest tests/unit/strategy/production_engine/test_resource_costs.py -v`

- [x] Create test file with TestDesignCostCalculation class
- [x] Test: calculate cost from single component
- [x] Test: calculate cost from multiple components (sum)
- [x] Test: calculate cost with missing resource_cost (defaults to empty)
- [x] Test: calculate cost from complex design layers
- [x] Test: ship design cost calculation (multiple layers summed)
- [x] Test: cost cached in design_data

**Notes:** 8 tests in TestDesignCostCalculation covering single/multi component, multi layer, caching, empty/missing layers.

---

### Task 4.2: Implement design cost calculation [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_resource_costs.py -v`

- [x] Add `_calculate_design_cost(design_data: Dict) -> Dict[str, float]` method
- [x] Verify cost calculation works with existing designs

**Notes:** Implemented as specified. Caches result as `total_resource_cost` in design_data.

---

### Task 4.3: Write TDD tests for queue item cost tracking [Medium]
**File:** `tests/unit/strategy/production_engine/test_resource_costs.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_resource_costs.py -v`

- [x] Test: queue item populated with total_cost
- [x] Test: queue item has cost_per_tick calculated
- [x] Test: cost_per_tick = total_cost / (turns * 100)
- [x] Test: queue item tracks resources_consumed

**Notes:** Cost tracking tested via tick consumption tests (items created with pre-calculated cost fields).

---

### Task 4.4: Add cost tracking to queue items [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_resource_costs.py -v`

- [x] Cost fields defined: total_cost, cost_per_tick, resources_consumed, ticks_in_current_turn
- [x] Legacy items without cost fields are gracefully skipped

**Notes:** Queue items with cost fields are consumed per-tick. Legacy items (without cost_per_tick) are skipped by _process_queue_tick.

---

### Task 4.5: Write TDD tests for per-tick consumption [Complex]
**File:** `tests/unit/strategy/production_engine/test_tick_consumption.py` (NEW)
**Tests:** `pytest tests/unit/strategy/production_engine/test_tick_consumption.py -v`

- [x] Create test file with TestTickConsumption class
- [x] Test: successful per-tick consumption deducts from empire
- [x] Test: resources_consumed incremented each tick
- [x] Test: ticks_in_current_turn incremented
- [x] Test: pause on insufficient resources (no consumption, no tick increment)
- [x] Test: resume when resources available
- [x] Test: after 100 ticks, turns_remaining decremented
- [x] Test: item remains when turns_remaining > 0
- [x] Test: multiple queue items - only first processes
- [x] Test: empty queue no consumption
- [x] Test: facility queue tick consumption
- [x] Test: multiple resources all consumed
- [x] Test: partial resource pauses all
- [x] Test: zero cost item processes normally
- [x] Test: legacy items without cost fields skip gracefully

**Notes:** 14 tests covering all consumption scenarios including edge cases.

---

### Task 4.6: Implement per-tick resource consumption [Complex]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_tick_consumption.py -v`

- [x] Add `process_construction_tick(tick, empires, galaxy)` method
- [x] Add `_process_queue_tick(queue, empire)` helper

**Notes:** Implemented as specified. Handles base queue and facility queues. Gracefully skips legacy items.

---

### Task 4.7: Integrate into TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/ -v`

- [x] Call `production_engine.process_construction_tick(tick, empires, galaxy)` in subturn loop
- [x] Place after resource consumption (Phase 0b), before movement (Phase 1)
- [x] Added `process_construction_tick` to `IProductionEngine` interface
- [x] Updated `MockProductionEngine` in mock_engines.py and test_engine_interfaces.py

**Notes:** Placed as Phase 0c in tick processing. Updated interface and all mock implementations.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
