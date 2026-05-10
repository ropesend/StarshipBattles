# Phase 1: Fix Column Swap Bug [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-221 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the column reordering arrows in EmpireBuildQueueWindow

---

## Tasks

### Task 1.1: Fix swap_column handling in EmpireBuildQueueWindow [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Read `update()` method (lines ~482-498) to confirm the bug location
- [x] Add `swap_col` handling branch: extract `(col_dict, direction)` tuple from `swap_col`
- [x] Call `self._column_manager.swap_column(col_dict['id'], direction)`
- [x] Call `self._virtual_table.rebuild_headers()`
- [x] Call `self._virtual_table.rebuild_row_pool()`
- [x] Call `self._refresh_list()` after rebuild
- [x] Ensure swap and sort are distinct branches — swap must NOT call `set_sort()`
- [x] Verify: pattern matches FleetReportWindow (correct reference — PlanetListWindow is also missing swap_column call)

**Notes:**

### Task 1.2: Add tests for swap_column handling [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Add test: `test_column_swap_calls_swap_column_on_manager` — mock `check_header_presses` to return `{'swap_column': (col_dict, 1), 'sort_column': None}`, verify `column_manager.swap_column()` called with correct args
- [x] Add test: `test_column_swap_rebuilds_headers_and_rows` — verify `rebuild_headers()` and `rebuild_row_pool()` called after swap
- [x] Add test: `test_column_swap_does_not_set_sort` — verify `set_sort()` NOT called when swap event fires
- [x] Run: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` — all pass (187 passed)

**Notes:**

### Task 1.3: Verify table infrastructure tests [Simple]
**Tests:** `pytest tests/unit/ui/components/table/`

- [x] Run `pytest tests/unit/ui/components/table/` — all 39+ tests pass (column_manager, header, virtual_table)
- [x] Run `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` — full suite passes (187 passed)
- [x] Run `pytest tests/ --testmon` — no regressions (13184 passed, 2 skipped)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
