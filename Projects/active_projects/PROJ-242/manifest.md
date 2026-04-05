# PROJ-242 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/simulation/formula_system.py | Production | Add FormulaEvaluator class, delete old functions, add aliases |
| game/simulation/components/modifier_effects.py | Production | Delegate ModifierEffectEvaluator methods to FormulaEvaluator |
| game/simulation/components/component.py | Production | Remove vestigial safe_evaluate_math_formula import (line 62) |
| game/simulation/components/component_stats_calculator.py | Production | Migrate 3 call sites to FormulaEvaluator |
| game/simulation/components/component_resource_manager.py | Production | Migrate 1 call site to FormulaEvaluator |
| game/simulation/components/abilities/weapons.py | Production | Migrate 2 call sites to FormulaEvaluator |
| game/strategy/services/ship_stats_calculator.py | Production | Migrate 1 call site to FormulaEvaluator |
| game/simulation/components/modifier_schema.py | Production | Update validation import |
| tests/unit/simulation/test_formula_evaluator.py | Test | New — comprehensive FormulaEvaluator tests |
