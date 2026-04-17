# Phase 8: Fix `_apply_bonuses` zero-value filter (MEDIUM — Code M1)

**Status:** Complete
**Risk:** LOW (bug fix with minor semantic change; no current aura produces 0.0)
**Depends On:** None
**Objective:** `FleetAuraManager._apply_bonuses` at line ~328 uses `{k: v for k, v in totals.items() if v}` — `if v` is truthy filter that drops 0.0 values. A legitimate `damage_mult=0.0` suppressor (meaning "enemy ships deal 0 damage") would be silently discarded. Replace with `if v is not None` to keep zero values.

No current aura produces 0.0, but the bug is a correctness regression waiting to happen.

## Tasks

### Task 8.1: Failing test for zero-value preservation [Simple]
**File:** `tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py`

- [ ] Failing test: external entry `damage_mult=0.0` on per_team[0] → ship 0's external_stats has `damage_mult == 0.0`, NOT missing.
- [ ] Run — fails.

### Task 8.2: Fix filter [Simple]
**File:** `game/simulation/combat/fleet_aura_manager.py` `_recalculate` / `_apply_bonuses`

- [ ] Change `{k: v for k, v in totals.items() if v}` → `{k: v for k, v in totals.items() if v is not None}`.
- [ ] Verify no other filters in the file have the same anti-pattern.

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] Zero-value preservation locked
- [ ] Update plan.md
