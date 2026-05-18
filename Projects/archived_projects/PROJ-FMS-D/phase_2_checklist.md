# PROJ-FMS-D Phase 2: Recovery (separate ability gate from fighters)

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Satellite recovery works at both strategic (explicit empire action) and tactical (end-of-battle reboard) layers, with a separate ability gate from fighter recovery.

## Tasks

### Strategic satellite recovery (Command → OrderType → Handler)

- [x] `OrderType.RECOVER_SATELLITES` reserved by PROJ-FMS-A Phase 5. Verify.
- [x] New `IssueRecoverSatellitesCommand` + handler in [`game/strategy/engine/handlers/`](../../../game/strategy/engine/handlers/).
- [x] New `RecoverSatellitesOrderHandler(BaseOrderHandler)` in [`game/strategy/engine/order_handlers/recover_satellites.py`](../../../game/strategy/engine/order_handlers/). Mirrors PROJ-FMS-C Phase 3's `RecoverFightersOrderHandler`, but:
  - Acts on `satellite_group` Fleets only.
  - Pops `CarriedVehicle`s back into a satellite-capable bay (respecting the type filter from Phase 1).
- [x] A ship with `RecoverFightersAbility` only **cannot** recover satellites and vice versa. This is the design intent — separate ability gates create design space for specialized carriers.

### End-of-battle reboard
- [x] Extend the end-of-battle reboard hook from PROJ-FMS-C Phase 3 to also handle satellites:
  - Satellites launched during this battle (tagged `launched_in_battle_id`) auto-reboard into any friendly ship with satellite-bay space.
  - Pre-existing `satellite_group` satellites stay in the sector.
  - Overflow → new sector `satellite_group`.
- [x] Verify the existing hook handles both fighters and satellites correctly — either via a generalised pass over all `launched_in_battle_id`-tagged vehicles of either type, or via two separate passes.

### Edge cases
- [x] Satellite at 0 HP at battle end: destroyed, not recovered.
- [x] Carrier with only fighter bay (no satellite bay) survives: cannot recover its launched satellites; they overflow.
- [x] HP / damage state preserved through the round trip.

### Tests
- [x] Strategic recovery: pre-existing `satellite_group` of 4, carrier with `RecoverSatellitesAbility` + 5 satellite bay slots in same hex → recover all 4, group destroyed.
- [x] Bay-type mismatch: carrier with only fighter bay → `RecoverSatellitesAbility` fails to find space → satellites stay in group.
- [x] End-of-battle: launch 3 satellites mid-battle, all survive, carrier has 3 satellite bay slots → all 3 reboard.
- [x] HP preserved through round trip.
- [x] Pre-existing satellites that participate but were not launched this battle do NOT auto-reboard.

## Verification
- `python Tools/test_sharded/test_sharded.py`
- `pytest tests/unit/simulation/components/abilities/test_recover_satellites.py`
- Manual: design carrier with both fighter and satellite bays + recovery abilities; verify each recovery type respects its bay gate.

## Exit criteria
- Strategic satellite recovery works with separate ability gate.
- End-of-battle reboard handles satellites correctly with overflow behavior.
- Fighter-only recovery cannot recover satellites; satellite-only recovery cannot recover fighters.
