# Consistency Violations Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 22
- **Total Issues Found:** 16
- **Critical:** 0 | **Major:** 5 | **Minor:** 9 | **Info:** 2

## Findings

#### MAJOR: Inconsistent Dependency Injection Patterns Across Services
**ID:** CON-UI2-001
**Location:** `game/ui/services/*.py` (multiple files)
**Issue:** Services use three different DI patterns:
1. **Strict DI (required):** `VehicleClassService.__init__` raises `ValueError` if `registry_provider` is None
2. **Optional DI with lazy resolution:** `ComponentService.__init__` accepts `Optional[IRegistryProvider]` and calls `get_default_registry_provider()` when needed
3. **Optional DI via default function call:** `DesignLoaderAdapter.__init__` calls `get_default_registries()` immediately if `registry_provider` is None
4. **Class injection:** `ShipIOAdapter.__init__` injects a class reference (`ship_io_class`) rather than an instance

The established convention is "optional DI with lazy resolution" as documented in `ComponentService`. However, `VehicleClassService` explicitly uses "strict DI" (per PROJ-50 mandate), and `BattleUIService.__init__` uses a required `battle_service` parameter without fallback (yet another pattern).
**Impact:** Cognitive overhead when using services; inconsistent test setup requirements; unclear which services need explicit injection vs. can use defaults
**Recommendation:** Document the two sanctioned patterns: (1) Strict DI where caller must provide dependency, (2) Optional DI with lazy resolution via `get_default_*()`. Remove the immediate resolution pattern from `DesignLoaderAdapter`.
**Effort:** Medium

#### MAJOR: Inconsistent Parameter Naming for Registry/Provider Injection
**ID:** CON-UI2-002
**Location:** `game/ui/services/ship_factory.py:40-41`, `game/ui/services/design_loader_adapter.py:31`, `game/ui/services/component_service.py:31`, `game/ui/services/vehicle_class_service.py:36`
**Issue:** Registry provider parameters use inconsistent names:
- `registry_provider` (ComponentService, VehicleClassService, DesignLoaderAdapter keyword-only)
- `registry_provider` as keyword-only in ShipFactory but returns `GameRegistries` not `IRegistryProvider`
- `_provider` as internal attribute in ComponentService and VehicleClassService
- `_registry_provider` as internal attribute in ShipFactory

The internal attribute naming is also inconsistent: `_provider` vs `_registry_provider`.
**Impact:** Confusion when reading code or writing tests; harder to establish patterns for new services
**Recommendation:** Standardize on `registry_provider` parameter name and `_registry_provider` internal attribute name across all services
**Effort:** Simple

#### MAJOR: Singleton Pattern vs Dependency Injection Inconsistency
**ID:** CON-UI2-003
**Location:** `game/ui/services/screenshot_manager.py:11`, `game/ui/renderer/sprites.py:7`, `game/ui/assets/ship_theme_manager.py:11`
**Issue:** Three classes use `SingletonMeta` metaclass for instance management (`ScreenshotManager`, `SpriteManager`, `ShipThemeManager`), while the project convention prefers dependency injection for testability. These singletons require `reset()` methods for test isolation.

Meanwhile, services like `ValidationService`, `ComponentService`, etc. follow proper DI patterns.
**Impact:** Harder to test in isolation; requires explicit `reset()` calls in test teardown; contradicts project's stated preference for DI over singletons
**Recommendation:** Consider converting these managers to DI-injectable services, or document that managers (as opposed to services) are allowed to use singleton pattern
**Effort:** Complex

#### MAJOR: Return Type Inconsistency for Failure Cases
**ID:** CON-UI2-004
**Location:** `game/ui/services/ship_io_adapter.py:72-103`, `game/ui/services/design_loader_adapter.py:46-87`
**Issue:** I/O operations return inconsistent types for failure/cancellation:
- `ShipIOAdapter.save_ship`: Returns `Tuple[bool, Optional[str]]` - `(False, None)` on cancel
- `ShipIOAdapter.load_ship`: Returns `Tuple[Optional[Any], Optional[str]]` - `(None, None)` on cancel
- `DesignLoaderAdapter.load_ship_from_design_data`: Returns `Optional[Any]` - `None` on error
- `DesignLoaderAdapter.load_ship_from_file`: Returns `Tuple[Optional[Any], str]` - always returns message string

The `ShipIOAdapter` documents this intentionally, but it's still inconsistent with the rest of the codebase where operations typically either return `None` or raise exceptions, not mixed tuple patterns.
**Impact:** Callers must handle multiple return type patterns for similar operations; harder to compose error handling
**Recommendation:** Standardize on `Result[T, E]`-style return or use exceptions for failures. Consider a unified `IOResult` type for all I/O operations.
**Effort:** Medium

