# Legacy System Holdovers Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 22
- **Total Issues Found:** 6
- **Critical:** 0 | **Major:** 1 | **Minor:** 3 | **Info:** 2

## Findings

#### MAJOR: Unused Method - create_ai_for_ship in BattleOrchestrator
**ID:** LEG-UI2-001
**Location:** `game/ui/orchestration/battle_orchestrator.py:82-98`
**Issue:** The method `create_ai_for_ship()` is defined with a comment "for reinforcements" but is never called anywhere in the production codebase (game/ directory). It is only used in test files (`tests/unit/ui/test_battle_orchestrator.py` and `tests/unit/combat/test_battle_engine_core.py`). Only `create_ai_controllers()` is used in production.
**Impact:** ~17 lines of anticipatory/dead code. The docstring implies this was intended for a reinforcement feature that was never fully implemented in production code. Having tested but unused code creates uncertainty about whether the feature is incomplete or deprecated.
**Recommendation:** Either implement the reinforcement feature that uses this method in production code, or delete the method and its tests. If reinforcements are a planned feature, document this in a TODO or project plan.
**Effort:** Simple (delete) or Medium (implement feature)

#### MINOR: Comment References "legacy behavior" in ship_factory.py
**ID:** LEG-UI2-002
**Location:** `game/ui/services/ship_factory.py:15-16`
**Issue:** The docstring states "When registries is not provided, uses global RegistryManager (legacy behavior)." This indicates the code path is considered legacy but is still maintained as a fallback. Per PROJ-50 strict DI principles, callers should always provide registries explicitly.
**Impact:** Low - this is a soft fallback for DI, not a hard legacy pattern. However, inconsistency with `VehicleClassService` which makes the parameter required creates confusion about which pattern is preferred.
**Recommendation:** Consider auditing all callers of `ShipFactory` to ensure they pass `registry_provider` explicitly, then make the parameter required like `VehicleClassService` does.
**Effort:** Medium

#### MINOR: Excessive getattr() with Defaults in battle_ui_service.py
**ID:** LEG-UI2-003
**Location:** `game/ui/services/battle_ui_service.py:171-274`
**Issue:** Multiple `getattr()` calls with default values suggest uncertainty about object schemas:
- Line 171: `getattr(ship, 'id', id(ship))`
- Lines 196-197: `getattr(ship, 'crew_onboard', 0)`, `getattr(ship, 'crew_required', 0)`
- Lines 235-236: `getattr(comp, 'shots_fired', 0)`, `getattr(comp, 'shots_hit', 0)`
- Lines 250-274: Multiple getattr() calls on projectile objects

The comment on lines 195-196 explains that crew attributes are "dynamically set by ShipStatsCalculator, not in __init__", indicating a known schema inconsistency in Ship class.
**Impact:** Low - these are defensive patterns for DTO conversion. However, the defensive coding obscures whether attributes are truly optional or just poorly initialized.
**Recommendation:** Consider whether Ship/Component/Projectile classes should guarantee these attributes in `__init__` to avoid defensive coding in consumers. Document which attributes are guaranteed vs optional.
**Effort:** Medium

#### MINOR: ModifierEditorPanel Marked as Legacy
**ID:** LEG-UI2-004
**Location:** `game/ui/screens/builder/modifier_editor.py:1-7`
**Issue:** The file explicitly marks itself as "Legacy modifier editor panel" with a note "Consider migration to ModifierLogic for new code." However, the class is still actively used by `workshop_screen.py` (line 1014 imports it) and `builder_widgets.py` (line 42 imports ModifierEditorPanel).
**Impact:** Low - the code is functional but the "legacy" label creates uncertainty about whether it should be used or avoided. The recommended alternative (ModifierLogic) is already imported and used within the file itself.
**Recommendation:** Either complete the migration to remove ModifierEditorPanel usage entirely, or update the docstring to clarify that this is the current implementation (not actually legacy).
**Effort:** Medium (migration) or Simple (documentation fix)

#### INFO: Singleton Pattern Still in Use for Asset Managers
**ID:** LEG-UI2-005
**Location:** `game/ui/assets/ship_theme_manager.py:11`, `game/ui/services/screenshot_manager.py:11`, `game/ui/renderer/sprites.py:7`
**Issue:** Three classes use `SingletonMeta`: `ShipThemeManager`, `ScreenshotManager`, and `SpriteManager`. While the project has moved toward dependency injection in many areas (per PROJ-50), these asset-loading singletons remain.
**Impact:** Acceptable - these are stateful asset caches where singleton pattern is appropriate. The classes expose `.instance()` and `reset()` methods for testing.
**Recommendation:** No action required. These are legitimate use cases for singletons (global caches with expensive initialization). Document that asset managers are intentional exceptions to the DI preference.
**Effort:** N/A

#### INFO: hasattr() Check in Camera for Defensive Coding
**ID:** LEG-UI2-006
**Location:** `game/ui/renderer/camera.py:58`
**Issue:** The line `if hasattr(self.target, 'is_alive') and not self.target.is_alive:` uses hasattr() to check for an attribute before accessing it. This suggests the target object's type is not guaranteed to have `is_alive`.
**Impact:** Very low - this is acceptable defensive coding for duck typing, where the camera can follow any object with a `.position` attribute.
**Recommendation:** Consider documenting the protocol/interface that camera targets should implement, or use typing.Protocol to formalize the expected attributes.
**Effort:** Simple

## Top 5 Priority Issues

1. **LEG-UI2-001 (MAJOR):** Unused `create_ai_for_ship` method in BattleOrchestrator - tested but never called in production, indicating incomplete feature or dead code.

2. **LEG-UI2-004 (MINOR):** ModifierEditorPanel marked as "legacy" but still in active use - creates confusion about whether to use or avoid this code.

3. **LEG-UI2-002 (MINOR):** ship_factory.py documents "legacy behavior" for optional parameter - inconsistent with strict DI pattern used elsewhere.

4. **LEG-UI2-003 (MINOR):** Excessive getattr() defensive coding in battle_ui_service.py - indicates schema inconsistency in domain objects.

5. **LEG-UI2-005 (INFO):** Singleton pattern used for asset managers - acceptable but worth documenting as intentional exception.

## Verification Notes

The following issues from the previous sweep (2026-02-11) have been resolved:
- **LEG-UI2-001 (old):** Dead code `draw_hud` and `draw_bar` in game_renderer.py - **RESOLVED** (functions no longer exist, file is now 145 lines)
- **LEG-UI2-003 (old):** Unused `capture_step` debugging method - **RESOLVED** (method no longer exists)
- **LEG-UI2-004 (old):** Duplicate exception handlers in ShipIO - **RESOLVED** (exception handlers are now properly ordered without overlap)
- **LEG-UI2-006 (old):** Basic color constants (BLUE, RED, GREEN) - **RESOLVED** (constants no longer exist in colors.py)
- **LEG-UI2-007 (old):** Inconsistent ShipIO vs ShipIOAdapter usage - **RESOLVED** (all usage now goes through adapters)
