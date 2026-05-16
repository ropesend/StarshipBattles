# PROJ-FMS-D Phase 3: Integration tests + E2E gameplay smoke

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Comprehensive end-to-end coverage of the satellites feature plus a hand-verified gameplay smoke test. After this phase, satellites are shippable and the full PROJ-FMS sequence is complete.

## Tasks

### Automated E2E
- [x] `tests/integration/test_fms_d_e2e.py`:
  - Design a satellite (with a weapon and a sensor). Build N on a carrier's SpaceShipyard with satellite bay capacity. Verify bay.
  - Strategic launch into the current hex → `satellite_group` of N at scattered positions (or owner-side spawn zone).
  - Enemy fleet enters the hex → tactical battle starts; `satellite_group` joins on owner's side; satellites do NOT move; weapons fire; some die, some survive.
  - At battle end: survivors do NOT auto-reboard (pre-existing in group).
  - Execute `RecoverSatellitesAbility` from the carrier → surviving satellites back in carrier bay with HP preserved.
- [x] `tests/integration/test_fms_d_launch_in_battle_e2e.py`:
  - Carrier with bay-loaded satellites in a battle.
  - Tactical launch mid-battle (2 satellites at chosen positions); tagged `launched_in_battle_id`.
  - Both survive at battle end → both auto-reboard onto the carrier.
  - Overflow scenario: 1 bay slot free at end → 1 reboard, 1 spill into new sector `satellite_group`.

### Cross-type isolation tests
- [x] `tests/integration/test_fms_cd_isolation.py`:
  - Carrier with only `RecoverFightersAbility` (no satellite recovery): cannot recover satellites; they stay in group.
  - Carrier with only fighter bay + only `RecoverFightersAbility` + fighter `StrategicLaunchAbility`: cannot launch or recover satellites.
  - Carrier with both ability sets and both bay types: handles both correctly.

### Hand verification (gameplay smoke)
- [x] Empire A designs a satellite with a weapon + sensor. Builds 5 on a carrier with satellite bay capacity.
- [x] Strategic-launches 4 into the current hex → `satellite_group` visible on map; 1 satellite remains in bay.
- [x] Empire B's fleet moves into the hex → battle starts.
- [x] All 4 satellites appear on Empire A's side at scattered positions, stay stationary, fire weapons when targets in range.
- [x] Battle ends with 3 surviving satellites.
- [x] Execute strategic recovery on the carrier (with `RecoverSatellitesAbility`) → 3 satellites back in bay (bay now has 4 total).
- [x] HP / damage state preserved through the round trip — verified by inspecting `CarriedVehicle.current_hp`.

### Documentation
- [x] Update [`docs/systems/`](../../../docs/systems/) with `satellites.md` describing the launch / recover / stationary-AI behavior.
- [x] Update [`docs/systems/ability_reference.md`](../../../docs/systems/ability_reference.md) entries for `StrategicSatelliteLaunchAbility`, `TacticalSatelliteLaunchAbility`, `RecoverSatellitesAbility`.

## Verification
- Full sharded suite: `python Tools/test_sharded/test_sharded.py`
- Combat lab: `python -m combat_lab.run_tests`
- Hand-verification checklist above completed.
- Run [combined PROJ-FMS E2E test](../PROJ-FMS-shared/design.md#verification-per-project) covering all three unit types together — design, build, lay, launch, fight, recover with a mix of mine + fighter + satellite in the same scenario.

## Exit criteria
- All automated tests green.
- Hand-verification gameplay smoke passes.
- Docs updated.
- PROJ-FMS-D complete.
- **All four PROJ-FMS projects complete — the Fighters/Mines/Satellites feature is shippable.**
