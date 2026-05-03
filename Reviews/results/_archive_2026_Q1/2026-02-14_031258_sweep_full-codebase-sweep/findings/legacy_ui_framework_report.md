# Legacy System Holdovers Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 26
- **Total Issues Found:** 8
- **Critical:** 1 | **Major:** 2 | **Minor:** 4 | **Info:** 1

## Methodology Notes

Files scanned in this shard:
- `game/ui/__init__.py`
- `game/ui/utils.py`
- `game/ui/config.py`
- `game/ui/colors.py`
- `game/ui/services/` (13 files): `__init__.py`, `vehicle_class_service.py`, `component_service.py`, `design_loader_adapter.py`, `ship_io_adapter.py`, `input_mapper.py`, `tkinter_utils.py`, `battle_factories.py`, `battle_ui_service.py`, `ship_io.py`, `screenshot_manager.py`, `ship_factory.py`, `validation_service.py`
- `game/ui/renderer/` (4 files): `__init__.py`, `camera.py`, `sprites.py`, `game_renderer.py`
- `game/ui/interfaces/` (2 files): `__init__.py`, `battle_ui.py`
- `game/ui/orchestration/` (2 files): `__init__.py`, `battle_orchestrator.py`
- `game/ui/assets/` (2 files): `__init__.py`, `ship_theme_manager.py`

## Findings

#### CRITICAL: BattleOrchestrator is Defined but Never Used
**ID:** LEG-UI2-001
**Location:** `game/ui/orchestration/battle_orchestrator.py:1-99`
**Issue:** The entire `BattleOrchestrator` class (created in PROJ-17) is defined and exported but never imported or used anywhere in the production codebase. The class provides `create_ai_controllers()` and `create_ai_for_ship()` methods, but actual AI controller creation is done differently via `BattleController` and `AIControllerFactory` (see `battle_factories.py`).
**Impact:** Dead code module (99 lines) that creates confusion about how AI controllers should be created. The comments in `BattleEngine.start()` mention "BattleOrchestrator" but the actual code path uses `ai_factory` instead. This creates architectural confusion about the intended design.
**Recommendation:** Either delete the entire `game/ui/orchestration/` directory (if truly unused), or complete the migration to use `BattleOrchestrator` consistently. The `battle_factories.py` already provides equivalent functionality via `AIControllerFactory`, suggesting `BattleOrchestrator` is obsolete.
**Effort:** Medium (need to verify all battle creation paths)

