# PROJ-257: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Skeptical review confirmed 4 genuine architectural issues in the foundation layers:

1. **Engine->Simulation layer violation**: `game/engine/collision.py:53` imports `DamageContext` from `game.simulation.combat.combat_events`. Per `docs/01_ARCHITECTURE.md`, the Engine layer may only depend on Core. This is a real violation because Engine must not import Simulation.

2. **PhysicsBody dead code**: `PhysicsBody.apply_force()` has zero call sites outside its own definition. `PhysicsBody.update()` is never called by Ship or Projectile. Ship uses `ShipPhysicsMixin.update_physics_movement()` exclusively. Projectile does `self.position += self.velocity` directly in its own `update()`. The base class provides useful properties (position, velocity, angle, forward_vector) but the force-accumulation model is unused.

3. **FormulaEvaluator in wrong layer**: `game/simulation/formula_system.py` imports only `game.core.exceptions.FormulaException` and `game.core.error_codes.ErrorCode`. It has zero simulation dependencies. Yet Strategy layer imports it (`game/strategy/services/ship_stats_calculator.py:36`, `design_validator.py:83`), creating a Strategy->Simulation dependency that should be Strategy->Core.

4. **eval() in FormulaEvaluator.evaluate()**: The existing `validate()` method already uses `ast.parse()` and walks the AST for safety checking. The `evaluate()` method then calls `eval()` separately. This is redundant -- a single AST walk can both validate and evaluate, eliminating `eval()` entirely.

## Design Decisions

### 1. DamageContext Move to Core

**What:** Move `DamageContext` frozen dataclass from `game/simulation/combat/combat_events.py:61-70` to a new file `game/core/combat_types.py`.

**Why it belongs in Core:**
- `DamageContext` is a pure frozen dataclass with zero logic
- Its fields are all `Optional[Any]` or `str` -- no simulation types
- It is consumed by Engine layer (collision.py), which must not import Simulation
- It is a DTO (Data Transfer Object) for threading attacker identity through the damage pipeline
- Core already contains similar cross-layer types: `LayerType`, `AttackType`, `CombatConstants`

**What stays in simulation:**
- `CombatEvent`, `CombatEventType`, `EventDetailLevel`, `CombatEventBus` all stay in `game/simulation/combat/combat_events.py`
- These types reference simulation entities and are only used within simulation/UI layers

**Re-export strategy:**
- `combat_events.py` will re-export `DamageContext` from core for backward compatibility
- All production code will be updated to import from `game.core.combat_types`
- Test imports from `combat_events` will continue to work via re-export

### 2. PhysicsBody Boundary Clarification

**Current state:**
- `PhysicsBody` provides: position, velocity, acceleration, angle, angular_velocity, mass, drag, angular_drag, x/y properties, forward_vector(), apply_force(), update()
- `Ship(PhysicsBody, ShipPhysicsMixin)` inherits PhysicsBody but never calls `apply_force()` or `super().update()`. ShipPhysicsMixin.update_physics_movement() completely overrides the physics update with arcade-style movement
- `Projectile(PhysicsBody)` inherits PhysicsBody but does `self.position += self.velocity` directly, never calling `super().update()` or `apply_force()`

**Design: Document boundary, keep inheritance for properties**

The inheritance is useful because PhysicsBody provides:
- `position: Vector2` -- used everywhere
- `velocity: Vector2` -- used by Ship, Projectile, AI targeting, combat engine
- `angle: float` -- used by Ship, rendering
- `forward_vector()` -- used by Ship and AI
- `mass: float` -- used by Ship stats

**Actions:**
- Remove `apply_force()` method -- zero call sites, misleading API
- Remove `update()` method body -- neither Ship nor Projectile calls it
- Keep `update()` as empty/pass or raise NotImplementedError (subclasses must override)
- Add comprehensive docstring documenting the "property bag + forward_vector" role
- Document in physics.py that Ship uses arcade physics (ShipPhysicsMixin) and Projectile uses direct velocity integration
- Do NOT change the inheritance hierarchy -- PhysicsBody as a property container is a valid pattern

### 3. FormulaEvaluator Core Extraction

**What:** Move the entire content of `game/simulation/formula_system.py` to `game/core/formula_evaluator.py`.

**Why:**
- FormulaEvaluator imports only `game.core.exceptions.FormulaException` and `game.core.error_codes.ErrorCode`
- Zero simulation dependencies
- Strategy layer imports it, creating an unnecessary Strategy->Simulation dependency
- Formula evaluation is a utility/infrastructure concern, not a simulation concern
- Core already contains the exception types it depends on

**What moves:**
- `ALLOWED_MATH_FUNCTIONS`, `ALLOWED_BUILTINS`, `DANGEROUS_NAMES` constants
- `FormulaContext` frozen dataclass
- `FormulaEvaluator` class (evaluate, validate, safe_evaluate)

