# Phase 5: Migrate Event Log

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-188 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Simplest migration. Event Log gains virtual scrolling, sortable columns, and column-based display.

---

## Tasks

### Task 5.1: Create EventLogDataSource [Medium]
**File:** `game/ui/screens/event_log_data_source.py`
**Tests:** `tests/unit/ui/screens/test_event_log_data_source.py`

- [ ] Write tests for EventLogDataSource:
  - `get_columns()` returns EVENT_LOG_COLUMNS (3 columns: category, turn, message)
  - `get_row_count()` returns count of filtered events
  - `get_cell_value()` for 'category' column: returns category icon prefix + name
  - `get_cell_value()` for 'turn' column: returns str(turn)
  - `get_cell_value()` for 'message' column: returns message text
  - `set_filter("all")` shows all events
  - `set_filter("combat")` shows only combat events
  - `set_filter("production")` shows only production events
  - `set_filter("colonies")` shows only colonies events
  - Events sorted by turn descending (newest first)
  - `update_events(events)` replaces event data
- [ ] Define EVENT_LOG_COLUMNS:
  ```python
  EVENT_LOG_COLUMNS = [
      {'id': 'category', 'width': 90, 'title': 'Category', 'visible': True, 'sortable': True},
      {'id': 'turn', 'width': 60, 'title': 'Turn', 'visible': True, 'sortable': True},
      {'id': 'message', 'width': 500, 'title': 'Message', 'visible': True, 'sortable': True},
  ]
  ```
- [ ] Create `EventLogDataSource(ITableDataSource)`:
  - Constructor: `__init__(events: list, current_filter: str = "all")`
  - Category icon mapping from existing `CATEGORY_ICONS` dict (port from `event_log_window.py`)
  - `set_filter(category)`: Update filter, recompute filtered list (sorted by turn descending)
  - `update_events(events)`: Replace source data, reapply filter
  - `get_row_count()`, `get_cell_value()`, `get_columns()`
- [ ] Verify: `pytest tests/unit/ui/screens/test_event_log_data_source.py -v` passes

**Notes:**

---

### Task 5.2: Wire EventLogWindow to VirtualTable [Medium]
**File:** `game/ui/screens/event_log_window.py` (modify)
**Tests:** `tests/unit/ui/screens/test_event_log_window.py`

- [ ] Replace imports:
  - Add: `from game.ui.components.table import VirtualTable, TableColumnManager, NoSelect`
  - Add: `from game.ui.screens.event_log_data_source import EventLogDataSource, EVENT_LOG_COLUMNS`
- [ ] Update `__init__()`:
  - Create `self.data_source = EventLogDataSource(events)`
  - Create `self.column_manager = TableColumnManager(EVENT_LOG_COLUMNS)`
  - Create `self.virtual_table = VirtualTable(list_panel, manager, self.data_source, self.column_manager, NoSelect(), row_height=ROW_HEIGHT, header_height=HEADER_HEIGHT)`
  - Remove `self.row_labels` list
  - Remove `self.scroll_bar` (owned by VirtualTable now)
- [ ] Keep filter tab buttons (All, Combat, Production, Colonies)
- [ ] Update `_rebuild_list()`:
  - Replace label creation loop with:
    ```python
    self.data_source.set_filter(self.current_filter)
    self.virtual_table.update_scroll_bar()
    self.virtual_table.update_visible_rows()
    ```
  - Remove old `for label in self.row_labels: label.kill()` cleanup
- [ ] Update `process_event()`:
  - Keep filter button handling (UI_BUTTON_PRESSED for filter tabs)
  - On filter change: call `self._rebuild_list()` (same as before, but now delegates to VirtualTable)
- [ ] Update `set_filter()`:
  - Set `self.current_filter = category`
  - Call `self._rebuild_list()`
  - Call `self._update_filter_buttons()`
- [ ] Remove `get_filtered_events()` if no longer needed (filtering now in DataSource), or keep as delegate for backward compatibility
- [ ] Update existing tests (mock structures may need adjustment)
- [ ] Verify: `pytest tests/unit/ui/screens/test_event_log_window.py -v` passes

**Notes:**

---

### Task 5.3: Phase verification [Simple]
**Tests:** `pytest tests/unit/ui/ -v` and `pytest tests/ --testmon`

- [ ] Run `pytest tests/unit/ui/ -v` — all UI tests pass
- [ ] Run `pytest tests/ --testmon` — no regressions
- [ ] Event log now has virtual scrolling (verify with visual test if possible)
- [ ] Event log now has sortable column headers

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] EventLogWindow uses VirtualTable + EventLogDataSource + NoSelect
- [ ] Event log has virtual scrolling
- [ ] Event log has column headers with sort indicators
- [ ] Filter tabs still work (All/Combat/Production/Colonies)
- [ ] All existing event log tests pass
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
