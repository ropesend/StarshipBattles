# PROJ-257: Foundation - Layer Violations, Formula Extraction, AST Parser

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-257` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-257 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. DamageContext Move + PhysicsBody Boundary | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. FormulaEvaluator Extraction + AST Walker | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Documentation + Final Verification | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-08
**Active Phase:** ALL PHASES COMPLETE — Ready for audit
**Last Action:** Phase 3 complete — docs/01_ARCHITECTURE.md updated with combat_types.py, formula_evaluator.py, PhysicsBody boundary description. All grep verifications pass: zero Engine→Simulation imports, zero eval() calls, all backward-compat re-exports work. 14636 pytest tests pass + 162 simulation tests pass.
**Next Action:** Audit and user verification
**Blockers:** None

## Overview

This project fixes 4 verified architectural issues in the foundation layers (Core, Engine, Simulation). Issue #1 moves `DamageContext` from simulation to core to fix an Engine-to-Simulation layer violation. Issue #2 clarifies the `PhysicsBody` boundary by documenting the arcade physics model and removing dead code. Issue #4 extracts `FormulaEvaluator` from simulation to core since it has zero simulation dependencies. Issue #26 replaces the existing `eval()` call with an AST tree walker for formula evaluation, adding LRU caching and better error messages.

## Goals
- Fix the Engine->Simulation layer violation (`collision.py` importing from `game.simulation`)
- Clarify the PhysicsBody/ShipPhysicsMixin boundary with documentation
- Extract `FormulaEvaluator` to `game/core/` where it architecturally belongs
- Replace `eval()` with a safe AST tree walker using the existing `ast.parse` pattern from `validate()`
- Add LRU caching for parsed formula ASTs
- Maintain backward compatibility via re-exports during transition

## Scope
**In:**
- Moving `DamageContext` frozen dataclass from `game/simulation/combat/combat_events.py` to `game/core/combat_types.py`
- Updating all 5 importers of `DamageContext` in production code
- Documenting PhysicsBody arcade physics model in docstrings
- Removing `apply_force()` if confirmed unused (currently 0 call sites outside definition)
- Extracting `FormulaEvaluator`, `FormulaContext`, and related constants to `game/core/formula_evaluator.py`
- Building AST tree walker to replace `eval()` in `FormulaEvaluator.evaluate()`
- Adding `functools.lru_cache` for parsed AST trees
- Updating all 6 production importers of `FormulaEvaluator`
- Backward-compat re-exports from original module locations

**Out:**
- Refactoring PhysicsBody inheritance hierarchy (Ship/Projectile)
- Changing the CombatEvent or CombatEventBus (stays in simulation)
- Modifying formula semantics or adding new formula functions
- Touching any UI code
- Re-exports in `game/core/__init__.py` for FormulaEvaluator (it is not a top-level core API)

## Key Files
| Component | File Path |
|-----------|-----------|
| DamageContext (current) | `game/simulation/combat/combat_events.py:61-70` |
| DamageContext (new) | `game/core/combat_types.py` (to be created) |
| Engine layer violation | `game/engine/collision.py:53` |
| ProjectileManager import | `game/simulation/projectile_manager.py:146` |
| DamageCalculator TYPE_CHECKING import | `game/simulation/combat/damage_calculator.py:25-28` |
| ShipCombatEngine (no direct DamageContext import) | `game/simulation/entities/ship_combat_engine.py` |
| PhysicsBody | `game/engine/physics.py` |
| ShipPhysicsMixin | `game/simulation/entities/ship_physics.py` |
| Ship (extends PhysicsBody) | `game/simulation/entities/ship.py:30` |
| Projectile (extends PhysicsBody) | `game/simulation/entities/projectile.py:18` |
| FormulaEvaluator (current) | `game/simulation/formula_system.py` |
| FormulaEvaluator (new) | `game/core/formula_evaluator.py` (to be created) |
| Production importers (simulation) | `game/simulation/components/modifier_effects.py:19`, `component_stats_calculator.py:16`, `component_resource_manager.py:14`, `abilities/weapons.py:7` |
| Production importers (strategy) | `game/strategy/services/ship_stats_calculator.py:36`, `design_validator.py:83` |
| Test: combat events | `tests/unit/simulation/combat/test_combat_events.py` |
| Test: formula evaluator | `tests/unit/simulation/test_formula_evaluator.py` |
| Test: formula system | `tests/unit/systems/test_formula_system.py` |
| Test: formula exceptions | `tests/unit/simulation/test_formula_exceptions.py` |
| Test: formula overflow | `tests/unit/systems/test_formula_overflow_underflow.py` |
| Engine __init__ | `game/engine/__init__.py` |
| Core __init__ | `game/core/__init__.py` |
| Docs: architecture | `docs/01_ARCHITECTURE.md` |
| Docs: patterns | `docs/02_PATTERNS.md` |

## Decisions Log
See [decisions.md](decisions.md) for the full decisions history.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File manifest for conflict detection

## Verification
- [ ] All phase checklists complete
- [ ] All 14783+ tests passing (`python Tools/test_sharded/test_sharded.py`)
- [ ] No `game.engine` module imports from `game.simulation` (grep verification)
- [ ] No `eval()` calls remain in formula evaluation path
- [ ] `FormulaEvaluator` importable from `game.core.formula_evaluator`
- [ ] Backward-compat re-exports work from `game.simulation.formula_system`
- [ ] `docs/01_ARCHITECTURE.md` updated
- [ ] Audit passed
- [ ] User verified
