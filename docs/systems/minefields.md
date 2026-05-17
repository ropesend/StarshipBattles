# Minefields (PROJ-FMS-B)

End-to-end mine system. Players design mines in the workshop, build them
through standard shipyard production, load them into a ship's
``VehicleBay``, and lay them strategically into a hex via the
``LAY_MINES`` order. Enemy fleets that subsequently enter the hex face
a per-ship warhead pass and laserhead pass before normal conflict
resolution. Mines also participate in tactical combat — they sit at
scattered coordinates on the battle map and react per-tick to enemy
ship movement.

## Vehicle and component model

Authored in `data/vehicleclasses.json` and `data/vehiclelayers.json`
(PROJ-FMS-A):

- Four mine vehicle classes: `Mine (Small/Medium/Large/Heavy)`.
- One `Mine_Standard` layer (single CORE) with a component whitelist
  for `Warhead`, `Laserhead`, `StructuralIntegrity`, and
  `ToHitAttackModifier`.
- Per-class ``signature_bonus`` flowed into `total_defense_score`
  through `game/simulation/entities/ship_stats.py` (the
  `signature_bonus` aggregation block), making mines very hard to
  hit by conventional weapons.

Component data (in `data/components.json`):

- `warhead_{small,medium,large}` — explosive payload.
- `laserhead_{small,medium,large}` — single-shot beam.
- `small_targeting_sensor` / `small_targeting_sensor_advanced` —
  ToHitAttackModifier without `RequiresCommandAndControl`.
- `hull_mine_{small,medium,large,heavy}` — provides mine HP via
  `StructuralIntegrity`.
- `ram_target_module` — designates the mine / fighter / ship as
  able to set a ram target.

Three new ability classes (PROJ-FMS-A Phase 2):

- `WarheadAbility` — single `damage` attribute. Always hits on
  trigger (no second accuracy roll).
- `LaserheadAbility(BeamWeaponAbility)` — inherits beam targeting /
  range / hit-chance sigmoid; adds `consume_on_fire=True`.
- `RamTargetAbility` — explicit set-target action; collision
  detonates all warheads on the rammer.

## Strategic mine laying

Command -> Order -> Handler chain (mirrors `ColonizeHandler`):

1. UI dispatches `IssueLayMinesCommand(fleet_id, ship_instance_id,
   mine_design_id, count, target_hex)` via
   `dispatch_issue_lay_mines`.
2. `LayMinesCommandHandler` validates carrier presence + mine count
   and queues `Order(OrderType.LAY_MINES, target={...})`.
3. `ActionExecutionEngine` ticks the order; the registered
   `LayMinesOrderHandler` pops the mines from the carrier's
   `VehicleBay` and creates / extends a `mine_group` Fleet at the
   target hex.

A `mine_group` Fleet has `group_kind == "mine_group"` (PROJ-FMS-A
Phase 4). New `mine_group`s default to:

- Sensitivity `MED` (warhead trigger multiplier 1.0).
- `expected_hit_chance_threshold = 0.30` (from
  `data/balance/mines.json`).

The mine_group stores:

- `sensitivity` (LOW / MED / HIGH).
- `expected_hit_chance_threshold` (continuous 0.0..1.0).
- `mine_positions` (List[(x, y)]) — scatter coords.
- `scatter_seed` (int) — stable PRNG seed for the layout.

Multiple `mine_group`s per owner per hex are allowed; each
`IssueLayMinesCommand` mints a fresh `mine_group` — no auto-merge
(PROJ-FMS-B audit Fix 4).

## Strategic detonation math

At the strategic layer, an enemy fleet that ends a movement tick on
a hex containing one or more enemy `mine_group`s runs the minefield
resolver BEFORE `ConflictResolutionEngine`. Wired in
`game/strategy/engine/turn_phase_registry.py::_derive_moved_fleet_ids`
as a post-hook on the `movement_apply` phase.

Per ship, in fleet-entry order, the resolver runs the warhead pass
then the laserhead pass.

**Warhead pass** — per-mine trigger chance:

