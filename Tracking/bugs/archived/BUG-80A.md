# BUG-80: Planets List - Planet details panel dimensions and positioning

## Description

The planet details window in the Planets List should be the same dimensions as the planet details panel on the main strategy layer. Currently the 1st is much shorter than the latter. Also when the planets window is resized, the planet details panel should move with it.

Related: BUG-86 (Build Queue planet details also inconsistent)

## Priority
Medium

## Status (Awaiting Confirmation)

## Root Cause

Two issues in `planet_list_window.py`:

1. **Height hardcoded to 400px** (line 450): The PlanetReportPanel requires minimum 450px (`get_height_required()` returns 350 + RESOURCE_PANEL_HEIGHT=100 = 450), so the 400px was too short, cutting off content. The strategy layer uses dynamic height that fills available space.

2. **No resize handling**: The panel position was computed once at creation time and never updated when the PlanetListWindow was resized. Since the window is created with `resizable=True`, the panel would stay at its original X position even when the window grew/shrank.

## Fix

In `game/ui/screens/planet_list_window.py`:

1. **Extracted `_detail_panel_geometry()`** method that calculates panel position and dynamic height:
   - X: `window_width - detail_panel_width - 10` (right-aligned)
   - Y: 60 (below title bar)
   - Height: `max(450, window_height - 60 - 80)` (fills available space, minimum 450)

2. **Updated `_on_planet_selected()`** to use `_detail_panel_geometry()` for both the panel rect and button positioning.

3. **Added `set_dimensions()` override** that recreates the detail panel when the window is resized, so the panel repositions correctly.

## Tests

6 new tests in `tests/unit/ui/screens/test_planet_list_components.py::TestDetailPanelGeometry`:
- `test_panel_x_is_right_aligned` - Panel X = window_width - 580 - 10
- `test_panel_y_is_below_title` - Panel Y = 60
- `test_panel_height_fills_window` - Dynamic height from window size
- `test_panel_height_minimum_450` - Never below 450px minimum
- `test_taller_window_gives_taller_panel` - Larger window = taller panel
- `test_wider_window_shifts_panel_right` - Wider window shifts panel right

All 41 planet list tests pass (35 existing + 6 new).

## Work Log
- 2026-02-11: Root cause identified and fixed. Dynamic height + resize handling added.
