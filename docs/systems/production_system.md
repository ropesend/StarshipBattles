# Production System - Compact Agent Reference

> **Last verified:** 2026-05-22 — PROJ-436 Phase 10 doc refresh: `ProductionEngine.context_type` storage-dispatch deleted (Phase 8) — replaced with the `IProductionResourceSource` Protocol (`production_has_resources` / `production_get_resource` / `production_consume_resource`) satisfied by both `Planet` and `Fleet` via polymorphic delegators. `BuildQueueSource.context_type` is **UI entity routing only** (Phase 6a kept it for that purpose); the engine no longer reads it. Staging-yard pods are typed `DropPod` entries in `ship.bay_inventory.pods` (Phase 9).

This is the strategy-layer construction pipeline. Players queue designs in the
Build Queue UI; `ProductionEngine` consumes local resources over 100 ticks per
turn; `ProductionSpawner` materializes completed items. One queue algorithm
handles planet base yards, planet shipyard facilities, and fleet space yards.

Core invariant: `Planet`, `Fleet`, and `PlanetaryFacility` own queue data only.
They do not process production. Queue ticking, affordability, progress updates,
completion, and spawn dispatch belong to `ProductionEngine` and
`ProductionSpawner`.

## Build Contexts

| Context | Queue | Builds | Rate source | Requirement |
|---|---|---|---|---|
| Planet base queue | `Planet.construction_queue` | Complexes and drop pods only by policy/UI; engine stops on non-complex queue head | `planetary_yard` default rates, size scaled in queue discovery | Operational facility with `PlanetaryYard` ability |
| Planet shipyard facility | `PlanetaryFacility.construction_queue` | Ships, fighters, satellites, complexes | Facility `SpaceShipyard` rates or defaults, size/bonus scaled | `facility.is_shipyard` |
| Fleet space yard | `Fleet.construction_queue` | Ships, fighters, satellites, complexes | `space_shipyard` default rate times yard count in engine | Fleet has BUILD order and `fleet.capabilities.has_space_shipyard` |

Default rates are loaded from `data/production_rates.json` via
`game/strategy/data/build_queue_source.py`:

| Yard | Per-turn rate for metals, organics, radioactives, vapors, exotics |
|---|---|
| `planetary_yard` | 2000 each |
| `space_shipyard` | 30000 each |

Rates are per turn. `ProductionEngine` divides by `TICKS_PER_TURN == 100`
when calculating per-tick spend.

## Main Flow

1. A design is created or loaded by the Workshop/design library.
2. UI or facade dispatches `AddToConstructionQueueCommand`.
3. `AddToConstructionQueueCommandHandler` resolves the actual queue, validates
   the design, calculates total cost, and initializes `turns_remaining`.
4. `TurnEngine.process_turn()` runs 100 sub-ticks; phase `0e` calls
   `ProductionEngine.process_construction_tick(...)`.
5. The engine consumes resources from the build location, updates
   `resources_consumed`, and completes items when every cost is paid.
6. `ProductionSpawner` creates facilities, fleets, ships, or staging-yard items.

## Key Data Shapes

`PlanetaryFacility` lives in `game/strategy/data/planetary_facility.py`:

```python
PlanetaryFacility(
    instance_id: str,
    design_id: str,
    name: str,
    design_data: dict,
    is_operational: bool = True,
    construction_queue: list[dict],
    construction_queue_paused: bool = False,
    consumable_levels: dict[str, float],
    component_states: dict[str, dict],
)
```

Important contracts:

- `to_dict()` / `from_dict()` persist queue, pause flag, consumables, and
  component activation state.
- `is_shipyard` returns true only for operational facilities whose design data
  contains component id `space_shipyard` or inline `SpaceShipyard`.
- Consumable storage uses the generic API: `get_consumable_storage(resource_id)`,
  `get_max_consumable_storage(resource_id, registries)`,
  `add_consumable(resource_id, amount, registries)`,
  `withdraw_consumable(resource_id, amount)`. Fuel is one such consumable
  (`resource_id="fuel"`); legacy fuel-specific wrappers were removed in PROJ-487.
