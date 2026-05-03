# Architecture Drift Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 24
- **Total Issues Found:** 4
- **Critical:** 0 | **Major:** 1 | **Minor:** 2 | **Info:** 1

## Scan Coverage

The following files were exhaustively analyzed for architecture violations:

**Root Files (4):**
- `game/ui/__init__.py`
- `game/ui/utils.py`
- `game/ui/config.py`
- `game/ui/colors.py`

**Services (11):**
- `game/ui/services/__init__.py`
- `game/ui/services/validation_service.py`
- `game/ui/services/vehicle_class_service.py`
- `game/ui/services/component_service.py`
- `game/ui/services/ship_factory.py`
- `game/ui/services/design_loader_adapter.py`
- `game/ui/services/ship_io_adapter.py`
- `game/ui/services/battle_ui_service.py`
- `game/ui/services/screenshot_manager.py`
- `game/ui/services/ship_io.py`
- `game/ui/services/input_mapper.py`

**Renderer (4):**
- `game/ui/renderer/__init__.py`
- `game/ui/renderer/camera.py`
- `game/ui/renderer/sprites.py`
- `game/ui/renderer/game_renderer.py`

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

#### MAJOR: Direct Simulation Layer Import in ship_io.py
**ID:** ADR-UI2-001
**Location:** `game/ui/services/ship_io.py:16`
**Issue:** Direct import of `Ship` from simulation layer creates tight coupling
**Code:**
```python
from game.simulation.entities.ship import Ship
```
**Impact:** While this file is correctly placed in UI (moved from simulation per PROJ-113 due to tkinter dependency), the direct Ship import means the UI service depends directly on the simulation entity implementation rather than using a protocol or DTO. This creates coupling that makes the UI harder to test in isolation and requires the full simulation layer to be present.
**Recommendation:** Create a protocol/interface for the ship data needed by ShipIO (name, to_dict(), from_dict() methods). The service could accept data dicts rather than Ship objects directly, or use a protocol type.
**Effort:** Medium

#### MINOR: TYPE_CHECKING Import from Simulation in ship_factory.py
**ID:** ADR-UI2-002
**Location:** `game/ui/services/ship_factory.py:22-23`
**Issue:** TYPE_CHECKING imports from simulation layer for type hints
**Code:**
```python
if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.core.registry import GameRegistries
```
**Impact:** This is a milder form of coupling - the runtime code doesn't import Ship directly, only for type hints. However, it indicates the service's interface is defined in terms of simulation entities rather than abstractions. The service also imports Ship at runtime inside `create_from_design()` (line 83).
**Recommendation:** This is partially acceptable as the service is an adapter/facade. Consider whether a DTO return type would be cleaner, but current design is functional.
**Effort:** Medium

#### MINOR: TYPE_CHECKING Import from Simulation in battle_ui_service.py
**ID:** ADR-UI2-003
**Location:** `game/ui/services/battle_ui_service.py:26-27`
**Issue:** TYPE_CHECKING imports from simulation layer
**Code:**
```python
if TYPE_CHECKING:
    from game.simulation.services import BattleService
    from game.simulation.entities.ship import Ship
```
**Impact:** The service correctly converts simulation objects to DTOs for UI consumption (good pattern). The TYPE_CHECKING imports are for internal implementation details and don't affect the public interface which exposes only DTOs. This is actually the correct pattern for a UI adapter service.
**Recommendation:** No action needed - this is the intended design pattern. The service wraps simulation objects and exposes only DTOs to the UI.
**Effort:** N/A

#### INFO: Intentional Cross-Layer Orchestration in battle_orchestrator.py
**ID:** ADR-UI2-004
**Location:** `game/ui/orchestration/battle_orchestrator.py:23-26`
**Issue:** Direct imports from AI layer (intentional)
**Code:**
```python
from game.ai.controller import AIController
from game.ai.interfaces import ShipControllableAdapter
from game.engine.spatial import SpatialGrid
```
**Impact:** This is explicitly documented as an intentional boundary-crossing module. The file comment explains: "This class handles AI controller creation, which requires importing from the AI layer. By placing this in the UI layer instead of Simulation, we maintain proper layer boundaries: - Simulation depends on Core only - UI coordinates between all layers"
**Recommendation:** No action needed - this is architecturally correct. The UI layer is allowed to depend on all other layers and serve as an orchestration point.
**Effort:** N/A

## Positive Observations

### Well-Designed Service Facades
The `game/ui/services/` package demonstrates good architecture:
1. **ValidationService** - Wraps simulation validator without exposing internals
2. **VehicleClassService** - Uses IRegistryProvider protocol for DI
3. **ComponentService** - Clean facade over registry with optional DI
4. **BattleUIService** - Properly converts simulation entities to immutable DTOs
5. **ShipIOAdapter** - Clean adapter pattern wrapping ShipIO

### Proper DTO Pattern
`game/ui/interfaces/battle_ui.py` defines frozen dataclasses (ShipDTO, ProjectileDTO, BeamDTO, etc.) that provide immutable snapshots for safe UI consumption. This is the correct pattern for layer separation.

### UI-Only Pygame Usage
All pygame imports are correctly confined to UI layer files:
- `game/ui/utils.py` - pygame.Surface, pygame.Rect
- `game/ui/renderer/camera.py` - pygame.math.Vector2, events
- `game/ui/renderer/sprites.py` - pygame.image
- `game/ui/renderer/game_renderer.py` - pygame.draw
- `game/ui/assets/ship_theme_manager.py` - pygame.image
- `game/ui/services/screenshot_manager.py` - pygame.display, pygame.image
- `game/ui/services/input_mapper.py` - pygame.KEYDOWN, modifiers

### Color Constants Correctly Located
`game/ui/colors.py` contains UI color definitions (per PROJ-113 migration from core to UI layer), including projectile colors now in `battle_ui_service.py`.

## Top 5 Priority Issues

1. **ADR-UI2-001 (MAJOR)** - `ship_io.py` directly imports Ship entity. While functionally correct, could be cleaner with a protocol.

2. **ADR-UI2-002 (MINOR)** - `ship_factory.py` has runtime imports of Ship inside methods. This is acceptable for a factory/adapter but worth noting.

3-5. No additional priority issues - the UI-Framework shard is generally well-architected with proper use of facades, adapters, and DTOs.

## Conclusion

The UI-Framework shard demonstrates good architectural practices overall. The services package correctly implements the facade/adapter pattern to decouple UI from simulation. The one notable issue (ADR-UI2-001) is a minor coupling that could be improved but doesn't prevent headless operation or cause circular dependencies.

The intentional orchestration in `battle_orchestrator.py` is correctly placed in UI as the coordination point between layers, and is well-documented.

No critical issues were found. The pygame boundary is properly maintained.
