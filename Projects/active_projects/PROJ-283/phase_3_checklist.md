# Phase 3: Unified point budget

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-283 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rewrite `race_point_budget.py` around per-factor step constants from `FACTOR_REGISTRY`. Implement `calculate_preferences_cost(race_config)` and `calculate_reproduction_cost(rate)`. Drop `aptitude_happiness` and `aptitude_population_growth` from the aptitude cost list.

---

## Tasks

### Task 3.1: Replace hardcoded step constants with registry-driven computation [Medium]
**File:** `game/strategy/data/race_point_budget.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_point_budget_v2.py`

- [ ] Delete the hardcoded step constants (gravity 0.1, temperature 10, water 0.1, radiation 10, atmosphere 10). Each factor now owns its `step`.
- [ ] Add `calculate_preferences_cost(race_config) -> int`:
  ```python
  def calculate_preferences_cost(race_config) -> int:
      total = 0
      for factor_id, pref in race_config.preferences.items():
          factor = get_factor(factor_id)
          # Compute steps between the actual tolerance and the default tolerance
          steps = abs(round((pref.tolerance - factor.default_tolerance) / factor.step))
          if steps > 0:
              total += _exponential_cost(steps)
      return total
  ```
- [ ] Setpoint is free: no cost contribution regardless of where setpoint sits within `[min_value, max_value]`.
- [ ] Tolerance cost: exponential in number of steps from default, in either direction (tighter OR wider tolerances cost). This matches the existing philosophy where deviating from the default costs points.
- [ ] Keep `_exponential_cost(steps) = 2^steps - 1` as-is.

### Task 3.2: Reproduction rate cost curve [Medium]
**File:** `game/strategy/data/race_point_budget.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_point_budget_v2.py::test_reproduction_cost_curve`

- [ ] Add `calculate_reproduction_cost(rate: float) -> int`:
  ```python
  REPRO_DEFAULT = 0.03
  REPRO_FLOOR = 0.005
  REPRO_STEP = 0.01  # 1% per step
  REPRO_REFUND_PER_STEP = 2  # linear refund per step below default
  
  def calculate_reproduction_cost(rate: float) -> int:
      steps = round((rate - REPRO_DEFAULT) / REPRO_STEP)
      if steps > 0:
          return _exponential_cost(steps)  # 1, 3, 7, 15, ...
      elif steps < 0:
          # Linear refund to REPRO_FLOOR
          floor_steps = round((REPRO_FLOOR - REPRO_DEFAULT) / REPRO_STEP)
          clamped_steps = max(steps, floor_steps)
          return clamped_steps * REPRO_REFUND_PER_STEP  # negative
      return 0
  ```
- [ ] Validate rate cannot go below `REPRO_FLOOR` — clamp or raise (recommend clamp + warn).
- [ ] Test the cost table: 3%→0, 4%→1, 5%→3, 6%→7, 7%→15; 2%→-2, 1%→-4, 0.5%→-5 (floor).

### Task 3.3: Drop `aptitude_happiness` and `aptitude_population_growth` from aptitude costs [Simple]
**File:** `game/strategy/data/race_point_budget.py`

- [ ] Remove both from the APTITUDE_NAMES list / cost calculation.
- [ ] `calculate_aptitude_cost(race_config)` now iterates the remaining 7 aptitudes.

### Task 3.4: Update `calculate_total_cost` and `get_remaining_points` [Simple]
**File:** `game/strategy/data/race_point_budget.py`

- [ ] `calculate_total_cost = calculate_aptitude_cost + calculate_preferences_cost + calculate_reproduction_cost(base_reproduction_rate)`.
- [ ] `get_remaining_points = DEFAULT_BUDGET - calculate_total_cost`.
- [ ] Remove the old `calculate_tolerance_cost` function (superseded by `calculate_preferences_cost`).
- [ ] Update `get_aptitude_breakdown` / `get_tolerance_breakdown` to reflect the new structure; prefer a single `get_breakdown()` returning a flat dict keyed by `aptitude:*`, `pref:*`, `reproduction`.

### Task 3.5: Write v2 point budget tests [Medium]
**File:** `tests/unit/strategy/data/test_race_point_budget_v2.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_race_point_budget_v2.py`

- [ ] Test per-axis cost parity at equal step counts: shifting gravity tolerance by 1 step costs the same as shifting temperature tolerance by 1 step (both use `_exponential_cost(1) = 1`).
- [ ] Test reproduction cost table: 3%→0, 4%→1, 5%→3, 6%→7, 7%→15.
- [ ] Test reproduction refund: 2%→-2, 1%→-4, 0.5%→-5 (floor). 0.1% clamps to 0.5% with -5 refund.
- [ ] Test total budget for a near-default race → remaining ≈ 100.
- [ ] Test a maxed-out race with 10 tolerance-step deviations → reasonable point drain.

### Task 3.6: Update tests broken by field removal [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Find and update any existing budget tests that expected `aptitude_happiness` or `aptitude_population_growth` costs. These are now 0-cost (not counted) or expected to reference `base_reproduction_rate` cost.
- [ ] Full suite green.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
