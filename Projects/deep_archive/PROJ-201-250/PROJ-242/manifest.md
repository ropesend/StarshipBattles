# PROJ-242 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated during implementation.

## Files

| File | Type | Notes |
|------|------|-------|
| game/simulation/formula_system.py | Production | Added FormulaContext, FormulaEvaluator; deleted old functions; added aliases |
| game/simulation/components/modifier_effects.py | Production | Delegated evaluate_formula/validate_formula to FormulaEvaluator; removed math/ast/ErrorCode imports |
| game/simulation/components/component.py | Production | Removed vestigial safe_evaluate_math_formula import |
| game/simulation/components/component_stats_calculator.py | Production | Migrated to FormulaEvaluator.safe_evaluate |
| game/simulation/components/component_resource_manager.py | Production | Migrated to FormulaEvaluator.safe_evaluate |
| game/simulation/components/abilities/weapons.py | Production | Migrated to FormulaEvaluator.safe_evaluate |
| game/strategy/services/ship_stats_calculator.py | Production | Migrated to FormulaEvaluator.safe_evaluate |
| tests/unit/simulation/test_formula_evaluator.py | Test | New - 58 tests for FormulaEvaluator and FormulaContext |
