# PROJ-FMS-A Phase 5: Launch / recover ability skeletons + integration tests

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Register all six strategic/tactical launch abilities and two recovery abilities as **data-bearing skeleton classes** — they instantiate from component data, hold their config attributes, and pass design validation, but they do not execute anything yet. Strategic execution will be added later via `OrderType` + `BaseOrderHandler` subclasses (the pattern used by [`colonize.py`](../../../game/strategy/engine/order_handlers/colonize.py) and [`self_destruct.py`](../../../game/strategy/engine/order_handlers/self_destruct.py)). Tactical execution will be added later via battle-engine / weapon-firing-system hooks. **There is no `apply()` method on the `Ability` base class** — see [`base.py:59-227`](../../../game/simulation/components/abilities/base.py#L59) (the base exposes `update()`, `on_activation()`, `recalculate()`, and `sync_data()`, but no `apply()`). Strategic actions are not dispatched via ability methods; they are dispatched via Command → OrderType → Handler.

Then run a full integration test pass over Phases 1–4.

## Tasks

### Launch ability skeletons (six)
All in [`game/simulation/components/abilities/`](../../../game/simulation/components/abilities/), one new file per family or grouped under a `launch.py`. Each is a subclass of `Ability` overriding `layer` (class attribute) and `_parse_attrs()` to extract its config from component data. **No execution methods.** Execution wires into the actual game-loop / handler machinery in PROJ-FMS-B/C/D.

- [x] `StrategicMineLayerAbility` — `layer = AbilityLayer.STRATEGIC`. Data attrs: `capacity_per_action: int`, `cycle_time: float`. **Real behavior:** added via a new `OrderType.LAY_MINES` + `LayMinesOrderHandler` in PROJ-FMS-B Phase 1.
- [x] `StrategicFighterLaunchAbility` — `layer = AbilityLayer.STRATEGIC`. Same data attrs. **Real behavior:** added via new `OrderType.LAUNCH_FIGHTERS` + handler in PROJ-FMS-C Phase 1.
- [x] `StrategicSatelliteLaunchAbility` — same shape. **Real behavior:** PROJ-FMS-D Phase 1 (`OrderType.LAUNCH_SATELLITES` + handler).
- [x] `TacticalMineLayerAbility` — `layer = AbilityLayer.COMBAT`. **Real behavior:** PROJ-FMS-B **Phase 3** (tactical mine resolver hook into [`battle_engine.py`](../../../game/simulation/systems/battle_engine.py)). _(Was previously mis-cited as Phase 5.)_
- [x] `TacticalFighterLaunchAbility` — replaces the existing `VehicleLaunchAbility` at [`markers.py:9-61`](../../../game/simulation/components/abilities/markers.py#L9). For now, leave the existing class in place and register the new one alongside; the cut-over and behavior rewrite is **PROJ-FMS-C Phase 1** (rewriting the firing-system / attack-processor path at [`weapon_firing_system.py:130-140`](../../../game/simulation/combat/weapon_firing_system.py#L130) and [`attack_processor.py:68-97`](../../../game/simulation/systems/attack_processor.py#L68)).
- [x] `TacticalSatelliteLaunchAbility` — `layer = AbilityLayer.COMBAT`. **Real behavior:** PROJ-FMS-D Phase 1.

### Recovery ability skeletons (two)
- [x] `RecoverFightersAbility` — `layer = AbilityLayer.STRATEGIC`. Data attrs: `recovery_per_action: int`. **Real behavior:** PROJ-FMS-C Phase 3 (`OrderType.RECOVER_FIGHTERS` + handler).
- [x] `RecoverSatellitesAbility` — same shape. **Real behavior:** PROJ-FMS-D Phase 2.

### Registration
- [x] Register all eight ability classes in [`abilities/__init__.py`](../../../game/simulation/components/abilities/__init__.py).
- [x] Add at least one component definition per ability in [`data/components.json`](../../../data/components.json) so designs can include them — e.g., `mine_launcher_small`, `fighter_launch_bay_small`, `fighter_recovery_bay_small`. (Components for these abilities — what `SpaceShipyard` is to capital construction.) Tier sizes determine `capacity_per_action`.
- [x] Extend per-ship layer / classification rules in [`vehiclelayers.json`](../../../data/vehiclelayers.json) and each component's `allowed_vehicle_types` so the new components can be slotted on capital ships and planets.

### `OrderType` enum reservations (no behavior, just enum values)
- [x] Add new values to the `OrderType` enum in [`game/strategy/data/order_types.py`](../../../game/strategy/data/order_types.py) (or wherever the enum lives): `LAY_MINES`, `LAUNCH_FIGHTERS`, `LAUNCH_SATELLITES`, `RECOVER_FIGHTERS`, `RECOVER_SATELLITES`. No handlers yet — they're added in PROJ-FMS-B/C/D. Reserving the enum values now keeps later projects' diffs focused.

### Integration tests (Phases 1–4 rollup)
- [x] Design a mine in the workshop, including a `Warhead`, `Hull`, `SmallTargetingSensor`. Validates.
- [x] Design a fighter with `Warhead` + `RamTarget`. Validates.
- [x] Design a capital ship with `VehicleBayAbility` + `StrategicFighterLaunchAbility` + `RecoverFightersAbility` components. Validates.
- [x] Production: planet builds a fighter design → `staging_yard` gains a `CarriedVehicle` entry with the right `vehicle_type` and `current_hp = full`.
- [x] Production: fleet-yard ship builds the same design → fleet-level bay-selection rule (flagship-first, then canonical fleet order) places it correctly. Without any compatible bay in the fleet, build fails cleanly.
- [x] Transfer the fighter from planet staging to a ship's bay via the existing transfer order — design integrity preserved.
    - *Audit fix pass (2026-05-16):* the original Phase 5 integration test only exercised the cargo manager directly. A real end-to-end `TransferHandler` test with `cargo_type="vehicle"` (load and unload) was added to `tests/integration/test_fms_a_e2e.py::TestTransferHandlerVehicleE2E`. Required adding `"vehicle"` to `TransferValidator.VALID_CARGO_TYPES`.
- [x] Create a `Fleet` with `group_kind="fighter_group"` programmatically; verify Move / Intercept / Warp / Build command rejection.
- [x] Verify mine designs have boosted `total_defense_score` via `signature_bonus`.
- [x] Verify the eight skeleton ability classes instantiate cleanly from component data, expose their config attrs, and are discoverable via the ability-lookup machinery used in [`ability_manager.py:71-145`](../../../game/simulation/components/ability_manager.py#L71). (No `apply()` invariant — they hold data, not behavior.)

## Verification
- `python Tools/test_sharded/test_sharded.py` — full suite green.
- `python -m combat_lab.run_tests` — no combat regressions.
- Documentation updates: any new ability surfaces must be added to [`docs/systems/ability_reference.md`](../../../docs/systems/ability_reference.md) per the documentation-first convention.

## Exit criteria
- All eight launch/recovery skeleton ability classes registered and instantiable from data.
- Reserved `OrderType` enum values landed.
- Full integration of Phases 1–4 verified end-to-end through a workshop → build → transfer → bay storage round-trip.
- PROJ-FMS-A complete; PROJ-FMS-B can begin.

## Handoff to PROJ-FMS-B
The next project picks up by implementing the `OrderType.LAY_MINES` order handler, the warhead trigger math in a new `minefield_resolver.py`, the laserhead behavior, the tactical mine resolver hook, sensitivity UI, self-destruct UI, and the ram target ability. See [`../PROJ-FMS-B/plan.md`](../PROJ-FMS-B/plan.md).
