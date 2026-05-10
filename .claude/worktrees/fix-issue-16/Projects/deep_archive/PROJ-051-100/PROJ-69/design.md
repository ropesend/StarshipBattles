# PROJ-69: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Build Queue Architecture
- **Single queue per entity:** `Planet.construction_queue: list` (planet.py:89) and `Fleet.construction_queue: List[Dict]` (fleet.py:70)
- **Queue item format:** `{"design_id": str, "type": str, "turns_remaining": int}`
- **BuildContext protocol** (build_context.py): Unified interface for Planet/Fleet with `construction_queue`, `has_space_shipyard`, `can_build_type()`, `context_type`
- **Production engine** (production_engine.py): Processes only `construction_queue[0]` per entity per turn (FIFO)
- **UI is a full-screen modal** (build_queue_screen.py, 653 lines) with panels: context report (580w), filter (200w), available designs (360w), build queue (flexible), design report (400w)
- **Separated concerns:** BuildQueueController (business logic), BuildQueueDragHandler (drag-drop), BuildQueuePortraitLoader (assets)

### Planet Facilities System
- `PlanetaryFacility` dataclass (planet.py:24-30): `instance_id`, `design_id`, `name`, `design_data`, `is_operational`
- Facilities stored in `Planet.facilities: List[PlanetaryFacility]` (planet.py:96)
- Shipyard detection: `has_space_shipyard` property scans facilities for component `id == "space_shipyard"` or ability `"SpaceShipyard"` (planet.py:147-165)
- Fleet shipyard: scans combat ships for `id == "fleet_space_yard"` (fleet.py:131-152)

### Hex Lookup
- `galaxy.get_planets_at_global_hex(hex)` - O(1) spatial lookup (galaxy.py:192-194)
- Fleet lookup: O(n*m) iteration via `empire.fleets` (no spatial index)
- `StrategySessionFacade.get_fleets_at_hex()` exists but returns DTOs

### Strategy Screen Integration
- `on_build_yard_click()` (strategy_screen.py:358-396): Creates BuildQueueScreen with planet as build_context
- `on_fleet_build_click()` (strategy_screen.py:449-487): Creates BuildQueueScreen with fleet as build_context
- Close callback handles fleet BUILD order auto-issuance

## Swarm Findings Summary

### Architecture
- **Polymorphic design works well:** BuildContext protocol already supports Planet/Fleet uniformly
- **Modular UI:** Screen, Controller, DragHandler, PortraitLoader are properly separated
- **Production engine is simple:** Clear FIFO processing, easy to extend for multiple queues
- **PlanetaryFacility is minimal:** Adding a `construction_queue` field is straightforward

### Key Patterns to Reuse
- **BuildContext protocol:** `game/strategy/data/build_context.py` - model for queue-source capabilities
- **UIScrollingContainer pattern:** Used in build_queue_screen.py:231-236 for scrollable lists
- **Button toggle pattern:** Used in planet_list_window.py for filter selection (no checkbox widget)
- **Virtual list rendering:** `game/ui/screens/planet_list_window.py` - for large scrollable lists
- **DI pattern:** Dependencies injected at screen creation for testability

### Dependencies & Risks
1. **Production engine processes queue[0] only** - Must change to iterate facility queues. Risk: breaking existing tests. Mitigation: base queue behavior unchanged, facility queues are additive.
2. **BuildQueueScreen tightly coupled to single build_context** - Must support multiple queue sources. Risk: complex refactor. Mitigation: introduce BuildQueueSource abstraction layer.
3. **Serialization format change** - PlanetaryFacility gains `construction_queue`. Risk: old saves incompatible. Mitigation: saves are disposable (CLAUDE.md policy).
4. **No fleet spatial index** - Finding fleets at hex requires O(n*m) iteration. Risk: performance with many empires/fleets. Mitigation: acceptable for current game scale.
5. **Drag handler assumes single queue** - All drag operations reference `build_context.construction_queue`. Risk: bugs in multi-queue mode. Mitigation: disable drag in multi-select, update for active queue source.

