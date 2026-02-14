# Architecture Drift Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 25
- **Total Issues Found:** 5
- **Critical:** 0 | **Major:** 2 | **Minor:** 2 | **Info:** 1

## Analysis Overview

The UI-Framework shard consists of:
- **Root files (4):** `__init__.py`, `utils.py`, `config.py`, `colors.py`
- **Services (13):** Ship factory, component service, validation, IO adapters, battle services, input mapper, screenshot manager, tkinter utils
- **Renderer (4):** Camera, sprites, game renderer, `__init__.py`
- **Interfaces (2):** Battle UI protocol and DTOs
- **Orchestration (2):** Battle orchestrator
- **Assets (2):** Ship theme manager

### Architecture Compliance Summary

The UI layer is correctly positioned as the top layer in the dependency hierarchy. All imports from lower layers (core, simulation, ai, engine, strategy) are **architecturally valid** since UI is permitted to depend on all lower layers.

**Key Observations:**
1. **Layer dependencies are correct** - UI properly imports from core, simulation, ai, and engine
2. **Pygame usage is appropriate** - All pygame imports are within the UI layer as required
3. **TYPE_CHECKING blocks used appropriately** - Several files use TYPE_CHECKING to reduce runtime coupling while maintaining type safety
4. **Services provide good abstraction** - The services layer (ship_factory, component_service, validation_service) properly encapsulates simulation layer access

## Findings

#### MAJOR: ShipIO Direct Import of Simulation Entity
**ID:** ADR-UI2-001
**Location:** `game/ui/services/ship_io.py:20`
**Issue:** Direct import of `Ship` class from simulation layer at module level
**Code:**
```python
from game.simulation.entities.ship import Ship
```
**Impact:** While UI is allowed to import from simulation, this direct entity import in a service file slightly reduces the decoupling benefits that the adapter pattern provides. The file's docstring indicates it was moved from simulation layer (PROJ-113) and uses Ship.from_dict() and Ship.to_dict() directly.
**Recommendation:** Consider using TYPE_CHECKING for the type hint and passing the entity conversion through the DesignLoaderAdapter, maintaining consistency with other service files.
**Effort:** Medium

#### MAJOR: Camera Uses pygame.math.Vector2 Instead of Core Vector2
**ID:** ADR-UI2-002
**Location:** `game/ui/renderer/camera.py:14,46,60,89,96,116-132,143,146`
**Issue:** Camera module uses `pygame.math.Vector2` for position and calculations instead of the core `game.core.math.Vector2`
**Code:**
```python
self.position = pygame.math.Vector2(0, 0)
# ... multiple uses of pygame.math.Vector2
```
**Impact:** Creates implicit coupling between the camera interface and pygame. If the position were passed to non-UI code or stored in DTOs, this would cause type mismatches. Currently contained within UI layer but reduces consistency.
**Recommendation:** Use `game.core.math.Vector2` for consistency with DTOs and other services. The UI layer can still use pygame.math.Vector2 internally for rendering calculations if needed.
**Effort:** Simple

#### MINOR: Game Renderer Inline Import of ShipThemeManager
**ID:** ADR-UI2-003
**Location:** `game/ui/renderer/game_renderer.py:68-69`
**Issue:** Late import of `ShipThemeManager` inside the `draw_ship` function
**Code:**
```python
def draw_ship(surface, ship, camera):
    # ...
    from game.ui.assets import ShipThemeManager
    theme_mgr = ShipThemeManager.instance()
```
**Impact:** While this is intra-UI layer (no architectural violation), inline imports inside frequently-called functions can have performance implications and make dependencies less visible.
**Recommendation:** Move import to module level. The ShipThemeManager is a singleton with lazy initialization, so there's no circular dependency risk.
**Effort:** Simple

#### MINOR: BattleOrchestrator Mixing Layer Concerns
**ID:** ADR-UI2-004
**Location:** `game/ui/orchestration/battle_orchestrator.py:23-26`
**Issue:** The orchestrator explicitly imports from three different layers (ai, engine)
**Code:**
```python
from game.ai.controller import AIController
from game.ai.interfaces import ShipControllableAdapter
from game.engine.spatial import SpatialGrid
```
**Impact:** This is documented as intentional (see docstring lines 13-21), but it creates a focal point of cross-layer coupling. The file acknowledges this is a "boundary-crossing module."
**Recommendation:** This is acceptable as documented. The architecture correctly places orchestration in the UI layer. Consider adding this to architectural documentation as an example of valid cross-layer coordination.
**Effort:** N/A (Intentional design)

