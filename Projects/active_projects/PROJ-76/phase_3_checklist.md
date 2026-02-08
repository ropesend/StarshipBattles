# Phase 3: Column System

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-76 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add configurable columns

---

## Tasks

### Task 3.1: Define column configuration [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Define `self.columns` list with column definitions:
  - `{'id': 'portrait', 'width': 50, 'title': '', 'type': 'image', 'visible': True}`
  - `{'id': 'location', 'width': 180, 'title': 'Location', 'visible': True}`
  - `{'id': 'system', 'width': 120, 'title': 'System', 'visible': True}`
  - `{'id': 'sector', 'width': 80, 'title': 'Sector', 'visible': True}`
  - `{'id': 'queue_count', 'width': 80, 'title': 'Items', 'visible': True}`
  - `{'id': 'first_item', 'width': 150, 'title': 'Building', 'visible': True}`
  - `{'id': 'turns_left', 'width': 80, 'title': 'Turns', 'visible': True}`
  - `{'id': 'capabilities', 'width': 100, 'title': 'Can Build', 'visible': True}`
  - `{'id': 'build_rate', 'width': 80, 'title': 'Rate/Turn', 'visible': False}`
- [ ] Create `_get_visible_columns()` method
- [ ] Create `_get_column_value(source, col_id)` method for each column

**Notes:**

---

### Task 3.2: Render columns dynamically [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** Manual test - verify columns display correctly

- [ ] Update header row to use visible columns
- [ ] Update row rendering to use visible columns
- [ ] Calculate column x positions dynamically

**Notes:**

---

### Task 3.3: Add column visibility toggles in sidebar [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** Manual test - toggle columns

- [ ] Add "Columns" section in sidebar
- [ ] Add checkbox button for each column: `[x] Column Name` / `[ ] Column Name`
- [ ] Handle click to toggle `col['visible']`
- [ ] Rebuild header and rows on toggle

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Manual test: All columns display correctly
- [ ] Manual test: Column visibility toggles work
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
