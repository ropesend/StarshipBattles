# PROJ-242 Design Pattern Analysis Report

**Date:** 2026-04-10
**Reviewer Role:** Design Pattern Analyst
**Scope:** Verify implementation matches documented architecture patterns and conventions

---

## Executive Summary

PROJ-242 (Unified Formula Evaluation System) is functionally complete and well-executed. The core goal -- merging two parallel formula evaluation systems into a single `FormulaEvaluator` class -- was achieved correctly. However, the project was designed against a codebase state that predated PROJ-257 (Foundation), which subsequently moved `FormulaEvaluator` from `game/simulation/formula_system.py` to `game/core/formula_evaluator.py` and replaced `eval()` with an AST tree walker. As a result, the plan's assumptions about file placement were superseded, and some artifacts of the transition remain.

**Findings:** 5 total (1 moderate, 2 minor, 2 informational)

---

## Findings

### DP-001: Plan vs. Reality -- File Placement Conflict with PROJ-257

**Plan Assumption:** PROJ-242's plan specifies `game/simulation/formula_system.py` as the home for `FormulaEvaluator` (Decision: "Keep unified evaluator in `formula_system.py`"). Phase 1 tasks describe adding `FormulaContext` and `FormulaEvaluator` to `formula_system.py`.

**Current Reality:** PROJ-257 (completed 2026-02-26) extracted `FormulaEvaluator` and `FormulaContext` to `game/core/formula_evaluator.py` and replaced `eval()` with an AST tree walker. PROJ-242 (completed 2026-04-05) ran afterward and built its unified evaluator directly in `game/core/formula_evaluator.py`. The plan was never updated to reflect this, but the implementation correctly placed the code in core.

**Impact:** None at the code level -- the implementation is in the correct location (`game/core/`). The stale plan text could confuse future agents reading the project docs, since it describes adding code to `formula_system.py` while the implementation lives in `formula_evaluator.py`.

**Evidence:**
- `game/core/formula_evaluator.py` (414 lines) -- canonical implementation with AST walker, FormulaEvaluator, FormulaContext
- `game/simulation/formula_system.py` (19 lines) -- re-export shim only
- `docs/01_ARCHITECTURE.md:113` correctly documents: `formula_system.py (re-export shim -> game.core.formula_evaluator)`
- All 6 production callers import from `game.core.formula_evaluator`, not `game.simulation.formula_system`

**Proposed Resolution:** No code changes needed. Plan document is historical and does not need updating since the project is marked complete.

---

### DP-002: Backward-Compatible Aliases Violate System Migration Policy (Moderate)

**Plan Assumption:** PROJ-242 plan Decision #8: "Module-level aliases for backward compatibility with test imports." Phase 4 Task 4.1 note: "Used module-level aliases per plan recommendation."

**Current Reality:** Three backward-compatible aliases exist in TWO locations:

1. `game/core/formula_evaluator.py` (lines 411-413):
   ```python
   evaluate_math_formula = FormulaEvaluator.evaluate
   safe_evaluate_math_formula = FormulaEvaluator.safe_evaluate
   validate_formula = FormulaEvaluator.validate
   ```

2. `game/simulation/formula_system.py` (lines 17-19):
   ```python
   evaluate_math_formula = FormulaEvaluator.evaluate
   safe_evaluate_math_formula = FormulaEvaluator.safe_evaluate
   validate_formula = FormulaEvaluator.validate
   ```

The aliases in `game/core/formula_evaluator.py` are **dead code** -- no file imports them from that location (verified via grep). The aliases in `game/simulation/formula_system.py` are used by ~30 test import sites across 3 test files:
- `tests/unit/systems/test_formula_system.py` (13 imports)
- `tests/unit/simulation/test_formula_exceptions.py` (16 imports)  
- `tests/unit/systems/test_formula_overflow_underflow.py` (3 imports)

**Impact:** This conflicts with the project's System Migration Policy (CLAUDE.md and docs/03_CONVENTIONS.md section 6.5): "When a new system replaces an old one, ERADICATE the old system completely. DO NOT add backward compatibility layers 'just in case'."

The aliases are backward compatibility layers. The tests should be migrated to import `FormulaEvaluator` directly from `game.core.formula_evaluator` and use `FormulaEvaluator.evaluate()` / `.safe_evaluate()` / `.validate()` instead of the old function names.

**Proposed Resolution:**
1. Delete the 3 alias lines from `game/core/formula_evaluator.py` (dead code, zero consumers)
2. Migrate the 3 test files to use `FormulaEvaluator.*` directly from `game.core.formula_evaluator`
3. Delete the 3 alias lines from `game/simulation/formula_system.py`
4. At that point, `formula_system.py` would only re-export `FormulaEvaluator`, `FormulaContext`, and the constant sets -- could potentially be deleted entirely if the remaining test file (`test_formula_evaluator.py`) is updated to import from `game.core.formula_evaluator`

