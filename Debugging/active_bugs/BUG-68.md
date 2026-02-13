# BUG-68: Fleet Report - Ship Selection and Ship Report Panel

## Description

In the Fleet Report I need to be able to select a ship, the Ship report should show on the right side. Once selected I need to be able to remove a ship from the fleet.

## Priority
Medium

## Status
In-Progress

## Root Cause

The Fleet Report's right detail panel was using `DesignReportPanel` (which shows static design specifications) instead of `ShipDetailPanel` (which shows live ship instance data with damage, resources, and a "Remove from Fleet" button). This meant:
- No damage/resource info shown for actual ship instances
- No "Remove from Fleet" button available
- Events not forwarded to the detail panel (layer toggles, remove button)

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

## Work Log
- 2026-02-07: Original fix applied (added remove button to ShipDetailPanel)
- 2026-02-11: Fix rejected - panel was wrong type (DesignReportPanel vs ShipDetailPanel)
- 2026-02-11: Reworked - swapped DesignReportPanel for ShipDetailPanel, wired callbacks, forwarded events

---
### Fix Rejected [2026-02-11 12:00]
**Reason:** 68
**New Constraints:** None provided
---
