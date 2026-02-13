# PROJ-101: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Fleet Report Architecture
The Fleet Report Window (`game/ui/screens/fleet_report_window.py`, 855 lines) has a three-panel layout:
- **Left Sidebar** (300px): Fleet stats, filters, column toggles
- **Center Ship List** (dynamic): Virtual-scrolling ship list with column headers
- **Right Detail Panel** (350px): ShipDetailPanel showing instance damage/status

State management is split across:
- `FleetListViewModel` (fleet_report_view_model.py) — filter + sort state
- `ColumnManager` (column_manager.py) — column definitions + value extraction
- `fleet_report_filters.py` — filter_ships() and sort_ships() pure functions

### DesignReportPanel Integration Path
Build Queue uses this flow to display ship designs:
1. `BuildQueueController.refresh_design_report(design_id)` (build_queue_controller.py:561)
2. Loads design_data via `DesignLibrary.load_design_data(design_id)`
3. Creates Ship via `SimulationDesignLoader.load_ship_from_design_data(design_data, x, y)`
4. Passes Ship to `DesignReportPanel.update_design(ship)`

For Fleet Report, the path is simpler since we already have `ShipInstance.design_data`:
1. On ship click, get `ship_instance.design_data`
2. Create Ship via `DesignLoaderAdapter.load_ship_from_design_data(design_data, 0, 0)`
3. Pass Ship to `DesignReportPanel.update_design(ship)`

### Ship Data Properties Available
From `ShipInstance.get_calculated_stats()`:
- `mass` (float) — ship tonnage
- `resource_storage` (dict) — resource capacities by type
- `cargo_storage` (dict) — cargo capacities by type (e.g., 'passengers')
- `strategic_movement` (float) — movement points for speed calculation
- `warp_max_tonnage` (int) — warp capability indicator
- `warp_resource_costs` (dict) — warp resource requirements

From ShipInstance directly:
- `resource_levels` (dict) — current resource amounts
- `cargo_contents` (dict) — current cargo amounts
- `get_resource_percentage(resource)` — resource fill percentage

Speed formula: `floor((strategic_movement * 25) / mass)`, clamped 0-10 (FleetSpeedCalculator)

### Existing Patterns
- **Multi-select**: empire_build_queue_window.py:304-337 — `selected_indices: Set[int]`, Ctrl+click toggle
- **Column definitions**: column_manager.py:15-23 — dict with id, width, title, visible, type
- **Filter toggle buttons**: fleet_report_window.py:242-294 — UIButton with [Label]/Label states
- **Ship removal**: Fleet.remove_ship(ship) exists (fleet.py:115-121), triggers speed recalc

## Swarm Findings Summary

### Architecture
- Clean separation: ColumnManager handles data, FleetListViewModel handles state, pure functions handle filtering/sorting
- Virtual scrolling with row pool pattern enables large fleets
- ShipDetailPanel is self-contained with its own event handling and scroll container

### Key Patterns to Reuse
- **Multi-select**: `empire_build_queue_window.py:304-337` — Set-based Ctrl+click
- **Design loading**: `build_queue_controller.py:561-597` — DesignLoaderAdapter pattern
- **Filter toggles**: `fleet_report_window.py:242-294` — UIButton select/unselect
- **Column value extraction**: `column_manager.py:118-157` — elif chain in get_column_value()
- **Sort keys**: `fleet_report_filters.py:177-195` — get_sort_key() closure

### Dependencies & Risks
1. **DesignReportPanel requires Ship object** — Need DesignLoaderAdapter conversion. Performance: cached via get_calculated_stats(). Only converts on click, not per-row.
2. **Empire reference needed for fleet creation** — Thread through from strategy_window_manager.py. Self.scene.current_empire is readily available.
3. **Sidebar vertical overflow** — Adding 4 filter buttons (~120px). Current sidebar uses ~800px. At 1600px min height, usable is ~1390px. Safe.
4. **Latent bug: _update_sidebar()** — Called on line 778 but method doesn't exist (renamed to _update_summary in PROJ-44). Fix in Phase 1.

### Opportunities Discovered
- DesignReportPanel shows comprehensive design specs (weapons, shields, armor, movement) which is more informative than ShipDetailPanel's limited status view
- FleetCapabilityCalculator.ship_has_spaceyard() can be reused by both column value extraction and filter logic

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
