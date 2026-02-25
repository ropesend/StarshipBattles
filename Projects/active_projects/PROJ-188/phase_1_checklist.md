# Phase 1: Generic Components (Foundation)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-188 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the reusable table infrastructure in `game/ui/components/table/` with full test coverage.

---

## Tasks

### Task 1.1: Package structure [Simple]
**Tests:** N/A (package init files)

- [ ] Create `game/ui/components/__init__.py` (empty)
- [ ] Create `game/ui/components/table/__init__.py` (empty initially, exports added in Task 1.7)
- [ ] Create `tests/unit/ui/components/__init__.py`
- [ ] Create `tests/unit/ui/components/table/__init__.py`
- [ ] Verify: directories exist, no import errors

**Notes:**

---

### Task 1.2: ITableDataSource base class [Medium]
**File:** `game/ui/components/table/data_source.py`
**Tests:** `tests/unit/ui/components/table/test_data_source.py`

- [ ] Write tests for ITableDataSource interface contract:
  - Required methods raise NotImplementedError when not overridden
  - Optional methods return defaults (get_cell_image → None, get_row_highlight → None)
  - get_visible_columns filters correctly by `visible` key
  - Test with a mock subclass implementing required methods
- [ ] Create `ITableDataSource` base class:
  ```python
  class ITableDataSource:
      def get_row_count(self) -> int: raise NotImplementedError
      def get_cell_value(self, row_index: int, column_id: str) -> str: raise NotImplementedError
      def get_columns(self) -> List[Dict[str, Any]]: raise NotImplementedError
      def get_visible_columns(self) -> List[Dict[str, Any]]:
          return [c for c in self.get_columns() if c.get('visible', True)]
      def get_cell_image(self, row_index: int, column_id: str) -> Optional[pygame.Surface]:
          return None
      def get_row_highlight(self, row_index: int) -> Optional[Tuple[int, int, int]]:
          return None
  ```
- [ ] Verify: `pytest tests/unit/ui/components/table/test_data_source.py -v` passes

**Notes:**

---

### Task 1.3: ISelectionStrategy + implementations [Medium]
**File:** `game/ui/components/table/selection.py`
**Tests:** `tests/unit/ui/components/table/test_selection.py`

- [ ] Write tests for all 3 strategies:
  - **SingleSelect**: `handle_click(5, False)` → `{5}`; `handle_click(3, False)` → `{3}`; `handle_click(3, True)` → `{3}` (Ctrl ignored); `clear()` → empty; `set_selected({7})` → `{7}`
  - **MultiSelect**: `handle_click(5, False)` → `{5}`; `handle_click(3, True)` → `{5, 3}`; `handle_click(5, True)` on `{5,3}` → `{3}` (toggle off); `handle_click(3, True)` on `{3}` → `{3}` (cannot deselect last); `clear()` → empty
  - **NoSelect**: `handle_click(any, any)` → `set()`; `get_selected_indices()` → `set()`; `set_selected({1,2})` → still `set()`
- [ ] Create `ISelectionStrategy` base class:
  ```python
  class ISelectionStrategy:
      def handle_click(self, index: int, ctrl_held: bool = False) -> set[int]: ...
      def get_selected_indices(self) -> set[int]: ...
      def clear(self) -> None: ...
      def set_selected(self, indices: set[int]) -> None: ...
  ```
- [ ] Implement `SingleSelect(ISelectionStrategy)`
- [ ] Implement `MultiSelect(ISelectionStrategy)` — Ctrl+click toggles, cannot remove last selected
- [ ] Implement `NoSelect(ISelectionStrategy)` — always empty
- [ ] Verify: `pytest tests/unit/ui/components/table/test_selection.py -v` passes

**Notes:**

---

### Task 1.4: TableColumnManager [Medium]
**File:** `game/ui/components/table/column_manager.py`
**Tests:** `tests/unit/ui/components/table/test_column_manager.py`

- [ ] Write tests for column management:
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
- [ ] Create `TableColumnManager`:
  ```python
  class TableColumnManager:
      def __init__(self, columns: List[Dict[str, Any]]):
          self._columns = [dict(c) for c in columns]
          self.sort_column_id: Optional[str] = None
          self.sort_descending: bool = False
      # ... all methods listed above
  ```
- [ ] Verify: `pytest tests/unit/ui/components/table/test_column_manager.py -v` passes

**Notes:**

---

### Task 1.5: TableHeader [Complex]
**File:** `game/ui/components/table/header.py`
**Tests:** `tests/unit/ui/components/table/test_header.py`

- [ ] Write tests for header creation and interaction:
  - Constructor creates header with correct number of buttons per visible column
  - `rebuild()` creates 3 buttons per column (left arrow, title, right arrow)
  - Sort indicator shows ▲/▼ on sorted column
  - Left arrow hidden for first visible column
  - Right arrow hidden for last visible column
  - `check_presses()` returns `{'swap_column': None, 'sort_column': None}` when no press
  - `kill()` cleans up all widgets
