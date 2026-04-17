# Phase 3: TargetEvaluator projectile-candidate guards (HIGH — H2 code/tests)

**Status:** Complete
**Risk:** LOW (additive guards; no behavior change for non-projectile candidates)
**Depends On:** None
**Objective:** `TargetEvaluator._eval_has_weapons_rule` fallback path (line ~177) + `_eval_least_armor_rule` (line ~189) call ship-only methods (`get_components_by_ability`, `get_components_by_layer`) on `candidate`. When a Projectile (missile) is the candidate, these crash with AttributeError — the outer try/except in `_score_and_sort_enemies` catches and silently DROPS the missile from scoring. Fix: guard rules with `is_combat_ship`, return a sensible default for non-ships (usually "rule doesn't apply, score 0, not required").

This is the same bug class as the `_build_capabilities_cache` crash from earlier today — but in a different layer. `_build_capabilities_cache` fix prevents the crash on the BUILD path; the evaluator fallback path still has it.

## Tasks

### Task 3.1: Failing test reproducing silent-drop [Medium]
**File:** `tests/unit/ai/target_evaluator/test_target_evaluator.py` (or similar)

- [ ] Failing test: `TargetEvaluator.evaluate(ship, projectile_candidate, rules, ship_capabilities_cache={})` with a rule that triggers `_eval_has_weapons_rule` → should NOT raise AttributeError; should return a score (0 or -inf) with the rule's `required` respected.
- [ ] Same for `_eval_least_armor_rule`.
- [ ] Run — fails (AttributeError is raised, or score returned is garbage).

### Task 3.2: Add `is_combat_ship` guards [Medium]
**File:** `game/ai/target_evaluator.py`

- [ ] Import `is_combat_ship` from entity protocols.
- [ ] `_eval_has_weapons_rule` fallback: if `not is_combat_ship(candidate)`, return `(0, not required)` — projectile has no weapons-in-ship-sense; rule treats as "no weapons".
- [ ] `_eval_least_armor_rule`: if `not is_combat_ship(candidate)`, return `(0, True)` — armor doesn't apply to projectiles.
- [ ] Audit other rules in the file for the same pattern.

### Task 3.3: Remove silent-drop try/except (or narrow it) [Medium]
**File:** `game/ai/controller.py` `_score_and_sort_enemies`

- [ ] The outer `try/except (AttributeError, TypeError)` at line ~245 currently catches and logs. After Phase 3.2 guards, this catch should only fire for UNEXPECTED errors. Consider narrowing OR adding explicit logging that says "evaluator bug detected" rather than generic "skipping target".

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] No AttributeError on projectile candidates in evaluator
- [ ] Update plan.md
