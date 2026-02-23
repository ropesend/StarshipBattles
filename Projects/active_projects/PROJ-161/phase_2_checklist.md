# Phase 2: MaintenanceEngine Per-Tick Conversion

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-161 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `process_maintenance_tick(tick, empires)` to MaintenanceEngine with per-tick cost spreading and immediate scuttle on failure.

---

## Tasks

### Task 2.1: Update IMaintenanceEngine Interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py`

- [ ] Add `process_maintenance_tick(self, tick: int, empires: List) -> List` abstract method after existing `process_maintenance` (around line 408)
- [ ] Update class docstring to mention per-tick operation
- [ ] Keep `process_maintenance` in interface for now (removed in Phase 5)
- [ ] Verify: no import errors

**Notes:**

---

### Task 2.2: Implement `process_maintenance_tick` in MaintenanceEngine [Medium]
**File:** `game/strategy/engine/maintenance_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py`

- [ ] Add `process_maintenance_tick(self, tick: int, empires: List) -> List[ScuttleEvent]` public method
- [ ] Add `_calculate_maintenance_cost_per_tick` helper (or modify existing chain):
  ```python
  def _calculate_maintenance_cost_per_tick(self, design_data):
      full_cost = calculate_maintenance_cost(design_data, MAINTENANCE_RATE)
      return {res: amount / 100.0 for res, amount in full_cost.items()}
  ```
- [ ] Reuse `_process_empire` -> `_process_colony_facilities` / `_process_fleet_ships` chain but with per-tick costs
- [ ] Design choice: either add tick-aware parameter to existing methods, or create parallel `_process_*_tick` methods. Prefer minimal approach.
- [ ] Immediate scuttle if a tick's 1/100th payment fails (same as current behavior, just smaller amounts)
- [ ] Return `List[ScuttleEvent]` for entities scuttled this tick
- [ ] `_cleanup_empty_fleets` still runs after scuttle (same as current)
- [ ] Verify: calling 100 times produces same total deduction as single `process_maintenance` call

**Notes:** `MAINTENANCE_RATE = 0.05` is at line 25 of `maintenance_engine.py`. The `calculate_maintenance_cost()` module-level function (lines 28-68) computes 5% of total build cost. Per-tick = that / 100.

---

### Task 2.3: Write Unit Tests for Per-Tick Maintenance [Medium]
**File:** `tests/unit/strategy/engine/test_maintenance_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py`

- [ ] Add `TestPerTickMaintenance` test class with these tests:
- [ ] `test_single_tick_deducts_one_hundredth` -- verify 1/100th of per-turn maintenance cost deducted
- [ ] `test_100_ticks_equals_full_turn_cost` -- call 100 times, verify total deduction matches old `process_maintenance`
- [ ] `test_immediate_scuttle_on_tick_failure` -- verify entity scuttled when tick payment fails
- [ ] `test_non_operational_facility_free_per_tick` -- verify non-operational facilities cost nothing
- [ ] `test_scuttle_event_fields_correct` -- verify ScuttleEvent has correct entity_type, entity_name, location
- [ ] `test_multiple_entities_independent_per_tick` -- verify each facility/ship pays independently
- [ ] All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/engine/test_maintenance_engine.py` -- all pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
