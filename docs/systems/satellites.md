# Satellites System

> **Last verified:** 2026-05-17 — PROJ-FMS-D end-to-end satellite
> system shipped (completing the Fighters / Mines / Satellites
> sequence); Round 4 QA pass re-architected the system:
> `satellite_bay_small/medium/large` consolidated to single
> `satellite_bay` scaled by `simple_size_mount`; `satellite_launch_bay`
> now collocates `RecoverSatellites`; tactical launch rewritten from
> count-per-cycle/cooldown to mass-tons/sec budget; planet-issued
> launch/recovery first-class via `IIssuerAdapter` (Pattern #40).

End-to-end satellite lifecycle: design → bay → strategic launch →
tactical combat (stationary AI) → strategic recovery, with mid-battle
launches that auto-reboard at battle end. Mirrors the fighter pipeline
with three deliberate differences: stationary tactical AI, separate
ability gates from fighters, and a distinct `satellite_group` fleet
namespace. Source design lives at
[`PROJ-FMS-shared/design.md`](../../Projects/active_projects/PROJ-FMS-shared/design.md);
this doc is the runtime reference.

## Quick lifecycle map

```text
Workshop / Build queue
        |
        v  (Satellite design as a CarriedVehicle in the carrier's bay)
ShipInstance.carried_items[*]  ← VehicleBayAbility caps total mass + allowed_types filter
        |
        v  IssueLaunchSatellitesCommand → OrderType.LAUNCH_SATELLITES
LaunchSatellitesCommandHandler
        | ability gate: carrier must mount StrategicSatelliteLaunchAbility
        v
LaunchSatellitesOrderHandler
        | pops N matching satellite CarriedVehicles, creates a
        | satellite_group Fleet (id namespace 300000+)
        v
satellite_group Fleet (group_kind="satellite_group")
        |  ships: List[ShipInstance]   ← real combat-capable entities
        |  HP preserved from CarriedVehicle.current_hp
        |
        v  contested-hex combat → build_strategy_battle_spec
spec compiler groups fleets by owner_id; satellite_group merges onto the
owner's team alongside any regular fleets (only mine_groups are filtered
out by `_split_mine_groups_from_fleets`).
        |
        v
BattleEngine ticks; SatelliteAIController forces zero throttle / zero
turn throttle but still acquires nearest enemy + pulls the trigger.
        |
        v  battle ends
Post-battle hook → fighter_reboard.apply_reboard(engine, fleets, empires)
        | (the module name pre-dates PROJ-FMS-D; the implementation is
        | now vehicle-type aware and handles both fighters AND satellites)
        | + apply_outcome_to_fleets prunes destroyed / retreated ships
        v
Mid-battle launches (tagged launched_in_battle_id) auto-reboard onto
friendly bays whose allowed_types accept the vehicle's type; overflow
spills into a new (or pre-existing) sector group of matching kind.
Pre-existing satellite_group satellites stay in their group unless
explicitly recovered.
        |
        v  IssueRecoverSatellitesCommand → OrderType.RECOVER_SATELLITES
RecoverSatellitesOrderHandler
        | pops N ShipInstances from the target satellite_group, converts
        | each back to a CarriedVehicle (HP + component states preserved),
        | loads into bay (allowed_types filter enforced)
        v
ShipInstance.carried_items[*]   ← back where we started.
```

## Differences from fighters

| Aspect | Fighters | Satellites |
|---|---|---|
| Tactical AI | `FighterAIController` — target nearest, turn, thrust, fire | `SatelliteAIController` — target nearest, fire; zero throttle / turn always |
| Ability gate | `StrategicFighterLaunch` / `RecoverFighters` | `StrategicSatelliteLaunch` / `RecoverSatellites` (cross-type isolation) |
| Bay accepts | `allowed_types` filter; fighter-only bays available | `allowed_types` filter; satellite-only bays available |
| Tactical launch | `BattleEngine.launch_fighters_in_battle` | `BattleEngine.launch_satellites_in_battle` |
| Carrier AI | `CarrierAIController._maybe_launch_fighter_wave()` → shared `_maybe_launch_wave("TacticalFighterLaunch", "fighter", "launch_fighters_in_battle")` | `CarrierAIController._maybe_launch_satellite_wave()` → same shared `_maybe_launch_wave("TacticalSatelliteLaunch", "satellite", "launch_satellites_in_battle")` |
| Launch bay collocates recovery | `fighter_launch_bay` carries `RecoverFighters` (Round 4 Obs C) | `satellite_launch_bay` carries `RecoverSatellites` (Round 4 Obs C) |
| Fleet group | `fighter_group` (id namespace 200000+) | `satellite_group` (id namespace 300000+) |
| Overflow into | `fighter_group` | `satellite_group` |

## Strategic launch (`OrderType.LAUNCH_SATELLITES`)

```python
IssueLaunchSatellitesCommand(
    fleet_id:            Optional[int] = None,
    ship_instance_id:    Optional[str] = None,
    satellite_design_id: str            = "auto",
    count:               Optional[int]  = None,   # None = launch ALL matching
    target_hex:          Optional[HexCoord] = None,
    planet_id:           Optional[int] = None,    # planet-issued alternative
)
```

Exactly one of `fleet_id` / `planet_id` is set (Round 4 Obs B). The
validator (`LaunchSatellitesCommandHandler`) rejects non-fleet
`group_kind` callers (for fleet-issued) and verifies the issuer holds
at least one matching satellite `CarriedVehicle` (or `count` matching
when count is positive). `satellite_design_id = "auto"` matches any
satellite-type CarriedVehicle.

`LaunchSatellitesOrderHandler.execute_action_order`:

1. Re-resolves the carrier and the requested count from the order
   payload.
2. Pops `count` matching CarriedVehicles from `carrier.carried_items`
   using the same vehicle-type filter (`cv.vehicle_type == "satellite"`).
3. Mints a fresh `satellite_group` Fleet at the target hex — same
   no-auto-merge policy PROJ-FMS-C uses for fighter_groups.
4. Materialises one `ShipInstance` per popped CarriedVehicle, preserving
   `current_hp` and `component_states`.

Same-hex launches do NOT auto-merge: each launch action produces its
own `satellite_group`. Players (or the AI) consolidate via the strategic
recover action.

## Tactical launch (mid-battle)

`BattleEngine.launch_satellites_in_battle(carrier, [CarriedVehicle, ...])`
is the explicit action surface. Production caller:
`CarrierAIController._maybe_launch_satellite_wave()`, a thin wrapper
that delegates to the shared helper `_maybe_launch_wave(ability_name,
vehicle_type, launch_method_name)`:

QA-C (Round 4): the entire tactical-launch path was rewritten from the
older count-per-cycle + cooldown model (which PROJ-FMS-D originally
shipped) to the mass-tons/sec budget below. The same shared helper now
serves both fighters and satellites, parameterised on ability name and
vehicle type.

The helper:

- Sums `launch_rate_tons_per_sec` across active
  `TacticalSatelliteLaunchAbility` components on the carrier and
  accumulates `rate * TICK_RATE` into a per-vehicle-type mass budget.
- Checks an enemy is in launch radius (cheap spatial-grid query).
- Pops carried satellite CarriedVehicles whose mass fits the residual
  budget, deducting each launch's mass.
- Calls the engine action surface, which spawns full design-backed
  satellites with components / weapons / HP and tags each with
  `launched_in_battle_id` for the end-of-battle reboard pipeline.

The budget accumulator is keyed by ability name; a carrier mounting
both bays launches each type independently as its respective budget
refills.

## Stationary tactical AI

`SatelliteAIController` (`game/ai/satellite_controller.py`) is the
production controller for satellites:

- Factory dispatch: `AIControllerFactory.create_for_ship` returns a
  `SatelliteAIController` when `ship.vehicle_type == "Satellite"`.
- Per-tick: forces `set_throttle(0.0)` and `set_turn_throttle(0.0)`;
  acquires the nearest live enemy from the spatial grid; calls
  `set_current_target(target)` and `set_trigger_pulled(True)` so the
  weapon firing system runs through its normal range / cooldown gates.
- No formation, no avoidance, no behaviour-tree retreat, no ram-target
  handling. Satellites are pure defensive emplacements.

The base `AIController` (in `game/ai/controller.py:361-363`) already
short-circuits behaviour execution for `Satellite`-typed ships; the
dedicated controller exists so the satellite never accidentally
inherits a non-zero throttle from a prior controller swap.

## Strategic recovery (`OrderType.RECOVER_SATELLITES`)

```python
IssueRecoverSatellitesCommand(
    fleet_id:            Optional[int] = None,
    ship_instance_id:    Optional[str] = None,
    satellite_group_id:  Optional[int] = None,
    count:               Optional[int] = None,   # None = recover ALL (capped by capacity)
    planet_id:           Optional[int] = None,   # planet-issued alternative
)
```

Exactly one of `fleet_id` / `planet_id` is set (Round 4 Obs B).

`RecoverSatellitesOrderHandler.execute_action_order`:

1. Locates the target `satellite_group` (specific id, or first owner-
   owned group at the recovering fleet's hex).
2. For each ship up to `count` (or all when `None`): converts to
   `CarriedVehicle` (HP + per-component damage preserved), calls
   `carrier._cargo_mgr.load_vehicle(cv)`. Partial recovery is allowed
   when bay capacity / type filter runs out.
3. Removes recovered ships from the group; prunes the source group from
   `empire.fleets` if empty.

The ability-gate test pins that a carrier with only
`RecoverFightersAbility` cannot recover satellites — the static
`ORDER_TO_ABILITY_MAP` lookup gates the order at action-time
resolution, and the bay-side `allowed_types` filter rejects satellites
into a fighter-only bay even if the order somehow slipped through.

## Planet-issued launch / recovery (QA Observation B / Pattern #40)

A planetary-complex facility component exposing
`StrategicSatelliteLaunch` lets a planet issue
`IssueLaunchSatellitesCommand(planet_id=...)`; the same
`LaunchSatellitesOrderHandler.execute_for_issuer` method ticks via
`PlanetStagingYardIssuerAdapter`, popping satellites from the planet's
`staging_yard` and spawning a `satellite_group` at the planet's hex.
`ActionExecutionEngine` was widened in Round 4 to tick BOTH
`fleet.orders` and `planet.orders` so the same handler executes for
either issuer kind; planet-side capability gates check the facility
for the required ability before accepting the order. Recovery mirrors
it: a facility with `RecoverSatellites` issues
`IssueRecoverSatellitesCommand(planet_id=...)`; recovered satellites
re-stage to `staging_yard` (capacity-checked by `max_staging_mass`). The
planet right-click menu
([`planet_menu_items.build_menu_items`](../../game/ui/screens/planet_menu_items.py),
wired through [`fms_menu_callbacks`](../../game/ui/screens/fms_menu_callbacks.py))
exposes both rows when capability gates pass.

## End-of-battle reboard

`fighter_reboard.apply_reboard` (file name retained from PROJ-FMS-C;
the contents are vehicle-type aware as of PROJ-FMS-D Phase 2) walks
`engine.reboard_tracker.launched_ships`. For each survivor:

- Reads the Sim Ship's `vehicle_type` -> classifies the CarriedVehicle
  as `"fighter"` or `"satellite"`.
- Attempts to load into any friendly carrier's bay (each `load_vehicle`
  call honours that bay's `allowed_types`).
- On overflow, mints / merges into a sector group of matching kind:
  satellite overflow -> `satellite_group`, fighter overflow ->
  `fighter_group`.

Pre-existing satellite_group satellites that participated stay in the
group unless explicitly recovered via the strategic action.

## File map

### Production code

- `game/strategy/engine/commands/__init__.py` — `IssueLaunchSatellitesCommand`,
  `IssueRecoverSatellitesCommand` DTOs (both carry `planet_id`).
- `game/strategy/engine/issuer_adapter.py` — `IIssuerAdapter`,
  `FleetShipIssuerAdapter`, `PlanetStagingYardIssuerAdapter` (shared
  with all five FMS order handlers).
- `game/ui/screens/planet_menu_items.py`, `fms_menu_callbacks.py`,
  `planet_context_menu.py` — planet right-click menu wiring.
- `game/strategy/engine/handlers/launch_satellites.py` —
  `LaunchSatellitesCommandHandler`.
- `game/strategy/engine/handlers/recover_satellites.py` —
  `RecoverSatellitesCommandHandler`.
- `game/strategy/engine/order_handlers/launch_satellites.py` —
  `LaunchSatellitesOrderHandler`.
- `game/strategy/engine/order_handlers/recover_satellites.py` —
  `RecoverSatellitesOrderHandler`.
- `game/strategy/engine/order_handlers/registry_factory.py` — registers
  both handlers.
- `game/strategy/data/order_types.py` — `LAUNCH_SATELLITES` and
  `RECOVER_SATELLITES` in `ACTION_ORDER_TYPES`.
- `game/simulation/systems/battle_engine.py` —
  `BattleEngine.launch_satellites_in_battle`.
- `game/simulation/systems/fighter_reboard.py` — generalised
  vehicle-type aware reboard (handles fighters and satellites in one
  hook).
- `game/ai/satellite_controller.py` — `SatelliteAIController`.
- `game/ai/carrier_controller.py` — per-type wrappers
  `_maybe_launch_fighter_wave()` / `_maybe_launch_satellite_wave()`
  delegate to the shared `_maybe_launch_wave(ability_name,
  vehicle_type, launch_method_name)` helper, rewritten in Round 4 to a
  per-tick mass-tons/sec budget (replacing the original count-per-cycle
  + cooldown model).
- `game/ai/ai_factory.py` — factory dispatches `Satellite`-typed ships
  to `SatelliteAIController`; carriers with either `TacticalFighterLaunch`
  OR `TacticalSatelliteLaunch` get the `CarrierAIController`.
- `game/simulation/entities/stat_contributors/launch.py` —
  `contribute_tactical_satellite_launch` writes to
  `ship.satellite_launch_rate_tons_per_sec` /
  `ship.satellite_capacity` (Round 4 renamed `satellites_per_wave` /
  `satellite_launch_cycle` to the single `*_launch_rate_tons_per_sec`
  field; the cycle-based cooldown stat is gone).
- `game/simulation/entities/stat_contributors/registry.py` — seeded as
  `TacticalSatelliteLaunch` -> `contribute_tactical_satellite_launch`.
- `game/simulation/entities/ship_stats.py` — resets the satellite
  stat fields (`satellite_launch_rate_tons_per_sec`,
  `satellite_capacity`) each recalculation.
- `game/strategy/data/design_role.py` — `_CARRIER_ABILITIES` extended
  to include the satellite launch abilities.
- `data/components.json` — ships the consolidated `fighter_bay`,
  `satellite_bay`, `mine_bay`, and universal `vehicle_bay` typed-bay
  components. QA-C: capacity scales through `simple_size_mount` rather
  than separate `_small / _medium / _large` tiers.

### Tests

- `tests/unit/strategy/engine/order_handlers/test_launch_satellites_handler.py`
- `tests/unit/strategy/engine/order_handlers/test_recover_satellites_handler.py`
- `tests/unit/simulation/components/abilities/test_tactical_satellite_launch.py`
- `tests/unit/ai/test_satellite_controller.py`
- `tests/unit/strategy/combat/test_satellite_group_combat_join.py`
- `tests/unit/simulation/systems/test_satellite_reboard.py`
- `tests/integration/test_fms_d_e2e.py`
- `tests/integration/test_fms_d_launch_in_battle_e2e.py`
- `tests/integration/test_fms_cd_isolation.py`

## Pre-PROJ-FMS-D state

Before this project, the satellite ability skeletons were registered
(PROJ-FMS-A Phase 5) but had no behaviour. `OrderType.LAUNCH_SATELLITES`
and `OrderType.RECOVER_SATELLITES` were in the reserved-no-command-yet
set. There was no satellite combat AI variant separate from the base
`AIController`'s line-361 short-circuit. PROJ-FMS-D wires every layer:
command + handler + order handler + tactical action surface + AI
controller + stat aggregation + reboard generalisation + tests.
