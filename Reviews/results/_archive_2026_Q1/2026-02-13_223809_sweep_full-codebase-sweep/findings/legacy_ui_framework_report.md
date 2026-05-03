# Legacy System Holdovers Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 22
- **Total Issues Found:** 5
- **Critical:** 0 | **Major:** 2 | **Minor:** 2 | **Info:** 1

## Scan Scope
Files scanned:
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
- `game/ui/services/battle_factories.py`
- `game/ui/services/battle_ui_service.py`
- `game/ui/services/input_mapper.py`
- `game/ui/services/screenshot_manager.py`
- `game/ui/services/ship_io.py`
- `game/ui/renderer/__init__.py`
- `game/ui/renderer/camera.py`
- `game/ui/renderer/game_renderer.py`
- `game/ui/renderer/sprites.py`
- `game/ui/interfaces/__init__.py`
- `game/ui/interfaces/battle_ui.py`
- `game/ui/orchestration/__init__.py`
- `game/ui/orchestration/battle_orchestrator.py`
- `game/ui/assets/__init__.py`
- `game/ui/assets/ship_theme_manager.py`

## Findings

#### MAJOR: BattleOrchestrator Class Is Unused In Game Code
**ID:** LEG-UI2-001
**Location:** `game/ui/orchestration/battle_orchestrator.py:32-99`
**Issue:** The `BattleOrchestrator` class is defined and exported but never instantiated in any game code. It is only used in test files (`tests/unit/combat/test_battle_engine_core.py`, `tests/unit/ui/test_battle_orchestrator.py`).
**Impact:** Dead code that creates maintenance burden. The class was created during PROJ-17 for UI-layer battle orchestration but the battle screen uses a different approach (`BattleController` with `AIControllerFactory` injection via `battle_factories.py`).
**Recommendation:** Delete `game/ui/orchestration/` directory entirely. The modern approach uses `BattleController` with factory injection from `game/ui/services/battle_factories.py`.
**Effort:** Simple

#### MAJOR: IBattleUI Protocol Is Exported But Never Used For Type Checking
**ID:** LEG-UI2-002
**Location:** `game/ui/interfaces/battle_ui.py:176-244`
**Issue:** The `IBattleUI` Protocol class is defined and exported through `game/ui/interfaces/__init__.py` but is never used as a type hint anywhere in the codebase. `BattleUIService` does satisfy the protocol, but no code uses `IBattleUI` for type annotations.
**Impact:** The Protocol adds cognitive overhead without providing static type checking benefits. If the interface is intended for DI/mocking, it should be used in type hints.
**Recommendation:** Either use `IBattleUI` in type hints (e.g., `def __init__(self, battle_ui: IBattleUI)`) or remove the Protocol class and keep only the DTOs.
**Effort:** Simple

#### MINOR: WHITE and BLACK Color Constants Are Dead Code
**ID:** LEG-UI2-003
**Location:** `game/ui/colors.py:7-8`
**Issue:** The `WHITE` and `BLACK` color constants were moved from `game/core/constants.py` to `game/ui/colors.py` in PROJ-113, but no code imports or uses these constants. The migration was incomplete - the constants were moved but call sites were never updated, and now no code references them.
**Impact:** Small amount of dead code (~2 lines). Minor cleanup opportunity.
**Recommendation:** Delete the `WHITE` and `BLACK` constant definitions from `game/ui/colors.py`.
**Effort:** Simple

#### MINOR: get_visible_bounding_box Function Has No External Callers
**ID:** LEG-UI2-004
**Location:** `game/ui/utils.py:97-113`
**Issue:** The `get_visible_bounding_box` function is only called internally by `scale_image_by_visible_portion` in the same file. It is not exported in `__all__` and has no external callers in the codebase. The function exists as a helper that could be inlined or made explicitly internal with underscore prefix.
**Impact:** Minor dead code pattern - the function works but could be private.
**Recommendation:** Either rename to `_get_visible_bounding_box` to indicate internal use, or inline into `scale_image_by_visible_portion` if the logic is simple enough.
**Effort:** Simple

#### INFO: Singleton Pattern Still Used in UI Layer
**ID:** LEG-UI2-005
**Location:** Multiple files (ship_theme_manager.py, sprites.py, screenshot_manager.py)
**Issue:** The UI layer uses `SingletonMeta` for `ShipThemeManager`, `SpriteManager`, and `ScreenshotManager`. While the project moved toward dependency injection in many areas, these singletons remain for valid reasons (they manage global caches and require consistent access across the UI).
**Impact:** Not a legacy holdover - these are intentional singletons for resource management. They have proper `reset()` and `clear()` methods for test isolation.
**Recommendation:** No action needed. Document as accepted pattern for UI resource managers.
**Effort:** N/A

## Top 5 Priority Issues

1. **LEG-UI2-001 (MAJOR):** Delete unused `BattleOrchestrator` class and `game/ui/orchestration/` directory - it was superseded by `battle_factories.py` pattern.

2. **LEG-UI2-002 (MAJOR):** Either use `IBattleUI` Protocol for type hints or remove it - currently provides no value as an unused interface definition.

3. **LEG-UI2-003 (MINOR):** Delete dead `WHITE` and `BLACK` color constants from `game/ui/colors.py`.

4. **LEG-UI2-004 (MINOR):** Make `get_visible_bounding_box` private with underscore prefix or inline it.

5. **LEG-UI2-005 (INFO):** No action - singleton usage is intentional for resource managers.

## Notes

The UI framework layer is generally clean with minimal legacy holdovers. The main issues are:
- One complete module (`orchestration/`) that was superseded by a different approach
- One Protocol interface that was created for extensibility but never used
- Two orphaned color constants from an incomplete migration

All identified issues are low-risk and can be safely cleaned up without impacting functionality.
