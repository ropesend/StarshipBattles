# Phase 3: Update Test Assertions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-167 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update 27+ test assertions to use imported constants instead of hardcoded hex strings

---

## Tasks

### Task 3.1: Update test_defense_isolation.py [Simple]
**File:** `tests/unit/simulation/components/abilities/test_defense_isolation.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_defense_isolation.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_SHIELD_CAP, HINT_SHIELD_REGEN, HINT_DAMAGE, HINT_EVASION, HINT_ACCURACY`
- [ ] Line ~161: Replace `'#00FFFF'` → `HINT_SHIELD_CAP` (ShieldProjection test)
- [ ] Line ~276: Replace `'#00C8FF'` → `HINT_SHIELD_REGEN` (ShieldRegeneration test)
- [ ] Line ~360: Replace `'#FF6464'` → `HINT_DAMAGE` (ToHitAttackModifier test)
- [ ] Line ~441: Replace `'#64FFFF'` → `HINT_EVASION` (ToHitDefenseModifier test)
- [ ] Line ~530: Replace `'#FFFF00'` → `HINT_ACCURACY` (EmissiveArmor test)
- [ ] Verify: test file passes

**Notes:**

---

### Task 3.2: Update test_crew_abilities.py [Simple]
**File:** `tests/unit/simulation/components/abilities/test_crew_abilities.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_crew_abilities.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_CREW_CAP, HINT_LIFE_SUPPORT, HINT_CREW_REQ`
- [ ] Line ~154: Replace `'#96FF96'` → `HINT_CREW_CAP` (CrewCapacity test)
- [ ] Line ~286: Replace `'#96FFFF'` → `HINT_LIFE_SUPPORT` (LifeSupportCapacity test)
- [ ] Line ~435: Replace `'#FF9696'` → `HINT_CREW_REQ` (CrewRequired test)
- [ ] Verify: test file passes

**Notes:**

---

### Task 3.3: Update test_resource_consumption.py [Simple]
**File:** `tests/unit/simulation/components/abilities/test_resource_consumption.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_resource_consumption.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_RANGE, HINT_WARP_ENERGY, HINT_PROJECTILE_SPEED, HINT_DEFAULT`
- [ ] Line ~953: Replace `'#FFA500'` → `HINT_RANGE` (fuel orange)
- [ ] Line ~963: Replace `'#64C8FF'` → `HINT_WARP_ENERGY` (energy blue)
- [ ] Line ~973: Replace `'#C8C832'` → `HINT_PROJECTILE_SPEED` (ammo yellow)
- [ ] Line ~981: Replace `'#FFFFFF'` → `HINT_DEFAULT` (unknown white)
- [ ] Verify: test file passes

**Notes:**

---

### Task 3.4: Update test_superweapons.py [Simple]
**File:** `tests/unit/simulation/components/abilities/test_superweapons.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_superweapons.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_SUPERWEAPON`
- [ ] Line ~125: Replace `'#FF4444'` → `HINT_SUPERWEAPON`
- [ ] Verify: test file passes

**Notes:**

---

### Task 3.5: Update test_colonize_harvester.py [Simple]
**File:** `tests/unit/simulation/components/abilities/test_colonize_harvester.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_colonize_harvester.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_COLONIZE, HINT_ACCURACY, HINT_SHIELD_CAP, HINT_DEFAULT`
- [ ] Lines ~94, ~212, ~343: Replace `'#00FF00'` → `HINT_COLONIZE` (resource type green)
- [ ] Lines ~215, ~346: Replace `'#FFFF00'` → `HINT_ACCURACY` (storage capacity yellow)
- [ ] Line ~433: Replace `'#00FFFF'` → `HINT_SHIELD_CAP` (construction bonus cyan)
- [ ] Line ~436: Replace `'#FFFFFF'` → `HINT_DEFAULT` (max ship mass white)
- [ ] Line ~452: Replace `'#00FF00'` → `HINT_COLONIZE` (production rate green)
- [ ] Verify: test file passes

**Notes:**

---

### Task 3.6: Update test_cargo_storage.py [Simple]
**File:** `tests/unit/simulation/abilities/test_cargo_storage.py`
**Tests:** `pytest tests/unit/simulation/abilities/test_cargo_storage.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_CARGO_PASSENGER, HINT_CARGO_GENERIC`
- [ ] Line ~148: Replace `'#98FB98'` → `HINT_CARGO_PASSENGER`
- [ ] Line ~160: Replace `'#FFD700'` → `HINT_CARGO_GENERIC`
- [ ] Verify: test file passes

**Notes:**

---

### Task 3.7: Update test_abilities.py [Simple]
**File:** `tests/unit/entities/test_abilities.py`
**Tests:** `pytest tests/unit/entities/test_abilities.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_THRUST`
- [ ] Line ~122: Replace `'#64FF64'` → `HINT_THRUST` (CombatPropulsion)
- [ ] Verify: test file passes

**Notes:**

---

### Task 3.8: Update test_detail_panel_rendering.py [Simple]
**File:** `tests/unit/ui/test_detail_panel_rendering.py`
**Tests:** `pytest tests/unit/ui/test_detail_panel_rendering.py -q`

- [ ] Add import: `from game.simulation.components.abilities.ui_colors import HINT_CARGO_GENERIC, HINT_CREW_CAP`
- [ ] Line ~247: Replace `'#FFD700'` → `HINT_CARGO_GENERIC` (mandatory modifier gold)
- [ ] Line ~251: Replace `'#96FF96'` → `HINT_CREW_CAP` (optional modifier green)
- [ ] Note: Lines ~139-140, ~149-150 use `'#FF0000'` and `'#00FF00'` in MOCK DATA — these are test-specific mock values, NOT real ability colors. Leave them as-is.
- [ ] Verify: test file passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run all affected test files: `pytest tests/unit/simulation/components/abilities/ tests/unit/entities/test_abilities.py tests/unit/ui/test_detail_panel_rendering.py -q` — all pass
- [ ] Grep check: `grep -rn "'#[0-9A-Fa-f]\{6\}'" tests/unit/simulation/components/abilities/` — only mock data and non-color strings remain
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
