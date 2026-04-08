# PROJ-257: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-08 | Project initialized | Starting point for Foundation - Layer Violations, Formula Extraction, AST Parser |
| 2026-04-08 | Skeptical review confirmed all 4 issues as genuine | #1: Engine->Simulation import verified at collision.py:53. #2: apply_force() has 0 call sites, PhysicsBody.update() never called by subclasses. #4: formula_system.py imports only core modules. #26: validate() already uses ast.parse, eval() is redundant. |
| 2026-04-08 | Move DamageContext to `game/core/combat_types.py` (not re-export from core) | DamageContext is a pure frozen DTO with `Optional[Any]` fields and zero simulation logic. Core already contains similar cross-layer types (LayerType, AttackType, CombatConstants). Moving it fully to core (not just re-exporting) makes the dependency direction clean. |
| 2026-04-08 | Keep backward-compat re-export of DamageContext from `combat_events.py` | Test file `tests/unit/simulation/combat/test_combat_events.py` imports DamageContext from combat_events. Re-export avoids churn in test files while production code migrates to core import. |
| 2026-04-08 | PhysicsBody: document boundary, remove dead methods, keep inheritance | Ship and Projectile use PhysicsBody for its property container role (position, velocity, angle, mass, forward_vector). The force-accumulation model (apply_force + update) is never used. Remove apply_force() and neuter update(), add docstrings explaining the arcade physics model. Do NOT refactor the inheritance hierarchy -- that is a larger change out of scope. |
| 2026-04-08 | Keep PhysicsBody.update() as a no-op with docstring rather than removing entirely | Some code might call `super().__init__()` which is fine, but completely removing update() could break if any forgotten path calls it. A no-op with a clear docstring is safer and self-documenting. |
| 2026-04-08 | AST walker approach: extend existing ast.parse pattern from validate() | validate() already parses to AST and walks it. The evaluate() method should do the same instead of calling eval(). This eliminates eval() entirely while reusing the proven ast.parse infrastructure. |
| 2026-04-08 | LRU cache for AST parse, maxsize=256 | Only 52 formulas exist in the codebase, but modifiers may create variants. 256 provides generous headroom. Cache is keyed on (formula_string, caret_as_power) since caret substitution changes the parse. |
| 2026-04-08 | Keep backward-compat re-exports from `game/simulation/formula_system.py` during migration | 6 test files import from `game.simulation.formula_system`. Re-export shim avoids mass test churn while production code moves to `game.core.formula_evaluator`. Old aliases (evaluate_math_formula, etc.) also preserved for test compat. |
| 2026-04-08 | Production code updated to import from core; test code allowed to keep simulation imports | Clean separation: production imports use canonical `game.core.formula_evaluator` path. Test imports work via re-exports from `game.simulation.formula_system`. This keeps the migration focused on architectural correctness in production code. |
| 2026-04-08 | No dependencies on other active projects | PROJ-87/86/88/89 (God Class Decomposition) do not overlap with these foundation-layer changes. FormulaEvaluator extraction is independent of any decomposition work. |
