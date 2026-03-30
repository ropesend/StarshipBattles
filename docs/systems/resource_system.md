# Resource System

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
- A resource referenced in design `resource_cost` fields is required for construction

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
       +-- Harvesting: ResourceHarvesterAbility extracts from deposits
       |   into empire resource pool
       |
       +-- Construction: ProductionEngine consumes from empire pool
       |   based on design resource_cost
       |
       +-- Ship Initialization: ResourceStorage abilities determine
       |   what consumables a ship carries
       |
       +-- Combat: ResourceConsumption/ResourceGeneration abilities
       |   consume and regenerate consumables per tick
       |
       +-- Strategic Movement: FleetResourceAggregator tracks per-hex
           and warp resource costs across fleet ships
```

## Migration Status

The resource system is being unified from two previously separate concepts:
- `PLANET_RESOURCES` constant (deprecated, will be removed)
- `ResourceType` class (deprecated, will be removed)

New code should use `ResourceCatalog` instead of these constants. The legacy
`load_resources_data()` function is maintained for backward compatibility during
migration.

## Modding Guide

To add a new resource type:

1. Add an entry to `data/resources.json` with a unique `id`
2. If the resource should appear on planets: add affinity entries to
   `data/astrophysics.json` under `planet_type_affinities`
3. If the resource is a construction material: add it to component
   `resource_cost` fields in `data/components.json`
4. If ships should store/consume/generate it: add `ResourceStorage`,
   `ResourceConsumption`, or `ResourceGeneration` abilities to components
5. No Python code changes are required
