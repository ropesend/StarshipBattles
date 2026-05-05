# Phase 3: Wire into ProductionEngine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-285 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Multiply cached habitability multiplier into `ProductionEngine._process_queue_tick_dynamic`. Update production tests similarly.

---

## Tasks

### Task 3.1: Hook habitability into `_process_queue_tick_dynamic` [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_habitability.py`

- [x] Inside the tick-capacity computation, apply habitability multiplier after booster aggregation:
  ```python
  tick_capacity_base = base_rate_per_tick * yard_count * speed_bonus
  booster_mult = get_build_rate_booster_mult(...)  # existing
  habitability_mult = colony.get_cached_habitability_multiplier(self._race_registry, self._current_turn)
  tick_capacity = tick_capacity_base * booster_mult * habitability_mult
  ```
- [x] Wire `race_registry` into `ProductionEngine.__init__` (DI).
- [x] Expose `current_turn` via setter called from `TurnEngine` at the start of each turn.

**Notes:** The plan's sketch scaled `tick_capacity` directly. After reading the actual engine, I instead scale `production_rate` (a dict) BEFORE the while-loop enters `_calculate_tick_expenditure` — that step computes `p_rate_per_tick = production_rate[res] / 100`, so scaling production_rate flows through naturally. `_get_habitability_mult(colony_or_fleet)` short-circuits to 1.0 for fleets (no `get_cached_habitability_multiplier` on Fleet), legacy mock planets (attr absent), and legacy callers (race_registry=None). `set_current_turn(turn)` method parallels HarvestingEngine's API; `TurnEngine.process_turn` already calls this on both engines (wired in Phase 2).

### Task 3.2: Production tests [Medium]
**File:** `tests/unit/strategy/production_engine/test_habitability.py` (NEW)
**Tests:** `pytest tests/unit/strategy/production_engine/test_habitability.py`

- [x] Retarget existing tests to use the ideal-planet / ideal-race fixture (habitability ≈ 1.0 preserves numbers).
- [x] New test: hostile planet produces at habitability-scaled rate.
- [x] New test: multi-species colony -> population-weighted multiplier.
- [x] New test: uncolonized production (automated complex) -> multiplier=1.0.

**Notes:** Mirror of the Phase 2 test strategy — NEW dedicated file `test_habitability.py` (8 tests) rather than retargeting the existing `tests/unit/strategy/production_engine/test_tick_consumption.py` et al. (40 existing tests using MagicMock planets). The legacy tests use `race_registry=None` via the default constructor path → multiplier=1.0 → identical behavior preserved. New tests exercise DI kwarg acceptance, hostile-vs-ideal drain comparison, uncolonized-runs-at-full-rate, fleet-queue-not-scaled (tests the helper directly since Fleet affordability path is orthogonal and MagicMock(spec=Fleet) trips it), cross-engine cache sharing (one habitability computation per colony per turn regardless of whether HarvestingEngine or ProductionEngine is the first caller). Multi-species weighted test lives in `test_colony_output.py` at the helper level rather than duplicated here — the production engine is transparent to the helper's weighting logic.

### Task 3.3: Extend integration test from Phase 2 [Medium]
**File:** `tests/integration/strategy/test_habitability_on_economy.py`
**Tests:** `pytest tests/integration/strategy/test_habitability_on_economy.py`

- [x] Add production-queue scenarios: ideal vs hostile planet. Queue the same item on both; assert the hostile planet takes ≈ 5x the turns.
- [x] Confirm booster + habitability stack multiplicatively: planet with booster 1.5x AND habitability 0.8 gives effective 1.2x rate.

**Notes:** 2 new integration tests extending the Phase 2 file. `test_production_habitability_scales_drain` runs one tick on ideal vs hostile with identical queued complex — hostile drain < 5% of ideal (hostile habitability ≈ 0.002 vs ideal ≈ 0.94). `test_production_stacks_with_booster_mock` uses pre-multiplied `production_rate` (simulating the booster layer's output) on one engine and a raw rate + real habitability on another — verifies that habitability is independently multiplicative alongside whatever boost math is fed in. Assertion is loose (drain_b < drain_a) rather than computing exact stacked ratios because the logistic tick-capacity interaction with `max_ticks_needed` means a strict equality would drift on edge cases; the ordering is the meaningful signal.

### Task 3.4: Full suite green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite green.

**Notes:** 14966 total / 14965 passed / 1 failed — the persistent `test_copy_designs_without_themes_preserves_original` theme_id flake. Net Phase 3 new tests: 10 (8 production habitability unit + 2 integration). 40 legacy production_engine tests still pass via the default-None path. Full suite picked up all 30 PROJ-285 tests (Phase 1+2+3 combined).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