---

### DP-003: Test Logger Name References Wrong Module (Minor)

**Plan Assumption:** Tests should correctly verify logging behavior.

**Current Reality:** `tests/unit/simulation/test_formula_evaluator.py` line 371 uses:
```python
with caplog.at_level(logging.WARNING, logger="game.simulation.formula_system"):
```

But the actual logger in `game/core/formula_evaluator.py` line 24 is:
```python
logger = logging.getLogger(__name__)  # = "game.core.formula_evaluator"
```

The test passes because `caplog` captures all log records regardless of the logger name passed to `at_level()` -- the name parameter only sets the minimum level on that specific logger, but `caplog.records` captures from all loggers. So the assertion `any("bad_var" in record.message for record in caplog.records)` succeeds by inspecting records from the actual logger.

**Impact:** The test works but for the wrong reason. If pytest's caplog behavior changes, or if someone reads the test and assumes the formula system logs to `game.simulation.formula_system`, they'd be misled. This is a code smell, not a correctness bug.

**Proposed Resolution:** Update the logger name to `"game.core.formula_evaluator"` to match the actual logger.

---

### DP-004: FormulaEvaluator Correctly Excluded from ApplicationContext (Informational)

**Plan Assumption:** Not explicitly discussed in PROJ-242 plan.

**Current Reality:** `FormulaEvaluator` is a stateless class with only `@classmethod` methods. It is not registered in `ApplicationContext` (verified: `game/context.py` has no reference to it).

**Impact:** None. This is the correct design per PROJ-258 (ApplicationContext) patterns -- ApplicationContext manages stateful services that need lifecycle management (10 services total). `FormulaEvaluator` has no state, no initialization, and no cleanup needs. Stateless utility classes should NOT be in the DI container.

**Proposed Resolution:** None needed. Design is correct.

---

### DP-005: Naming and Convention Compliance (Informational)

**Plan Assumption:** Code should follow docs/03_CONVENTIONS.md naming patterns.

**Current Reality:** Verified compliance across multiple dimensions:

| Convention | Status | Notes |
|------------|--------|-------|
| Class naming (PascalCase) | PASS | `FormulaEvaluator`, `FormulaContext`, `ModifierEffect` |
| Module naming (snake_case) | PASS | `formula_evaluator.py`, `modifier_effects.py` |
| Layer dependencies | PASS | `formula_evaluator.py` imports only from `game.core` (standard lib + core exceptions/error_codes) |
| Type hints on signatures | PASS | All public methods have full type annotations |
| Docstrings on public APIs | PASS | Class-level and method-level docstrings present |
| Function size (<50 lines) | PASS | `evaluate()` is 47 lines including error handling |
| ErrorCode enum (not strings) | PASS | All error codes use `ErrorCode.*.value` |
| Frozen dataclass for DTOs | PASS | `FormulaContext` is `@dataclass(frozen=True)` |
| Import conventions | PASS | Three-group ordering, no wildcard imports |
| `__all__` / exports | N/A | `formula_evaluator.py` doesn't define `__all__` but is not a package `__init__.py` |

**Impact:** None. Implementation follows all documented conventions.

**Proposed Resolution:** None needed.

---

## Summary Table

| ID | Title | Severity | Action Needed |
|----|-------|----------|---------------|
| DP-001 | Plan vs. Reality -- File Placement | Info | None (plan is historical) |
| DP-002 | Backward-Compatible Aliases | Moderate | Delete dead aliases in core; migrate test imports; consider deleting shim |
| DP-003 | Test Logger Name Wrong | Minor | Update logger name in test |
| DP-004 | ApplicationContext Exclusion | Info | None (correct as-is) |
| DP-005 | Naming/Convention Compliance | Info | None (fully compliant) |

---

## Overall Assessment

PROJ-242 successfully achieved its primary goal of unifying two parallel formula evaluation systems into a single `FormulaEvaluator` class. The implementation is clean, well-tested (58 new tests plus 380+ existing tests passing), and follows all documented patterns and conventions.

The main concern is **DP-002** (backward-compatible aliases). The project's own plan explicitly called for "eradicating old systems" but then chose to keep aliases for test import convenience. This creates exactly the kind of compatibility layer the migration policy warns against. The aliases are harmless functionally, but they signal to future developers that the old function names are still valid API, and they keep the `formula_system.py` shim alive when it could potentially be deleted entirely.

The PROJ-257 interaction (DP-001) was handled well at the implementation level -- the code landed in the right place -- even though the plan documents were not updated to reflect the changed landscape.