- Facility component activation state uses `ComponentActivationState`; the
  legacy `set_component_active()` / `is_component_active()` wrappers still
  translate to that model.

Queue item format created by `AddToConstructionQueueCommandHandler`:

```python
{
    "design_id": "design_key",
    "type": "ship" | "fighter" | "satellite" | "complex" | "drop_pod",
    "turns_remaining": 0.75,
    "total_cost": {"metals": 50.0},
    "resources_consumed": {"metals": 0.0},
    "target_planet_id": 12,  # optional, fleet-built complexes
}
```

`total_cost` is mandatory for production ticks. If a queue item lacks it,
`ProductionEngine._validate_queue_item()` logs a warning and skips the item.
`resources_consumed` persists partial progress and is not reset by pausing.

## Queue Discovery and Rates

File: `game/strategy/data/build_queue_source.py`.

`BuildQueueSource` is the consumer-facing descriptor used by UI, command
helpers, and forecasts:

```python
BuildQueueSource(
    queue_id: str,
    display_name: str,
    owner_entity: Any,          # Planet or Fleet
    construction_queue: list,   # reference to the real queue list
    can_build_ships: bool,
    can_build_complexes: bool,
    context_type: "planet" | "fleet",   # UI entity routing only —
                                        # NOT engine storage dispatch
                                        # (PROJ-436 Phase 6a kept this
                                        # for UI; Phase 8 deleted the
                                        # engine-side context_type read)
    build_rate: dict[str, float],
    planet_id: int | None = None,
    is_paused: bool = False,
)
```

Authoritative helpers:

- `collect_build_queues_at_hex(hex_coord, galaxy, empire, registries=None)`
- `collect_all_build_queues_for_empire(empire, registries=None)`
- `get_production_rate_for_queue(entity, queue_id)`
- `estimate_build_turns(total_cost, production_rate)`
- `get_default_production_rates(yard_type)`
- `forecast_queue_turn_spend(queue, build_rate)` in
  `game/strategy/engine/construction_forecast.py`
- `colony_has_planetary_yard(colony, registries=None)`

Do not duplicate turn-estimate or forecast logic in UI, commands, or economy
projections.

Current rate-modifier boundaries:

- `resolve_size_multiplier(comp)` applies `simple_size_mount` scaling for
  `PlanetaryYard` and `SpaceShipyard` components.
- `SpaceShipyard` ability data may define `production_rates` and
  `construction_speed_bonus`; `_get_facility_production_rates()` applies both.
- `BuildRateBooster` is applied by `_collect_planet_sources()` when both
  `galaxy` and `empire` context are provided. `collect_all_build_queues_for_empire()`
  currently does not pass those context args, and `ProductionEngine` resolves
  rates directly rather than through `BuildQueueSource`.
- Habitability scaling is applied inside `ProductionEngine` only when that
  engine was constructed with a `race_registry`.

Those boundaries matter: do not document booster or habitability effects as
unconditional engine behavior unless the caller path actually injects the
needed context.

## Production Tick Flow

Files:

- `game/strategy/engine/production_engine.py`
- `game/strategy/engine/production_math.py`
- `game/strategy/engine/production_spawner.py`
- `game/strategy/engine/construction_forecast.py`

Entry point:

```python
ProductionEngine.process_construction_tick(
    tick: int,
    empires: list[Empire],
    galaxy: Galaxy | None,
    save_path: str | None = None,
) -> None
```

`ProductionEngine.__init__(*, registries, event_bus=None, race_registry=None)`
requires `registries`; `registries=None` raises `ValidationException`.
Before mutating state, `_validate_tick_inputs()` requires every empire to have
a non-`None` `resource_pool`.

Per empire, the engine processes:

1. Planet base queues that are non-empty, unpaused, and backed by an operational
   `PlanetaryYard`.
