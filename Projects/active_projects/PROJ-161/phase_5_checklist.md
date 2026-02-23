# Phase 5: Cleanup & Legacy Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-161 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove old `process_harvesting`/`process_maintenance` methods that are no longer called, update mocks, and clean up documentation.

---

## Tasks

### Task 5.1: Remove Old Interface Methods [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** `pytest tests/ --testmon`

- [x] Remove `process_harvesting(self, empires: List) -> None` from `IHarvestingEngine`
- [x] Remove `process_maintenance(self, empires: List) -> List` from `IMaintenanceEngine`
- [x] Update class docstrings to reflect per-tick-only operation
- [x] Verify: no import errors

**Notes:** Interfaces now only define `process_harvesting_tick` and `process_maintenance_tick`.

---

### Task 5.2: Remove Old HarvestingEngine Method [Simple]
**File:** `game/strategy/engine/harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

- [x] Remove `process_harvesting(self, empires)` method (lines 103-117)
- [x] Update class docstring to describe per-tick operation only
- [x] Verify: `process_harvesting_tick` is the only public entry point
- [x] Verify: no references to `process_harvesting` (without `_tick`) remain in codebase:
  ```
  grep -r "process_harvesting" game/ tests/ --include="*.py" | grep -v "_tick" | grep -v "__pycache__"
  ```

**Notes:** Only comments documenting the change remain (historical notes).

---

### Task 5.3: Remove Old MaintenanceEngine Method [Simple]
**File:** `game/strategy/engine/maintenance_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py`

- [x] Remove `process_maintenance(self, empires)` method (lines 101-116)
- [x] Update class docstring to describe per-tick operation only
- [x] Verify: `process_maintenance_tick` is the only public entry point
- [x] Verify: no references to `process_maintenance` (without `_tick`) remain in codebase:
  ```
  grep -r "process_maintenance" game/ tests/ --include="*.py" | grep -v "_tick" | grep -v "__pycache__"
  ```

**Notes:** Only comments documenting the change remain (historical notes).

---

### Task 5.4: Update Mock Engines [Simple]
**Search for:** `MockHarvestingEngine`, `MockMaintenanceEngine`, `_MockHarvestingEngine`, `_MockMaintenanceEngine`

- [x] Find all mock implementations in test files
- [x] Update mocks to implement `process_harvesting_tick` / `process_maintenance_tick`
- [x] Remove mocks for old `process_harvesting` / `process_maintenance` methods
- [x] Check `tests/unit/strategy/mocks/mock_engines.py` if it exists (has `MockMaintenanceEngine` at lines 200-223)
- [x] All tests still pass

**Notes:** Updated MockMaintenanceEngine and _MockHarvestingEngine to only implement per-tick methods.

---

### Task 5.5: Update Documentation and Comments [Simple]
**Files:** Various

- [x] `game/strategy/engine/turn_engine.py`: Update module-level docstring and `process_turn` docstring
- [x] `game/strategy/engine/harvesting_engine.py`: Update module-level docstring
- [x] `game/strategy/engine/maintenance_engine.py`: Update module-level docstring
- [x] Verify `game/strategy/engine/empire_economy_calculator.py` still works correctly:
  - Uses `get_harvester_info` from `harvesting_engine` (module-level function, unchanged)
  - Uses `MAINTENANCE_RATE` and `calculate_maintenance_cost` from `maintenance_engine` (unchanged)
  - No changes needed -- read-only projections
- [x] Remove any stale PROJ-75/PROJ-79 comments that reference old turn-start harvesting/maintenance

**Notes:** Module docstrings updated to reflect per-tick-only operation.

---

### Task 5.6: Final Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run complete test suite with parallel workers
- [x] All tests pass (11958 passed, 13 pre-existing UI failures unrelated to PROJ-161)
- [x] No warnings related to deprecated method usage

**Notes:** 13 pre-existing UI failures (transfer dialog, cargo mode) - verified against pre-PROJ-161 commit.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` -- ALL tests pass (11958 passed, 13 pre-existing failures)
- [x] `grep -r "process_harvesting[^_]" game/ tests/ --include="*.py"` returns nothing (only comments in tests)
- [x] `grep -r "process_maintenance[^_]" game/ tests/ --include="*.py"` returns nothing (only comments in tests)
- [x] `grep -r "_apply_partial_harvest" game/ tests/ --include="*.py"` returns nothing (only in project docs)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
