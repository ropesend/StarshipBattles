# Architecture Drift Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 24
- **Total Issues Found:** 8
- **Critical:** 0 | **Major:** 3 | **Minor:** 3 | **Info:** 2

## Findings

#### MAJOR: ShipFactory uses pygame.math.Vector2 in method signature
**ID:** ADR-UI2-001
**Location:** `game/ui/services/ship_factory.py:113-117`
**Issue:** The `configure_ship` method takes `pygame.math.Vector2` as a parameter type. While UI layer can use pygame, this creates tight coupling where any caller must pass a pygame type rather than a game-agnostic Vector2.
**Impact:** Reduces reusability - callers outside UI must construct pygame objects. Method signatures should use `game.core.math.Vector2` for better layer isolation.
**Recommendation:** Change parameter type to `game.core.math.Vector2` and convert internally if needed.
**Effort:** Simple

#### MAJOR: ShipIO module-level Tkinter initialization causes test isolation issues
**ID:** ADR-UI2-002
**Location:** `game/ui/services/ship_io.py:20-32`
**Issue:** Module-level code creates a tkinter.Tk() instance at import time. This is noted in `game/ui/__init__.py` as problematic for test isolation (lines 6-9). The module-level side effect violates the principle of lazy initialization.
**Impact:** Import-time side effects make testing difficult. Tests may fail or have flaky behavior due to Tkinter state bleeding across tests. Additionally, importing this module in a headless environment will fail.
**Recommendation:** Refactor to lazy initialization pattern - create Tk root only when first needed via a `_get_tk_root()` helper function.
**Effort:** Medium

#### MAJOR: Camera class uses pygame.math.Vector2 instead of game.core.math.Vector2
**ID:** ADR-UI2-003
**Location:** `game/ui/renderer/camera.py:14, 46, 60, 82, 95-96, 119-123, 128-132, 146`
**Issue:** The Camera class extensively uses `pygame.math.Vector2` directly rather than the game's platform-agnostic `game.core.math.Vector2`. While this is technically allowed in UI layer, it creates inconsistency with other UI code that uses the core Vector2.
**Impact:** Inconsistency between modules - some UI services use `game.core.math.Vector2` (e.g., `battle_ui_service.py`) while renderer uses pygame's. This makes refactoring harder and creates potential type mismatch issues.
**Recommendation:** Consider standardizing on `game.core.math.Vector2` in Camera class for consistency, or document the intentional divergence.
**Effort:** Medium

#### MINOR: TYPE_CHECKING import of GameRegistries from core.registry
**ID:** ADR-UI2-004
**Location:** `game/ui/services/ship_factory.py:23`
**Issue:** `GameRegistries` is imported under TYPE_CHECKING from `game.core.registry`. This is acceptable but worth noting - the UI layer depends on core layer types for DI patterns.
**Impact:** No operational impact - this is proper layer direction (UI depends on Core). Noted for completeness.
**Recommendation:** No action needed - this is correct architecture.
**Effort:** N/A

#### MINOR: BattleOrchestrator imports from engine layer
**ID:** ADR-UI2-005
**Location:** `game/ui/orchestration/battle_orchestrator.py:27`
**Issue:** Imports `SpatialGrid` from `game.engine.spatial`. The engine layer's position in the architecture hierarchy is unclear from the documented rules.
**Impact:** If engine is meant to be at the same level as simulation, this could be a minor violation. The code documents this as intentional boundary-crossing for orchestration purposes.
**Recommendation:** Clarify engine layer's position in architecture documentation. Current usage appears intentional per code comments.
**Effort:** Simple (documentation)

#### MINOR: Inconsistent use of Any type hints masking actual types
**ID:** ADR-UI2-006
**Location:** `game/ui/services/validation_service.py:48`, `game/ui/services/component_service.py:52`, `game/ui/services/design_loader_adapter.py:51`
**Issue:** Several service methods use `Any` as return type or parameter type where more specific types (like `Ship`, `Component`, `ValidationResult`) would be appropriate. This was done to avoid importing simulation types, but excessive `Any` usage reduces type safety.
**Impact:** IDE tooling and type checkers cannot verify correct usage. Bugs may slip through that would be caught with proper typing. The docstrings describe expected types, but code doesn't enforce them.
**Recommendation:** Use TYPE_CHECKING imports to provide proper type hints while avoiding runtime imports, or define UI-layer protocols that the simulation types implement.
**Effort:** Medium

#### INFO: DesignLoaderAdapter directly imports SimulationDesignLoader
**ID:** ADR-UI2-007
**Location:** `game/ui/services/design_loader_adapter.py:14`
**Issue:** The adapter imports `SimulationDesignLoader` from `game.simulation.services.design_loader` at runtime. This is valid (UI can depend on simulation) but defeats the stated purpose of the adapter pattern, which is to decouple UI from simulation internals.
**Impact:** The adapter provides value by allowing dependency injection for testing, but the tight coupling to simulation internals remains. The "adapter" is more of a thin wrapper than a true abstraction.
**Recommendation:** Consider whether the adapter provides sufficient value or if direct usage would be cleaner. Alternatively, define an interface/protocol that SimulationDesignLoader implements.
**Effort:** Medium

#### INFO: Screenshot manager uses hardcoded strategy layer attributes
**ID:** ADR-UI2-008
**Location:** `game/ui/services/screenshot_manager.py:119-180`
**Issue:** The `capture_strategy_layer` method directly accesses strategy layer scene attributes like `_renderer`, `ui`, `build_queue_screen`, `SIDEBAR_WIDTH`, `TOP_BAR_HEIGHT`. This creates tight coupling between screenshot functionality and specific screen implementation details.
**Impact:** If strategy screen implementation changes, this method will break. The screenshot manager "knows too much" about strategy layer internals.
**Recommendation:** Define a protocol/interface for screenshot-capable screens that provides the necessary surfaces, rather than reaching into private attributes.
**Effort:** Complex

## Top 5 Priority Issues

1. **ADR-UI2-002 (MAJOR):** ShipIO module-level Tkinter initialization - causes test isolation problems and headless environment failures. Should be refactored to lazy initialization.

2. **ADR-UI2-001 (MAJOR):** ShipFactory pygame.Vector2 in signatures - forces callers to use pygame types, reducing reusability. Easy fix with good impact.

3. **ADR-UI2-003 (MAJOR):** Camera inconsistent Vector2 usage - creates type inconsistency across UI layer. Medium effort to standardize.

4. **ADR-UI2-006 (MINOR):** Excessive Any type hints - reduces type safety across service layer. Should add TYPE_CHECKING imports for proper hints.

5. **ADR-UI2-008 (INFO):** Screenshot manager inappropriate intimacy - knows too much about strategy layer internals. Consider defining screenshot protocol interface.

## Architecture Compliance Notes

The UI-Framework layer is generally well-architected:

- **Correct layer dependencies:** UI services properly depend on simulation and AI layers (allowed direction)
- **DTO pattern:** BattleUIService correctly converts simulation objects to immutable DTOs for safe UI consumption
- **Service facades:** Services like ValidationService, ComponentService provide clean interfaces that hide simulation internals
- **Orchestration:** BattleOrchestrator correctly documents and justifies its cross-layer coordination role
- **No pygame in simulation:** All pygame usage is correctly confined to the UI layer

The issues found are primarily about internal consistency and code quality rather than critical layer violations.
