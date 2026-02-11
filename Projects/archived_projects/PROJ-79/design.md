# PROJ-79: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Build Queue Architecture
The build queue system has a multi-source architecture (PROJ-69) with three queue types:
1. **Planet base queue** (`planet.construction_queue`) - complexes only
2. **Shipyard facility queues** (`facility.construction_queue`) - ships + complexes, one per shipyard
3. **Fleet space yard queues** (`fleet.construction_queue`) - ships + complexes when in BUILD order

All three are abstracted via `BuildQueueSource` dataclass discovered by `collect_build_queues_at_hex()`.

### Key Findings
- `turns_remaining` is hardcoded to `turns=1` in all `add_to_queue()` calls (controller lines 220, 256, 290)
- `SpaceShipyardAbility` has `construction_speed_bonus` (1.0x) and `max_ship_mass` (100k) but they are **completely unused** in production
- Production completion happens at end-of-turn only (`process_production()` at turn_engine.py line 272), not during the 100-tick loop
- Per-tick resource consumption exists (PROJ-75) but only deducts resources; doesn't check for completion
- `_spawn_fleet_complex()` blindly uses `planets_at_hex[0]` with no target planet selection
- Resource portrait icons exist at `assets/Images/Resource Portraits/` but are unused in the UI
- Queue selector uses `#queue_selector_selected` vs `#queue_selector_item` object IDs for theming but visual distinction may be insufficient

### Current Turn Structure
```
process_turn():
  0. Harvesting (extract planetary resources)
  0b. Maintenance (deduct 5% build cost)
  1. Subturn loop (ticks 1-100):
     0: Per-turn resource consumption
     0a: Fuel generation
     0b: Fleet resupply
     0c: Construction resource consumption (cost_per_tick deduction)
     1: Join fleet orders
     2: Calculate movements
     3: Apply movements
     4: Combat
  2. End-of-turn orders (colonize)
  3. Production (colony queues - decrement turns, spawn)
  4. Fleet production (fleet queues - decrement turns, spawn)
  5. Population growth
```

## Swarm Findings Summary

### Architecture
- **Build Queue Screen** (`build_queue_screen.py`, 1076 lines): Full-screen modal with 7 panels. Queue selector is 200px wide at position x=500.
- **BuildQueueController** (`build_queue_controller.py`, 337 lines): Business logic for add/filter operations. Supports single-queue, multi-queue, and fallback modes.
- **ProductionEngine** (`production_engine.py`, 524 lines): Handles end-of-turn completion + per-tick cost deduction. Two separate code paths for colony and fleet production.
- **HarvestingEngine** (`harvesting_engine.py`, 294 lines): Runs once at turn start. Scans facilities for ResourceHarvester abilities, extracts resources based on `base_rate * quality`.

### Key Patterns to Reuse
- **PlanetSelectionWindow**: `game/ui/screens/planet_selection_window.py` - UIWindow with UISelectionList + PlanetReportPanel + callback. Currently colonization-specific (hardcoded title). Easy to generalize.
- **Multi-select with Ctrl+Click**: `empire_build_queue_window.py` lines 300-333 - Set[int] with toggle logic. Already used in build queue screen for queue sources.
- **Selection Highlighting**: Two patterns available - object_id theming (line 295) and draw() border overlay (line 1065-1072).
- **Column System**: `empire_build_queue_window.py` lines 88-97 - Dict-based column definitions with header labels and value extraction.
- **Resource Format**: `_format_resource_cost()` at build_queue_screen.py line 558 - Abbreviations M, O, V, R, E.
- **Cost Tracking**: PROJ-75 queue item fields: `total_cost`, `cost_per_tick`, `resources_consumed`, `ticks_in_current_turn`.

### Dependencies & Risks
1. **Tick-granular production changes the turn structure** - Moving completion from end-of-turn into per-tick requires careful integration with spawning, harvesting, and storage recalculation. Risk: ordering issues where spawned facilities interact with same-tick processing.
2. **Mid-turn harvesting** - HarvestingEngine runs once at turn start. Adding proportional harvest for mid-turn spawns requires either a callback from ProductionEngine or a standalone harvest function. Risk: double-harvesting if not careful.
3. **Legacy queue items** - Existing queue items in save files won't have cost tracking fields. The tick processor already handles this (skips items without `cost_per_tick`). These items fall through to end-of-turn processing which still works.
4. **PlanetSelectionWindow generalization** - Changing constructor signature could break existing colonization callers if not done carefully with defaults.

### Opportunities Discovered
- `construction_speed_bonus` on SpaceShipyardAbility is ready to use but never wired in - this project activates it
- Resource portraits already exist - just need to load and display them
- PROJ-75 cost tracking infrastructure is in place - just needs completion detection added to the tick loop

## Design Decisions

### Build Rate Formula
```
build_rate = 2000.0 (Planetary Yard) or 3000.0 (Shipyard)
max_resource_cost = max(total_cost.values())  # Most expensive single resource
turns = max(1, ceil(max_resource_cost / build_rate))

# Per-tick cost is proportional for all resources:
cost_per_tick = {res: total_cost[res] / (turns * 100) for res in total_cost}
```

Example: Design costs {Metals: 100000, Organics: 10000} at Planetary Yard (2000/turn):
- max_resource = 100000 (Metals)
- turns = ceil(100000 / 2000) = 50
- cost_per_tick = {Metals: 20, Organics: 2}  (per tick, x100 = per turn: 2000 Met, 200 Org)

### Tick-Granular Production Flow
```
process_construction_tick(tick, empires, galaxy, save_path):
  for each queue:
    item = queue[0]
    if empire.has_resources(cost_per_tick):
      consume_resources(cost_per_tick)
      resources_consumed += cost_per_tick
      if all resources_consumed >= total_cost:
        queue.pop(0)
        spawn(item)  # spawn ship/complex immediately
        if tick < 100 and queue:
          start processing next item in same tick
```

### Queue Item Schema (after PROJ-79)
```python
{
    "design_id": str,
    "type": str,  # "ship", "complex", "fighter", "satellite"
    "turns_remaining": int,  # calculated from cost (for display/legacy)
    # Cost tracking (PROJ-75, now mandatory for new items):
    "total_cost": Dict[str, float],
    "cost_per_tick": Dict[str, float],
    "resources_consumed": Dict[str, float],
    "ticks_in_current_turn": int,
    # New in PROJ-79:
    "target_planet_id": Optional[int],  # only for fleet-built complexes
}
```

### BuildQueueSource Schema (after PROJ-79)
```python
@dataclass
class BuildQueueSource:
    queue_id: str
    display_name: str  # "Earth - Planetary Yard", "Earth - Shipyard 1"
    owner_entity: Any
    construction_queue: List[Dict[str, Any]]
    can_build_ships: bool
    can_build_complexes: bool
    context_type: str  # "planet" or "fleet"
    build_rate: float = 2000.0  # NEW: resources per turn
    planet_id: Optional[int] = None  # NEW: which planet this queue builds for
```

### Mid-Turn Facility Activation
When a complex spawns mid-turn at tick N:
1. Facility created with `is_operational=True`
2. **Storage:** `harvesting_engine.recalculate_storage(empires)` called immediately so empire storage capacity increases
3. **Harvesting:** One-time proportional harvest: `harvest = base_rate * quality * ((100 - N) / 100.0)`, added to empire pool

See [decisions.md](decisions.md) for the full log with rationale.
