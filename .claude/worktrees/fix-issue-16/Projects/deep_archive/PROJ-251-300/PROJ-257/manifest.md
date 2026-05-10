# PROJ-257 File Manifest

> Generated during project planning. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## New Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/core/combat_types.py` | Production | 1 | DamageContext frozen dataclass (moved from simulation) |
| `game/core/formula_evaluator.py` | Production | 2 | FormulaEvaluator, FormulaContext, AST walker, LRU cache (moved from simulation) |
| `tests/unit/core/test_combat_types.py` | Test | 1 | Tests for DamageContext in core |
| `tests/unit/core/test_formula_evaluator.py` | Test | 2 | Tests for FormulaEvaluator in core, AST walker, LRU cache |

## Modified Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/simulation/combat/combat_events.py` | Production | 1 | Remove DamageContext class, add re-export from core |
| `game/engine/collision.py` | Production | 1 | Change DamageContext import from simulation to core |
| `game/simulation/projectile_manager.py` | Production | 1 | Change DamageContext import from simulation to core |
| `game/simulation/combat/damage_calculator.py` | Production | 1 | Change DamageContext TYPE_CHECKING import to core |
| `game/engine/physics.py` | Production | 1 | Remove apply_force(), neuter update(), update docstrings |
| `game/simulation/formula_system.py` | Production | 2 | Replace with thin re-export shim |
| `game/simulation/components/modifier_effects.py` | Production | 2 | Change FormulaEvaluator import to core |
| `game/simulation/components/component_stats_calculator.py` | Production | 2 | Change FormulaEvaluator import to core |
| `game/simulation/components/component_resource_manager.py` | Production | 2 | Change FormulaEvaluator import to core |
| `game/simulation/components/abilities/weapons.py` | Production | 2 | Change FormulaEvaluator import to core |
| `game/strategy/services/ship_stats_calculator.py` | Production | 2 | Change FormulaEvaluator import to core |
| `game/strategy/services/design_validator.py` | Production | 2 | Change FormulaEvaluator import to core |
| `tests/unit/systems/test_physics.py` | Test | 1 | Update tests for PhysicsBody boundary changes |
| `tests/unit/systems/test_physics_edge_cases.py` | Test | 1 | Update tests for PhysicsBody boundary changes |
| `docs/01_ARCHITECTURE.md` | Docs | 3 | Add combat_types.py and formula_evaluator.py to core table, update engine description |
| `docs/02_PATTERNS.md` | Docs | 3 | Update any formula/DamageContext references (if present) |

## Unchanged Files (read-only reference)

| File | Why Referenced |
|------|---------------|
| `game/simulation/entities/ship.py` | Inherits PhysicsBody -- not modified, just verified |
| `game/simulation/entities/projectile.py` | Inherits PhysicsBody -- not modified, just verified |
| `game/simulation/entities/ship_physics.py` | ShipPhysicsMixin -- not modified, just verified |
| `game/simulation/entities/ship_combat_engine.py` | Uses DamageContext via damage_calculator -- no direct import to change |
| `game/core/__init__.py` | May need update if FormulaEvaluator added to core public API (TBD) |
| `game/engine/__init__.py` | Verified no changes needed |
| `tests/unit/simulation/combat/test_combat_events.py` | Existing DamageContext tests -- unchanged, works via re-export |
| `tests/unit/simulation/test_formula_evaluator.py` | Existing FormulaEvaluator tests -- unchanged, works via re-export |
| `tests/unit/systems/test_formula_system.py` | Existing formula tests -- unchanged, works via re-export |
| `tests/unit/simulation/test_formula_exceptions.py` | Existing formula tests -- unchanged, works via re-export |
| `tests/unit/systems/test_formula_overflow_underflow.py` | Existing formula tests -- unchanged, works via re-export |
