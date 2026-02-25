# Phase 4: Migrate Empire Build Queue

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-188 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate Empire Build Queue to VirtualTable. Gains virtual scrolling it didn't have. Preserve EventBus/MVVM pattern.

---

## Tasks

### Task 4.1: Create BuildQueueDataSource [Medium]
**File:** `game/ui/screens/empire_build_queue_data_source.py`
**Tests:** `tests/unit/ui/screens/test_build_queue_data_source.py`

- [x] Write tests for BuildQueueDataSource:
  - `get_cell_value()` for location, system, sector, queue_count, first_item, turns_left, capabilities, build_rate columns
  - `get_cell_value()` for resource rate columns (res_metals_rate, etc.)
  - `get_cell_value()` for resource total columns (res_metals_total, etc.)
  - `get_columns()` returns filter_mgr.columns
  - `get_row_count()` returns len(viewmodel.filtered_sources)
- [x] Create `BuildQueueDataSource(ITableDataSource)`:
  - Constructor: `__init__(viewmodel: EmpireBuildQueueViewModel, filter_mgr: BuildQueueFilterManager, galaxy)`
  - Port value extraction from `empire_build_queue_window.py` `_get_column_value()` pattern:
    - 'location' → `source.display_name`
    - 'system' → `get_system_name(source, galaxy)`
    - 'sector' → `get_sector_text(source)`
    - Other columns → delegate to `viewmodel.get_column_value(source, col_id)`
  - `get_row_count()`: `len(viewmodel.filtered_sources)`
  - `get_columns()`: `filter_mgr.columns` (deep copy)
- [x] Verify: `pytest tests/unit/ui/screens/test_build_queue_data_source.py -v` passes

**Notes:** 27 tests created and passing.

---

### Task 4.2: Wire EmpireBuildQueueWindow to VirtualTable [Complex]
**File:** `game/ui/screens/empire_build_queue_window.py` (modify)
**Tests:** `tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Replace imports:
  - Remove: `from game.ui.screens.planet_list_columns import ColumnManager`
  - Add: `from game.ui.components.table import VirtualTable, TableColumnManager, MultiSelect`
  - Add: `from game.ui.screens.empire_build_queue_data_source import BuildQueueDataSource`
- [x] Update `__init__()`:
  - Replace `self.column_mgr = ColumnManager(columns, manager, header_container, header_height)` with `self._column_manager = TableColumnManager(self._filter_mgr.columns)`
  - Create `self._data_source = BuildQueueDataSource(self._viewmodel, self._filter_mgr, self.galaxy)`
  - Create `self._selection = MultiSelect()`
  - Create `self._virtual_table = VirtualTable(main_panel, manager, self._data_source, self._column_manager, self._selection, ...)`
  - Remove `self.row_elements` list (no longer needed)
- [x] Update `_refresh_list()`:
  - Remove: label creation loop (was creating UILabel per source)
  - Replace with: `self._virtual_table.update_scroll_bar()` + `self._virtual_table.update_visible_rows()`
  - Sync selection: `self._selection.set_selected(self._viewmodel.selected_indices)`
- [x] Update click handling:
  - Replace manual row click detection with `self._virtual_table.find_clicked_row(pos)`
  - Navigation logic (re-click = navigate): check if clicked index matches previous selection
  - Sync selection back to ViewModel: `self._viewmodel.select_source(index, ctrl_held)`
- [x] Update header handling:
  - Replace `self.column_mgr.handle_header_clicks()` with `self._virtual_table.check_header_presses()`
  - Handle sort: `self._column_manager.set_sort(col_id)` → re-sort via filter_mgr → refresh
- [x] Update column visibility toggles:
  - Rebuild virtual table headers and row pool after changes
- [x] Keep EventBus subscriptions (FILTERS_APPLIED, SELECTION_CHANGED, SOURCES_CHANGED):
  - These trigger `_refresh_list()` which now uses VirtualTable
- [x] Keep batch operations (batch add to selected queues)
- [x] Keep navigation logic (double-click / re-click navigates to hex build screen)
- [x] Update existing tests (mock structures updated for _column_manager, _virtual_table, etc.)
- [x] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_*.py -v` passes

**Notes:** All 262 build queue tests pass (including 118 window tests + 27 data source tests + others).

---

### Task 4.3: Phase verification [Simple]
**Tests:** `pytest tests/unit/ui/ -v` and `pytest tests/`

- [x] Run `pytest tests/unit/ui/ -v` — all 3152 UI tests pass
- [x] Run `pytest tests/ -n 12` — all 12,628 tests pass, 1 skipped
- [x] Verify `empire_build_queue_window.py` no longer imports from `planet_list_columns`
- [x] Verify `planet_list_columns.ColumnManager` now has 0 reverse dependencies (ready for deletion in Phase 6)

**Notes:** planet_list_columns.ColumnManager has 0 reverse dependencies in game/ui/screens/. Ready for Phase 6 deletion.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] EmpireBuildQueueWindow uses VirtualTable + BuildQueueDataSource + MultiSelect
- [x] Build queue now has virtual scrolling
- [x] EventBus integration preserved (FILTERS_APPLIED, SELECTION_CHANGED events still work)
- [x] Navigation logic preserved (re-click navigates to hex build screen)
- [x] Batch operations preserved
- [x] All existing build queue tests pass
- [x] No regressions: full test suite passes (12,628 passed, 1 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
