# Resource System Compact Reference

> **Last verified:** 2026-05-18 — PROJ-436 Phase 10 doc refresh: `TransferValidator.VALID_CARGO_TYPES` deletion (Phase 7), `ProductionEngine.context_type` deletion via `IProductionResourceSource` Protocol (Phase 8), `_CarriedItemsProxy` + `ShipInstance.carried_items` deletion (Phase 9). Drop-pod shape now describes the typed `DropPod` dataclass. Transferable-resource recipe simplified — no validator update needed when adding a resource to `data/resources.json`.

Source baseline: `docs/systems/resource_system.md`

The resource system is a unified, data-driven catalog for planetary materials and
operational consumables. Resource type definitions live in `data/resources.json`.
Behavior comes from references in planet generation data, component abilities,
construction costs, local storage, transfer orders, and combat or strategy
engines. The catalog defines what resource IDs exist; it does not define gameplay
categories by itself.

## Core Model

- `ResourceDefinition` (`game/core/resources.py`): frozen dataclass with `id`,
  `name`, `description`, `display_group`, and `has_quality`.
- `ResourceCatalog` (`game/core/resources.py`): registry of resource definitions.
  It loads from `Paths.RESOURCES_FILE` by default and supports custom paths for
  tests/mods.
- `GameRegistries.resource_catalog` (`game/core/registry.py`): canonical runtime
  access for systems that already receive registries.
- `DefaultRegistryProvider.get_resource_catalog()`: provider access path for
  code using registry DI. `TestRegistryProvider.get_resource_catalog()` returns
  `None`; tests that calculate ship stats should pass a `GameRegistries` with a
  real catalog or pass `planetary_resource_ids` directly.

Layer rule: `ResourceDefinition` and `ResourceCatalog` live in `game/core/` so
Strategy and Simulation can share resource definitions without reversing
dependencies.

## Resource Data

File: `data/resources.json`

```json
{
  "resources": [
    {
      "id": "metals",
      "name": "Metals",
      "description": "Refined metallic ores for structural construction.",
      "display_group": "planetary",
      "has_quality": true
    }
  ]
}
```

| Field | Required | Contract |
|---|---:|---|
| `id` | yes | Unique lowercase identifier used by data, abilities, cargo, and costs |
| `name` | yes | Display name; defaults to `id` if omitted in `from_data()` |
| `description` | no | Human-readable explanation; defaults to empty string |
| `display_group` | no | UI/grouping hint, e.g. `planetary`, `operational`; defaults to empty string |
| `has_quality` | no | Whether planet deposits track quality; defaults to false |

Current production definitions:

| ID | Name | Group | Quality | Main use |
|---|---|---|---:|---|
| `metals` | Metals | `planetary` | yes | Structural construction |
| `organics` | Organics | `planetary` | yes | Biological materials |
| `vapors` | Vapors | `planetary` | yes | Volatile gases |
| `radioactives` | Radioactives | `planetary` | yes | Fissile materials |
| `exotics` | Exotics | `planetary` | yes | Rare exotic matter |
| `fuel` | Fuel | `operational` | no | Movement and engines |
| `energy` | Energy | `operational` | no | Weapons, shields, systems |
| `ammo` | Ammunition | `operational` | no | Kinetic and ballistic weapons |

## Catalog API

```python
catalog = ResourceCatalog.from_json()
catalog = ResourceCatalog.from_json(custom_path)
catalog = ResourceCatalog.from_data(list_data)

definition = catalog.get("metals")        # ResourceDefinition | None
exists = catalog.has("fuel")              # bool
ids = catalog.all_ids()                   # list[str]
defs = catalog.all_definitions()          # list[ResourceDefinition]
planetary = catalog.by_display_group("planetary")
operational = catalog.by_display_group("operational")
```

Loading contracts:

- Missing files, malformed JSON, invalid shapes, and loader exceptions log a
  warning and return an empty catalog.
