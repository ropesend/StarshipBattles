# Phase 1: Migrate test imports + delete aliases

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-385 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate ~118 test invocations (across ~23 import sites in 3 files) of the `formula_evaluator` backward-compat aliases to the canonical `FormulaEvaluator.*` API, then delete the alias block (lines 407-413).

---

## Tasks

### Task 1.1: Enumerate test callers
**File:** `tests/`
**Tests:** —

- [x] Run `grep -rn -E "(evaluate_math_formula|safe_evaluate_math_formula|validate_formula)\b" tests/` to enumerate every import site and call site
- [x] Confirm zero hits in `game/`, `combat_lab/`, `Tools/` (LEG-04-001)

### Task 1.2: Migrate test files to canonical API
**File:** `tests/.../test_formula_system.py`, `tests/.../test_formula_overflow_underflow.py`, `tests/.../test_formula_exceptions.py`
**Tests:** `pytest tests/ -k formula`

- [x] Replace each `from game.core.formula_evaluator import evaluate_math_formula` with `from game.core.formula_evaluator import FormulaEvaluator`
- [x] Update each call site: `evaluate_math_formula(...)` → `FormulaEvaluator.evaluate(...)`, `safe_evaluate_math_formula(...)` → `FormulaEvaluator.safe_evaluate(...)`, `validate_formula(...)` → `FormulaEvaluator.validate(...)`
- [x] Run `pytest tests/ -k formula` and confirm pass

### Task 1.3: Delete the alias block
**File:** `game/core/formula_evaluator.py`
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Delete lines 407-413 (LEG-04-001) — the 3 aliases and the "Backward-compatible aliases for existing test imports" comment header
- [x] Verify: full sharded suite passes; `grep -rn -E "(evaluate_math_formula|safe_evaluate_math_formula|validate_formula)\b" .` returns zero hits

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
