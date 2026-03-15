# BUG-68: Fleet Report - Ship Selection and Ship Report Panel

## Description

In the Fleet Report I need to be able to select a ship, the Ship report should show on the right side. Once selected I need to be able to remove a ship from the fleet.

## Priority
Medium

## Status
Awaiting Confirmation

## Root Cause

**Two issues (both now fixed):**

1. **(Fixed earlier)** The Fleet Report's right detail panel was using `DesignReportPanel` instead of `ShipDetailPanel`. Fixed in PROJ-173 Phase 1 (2026-02-13).

2. **(Fixed 2026-03-14)** Ship row clicks never registered because `process_event()` listened for `pygame.MOUSEBUTTONDOWN`, which is consumed by child `UIPanel` elements before it reaches `FleetReportWindow`. pygame_gui's `UIManager` processes child panels at higher layers first; `UIPanel.process_event()` returns `True` for any `MOUSEBUTTONDOWN` inside the panel, breaking the event loop. The fix: use `MOUSEBUTTONUP` instead, which is not consumed by UIPanel. This matches `PlanetListWindow` (line 207) and `EmpireBuildQueueWindow` (line 447) which both use `MOUSEBUTTONUP` and work correctly.

## Fix

### 1. `game/ui/screens/fleet_report_window.py`
- **Replaced `DesignReportPanel` with `ShipDetailPanel`** in `_init_detail_panel()`
- Wired `on_remove_ship=self._on_remove_ship` callback to enable the remove button
- **Simplified `_update_detail_panel()`**: Now passes the actual `ShipInstance` directly via `ship_detail_panel.update_ship()` instead of loading a fresh ship from design data
- **Added event forwarding**: `process_event()` now forwards events to `ship_detail_panel.process_event()` so layer toggle and remove buttons work
- Removed unused `DesignReportPanel` import and `DesignLoaderAdapter` import/instance
- Updated `kill()` cleanup to reference `ship_detail_panel`

### 2. `tests/unit/ui/screens/test_fleet_report_window.py`
- Updated test fixture: `design_report_panel` → `ship_detail_panel` mock with `process_event` stub
- Updated `test_ship_selection_updates_detail_panel`: calls `update_ship(ship)` instead of `update_design()`
- Updated `test_detail_panel_shows_ship_info`: asserts `update_ship` called with ship instance
- Updated `test_detail_panel_placeholder_when_no_selection`: asserts `update_ship(None)` called

### Features now working:
- Ship selection by clicking rows (existing)
- ShipDetailPanel on right showing: images, HP/status, resource levels, component damage per layer (collapsible), combat record
- "Remove from Fleet" button at bottom of detail panel
- Layer collapse/expand toggles

## Tests
All 56 fleet report window tests pass (37 main + 19 multi-select).

## Investigation Report

### Code Path Trace
`FleetReportWindow.process_event()` → checks `MOUSEBUTTONDOWN` → `_handle_row_click(pos)` → `VirtualTable.handle_click(pos)` → `find_clicked_row(pos)` → `MultiSelect.handle_click()` → `_update_detail_panel()` → `ShipDetailPanel.update_ship()`

### Root Cause
`FleetReportWindow.process_event()` never receives the `MOUSEBUTTONDOWN` event. pygame_gui's `UIManager.process_events()` iterates UI sprites by layer (highest first). The row background `UIPanel` elements inside `_list_view_panel` consume `MOUSEBUTTONDOWN` (returning `True`), causing the UIManager to break its loop before reaching the `FleetReportWindow`.

### Similar Patterns Found
- `PlanetListWindow` (line 207): uses `MOUSEBUTTONUP` — works correctly
- `EmpireBuildQueueWindow` (line 447): uses `MOUSEBUTTONUP` — works correctly
- `EventLogWindow` (line 292): uses `MOUSEBUTTONDOWN` — same latent bug (also fixed)

### Documentation Discrepancies
None — code matches docs. No list+detail pattern is explicitly documented in `docs/`.

## Hypothesis Log

### Hypothesis 1: MOUSEBUTTONDOWN consumed by child UIPanels - CONFIRMED
**Theory:** pygame_gui's UIPanel.process_event() returns True for MOUSEBUTTONDOWN inside the panel, causing UIManager to break its event loop before reaching FleetReportWindow.
**Evidence For:** PlanetListWindow and EmpireBuildQueueWindow use MOUSEBUTTONUP and work. FleetReportWindow uses MOUSEBUTTONDOWN and doesn't work.
**Evidence Against:** None.
**Test:** Change MOUSEBUTTONDOWN to MOUSEBUTTONUP.
**Result:** Fix applied. All 56 tests pass.

## Work Log
- 2026-02-07: Original fix applied (added remove button to ShipDetailPanel)
- 2026-02-11: Fix rejected - panel was wrong type (DesignReportPanel vs ShipDetailPanel)
- 2026-02-11: Reworked - swapped DesignReportPanel for ShipDetailPanel, wired callbacks, forwarded events
- 2026-03-14: Deep investigation — root cause found: MOUSEBUTTONDOWN consumed by child UIPanels. Changed to MOUSEBUTTONUP in fleet_report_window.py and event_log_window.py. All 56 tests pass.

---
### Fix Rejected [2026-02-11 12:00]
**Reason:** 68
**New Constraints:** None provided
---