- Entries with missing/null/empty `id` are skipped.
- Duplicate IDs use last-write-wins semantics and currently do not warn.
- `GameRegistries.__post_init__()` replaces `resource_catalog=None` with an
  empty catalog so lightweight tests do not crash by default.
- `ShipStatsCalculator.calculate()` requires either `resource_catalog` or
  explicit `planetary_resource_ids`; omitting both raises `TypeError`.

Production bootstrap (`game/app_bootstrap.py`) loads one `ResourceCatalog`, hydrates
`ctx.registry_manager.resources` from it, and reuses the same catalog when building
`GameRegistries`.

## Behavior Sources

Adding a resource to the catalog makes the ID valid and discoverable. Actual
behavior appears only when another data file or component ability references it.

| Reference | Effect |
|---|---|
| `data/astrophysics.json` -> `resource_generation.planet_type_affinities` | Adjusts deposit quantities during planet generation |
| `game/strategy/data/planet_gen.py` | Generates deposits for `ResourceCatalog.by_display_group("planetary")` resources |
| Component `ResourceHarvester` ability | Harvests a deposit into `planet.stockpile` |
| Component `LocalStorage` ability | Increases `planet.max_stockpile` for one resource |
| Component `StagingYard` ability | Increases planet-side mass capacity for drop pods/fighters |
| Component `ResourceStorage` ability | Gives ships consumable capacity for a resource |
| Component `ResourceGeneration` ability | Regenerates a ship consumable |
| Component `ResourceConsumption` ability | Consumes a ship resource in combat, movement, warp, activation, or per-turn operation |
| Component `resource_cost` fields | Source cost data consumed by `DesignCostCalculator` |
| Design/queue `total_resource_cost` / `construction_cost` | Build-time resource requirements consumed by `ProductionEngine` |
| Transfer orders and cargo systems | Move stockpile/cargo between planets and fleets |

Important ability-key distinction: JSON uses `ResourceHarvester`, `LocalStorage`,
`StagingYard`, and `PlanetaryYard` keys; the corresponding Python classes are
`ResourceHarvesterAbility`, `LocalStorageAbility`, `StagingYardAbility`, and
`PlanetaryYardAbility` in `game/simulation/components/abilities/harvester.py`.
Ship consumable abilities use JSON keys matching class names:
`ResourceStorage`, `ResourceGeneration`, and `ResourceConsumption`.

## Runtime Paths

```text
data/resources.json
  -> ResourceCatalog
  -> RegistryManager.resources and GameRegistries.resource_catalog
  -> planet deposits from ResourceCatalog.by_display_group("planetary")
  -> HarvestingEngine: deposits -> planet.stockpile
  -> ProductionEngine: planet.stockpile or fleet cargo -> construction progress
  -> ShipStatsCalculator: ResourceStorage/Generation/Consumption -> ship resources
  -> FleetConsumableAggregator: per-hex and warp costs across ships
  -> TransferHandler: planet stockpile <-> fleet cargo, fleet <-> fleet cargo
```

Current engine files:

| Concern | File |
|---|---|
| Resource definitions | `game/core/resources.py`, `data/resources.json` |
| Registry DI | `game/core/registry.py`, `game/app_bootstrap.py` |
| Planet deposits | `game/strategy/data/planet_gen.py`, `game/strategy/data/resource_generation_config.py`, `data/astrophysics.json` |
| Harvest/storage/staging | `game/strategy/engine/harvesting_engine.py` |
| Production consumption/spawning | `game/strategy/engine/production_engine.py`, `game/strategy/engine/production_spawner.py` |
| Ship resource stats | `game/simulation/entities/ship_stats.py`, `game/simulation/entities/ship_design_stats.py` |
| Ship/fleet consumables | `game/strategy/data/ship_consumable_manager.py`, `game/strategy/data/fleet_consumable_aggregator.py` |
| Transfers | `game/strategy/engine/handlers/transfer.py`, `game/strategy/engine/order_handlers/transfer.py`, `game/strategy/engine/order_handlers/transfer_branches.py`, `game/strategy/validation/transfer_validator.py` |
| Colonization/drop pods | `game/strategy/validation/colonize_validator.py`, `game/strategy/engine/order_handlers/colonize.py` |

