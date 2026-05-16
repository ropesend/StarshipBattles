# Satellites System

> **Last verified:** 2026-05-16 — PROJ-FMS-D end-to-end satellite system
> shipped. Satellites are the third PROJ-FMS unit type, completing the
> Fighters / Mines / Satellites sequence.

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
| Carrier AI | `CarrierAIController._maybe_launch_fighter_wave` | `CarrierAIController._maybe_launch_satellite_wave` (same controller, separate ability lookup) |
| Fleet group | `fighter_group` (id namespace 200000+) | `satellite_group` (id namespace 300000+) |
| Overflow into | `fighter_group` | `satellite_group` |

## Strategic launch (`OrderType.LAUNCH_SATELLITES`)

`IssueLaunchSatellitesCommand(fleet_id, ship_instance_id,
satellite_design_id, count, target_hex)` queues a `LAUNCH_SATELLITES`
order on the issuing fleet. The validator
(`LaunchSatellitesCommandHandler`) rejects non-fleet `group_kind`
callers and verifies the carrier has at least `count` matching satellite
`CarriedVehicle`s. `satellite_design_id = "auto"` matches any
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
`CarrierAIController._maybe_launch_satellite_wave`, which:

- Walks the carrier's components for `TacticalSatelliteLaunchAbility`.
- Checks an enemy is in launch radius (cheap spatial-grid query).
- Pops up to `capacity_per_action` satellite CarriedVehicles.
- Calls the engine action surface, which spawns full design-backed
  satellites with components / weapons / HP and tags each with
  `launched_in_battle_id` for the end-of-battle reboard pipeline.

The same per-tick cooldown gates both fighter and satellite waves, so a
carrier mounting both ability sets alternates by exhausting one wave's
cooldown before launching the other.

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

`IssueRecoverSatellitesCommand(fleet_id, ship_instance_id,
satellite_group_id, count)` queues a `RECOVER_SATELLITES` order.

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
  `IssueRecoverSatellitesCommand` DTOs.
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
- `game/ai/carrier_controller.py` — extended with
  `_maybe_launch_satellite_wave` + shared `_maybe_launch_wave` helper.
- `game/ai/ai_factory.py` — factory dispatches `Satellite`-typed ships
  to `SatelliteAIController`; carriers with either `TacticalFighterLaunch`
  OR `TacticalSatelliteLaunch` get the `CarrierAIController`.
- `game/simulation/entities/stat_contributors/launch.py` —
  `contribute_tactical_satellite_launch` writes to
  `ship.satellites_per_wave` / `ship.satellite_launch_cycle` /
  `ship.satellite_capacity`.
- `game/simulation/entities/stat_contributors/registry.py` — seeded as
  `TacticalSatelliteLaunch` -> `contribute_tactical_satellite_launch`.
- `game/simulation/entities/ship_stats.py` — resets the three satellite
  stat fields each recalculation.
- `game/strategy/data/design_role.py` — `_CARRIER_ABILITIES` extended
  to include the satellite launch abilities.
- `data/components.json` — adds `fighter_bay_small`, `satellite_bay_small`
  / `_medium` / `_large` typed-bay components alongside the universal
  `vehicle_bay_*` entries (already shipped pre-FMS-D).

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
