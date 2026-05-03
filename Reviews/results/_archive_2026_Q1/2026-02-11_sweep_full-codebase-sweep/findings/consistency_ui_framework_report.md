# Consistency Violations Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 20
- **Total Issues Found:** 16
- **Critical:** 1 | **Major:** 5 | **Minor:** 7 | **Info:** 3

## Findings

#### CRITICAL: Inconsistent DI Pattern Across Services - Mixed Required vs Optional vs No-DI
**ID:** CON-UI2-001
**Location:** `game/ui/services/vehicle_class_service.py:36`, `game/ui/services/component_service.py:31`, `game/ui/services/ship_factory.py:40`, `game/ui/services/validation_service.py:33`, `game/ui/services/ship_io_adapter.py:42`, `game/ui/services/design_loader_adapter.py:31`, `game/ui/services/battle_ui_service.py:42`
**Issue:** The seven services in `game/ui/services/` use five different dependency injection patterns for their constructors:
1. **VehicleClassService** - `registry_provider: IRegistryProvider` (required, raises ValueError if None) -- strict DI
2. **ComponentService** - `registry_provider: Optional[IRegistryProvider] = None` (optional, lazy resolution via `get_default_registry_provider()`)
3. **ShipFactory** - `*, registry_provider: Optional['GameRegistries'] = None` (keyword-only optional, lazy resolution via `get_default_registries()`)
4. **ValidationService** - `validator: Optional[Any] = None` (optional, lazy resolution) -- named `validator` not `registry_provider`
5. **ShipIOAdapter** - `ship_io_class: Optional[Any] = None` (optional, wraps class not instance) -- named `ship_io_class`
6. **DesignLoaderAdapter** - `design_loader: Optional[Any] = None, *, registry_provider: Optional[Any] = None` (mixed positional+keyword, two injection points)
7. **BattleUIService** - `battle_service: 'BattleService'` (required, no default)

Additionally, the `registry_provider` parameter receives different types across services: `IRegistryProvider` (VehicleClassService, ComponentService), `GameRegistries` (ShipFactory), and `Any` (DesignLoaderAdapter). The internal storage naming also varies: `_provider`, `_registry_provider`, `_validator`, `_ship_io`, `_loader`, `_battle_service`.
**Impact:** Developers cannot predict how to instantiate a service without reading each constructor. The lack of a single DI convention makes it easy to pass the wrong type or forget required parameters. This is the single most impactful consistency violation in the shard.
**Recommendation:** Establish a single DI pattern for all services. The dominant pattern is "optional with lazy resolution" (used by 4 of 7 services). Standardize on: `registry_provider: Optional[IRegistryProvider] = None` with lazy resolution, naming the stored field `_provider`. Services needing other dependencies (validator, battle_service) should still follow the same optional-with-lazy pattern where possible.
**Effort:** Medium

#### MAJOR: Complete Absence of Type Hints in renderer/ and assets/ Modules
**ID:** CON-UI2-002
**Location:** `game/ui/renderer/camera.py:all`, `game/ui/renderer/game_renderer.py:all`, `game/ui/renderer/sprites.py:all`, `game/ui/assets/ship_theme_manager.py:all`
**Issue:** The `services/` package uses comprehensive type hints on every method (parameter types and return types). In contrast, the `renderer/` and `assets/` modules have zero type annotations on any method signature. For example:
- `Camera.__init__(self, width, height, offset_x=0, offset_y=0)` -- no types
- `Camera.world_to_screen(self, world_pos)` -- no parameter or return type
- `SpriteManager.get_sprite(self, index)` -- no types
- `ShipThemeManager.load_image(self, theme_name, ship_class)` -- no types
- `draw_ship(surface, ship, camera)` -- no types
- `draw_bar(surface, x, y, w, h, pct, color)` -- no types

Meanwhile `game/ui/utils.py` has full type hints on every function, and all 7 service classes have full type hints. The project convention (CLAUDE.md) requires: "Use type hints for function signatures."
**Impact:** High cognitive overhead reading renderer/assets code. IDE auto-complete and static analysis tools cannot help. Violates explicit project convention.
**Recommendation:** Add type hints to all public methods in `camera.py`, `game_renderer.py`, `sprites.py`, and `ship_theme_manager.py` to match the `services/` and `utils.py` standard.
**Effort:** Medium