## Planet Storage Contract

Resources are local to planets and fleets, not a mutable global empire pool.

- `planet.deposits`: raw underground deposits, `resource_id -> {quantity, quality}`.
- `planet.stockpile`: harvested usable resources, `dict[str, float]`.
- `planet.max_stockpile`: local storage capacity by resource, set from operational
  facility `LocalStorage` abilities.
- `planet.add_to_stockpile(resource, amount)`: adds locally and returns overflow.
- `planet.consume_from_stockpile(resource, amount)`: all-or-nothing local consume.
- `planet.has_stockpile(costs)`: affordability check for local construction.
- `empire.resource_pool`: read-only **pure aggregation query** over every
  colony's stockpile (PROJ-436 Phase 5). Returns `{resource_id: sum_over_colonies}`.
  Do not mutate the returned dict — it is a snapshot. To change empire-visible
  resources, mutate the owning planet's stockpile (`planet.add_to_stockpile` /
  `planet.consume_from_stockpile`).
- `empire.has_resources(costs)` / `empire.get_resource(resource_id)`: read-only
  helpers over `resource_pool`. Used by UI affordability widgets; production code
  consults the build-location's container (planet stockpile / fleet cargo)
  directly.

Stale-reference correction: older comments in some engine files still mention
harvesting or production through an empire pool. Current code harvests into
`planet.stockpile`; planet construction consumes `planet.stockpile`; fleet
construction consumes fleet cargo. PROJ-436 Phase 5 deleted the legacy
`Empire._fleet_resource_pool` durable storage along with the
`Empire.add_resources` / `Empire.consume_resources` mutators that wrote against
it — the empire-level resource view is now purely derivative.

## Production Contract

`DesignCostCalculator.calculate_total_cost(design_data, registries)` is the
central cost path.

- Component source data uses `resource_cost`, not `construction_cost`.
- For ship designs, the calculator loads the design through the simulation
  ship path so component registry costs, formulas, modifiers, and vehicle-class
  `cost_multiplier` are applied.
- Registry-resolved ship construction costs are initialized from
  `resource_catalog.by_display_group("planetary")`; a new construction material
  must be in that group unless the calculation contract is changed.
- Inline component `resource_cost` remains a supported fallback for test data
  and simple facility structures.
- Production queue items must carry `total_cost` plus tracking fields such as
  `resources_consumed`; items missing `total_cost` are skipped with a warning.
- `ProductionEngine._check_affordability()` reads through the unified
  `IProductionResourceSource` Protocol (PROJ-436 Phase 8) — both `Planet`
  and `Fleet` satisfy the protocol via `production_has_resources` /
  `production_get_resource` / `production_consume_resource` delegators
  (`planet.py` over the stockpile API; `fleet.py` over the cargo API).
  The legacy `context_type`-string dispatch is gone.

## Transfers

Command-to-order flow:

1. UI transfer actions create `IssueTransferCommand` with `cargo_type`,
   `direction`, `amount`, and either `planet_id` or `target_fleet_id`.
2. `TransferCommandHandler` validates and creates a `TRANSFER` order. For planet
   targets it may queue a MOVE order first.
3. `TransferHandler` executes the order in the action phase through seven
   explicit dispatch branches in `transfer_branches.py`.

Execution contracts:

- Planet -> fleet resource load: `planet.consume_from_stockpile()` then
  `fleet.resources.load_cargo_to_fleet()`.
- Fleet -> planet resource unload: `fleet.resources.unload_cargo_from_fleet()`
  then `planet.add_to_stockpile()`.