#### MAJOR: Defensive getattr Checks for Attributes That Should Always Exist
**ID:** LEG-UI2-002
**Location:** `game/ui/services/battle_ui_service.py:178,203-204,242-243,257,262,265,273-281`
**Issue:** Extensive use of `getattr(obj, 'attr', default)` for attributes that should always exist on simulation objects (e.g., `ship.id`, `ship.crew_onboard`, `comp.shots_fired`, `proj.radius`). These defensive patterns suggest either: (a) incomplete migration where attributes were not always present, or (b) overly cautious coding that masks bugs.
**Impact:** These getattr calls hide potential bugs - if an attribute is truly missing, it indicates a deeper issue. The defaults (0, None, 'active') may produce incorrect UI displays without any error surfacing.
**Recommendation:** Audit each getattr usage:
- If the attribute is guaranteed by current code: remove defensive getattr
- If the attribute can legitimately be absent: document why and keep
- Consider using Protocol types with required attributes instead
**Effort:** Medium (requires verifying each attribute's source)

#### MAJOR: VehicleClassService Methods Appear Unused
**ID:** LEG-UI2-003
**Location:** `game/ui/services/vehicle_class_service.py:102-128`
**Issue:** Methods `get_max_mass()` and `get_type_for_class()` are defined but grep shows no usage in the codebase outside the class definition itself. These appear to be API surface that was defined but never integrated with callers.
**Impact:** Dead code within an otherwise-used class. Increases maintenance burden and test coverage requirements for unused methods.
**Recommendation:** Remove `get_max_mass()` and `get_type_for_class()` methods if truly unused. If they are needed for future features, document the intended use case or move to a backlog item.
**Effort:** Simple

#### MINOR: ComponentService.is_modifier_allowed Duplicates ModifierService.is_modifier_allowed
**ID:** LEG-UI2-004
**Location:** `game/ui/services/component_service.py:82-126`
**Issue:** `ComponentService.is_modifier_allowed()` re-implements the same logic as `ModifierService.is_modifier_allowed()` in the simulation layer. The UI's `ModifierLogic` class delegates to `ComponentService`, but the simulation layer already has the canonical implementation.
**Impact:** Code duplication that could diverge over time. Changes to modifier restriction logic need to be made in two places.
**Recommendation:** Have `ComponentService.is_modifier_allowed()` delegate to `ModifierService.is_modifier_allowed()` rather than re-implementing the logic. This maintains the facade pattern while eliminating duplication.
**Effort:** Simple

#### MINOR: ScreenshotManager Uses Singleton Pattern
**ID:** LEG-UI2-005
**Location:** `game/ui/services/screenshot_manager.py:19`
**Issue:** `ScreenshotManager` uses `SingletonMeta` metaclass for singleton pattern. The project has been migrating away from singletons toward dependency injection (see PROJ-50), but several UI managers still use singletons.
**Impact:** Makes testing harder (need to call `reset()` between tests), prevents having multiple isolated instances, creates hidden global state.
**Recommendation:** Consider converting to a regular class that gets injected where needed. Note: This is a lower priority since ScreenshotManager is legitimately a single-purpose global utility.
**Effort:** Medium

#### MINOR: ShipThemeManager and SpriteManager Use Singleton Pattern
**ID:** LEG-UI2-006
**Location:** `game/ui/assets/ship_theme_manager.py:11`, `game/ui/renderer/sprites.py:8`
**Issue:** Both managers use `SingletonMeta`. Same concern as LEG-UI2-005 regarding the migration toward dependency injection.
**Impact:** Same as LEG-UI2-005 - testing complexity and hidden global state.
**Recommendation:** These are asset managers that genuinely benefit from single-instance semantics for caching. Keep as-is but document the rationale. Lower priority than other findings.
**Effort:** Medium (if changed)

#### MINOR: Inconsistent DI Patterns Across Services
**ID:** LEG-UI2-007
**Location:** `game/ui/services/component_service.py:31`, `game/ui/services/vehicle_class_service.py:36`
**Issue:** `VehicleClassService` requires `registry_provider` (strict DI per PROJ-50), but `ComponentService` accepts `Optional[IRegistryProvider]` with lazy resolution. This inconsistency in the same service family creates confusion about the expected pattern.
**Impact:** Code review friction, potential for misuse. Callers don't know which pattern to expect.
**Recommendation:** Align on one pattern. Given PROJ-50's strict DI mandate, `ComponentService` should also require `registry_provider`. Update callers accordingly.
**Effort:** Simple

#### INFO: hasattr Checks for Scene/UI Attributes
**ID:** LEG-UI2-008
**Location:** `game/ui/services/screenshot_manager.py:147,153`
**Issue:** `capture_strategy_layer()` uses `hasattr(scene, 'ui')` and `hasattr(scene, 'build_queue_screen')` checks. These are defensive checks against varying scene interfaces.
**Impact:** Minor - these checks are appropriate for polymorphic scene handling where not all scenes have all UI elements.
**Recommendation:** Consider defining a Protocol for scenes that support screenshot capture, making the interface explicit. Low priority.
**Effort:** Simple

## Top 5 Priority Issues

1. **LEG-UI2-001 (CRITICAL)**: `BattleOrchestrator` is completely unused dead code - entire module (99 lines) should be removed or properly integrated. This is the clearest example of an incomplete migration.

2. **LEG-UI2-002 (MAJOR)**: Defensive `getattr` usage in `BattleUIService` masks potential bugs. Each should be audited to determine if it's truly needed or if it's hiding missing attributes.

3. **LEG-UI2-003 (MAJOR)**: Unused methods in `VehicleClassService` - dead code in an active class should be removed.

4. **LEG-UI2-004 (MINOR)**: Duplicated `is_modifier_allowed` logic between `ComponentService` and `ModifierService` - should delegate rather than duplicate.

5. **LEG-UI2-007 (MINOR)**: Inconsistent DI patterns across services in the same family - should align on strict DI per PROJ-50.
