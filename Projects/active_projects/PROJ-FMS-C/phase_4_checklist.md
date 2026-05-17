# PROJ-FMS-C Phase 4: Integration tests + E2E gameplay smoke

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Comprehensive end-to-end coverage of the fighters feature plus a hand-verified gameplay smoke test. After this phase, fighters are shippable.

## Tasks

### Automated E2E
- [x] `tests/integration/test_fms_c_e2e.py`:
  - Design fighter (with some weapons). Build N on a carrier's SpaceShipyard. Verify bay.
  - Strategic launch into the current hex → `fighter_group` of N.
  - Move enemy fleet into the hex → tactical battle starts; `fighter_group` joins on owner's side; fighters fight via minimal AI; some die, some survive.
  - At battle end: survivors **NOT** auto-reboarded (because they were pre-existing in the group, not launched this battle).
  - Execute `RecoverFightersAbility` from the carrier → surviving fighters back in carrier bay with HP preserved.
- [x] `tests/integration/test_fms_c_launch_in_battle_e2e.py`:
  - Carrier with bay-loaded fighters in a battle.
  - Tactical launch mid-battle (4 fighters); they're tagged `launched_in_battle_id`.
  - 3 survive at battle end → all 3 auto-reboard onto the carrier.
  - Overflow scenario: launch 4, only 2 bay slots free at end → 2 reboard, 2 spill into new sector `fighter_group`.

### Stat correctness
- [x] Verify `fighter_capacity` / `fighters_per_wave` / `launch_cycle` stats from [`launch.py:29-61`](../../../game/simulation/entities/stat_contributors/launch.py#L29) are correct after the Phase 1 stat-contributor update. **(Superseded by Round 4 Obs C — `fighters_per_wave` / `launch_cycle` were renamed to a single `fighter_launch_rate_tons_per_sec` field; only `fighter_capacity` survives under its original name. See `decisions.md` "2026-05-17 — Round 4 follow-up".)**

### Hand verification (gameplay smoke)
> **PROJ-FMS-C audit Fix 3 (2026-05-16):** these items were marked `[x]`
> in the original Phase 4 commit but no human ever performed the smoke
> test. Re-flagged `[ ]` as accurate state. The integration tests + the
> new carrier-AI production caller cover the same contracts headlessly;
> manual gameplay smoke is now blocked on the pygame UI binding (a
> follow-up). See "Known Limitations" in
> [`findings/implementation_report.md`](findings/implementation_report.md).

- [ ] Load a save with multiple empires.
- [ ] Empire A designs a fighter with 1 weapon. Builds 10 on a carrier.
- [ ] Strategic-launches 6 into the current hex → `fighter_group` of 6 visible on map.
- [ ] Empire B's fleet moves into the hex → battle starts.
- [ ] Empire A's `fighter_group` joins; 6 fighters appear, AI targets nearest enemy, weapons fire.
- [ ] Mid-battle, Empire A launches 3 more from the carrier (tactical launch). These should join the fight with full HP / weapons.
- [ ] Battle ends: say 4 pre-existing + 2 newly-launched survive.
  - 2 newly-launched auto-reboard onto carrier (bay delta +2).
  - 4 pre-existing stay in `fighter_group` (which still exists in the hex).
- [ ] Execute strategic recovery on the carrier → pre-existing 4 reboard if bay space allows.
- [ ] Save / load mid-cycle to verify state persistence.

### Documentation
- [x] Update [`docs/systems/`](../../../docs/systems/) with a new `fighters.md` describing the launch / recover lifecycle and ability surface.
- [x] Update [`docs/systems/ability_reference.md`](../../../docs/systems/ability_reference.md) entries for `StrategicFighterLaunchAbility`, `TacticalFighterLaunchAbility`, `RecoverFightersAbility`.

## Verification
- Full sharded suite: `python Tools/test_sharded/test_sharded.py`
- Combat lab: `python -m combat_lab.run_tests`
- Hand-verification checklist above completed.

## Exit criteria
- All automated tests green.
- Hand-verification gameplay smoke passes.
- Docs updated.
- PROJ-FMS-C complete. PROJ-FMS-D can begin.
