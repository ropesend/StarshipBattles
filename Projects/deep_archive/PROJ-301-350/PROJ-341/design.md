# PROJ-341 — Design / Architecture context

This document captures *what each in-scope file does* and *how it fits into the strategy turn loop*, so a future maintainer reading the test files knows which collaborator's contract is being pinned.

This is not a redesign — it's a description of the production code as it stands today.

---

## 1. `game/strategy/engine/environmental_hazard_engine.py`

### What it does
Applies storm and fuel-drain effects to fleets each tick of the 100-tick turn loop. Originally backed by a dedicated `AreaEffectManager` (deleted in PROJ-300 Phase 7); now reads ability rows from the unified `system_effects_collector` pipeline so that storms + facility-projected hazards sum naturally.

### Public surface
- `EnvironmentalHazardEngine()` — no constructor args. Implements `IEnvironmentalHazardEngine`.
- `process_environmental_tick(tick: int, empires: List, galaxy) -> List[EnvironmentalEvent]` — the only public entry point.
- `EnvironmentalEvent(fleet_id, storm_name, damage_dealt, fuel_drained, tick)` — dataclass record returned per affected fleet.

### Private surface (still pinned by tests)
- `_validate_tick_inputs(empires)` — PROJ-251 precondition guard. Raises `ValidationException` if any fleet has `location is None`.
- `_apply_damage_to_ship(ship, damage) -> float` — applies environmental hull damage; bypasses shields. Returns actual damage dealt. Sets `ship.is_alive = False` if `new_hp <= 0`.
- `_drain_fuel_from_ship(ship, amount) -> float` — drains fuel via `ship.consume_resource("fuel", amount)`, capped at current fuel.

### Tick-loop integration
Phase 0f of the strategy turn loop, called each tick after Phase 0e (construction). Per-tick scaling: `damage_per_tick = damage_per_turn / 100.0`, `fuel_drain_per_tick = fuel_per_turn / 100.0`.

### Per-fleet flow inside `process_environmental_tick`
For each empire's fleets:
1. Resolve fleet's star system via `galaxy.get_system_at_location(fleet.location)`. If None, skip.
2. Call `collect_sector_effects(system, fleet.location, empire_id=None, registries=None)`.
3. Filter effects by `ability_name` into damage and fuel lists; sum `aggregate_value`.
4. If both zero or no combat-capable ships, skip.
5. Distribute damage: `damage_per_ship = damage_per_tick / len(combat_ships)`, applied per-ship.
6. Drain fuel: `fuel_drain_per_tick` applied **per ship** (not divided — see decision OBS-003).
7. Pick a representative `source_label` from the first provider that has one; fallback "Unknown Hazard".
8. Append `EnvironmentalEvent` if any damage or fuel drained.

### Collaborators
- `game.strategy.services.system_effects_collector.collect_sector_effects` — primary data source (mocked in tests).
- `galaxy.get_system_at_location(loc)` — duck-typed; tested via mock galaxy.
- `fleet.get_combat_capable_ships()` — must exist on the Fleet class.
- `ship.get_calculated_stats()`, `ship.current_hp`, `ship.is_alive`, `ship.get_current_resource("fuel")`, `ship.consume_resource("fuel", amount)` — ship duck-typed surface.

---

## 2. `game/strategy/engine/superweapon_order_processor.py`

### What it does
Processes the six superweapon order types during the strategy turn loop. Each method:
1. Validates the order type matches.
2. Looks up the spatial context (system, planet, target system).
3. Checks for stabilizer protection via `find_blocking_stabilizer` (delegated lookup; cancels order if blocked).
4. Locates the ship that carries the required ability via `SuperweaponValidator.find_ship_with_ability` (cancels if no ship).
5. Executes the effect.
6. Calls `_finalize_superweapon` to optionally consume the ship, pop the order, clean up empty fleets, and log the event.

