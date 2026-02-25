# Phase 2: Migrate Fleet Report

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-188 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Validate the generic architecture by migrating the most complex list (Fleet Report: multi-select, images, 19 columns, ~158 tests).

---

## Tasks

### Task 2.1: Create FleetDataSource [Complex]
**File:** `game/ui/screens/fleet_data_source.py`
**Tests:** `tests/unit/ui/screens/test_fleet_data_source.py`

- [ ] Write tests for FleetDataSource value extraction (port assertions from `tests/unit/ui/test_column_manager.py` value extraction tests):
  - Serial column: returns `ship.get_display_id()`
  - Design column: returns design name
  - HP% column: returns formatted percentage
  - Status column: returns OK/DAMAGED/DERELICT/DESTROYED
  - Speed, tonnage, warp, spaceyard, transport, resources, cargo columns
  - Special capability columns (can_destroy_planet, etc.)
  - Image columns: portrait and topdown return None for text extraction
  - get_cell_image() returns cached scaled surfaces for image columns
  - get_columns() returns DEFAULT_FLEET_COLUMNS (19 columns)
  - get_row_count() delegates to view_model.get_filtered_ships()
- [ ] Create `FleetDataSource(ITableDataSource)`:
  - Port `DEFAULT_FLEET_COLUMNS` from `game/ui/screens/column_manager.py:17-46`
  - Port `SPECIAL_CAPABILITY_COLUMNS` from `game/ui/screens/column_manager.py:47-57`
  - Port `get_column_value()` logic from `game/ui/screens/column_manager.py:141-229`
  - Port image cache logic from `game/ui/screens/fleet_list_renderer.py:316-352`
  - Constructor: `__init__(view_model: FleetListViewModel)`
  - Methods: `get_row_count()`, `get_cell_value()`, `get_columns()`, `get_cell_image()`
  - Keep late imports for FleetSpeedCalculator, ShipStatsCalculator, FleetCapabilityCalculator (same pattern as existing)
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_data_source.py -v` passes

**Notes:**

---

### Task 2.2: Wire FleetReportWindow to VirtualTable [Complex]
**File:** `game/ui/screens/fleet_report_window.py` (modify)
**Tests:** `tests/unit/ui/screens/test_fleet_report_window.py`, `tests/unit/ui/screens/test_fleet_report_window_multi_select.py`

- [ ] Replace imports:
  - Remove: `from game.ui.screens.fleet_list_renderer import FleetListRenderer`
  - Remove: `from game.ui.screens.column_manager import ColumnManager`
  - Add: `from game.ui.components.table import VirtualTable, TableColumnManager, MultiSelect`
  - Add: `from game.ui.screens.fleet_data_source import FleetDataSource, DEFAULT_FLEET_COLUMNS`
- [ ] Update `__init__()`:
  - Replace `self.column_manager = ColumnManager()` with `self.column_manager = TableColumnManager(DEFAULT_FLEET_COLUMNS)`
  - Create `self.data_source = FleetDataSource(self.view_model)`
  - Create `self.selection = MultiSelect()`
  - Replace `self.list_renderer = FleetListRenderer(panel, manager, column_manager, view_model, ...)` with `self.virtual_table = VirtualTable(panel, manager, self.data_source, self.column_manager, self.selection, row_height=..., header_height=...)`
- [ ] Update `refresh_list()`:
  - Replace `self.list_renderer.update_scroll_bar(filtered_ships)` with `self.virtual_table.update_scroll_bar()`
  - Replace `self.list_renderer.update_visible_rows(filtered_ships, self.selected_indices)` with `self.virtual_table.update_visible_rows()`
  - Selection state now in `self.selection` instead of `self.selected_indices`
- [ ] Update click handling:
  - Replace `self.list_renderer.find_clicked_row(pos)` with `self.virtual_table.handle_click(pos, ctrl_held)`
  - Selection indices from `self.selection.get_selected_indices()` instead of manual set tracking
- [ ] Update header handling (in `update()` method):
  - Replace `self.list_renderer.check_header_presses()` with `self.virtual_table.check_header_presses()`
- [ ] Update column toggle/swap:
  - Replace `self.column_manager.toggle_column(col_id)` with `self.column_manager.toggle_column(col_id)` (same API on TableColumnManager)
  - Replace `self.column_manager.swap_column(col, direction)` with `self.column_manager.swap_column(col, direction)`
  - Call `self.virtual_table.rebuild_headers()` and `self.virtual_table.rebuild_row_pool()` after changes
- [ ] Update `_on_remove_selected_ships()`:
  - Get selected ships via `self.selection.get_selected_indices()` and `self.data_source`
  - Clear selection after removal: `self.selection.clear()`
- [ ] Update sidebar integration:
  - Column visibility toggles: use `self.column_manager` (TableColumnManager)
  - Filter toggles: use `self.view_model` (unchanged)
- [ ] Update existing window tests (mock structures may need adjustment for new component types)
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py -v` passes

**Notes:**

---

### Task 2.3: Migrate column manager tests [Medium]
**File:** `tests/unit/ui/test_column_manager.py` (split/update)

- [ ] Identify which tests in `test_column_manager.py` test column config (get, toggle, swap, width) vs. value extraction (get_column_value for ships)
- [ ] Column config tests: verify they're covered by `tests/unit/ui/components/table/test_column_manager.py` (from Phase 1 Task 1.4). If not, add missing coverage there.
- [ ] Value extraction tests: migrate to `tests/unit/ui/screens/test_fleet_data_source.py` (from Task 2.1). Update to use FleetDataSource instead of old ColumnManager.
- [ ] Mark `tests/unit/ui/test_column_manager.py` for deletion in Phase 6 (or update imports to use new classes now)
- [ ] Verify: all migrated tests pass

**Notes:**

---

### Task 2.4: Phase verification [Simple]
**Tests:** `pytest tests/unit/ui/ -v` and `pytest tests/ --testmon`

- [ ] Run `pytest tests/unit/ui/ -v` — all UI tests pass
- [ ] Run `pytest tests/ --testmon` — no regressions
- [ ] Verify `fleet_report_window.py` no longer imports from `fleet_list_renderer` or old `column_manager`
- [ ] Verify `FleetListRenderer` has only 0 reverse dependencies (no other file imports it)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] FleetReportWindow uses VirtualTable + FleetDataSource + MultiSelect
- [ ] All ~158 fleet-related tests pass (or adapted equivalents)
- [ ] FleetDataSource has comprehensive value extraction tests
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
