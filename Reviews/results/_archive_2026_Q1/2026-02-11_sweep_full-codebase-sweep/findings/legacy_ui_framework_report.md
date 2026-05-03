# Legacy System Holdovers Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework (game/ui/ root files, services/, renderer/, interfaces/, orchestration/, assets/, components/, utils/)
- **Files Scanned:** 18
- **Total Issues Found:** 12
- **Critical:** 1 | **Major:** 5 | **Minor:** 4 | **Info:** 2

## Findings

#### CRITICAL: Legacy widgets.py Module - Entire File is Dead Code
**ID:** LEG-UI2-001
**Location:** `game/ui/widgets.py:1-102`
**Issue:** The entire `widgets.py` module containing `Button`, `Label`, and `Slider` classes is dead production code. The file is explicitly labeled with the comment `# --- Legacy UI Widgets ---` (line 3). These classes are never imported or used by any production code -- the only imports are in test files (`test_ui_widgets.py`, `test_ui_imports.py`) and UML diagram outputs. The project has migrated to pygame_gui widgets throughout the UI.
**Impact:** 102 lines of dead legacy code that creates confusion about which widget system is authoritative. New developers may mistakenly use these instead of the actual pygame_gui-based widgets. The `# --- Legacy UI Widgets ---` comment explicitly acknowledges this is legacy code that was never removed.
**Recommendation:** Delete `game/ui/widgets.py` entirely and remove the test file `tests/unit/ui/test_ui_widgets.py`. Update `tests/unit/ui/test_ui_imports.py` to remove the widgets import test.
**Effort:** Simple

#### MAJOR: SpriteManager Atlas Fallback - Dead Code Path for Non-Existent BMP File
**ID:** LEG-UI2-002
**Location:** `game/ui/renderer/sprites.py:40-43, 97-127`
**Issue:** The `load_sprites()` method contains a three-tier fallback: (1) Tiles subdirectory, (2) Components directory, (3) old BMP atlas file at `assets/Images/Components.bmp`. The atlas file does NOT exist on disk (`Components.bmp` is confirmed absent). The entire atlas fallback code path (`_load_atlas_file`, `_slice_sprites`, the `self.atlas` attribute, and `self.tile_size` attribute) is dead code -- approximately 35 lines including the methods and supporting state. These methods are never called from any other location.
**Impact:** Dead fallback code path for a removed asset format. The `tile_size = 36` constant and `self.atlas = None` initialization serve no purpose. The `import traceback` on line 113 is only used in the atlas path.
**Recommendation:** Remove `_load_atlas_file()`, `_slice_sprites()`, the atlas fallback branch in `load_sprites()`, the `self.atlas` attribute, and the `self.tile_size` attribute. Simplify `load_sprites()` to only handle directory-based loading.
**Effort:** Simple

#### MAJOR: draw_hud() and draw_bar() in game_renderer.py - Never Called by Production Code
**ID:** LEG-UI2-003
**Location:** `game/ui/renderer/game_renderer.py:145-225`
**Issue:** The `draw_hud()` function (lines 153-225) and `draw_bar()` helper (lines 145-151) are never imported or called by any production code. The only import is in the test file `test_rendering_logic.py`. The `battle_screen.py` imports only `draw_ship` from this module. The battle HUD rendering has been replaced by the `ship_stats_renderer.py` module in the panels package (functions like `draw_ship_info_header`, `draw_ship_vitals`, `draw_ship_resources`, `draw_ship_combat_stats`, `draw_ship_weapons`, `draw_ship_components`). The old `draw_hud` also creates fonts (`SysFont`) on every call -- a performance antipattern. Additionally, `ResourceType` is imported on line 9 but only used by `draw_hud`/`draw_bar`, so the import would also become dead.
**Impact:** ~80 lines of dead rendering code alongside the active `draw_ship()` function. Creates confusion about which HUD rendering code is authoritative. The `ResourceType` import is only needed for this dead code.
**Recommendation:** Delete `draw_hud()` and `draw_bar()` from `game_renderer.py`. Remove the `ResourceType` import. Update `test_rendering_logic.py` to remove tests for these dead functions.
**Effort:** Simple

