# Architecture Analysis - PROJ-16

**Agent Role:** Architecture Analyst
**Date:** 2026-01-25

## Executive Summary

All four re-export removals are architecturally safe with no blocking circular import risks. The primary concerns are architectural clarity (inverse dependencies, re-export semantics), test isolation (StrategyManager singleton), and API design (ship initialization facade).

## Circular Import Risk Assessment

| Re-export | Risk | Finding |
|-----------|------|---------|
| component.py → component_constants | NONE | component_constants has NO dependencies on simulation modules |
| ship.py → ship_loader | NONE | ship_loader imports ship_validator but no cycle with ship.py |
| controller.py → strategy_manager | NONE | strategy_manager has no back-references to controller |
| controller.py → target_evaluator | NONE | target_evaluator has no back-references to controller |
| planet.py → constants | NONE | constants is in core layer, planet in strategy (higher) |

## Layer Violations Identified

1. **planet.py re-exporting from core.constants** - This is an inverse dependency. Strategy layer should NOT re-export core concepts. This is the most problematic re-export.

2. **component.py SRP violation** - component.py both defines Component class AND re-exports constants. Clean split would improve cohesion.

3. **controller.py hiding singleton nature** - StrategyManager is a singleton but re-export location hides this from callers.

## Module Design Issues

- `ship.py` re-exports obscure that ship_loader handles initialization, not Ship class
- Developers cannot distinguish whether ComponentStatus is defined in component.py or re-exported

## Recommendations

1. **Remove PLANET_RESOURCES first** - Trivial, highest clarity gain, fixes inverse dependency
2. **Remove component constants second** - Isolated, no circular import risks
3. **Remove AI re-exports with test coordination** - Requires conftest.py updates
4. **Remove ship_loader last** - Critical path, needs parallel facade refactoring consideration