#### MAJOR: Complete Absence of Type Hints in widgets.py (Legacy Module)
**ID:** CON-UI2-003
**Location:** `game/ui/widgets.py:1-102`
**Issue:** The `widgets.py` module contains three classes (`Button`, `Label`, `Slider`) with zero type annotations on any method. Every `__init__`, `handle_event`, `draw`, `update_text`, `update_val`, and `get_handle_rect` method lacks parameter and return type hints. This module is explicitly labeled `# --- Legacy UI Widgets ---` but is still actively importable and part of the codebase.
**Impact:** Inconsistent with the fully-typed `utils.py` in the same directory. Makes it unclear whether the module is deprecated or actively maintained.
**Recommendation:** Either add type hints to bring it into compliance with project conventions, or if truly legacy, mark it with a deprecation notice and document the replacement.
**Effort:** Simple

#### MAJOR: Singleton Pattern Used in renderer/ and assets/ Despite Project Preference for DI
**ID:** CON-UI2-004
**Location:** `game/ui/renderer/sprites.py:7` (`SpriteManager(metaclass=SingletonMeta)`), `game/ui/assets/ship_theme_manager.py:11` (`ShipThemeManager(metaclass=SingletonMeta)`)
**Issue:** The project convention (CLAUDE.md) states: "Dependency Injection: Preferred over singletons for testability." The `services/` package consistently uses DI (constructor injection). However, `SpriteManager` and `ShipThemeManager` both use `SingletonMeta` and are accessed via `ShipThemeManager.instance()` / `SpriteManager.instance()`. Furthermore, `game_renderer.py:47` accesses the singleton directly inside a function: `theme_mgr = ShipThemeManager.instance()` -- a hidden dependency that cannot be injected for testing.
**Impact:** These singletons create hidden coupling, make unit testing difficult (requires `reset()` calls), and contradict the DI pattern established by the services layer. The inline `ShipThemeManager.instance()` call in `draw_ship()` means the renderer cannot be tested without the real theme manager.
**Recommendation:** Refactor to inject `ShipThemeManager` and `SpriteManager` as constructor or function parameters. The `draw_ship()` function could accept a `theme_manager` parameter. This aligns with the services layer pattern and project conventions.
**Effort:** Complex

#### MAJOR: Missing Docstrings on Public Methods in renderer/ and assets/
**ID:** CON-UI2-005
**Location:** `game/ui/renderer/sprites.py:27,45,97,116,129`, `game/ui/assets/ship_theme_manager.py:45,56,79,117,136,167,197,206,215,293`
**Issue:** The `services/` package has Google-style docstrings on 100% of public and private methods. In contrast:
- `SpriteManager` has a class docstring but `load_sprites()` has only an inline comment-style docstring. `_load_from_directory()`, `_load_atlas_file()`, `_slice_sprites()`, and `get_sprite()` have no docstrings.
- `ShipThemeManager` has a class docstring and brief one-line docstrings on some methods (`load_image`, `get_image_metrics`, `get_manual_scale`), but many methods have no Args/Returns documentation. `clear()`, `initialize()`, `_discover_theme()`, `_create_fallback_image()`, `get_available_themes()` lack formal docstrings or have minimal ones.
- `Camera` has docstrings on `update()` and `update_input()` (good, detailed) but none on `__init__`, `world_to_screen`, `screen_to_world`, `fit_objects`.

The `services/` standard is: every method has a docstring with Args/Returns sections.
**Impact:** Inconsistent documentation quality between modules increases onboarding time and maintenance burden.
**Recommendation:** Add Google-style docstrings (with Args/Returns) to all public methods in renderer/ and assets/ modules.
**Effort:** Medium

