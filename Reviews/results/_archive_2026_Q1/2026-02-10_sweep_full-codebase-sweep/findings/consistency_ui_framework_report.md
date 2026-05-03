# Consistency Violations Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 23
- **Total Issues Found:** 14
- **Critical:** 4 | **Major:** 5 | **Minor:** 3 | **Info:** 2

## Findings

#### CRITICAL: Inconsistent DI Pattern (registry_provider vs registries)
**ID:** CON-UI2-001
**Location:** `game/ui/services/vehicle_class_service.py`, `game/ui/services/component_service.py`, `game/ui/services/ship_factory.py`, `game/ui/services/design_loader_adapter.py`
**Issue:** Services use 4 different DI conventions: strict required, optional lazy, keyword-only, or dual parameters.
**Impact:** Callers must remember which pattern each service uses. Error-prone initialization.
**Recommendation:** Standardize on one pattern across all services.
**Effort:** Medium

#### CRITICAL: Null/None Handling Inconsistency in Services
**ID:** CON-UI2-002
**Location:** `game/ui/services/battle_ui_service.py:56-72`, vs other services
**Issue:** BattleUIService uses getattr with fallbacks extensively. ComponentService returns bool on errors. VehicleClassService returns Optional. No consistent None-handling strategy.
**Impact:** Callers cannot distinguish "not found" from "error occurred".
**Recommendation:** Define exception contract or consistently use Optional[T].
**Effort:** Medium

#### CRITICAL: Type Hints Missing on Private Methods
**ID:** CON-UI2-003
**Location:** `game/ui/services/battle_ui_service.py:121, 200, 232, 266`
**Issue:** Private converter methods lack return type hints (_convert_ship, _convert_component, _convert_projectile, _convert_beam) despite returning well-defined DTOs.
**Impact:** Static type checkers cannot verify conversions. IDE autocomplete breaks.
**Recommendation:** Add full type hints to all private methods.
**Effort:** Simple

#### CRITICAL: Return Type Inconsistency for File Operations
**ID:** CON-UI2-005
**Location:** `game/ui/services/ship_io_adapter.py:61, 77`
**Issue:** save_ship() returns Tuple[bool, Optional[str]]; load_ship() returns Tuple[Optional[Any], Optional[str]]. Different semantics for same pattern.
**Impact:** Callers must remember different result patterns.
**Recommendation:** Standardize tuple semantics across all I/O methods.
**Effort:** Medium

#### MAJOR: ShipThemeManager Singleton Pattern Violates DI Philosophy
**ID:** CON-UI2-006
**Location:** `game/ui/assets/ship_theme_manager.py:25-92`
**Issue:** Uses thread-safe singleton pattern. No way to inject mock for testing. Hard-coded Paths.ASSET_DIR.
**Impact:** Cannot test in isolation. UI code tightly coupled to asset system.
**Recommendation:** Refactor to injectable service pattern.
**Effort:** Medium

#### MAJOR: Inconsistent Constructor Parameter Naming
**ID:** CON-UI2-007
**Location:** Services package (component_service, vehicle_class_service, ship_factory, design_loader_adapter)
**Issue:** Some use registry_provider, others use registries (different semantic scope). No consistent naming.
**Impact:** Refactoring tools fail. Constant docstring reference needed.
**Recommendation:** Standardize on one parameter name.
**Effort:** Simple

#### MAJOR: Camera Class API Inconsistency
**ID:** CON-UI2-008
**Location:** `game/ui/renderer/camera.py:8-122`
**Issue:** Constructor uses positional args while all other UI classes use keyword-only args for DI. No type hints on any camera method. update_input() directly mutates state.
**Impact:** Camera API doesn't follow modern conventions.
**Recommendation:** Refactor to keyword-only args, add type hints.
**Effort:** Medium

#### MAJOR: BattleUIService Conversion Methods Lack Error Handling
**ID:** CON-UI2-009
**Location:** `game/ui/services/battle_ui_service.py:121-282`
**Issue:** _convert_ship() does not validate required attributes. Multiple getattr() with fallbacks, no logging of missing attributes.
**Impact:** Silent failures in battle rendering due to incompatible ship objects.
**Recommendation:** Add schema validation and logging for missing attributes.
**Effort:** Medium

#### MAJOR: Inconsistent Method Prefix Patterns
**ID:** CON-UI2-010
**Location:** Services across package
**Issue:** _get_provider() (private helper) vs get_ships() (public API). Some services use _get_* for lazy init, others for registry access.
**Impact:** Cannot predict method visibility/purpose from naming.
**Recommendation:** Use _get_ only for lazy init helpers; get_ for public accessors.
**Effort:** Simple

#### MINOR: Docstring Style Inconsistency
**ID:** CON-UI2-011
**Location:** Multiple files
**Issue:** Some use Google-style Args:/Returns:, some use bare docstrings, widgets.py has minimal docs.
**Impact:** Inconsistent IDE tooltips and documentation generation.
**Effort:** Simple

#### MINOR: Magic Numbers in Renderer Viewport
**ID:** CON-UI2-012
**Location:** `game/ui/renderer/camera.py:109-113`
**Issue:** Zoom multiplier hardcoded as 1.15. Min/max zoom limits hardcoded. No constants defined.
**Impact:** Changing zoom requires code search/replace.
**Recommendation:** Extract to module-level constants.
**Effort:** Simple

#### MINOR: Overloaded Semantic Meaning of "is_alive"
**ID:** CON-UI2-013
**Location:** `game/ui/interfaces/battle_ui.py:70` vs `game/ui/renderer/game_renderer.py:57`
**Issue:** ShipDTO.is_alive documented as "alive" but camera follows dead ships. Semantic mismatch between alive and controllable.
**Impact:** UI logic conflates alive and can_be_targeted.
**Recommendation:** Document full lifecycle (alive → derelict → dead).
**Effort:** Simple

#### INFO: PROJ References Without Version Tracking
**ID:** CON-UI2-014
**Location:** Services docstrings
**Issue:** Multiple PROJ references without dates or version numbers.
**Impact:** Future maintainers cannot track context.
**Effort:** None

#### INFO: Legacy Widgets Class
**ID:** CON-UI2-015
**Location:** `game/ui/widgets.py`
**Issue:** Legacy widget classes (Button, Label, Slider) exist but not imported in ui/__init__.py. No services, no interfaces.
**Impact:** Dead/legacy code mixed with modern framework.
**Recommendation:** Either migrate or move to _legacy/ directory.
**Effort:** Medium

## Top 5 Priority Issues
1. **CON-UI2-001**: DI pattern inconsistency - 4 different conventions across services
2. **CON-UI2-005**: Return type mismatch for I/O - different tuple semantics
3. **CON-UI2-006**: ShipThemeManager singleton - blocks testing
4. **CON-UI2-002**: None handling inconsistency - silent failures
5. **CON-UI2-008**: Camera API doesn't follow conventions - missing type hints
