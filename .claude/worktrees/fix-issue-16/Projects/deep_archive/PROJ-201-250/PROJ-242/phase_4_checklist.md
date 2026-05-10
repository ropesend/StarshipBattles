# Phase 4 Checklist: Delete Old Code and Final Cleanup
**Status:** Complete

### Task 4.1: Clean up formula_system.py [Simple]
**File:** `game/simulation/formula_system.py`
**Tests:** `pytest tests/unit/simulation/test_formula_evaluator.py tests/unit/systems/test_formula_system.py -v`
- [x] Delete string constant `FORMULA_ERROR_SYNTAX = "F001"`
- [x] Delete string constant `FORMULA_ERROR_UNDEFINED = "F002"`
- [x] Delete string constant `FORMULA_ERROR_RUNTIME = "F003"`
- [x] Delete string constant `FORMULA_ERROR_SECURITY = "F004"`
- [x] Delete old `validate_formula()` function
- [x] Delete old `evaluate_math_formula()` function
- [x] Delete old `safe_evaluate_math_formula()` function
- [x] Update module docstring to describe FormulaEvaluator as the primary API
- [x] Add module-level convenience aliases for backward compatibility with test imports
- [x] Run formula tests -- 138 passed
**Notes:** Used module-level aliases per plan recommendation. All existing test imports work without changes.

### Task 4.2: Clean up modifier_effects.py [Simple]
**File:** `game/simulation/components/modifier_effects.py`
**Tests:** `pytest tests/unit/simulation/components/test_modifier_effects.py tests/unit/modifiers/ -v`
- [x] Verify `evaluate_formula` and `validate_formula` are thin delegations
- [x] Verify no direct `eval(` call remains in file
- [x] Verify `import math` is removed
- [x] Verify `import ast` is removed
- [x] Verify `from game.core.error_codes import ErrorCode` is removed
- [x] Run tests -- 283 passed
**Notes:**

### Task 4.3: Final verification [Simple]
**Tests:** Full test suite
- [x] Grep for direct `eval(` calls in `game/simulation/` -- only in `FormulaEvaluator.evaluate()`
- [x] Grep for `FORMULA_ERROR_SYNTAX` etc. -- not found anywhere in production code
- [x] Grep for old function imports -- not found in `game/` (only in `tests/` via aliases)
- [x] Run full test suite: `pytest tests/` -- 14403 passed, 2 skipped, 0 failures
- [x] Check docs for formula references -- no updates needed (public API unchanged)
- [x] Checked `docs/01_ARCHITECTURE.md` and `docs/02_PATTERNS.md` -- no formula-specific entries to update
**Notes:** The sharded runner (`test_sharded.py`) shows all shards as FAILED due to pre-existing `test_build_order_command_handler.py` import error (unrelated to PROJ-242). Direct `pytest tests/` run confirms 14403 passed, 0 failures.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
