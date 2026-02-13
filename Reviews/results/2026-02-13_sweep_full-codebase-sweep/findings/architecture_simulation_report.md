# Architecture Drift Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 73
- **Total Issues Found:** 6
- **Critical:** 1 | **Major:** 3 | **Minor:** 1 | **Info:** 1

## Findings

#### CRITICAL: AI Layer Imports in Simulation Factory
**ID:** ADR-SIM-001
**Location:** `game/simulation/factories/ai_factory.py:56-58`
**Issue:** The simulation layer directly imports and instantiates classes from the AI layer (`game.ai.controller.AIController`, `game.ai.interfaces.ShipControllableAdapter`). According to architecture rules, simulation should only depend on core, not on ai.
**Import Lines:**
```python
from game.ai.controller import AIController
from game.ai.interfaces import ShipControllableAdapter
```
**Impact:**
- Breaks layer isolation: simulation depends on ai, but ai should depend on simulation (inverted dependency)
- Testing BattleEngine requires ai layer to be loaded
- Prevents true headless operation of simulation without ai layer
- Creates implicit circular dependency: simulation -> ai -> simulation

**Recommendation:**
The factory pattern is the right approach, but the factory should be moved to a higher layer (engine or orchestration layer) that can legally import both simulation and ai. Alternatively, dependency injection from the engine/orchestration layer should pass pre-created controllers.

**Effort:** Medium

---

#### MAJOR: TYPE_CHECKING Import of AI Controller
**ID:** ADR-SIM-002
**Location:** `game/simulation/systems/battle_engine.py:72-75`
**Issue:** BattleEngine uses TYPE_CHECKING to import AIController from game.ai for type hints. While this avoids runtime import, it still indicates architectural awareness of a layer that should not be visible to simulation.
**Import Lines:**
```python
if TYPE_CHECKING:
    from game.ai.controller import AIController
    from game.simulation.factories.ai_factory import AIControllerFactory
    from game.simulation.interfaces.ai_controller import IAIController
```
**Impact:**
- Type annotations reference cross-layer types
- IDE autocomplete and static analysis tools expose ai layer to simulation developers
- Indicates incomplete decoupling via interface

**Recommendation:**
Replace all AIController type hints with IAIController (the protocol defined in simulation.interfaces). The protocol is correctly placed; the type hints just need updating.

**Effort:** Simple

---

#### MAJOR: God Class - BattleController
**ID:** ADR-SIM-003
**Location:** `game/simulation/battle_controller.py` (848 lines)
**Issue:** BattleController exceeds the 500-line god class threshold at 848 lines. This indicates too many responsibilities concentrated in a single class.
**Impact:**
- Difficult to test individual behaviors in isolation
- High cognitive load for developers
- Changes to one feature risk breaking unrelated features
- Violates Single Responsibility Principle

**Recommendation:**
Continue decomposition started in prior PROJs. Consider extracting:
- Battle state machine management
- Ship lifecycle management
- Battle statistics tracking
- Event dispatching

**Effort:** Complex

---

#### MAJOR: God Class - Ship Entity
**ID:** ADR-SIM-004
**Location:** `game/simulation/entities/ship.py` (809 lines)
**Issue:** Ship class exceeds the 500-line god class threshold at 809 lines. As the central entity, it has accumulated many responsibilities.
**Impact:**
- Testing individual ship behaviors requires full entity setup
- Changes to ship can ripple across combat, movement, validation
- Mixes combat, physics, component management, and statistics

**Recommendation:**
The decomposition into ShipPhysics, ShipFormation, ShipCombatEngine, ShipStats, etc. is a good start. Continue extracting more responsibilities:
- ShipComponentManager (for add/remove/iterate operations)
- ShipLayerManager (for layer-specific operations)

**Effort:** Complex

---

#### MINOR: Possible Circular Import Workaround
**ID:** ADR-SIM-005
**Location:** `game/simulation/entities/ship_stats.py:72`
**Issue:** Comment indicates a local import to avoid circular dependency:
```python
# Import local to avoid circular dep if needed, or top level if safe.
```
**Impact:**
- Indicates structural coupling that needed workaround
- Local imports can cause subtle timing issues

**Recommendation:**
Review the import structure and consider extracting shared types to break the cycle properly.

**Effort:** Simple

---

#### INFO: Heavy Use of TYPE_CHECKING for Forward References
**ID:** ADR-SIM-006
**Location:** Multiple files (30+ files use TYPE_CHECKING)
**Issue:** Extensive use of TYPE_CHECKING blocks across the simulation layer. While this is valid Python practice for forward references, the sheer volume (30+ files) suggests tight coupling between modules that could benefit from cleaner interfaces.
**Observed Files:**
- battle_state.py
- battle_controller.py
- battle_engine.py
- ship.py
- component.py
- and 25+ others

**Impact:**
- Not a violation per se, but indicates many cross-references
- Can mask architectural issues if TYPE_CHECKING is used to hide imports that would otherwise be circular

**Recommendation:**
No immediate action required. Monitor during future refactoring to ensure TYPE_CHECKING is used for genuine forward references, not to hide dependency problems.

**Effort:** N/A

---

## Positive Findings

The simulation layer demonstrates several architectural strengths:

1. **No Pygame imports**: Complete separation from UI layer - no `import pygame` or `from pygame` found anywhere in the simulation layer.

2. **No Strategy layer imports**: Clean separation - no `from game.strategy` imports found.

3. **No UI layer imports**: Clean separation - no `from game.ui` imports found.

4. **Well-defined interface for AI**: The `IAIController` protocol in `game/simulation/interfaces/ai_controller.py` provides a clean contract, even though the factory violates layering.

5. **Decomposition in progress**: Evidence of ongoing refactoring (PROJ-12, PROJ-43, PROJ-44, PROJ-84, etc.) shows architectural debt is being actively addressed.

6. **Dependency injection patterns**: Services like `VehicleDesignService`, `BattleService`, and validators use constructor injection for registries.

---

## Top 5 Priority Issues

1. **ADR-SIM-001 (CRITICAL)**: AI layer imports in simulation factory - breaks fundamental layer isolation, must be resolved by moving factory or using proper DI from engine layer.

2. **ADR-SIM-003 (MAJOR)**: BattleController god class (848 lines) - core complexity hub needs continued decomposition.

3. **ADR-SIM-004 (MAJOR)**: Ship entity god class (809 lines) - central entity should continue extracting helper classes.

4. **ADR-SIM-002 (MAJOR)**: TYPE_CHECKING AI imports - finish interface-based decoupling by removing all ai layer type references.

5. **ADR-SIM-005 (MINOR)**: Circular import workaround in ship_stats.py - clean up structural coupling.
