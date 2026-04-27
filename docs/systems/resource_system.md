# Resource System

> **Last verified:** 2026-03-31

The resource system provides a unified, data-driven framework for all material and
consumable types in the game. Both planetary materials (metals, organics, etc.) and
operational consumables (fuel, energy, ammo) are defined as **resources** in a single
catalog, with behavior determined by what components and data files reference them.

## Core Concepts

- **Resource**: Any quantifiable material or consumable tracked by the game. Defined
  in `data/resources.json` and loaded into a `ResourceCatalog`.
- **ResourceDefinition**: Immutable record of a resource type (id, name, display_group,
  has_quality).
- **ResourceCatalog**: Registry of all resource definitions. Loaded once, injected via
  `GameRegistries.resource_catalog`.

There are **no hardcoded categories**. A resource's capabilities are determined by what
references it:
- A resource referenced in `astrophysics.json` planet affinities can appear in planet deposits
- A resource referenced in component `ResourceStorage` abilities can be stored on ships
- A resource referenced in component `ResourceConsumption` abilities can be consumed in combat/movement
- A resource referenced in design `construction_cost` fields is required for construction

This means a modder can create a resource that is both mineable from planets AND consumed
by ship engines, with no code changes.

## Data Schema

### `data/resources.json`

```json
{
  "resources": [
    {
      "id": "metals",
      "name": "Metals",
      "description": "Refined metallic ores for structural construction.",
      "display_group": "planetary",
      "has_quality": true
    },
    {
      "id": "fuel",
      "name": "Fuel",
      "description": "Powers ship engines and thrusters for movement.",
      "display_group": "operational",
      "has_quality": false
    }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique lowercase identifier |
| `name` | string | yes | Display name |
| `description` | string | no | Human-readable description |
| `display_group` | string | no | UI grouping hint (e.g., "planetary", "operational") |
| `has_quality` | bool | no | Whether planet deposits track quality (default: false) |

### Current Resources

| ID | Name | Display Group | Has Quality | Purpose |
|----|------|--------------|-------------|---------|
| `metals` | Metals | planetary | yes | Structural construction material |
| `organics` | Organics | planetary | yes | Biological compounds |
| `vapors` | Vapors | planetary | yes | Volatile gases |
| `radioactives` | Radioactives | planetary | yes | Fissile materials |
| `exotics` | Exotics | planetary | yes | Rare exotic matter |
| `fuel` | Fuel | operational | no | Ship engine power |
| `energy` | Energy | operational | no | Weapons, shields, systems |
| `ammo` | Ammunition | operational | no | Kinetic/ballistic weapons |

## Code Architecture

### ResourceCatalog (`game/core/resources.py`)

```python
catalog = ResourceCatalog.from_json()          # Load from data/resources.json
catalog = ResourceCatalog.from_data(list_data) # Build from in-memory data (tests)

catalog.get("metals")                  # -> ResourceDefinition or None
catalog.has("fuel")                    # -> True
catalog.all_ids()                      # -> ["metals", ..., "fuel", ...]
catalog.all_definitions()              # -> [ResourceDefinition, ...]
catalog.by_display_group("planetary")  # -> [ResourceDefinition, ...] (5 planet resources)
catalog.by_display_group("operational")# -> [ResourceDefinition, ...] (3 ship resources)
```

### Access via DI

The catalog is available through `GameRegistries`:

```python
# Via GameRegistries (preferred)
catalog = registries.resource_catalog

# Via DefaultRegistryProvider
provider = get_default_registry_provider()
catalog = provider.get_resource_catalog()
```

### Layer Placement

`ResourceCatalog` and `ResourceDefinition` live in `game/core/` so they can be
used by both the simulation layer and the strategy layer without violating the
dependency hierarchy.

## Resource Lifecycle

```
data/resources.json
       |
       v
ResourceCatalog (loaded once at startup)
       |
       +-- Planet Generation: astrophysics.json affinities determine
       |   which resources appear in planet deposits
       |
       +-- Colonization: Drop pod deployed from ship.carried_items as
       |   PlanetaryFacility (full player-designed complex with PlanetaryYard,
       |   harvesters, storage, etc.) + seed resources
       |
       +-- Harvesting: ResourceHarvesterAbility extracts from deposits
       |   into planet.stockpile (local storage)
       |
       +-- Construction: ProductionEngine consumes from planet.stockpile
       |   (or fleet cargo for fleet-bound shipyards)
       |   based on design construction_cost
       |
       +-- Ship Initialization: ResourceStorage abilities determine
       |   what consumables a ship carries
       |
       +-- Combat: ResourceConsumption/ResourceGeneration abilities
       |   consume and regenerate consumables per tick
       |
       +-- Strategic Movement: FleetConsumableAggregator tracks per-hex
           and warp resource costs across fleet ships
