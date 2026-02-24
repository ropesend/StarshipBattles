# PROJ-164: Extract Ability._parse_primary_value() Base Class Helper

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-164` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-164 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Add helper + tests | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate `__init__` callers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate `sync_data` callers + verify | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-23
**Active Phase:** Phase 2
**Last Action:** Phase 1 complete - helper method and 12 unit tests added
**Next Action:** Begin Phase 2 - migrate __init__ callers in defense.py, propulsion.py, crew.py
**Blockers:** None

## Overview
Extract the repeated `val = data if isinstance(data, (int, float)) else data.get('value', 0)` pattern from 10 ability classes (11 `__init__` sites + 3 `sync_data` sites) into a shared `_parse_primary_value()` static method on the `Ability` base class. This eliminates the single most-duplicated snippet in the ability system.

**Origin:** Review `2026-02-23_160413_general_duplication-consolidation-analysis`, Finding SIM-COMP CQ-001, verified as Tier 1 #5 with 14-20 instances across 10 classes.

## Goals
- Eliminate 11 identical parsing lines in `__init__` methods across 3 ability files
- Eliminate 3 identical parsing lines in `sync_data` methods in `propulsion.py`
- Provide a single source of truth for "how to parse a primary numeric value from ability data"
- Zero behavior change — pure refactor, all existing tests must pass unchanged

## Scope
**In:**
- Add `_parse_primary_value()` static method to `Ability` base class in `base.py`
- Migrate all **standard pattern** callers (the exact `val = data if isinstance(...)` line)
- Migrate `sync_data` variants (which add `if isinstance(data, dict) else 0` guard)
- Write unit tests for the new helper

**Out:**
- Multi-field parsers (WeaponAbility, SeekerWeaponAbility, BeamWeaponAbility, ProjectileWeaponAbility, WarpJump) — these parse named fields, not a single 'value' key
- Dict-only parsers (ResourceConsumption, ResourceStorage, ResourceGeneration, VehicleLaunchAbility, ResourceHarvester, EmpireStorage, SpaceShipyard) — these use `data.get('specific_key')`, not the generic pattern
- String-handling parsers (ColonizePlanet) — not a numeric parse
- The `recalculate()` duplication (separate future project)
- The `get_ui_rows()` duplication (separate future project)

## Key Files
| Component | File Path |
|-----------|-----------|
| Base class | `game/simulation/components/abilities/base.py` |
| Defense abilities | `game/simulation/components/abilities/defense.py` |
| Propulsion abilities | `game/simulation/components/abilities/propulsion.py` |
| Crew abilities | `game/simulation/components/abilities/crew.py` |
| Base class tests | `tests/unit/simulation/components/abilities/test_ability_base.py` |
| Ability tests | `tests/unit/entities/test_abilities.py` |
| Crew tests | `tests/unit/simulation/components/abilities/test_crew_abilities.py` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Static method, not classmethod | No cls/self needed — pure data transformation |
| 2026-02-23 | Keep `int()` callers doing their own cast | Some abilities use `int(val)` (CrewCapacity, LifeSupportCapacity, EmissiveArmor, CrewRequired). Helper returns `float`, caller casts to `int` if needed. Keeps helper simple. |
| 2026-02-23 | Handle `sync_data` variant too | `sync_data` has a 3-way check: numeric / dict / else 0. Same helper works — it already returns `default` for non-numeric, non-dict inputs. |
| 2026-02-23 | Leave CrewRequired as-is | CrewRequired uses `data.get('value', data.get('amount', 0))` — nested fallback is subclass-specific. Only 1 line, not worth complicating the helper for. |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Initial Analysis

### The Standard Pattern (11 sites in `__init__`)
All use this exact line (only the target field name differs):
```python
val = data if isinstance(data, (int, float)) else data.get('value', 0)
```

**Sites:**
| # | File | Class | Line | Target Field | Cast |
|---|------|-------|------|-------------|------|
| 1 | defense.py | ShieldProjection | 17 | base_capacity | `float()` |
| 2 | defense.py | ShieldRegeneration | 42 | base_rate | `float()` |
| 3 | defense.py | ToHitAttackModifier | 65 | value | `float()` |
| 4 | defense.py | ToHitDefenseModifier | 91 | value | `float()` |
| 5 | defense.py | EmissiveArmor | 114 | amount | `int()` |
| 6 | propulsion.py | CombatPropulsion | 17 | base_thrust | `float()` |
| 7 | propulsion.py | ManeuveringThruster | 46 | base_turn_rate | `float()` |
| 8 | propulsion.py | StrategicMovement | 93 | base_movement_points | `float()` |
| 9 | crew.py | CrewCapacity | 16 | amount | `int()` |
| 10 | crew.py | LifeSupportCapacity | 38 | amount | `int()` |
| 11 | crew.py | CrewRequired | 74 | amount | `int()` — **SKIP** (nested fallback variant) |

### The sync_data Variant (3 sites)
```python
val = data if isinstance(data, (int, float)) else data.get('value', 0) if isinstance(data, dict) else 0
```
| # | File | Class | Line |
|---|------|-------|------|
| 1 | propulsion.py | CombatPropulsion | 23 |
| 2 | propulsion.py | ManeuveringThruster | 52 |
| 3 | propulsion.py | StrategicMovement | 99 |

---

## Phases

### Phase 1: Add Helper Method + Unit Tests [Simple]
**Objective:** Add `_parse_primary_value()` to Ability base class and write comprehensive tests.
**Status:** Not Started

#### Task 1.1: Add `_parse_primary_value()` to `Ability` base class [Simple]
**File:** `game/simulation/components/abilities/base.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_ability_base.py -v`
- [ ] Add static method after `_parse_scope()` method (after line 110):
  ```python
  @staticmethod
  def _parse_primary_value(data, key: str = 'value', default: float = 0.0) -> float:
      """
      Parse a primary numeric value from ability data.

      Handles three input formats:
      - Primitive numeric (int/float): Returns float(data) directly
      - Dict with key: Returns float(data[key]) or default
      - Other (str, None, etc.): Returns default

      Args:
          data: Raw ability data (dict, int, float, or other)
          key: Dict key to look up (default: 'value')
          default: Fallback value if key missing (default: 0.0)

      Returns:
          Parsed float value
      """
      if isinstance(data, (int, float)):
          return float(data)
      if isinstance(data, dict):
          return float(data.get(key, default))
      return float(default)
  ```
- [ ] Verify existing tests still pass
**Notes:**

#### Task 1.2: Write unit tests for `_parse_primary_value()` [Simple]
**File:** `tests/unit/simulation/components/abilities/test_ability_base.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_ability_base.py -v`
- [ ] Add test class `TestParsePrimaryValue` with these test cases:
  - [ ] `test_int_input` — `Ability._parse_primary_value(42)` → `42.0`
  - [ ] `test_float_input` — `Ability._parse_primary_value(3.14)` → `3.14`
  - [ ] `test_zero_int` — `Ability._parse_primary_value(0)` → `0.0`
  - [ ] `test_negative` — `Ability._parse_primary_value(-5.5)` → `-5.5`
  - [ ] `test_dict_with_value_key` — `Ability._parse_primary_value({'value': 100})` → `100.0`
  - [ ] `test_dict_missing_key_returns_default` — `Ability._parse_primary_value({'other': 5})` → `0.0`
  - [ ] `test_dict_custom_key` — `Ability._parse_primary_value({'amount': 7}, key='amount')` → `7.0`
  - [ ] `test_dict_custom_default` — `Ability._parse_primary_value({}, default=99.0)` → `99.0`
  - [ ] `test_string_returns_default` — `Ability._parse_primary_value("hello")` → `0.0`
  - [ ] `test_none_returns_default` — `Ability._parse_primary_value(None)` → `0.0`
  - [ ] `test_bool_treated_as_int` — `Ability._parse_primary_value(True)` → `1.0`
  - [ ] `test_dict_with_int_value` — `Ability._parse_primary_value({'value': 5})` → `5.0`
- [ ] Run tests, verify all pass
**Notes:**

---

### Phase 2: Migrate `__init__` and `sync_data` Callers [Simple]
**Objective:** Replace 10 `__init__` parsing lines + 3 `sync_data` lines with calls to `_parse_primary_value()`.
**Status:** Not Started

#### Task 2.1: Migrate defense.py (5 classes) [Simple]
**File:** `game/simulation/components/abilities/defense.py`
**Tests:** `pytest tests/unit/entities/test_abilities.py tests/unit/simulation/components/abilities/ -v`
- [ ] ShieldProjection `__init__` (lines 17-18): Replace:
  ```python
  val = data if isinstance(data, (int, float)) else data.get('value', 0)
  self.base_capacity = float(val)
  ```
  With: `self.base_capacity = self._parse_primary_value(data)`
- [ ] ShieldRegeneration `__init__` (lines 42-43): Replace same pattern → `self.base_rate = self._parse_primary_value(data)`
- [ ] ToHitAttackModifier `__init__` (lines 65-66): Replace → `self.value = self._parse_primary_value(data)`
- [ ] ToHitDefenseModifier `__init__` (lines 91-92): Replace → `self.value = self._parse_primary_value(data)`
- [ ] EmissiveArmor `__init__` (lines 114-115): Replace → `self.amount = int(self._parse_primary_value(data))`
- [ ] Run tests
**Notes:** Each replacement removes the `val` temporary variable. The `int()` cast for EmissiveArmor stays.

#### Task 2.2: Migrate propulsion.py (3 `__init__` + 3 `sync_data`) [Simple]
**File:** `game/simulation/components/abilities/propulsion.py`
**Tests:** `pytest tests/unit/entities/test_abilities.py tests/unit/simulation/components/abilities/ tests/integration/test_strategic_abilities.py -v`
- [ ] CombatPropulsion `__init__` (lines 17-18): Replace → `self.base_thrust = self._parse_primary_value(data)`
- [ ] CombatPropulsion `sync_data` (line 23): Replace `val = data if isinstance(data, (int, float)) else data.get('value', 0) if isinstance(data, dict) else 0` → `val = self._parse_primary_value(data)` (keep existing `self.base_thrust = float(val)` on next line, or inline)
- [ ] ManeuveringThruster `__init__` (lines 46-47): Replace → `self.base_turn_rate = self._parse_primary_value(data)`
- [ ] ManeuveringThruster `sync_data` (line 52): Same replacement pattern
- [ ] StrategicMovement `__init__` (lines 93-94): Replace → `self.base_movement_points = self._parse_primary_value(data)`
- [ ] StrategicMovement `sync_data` (line 99): Same replacement pattern
- [ ] Run tests (include integration for strategic abilities)
**Notes:** The sync_data 3-way check is exactly what `_parse_primary_value()` does.

#### Task 2.3: Migrate crew.py (2 classes — skip CrewRequired) [Simple]
**File:** `game/simulation/components/abilities/crew.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_crew_abilities.py tests/unit/entities/test_abilities.py -v`
- [ ] CrewCapacity `__init__` (lines 16-17): Replace → `self.amount = int(self._parse_primary_value(data))`
- [ ] LifeSupportCapacity `__init__` (lines 38-39): Replace → `self.amount = int(self._parse_primary_value(data))`
- [ ] CrewRequired line 74: **SKIP** — leave as-is (nested `data.get('value', data.get('amount', 0))` fallback is intentional)
- [ ] Run tests
**Notes:**

---

### Phase 3: Final Verification [Simple]
**Objective:** Confirm zero regressions across full test suite.
**Status:** Not Started

#### Task 3.1: Full test suite run [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite
- [ ] Verify same pass count as baseline (7353+ tests)
- [ ] Verify no new warnings related to ability parsing
**Notes:**

#### Task 3.2: Verify duplication eliminated [Simple]
- [ ] Run: `grep -rn "val = data if isinstance" game/simulation/components/abilities/` — should only show CrewRequired line 74
- [ ] Verify `_parse_primary_value` is used in defense.py, propulsion.py, crew.py
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Run full test suite: `pytest tests/ -n 12` — all tests pass (establishes baseline)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass

### Final Verification
- [ ] Full test suite: `pytest tests/ -n 12` — same pass count as baseline
- [ ] Grep for old pattern — only CrewRequired remains
- [ ] Manual review: read `base.py` helper and confirm it handles all edge cases

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] Phase 1 complete (helper + tests)
- [ ] Phase 2 complete (10 `__init__` + 3 `sync_data` migrations)
- [ ] Phase 3 complete (full verification)
- [ ] All tests passing
- [ ] Old pattern only in CrewRequired (1 intentional exception)
- [ ] User verified
