# Architecture Drift Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 40
- **Total Issues Found:** 5
- **Critical:** 0 | **Major:** 3 | **Minor:** 1 | **Info:** 1

## Findings

#### MAJOR: game/research/ui/research_scene.py Late Import from game.ui Layer
**ID:** ADR-FND-001
**Location:** `game/research/ui/research_scene.py:45`
**Issue:** The research_scene.py module contains a late import inside a function that imports from `game.ui.renderer.camera`:
```python
def _create_default_camera(width: int, height: int) -> Any:
    from game.ui.renderer.camera import Camera
    return Camera(width, height)
```
This creates a runtime dependency from the research layer to the UI layer. While the import is inside a function (not at module level) and is documented as a workaround for PROJ-132, this is still an architectural concern since research should not depend on UI.
**Impact:** The research module cannot operate in headless mode if the default camera factory is invoked. This couples the research system to pygame/UI implementation details.
**Recommendation:** The current approach (dependency injection with a fallback factory) is a reasonable mitigation. To fully resolve, ensure all callers inject the camera explicitly, making the fallback factory dead code that can be removed.
**Effort:** Simple (remove fallback after ensuring all callers inject camera)

#### MAJOR: protocols.py Exceeds 500 Line Threshold (Potential God Module)
**ID:** ADR-FND-002
**Location:** `game/core/protocols.py` (579 lines)
**Issue:** The protocols.py module contains 579 lines of code, exceeding the 500-line threshold for potential god class/module issues. This module defines 16 runtime_checkable protocols and 12 TypeGuard functions across multiple domains (strategy entities, combat entities, camera, resources).
**Impact:** Large protocol files become harder to maintain and understand. Changes to one protocol may require understanding the entire file. Protocol definitions spanning multiple domains violate single-responsibility principle.
**Recommendation:** Split protocols by domain:
- `game/core/protocols/strategy.py` - IFleet, IPlanet, IStarSystem, IStar, IWarpPoint, ISectorEnvironment, IZoneOccupant
- `game/core/protocols/combat.py` - ICombatant, IDamageable, IPostBattleShip, IResourceHolder, IResourceReader
- `game/core/protocols/ui.py` - IScene, ICamera
- `game/core/protocols/registry.py` - IRegistryProvider
- `game/core/protocols/__init__.py` - Re-export all for backward compatibility
**Effort:** Medium

#### MAJOR: behaviors.py Exceeds 500 Line Threshold (Potential God Module)
**ID:** ADR-FND-003
**Location:** `game/ai/behaviors.py` (520 lines)
**Issue:** The behaviors.py module contains 520 lines defining 11 different AI behavior classes. While each class is reasonably sized, having all behaviors in a single file makes the module harder to navigate.
**Impact:** Adding new behaviors requires modifying a large file. Testing individual behaviors requires loading all behaviors. Changes to shared constants affect the entire file.
**Recommendation:** Consider organizing behaviors into submodules:
- `game/ai/behaviors/combat.py` - KiteBehavior, AttackRunBehavior, RamBehavior, FleeBehavior, OrbitBehavior
- `game/ai/behaviors/formation.py` - FormationBehavior
- `game/ai/behaviors/test.py` - DoNothingBehavior, StationaryFireBehavior, StraightLineBehavior, RotateOnlyBehavior, ErraticBehavior
- `game/ai/behaviors/__init__.py` - Re-export all for backward compatibility
**Effort:** Medium

#### MINOR: TYPE_CHECKING Block in protocols.py for HexCoord
**ID:** ADR-FND-004
**Location:** `game/core/protocols.py:36-38`
**Issue:** The protocols.py module uses a TYPE_CHECKING block to import HexCoord:
```python
if TYPE_CHECKING:
    from game.core.hex_math import HexCoord
```
This is within the same layer (core) so it is not a layer violation. However, TYPE_CHECKING blocks can indicate design issues where circular imports exist or where type dependencies create coupling. In this case, the comment notes "LayerData not imported - protocols use Any for cross-layer types" showing awareness of cross-layer concerns.
**Impact:** Minimal - this is a reasonable use of TYPE_CHECKING for type annotations without runtime import.
**Recommendation:** No action required. This is acceptable practice for type hints.
**Effort:** N/A

#### INFO: Well-Structured Dependency Injection in AI Factory
**ID:** ADR-FND-005
**Location:** `game/ai/ai_factory.py:25-29`
**Issue:** The AI factory correctly uses TYPE_CHECKING blocks for simulation layer imports:
```python
if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.engine.spatial import SpatialGrid
```
This demonstrates proper architectural awareness - the AI layer depends on simulation layer types for type hints only, with actual runtime objects passed via dependency injection.
**Impact:** Positive - this pattern enables testability and maintains proper layer separation.
**Recommendation:** Document this pattern as an exemplar for other cross-layer dependencies.
**Effort:** N/A

## Top 5 Priority Issues

1. **ADR-FND-002 (MAJOR):** protocols.py at 579 lines should be split by domain for maintainability. This is the largest file in the core layer and contains protocols spanning multiple unrelated domains.

2. **ADR-FND-003 (MAJOR):** behaviors.py at 520 lines should be organized into submodules. The 11 behavior classes would be easier to maintain and test as separate files.

3. **ADR-FND-001 (MAJOR):** The research_scene.py late import from game.ui creates a runtime dependency that should be eliminated by ensuring all callers inject the camera.

4. **ADR-FND-004 (MINOR):** The TYPE_CHECKING usage in protocols.py is acceptable but worth monitoring as the protocols file grows.

5. **ADR-FND-005 (INFO):** The ai_factory.py demonstrates exemplary dependency injection patterns that should be documented and replicated elsewhere.

## Positive Observations

The foundation layers (core, ai, research, engine) show strong architectural discipline:

1. **No pygame imports in non-UI code:** The core, ai, and engine layers have zero pygame imports. The research layer's pygame usage is properly isolated in the `research/ui/` subdirectory.

2. **No layer violations in core:** The core layer correctly has no imports from simulation, strategy, ui, or ai layers.

3. **Proper AI-to-simulation boundary:** The AI layer imports from simulation only via interfaces (IAIController) and TYPE_CHECKING blocks, maintaining testability.

4. **Clean engine layer:** The engine layer (physics, collision, spatial) has no dependencies outside core, making it fully portable.

5. **Research data layer isolation:** The `research/data/` and `research/systems/` directories have no pygame dependencies - only the `research/ui/` directory uses pygame.

6. **Consistent use of dependency injection:** Services like StrategyManager, RegistryManager, and AIControllerFactory use proper singleton patterns with clear reset methods for test isolation.