### Public surface
- `SuperweaponOrderProcessor(event_bus=None)` — optional EventBus for structured logging.
- `process_implode_planet(fleet, empire, galaxy, empires, component_registry=None) -> SuperweaponResult`
- `process_stellerate_star(fleet, empire, galaxy, empires, component_registry=None) -> SuperweaponResult` (suicide weapon — always consumes fleet)
- `process_open_warp_point(fleet, empire, galaxy, empires=None, component_registry=None) -> SuperweaponResult`
- `process_close_warp_point(fleet, empire, galaxy, empires=None, component_registry=None) -> SuperweaponResult`
- `process_create_dyson_sphere(fleet, empire, galaxy, empires, component_registry=None) -> SuperweaponResult`
- `process_self_destruct(fleet, empire, galaxy) -> SuperweaponResult`
- `SuperweaponResult(success, fleet_consumed, message)` — dataclass return type.

### Private surface (pinned by tests)
- `_finalize_superweapon(fleet, empire, ship, event_type, event_message, log_message, consume_ship=True, **event_kwargs)` — common end-pattern. Capture `fleet.location` BEFORE potentially removing fleet (FEAT-04). Consume ship if requested. Pop order. Detect empty fleet. Call `empire.remove_fleet(fleet, event_bus=...)` (SG-003). Log to logger + event bus.
- `_check_blocking_stabilizer(order_type, reference_planet, galaxy, empires, component_registry)` — thin delegate to `find_blocking_stabilizer`. Component registry MUST be threaded.
- `_get_reference_planet(fleet_location, galaxy)` — returns the **first** planet in the system at `fleet_location`, or None.

### Ship-consumption rule
Only `stellerate_star` and `self_destruct` consume the ship. Every other superweapon preserves the ship for reuse.

### Stabilizer-blocking rule
All five non-self-destruct superweapons consult `_check_blocking_stabilizer` before executing. If the registry returns a `StabilizerSpec`, the order is popped and `SuperweaponResult(success=False, message="<system> is protected by a <ability_name>")` is returned. The existing 27 tests do NOT exercise this branch for any superweapon — that's the primary gap.

### Open-warp-point geometry
Two warp points are added: a "near-end" at the fleet's local position within the current system, and a "far-end" at a hex on the target system pointing back toward the source. Far-end math (lines 376-384):
```
direction_q = current.global_location.q - target.global_location.q
direction_r = current.global_location.r - target.global_location.r
dist = max(abs(direction_q), abs(direction_r), 1)
far_q = round(direction_q / dist * 6)
far_r = round(direction_r / dist * 6)
```
Note `dist` is Chebyshev-style `max(|q|, |r|)`, not euclidean and not hex-axial. This produces deterministic but slightly non-symmetric placements for diagonal pairings.

### Close-warp-point sector-precision rule
Order target is a dict `{'destination_id': <name>, 'target_hex': {'q': ..., 'r': ...}}`. If the fleet's location does not match `expected_hex`, the order is rejected with a "wrong sector" message — protects against move-reorder bugs that put the fleet at the right system but wrong hex. Legacy plain-string targets (back-compat) skip the hex check.

### Dyson-Sphere creation
- Removes star(s) from system.
- Removes planets within Chebyshev-style distance `<= 5` from the primary star (clearing radius). The Dyson Sphere itself is registered with `radius_hexes=6` (a multi-hex zone of 91 hexes).
- Reads ideal environmental conditions from `empire.race_config.preferences` (PROJ-283 Phase 4 registry-driven preferences). Falls back to human-comfortable defaults if `empire.race_config is None`.

### Collaborators
- `game.strategy.services.stabilizer_registry.find_blocking_stabilizer` (deferred import).
- `game.strategy.services.system_destroyer.collect_system_contents`, `destroy_system` (used only by STELLERATE_STAR).
- `game.strategy.validation.superweapon_validator.SuperweaponValidator.find_ship_with_ability`.
- `game.strategy.data.pathfinding.get_system_at_hex`.
- `galaxy.unregister_planet(planet)`, `galaxy.register_planet(system, planet)`, `galaxy.remove_warp_link(src, dst)`, `galaxy.name_map`.
- `empire.colonies` (planet ownership lists), `empire.remove_fleet(fleet, event_bus=...)`, `empire.race_config`.

---

