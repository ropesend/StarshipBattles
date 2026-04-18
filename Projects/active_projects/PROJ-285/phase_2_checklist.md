# Phase 2: Wire into HarvestingEngine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-285 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Multiply the cached habitability multiplier into `HarvestingEngine._harvest_resource`. Update existing harvest tests to either use ideal planet/race fixtures or explicitly assert the habitability effect.

---

## Tasks

### Task 2.1: Hook habitability into `_harvest_resource` [Medium]
**File:** `game/strategy/engine/harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

- [ ] Inside `_harvest_resource`, resolve `habitability_mult = colony.get_cached_habitability_multiplier(self._race_registry, self._current_turn)`.
- [ ] Multiply into the formula AFTER `quality`, BEFORE `tick_fraction`:
  ```python
  harvest = base_rate * size_multiplier * booster_mult * quality * habitability_mult * tick_fraction
  ```
- [ ] `HarvestingEngine.__init__` needs access to `race_registry` — wire via constructor (DI) so tests can inject stubs.
- [ ] `HarvestingEngine.process_harvesting_tick` already receives `tick`; use the turn number to key the cache. If turn isn't naturally available, expose via a setter called from `TurnEngine` at the start of each turn.

### Task 2.2: Harvest tests [Medium]
**File:** `tests/unit/strategy/engine/test_harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

- [ ] Introduce `make_ideal_planet()` / `make_ideal_race()` test fixtures (or import from a new `tests/conftest.py` helper).
- [ ] Retarget existing harvest-rate tests to use ideal planet + ideal race -> habitability ≈ 1.0 -> existing numeric expectations preserved (within ±0.05 tolerance).
- [ ] New test: ideal vs hostile planet comparison — hostile planet harvests ≈ 20% of ideal given habitability ≈ 0.2.
- [ ] New test: uncolonized planet with extractor -> multiplier=1.0 (no penalty).
- [ ] New test: multi-species colony -> harvest rate matches population-weighted multiplier.

### Task 2.3: Integration test [Medium]
**File:** `tests/integration/strategy/test_habitability_on_economy.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_habitability_on_economy.py`

- [ ] Run a 1-turn harvest on an ideal planet; record stockpile delta.
- [ ] Run same harvest on a hostile planet; assert delta is substantially lower (>50% reduction given habitability ≈ 0.2).
- [ ] Confirm cache is used: two colonies at the same hostile planet show identical multiplier.

### Task 2.4: Full suite green [Simple]
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