#### INFO: TYPE_CHECKING Blocks Used Appropriately
**ID:** ADR-UI2-005
**Location:** Multiple files
**Issue:** Several files use TYPE_CHECKING blocks for simulation imports
**Files Using Pattern:**
- `game/ui/services/battle_factories.py:14,22-23` - Ship import
- `game/ui/services/battle_ui_service.py:12,24-26` - BattleService, Ship
- `game/ui/services/ship_factory.py:17,21-23` - pygame, Ship, GameRegistries
- `game/ui/services/validation_service.py:12,17-20` - LayerType, Ship, Component
- `game/ui/orchestration/battle_orchestrator.py:22,28-29` - Ship
**Impact:** This is a positive pattern that reduces runtime coupling while maintaining type safety. Not a violation.
**Recommendation:** Continue using this pattern. Document it as a best practice for UI-layer services.
**Effort:** N/A (Already following best practice)

## Top 5 Priority Issues

1. **ADR-UI2-002 (Major):** Camera using pygame.math.Vector2 creates inconsistency with core Vector2 used elsewhere. Easy fix with moderate codebase-wide benefit for consistency.

2. **ADR-UI2-001 (Major):** ShipIO direct Ship import slightly undermines the adapter pattern. Consider aligning with the pattern used by other service files.

3. **ADR-UI2-003 (Minor):** Inline import in game_renderer.py draw_ship function. Quick fix that improves performance visibility and code clarity.

4. **ADR-UI2-004 (Minor):** BattleOrchestrator cross-layer imports are documented and intentional - this is noted as information rather than a fix item.

5. **ADR-UI2-005 (Info):** TYPE_CHECKING pattern is a positive observation - worth documenting as a best practice.

## Files Scanned (25 total)

### Root (4 files)
| File | Lines | Issues |
|------|-------|--------|
| game/ui/__init__.py | 28 | None |
| game/ui/utils.py | 203 | None |
| game/ui/config.py | 67 | None |
| game/ui/colors.py | 46 | None |

### Services (13 files)
| File | Lines | Issues |
|------|-------|--------|
| game/ui/services/__init__.py | 37 | None |
| game/ui/services/vehicle_class_service.py | 129 | None |
| game/ui/services/component_service.py | 127 | None |
| game/ui/services/design_loader_adapter.py | 88 | None |
| game/ui/services/ship_io_adapter.py | 104 | None |
| game/ui/services/input_mapper.py | 379 | None |
| game/ui/services/tkinter_utils.py | 231 | None |
| game/ui/services/battle_factories.py | 201 | None |
| game/ui/services/battle_ui_service.py | 301 | None |
| game/ui/services/ship_io.py | 135 | ADR-UI2-001 |
| game/ui/services/screenshot_manager.py | 215 | None |
| game/ui/services/ship_factory.py | 191 | None |
| game/ui/services/validation_service.py | 78 | None |

### Renderer (4 files)
| File | Lines | Issues |
|------|-------|--------|
| game/ui/renderer/__init__.py | ~1 | None |
| game/ui/renderer/camera.py | 156 | ADR-UI2-002 |
| game/ui/renderer/sprites.py | 114 | None |
| game/ui/renderer/game_renderer.py | 167 | ADR-UI2-003 |

### Interfaces (2 files)
| File | Lines | Issues |
|------|-------|--------|
| game/ui/interfaces/__init__.py | 26 | None |
| game/ui/interfaces/battle_ui.py | 245 | None |

### Orchestration (2 files)
| File | Lines | Issues |
|------|-------|--------|
| game/ui/orchestration/__init__.py | 5 | None |
| game/ui/orchestration/battle_orchestrator.py | 99 | ADR-UI2-004 |

### Assets (2 files)
| File | Lines | Issues |
|------|-------|--------|
| game/ui/assets/__init__.py | 5 | None |
| game/ui/assets/ship_theme_manager.py | 314 | None |

## Positive Patterns Observed

1. **Service Adapters:** Files like `design_loader_adapter.py`, `ship_io_adapter.py`, `component_service.py`, and `validation_service.py` properly wrap simulation layer functionality for UI consumption.

2. **Dependency Injection:** Services accept optional dependencies (registry_provider, design_loader, validator) for testability while providing sensible defaults.

3. **DTO Pattern:** `battle_ui.py` defines frozen dataclasses (ShipDTO, ComponentDTO, etc.) that provide immutable snapshots for UI rendering.

4. **Protocol Definition:** `IBattleUI` protocol in battle_ui.py defines a clean interface that implementations must satisfy.

5. **Singleton Pattern:** `SpriteManager`, `ShipThemeManager`, `ScreenshotManager` use consistent SingletonMeta pattern with proper thread safety.

6. **Type Hints:** Comprehensive type hints throughout the codebase improve maintainability.

7. **Cross-Layer Documentation:** Files like `game_renderer.py` and `battle_orchestrator.py` document their cross-layer dependencies explicitly.