#### MAJOR: Mixed Method Verb Prefixes for Similar Operations
**ID:** CON-UI2-005
**Location:** Multiple files across services
**Issue:** Similar operations use different verb prefixes:
- **get_** pattern: `get_all_classes()`, `get_class_definition()`, `get_ships()`, `get_binding()`, `get_available_themes()`
- **load_** pattern: `load_image()`, `load_ship()`, `load_ship_from_design_data()`, `load_ship_from_file()`, `load_sprites()`
- **create_** pattern: `create_from_design()`, `create_ai_controllers()`, `create_ai_for_ship()`, `create_centered_rect()`
- **Mixed:** `get_portrait_image()` (should be `load_portrait_image()` since it loads from disk)

The distinction should be: `get_*` for retrieval from memory/cache, `load_*` for disk I/O, `create_*` for instantiation.
**Impact:** Cognitive overhead; unclear whether method performs I/O or uses cached data
**Recommendation:** Rename `get_portrait_image()` to `load_portrait_image()` or rename internal `_load_portrait_image()` to `_fetch_portrait_image()` for clarity
**Effort:** Simple

#### MINOR: Inconsistent Type Hint Usage for Ship Parameter
**ID:** CON-UI2-006
**Location:** `game/ui/services/ship_io_adapter.py:72`, `game/ui/services/ship_factory.py:110-118`
**Issue:** Ship parameters are typed inconsistently:
- `ShipIOAdapter.save_ship(ship: Any)` - uses `Any`
- `ShipFactory.configure_ship(ship: 'Ship')` - uses forward reference string
- `BattleOrchestrator.create_ai_for_ship(ship: 'Ship')` - uses forward reference

The convention should use `TYPE_CHECKING` imports with forward references for cross-layer types.
**Impact:** Loss of type safety; IDE autocomplete doesn't work with `Any`
**Recommendation:** Use consistent `'Ship'` forward reference with `TYPE_CHECKING` import
**Effort:** Simple

#### MINOR: Docstring Format Inconsistency
**ID:** CON-UI2-007
**Location:** Multiple files
**Issue:** Docstrings use mixed formats:
- **Google style (Args/Returns sections):** `ValidationService`, `ComponentService`, `ShipFactory`, `DesignLoaderAdapter`
- **Brief inline style:** `Camera`, `SpriteManager`
- **Sphinx :param: style:** `ScreenshotManager.capture` uses `:param:` format

Most files use Google style, but `Camera.update()` and `Camera.update_input()` use paragraph descriptions without structured Args sections, and `ScreenshotManager.capture` uses `:param:` style.
**Impact:** Inconsistent documentation; harder to auto-generate API docs
**Recommendation:** Standardize on Google style docstrings for all public methods
**Effort:** Simple

#### MINOR: Boolean Parameter Naming Without Prefix
**ID:** CON-UI2-008
**Location:** `game/ui/services/screenshot_manager.py:118`
**Issue:** `capture_strategy_layer(scene, include_ui=True, include_subwindows=True, label=None)` uses boolean parameters without `should_`/`is_` prefix. The project convention is to use `is_*`/`has_*`/`can_*`/`should_*` for boolean variables.

However, `include_*` is arguably clear as a verb phrase and common in APIs.
**Impact:** Minor inconsistency with boolean naming convention
**Recommendation:** This is acceptable since `include_*` is clear; no change needed
**Effort:** Simple

#### MINOR: Constants Defined at Module Level vs Class Level
**ID:** CON-UI2-009
**Location:** `game/ui/services/battle_ui_service.py:31-36`, `game/ui/renderer/game_renderer.py:13-19`, `game/ui/config.py:17-67`
**Issue:** Color and configuration constants are defined inconsistently:
- `PROJECTILE_COLORS` and `DEFAULT_PROJECTILE_COLOR` at module level in `battle_ui_service.py`
- `LAYER_COLORS` at module level in `game_renderer.py`
- `UIConfig` as a class with class attributes in `config.py`

The UIConfig class pattern is cleaner for namespacing. Color constants in other modules are module-level.
**Impact:** Minor inconsistency; harder to discover all UI constants
**Recommendation:** Consider adding color constants to `UIConfig` or a separate `UIColors` class in `colors.py`
**Effort:** Simple

#### MINOR: Mixed Logging Patterns
**ID:** CON-UI2-010
**Location:** `game/ui/services/screenshot_manager.py:36-37`, `game/ui/services/ship_io.py:72-76`, `game/ui/renderer/sprites.py:50,90`
**Issue:** Logging uses consistent `log_error()`, `log_info()`, `log_warning()` functions from `game.core.logger`. This is consistent across all files.

However, log message formats vary:
- `f"Created screenshot directory: {self.base_dir}"` (descriptive)
- `f"ShipIO: Permission denied saving ship: {e}"` (prefixed with class name)
- `f"loading {f}: {e}"` (lowercase, no context)
**Impact:** Inconsistent log searchability; harder to filter logs by component
**Recommendation:** Standardize on `f"ClassName: Action description: {details}"` format
**Effort:** Simple

