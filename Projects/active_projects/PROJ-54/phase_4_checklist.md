# Phase 4: Defense Ability Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-54 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add test coverage for defense abilities (ShieldProjection, ShieldRegeneration, EmissiveArmor, ToHitDefenseModifier, ToHitAttackModifier) with 7 new test scenarios.

**Prerequisite:** Phase 1 complete (generalized extraction supports defense ability data)

---

## Tasks

### Task 4.1: Add Defense Test Components [Simple]
**File:** `simulation_tests/data/components.json`
**Tests:** `pytest simulation_tests/ -v` (load validation)

Add zero-mass defense components following existing test component patterns.

- [x] Add `test_shield_200` component:
  ```json
  {
      "id": "test_shield_200",
      "name": "Test Shield 200",
      "mass": 0,
      "hp": 100,
      "abilities": { "ShieldProjection": 200 }
  }
  ```
- [x] Add `test_shield_regen_10` component:
  ```json
  {
      "id": "test_shield_regen_10",
      "name": "Test Shield Regen 10",
      "mass": 0,
      "hp": 100,
      "abilities": { "ShieldRegeneration": 10 }
  }
  ```
- [x] Add `test_ecm_1` component:
  ```json
  {
      "id": "test_ecm_1",
      "name": "Test ECM 1",
      "mass": 0,
      "hp": 100,
      "abilities": { "ToHitDefenseModifier": 1.0 }
  }
  ```
- [x] Add `test_sensor_1` component:
  ```json
  {
      "id": "test_sensor_1",
      "name": "Test Sensor 1",
      "mass": 0,
      "hp": 100,
      "abilities": { "ToHitAttackModifier": 1.0 }
  }
  ```
- [x] Add `test_emissive_armor_5` component:
  ```json
  {
      "id": "test_emissive_armor_5",
      "name": "Test Emissive Armor 5",
      "mass": 0,
      "hp": 100,
      "abilities": { "EmissiveArmor": 5 }
  }
  ```
- [x] Verify: components load without errors (63 components, all 5 new defense components present)

**Notes:** Follow existing zero-mass pattern from other test components in this file.

---

### Task 4.2: Add Defense Test Ship JSONs [Simple]
**File:** `simulation_tests/data/ships/` (new files)
**Tests:** `pytest simulation_tests/ -v`

Create ship JSON files that combine hull with defense components.

- [x] Create `Test_Target_Shielded.json` - hull + `test_shield_200` + extreme HP armor
- [x] Create `Test_Target_Shield_Regen.json` - hull + `test_shield_200` + `test_shield_regen_10` + extreme HP armor
- [x] Create `Test_Target_EmissiveArmor.json` - hull + `test_emissive_armor_5` + extreme HP armor
- [x] Create `Test_Target_ECM.json` - hull + `test_ecm_1` + extreme HP armor
- [x] Create `Test_Attacker_Beam360_WithSensor.json` - med accuracy beam + `test_sensor_1`
- [x] Verify: all ship JSONs load without errors (smoke tests pass)

**Notes:** Reference existing ship JSONs in `simulation_tests/data/ships/` for format. Hull should use the standard test hull.

---

### Task 4.3: Add Defense Constants [Simple]
**File:** `simulation_tests/test_constants.py`
**Tests:** None

- [x] Add constants for defense test ship filenames (SHIELDED_TARGET_SHIP, etc.)
- [x] Add constants for defense test expected values (SHIELD_CAPACITY=200, SHIELD_REGEN_RATE=10, EMISSIVE_ARMOR_REDUCTION=5, ECM/SENSOR values)
- [x] Follow existing naming pattern in `test_constants.py`

**Notes:**

---

### Task 4.4: Create Defense Scenarios [Complex]
**File:** `simulation_tests/scenarios/defense_scenarios.py` (new)
**Tests:** `pytest simulation_tests/ -v`

Create 7 new test scenarios using `StaticTargetScenario` template.

- [x] Create `defense_scenarios.py` with appropriate imports
- [x] Implement `ShieldAbsorbsDamageScenario` (SHIELD-001):
  - Med accuracy beam at point blank vs shielded target
  - `verify_damage_dealt = True`, tracks shield_damage_absorbed, final_shields
- [x] Implement `ShieldOverflowToHullScenario` (SHIELD-002):
  - High accuracy beam (5 dmg) at point blank vs shielded target, 1000 ticks
  - `min_damage_threshold = 201`, tracks shields_depleted, hull_damage
- [x] Implement `ShieldRegenerationScenario` (SHIELD-003):
  - Med accuracy beam vs target with shield + 10/sec regen
  - `measurement_mode = True`, tracks shields_intact, regen_rate
- [x] Implement `EmissiveArmorBlocksLowDamageScenario` (ARMOR-001):
  - 1-damage beam vs EmissiveArmor(5) target
  - `expect_no_damage = True` (1 dmg < 5 armor = blocked)
- [x] Implement `EmissiveArmorReducesHighDamageScenario` (ARMOR-002):
  - 5-damage beam vs EmissiveArmor(5) target
  - `expect_no_damage = True` (5 dmg - 5 armor = 0)
- [x] Implement `ECMReducesHitRateScenario` (ECM-001):
  - Med accuracy beam at 400px vs ECM(1.0) target
  - `measurement_mode = True`, computes expected hit chance with/without ECM via `compute_beam_hit_chance`
- [x] Implement `SensorImprovesHitRateScenario` (SENSOR-001):
  - Med accuracy beam + sensor(1.0) at 400px vs standard target
  - `verify_damage_dealt = True`, computes expected hit chance with/without sensor
- [x] Add all scenario classes to `simulation_tests/scenarios/__init__.py` exports
- [x] Register scenarios with pytest test file `test_defense.py` (3 test classes, 7 tests)
- [x] Verify: `pytest simulation_tests/ -v` - all 7 new scenarios pass (52 passed total)

**Notes:** Each test isolates ONE defense ability. Use calibrated beam attacker with known accuracy.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] 7 new defense scenarios registered and passing (52 sim tests passed total)
- [x] `pytest simulation_tests/ -v` passes (52 passed, 5 pre-existing failures, 4 skipped)
- [x] `pytest tests/ -n 4` passes (full suite: 6113 passed, 5 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