- [ ] Create `TableHeader`:
  ```python
  class TableHeader:
      def __init__(self, panel: UIPanel, manager, column_manager: TableColumnManager, header_height: int = 40):
          self._panel = panel
          self._manager = manager
          self._column_manager = column_manager
          self._header_height = header_height
          self._header_elements = []
          self.rebuild()

      def rebuild(self) -> None: ...  # Port from fleet_list_renderer.py:103-160
      def check_presses(self) -> Dict[str, Any]: ...  # Port from fleet_list_renderer.py:400-425
      def kill(self) -> None: ...
  ```
- [ ] Port header button pattern from `game/ui/screens/fleet_list_renderer.py:103-160`:
  - Arrow buttons: 20px wide, store `col_ref` and `direction` attributes
  - Title buttons: `column_width - 40` wide, store `sort_col_ref` attribute
  - Sort indicator: " ▲" (ascending) or " ▼" (descending) appended to title text
- [ ] Verify: `pytest tests/unit/ui/components/table/test_header.py -v` passes

**Notes:**

---

### Task 1.6: VirtualTable [Complex]
**File:** `game/ui/components/table/virtual_table.py`
**Tests:** `tests/unit/ui/components/table/test_virtual_table.py`

- [ ] Write tests for VirtualTable:
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
- [ ] Create `VirtualTable`:
  ```python
  class VirtualTable:
      def __init__(
          self,
          panel: UIPanel,
          manager,
          data_source: ITableDataSource,
          column_manager: TableColumnManager,
          selection_strategy: ISelectionStrategy,
          row_height: int = UIConfig.ROW_HEIGHT_LARGE,
          header_height: int = UIConfig.HEADER_HEIGHT,
      ):
          # Owns: TableHeader, UIVerticalScrollBar, list viewport UIPanel, row pool
  ```
- [ ] Implement core methods:
  - `rebuild_headers()` — delegate to TableHeader.rebuild()
  - `rebuild_row_pool()` — create row pool: `{'bg': UIPanel, 'widgets': [...], 'row_index': int}`
  - `update_visible_rows()` — virtual scroll using `start_percentage * total_height`:
    ```python
    total_h = data_source.get_row_count() * row_height
    scroll_y = scroll_bar.start_percentage * total_h
    start_index = int(scroll_y // row_height)
    offset_y = scroll_y % row_height
    # Position each pooled row at (i * row_height) - offset_y
    ```
  - `update_scroll_bar()` — `visible_pct = min(1.0, viewport_height / total_height)`
  - `find_clicked_row(pos)` — hit test against visible row panels
  - `handle_click(pos, ctrl_held)` — find_clicked_row → selection_strategy.handle_click → update highlights → return index
  - `check_header_presses()` — delegate to TableHeader.check_presses()
  - `force_update()` — reset `_last_scroll_pct` and `_last_row_count`
  - `kill()` — kill all widgets
- [ ] Selection highlighting using `bg_panel.background_colour`:
  - Selected: `pygame.Color(60, 80, 120)` (blue tint)
  - Unselected: `pygame.Color(35, 35, 35)` (dark grey)
  - Call `bg_panel.rebuild()` to apply color change
- [ ] Image column handling:
  - Check `column_manager.is_image_column(col)` per widget
  - Call `data_source.get_cell_image(row_index, col_id)` for image surface
  - Fall back to empty surface if None returned
- [ ] Dirty tracking optimization:
  - `_last_scroll_pct = -1.0`, `_last_row_count = -1`
  - Skip update if both match current values
- [ ] Verify: `pytest tests/unit/ui/components/table/test_virtual_table.py -v` passes

**Notes:**

---

### Task 1.7: Package exports + regression check [Simple]
**Tests:** `pytest tests/unit/ui/components/ -v` and `pytest tests/ --testmon`

- [ ] Update `game/ui/components/table/__init__.py` with all public exports:
  ```python
  from game.ui.components.table.data_source import ITableDataSource
  from game.ui.components.table.selection import (
      ISelectionStrategy, SingleSelect, MultiSelect, NoSelect,
  )
  from game.ui.components.table.column_manager import TableColumnManager
  from game.ui.components.table.header import TableHeader
  from game.ui.components.table.virtual_table import VirtualTable
  ```
- [ ] Verify: `pytest tests/unit/ui/components/ -v` — all new tests pass
- [ ] Verify: `pytest tests/ --testmon` — no regressions to existing tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 6 test files in `tests/unit/ui/components/table/` pass
- [ ] Import from `game.ui.components.table` works (VirtualTable, ITableDataSource, etc.)
- [ ] No existing tests broken: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