#### MAJOR: Inconsistent Error Handling - traceback Import Inside Except Block
**ID:** CON-UI2-006
**Location:** `game/ui/renderer/sprites.py:113-114`
**Issue:** In `SpriteManager._load_atlas_file()`, the `traceback` module is imported inside an except block:
```python
except (FileNotFoundError, OSError, pygame.error) as e:
    import traceback
    log_error(f"Exception loading atlas: {e}\n{traceback.format_exc()}")
```
No other file in the entire `game/ui/` shard uses `import traceback` inside an except block. The standard pattern elsewhere (e.g., `ShipThemeManager._load_single_image`, `ShipThemeManager._load_portrait_image`, `SpriteManager._load_from_directory`) is simply: `log_error(f"message: {e}")` without traceback formatting. The `game.core.logger` module should handle any necessary traceback capture.
**Impact:** Inconsistent error output format. Most errors log just the message; this one logs the full stack trace. Additionally, deferred imports in except blocks are a code smell.
**Recommendation:** Remove the inline `import traceback` and use the standard `log_error(f"...: {e}")` pattern used everywhere else. If full tracebacks are needed, configure the logger to capture them.
**Effort:** Simple

#### MINOR: Hardcoded Magic Colors in renderer/game_renderer.py, widgets.py, and assets/ship_theme_manager.py
**ID:** CON-UI2-007
**Location:** `game/ui/renderer/game_renderer.py:148-150,155-157,160-161,180-187`, `game/ui/widgets.py:6,30-31`, `game/ui/assets/ship_theme_manager.py:209-212`
**Issue:** `game/ui/colors.py` defines a `COLORS` dictionary with named color constants used by the builder screens. However, the renderer, widgets, and assets modules all use inline magic color tuples:
- `game_renderer.py`: `(50, 50, 50)`, `(200, 200, 200)`, `(100, 255, 100)`, `(255, 50, 50)`, `(255, 165, 0)`, `(200, 200, 255)`, etc.
- `widgets.py`: `(100, 100, 100)`, `(150, 150, 150)`, `(255, 255, 255)`, `(200, 200, 200)`
- `ship_theme_manager.py`: `(100, 100, 100)` in fallback image

None of these modules import from `game.ui.colors`. The COLORS dictionary already has semantic names like `bg_base`, `text_normal`, `border_subtle` that could replace many of these magic tuples.
**Impact:** Color changes require finding and updating magic tuples scattered across files instead of updating the central `COLORS` dictionary.
**Recommendation:** Import and use `COLORS` from `game.ui.colors` in renderer and widget modules for all UI-related colors.
**Effort:** Medium

#### MINOR: Hardcoded Font Creation in game_renderer.py and widgets.py
**ID:** CON-UI2-008
**Location:** `game/ui/renderer/game_renderer.py:155-157`, `game/ui/widgets.py:13,40`
**Issue:** Font objects are created with `pygame.font.SysFont("Arial", N)` at multiple locations:
- `draw_hud()` creates three font objects (`SysFont("Arial", 16)`, `SysFont("Arial", 14)`, `SysFont("Arial", 12)`) every time it is called -- inside the function body, not cached.
- `Button.__init__` and `Label.__init__` each create their own `SysFont("Arial", 20)`.

There is no centralized font management. Font sizes (12, 14, 16, 20) are magic numbers. Font family ("Arial") is hardcoded as a string.
**Impact:** Performance: `draw_hud()` creates 3 font objects per frame per ship. Maintainability: changing the font family requires finding every `SysFont("Arial", ...)` call.
**Recommendation:** Create a centralized font provider (e.g., in `utils.py` or a `fonts.py` module) with cached font instances and named size constants.
**Effort:** Medium

#### MINOR: game/ui/__init__.py Imports Screens but Not Services, Interfaces, or Orchestration
**ID:** CON-UI2-009
**Location:** `game/ui/__init__.py:14-16`
**Issue:** The top-level `__init__.py` imports from `renderer`, `screens`, and `panels` subpackages but does not import from `services`, `interfaces`, `orchestration`, or `assets`. The docstring explains this is for "pytest-xdist race conditions," but the selective inclusion means:
- `services/__init__.py` defines `__all__` with 7 exports
- `interfaces/__init__.py` defines `__all__` with 6 exports
- `orchestration/__init__.py` defines `__all__` with 1 export
- `assets/__init__.py` defines `__all__` with 1 export

None of these are included in the parent package's namespace.
**Impact:** Low impact since direct imports work, but creates asymmetry in how subpackages are treated. If the xdist rationale applies to some subpackages, it likely applies to all.
**Recommendation:** Either add the missing subpackages to `__init__.py` for consistency, or document why they are excluded.
**Effort:** Simple

