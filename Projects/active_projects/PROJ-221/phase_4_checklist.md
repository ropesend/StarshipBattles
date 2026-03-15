# Phase 4: VirtualTable Integration [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-221 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace hardcoded queue display with VirtualTable in BuildQueueScreen

---

## Tasks

### Task 4.1: Update BuildQueuePanels dataclass [Simple]
**File:** `game/ui/screens/build_queue_panel_factory.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [ ] Read `BuildQueuePanels` dataclass to identify fields to change
- [ ] Remove fields: `queue_header_text`, `queue_column_positions`
- [ ] Keep field: `queue_scrollable` (will be repurposed as VirtualTable container) OR remove and add `queue_table_panel`
- [ ] Add fields: `virtual_table: VirtualTable`, `column_manager: TableColumnManager`
- [ ] Update any type hints or imports needed

**Notes:** The `queue_scrollable` UIScrollingContainer will be replaced by a plain UIPanel that VirtualTable uses as its container.

### Task 4.2: Rewrite _create_build_queue_panel in factory [Medium]
**File:** `game/ui/screens/build_queue_panel_factory.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [ ] Read current `_create_build_queue_panel()` method (lines ~279-347)
- [ ] Keep the outer `build_queue_panel` creation (same position and size)
- [ ] Keep the queue header text label ("Build Queue" title) at the top
- [ ] Remove: manual column header labels (UILabel for "Item", "Turns", resource icons)
- [ ] Remove: `queue_scrollable` UIScrollingContainer creation
- [ ] Remove: `queue_column_positions` dict construction
- [ ] Add: create `queue_table_panel` UIPanel below the header text, filling remaining space
- [ ] Add: create `TableColumnManager(BUILD_QUEUE_COLUMNS)`
- [ ] Add: create `BuildQueueQueueDataSource(columns, portrait_loader, build_rate)`
- [ ] Add: create `VirtualTable(panel=queue_table_panel, manager=manager, data_source=data_source, column_manager=column_manager, selection_strategy=SingleSelect())`
- [ ] Store `virtual_table` and `column_manager` on BuildQueuePanels
- [ ] Import: `TableColumnManager`, `VirtualTable`, `SingleSelect` from `game.ui.components.table`
- [ ] Import: `BuildQueueQueueDataSource`, `BUILD_QUEUE_COLUMNS` from `build_queue_queue_data_source`

**Notes:** Follow PlanetListWindow pattern (lines 141-158). The VirtualTable manages its own header, scrollbar, and row rendering internally.

### Task 4.3: Update BuildQueueRenderer [Medium]
**File:** `game/ui/screens/build_queue_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [ ] Read current `refresh_queue_display()` method (lines ~123-249) to understand what to replace
- [ ] Rewrite `refresh_queue_display()`:
  - Get active queue from screen
  - Get build_rate from active_queue_source
  - Call `data_source.set_queue(queue, build_rate)` to update data
  - Call `virtual_table.update_scroll_bar()`
  - Call `virtual_table.force_update()`
  - Call `virtual_table.update_visible_rows()`
- [ ] Remove: all per-row UIPanel creation code
- [ ] Remove: all manual label positioning using `queue_column_positions`
- [ ] Remove: `self.queue_items` list (UIPanel references — used by DragHandler, will be adapted in Phase 5)
- [ ] Remove: `draw_selection_highlight()` method (VirtualTable handles selection highlighting)
- [ ] Update `update_queue_header()` to work without column positions if needed
- [ ] Remove unused imports (PLANET_RESOURCES for column layout, etc.)

**Notes:** The renderer becomes much simpler — it just updates the data source and tells VirtualTable to refresh.

### Task 4.4: Update BuildQueueScreen to wire VirtualTable [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [ ] Read current screen initialization to understand the wire-up
- [ ] Store references to `virtual_table` and `column_manager` from `BuildQueuePanels`
- [ ] Store reference to `data_source` for queue updates
- [ ] Add header press handling in `update()` or `handle_event()`:
  ```python
  header_result = self.virtual_table.check_header_presses()
  if header_result.get('swap_column'):
      col_dict, direction = header_result['swap_column']
      self.column_manager.swap_column(col_dict['id'], direction)
      self.virtual_table.rebuild_headers()
      self.virtual_table.rebuild_row_pool()
      self._refresh_queue_display()
  elif header_result.get('sort_column'):
      self.column_manager.set_sort(header_result['sort_column'])
      self._refresh_queue_display()
  ```
- [ ] Update `_refresh_queue_display()` to call renderer's new simplified method
- [ ] Update queue item selection to use VirtualTable's selection:
  - In `process_event()`, handle MOUSEBUTTONUP by calling `virtual_table.handle_click(pos)`
  - Get selected index from `virtual_table` selection strategy
  - Remove separate `selected_queue_index` tracking (or sync it from VirtualTable)
- [ ] Update `_on_queue_selection_changed()` to reset VirtualTable:
  - Call `virtual_table.force_update()` when switching queues
  - Clear selection: `selection_strategy.clear()` or equivalent
  - Reset scroll position
- [ ] Remove `draw_selection_highlight()` call from `draw()` method
- [ ] Handle scroll wheel events — delegate to VirtualTable

**Notes:** Follow PlanetListWindow pattern. Key concern: DragHandler still needs to work — Phase 5 handles that.

### Task 4.5: Update existing tests [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [ ] Update test fixtures to provide VirtualTable mocks where BuildQueuePanels is constructed
- [ ] Remove tests that check `queue_column_positions` — no longer exists
- [ ] Update tests that check `queue_scrollable` — replaced by VirtualTable
- [ ] Update tests that check `renderer.queue_items` — list no longer exists
- [ ] Update tests that check `draw_selection_highlight()` — method removed
- [ ] Add test: `test_header_swap_column_reorders` — verify swap handling
- [ ] Add test: `test_queue_refresh_updates_data_source` — verify data source is updated on refresh
- [ ] Add test: `test_queue_switch_resets_scroll_and_selection` — verify reset on queue change
- [ ] Run: `pytest tests/unit/ui/screens/test_build_queue_screen.py` — all pass

**Notes:** Some tests will need significant updates due to the architectural change. Focus on preserving behavioral coverage.

### Task 4.6: Update integration tests [Simple]
**File:** `tests/integration/ui/test_build_queue_*.py` and `tests/integration/ui/build_queue_screen/`
**Tests:** `pytest tests/integration/ui/`

- [ ] Run integration tests to identify failures: `pytest tests/integration/ui/ -k build_queue`
- [ ] Update failing tests to work with new VirtualTable-based rendering
- [ ] Focus on: `test_build_queue_formatting.py`, `test_build_queue_drag_drop.py`
- [ ] Run: `pytest tests/integration/ui/ -k build_queue` — all pass

**Notes:**

### Task 4.7: Run regression check [Simple]
**Tests:** `pytest tests/ --testmon`

- [ ] Run `pytest tests/ --testmon` — no regressions
- [ ] Verify build queue can be opened without crashes (manual test if possible)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
