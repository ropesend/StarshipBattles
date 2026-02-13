# Architecture Drift Sweep: Foundation

## Summary
- **Shard:** Foundation
- **Directories Scanned:** game/core/ (20 files), game/ai/ (8 files), game/research/ (11 files), game/engine/ (4 files)
- **Files Scanned:** 43
- **Total Issues Found:** 12
- **Critical:** 3 | **Major:** 4 | **Minor:** 4 | **Info:** 1

## Findings

#### CRITICAL: Pygame imported in game/core/input_mapper.py (Core Layer Violation)
**ID:** ADR-FND-001
**Location:** `game/core/input_mapper.py:26,34-38,146-160,162-178,202`
**Issue:** The core layer must have NO framework dependencies, but `input_mapper.py` imports `pygame` at the top level and uses `pygame.KMOD_CTRL`, `pygame.KMOD_SHIFT`, `pygame.KMOD_ALT`, `pygame.KEYDOWN`, and `pygame.K_*` constants throughout. This directly violates the "Core - NO dependencies on simulation, strategy, ui, or ai" rule and the "Pygame is UI-only" rule.
**Impact:** Any code importing `game.core.input_mapper` (or `game.core` via `__init__.py` if it were re-exported) forces a pygame dependency. This prevents headless testing of core utilities and couples the foundation layer to a specific rendering framework. The `InputMapper` class cannot be used in a headless server or non-pygame frontend without pygame installed.
**Recommendation:** Split into two parts: (1) Keep `InputAction` and `KeyBinding` in core (already clean in `input_actions.py`). (2) Move `InputMapper` to `game/ui/input/` since it is inherently a pygame event processor. The core layer should only define the action enum and binding data model; the pygame-specific resolution belongs in the UI layer.
**Effort:** Medium

#### CRITICAL: Pygame imported in game/core/screenshot_manager.py (Core Layer Violation)
**ID:** ADR-FND-002
**Location:** `game/core/screenshot_manager.py:4,51,67-79,147,172-180,186`
**Issue:** `ScreenshotManager` imports `pygame` at the top level and uses `pygame.display.get_surface()`, `pygame.image.save()`, `pygame.Surface()`, `pygame.Rect()`, and `pygame.error` throughout. This is a clear violation of the architecture rule that pygame is UI-only and that core has no framework dependencies.
**Impact:** The `ScreenshotManager` singleton cannot be instantiated without pygame. It also has deep knowledge of `StrategyScreen` internals in `capture_strategy_layer()` (accessing `scene._renderer`, `scene.ui`, `scene.build_queue_screen` -- private attributes of a UI class). This creates tight coupling from core to the UI layer.
**Recommendation:** Move `ScreenshotManager` to `game/ui/` (e.g., `game/ui/screenshot_manager.py`). It is fundamentally a UI service that captures pygame surfaces. If a lightweight core interface is needed, define a protocol in core and implement it in UI.
**Effort:** Simple

#### CRITICAL: Research scene imports from game.ui (Layer Violation)
**ID:** ADR-FND-003
**Location:** `game/research/ui/research_scene.py:19`
**Issue:** `ResearchTreeScene` imports `from game.ui.renderer.camera import Camera`. The architecture rules state that `game/research/` depends on core only, with NO simulation, NO strategy, NO ui dependencies. This is a direct violation of the layer boundary.
**Impact:** The research package cannot be used independently of the UI layer. This creates a circular-like dependency concern: research depends on UI, and UI presumably depends on research. The `Camera` class is a concrete UI implementation being pulled into a supposedly core-adjacent package.
**Recommendation:** Either (1) Move all of `game/research/ui/` into `game/ui/research/` since these files are inherently UI components (they use pygame, pygame_gui), or (2) Use the existing `ICamera` protocol from `game.core.protocols` for construction too -- inject a camera instance rather than importing the concrete class. Option 1 is cleaner since `research_controls.py`, `research_renderer.py`, and `research_scene.py` are all full pygame UI code.
**Effort:** Medium

#### MAJOR: Core protocols.py TYPE_CHECKING import from simulation layer
**ID:** ADR-FND-004
**Location:** `game/core/protocols.py:42`
**Issue:** Inside `TYPE_CHECKING` block: `from game.simulation.entities.layer_data import LayerData`. While TYPE_CHECKING imports do not create runtime dependencies, they indicate that the core layer's type signatures are aware of and coupled to simulation-layer types. The `IPostBattleShip` and `IResourceHolder` protocols in core reference `LayerData` from the simulation layer in their `layers` property type hints.
**Impact:** This is an architectural awareness violation. Core protocols should use generic types (`Any`, `Dict`) for cross-layer boundaries rather than referencing concrete simulation types. If `LayerData` changes, core protocol signatures need updating.
**Recommendation:** Replace `Dict['LayerType', 'LayerData']` with `Dict[Any, Any]` in the protocol definitions, or define a `ILayerData` protocol in core that `LayerData` satisfies. This removes the import entirely.
**Effort:** Simple

