# PROJ-FMS-C Phase 1: Strategic + tactical fighter launch (design-instance based)

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Player can strategically launch fighters from a ship's bay into the hex (creating a `fighter_group`) or tactically deploy them onto a battle map (using actual carried design instances, not class-string shells).

## Tasks

### Strategic fighter-launch execution (Command → OrderType → Handler)

Strategic actions flow through Command classes (in `handlers/`) that issue an `Order` (with a typed `OrderType`); the order is later executed by an `OrderHandler` subclass in `order_handlers/`. See [`colonize.py`](../../../game/strategy/engine/order_handlers/colonize.py) for the canonical pattern. There is **no `apply()` method on `Ability`** — see [`base.py:59-227`](../../../game/simulation/components/abilities/base.py#L59).

- [ ] `OrderType.LAUNCH_FIGHTERS` reserved by PROJ-FMS-A Phase 5. Verify.
- [ ] New `IssueLaunchFightersCommand` + handler in [`game/strategy/engine/handlers/`](../../../game/strategy/engine/handlers/). Inputs: launching `fleet_id`, `ship_instance_id`, count, fighter `design_id` (or `"auto"` = pick from bay).
- [ ] New `LaunchFightersOrderHandler(BaseOrderHandler)` in [`game/strategy/engine/order_handlers/launch_fighters.py`](../../../game/strategy/engine/order_handlers/). `supported_order_types = (OrderType.LAUNCH_FIGHTERS,)`. `execute_action_order()`:
  - Pop N matching `CarriedVehicle`s from the issuing ship's `VehicleBay`.
  - Locate or create a `fighter_group` Fleet for the owner at the current hex.
  - Append the fighters to the group's ships (each `CarriedVehicle` converted to a `ShipInstance`-like representation living in the group).
- [ ] Multiple `fighter_group`s per owner per hex allowed; no auto-merge.
- [ ] Mixed-design groups supported — fighters of different designs can sit in the same group.
- [ ] HP from `CarriedVehicle.current_hp` carries over to the deployed wing's per-fighter state.

### Tactical fighter-launch execution (replace existing firing-system path)

The existing tactical fighter launch lives in the weapon-firing-system per-tick scan at [`weapon_firing_system.py:130-140`](../../../game/simulation/combat/weapon_firing_system.py#L130), which currently emits a generic `fighter_class` string (a class-shell, not a real design instance) handled at [`attack_processor.py:68-97`](../../../game/simulation/systems/attack_processor.py#L68).

- [ ] Replace that path: instead of `current_target`-triggered auto-launch, gate launch on a player/AI-committed battle action.
- [ ] Inputs to the battle action: launching `Ship`, count, fighter `design_id`, optional target position.
- [ ] Pop N `CarriedVehicle`s from the launching ship's `VehicleBay`; spawn them as real combat entities on the tactical map using their actual design data (full component layout, weapons, HP per design).
- [ ] **Tag each launched fighter** with `launched_in_battle_id` so the end-of-battle reboard hook (Phase 3) knows which ones are eligible for auto-recovery.

### Rewrite the existing launch path
- [ ] Update [`game/simulation/systems/attack_processor.py:68-97`](../../../game/simulation/systems/attack_processor.py#L68) to accept a design-instance payload, not a class-string. The attack payload from a tactical launch now carries the `CarriedVehicle` data + tagging.
- [ ] Verify spawning preserves all design components, abilities, HP — equivalent to a freshly-built ship with full stats but with possibly-reduced HP from prior wear.
- [ ] Backwards-compatibility shim: if PROJ-FMS-A left the old `VehicleLaunchAbility` in place, leave its code as-is (no callers will hit it once existing designs migrate); add a deprecation log warning on use. Plan to remove fully in a follow-up housekeeping pass once no designs reference it.

### Stat aggregator
- [ ] Update [`game/simulation/entities/stat_contributors/launch.py:29-61`](../../../game/simulation/entities/stat_contributors/launch.py#L29) to read from the new tactical launch ability shape. Aggregate per-ship `fighter_launch_capacity`, `fighter_launch_cycle`, etc. from `TacticalFighterLaunchAbility` instances.

### Tests
- [ ] Strategic: load 6 fighters into a carrier's bay (mixed designs allowed), launch 4 into the current hex → `fighter_group` appears with 4 entries, carrier's bay now has 2.
- [ ] Cannot launch more than bay-resident count.
- [ ] Tactical: in-battle launch of 2 fighters → 2 entities on the tactical map with full design components / weapons / HP; each tagged with `launched_in_battle_id`.
- [ ] Old `VehicleLaunchAbility` (if retained for compat) logs a deprecation warning when invoked.
- [ ] HP from `CarriedVehicle.current_hp` carries through the strategic→tactical→battle path.

## Verification
- `python Tools/test_sharded/test_sharded.py`
- `pytest tests/unit/simulation/combat/test_attack_processor.py` — confirm new payload path works, old class-string path either dead or warns.
- Manual: load carrier with fighters via dev console, launch into hex, observe `fighter_group` on map.

## Exit criteria
- Both launch abilities work end-to-end.
- Existing class-string launch path replaced (or warning-flagged for removal).
- HP persists from bay → tactical instance.
