# Architecture Drift Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 70
- **Total Issues Found:** 7
- **Critical:** 1 | **Major:** 3 | **Minor:** 1 | **Info:** 2

## Findings

#### CRITICAL: Simulation imports AI layer in factory functions
**ID:** ADR-SIM-001
**Location:** `game/simulation/battle_controller.py:718`
**Issue:** The `_create_default_ai_factory()` function contains a runtime import from the AI layer:
```python
def _create_default_ai_factory() -> 'IAIControllerFactory':
    from game.ai.ai_factory import AIControllerFactory
    return AIControllerFactory()
```
This violates the layer dependency rule: Simulation -> Core only. AI should depend on Simulation, not vice versa.
**Impact:**
- Creates bidirectional coupling between simulation and AI layers
- Prevents true headless operation of simulation without AI layer present
- Makes testing simulation layer in isolation more difficult
- Violates the stated architecture: "Simulation depends on Core ONLY"
**Recommendation:**
1. Remove the `_create_default_ai_factory()` function entirely from battle_controller.py
2. Require callers (in UI/strategy layers) to always inject the AI factory
3. The factory functions `create_manual_battle()`, `create_test_battle()`, `create_strategy_battle()`, and `create_hypothetical_battle()` should be moved to a higher layer (e.g., game/engine/ or a service in game/ui/)
**Effort:** Medium

---

#### MAJOR: TYPE_CHECKING import from AI layer
**ID:** ADR-SIM-002
**Location:** `game/simulation/systems/battle_engine.py:72-73`
**Issue:** TYPE_CHECKING block imports from AI layer:
```python
if TYPE_CHECKING:
    from game.ai.controller import AIController
    from game.simulation.interfaces.ai_controller import IAIController, IAIControllerFactory
```
While TYPE_CHECKING imports don't create runtime dependencies, they indicate architectural awareness of a layer that simulation should not know about.
**Impact:**
- Type annotations reference concrete AI implementation
- Creates implicit coupling in tooling (mypy, IDEs)
- Method signatures reference `AIController` type (lines 214, 298) instead of using only the interface `IAIController`
**Recommendation:**
1. Remove the `from game.ai.controller import AIController` import
2. Use only `IAIController` (the protocol) in all type annotations
3. Change method signatures from `Optional['AIController']` to `Optional['IAIController']`
**Effort:** Simple

---

#### MAJOR: Ship class exceeds 500 lines (God Class)
**ID:** ADR-SIM-003
**Location:** `game/simulation/entities/ship.py` (810 lines)
**Issue:** The Ship class is 810 lines, exceeding the god class threshold of 500 lines. While significant decomposition has occurred (ShipPhysicsMixin, ShipStatsCalculator, ShipCombatEngine, ShipFormation, ShipStatQuerier, ShipValidatorHelper), the class still has too many responsibilities.
**Impact:**
- Difficult to understand the class at a glance
- Many methods still exist on Ship as facade/delegation methods
- Testing requires understanding the full class structure
**Recommendation:**
1. Continue god class decomposition per PROJ-12
2. Consider moving more methods to helper classes
3. Ship could potentially be split into ShipEntity (data) and ShipBehavior (operations)
**Effort:** Complex

---

#### MAJOR: BattleController exceeds 500 lines (God Class)
**ID:** ADR-SIM-004
**Location:** `game/simulation/battle_controller.py` (872 lines)
**Issue:** BattleController is 872 lines, the largest file in the simulation layer. It orchestrates battles, manages retreat, handles state save/load, and contains factory functions.
**Impact:**
- Factory functions at module level (~150 lines) bloat the file
- Multiple responsibilities: battle lifecycle, retreat management, state management
- Difficult to test individual aspects in isolation
**Recommendation:**
1. Extract factory functions to a separate module (e.g., `battle_factories.py`) - but note these should likely move to a higher layer due to ADR-SIM-001
2. State save/load delegation to BattleStateManager is already done, verify no duplication
3. Consider further decomposition of retreat handling into RetreatManager (already exists)
**Effort:** Medium

---

