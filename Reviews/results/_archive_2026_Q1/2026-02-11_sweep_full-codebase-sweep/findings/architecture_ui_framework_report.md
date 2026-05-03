# Architecture Drift Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 22
- **Total Issues Found:** 10
- **Critical:** 2 | **Major:** 4 | **Minor:** 3 | **Info:** 1

### Scope
All Python files in `game/ui/` root, `game/ui/services/`, `game/ui/renderer/`, `game/ui/interfaces/`, `game/ui/orchestration/`, `game/ui/assets/`, `game/ui/components/`, `game/ui/utils/` -- excluding `game/ui/screens/` and `game/ui/panels/`.

### Files Scanned (22)
- `game/ui/__init__.py` (27 lines)
- `game/ui/colors.py` (35 lines)
- `game/ui/widgets.py` (101 lines)
- `game/ui/utils.py` (202 lines)
- `game/ui/services/__init__.py` (25 lines)
- `game/ui/services/validation_service.py` (72 lines)
- `game/ui/services/vehicle_class_service.py` (128 lines)
- `game/ui/services/battle_ui_service.py` (276 lines)
- `game/ui/services/component_service.py` (126 lines)
- `game/ui/services/ship_factory.py` (188 lines)
- `game/ui/services/ship_io_adapter.py` (101 lines)
- `game/ui/services/design_loader_adapter.py` (87 lines)
- `game/ui/renderer/__init__.py` (1 line, empty)
- `game/ui/renderer/camera.py` (154 lines)
- `game/ui/renderer/game_renderer.py` (224 lines)
- `game/ui/renderer/sprites.py` (132 lines)
- `game/ui/interfaces/battle_ui.py` (244 lines)
- `game/ui/interfaces/__init__.py` (25 lines)
- `game/ui/orchestration/__init__.py` (4 lines)
- `game/ui/orchestration/battle_orchestrator.py` (98 lines)
- `game/ui/assets/__init__.py` (4 lines)
- `game/ui/assets/ship_theme_manager.py` (313 lines)

---

## Findings

#### CRITICAL: Pygame in Core Layer -- ScreenshotManager
**ID:** ADR-UI2-001
**Location:** `game/core/screenshot_manager.py:4`
**Issue:** `import pygame` in the core layer violates the strict rule that `game/core/` has NO dependencies on UI frameworks. The `ScreenshotManager` class uses `pygame.display.get_surface()`, `pygame.Surface`, `pygame.Rect`, `pygame.image.save()`, and `pygame.error` throughout. This is a full pygame dependency embedded in the foundation layer.
**Impact:** The core layer cannot be used headlessly (e.g., for simulation-only testing, CI pipelines, or server-side game logic) without having pygame installed and initialized. Any module that imports from `game.core` transitively pulls in pygame. This defeats the purpose of layer separation.
**Recommendation:** Move `ScreenshotManager` to `game/ui/` (e.g., `game/ui/services/screenshot_manager.py`) since it is fundamentally a UI concern. Alternatively, extract a screenshot protocol in core and implement it in the UI layer.
**Effort:** Medium

#### CRITICAL: Pygame in Core Layer -- InputMapper
**ID:** ADR-UI2-002
**Location:** `game/core/input_mapper.py:26`
**Issue:** `import pygame` in the core layer. `InputMapper` directly references `pygame.KMOD_CTRL`, `pygame.KMOD_SHIFT`, `pygame.KMOD_ALT`, `pygame.key.name()`, and other pygame constants. The entire keybinding system is tightly coupled to pygame event types.
**Impact:** The input mapping system cannot be tested or used without pygame. This prevents headless operation and makes the core layer depend on a specific rendering framework. Any non-pygame frontend (e.g., a web UI or CLI) would need to bypass this entirely.
**Recommendation:** Move `InputMapper` to `game/ui/` or `game/engine/` layer. Alternatively, define framework-agnostic input action constants in core, and place the pygame-specific key resolution in the UI layer.
**Effort:** Complex (InputMapper is used widely; migration requires updating all import sites)

