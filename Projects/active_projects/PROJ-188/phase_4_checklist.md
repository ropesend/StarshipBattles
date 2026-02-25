# Phase 4: Migrate Empire Build Queue

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-188 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate Empire Build Queue to VirtualTable. Gains virtual scrolling it didn't have. Preserve EventBus/MVVM pattern.

---

## Tasks

### Task 4.1: Create BuildQueueDataSource [Medium]
**File:** `game/ui/screens/empire_build_queue_data_source.py`
**Tests:** `tests/unit/ui/screens/test_build_queue_data_source.py`

- [ ] Write tests for BuildQueueDataSource:
  - `get_cell_value()` for location, system, sector, queue_count, first_item, turns_left, capabilities, build_rate columns
  - `get_cell_value()` for resource rate columns (res_metals_rate, etc.)
  - `get_cell_value()` for resource total columns (res_metals_total, etc.)
  - `get_columns()` returns filter_mgr.columns
  - `get_row_count()` returns len(viewmodel.filtered_sources)
- [ ] Create `BuildQueueDataSource(ITableDataSource)`:
  - Constructor: `__init__(viewmodel: EmpireBuildQueueViewModel, filter_mgr: BuildQueueFilterManager, galaxy)`
  - Port value extraction from `empire_build_queue_window.py` `_get_column_value()` pattern:
    - 'location' → `source.display_name`
    - 'system' → `get_system_name(source, galaxy)`
    - 'sector' → `get_sector_text(source)`
    - Other columns → delegate to `viewmodel.get_column_value(source, col_id)`
  - `get_row_count()`: `len(viewmodel.filtered_sources)`
  - `get_columns()`: `filter_mgr.columns` (deep copy)
- [ ] Verify: `pytest tests/unit/ui/screens/test_build_queue_data_source.py -v` passes

**Notes:**

---

### Task 4.2: Wire EmpireBuildQueueWindow to VirtualTable [Complex]
**File:** `game/ui/screens/empire_build_queue_window.py` (modify)
**Tests:** `tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Replace imports:
  - Remove: `from game.ui.screens.planet_list_columns import ColumnManager`
  - Add: `from game.ui.components.table import VirtualTable, TableColumnManager, MultiSelect`
  - Add: `from game.ui.screens.empire_build_queue_data_source import BuildQueueDataSource`
- [ ] Update `__init__()`:
  - Replace `self.column_mgr = ColumnManager(columns, manager, header_container, header_height)` with `self.column_manager = TableColumnManager(self._filter_mgr.columns)`
  - Create `self.data_source = BuildQueueDataSource(self._viewmodel, self._filter_mgr, self.galaxy)`
  - Create `self.selection = MultiSelect()`
  - Create `self.virtual_table = VirtualTable(list_panel, manager, self.data_source, self.column_manager, self.selection, row_height=UIConfig.ROW_HEIGHT_LARGE, header_height=UIConfig.HEADER_HEIGHT)`
  - Remove `self.row_elements` list (no longer needed)
- [ ] Update `_refresh_list()`:
  - Remove: label creation loop (was creating UILabel per source)
  - Replace with: `self.virtual_table.update_scroll_bar()` + `self.virtual_table.update_visible_rows()`
  - Sync selection: `self.selection.set_selected(self._viewmodel.selected_indices)`
- [ ] Update click handling:
  - Replace manual row click detection (was checking UILabel click targets) with `self.virtual_table.handle_click(pos, ctrl_held)`
  - Navigation logic (re-click = navigate): check if clicked index matches previous selection
  - Sync selection back to ViewModel: `self._viewmodel.select_source(index, ctrl_held)`
- [ ] Update header handling:
  - Replace `self.column_mgr.handle_header_clicks()` with `self.virtual_table.check_header_presses()`
  - Handle sort: `self.column_manager.set_sort(col_id)` → re-sort via filter_mgr → refresh
  - Handle swap: `self.column_manager.swap_column(col, dir)` → rebuild
- [ ] Update column visibility toggles:
  - Replace: `self.column_mgr.toggle_visibility(col_id)` with `self.column_manager.toggle_column(col_id)`
  - Rebuild virtual table after changes
- [ ] Keep EventBus subscriptions (FILTERS_APPLIED, SELECTION_CHANGED, SOURCES_CHANGED):
  - These trigger `_refresh_list()` which now uses VirtualTable
- [ ] Keep batch operations (batch add to selected queues)
- [ ] Keep navigation logic (double-click / re-click navigates to hex build screen)
- [ ] Update existing tests (mock structures may need adjustment)
- [ ] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_*.py -v` passes

**Notes:**

---

### Task 4.3: Phase verification [Simple]
**Tests:** `pytest tests/unit/ui/ -v` and `pytest tests/ --testmon`

- [ ] Run `pytest tests/unit/ui/ -v` — all UI tests pass
- [ ] Run `pytest tests/ --testmon` — no regressions
- [ ] Verify `empire_build_queue_window.py` no longer imports from `planet_list_columns`
- [ ] Verify `planet_list_columns.ColumnManager` now has 0 reverse dependencies (ready for deletion in Phase 6)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] EmpireBuildQueueWindow uses VirtualTable + BuildQueueDataSource + MultiSelect
- [ ] Build queue now has virtual scrolling
- [ ] EventBus integration preserved (FILTERS_APPLIED, SELECTION_CHANGED events still work)
- [ ] Navigation logic preserved (re-click navigates to hex build screen)
- [ ] Batch operations preserved
- [ ] All existing build queue tests pass
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
