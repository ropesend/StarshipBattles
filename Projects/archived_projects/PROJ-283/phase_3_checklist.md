# Phase 3: Unified point budget

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-283 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Rewrite `race_point_budget.py` around per-factor step constants from `FACTOR_REGISTRY`. Implement `calculate_preferences_cost(race_config)` and `calculate_reproduction_cost(rate)`. Drop `aptitude_happiness` and `aptitude_population_growth` from the aptitude cost list.

---

## Tasks

### Task 3.1: Replace hardcoded step constants with registry-driven computation [Medium]
**File:** `game/strategy/data/race_point_budget.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_point_budget_v2.py`

- [x] Delete the hardcoded step constants (gravity 0.1, temperature 10, water 0.1, radiation 10, atmosphere 10). Each factor now owns its `step`.
- [x] Add `calculate_preferences_cost(race_config) -> int` (instance method on `RacePointBudget`):
  ```python
  def calculate_preferences_cost(self, race_config) -> int:
      total = 0
      for factor_id, pref in race_config.preferences.items():
          factor = get_factor(factor_id)
          steps = abs(round((pref.tolerance - factor.default_tolerance) / factor.step))
          total += self._exponential_cost(steps)
      return total
  ```
- [x] Setpoint is free: no cost contribution regardless of where setpoint sits within `[min_value, max_value]`.
- [x] Tolerance cost: exponential in number of steps from default, in either direction (tighter OR wider tolerances cost). Verified by parametrized tests across all 7 scalar axes + gas axis.
- [x] Keep `_exponential_cost(steps) = 2^steps - 1` as-is (instance method preserved).

**Notes:** Implemented as instance methods on the existing `RacePointBudget` class rather than module functions — UI callers (5 files) already instantiate `RacePointBudget()`, so converting to module-level would have rippled into 5 UI files for no behavioural gain. See decisions.md (2026-04-18). The plan-suggested integer rounding via `round()` proved correct for tolerance cost (deviation amplitudes use absolute integer steps); only the reproduction-rate refund needed continuous-rate math.

### Task 3.2: Reproduction rate cost curve [Medium]
**File:** `game/strategy/data/race_point_budget.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_point_budget_v2.py::TestCalculateReproductionCost`

