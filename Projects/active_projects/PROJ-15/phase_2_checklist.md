# Phase 2: Singleton Accessor Aliases [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove `get_instance = instance` aliases and update callers to use `instance()`

---

## Tasks

### Task 2.1: ScreenshotManager [Simple]
**File:** `game/core/screenshot_manager.py`
**Tests:** `pytest tests/unit/test_screenshot_manager.py -v`

- [x] Update `game/ui/screens/workshop_screen.py` (line 88):
  - Change `ScreenshotManager.get_instance()` to `ScreenshotManager.instance()`
- [x] Update `tests/unit/test_screenshot_manager.py` (line 16):
  - Change `ScreenshotManager.get_instance()` to `ScreenshotManager.instance()`
- [x] Delete alias in `game/core/screenshot_manager.py` (line 47):
  - Remove `get_instance = instance`
- [x] Verify: Run tests - should pass (3 passed)

**Notes:** All 3 tests pass.

---

### Task 2.2: ShipThemeManager [Simple]
**File:** `game/simulation/ship_theme.py`
**Tests:** `pytest tests/unit/entities/test_ship_theme_logic.py tests/unit/entities/test_ship_classes.py tests/unit/ui/test_theme_discovery.py tests/unit/regressions/test_regressions.py -v`

**Production code (2 files):**
- [x] Update `game/ui/renderer/game_renderer.py` (line 42):
  - Change `ShipThemeManager.get_instance()` to `ShipThemeManager.instance()`
- [x] Update `game/ui/screens/workshop_screen.py` (line 117):
  - Change `ShipThemeManager.get_instance()` to `ShipThemeManager.instance()`

**Test code (4 files):**
- [x] Update `tests/unit/ui/test_theme_discovery.py` (line 24):
  - Change to `ShipThemeManager.instance()`
- [x] Update `tests/unit/regressions/test_regressions.py` (line 55):
  - Change to `ShipThemeManager.instance()`
- [x] Update `tests/unit/entities/test_ship_theme_logic.py` (lines 19, 34, 35):
  - Change all `ShipThemeManager.get_instance()` to `ShipThemeManager.instance()`
- [x] Update `tests/unit/entities/test_ship_classes.py` (line 19):
  - Change to `ShipThemeManager.instance()`

**Delete alias:**
- [x] Delete alias in `game/simulation/ship_theme.py` (line 44):
  - Remove `get_instance = instance`
- [x] Verify: Run tests - should pass (14 passed)

**Notes:** All 14 tests pass.

---

### Task 2.3: SpriteManager [Simple]
**File:** `game/ui/renderer/sprites.py`
**Tests:** `pytest tests/unit/ui/test_sprite_loading.py -v`

- [x] Update `game/app.py` (line 111):
  - Change `SpriteManager.get_instance()` to `SpriteManager.instance()`
- [x] Update `game/ui/screens/workshop_screen.py` (line 114):
  - Change `SpriteManager.get_instance()` to `SpriteManager.instance()`
- [x] Update `tests/unit/ui/test_sprite_loading.py` (line 14):
  - Change to `SpriteManager.instance()`
- [x] Delete alias in `game/ui/renderer/sprites.py` (line 47):
  - Remove `get_instance = instance`
- [x] Verify: Run tests - should pass (2 passed)

**Notes:** All 2 tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/ -v --tb=short` - all pass (13 tests passed for Phase 2 related tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
