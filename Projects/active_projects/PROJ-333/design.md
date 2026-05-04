# PROJ-333 — Design / Architecture Context

Per-engine architecture context: callers, callees (with module paths), state mutated, branching surface, error paths. Plus the surprising-behavior catalogue and testability notes used to scope test fixtures.

---

## `production_engine.py`

- **Caller:** `turn_engine.py` Phase 0e (per-tick `process_construction_tick`).
- **Calls:**
  - `production_math.find_limiting_resource_ticks`
  - `build_queue_source.{get_default_production_rates, _get_facility_production_rates, colony_has_planetary_yard}`
  - `services.design_cost_calculator.DesignCostCalculator`
  - `ProductionSpawner.spawn_completed_item`
  - `EventBus.log_event`
- **Mutates:**
  - `colony.construction_queue`, `facility.construction_queue`, `fleet.construction_queue` (pop / mutate)
  - `item['resources_consumed']`, `item['turns_remaining']`, `item['_shortage_logged']`
  - `Empire.resource_pool` via `consume_resources`
  - `Planet.stockpile` via `consume_from_stockpile`
  - `Fleet` cargo via `consume_cargo_resource`
  - Internal `_current_turn` field
- **Branching:**
  - Queue-paused flags at colony / facility / fleet levels
  - `is_shipyard` gate
  - Complex-only filter
  - Planet-presence requirement for fleet complexes
  - Per-resource affordability
  - Completion epsilon
- **Errors:** `ValidationException` if `registries` is `None` or `Empire.resource_pool` is `None`.

---

## `production_spawner.py`

- **Caller:** `production_engine._complete_item`.
- **Calls:**
  - `DesignLibrary.{load_design_data, increment_built_count}`
  - `ShipInstance.create`
  - `Galaxy.{get_planets_at_global_hex, get_system_of_planet, get_next_fleet_id}`
  - `Planet.{add_to_staging_yard, facilities.append}`
  - `Fleet.add_ship`
  - `Empire.{add_fleet, get_next_fleet_display_number}`
  - `EventBus.log_event`
  - `simulation.entities.ship_design_stats.calculate_design_stats`
- **Mutates:** `Planet.facilities`, `Planet.staging_yard`, `Fleet.ships`, `Empire.fleets`. Increments `DesignLibrary` built counter.
- **Branching:** `Fleet` vs colony context; `vehicle_type` dispatch (`complex` / `planetary_complex` / `drop_pod` / `fighter` / default ship); `target_planet_id` lookup with first-planet fallback; staging-yard-full case.
- **Errors:** None raised; failures log warnings and return early.

---

## `consumable_management_engine.py`

- **Caller:** `turn_engine.py` Phase 0b (per-tick).
- **Calls:**
  - `ship.is_combat_capable`, `ship.get_all_resource_costs_per_turn`, `ship.consume_resource`, `ship.set_component_enabled`
  - `services.component_inspector.{get_component_abilities, get_ability_list}`
- **Mutates:** `ship.resources` (via `consume_resource`); per-component-enabled flag.
- **Branching:** Skip non-combat-capable; skip zero-cost; layer is `list` vs `dict`; component-id lookup miss; ability trigger == `per_turn` AND resource matches.
- **Errors:** `ValidationException` if `registries` is `None` or any `fleet.ships is None`.

---

## `fleet_movement_engine.py`

- **Caller:** `turn_engine.py` Phase 2 (`collect_movements`) + Phase 3 (`apply_movements`).
- **Calls:**
  - `FleetNavigationService.calculate_fleet_next_hex`
  - `services.system_effects_collector.{collect_sector_effects, aggregate_value_or}`
  - `services.fleet_speed_calculator.get_tick_interval`
  - `core.hex_math.hex_distance`
  - `Fleet.{capabilities.can_use_warp, resources.has_resources_for_movement, resources.has_resources_for_warp, resources.consume_warp_resources, resources.consume_movement_resources, clear_orders, pop_order, get_current_order}`
- **Mutates:** `fleet.location`; clears / pops orders; consumes fleet movement and warp resources.
- **Branching:** speed ≤ 0; effective speed (storm modifier); tick % interval; ACTION_ORDER_TYPES skip; BUILD-order skip; warp distance > 1; warp capability + resources; mutual-pursuit swap parity; size tiebreak by ship count then fleet id.
- **Errors:** `ValidationException` if any `fleet.location is None`.

---

## `order_processor.py`

- **Callers:** `turn_engine.py` Phase 1 (instant orders) + `ActionExecutionEngine` (action orders) + `BuildOrderProcessor` (build orders).
- **Calls:**
  - `Fleet.merge_with`
  - `Empire.{remove_fleet, add_colony, add_fleet, race_config}`
  - `validation.ColonizeValidator.{validate, fleet_has_drop_pod, find_ship_with_drop_pod}`
  - `validation.TransferValidator.validate`
  - `Planet.{add_to_stockpile, consume_from_stockpile, get_stockpile, add_to_staging_yard, remove_from_staging_yard, populations, facilities}`
  - `Fleet.resources.{get_fleet_cargo_current, get_fleet_cargo_capacity, load_cargo_to_fleet, unload_cargo_from_fleet}`
  - `Ship.{can_carry_pod, get_pod_storage_capacity, carried_items}`
  - `Galaxy.{get_planet_by_id, get_planets_at_global_hex, get_system_of_planet}`
  - `SuperweaponOrderProcessor.process_*`
  - `EventBus.log_event`
