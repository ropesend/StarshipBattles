# BUG-86: Build Queue planet details missing resource production numbers

## Description

When I look at the planet details in the Build Queue there are no resource production numbers. For the same planet on the strategy layer there are production numbers. These panels should be using the same code. Please get the build queue planet details report to show the same values. The same problem is happening with the panel in the planets list. All three panels should be the same dimensions and look identical.

Related: BUG-80 (Planets List panel dimensions)

## Priority
High

## Status (Awaiting Confirmation)

## Root Cause
The `PlanetReportPanel` accepts an optional `production_rates` parameter to populate the resource grid's "Prod" row. The strategy detail formatter passed this parameter (via `compute_planet_production()`), but the build queue screen and planets list window did NOT — they created the panel without production_rates, so it defaulted to empty `{}` and showed all zeros.

## Fix
1. **`game/ui/panels/planet_report_panel.py`**: Extracted `compute_planet_production()` and `_get_harvester_info()` as module-level shared functions (previously duplicated as instance/static methods on `StrategyDetailFormatter`).

2. **`game/ui/screens/build_queue_screen.py`**: Added `production_rates=compute_planet_production(self.build_context)` when creating `PlanetReportPanel`.

3. **`game/ui/screens/planet_list_window.py`**: Added `production_rates=compute_planet_production(planet)` when creating `PlanetReportPanel`.

4. **`game/ui/screens/strategy_detail_formatter.py`**: Refactored `compute_planet_production()` to delegate to the shared function. Removed duplicate `_get_harvester_info()` static method.

5. **`tests/unit/ui/screens/test_strategy_detail_formatter.py`**: Updated `TestGetHarvesterInfo` tests to use the shared `_get_harvester_info` from `planet_report_panel`.

## Tests Added
- `test_compute_planet_production.py` with 5 tests:
  - `test_unowned_planet_returns_empty` - unowned planets return {}
  - `test_planet_with_inline_harvester` - inline abilities work
  - `test_planet_with_registry_lookup` - registry fallback works (BUG-86 root cause)
  - `test_planet_no_facilities_returns_empty` - no facilities = no production
  - `test_non_operational_facility_skipped` - disabled facilities skipped

## Work Log
- Traced PlanetReportPanel usage in build queue, planets list, and strategy screen
- Found build queue and planets list missing production_rates parameter
- Extracted shared compute_planet_production() to planet_report_panel module
- Updated all 3 call sites to use shared function
- All 436 related tests pass, 77 strategy detail tests pass
