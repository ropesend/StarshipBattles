# Consistency Violations Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 22
- **Total Issues Found:** 18
- **Critical:** 1 | **Major:** 5 | **Minor:** 9 | **Info:** 3

## Findings

#### CRITICAL: Mixed DI Patterns - Some Services Require Provider, Others Optional
**ID:** CON-UI2-001
**Location:** `game/ui/services/vehicle_class_service.py:36-47`, `game/ui/services/component_service.py:31-50`, `game/ui/services/validation_service.py:33-46`
**Issue:** `VehicleClassService` requires `registry_provider` (raises `ValueError` if None) while `ComponentService` and `ValidationService` make it optional with lazy resolution. The docstring in `ComponentService` explicitly documents this inconsistency: "Services may choose strict required pattern (raises ValueError if None) when PROJ-50 explicitly mandated it (e.g., VehicleClassService)."
**Impact:** Developers must remember which services require DI and which don't. This creates potential runtime errors when switching between services or writing tests. The inconsistency also means some code paths are tested (required DI) while others silently fall back to globals.
**Recommendation:** Standardize on one pattern. Given PROJ-50's goal of strict DI, all services should require `registry_provider` with no lazy fallback. The fallback pattern defeats the purpose of DI.
**Effort:** Medium

#### MAJOR: Inconsistent Return Type Conventions for Save/Load Operations
**ID:** CON-UI2-002
**Location:** `game/ui/services/ship_io_adapter.py:72-103`, `game/ui/services/ship_io.py:42-126`
**Issue:** Save operations return `Tuple[bool, Optional[str]]` (success flag + message) while load operations return `Tuple[Optional[T], Optional[str]]` (object + message). The docstring acknowledges this: "The different return types are intentional."
**Impact:** Callers must handle different return tuple semantics for related operations. This is documented but still creates cognitive overhead and potential for incorrect handling.
**Recommendation:** This is a conscious design decision that's well-documented. Consider adding a typed union or result type to make the pattern more explicit, but the current approach is acceptable given the documentation.
**Effort:** Simple (documentation already exists)

#### MAJOR: Inconsistent Private Method Naming - Single vs Double Underscore
**ID:** CON-UI2-003
**Location:** `game/ui/services/input_mapper.py:127-160`, `game/ui/assets/ship_theme_manager.py:79-115`
**Issue:** Most private methods use single underscore (`_get_provider`, `_convert_ship`), but `InputMapper._resolve_pygame_key` and `InputMapper._contexts_overlap` are `@staticmethod` methods with single underscore. The convention is inconsistent between instance methods and static methods that serve as implementation details.
**Impact:** Minor cognitive load, but Python convention is single underscore for private members regardless of method type. This is consistent.
**Recommendation:** Current usage is actually consistent (single underscore for all private members). No action needed.
**Effort:** N/A

