# PROJ-336 — Architecture context for the four services

> Read this before writing tests. Production behavior is the spec. Behavior
> here is described to-pin, not to-judge.

## fleet_navigation_service.py (759 LOC)

**Public surface (`FleetNavigationService` — module-level helpers/dataclasses also public):**

- `NavigationState` (frozen dataclass, `from_fleet(fleet)` classmethod) — immutable snapshot of fleet for pure-function calculation.
- `PathSegment` (frozen dataclass, `to_dict()`) — one step in projected path; `to_dict()` includes a `'hex'` alias for `'end'` (intentional internal API).
- `NavigationStep` (frozen dataclass) — `(next_hex, new_state, order_complete)` triple returned by `compute_next_step`.
- `_projection_guard` (module-level `threading.local`) — per-thread reentrancy guard for `project_path` (cyclic MOVE_TO_FLEET protection).
- Methods on the service:
  - `get_destination(state, order, galaxy, self_fleet=None)` — switches on `order.type`; FEAT-28 mutual-pursuit short-circuit for `MOVE_TO_FLEET`; calls `calculate_intercept_point` otherwise.
  - `compute_path(state, destination, galaxy)` — wraps `find_hybrid_path` + `strip_start_hex`.
  - `compute_path_for_warp(state, warp_point_hex, galaxy)` — pathfinds to warp point, then appends exit hex via `_resolve_warp_exit`.
  - `_resolve_warp_exit(warp_point_hex, galaxy)` — looks up source system in `galaxy._global_hex_warp_points`, finds local warp point, resolves destination system + reciprocal exit. Three failure modes (no source / no local match / no destination system) all log + return None; one fallback (no reciprocal warp point → use destination system center).
  - `compute_next_step(state, galaxy, self_fleet=None)` — pure orchestrator. Special branch: WARP order at warp-point hex jumps directly to exit and pops order with `order_complete=True`.
  - `project_path(fleet, galaxy, max_turns=10, component_registry=None)` — outer wrapper: re-entrancy guard add/remove around `_project_path_inner`.
  - `_project_path_inner` — main simulation loop: advances by movement ticks or action ticks, respects `max_turns`, has a `max_steps = max_turns * moves_per_turn + 100` safety break.
  - `_consume_ticks(moves_left, current_turn, moves_per_turn, max_turns, ticks)` — pure static method; turn-boundary crossing.
  - `_project_action_order(...)` — consumes `action_time` ticks (adjusted by `initial_progress` on first action only) and advances state by popping the order.
  - `_resolve_path_for_order(...)` — destination + path resolution for movement orders.
  - `project_path_as_dicts(fleet, galaxy, max_turns=10, component_registry=None)` — wraps `project_path` and `to_dict`s each segment.
  - `calculate_fleet_next_hex(fleet, galaxy)` — mutation bridge: invalidates `MOVE_TO_FLEET` orders with `target=None` (pops + returns None), otherwise wraps `compute_next_step`, applies `step.new_state.path` to fleet, pops order on completion.

**State mutations:**
- Almost everything is pure (NavigationState is frozen; `replace` returns new instances).
- `calculate_fleet_next_hex` mutates fleet: assigns `fleet.path = list(...)` and calls `fleet.pop_order()`.
- `_projection_guard.fleet_ids` is mutated as a per-thread set (add on enter, discard on exit).

**Branching summary:** `get_destination` 4-way; `_resolve_warp_exit` 4 outcomes; `compute_next_step` ~6 branches; `_project_path_inner` while-loop with action-vs-movement order branches.

## system_destroyer.py (179 LOC)

**Public surface (module functions + 2 dataclasses):**

- `SYSTEM_RADIUS_HEXES = 50` — module constant matching `pathfinding.get_system_at_hex`'s radius.
- `SystemDestructionPlan` (frozen dataclass) — `system, planets, stars, fleets` plus `fleet_count` property.
- `SystemDestructionResult` (mutable dataclass) — counts and ship_names list.
- `collect_system_contents(system, galaxy, empires, *, radius=SYSTEM_RADIUS_HEXES)` — snapshots planets, stars, and fleets-in-radius into an immutable plan. **No mutation.** Uses `dist < radius` (strict less-than).
- `destroy_system(plan, galaxy, empires, *, remove_stars=True, event_bus=None)` — applies the plan: removes planets (drops from owner empire colonies + `galaxy.unregister_planet`), removes fleets (collects ship names, calls `Empire.remove_fleet(event_bus=event_bus)`), optionally removes stars (just `plan.system.stars = []`).

