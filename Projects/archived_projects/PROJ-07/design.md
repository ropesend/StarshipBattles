# PROJ-07: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis
The strategy layer was incorrectly reading ship stats from `expected_stats` instead of calculating them from actual component definitions. The `expected_stats` field is intended ONLY for load-time validation in `ship_serialization.py`, not as runtime data.

## Implementation Summary

### Phase 1: Ship Stats Service - COMPLETE
Created `game/strategy/services/ship_stats_service.py` with:
- `ShipStatsService.calculate_stats()` - calculates stats from component definitions
- `ShipStatsService.get_component_effectiveness()` - damage effectiveness model
- `ShipStatsService._get_warp_effectiveness()` - warp requires 100% HP
- `ShipStatsService._iterate_design_components()` - iterates layers with registry lookup
- Fallback to `expected_stats` when no components found in layers

22 unit tests in `tests/unit/strategy/test_ship_stats_service.py`

### Phase 2: Caching in ShipInstance - COMPLETE
Added to `game/strategy/data/ship_instance.py`:
- `_cached_stats: Optional[Dict[str, Any]]` attribute
- `get_calculated_stats(force_refresh=False)` method
- `invalidate_stats_cache()` method
- Cache invalidation in `update_from_ship()` and `repair()`

### Phase 3: Refactor ShipInstance Methods - COMPLETE
Replaced all `expected_stats` reads with `get_calculated_stats()`:
- `get_hp_percentage()`, `get_resource_percentage()`, `get_fuel_cost_per_hex()`
- `get_current_fuel()`, `consume_fuel()`, `get_warp_energy_cost()`
- `get_current_energy()`, `consume_energy()`, `get_hp_display()`
- `get_resource_display()`, `repair()`, `resupply()`

### Phase 4: Refactor Fleet Mobility Service - COMPLETE
Updated `game/strategy/services/fleet_mobility_service.py`:
- `calculate_ship_speed()` now uses `ship_instance.get_calculated_stats()`

### Phase 5: Refactor Fleet Report Filters - COMPLETE
Updated `game/ui/screens/fleet_report_filters.py`:
- `has_warp_capability()` now uses calculated stats (warp disabled when damaged)
- `calculate_fleet_stats()` now uses calculated stats for all ships

### Phase 6: Update Tests - COMPLETE
Updated test files to configure `get_calculated_stats()` on mock objects

## Key Patterns Used
- **Service Pattern**: `ShipStatsService` is stateless, only imports from `game.core.registry`
- **Caching with Invalidation**: Stats cached on ShipInstance, invalidated on damage/repair
- **Fallback Pattern**: Falls back to `expected_stats` for test fixtures

## Verification Results
- **2656 tests passed**, 1 skipped, 0 failures
- Ships with warp drives show correct warp capability
- Damaged warp drives disable warp capability (any damage)
- Damaged components reduce calculated stats proportionally
- Components at/below 30% HP become inactive
- Armor never degrades, mass never degrades
