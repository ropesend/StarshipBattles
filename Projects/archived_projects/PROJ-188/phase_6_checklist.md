# Phase 6: Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-188 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete all old renderers, column managers, and dead code. ~1,088 lines removed. No backward compatibility retained.

---

## Tasks

### Task 6.1: Delete old Fleet components [Simple]
**Tests:** `pytest tests/ --testmon`

- [x] Verify no remaining imports of `fleet_list_renderer`:
  - `grep -r "fleet_list_renderer" game/ tests/` should return 0 results
- [x] Verify no remaining imports of old `column_manager` (the fleet-specific one):
  - `grep -r "from game.ui.screens.column_manager import" game/ tests/` should return 0 results
  - Note: `SPECIAL_CAPABILITY_COLUMNS` may still be imported by `fleet_report_filters.py` — if so, update that import to reference `fleet_data_source.py` instead
- [x] Delete `game/ui/screens/fleet_list_renderer.py` (426 lines)
- [x] Delete `game/ui/screens/column_manager.py` (234 lines)
- [x] Run `pytest tests/ --testmon` — verify no breakage

**Notes:** Updated fleet_report_filters.py to import SPECIAL_CAPABILITY_COLUMNS from fleet_data_source.py instead of old column_manager.py

---

### Task 6.2: Delete old Planet List components [Simple]
**Tests:** `pytest tests/ --testmon`

- [x] Verify no remaining imports of `planet_list_renderer`:
  - `grep -r "planet_list_renderer" game/ tests/` should return 0 results
- [x] Verify no remaining imports of `planet_list_columns`:
  - `grep -r "planet_list_columns" game/ tests/` should return 0 results
- [x] Delete `game/ui/screens/planet_list_renderer.py` (227 lines)
- [x] Delete `game/ui/screens/planet_list_columns.py` (201 lines)
- [x] Run `pytest tests/ --testmon` — verify no breakage

**Notes:**

---

### Task 6.3: Clean up test files [Medium]
**Tests:** `pytest tests/ --testmon`

- [x] Check `tests/unit/ui/test_column_manager.py`:
  - If still testing old ColumnManager: delete file (tests migrated in Phase 2)
  - If already migrated to test TableColumnManager: keep
- [x] Check for any test files that still import deleted modules
- [x] Remove or update any stale test files
- [x] Verify all test files compile: `python -m py_compile tests/unit/ui/test_*.py` (or equivalent)
- [x] Run `pytest tests/ --testmon` — verify no breakage

**Notes:**
- Deleted tests/unit/ui/test_column_manager.py (tested old fleet ColumnManager)
- Deleted tests/repro_issues/test_crash_planet_list_method.py (tested old planet_list_columns)
- Removed TestColumnManager class from test_planet_list_components.py (tested old planet_list_columns.ColumnManager)
- New TableColumnManager tests exist at tests/unit/ui/components/table/test_column_manager.py

---

### Task 6.4: Final verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify test count >= 12,366 (plus new tests added)
- [x] Verify 0 failures, 0 errors
- [x] Count lines deleted:
  - `fleet_list_renderer.py`: 425 lines
  - `column_manager.py`: 233 lines
  - `planet_list_renderer.py`: 226 lines
  - `planet_list_columns.py`: 200 lines
  - **Total: 1,084 lines deleted**
- [x] Verify all 4 windows use VirtualTable:
  - `grep -l "VirtualTable" game/ui/screens/fleet_report_window.py game/ui/screens/planet_list_window.py game/ui/screens/empire_build_queue_window.py game/ui/screens/event_log_window.py` should return all 4 files

**Notes:** Tests: 12,623 passed, 1 skipped (some old tests for deleted code were also removed)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `fleet_list_renderer.py` deleted (425 lines)
- [x] `column_manager.py` deleted (233 lines)
- [x] `planet_list_renderer.py` deleted (226 lines)
- [x] `planet_list_columns.py` deleted (200 lines)
- [x] No imports reference deleted files
- [x] Full test suite passes: `pytest tests/ -n 12`
- [x] Test count >= 12,366
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
