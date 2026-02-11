# Architecture Drift Sweep: Foundation

## Summary
- **Shard:** Foundation
- **Files Scanned:** 40
- **Total Issues Found:** 5
- **Critical:** 1 | **Major:** 3 | **Minor:** 1 | **Info:** 0

## Findings

#### CRITICAL: Research/UI Cross-Layer Dependency
**ID:** ADR-FND-001
**Location:** `game/research/ui/research_scene.py:14` AND `game/research/ui/research_renderer.py:12`
**Issue:** Research layer imports from game.ui.renderer.camera: `from game.ui.renderer.camera import Camera`. Per architecture rules, research layer should only depend on core. This creates cross-layer dependency on UI subsystem.
**Impact:** Violates layer separation principle. Creates implicit coupling to entire UI subsystem. Makes research layer harder to test in isolation.
**Recommendation:** Extract Camera to game.engine.visualization or game.core.rendering as pure math/rendering utility.
**Effort:** Medium

#### MAJOR: God Module - behaviors.py (513 lines, 11 behavior classes)
**ID:** ADR-FND-002
**Location:** `game/ai/behaviors.py`
**Issue:** Single module contains AIBehavior base class plus 11 concrete implementations (RamBehavior, FleeBehavior, KiteBehavior, AttackRunBehavior, FormationBehavior, OrbitBehavior, StationaryFireBehavior, DoNothingBehavior, StraightLineBehavior, RotateOnlyBehavior, ErraticBehavior). 513 lines.
**Impact:** Hard to locate specific behavior code. Testing individual behaviors requires loading entire module.
**Recommendation:** Extract each behavior to own module: game/ai/behaviors/ram.py, game/ai/behaviors/kite.py, etc.
**Effort:** Medium

#### MAJOR: High Complexity - AIController (479 lines, 17 methods)
**ID:** ADR-FND-003
**Location:** `game/ai/controller.py`
**Issue:** Handles target selection, behavior switching, formation management, capability caching, avoidance logic. Too many responsibilities. update() method ~80 lines.
**Impact:** Hard to understand control flow. Difficult to test targeting independently from movement.
**Recommendation:** Extract TargetSelector, FormationManager, CapabilityAnalyzer as separate classes.
**Effort:** Complex

#### MAJOR: High Complexity - TargetEvaluator (459 lines, 16 methods)
**ID:** ADR-FND-004
**Location:** `game/ai/target_evaluator.py`
**Issue:** Single evaluate() method ~120 lines handling all targeting rule logic. New rule types require editing massive method. Not extensible.
**Impact:** Adding new targeting rules requires modifying core method.
**Recommendation:** Strategy pattern - extract rules into pluggable RuleEvaluator classes. Make evaluate() a dispatcher.
**Effort:** Complex

#### MINOR: Missing Type Annotations in TargetEvaluator Helpers
**ID:** ADR-FND-005
**Location:** `game/ai/target_evaluator.py:35-132`
**Issue:** Module-level functions _get_position(), _get_rotation(), _get_all_components() lack return type hints. Inconsistent with rest of codebase.
**Impact:** Type checkers cannot validate function returns.
**Recommendation:** Add return type hints (-> Vector2, -> float, -> List[Any]).
**Effort:** Simple

## Positive Findings

- **Core layer is clean**: No imports from simulation, strategy, ui, or ai layers
- **Engine layer is clean**: TYPE_CHECKING blocks properly used
- **AI layer respects rules**: Only imports from core, simulation, and strategy (no UI)
- **Research data layer is clean**: No inappropriate dependencies (only research/ui has violation)
- **No circular dependencies detected** between assigned layers

## Top 5 Priority Issues
1. **ADR-FND-001**: Research/UI cross-layer dependency - clear architecture violation
2. **ADR-FND-002**: behaviors.py god module - 11 classes in one file
3. **ADR-FND-003**: AIController high complexity - too many responsibilities
4. **ADR-FND-004**: TargetEvaluator not extensible - needs strategy pattern
5. **ADR-FND-005**: Missing type annotations - quick fix
