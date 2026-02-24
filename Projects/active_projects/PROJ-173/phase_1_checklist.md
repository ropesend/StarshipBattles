# Phase 1: FleetReportWindow MVVM Completion

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-173 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Complete the MVVM extraction of FleetReportWindow (1,108 lines) by extracting the sidebar UI subsystem (~430 lines) and the list renderer (~200 lines). The window already has FleetListViewModel, ColumnManager, and ShipDetailPanel extracted. This phase finishes the job.

**Already Extracted (DO NOT RE-EXTRACT):**
- `fleet_report_view_model.py` — FleetListViewModel (280L) — filter/sort state + lazy refresh
- `column_manager.py` — ColumnManager (234L) — column config + value extraction
- `ship_detail_panel.py` — ShipDetailPanel — ship detail rendering

---

## Tasks

### Task 1.1: Extract FleetReportSidebar [Complex]
**File:** `game/ui/screens/fleet_report_window.py` (read)
**New File:** `game/ui/screens/fleet_report_sidebar.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py -v`

- [x] Read `fleet_report_window.py` fully, catalog `_init_sidebar()` method (lines 104-457, ~354 lines)
- [x] Identify all sidebar state: `lbl_*` labels (13), `filter_buttons` dict, `column_buttons` dict, remove button
- [x] Create `game/ui/screens/fleet_report_sidebar.py`:
  - [x] `FleetReportSidebar` class
  - [x] Constructor: `__init__(self, panel, manager, view_model, column_manager, empire, on_remove_selected)`
  - [x] Move all widget creation from `_init_sidebar()` into constructor
  - [x] Move `_update_summary(stats)` method — updates 13 summary labels
  - [x] Move `_update_remove_button(selected_count)` method — button enable/disable
  - [x] Expose filter button and column button references for event polling
  - [x] Sidebar does NOT import FleetReportWindow (one-way dependency)
- [x] Update `fleet_report_window.py`:
  - [x] In `__init__`: create `self.sidebar = FleetReportSidebar(...)`
  - [x] Remove `_init_sidebar()` method entirely
  - [x] Remove `_update_summary()` method — now `self.sidebar.update_summary(stats)`
  - [x] Remove `_update_remove_button()` method — now `self.sidebar.update_remove_button(count)`
  - [x] Update `refresh_list()` to call `self.sidebar.update_summary(stats)`
  - [x] Update `update()` to poll sidebar button references
- [x] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py -v`

**Notes:** Created FleetReportSidebar (554 lines) with all sidebar widgets, filter buttons, column buttons, and summary labels.

---

### Task 1.2: Extract FleetListRenderer [Medium]
**File:** `game/ui/screens/fleet_report_window.py` (read)
**New File:** `game/ui/screens/fleet_list_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py -v`

- [x] Identify renderer methods:
  - [x] `_init_ship_list()` — list panel + header + viewport
  - [x] `_rebuild_headers()` — sortable column header buttons
  - [x] `_rebuild_row_pool()` — virtual scroll row pool
  - [x] `_update_visible_rows()` — scroll-based visibility
  - [x] `_update_row_data()` — cell value updates
  - [x] `_apply_row_highlight()` — selection highlighting
  - [x] `_get_ship_image()` — image loading + cache
  - [x] `_create_placeholder()` — placeholder surface
- [x] Create `game/ui/screens/fleet_list_renderer.py`:
  - [x] `FleetListRenderer` class
  - [x] Constructor: `__init__(self, panel, manager, column_manager, view_model, header_height, row_height)`
  - [x] Move all ship list initialization into constructor
  - [x] Move header management: `rebuild_headers()`, header button check
  - [x] Move row pool management: `rebuild_row_pool()`, `update_visible_rows()`, `update_row_data()`, `apply_row_highlight()`
  - [x] Move image cache: `_get_ship_image()`, `_create_placeholder()`
  - [x] Expose: `row_pool`, `scroll_bar`, `header_widgets` for event routing
- [x] Update `fleet_report_window.py`:
  - [x] In `__init__`: create `self.list_renderer = FleetListRenderer(...)`
  - [x] Remove all moved methods
  - [x] Update `refresh_list()` to call renderer methods
  - [x] Update `process_event()` to route header clicks and scroll to renderer
- [x] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py -v`

**Notes:** Created FleetListRenderer (425 lines) with virtual scrolling, column headers, row pool, and image caching.

---

### Task 1.3: Refactor FleetReportWindow to coordinator [Medium]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py -v`

- [x] Verify window is now thin coordinator:
  - [x] `__init__()` — creates layout, sidebar, list_renderer, detail panel
  - [x] `process_event()` — routes events to sidebar, renderer, detail panel
  - [x] `refresh_list()` — triggers renderer + sidebar refresh
  - [x] `update()` — polls toggle buttons, delegates to handlers
  - [x] `_handle_row_click()` — selection logic (kept in window for orchestration)
  - [x] `_toggle_filter()` / `_toggle_column()` — delegates to ViewModel/ColumnManager
  - [x] Ship removal methods — kept in window (orchestration)
  - [x] `kill()` — cleanup
- [x] Verify: FleetReportWindow public API unchanged (constructor, process_event, update, kill)
- [x] Run all tests: `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py -v`
- [x] Fix any test failures from moved methods
- [x] Verify: FleetReportWindow < 500 lines (now 359 lines)

**Notes:** FleetReportWindow reduced from 1,109 lines to 359 lines - a 68% reduction.

---

### Task 1.4: Phase 1 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify: 12,312 tests pass, 0 failures
- [x] Verify line counts:
  - [x] `fleet_report_window.py` = 359 lines (< 500 lines target)
  - [x] `fleet_report_sidebar.py` = 554 lines (exists)
  - [x] `fleet_list_renderer.py` = 425 lines (exists)
- [x] Verify: Sidebar does NOT import FleetReportWindow

**Notes:** All verification criteria met.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
