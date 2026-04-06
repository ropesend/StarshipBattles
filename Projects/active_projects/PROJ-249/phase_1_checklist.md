# PROJ-249 Phase 1: Add pdc_valid_targets to Weapon Ability

> **BEFORE MARKING THIS PHASE COMPLETE:**
> Run: `pytest tests/unit/simulation/combat/test_targeting_system.py -x`

## Objective
Replace hardcoded PDC targeting with data-driven target list on weapon ability.

## Status: Not Started

---

### Task 1.1: Add pdc_valid_targets to BeamWeaponAbility [Medium]
**File:** `game/simulation/components/abilities/weapons.py`
**Tests:** `pytest tests/unit/simulation/components/ -x`

- [ ] Add `pdc_valid_targets: List[str]` attribute to BeamWeaponAbility.__init__
- [ ] Default to `["MISSILE", "FIGHTER"]`
- [ ] Parse from ability data dict if `pdc_valid_targets` key is present in JSON
- [ ] Run tests: `pytest tests/unit/simulation/components/ -x`

### Task 1.2: Replace hardcoded checks in targeting_system.py [Medium]
**File:** `game/simulation/combat/targeting_system.py`
**Tests:** `pytest tests/unit/simulation/combat/test_targeting_system.py -x`

- [ ] Lines 163-173: Replace hardcoded MISSILE/FIGHTER checks with lookup against weapon's `pdc_valid_targets`
- [ ] Check if the firing weapon has `pdc_valid_targets` attribute; if not, use default `["MISSILE", "FIGHTER"]`
- [ ] Match target type: `AttackType.MISSILE` → "MISSILE", `vehicle_type == 'Fighter'` → "FIGHTER"
- [ ] Run tests: `pytest tests/unit/simulation/combat/test_targeting_system.py -x`

### Task 1.3: Verify No Regressions [Simple]
- [ ] Run `pytest tests/ --testmon`
- [ ] Run `python -m simulation_tests.run_tests SEEKER-PD --no-history`
- [ ] Run `python -m simulation_tests.run_tests --fast --no-history`

**Notes:** No production data files need updating — default matches current behavior.
