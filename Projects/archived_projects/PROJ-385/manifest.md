# PROJ-385 File Manifest

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/core/formula_evaluator.py` | Production | Edit | LEG-04-001 — delete 3 aliases + comment header at lines 407-413 |
| `tests/.../test_formula_system.py` | Test | Migrate-callers | Replace alias imports with canonical `FormulaEvaluator.*` API |
| `tests/.../test_formula_overflow_underflow.py` | Test | Migrate-callers | Same |
| `tests/.../test_formula_exceptions.py` | Test | Migrate-callers | Same |
