# Consistency Violations Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 21
- **Total Issues Found:** 18
- **Critical:** 1 | **Major:** 6 | **Minor:** 8 | **Info:** 3

## Findings

#### CRITICAL: Inconsistent DI Pattern - Some Services Require Provider, Others Allow None
**ID:** CON-UI2-001
**Location:** `game/ui/services/vehicle_class_service.py:36-47` vs `game/ui/services/component_service.py:31-44`
**Issue:** VehicleClassService requires registry_provider (raises ValueError if None) while ComponentService allows None with lazy resolution. Both claim to follow DI patterns but enforce different contracts.
**Impact:** Callers cannot reason about which services require explicit DI. VehicleClassService fails at construction time if not given a provider; ComponentService works silently. This inconsistency creates confusion about initialization requirements.
**Recommendation:** Standardize on one pattern across all UI services. Either all services require explicit DI (strict pattern - already documented as PROJ-50) or all allow lazy resolution. The PROJ-50 mandate for strict DI should be applied consistently.
**Effort:** Medium

#### MAJOR: Singleton vs Dependency Injection Pattern Conflict
**ID:** CON-UI2-002
**Location:** `game/ui/services/screenshot_manager.py:11`, `game/ui/renderer/sprites.py:7`, `game/ui/assets/ship_theme_manager.py:11`
**Issue:** Three managers use SingletonMeta pattern while other services use constructor-based DI. Project conventions prefer dependency injection over singletons for testability.
**Impact:** Inconsistent testability. Singleton managers require `reset()` calls in tests, while DI-based services can be mocked naturally. Mixed patterns create confusion about how to properly test UI code.
**Recommendation:** Consider refactoring singleton managers to support DI pattern. ShipThemeManager and SpriteManager could accept their dependencies (paths, pygame) via constructor.
**Effort:** Complex

#### MAJOR: Mixed Return Type Patterns for Error Handling
**ID:** CON-UI2-003
**Location:** `game/ui/services/ship_io.py:42-82` vs `game/ui/services/design_loader_adapter.py:46-69`
**Issue:** ShipIO.save_ship returns `(bool, Optional[str])` tuple while ShipIO.load_ship returns `(Optional[Ship], Optional[str])`. DesignLoaderAdapter.load_ship_from_design_data returns `Optional[Ship]` (no message). Three different patterns for similar operations.
**Impact:** Callers must handle different return type contracts for related operations. Error handling code becomes inconsistent.
**Recommendation:** Standardize on the tuple pattern `(success/result, Optional[message])` documented in ShipIOAdapter docstring for all I/O operations, or use a Result type wrapper.
**Effort:** Medium

#### MAJOR: Inconsistent Parameter Naming for Registry Provider
**ID:** CON-UI2-004
**Location:** Multiple files in `game/ui/services/`
**Issue:** Services use different names for the same concept:
- `registry_provider` (VehicleClassService, ComponentService, DesignLoaderAdapter keyword)
- `registries` (ShipFactory stores as _registry_provider but parameter named `registry_provider`)
- `validator` (ValidationService - different type but same pattern)
**Impact:** Cognitive overhead when working across services. Hard to remember which parameter name each service uses.
**Recommendation:** Standardize on `registry_provider` for IRegistryProvider instances. Document the naming convention in services/__init__.py.
**Effort:** Simple

#### MAJOR: Missing Type Hints on Public Functions
**ID:** CON-UI2-005
**Location:** `game/ui/renderer/game_renderer.py:22,145,153`
**Issue:** Module-level functions `draw_ship`, `draw_bar`, `draw_hud` lack type hints for parameters and return types. Project conventions require type hints on function signatures.
**Impact:** IDE autocomplete degraded, static analysis cannot catch type errors, documentation incomplete.
**Recommendation:** Add complete type hints: `def draw_ship(surface: pygame.Surface, ship: Ship, camera: Camera) -> None:`
**Effort:** Simple

