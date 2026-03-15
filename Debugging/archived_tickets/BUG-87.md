# BUG-87: Empire Treasury window missing colony resource production totals

## Description
The Empire --> Treasury Window does not show the values produced by the colonies, the 1st row should total all of the various resources produced by each colony per turn.

## Priority
**High** - Significant feature broken (key economic data not displayed)

## Status (Awaiting Confirmation)

## Root Cause
`EmpireEconomyCalculator._aggregate_colony_production()` only checked for inline `abilities` dict on components in facility design_data. Real facility designs (e.g. `qs_metals_complex.json`) store components as `{"id": "metal_harvester", "modifiers": [...]}` without inline abilities — the ResourceHarvester ability is in the component registry, not embedded in the design file.

The strategy detail formatter (`compute_planet_production()`) worked correctly because it had a registry fallback lookup, but the economy calculator lacked this fallback.

## Fix
1. **`game/strategy/engine/empire_economy_calculator.py`**: Added `__init__(self, *, registries=None)` parameter, extracted `_get_harvester_info()` and `_lookup_harvester_in_registry()` helper methods (matching the pattern used by `HarvestingEngine` and `strategy_detail_formatter`). The calculator now checks inline abilities first, then falls back to registry lookup.

2. **`game/ui/screens/empire_panel_window.py`**: Updated `_build_treasury_tab()` to pass `registries=get_default_registries()` when constructing `EmpireEconomyCalculator`.

## Tests Added
- `test_registry_fallback_for_colony_production` — verifies production calculated via registry lookup
- `test_registry_fallback_with_no_registries_returns_zero` — graceful degradation without registries

## Work Log
- Investigated treasury panel -> EmpireEconomySnapshot -> EmpireEconomyCalculator pipeline
- Compared calculator with strategy_detail_formatter.compute_planet_production() - found missing registry fallback
- Verified real facility designs use component IDs without inline abilities (qs_metals_complex.json)
- Added registry support to calculator, updated call site, all 34 tests pass
