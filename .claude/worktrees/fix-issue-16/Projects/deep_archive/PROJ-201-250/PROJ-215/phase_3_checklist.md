# Phase 3: Add Sidebar with Column Toggles

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-215 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create a sidebar panel for the Event Log window with column visibility checkboxes, following the FleetReport/PlanetList pattern.

---

## Tasks

### Task 3.1: Create EventLogSidebar class [Medium]
**File:** `game/ui/screens/event_log_sidebar.py` (new file)
**Tests:** `pytest tests/unit/ui/screens/test_event_log_sidebar.py`
**Reference:** `game/ui/screens/fleet_report_sidebar.py` lines 347-375

- [x] Create `EventLogSidebar` class
- [x] Constructor takes: `panel` (UIPanel container), `manager`, `column_manager` (TableColumnManager), `on_column_toggle` callback
- [x] Implement `_build_column_section()` using `column_manager.get_toggleable_columns()`
- [x] Use `[x]`/`[ ]` button pattern with `object_id=f"#column_{col_id}"` and `btn.col_ref = col`
- [x] Store `self.column_buttons: Dict[str, UIButton]`
- [x] Add `COLUMNS` label header
- [x] Implement `handle_button_click(ui_element)` → returns column_id if column toggle, else None
- [x] Implement `refresh_button_labels()` to update `[x]`/`[ ]` text after toggle

**Notes:** Created following FleetReportSidebar pattern exactly.

### Task 3.2: Integrate sidebar into EventLogWindow [Medium]
**File:** `game/ui/screens/event_log_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [x] Add `SIDEBAR_WIDTH = 180` constant
- [x] In `_init_layout()`: Create left sidebar UIPanel of width `SIDEBAR_WIDTH`
- [x] Shift table panel right by `SIDEBAR_WIDTH` and reduce its width
- [x] Create `EventLogSidebar` instance, passing `self.column_manager`
- [x] In `process_event()`: Handle sidebar column toggle clicks → toggle column → rebuild table
- [x] Rebuild sequence: `rebuild_headers()` → `rebuild_row_pool()` → `force_update()` → `update_visible_rows()`

**Notes:** Header panel also shifted right by SIDEBAR_WIDTH.

### Task 3.3: Write sidebar tests [Medium]
**File:** `tests/unit/ui/screens/test_event_log_sidebar.py` (new file)
**Tests:** `pytest tests/unit/ui/screens/test_event_log_sidebar.py`

- [x] Test sidebar creates correct number of column toggle buttons
- [x] Test `handle_button_click()` returns column_id for column buttons
- [x] Test `handle_button_click()` returns None for non-column buttons
- [x] Test `refresh_button_labels()` updates text to reflect visibility state

**Notes:** 14 tests covering all sidebar functionality.

### Task 3.4: Update EventLogWindow tests [Simple]
**File:** `tests/unit/ui/screens/test_event_log_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [x] Update any tests that depend on window layout (table positioning)
- [x] Add test verifying column toggle integration
- [x] Run tests, verify all pass

**Notes:** Added TestEventLogSidebarIntegration test class.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
