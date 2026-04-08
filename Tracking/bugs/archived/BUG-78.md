# BUG-78: Planet Production values display as 0; icons not centered on columns

## Description

Planet Production values are reported to be 0 when they are not. Also the icons should be centered on the columns.

**Screenshot:** `output/screenshots/screenshot_20260209_193304_946970_strategy_viewport.png`

## Priority

**High** — Production values showing 0 is a significant data display bug that misleads the player about planet output.

## Status
Awaiting Confirmation

## Root Cause

### Production Values = 0
`StrategyDetailFormatter.compute_planet_production()` only checked for inline `abilities` in the facility `design_data`. However, actual facility designs store components as `{"id": "metal_harvester", "modifiers": [...]}` without inline abilities. The `HarvestingEngine` correctly does registry lookup, but the UI display method did not.

### Icons Not Centered
`planet_report_panel.py` placed icons at `col_x` (left-aligned) instead of centering within the column width.

## Fix Applied
- **`game/ui/screens/strategy_detail_formatter.py`**: Added `_get_harvester_info()` with registry lookup fallback. Updated `compute_planet_production()` to use it.
- **`game/ui/panels/planet_report_panel.py`**: Changed icon x-position to `col_x + (col_w - 24) // 2`.

## Tests
- **`tests/unit/ui/screens/test_planet_production_display.py`** (5 new tests, all pass)
- 1447/1447 UI tests pass, no regressions

## Work Log
- Traced production display chain to `compute_planet_production()`
- Found it only checked inline abilities, not registry
- Applied same pattern as `HarvestingEngine._get_harvester_info()`
- Fixed icon centering calculation
