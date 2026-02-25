# Phase 6: Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-188 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete all old renderers, column managers, and dead code. ~1,088 lines removed. No backward compatibility retained.

---

## Tasks

### Task 6.1: Delete old Fleet components [Simple]
**Tests:** `pytest tests/ --testmon`

- [ ] Verify no remaining imports of `fleet_list_renderer`:
  - `grep -r "fleet_list_renderer" game/ tests/` should return 0 results
- [ ] Verify no remaining imports of old `column_manager` (the fleet-specific one):
  - `grep -r "from game.ui.screens.column_manager import" game/ tests/` should return 0 results
  - Note: `SPECIAL_CAPABILITY_COLUMNS` may still be imported by `fleet_report_filters.py` — if so, update that import to reference `fleet_data_source.py` instead
- [ ] Delete `game/ui/screens/fleet_list_renderer.py` (426 lines)
- [ ] Delete `game/ui/screens/column_manager.py` (234 lines)
- [ ] Run `pytest tests/ --testmon` — verify no breakage

**Notes:**

---

### Task 6.2: Delete old Planet List components [Simple]
**Tests:** `pytest tests/ --testmon`

- [ ] Verify no remaining imports of `planet_list_renderer`:
  - `grep -r "planet_list_renderer" game/ tests/` should return 0 results
- [ ] Verify no remaining imports of `planet_list_columns`:
  - `grep -r "planet_list_columns" game/ tests/` should return 0 results
- [ ] Delete `game/ui/screens/planet_list_renderer.py` (227 lines)
- [ ] Delete `game/ui/screens/planet_list_columns.py` (201 lines)
- [ ] Run `pytest tests/ --testmon` — verify no breakage

**Notes:**

---

### Task 6.3: Clean up test files [Medium]
**Tests:** `pytest tests/ --testmon`

- [ ] Check `tests/unit/ui/test_column_manager.py`:
  - If still testing old ColumnManager: delete file (tests migrated in Phase 2)
  - If already migrated to test TableColumnManager: keep
- [ ] Check for any test files that still import deleted modules
- [ ] Remove or update any stale test files
- [ ] Verify all test files compile: `python -m py_compile tests/unit/ui/test_*.py` (or equivalent)
- [ ] Run `pytest tests/ --testmon` — verify no breakage

**Notes:**

---

### Task 6.4: Final verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify test count >= 12,366 (plus new tests added)
- [ ] Verify 0 failures, 0 errors
- [ ] Count lines deleted:
  - `fleet_list_renderer.py`: 426 lines
  - `column_manager.py`: 234 lines
  - `planet_list_renderer.py`: 227 lines
  - `planet_list_columns.py`: 201 lines
  - **Total: ~1,088 lines deleted**
- [ ] Verify all 4 windows use VirtualTable:
  - `grep -l "VirtualTable" game/ui/screens/fleet_report_window.py game/ui/screens/planet_list_window.py game/ui/screens/empire_build_queue_window.py game/ui/screens/event_log_window.py` should return all 4 files

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `fleet_list_renderer.py` deleted (426 lines)
- [ ] `column_manager.py` deleted (234 lines)
- [ ] `planet_list_renderer.py` deleted (227 lines)
- [ ] `planet_list_columns.py` deleted (201 lines)
- [ ] No imports reference deleted files
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] Test count >= 12,366
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