#### MAJOR: Renderer Directly Accesses Simulation Domain Objects
**ID:** ADR-UI2-003
**Location:** `game/ui/renderer/game_renderer.py:22-225`
**Issue:** The `draw_ship()` and `draw_hud()` functions accept raw `Ship` domain objects from the simulation layer and access their internal attributes extensively: `ship.layers[ltype].components`, `ship.resources.get_value(ResourceType.FUEL)`, `ship.forward_vector()`, `ship.angle`, `ship.radius`, `ship.mass`, `ship.drag`, `ship.total_thrust`, `comp.has_ability('WeaponAbility')`, `comp.major_classification`, etc. This bypasses the DTO boundary established by `IBattleUI` / `BattleUIService` in `game/ui/interfaces/`.
**Impact:** The renderer is tightly coupled to the Ship domain model's internal structure. Any refactoring of Ship internals (e.g., changing how layers work, renaming attributes) will break the renderer. The DTOs (`ShipDTO`, `ComponentDTO`) were created specifically to prevent this coupling but are not used by the renderer.
**Recommendation:** Refactor `draw_ship()` and `draw_hud()` to accept `ShipDTO` objects instead of raw `Ship` objects. Add any missing fields to the DTO if needed (e.g., `radius`, `drag`, `forward_vector`). This aligns the renderer with the established DTO pattern.
**Effort:** Medium

#### MAJOR: ShipFactory Uses pygame.math.Vector2 Instead of Core Vector2
**ID:** ADR-UI2-004
**Location:** `game/ui/services/ship_factory.py:19,113`
**Issue:** `ShipFactory` has a top-level `import pygame` (line 19) and uses `pygame.math.Vector2` as a type annotation in `configure_ship()` (line 113). The project has a framework-agnostic `game.core.math.Vector2` specifically designed to decouple from pygame. A service layer facade should use the core Vector2, not the pygame one.
**Impact:** The `ShipFactory` service cannot be instantiated without pygame installed, even though it is a facade meant to decouple UI from simulation. This prevents headless testing of the factory logic.
**Recommendation:** Replace `import pygame` with `from game.core.math import Vector2` and use the core `Vector2` type in the `configure_ship()` signature. The core Vector2 is API-compatible with pygame's.
**Effort:** Simple

#### MAJOR: DesignLoaderAdapter Has Hard Runtime Import of SimulationDesignLoader
**ID:** ADR-UI2-005
**Location:** `game/ui/services/design_loader_adapter.py:14`
**Issue:** `from game.simulation.services.design_loader import SimulationDesignLoader` is a top-level runtime import. The adapter's stated purpose is to "allow UI code to create Ship objects from design data without directly importing from game.simulation.services.design_loader" -- but it does exactly that at the module level. The class constructor creates a `SimulationDesignLoader` instance directly. Contrast with `ShipIOAdapter` which uses lazy import inside `__init__`.
**Impact:** Importing `design_loader_adapter` immediately triggers a load of the entire simulation design loader chain. The facade provides no decoupling benefit since the import happens at module load time regardless.
**Recommendation:** Move the `SimulationDesignLoader` import into a lazy import inside `__init__()`, consistent with the pattern used by `ShipIOAdapter`. This preserves the module-level decoupling the adapter was designed to provide.
**Effort:** Simple

#### MAJOR: Pygame TYPE_CHECKING Import in AI Layer
**ID:** ADR-UI2-006
**Location:** `game/ai/interfaces/controllable.py:19`
**Issue:** `from pygame.math import Vector2` inside a `TYPE_CHECKING` block in the AI layer. While this doesn't create a runtime dependency, it indicates the AI interface is architecturally aware of pygame -- a UI framework. The AI layer should depend only on core, simulation, and strategy per the architecture rules.
**Impact:** The type hints in the AI interface reference a UI framework type. This creates conceptual coupling and means type checkers (mypy, pyright) will require pygame to validate the AI layer. The project has `game.core.math.Vector2` for this exact purpose.
**Recommendation:** Replace `from pygame.math import Vector2` with `from game.core.math import Vector2` in the TYPE_CHECKING block.
**Effort:** Simple