2. Each unpaused operational shipyard facility queue independently.
3. Fleet queues only when `fleet.is_building` is true and
   `fleet.capabilities.has_space_shipyard` is true.

Constants:

- `TICKS_PER_TURN = 100` from `game/strategy/engine/turn_engine.py`
- `TICK_CAPACITY_EPSILON = 0.0001`
- `COMPLETION_EPSILON = 0.001`
- `MAX_QUEUE_ITERATIONS = 10` per queue tick safety cap

Important queue behavior:

- Planet base queue runs with `is_complex_only=True`; a non-complex head item
  returns `STOP`, leaving the queue in place.
- Invalid non-dict items return `SKIP` and are removed.
- Fleet-built complexes require `galaxy` and at least one planet at the
  fleet's current global hex; otherwise the queue stops for that tick.
- Multiple completions can happen in one tick because unused tick capacity
  carries to the next queue head.
- Shortages log at most one `RESOURCE_SHORTAGE` production event per item per
  turn via `_shortage_logged`; flags are cleared on tick 1.

## Tick Expenditure Formula

Single-source helper:

```python
find_limiting_resource_ticks(
    remaining_cost,
    rate_per_turn,
    ticks_per_turn=100,
)
```

For each required resource:

```text
rate_per_tick = rate_per_turn[resource] / ticks_per_turn
ticks_needed = remaining_cost[resource] / rate_per_tick
max_ticks_needed = max(ticks_needed for all required resources)
```

If any required resource has no positive rate, the helper returns `None` and
the queue stops.

Within one production tick:

```text
ticks_to_spend = min(tick_capacity, max_ticks_needed)
cost_this_step[resource] =
    min(rate_per_turn[resource] / 100 * ticks_to_spend, remaining_cost[resource])
```

The engine checks affordability, consumes resources, subtracts tick capacity,
updates `turns_remaining`, and completes the item when every consumed amount is
within `COMPLETION_EPSILON` of its total.

Forecasting uses the same helper with `ticks_per_turn=1`, treating one turn as
capacity `1.0`.

## Resource Sources

Production consumes resources at the build location through the
unified `IProductionResourceSource` Protocol declared in
`game/strategy/engine/production_engine.py` (PROJ-436 Phase 8):

- `production_has_resources(costs)` — affordability check.
- `production_get_resource(resource_type)` — read available amount.
- `production_consume_resource(resource_type, amount)` — all-or-nothing
  consume.

Both `Planet` and `Fleet` satisfy this Protocol via thin polymorphic
delegators:

- Planet delegators forward to the existing stockpile API
  (`has_stockpile` / `get_stockpile` / `consume_from_stockpile`).
- Fleet delegators forward to the existing cargo API
  (`has_cargo_resources` / `get_cargo_resource` /
  `consume_cargo_resource`).

The engine no longer branches on `context_type` for storage routing,
and the Phase 5 `ValueError`-on-unknown-owner contract is gone — an
owner that does not satisfy `IProductionResourceSource` raises the
natural `AttributeError` Python emits when a method is missing. The
empire pool is not a fallback; do not reintroduce the old "empire
pool pays for everything" assumption.

## Pause Contract

Each yard owner carries its own `construction_queue_paused: bool`:

| Queue | Owner field |
|---|---|
| Planetary base queue | `Planet.construction_queue_paused` |
| Facility shipyard queue | `PlanetaryFacility.construction_queue_paused` |
| Fleet space-yard queue | `Fleet.construction_queue_paused` |

When paused, the engine skips the queue entirely: no resource draw, no
`resources_consumed` change, no shortage logging. Queue CRUD still works, and
existing progress resumes after unpause.

Toggle command:

```python
SetBuildQueuePausedCommand(
    entity_id: int,
    entity_type: BuildEntityType,  # "planet" or "fleet"
    paused: bool,
    queue_id: str | None = None,
)
```

