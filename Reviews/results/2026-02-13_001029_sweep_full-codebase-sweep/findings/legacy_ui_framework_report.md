# Legacy System Holdovers Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 25
- **Total Issues Found:** 10
- **Critical:** 0 | **Major:** 3 | **Minor:** 5 | **Info:** 2

## Findings

#### MAJOR: Dead Code - draw_hud and draw_bar Functions Never Called
**ID:** LEG-UI2-001
**Location:** `game/ui/renderer/game_renderer.py:145-225`
**Issue:** The functions `draw_hud()` (lines 153-225) and `draw_bar()` (lines 145-150) are defined but never imported or called anywhere in the codebase. The only import from this module is `draw_ship` and `LAYER_COLORS`.
**Impact:** ~80 lines of dead code creating maintenance burden and confusion about which rendering functions are authoritative. There's a separate `draw_hud` method in `battle_screen.py:571` that IS used.
**Recommendation:** Delete both functions since they are unused. If battle HUD rendering is needed, the `battle_screen.py` implementation is the canonical one.
**Effort:** Simple

#### MAJOR: Unused Method - create_ai_for_ship in BattleOrchestrator
**ID:** LEG-UI2-002
**Location:** `game/ui/orchestration/battle_orchestrator.py:82-98`
**Issue:** The method `create_ai_for_ship()` is defined with a comment "for reinforcements" but is never called anywhere in the codebase. Only `create_ai_controllers()` is used.
**Impact:** ~17 lines of anticipatory/dead code. The docstring implies this was intended for a reinforcement feature that was never implemented.
**Recommendation:** Delete the method. If a reinforcements feature is implemented, the method can be recreated at that time.
**Effort:** Simple

#### MAJOR: Unused Method - capture_step in ScreenshotManager
**ID:** LEG-UI2-003
**Location:** `game/ui/services/screenshot_manager.py:118-124`
**Issue:** The method `capture_step()` is defined for "debugging draw order" but is never called anywhere in the codebase. Only `capture()` and `capture_strategy_layer()` are used.
**Impact:** Dead code intended for debugging that was never used or was removed from call sites but left in the class.
**Recommendation:** Delete the method.
**Effort:** Simple

#### MINOR: Duplicate Exception Handlers in ShipIO
**ID:** LEG-UI2-004
**Location:** `game/ui/services/ship_io.py:71-82, 124-129`
**Issue:** Both `save_ship()` and `load_ship()` methods have duplicate exception handlers. For example in `save_ship()`:
- Line 74: `except OSError as e:`
- Line 80: `except (OSError, PermissionError) as e:` (OSError is caught twice)
Similarly in `load_ship()`:
- Line 125: `except OSError as e:`
- Line 127: `except (OSError, PermissionError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` (catches exceptions already handled above)
**Impact:** The second catch block is unreachable for exception types already caught above. This suggests incomplete cleanup after refactoring.
**Recommendation:** Remove duplicate exception handlers, keeping only the more specific ones.
**Effort:** Simple

#### MINOR: Comment References "legacy behavior" in ship_factory.py
**ID:** LEG-UI2-005
**Location:** `game/ui/services/ship_factory.py:15-16`
**Issue:** The docstring states "When registries is not provided, uses global RegistryManager (legacy behavior)." This indicates the code path is considered legacy but is still maintained as a fallback.
**Impact:** Low - this is a soft fallback for DI, not a hard legacy pattern. However, per PROJ-50 strict DI principles, callers should always provide registries.
**Recommendation:** Consider auditing all callers of `ShipFactory` to ensure they pass `registry_provider` explicitly, then make the parameter required like `VehicleClassService` does.
**Effort:** Medium

#### MINOR: Basic Color Constants (BLUE, RED, GREEN) Minimally Used
**ID:** LEG-UI2-006
**Location:** `game/ui/colors.py:9-11`
**Issue:** The constants `BLUE`, `RED`, and `GREEN` are defined but only imported by one file (`game/ui/screens/test_lab/screen.py`). The project has moved to the `COLORS` dictionary pattern for theming.
**Impact:** Minimal usage suggests these are legacy holdovers from before the COLORS dictionary pattern was established.
**Recommendation:** Migrate the single usage to inline color tuples or COLORS dictionary, then remove the unused constants from colors.py.
**Effort:** Simple