### Opportunities Discovered
- The `SpaceShipyardAbility` already has `construction_speed_bonus` and `max_ship_mass` fields (harvester.py:45-77) - could be used for per-shipyard production modifiers in future
- Virtual list rendering from PlanetListWindow could be reused for queue selector if lists get very long

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

## New Data Model: BuildQueueSource

```python
@dataclass
class BuildQueueSource:
    """A single build queue source from a planet facility or fleet."""
    queue_id: str           # Unique: facility instance_id or f"fleet_{fleet.id}"
    display_name: str       # "Alpha Prime - Base" or "Alpha Prime - Shipyard 1"
    owner_entity: Any       # Planet or Fleet reference
    construction_queue: List[Dict[str, Any]]  # Reference to actual queue list
    can_build_ships: bool   # True for shipyard queues
    can_build_complexes: bool  # True for base and shipyard queues
    context_type: str       # "planet" or "fleet"
```

### collect_build_queues_at_hex()
```python
def collect_build_queues_at_hex(hex_coord, galaxy, empire) -> List[BuildQueueSource]:
    """Gather all build queue sources at a hex for the given empire."""
    sources = []

    # Planets at this hex
    for planet in galaxy.get_planets_at_global_hex(hex_coord):
        if planet.owner_id != empire.id:
            continue
        # Base queue (complexes only)
        sources.append(BuildQueueSource(
            queue_id=f"planet_{planet.id}_base",
            display_name=f"{planet.name} - Base",
            owner_entity=planet,
            construction_queue=planet.construction_queue,
            can_build_ships=False,
            can_build_complexes=True,
            context_type="planet"
        ))
        # Shipyard facility queues
        shipyard_index = 0
        for facility in planet.facilities:
            if not facility.is_operational:
                continue
            if _facility_is_shipyard(facility):
                shipyard_index += 1
                sources.append(BuildQueueSource(
                    queue_id=facility.instance_id,
                    display_name=f"{planet.name} - Shipyard {shipyard_index}",
                    owner_entity=planet,
                    construction_queue=facility.construction_queue,
                    can_build_ships=True,
                    can_build_complexes=True,
                    context_type="planet"
                ))

    # Fleets at this hex
    for fleet in empire.fleets:
        if fleet.location != hex_coord:
            continue
        if not fleet.has_space_shipyard:
            continue
        sources.append(BuildQueueSource(
            queue_id=f"fleet_{fleet.id}",
            display_name=f"{fleet.name} - Space Yard",
            owner_entity=fleet,
            construction_queue=fleet.construction_queue,
            can_build_ships=True,
            can_build_complexes=True,
            context_type="fleet"
        ))

    return sources
```

## UI Layout (New)

```
┌─────────────────────────────────────────────────────────────────────┐
│ Context Rpt  │ Queue Selector  │ Build Queue    │ Design Report    │
│ (480w)       │ (200w)          │ (flexible w)   │ (400w)           │
│ top-left     │ full height     │ full height    │ full height      │
│              │ scrollable      │ shows active   │                  │
├──────┬───────┤ toggle buttons  │ queue contents │                  │
│Filter│Avail  │ for multi-sel   │                │                  │
│(200) │Designs│                 │                │                  │
│      │(280)  │                 │                │                  │
├──────┴───────┴─────────────────┴────────────────┴──────────────────┤
│ Bottom Bar (Close, Turn info)                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Queue Selector Behavior
- **Single click:** Select that queue only, deselect others, show queue contents
- **Ctrl+click / checkbox toggle:** Multi-select mode
- **Multi-select active:** Queue contents panel shows "Adding to N queues" message instead of items
- **Add to queue (multi):** Appends design to ALL selected queues
- **Each row shows:** Queue name + item count badge
