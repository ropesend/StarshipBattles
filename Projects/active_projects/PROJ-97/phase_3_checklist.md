# Phase 3: Controller Turn Calc & Tick Capping

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-97 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update BuildQueueController to use per-resource rates for turn calculation and cost_per_tick capping

---

## Tasks

### Task 3.1: Update `_calculate_build_turns()` [Medium]
**File:** `game/ui/panels/build_queue_controller.py` (lines 196-214)
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py`

- [ ] Change signature: `build_rate: float` → `build_rate: Dict[str, float]`
- [ ] New formula: `turns = max(1, max(ceil(cost[res] / rate) for res, rate in build_rate.items() if cost.get(res, 0) > 0 and rate > 0))`
- [ ] Handle edge case: resource in cost but not in rates → treat as unbounded (1 turn)
- [ ] Handle edge case: rate is 0 → skip (don't divide by zero)
- [ ] Handle empty cost or empty rates → return 1

**Notes:**

### Task 3.2: Update `_build_cost_tracking()` to cap per-resource [Medium]
**File:** `game/ui/panels/build_queue_controller.py` (lines 216-234)
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py`

- [ ] Accept `build_rate: Dict[str, float]` parameter (add parameter)
- [ ] Calculate `max_per_tick = {res: rate / 100 for res, rate in build_rate.items()}`
- [ ] Cap each resource's per-tick cost: `min(amount / total_ticks, max_per_tick.get(res, float('inf')))`
- [ ] This ensures no resource exceeds its rate limit within a single turn

**Notes:** The key insight: when turns > 1, cost_per_tick is already < max_per_tick for the bottleneck resource. But for non-bottleneck resources that would finish in fewer turns, we cap them to prevent front-loading.

### Task 3.3: Update all callers to pass Dict build_rate [Simple]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py`

- [ ] `_add_to_single_queue()` (line 389): already reads `source.build_rate`, now a dict
- [ ] `_add_to_single_queue()` (line 391): pass dict to `_calculate_build_turns`
- [ ] `_add_item_with_target_planet()` (line 432): same pattern
- [ ] `_add_to_multiple_queues()` (line 476): pass `source.build_rate` dict
- [ ] `_add_to_fallback()` (line 516): replace `PLANETARY_YARD_BUILD_RATE` constant with `get_default_production_rates("planetary_yard")`
- [ ] Pass `build_rate` to `_build_cost_tracking()` calls
- [ ] Remove `PLANETARY_YARD_BUILD_RATE = 2000.0` constant (line 18) — no longer needed

**Notes:**

### Task 3.4: Update controller tests [Medium]
**File:** `tests/unit/ui/panels/test_build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py`

- [ ] Update `_make_source()` helper to accept `build_rate` as dict (currently passes float)
- [ ] Update test at line 383: `build_rate=2000.0` → `build_rate={"Metals": 2000.0, ...}`
- [ ] Update test at line 401: `build_rate=3000.0` → `build_rate={"Metals": 3000.0, ...}`
- [ ] Update test at line 416-417: slow/fast sources with dict rates
- [ ] Update test at line 425: fallback rate test
- [ ] Add new test: per-resource bottleneck (5500 Metals at 3000/turn, 1000 Organics at 3000/turn → 2 turns from Metals)
- [ ] Add new test: different per-resource rates (Metals 3000, Exotics 1500 → Exotics is bottleneck)
- [ ] Add new test: cost_per_tick is capped per-resource

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