#### MAJOR: AI controllable.py TYPE_CHECKING import of pygame.math.Vector2
**ID:** ADR-FND-005
**Location:** `game/ai/interfaces/controllable.py:19`
**Issue:** Inside `TYPE_CHECKING` block: `from pygame.math import Vector2`. The AI layer should have NO pygame dependency per architecture rules ("Pygame is UI-only"). While this is only a type annotation import, it creates a conceptual dependency on pygame types in the AI interface layer.
**Impact:** The type hints reference `pygame.math.Vector2` rather than `game.core.math.Vector2`. This is misleading since the project has its own framework-agnostic `Vector2` in core. Type checkers will expect pygame types where core types should be used.
**Recommendation:** Change the TYPE_CHECKING import to use `from game.core.math import Vector2` instead. The core `Vector2` is API-compatible with pygame's `Vector2` and is the correct type to reference.
**Effort:** Simple

#### MAJOR: Research UI files use pygame directly (Misplaced in package hierarchy)
**ID:** ADR-FND-006
**Location:** `game/research/ui/research_controls.py:11-16`, `game/research/ui/research_renderer.py:9`, `game/research/ui/research_scene.py:14-15`
**Issue:** Three files in `game/research/ui/` use `import pygame`, `import pygame_gui`, and `from pygame_gui.elements import ...`. Per architecture rules, `game/research/` depends on core only, with NO ui dependencies. These files are full pygame UI components (creating `pygame.Rect`, `pygame.Surface`, `pygame_gui.UIManager`, etc.) but are located under the research package rather than the UI package.
**Impact:** The research package as a whole cannot be treated as a core-adjacent, framework-agnostic module. Any import of `game.research.ui` forces a pygame dependency. The data and systems sub-packages within research are clean, but the ui sub-package violates the layer rules.
**Recommendation:** Move `game/research/ui/` to `game/ui/research/` (i.e., `game/ui/research/research_scene.py`, etc.). The research data models and service logic remain in `game/research/data/` and `game/research/systems/`. This cleanly separates the framework-agnostic research logic from its pygame presentation layer.
**Effort:** Medium

#### MAJOR: AIController deep attribute chain (Law of Demeter violation)
**ID:** ADR-FND-007
**Location:** `game/ai/controller.py:410`
**Issue:** The expression `own_ship.formation.master.formation.members.remove(own_ship)` traverses 5 levels of object graph in a single statement. This is a severe Law of Demeter violation -- the AI controller reaches deep into the formation data structure to mutate a list on a related object.
**Impact:** This creates fragile coupling: any change to the formation data model (e.g., renaming `formation.members`, changing `master` to return an ID instead of an object) breaks this code silently. It also makes the code hard to test -- mocking requires setting up deeply nested object structures.
**Recommendation:** Add a method to the `IControllable` interface (or Ship/formation) like `leave_formation()` that encapsulates the internal formation cleanup. The AI controller should call a single method rather than reaching into internals.
**Effort:** Simple

#### MINOR: UIConfig class in game/core/config.py contains UI-specific constants
**ID:** ADR-FND-008
**Location:** `game/core/config.py:132-198`
**Issue:** The `UIConfig` class in the core layer contains UI-specific layout constants (font sizes, panel dimensions, alpha values, sidebar widths, grid spacing). While having named constants is good practice, placing UI layout constants in the core layer means core "knows about" UI concerns like `TOAST_WIDTH`, `PANEL_ALPHA`, `FONT_TITLE`, `STATS_PANEL_WIDTH`, and `STRATEGY_SIDEBAR_WIDTH`.
**Impact:** This is a mild data flow violation. Core should contain domain/game-logic constants only. UI layout constants belong in the UI layer. Changes to UI layout require modifying core files.
**Recommendation:** Move `UIConfig` to `game/ui/config.py` or `game/ui/ui_config.py`. Core's `config.py` should only contain `DisplayConfig`, `AIConfig`, `PhysicsConfig`, and `BattleConfig` which are used by non-UI layers.
**Effort:** Simple

