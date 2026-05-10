# Architecture Drift Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 22
- **Total Issues Found:** 3
- **Critical:** 0 | **Major:** 1 | **Minor:** 1 | **Info:** 1

## Files Scanned

The following 22 Python files were exhaustively analyzed:

**Root files (4):**
- `game/ui/__init__.py`
- `game/ui/utils.py`
- `game/ui/config.py`
- `game/ui/colors.py`

**Services (12):**
- `game/ui/services/__init__.py`
- `game/ui/services/validation_service.py`
- `game/ui/services/vehicle_class_service.py`
- `game/ui/services/component_service.py`
- `game/ui/services/ship_factory.py`
- `game/ui/services/design_loader_adapter.py`
- `game/ui/services/ship_io_adapter.py`
- `game/ui/services/battle_factories.py`
- `game/ui/services/battle_ui_service.py`
- `game/ui/services/input_mapper.py`
- `game/ui/services/screenshot_manager.py`
- `game/ui/services/ship_io.py`

**Renderer (4):**
- `game/ui/renderer/__init__.py`
- `game/ui/renderer/camera.py`
- `game/ui/renderer/game_renderer.py`
- `game/ui/renderer/sprites.py`

**Interfaces (2):**
- `game/ui/interfaces/__init__.py`
- `game/ui/interfaces/battle_ui.py`

**Orchestration (2):**
- `game/ui/orchestration/__init__.py`
- `game/ui/orchestration/battle_orchestrator.py`

**Assets (2):**
- `game/ui/assets/__init__.py`
- `game/ui/assets/ship_theme_manager.py`

## Findings

#### INFO: pygame.math.Vector2 Usage in UI Services
**ID:** ADR-UI2-001
**Location:** `game/ui/services/ship_factory.py:19, 113, 181-188`
**Issue:** Uses `pygame.math.Vector2` as a parameter type for UI service methods. While pygame usage is allowed in UI, this creates a hard pygame dependency in the service interface that consumers must be aware of.
**Impact:** No layer violation (UI can use pygame), but reduces portability if services need to be used without pygame initialized. This is acceptable but noted for awareness.
**Recommendation:** None required - pygame usage in UI layer is allowed per architecture rules.
**Effort:** N/A

#### MINOR: TYPE_CHECKING Import Pattern in ship_factory.py
**ID:** ADR-UI2-002
**Location:** `game/ui/services/ship_factory.py:21-23`
```python
if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.core.registry import GameRegistries
```
**Issue:** Uses TYPE_CHECKING block for simulation-layer imports. While this pattern avoids runtime circular dependencies, it indicates awareness of simulation layer internals for type hints. UI is allowed to depend on simulation, so this is not a violation, but the pattern suggests tight coupling.
**Impact:** No direct layer violation - UI can depend on simulation. The TYPE_CHECKING pattern is acceptable for avoiding import cycles.
**Recommendation:** None required - this is a valid pattern for UI depending on simulation types.
**Effort:** N/A

#### MAJOR: God Class Potential - InputMapper
**ID:** ADR-UI2-003
**Location:** `game/ui/services/input_mapper.py:1-379`
**Issue:** InputMapper class is 379 lines with 15+ methods. While not exceeding the 500-line threshold, it handles multiple responsibilities: loading/saving bindings, resolving events, conflict detection, and display formatting. The class is approaching god-class territory.
**Impact:** Moderate maintainability concern. Changes to one responsibility (e.g., conflict detection) require understanding the entire class.
**Recommendation:** Consider splitting into smaller focused classes in future refactoring:
  - `KeyBindingLoader` - load/save operations
  - `InputResolver` - event resolution
  - `BindingConflictChecker` - conflict detection
**Effort:** Medium

#### INFO: Well-Documented Cross-Layer Orchestration
**ID:** ADR-UI2-004
**Location:** `game/ui/orchestration/battle_orchestrator.py:1-22`
**Issue:** This file explicitly imports from AI layer (`game.ai.controller`, `game.ai.interfaces`) and engine layer (`game.engine.spatial`). However, this is **intentionally documented** as an orchestration module.
**Impact:** None - the architecture explicitly allows UI to depend on all lower layers, and the cross-layer nature is well-documented in the module docstring.
**Recommendation:** No action needed. This is a model example of properly documenting intentional cross-layer imports.
**Effort:** N/A

