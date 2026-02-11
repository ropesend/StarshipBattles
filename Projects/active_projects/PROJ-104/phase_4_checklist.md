# Phase 4: TargetEvaluator.evaluate (CC 49 → ≤10)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-104 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract per-rule-type evaluation into static helper methods

---

## Tasks

### Task 4.1: Extract distance rule handlers [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -x -q`

- [x] Create `_eval_distance_rule(ship, candidate, rule, distance_cache)` → `(val, match)` static method
- [x] Handles `nearest`, `farthest`, `distance` rule types (lines 176-209)
- [x] Verify tests

**Notes:** Extracted successfully

### Task 4.2: Extract mass/size rule handlers [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -x -q`

- [x] Create `_eval_mass_rule(candidate, rule)` → `(val, match)` static method
- [x] Handles `mass`, `largest`, `smallest`, `strongest`, `weakest` (lines 211-259)
- [x] Verify tests

**Notes:** Extracted successfully

### Task 4.3: Extract speed rule handlers [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -x -q`

- [x] Create `_eval_speed_rule(candidate, rule)` → `(val, match)` static method
- [x] Handles `fastest`, `slowest` (lines 226-232)
- [x] Verify tests

**Notes:** Extracted successfully

### Task 4.4: Extract damage rule handlers [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -x -q`

- [x] Create `_eval_damage_rule(candidate, rule, stat_helpers)` → `(val, match)` static method
- [x] Handles `most_damaged`, `least_damaged` (lines 234-249)
- [x] Verify tests

**Notes:** Extracted successfully

### Task 4.5: Extract capability rule handlers [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -x -q`

- [x] Create `_eval_capability_rule(ship, candidate, rule, stat_helpers, ship_capabilities_cache)` → `(val, match)` static method
- [x] Handles `has_weapons`, `least_armor`, `pdc_arc`/`missiles_in_pdc_arc` (lines 261-300)
- [x] Further split into _eval_has_weapons_rule, _eval_least_armor_rule, _eval_pdc_arc_rule
- [x] Verify tests

**Notes:** Split into 3 sub-methods to reduce CC below 15

### Task 4.6: Refactor `evaluate` as dispatcher loop [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -x -q`

- [x] `evaluate` loop becomes: get rule type → dispatch to `_eval_*` helper → check required → accumulate score
- [x] Use dict mapping rule types to handler methods
- [x] **CRITICAL:** Preserve `required` early termination in the loop (NOT in handlers)
- [x] Verify all 48 targeting tests pass

**Notes:** evaluate() now 25 lines, dispatches to 5 main rule handlers

### Task 4.7: Verify CC reduction [Simple]
- [x] Run `radon cc game/ai/target_evaluator.py -s -n C` — `evaluate` should be ≤10
- [x] Run full suite: `pytest tests/ -n 12 -q`

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `evaluate` CC ≤ 10 confirmed via radon (CC = 10)
- [x] All 8167 tests passing
- [x] All extracted methods are `@staticmethod`
- [x] No public API changes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
