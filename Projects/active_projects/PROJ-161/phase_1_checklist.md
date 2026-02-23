# Phase 1: HarvestingEngine Per-Tick Conversion

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-161 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `process_harvesting_tick(tick, empires)` to HarvestingEngine and update the interface. The existing `process_harvesting` method remains temporarily for backward compat (removed in Phase 5).

---

## Tasks

### Task 1.1: Update IHarvestingEngine Interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

- [ ] Add `process_harvesting_tick(self, tick: int, empires: List) -> None` abstract method after existing `process_harvesting` (around line 370)
- [ ] Update class docstring to mention per-tick operation alongside existing method
- [ ] Keep `process_harvesting` in interface for now (removed in Phase 5)
- [ ] Verify: no import errors

**Notes:**

---

### Task 1.2: Implement `process_harvesting_tick` in HarvestingEngine [Medium]
**File:** `game/strategy/engine/harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

- [ ] Add `process_harvesting_tick(self, tick: int, empires: List) -> None` public method
- [ ] Call `self.recalculate_storage(empires)` each tick (per design decision)
- [ ] Reuse existing `_process_empire` -> `_process_colony` -> `_process_facility` chain but with per-tick harvest
- [ ] Key change in `_harvest_resource`: divide harvest by 100.0:
  ```python
  # Current (line ~306):
  harvest = base_rate * quality

  # New approach - add tick_fraction parameter or per-tick method:
  tick_harvest = (base_rate * quality) / 100.0
  actual_harvest = min(tick_harvest, quantity)
  ```
- [ ] Design choice: either add a `_tick_mode` flag to reuse `_harvest_resource`, or create `_harvest_resource_tick` that divides by 100. Prefer minimal approach.
- [ ] Update logging to indicate per-tick harvest amounts
- [ ] Verify: calling 100 times produces same total as single `process_harvesting` call

**Notes:**

---

### Task 1.3: Write Unit Tests for Per-Tick Harvesting [Medium]
**File:** `tests/unit/strategy/engine/test_harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

- [ ] Add `TestPerTickHarvesting` test class with these tests:
- [ ] `test_single_tick_harvests_one_hundredth` -- verify 1/100th of per-turn rate extracted per tick
- [ ] `test_100_ticks_equals_full_turn` -- call `process_harvesting_tick` 100 times, verify total matches old `process_harvesting` result
- [ ] `test_storage_cap_enforced_per_tick` -- verify storage cap works with incremental additions (empire near cap gets capped correctly)
- [ ] `test_planet_depletion_across_ticks` -- planet with small quantity runs out mid-turn, verify no negative quantity
- [ ] `test_non_operational_facility_skipped_per_tick` -- verify non-operational facilities produce nothing
- [ ] `test_recalculate_storage_called_each_tick` -- verify storage recalculation happens on each call
- [ ] All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/engine/test_harvesting_engine.py` -- all pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
