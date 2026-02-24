# Phase 2: Migrate `__init__` and `sync_data` Callers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-164 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace 10 `__init__` parsing lines + 3 `sync_data` lines with calls to `_parse_primary_value()`.

---

## Tasks

### Task 2.1: Migrate defense.py (5 classes) [Simple]
**File:** `game/simulation/components/abilities/defense.py`
**Tests:** `pytest tests/unit/entities/test_abilities.py tests/unit/simulation/components/abilities/ -v`

- [ ] ShieldProjection `__init__` (lines 17-18): Replace 2 lines with:
  `self.base_capacity = self._parse_primary_value(data)`
- [ ] ShieldRegeneration `__init__` (lines 42-43): Replace with:
  `self.base_rate = self._parse_primary_value(data)`
- [ ] ToHitAttackModifier `__init__` (lines 65-66): Replace with:
  `self.value = self._parse_primary_value(data)`
- [ ] ToHitDefenseModifier `__init__` (lines 91-92): Replace with:
  `self.value = self._parse_primary_value(data)`
- [ ] EmissiveArmor `__init__` (lines 114-115): Replace with:
  `self.amount = int(self._parse_primary_value(data))`
- [ ] Run tests

**Notes:**

### Task 2.2: Migrate propulsion.py (3 `__init__` + 3 `sync_data`) [Simple]
**File:** `game/simulation/components/abilities/propulsion.py`
**Tests:** `pytest tests/unit/entities/test_abilities.py tests/unit/simulation/components/abilities/ tests/integration/test_strategic_abilities.py -v`

- [ ] CombatPropulsion `__init__` (lines 17-18): Replace with:
  `self.base_thrust = self._parse_primary_value(data)`
- [ ] CombatPropulsion `sync_data` (line 23): Replace with:
  `val = self._parse_primary_value(data)`
- [ ] ManeuveringThruster `__init__` (lines 46-47): Replace with:
  `self.base_turn_rate = self._parse_primary_value(data)`
- [ ] ManeuveringThruster `sync_data` (line 52): Replace with:
  `val = self._parse_primary_value(data)`
- [ ] StrategicMovement `__init__` (lines 93-94): Replace with:
  `self.base_movement_points = self._parse_primary_value(data)`
- [ ] StrategicMovement `sync_data` (line 99): Replace with:
  `val = self._parse_primary_value(data)`
- [ ] Run tests (include integration for strategic abilities)

**Notes:** The sync_data 3-way check is exactly what `_parse_primary_value()` does natively.

### Task 2.3: Migrate crew.py (2 classes — skip CrewRequired) [Simple]
**File:** `game/simulation/components/abilities/crew.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_crew_abilities.py tests/unit/entities/test_abilities.py -v`

- [ ] CrewCapacity `__init__` (lines 16-17): Replace with:
  `self.amount = int(self._parse_primary_value(data))`
- [ ] LifeSupportCapacity `__init__` (lines 38-39): Replace with:
  `self.amount = int(self._parse_primary_value(data))`
- [ ] CrewRequired line 74: **SKIP** — leave as-is (nested `data.get('value', data.get('amount', 0))` fallback)
- [ ] Run tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
