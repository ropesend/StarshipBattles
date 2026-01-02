
## Status
*   **Phase 1**: Data Schema & Utilities (Complete)
*   **Phase 2**: Ship Logic Refactor (Complete)
*   **Phase 3**: Physics & Combat Integration (Complete)
*   **Phase 4**: UI & Builder Updates (Complete)
*   **Phase 5**: Data Migration (Pending)

## Goal
Unify the handling of Fuel, Energy, and Ammunition (and potential future resources) into a single, generic **Resource System**. This removes hardcoded fields like `fuel_cost` or `max_energy` and replaces them with data-driven "Abilities" attached to components.

## Core Concepts

### 1. Generic Resource Logic
Instead of hardcoded properties (`ship.current_fuel`), the Ship class will maintain a dynamic registry of resources.
*   **Data Structure**: `ship.resources = { "fuel": ResourceState, "energy": ResourceState, ... }`
*   **ResourceState**: Object tracking `current`, `max`, `regeneration_rate`.

### 2. Component Abilities
Components will define their interaction with resources via the `abilities` dictionary in `components.json`.

#### Consumption
Usage of a resource.
```json
"abilities": {
    "ResourceConsumption": [
        { 
            "resource": "fuel", 
            "amount": 0.5, 
            "trigger": "constant" // Options: "constant" (per tick/sec), "activation" (per use/shot)
        },
        {
            "resource": "energy",
            "amount": 10.0,
            "trigger": "activation"
        }
    ]
}
```

#### Storage
Capacity for a resource.
```json
"abilities": {
    "ResourceStorage": [
        { "resource": "fuel", "amount": 100.0 }
    ]
}
```

#### Generation
Passive regeneration of a resource.
```json
"abilities": {
    "ResourceGeneration": [
        { "resource": "energy", "amount": 5.0 }
    ]
}
```

## Implementation Steps

### Phase 1: Data Schema & Utilities (Complete)
1.  **Define `ResourceState` class**: Handling clamping, regeneration, and consumption checks.
2.  **Update `Component` class**: Add helper methods to parse `ResourceConsumption`, `ResourceStorage`, and `ResourceGeneration` abilities from the `data` dictionary.
    *   `get_consumption(trigger_type)`: Returns list of required resources for that trigger.
    *   `get_storage_capacity()`: Returns dict of capacities provided.

### Phase 2: Ship Logic Refactor (Complete)
1.  **Refactor `Ship.__init__`**: Initialize `self.resources` dictionary.
2.  **Refactor `Ship.recalculate_stats()`**: 
    *   Iterate all components.
    *   Sum up `ResourceStorage` abilities to set `max` for each resource.
    *   Sum up `ResourceGeneration` abilities to set `regen` rates.
3.  **Refactor `Ship.update()`**:
    *   Apply regeneration for all resources in `self.resources`.
    *   Handle "constant" consumption (e.g., Life Support, Inertial Dampeners if added).

### Phase 3: Physics & Combat Integration (Complete)
1.  **Physics (`ShipPhysicsMixin`)**:
    *   Modify `thrust_forward`: Get `constant` consumption from Active Engines.
    *   Call `ship.consume_resources(requirements)`. If false, deny thrust.
2.  **Combat (`ShipCombatMixin`)**:
    *   Modify `fire_weapons`: Get `activation` consumption from Weapon.
    *   Call `ship.consume_resources(requirements)`. If false, deny fire / set on cooldown.

### Phase 4: UI & Builder Updates (Complete)
1.  **Ship Builder Stats**:
    *   Remove hardcoded "Fuel", "Energy", "Ammo" rows.
    *   Dynamically generate stat rows based on `ship.resources.keys()`.
2.  **Battle HUD**:
    *   Dynamically render bars for any resource with `max > 0`.
    *   (Optionally preserve specific colors for known types: Fuel=Yellow, Energy=Blue, Ammo=Red).

### Phase 5: Data Migration
1.  **Update `components.json`**: Use a script to convert `fuel_cost`, `energy_cost`, `ammo_cost`, `max_fuel`, etc., into the new `abilities` format.
2.  **Update `ships/` JSON**: Remove legacy stats (`max_fuel`, etc.) and rely on calculated stats.

## Example Data Transformations

**Old Engine:**
```json
{
    "id": "engine_std",
    "thrust_force": 100,
    "fuel_cost": 0.1
}
```

**New Engine:**
```json
{
    "id": "engine_std",
    "thrust_force": 100,
    "abilities": {
        "ResourceConsumption": [{ "resource": "fuel", "amount": 0.1, "trigger": "constant" }]
    }
}
```

**Old Tank:**
```json
{
    "id": "fuel_tank_small",
    "capacity": 100,
    "resource_type": "fuel"
}
```

**New Tank:**
```json
{
    "id": "fuel_tank_small",
    "abilities": {
        "ResourceStorage": [{ "resource": "fuel", "amount": 100 }]
    }
}
```

## Benefits
*   **Extensibility**: Adding "ShieldCells", "Missiles", "Biomass" is trivial (just data).
*   **Consistency**: Logic for consuming Energy for a laser is identical to consuming Fuel for an engine.
*   **Code Cleanup**: Removes duplicate logic for managing 3 different pools.