Handler: `SetBuildQueuePausedCommandHandler` in
`game/strategy/engine/handlers/construction_queue.py`. It resolves the queue
owner with `BaseCommandHandler._resolve_queue_owner()`. Fleet pause mutation
routes through `session.fleet_mutator.set_construction_queue_paused(...)`;
planet and facility owners set the flag directly.

`BuildQueueSource.is_paused` is a snapshot populated during queue collection.
Treasury, planet-detail forecasts, and Empire Build Queue status should read
that field rather than reaching back through `owner_entity`.

## Spawning

`ProductionEngine._complete_item()` removes the queue head and delegates:

```python
ProductionSpawner.spawn_completed_item(
    item,
    empire,
    colony_or_fleet,
    galaxy,
    save_path,
    tick,
)
```

Dispatch:

| Item/context | Spawner path | Result |
|---|---|---|
| Planet complex | `_create_and_place_facility()` | Adds `PlanetaryFacility` to planet |
| Planet `drop_pod` or `fighter` | `_spawn_to_staging_yard()` | Adds discrete staging-yard item to planet |
| Planet ship/satellite/other | `_spawn_ship()` | Creates a new `Fleet` at planet location |
| Fleet complex | `_spawn_fleet_complex()` then `_create_and_place_facility()` | Adds facility to a planet at fleet hex, honoring optional `target_planet_id` |
| Fleet ship/fighter/satellite/other | `_spawn_fleet_ship()` | Adds `ShipInstance` to existing fleet |

Design loading uses the per-empire `DesignCatalog` resolved from
`session.services.design_catalogs_by_empire[empire.id]` (PROJ-427 /
PROJ-434). Ship creation uses
`ShipInstance.create(..., registries=self._registries)`, and successful
ship creation calls `catalog.record_built(design_id)` — the pending
counts are flushed through `DesignRepository.increment_built_count` at
save time.

Facility placement routes through `PlanetWriteService` via
`ProductionSpawner._get_planet_mutator().add_facility(planet, facility)`.
Do not append directly to `planet.facilities` in new spawn code.

Mass for staging-yard items is calculated through
`calculate_design_stats(design_data, registries)` in
`game/simulation/entities/ship_design_stats.py`, preserving the simulation
`Ship` path as the single source of truth for stats.

Events:

- Complex completion logs `EventType.COMPLEX_BUILT`.
- Ship completion logs `EventType.SHIP_BUILT`.
- Event location fields use galaxy/system lookup when available.

## Habitability

Formula intent:

```text
effective_rate = base_rate * habitability_mult
habitability_mult = sum(pop.count * score_for_pop_race) / sum(pop.count)
```

Current production-code contract:

- `ProductionEngine._get_habitability_mult(owner)` returns `1.0` unless
  `race_registry` is injected and the owner exposes
  `get_cached_habitability_multiplier`.
- Fleets always receive multiplier `1.0`.
- `Planet.get_cached_habitability_multiplier(race_registry, turn)` delegates
  to `get_default_planet_habitability_service()` or a default
  `PlanetHabitabilityService`.
- The cache fields on `Planet` are transient and are not serialized.
- `TurnEngine` calls `set_current_turn(session.turn_number)` on production and
  harvesting engines when the method exists.

Formula edge cases live in `game/strategy/formulas/colony_output.py`:
uncolonized planets, zero-population colonies, and missing race configs return
or effectively preserve `1.0`; zero-count species and missing race IDs are
excluded from numerator and denominator.

Warning: current `TurnEngineConfig.create_default()` threads `race_registry` to
population/happiness engines but constructs `ProductionEngine` with registries
and event bus only. Tests and custom wiring can inject production
`race_registry`; do not assume all production ticks are habitability-scaled.

## Commands and Validation

Command dataclasses live in `game/strategy/engine/commands/__init__.py`:

- `AddToConstructionQueueCommand`
- `RemoveFromConstructionQueueCommand`
- `ReorderConstructionQueueCommand`
- `SetBuildQueuePausedCommand`

