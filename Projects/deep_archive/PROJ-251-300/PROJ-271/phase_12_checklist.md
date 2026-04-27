# Phase 12: Misc cleanup + semantic fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 12`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Risk:** LOW (cleanup + small semantic fix)
**Depends On:** None — independent cleanup
**Objective:** Address the LOW/MEDIUM-priority findings from the audit that don't warrant dedicated phases but shouldn't be left behind.

## Tasks

### Task 12.1: Shield pipeline — apply `capacity_mult` to flat bonus [Medium]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** extend `tests/unit/simulation/entities/test_ship_shield_bonus_add.py`

Audit finding M1 (architecture skeptic): the "virtual extra shield component" semantic is described in decisions.md — a flat bonus should behave identically to a real shield component. Real shield components multiply `base_capacity` by BOTH `capacity_mult` (general) AND `shield_capacity_mult` (specific). But PROJ-271 Phase 1.2 only applies `shield_capacity_mult` to the flat bonus.

- [ ] Write failing test: ship with `external_stats = {"shield_bonus_add": 50, "capacity_mult": 2.0, "shield_capacity_mult": 0.5}` → effective max_shields should be `base + flat * capacity_mult * shield_capacity_mult = base + 50 * 2.0 * 0.5 = base + 50`. (Or whatever the documented correct order is — confirm with user before committing.)
- [ ] Note: `capacity_mult` is not currently populated by any fleet aura, so this is a latent bug, not a live one. But fixing it preempts future surprise.
- [ ] Implement: multiply `flat_shield_bonus` by BOTH mults, matching `ShieldProjection.recalculate`.
- [ ] Verify all existing tests still pass.

### Task 12.2: Delete unused imports [Simple]
**File:** `game/simulation/entities/ship_stats.py:62-65`

- [ ] Verify `IResourceStorageAbility`, `IResourceGenerationAbility`, `IResourceConsumptionAbility`, `IWarpJumpAbility` are genuinely unused (IDE flagged them).
- [ ] Delete the imports.
- [ ] Run tests — no breakage.

### Task 12.3: Delete unused `_NUM_TEAMS` constant [Simple]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`

- [ ] Verify `_NUM_TEAMS = 2` constant has no callers (audit flagged as unused).
- [ ] Delete it OR wire it into `_route_team_for_scope` as the assumption anchor.

### Task 12.4: Delete dead `_noop_hook` [Simple]
**File:** `game/strategy/combat/spec_compiler.py`

- [ ] Audit flagged `_noop_hook` at line ~510 as dead. Verify no callers.
- [ ] Delete.

### Task 12.5: Delete dead Component-object branch [Simple]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`

- [ ] Audit M5: the `isinstance(comp_def, dict)` / else branch — registry only ever returns dicts in practice (not Component objects). Verify by grep.
- [ ] If confirmed dead, simplify: drop the isinstance check, access `comp_def["abilities"]` directly.
- [ ] Alternatively, keep it if future plans call for Component objects — document why.

### Task 12.6: Narrow TestNoLegacyScenarioSetup to cover base.py [Simple]
**File:** `tests/unit/simulation/test_unified_entry_guard.py`

- [ ] Test L3 (low): the existing guard excludes `base.py` and `__init__.py`. A `setup()` added to `base.py` (however unlikely) would escape detection.
- [ ] Tighten: keep the base.py exemption only for DOCSTRING references; fail on actual `def setup(` bodies.

### Task 12.7: Regression gate [Simple]

- [ ] `pytest tests/ --tb=no -q` — no net regression.
- [ ] Combat Lab fast + full green.

## Phase Completion Checklist

- [ ] All task checkboxes above are checked
- [ ] Shield pipeline now applies `capacity_mult` to flat bonus (or decision documented)
- [ ] Dead code deleted
- [ ] Regression gate green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