#### MINOR: Late import pattern for circular dependency avoidance
**ID:** ADR-SIM-005
**Location:** `game/simulation/entities/ship.py:492, 537`
**Issue:** ModifierService is imported inside `add_component()` and `add_components_bulk()` methods:
```python
from game.simulation.services.modifier_service import ModifierService
```
This is documented as intentional (see ARCHITECTURE.md line 139-143), but indicates a design issue that could be resolved.
**Impact:**
- Performance cost on each component addition (import overhead)
- Makes the dependency graph harder to understand statically
- Import happens in hot path during ship construction
**Recommendation:**
- Consider restructuring ModifierService to break the cycle
- Alternative: cache the import result at module level after first access
- Note: ARCHITECTURE.md documents this as "real import cycle that cannot be moved to module level"
**Effort:** Complex

---

#### INFO: game/engine layer used by simulation
**ID:** ADR-SIM-006
**Location:** Multiple files
**Issue:** Simulation layer imports from `game/engine/`:
- `game/simulation/systems/battle_engine.py`: SpatialGrid, CollisionSystem
- `game/simulation/entities/ship.py`: PhysicsBody
- `game/simulation/entities/projectile.py`: PhysicsBody
- `game/simulation/entities/ship_physics.py`: PhysicsBody
- `game/simulation/interfaces/ai_controller.py`: SpatialGrid (TYPE_CHECKING)
**Impact:** Not a violation per se, but the game/engine layer's role is unclear in the architecture documentation. CLAUDE.md describes it as "thin orchestration layer" while ARCHITECTURE.md shows only Core/Simulation/Strategy/UI layers.
**Recommendation:**
- Document game/engine as a foundation layer (like Core) that provides physics/spatial infrastructure
- Verify game/engine has no pygame dependencies (confirmed: no pygame imports found)
- Consider merging into Core layer or documenting clearly as an infrastructure layer
**Effort:** Simple (documentation only)

---

#### INFO: Component.py approaching god class threshold
**ID:** ADR-SIM-007
**Location:** `game/simulation/components/component.py` (723 lines)
**Issue:** Component class file is 723 lines. While significant delegation to managers exists (AbilityManager, ModifierManager, ComponentStatsCalculator, ComponentResourceManager, ComponentHealthManager), the file contains multiple responsibilities including cache management and factory functions.
**Impact:**
- File contains both Component class and ComponentCacheManager singleton
- Factory functions (`create_component`, `load_components`, `load_modifiers`) are at module level
- Getting close to needing further extraction
**Recommendation:**
- Consider moving factory functions to a separate module
- ComponentCacheManager could be in its own file
- Monitor file growth; extract if it exceeds 800 lines
**Effort:** Simple

---

## Top 5 Priority Issues

1. **ADR-SIM-001 (CRITICAL)**: Simulation imports AI layer - This is the only true layer violation in the shard. The factory functions with AI imports should be moved to a higher layer that is allowed to import both simulation and AI.

2. **ADR-SIM-002 (MAJOR)**: TYPE_CHECKING import of AIController - Should use only the IAIController protocol, not the concrete implementation.

3. **ADR-SIM-003 (MAJOR)**: Ship god class (810 lines) - Continue decomposition to improve maintainability.

4. **ADR-SIM-004 (MAJOR)**: BattleController god class (872 lines) - Extract factory functions and consider further decomposition.

5. **ADR-SIM-005 (MINOR)**: Late import for circular dependency - While documented as intentional, represents a design limitation that could be addressed in future refactoring.

## Notes

### Clean Architecture Compliance

The simulation layer largely follows the architectural rules:
- **No pygame imports**: Confirmed - all 70 files are clean of pygame dependencies
- **No strategy imports**: Confirmed - no `from game.strategy` or `import game.strategy` found
- **No UI imports**: Confirmed - no `from game.ui` or `import game.ui` found
- **Core imports**: All files correctly depend on game/core for shared utilities

### Positive Patterns Observed

1. **Protocol Usage**: The `IAIController` and `IAIControllerFactory` protocols in `game/simulation/interfaces/ai_controller.py` properly define interfaces for AI layer injection. This is the correct pattern for cross-layer communication.

2. **Dependency Injection**: BattleEngine, BattleService, and BattleController all accept AI factory via constructor injection, allowing the simulation layer to remain decoupled from AI implementation.

3. **God Class Decomposition**: Significant progress has been made extracting Ship responsibilities (ShipCombatEngine, ShipStatsCalculator, etc.) and Component responsibilities (ComponentHealthManager, ComponentResourceManager, etc.).

4. **TYPE_CHECKING for Circular Deps**: Appropriate use of TYPE_CHECKING to handle intra-layer circular references without creating runtime import cycles.