- **Mutates:** Fleet membership, planet ownership, planet population, planet stockpile, planet facilities, planet staging yard, ship `carried_items`, fleet cargo. Pops orders.
- **Branching:**
  - JOIN_FLEET — target valid? co-located?
  - COLONIZE — validation, drop-pod check, target resolution including the "Any" planet sentinel
  - TRANSFER — direction × `cargo_type` × target-kind (planet vs fleet, drop_pod / passengers / resources)
  - BUG-70 auto-resolve `LOAD_POPULATION` at fleet hex
  - Instant-orders Phase A/B/C with mutual-pair election (most ships wins, smaller id tiebreak) and cycle-of-3+ deferral
  - Superweapon dispatch via handler dict
- **Errors:** `ValidationException` if `fleet.orders is None`; `logger.error` if COLONIZE missing `component_registry`.

---

## Top 3 surprising behaviors per file (15 total)

### `production_engine.py`

1. `MAX_QUEUE_ITERATIONS = 10` silent cap — 11+ free items in one tick stall silently.
2. `is_complex_only` queue STOPs (not SKIPs) on the first non-complex item — one bad item poisons the rest of the colony's base queue for that tick.
3. `_calculate_tick_expenditure` returns `None` when ANY required resource has rate 0 — the entire item halts even if other resources have abundant rate.

### `production_spawner.py`

1. `_load_design` returns `{}` (not `None`) on failure, and `_create_and_place_facility` happily builds a `PlanetaryFacility` named `design_id` with empty `design_data` — silent half-broken facility.
2. `_spawn_to_staging_yard` calculates mass via `simulation.entities.ship_design_stats.calculate_design_stats` with the production registries — a strategy-layer engine reaching into simulation for cost math.
3. `_spawn_fleet_complex` falls back to `planets_at_hex[0]` if `target_planet_id` doesn't match any planet — silent wrong-planet spawn rather than failure.

### `consumable_management_engine.py`

1. Hard-coded `total_cost / 100.0` divisor (not the `TICKS_PER_TURN` constant) — drift hazard if `TICKS_PER_TURN` is ever retuned.
2. Auto-disable iterates ALL components matching the depleted resource per ship per tick — repeated depletions on the same tick re-disable the same components and re-log.
3. `is_combat_capable()` is the gate for ALL consumption — non-combat ships skip per-turn consumption entirely (no fuel burn for transports?).

### `fleet_movement_engine.py`

1. `_get_effective_fleet_speed` returns `max(0.0, float(int(modified_speed)))` — `int(0.99) = 0`, so a 0.99× modifier turns a speed-1 fleet immobile.
2. `_filter_jump_past_collisions` only handles distance-1 swap parity; distance-3 leapfrog explicitly deferred — fleets at distance 3 with parity speed 2 pass through each other and only co-locate by chance next tick.
3. `apply_movement` for warp `pop_order()` on warp-blocked-no-capability AND warp-blocked-no-resources, but warp-no-resources logs the SAME `warp_blocked=False` field as the non-warp path — caller can't distinguish "warp resource shortage" from "ordinary movement complete-with-no-move".

### `order_processor.py`

1. `process_transfer` looks up target fleets via `getattr(galaxy, 'empires', [])` — silently empty if `galaxy` has no `empires` attr; transfer cancels with no diagnostic.
2. `process_join_fleet` (single) pops the order on "Not at same location"; `process_instant_orders` Phase A simply skips non-colocated candidates without popping — call-path ordering matters.
3. `_load_pod_from_staging_yard` iterates the staging yard in REVERSE — last-in-first-out for pods, which conflicts with the "first compatible ship" forward scan inside the loop. Order-dependent behavior.

---

## Testability Blockers

**None.** All 5 engines are constructor-injected with explicit dependencies (registries, event_bus, nav_service). `Galaxy`, `Empire`, `Fleet`, `Planet` are all duck-typed in the engine bodies (no `isinstance` checks except for `Fleet` and `Planet`), so `MagicMock` with the right attribute set works.

The only shape gotcha is `production_engine`'s `colony_or_fleet.context_type` discrimination — fixtures must set `context_type='planet'` or `'fleet'` explicitly, since `MagicMock` would otherwise auto-attribute and break the empire-pool fallback path.

---

## production_engine test-file split boundary (MAJ-002 clarification)

The two `test_production_engine_*.py` files split coverage of the same
production class along a usage-axis line — NOT along a method boundary.
Both files exercise overlapping methods; the split is which BEHAVIORS each
file pins, not which methods each file calls.

| Test file | Pins behaviors related to | Methods exercised (overlap allowed) |
|---|---|---|
| `test_production_engine_queue.py` | Queue iteration semantics: `MAX_QUEUE_ITERATIONS=10` cap, `is_complex_only` STOP-not-SKIP behavior, multi-item tick processing, completion-and-spawn handoff | `process_production`, `_process_queue_item`, `_calculate_tick_expenditure` (called as supporting), `_complete_item` |
| `test_production_engine_consumption.py` | Resource math + affordability routing: `context_type` planet-vs-fleet branch, zero-rate-required-resource-halts-item, shortage logging, partial-affordability arithmetic | `_calculate_tick_expenditure` (focal), `_route_consumption_by_context`, `_consume_resources`, `_log_shortage` |

`_calculate_tick_expenditure` is exercised in BOTH files: the `_queue.py`
file pins what happens when it returns `None` (item halts, queue continues
to next item), and the `_consumption.py` file pins WHEN it returns `None`
(zero-rate required resource) and the math of its return value when it
returns a non-empty dict. Tests in both files use a real
`production_engine` instance — no shared fixture mocks the method out.
Each file writes its own narrow expenditure scenarios; the test cases do
not overlap even though the method coverage does.

If a future refactor moves `_calculate_tick_expenditure` to a sibling
module (per a separate ticket), update this section's method column and
both test files; the behavioral split (queue iteration vs. resource math)
stays valid regardless of where the method physically lives.