#### MINOR: Import Organization Inconsistencies
**ID:** CON-UI2-011
**Location:** `game/ui/assets/ship_theme_manager.py:1-8`, `game/ui/services/ship_io.py:11-18`
**Issue:** Import grouping varies:
- Most files follow: stdlib -> third-party (pygame) -> local (game.*)
- `ship_theme_manager.py` mixes: `os`, `pygame`, `threading` (stdlib), then local - pygame grouped with stdlib
- `ship_io.py`: stdlib (`json`, `os`, `tkinter`), then local

This is generally consistent but `pygame` is sometimes grouped with stdlib when it should be in third-party section.
**Impact:** Minor style inconsistency
**Recommendation:** Add blank line between stdlib and pygame imports
**Effort:** Simple

#### MINOR: Inconsistent Use of Optional vs Default None
**ID:** CON-UI2-012
**Location:** `game/ui/services/input_mapper.py:71-75`, `game/ui/services/design_loader_adapter.py:31`
**Issue:** Some methods use `Optional[str] = None` while others just use `= None`:
- `InputMapper.load(defaults_path: Optional[str] = None)` - explicit Optional
- Most methods just use `param = None` without Optional type hint

The typing module `Optional` should be used for clarity when None is a valid value.
**Impact:** Minor type safety issue
**Recommendation:** Use `Optional[T]` consistently for parameters that can be None
**Effort:** Simple

#### MINOR: Thread Safety Documentation Inconsistency
**ID:** CON-UI2-013
**Location:** `game/ui/services/screenshot_manager.py:17`, `game/ui/assets/ship_theme_manager.py:18`, `game/ui/renderer/sprites.py:13`
**Issue:** Singleton classes document thread safety in their docstrings, but implementation varies:
- `ShipThemeManager` uses `_init_lock` and `_io_lock` for proper thread safety
- `ScreenshotManager` has no internal locking
- `SpriteManager` has no internal locking

If these are thread-safe via SingletonMeta, their internal state mutations should also be protected.
**Impact:** Potential race conditions in multi-threaded scenarios
**Recommendation:** Add locking to `ScreenshotManager` and `SpriteManager` or document that they are not internally thread-safe
**Effort:** Medium

#### MINOR: User Story Comment in Production Code
**ID:** CON-UI2-014
**Location:** `game/ui/renderer/game_renderer.py:77`
**Issue:** Comment `# "I want to have a empty circle that should represent the radius of the vesle when the ovelay is on"` appears to be a user story/requirement comment, not code documentation.
**Impact:** Unprofessional appearance, noise in codebase
**Recommendation:** Remove user story comments or convert to proper documentation
**Effort:** Simple

#### INFO: Protocol Definition Location
**ID:** CON-UI2-015
**Location:** `game/ui/interfaces/battle_ui.py`
**Issue:** The `IBattleUI` Protocol is defined alongside its DTOs in the same file. This is appropriate since they're closely related.

The interfaces package exports these cleanly via `__init__.py`. This follows good practice.
**Impact:** None - this is good design
**Recommendation:** No change needed
**Effort:** N/A

#### INFO: __init__.py Export Patterns
**ID:** CON-UI2-016
**Location:** `game/ui/__init__.py`, `game/ui/services/__init__.py`, `game/ui/interfaces/__init__.py`, `game/ui/orchestration/__init__.py`, `game/ui/assets/__init__.py`
**Issue:** All `__init__.py` files consistently:
- Import from submodules
- Define `__all__` lists
- Use explicit imports (not `from . import *`)

This is excellent consistency across the UI package.
**Impact:** None - exemplary pattern
**Recommendation:** Maintain this pattern
**Effort:** N/A

## Top 5 Priority Issues

1. **CON-UI2-001 (MAJOR): Inconsistent Dependency Injection Patterns** - Services use 4 different DI patterns (strict required, optional with lazy, optional with immediate, class injection). This creates confusion about how to construct and test services. Standardize on 2 patterns and document when each applies.

2. **CON-UI2-003 (MAJOR): Singleton Pattern vs Dependency Injection** - Three manager classes use SingletonMeta while the project prefers DI. This creates test isolation issues and contradicts stated conventions. Consider whether managers are an exception or should be converted.

3. **CON-UI2-004 (MAJOR): Return Type Inconsistency for Failure Cases** - I/O operations return inconsistent types (`bool, Optional[str]` vs `Optional[T], Optional[str]` vs `Optional[T]`). This makes error handling difficult. Consider a unified Result type or consistent exception-based approach.

4. **CON-UI2-002 (MAJOR): Inconsistent Parameter Naming for Registry Injection** - Registry provider parameters use different names (`registry_provider`, with different internal storage names). Standardize naming for consistency.

5. **CON-UI2-005 (MAJOR): Mixed Method Verb Prefixes** - `get_*` vs `load_*` vs `create_*` are used inconsistently. The `get_portrait_image()` method loads from disk but uses `get_` prefix. Clarify verb semantics: get = from memory, load = from disk, create = new instance.
