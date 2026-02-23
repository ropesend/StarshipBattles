# Phase 5: Rewrite Economy E2E Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-158 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the 5 failing economy E2E tests that create queue items with dead fields (`cost_per_tick`, `ticks_in_current_turn`).

**Key Reference — Dynamic System Math:**
- Planetary yard rate: 2000/turn = 20/tick per resource
- Per-tick consumption = rate_per_tick for each resource, capped by remaining_cost
- Limiting resource determines pace: the resource with the highest `remaining / rate` ratio

---

## Tasks

### Task 5.1: Rewrite economy construction tests [Medium]
**File:** `tests/integration/strategy/test_economy_e2e.py`
**Tests:** `pytest tests/integration/strategy/test_economy_e2e.py -q`

For each test, remove `cost_per_tick` and `ticks_in_current_turn` from queue items, then calculate correct expected values:

- [x] `test_construction_consumes_resources_per_tick` (line ~291):
  - Removed `cost_per_tick` and `ticks_in_current_turn` from queue item
  - Item completes at tick 8, consuming all 150 Metals
  - Expected: 850 Metals remaining, queue empty

- [x] `test_resource_depletion_pauses_construction` (line ~322):
  - Removed dead fields
  - System pauses when can't afford full 20/tick
  - At 30 Metals: tick 1 consumes 20, tick 2 can't afford 20, pauses
  - Expected: 10 Metals remaining, 20 consumed, item still in queue

- [x] `test_multi_resource_construction` (line ~436):
  - Removed dead fields
  - Item completes at tick 5, all 100 Metals + 60 Organics consumed
  - Expected: 900 Metals, 440 Organics, queue empty

- [x] `test_multi_resource_pauses_if_one_depletes` (line ~465):
  - Removed dead fields
  - After 1 tick: 20 Metals, 20 Organics consumed. Organics exhausted.
  - Assert on `resources_consumed` for progress tracking

- [x] `test_maintenance_paid_before_construction_tick` (line ~523):
  - Removed dead fields
  - Maintenance: 50, Construction: 100, Empire starts 200 → 50 remaining
  - Queue empty (item completed)

- [x] Verify all 15 economy tests pass (10 already passing + 5 rewritten)

- [x] Updated `test_construction_queue_save_load` to remove dead fields from serialization test

**Notes:** Discovered that system pauses when empire can't afford full tick's consumption (not partial consumption). Test adjusted to expect 10 Metals remaining when starting with 30 (20 consumed in 1 full tick).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/integration/strategy/test_economy_e2e.py -q` — all 15 tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
