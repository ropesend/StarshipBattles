# PROJ-74: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Existing Fuel System
- Fuel tanks already allow "Planetary Complex" in `allowed_vehicle_types` (`data/components.json:243-247`)
- `ResourceGeneration` ability exists for energy generation (`game/simulation/components/abilities/resources.py:191-228`)
- `ShipInstance` already has `resupply()` method for adding fuel (`game/strategy/data/ship_instance.py`)
- `Galaxy.get_planets_at_global_hex()` provides O(1) lookup for fleets at planet locations

### Gap Identified
- `PlanetaryFacility` has no `resource_levels` field - cannot track current fuel storage
- No inter-ship resource sharing exists - each ship tracks resources independently
- No mechanism for transferring resources from complexes to ships

## Swarm Findings Summary

### Architecture
- ResupplyEngine should fit in Phase 0 of `_process_tick()` (same timing as ResourceManagementEngine)
- Follow existing engine DI pattern: `__init__(self, *, registries: GameRegistries)`
- TurnEngine needs `resupply_engine` property with lazy initialization
- PlanetaryFacility needs `resource_levels: Dict[str, float]` field added

### Key Patterns to Reuse
- **Engine DI Pattern**: `game/strategy/engine/resource_management_engine.py:42-55` - strict registries DI with TypeError on None
- **Ability Query**: `game/strategy/data/build_queue_source.py:42-67` - scanning design_data layers for component abilities
- **Spatial Lookup**: `galaxy.get_planets_at_global_hex(fleet.location)` - O(1) location check
- **Serialization**: Follow `ShipInstance.to_dict()/from_dict()` pattern for facility resources
- **Result Dataclass**: Use `@dataclass` for ResupplyEvent (like ResourceDepletion, MovementResult)

### Dependencies & Risks
1. **Multiple fleets simultaneous draw** - Use owner priority + sequential processing per tick
2. **Save/load persistence** - Add resource_levels to PlanetaryFacility serialization (to_dict/from_dict)
3. **Complex goes offline mid-turn** - Check `is_operational` before each generation/transfer operation
4. **Performance O(n²)** - Use `galaxy.get_planets_at_global_hex()` for O(1) spatial indexing

### Opportunities Discovered
- Fuel tank component already allows Planetary Complex - no modification needed
- ResourceGeneration ability can be reused directly for fuel (just change resource type to "fuel")
- Existing test patterns in `tests/unit/strategy/engine/` provide clear templates

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

## Range Equalization Algorithm

The user requested that fuel be distributed to equalize range across all fleet ships:

```python
def _calculate_fuel_distribution(self, fleet, available_fuel):
    """
    Distribute fuel to equalize range across all ships.
    All ships get enough fuel for the same hex range.
    Tankers (high capacity, low consumption) may be partially filled.
    """
    # Calculate fleet's total fuel cost per hex
    total_cost_per_hex = sum(
        ship.get_fuel_cost_per_hex()
        for ship in fleet.ships
        if ship.is_combat_capable()
    )
    if total_cost_per_hex <= 0:
        return {}

    # Calculate max range achievable with available fuel + current fuel
    current_total_fuel = sum(ship.get_current_fuel() for ship in fleet.ships)
    max_range = (available_fuel + current_total_fuel) / total_cost_per_hex

    # Each ship gets fuel for max_range hexes (capped at tank capacity)
    distribution = {}
    for ship in fleet.ships:
        target_fuel = ship.get_fuel_cost_per_hex() * max_range
        target_fuel = min(target_fuel, ship.get_fuel_capacity())
        deficit = target_fuel - ship.get_current_fuel()
        distribution[ship] = max(0, deficit)

    return distribution
```

### Example
- Fleet has 3 ships: Cruiser (100 fuel capacity, 2 fuel/hex), Tanker (500 capacity, 1 fuel/hex), Scout (50 capacity, 0.5 fuel/hex)
- Total cost/hex: 2 + 1 + 0.5 = 3.5 fuel/hex
- Available fuel: 350 from complex
- Max range: 350 / 3.5 = 100 hexes
- Cruiser gets: 2 * 100 = 200 (capped at 100) = 100 fuel (full)
- Tanker gets: 1 * 100 = 100 fuel (partial - has 500 capacity)
- Scout gets: 0.5 * 100 = 50 fuel (full)
- All ships can now travel 100 hexes together

## Turn Processing Flow

```
TURN (100 ticks):
├─ FOR tick 1-100: _process_tick()
│  ├─ Phase 0: Per-turn resource consumption (ResourceManagementEngine)
│  ├─ Phase 0a: Fuel generation at facilities (ResupplyEngine) [NEW]
│  ├─ Phase 0b: Fleet resupply from facilities (ResupplyEngine) [NEW]
│  ├─ Phase 1: Instant orders (FleetOrderProcessor)
│  ├─ Phase 2: Calculate moves (FleetMovementEngine)
│  ├─ Phase 3: Apply moves (FleetMovementEngine)
│  └─ Phase 4: Combat (ConflictResolutionEngine)
├─ End-of-turn orders
├─ Production phase
├─ Fleet production phase
└─ Population growth phase
```
