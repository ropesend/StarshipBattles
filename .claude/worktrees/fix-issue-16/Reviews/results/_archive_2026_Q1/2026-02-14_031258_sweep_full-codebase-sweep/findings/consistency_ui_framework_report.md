# Consistency Violations Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 22
- **Total Issues Found:** 14
- **Critical:** 0 | **Major:** 5 | **Minor:** 7 | **Info:** 2

## Files Analyzed
- `game/ui/__init__.py`
- `game/ui/utils.py`
- `game/ui/config.py`
- `game/ui/colors.py`
- `game/ui/services/__init__.py`
- `game/ui/services/vehicle_class_service.py`
- `game/ui/services/component_service.py`
- `game/ui/services/design_loader_adapter.py`
- `game/ui/services/ship_io_adapter.py`
- `game/ui/services/input_mapper.py`
- `game/ui/services/tkinter_utils.py`
- `game/ui/services/battle_factories.py`
- `game/ui/services/battle_ui_service.py`
- `game/ui/services/ship_io.py`
- `game/ui/services/screenshot_manager.py`
- `game/ui/services/ship_factory.py`
- `game/ui/services/validation_service.py`
- `game/ui/renderer/__init__.py`
- `game/ui/renderer/camera.py`
- `game/ui/renderer/sprites.py`
- `game/ui/renderer/game_renderer.py`
- `game/ui/interfaces/__init__.py`
- `game/ui/interfaces/battle_ui.py`
- `game/ui/orchestration/__init__.py`
- `game/ui/orchestration/battle_orchestrator.py`
- `game/ui/assets/__init__.py`
- `game/ui/assets/ship_theme_manager.py`

## Findings

#### MAJOR: Inconsistent Dependency Injection Patterns Across Services
**ID:** CON-UI2-001
**Location:** `game/ui/services/` (multiple files)
**Issue:** Services use three different DI patterns:
1. **Strict required** (ValueError if None): `VehicleClassService` - registry_provider required
2. **Optional with lazy resolution**: `ComponentService`, `ValidationService` - optional with lazy fallback
3. **Positional + keyword parameters**: `DesignLoaderAdapter` - design_loader positional, registry_provider keyword-only

Additionally, parameter naming varies:
- `registry_provider` (most services)
- `registries` (ShipFactory internally)
- `registry_provider` keyword in DesignLoaderAdapter but `registries=` passed to SimulationDesignLoader

**Impact:** Cognitive overhead when using services; unclear which pattern to follow for new services; potential bugs from incorrect assumptions about required vs optional parameters.
**Recommendation:** Standardize on one pattern. Recommended: Optional with lazy resolution (`registry_provider: Optional[IRegistryProvider] = None`), using `_get_provider()` helper method. Document pattern in CLAUDE.md.
**Effort:** Medium

#### MAJOR: Mixed Return Type Conventions for IO Operations
**ID:** CON-UI2-002
**Location:** `game/ui/services/ship_io_adapter.py:72-103`, `game/ui/services/ship_io.py:35-135`
**Issue:** Save and load operations use different return tuple structures:
- Save: `Tuple[bool, Optional[str]]` - (success_flag, message)
- Load: `Tuple[Optional[Ship], Optional[str]]` - (object_or_none, message)

While documented in ShipIOAdapter docstring, this asymmetry can cause confusion. The same `None` message means "cancelled" for both, but success is indicated differently (bool vs presence of object).
**Impact:** Cognitive overhead; potential for incorrect result handling.
**Recommendation:** Consider unified Result pattern: `@dataclass class IOResult: success: bool; value: Optional[T]; message: Optional[str]` or use Python 3.11+ `Result` type pattern.
**Effort:** Medium

#### MAJOR: Inconsistent Type Hint Completeness
**ID:** CON-UI2-003
**Location:** Multiple files in `game/ui/renderer/` and `game/ui/assets/`
**Issue:** Type hints are incomplete or missing in several locations:
1. `camera.py:20` - `target = None` lacks type annotation
2. `sprites.py:27-113` - `load_sprites`, `_load_from_directory`, `get_sprite` methods lack return type annotations except `get_sprite`
3. `game_renderer.py:44` - `draw_ship(surface, ship, camera)` has no type hints at all
4. `ship_theme_manager.py` - Many methods lack type hints (load_image, get_image_metrics, etc.)

Contrast with services/ which have comprehensive type hints.
**Impact:** Reduced IDE support; harder to understand API contracts; inconsistent with project convention requiring type hints on all function signatures.
**Recommendation:** Add type hints to all public methods following the pattern in `services/`.
**Effort:** Simple

