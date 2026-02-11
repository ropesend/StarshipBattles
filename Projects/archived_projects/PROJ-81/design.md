# PROJ-81: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Stats Display Bug (Issue a)
The `DesignReportPanel.update_design()` method at line 99 of `design_report_panel.py`:
1. Creates `DesignStatsPanel(manager, rect, container, ship=ship)` (line 126-132)
2. `DesignStatsPanel.__init__` calls `_build_layout(ship)` which calls `_build_sections(ship)`
3. `_build_sections` creates `StatRow` objects with default value `"--"` (design_stats_panel.py:56)
4. **But `update_stats(ship)` is never called** to populate the actual values
5. Same bug was fixed in Workshop as BUG-04: `right_panel.py:57-59` explicitly calls `self.update_stats_display(ship)`

### Production Cost Bug (Issues b, g)
Two-step data flow problem:
1. `DesignMetadata._calculate_resource_cost(data)` reads `comp_data.get("cost", {})` from raw design JSON
2. But design JSON files only store component `id` and `modifiers` - no `cost` field
3. So `resource_cost` on `DesignMetadata` is always `{}`
4. `_calculate_build_turns()` uses `design.resource_cost` -> empty -> `max_cost=0` -> returns 1

**Correct path exists:** `ShipStatsCalculator.recalculate_stats()` (ship_stats.py:94-104) correctly calculates `ship.construction_cost` by calling `comp.get_resource_cost()` on instantiated components, which reads from the component registry data (`data.get("resource_cost", {})`).

**Fix approach:** Modify `_calculate_build_turns()` and `_build_cost_tracking()` to load the ship via `design_loader` and use `ship.construction_cost` instead of the broken `design.resource_cost`. The `refresh_design_report()` method already does this pattern (controller.py:517-539).

### Layout Analysis
- Target display: 2560x1600 minimum, optimized for 4K (3840x2160)
- Current layout (left to right): Context(480) + QueueSelector(280) + BuildQueue(dynamic) + DesignReport(750)
- At 2560px: 2560-480-280-750-50(gaps) = 1000px for BuildQueue
- Widening QueueSelector to 700px at 2560: 2560-480-700-750-50 = 580px for BuildQueue (still ample)
- At 3840px: even more spacious

## Architecture

### Data Flow: Design -> Stats Display
```
Design JSON file
  -> DesignLibrary.load_design_data(design_id) -> raw dict
  -> SimulationDesignLoader.load_ship_from_design_data(data) -> Ship object
  -> ShipStatsCalculator.recalculate_stats(ship) -> populates ship.construction_cost, etc.
  -> DesignReportPanel.update_design(ship)
  -> DesignStatsPanel._build_layout(ship) -> creates StatRow layout
  -> DesignStatsPanel.update_stats(ship) -> MUST BE CALLED to populate values
```

### Data Flow: Add to Queue
```
User clicks "Add to Queue"
  -> BuildQueueController.add_to_queue(design_id)
  -> _calculate_build_turns(design_id, build_rate)
     -> Currently: uses design.resource_cost from DesignMetadata (BROKEN - empty)
     -> Fix: load ship, use ship.construction_cost
  -> _build_cost_tracking(design_id, turns)
     -> Currently: uses design.resource_cost from DesignMetadata (BROKEN - empty)
     -> Fix: use ship.construction_cost
  -> Creates queue_item dict with total_cost, cost_per_tick, etc.
```

### Key Patterns to Reuse
- **BUG-04 Fix Pattern**: `right_panel.py:57-59` - always call `update_stats(ship)` after creating stats panel
- **Ship Loading Pattern**: `controller.refresh_design_report()` (lines 517-539) - loads design via `design_loader.load_ship_from_design_data()`
- **Resource Cost from Ship**: `ship.construction_cost` dict is correctly populated by `ShipStatsCalculator`
- **Dynamic Header Update**: Queue selector buttons already update via `_refresh_queue_selector()` - same pattern for header text

### Dependencies & Risks
1. **Performance of loading ship for cost calculation** - Loading a full Ship object just to get `construction_cost` may be slower than reading from metadata. Mitigated by the fact that this only happens when adding to queue (not on every frame).
2. **Column spacing change** - Wider resource icon columns may overflow on narrow build queue panels. Mitigated by targeting 2560+ displays.

### Opportunities Discovered
- Could cache loaded ship's `construction_cost` on the `DesignMetadata` object for future use
- Could also fix `DesignMetadata._calculate_resource_cost()` to use the component registry for a proper long-term fix