#### MINOR: Mixed Naming for Internal Provider Accessor Methods
**ID:** CON-UI2-010
**Location:** `game/ui/services/component_service.py:46` (`_get_provider`), `game/ui/services/vehicle_class_service.py:50` (`_get_provider`), `game/ui/services/ship_factory.py:49` (`_get_registries`), `game/ui/services/validation_service.py:42` (`_get_validator`)
**Issue:** Services use different names for their internal dependency accessor method:
- `ComponentService._get_provider()` -> returns `IRegistryProvider`
- `VehicleClassService._get_provider()` -> returns `IRegistryProvider`
- `ShipFactory._get_registries()` -> returns `GameRegistries`
- `ValidationService._get_validator()` -> returns validator

While the different names somewhat reflect the different return types, the pattern is inconsistent. Two services call it `_get_provider`, one calls it `_get_registries`, one calls it `_get_validator`.
**Impact:** Minor cognitive overhead when reading service implementations.
**Recommendation:** Standardize on `_get_provider()` for all services that wrap a registry-like dependency. For services wrapping other kinds of dependencies (validator, battle_service), `_get_delegate()` or keeping the specific name is acceptable.
**Effort:** Simple

#### MINOR: Inconsistent Return Patterns for load_ship Operations
**ID:** CON-UI2-011
**Location:** `game/ui/services/ship_io_adapter.py:70,86`, `game/ui/services/design_loader_adapter.py:46,71`
**Issue:** Ship loading operations have inconsistent return types:
- `ShipIOAdapter.save_ship()` -> `Tuple[bool, Optional[str]]` (success flag + message)
- `ShipIOAdapter.load_ship()` -> `Tuple[Optional[Any], Optional[str]]` (object + message)
- `DesignLoaderAdapter.load_ship_from_design_data()` -> `Optional[Any]` (just the object, no message)
- `DesignLoaderAdapter.load_ship_from_file()` -> `Tuple[Optional[Any], str]` (object + message, message always present)

Note: `ShipIOAdapter.load_ship` returns `Optional[str]` for the message (None on cancel), while `DesignLoaderAdapter.load_ship_from_file` returns bare `str` (never None). The `ShipIOAdapter` docstring documents this difference explicitly, so it is somewhat intentional, but the inconsistency between the two adapter classes remains.
**Impact:** Callers must check the return convention for each specific method. Not a high-risk bug source since both adapters are well-documented, but increases cognitive load.
**Recommendation:** Consider standardizing on a `Result` or `LoadResult` dataclass across all load operations for consistent return types.
**Effort:** Medium

#### MINOR: Camera.fit_objects Sets zoom Directly, Bypassing target_zoom Animation
**ID:** CON-UI2-012
**Location:** `game/ui/renderer/camera.py:153`
**Issue:** `Camera.fit_objects()` sets `self.zoom = min(zoom_x, zoom_y)` directly, bypassing the `target_zoom` + smooth interpolation pattern used by `update_input()` (line 109: `self.target_zoom *= 1.15`). The `update()` method animates from `self.zoom` to `self.target_zoom`, but `fit_objects()` snaps `self.zoom` immediately without updating `self.target_zoom`. This means after `fit_objects()`, the next `update()` call could animate zoom back to the old `target_zoom` value.
**Impact:** Potential visual glitch: calling `fit_objects()` then immediately receiving a mouse wheel event could cause unexpected zoom behavior because `target_zoom` is stale.
**Recommendation:** `fit_objects()` should set both `self.zoom` and `self.target_zoom` to the calculated value to maintain consistency.
**Effort:** Simple

#### MINOR: draw_ship Contains Inline Import of ShipThemeManager
**ID:** CON-UI2-013
**Location:** `game/ui/renderer/game_renderer.py:46-47`
**Issue:** `draw_ship()` contains a deferred import inside the function body:
```python
from game.ui.assets import ShipThemeManager
theme_mgr = ShipThemeManager.instance()
```
This is the only deferred import in the renderer module. All other imports in `game_renderer.py` are at module level (lines 7-10). Deferred imports inside frequently-called rendering functions add per-call overhead (even though Python caches the module, the import statement still runs).
**Impact:** Minor performance cost per frame. The real issue is readability: the hidden dependency makes the function's actual requirements unclear from its signature.
**Recommendation:** Move the import to module level and pass the theme manager as a parameter (aligns with the DI pattern recommendation in CON-UI2-004).
**Effort:** Simple

