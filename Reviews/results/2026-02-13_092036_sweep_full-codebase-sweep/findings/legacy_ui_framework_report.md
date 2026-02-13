# Legacy System Holdovers Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 22
- **Total Issues Found:** 8
- **Critical:** 0 | **Major:** 2 | **Minor:** 5 | **Info:** 1

## Scope Details
Files in scope:
- `game/ui/__init__.py`
- `game/ui/utils.py`
- `game/ui/config.py`
- `game/ui/colors.py`
- `game/ui/services/__init__.py`
- `game/ui/services/validation_service.py`
- `game/ui/services/vehicle_class_service.py`
- `game/ui/services/component_service.py`
- `game/ui/services/ship_factory.py`
- `game/ui/services/design_loader_adapter.py`
- `game/ui/services/ship_io_adapter.py`
- `game/ui/services/battle_ui_service.py`
- `game/ui/services/screenshot_manager.py`
- `game/ui/services/ship_io.py`
- `game/ui/services/input_mapper.py`
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

#### MAJOR: Global Registry Fallback Pattern in ShipFactory
**ID:** LEG-UI2-001
**Location:** `game/ui/services/ship_factory.py:15,44-56`
**Issue:** ShipFactory explicitly documents "legacy behavior" of falling back to global `get_default_registries()` when no registries are provided. Two production callers (`setup_data_io.py:21` and `setup_screen.py:28`) rely on this fallback pattern instead of injecting registries.
**Impact:** Creates inconsistency with PROJ-50's strict DI policy. The comment explicitly acknowledges this is legacy behavior that was retained for backward compatibility.
**Recommendation:** Update `setup_data_io.py` and `setup_screen.py` to inject registries explicitly, then remove the fallback from ShipFactory to enforce strict DI.
**Effort:** Medium

#### MAJOR: Global Registry Fallback Pattern in ComponentService
**ID:** LEG-UI2-002
**Location:** `game/ui/services/component_service.py:31-49`
**Issue:** ComponentService follows the same optional DI pattern with fallback to `get_default_registry_provider()`. Unlike VehicleClassService (which was updated to strict DI in PROJ-50), ComponentService retained the fallback pattern.
**Impact:** Inconsistency in DI policy across services in the same package. VehicleClassService requires registry_provider, ComponentService does not.
**Recommendation:** Update ComponentService to require registry_provider and enforce strict DI for consistency with VehicleClassService.
**Effort:** Medium

#### MINOR: Unused Protocol Import (IBattleUI)
**ID:** LEG-UI2-003
**Location:** `game/ui/services/battle_ui_service.py:14-15`
**Issue:** `IBattleUI` is imported from `game.ui.interfaces.battle_ui` but never used in the module. The class `BattleUIService` claims to "implement the IBattleUI protocol" in its docstring but doesn't actually declare it.
**Impact:** Dead import. The protocol is defined but never enforced through type annotations or isinstance checks anywhere in the codebase.
**Recommendation:** Either remove the unused import and protocol definition, or properly annotate BattleUIService as implementing the protocol.
**Effort:** Simple

#### MINOR: Unused Method get_ships_folder in ShipIOAdapter
**ID:** LEG-UI2-004
**Location:** `game/ui/services/ship_io_adapter.py:64-70`
**Issue:** The `get_ships_folder()` method is defined in ShipIOAdapter but never called from production code. Only used in unit tests.
**Impact:** Dead code in production. Test-only method should be either removed or marked as test utility.
**Recommendation:** Remove the method if it's not needed for production, or document it as a test helper.
**Effort:** Simple

#### MINOR: Global Registry Fallback in DesignLoaderAdapter
**ID:** LEG-UI2-005
**Location:** `game/ui/services/design_loader_adapter.py:31-44`
**Issue:** DesignLoaderAdapter follows the same optional DI pattern with fallback to `get_default_registries()`. Same inconsistency as ComponentService.
**Impact:** Inconsistent DI policy within the services package.
**Recommendation:** Update to require registry_provider for consistency with strict DI policy.
**Effort:** Simple

