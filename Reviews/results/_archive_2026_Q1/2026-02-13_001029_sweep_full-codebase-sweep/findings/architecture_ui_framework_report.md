# Architecture Drift Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 21
- **Total Issues Found:** 5
- **Critical:** 0 | **Major:** 2 | **Minor:** 2 | **Info:** 1

## Findings

#### MAJOR: pygame.math.Vector2 Usage in game_renderer.py Instead of game.core.math.Vector2
**ID:** ADR-UI2-001
**Location:** `game/ui/renderer/game_renderer.py:121`
**Issue:** The renderer uses `pygame.math.Vector2` directly when calculating component positions in the draw_ship function, creating a dependency on pygame's math types within rendering logic. While this file is in the UI layer (where pygame is allowed), it inconsistently mixes pygame.math.Vector2 with what should be game.core.math.Vector2 for world coordinate calculations.
**Impact:** Creates coupling between rendering math and pygame's specific implementation. Makes it harder to test rendering logic in isolation or use alternative math libraries.
**Recommendation:** Use `game.core.math.Vector2` consistently for world coordinate calculations. The pygame.math.Vector2 should only be used for screen-space operations within drawing functions.
**Effort:** Simple

#### MAJOR: God Class Potential in ShipThemeManager
**ID:** ADR-UI2-002
**Location:** `game/ui/assets/ship_theme_manager.py:1-314`
**Issue:** ShipThemeManager has 314 lines with 15+ methods handling multiple responsibilities: theme discovery, image loading, caching, portrait loading, metrics calculation, and fallback image generation. While not exceeding 500 lines, this class is approaching god-class territory and handles too many distinct concerns.
**Impact:** Difficult to test individual concerns in isolation. Changes to one responsibility (e.g., caching strategy) risk breaking others. Portrait loading was added (lines 219-314) as a separate concern that could be its own class.
**Recommendation:** Consider extracting concerns: (1) ThemeDiscovery - scanning and parsing theme.json files, (2) ImageCache - caching loaded surfaces with LRU policy, (3) PortraitLoader - portrait-specific loading logic with name conversion.
**Effort:** Medium

#### MINOR: Lazy Import Pattern in ship_factory.py Could Be Structured Better
**ID:** ADR-UI2-003
**Location:** `game/ui/services/ship_factory.py:55-56, 83-84`
**Issue:** The ShipFactory uses lazy imports inside methods (`from game.core.registry import get_default_registries` and `from game.simulation.entities.ship import Ship`). While these imports are valid for the UI layer, scattering imports inside methods makes dependency tracking harder.
**Impact:** Code analysis tools may miss these dependencies. Makes it harder to understand the module's full dependency graph at a glance.
**Recommendation:** Consider consolidating lazy imports into a single `_import_dependencies()` method or using TYPE_CHECKING imports with runtime-conditional loading in `__init__`.
**Effort:** Simple

#### MINOR: TYPE_CHECKING Import for GameRegistries Not Used Consistently
**ID:** ADR-UI2-004
**Location:** `game/ui/services/ship_factory.py:21-24`
**Issue:** ShipFactory imports `Ship` and `GameRegistries` in TYPE_CHECKING block, but only uses these for type hints. This is correct usage, but the runtime import of Ship at line 83 duplicates the type hint import. The pattern is slightly inconsistent.
**Impact:** Minor inconsistency in import patterns. No functional impact.
**Recommendation:** Document the pattern in the module docstring or unify the approach across services.
**Effort:** Simple

#### INFO: BattleOrchestrator Correctly Documents Cross-Layer Imports
**ID:** ADR-UI2-005
**Location:** `game/ui/orchestration/battle_orchestrator.py:1-99`
**Issue:** This is NOT a violation - documenting as INFO. BattleOrchestrator imports from AI layer (game.ai.controller, game.ai.interfaces) and engine layer (game.engine.spatial). These cross-layer imports are explicitly documented in the module docstring as intentional orchestration-layer behavior.
**Impact:** None - this is the correct pattern for orchestration modules in the UI layer.
**Recommendation:** This serves as a model pattern for other orchestration code. The explicit documentation of cross-layer imports should be replicated elsewhere.
**Effort:** N/A