#### INFO: Service Class Naming Convention - "Service" vs "Adapter" vs "Factory"
**ID:** CON-UI2-014
**Location:** `game/ui/services/` directory
**Issue:** The services directory contains three different suffix conventions:
- **Service**: `ValidationService`, `VehicleClassService`, `ComponentService`, `BattleUIService`
- **Adapter**: `ShipIOAdapter`, `DesignLoaderAdapter`
- **Factory**: `ShipFactory`

The "Service" suffix dominates (4 of 7), while "Adapter" and "Factory" each appear once or twice. The different suffixes do communicate intent: Adapters wrap a single simulation class, Factories create objects, Services provide broader functionality. This appears to be deliberate naming based on the Gang of Four pattern each class follows.
**Impact:** Low -- the naming actually carries semantic meaning and is arguably correct.
**Recommendation:** No change needed. The naming communicates the design pattern intent. Document the naming convention in the package docstring for clarity.
**Effort:** N/A

#### INFO: colors.py Has No Module Docstring and No Type Annotations
**ID:** CON-UI2-015
**Location:** `game/ui/colors.py:1-35`
**Issue:** `colors.py` has only a comment (`# StarshipBattles UI Style Guide Colors`) instead of a proper module docstring. The `COLORS` dictionary is typed as a plain dict literal without a type annotation. Compare to `utils.py` which has a proper module docstring with description and rationale. The `COLORS` dict values are all `Tuple[int, int, int]` but this is not documented.
**Impact:** Minimal -- the file is small and self-explanatory.
**Recommendation:** Add a module docstring and optionally type the dict: `COLORS: Dict[str, Tuple[int, int, int]] = {...}`.
**Effort:** Simple

#### INFO: Inconsistent Docstring Style Between renderer/ Methods
**ID:** CON-UI2-016
**Location:** `game/ui/renderer/camera.py:24-53` vs `game/ui/renderer/camera.py:115-131`, `game/ui/renderer/game_renderer.py:22-23`
**Issue:** Within `camera.py`, `update()` and `update_input()` have detailed multi-section docstrings with `Args:` sections and descriptions of subsystem behavior. But `world_to_screen()`, `screen_to_world()`, and `fit_objects()` have only single-line docstrings. In `game_renderer.py`, `draw_ship()` and `draw_bar()` have single-line docstrings while `draw_hud()` has one too. This is internally inconsistent -- some methods in the same file get detailed docs, others get minimal ones.
**Impact:** Low -- the simpler methods may not need long docstrings, but the inconsistency within a single file is notable.
**Recommendation:** At minimum, add `Args:` and `Returns:` sections to `world_to_screen`, `screen_to_world`, `fit_objects`, and the renderer drawing functions.
**Effort:** Simple

## Top 5 Priority Issues

1. **CON-UI2-001 (CRITICAL): Inconsistent DI Pattern Across Services** -- Five different constructor injection patterns across seven services creates confusion and makes the service layer unpredictable. This is the highest priority because it affects API design at the architectural level.

2. **CON-UI2-002 (MAJOR): Complete Absence of Type Hints in renderer/ and assets/** -- The `services/` package is fully typed, `utils.py` is fully typed, but the entire `renderer/` and `assets/` packages have zero type annotations. This directly violates the project convention "Use type hints for function signatures."

3. **CON-UI2-004 (MAJOR): Singleton Pattern vs Project DI Preference** -- `SpriteManager` and `ShipThemeManager` use SingletonMeta despite the project preferring DI. The inline `ShipThemeManager.instance()` call in `draw_ship()` creates an untestable hidden dependency.

4. **CON-UI2-005 (MAJOR): Missing Docstrings on Public Methods** -- The services layer has 100% docstring coverage with Args/Returns sections. The renderer and assets layers have patchy, inconsistent docstrings. This violates the "Docstrings on public APIs" convention.

5. **CON-UI2-006 (MAJOR): Inconsistent Error Handling with Inline traceback Import** -- One error handler in `sprites.py` imports `traceback` inline and logs full stack traces, while every other error handler in the shard uses simple `log_error(f"...: {e}")`. This should be standardized.
