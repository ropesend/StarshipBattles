
## Status
*   **Phase 1**: Data Schema & Utilities (Complete)
*   **Phase 2**: Ship Logic Refactor (Complete)
*   **Phase 3**: Physics & Combat Integration (Complete)
*   **Phase 4**: UI & Builder Updates (Complete)
*   **Phase 5**: Data Migration (Complete) - Verified Clean
*   **Phase 6**: Cleanup & Verification (Complete) - Legacy Code Removed

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

### Phase 5: Data Migration (Complete)
1.  **Update `components.json`**: Verified that all `fuel_cost`, `energy_cost`, etc. keys have been removed and replaced with `abilities`.
2.  **Verify Ship Files**: Checked `data/ships/*.json` and `data/vehicleclasses.json`; no legacy keys found.

### Phase 6: Cleanup & Verification (Complete)
1.  **Remove Legacy Code**: Deleted `_apply_legacy_shim` and `_ensure_consumption` from `components.py`.
2.  **Strict Initialization**: Updated Component subclasses (`Engine`, `Tank`, `Weapon`, `Generator`) to strictly load from `abilities`.
3.  **Regression Testing (Fixed)**:
    *   **Unit Tests**: Resolved regressions in `test_modifiers.py`, `test_shields.py`, `test_scaling_logic.py`, and `test_ship_loading.py`.
    *   **Test Pollution**: Fixed `test_ui_dynamic_update.py` by removing harmful `importlib.reload` calls.
    *   **Registry**: Added `EnergyConsumption` to `ABILITY_REGISTRY` in `resources.py` to support legacy data equivalence.
    *   **Data**: Added missing `efficient_engines` modifier to `modifiers.json`.
    *   **Verified**: 100% pass rate on resource-related unit tests.

## What May Be Needed (Post-Migration)
1.  **Monitor for Regressions**: Watch for any persistent "0 resource" bugs in UI (unlikely after fixes).
2.  **Visual Polish**:
    *   **Colors**: Ensure default resource bar colors are distinct (possibly hash-based or manually mapped).
    *   **Icons**: Add support for resource icons in the UI (Stats Panel and HUD).
3.  **Regression Testing**: 
    *   Verify that saved ship designs load correctly with the new schema.
    *   Ensure older "standard" ships from `vehicleclasses.json` behave identically in combat simulation (endurance, ammo counts) as before.

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

### Phase 7: Final Cleanup (Complete)
1.  **Redundant Data Removal**:
    *   Removed `self.capacity` and `self.resource_type` from `Tank` component.
    *   Refactor: `Tank` now relies purely on `ResourceStorage` abilities.
    *   Tests: Updated `test_components.py` and added `test_storage_capacity_modifier`.
2.  **Wrapper Deprecation**:
    *   Added `DeprecationWarning` to `ship.current_fuel`, `ship.max_fuel`, etc.
    *   These properties still work (proxy to `ship.resources`) but log warnings.
3.  **UI Modernization**:
    *   Refactored `ShipStatsPanel` (`battle_panels.py`) to dynamically iterate `ship.resources`.
    *   Result: New resources (e.g. Biomass) will automatically appear in the Battle UI.
    *   Removed hardcoded Fuel/Energy/Ammo blocks.

## Post-Refactor Status & Handover
*   **Refactor Complete**: The system is fully migrated. No legacy logic remains active.
*   **Known Issues (Tests)**:
    *   There appear to be regressions in some `unit_tests/` (e.g. `test_slider_increment.py` is open).
    *   **Context for Fixes**: Any test failures related to "missing attribute 'current_fuel'" in *mock* objects likely need those mocks updated to include the wrapper property or a `resources` mock. PROD code has the wrappers, but mocks might not.
    *   **Battle UI**: Verified working dynamically.
    *   **Tank**: Verified strict ability usage.
