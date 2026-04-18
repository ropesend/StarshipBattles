# Phase 3: Wire into ProductionEngine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-285 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Multiply cached habitability multiplier into `ProductionEngine._process_queue_tick_dynamic`. Update production tests similarly.

---

## Tasks

### Task 3.1: Hook habitability into `_process_queue_tick_dynamic` [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_engine.py`

- [ ] Inside the tick-capacity computation, apply habitability multiplier after booster aggregation:
  ```python
  tick_capacity_base = base_rate_per_tick * yard_count * speed_bonus
  booster_mult = get_build_rate_booster_mult(...)  # existing
  habitability_mult = colony.get_cached_habitability_multiplier(self._race_registry, self._current_turn)
  tick_capacity = tick_capacity_base * booster_mult * habitability_mult
  ```
- [ ] Wire `race_registry` into `ProductionEngine.__init__` (DI).
- [ ] Expose `current_turn` via setter called from `TurnEngine` at the start of each turn.

### Task 3.2: Production tests [Medium]
**File:** `tests/unit/strategy/engine/test_production_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_engine.py`

- [ ] Retarget existing tests to use the ideal-planet / ideal-race fixture (habitability ≈ 1.0 preserves numbers).
- [ ] New test: hostile planet produces at habitability-scaled rate.
- [ ] New test: multi-species colony -> population-weighted multiplier.
- [ ] New test: uncolonized production (automated complex) -> multiplier=1.0.

### Task 3.3: Extend integration test from Phase 2 [Medium]
**File:** `tests/integration/strategy/test_habitability_on_economy.py`
**Tests:** `pytest tests/integration/strategy/test_habitability_on_economy.py`

- [ ] Add production-queue scenarios: ideal vs hostile planet. Queue the same item on both; assert the hostile planet takes ≈ 5x the turns.
- [ ] Confirm booster + habitability stack multiplicatively: planet with booster 1.5x AND habitability 0.8 gives effective 1.2x rate.

### Task 3.4: Full suite green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite green.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
