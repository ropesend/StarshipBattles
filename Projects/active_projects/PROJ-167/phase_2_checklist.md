# Phase 2: Migrate Ability Files to Constants

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-167 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace all 51 inline hex strings in 11 ability files + detail_panel.py with imported constants

---

## Tasks

### Task 2.1: Migrate weapons.py [Simple]
**File:** `game/simulation/components/abilities/weapons.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_weapon*.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_DAMAGE, HINT_RANGE, HINT_RELOAD, HINT_PROJECTILE_SPEED, HINT_ACCURACY`
- [ ] Line ~210: Replace `'#FF6464'` → `HINT_DAMAGE` (WeaponAbility.get_ui_rows, "Damage")
- [ ] Line ~211: Replace `'#FFA500'` → `HINT_RANGE` (WeaponAbility.get_ui_rows, "Range")
- [ ] Line ~212: Replace `'#FFC864'` → `HINT_RELOAD` (WeaponAbility.get_ui_rows, "Reload")
- [ ] Line ~259: Replace `'#C8C832'` → `HINT_PROJECTILE_SPEED` (ProjectileWeaponAbility.get_ui_rows, "Speed")
- [ ] Line ~285: Replace `'#FFFF00'` → `HINT_ACCURACY` (BeamWeaponAbility.get_ui_rows, "Accuracy")
- [ ] Verify: `pytest tests/unit/simulation/components/abilities/test_weapon*.py -q`

**Notes:**

---

### Task 2.2: Migrate defense.py [Simple]
**File:** `game/simulation/components/abilities/defense.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_defense*.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_SHIELD_CAP, HINT_SHIELD_REGEN, HINT_DAMAGE, HINT_EVASION, HINT_ACCURACY`
- [ ] Line ~27: Replace `'#00FFFF'` → `HINT_SHIELD_CAP` (ShieldProjection, "Shield Cap")
- [ ] Line ~52: Replace `'#00C8FF'` → `HINT_SHIELD_REGEN` (ShieldRegeneration, "Regen")
- [ ] Line ~78: Replace `'#FF6464'` → `HINT_DAMAGE` (ToHitAttackModifier, "Targeting")
- [ ] Line ~101: Replace `'#64FFFF'` → `HINT_EVASION` (ToHitDefenseModifier, "Evasion")
- [ ] Line ~122: Replace `'#FFFF00'` → `HINT_ACCURACY` (EmissiveArmor, "Dmg Ignore")
- [ ] Verify: `pytest tests/unit/simulation/components/abilities/test_defense*.py -q`

**Notes:**

---

### Task 2.3: Migrate propulsion.py [Simple]
**File:** `game/simulation/components/abilities/propulsion.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/ -q -k propulsion`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_THRUST, HINT_TURN_SPEED, HINT_STRATEGIC_MOBILITY, HINT_SHIELD_CAP, HINT_DEFAULT, HINT_WARP_ENERGY`
- [ ] Line ~31: Replace `'#64FF64'` → `HINT_THRUST` (CombatPropulsion, "Thrust")
- [ ] Line ~60: Replace `'#64FF96'` → `HINT_TURN_SPEED` (ManeuveringThruster, "Turn Speed")
- [ ] Line ~107: Replace `'#6496FF'` → `HINT_STRATEGIC_MOBILITY` (StrategicMovement, "Strategic Mobility")
- [ ] Line ~157: Replace `'#00FFFF'` → `HINT_SHIELD_CAP` (WarpJump, "Warp Capable")
- [ ] Line ~158: Replace `'#FFFFFF'` → `HINT_DEFAULT` (WarpJump, "Max Tonnage")
- [ ] Line ~161: Replace `'#64C8FF'` → `HINT_WARP_ENERGY` (WarpJump, "Warp Energy")
- [ ] Verify: tests pass

**Notes:**

---

### Task 2.4: Migrate crew.py [Simple]
**File:** `game/simulation/components/abilities/crew.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_crew*.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_CREW_CAP, HINT_LIFE_SUPPORT, HINT_CREW_REQ`
- [ ] Line ~24: Replace `'#96FF96'` → `HINT_CREW_CAP` (CrewCapacity, "Crew Cap")
- [ ] Line ~46: Replace `'#96FFFF'` → `HINT_LIFE_SUPPORT` (LifeSupportCapacity, "Life Support")
- [ ] Line ~88: Replace `'#FF9696'` → `HINT_CREW_REQ` (CrewRequired, "Crew Req")
- [ ] Verify: `pytest tests/unit/simulation/components/abilities/test_crew*.py -q`

**Notes:**

---

### Task 2.5: Migrate cargo.py [Simple]
**File:** `game/simulation/components/abilities/cargo.py`
**Tests:** `pytest tests/unit/simulation/abilities/test_cargo*.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_CARGO_PASSENGER, HINT_CARGO_GENERIC`
- [ ] Line ~67: Replace `'#98FB98'` → `HINT_CARGO_PASSENGER` (CargoStorage passengers)
- [ ] Line ~70: Replace `'#FFD700'` → `HINT_CARGO_GENERIC` (CargoStorage generic)
- [ ] Verify: tests pass

**Notes:**

---

### Task 2.6: Migrate resources.py [Simple]
**File:** `game/simulation/components/abilities/resources.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_resource*.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_DEFAULT, HINT_RANGE, HINT_WARP_ENERGY, HINT_PROJECTILE_SPEED, HINT_EVASION, HINT_SHIELD_CAP, HINT_ACCURACY`
- [ ] ResourceConsumption.get_ui_rows (lines ~132-138):
  - [ ] Replace `'#FFFFFF'` → `HINT_DEFAULT` (default fallback)
  - [ ] Replace `'#FFA500'` → `HINT_RANGE` (fuel — same orange as range)
  - [ ] Replace `'#64C8FF'` → `HINT_WARP_ENERGY` (energy)
  - [ ] Replace `'#C8C832'` → `HINT_PROJECTILE_SPEED` (ammo — same yellow)
- [ ] ResourceStorage.get_ui_rows (lines ~182-184):
  - [ ] Replace `'#64FFFF'` → `HINT_EVASION` (default resource cap)
  - [ ] Replace `'#00FFFF'` → `HINT_SHIELD_CAP` (shield cap)
- [ ] ResourceGeneration.get_ui_rows (lines ~222-224):
  - [ ] Replace `'#FFFFFF'` → `HINT_DEFAULT` (default)
  - [ ] Replace `'#FFFF00'` → `HINT_ACCURACY` (energy gen)
- [ ] Verify: `pytest tests/unit/simulation/components/abilities/test_resource*.py -q`

**Notes:**

---

### Task 2.7: Migrate markers.py [Simple]
**File:** `game/simulation/components/abilities/markers.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/ -q -k marker`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_NEUTRAL, HINT_CREW_CAP, HINT_REQUIREMENT`
- [ ] Line ~40: Replace `'#C8C8C8'` → `HINT_NEUTRAL` (VehicleLaunchAbility, "Hangar")
- [ ] Line ~41: Replace `'#C8C8C8'` → `HINT_NEUTRAL` (VehicleLaunchAbility, "Cycle")
- [ ] Line ~54: Replace `'#96FF96'` → `HINT_CREW_CAP` (CommandAndControl, "Command")
- [ ] Line ~66: Replace `'#FFCC66'` → `HINT_REQUIREMENT` (RequiresC&C)
- [ ] Line ~78: Replace `'#FFCC66'` → `HINT_REQUIREMENT` (RequiresCombatMovement)
- [ ] Line ~90: Replace `'#96FF96'` → `HINT_CREW_CAP` (StructuralIntegrity)
- [ ] Verify: tests pass

