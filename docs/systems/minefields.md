# Minefields (PROJ-FMS-B)

> **Last verified:** 2026-05-17 — PROJ-FMS-B end-to-end mine system
> shipped; Round 4 QA pass renamed `mine_launcher_small` to
> `mine_deployer`, added mine-only `mine_bay` storage, and widened
> `IssueLayMinesCommand` for planet-issued laying via the polymorphic
> `IIssuerAdapter` seam (see Pattern #40).

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

- `warhead` — explosive payload. Single component; explosive yield scales
  via `simple_size_mount` (`damage_mult` binding on `WarheadAbility`). QA
  Obs 1 (2026-05-16) consolidated the former `warhead_small/medium/large`
  tier triple into this one entry.
- `laserhead` — single-shot beam. Single component; damage / range / etc.
  inherit `BeamWeaponAbility`'s STAT_BINDINGS so `simple_size_mount`
  drives the tier. QA Obs 1 (2026-05-16) consolidated the former
  `laserhead_small/medium/large` triple.
- `small_targeting_sensor` / `small_targeting_sensor_advanced` —
  ToHitAttackModifier without `RequiresCommandAndControl`.
- `hull_mine_{small,medium,large,heavy}` — provides mine HP via
  `StructuralIntegrity`.
- `mine_deployer` — carries `StrategicMineLayer` /
  `TacticalMineLayer` (Round 4 Obs C renamed from
  `mine_launcher_small`; capacity / launch rate scale via
  `simple_size_mount`).
- `mine_bay` — typed mine-only storage (`VehicleBay` with
  `allowed_types=["mine"]`; added in Round 4 Obs C alongside
  the `fighter_bay` / `satellite_bay` typed bays).

Note: the legacy `ram_target_module` component was deleted by QA
2026-05-16 Obs 1b — ramming is now a universal tactical action with no
component gate. See the "Ramming" section below.

Ability classes (originally PROJ-FMS-A Phase 2):

- `WarheadAbility` — single `damage` attribute, scales via
  `simple_size_mount` `damage_mult` (Obs 1). Always hits on trigger
  (no second accuracy roll). Exposes a `consumed: bool` flag set by
  `RamTargetResolver` after a ramming collision (one-shot).
- `LaserheadAbility(BeamWeaponAbility)` — inherits beam targeting /
  range / hit-chance sigmoid; adds `consume_on_fire=True`. Single
  component scaled via `simple_size_mount` (Obs 1).

## Strategic mine laying

Command -> Order -> Handler chain (mirrors `ColonizeHandler`):

```python
IssueLayMinesCommand(
    fleet_id:          Optional[int] = None,
    ship_instance_id:  Optional[str] = None,
    mine_design_id:    str            = "",
    count:             Optional[int]  = None,   # None = lay ALL matching
    target_hex:        Optional[HexCoord] = None,
    planet_id:         Optional[int] = None,    # planet-issued alternative
)
```

Exactly one of `fleet_id` / `planet_id` is set (Round 4 Obs B).

1. UI dispatches `IssueLayMinesCommand(...)` via
   `dispatch_issue_lay_mines`.
2. `LayMinesCommandHandler` validates issuer presence + mine count
   (carrier ship for fleet-issued; facility staging-yard for
   planet-issued) and queues `Order(OrderType.LAY_MINES, target={...})`.
3. `ActionExecutionEngine` ticks both `fleet.orders` and
   `planet.orders` (widened in Round 4 Obs B); the registered
   `LayMinesOrderHandler` operates on an `IIssuerAdapter` (see
   Pattern #40), popping mine `CarriedVehicle`s via
   `adapter.pop_carried(...)` — `ship.carried_items` for fleet-issued,
   `planet.staging_yard` for planet-issued — and creates / extends a
   `mine_group` Fleet at the target hex.

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

## Planet-issued mine laying (QA Observation B / Pattern #40)

A planetary-complex facility component exposing `StrategicMineLayer`
lets a planet issue `IssueLayMinesCommand(planet_id=...)`; the same
`LayMinesOrderHandler` ticks via the `IIssuerAdapter` seam (see
Pattern #40 in `docs/02_PATTERNS.md`) using
`PlanetStagingYardIssuerAdapter`, popping mine `CarriedVehicle`s from
the planet's `staging_yard` and producing a `mine_group` at the
planet's hex (or merging into an existing one). The planet right-click
menu ([`planet_menu_items.build_menu_items`](../../game/ui/screens/planet_menu_items.py),
wired through [`fms_menu_callbacks`](../../game/ui/screens/fms_menu_callbacks.py)
and [`planet_context_menu`](../../game/ui/screens/planet_context_menu.py))
exposes the "Lay Mines" row when the facility ability gate passes and
the staging yard holds at least one mine.

## Ramming

`game/simulation/combat/ram_target_resolver.py::RamTargetResolver`
(symmetric universal model — QA 2026-05-16 Obs 1b):

- `set_ram_target(rammer, target)` — ungated by ability / component;
  any alive ship can be assigned a ram target. Stashes
  `ram_target` + `ram_target_id` on the rammer. Returns False only
  if either ship is dead or `rammer is target`.
- `process_ramming_tick(ships)` — for each ship with an assigned
  `ram_target`: collision-checks hull radii; on intersection, applies
  a **symmetric simultaneous damage exchange**:

      rammer_delivered = rammer.current_shields + rammer.hp +
                         sum(warhead.damage on rammer)
      target_delivered = target.current_shields + target.hp +
                         sum(warhead.damage on target)

  Both values sampled at collision instant; applied through
  `DamageCalculator.apply_damage` in parallel so the rammer's state
  going to zero does not reduce the damage it delivers. All warheads
  on both sides are consumed (one-shot, mirroring `consume_on_fire`
  on beam laserheads). The rammer's `ram_target` is cleared after
  collision so a survivor does not auto-re-collide on the next tick.

- If the target dies before collision, the rammer's `ram_target`
  clears and it reverts to default AI.

Survival is possible: a heavy ship with ample shields/HP ramming a
fighter eats little; a kamikaze fighter ramming a dreadnought is
annihilated but does big damage if it carries warheads. Kamikaze
behaviour comes from the AI controller calling `set_ram_target` on
spawn (see `FighterAIController.update`), not from a component on
the design.

Pre-2026-05-16 ramming was gated on a `RamTargetAbility` /
`ram_target_module` component and auto-destroyed the rammer; that
model was replaced after user feedback during the 2026-05-16 QA
session.

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
| `game/strategy/engine/order_handlers/lay_mines.py` | LAY_MINES order handler (operates on `IIssuerAdapter`) |
| `game/strategy/engine/handlers/lay_mines.py` | LayMines command handler |
| `game/strategy/engine/commands/__init__.py` | `IssueLayMinesCommand` (carries `planet_id`) |
| `game/strategy/engine/issuer_adapter.py` | `IIssuerAdapter` + `FleetShipIssuerAdapter` / `PlanetStagingYardIssuerAdapter` (Round 4 Obs B) |
| `game/ui/screens/planet_menu_items.py` | Planet right-click menu items (FMS rows) |
| `game/ui/screens/fms_menu_callbacks.py` | Shared FMS menu callbacks (Lay Mines / Launch * / Recover *) |
| `game/ui/screens/planet_context_menu.py` | Planet context-menu wiring |
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
