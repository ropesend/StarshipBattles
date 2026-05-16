# PROJ-FMS-C Phase 3: Recovery + end-of-battle reboard

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Surviving fighters can return to bay storage — explicitly via a strategic empire action, automatically at end-of-battle for fighters launched during that battle, with overflow becoming a new sector group.

## Tasks

### Strategic fighter recovery (Command → OrderType → Handler)

- [ ] `OrderType.RECOVER_FIGHTERS` reserved by PROJ-FMS-A Phase 5. Verify.
- [ ] New `IssueRecoverFightersCommand` + handler in [`game/strategy/engine/handlers/`](../../../game/strategy/engine/handlers/). Inputs: recovering `fleet_id`, `ship_instance_id`, target `fighter_group_id` (or "any in current hex"), count (or "all").
- [ ] New `RecoverFightersOrderHandler(BaseOrderHandler)` in [`game/strategy/engine/order_handlers/recover_fighters.py`](../../../game/strategy/engine/order_handlers/). `supported_order_types = (OrderType.RECOVER_FIGHTERS,)`. `execute_action_order()`:
  - Pop N `ShipInstance`-style fighters from the target group.
  - Convert each back to a `CarriedVehicle` with `current_hp` from the deployed instance.
  - Load into the recovering ship's `VehicleBay` (fail per-fighter if bay capacity exceeded, partial recovery allowed).
- [ ] If `fighter_group` reduced to zero ships, remove it from the empire's fleets.
- [ ] HP / damage state preserved through the round trip.

### End-of-battle reboard
- [ ] Hook at battle shutdown in [`game/simulation/systems/battle_engine.py`](../../../game/simulation/systems/battle_engine.py) (look near the existing battle-end / cleanup path).
- [ ] For each surviving fighter on the owner's side:
  - If `launched_in_battle_id == this_battle_id` (i.e., launched during this battle): try to reboard onto any friendly ship in the battle that has bay space. Pop into the ship's `VehicleBay` as a `CarriedVehicle` with current HP.
  - If no friendly ship has bay space: spill into a new `fighter_group` Fleet in the sector (or append to an existing pre-existing `fighter_group` if one is in the hex — design choice, document in [`decisions.md`](decisions.md)).
  - If `launched_in_battle_id` is NOT set (i.e., came from a pre-existing `fighter_group` in the hex): do NOT auto-reboard; the fighter remains in its original group (or a new one if its original was destroyed; lean: stay in original group).
- [ ] Pre-existing groups whose fighters all survive stay in the sector unchanged.

### Edge cases
- [ ] Carrier destroyed mid-battle but its fighters survive: those fighters CANNOT reboard onto the destroyed carrier; they look for any other friendly ship with bay space; if none, overflow to sector group. Surfacing this in events log is important.
- [ ] Fighter at 0 HP at battle end (just-barely dead): destroyed, not recovered. Same as any combat unit.
- [ ] Fighter with damage but > 0 HP: recovered with the damage state preserved.

### Tests
- [ ] Strategic recovery: pre-existing `fighter_group` of 5 in hex, carrier with `RecoverFightersAbility` and 6 bay slots in same hex, recover 5 → carrier bay has 5 (`CarriedVehicle`s with correct HP); group destroyed.
- [ ] Partial recovery: bay has only 3 slots, recover 5 → carrier gets 3, group has 2 remaining.
- [ ] HP preserved: damage a fighter in a pre-test battle, recover, inspect `CarriedVehicle.current_hp`.
- [ ] End-of-battle reboard: launch 4 from a carrier in battle, 3 survive → all 3 reboard onto carrier (bay has 3 entries).
- [ ] Overflow: launch 4, 4 survive, carrier bay only has 2 free slots → 2 reboard, 2 overflow into new `fighter_group` in the sector.
- [ ] Pre-existing group fighters that participate but don't get launched during *this* battle do NOT auto-reboard.
- [ ] Carrier destroyed mid-battle, its fighters survive → fighters look for other friendly carriers; otherwise overflow.

## Verification
- `python Tools/test_sharded/test_sharded.py`
- `pytest tests/unit/simulation/components/abilities/test_recover_fighters.py`
- Manual: full launch → battle → reboard cycle. Verify HP persistence across save/load.

## Exit criteria
- Strategic recovery works (HP preserved).
- End-of-battle reboard correctly distinguishes launched-this-battle from pre-existing.
- Overflow → sector group works.
- Destroyed carrier doesn't break the reboard flow.