#### MAJOR: Singleton Pattern vs Dependency Injection Conflict
**ID:** CON-UI2-004
**Location:** `game/ui/services/screenshot_manager.py:11-24`, `game/ui/renderer/sprites.py:8-21`, `game/ui/assets/ship_theme_manager.py:11-25`
**Issue:** Three classes use `SingletonMeta` metaclass (`ScreenshotManager`, `SpriteManager`, `ShipThemeManager`) while the project convention from CLAUDE.md states "Dependency Injection: Preferred over singletons for testability."
**Impact:** Singletons make testing difficult and create hidden global state. While the singleton pattern is used consistently within these managers, it conflicts with the stated project preference for DI.
**Recommendation:** Consider refactoring these managers to use DI pattern with a factory function that returns a shared instance, allowing tests to inject mock instances. Alternatively, document these as acceptable exceptions (asset managers that don't affect game logic).
**Effort:** Complex

#### MAJOR: Inconsistent Type Hints - `Any` vs Proper Types
**ID:** CON-UI2-005
**Location:** `game/ui/services/validation_service.py:33-60`, `game/ui/services/ship_factory.py:17-24`, `game/ui/services/design_loader_adapter.py:31-44`
**Issue:** Many methods use `Any` type hints for `ship`, `component`, `validator`, etc. when proper types exist in the codebase. For example, `ValidationService.validate_addition(ship: Any, component: Any, layer_type: 'LayerType')` could use proper Ship and Component types.
**Impact:** Loss of IDE support, type checker benefits, and documentation clarity. The `Any` type defeats the purpose of type hints.
**Recommendation:** Use `TYPE_CHECKING` imports to avoid circular dependencies while still providing proper type hints. Example: `from game.simulation.entities.ship import Ship` under `if TYPE_CHECKING:`, then use `'Ship'` string annotation.
**Effort:** Medium

#### MAJOR: Missing Type Hints on Multiple Functions
**ID:** CON-UI2-006
**Location:** `game/ui/renderer/game_renderer.py:22-142`, `game/ui/services/screenshot_manager.py:40-50`, `game/ui/assets/ship_theme_manager.py:117-135`
**Issue:** Several functions lack type hints entirely:
- `draw_ship(surface, ship, camera)` - no type hints
- `capture(self, surface=None, region=None, label=None)` - partial type hints (only return type documented)
- `load_image(self, theme_name, ship_class)` - no type hints
**Impact:** Violates project convention "Type Hints: Expected on all function signatures."
**Recommendation:** Add complete type hints to all public and private methods.
**Effort:** Medium

#### MINOR: Inconsistent Docstring Format Between Modules
**ID:** CON-UI2-007
**Location:** Multiple files
**Issue:** Most files use Google-style docstrings with Args/Returns sections (e.g., `ValidationService`, `InputMapper`), but some functions have minimal or no docstrings (e.g., `draw_ship` in `game_renderer.py`). The consistency within the services/ directory is good, but renderer/ is less consistent.
**Impact:** Reduced documentation quality and inconsistent developer experience.
**Recommendation:** Add Google-style docstrings to all public functions in renderer/ module.
**Effort:** Simple

#### MINOR: Inconsistent Method Verb Prefixes for Getter Operations
**ID:** CON-UI2-008
**Location:** `game/ui/services/component_service.py`, `game/ui/services/vehicle_class_service.py`, `game/ui/assets/ship_theme_manager.py`
**Issue:** Getter methods use inconsistent verb prefixes:
- `get_all_components()`, `get_modifier_registry()`, `get_all_classes()` - uses `get_`
- `load_image()`, `load_ship()` - uses `load_` (implies I/O operation)
- `is_modifier_allowed()` - uses `is_` predicate
The distinction between `get_` and `load_` is meaningful (memory vs I/O), so this is mostly consistent.
**Impact:** Minimal - the distinction between `get_` (retrieval) and `load_` (I/O) is actually a good convention.
**Recommendation:** Current usage is appropriate. No action needed.
**Effort:** N/A

#### MINOR: Inconsistent Error Handling - Exceptions vs Return None
**ID:** CON-UI2-009
**Location:** `game/ui/services/ship_factory.py:58-84`, `game/ui/services/design_loader_adapter.py:46-69`
**Issue:** `ShipFactory.create_from_design()` documents it raises `KeyError` and `ValueError` on error, while `DesignLoaderAdapter.load_ship_from_design_data()` returns `None` on error. Both wrap similar underlying functionality.
**Impact:** Callers must know which methods raise exceptions and which return None. This is documented but creates inconsistency.
**Recommendation:** Standardize error handling - either all raise exceptions or all return Optional with error indicator.
**Effort:** Medium

#### MINOR: Inconsistent Import Organization
**ID:** CON-UI2-010
**Location:** `game/ui/services/screenshot_manager.py:1-8`, `game/ui/assets/ship_theme_manager.py:1-8`
**Issue:** Import organization varies:
- `screenshot_manager.py`: stdlib imports not grouped, pygame after os/datetime
- `ship_theme_manager.py`: stdlib imports grouped, then third-party (pygame), then local
- Most service files follow the correct pattern
**Impact:** Minor code style inconsistency.
**Recommendation:** Standardize on: stdlib -> third-party (pygame) -> local game imports, with blank lines between groups.
**Effort:** Simple

#### MINOR: Inconsistent Naming - `registry_provider` vs `registries` Parameter
**ID:** CON-UI2-011
**Location:** `game/ui/services/ship_factory.py:40`, `game/ui/services/design_loader_adapter.py:31`
**Issue:** Parameters for GameRegistries are named differently:
- `ShipFactory.__init__(registry_provider: GameRegistries)` - uses `registry_provider`
- `DesignLoaderAdapter.__init__(registry_provider: Any)` - uses `registry_provider`
- But docstrings sometimes refer to "registries" vs "registry_provider"
**Impact:** Minor naming inconsistency, but the pattern is mostly consistent.
**Recommendation:** Standardize on `registry_provider` for IRegistryProvider and `registries` for GameRegistries instances.
**Effort:** Simple

#### MINOR: Hardcoded Color Tuples Instead of Using colors.py Constants
**ID:** CON-UI2-012
**Location:** `game/ui/renderer/game_renderer.py:14-19`, `game/ui/services/battle_ui_service.py:30-35`
**Issue:** Both files define color tuples inline instead of using the centralized `game/ui/colors.py`:
- `LAYER_COLORS` dict in `game_renderer.py`
- `PROJECTILE_COLORS` dict in `battle_ui_service.py`
**Impact:** Color definitions scattered across files instead of centralized in colors.py.
**Recommendation:** Move these color definitions to `colors.py` to maintain a single source of truth for UI colors.
**Effort:** Simple

#### MINOR: Inconsistent Module-Level Docstrings
**ID:** CON-UI2-013
**Location:** `game/ui/renderer/sprites.py`, `game/ui/renderer/camera.py`
**Issue:** `sprites.py` has no module-level docstring, while `camera.py` has a minimal one-liner. Other files like `input_mapper.py` have comprehensive module docstrings with usage examples.
**Impact:** Inconsistent documentation quality.
**Recommendation:** Add comprehensive module docstrings to renderer/ files.
**Effort:** Simple

#### MINOR: Boolean Method Naming - Missing `is_`/`has_`/`can_` Prefix
**ID:** CON-UI2-014
**Location:** `game/ui/services/battle_ui_service.py:100-109`
**Issue:** `is_battle_over()` correctly uses `is_` prefix, but related method naming is inconsistent with the pattern.
**Impact:** Minimal - the naming is actually consistent for boolean methods.
**Recommendation:** Current naming is good. No action needed.
**Effort:** N/A

#### MINOR: Magic Numbers in Configuration
**ID:** CON-UI2-015
**Location:** `game/ui/renderer/camera.py:17-19`, `game/ui/assets/ship_theme_manager.py:209`
**Issue:** Magic numbers used without named constants:
- `zoom_speed = 8.0` - hardcoded zoom animation speed
- `min_zoom = 0.01`, `max_zoom = 5.0` - hardcoded zoom limits
- Fallback image size `(100, 100)` in `_create_fallback_image`
**Impact:** These could be in UIConfig but are hardcoded.
**Recommendation:** Move camera zoom constants and fallback dimensions to UIConfig.
**Effort:** Simple

#### INFO: Intentional Pattern Variation - Adapter vs Service vs Factory Naming
**ID:** CON-UI2-016
**Location:** `game/ui/services/` directory
**Issue:** Different suffix conventions used intentionally:
- `*Service` - stateless service classes (`ValidationService`, `ComponentService`)
- `*Adapter` - adapter pattern wrapping other classes (`ShipIOAdapter`, `DesignLoaderAdapter`)
- `*Factory` - factory pattern for object creation (`ShipFactory`)
**Impact:** None - this is intentional and follows design pattern naming conventions.
**Recommendation:** Document this naming convention. Current usage is correct.
**Effort:** N/A

#### INFO: Different __init__.py Export Styles
**ID:** CON-UI2-017
**Location:** `game/ui/services/__init__.py`, `game/ui/interfaces/__init__.py`, `game/ui/assets/__init__.py`
**Issue:** `services/__init__.py` and `interfaces/__init__.py` use explicit imports with `__all__`, while `assets/__init__.py` is minimal but still uses `__all__`. The pattern is consistent.
**Impact:** None - the pattern is consistent across the UI framework.
**Recommendation:** No action needed.
**Effort:** N/A

#### INFO: Cross-Layer Import Documentation Quality
**ID:** CON-UI2-018
**Location:** `game/ui/renderer/game_renderer.py:1-6`, `game/ui/orchestration/battle_orchestrator.py:10-21`
**Issue:** Both files document their cross-layer imports, but with different levels of detail:
- `game_renderer.py`: Brief comment explaining why LayerType is imported
- `battle_orchestrator.py`: Comprehensive explanation of the architectural rationale
**Impact:** Good practice, minor inconsistency in documentation depth.
**Recommendation:** Standardize on the more detailed documentation style from `battle_orchestrator.py` for all cross-layer imports.
**Effort:** Simple

## Top 5 Priority Issues

1. **CON-UI2-001 (CRITICAL): Mixed DI Patterns** - Some services require registry_provider while others make it optional. This creates runtime surprises and inconsistent testing patterns. Standardize on required DI.

2. **CON-UI2-004 (MAJOR): Singleton vs DI Conflict** - Three manager classes use SingletonMeta which conflicts with the project's stated preference for DI. Consider refactoring to DI with shared instances.

3. **CON-UI2-005 (MAJOR): `Any` Type Hints** - Many methods use `Any` instead of proper types, defeating the purpose of type hints and losing IDE support.

4. **CON-UI2-006 (MAJOR): Missing Type Hints** - Several public functions in renderer/ module lack type hints entirely, violating project conventions.

5. **CON-UI2-012 (MINOR): Scattered Color Definitions** - Color tuples defined in multiple files instead of centralized in colors.py, creating maintenance burden.
