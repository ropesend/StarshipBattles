# Phase 1: FleetReportWindow MVVM Completion

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-173 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Read `fleet_report_window.py` fully, catalog `_init_sidebar()` method (lines 104-457, ~354 lines)
- [ ] Identify all sidebar state: `lbl_*` labels (13), `filter_buttons` dict, `column_buttons` dict, remove button
- [ ] Create `game/ui/screens/fleet_report_sidebar.py`:
  - [ ] `FleetReportSidebar` class
  - [ ] Constructor: `__init__(self, rect, manager, container, view_model, column_manager, empire, callbacks)`
  - [ ] Move all widget creation from `_init_sidebar()` into constructor
  - [ ] Move `_update_summary(stats)` method — updates 13 summary labels
  - [ ] Move `_update_remove_button(selected_count)` method — button enable/disable
  - [ ] Expose filter button and column button references for event polling
  - [ ] Sidebar does NOT import FleetReportWindow (one-way dependency)
- [ ] Update `fleet_report_window.py`:
  - [ ] In `__init__`: create `self.sidebar = FleetReportSidebar(...)`
  - [ ] Remove `_init_sidebar()` method entirely
  - [ ] Remove `_update_summary()` method — now `self.sidebar.update_summary(stats)`
  - [ ] Remove `_update_remove_button()` method — now `self.sidebar.update_remove_button(count)`
  - [ ] Update `refresh_list()` to call `self.sidebar.update_summary(stats)`
  - [ ] Update `update()` to poll sidebar button references
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py -v`

**Notes:**

---

### Task 1.2: Extract FleetListRenderer [Medium]
**File:** `game/ui/screens/fleet_report_window.py` (read)
**New File:** `game/ui/screens/fleet_list_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py -v`

- [ ] Identify renderer methods:
  - [ ] `_init_ship_list()` (lines 468-504, ~37 lines) — list panel + header + viewport
  - [ ] `_rebuild_headers()` (lines 518-577, ~60 lines) — sortable column header buttons
  - [ ] `_swap_columns()` (lines 578-585, ~8 lines) — column reorder
  - [ ] `_rebuild_row_pool()` (lines 586-647, ~62 lines) — virtual scroll row pool
  - [ ] `_update_visible_rows()` (lines 648-689, ~42 lines) — scroll-based visibility
  - [ ] `_update_row_data()` (lines 706-731, ~26 lines) — cell value updates
  - [ ] `_apply_row_highlight()` (lines 690-705, ~15 lines) — selection highlighting
  - [ ] `_get_ship_image()` (lines 732-769, ~38 lines) — image loading + cache
  - [ ] `_create_placeholder()` (lines 770-776, ~7 lines) — placeholder surface
- [ ] Create `game/ui/screens/fleet_list_renderer.py`:
  - [ ] `FleetListRenderer` class
  - [ ] Constructor: `__init__(self, rect, manager, container, column_manager, view_model)`
  - [ ] Move all ship list initialization into constructor
  - [ ] Move header management: `rebuild_headers()`, `swap_columns(col, direction)`
  - [ ] Move row pool management: `rebuild_row_pool()`, `update_visible_rows(scroll_y)`, `update_row_data(row, ship)`, `apply_row_highlight(row, selected)`
  - [ ] Move image cache: `get_ship_image(ship)`, `_create_placeholder()`
  - [ ] Expose: `row_pool`, `scroll_bar`, `header_widgets` for event routing
- [ ] Update `fleet_report_window.py`:
  - [ ] In `__init__`: create `self.renderer = FleetListRenderer(...)`
  - [ ] Remove all moved methods
  - [ ] Update `refresh_list()` to call `self.renderer.rebuild_row_pool()` / `update_visible_rows()`
  - [ ] Update `process_event()` to route header clicks and scroll to renderer
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py -v`

**Notes:**

---

### Task 1.3: Refactor FleetReportWindow to coordinator [Medium]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py -v`

- [ ] Verify window is now thin coordinator:
  - [ ] `__init__()` — creates layout, sidebar, renderer, detail panel
  - [ ] `process_event()` — routes events to sidebar, renderer, detail panel
  - [ ] `refresh_list()` — triggers renderer + sidebar refresh
  - [ ] `update()` — polls toggle buttons, delegates to handlers
  - [ ] `_handle_row_click()` — selection logic (keep in window or move to renderer)
  - [ ] `_toggle_filter()` / `_toggle_column()` — delegates to ViewModel/ColumnManager
  - [ ] Ship removal methods — keep in window (orchestration)
  - [ ] `kill()` — cleanup
- [ ] Verify: FleetReportWindow public API unchanged (constructor, process_event, update, kill)
- [ ] Run all tests: `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py -v`
- [ ] Fix any test failures from moved methods
- [ ] Verify: FleetReportWindow < 500 lines

**Notes:**

---

### Task 1.4: Phase 1 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: 12,023+ tests pass, 0 failures
- [ ] Verify line counts:
  - [ ] `fleet_report_window.py` < 500 lines
  - [ ] `fleet_report_sidebar.py` exists
  - [ ] `fleet_list_renderer.py` exists
- [ ] Verify: Sidebar does NOT import FleetReportWindow

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
