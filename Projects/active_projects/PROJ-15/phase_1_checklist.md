# Phase 1: Singleton Aliases [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove get_instance() aliases and update all callers to use instance()

---

## Tasks

### Task 1.1: SpriteManager [Simple]
**File:** `game/ui/renderer/sprites.py`
**Tests:** `pytest tests/unit/ui/test_sprite_loading.py -v`

- [x] `game/ui/renderer/sprites.py:47` - Delete line: `get_instance = instance`
- [x] `game/app.py:116` - Change `SpriteManager.get_instance()` to `SpriteManager.instance()`
- [x] `game/ui/screens/workshop_screen.py:114` - Change `SpriteManager.get_instance()` to `SpriteManager.instance()`
- [x] `Tools/visual_test_sprites.py:19` - FILE DOES NOT EXIST (stale reference)
- [x] `tests/unit/ui/test_sprite_loading.py:14` - Change `SpriteManager.get_instance()` to `SpriteManager.instance()`
- [x] Verify: Run `pytest tests/unit/ui/test_sprite_loading.py -v` - all tests pass

**Notes:** Tools/visual_test_sprites.py does not exist - removed from checklist.

---

### Task 1.2: ShipThemeManager [Simple]
**File:** `game/simulation/ship_theme.py`
**Tests:** `pytest tests/unit/entities/test_ship_theme_logic.py tests/unit/ui/test_theme_discovery.py -v`

- [x] `game/simulation/ship_theme.py:44` - Delete line: `get_instance = instance`
- [x] `game/ui/screens/workshop_screen.py:117` - Change `ShipThemeManager.get_instance()` to `ShipThemeManager.instance()`
- [x] `game/ui/renderer/game_renderer.py:42` - Change `ShipThemeManager.get_instance()` to `ShipThemeManager.instance()`
- [x] `tests/unit/ui/test_theme_discovery.py:24` - Change to `ShipThemeManager.instance()`
- [x] `tests/unit/entities/test_ship_theme_logic.py:19` - Change to `ShipThemeManager.instance()`
- [x] `tests/unit/entities/test_ship_theme_logic.py:34` - Change to `ShipThemeManager.instance()`
- [x] `tests/unit/entities/test_ship_theme_logic.py:35` - Change to `ShipThemeManager.instance()`
- [x] `tests/unit/entities/test_ship_classes.py:19` - Change to `ShipThemeManager.instance()`
- [x] `tests/unit/regressions/test_regressions.py:55` - Change to `ShipThemeManager.instance()`
- [x] Verify: Run `pytest tests/unit/entities/test_ship_theme_logic.py tests/unit/ui/test_theme_discovery.py -v` - all tests pass

**Notes:** Also fixed `tests/unit/ui/test_rendering_logic.py:64` which had `mock_theme_mgr_cls.get_instance.return_value` - updated to `instance`.

---

### Task 1.3: ScreenshotManager [Simple]
**File:** `game/core/screenshot_manager.py`
**Tests:** `pytest tests/unit/test_screenshot_manager.py -v`

- [x] `game/core/screenshot_manager.py:47` - Delete line: `get_instance = instance`
- [x] `game/ui/screens/workshop_screen.py:88` - Change `ScreenshotManager.get_instance()` to `ScreenshotManager.instance()`
- [x] `tests/unit/test_screenshot_manager.py:16` - Change to `ScreenshotManager.instance()`
- [x] Verify: Run `pytest tests/unit/test_screenshot_manager.py -v` - all tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] No remaining `get_instance()` calls: `grep -r "get_instance" game/ --include="*.py" | grep -v __pycache__`
- [x] Run: `pytest tests/unit/ui/ tests/unit/entities/test_ship_theme_logic.py tests/unit/test_screenshot_manager.py -v`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