## Architecture Compliance Analysis

### Layer Dependencies Verified

The UI layer correctly depends only on lower layers:

1. **Core dependencies (allowed):**
   - `game.core.constants` - Used by renderer, services
   - `game.core.math` - Vector2 used in battle_ui_service, interfaces
   - `game.core.registry` - Used by component_service, design_loader_adapter
   - `game.core.protocols` - IRegistryProvider used by services
   - `game.core.logger` - Logging utilities
   - `game.core.paths` - Path constants
   - `game.core.singleton` - SingletonMeta pattern
   - `game.core.json_utils` - JSON loading/saving
   - `game.core.input_actions` - InputAction enum
   - `game.core.profiling` - Profile blocks

2. **Simulation dependencies (allowed):**
   - `game.simulation.entities.ship` - Ship creation, serialization
   - `game.simulation.entities.ship_loader` - Validator access
   - `game.simulation.services.design_loader` - SimulationDesignLoader
   - `game.simulation.battle_controller` - BattleController
   - `game.simulation.battle_config` - BattleConfig, BattleMode
   - `game.simulation.services` - BattleService (TYPE_CHECKING)

3. **AI dependencies (allowed):**
   - `game.ai.ai_factory` - AIControllerFactory
   - `game.ai.controller` - AIController
   - `game.ai.interfaces` - ShipControllableAdapter

4. **Engine dependencies (allowed):**
   - `game.engine.spatial` - SpatialGrid

### Pygame Boundary Compliance

All pygame usage is correctly confined to the UI layer:
- `game/ui/utils.py` - pygame.Rect, pygame.Surface, transform
- `game/ui/renderer/camera.py` - pygame.math.Vector2, pygame.key, pygame.mouse, pygame.event
- `game/ui/renderer/game_renderer.py` - pygame.draw, pygame.math.Vector2
- `game/ui/renderer/sprites.py` - pygame.image, pygame.Surface
- `game/ui/services/input_mapper.py` - pygame.KEYDOWN, key constants, modifiers
- `game/ui/services/screenshot_manager.py` - pygame.display, pygame.image
- `game/ui/services/ship_factory.py` - pygame.math.Vector2
- `game/ui/assets/ship_theme_manager.py` - pygame.image, pygame.Surface, pygame.draw

No pygame imports were found in non-UI code within this shard (as expected since this is the UI shard).

### Circular Dependency Analysis

No circular dependencies were detected in the scanned files:
- All TYPE_CHECKING imports are for lower-layer types (valid pattern)
- No late imports with circular-avoidance comments found
- All modules have clean, directed dependency graphs

### God Class Analysis

Files analyzed for size and complexity:

| File | Lines | Methods | Status |
|------|-------|---------|--------|
| input_mapper.py | 379 | 15+ | Approaching threshold |
| ship_theme_manager.py | 314 | 12 | Acceptable |
| battle_ui_service.py | 293 | 10 | Acceptable |
| ship_io.py | 127 | 3 | Acceptable |
| ship_factory.py | 189 | 5 | Acceptable |

Only InputMapper approaches the 500-line threshold but remains within bounds.

### Data Flow Analysis

No data flow violations detected:
- UI DTOs (ShipDTO, ProjectileDTO, etc.) are properly defined in `game/ui/interfaces/`
- Color mappings (PROJECTILE_COLORS) correctly placed in UI layer
- Display coordinates handled only in UI layer
- UIConfig properly isolates layout constants

## Top 5 Priority Issues

1. **ADR-UI2-003 (MAJOR):** InputMapper class approaching god-class size (379 lines, 15+ methods). Consider future refactoring to improve maintainability.

2. **N/A - Overall architecture is healthy:** The UI-Framework shard demonstrates good architectural compliance. All layer dependencies flow in the correct direction, pygame is properly isolated, and cross-layer orchestration is well-documented.

## Conclusion

The UI-Framework shard is **architecturally sound**. The codebase demonstrates:
- Proper layer separation with UI correctly depending only on lower layers
- Pygame usage correctly isolated to UI layer only
- Well-documented intentional cross-layer orchestration
- Clean DTO boundaries for simulation-to-UI data transfer
- No circular dependencies

The single major finding (InputMapper complexity) is a maintainability observation rather than an architectural violation. No critical issues were identified.
