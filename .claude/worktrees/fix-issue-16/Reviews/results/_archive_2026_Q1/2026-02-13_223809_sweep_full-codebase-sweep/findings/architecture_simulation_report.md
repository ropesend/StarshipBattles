# Architecture Drift Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 69
- **Total Issues Found:** 7
- **Critical:** 0 | **Major:** 3 | **Minor:** 3 | **Info:** 1

## Analysis Overview

The simulation layer (`game/simulation/`) was exhaustively scanned for architectural violations. The analysis covered:
- Import graph analysis (all 69 Python files)
- Pygame boundary violations
- Layer dependency violations (strategy, ui, ai imports)
- TYPE_CHECKING blocks
- Circular dependency indicators
- God class patterns
- Data flow violations

### Positive Findings

The simulation layer demonstrates **excellent architectural compliance**:
1. **No pygame imports** - Zero occurrences of `import pygame` or `from pygame` in the simulation layer
2. **No strategy/ui/ai imports** - No direct runtime imports from `game.strategy`, `game.ui`, or `game.ai`
3. **Clean TYPE_CHECKING blocks** - All type hints for higher layers are properly guarded in TYPE_CHECKING blocks
4. **Dependency injection** - Strict DI pattern (PROJ-50) is consistently applied throughout

## Findings

#### MAJOR: Simulation Depends on game.engine (PhysicsBody)
**ID:** ADR-SIM-001
**Location:** `game/simulation/entities/ship.py:5`, `game/simulation/entities/ship_physics.py:1`, `game/simulation/entities/projectile.py:2`
**Issue:** The simulation layer imports `PhysicsBody` from `game.engine.physics`. According to the architecture rules, `game/engine/` is described as a "thin orchestration layer", which suggests it may be at the same level or above simulation.
**Impact:** If engine is intended to be above simulation, this creates a dependency direction violation. However, if engine provides low-level physics infrastructure used by simulation, this may be acceptable.
**Recommendation:** Clarify the architectural role of `game.engine`. If it provides foundational physics, consider documenting it as "Core-adjacent" infrastructure. If it orchestrates simulation, the PhysicsBody should be moved to a lower layer.
**Effort:** Medium

#### MAJOR: Simulation Depends on game.engine (SpatialGrid, CollisionSystem)
**ID:** ADR-SIM-002
**Location:** `game/simulation/systems/battle_engine.py:62,66`, `game/simulation/projectile_manager.py:8` (TYPE_CHECKING), `game/simulation/interfaces/ai_controller.py:19` (TYPE_CHECKING)
**Issue:** BattleEngine directly imports `SpatialGrid` from `game.engine.spatial` and `CollisionSystem` from `game.engine.collision` at runtime. Additional TYPE_CHECKING imports exist in projectile_manager and ai_controller interface.
**Impact:** This creates a strong coupling between simulation and engine layers. If engine layer changes, simulation layer is affected.
**Recommendation:** Same as ADR-SIM-001 - clarify engine's architectural role. If these are infrastructure utilities, document them as such. If not, consider extracting to core layer or creating interfaces.
**Effort:** Medium

#### MAJOR: Circular Import Risk - Ship and ModifierService
**ID:** ADR-SIM-003
**Location:** `game/simulation/entities/ship.py:491-495,536-540`
**Issue:** Ship class uses late imports for ModifierService with explicit comment: "LATE IMPORT: services/__init__.py imports VehicleDesignService which imports Ship". This indicates a circular dependency that requires runtime import workarounds.
**Impact:** Circular imports make the codebase harder to understand, can cause import-time errors if code paths change, and indicate tight coupling between modules that should be more independent.
**Recommendation:** Extract modifier application logic into a standalone function or service that doesn't require bidirectional knowledge. Consider using an event/callback pattern where Ship emits component-added events that the modifier system subscribes to.
**Effort:** Medium

