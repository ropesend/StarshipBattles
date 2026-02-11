# Phase 3: Controller Turn Calc & Tick Capping

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-97 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update BuildQueueController to use per-resource rates for turn calculation and cost_per_tick capping

---

## Tasks

### Task 3.1: Update `_calculate_build_turns()` [Medium]
**File:** `game/ui/panels/build_queue_controller.py` (lines 196-214)
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py`

- [x] Change signature: `build_rate: float` → `build_rate: Dict[str, float]`
- [x] New formula: `turns = max(1, max(ceil(cost[res] / rate) for res, rate in build_rate.items() if cost.get(res, 0) > 0 and rate > 0))`
- [x] Handle edge case: resource in cost but not in rates → treat as unbounded (1 turn)
- [x] Handle edge case: rate is 0 → skip (don't divide by zero)
- [x] Handle empty cost or empty rates → return 1

**Notes:** Implemented per-resource bottleneck formula.

### Task 3.2: Update `_build_cost_tracking()` to cap per-resource [Medium]
**File:** `game/ui/panels/build_queue_controller.py` (lines 216-234)
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py`

- [x] Accept `build_rate: Dict[str, float]` parameter (add parameter)
- [x] Calculate `max_per_tick = {res: rate / 100 for res, rate in build_rate.items()}`
- [x] Cap each resource's per-tick cost: `min(amount / total_ticks, max_per_tick.get(res, float('inf')))`
- [x] This ensures no resource exceeds its rate limit within a single turn

**Notes:** The key insight: when turns > 1, cost_per_tick is already < max_per_tick for the bottleneck resource. But for non-bottleneck resources that would finish in fewer turns, we cap them to prevent front-loading.

### Task 3.3: Update all callers to pass Dict build_rate [Simple]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py`

- [x] `_add_to_single_queue()` (line 389): already reads `source.build_rate`, now a dict
- [x] `_add_to_single_queue()` (line 391): pass dict to `_calculate_build_turns`
- [x] `_add_item_with_target_planet()` (line 432): same pattern
- [x] `_add_to_multiple_queues()` (line 476): pass `source.build_rate` dict
- [x] `_add_to_fallback()` (line 516): replace `PLANETARY_YARD_BUILD_RATE` constant with `get_default_production_rates("planetary_yard")`
- [x] Pass `build_rate` to `_build_cost_tracking()` calls
- [x] Remove `PLANETARY_YARD_BUILD_RATE = 2000.0` constant (line 18) — no longer needed

**Notes:** Removed constant, using get_default_production_rates() from build_queue_source.

### Task 3.4: Update controller tests [Medium]
**File:** `tests/unit/ui/panels/test_build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py`

- [x] Update `_make_source()` helper to accept `build_rate` as dict (currently passes float)
- [x] Update test at line 383: `build_rate=2000.0` → `build_rate={"Metals": 2000.0, ...}`
- [x] Update test at line 401: `build_rate=3000.0` → `build_rate={"Metals": 3000.0, ...}`
- [x] Update test at line 416-417: slow/fast sources with dict rates
- [x] Update test at line 425: fallback rate test
- [x] Add new test: per-resource bottleneck (5500 Metals at 3000/turn, 1000 Organics at 3000/turn → 2 turns from Metals)
- [x] Add new test: different per-resource rates (Metals 3000, Exotics 1500 → Exotics is bottleneck)
- [x] Add new test: cost_per_tick is capped per-resource

**Notes:** Added TestPerResourceBuildRates class with 9 new tests.

### Bonus: UI Display Updates (pulled forward from Phase 4)
- [x] Updated empire_build_queue_window.py: `_get_column_value` for build_rate column
- [x] Updated build_queue_selector.py: rate display uses max(source.build_rate.values())
- [x] Updated test_empire_build_queue_window.py: _make_source with build_rate dict
- [x] Updated test_empire_build_queue_formatter.py: source.build_rate as dict

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