#### MAJOR: Docstring Inconsistency - Some Use Google Style, Others Minimal
**ID:** CON-UI2-006
**Location:** `game/ui/services/screenshot_manager.py:40-46` vs `game/ui/services/validation_service.py:48-60`
**Issue:** ScreenshotManager.capture uses minimal `:param:` docstrings while ValidationService uses full Google-style Args/Returns blocks. Mixed styles across the codebase.
**Impact:** Inconsistent documentation style makes codebase harder to read. Different IDE parsers handle different styles differently.
**Recommendation:** Standardize on Google-style docstrings (Args:/Returns:/Raises:) as used in validation_service.py, component_service.py, and vehicle_class_service.py.
**Effort:** Simple

#### MAJOR: Inconsistent Module-Level vs Class-Level Constants
**ID:** CON-UI2-007
**Location:** `game/ui/colors.py:7-14` vs `game/ui/config.py:17-67`
**Issue:** colors.py defines module-level constants (WHITE, BLACK, etc.) while config.py wraps all constants in UIConfig class. Both are valid but inconsistent.
**Impact:** Callers import differently: `from colors import WHITE` vs `UIConfig.PANEL_PADDING`. Inconsistent access patterns.
**Recommendation:** For organizational consistency, either move basic colors into a Colors class or make UIConfig values module-level. Given the semantic grouping in colors.py (basic + COLORS dict), the current split is acceptable but should be documented.
**Effort:** Simple

#### MINOR: Inconsistent Boolean Method Naming
**ID:** CON-UI2-008
**Location:** `game/ui/services/component_service.py:82` vs `game/ui/interfaces/battle_ui.py:222`
**Issue:** `is_modifier_allowed` uses `is_` prefix (correct for boolean returns). `is_battle_over` also correct. But some checks are done inline without method extraction. Pattern is mostly consistent.
**Impact:** Low - naming is mostly consistent.
**Recommendation:** Maintain current convention. Ensure any new boolean methods use `is_/has_/can_/should_` prefixes.
**Effort:** N/A (acceptable)

#### MINOR: Redundant Exception Handling in ship_io.py
**ID:** CON-UI2-009
**Location:** `game/ui/services/ship_io.py:71-82` and `127-129`
**Issue:** Both save_ship and load_ship have redundant exception catches. OSError and PermissionError are caught twice. Second catch is unreachable.
**Impact:** Dead code, potential confusion about error handling intent.
**Recommendation:** Remove duplicate exception handlers on lines 80-82 and 127-129.
**Effort:** Simple

#### MINOR: Inconsistent Import Organization
**ID:** CON-UI2-010
**Location:** `game/ui/renderer/sprites.py:1-4` vs `game/ui/services/input_mapper.py:22-31`
**Issue:** sprites.py mixes stdlib and local imports without clear grouping. input_mapper.py has clear separation with `from __future__` first, then stdlib, then local. Import organization varies across files.
**Impact:** Minor readability impact. Some files harder to scan for dependencies.
**Recommendation:** Standardize import order: future, stdlib, third-party (pygame), local. Add blank line between groups.
**Effort:** Simple

#### MINOR: Method Prefix Inconsistency - get_ vs load_
**ID:** CON-UI2-011
**Location:** `game/ui/assets/ship_theme_manager.py:117,167,219`
**Issue:** Mixed use of `load_image`, `get_image_metrics`, `get_portrait_image`. `load_image` and `get_portrait_image` both load from disk and cache. Inconsistent verb choice for similar operations.
**Impact:** Cognitive overhead - unclear if method will hit disk or return cached data.
**Recommendation:** Use `get_` for cached access (may trigger load). Use `load_` only for explicit load operations. Or document the caching behavior clearly.
**Effort:** Simple

#### MINOR: Inconsistent Private Method Naming
**ID:** CON-UI2-012
**Location:** `game/ui/assets/ship_theme_manager.py:136,247,293`
**Issue:** Private methods `_load_single_image`, `_load_portrait_image`, `_ship_class_to_portrait_name` use single underscore consistently. However, `_discover_theme` at line 79 is discovery not loading. Method naming convention is consistent but verb choices vary (load vs discover vs create).
**Impact:** Low - underscore convention is consistent.
**Recommendation:** Current pattern is acceptable. Single underscore for private is correct.
**Effort:** N/A (acceptable)

