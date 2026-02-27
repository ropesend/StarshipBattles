# Phase 1: Generic Components (Foundation)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-188 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the reusable table infrastructure in `game/ui/components/table/` with full test coverage.

---

## Tasks

### Task 1.1: Package structure [Simple]
**Tests:** N/A (package init files)

- [x] Create `game/ui/components/__init__.py` (empty)
- [x] Create `game/ui/components/table/__init__.py` (empty initially, exports added in Task 1.7)
- [x] Create `tests/unit/ui/components/__init__.py`
- [x] Create `tests/unit/ui/components/table/__init__.py`
- [x] Verify: directories exist, no import errors

**Notes:** Package structure created successfully.

---

### Task 1.2: ITableDataSource base class [Medium]
**File:** `game/ui/components/table/data_source.py`
**Tests:** `tests/unit/ui/components/table/test_data_source.py`

- [x] Write tests for ITableDataSource interface contract:
  - Required methods raise NotImplementedError when not overridden
  - Optional methods return defaults (get_cell_image → None, get_row_highlight → None)
  - get_visible_columns filters correctly by `visible` key
  - Test with a mock subclass implementing required methods
- [x] Create `ITableDataSource` base class
- [x] Verify: `pytest tests/unit/ui/components/table/test_data_source.py -v` passes

**Notes:** 7 tests passing.

---

### Task 1.3: ISelectionStrategy + implementations [Medium]
**File:** `game/ui/components/table/selection.py`
**Tests:** `tests/unit/ui/components/table/test_selection.py`

- [x] Write tests for all 3 strategies:
  - **SingleSelect**: `handle_click(5, False)` → `{5}`; `handle_click(3, False)` → `{3}`; `handle_click(3, True)` → `{3}` (Ctrl ignored); `clear()` → empty; `set_selected({7})` → `{7}`
  - **MultiSelect**: `handle_click(5, False)` → `{5}`; `handle_click(3, True)` → `{5, 3}`; `handle_click(5, True)` on `{5,3}` → `{3}` (toggle off); `handle_click(3, True)` on `{3}` → `{3}` (cannot deselect last); `clear()` → empty
  - **NoSelect**: `handle_click(any, any)` → `set()`; `get_selected_indices()` → `set()`; `set_selected({1,2})` → still `set()`
- [x] Create `ISelectionStrategy` base class
- [x] Implement `SingleSelect(ISelectionStrategy)`
- [x] Implement `MultiSelect(ISelectionStrategy)` — Ctrl+click toggles, cannot remove last selected
- [x] Implement `NoSelect(ISelectionStrategy)` — always empty
- [x] Verify: `pytest tests/unit/ui/components/table/test_selection.py -v` passes

**Notes:** 20 tests passing.

---

### Task 1.4: TableColumnManager [Medium]
**File:** `game/ui/components/table/column_manager.py`
**Tests:** `tests/unit/ui/components/table/test_column_manager.py`

- [x] Write tests for column management:
  - Constructor deep-copies columns (mutation safety)
  - `get_columns()` returns all columns
  - `get_visible_columns()` filters by visible=True
  - `get_column('id')` returns correct column or None
  - `toggle_column('id')` toggles visible, returns new state
  - `swap_column(col, 1)` moves right, `swap_column(col, -1)` moves left
  - `swap_column` returns False at edges (can't swap past first/last)
  - `get_total_visible_width()` sums visible column widths
  - `is_image_column(col)` checks col.get('type') == 'image'
  - `set_sort('col_id')` sets sort_column_id; calling again toggles sort_descending
  - `set_sort('different_id')` resets sort_descending to False
- [x] Create `TableColumnManager`
- [x] Verify: `pytest tests/unit/ui/components/table/test_column_manager.py -v` passes

**Notes:** 17 tests passing.

---

### Task 1.5: TableHeader [Complex]
**File:** `game/ui/components/table/header.py`
**Tests:** `tests/unit/ui/components/table/test_header.py`

- [x] Write tests for header creation and interaction:
  - Constructor creates header with correct number of buttons per visible column
  - `rebuild()` creates 3 buttons per column (left arrow, title, right arrow)
  - Sort indicator shows ▲/▼ on sorted column
  - Left arrow hidden for first visible column
  - Right arrow hidden for last visible column
  - `check_presses()` returns `{'swap_column': None, 'sort_column': None}` when no press
  - `kill()` cleans up all widgets
- [x] Create `TableHeader`
- [x] Port header button pattern from `game/ui/screens/fleet_list_renderer.py:103-160`:
  - Arrow buttons: 20px wide, store `col_ref` and `direction` attributes
  - Title buttons: `column_width - 40` wide, store `sort_col_ref` attribute
  - Sort indicator: " ▲" (ascending) or " ▼" (descending) appended to title text
- [x] Verify: `pytest tests/unit/ui/components/table/test_header.py -v` passes

**Notes:** 10 tests passing.

---

### Task 1.6: VirtualTable [Complex]
**File:** `game/ui/components/table/virtual_table.py`
**Tests:** `tests/unit/ui/components/table/test_virtual_table.py`

- [x] Write tests for VirtualTable:
  - Constructor creates header panel, list viewport, scroll bar
  - `rebuild_row_pool()` creates `(visible_height / row_height) + 2` rows
  - Each row has UIPanel bg + UILabel/UIImage widgets per visible column
  - `update_visible_rows()` uses scroll math: `start_percentage * total_height`
  - `update_visible_rows()` dirty tracking: skips if scroll_pct + row_count unchanged
  - `update_scroll_bar()` sets visible percentage correctly
  - `find_clicked_row(pos)` returns correct row index or -1
  - `handle_click(pos, ctrl_held)` delegates to selection strategy
  - Selection highlighting: selected rows get Color(60,80,120), unselected get Color(35,35,35)
  - Image columns: calls `data_source.get_cell_image()` for image-type columns
  - `force_update()` resets dirty tracking state
  - `kill()` cleans up all widgets
- [x] Create `VirtualTable`
- [x] Implement core methods
- [x] Selection highlighting using `bg_panel.background_colour`
- [x] Image column handling
- [x] Dirty tracking optimization
- [x] Verify: `pytest tests/unit/ui/components/table/test_virtual_table.py -v` passes

**Notes:** 11 tests passing.

---

### Task 1.7: Package exports + regression check [Simple]
**Tests:** `pytest tests/unit/ui/components/ -v` and `pytest tests/ --testmon`

- [x] Update `game/ui/components/table/__init__.py` with all public exports
- [x] Verify: `pytest tests/unit/ui/components/ -v` — all new tests pass (65 passed)
- [x] Verify: `pytest tests/ -n 12` — no regressions to existing tests (12531 passed, 1 skipped)

**Notes:** Full test suite passing. testmon had Windows path issues, used full pytest run instead.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All 6 test files in `tests/unit/ui/components/table/` pass
- [x] Import from `game.ui.components.table` works (VirtualTable, ITableDataSource, etc.)
- [x] No existing tests broken: `pytest tests/ -n 12`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