- [x] Add `calculate_reproduction_cost(rate: float) -> int` as an instance method on `RacePointBudget`. Constants exposed as class attributes: `REPRO_DEFAULT=0.03`, `REPRO_FLOOR=0.005`, `REPRO_STEP=0.01`, `REPRO_REFUND_PER_STEP=2`.
- [x] Validate rate cannot go below `REPRO_FLOOR` — clamps to floor (no warn — silent clamp matches the plan's "recommend clamp" guidance and lets the UI present the floor as a hard limit without surfacing warnings).
- [x] Test the cost table: 3%→0, 4%→1, 5%→3, 6%→7, 7%→15; 2%→-2, 1%→-4, 0.5%→-5 (floor); 0.1% clamps to 0.5% with -5 refund.

**Notes:** The plan's pseudocode used `round((REPRO_FLOOR - REPRO_DEFAULT) / REPRO_STEP)` for the refund computation, which evaluates to `round(-2.5)`. Python's banker's rounding makes that -2 (not -3), giving a refund of -4 at the floor instead of the table's -5. Switched to linear-in-rate math: `delta = REPRO_DEFAULT - rate; refund = -round(delta/step * refund_per_step)`. This produces 2%→-2, 1%→-4, 0.5%→-5 exactly. Documented in decisions.md.

### Task 3.3: Drop `aptitude_happiness` and `aptitude_population_growth` from aptitude costs [Simple]
**File:** `game/strategy/data/race_point_budget.py`

- [x] Removed both from the `_iter_paid_aptitudes` generator (the new internal helper that lists the 7 paid aptitudes).
- [x] `calculate_aptitude_cost(race_config)` now iterates the remaining 7 aptitudes via `_iter_paid_aptitudes`.
- [x] `get_aptitude_breakdown(race_config)` also dropped — no longer returns `happiness` or `population_growth` keys.

**Notes:** Legacy fields `aptitude_happiness` and `aptitude_population_growth` STAY on `RaceConfig` until Phase 4. Phase 3's only behavioural change is "they no longer cost points." UI panels that display them (`race_summary_panel`, `empire_panel_window`, `race_validator`) are untouched until Phase 4.

### Task 3.4: Update `calculate_total_cost` and `get_remaining_points` [Simple]
**File:** `game/strategy/data/race_point_budget.py`

- [x] `calculate_total_cost = calculate_aptitude_cost + calculate_preferences_cost + calculate_reproduction_cost(base_reproduction_rate)`.
- [x] `get_remaining_points = DEFAULT_BUDGET - calculate_total_cost`.
- [x] Removed the old `calculate_tolerance_cost` method (superseded by `calculate_preferences_cost`).
- [x] Added `get_breakdown(race_config)` returning a flat dict keyed by `aptitude:*`, `pref:*`, `reproduction`. Sum of values equals `calculate_total_cost`. `get_aptitude_breakdown` retained as a focused per-aptitude helper.

**Notes:** Updated UI callers in the same change: `race_aptitudes_panel.py:194,279` and `race_environment_panel.py:442` now call `calculate_preferences_cost` instead of the deleted `calculate_tolerance_cost`. Same `(race_config) → int` signature, no other code changes needed in the panels.

### Task 3.5: Write v2 point budget tests [Medium]
**File:** `tests/unit/strategy/data/test_race_point_budget_v2.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_race_point_budget_v2.py`

- [x] Test per-axis cost parity at equal step counts: shifting any scalar tolerance by 1 step costs 1 (`TestCalculatePreferencesCost::test_per_axis_cost_parity` + parametrized one-step tests for all 7 scalars).
- [x] Test reproduction cost table: 3%→0, 4%→1, 5%→3, 6%→7, 7%→15 (parametrized).
- [x] Test reproduction refund: 2%→-2, 1%→-4, 0.5%→-5 (floor). 0.1% clamps to 0.5% with -5 refund (`test_below_floor_clamps_to_floor_refund`).
- [x] Test total budget for a near-default race → remaining ≈ 100 (`TestCalculateTotalCost::test_remaining_points_default_is_full_budget`).
- [x] Test maxed-out tolerance combinations and aptitude edge cases (TestAptitudeCostEdgeCases: max=440, min=-49; TestCustomBudget::test_remaining_can_go_negative covers the over-budget case).

**Notes:** 46 tests total in `test_race_point_budget_v2.py`, all passing. Coverage exceeded the plan: also added `TestLegacyMethodsRemoved` to enforce the System Migration Policy (asserts `hasattr` returns False for the deleted methods so future contributors can't accidentally re-introduce them).

### Task 3.6: Update tests broken by field removal [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Found all callers of `calculate_tolerance_cost` / `get_tolerance_breakdown` — 12 tests in `tests/unit/strategy/data/test_race_point_budget.py` plus 3 UI sites. UI sites updated to `calculate_preferences_cost`.
- [x] Deleted the legacy `tests/unit/strategy/data/test_race_point_budget.py` per System Migration Policy (eradicate the old, don't keep parallel suites). Surviving aptitude edge-case coverage ported to v2's `TestAptitudeCostEdgeCases` + `TestCustomBudget`.
- [x] Full sharded suite green: 14797/14798. Sole failure is the same pre-existing flaky `test_copy_designs_without_themes_preserves_original` (Klingons vs Federation theme leak) flagged in Phase 1 + Phase 2 handoffs — unrelated to PROJ-283.

**Notes:** No `aptitude_happiness` or `aptitude_population_growth` tests broke from this change (their values are still accepted by the dataclass; they just no longer cost points). Pre-existing 16-test `TestRaceConfigValidation` failure (tuple-unpacking bug from Phase 1 handoff watchout #1) remains hidden in sharded runs and is still out of PROJ-283 scope.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