#### MINOR: ScreenshotManager Accesses Private _renderer Attribute of StrategyScreen
**ID:** ADR-UI2-007
**Location:** `game/core/screenshot_manager.py:150,176`
**Issue:** `capture_strategy_layer()` accesses `scene._renderer.draw()` -- a private attribute of `StrategyScreen`. It also accesses `scene.build_queue_screen`, `scene.screen_width`, `scene.screen_height`, and `scene.ui.draw()`. This creates inappropriate intimacy between the core layer and specific UI screen implementations.
**Impact:** The ScreenshotManager is tightly coupled to the internal structure of `StrategyScreen`. Any refactoring of the strategy screen (renaming `_renderer`, changing the drawing pipeline) will break screenshot capture. A core-layer class should not know about UI screen internals.
**Recommendation:** This is part of the same issue as ADR-UI2-001. Moving ScreenshotManager to the UI layer resolves the layer violation. Additionally, the strategy screen should expose a public `capture()` or `render_to_surface()` method rather than having external code reach into private attributes.
**Effort:** Medium (combined with ADR-UI2-001)

#### MINOR: ValidationService Has Eager Runtime Import of Simulation Layer
**ID:** ADR-UI2-008
**Location:** `game/ui/services/validation_service.py:14`
**Issue:** `from game.simulation.entities.ship_loader import get_or_create_validator` is a top-level runtime import. While the UI layer is allowed to depend on simulation, this particular service was designed as a facade to decouple UI from simulation internals. An eager import partially undermines that goal.
**Impact:** Minimal operational impact since the UI layer can depend on simulation. However, the inconsistency with other service facades (which use lazy imports) reduces the decoupling benefit.
**Recommendation:** Consider converting to a lazy import inside `_get_validator()` for consistency with the adapter pattern used elsewhere in this package.
**Effort:** Simple

#### MINOR: game_renderer.py Uses Lazy Import Inside draw_ship Function
**ID:** ADR-UI2-009
**Location:** `game/ui/renderer/game_renderer.py:46-47`
**Issue:** `from game.ui.assets import ShipThemeManager` is a lazy import inside the `draw_ship()` function, followed by `ShipThemeManager.instance()`. This lazy import runs on every frame for every ship, creating unnecessary overhead. The import is within the UI layer (ui.renderer importing from ui.assets), so there is no layer violation.
**Impact:** Minor performance overhead from repeated lazy import resolution inside a hot rendering loop. Python caches module imports so the actual cost is small, but it is a code smell that suggests the dependency should be injected or imported at module level.
**Recommendation:** Move the import to the top of the file or inject the `ShipThemeManager` instance as a parameter to `draw_ship()`.
**Effort:** Simple

#### INFO: Consistent Use of Facade/Adapter Pattern in Services
**ID:** ADR-UI2-010
**Location:** `game/ui/services/` (all files)
**Issue:** The services package demonstrates a well-implemented facade pattern with `ShipFactory`, `ComponentService`, `VehicleClassService`, `ValidationService`, `ShipIOAdapter`, `DesignLoaderAdapter`, and `BattleUIService`. These facades successfully decouple most UI code from direct simulation imports. The `BattleUIService` properly converts domain objects to DTOs (`ShipDTO`, `ComponentDTO`, etc.) through the `IBattleUI` protocol.
**Impact:** Positive architectural pattern. The main gap is that the renderer (`game_renderer.py`) does not use these DTOs, undermining the boundary they establish.
**Recommendation:** Continue extending this pattern. Ensure the renderer and other direct consumers of simulation objects are migrated to use DTOs.
**Effort:** N/A (observation)

---

## Top 5 Priority Issues

1. **ADR-UI2-001 (CRITICAL): Pygame in Core -- ScreenshotManager** -- The core layer must remain framework-agnostic. ScreenshotManager belongs in the UI layer. This is the most fundamental layer violation since it affects the foundation of the architecture.

2. **ADR-UI2-002 (CRITICAL): Pygame in Core -- InputMapper** -- Same principle as above. The input mapping system's pygame dependency in core prevents headless operation and violates the foundational layer rule. More complex to fix due to widespread usage.

3. **ADR-UI2-003 (MAJOR): Renderer Bypasses DTO Boundary** -- The game renderer directly accesses Ship domain internals instead of using the DTO interface that was explicitly created for this purpose. This is the largest coupling surface in the UI framework layer.

4. **ADR-UI2-004 (MAJOR): ShipFactory Uses pygame.math.Vector2** -- A service facade using `import pygame` at runtime defeats its purpose as a decoupling layer. Simple fix: switch to `game.core.math.Vector2`.

5. **ADR-UI2-006 (MAJOR): Pygame TYPE_CHECKING in AI Layer** -- The AI layer should not reference pygame at all, even in TYPE_CHECKING blocks. Simple fix: use `game.core.math.Vector2`.
