# PROJ-70: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

The Fleet Details panel (bottom third of right sidebar in `strategy_ui.py`) currently shows minimal info: fleet ID, owner, ship count, location, and an order list. The code has a duplication problem: inline fleet formatting in `strategy_ui.py:561-600` duplicates `format_fleet_info()` in `strategy_detail_fmt.py:203-240`, and neither version is complete (inline has BUILD handling, fmt has TRANSFER handling).

**Baseline:** 6519 tests passing.

## Swarm Findings Summary

### Architecture
- Fleet detail formatting is inlined in `strategy_ui.py` instead of using the dedicated `format_fleet_info()` function
- `format_fleet_info()` in `strategy_detail_fmt.py` exists but is **never called by the UI** at runtime
- The PlanetReportPanel pattern (PROJ-54) provides a good reference but is overkill here - a simple formatting function consolidation is sufficient
- All fleet properties needed for display are safe to access from UI layer (no side effects, no new cross-layer imports needed)
- Fleet objects are live references (not snapshots) - display is always current at selection time

### Key Patterns to Reuse
- **HTML formatter pattern**: `strategy_detail_fmt.py:58-160` - `format_planet_info()` builds HTML with `<b>Label:</b> value<br>` pattern
- **K/M number formatting**: `strategy_detail_fmt.py:100-112` - inline population formatting
- **Fleet capability methods**: `fleet.py:506-522` - `get_capability_summary()` provides speed, fuel endurance, warp info
- **Cargo aggregation**: `fleet.py:541-554` - `get_fleet_cargo_current(cargo_type)` already aggregates across ships
- **Ship stats access**: `ship_instance.py:179` - `get_calculated_stats()` returns cached dict including mass
- **Mock patterns**: `tests/conftest.py` - `make_mock_ship_instance()` helper; existing test file uses MagicMock

### Dependencies & Risks
1. **Destroyed ship cargo asymmetry**: `get_fleet_cargo_capacity()` uses combat-capable ships only, but `get_fleet_cargo_current()` uses ALL ships. For display purposes, iterate `cargo_contents` directly on all ships to show what's physically on them.
2. **Empty fleet**: `fuel_endurance()` returns -1 for empty fleets (safe), `speed` is 0 (safe). Handle display gracefully.
3. **Missing design_data**: `get_calculated_stats()` can return empty dict. Default mass to 0 for sorting.
4. **No existing ship-grouping utility**: Must implement grouping by `design_id` with `collections.Counter`.
5. **PROJ-68 in-flight changes**: TRANSFER order handling exists in `format_fleet_info()` but not in the inline code - both must be merged.

### Opportunities Discovered
- Consolidate inline formatting with `format_fleet_info()` to eliminate code duplication
- Add BUILD order handling that was missing from the formatter
- All data needed is already available on the Fleet/ShipInstance objects - no new data sources required

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

**Key decisions:**
1. Enhance `format_fleet_info()` rather than creating a FleetReportPanel class (simpler, sufficient)
2. Use `ship.get_calculated_stats()['mass']` for sorting (cached, called once per unique design)
3. Aggregate cargo by iterating all ships' `cargo_contents` dicts (data-driven, future-proof)
4. Show both speed (hex/turn) and fuel endurance (total hexes)
5. Remove inline fleet code from `strategy_ui.py` and call `format_fleet_info()` instead