#### MINOR: Magic Numbers in game_renderer.py
**ID:** CON-UI2-013
**Location:** `game/ui/renderer/game_renderer.py:33,155-157,180-188`
**Issue:** Magic numbers not using UIConfig constants: `50 * camera.zoom`, font sizes 16/14/12, bar dimensions 100/8. UIConfig exists but isn't used in this file.
**Impact:** If UI sizing needs change, values are scattered. Not using centralized config.
**Recommendation:** Either use UIConfig constants or add renderer-specific constants to UIConfig.
**Effort:** Medium

#### MINOR: Inconsistent Error Logging Format
**ID:** CON-UI2-014
**Location:** `game/ui/services/ship_io.py:72,116` vs `game/ui/assets/ship_theme_manager.py:112,161`
**Issue:** ShipIO uses format: `ShipIO: Permission denied loading ship: {e}`. ShipThemeManager uses: `Lazy load failed - file not found {path}: {e}`. Different prefixing and message structure.
**Impact:** Log parsing and filtering becomes harder with inconsistent formats.
**Recommendation:** Standardize on `{ClassName}: {action} - {detail}: {exception}` format.
**Effort:** Simple

#### MINOR: Unused Comments as Section Headers
**ID:** CON-UI2-015
**Location:** `game/ui/renderer/game_renderer.py:76-77`
**Issue:** Comment "I want to have a empty circle..." appears to be a user story/requirement comment, not code documentation.
**Impact:** Unprofessional appearance, noise in codebase.
**Recommendation:** Remove user story comments or convert to proper documentation.
**Effort:** Simple

#### INFO: Cross-Layer Imports Documented But Inconsistently
**ID:** CON-UI2-016
**Location:** `game/ui/orchestration/battle_orchestrator.py:16-21` vs `game/ui/renderer/game_renderer.py:1-10`
**Issue:** battle_orchestrator.py has excellent cross-layer import documentation. game_renderer.py has brief note but less detailed. Documentation quality varies.
**Impact:** Low - better documentation is good, but inconsistent.
**Recommendation:** Add detailed cross-layer import notes to all files that import from other layers (game_renderer imports LayerType from core).
**Effort:** Simple

#### INFO: DTO Classes Could Use __slots__
**ID:** CON-UI2-017
**Location:** `game/ui/interfaces/battle_ui.py:17-172`
**Issue:** DTOs are frozen dataclasses which is correct. Using `__slots__` could reduce memory for frequently created DTOs, but frozen dataclasses handle this reasonably well.
**Impact:** Negligible performance difference.
**Recommendation:** Consider adding `slots=True` to dataclass decorator in Python 3.10+ for slight memory optimization. Not critical.
**Effort:** Simple

#### INFO: UIConfig Class Has No Methods
**ID:** CON-UI2-018
**Location:** `game/ui/config.py:17-67`
**Issue:** UIConfig is a pure data class with only class attributes. Could be a module-level namespace or a dataclass.
**Impact:** None - current pattern works fine.
**Recommendation:** Current approach is acceptable. Class provides namespace grouping.
**Effort:** N/A (acceptable)

## Top 5 Priority Issues

1. **CON-UI2-001 (CRITICAL):** DI pattern inconsistency between VehicleClassService (strict) and ComponentService (lazy). This directly violates the stated PROJ-50 mandate and causes initialization confusion.

2. **CON-UI2-002 (MAJOR):** Singleton vs DI pattern conflict. Three singleton managers violate project DI preference, hurting testability.

3. **CON-UI2-003 (MAJOR):** Mixed return type patterns for I/O operations make error handling code inconsistent and error-prone.

4. **CON-UI2-004 (MAJOR):** Inconsistent `registry_provider` parameter naming across services increases cognitive load.

5. **CON-UI2-005 (MAJOR):** Missing type hints on public renderer functions violates project conventions and degrades tooling support.
