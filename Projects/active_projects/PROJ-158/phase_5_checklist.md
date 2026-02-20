# Phase 5: Rewrite Economy E2E Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-158 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] `test_construction_consumes_resources_per_tick` (line ~291):
  - Remove `cost_per_tick` and `ticks_in_current_turn` from queue item
  - Item: `total_cost={"Metals": 150}`, empire starts with 1000 Metals
  - At 20/tick rate: item completes in 7.5 ticks, consuming all 150 Metals
  - Expected: `empire.resource_pool["Metals"] == approx(850.0)` (1000 - 150)
  - Queue should be EMPTY (item completed mid-turn)
  - Update assertions accordingly

- [ ] `test_resource_depletion_pauses_construction` (line ~322):
  - Remove dead fields
  - Item: `total_cost={"Metals": 300}`, empire has 30 Metals
  - At 20/tick: consumes 20 on tick 1, 10 on tick 2 (only 10 left), pauses at tick 2
  - Expected: `empire.resource_pool["Metals"] == approx(0.0)` (or close)
  - Assert on `resources_consumed["Metals"]` for progress tracking (not `ticks_in_current_turn`)
  - Update comment explaining the pause behavior

- [ ] `test_multi_resource_construction` (line ~436):
  - Remove dead fields
  - Item: `total_cost={"Metals": 100, "Organics": 60}`, empire has 1000/500
  - Limiting resource: Metals at 100/20=5 ticks, Organics at 60/20=3 ticks → Metals is limiting (5 ticks)
  - Per tick: Metals=20, Organics=60/5=12
  - After 100 ticks: item completes at tick 5, all consumed (100 Metals, 60 Organics)
  - Expected: 900 Metals, 440 Organics remaining
  - Queue should be EMPTY

- [ ] `test_multi_resource_pauses_if_one_depletes` (line ~465):
  - Remove dead fields
  - Item: `total_cost={"Metals": 200, "Organics": 200}`, empire has 1000 Metals, 20 Organics
  - Both rates = 20/tick. Same rate → both limiting equally (200/20 = 10 ticks each)
  - Per tick: 20 Metals + 20 Organics. After 1 tick: 20 consumed of each. Organics runs out.
  - Expected: `empire.resource_pool["Metals"] == approx(980.0)`, Organics ~= 0.0
  - Assert on `resources_consumed` for progress, not `ticks_in_current_turn`

- [ ] `test_maintenance_paid_before_construction_tick` (line ~523):
  - Remove dead fields
  - Maintenance: 50 Metals (5% of 1000 facility cost)
  - Construction: `total_cost={"Metals": 100}` at 20/tick → completes in 5 ticks, consumes 100 Metals
  - Empire starts with 200 Metals → after maintenance (50) and construction (100) = 50 Metals
  - Expected: `empire.resource_pool["Metals"] == approx(50.0)`

- [ ] Verify all 15 economy tests pass (10 already passing + 5 rewritten)

**Notes:** Some items may complete mid-turn (when `total_cost` is small enough). This is correct behavior — the dynamic system supports mid-turn completion and carry-over production. Tests should expect empty queues when items are cheap enough to complete in one turn.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/integration/strategy/test_economy_e2e.py -q` — all 15 tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