## 3. `game/strategy/engine/action_execution_engine.py`

### What it does
Drives tick-based progress for action orders (everything except MOVE / WARP / BUILD). On each tick, decides which fleets are eligible (based on speed → tick interval), increments `order.execution_progress`, and delegates to the injected order processor when progress reaches `action_time`.

### Public surface
- `ActionExecutionEngine(order_processor, action_time_resolver=None)` — DI-friendly constructor. Implements `IActionExecutionEngine`.
- `process_action_ticks(empires, galaxy, tick, component_registry=None, all_empires=None) -> List[ActionTickResult]`.
- `ActionTickResult(fleet_id, order_type, action_completed, fleet_consumed, execution_progress, action_time)` — dataclass return type.

### Private surface (pinned by tests)
- `_validate_tick_inputs(empires)` — PROJ-251 guard, identical contract to the environmental engine.
- `_process_fleet_action_tick(fleet, empire, galaxy, tick, component_registry, all_empires) -> Optional[ActionTickResult]` — per-fleet branching.
- `_execute_action(fleet, empire, galaxy, component_registry, all_empires) -> bool` — thin pass-through to `order_processor.execute_action_order(...)`.

### Per-fleet decision tree (inside `_process_fleet_action_tick`)
1. Skip if `fleet.speed <= 0` (immobile).
2. Compute `interval = get_tick_interval(fleet.speed)` (PROJ-204 shared logic). Skip if `tick % interval != 0`.
3. Skip if `fleet.get_current_order() is None`.
4. Skip if order type is in `MOVEMENT_ORDER_TYPES` (handled by FleetMovementEngine).
5. Special-case BUILD: if `construction_queue` is empty, auto-pop; otherwise skip (handled by ProductionEngine).
6. Skip if order type is not in `ACTION_ORDER_TYPES`.
7. Increment `order.execution_progress`.
8. Resolve `action_time` via `ActionTimeResolver.resolve_action_time(fleet, order, component_registry)`.
9. If `progress >= action_time`, call `_execute_action` (which delegates to the order processor) and return `ActionTickResult(action_completed=True, fleet_consumed=...)`. Otherwise return `ActionTickResult(action_completed=False, ...)`.

### Order-popping responsibility
The engine **does not** pop completed orders. The injected order processor is expected to pop the order as part of its handler (e.g. `_finalize_superweapon` does this). The engine just signals completion via `action_completed=True`.

### Iteration safety
`process_action_ticks` iterates `list(empire.fleets)` (a copy) so the order processor can `empire.remove_fleet(fleet)` mid-iteration without invalidating the loop.

### Collaborators
- `game.strategy.services.action_time_resolver.ActionTimeResolver.resolve_action_time`.
- `game.strategy.services.fleet_speed_calculator.get_tick_interval`.
- `game.strategy.data.fleet.MOVEMENT_ORDER_TYPES`, `ACTION_ORDER_TYPES`, `OrderType.BUILD`.
- The injected `order_processor.execute_action_order(fleet, empire, galaxy, component_registry, empires)` — duck-typed; tests use a `MagicMock`.

---

## How the three files connect

The `action_execution_engine` is the dispatcher; on completion it calls into the injected order processor (in production, the strategy layer's monolithic `OrderProcessor`, which routes to `SuperweaponOrderProcessor` for the six superweapon types). The `environmental_hazard_engine` runs in a different phase of the same tick — it is independent of the action engine but consumes the same `Fleet` and `Empire` shape.

```
Turn loop (per tick):
  Phase 0e: ProductionEngine (BUILD)
  Phase 0f: EnvironmentalHazardEngine (this scope)         <-- file 2
  Phase 0g: ActionExecutionEngine (this scope)             <-- file 3
              \-> order_processor.execute_action_order
                    \-> SuperweaponOrderProcessor.process_X (this scope)   <-- file 1
  Phase 0h: FleetMovementEngine (MOVE / WARP / MOVE_TO_FLEET)
```

All three files share the PROJ-251 `_validate_tick_inputs` pattern and the PROJ-204 `get_tick_interval` speed model.
