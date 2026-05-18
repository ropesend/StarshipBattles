# PROJ-FMS-B Phase 1: Strategic mine layer + minefield_resolver + warhead trigger math

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Player can strategically lay mines from a ship's bay; an enemy fleet entering the mined hex takes warhead damage via the formula in the shared design. Laserhead pass deferred to Phase 2 (this phase only does the warhead pass).

## Tasks

### Balance file
- [x] Create [`data/balance/mines.json`](../../../data/balance/) with constants:
  ```json
  {
    "warhead_trigger": {
      "k_size": 1.0,
      "k_eva": 0.5,
      "bias": 2.0
    },
    "sensitivity_multipliers": { "LOW": 0.5, "MED": 1.0, "HIGH": 1.5 },
    "scatter": {
      "fallback_radius_m": 5000.0,
      "seed_namespace": "fms.mines.scatter.v1"
    },
    "laserhead": {
      "default_threshold": 0.30
    }
  }
  ```
- [x] Loader for this file alongside other balance files. Expose via DI to the resolver.

### Strategic mine-laying execution (Command → OrderType → Handler)

Strategic actions in this codebase flow through Command classes (in [`game/strategy/engine/handlers/`](../../../game/strategy/engine/handlers/)) that issue an `Order` (with a typed `OrderType`); the order is later executed by an `OrderHandler` subclass in [`game/strategy/engine/order_handlers/`](../../../game/strategy/engine/order_handlers/). See [`colonize.py`](../../../game/strategy/engine/order_handlers/colonize.py) for the canonical pattern.

- [x] `OrderType.LAY_MINES` should already be reserved in [`order_types.py`](../../../game/strategy/data/order_types.py) from PROJ-FMS-A Phase 5. Verify.
- [x] New `IssueLayMinesCommand` + `LayMinesCommandHandler` in [`game/strategy/engine/handlers/`](../../../game/strategy/engine/handlers/) (or in a new file). Inputs: `fleet_id`, `ship_instance_id`, `target_hex` (default = current hex), `count`, `mine_design_id`. The command issues an Order on the fleet that runs at the next strategic resolution.
- [x] New `LayMinesOrderHandler(BaseOrderHandler)` in [`game/strategy/engine/order_handlers/lay_mines.py`](../../../game/strategy/engine/order_handlers/). `supported_order_types = (OrderType.LAY_MINES,)`. `execute_action_order(fleet, empire, galaxy, ...)`:
  - Pop N matching mines from the issuing ship's `VehicleBay` (fail cleanly via `OrderExecutionResult(success=False, ...)` if insufficient).
  - Locate or create a `mine_group` Fleet for that owner at the target hex.
  - Append the mines to the group.
- [x] Multiple `mine_group`s per owner per hex allowed (no auto-merge).
- [x] Newly created `mine_group` defaults to sensitivity `MED` and `expected_hit_chance_threshold = laserhead.default_threshold` (from balance file).
- [x] Scatter coords on the group are populated using the deterministic PRNG (seeded by `{seed_namespace, owner_id, hex, launch_turn}`) — fallback radius from balance file since we don't have a tactical map at strategic-launch time.

### `minefield_resolver.py`
- [x] New file at `game/strategy/engine/minefield_resolver.py`.
- [x] Entry point: `resolve_minefield_entry(galaxy_state, fleet, hex) -> List[CombatEvent]`.
- [x] For each `mine_group` in the hex **not owned by `fleet.owner`**:
  - For each enemy ship in `fleet` in fleet-entry order:
    - Compute `p_trigger` per warhead mine using ship's `size_score`, `maneuver_score`, and the group's `sensitivity`.
    - Compute `P_trigger_pass = 1 - (1 - p_trigger)^N` over the group's *current* warhead-mine count `N`.
    - Roll once. On trigger: pop one warhead mine, apply `Warhead.damage` through [`damage_calculator.py:44-84`](../../../game/simulation/combat/damage_calculator.py#L44) against the ship; emit a `CombatEvent`.
    - **Laserhead pass placeholder**: log "TODO PROJ-FMS-B Phase 2" — implement in Phase 2.
- [x] If the `mine_group` is reduced to zero mines, remove it from the empire's fleets list.

### Wire into turn engine
- [x] In [`game/strategy/engine/turn_engine.py`](../../../game/strategy/engine/turn_engine.py), find the movement phase. After fleet moves resolve and **before** [`conflict_resolution_engine.py`](../../../game/strategy/engine/conflict_resolution_engine.py) runs, call `resolve_minefield_entry` for any fleet that entered a hex containing enemy `mine_group`s.
- [x] If a fleet is destroyed by mines before combat would begin, prune it from the conflict resolution input.

### `WarheadAbility` data wiring
- [x] Confirm `WarheadAbility.damage` is readable from a `CarriedVehicle`'s design — the resolver needs to read each warhead's damage value to apply, and a single mine may carry warheads of multiple sizes. (Single mine = single warhead is the common case, but the data model supports multiple.)

### Tests
- [x] Lay 5 warhead mines via `IssueLayMinesCommand`; verify a `mine_group` appears in empire fleets with 5 entries and correct scatter coords after the next strategic resolution.
- [x] Insufficient mines in bay → `LayMinesOrderHandler.execute_action_order()` returns `OrderExecutionResult(success=False, ...)` cleanly with a clear error.
- [x] Enter the mined hex with a destroyer-class enemy; assert `P_trigger > 0` and `< 1`; over many trials, observed trigger rate ≈ `P_trigger_pass`.
- [x] Mine count decrements on each successful trigger.
- [x] Bigger ship (dreadnought-class) triggers more often than a destroyer-class for the same field — statistical test over many runs.
- [x] All warhead mines consumed → group removed from empire fleets.
- [x] Friendly fleet entering the hex → no trigger rolls performed.
- [x] Resolver runs **before** combat starts: a fleet destroyed entirely by mines never reaches `conflict_resolution_engine`.

## Verification
- `python Tools/test_sharded/test_sharded.py`
- `pytest tests/unit/strategy/engine/test_minefield_resolver.py -v`
- Manual: load a save, lay mines via dev console / UI affordance from PROJ-FMS-A, move enemy fleet into the hex, observe damage events.

## Exit criteria
- Strategic mine laying works end-to-end through the data model.
- Warhead pass triggers per the formula; laserhead pass is a TODO marker for Phase 2.
- No regressions in turn-engine movement / conflict resolution.
