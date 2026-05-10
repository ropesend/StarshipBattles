# Phase 2: MaintenanceEngine Per-Tick Conversion

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-161 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `process_maintenance_tick(tick, empires)` to MaintenanceEngine with per-tick cost spreading and immediate scuttle on failure.

---

## Tasks

### Task 2.1: Update IMaintenanceEngine Interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py`

- [x] Add `process_maintenance_tick(self, tick: int, empires: List) -> List` abstract method after existing `process_maintenance` (around line 408)
- [x] Update class docstring to mention per-tick operation
- [x] Keep `process_maintenance` in interface for now (removed in Phase 5)
- [x] Verify: no import errors

**Notes:** Added PROJ-161 reference to docstring. Method is now abstract.

---

### Task 2.2: Implement `process_maintenance_tick` in MaintenanceEngine [Medium]
**File:** `game/strategy/engine/maintenance_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py`

- [x] Add `process_maintenance_tick(self, tick: int, empires: List) -> List[ScuttleEvent]` public method
- [x] Add `_calculate_maintenance_cost_per_tick` helper (or modify existing chain):
  ```python
  def _calculate_maintenance_cost_per_tick(self, design_data):
      full_cost = calculate_maintenance_cost(design_data, MAINTENANCE_RATE)
      return {res: amount / 100.0 for res, amount in full_cost.items()}
  ```
- [x] Reuse `_process_empire` -> `_process_colony_facilities` / `_process_fleet_ships` chain but with per-tick costs
- [x] Design choice: either add tick-aware parameter to existing methods, or create parallel `_process_*_tick` methods. Prefer minimal approach.
- [x] Immediate scuttle if a tick's 1/100th payment fails (same as current behavior, just smaller amounts)
- [x] Return `List[ScuttleEvent]` for entities scuttled this tick
- [x] `_cleanup_empty_fleets` still runs after scuttle (same as current)
- [x] Verify: calling 100 times produces same total deduction as single `process_maintenance` call

**Notes:** Used tick_fraction parameter approach (0.01 for per-tick, 1.0 for full turn) to minimize code duplication. Modified `_calculate_maintenance_cost()` to accept tick_fraction and apply it to costs.

---

### Task 2.3: Write Unit Tests for Per-Tick Maintenance [Medium]
**File:** `tests/unit/strategy/engine/test_maintenance_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py`

- [x] Add `TestPerTickMaintenance` test class with these tests:
- [x] `test_single_tick_deducts_one_hundredth` -- verify 1/100th of per-turn maintenance cost deducted
- [x] `test_100_ticks_equals_full_turn_cost` -- call 100 times, verify total deduction matches old `process_maintenance`
- [x] `test_immediate_scuttle_on_tick_failure` -- verify entity scuttled when tick payment fails
- [x] `test_non_operational_facility_free_per_tick` -- verify non-operational facilities cost nothing
- [x] `test_scuttle_event_fields_correct` -- verify ScuttleEvent has correct entity_type, entity_name, location
- [x] `test_multiple_entities_independent_per_tick` -- verify each facility/ship pays independently
- [x] All tests pass

**Notes:** 6 new tests in TestPerTickMaintenance class. All 23 maintenance tests passing.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/engine/test_maintenance_engine.py` -- all pass (23 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