**Re-export strategy:**
- `game/simulation/formula_system.py` becomes a thin re-export shim:
  ```python
  from game.core.formula_evaluator import (
      FormulaEvaluator, FormulaContext,
      ALLOWED_MATH_FUNCTIONS, ALLOWED_BUILTINS, DANGEROUS_NAMES,
  )
  # Backward-compatible aliases
  evaluate_math_formula = FormulaEvaluator.evaluate
  safe_evaluate_math_formula = FormulaEvaluator.safe_evaluate
  validate_formula = FormulaEvaluator.validate
  ```
- Production code in `game/` will be updated to import from `game.core.formula_evaluator`
- Test code can keep importing from `game.simulation.formula_system` via re-exports (less churn)

### 4. AST Tree Walker (Replace eval())

**Current flow:**
1. `validate()` calls `ast.parse(formula, mode='eval')` and walks the AST to check for disallowed names
2. `evaluate()` calls `eval(formula, {"__builtins__": {}}, names)` with a restricted namespace

**New flow:**
1. Parse formula to AST via `ast.parse(formula, mode='eval')` (same as validate)
2. Cache the parsed AST using `functools.lru_cache` keyed on formula string
3. Walk the AST to evaluate, handling: `ast.Constant` (numbers), `ast.Name` (variable lookup), `ast.BinOp` (arithmetic), `ast.UnaryOp` (negation), `ast.Call` (function calls), `ast.Compare` (comparisons)
4. Reject any AST node type not in the whitelist (raises FormulaException)

**AST node handling:**

| AST Node | Handler |
|----------|---------|
| `ast.Constant` | Return the literal value (int/float) |
| `ast.Name` | Look up in context dict, raise if not found |
| `ast.BinOp` | Recursively evaluate left/right, apply operator |
| `ast.UnaryOp` | Recursively evaluate operand, apply unary op |
| `ast.Call` | Look up function name in allowed names, evaluate args, call |
| `ast.Compare` | Evaluate comparands, apply comparison ops |
| `ast.IfExp` | Evaluate condition, return appropriate branch |
| `ast.Attribute` | Reject (no attribute access allowed) |
| `ast.Subscript` | Reject (no subscript access allowed) |

**Operators whitelist:**
- Binary: `Add`, `Sub`, `Mult`, `Div`, `FloorDiv`, `Mod`, `Pow`
- Unary: `UPos`, `UNeg`
- Comparison: `Lt`, `LtE`, `Gt`, `GtE`, `Eq`, `NotEq`

**LRU Cache design:**
- Cache `ast.parse()` result keyed on `(formula_string, caret_as_power)` tuple
- `maxsize=256` (52 known formulas, generous headroom for modifier variants)
- Cache is at module level, shared across all FormulaEvaluator calls
- Only the parse step is cached; evaluation still uses the per-call context dict

**Error messages:**
- Include the formula string, the problematic AST node type, and available variables
- Example: `"Unsupported operation in formula 'x[0] + 1': Subscript not allowed"`
- Example: `"Undefined variable 'thrust' in formula 'thrust * 2'. Available: ['mass', 'count']"`

**Validation integration:**
- `validate()` continues to use its own AST walk (it checks names without evaluating)
- `evaluate()` uses the new AST walker (validates implicitly by rejecting unknown nodes)
- Both share the cached `ast.parse()` call

## Key Patterns to Reuse

- **Frozen dataclass with slots**: `DamageContext` already uses `@dataclass(frozen=True, slots=True)` -- maintain this pattern in the new location
- **Re-export for backward compatibility**: Same pattern used by `game/simulation/formula_system.py` lines 268-270 for the old function aliases
- **AST validation walk**: Existing pattern in `FormulaEvaluator.validate()` lines 200-232 walks `ast.walk(tree)` checking node types
- **Module-level constants**: `ALLOWED_MATH_FUNCTIONS`, `ALLOWED_BUILTINS`, `DANGEROUS_NAMES` follow the core pattern of module-level constant sets

## Dependencies & Risks

1. **Import cycle risk (DamageContext)**: Low. DamageContext has no imports beyond stdlib. Moving to core introduces no new dependencies.
2. **Formula behavior change risk (AST walker)**: Medium. Must verify all 52 formulas produce identical results. TDD approach: capture eval() results for every formula, then verify AST walker matches exactly.
3. **Test import breakage risk**: Low. Re-exports from original locations ensure existing test imports work. Tests will be updated incrementally.
4. **PhysicsBody removal risk**: Low. `apply_force()` has zero call sites. `update()` has zero call sites from Ship or Projectile. But third-party or test code might reference them -- grep will confirm.
