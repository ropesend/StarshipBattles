# Consistency Violations Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 24
- **Total Issues Found:** 14
- **Critical:** 0 | **Major:** 5 | **Minor:** 7 | **Info:** 2

## Findings

#### MAJOR: Inconsistent DI Pattern Between Services
**ID:** CON-UI2-001
**Location:** `game/ui/services/` - multiple files
**Issue:** Services use three different dependency injection patterns:
1. **Strict required DI** (VehicleClassService:36-47): Raises ValueError if registry_provider is None
2. **Optional with lazy resolution** (ComponentService:31-50): Optional with fallback to get_default_registry_provider()
3. **Optional with instance+method override** (ShipFactory:40-56): Can be passed at both construction and method call time

The docstring in ComponentService:34-38 documents this inconsistency as intentional ("Services may choose strict required pattern...when PROJ-50 explicitly mandated it") but this creates cognitive overhead when deciding which pattern to use for new services.
**Impact:** Cognitive load when using services - developers must remember which pattern each service uses. Risk of runtime errors if using wrong pattern.
**Recommendation:** Standardize on one pattern. Recommended: strict required DI with factory function for convenience (mimics simulation layer's BattleService pattern).
**Effort:** Medium

#### MAJOR: Mixed Parameter Naming for Registry Injection
**ID:** CON-UI2-002
**Location:** `game/ui/services/` - multiple files
**Issue:** Services use inconsistent parameter names for the registry dependency:
- `registry_provider` (ValidationService:33, VehicleClassService:36, ComponentService:31)
- `registry_provider` (ShipFactory:40) - but docstring says "registries" for GameRegistries
- `registry_provider` (DesignLoaderAdapter:31) - accepts Any type

Additionally, type hints vary:
- `Optional[IRegistryProvider]` (ComponentService:31)
- `IRegistryProvider` (VehicleClassService:36) - required
- `Optional['GameRegistries']` (ShipFactory:40)
- `Optional[Any]` (DesignLoaderAdapter:31)
**Impact:** Confusion about what type to pass; inconsistent type narrowing in callers.
**Recommendation:** Standardize on `registry_provider: IRegistryProvider` for protocol-based injection or `registries: GameRegistries` for concrete type. Document when each is appropriate.
**Effort:** Simple

#### MAJOR: Singleton Classes Missing Type Hints on Methods
**ID:** CON-UI2-003
**Location:** `game/ui/renderer/sprites.py:26-112`, `game/ui/assets/ship_theme_manager.py:45-314`
**Issue:** Singleton classes (SpriteManager, ShipThemeManager) lack type hints on most methods, while the project convention (per CLAUDE.md) requires "type hints for function signatures". Compare to:
- Well-typed: ValidationService, ComponentService, BattleUIService (all methods have full type hints)
- Missing types: SpriteManager.load_sprites() has return None implicit, `_load_from_directory()` has no return type
- ShipThemeManager methods like `load_image`, `get_image_metrics`, `get_manual_scale` return implicitly typed values
**Impact:** Reduced IDE support, potential type errors not caught by type checkers, inconsistent API surface.
**Recommendation:** Add return type hints to all public methods. Example: `def load_image(self, theme_name: str, ship_class: str) -> Optional[pygame.Surface]:`
**Effort:** Simple

#### MAJOR: Inconsistent Docstring Presence and Format
**ID:** CON-UI2-004
**Location:** Multiple files in `game/ui/`
**Issue:** Docstring coverage varies significantly:
- **Complete Google-style**: utils.py (all functions), services/*.py (all methods), interfaces/battle_ui.py
- **Partial or missing**: camera.py (update has docstring, but world_to_screen/screen_to_world have one-liners), game_renderer.py (draw_ship has no docstring for parameters)
- **Colons in :param style** (screenshot_manager.py:40-46, 118-129) vs **Google Args: style** everywhere else

Example of mixed style in screenshot_manager.py:118-129:
```python
def capture_strategy_layer(self, scene, include_ui=True, ...):
    """
    :param scene: The StrategyScreen instance to capture.
    :param include_ui: Whether to include UI panels...
    """
```
vs standard in utils.py:
```python
def create_centered_rect(...):
    """
    Args:
        width: Width of the rectangle
    """
```
**Impact:** Inconsistent documentation style hinders readability and auto-documentation tools.
**Recommendation:** Standardize on Google-style docstrings (Args:, Returns:, Raises:) as used in core/protocols.py and most services.
**Effort:** Medium

#### MAJOR: Static Methods vs Instance Methods Inconsistency
**ID:** CON-UI2-005
**Location:** `game/ui/services/ship_io.py:41-126`
**Issue:** ShipIO uses @staticmethod for save_ship and load_ship, accessing class variables via `ShipIO.default_ships_folder`. This is unusual in the codebase:
- Most services use instance methods with dependency injection (ValidationService, ComponentService, BattleUIService)
- ShipIO uses static methods with class-level state (`default_ships_folder`)
- ShipIOAdapter wraps this by storing the class reference and calling static methods on it

This pattern breaks the DI pattern used elsewhere and makes testing harder (must patch class attribute rather than inject mock).
**Impact:** Testing difficulty; inconsistent with established service patterns.
**Recommendation:** Convert to instance methods with injected config, or use a dataclass/config object for the folder path.
**Effort:** Medium

#### MINOR: Boolean Parameter Naming Inconsistency
**ID:** CON-UI2-006
**Location:** `game/ui/services/battle_ui_service.py:101`, `game/ui/interfaces/battle_ui.py:222`
**Issue:** Method `is_battle_over()` follows correct is_ prefix convention. However, ComponentDTO uses `is_active` (correct) and `has_weapon` (correct). The DTOs are consistent.

In camera.py:58, there's an unnamed boolean check:
```python
if hasattr(self.target, 'is_alive') and not self.target.is_alive:
```
The property `is_alive` follows convention, but the check could use a named variable for clarity.
**Impact:** Low - the convention is mostly followed, just minor readability improvement possible.
**Recommendation:** No change required; convention is followed.
**Effort:** N/A

#### MINOR: Inconsistent Error Handling - Return vs Raise
**ID:** CON-UI2-007
**Location:** `game/ui/services/ship_io.py`, `game/ui/services/design_loader_adapter.py`
**Issue:** Error handling varies between services:
- ShipIO.save_ship/load_ship: Returns tuple (success/object, message) - never raises
- ValidationService.validate_addition: Returns ValidationResult object (never raises)
- DesignLoaderAdapter.load_ship_from_file: Returns tuple (Optional[Ship], message)
- ShipFactory.create_from_design: Can raise KeyError, ValueError (per docstring)

The return-tuple pattern is documented in ShipIOAdapter:29-36 but ShipFactory explicitly documents it raises.
**Impact:** Callers must know which pattern each service uses; potential for uncaught exceptions.
**Recommendation:** Document the convention clearly. For UI services that interact with user (file dialogs), return-tuple is appropriate. For internal services, consider consistent exception-raising.
**Effort:** Simple (documentation)

#### MINOR: Import Organization Inconsistency
**ID:** CON-UI2-008
**Location:** Various files in `game/ui/`
**Issue:** Import organization varies:
- **Grouped correctly**: services/__init__.py, interfaces/__init__.py
- **Mixed grouping**: ship_theme_manager.py (os, pygame, threading together before game imports - correct)
- **TYPE_CHECKING block placement**: Some files put TYPE_CHECKING at top after regular imports (ship_factory.py:17-23), others in middle of imports

Most files follow: stdlib -> third-party -> game imports, which is correct. Minor variations exist.
**Impact:** Low - mostly consistent, minor cognitive load.
**Recommendation:** Maintain current practice; enforce via linter.
**Effort:** Simple

#### MINOR: Magic Numbers in Rendering Code
**ID:** CON-UI2-009
**Location:** `game/ui/renderer/game_renderer.py:33-34, 91, 129, 135, 141`
**Issue:** Several magic numbers exist despite UIConfig being available:
- Line 33-34: `radius_screen = 50 * camera.zoom` - why 50?
- Line 91: `if camera.zoom > 0.3:` - threshold not named
- Line 129: `max(1, scale(3))` - component dot radius
- Line 135: `max(1, scale(2))` - direction indicator width
- Line 141: `max(2, scale(3))` - fallback dot size
- Line 149: width = max_x - min_x + 500 # Margin (camera.py) - margin value

UIConfig exists in game/ui/config.py but these rendering values aren't centralized there.
**Impact:** Difficult to tune visual parameters; unclear meaning of values.
**Recommendation:** Add rendering constants to UIConfig (e.g., COMPONENT_DOT_RADIUS, ZOOM_DETAIL_THRESHOLD, CULLING_MARGIN).
**Effort:** Simple

#### MINOR: Inconsistent Use of Optional Type Annotation
**ID:** CON-UI2-010
**Location:** Multiple service files
**Issue:** Some files use `Optional[X]` explicitly, others use `X | None` (Python 3.10+ syntax). The codebase appears to standardize on `Optional[X]`:
- battle_ui.py:11: `from typing import List, Optional, Tuple, Protocol`
- All services use `Optional`

However, sprites.py:101 uses the newer union syntax:
```python
def get_sprite(self, index: int) -> "pygame.Surface | None":
```
**Impact:** Minor inconsistency; could cause issues if targeting older Python versions.
**Recommendation:** Standardize on `Optional[X]` for consistency with rest of codebase.
**Effort:** Simple

#### MINOR: Inconsistent Private Method Naming
**ID:** CON-UI2-011
**Location:** Various service files
**Issue:** Private methods use single underscore consistently, which is correct. However, naming patterns vary:
- `_get_provider()` (ComponentService, VehicleClassService)
- `_get_registries()` (ShipFactory)
- `_get_validator()` (ValidationService)
- `_convert_ship()`, `_convert_component()` (BattleUIService)

The verb patterns are consistent (get_, convert_), but the noun varies (provider vs registries vs validator). This is acceptable given different return types.
**Impact:** Low - naming is reasonably consistent.
**Recommendation:** No change required.
**Effort:** N/A

#### MINOR: Module-Level Side Effects
**ID:** CON-UI2-012
**Location:** `game/ui/services/ship_io.py:20-32`
**Issue:** Module has side effects at import time (Tkinter initialization):
```python
try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
except tkinter.TclError as e:
    ...
```
This is documented and intentional (file dialogs need Tk), but differs from other modules which defer initialization. The __init__.py for the UI package (game/ui/__init__.py:6-9) explicitly documents avoiding eager imports with side effects.

ShipIO is imported via ShipIOAdapter, so the side effect occurs when the adapter is imported.
**Impact:** Potential test issues; noted in ui/__init__.py but ship_io isn't in the explicit exclusion list.
**Recommendation:** Consider lazy initialization pattern (init on first save/load call) to match the workshop_screen exclusion pattern.
**Effort:** Medium

#### INFO: Color Constants Location
**ID:** CON-UI2-013
**Location:** `game/ui/colors.py`, `game/ui/renderer/game_renderer.py:14-19`, `game/ui/services/battle_ui_service.py:31-36`
**Issue:** Color constants are defined in multiple places:
- `colors.py`: COLORS dict with semantic names (bg_deep, text_normal, etc.)
- `game_renderer.py`: LAYER_COLORS dict
- `battle_ui_service.py`: PROJECTILE_COLORS dict

This is intentional separation (different concerns: UI style vs game visualization), but could be centralized for discoverability.
**Impact:** Developers may not know where to look for color constants.
**Recommendation:** Document in colors.py that layer-specific colors are in their respective modules, or consider a colors/ package.
**Effort:** Simple (documentation)

#### INFO: Protocol Inheritance Pattern
**ID:** CON-UI2-014
**Location:** `game/ui/interfaces/battle_ui.py:175-244`
**Issue:** IBattleUI Protocol uses `@runtime_checkable` decorator, matching the pattern in core/protocols.py. BattleUIService doesn't explicitly inherit from IBattleUI but implements its methods (duck typing).

This is correct Protocol usage but differs from some services that explicitly document implementing an interface.
**Impact:** None - this is correct Python Protocol usage.
**Recommendation:** No change required; consider adding explicit `# Implements IBattleUI` comment for documentation.
**Effort:** N/A

## Top 5 Priority Issues

1. **CON-UI2-001 (MAJOR): Inconsistent DI Pattern Between Services** - Creates confusion about which pattern to use for new services and increases cognitive load when using existing services. Standardizing would improve maintainability.

2. **CON-UI2-002 (MAJOR): Mixed Parameter Naming for Registry Injection** - The inconsistent naming and typing for registry parameters creates type confusion. Should standardize naming convention.

3. **CON-UI2-003 (MAJOR): Singleton Classes Missing Type Hints** - SpriteManager and ShipThemeManager lack type hints despite project conventions requiring them. This reduces IDE support and type safety.

4. **CON-UI2-004 (MAJOR): Inconsistent Docstring Format** - Mixed :param style and Google Args: style reduces documentation consistency. Should standardize on Google style.

5. **CON-UI2-005 (MAJOR): Static Methods in ShipIO** - The static method pattern with class-level state breaks the DI pattern used elsewhere and makes testing harder.