```

## Local Resource Storage

Resources are stored locally on each planet, not in a global empire pool.

- **`planet.deposits`**: Raw mineral data (`{quantity, quality}`) — what's underground
- **`planet.stockpile`**: Harvested resources available for use (`Dict[str, float]`)
- **`planet.max_stockpile`**: Storage capacity per resource (`Dict[str, float]`), set by `LocalStorageAbility` components on facilities

The `HarvestingEngine` extracts from `deposits` into `stockpile`. The `ProductionEngine`
draws from `stockpile` for construction. Resources must be transferred between planets
via cargo ships.

The empire-level `resource_pool` is a read-only computed property (sum of all colony
stockpiles plus `_fleet_resource_pool`). It cannot be mutated directly — to add
resources, use `planet.add_to_stockpile()` on each colony.

## Resource Transfers

Resources are moved between planets and fleets via the transfer order system:

1. **UI**: Player opens the Transfer Dialog (T key) and adjusts transfer amounts per resource
2. **Command**: Each non-zero transfer creates an `IssueTransferCommand` with `cargo_type`, `direction` (load/unload), and `amount`
3. **Handler**: `TransferCommandHandler` validates the transfer and auto-adds a MOVE order if the fleet isn't at the target location
4. **Order**: A `TRANSFER` order is added to the fleet's order queue
5. **Execution**: `OrderProcessor` executes the transfer in Phase 1.5 via `_execute_load()` or `_execute_unload()`
   - **Load** (planet → fleet): Deducts from `planet.stockpile`, adds to fleet ship cargo
   - **Unload** (fleet → planet): Deducts from fleet ship cargo, adds to `planet.stockpile`
   - **Fleet-to-fleet**: Uses `source.resources.unload_cargo_from_fleet()` → `dest.resources.load_cargo_to_fleet()`

Fleet construction also draws from fleet cargo via `fleet.has_cargo_resources()` and
`fleet.consume_cargo_resource()`, aggregated across all ships in the fleet.

## Per-Turn Resource Costs

There is no blanket maintenance cost. Instead, individual components can define
per-turn resource consumption via `ResourceConsumption` abilities with
`trigger='per_turn'` in their JSON definitions. The `ConsumableManagementEngine`
processes these each tick (1/100th of per-turn cost per tick).

When a ship's per-turn resource is depleted, the consuming components are
automatically disabled. The `is_operational` field on `ShipInstance` and
`PlanetaryFacility` can also be used to manually disable entities.

## Drop Pods

Drop Pods are a vehicle type designed for planetary colonization. They bridge the
workshop, production, and colonization systems.

### Design and Construction

- **Vehicle type:** `Drop Pod` (classes: Small/Medium/Large/Heavy, max mass 1000-8000)
- **Cost multiplier:** 5x (applied by `DesignCostCalculator._apply_cost_multiplier()` from `vehicleclasses.json`)
- **Layer config:** `Planetary_Complex` (uses complex component slots)
- Designed in the workshop like any other vehicle, using complex-type components
  (harvesters, storage, planetary yard, energy generators, etc.)

### Production and Staging

- Built at colonies via the base construction queue (same as complexes)
- On completion, `ProductionSpawner._spawn_to_staging_yard()` places the finished
  pod into the planet's staging yard (not into a fleet)
- The staging yard is a mass-limited buffer on the planet, sized by
  `StagingYardAbility` on colony facilities

### Loading and Transport

- Colony ships load drop pods from the staging yard as **carried items**
- Stored in `ship.carried_items` as structured cargo preserving the full design data:
  ```python
  {"design_id": "...", "name": "...", "vehicle_type": "drop_pod", "design_data": {...}, "mass": ...}
  ```
- Each carried item retains all component choices the player made in the workshop

### Deployment during Colonization

- `ColonizeValidator` checks `ship.carried_items` for entries with `vehicle_type='drop_pod'`
- Drop pods are **universal** -- any drop pod works on any planet type
- `OrderProcessor._deploy_drop_pod()` removes the pod from `carried_items` and
  creates a `PlanetaryFacility` using its full `design_data`
- The colony ship stays in the fleet (it is not consumed)

## Migration Status

The resource system has been unified under `ResourceCatalog`. The legacy
`PLANET_RESOURCES` constant, `ResourceType` class, and `load_resources_data()`
function have been removed. All code now uses `ResourceCatalog.from_json()`
and queries like `catalog.by_display_group("planetary")` to get resource lists.

## Modding Guide

To add a new resource type:

1. Add an entry to `data/resources.json` with a unique `id`
2. If the resource should appear on planets: add affinity entries to
   `data/astrophysics.json` under `planet_type_affinities`
3. If the resource is a construction material: add `resource_cost` entries to
   component definitions in `data/components.json` (these are summed into the
   design's `construction_cost` by `DesignCostCalculator`)
4. If ships should store/consume/generate it: add `ResourceStorage`,
   `ResourceConsumption`, or `ResourceGeneration` abilities to components
5. No Python code changes are required
