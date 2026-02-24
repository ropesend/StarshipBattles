# Phase 2: Migrate `__init__` and `sync_data` Callers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-164 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace 10 `__init__` parsing lines + 3 `sync_data` lines with calls to `_parse_primary_value()`.

---

## Tasks

### Task 2.1: Migrate defense.py (5 classes) [Simple]
**File:** `game/simulation/components/abilities/defense.py`
**Tests:** `pytest tests/unit/entities/test_abilities.py tests/unit/simulation/components/abilities/ -v`

- [x] ShieldProjection `__init__` (lines 17-18): Replace 2 lines with:
  `self.base_capacity = self._parse_primary_value(data)`
- [x] ShieldRegeneration `__init__` (lines 42-43): Replace with:
  `self.base_rate = self._parse_primary_value(data)`
- [x] ToHitAttackModifier `__init__` (lines 65-66): Replace with:
  `self.value = self._parse_primary_value(data)`
- [x] ToHitDefenseModifier `__init__` (lines 91-92): Replace with:
  `self.value = self._parse_primary_value(data)`
- [x] EmissiveArmor `__init__` (lines 114-115): Replace with:
  `self.amount = int(self._parse_primary_value(data))`
- [x] Run tests

**Notes:** All 5 defense.py classes migrated successfully.

### Task 2.2: Migrate propulsion.py (3 `__init__` + 3 `sync_data`) [Simple]
**File:** `game/simulation/components/abilities/propulsion.py`
**Tests:** `pytest tests/unit/entities/test_abilities.py tests/unit/simulation/components/abilities/ tests/integration/test_strategic_abilities.py -v`

- [x] CombatPropulsion `__init__` (lines 17-18): Replace with:
  `self.base_thrust = self._parse_primary_value(data)`
- [x] CombatPropulsion `sync_data` (line 23): Replace with:
  `self.base_thrust = self._parse_primary_value(data)` (inlined, removed temp var)
- [x] ManeuveringThruster `__init__` (lines 46-47): Replace with:
  `self.base_turn_rate = self._parse_primary_value(data)`
- [x] ManeuveringThruster `sync_data` (line 52): Replace with:
  `self.base_turn_rate = self._parse_primary_value(data)` (inlined)
- [x] StrategicMovement `__init__` (lines 93-94): Replace with:
  `self.base_movement_points = self._parse_primary_value(data)`
- [x] StrategicMovement `sync_data` (line 99): Replace with:
  `self.base_movement_points = self._parse_primary_value(data)` (inlined)
- [x] Run tests (include integration for strategic abilities)

**Notes:** All 3 __init__ + 3 sync_data in propulsion.py migrated. Inlined assignments directly instead of using temp var.

### Task 2.3: Migrate crew.py (2 classes — skip CrewRequired) [Simple]
**File:** `game/simulation/components/abilities/crew.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_crew_abilities.py tests/unit/entities/test_abilities.py -v`

- [x] CrewCapacity `__init__` (lines 16-17): Replace with:
  `self.amount = int(self._parse_primary_value(data))`
- [x] LifeSupportCapacity `__init__` (lines 38-39): Replace with:
  `self.amount = int(self._parse_primary_value(data))`
- [x] CrewRequired line 74: **SKIP** — leave as-is (nested `data.get('value', data.get('amount', 0))` fallback)
- [x] Run tests

**Notes:** 2 crew.py classes migrated. CrewRequired intentionally skipped per plan.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