#### MAJOR: Inconsistent Method Naming for Registry/Provider Access
**ID:** CON-UI2-004
**Location:** `game/ui/services/` (multiple files)
**Issue:** Internal helper methods for registry access use different naming:
- `_get_provider()` - ComponentService, VehicleClassService
- `_get_registries()` - ShipFactory
- `_get_validator()` - ValidationService
- Direct access via `self._loader` - DesignLoaderAdapter

**Impact:** Cognitive overhead; inconsistent internal API patterns.
**Recommendation:** Standardize on `_get_provider()` pattern across all services. For ShipFactory, rename `_get_registries()` to `_get_provider()` and internally store as `_provider`.
**Effort:** Simple

#### MAJOR: Two Singleton Patterns in Use
**ID:** CON-UI2-005
**Location:** `game/ui/renderer/sprites.py`, `game/ui/services/screenshot_manager.py`, `game/ui/assets/ship_theme_manager.py`
**Issue:** All three singletons use `SingletonMeta` metaclass but have inconsistent initialization and access patterns:
1. `SpriteManager` - No `instance()` method documented in usage comment
2. `ScreenshotManager` - Has `instance()` method, `reset()` method
3. `ShipThemeManager` - Has `instance()` method, `clear()` method for test isolation

The method for test isolation differs: `reset()` vs `clear()` with different semantics.
**Impact:** Inconsistent API for singletons; test isolation approaches vary.
**Recommendation:** Standardize singleton pattern: all should expose `.instance()`, `.reset()` for complete destruction, and optionally `.clear()` for cache reset while preserving instance.
**Effort:** Simple

#### MINOR: Inconsistent Docstring Styles
**ID:** CON-UI2-006
**Location:** Various files
**Issue:** Docstring formatting varies:
1. **Google style** (most services): Args/Returns sections with descriptions
2. **Abbreviated** (camera.py, sprites.py): Single-line descriptions without full Args/Returns
3. **Mixed within file** (ship_theme_manager.py): Some methods have full docstrings, others have minimal

Examples:
- `camera.py:134 fit_objects()` - minimal docstring
- `component_service.py:82 is_modifier_allowed()` - full Google style

**Impact:** Inconsistent documentation quality; harder to navigate API.
**Recommendation:** Standardize on Google style docstrings for all public methods.
**Effort:** Simple

#### MINOR: Inconsistent Private Member Naming
**ID:** CON-UI2-007
**Location:** `game/ui/services/input_mapper.py`, `game/ui/assets/ship_theme_manager.py`
**Issue:** Module-level private variables use different conventions:
- `_MOD_MAP` - UPPER_SNAKE_CASE (input_mapper.py:34)
- `_CONTEXT_OVERLAP` - UPPER_SNAKE_CASE (input_mapper.py:43)
- `_tk_root` - lower_snake_case (tkinter_utils.py:25)
- `_initialized` - lower_snake_case (tkinter_utils.py:26)

The convention differs: constants vs state variables, but not consistently applied.
**Impact:** Minor cognitive overhead distinguishing constants from mutable state.
**Recommendation:** Use `_UPPER_SNAKE` for module constants, `_lower_snake` for mutable module state.
**Effort:** Simple

#### MINOR: Inconsistent Error Handling Patterns
**ID:** CON-UI2-008
**Location:** `game/ui/services/ship_io.py`, `game/ui/services/tkinter_utils.py`
**Issue:** Error handling varies between returning None/False and logging:
1. `ship_io.py` - Catches specific exceptions (PermissionError, OSError, etc.), logs with `log_error()`, returns tuple with error message
2. `tkinter_utils.py` - Uses `log_warning()` for all failures, returns None
3. `screenshot_manager.py` - Uses both `log_warning()` and `log_error()` for different cases

**Impact:** Inconsistent error severity classification; mixed patterns for communicating errors to callers.
**Recommendation:** Document error handling pattern: use `log_error()` for recoverable errors that affect operation, `log_warning()` for degraded functionality. Return error info to caller when they can act on it.
**Effort:** Simple

#### MINOR: Inconsistent Import Organization
**ID:** CON-UI2-009
**Location:** Multiple files
**Issue:** Import grouping order varies:
1. `camera.py` - TYPE_CHECKING not used, no clear grouping
2. `sprites.py` - pygame before os
3. `battle_ui_service.py` - game.ui imports before game.core
4. `battle_factories.py` - Correct order (stdlib, third-party, local) with TYPE_CHECKING at end

