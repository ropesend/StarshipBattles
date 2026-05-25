# Phase 1: CAT-9 simplification (core)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-495 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace remaining CAT-9 simplification patterns in core-mechanical tests. Inherited from PROJ-480 Phase 1.

Line refs advisory — Phase 0 should have refreshed them. Re-grep before editing.

---

## Tasks

### Task 1.1: test_weapon_firing_system.py — inline ship construction
**File:** `tests/unit/simulation/combat/test_weapon_firing_system.py`
**Tests:** `pytest tests/unit/simulation/combat/test_weapon_firing_system.py`
**Origin:** PROJ-480 T1.16

- [x] Create `_make_ship_mock(**kwargs)` factory with defaults for the 6+ recurring attrs (team_id, position, velocity, angle, total_shots_fired, max_targets, secondary_targets). Replace inline constructions in 15+ tests (PROJ-480 cited lines 100-115+).
- [x] Verify: 26 tests pass; ~17 inline construction sites replaced with `_make_ship_mock(**overrides)`.

### Task 1.2: test_damage_calculator.py — mock_ship factory unused
**File:** `tests/unit/simulation/combat/test_damage_calculator.py`
**Tests:** `pytest tests/unit/simulation/combat/test_damage_calculator.py`
**Origin:** PROJ-480 T1.21

- [x] Use the existing `mock_ship` factory at PROJ-480-cited lines 357-370 in the later test classes (lines 831+); currently those classes construct ship via inline MagicMock instead. Extended factory signature with optional kwargs for `emissive_armor` / `shield_regenerating_armor` / `current_shields` / `max_shields` / etc.
- [x] Verify: 48 tests pass; 5 inline construction sites in `TestCombinedArmorScenarios`, `TestShieldRegeneratingArmorEdgeCases`, `TestShieldDamageEdgeCases`, `TestDamageCallbackConditions` converted to factory calls.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2 (CAT-8 needless complexity)
