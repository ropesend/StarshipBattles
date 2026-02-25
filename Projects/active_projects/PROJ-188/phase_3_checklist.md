# Phase 3: Migrate Planet List

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-188 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Second migration — Planet List with single select, func/attr column extraction, icon caching with rotation.

---

## Tasks

### Task 3.1: Create PlanetDataSource [Complex]
**File:** `game/ui/screens/planet_data_source.py`
**Tests:** `tests/unit/ui/screens/test_planet_data_source.py`

- [ ] Write tests for PlanetDataSource:
  - `get_cell_value()` with `func` callable columns (e.g., `get_system_name`, `get_owner_name`)
  - `get_cell_value()` with `attr` dotted path columns (e.g., `"surface_gravity"`, `"planet_type.name"`)
  - `get_cell_value()` with `fmt` format string (e.g., `"{:.2f}"` for float formatting)
  - `get_cell_value()` returns "?" for missing attributes
  - `get_cell_image()` for icon column returns cached scaled Surface
  - `get_cell_image()` handles planet rotation in cache key
  - `get_cell_image()` returns fallback blank surface for missing images
  - `get_columns()` returns planet column definitions
  - `get_row_count()` returns len(filtered_planets)
  - `update_data(filtered_planets)` updates internal data reference
- [ ] Create `PlanetDataSource(ITableDataSource)`:
  - Constructor: `__init__(columns: List[Dict], galaxy, empire)`
  - Port value extraction from `game/ui/screens/planet_list_filters.py:147-172` (func/attr/fmt pattern)
  - Port icon caching from `game/ui/screens/planet_list_renderer.py:142-176` (AssetManager + rotation)
  - `update_data(filtered_planets: list)` — set current data list
  - `get_row_count()`, `get_cell_value()`, `get_columns()`, `get_cell_image()`
  - Image cache: dict keyed by `f"icon_{planet.image_id}_{planet.image_rotation or 0}"`
  - Blank surface fallback: `pygame.Surface((40, 40))`
- [ ] Verify: `pytest tests/unit/ui/screens/test_planet_data_source.py -v` passes

**Notes:**

---

### Task 3.2: Wire PlanetListWindow to VirtualTable [Complex]
**File:** `game/ui/screens/planet_list_window.py` (modify)
**Tests:** `tests/unit/ui/screens/test_planet_list_components.py`

- [ ] Replace imports:
  - Remove: `from game.ui.screens.planet_list_renderer import VirtualListRenderer`
  - Remove: `from game.ui.screens.planet_list_columns import ColumnManager`
  - Add: `from game.ui.components.table import VirtualTable, TableColumnManager, SingleSelect`
  - Add: `from game.ui.screens.planet_data_source import PlanetDataSource`
- [ ] Update `__init__()`:
  - Replace `self.column_mgr = ColumnManager(columns, manager, header_container, header_height)` with `self.column_manager = TableColumnManager(self.columns)`
  - Create `self.data_source = PlanetDataSource(self.columns, self.galaxy, self.empire)`
  - Create `self.selection = SingleSelect()`
  - Replace `self.renderer = VirtualListRenderer(list_panel, row_height, manager)` with `self.virtual_table = VirtualTable(list_panel, manager, self.data_source, self.column_manager, self.selection, row_height=..., header_height=...)`
- [ ] Update `refresh_list()`:
  - Keep: `gather_planets()`, `filter_planets()`, `sort_planets()` calls (unchanged)
  - Add: `self.data_source.update_data(self.filtered_planets)`
  - Replace: `self.renderer.update_visible_rows(filtered_planets, scroll_bar)` with `self.virtual_table.update_visible_rows()`
  - Replace: `self.renderer.force_update()` with `self.virtual_table.force_update()`
- [ ] Update `process_event()`:
  - Replace: `self.renderer.get_clicked_planet_index(mouse_pos, list_abs_rect, scroll_bar, total_planets)` with `self.virtual_table.handle_click(mouse_pos)`
  - Selection via `self.selection.get_selected_indices()`
- [ ] Update `update()` method (header press checks):
  - Replace: `self.column_mgr.handle_header_clicks()` with `self.virtual_table.check_header_presses()`
  - Handle sort changes: `self.column_manager.set_sort(col_id)` → refresh
  - Handle column swaps: `self.column_manager.swap_column(col, dir)` → rebuild headers + row pool
- [ ] Update column visibility toggles:
  - Replace: `self.column_mgr.toggle_visibility(col_id)` with `self.column_manager.toggle_column(col_id)`
  - Call `self.virtual_table.rebuild_headers()` and `self.virtual_table.rebuild_row_pool()` after changes
- [ ] Update sort_planets calls to use `self.column_manager.sort_column_id` and `self.column_manager.sort_descending`
- [ ] Keep preset system logic (capture/apply state):
  - Preset capture: read column visibility/ordering from `self.column_manager`
  - Preset apply: update column manager then rebuild virtual table
  - May need to adapt preset serialization for TableColumnManager API
- [ ] Update existing tests (mock structures may need adjustment)
- [ ] Verify: `pytest tests/unit/ui/screens/test_planet_list_components.py tests/unit/ui/screens/test_planet_list_filters.py -v` passes

**Notes:**

---

### Task 3.3: Phase verification [Simple]
**Tests:** `pytest tests/unit/ui/ -v` and `pytest tests/ --testmon`

- [ ] Run `pytest tests/unit/ui/ -v` — all UI tests pass
- [ ] Run `pytest tests/ --testmon` — no regressions
- [ ] Verify `planet_list_window.py` no longer imports from `planet_list_renderer` or `planet_list_columns`
- [ ] Verify `VirtualListRenderer` has 0 reverse dependencies
- [ ] Verify `planet_list_columns.ColumnManager` only imported by `empire_build_queue_window.py` (migrated in Phase 4)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] PlanetListWindow uses VirtualTable + PlanetDataSource + SingleSelect
- [ ] All planet list tests pass (or adapted equivalents)
- [ ] PlanetDataSource has comprehensive tests (func, attr, fmt, images)
- [ ] Preset system still works with new TableColumnManager
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
