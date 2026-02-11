# Phase 4: TargetEvaluator.evaluate (CC 49 → ≤10)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-104 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract per-rule-type evaluation into static helper methods

---

## Tasks

### Task 4.1: Extract distance rule handlers [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -x -q`

- [ ] Create `_eval_distance_rule(ship, candidate, rule, distance_cache)` → `(val, match)` static method
- [ ] Handles `nearest`, `farthest`, `distance` rule types (lines 176-209)
- [ ] Verify tests

**Notes:**

### Task 4.2: Extract mass/size rule handlers [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -x -q`

- [ ] Create `_eval_mass_rule(candidate, rule)` → `(val, match)` static method
- [ ] Handles `mass`, `largest`, `smallest`, `strongest`, `weakest` (lines 211-259)
- [ ] Verify tests

**Notes:**

### Task 4.3: Extract speed rule handlers [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -x -q`

- [ ] Create `_eval_speed_rule(candidate, rule)` → `(val, match)` static method
- [ ] Handles `fastest`, `slowest` (lines 226-232)
- [ ] Verify tests

**Notes:**

### Task 4.4: Extract damage rule handlers [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -x -q`

- [ ] Create `_eval_damage_rule(candidate, rule, stat_helpers)` → `(val, match)` static method
- [ ] Handles `most_damaged`, `least_damaged` (lines 234-249)
- [ ] Verify tests

**Notes:**

### Task 4.5: Extract capability rule handlers [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -x -q`

- [ ] Create `_eval_capability_rule(ship, candidate, rule, stat_helpers, ship_capabilities_cache)` → `(val, match)` static method
- [ ] Handles `has_weapons`, `least_armor`, `pdc_arc`/`missiles_in_pdc_arc` (lines 261-300)
- [ ] Verify tests

**Notes:**

### Task 4.6: Refactor `evaluate` as dispatcher loop [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -x -q`

- [ ] `evaluate` loop becomes: get rule type → dispatch to `_eval_*` helper → check required → accumulate score
- [ ] Use dict mapping rule types to handler methods
- [ ] **CRITICAL:** Preserve `required` early termination in the loop (NOT in handlers)
- [ ] Verify all 48 targeting tests pass

**Notes:**

### Task 4.7: Verify CC reduction [Simple]
- [ ] Run `radon cc game/ai/target_evaluator.py -s -n C` — `evaluate` should be ≤10
- [ ] Run full suite: `pytest tests/ -n 12 -q`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `evaluate` CC ≤ 10 confirmed via radon
- [ ] All 8167 tests passing
- [ ] All extracted methods are `@staticmethod`
- [ ] No public API changes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
