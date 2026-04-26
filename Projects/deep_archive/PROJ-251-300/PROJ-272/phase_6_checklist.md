# Phase 6: Remove `capacity_mult` time-bomb read (HIGH — E2E H-2)

**Status:** Complete
**Risk:** LOW (reverts recent Phase 12.1 change; no current aura populates `capacity_mult`)
**Depends On:** None
**Objective:** PROJ-271 Phase 12.1 added `capacity_mult` to the flat-bonus scaling in `ship_stats.py::_apply_aggregated_stats` to mirror `ShieldProjection.recalculate`. But `capacity_mult` isn't populated by any fleet aura today. The read is a latent double-multiply: if ANY future aura populates it, flat shield bonus silently multiplies twice. Revert to `shield_capacity_mult` only.

See decisions.md for full rationale. User-clarified intent ("virtual extra shield component") is honored by `shield_capacity_mult` alone for current aura inventory.

## Tasks

### Task 6.1: Revert the read [Simple]
**File:** `game/simulation/entities/ship_stats.py` `_apply_aggregated_stats`

- [ ] Remove `capacity_mult = external_stats.get('capacity_mult', 1.0)` read.
- [ ] Change `ship.max_shields += flat_shield_bonus * capacity_mult * shield_cap_mult` → `ship.max_shields += flat_shield_bonus * shield_cap_mult`.
- [ ] Update the comment to reflect the revert + reference this phase.

### Task 6.2: Update pipeline-ordering test [Simple]
**File:** `tests/unit/simulation/entities/test_ship_shield_bonus_add.py`

- [ ] Delete `test_flat_bonus_stacks_with_capacity_mult_too` (added in Phase 12.1) OR flip its assertion to prove flat bonus is NOT scaled by capacity_mult.
- [ ] Other pipeline tests should still pass unchanged.

### Task 6.3: Update docs [Simple]
**Files:** `docs/systems/combat_simulation.md` "Shield Stat Pipeline Ordering" section; `docs/systems/ability_reference.md` SHIELD_BONUS_ADD row

- [ ] Formula changes from `(base + flat) × capacity_mult × shield_capacity_mult` → `(base + flat) × shield_capacity_mult`.
- [ ] Note this is a deliberate scope decision — revisit if a real `capacity_mult` team aura ever appears.

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] Time-bomb removed
- [ ] Docs + tests consistent
- [ ] Update plan.md
