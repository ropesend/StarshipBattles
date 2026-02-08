# Phase 3: Column System

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-76 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add configurable columns

---

## Tasks

### Task 3.1: Define column configuration [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Define `self.columns` list with column definitions (8 columns: location, system, sector, queue_count, first_item, turns_left, capabilities, build_rate)
  - Skipped portrait column (no asset resolver yet, deferred)
- [x] Create `_get_visible_columns()` method
- [x] Create `_get_column_value(source, col_id)` method for each column

**Notes:** Added _get_system_name(), _get_sector_text(), _get_turns_left_text() formatters. build_rate returns fixed "1/turn".

---

### Task 3.2: Render columns dynamically [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** Manual test - verify columns display correctly

- [x] Update header row to use visible columns
- [x] Update row rendering to use visible columns
- [x] Calculate column x positions dynamically

**Notes:** _build_header_labels() and _refresh_list() now iterate _get_visible_columns(). Labels cleared/rebuilt on toggle.

---

### Task 3.3: Add column visibility toggles in sidebar [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** Manual test - toggle columns

- [x] Add "Columns" section in sidebar
- [x] Add checkbox button for each column: `[x] Column Name` / `[ ] Column Name`
- [x] Handle click to toggle `col['visible']`
- [x] Rebuild header and rows on toggle

**Notes:** _build_sidebar_column_toggles() creates buttons, _handle_column_toggle_click() toggles + rebuilds. toggle_column_visibility() is a clean public API. 26 new tests added.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Manual test: All columns display correctly
- [x] Manual test: Column visibility toggles work
- [x] No regressions: `pytest tests/ --testmon`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