Handlers live in `game/strategy/engine/handlers/construction_queue.py`.
The old broad reference to `game/strategy/engine/command_handlers.py` is stale
for construction queue work; that shim was deleted in PROJ-383.

Add flow:

1. Resolve planet/fleet with `_resolve_build_entity(session, entity_id, entity_type)`.
2. Resolve the actual queue with `_resolve_queue(entity, queue_id)`.
3. Validate insert index.
4. Validate design through `DesignValidator(session.registries)` when design
   data is available. Errors and warnings block insertion.
5. Calculate cost with
   `DesignCostCalculator.calculate_total_cost(load_result.data, session.registries)`.
6. Resolve queue rate with `get_production_rate_for_queue(...)`.
7. Initialize `turns_remaining` with `estimate_build_turns(...)`.
8. Insert or append the queue item.

Remove/reorder use the same queue resolution path and validate indexes.

## UI Surfaces

Primary UI files:

- `game/ui/screens/build_queue_screen.py`
- `game/ui/screens/empire_build_queue_window.py`
- `game/ui/panels/build_queue_controller.py`
- `game/ui/components/table/virtual_table.py`
- `game/ui/screens/transfer_dialog.py`

The Build Queue UI works with `BuildQueueSource`, not direct planet/fleet
branching. It supports yard selection, available-design filtering, queue
quantity/reorder controls, per-item turns, per-turn spend, remaining cost, and
pause/resume.

`BuildQueueScreen._dispatch_toggle_pause_command()` flips the active source's
pause state, dispatches `SetBuildQueuePausedCommand`, and recollects sources so
`is_paused` reflects the mutated owner. The renderer refreshes the pause button
label on selection and queue refresh.

Staging-yard pods/items are discrete typed `DropPod` entries in
`ship.bay_inventory.pods` (PROJ-436 Phase 9 deleted the legacy
`carried_items` projection), not bulk cargo. Transfer to ships happens
through the Transfer dialog.

## Components and Abilities

Key ability implementations:

- Yard and harvester abilities:
  `game/simulation/components/abilities/harvester.py`
- Component data: `data/components.json`
- Shared ability scanning/stacking:
  `game/strategy/services/strategic_ability_scanner.py`
- Size mount scaling:
  `game/strategy/services/modifier_resolver.py`

Current notable production-related component IDs in `data/components.json`:

| ID | Role |
|---|---|
| `metal_harvester`, `organic_harvester`, `vapor_harvester`, `radioactive_harvester`, `exotic_harvester` | Resource harvesting components |
| `resource_vault_metals`, `resource_vault_organics`, `resource_vault_vapors`, `resource_vault_radioactives`, `resource_vault_exotics` | Local storage |
| `space_shipyard` | Shipyard facility or ship component |
| `planetary_yard_module`, `starter_colony_hub` | Planetary yard providers |
| `build_rate_booster_sector`, `build_rate_booster_system` | Build-rate booster examples |

Warning: designs often store component IDs rather than inline abilities.
`colony_has_planetary_yard()` handles registry lookup for `PlanetaryYard`.
`PlanetaryFacility.is_shipyard` currently detects only component id
`space_shipyard` or inline `SpaceShipyard`; a new registry-only shipyard
component needs that central detection contract updated.

## Extension Recipes

Adding a new build context:

1. Add a data holder with `construction_queue`,
   `construction_queue_paused`, and implementations of the three
   `IProductionResourceSource` Protocol methods
   (`production_has_resources` / `production_get_resource` /
   `production_consume_resource`) over whatever storage substrate the
   new entity uses.
2. Extend queue discovery to emit `BuildQueueSource` with a live
   queue-list reference and a `context_type` UI-routing string (the
   `BuildQueueSource.context_type` field is UI entity routing, not
   storage dispatch — see PROJ-436 Phase 6a audit).