- Fleet -> fleet transfer: source fleet unloads cargo, destination fleet loads it.
- Passenger and drop-pod transfers use the same order family but separate branch
  methods.

PROJ-436 Phase 7 deleted `TransferValidator.VALID_CARGO_TYPES`. The new
contract: `_is_known_cargo_type(cargo_type)` returns True iff
`cargo_type` is one of three categorical sentinels (`passengers`,
`drop_pod`, `vehicle`) — which route to distinct dispatch branches in
`transfer_branches.py` and intentionally live outside
`data/resources.json` — OR `ResourceCatalog.has(cargo_type)` returns
True. Adding a new resource to `data/resources.json` makes it
transferable automatically; no validator update required.

## Operational Consumption

There is no universal maintenance cost. Components opt in with
`ResourceConsumption` ability data:

```json
{
  "ResourceConsumption": [
    {"resource": "fuel", "amount": 100, "trigger": "strategic_per_hex"}
  ]
}
```

Current trigger meanings:

| Trigger | Consumer |
|---|---|
| `constant` | Combat tick consumption; amount is per second and multiplied by `PhysicsConfig.TICK_RATE` |
| `activation` | One-shot per-use consumption, e.g. weapon ammo |
| `strategic_per_hex` | Strategic movement cost aggregated by `FleetConsumableAggregator` |
| `warp_jump` | Warp resource cost exposed through `ship.get_warp_resource_costs()` and consumed atomically by fleet warp |
| `per_turn` | Strategy turn upkeep handled by `ConsumableManagementEngine` |

Per-turn consumption is divided across 100 ticks. Depletion disables components
whose registry-defined `ResourceConsumption` entry matches the depleted resource
and `trigger == "per_turn"`. Manual disable remains available through
`ShipInstance.is_operational`, `PlanetaryFacility.is_operational`, and component
toggle state.

Resource aggregation is data-driven in `ShipStatsCalculator`: dynamic resource
keys live inside `StatAccumulator.resource_storage`,
`StatAccumulator.resource_generation`, and `warp_resource_costs`, not synthetic
`max_<resource>` / `gen_<resource>` keys.

## Drop Pods

Drop Pods are player-designed colonization vehicles that carry complete complex
design data.

- Vehicle type: `Drop Pod`; classes in `data/vehicleclasses.json` are
  `Drop Pod (Small)`, `Drop Pod (Medium)`, `Drop Pod (Large)`, and
  `Drop Pod (Heavy)`.
- Cost multiplier: `cost_multiplier` from the vehicle class, applied by
  `DesignCostCalculator._apply_cost_multiplier()`.
- Layer config: `Planetary_Complex`; built from complex components such as
  harvesters, storage, planetary yards, and energy generators.
- Completed pods are placed into `planet.staging_yard` by
  `ProductionSpawner._spawn_to_staging_yard()`.
- Staging capacity is mass-limited by `StagingYard` abilities and
  `planet.max_staging_mass`.
- Transfer uses `cargo_type == "drop_pod"`: load from staging yard into
  `ship.bay_inventory.pods` (typed `DropPod` entries); unload from
  `ship.bay_inventory.pods` back to staging yard.
- Colonization requires a `DropPod` in `ship.bay_inventory.pods`.
  `ColonizeHandler._deploy_drop_pod()` removes the typed pod, creates a
  `PlanetaryFacility` from its `design_data`, and seeds any
  `design_data.initial_stockpile` into the new colony. The colony ship remains
  in the fleet.

Typed `DropPod` shape (`game/strategy/data/bay_inventory.py`):

```python
@dataclass
class DropPod:
    design_id: str
    design_data: Dict[str, Any]
    mass: float = 0.0
    payload: Dict[str, Any] = field(default_factory=dict)
    # payload preserves the legacy `name` / `vehicle_type` keys
    # for callers that round-trip through it
```