#### MINOR: ScreenshotManager.capture_strategy_layer accesses private UI attributes
**ID:** ADR-FND-009
**Location:** `game/core/screenshot_manager.py:126-187`
**Issue:** The `capture_strategy_layer()` method accesses `scene._renderer` (private attribute with underscore prefix), and uses `hasattr` to probe for `scene.ui`, `scene.build_queue_screen`, and `scene.SIDEBAR_WIDTH`. This method has deep knowledge of the `StrategyScreen` internal structure.
**Impact:** This is inappropriate intimacy -- a core-layer class knows the internal structure of a specific UI screen. Any refactoring of `StrategyScreen` (which is actively being decomposed in PROJ-86) risks breaking this method.
**Recommendation:** When moving `ScreenshotManager` to the UI layer (per ADR-FND-002), refactor `capture_strategy_layer` to accept a rendering callback or surface rather than reaching into scene internals.
**Effort:** Simple (addressed when fixing ADR-FND-002)

#### MINOR: Engine collision.py TYPE_CHECKING import from simulation layer
**ID:** ADR-FND-010
**Location:** `game/engine/collision.py:55`
**Issue:** Inside `TYPE_CHECKING` block: `from game.simulation.entities.ship import Ship`. The engine layer is documented as a "thin orchestration layer" but its exact dependency rules are not explicitly stated. However, importing from simulation in TYPE_CHECKING indicates the collision system's type signatures are coupled to the concrete `Ship` class.
**Impact:** Mild. The `process_ramming` method uses `List['Ship']` in its type hint. At runtime, it accesses ship attributes directly (`s.is_alive`, `s.current_target`, `s.radius`, `s.position`, `s.combat_engine`). This works via duck typing but the type annotation creates a conceptual dependency.
**Recommendation:** Define a protocol (e.g., `IRammableEntity`) in core for the attributes the collision system needs, and use that instead of the concrete `Ship` type.
**Effort:** Simple

#### MINOR: Constants file mixes UI concerns (colors, fonts) with game logic
**ID:** ADR-FND-011
**Location:** `game/core/constants.py:42-49`
**Issue:** The constants file defines `WHITE`, `BLACK`, `BLUE`, `RED`, `GREEN` color tuples and `FONT_MAIN = "Arial"` alongside game-logic enums like `AttackType`, `GameState`, `LayerType`. Colors and font names are UI rendering concerns that do not belong in the core constants module.
**Impact:** Low. These constants create a conceptual mixing of concerns but do not create runtime dependencies. However, they set a precedent for adding more UI-specific values to core.
**Recommendation:** Move `WHITE`, `BLACK`, `BLUE`, `RED`, `GREEN`, and `FONT_MAIN` to a UI-layer constants file (e.g., `game/ui/colors.py` or `game/ui/ui_constants.py`).
**Effort:** Simple

#### INFO: Research package has clean data/systems separation
**ID:** ADR-FND-012
**Location:** `game/research/data/`, `game/research/systems/`
**Issue:** The `game/research/data/` (tech_node.py, tech_tree.py, research_tracker.py) and `game/research/systems/` (research_service.py) sub-packages are cleanly architected with no pygame or cross-layer dependencies. They depend only on `game.core` as intended. This is a positive observation -- only the `game/research/ui/` sub-package has layer violations.
**Impact:** None (positive finding). The data and systems code can be extracted to a standalone package with zero changes.
**Recommendation:** No action needed for data/systems. The UI sub-package relocation (ADR-FND-006) would complete the cleanup.
**Effort:** N/A

## Top 5 Priority Issues

1. **ADR-FND-001 (CRITICAL): Pygame in core/input_mapper.py** -- Move `InputMapper` to `game/ui/input/`. The core layer must remain framework-agnostic. This is the most impactful violation because `InputMapper` is used throughout the game loop and its presence in core normalizes pygame imports in the foundation layer.

2. **ADR-FND-002 (CRITICAL): Pygame in core/screenshot_manager.py** -- Move `ScreenshotManager` to `game/ui/`. This class is entirely a pygame UI service masquerading as a core utility. It also has inappropriate intimacy with `StrategyScreen` internals (ADR-FND-009).

3. **ADR-FND-003 + ADR-FND-006 (CRITICAL/MAJOR): Research UI layer violations** -- Move `game/research/ui/` to `game/ui/research/`. Three files with full pygame dependencies are incorrectly placed in the research package. The concrete `Camera` import from `game.ui` in research_scene.py makes this a bidirectional dependency concern.

4. **ADR-FND-008 (MINOR): UIConfig in core/config.py** -- Move `UIConfig` to the UI layer. This is low-risk but addresses the principle that core should not contain UI layout constants.

5. **ADR-FND-007 (MAJOR): Deep attribute chain in AIController** -- Refactor `own_ship.formation.master.formation.members.remove(own_ship)` to use a proper formation API method. This is a maintenance hazard during the ongoing god class decomposition work (PROJ-86/87).