3. Add central rate resolution in `build_queue_source.py` or a sibling helper.
4. Reuse `_process_queue_tick_dynamic`; do not fork the tick algorithm.
5. Add spawn behavior to `ProductionSpawner` only if completion materializes a
   new entity type.
6. Add command-handler queue resolution support if existing `_resolve_queue()`
   and `_resolve_queue_owner()` cannot find the new queue.

Adding a new yard ability or component:

1. Prefer data-driven component abilities and shared properties over hardcoded
   type lists.
2. Put component definitions in `data/components.json`.
3. Ensure queue discovery, rate resolution, and shipyard/yard detection all
   use the same central contract.
4. Use registry lookup for ability checks when designs store component IDs.
5. Keep formulas in `production_math.py` and rates in
   `build_queue_source.py` / `data/production_rates.json`.

Adding a new completion item type:

1. Keep the queue `type` stable; `ProductionSpawner` normalizes by lowercasing
   and replacing spaces with underscores.
2. Decide whether the result is a fleet ship, staging-yard item, facility, or
   new entity class.
3. Route only spawn dispatch through `ProductionSpawner`; the consumption
   algorithm should not care about the new type except for validation
   constraints.
4. If stats or mass are needed, use
   `calculate_design_stats(design_data, registries)`.

## Testing and Commands

Targeted tests for production work:

- `pytest tests/unit/strategy/production_engine/`
- `pytest tests/unit/strategy/engine/test_production_engine_queue.py`
- `pytest tests/unit/strategy/engine/test_production_engine_consumption.py`
- `pytest tests/unit/strategy/engine/test_set_build_queue_paused_command.py`
- `pytest tests/unit/strategy/data/test_build_queue_source.py`
- `pytest tests/unit/strategy/data/test_construction_queue_paused_persistence.py`
- `pytest tests/unit/strategy/data/test_facility_construction_queue.py`
- `pytest tests/unit/ui/panels/test_build_queue_controller.py`
- `pytest tests/integration/strategy/production/`
- `pytest tests/integration/strategy/test_projector_drain_matches_engine.py`

Full suite:

```bash
python Tools/test_sharded/test_sharded.py
```

For docs-only edits, a narrow sanity check is usually enough; production-code
changes should run the relevant targeted tests before the full sharded suite.

## Key Files

| Concern | File |
|---|---|
| Production ticking | `game/strategy/engine/production_engine.py` |
| Spawning | `game/strategy/engine/production_spawner.py` |
| Shared limiting-resource formula | `game/strategy/engine/production_math.py` |
| Forecast spend | `game/strategy/engine/construction_forecast.py` |
| Queue discovery/rates | `game/strategy/data/build_queue_source.py` |
| Planet facility data | `game/strategy/data/planetary_facility.py` |
| Planet queue/stockpile/staging | `game/strategy/data/planet.py` |
| Fleet queue/cargo | `game/strategy/data/fleet.py` |
| Queue command handlers | `game/strategy/engine/handlers/construction_queue.py` |
| Queue commands | `game/strategy/engine/commands/__init__.py` |
| Turn engine phase loop | `game/strategy/engine/turn_engine.py` |
| Turn engine config | `game/strategy/engine/turn_engine_config.py` |
| UI screen | `game/ui/screens/build_queue_screen.py` |
| Empire queue window | `game/ui/screens/empire_build_queue_window.py` |
| Build queue controller | `game/ui/panels/build_queue_controller.py` |
| Yard/harvester abilities | `game/simulation/components/abilities/harvester.py` |
| Component definitions | `data/components.json` |
| Production rates | `data/production_rates.json` |
| Design repository (engine-internal) | `game/strategy/systems/design_repository.py` |
| Design catalog (workshop / UI-facing) | `game/strategy/systems/design_catalog.py` |
| Design costs | `game/strategy/services/design_cost_calculator.py` |
| Design validation | `game/strategy/services/design_validator.py` |
| Habitability service | `game/strategy/services/planet_habitability_service.py` |