#### MINOR: ShipIOAdapter vs ShipIO Direct Access
**ID:** LEG-UI2-007
**Location:** `game/ui/services/ship_io_adapter.py` and `game/ui/services/ship_io.py`
**Issue:** `ShipIOAdapter` exists as a facade over `ShipIO`, but the builder module (`game/ui/screens/builder/main.py:1057-1115`) directly calls `ShipIO.save_ship()` and `ShipIO.load_ship()`, bypassing the adapter. Only `workshop_screen.py` and `workshop_data_reloader.py` use the adapter.
**Impact:** Inconsistent usage pattern - some UI code uses the adapter while other UI code directly accesses the underlying class.
**Recommendation:** Either migrate all callers to use `ShipIOAdapter`, or remove the adapter if direct access is preferred.
**Effort:** Medium

#### MINOR: Excessive getattr() with Defaults in battle_ui_service.py
**ID:** LEG-UI2-008
**Location:** `game/ui/services/battle_ui_service.py:171-274`
**Issue:** Multiple `getattr()` calls with default values suggest uncertainty about object schemas:
- Line 171: `getattr(ship, 'id', id(ship))`
- Lines 196-197: `getattr(ship, 'crew_onboard', 0)`, `getattr(ship, 'crew_required', 0)`
- Lines 235-236: `getattr(comp, 'shots_fired', 0)`, `getattr(comp, 'shots_hit', 0)`
- Lines 255-274: Multiple getattr() calls on projectile objects
**Impact:** Low - these are defensive patterns for DTO conversion. However, the comment on lines 195-196 explains that crew attributes are "dynamically set by ShipStatsCalculator, not in __init__", indicating a known schema inconsistency.
**Recommendation:** Consider whether Ship/Component/Projectile classes should guarantee these attributes in __init__ to avoid defensive coding in consumers.
**Effort:** Medium

#### INFO: Singleton Pattern Still in Use for Asset Managers
**ID:** LEG-UI2-009
**Location:** `game/ui/assets/ship_theme_manager.py:11`, `game/ui/services/screenshot_manager.py:11`, `game/ui/renderer/sprites.py:7`
**Issue:** Three classes use `SingletonMeta`: `ShipThemeManager`, `ScreenshotManager`, and `SpriteManager`. While the project has moved toward dependency injection in many areas, these asset-loading singletons remain.
**Impact:** Acceptable for now - these are stateful asset caches where singleton pattern is appropriate. The classes expose `.instance()` and `reset()` methods for testing.
**Recommendation:** No immediate action. These are legitimate use cases for singletons (global caches with expensive initialization). Document that asset managers are intentional exceptions to the DI preference.
**Effort:** N/A

#### INFO: Anticipatory Code in _CONTEXT_OVERLAP
**ID:** LEG-UI2-010
**Location:** `game/ui/services/input_mapper.py:43-51`
**Issue:** The `_CONTEXT_OVERLAP` dictionary defines context overlap rules for keybinding conflict detection. Some contexts like `build_queue`, `fleet_orders`, and `transfer` are defined but only map to themselves, suggesting they were added anticipating features.
**Impact:** Minimal - these are data-driven mappings that don't create code bloat.
**Recommendation:** Document the intended behavior for these contexts or remove unused ones if the features were never implemented.
**Effort:** Simple

## Top 5 Priority Issues

1. **LEG-UI2-001 (MAJOR):** Dead code `draw_hud` and `draw_bar` in game_renderer.py - ~80 lines of unused code that could mislead developers about the rendering architecture.

2. **LEG-UI2-002 (MAJOR):** Unused `create_ai_for_ship` method - anticipatory code for unimplemented feature creates confusion about API surface.

3. **LEG-UI2-004 (MINOR):** Duplicate exception handlers in ShipIO - suggests incomplete refactoring cleanup, could mask bugs.

4. **LEG-UI2-007 (MINOR):** Inconsistent ShipIO vs ShipIOAdapter usage - architectural inconsistency violates the principle that adapters should be the exclusive interface.

5. **LEG-UI2-003 (MAJOR):** Unused `capture_step` debugging method - dead code from debugging session that was never cleaned up.