#### MINOR: Defensive getattr Patterns for Missing Attributes
**ID:** LEG-UI2-006
**Location:** `game/ui/services/battle_ui_service.py:171,196-197,235-236,250,255,258,266-274`
**Issue:** BattleUIService uses extensive `getattr(..., default)` patterns for attributes like `crew_onboard`, `crew_required`, `shots_fired`, `shots_hit`, etc. Comments explain these are "dynamically set by ShipStatsCalculator, not in __init__" - indicating the Ship class has attributes that aren't always guaranteed to exist.
**Impact:** While this is defensive coding, it masks potential issues where objects may not be fully initialized. The ship/component/projectile classes could benefit from always initializing these attributes to their defaults.
**Recommendation:** Consider auditing Ship/Component/Projectile classes to ensure all expected attributes are initialized in `__init__` to remove the need for defensive getattr calls.
**Effort:** Medium (cross-module)

#### MINOR: hasattr Checks for Potentially Missing Attributes
**ID:** LEG-UI2-007
**Location:** `game/ui/services/battle_ui_service.py:161,167,219,224,251`, `game/ui/services/screenshot_manager.py:145,151`
**Issue:** Multiple `hasattr` checks for attributes that should consistently exist if the architecture is clean. Examples: checking if `ship.current_target` has `name`, if `comp` has `status` and `has_ability`, if scene has `ui` and `build_queue_screen`.
**Impact:** These checks suggest the interfaces between layers are not well-defined, requiring defensive programming. May indicate incomplete protocol definitions.
**Recommendation:** Review the interfaces to determine if these attributes should always exist and update type hints/protocols accordingly.
**Effort:** Medium

#### INFO: Singleton Pattern Usage
**ID:** LEG-UI2-008
**Location:** `game/ui/renderer/sprites.py:7`, `game/ui/services/screenshot_manager.py:11`, `game/ui/assets/ship_theme_manager.py:11`
**Issue:** Three classes in scope use `SingletonMeta` metaclass: `SpriteManager`, `ScreenshotManager`, and `ShipThemeManager`. The project prefers dependency injection over singletons.
**Impact:** These singletons are used for caching (sprites, images) and cross-cutting concerns (screenshots). They are functioning correctly but represent an older pattern that doesn't align with the stated preference for DI.
**Recommendation:** No immediate action needed - these are legitimate use cases for singletons (global caches). Document the rationale for retaining singleton pattern for these specific cases.
**Effort:** N/A - informational

## Top 5 Priority Issues

1. **LEG-UI2-001 (MAJOR):** Global Registry Fallback in ShipFactory - Two production callers rely on legacy fallback behavior that contradicts PROJ-50's strict DI policy.

2. **LEG-UI2-002 (MAJOR):** Global Registry Fallback in ComponentService - Inconsistent DI policy within the same services package (VehicleClassService is strict, ComponentService is not).

3. **LEG-UI2-006 (MINOR):** Defensive getattr Patterns - Extensive use of getattr with defaults indicates Ship/Component/Projectile classes don't consistently initialize all attributes used by UI layer.

4. **LEG-UI2-003 (MINOR):** Unused IBattleUI Protocol Import - Protocol is defined and documented but never actually used for type checking.

5. **LEG-UI2-005 (MINOR):** Global Registry Fallback in DesignLoaderAdapter - Third service in the same package with inconsistent DI policy.

## Notes

The UI-Framework shard is generally clean with no critical issues. The main theme across findings is **inconsistent DI policy**: some services were updated to strict DI in PROJ-50 (VehicleClassService) while others retained fallback patterns (ShipFactory, ComponentService, DesignLoaderAdapter).

The project's migration to strict DI is incomplete within this package. A follow-up project to standardize all services to strict DI would improve consistency and eliminate the documented "legacy behavior" patterns.