```
p_trigger      = sensitivity * sigmoid(k_size * bulk_score
                                         - k_eva * maneuver_score
                                         - bias)
P_trigger_pass = 1 - (1 - p_trigger) ** N         (over N warhead mines)
```

where:

- `bulk_score = -ship.size_score` (the `size_score` computed in
  `ship_stats.py` is negative for bigger ships because it's a
  defense term; the trigger formula uses the negated value so bigger
  = more triggers).
- `maneuver_score = sqrt(accel / 20 + turn_speed / 360)`.
- `sensitivity` = the mine_group's LOW/MED/HIGH multiplier
  (0.5 / 1.0 / 1.5) from `data/balance/mines.json`.

On trigger, one warhead mine is sampled uniformly and its damage is
applied through `DamageCalculator.apply_damage` (when registries are
available; falls back to direct HP decrement otherwise). The mine is
removed from the group's inventory.

`P_trigger_pass` is computed in log-space so the "never 100%"
invariant holds for arbitrarily-large N (`exp(N * log(1-p))` floored
just above zero).

**Laserhead pass** — per-mine continuous threshold gate:

For each laserhead mine in the group:

```
expected_hit_chance = sigmoid(base_accuracy + sensor_bonus
                                  - accuracy_falloff * distance
                                  - defense_score)
```

If `expected_hit_chance < mine_group.expected_hit_chance_threshold`,
the laserhead is **skipped** (not consumed). Otherwise the standard
beam hit roll fires; the laserhead is consumed regardless of hit /
miss (`consume_on_fire`).

Friendly fleets at the hex skip the resolver entirely.

## Tactical (in-battle) mines

`game/simulation/systems/tactical_mine_resolver.py` owns per-tick
behaviour:

- Construction: `TacticalMineResolver.from_mine_group(mine_group,
  battle_boundary=(xmin, ymin, xmax, ymax))` builds the resolver from
  the strategic-layer `mine_group`. Mines scatter uniformly inside
  the battle boundary using the mine_group's stored seed
  (deterministic across re-entries). When no boundary is provided,
  the strategic-launch-time positions are used as-is.
- Per tick (`TacticalMineResolver.tick(...)`):
  - For each alive mine, find the closest enemy ship inside
    `warhead_proximity_radius` (default 600m, from
    `data/balance/mines.json`).
  - Warhead per-tick chance =
    ``strategic_p_trigger / expected_ticks_in_proximity`` (default
    expected = 50 ticks). Floored at `min_tick_chance`.
  - Laserhead within beam range: same threshold gate as strategic.
- Mines destroyed by point-defense fire (HP <= 0) are pruned without
  detonating.

The battle engine calls `_run_mine_resolver_tick()` after the
standard tick phases (`update()` in `battle_engine.py`). PROJ-FMS-B
audit Fix 2 added automatic spec-compiler wiring via
`build_mine_resolver_setup` (one `TacticalMineResolver` per
`mine_group` attached to `BattleEngine.mine_resolvers`, threaded
through a `pre_tick_loop_callback` plus a `_mine_groups` side-channel
on the frozen `BattleSpec`). `BattleEngine.mine_resolvers` (plural
list) is the load-bearing slot; `BattleEngine.mine_resolver`
(singular) is retained as a backwards-compat alias for the Phase 3
unit tests.

## Player controls (UI / service)

`game/strategy/services/mine_group_service.py::MineGroupService`:

- `set_sensitivity(mine_group, "LOW" | "MED" | "HIGH")`.
- `set_threshold(mine_group, 0.0..1.0)`.
- `get_mine_counts_by_design(mine_group)`.
- `self_destruct(mine_group, empire, {design_id: count})` —
  selectively destroys mines without triggering damage; prunes the
  group from the empire's fleet list when emptied.

The UI screens hook into these methods rather than mutating Fleet
state directly. (Pygame screen wiring is intentionally minimal; the
service layer is the testable boundary.)

## Planet-issued mine laying (QA Observation B)

