# Phase 5: Cleanup & Legacy Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-161 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove old `process_harvesting`/`process_maintenance` methods that are no longer called, update mocks, and clean up documentation.

---

## Tasks

### Task 5.1: Remove Old Interface Methods [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Remove `process_harvesting(self, empires: List) -> None` from `IHarvestingEngine`
- [ ] Remove `process_maintenance(self, empires: List) -> List` from `IMaintenanceEngine`
- [ ] Update class docstrings to reflect per-tick-only operation
- [ ] Verify: no import errors

**Notes:**

---

### Task 5.2: Remove Old HarvestingEngine Method [Simple]
**File:** `game/strategy/engine/harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

- [ ] Remove `process_harvesting(self, empires)` method (lines 103-117)
- [ ] Update class docstring to describe per-tick operation only
- [ ] Verify: `process_harvesting_tick` is the only public entry point
- [ ] Verify: no references to `process_harvesting` (without `_tick`) remain in codebase:
  ```
  grep -r "process_harvesting" game/ tests/ --include="*.py" | grep -v "_tick" | grep -v "__pycache__"
  ```

**Notes:** Ensure `recalculate_storage` remains as a public method (called by per-tick method and potentially useful standalone).

---

### Task 5.3: Remove Old MaintenanceEngine Method [Simple]
**File:** `game/strategy/engine/maintenance_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py`

- [ ] Remove `process_maintenance(self, empires)` method (lines 101-116)
- [ ] Update class docstring to describe per-tick operation only
- [ ] Verify: `process_maintenance_tick` is the only public entry point
- [ ] Verify: no references to `process_maintenance` (without `_tick`) remain in codebase:
  ```
  grep -r "process_maintenance" game/ tests/ --include="*.py" | grep -v "_tick" | grep -v "__pycache__"
  ```

**Notes:**

---

### Task 5.4: Update Mock Engines [Simple]
**Search for:** `MockHarvestingEngine`, `MockMaintenanceEngine`, `_MockHarvestingEngine`, `_MockMaintenanceEngine`

- [ ] Find all mock implementations in test files
- [ ] Update mocks to implement `process_harvesting_tick` / `process_maintenance_tick`
- [ ] Remove mocks for old `process_harvesting` / `process_maintenance` methods
- [ ] Check `tests/unit/strategy/mocks/mock_engines.py` if it exists (has `MockMaintenanceEngine` at lines 200-223)
- [ ] All tests still pass

**Notes:**

---

### Task 5.5: Update Documentation and Comments [Simple]
**Files:** Various

- [ ] `game/strategy/engine/turn_engine.py`: Update module-level docstring and `process_turn` docstring
- [ ] `game/strategy/engine/harvesting_engine.py`: Update module-level docstring
- [ ] `game/strategy/engine/maintenance_engine.py`: Update module-level docstring
- [ ] Verify `game/strategy/engine/empire_economy_calculator.py` still works correctly:
  - Uses `get_harvester_info` from `harvesting_engine` (module-level function, unchanged)
  - Uses `MAINTENANCE_RATE` and `calculate_maintenance_cost` from `maintenance_engine` (unchanged)
  - No changes needed -- read-only projections
- [ ] Remove any stale PROJ-75/PROJ-79 comments that reference old turn-start harvesting/maintenance

**Notes:**

---

### Task 5.6: Final Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run complete test suite with parallel workers
- [ ] All tests pass
- [ ] No warnings related to deprecated method usage

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` -- ALL tests pass
- [ ] `grep -r "process_harvesting[^_]" game/ tests/ --include="*.py"` returns nothing (only `process_harvesting_tick` references)
- [ ] `grep -r "process_maintenance[^_]" game/ tests/ --include="*.py"` returns nothing (only `process_maintenance_tick` references)
- [ ] `grep -r "_apply_partial_harvest" game/ tests/ --include="*.py"` returns nothing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
