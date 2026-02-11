# PROJ-67: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Space Yard System (Planet-Based)
The existing space yard system is entirely planet-centric:

1. **Component:** `space_shipyard` in `data/components.json` with `SpaceShipyard` ability
   - `allowed_vehicle_types: ["Planetary Complex"]` - only complexes can have it
   - Properties: `construction_speed_bonus` (1.0x default), `max_ship_mass` (100,000)

2. **Detection:** `Planet.has_space_shipyard` property scans facilities for the component

3. **Build Queue:** `Planet.construction_queue` is a list of dicts:
   ```python
   {"design_id": str, "type": str, "turns_remaining": int}
   ```

4. **Production:** `ProductionEngine.process_production()` iterates `empire.colonies` → queues
   - Ships/fighters/satellites require `colony.has_space_shipyard == True`
   - Complexes don't require shipyard
   - Completed items: complexes → `planet.facilities`, ships → new Fleet at planet hex

5. **UI:** `BuildQueueScreen` is a full-screen modal tightly coupled to `Planet` objects
   - `BuildQueueController` manages business logic (category filtering, queue operations)
   - `BuildQueuePortraitLoader` handles design portrait images
   - `BuildQueueDragHandler` handles drag-and-drop

### Fleet System
- `Fleet` has `ships: List[ShipInstance]`, `orders: List[FleetOrder]`, `location: HexCoord`
- `OrderType` enum: MOVE, COLONIZE, MOVE_TO_FLEET, JOIN_FLEET
- No explicit "locked" or "can_move" property - movement is order-driven
- Fleet speed calculated as minimum of all ships' speeds
- `FleetMovementEngine` handles movement; `FleetOrderProcessor` handles order lifecycle

### Key Observations
- **No fleet-level construction queue** exists yet
- **No BUILD order type** exists
- **BuildQueueScreen** is hardcoded to `Planet` - needs abstraction
- **ProductionEngine** only processes `empire.colonies` - needs to also process fleets
- **Fleet has no `has_space_shipyard` check** - needs to be added

## Swarm Findings Summary

### Architecture
The system follows clean separation of concerns:
- **Data layer:** `game/strategy/data/` (Fleet, Planet, ShipInstance)
- **Engine layer:** `game/strategy/engine/` (TurnEngine, ProductionEngine, FleetMovementEngine)
- **Service layer:** `game/strategy/services/` (FleetSpeedCalculator, FleetNavigationService)
- **Facade layer:** `game/strategy/facade/` (DTOs, StrategySessionFacade)
- **UI layer:** `game/ui/` (screens, panels)

The `TurnEngine` orchestrates: subticks (movement/combat) → end-of-turn orders → production.

### Key Patterns to Reuse
- **SpaceShipyardAbility:** `game/simulation/components/abilities/harvester.py:45-77` - marker ability with speed bonus
- **BuildQueueController:** `game/ui/panels/build_queue_controller.py` - extracted business logic pattern
- **ProductionEngine spawn pattern:** `game/strategy/engine/production_engine.py:118-173` - ship spawning
- **FleetOrder pattern:** `game/strategy/data/fleet.py:18-43` - order serialization
- **DI pattern in TurnEngine:** `game/strategy/engine/turn_engine.py:83-134` - lazy engine init

### Dependencies & Risks
1. **BuildQueueScreen coupling to Planet** - The screen directly accesses `self.planet` throughout. Refactoring to a generic "build context" requires careful abstraction. Mitigate with a `BuildContext` protocol/interface.
2. **ProductionEngine coupling to empire.colonies** - Only iterates planets. Must extend to iterate fleet build queues too. Keep the same engine, add fleet processing.
3. **Fleet serialization** - Adding `construction_queue` to Fleet requires save/load changes. Must update `Fleet.to_dict()` and `Fleet.from_dict()`.
4. **Movement blocking** - BUILD order must prevent movement. The `FleetMovementEngine` skips fleets with no MOVE orders, but we need to ensure BUILD doesn't get picked up as a MOVE.

### Opportunities Discovered
- The `BuildQueueController` was already extracted (PROJ-63) as a separate class, making it easier to generalize
- The `FleetOrderProcessor` already handles end-of-turn orders, making it the natural place for BUILD processing
- `SpaceShipyardAbility` already has `construction_speed_bonus` and `max_ship_mass` - can be used for fleet yards too

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

## Architecture: BuildContext Abstraction

The key architectural change is introducing a `BuildContext` protocol that both `Planet` and `Fleet` can satisfy:

```python
class BuildContext(Protocol):
    """Anything that can have a build queue."""
    @property
    def name(self) -> str: ...
    @property
    def construction_queue(self) -> list: ...
    @property
    def has_space_shipyard(self) -> bool: ...
    @property
    def owner_id(self) -> int: ...

    def can_build_type(self, vehicle_type: str) -> bool:
        """Whether this context can build the given vehicle type."""
        ...
```

**Planet** already satisfies most of this. **Fleet** needs:
- `construction_queue: list` field added
- `has_space_shipyard` property checking ship components
- `can_build_type()` method checking proximity rules

## Architecture: Fleet Production Flow

```
Player selects fleet → Opens BuildQueueScreen(fleet_context)
  → Adds designs to fleet.construction_queue
  → Issues BUILD order to fleet

TurnEngine.process_turn():
  1. Subtick loop:
     - Fleet with BUILD order: speed effectively 0 (skipped by movement)
  2. End-of-turn orders:
     - FleetOrderProcessor handles BUILD: validates fleet still has yard
  3. Production:
     - ProductionEngine processes fleet build queues (new path)
     - Completed ships → fleet.add_ship_instance()
     - Completed complexes → planet.facilities (if at planet hex)
```

## Architecture: Complex-Near-Planet Validation

For complex building, the fleet must be at the same hex as a planet:
1. `fleet.can_build_type("complex")` checks `galaxy.get_planets_at_global_hex(fleet.location)`
2. BuildQueueController validates before adding to queue
3. ProductionEngine validates again at spawn time (fleet may have moved)
4. If fleet moves away while complex is in queue → complex build pauses (not cancelled)
