# PROJ-385 Implementation Review

**Project:** PROJ-385 - Legacy removal: formula_evaluator backward-compat aliases  
**Review date:** 2026-05-09  
**Reviewer:** Codex  
**Verdict:** Code goal met; audit passes for the narrow implementation, with audit-evidence/checklist caveats.

## Validation Result

- `python Projects/scripts/validate_audit_ready.py PROJ-385`: PASSED.
  - Warning: project index still reports `PROJ-385` as `Planning`.
- `python Projects/scripts/validate_phase.py PROJ-385 1`: PASSED.
  - Warnings: Tasks 1.1, 1.2, and 1.3 are complete but have empty Notes.

## Tests Run

- `pytest tests/unit/systems/test_formula_system.py tests/unit/systems/test_formula_overflow_underflow.py tests/unit/simulation/test_formula_exceptions.py`: 80 passed.
- `pytest tests/ -k formula`: 414 passed.
- `python -c "from game.core import formula_evaluator as f; print(hasattr(f, 'evaluate_math_formula'), hasattr(f, 'safe_evaluate_math_formula'), hasattr(f, 'validate_formula'))"`: `False False False`.
- `rg -n "\b(evaluate_math_formula|safe_evaluate_math_formula)\b" game tests combat_lab Tools`: no matches.

I did not rerun the full sharded suite. The project state records a prior sharded run as `19084 passed, 3 pre-existing unrelated failures`, which is not a clean full-suite pass.

## Plan Goals vs Actual Implementation

### Goal: migrate test callers to `FormulaEvaluator.*`

Met. The three scoped test files now import and call the canonical class API:

- `tests/unit/systems/test_formula_system.py:13` imports `FormulaEvaluator`, with calls to `FormulaEvaluator.evaluate`, `FormulaEvaluator.safe_evaluate`, and `FormulaEvaluator.validate`.
- `tests/unit/systems/test_formula_overflow_underflow.py:11` imports `FormulaEvaluator`, with overflow/underflow tests using `FormulaEvaluator.evaluate` and `FormulaEvaluator.safe_evaluate`.
- `tests/unit/simulation/test_formula_exceptions.py:15`, `:25`, `:35`, and other local imports use `FormulaEvaluator` directly.

Focused and formula-wide tests passed.

### Goal: delete the three module-level aliases

Met. `game/core/formula_evaluator.py` defines `FormulaEvaluator.evaluate` at line 234, `FormulaEvaluator.validate` at line 316, and `FormulaEvaluator.safe_evaluate` at line 379. The file ends at line 404 after `safe_evaluate`; the former module-level alias block is gone. Runtime attribute checks also confirmed the old module-level names no longer exist.

## Literal Checklist Execution

- Task 1.1 is mostly satisfied for the two unique alias names `evaluate_math_formula` and `safe_evaluate_math_formula`, which have no remaining matches under `game`, `tests`, `combat_lab`, or `Tools`.
- Task 1.2 is satisfied. `pytest tests/ -k formula` passed with 414 tests.
- Task 1.3 is satisfied for alias deletion, but not literally satisfied for the recorded grep/full-suite evidence. The checklist says the broad grep over `.` returns zero hits and the full sharded suite passes. Current evidence contradicts both statements as written.
- Phase metadata is internally close but not perfect. `validate_phase.py` passed, but it warned that all three tasks have empty Notes. The top-level plan verification checklist at `Projects/active_projects/PROJ-385/plan.md:51-55` is still unchecked.

## Findings

### Major: checklist verification overclaims what was actually verified

**Evidence:** `Projects/active_projects/PROJ-385/phase_1_checklist.md:35` says the full sharded suite passes and that `grep -rn -E "(evaluate_math_formula|safe_evaluate_math_formula|validate_formula)\b" .` returns zero hits. `Projects/active_projects/PROJ-385/plan.md:21` instead records `19084 passed, 3 pre-existing unrelated failures`, which is not a passing full-suite result. The broad grep also cannot return zero because unrelated, legitimate `validate_formula` APIs remain, for example `game/simulation/components/modifier_effects.py:225` and `game/simulation/components/modifier_schema.py:237`.

**Impact:** The implementation goal is still met, but the audit trail is weaker than the checklist claims. A future reviewer following the literal checklist will see false failures and no clean full-suite receipt.

**Recommended follow-up:** Record a targeted verification command for the removed aliases, such as checking `game/core/formula_evaluator.py` and runtime module attributes, and either attach a clean full-suite receipt or explicitly retain the known unrelated failures as a caveat.

### Minor: the initial plan used an over-broad symbol check

**Evidence:** `Projects/active_projects/PROJ-385/plan.md:54` treats all references to `validate_formula` as if they are references to the deleted alias. `ModifierEffectEvaluator.validate_formula` is a separate method, currently used by production validation at `game/simulation/components/modifier_schema.py:237`.

**Impact:** The plan failed to account for unrelated symbols sharing the same simple name. This did not break the implementation because the in-scope alias was deleted, but it made the stated zero-reference acceptance criterion inaccurate.

**Recommended follow-up:** Scope the check to module-level exports in `game/core/formula_evaluator.py` or to import statements from that module, not all `validate_formula` occurrences.

### Minor: manifest paths are not exact enough for audit traceability

**Evidence:** `Projects/active_projects/PROJ-385/manifest.md:8-10` lists `tests/.../test_formula_system.py`, `tests/.../test_formula_overflow_underflow.py`, and `tests/.../test_formula_exceptions.py` instead of exact paths.

**Impact:** This did not block review because the files were easy to find with `rg`, but the manifest is less useful as an audit artifact than it should be.

**Recommended follow-up:** Use exact repo-relative paths in manifests even for small projects.

## Plan Gaps and Missed Assumptions

- The plan assumed `validate_formula` was unique to the legacy alias cluster. It was not; `ModifierEffectEvaluator.validate_formula` remains a legitimate API.
- The plan conflated "no remaining removed alias exports" with "no remaining textual occurrences of any old simple name." The former is the correct acceptance criterion.
- The plan did not define how to handle known unrelated full-suite failures while still marking a checklist item as "full sharded suite passes."
- The manifest did not preserve exact test paths, which made traceability dependent on search rather than the project artifact.

## Residual Risks

- No clean full-suite run was produced during this review. Focused formula coverage is green, but repository-wide regression status remains dependent on the prior reported sharded run with 3 unrelated failures.
- Because project files are out of scope for this review write-up, the inaccurate checklist/plan wording remains in place.
- There may be external or ad hoc scripts importing the old aliases outside `game`, `tests`, `combat_lab`, and `Tools`; I did not search ignored/generated paths or external consumers.

## Summary

The actual code change is correct for PROJ-385's narrow intent: the old module-level formula evaluator aliases are gone, the scoped tests call `FormulaEvaluator.*`, and focused formula tests pass. The main issue is not the implementation but the audit trail: the checklist overstates full-suite status and uses a broad grep that is false because another valid `validate_formula` method exists.