**State mutations (in `destroy_system`):**
- `empire.colonies.remove(planet)` for the owning empire.
- `galaxy.unregister_planet(planet)` — outbound side effect.
- `Empire.remove_fleet(victim_fleet, event_bus=event_bus)` — outbound side effect.
- `plan.system.stars = []` — direct list reassignment on the (referenced, not snapshotted) StarSystem.

**Edge cases / branching:**
- Empty empires iterable → empty fleets in plan.
- Empty fleets list per empire → handled.
- Planet with `owner_id=None` → skipped in colony-removal loop.
- Planet not in any empire's colonies → still unregistered (no-op for colonies).
- `remove_stars=False` → stars left intact, `result.stars_removed = 0`.
- `event_bus=None` → passed through to `Empire.remove_fleet` (its own contract handles None).
- Fleet at exact `radius` → excluded (because `<`, not `<=`).

## fleet_cargo_projector.py (64 LOC)

**Public surface:**
- `FleetCargoProjector.get_projected_cargo(fleet, cargo_type) -> int` (staticmethod).

**Logic flow:**
- Read `current = fleet.resources.get_fleet_cargo_current(cargo_type)`.
- Read `capacity = fleet.resources.get_fleet_cargo_capacity(cargo_type)`.
- Walk `fleet.orders`, filter to (`TRANSFER`, `LOAD_POPULATION`, `UNLOAD_POPULATION`).
- Skip if `order.target` is not a dict (defensive — happens for fleet-target orders).
- Skip if `params.get('cargo_type') != cargo_type`.
- For `direction == 'load'`: `delta = amount if amount > 0 else (capacity - projected)`; `projected = min(projected + delta, capacity)`.
- For `direction == 'unload'`: `delta = amount if amount > 0 else projected`; `projected = max(projected - delta, 0)`.
- Anything other than `'load'` / `'unload'` (including missing key) → no-op for that order.

**Edge cases:**
- Empty order queue → returns `current`.
- Order with non-dict target → silently skipped.
- `amount=0, direction='load'` → fills to capacity.
- `amount=0, direction='unload'` → unloads everything.
- Negative amount → applied as-is (Decision D-008 observation).
- Multiple orders for same cargo_type → cumulative.
- Mixed cargo types → only matching cargo_type orders affect projection.

## stabilizer_registry.py (119 LOC)

**Public surface:**
- `StabilizerSpec` (frozen dataclass): `ability_name, scopes, blocks`.
- `STABILIZERS` (module tuple): 3 specs — Geologic, Stellar, WarpField.
- `find_blocking_stabilizer(order_type, reference_planet, galaxy, empires, component_registry=None) -> Optional[StabilizerSpec]`.

**Logic flow:**
- If `reference_planet is None`: return None (Decision D-007 observation).
- For each `spec in STABILIZERS`:
  - If `order_type not in spec.blocks`: continue.
  - For each `empire in empires`:
    - For each `scope in spec.scopes` (narrow → wide):
      - Call `find_abilities_in_scope(spec.ability_name, reference_planet, galaxy, empire, scope, registries=component_registry, require_active=True)`.
      - If found: return spec immediately (first-hit-wins).
- Return None if nothing matches.

**Branching / iteration order matters:**
- Outer loop: STABILIZERS order (currently Geologic, Stellar, WarpField). For an order_type blocked by only one spec the order is irrelevant; if a future spec block-set overlaps another's, the iteration order determines which `StabilizerSpec` is returned.
- Inner loop: empires-then-scopes. A geologic stabilizer in `system` scope on empire A is found BEFORE a geologic stabilizer in `planet` scope on empire B. (May be intentional, may not be — pin as observation, do not "fix".)

**Edge cases:**
- `reference_planet=None` → None (short-circuit).
- `empires=[]` → None.
- `order_type` not in any spec's `blocks` → None.
- `component_registry=None` → passed through to `find_abilities_in_scope` (which is documented as "required" in this module's docstring — pin current behavior, flag if asymmetry).