A planetary-complex facility component exposing `StrategicMineLayer`
lets a planet issue `IssueLayMinesCommand(planet_id=...)`; the same
`LayMinesOrderHandler` ticks via `PlanetStagingYardIssuerAdapter`,
popping mine `CarriedVehicle`s from the planet's `staging_yard` and
producing a `mine_group` at the planet's hex (or merging into an
existing one). The planet right-click menu
([`planet_menu_items.build_menu_items`](../../game/ui/screens/planet_menu_items.py))
exposes the "Lay Mines" row when the facility ability gate passes and
the staging yard holds at least one mine.

## Ramming

`game/simulation/combat/ram_target_resolver.py::RamTargetResolver`:

- `set_ram_target(rammer, target)` — requires `RamTargetAbility` on
  the rammer; stashes `ram_target` + `ram_target_id` on the ship and
  on the ability instance.
- `process_ramming_tick(ships)` — for each ship with an assigned
  ram_target: collision-checks hull radii; on intersection, every
  `WarheadAbility` on the rammer detonates against the target via
  the damage pipeline; the rammer is destroyed regardless of damage
  outcome. If the target dies before collision, the rammer's ram
  target clears and it reverts to default AI.

Designs without `RamTargetAbility` cannot ram. Warheads on such
designs are inert payload (still cargo).

## Balance constants

`data/balance/mines.json`:

| Key | Default | Meaning |
|---|---|---|
| `warhead_trigger.k_size` | 1.0 | Bulk-score weight |
| `warhead_trigger.k_eva` | 0.5 | Maneuver-score weight |
| `warhead_trigger.bias` | 2.0 | Sigmoid bias (lower => more triggers) |
| `sensitivity_multipliers.LOW` | 0.5 | LOW factor |
| `sensitivity_multipliers.MED` | 1.0 | MED factor |
| `sensitivity_multipliers.HIGH` | 1.5 | HIGH factor |
| `scatter.fallback_radius_m` | 5000.0 | Strategic-launch scatter radius |
| `scatter.seed_namespace` | "fms.mines.scatter.v1" | PRNG namespace |
| `laserhead.default_threshold` | 0.30 | Default laserhead threshold |
| `tactical.warhead_proximity_radius` | 600.0 | Per-tick proximity radius |
| `tactical.per_tick_scaling` | "expected_ticks_in_proximity" | Scaling strategy |
| `tactical.min_tick_chance` | 1e-6 | Floor on per-tick chance |

## File map

| File | Purpose |
|---|---|
| `data/balance/mines.json` | Balance constants |
| `game/strategy/engine/minefield_balance.py` | Balance loader + dataclasses |
| `game/strategy/engine/minefield_resolver.py` | Strategic-entry resolver |
| `game/strategy/engine/order_handlers/lay_mines.py` | LAY_MINES order handler |
| `game/strategy/engine/handlers/lay_mines.py` | LayMines command handler |
| `game/strategy/engine/commands/__init__.py` | `IssueLayMinesCommand` |
| `game/strategy/engine/turn_phase_registry.py` | Turn-engine wiring (post-hook on movement_apply) |
| `game/strategy/services/mine_group_service.py` | Player operations on mine_groups |
| `game/simulation/systems/tactical_mine_resolver.py` | Per-tick tactical mine logic |
| `game/simulation/systems/battle_engine.py` | `mine_resolver` hook + per-tick invocation |
| `game/simulation/combat/ram_target_resolver.py` | Ramming behaviour |

## Test map

| File | Coverage |
|---|---|
| `tests/unit/strategy/engine/test_minefield_resolver.py` | Math invariants, warhead + laserhead passes, friendly skip |
| `tests/unit/strategy/engine/order_handlers/test_lay_mines_handler.py` | Lay-mines order handler |
| `tests/unit/simulation/systems/test_tactical_mine_resolver.py` | Per-tick tactical mines, scatter |
| `tests/unit/strategy/services/test_mine_group_service.py` | Sensitivity / threshold / self-destruct |
| `tests/unit/simulation/combat/test_ram_target_resolver.py` | Ramming behaviour |
| `tests/integration/test_fms_b_e2e.py` | Lay -> trigger -> self-destruct E2E |
| `tests/integration/test_ramming_e2e.py` | Kamikaze ramming E2E |
| `tests/integration/test_fms_b_statistical_balance.py` | 1000-trial statistical balance |