PROJ-436 Phase 9 deleted the legacy `_CarriedItemsProxy` shim and
the `ShipInstance.carried_items` property/setter; the typed
`BayInventory` (`bay`, `pods`, `resources`, `population` slots) is
the canonical write surface.

## Extension Recipes

Add a mineable planetary resource:

1. Add an entry to `data/resources.json` with a unique `id` and
   `display_group: "planetary"`.
2. Add `planet_type_affinities` entries in `data/astrophysics.json`.
3. Add facility components with `ResourceHarvester` and `LocalStorage` ability
   entries using `resource_type: "<id>"`.
4. Validate with catalog and resource pipeline tests.

Add an operational ship consumable:

1. Add an entry to `data/resources.json` with a unique `id`.
2. Add `ResourceStorage` ability entries using `resource: "<id>"`.
3. Add `ResourceConsumption` and/or `ResourceGeneration` entries using the same
   resource ID and appropriate trigger.
4. For strategic movement or warp, verify `resource_consumption_per_hex` or
   `warp_resource_costs` appears in calculated stats.

Add a construction material:

1. Add the resource to `data/resources.json`; use `display_group: "planetary"`
   for registry-resolved ship/component construction costs.
2. Add component `resource_cost` entries in `data/components.json`.
3. Ensure the design path uses `DesignCostCalculator.calculate_total_cost()` so
   registry costs and vehicle-class multipliers are applied.
4. For planet construction, ensure the colony has storage and stockpile for the
   resource; for fleet construction, ensure fleet cargo contains it.

Add a transferable resource:

1. Complete the catalog/storage/cargo setup above.
2. **No validator change required.** `TransferValidator._is_known_cargo_type`
   delegates to `ResourceCatalog.has()` for any non-sentinel cargo
   type — adding the resource to `data/resources.json` (step 1) is
   enough.
3. Add transfer coverage for planet->fleet, fleet->planet, and any fleet->fleet
   behavior the new resource needs.

## Agent Invariants

- Treat `data/resources.json` plus `ResourceCatalog` as the source of truth for
  resource definitions.
- Do not reintroduce `PLANET_RESOURCES`, `ResourceType`, `load_resources_data()`,
  or a parallel resource loader.
- Do not infer gameplay behavior from `display_group` unless the subsystem
  explicitly documents that contract. It is primarily a grouping hint.
- Prefer catalog and ability lookups over resource-name branches.
- Resolve component abilities through the registry when design data stores only
  component IDs. Loaded designs usually do not carry inline ability dicts.
- Keep resources local to their owner: planet stockpile, ship consumable levels,
  fleet cargo, or staging yard. Do not mutate `empire.resource_pool` as a write
  path for colony resources.
- Construction and transfer code must consume from local stockpiles or fleet
  cargo, not from catalog definitions.
- Keep new resource IDs consistent across `data/resources.json`,
  `data/astrophysics.json`, component ability data, component `resource_cost`,
  transfer validation, and tests.

## Verification Commands

Targeted resource/catalog checks:

```bash
pytest tests/unit/core/test_resource_catalog.py
pytest tests/unit/core/resources_registry/test_loading.py
pytest tests/integration/resource_system/test_custom_resource_lifecycle.py
pytest tests/integration/resource_system/test_resource_pipeline.py
pytest tests/integration/resource_system/test_fleet_operations.py
```

Related strategy paths:

```bash
pytest tests/unit/strategy/data/test_fleet_consumable_aggregator.py
pytest tests/unit/strategy/engine/test_order_processor_transfer.py
pytest tests/unit/strategy/engine/test_pod_transfer.py
pytest tests/unit/strategy/engine/test_production_spawner.py
pytest tests/unit/strategy/engine/test_production_spawner_staging_yard.py
```

Full-suite command:

```bash
python Tools/test_sharded/test_sharded.py
```
