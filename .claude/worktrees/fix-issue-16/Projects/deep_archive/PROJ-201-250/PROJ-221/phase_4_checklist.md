# Phase 4: VirtualTable Integration [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-221 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace hardcoded queue display with VirtualTable in BuildQueueScreen

---

## Tasks

### Task 4.1: Update BuildQueuePanels dataclass [Simple]
**File:** `game/ui/screens/build_queue_panel_factory.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [x] Read `BuildQueuePanels` dataclass to identify fields to change
- [x] Remove fields: `queue_scrollable`, `queue_column_positions`
- [x] Keep field: `queue_header_text` (still used for header title updates)
- [x] Add fields: `virtual_table: VirtualTable`, `column_manager: TableColumnManager`, `data_source: BuildQueueQueueDataSource`
- [x] Update type hints and imports

**Notes:** The `queue_scrollable` UIScrollingContainer will be replaced by a plain UIPanel that VirtualTable uses as its container.

### Task 4.2: Rewrite _create_build_queue_panel in factory [Medium]
**File:** `game/ui/screens/build_queue_panel_factory.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [x] Rewrote `_create_build_queue_panel()` with VirtualTable integration
- [x] Kept outer build_queue_panel and header text
- [x] Removed: manual column headers, scrollable container, column positions
- [x] Added: VirtualTable, TableColumnManager, BuildQueueQueueDataSource, SingleSelect
- [x] Updated return signature and imports

**Notes:** Follow PlanetListWindow pattern (lines 141-158). The VirtualTable manages its own header, scrollbar, and row rendering internally.

### Task 4.3: Update BuildQueueRenderer [Medium]
**File:** `game/ui/screens/build_queue_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [x] Rewrote `refresh_queue_display()` to update data source and VirtualTable
- [x] Removed all per-row UIPanel creation code
- [x] Removed `self.queue_items` list
- [x] Removed `draw_selection_highlight()` method
- [x] Kept `update_queue_header()` unchanged
- [x] Removed unused imports (PLANET_RESOURCES, TEAM_1_TEXT)

**Notes:** The renderer becomes much simpler — it just updates the data source and tells VirtualTable to refresh.

### Task 4.4: Update BuildQueueScreen to wire VirtualTable [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [x] Updated `_refresh_queue_display()` to pass build_rate to renderer
- [x] Removed `draw_selection_highlight()` call from `draw()`
- [x] Updated `_handle_drag_operations()` to pass VirtualTable instead of queue_items/queue_scrollable
- [x] Selection handled through VirtualTable.handle_click() in drag handler

**Notes:** Follow PlanetListWindow pattern. Key concern: DragHandler still needs to work — Phase 5 handles that.

### Task 4.5: Update existing tests [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [x] Existing unit tests all pass (use MagicMock, not affected by VirtualTable changes)
- [x] Run: `pytest tests/unit/ui/screens/test_build_queue_screen.py` — all 39 pass

**Notes:** Some tests will need significant updates due to the architectural change. Focus on preserving behavioral coverage.

### Task 4.6: Update integration tests [Simple]
**File:** `tests/integration/ui/test_build_queue_*.py` and `tests/integration/ui/build_queue_screen/`
**Tests:** `pytest tests/integration/ui/`

- [x] Run integration tests: `pytest tests/integration/ui/ -k build_queue` — 106 passed
- [x] Updated `test_basics.py` — check data_source.get_row_count() instead of renderer.queue_items
- [x] Updated `test_queue_selector.py` — check data_source.get_row_count()
- [x] Updated `test_build_queue_drag_drop.py` — use VirtualTable row_pool for panel positions

**Notes:**

### Task 4.7: Run regression check [Simple]
**Tests:** `pytest tests/ --testmon`

- [x] Run `pytest tests/` — 13212 passed, 2 skipped (no regressions)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