#### MAJOR: BattleOrchestrator Never Used in Production Code
**ID:** LEG-UI2-004
**Location:** `game/ui/orchestration/battle_orchestrator.py:1-99`, `game/ui/orchestration/__init__.py:1-5`
**Issue:** The `BattleOrchestrator` class and its entire `game/ui/orchestration/` package are never imported by any production game code. No file in `game/` imports from `game.ui.orchestration`. The only consumers are test files (`test_battle_orchestrator.py`, `test_battle_engine_core.py`). The `battle_screen.py` does not use it, and `app.py` does not use it. The `BattleEngine` docstrings reference `BattleOrchestrator` in comments but the actual production battle setup code follows a different path.
**Impact:** An entire package (2 files, ~100 lines) that exists only for test usage. The orchestrator pattern may have been superseded by direct AI controller creation in the battle setup flow.
**Recommendation:** Investigate whether `BattleOrchestrator` is truly unused in production. If confirmed dead, either delete the package or move the utility into the test helpers where it is actually used. Update `BattleEngine` docstrings that reference it.
**Effort:** Medium

#### MAJOR: show_overlay Hack - State Passed via Dynamic Attribute on Camera
**ID:** LEG-UI2-005
**Location:** `game/ui/renderer/game_renderer.py:78`
**Issue:** The `draw_ship()` function reads `show_overlay` from the Camera object using `getattr(camera, 'show_overlay', False)` -- a defensive access for a dynamically monkey-patched attribute. The `battle_screen.py` (line 547) sets this via `self.camera.show_overlay = self.ui.show_overlay` with an explicit comment: `# Hack to pass state to renderer`. The Camera class has no `show_overlay` attribute defined. This is a cross-cutting concern passed through an ad-hoc mechanism rather than a proper parameter.
**Impact:** The `getattr` guard masks the fact that `show_overlay` is not part of Camera's interface. This pattern is fragile and obscures the data flow between the battle screen and renderer.
**Recommendation:** Add `show_overlay` as a proper parameter to the `draw_ship()` function, or add it as a formal Camera attribute. Remove the monkey-patching in `battle_screen.py`.
**Effort:** Simple

#### MAJOR: draw_ship() Uses Singleton ShipThemeManager.instance() Inside Render Loop
**ID:** LEG-UI2-006
**Location:** `game/ui/renderer/game_renderer.py:46-48`
**Issue:** The `draw_ship()` function calls `ShipThemeManager.instance()` on every invocation (every ship, every frame). This is a singleton access pattern that the project has been migrating away from in favor of dependency injection. The import `from game.ui.assets import ShipThemeManager` is done at module level, but the `.instance()` call at line 47 is a runtime singleton lookup. Other parts of the codebase (e.g., builder, workshop) store the instance once during initialization via DI.
**Impact:** Per-frame singleton access in a hot loop. While not causing bugs, this is inconsistent with the DI migration direction and creates an implicit dependency that cannot be injected for testing.
**Recommendation:** Pass the theme manager as a parameter to `draw_ship()` or inject it during renderer initialization. The caller (`battle_screen.py`) already has access to the theme manager.
**Effort:** Medium

#### MINOR: Unnecessary hasattr Guard on LayerType.value in BattleUIService
**ID:** LEG-UI2-007
**Location:** `game/ui/services/battle_ui_service.py:142`
**Issue:** The line `layer_name = layer_type.value if hasattr(layer_type, 'value') else str(layer_type)` contains a defensive `hasattr` check for `.value` on `LayerType` enum instances. Since `ship.layers` is always `Dict[LayerType, LayerData]` (confirmed in `ship.py` line 342), `layer_type` is always a `LayerType` enum and always has `.value`. The `else str(layer_type)` branch is dead code.
**Impact:** Minor confusion about whether non-enum keys are possible. A reader might wonder what non-enum layer types exist.
**Recommendation:** Replace with `layer_name = layer_type.value` directly.
**Effort:** Simple

#### MINOR: getattr(ship, 'id', id(ship)) - Ship.id Never Exists
**ID:** LEG-UI2-008
**Location:** `game/ui/services/battle_ui_service.py:158`
**Issue:** The line `ship_id = str(getattr(ship, 'id', id(ship)))` uses a defensive `getattr` to access `ship.id` with a fallback to Python's `id()`. However, the `Ship` class never defines an `id` attribute (confirmed by searching `ship.py`). This means the fallback `id(ship)` is always used, making the `getattr` check pointless. The same pattern appears for projectiles at line 242.
**Impact:** Minor: creates a false impression that some ships might have an `.id` attribute. The `id(ship)` Python object identity is used as the ship identifier, which is adequate but the code obscures this.
**Recommendation:** Replace with `ship_id = str(id(ship))` or, better, add a proper `id` attribute to the `Ship` class.
**Effort:** Simple