## Detailed Analysis

### Phase 1: Import Graph Analysis

All 21 files were scanned for imports. The UI layer correctly uses:
- `game.core.*` imports - VALID (Core depends on nothing)
- `game.simulation.*` imports - VALID (UI can depend on Simulation)
- `game.ai.*` imports - VALID (UI can depend on AI)
- `game.engine.*` imports - VALID (UI can depend on Engine)

No violations of the layer hierarchy were found. All imports follow the allowed dependency directions.

### Phase 2: Pygame Boundary Violations

All pygame imports (`import pygame`, `from pygame`) are within the UI layer:
- `game/ui/utils.py` - pygame for Surface operations
- `game/ui/services/ship_factory.py` - pygame.math.Vector2
- `game/ui/services/screenshot_manager.py` - pygame for screenshots
- `game/ui/services/input_mapper.py` - pygame for key constants
- `game/ui/renderer/*.py` - pygame for rendering
- `game/ui/assets/ship_theme_manager.py` - pygame for image loading

This is the expected location for pygame usage. No pygame imports found outside UI layer in this shard.

### Phase 3: Circular Dependencies

No circular dependencies detected in this shard. The UI layer imports from lower layers without any back-references.

### Phase 4: God Classes and Inappropriate Intimacy

One potential god class identified (ShipThemeManager). Other classes are well-focused:
- Services (validation, component, vehicle_class) are single-purpose facades
- BattleUIService correctly converts domain objects to DTOs
- Camera and rendering utilities are cohesive

### Phase 5: Data Flow Violations

No data flow violations detected:
- DTOs in battle_ui.py correctly separate UI concerns from simulation
- Colors defined in PROJECTILE_COLORS are UI-specific (correct layer)
- No screen coordinates flowing into non-UI logic

### Phase 6: Dependency Direction Violations

No dependency direction violations:
- No lower-layer code registering UI callbacks
- No simulation code handling UI exceptions
- Services correctly wrap simulation layer functionality

## Top 5 Priority Issues

1. **ADR-UI2-001 (MAJOR)**: Inconsistent Vector2 usage in game_renderer.py - should use game.core.math.Vector2 for world coordinates to maintain consistency with the rest of the codebase.

2. **ADR-UI2-002 (MAJOR)**: ShipThemeManager approaching god-class size with 15+ methods and 314 lines. Portrait loading (lines 219-314) is a distinct concern that could be extracted.

3. **ADR-UI2-003 (MINOR)**: Lazy import pattern in ship_factory.py scatters dependencies across methods rather than centralizing them.

4. **ADR-UI2-004 (MINOR)**: TYPE_CHECKING import pattern slightly inconsistent in ship_factory.py.

5. **ADR-UI2-005 (INFO)**: BattleOrchestrator provides a good model for documenting intentional cross-layer orchestration.

## Appendix: Files Scanned

1. `game/ui/__init__.py`
2. `game/ui/utils.py`
3. `game/ui/config.py`
4. `game/ui/colors.py`
5. `game/ui/services/__init__.py`
6. `game/ui/services/validation_service.py`
7. `game/ui/services/vehicle_class_service.py`
8. `game/ui/services/component_service.py`
9. `game/ui/services/ship_factory.py`
10. `game/ui/services/screenshot_manager.py`
11. `game/ui/services/design_loader_adapter.py`
12. `game/ui/services/input_mapper.py`
13. `game/ui/services/ship_io.py`
14. `game/ui/services/ship_io_adapter.py`
15. `game/ui/services/battle_ui_service.py`
16. `game/ui/renderer/__init__.py`
17. `game/ui/renderer/game_renderer.py`
18. `game/ui/renderer/camera.py`
19. `game/ui/renderer/sprites.py`
20. `game/ui/interfaces/__init__.py`
21. `game/ui/interfaces/battle_ui.py`
22. `game/ui/orchestration/__init__.py`
23. `game/ui/orchestration/battle_orchestrator.py`
24. `game/ui/assets/__init__.py`
25. `game/ui/assets/ship_theme_manager.py`
