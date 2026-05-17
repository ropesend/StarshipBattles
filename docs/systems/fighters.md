# Fighters System

> **Last verified:** 2026-05-17 - PROJ-FMS-C end-to-end fighter system
> shipped; Round 4 QA pass re-architected the system: components were
> consolidated (`fighter_launch_bay`, `fighter_bay`, `vehicle_bay`;
> recovery collocated on launch bays), tactical launch was rewritten
> from count-per-cycle/cooldown to a per-tick mass-tons/sec budget,
> and planet-issued launches/recoveries became first-class via the
> polymorphic `IIssuerAdapter` seam (see Pattern #40).

End-to-end fighter lifecycle: design → bay → strategic launch → tactical
combat → strategic recovery, with mid-battle launches that auto-reboard
at battle end. Source design lives at
[`PROJ-FMS-shared/design.md`](../../Projects/active_projects/PROJ-FMS-shared/design.md);
this doc is the runtime reference.

## Component model (Round 4)

Round 4 Obs C consolidated the fighter-related components from per-size
variants (`fighter_launch_bay_small`, `fighter_bay_small`,
`vehicle_bay_small/medium/large`) to single shipped IDs whose capacity
and launch rate scale through the `simple_size_mount` modifier:

- `fighter_launch_bay` — carries BOTH `StrategicFighterLaunch` /
  `TacticalFighterLaunch` AND `RecoverFighters` (launch and recovery
  collocated; the standalone `fighter_recovery_bay_small` was deleted).
- `fighter_bay` — fighter-typed storage (`allowed_types=["fighter"]`).
- `vehicle_bay` — universal storage
  (`allowed_types=["mine","fighter","satellite"]`).

The `simple_size_mount` modifier dials per-component:

- `launch_rate_mult` — scales `launch_rate_tons_per_sec` on
  `TacticalFighterLaunch`.
- `recovery_rate_mult` — scales recovery throughput on `RecoverFighters`.
- `bay_capacity_mult` — scales `capacity_mass` on `VehicleBay`.

## Quick lifecycle map

```text
Workshop / Build queue
        |
        v  (Fighter design as a CarriedVehicle in the carrier's bay)
ShipInstance.carried_items[*]  ← VehicleBayAbility caps total mass
        |
        v  IssueLaunchFightersCommand → OrderType.LAUNCH_FIGHTERS
LaunchFightersOrderHandler
        | pops N matching CarriedVehicles, creates a fighter_group Fleet
        v
fighter_group Fleet (group_kind="fighter_group")
        |  ships: List[ShipInstance]   ← real combat-capable entities
        |  HP preserved from CarriedVehicle.current_hp
        |
        v  contested-hex combat → build_strategy_battle_spec
spec compiler groups fleets by owner_id; fighter_group merges onto the
owner's team alongside any regular fleets.
        |
        v
BattleEngine ticks; FighterAIController drives each fighter ("target
nearest enemy"); kamikaze fighters (set via
BattleEngine.set_ram_target on spawn) defer to the engine's
RamTargetResolver for the symmetric collision exchange.
        |
        v  battle ends
Post-battle hook → fighter_reboard.apply_reboard(engine, fleets, empires)
        | + apply_outcome_to_fleets prunes destroyed/retreated ships
        v
Mid-battle launches (tagged launched_in_battle_id) auto-reboard onto
friendly bays; overflow spills into a new (or pre-existing) sector
fighter_group. Pre-existing fighter_group fighters stay in their
group unless explicitly recovered.
        |
        v  IssueRecoverFightersCommand → OrderType.RECOVER_FIGHTERS
RecoverFightersOrderHandler
        | pops N ShipInstances from the target fighter_group, converts
        | each back to a CarriedVehicle (HP preserved), loads into bay
        v
ShipInstance.carried_items[*]   ← back where we started.
```

## Strategic launch (`OrderType.LAUNCH_FIGHTERS`)

```python
IssueLaunchFightersCommand(
    fleet_id:          Optional[int] = None,
    ship_instance_id:  Optional[str] = None,
    fighter_design_id: str            = "auto",
    count:             Optional[int]  = None,   # None = launch ALL matching
    target_hex:        Optional[HexCoord] = None,
    planet_id:         Optional[int] = None,    # planet-issued alternative
)
```

Exactly one of `fleet_id` / `planet_id` is set (Round 4 Obs B); planet-
issued launches operate against the planet's staging yard via
`PlanetStagingYardIssuerAdapter` instead of a carrier ship. The
validator (`LaunchFightersCommandHandler`) rejects non-fleet
`group_kind` callers (for fleet-issued) and verifies the issuer holds
at least `count` matching fighter `CarriedVehicle`s (or ≥1 when
`count is None`).

`LaunchFightersOrderHandler.execute_action_order` operates on an
`IIssuerAdapter` (see Pattern #40):

1. Pops the matching `CarriedVehicle`s via `adapter.pop_carried(...)`
   (atomic — partial pops are restored on failure). For a fleet ship
   the adapter drains `ship.carried_items`; for a planet it drains
   `planet.staging_yard`.
2. Mints a fresh `fighter_group` Fleet at `adapter.location` (no
   auto-merge — mirrors PROJ-FMS-B audit Fix 4 for mine_groups).
3. Builds a deployed `ShipInstance` per CarriedVehicle, preserving
   `current_hp` and `component_states` when present.
4. Adds the group to `empire.fleets`. Conflict-resolution picks it up
   automatically via the existing `empire.fleets` iteration.

Files: [`game/strategy/engine/handlers/launch_fighters.py`](../../game/strategy/engine/handlers/launch_fighters.py),
[`game/strategy/engine/order_handlers/launch_fighters.py`](../../game/strategy/engine/order_handlers/launch_fighters.py),
[`game/strategy/engine/issuer_adapter.py`](../../game/strategy/engine/issuer_adapter.py).

## Tactical launch (mid-battle, design-instance)

The legacy `VehicleLaunchAbility` auto-launch path was removed in
PROJ-FMS-C audit Fix 1. The shipped production path is design-instance
only: `BattleEngine.launch_fighters_in_battle(carrier, [CarriedVehicle, ...])`
drives the spawn via `ShipSerializer.from_dict`, and
[`attack_processor.process_launch_attack`](../../game/simulation/systems/attack_processor.py)
now requires a `carried_vehicle` payload — legacy class-string payloads
without `carried_vehicle` are logged and skipped (no generic-fighter
fallback). The carrier-side decision of *when* to launch is owned by
[`CarrierAIController`](../../game/ai/carrier_controller.py), wired through
`AIControllerFactory.create_for_ship` and the spec compiler's
`pre_tick_loop_callback`. Recovery is now collocated on
`fighter_launch_bay` (the standalone `fighter_recovery_bay_small` was
deleted in Round 4 Obs C).

Round 4 rewrote the controller from a count-per-cycle + cooldown model
to a per-tick mass-tons/sec budget. The per-type wrapper
`CarrierAIController._maybe_launch_fighter_wave()` (in
[`game/ai/carrier_controller.py`](../../game/ai/carrier_controller.py))
delegates to the shared
`_maybe_launch_wave(ability_name, vehicle_type, launch_method_name)`
helper, which sums `launch_rate_tons_per_sec` across active
`TacticalFighterLaunchAbility` components on the carrier, accumulates
`rate * TICK_RATE` into a per-vehicle-type mass budget, and pops
carried fighter `CarriedVehicle`s whose mass fits the residual budget
— deducting each launch's mass from the accumulator. Variable-mass
fighters launched from the same bay therefore launch at variable
counts as the budget refills, with no cycle gate.

`BattleEngine.launch_fighters_in_battle` spawns each fighter, tags it with
`launched_in_battle_id`, and registers it on the engine's `ReboardTracker`
for end-of-battle reboard.

## Combat join via `group_kind`

`fighter_group` Fleets are real combat fleets — unlike `mine_group`s
they ARE combat-capable entities and translate to `ShipSpec` entries on
the owner's team in `build_strategy_battle_spec` /
`build_strategy_battle_assembly`. The strategy assembler's
`TeamSpecBuilder.split_mine_groups` only filters mine groups; fighter_groups
fall through to the normal `fleets_by_owner` grouping.

Each `ShipInstance` in the fighter_group becomes a tactical entity
through the standard materialiser pipeline
(`InstanceBackedMaterializer` calls `ShipInstance.to_ship(...)`).

## Fighter AI

`FighterAIController` (in [`game/ai/fighter_controller.py`](../../game/ai/fighter_controller.py))
implements the minimal "target nearest enemy" behavior:

1. Find the closest live enemy via the spatial grid (bypasses the policy
   weighting in `AIController.find_target` — fighters always want the
   nearest threat).
2. Set it as the current target so the weapon firing system fires.
3. Turn toward it and thrust forward via `AIController.navigate_to`.
4. When `ship.ram_target` is set (kamikaze flow — see Obs 1b: ramming
   is now a universal tactical action set by
   `BattleEngine.set_ram_target`, no component gate), defer movement
   to the engine's `RamTargetResolver`; still pull the trigger so any
   non-ram weapons fire on the ram target en-route.

`AIControllerFactory.create_for_ship` dispatches based on
`ship.vehicle_type`: `Fighter` gets `FighterAIController`; everything
else gets the full `AIController`.

## Strategic recovery (`OrderType.RECOVER_FIGHTERS`)

```python
IssueRecoverFightersCommand(
    fleet_id:          Optional[int] = None,
    ship_instance_id:  Optional[str] = None,
    fighter_group_id:  Optional[int] = None,
    count:             Optional[int] = None,   # None = recover ALL (capped by capacity)
    planet_id:         Optional[int] = None,   # planet-issued alternative
)
```

Exactly one of `fleet_id` / `planet_id` is set (Round 4 Obs B). The
handler:

1. Locates the source `fighter_group` (by id, or first owner-owned
   group at the recovering fleet's hex).
2. Pops up to `count` ShipInstances (or all when `count is None`).
3. Converts each into a CarriedVehicle preserving `current_hp` and
   per-component damage state.
4. Loads each into the carrier's bay via `ShipCargoManager.load_vehicle`.
   Partial recovery is allowed — fighters that don't fit stay in the
   group.
5. If the source group ends up empty, removes it from `empire.fleets`.

Files: [`game/strategy/engine/handlers/recover_fighters.py`](../../game/strategy/engine/handlers/recover_fighters.py),
[`game/strategy/engine/order_handlers/recover_fighters.py`](../../game/strategy/engine/order_handlers/recover_fighters.py).

## Planet-issued launch / recovery (QA Observation B / Pattern #40)

Both launch and recovery are polymorphic across fleet ships AND planetary
complex facilities via the `IIssuerAdapter` seam (Pattern #40 in
`docs/02_PATTERNS.md`). A planet whose facility component exposes
`StrategicFighterLaunch` can issue `IssueLaunchFightersCommand(planet_id=...)`
(no `ship_instance_id`); the same `LaunchFightersOrderHandler.execute_for_issuer`
method ticks the order through `PlanetStagingYardIssuerAdapter`, popping
fighters from the planet's `staging_yard` and producing a `fighter_group`
at the planet's hex. `ActionExecutionEngine` was widened in Round 4 to
tick BOTH `fleet.orders` and `planet.orders` so the same handler
executes for either issuer kind. Planet-side capability gates check the
facility's components for the required `StrategicFighterLaunch` /
`RecoverFighters` ability before the order is accepted. Recovery
mirrors that: a facility with `RecoverFighters` issues
`IssueRecoverFightersCommand(planet_id=...)`, drains the matching
`fighter_group` at the hex, and re-stages recovered fighters back into
the planet's `staging_yard` (capacity-checked by `max_staging_mass`). The
right-click planet menu (built by
[`planet_menu_items.build_menu_items`](../../game/ui/screens/planet_menu_items.py),
wired through [`fms_menu_callbacks`](../../game/ui/screens/fms_menu_callbacks.py)
and [`planet_context_menu`](../../game/ui/screens/planet_context_menu.py))
exposes both rows when capability gates pass.

## End-of-battle reboard

The strategy-side post-battle hook in
[`spec_compiler.py`](../../game/strategy/combat/spec_compiler.py)
runs `fighter_reboard.apply_reboard(...)` BEFORE
`apply_outcome_to_fleets` so reboarded fighters land on friendly bays
before the regular ship-outcome processing prunes empty fleets.

Policy:

- **Survivors tagged `launched_in_battle_id == this_battle_id`** auto-
  reboard onto any friendly ship in the battle that has bay space.
  Walks the participating fleets in order (carrier's home fleet first).
- **Overflow** spills into a new `fighter_group` Fleet at the sector.
  If a pre-existing fighter_group at that hex already belongs to the
  same empire, overflow MERGES into it rather than fragmenting.
- **Dead-on-arrival** fighters (HP <= 0 or `is_alive == False` at battle
  end) are discarded.
- **Carrier destroyed mid-battle** is handled implicitly — the destroyed
  carrier is skipped in the friendly-ship walk; the reboard finds the
  next live carrier or falls through to overflow.

Wiring:

- [`fighter_reboard.ReboardTracker`](../../game/simulation/systems/fighter_reboard.py)
  installed on the engine via the spec compiler's
  `build_fighter_reboard_setup` pre_tick_loop_callback.
- [`attack_processor.process_launch_attack`](../../game/simulation/systems/attack_processor.py)
  appends each spawned fighter to the tracker.
- The post-battle hook built by `PostBattleHookBuilder` reads the
  engine via the shared `engine_ref` mutable one-slot list on
  `StrategyBattleAssembly.extensions` (PROJ-426 typed sidecar; was
  formerly an `object.__setattr__(spec, "_engine_ref", ...)` side-channel)
  and calls `apply_reboard`.
- `PreTickBattleSetupRegistry` composes `mine_setup` and `reboard_setup`
  into the single `pre_tick_loop_callback` passed to `run_battle`.

## Tests

| Layer | File |
|---|---|
| Strategic launch handler unit | `tests/unit/strategy/engine/order_handlers/test_launch_fighters_handler.py` |
| Strategic recovery handler unit | `tests/unit/strategy/engine/order_handlers/test_recover_fighters_handler.py` |
| Tactical launch (design-instance) unit | `tests/unit/simulation/components/abilities/test_tactical_fighter_launch.py` |
| Fighter AI controller unit | `tests/unit/ai/test_fighter_controller.py` |
| Spec-compiler / combat-join unit | `tests/unit/strategy/combat/test_fighter_group_combat_join.py` |
| End-of-battle reboard unit | `tests/unit/simulation/systems/test_fighter_reboard.py` |
| Strategic launch → recover round-trip | `tests/integration/test_fms_c_e2e.py` |
| Mid-battle launch + reboard + overflow | `tests/integration/test_fms_c_launch_in_battle_e2e.py` |

## Decisions captured

See [`Projects/active_projects/PROJ-FMS-C/decisions.md`](../../Projects/active_projects/PROJ-FMS-C/decisions.md)
for the per-phase implementation decisions (no-auto-merge,
overflow-merge-into-existing-group policy, fighter AI scope, etc.).