#### MINOR: Excessive getattr Usage in _convert_projectile for Standard Attributes
**ID:** LEG-UI2-009
**Location:** `game/ui/services/battle_ui_service.py:237-257`
**Issue:** The `_convert_projectile()` method uses `getattr()` with defaults for 10 different projectile attributes (`target`, `id`, `color`, `radius`, `hp`, `max_hp`, `status`, `endurance`, `max_endurance`, `max_speed`). While some defensive access may be appropriate for attributes set dynamically (like `shots_fired` on components), this many `getattr` calls on a single object type suggests the projectile interface is not well-defined. These may be leftover defensive guards from when projectiles had varying structures.
**Impact:** Makes it unclear which projectile attributes are guaranteed vs. optional. Obscures the actual projectile interface.
**Recommendation:** Verify which attributes are always present on projectiles and access them directly. Use `getattr` only for truly optional attributes.
**Effort:** Medium

#### MINOR: interfaces/__init__.py Re-exports Never Used Through Package
**ID:** LEG-UI2-010
**Location:** `game/ui/interfaces/__init__.py:1-25`
**Issue:** The `__init__.py` re-exports `IBattleUI`, `ShipDTO`, `ComponentDTO`, `ProjectileDTO`, `BeamDTO`, and `ResourceDTO` from `battle_ui.py`. However, every consumer in the codebase imports directly from `game.ui.interfaces.battle_ui` rather than from `game.ui.interfaces`. The re-exports exist but are never used through the package shortcut.
**Impact:** Minor inconsistency. The re-exports are not harmful but serve no purpose since no caller uses them.
**Recommendation:** Either update callers to use the package-level import (preferred for cleaner imports) or remove the re-exports to avoid dead code. Preferably the former.
**Effort:** Simple

#### INFO: SpriteManager and ShipThemeManager Use SingletonMeta Pattern
**ID:** LEG-UI2-011
**Location:** `game/ui/renderer/sprites.py:7`, `game/ui/assets/ship_theme_manager.py:11`
**Issue:** Both `SpriteManager` and `ShipThemeManager` use the `SingletonMeta` metaclass pattern. While the project has been migrating toward dependency injection (PROJ-50), these two managers remain as singletons with `.instance()` access. Their callers access them as `SpriteManager.instance()` and `ShipThemeManager.instance()` throughout the UI layer.
**Impact:** This is a known aging pattern. The singletons work correctly but are inconsistent with the DI direction. Both classes have `clear()`/`reset()` methods for test isolation.
**Recommendation:** Consider migrating to DI in a future project. Low priority since the current approach works and has test isolation support.
**Effort:** Complex

#### INFO: game/ui/__init__.py Purpose is xdist Race Prevention, Not Public API
**ID:** LEG-UI2-012
**Location:** `game/ui/__init__.py:1-27`
**Issue:** The `__init__.py` imports `sprites`, `camera`, `game_renderer`, `battle_screen`, `battle_ui`, `battle_panels`, and `builder_widgets` and exports them in `__all__`. However, no code anywhere does `from game.ui import ...` to use these exports. The docstring explains the imports exist to "prevent pytest-xdist race conditions" and ensure consistent initialization. This is infrastructure code, not a public API.
**Impact:** None functionally. The purpose is documented. However, the `__all__` export list and "Export for convenience" comment are misleading since nothing uses these as convenience exports.
**Recommendation:** Remove the `__all__` list and the "Export for convenience" comment. Keep the imports with only the xdist race prevention explanation.
**Effort:** Simple

## Top 5 Priority Issues

1. **LEG-UI2-001 (CRITICAL):** Delete `widgets.py` -- 102 lines of explicitly labeled legacy code with zero production callers. Cleanest possible cleanup.

2. **LEG-UI2-003 (MAJOR):** Remove dead `draw_hud()` and `draw_bar()` from `game_renderer.py` -- ~80 lines superseded by the panels/`ship_stats_renderer.py` system. The `ResourceType` import becomes dead too.

3. **LEG-UI2-002 (MAJOR):** Remove atlas fallback code from `sprites.py` -- the BMP atlas file no longer exists, making the entire `_load_atlas_file`/`_slice_sprites` code path unreachable (~35 lines).

4. **LEG-UI2-004 (MAJOR):** Investigate and potentially remove `BattleOrchestrator` -- entire package (100 lines) with no production callers. May be test-only utility.

5. **LEG-UI2-005 (MAJOR):** Fix the `show_overlay` hack -- monkey-patched Camera attribute with defensive `getattr` in the renderer. Simple fix with clear improvement to code clarity.
