# Phase 2: Extract Shared Limiting-Resource Formula

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-233 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Eliminate duplicated limiting-resource calculation between `production_engine.py` and `construction_forecast.py`.

---

## Tasks

### Task 2.1: Create `production_math.py` [Simple]
**File:** `game/strategy/engine/production_math.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_production_math.py -v`

- [ ] Create `game/strategy/engine/production_math.py` with:
  ```python
  """Shared production math utilities.

  PROJ-233: Extracted from ProductionEngine._calculate_tick_expenditure
  and construction_forecast.forecast_queue_turn_spend to eliminate duplication.
  """
  from typing import Dict, Optional

  def find_limiting_resource_ticks(
      remaining_cost: Dict[str, float],
      rate_per_turn: Dict[str, float],
      ticks_per_turn: int = 100,
  ) -> Optional[float]:
      """Return total ticks needed to complete, or None if any required rate is zero.

      Finds the limiting resource (the one that takes longest to produce at the
      given rate) and returns the number of ticks needed.

      Args:
          remaining_cost: Resource amounts still needed (resource_name -> amount).
          rate_per_turn: Production rate per turn (resource_name -> amount_per_turn).
          ticks_per_turn: Number of ticks per turn (default 100).

      Returns:
          Total ticks needed (float), or None if any required resource has zero rate.
      """
      if not remaining_cost:
          return 0.0

      max_ticks = 0.0
      for resource, amount in remaining_cost.items():
          rate = rate_per_turn.get(resource, 0.0)
          if rate <= 0:
              return None
          rate_per_tick = rate / ticks_per_turn
          ticks = amount / rate_per_tick
          if ticks > max_ticks:
              max_ticks = ticks
      return max_ticks
  ```
- [ ] Verify: File is ~35 lines, pure function with no game imports

**Notes:**

### Task 2.2: Write unit tests for shared formula [Simple]
**File:** `tests/unit/strategy/engine/test_production_math.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_production_math.py -v`

- [ ] Create test file with cases:
  - `test_empty_remaining_cost_returns_zero` — `{}` → `0.0`
  - `test_single_resource` — `{"Metals": 50}` at rate `{"Metals": 100}` per turn → 50 ticks
  - `test_limiting_resource_wins` — two resources, one takes longer → returns longer
  - `test_zero_rate_returns_none` — rate is 0 for a needed resource → `None`
  - `test_missing_rate_returns_none` — resource not in rate dict → `None`
  - `test_custom_ticks_per_turn` — verify `ticks_per_turn=1` gives turns instead of ticks
- [ ] Run tests: All pass

**Notes:**

### Task 2.3: Update `production_engine.py` to use shared formula [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/ tests/unit/strategy/engine/test_production_refactor.py -v`

- [ ] Add import: `from game.strategy.engine.production_math import find_limiting_resource_ticks`
- [ ] In `_calculate_tick_expenditure()`, replace the inline loop (lines 399-410):
  ```python
  # OLD (lines 399-410):
  max_ticks_needed = 0.0
  for res, amount in remaining_cost.items():
      p_rate_per_turn = production_rate.get(res, 0.0)
      if p_rate_per_turn <= 0:
          return None
      p_rate_per_tick = p_rate_per_turn / TICKS_PER_TURN
      ticks_needed = amount / p_rate_per_tick
      if ticks_needed > max_ticks_needed:
          max_ticks_needed = ticks_needed

  # NEW:
  max_ticks_needed = find_limiting_resource_ticks(remaining_cost, production_rate, TICKS_PER_TURN)
  if max_ticks_needed is None:
      return None
  ```
- [ ] Run tests: All pass, behavior identical

**Notes:**

### Task 2.4: Update `construction_forecast.py` to use shared formula [Simple]
**File:** `game/strategy/engine/construction_forecast.py`
**Tests:** `pytest tests/unit/strategy/engine/ tests/unit/ui/panels/test_build_queue_controller.py -v`

- [ ] Add import: `from game.strategy.engine.production_math import find_limiting_resource_ticks`
- [ ] Replace the inline loop (lines 68-78):
  ```python
  # OLD (lines 68-78):
  turns_needed = 0.0
  can_build = True
  for res, rem in remaining_cost.items():
      rate = build_rate.get(res, 0.0)
      if rate <= 0:
          can_build = False
          break
      t = rem / rate
      if t > turns_needed:
          turns_needed = t

  # NEW:
  ticks_needed = find_limiting_resource_ticks(remaining_cost, build_rate, ticks_per_turn=1)
  if ticks_needed is None:
      result.append({r: 0.0 for r in PLANET_RESOURCES})
      continue
  turns_needed = ticks_needed  # ticks_per_turn=1 means result is in turns
  ```
  Note: By passing `ticks_per_turn=1`, the division by ticks_per_turn is a no-op, so `remaining / rate` gives turns directly.
- [ ] Remove `can_build` variable (no longer needed)
- [ ] Run tests: All pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
