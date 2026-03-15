# Phase 1: Fix Column Swap Bug [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-221 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix the column reordering arrows in EmpireBuildQueueWindow

---

## Tasks

### Task 1.1: Fix swap_column handling in EmpireBuildQueueWindow [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Read `update()` method (lines ~482-498) to confirm the bug location
- [ ] Add `swap_col` handling branch: extract `(col_dict, direction)` tuple from `swap_col`
- [ ] Call `self._column_manager.swap_column(col_dict['id'], direction)`
- [ ] Call `self._virtual_table.rebuild_headers()`
- [ ] Call `self._virtual_table.rebuild_row_pool()`
- [ ] Call `self._refresh_list()` after rebuild
- [ ] Ensure swap and sort are distinct branches — swap must NOT call `set_sort()`
- [ ] Verify: pattern matches PlanetListWindow (lines ~296-304) which handles swap correctly

**Notes:**

### Task 1.2: Add tests for swap_column handling [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Add test: `test_column_swap_calls_swap_column_on_manager` — mock `check_header_presses` to return `{'swap_column': (col_dict, 1), 'sort_column': None}`, verify `column_manager.swap_column()` called with correct args
- [ ] Add test: `test_column_swap_rebuilds_headers_and_rows` — verify `rebuild_headers()` and `rebuild_row_pool()` called after swap
- [ ] Add test: `test_column_swap_does_not_set_sort` — verify `set_sort()` NOT called when swap event fires
- [ ] Run: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` — all pass

**Notes:**

### Task 1.3: Verify table infrastructure tests [Simple]
**Tests:** `pytest tests/unit/ui/components/table/`

- [ ] Run `pytest tests/unit/ui/components/table/` — all 39+ tests pass (column_manager, header, virtual_table)
- [ ] Run `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` — full suite passes
- [ ] Run `pytest tests/ --testmon` — no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