**Notes:**

---

### Task 2.8: Migrate harvester.py [Simple]
**File:** `game/simulation/components/abilities/harvester.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_colonize_harvester.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_COLONIZE, HINT_ACCURACY, HINT_SHIELD_CAP, HINT_DEFAULT`
- [ ] Lines ~35, ~85: Replace `'#00FF00'` → `HINT_COLONIZE` (ResourceHarvester/EmpireStorage, "Resource Type")
- [ ] Lines ~40, ~90: Replace `'#FFFF00'` → `HINT_ACCURACY` (harvest rate/storage capacity)
- [ ] Line ~122: Replace `'#00FFFF'` → `HINT_SHIELD_CAP` (SpaceShipyard, "Construction Bonus")
- [ ] Line ~127: Replace `'#FFFFFF'` → `HINT_DEFAULT` (SpaceShipyard, "Max Ship Mass")
- [ ] Lines ~137, ~143: Replace `'#00FF00'` → `HINT_COLONIZE` (SpaceShipyard, "Production Rate")
- [ ] Verify: tests pass

**Notes:**

---

### Task 2.9: Migrate superweapons.py [Simple]
**File:** `game/simulation/components/abilities/superweapons.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_superweapons.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_SUPERWEAPON`
- [ ] Replace `'#FF4444'` → `HINT_SUPERWEAPON` at 6 locations (lines ~44, ~73, ~102, ~131, ~161, ~190)
- [ ] Verify: tests pass

**Notes:**

---

### Task 2.10: Migrate colonize.py [Simple]
**File:** `game/simulation/components/abilities/colonize.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_colonize*.py tests/unit/abilities/test_colonize*.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_COLONIZE`
- [ ] Line ~67: Replace `'#00FF00'` → `HINT_COLONIZE` (ColonizePlanet, "Colonizes")
- [ ] Verify: tests pass

**Notes:**

---

### Task 2.11: Migrate detail_panel.py [Simple]
**File:** `game/ui/screens/builder/detail_panel.py`
**Tests:** `pytest tests/unit/ui/test_detail_panel*.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_NEUTRAL, HINT_CREW_CAP, HINT_CARGO_GENERIC`
- [ ] Line ~144: Replace fallback `'#C8C8C8'` → `HINT_NEUTRAL`
- [ ] Line ~171: Replace `'#96FF96'` → `HINT_CREW_CAP` (optional modifier color)
- [ ] Line ~175: Replace `'#FFD700'` → `HINT_CARGO_GENERIC` (mandatory modifier color)
- [ ] Verify: `pytest tests/unit/ui/test_detail_panel*.py -q`

**Notes:** detail_panel is in UI layer importing from simulation layer — this is fine since UI already imports from simulation.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full ability tests: `pytest tests/unit/simulation/components/abilities/ -q` — all pass
- [ ] Run detail panel tests: `pytest tests/unit/ui/test_detail_panel*.py -q` — all pass
- [ ] Grep check: `grep -rn "color_hint.*'#" game/simulation/components/abilities/` returns only ui_colors.py
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
