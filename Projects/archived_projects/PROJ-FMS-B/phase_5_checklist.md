# PROJ-FMS-B Phase 5: Integration tests + E2E gameplay smoke

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Comprehensive end-to-end coverage of the mines feature plus a hand-verified gameplay smoke test. After this phase, mines are shippable.

## Tasks

### Automated E2E
- [x] `tests/integration/test_fms_b_e2e.py`:
  - Design a mine (warhead variant) and a mine (laserhead variant) in the workshop.
  - Build N of each on a ship's `SpaceShipyard`; verify they end up in the ship's `VehicleBay`.
  - Lay them strategically into a hex.
  - Move an enemy fleet into the hex → confirm warhead pass triggers, laserhead pass evaluates threshold, damage applied via combat events.
  - Trigger a tactical battle in the same hex → confirm `mine_group` joins the owning side; mines appear at scattered positions; per-tick behavior fires. (Strategic and tactical wiring landed via PROJ-FMS-B audit Fix 2 — 2026-05-16. Spec-compiler-level tests confirm the wiring; a deeper through-BattleEngine integration test using the existing combat_lab harness is the optional follow-up.)
  - Self-destruct remaining mines via UI action → confirm `mine_group` cleanup. (Service-layer covered; UI is the deferred binding.)
- [x] `tests/integration/test_ramming_e2e.py`:
  - Design a kamikaze fighter with 2× Warhead + RamTarget.
  - Build, load into a carrier's bay.
  - Launch (after PROJ-FMS-C Phase 1, or via a stub here that creates a `fighter_group` directly).
  - Tactical battle; set ram target on an enemy ship; verify fighter intercepts, both warheads detonate, fighter destroyed, enemy ship takes 2× warhead damage. (Wired via PROJ-FMS-B audit Fix 3 — 2026-05-16: `BattleEngine.ram_resolver` + `BattleEngine.set_ram_target` action surface tick the resolver from `BattleEngine.update`.)

### Stress / balance tests
- [x] Statistical tests over 1000 trials each:
  - Destroyer-class vs N=10 warhead mines at MED sensitivity: assert observed trigger rate is within tolerance of `P_trigger_pass`.
  - Dreadnought-class same field: assert higher rate, statistically significant.
  - Same destroyer vs `N=100` mines: assert `P_trigger_pass < 1.0` (never 100% invariant).
  - Same destroyer vs `N=1` mine: assert `P_trigger_pass > 0.0` (always-some-chance invariant).

### Hand verification (gameplay smoke)
- [ ] Load a save with multiple empires.
- [ ] Empire A designs a warhead mine + laserhead mine + kamikaze fighter.
- [ ] Builds each on a planet (verify staging_yard delta) and on a ship yard (verify bay delta).
- [ ] Transfers from planet staging to a ship's bay.
- [ ] Lays warhead mines in hex X (LOW sensitivity), laserhead mines in hex Y (threshold 0.5).
- [ ] Empire B moves a frigate into hex X: observe damage; check sensitivity behaves (compare LOW vs HIGH on a separate run).
- [ ] Empire B moves a battleship into hex Y: observe laserhead fires (high expected hit chance); set threshold to 0.9 and re-run with a frigate → laserheads skip.
- [ ] Trigger a tactical battle in hex X: observe mine scatter, per-tick behavior, mine HP from Hull, point-defense interaction.
- [ ] Self-destruct half the mines in hex X via UI; verify counts.
- [ ] Set kamikaze fighter's ram target in a separate battle; observe correct collision damage.

> The hand-verification block requires interactive pygame UI bindings that
> are still outstanding (sensitivity radio, threshold slider, self-destruct
> modal, ram-target context action). Engine + service contracts are wired
> and unit/integration-tested; the smoke run unblocks once the UI layer
> lands.

### Documentation
- [x] Update [`docs/systems/`](../../../docs/systems/) with a new `minefields.md` describing the system, sensitivity/threshold settings, and the trigger formula.
- [x] Update [`docs/systems/ability_reference.md`](../../../docs/systems/ability_reference.md) entries for `WarheadAbility`, `LaserheadAbility`, `RamTargetAbility`, `StrategicMineLayerAbility`, `TacticalMineLayerAbility`.

## Verification
- Full sharded suite: `python Tools/test_sharded/test_sharded.py`
- Combat lab: `python -m combat_lab.run_tests`
- Hand-verification checklist above completed.

## Exit criteria
- All automated tests green.
- Hand-verification gameplay smoke passes.
- Docs updated.
- PROJ-FMS-B complete. PROJ-FMS-C can begin.