#### MINOR: Circular Import Risk - ShipSerializer and Ship
**ID:** ADR-SIM-004
**Location:** `game/simulation/entities/ship_serialization.py:142-143`
**Issue:** ShipSerializer requires a runtime import of Ship inside `from_dict()` with comment: "MUST remain a runtime import - ship.py imports ShipSerializer at module level". This is a bidirectional dependency between Ship and ShipSerializer.
**Impact:** While this is a common serialization pattern, it creates tight coupling. The workaround is properly documented but adds complexity.
**Recommendation:** Consider using a factory pattern where ShipSerializer.from_dict() receives a ship_factory callable instead of directly importing Ship. Alternatively, accept this as a reasonable trade-off for the convenience of having Ship.from_dict() as a static method.
**Effort:** Simple

#### MINOR: God Class Indicator - Ship Class (810 LOC, 41 methods)
**ID:** ADR-SIM-005
**Location:** `game/simulation/entities/ship.py` (entire file)
**Issue:** The Ship class has 810 lines and approximately 41 methods. While this is below the 30-method threshold mentioned in guidelines, the class still carries significant responsibilities including: layer management, component management, stat caching, combat delegation, physics (via mixin), serialization delegation, and validation delegation.
**Impact:** Large classes are harder to test, understand, and modify. Changes in one area may unexpectedly affect others.
**Recommendation:** The class already uses good patterns (delegation to ShipStatsCalculator, ShipCombatEngine, ShipSerializer, ShipValidatorHelper, ShipPhysicsMixin). Consider further extraction of layer management into a dedicated LayerManager helper class. Monitor growth and split if it exceeds 1000 LOC.
**Effort:** Complex

#### MINOR: God Class Indicator - Component Class (723 LOC)
**ID:** ADR-SIM-006
**Location:** `game/simulation/components/component.py` (entire file)
**Issue:** The Component class has 723 lines with approximately 34 methods. This handles abilities, modifiers, stats calculation, health management, resource management, and serialization.
**Impact:** Similar to Ship, a large class with many responsibilities can be difficult to maintain and test.
**Recommendation:** The file already has good extraction patterns (ComponentHealthManager, ComponentResourceManager, ComponentStatsCalculator). Continue monitoring size and consider further decomposition if it grows.
**Effort:** Medium

#### INFO: TYPE_CHECKING Used Extensively for Layer Isolation
**ID:** ADR-SIM-007
**Location:** Multiple files (37 occurrences in TYPE_CHECKING blocks)
**Issue:** TYPE_CHECKING is used extensively throughout the simulation layer to import types without creating runtime dependencies. This is good practice for type hints but the high count suggests complex type relationships.
**Impact:** No operational impact - this is the correct pattern. However, the extensive use indicates the simulation layer has complex type relationships that need careful management.
**Recommendation:** No action required. This is proper use of TYPE_CHECKING for maintaining layer boundaries while supporting type hints.
**Effort:** N/A

## Top 5 Priority Issues

1. **ADR-SIM-001/002: Engine Layer Dependency** - The simulation layer's dependency on `game.engine` needs architectural clarification. If engine is infrastructure, document it. If not, refactor. (Priority: High for clarity)

2. **ADR-SIM-003: Ship/ModifierService Circular** - The circular import between Ship and ModifierService is a maintainability concern that could cause issues as the codebase evolves. (Priority: Medium)

3. **ADR-SIM-005: Ship God Class** - At 810 LOC, Ship is approaching the threshold for a god class. Continue decomposition efforts. (Priority: Low - well-managed currently)

4. **ADR-SIM-004: Ship/ShipSerializer Circular** - A minor circular dependency that is well-documented and acceptable for serialization patterns. (Priority: Low)

5. **ADR-SIM-006: Component God Class** - At 723 LOC, Component is also large but has good extraction patterns in place. (Priority: Low)

## Architectural Compliance Summary

| Check | Result |
|-------|--------|
| No pygame imports | PASS |
| No strategy layer imports | PASS |
| No UI layer imports | PASS |
| No AI layer imports | PASS |
| Proper TYPE_CHECKING usage | PASS |
| No critical layer violations | PASS |
| Dependency injection | PASS (PROJ-50 compliant) |

The simulation layer is **architecturally sound** with no critical violations. The identified issues are either documentation/clarification needs (engine dependency) or minor maintainability concerns (circular imports, class sizes) that are well-managed with existing patterns.