Standard Python convention: stdlib > third-party > local, alphabetical within groups.
**Impact:** Minor readability issue; inconsistent with PEP 8.
**Recommendation:** Use isort or ruff to enforce consistent import ordering.
**Effort:** Simple

#### MINOR: Magic Numbers in Renderer
**ID:** CON-UI2-010
**Location:** `game/ui/renderer/game_renderer.py:151`, `game/ui/renderer/camera.py:149`
**Issue:** While game_renderer.py has extracted many constants (PROJ-141 CON-UI2-012), some magic numbers remain:
- `camera.py:149` - `width = max_x - min_x + 500` (margin value)
- `camera.py:17-18` - `zoom_speed = 8.0`, hardcoded defaults

**Impact:** Harder to tune behavior; inconsistent with extracted constants pattern in same module.
**Recommendation:** Extract to UIConfig or module-level constants.
**Effort:** Simple

#### MINOR: Inconsistent Boolean Parameter Naming
**ID:** CON-UI2-011
**Location:** `game/ui/services/battle_factories.py`
**Issue:** Boolean parameters don't consistently use is_/has_/can_ prefixes:
- `headless: bool` (line 84, 114, 129) - could be `is_headless`
- `allow_retreat: bool` (line 143) - could be `can_retreat`
- `isolated: bool` (BattleConfig line 191) - could be `is_isolated`

Contrast with DTO attributes which use `is_alive`, `is_derelict`, `is_active`, `has_weapon`.
**Impact:** Minor inconsistency with project convention.
**Recommendation:** Rename to use prefixes: `is_headless`, `can_retreat`, `is_isolated`.
**Effort:** Simple

#### MINOR: Inconsistent Method Prefix Verbs
**ID:** CON-UI2-012
**Location:** `game/ui/assets/ship_theme_manager.py`, `game/ui/services/`
**Issue:** Similar operations use different verb prefixes:
- `get_image_metrics()` vs `load_image()` - get vs load for retrieval with caching
- `get_portrait_image()` vs `load_image()` - inconsistent within same class
- `get_manual_scale()` - pure retrieval
- `get_available_themes()` - returns list

Pattern should be: `get_*` for pure retrieval, `load_*` for I/O with caching.
**Impact:** Unclear whether method does I/O or is pure accessor.
**Recommendation:** Rename `get_portrait_image()` to `load_portrait_image()` for consistency, or clarify naming convention in docstrings.
**Effort:** Simple

#### INFO: Different Service Class Suffixes
**ID:** CON-UI2-013
**Location:** `game/ui/services/`
**Issue:** Service classes use different suffixes:
- `*Service` - ComponentService, VehicleClassService, ValidationService, BattleUIService
- `*Adapter` - DesignLoaderAdapter, ShipIOAdapter
- `*Factory` - ShipFactory
- `*Manager` - SpriteManager, ShipThemeManager, ScreenshotManager, InputMapper

This is actually appropriate semantic distinction:
- Service: Stateless business logic
- Adapter: Wraps external interface
- Factory: Creates objects
- Manager: Stateful singleton with lifecycle

**Impact:** None - this is intentional and appropriate.
**Recommendation:** Document the naming convention to maintain consistency.
**Effort:** None needed

#### INFO: Constants Module Location
**ID:** CON-UI2-014
**Location:** `game/ui/colors.py`, `game/ui/config.py`
**Issue:** UI constants are split across two files:
- `colors.py` - Color constants (WHITE, BLACK, COLORS dict)
- `config.py` - UIConfig class with layout constants

Additionally, `game_renderer.py` has its own rendering constants section (lines 13-41).
**Impact:** Minor - developers must know where to find constants.
**Recommendation:** Consider consolidating into single `game/ui/constants.py` or documenting locations in module docstrings.
**Effort:** Simple (optional)

## Top 5 Priority Issues

1. **CON-UI2-001 (MAJOR): Inconsistent Dependency Injection Patterns** - This affects all service classes and sets precedent for future development. Standardizing DI patterns improves maintainability and reduces confusion.

2. **CON-UI2-003 (MAJOR): Inconsistent Type Hint Completeness** - Type hints are a documented project convention. The renderer and assets modules lack coverage compared to services, creating inconsistency.

3. **CON-UI2-005 (MAJOR): Two Singleton Patterns** - While all use SingletonMeta, the test isolation methods (reset vs clear) differ. This affects test reliability.

4. **CON-UI2-004 (MAJOR): Inconsistent Method Naming for Registry Access** - Internal consistency matters for maintainability. All services should use same helper pattern.

5. **CON-UI2-002 (MAJOR): Mixed Return Type Conventions** - IO operations return different tuple structures. Consider unified Result pattern.
