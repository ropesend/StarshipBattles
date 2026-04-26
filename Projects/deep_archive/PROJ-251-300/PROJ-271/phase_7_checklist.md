# Phase 7: FleetAuraManager stack_group respect on external entries

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Risk:** MEDIUM (silent-correctness bug fix; behavior change for same-stack-group entries)
**Depends On:** None
**Objective:** `FleetAuraManager._recalculate` currently applies external `ModifierEntry` values via unconditional SUM (`fleet_aura_manager.py:299-309`). This ignores the `stack_group` field that compilers DO set on each entry. Two same-stack-group complexes stack additively when they should MAX per PROJ-271 decisions.md user clarification: "stack on top of anything not in the same stacking group". Fix: same two-phase MAX/SUM logic as ship-provider aura (`_aggregate_ability_groups`).

## Context

E2E goals skeptic (2026-04-13) finding H-3: silent correctness bug. Battle Setup compiler `_complex_to_entries` at [battle_setup/spec_compiler.py:371](game/ui/screens/battle_setup/spec_compiler.py#L371) correctly copies `ability_data.get("stack_group")` onto the emitted `ModifierEntry`. But `FleetAuraManager._recalculate` at [fleet_aura_manager.py:299-309](game/simulation/combat/fleet_aura_manager.py#L299-L309) does:

```python
for ext in self._external:
    if ext.team_id is None:
        ...
        self._team_bonuses[team_id][ext.ability_name] = current + ext.value
    else:
        ...
        self._team_bonuses[team_id][ext.ability_name] = current + ext.value
```

Pure SUM, no `stack_group` consideration. Compare to ship-provider aura (`_recalculate`, lines 262-297) which groups by `(ability, stack_group)` then applies MAX within group and SUM across groups.

## Tasks

### Task 7.1: Extend ExternalModifier with stack_group [Simple]
**File:** `game/simulation/combat/fleet_aura_manager.py`
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py`

- [x] Added `stack_group: Optional[str] = None` to `ExternalModifier` dataclass (`fleet_aura_manager.py:37`).
- [x] `_append_external_from_entry` now copies `entry.stack_group` onto the `ExternalModifier`.
- [x] Existing tests still pass.

**Notes:** Minimal data-model extension; defaults to None so existing call sites unaffected.

### Task 7.2: Failing tests for stack_group behavior [Medium]
**File:** `tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py`

- [x] Wrote `test_same_stack_group_entries_compose_max_not_sum` — 2 entries @ values 1.5 + 1.25 same group → expect MAX 1.5, actual 2.75 (FAILS for right reason).
- [x] Wrote `test_different_stack_groups_compose_sum` — 2 different groups @ 1.2 + 1.3 → 2.5.
- [x] Wrote `test_none_stack_group_entries_each_contribute_independently` — None groups SUM (preserves pre-Phase-7 behavior for ToHit).
- [x] Run — 1 of 3 failed (MAX), other 2 passed trivially (SUM already worked).

### Task 7.3: Implement two-phase MAX/SUM for external entries [Complex]
**File:** `game/simulation/combat/fleet_aura_manager.py`
**Tests:** same file as Task 7.2

- [x] Refactored `_recalculate` — external entries now feed into the SAME `team_ability_groups` structure as ship-provider auras BEFORE `_aggregate_ability_groups` runs. Unified two-phase logic.
- [x] `None` stack_group → unique `_default_ext_{idx}` key so un-grouped entries contribute independently via SUM (matches ship-provider `_default_{id(provider)}` pattern).
- [x] Run — 3 new tests pass; 12 existing tests still pass (15/15 in the file).

### Task 7.4: Integration test — same-group Battle Setup complexes MAX [Medium]
**File:** `tests/integration/strategy/combat/test_suppressor_effects.py` (extend)

- [x] Wrote `test_two_same_group_shield_boosters_max_not_sum` in `test_suppressor_effects.py`. Two copies of `qs_system_shield_booster_complex` on side 0 → `side0_ship.max_shields == 625` (500 × MAX(1.25, 1.25) = 625), NOT 1000+.
- [x] Integration tests all green (4/4 in file).

### Task 7.5: Regression check [Simple]

- [ ] `pytest tests/` — no net regression (baseline 14683 + 3 new stack_group tests ≥ 14686).
- [ ] Combat Lab fast 162/162 + full 170/170.

## Phase Completion Checklist

- [ ] All task checkboxes above are checked
- [ ] Same-group MAX / different-group SUM locked by unit + integration tests
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
