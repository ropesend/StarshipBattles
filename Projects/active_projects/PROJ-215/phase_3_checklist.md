# Phase 3: Add Sidebar with Column Toggles

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-215 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create a sidebar panel for the Event Log window with column visibility checkboxes, following the FleetReport/PlanetList pattern.

---

## Tasks

### Task 3.1: Create EventLogSidebar class [Medium]
**File:** `game/ui/screens/event_log_sidebar.py` (new file)
**Tests:** `pytest tests/unit/ui/screens/test_event_log_sidebar.py`
**Reference:** `game/ui/screens/fleet_report_sidebar.py` lines 347-375

- [ ] Create `EventLogSidebar` class
- [ ] Constructor takes: `panel` (UIPanel container), `manager`, `column_manager` (TableColumnManager), `on_column_toggle` callback
- [ ] Implement `_build_column_section()` using `column_manager.get_toggleable_columns()`
- [ ] Use `[x]`/`[ ]` button pattern with `object_id=f"#column_{col_id}"` and `btn.col_ref = col`
- [ ] Store `self.column_buttons: Dict[str, UIButton]`
- [ ] Add `COLUMNS` label header
- [ ] Implement `handle_button_click(ui_element)` → returns column_id if column toggle, else None
- [ ] Implement `refresh_button_labels()` to update `[x]`/`[ ]` text after toggle

**Notes:**

### Task 3.2: Integrate sidebar into EventLogWindow [Medium]
**File:** `game/ui/screens/event_log_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [ ] Add `SIDEBAR_WIDTH = 180` constant
- [ ] In `_init_layout()`: Create left sidebar UIPanel of width `SIDEBAR_WIDTH`
- [ ] Shift table panel right by `SIDEBAR_WIDTH` and reduce its width
- [ ] Create `EventLogSidebar` instance, passing `self.column_manager`
- [ ] In `process_event()`: Handle sidebar column toggle clicks → toggle column → rebuild table
- [ ] Rebuild sequence: `rebuild_headers()` → `rebuild_row_pool()` → `force_update()` → `update_visible_rows()`

**Notes:**

### Task 3.3: Write sidebar tests [Medium]
**File:** `tests/unit/ui/screens/test_event_log_sidebar.py` (new file)
**Tests:** `pytest tests/unit/ui/screens/test_event_log_sidebar.py`

- [ ] Test sidebar creates correct number of column toggle buttons
- [ ] Test `handle_button_click()` returns column_id for column buttons
- [ ] Test `handle_button_click()` returns None for non-column buttons
- [ ] Test `refresh_button_labels()` updates text to reflect visibility state

**Notes:**

### Task 3.4: Update EventLogWindow tests [Simple]
**File:** `tests/unit/ui/screens/test_event_log_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [ ] Update any tests that depend on window layout (table positioning)
- [ ] Add test verifying column toggle integration
- [ ] Run tests, verify all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
