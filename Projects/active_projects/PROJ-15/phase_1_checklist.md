# Phase 1: Singleton Aliases [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove get_instance() aliases and update all callers to use instance()

---

## Tasks

### Task 1.1: SpriteManager [Simple]
**File:** `game/ui/renderer/sprites.py`
**Tests:** `pytest tests/unit/ui/test_sprite_loading.py -v`

- [ ] `game/ui/renderer/sprites.py:47` - Delete line: `get_instance = instance`
- [ ] `game/app.py:111` - Change `SpriteManager.get_instance()` to `SpriteManager.instance()`
- [ ] `game/ui/screens/workshop_screen.py:114` - Change `SpriteManager.get_instance()` to `SpriteManager.instance()`
- [ ] `Tools/visual_test_sprites.py:19` - Change `SpriteManager.get_instance()` to `SpriteManager.instance()`
- [ ] `tests/unit/ui/test_sprite_loading.py:14` - Change `SpriteManager.get_instance()` to `SpriteManager.instance()`
- [ ] Verify: Run `pytest tests/unit/ui/test_sprite_loading.py -v` - all tests pass

**Notes:**

---

### Task 1.2: ShipThemeManager [Simple]
**File:** `game/simulation/ship_theme.py`
**Tests:** `pytest tests/unit/entities/test_ship_theme_logic.py tests/unit/ui/test_theme_discovery.py -v`

- [ ] `game/simulation/ship_theme.py:44` - Delete line: `get_instance = instance`
- [ ] `game/ui/screens/workshop_screen.py:117` - Change `ShipThemeManager.get_instance()` to `ShipThemeManager.instance()`
- [ ] `game/ui/renderer/game_renderer.py:42` - Change `ShipThemeManager.get_instance()` to `ShipThemeManager.instance()`
- [ ] `tests/unit/ui/test_theme_discovery.py:24` - Change to `ShipThemeManager.instance()`
- [ ] `tests/unit/entities/test_ship_theme_logic.py:19` - Change to `ShipThemeManager.instance()`
- [ ] `tests/unit/entities/test_ship_theme_logic.py:34` - Change to `ShipThemeManager.instance()`
- [ ] `tests/unit/entities/test_ship_theme_logic.py:35` - Change to `ShipThemeManager.instance()`
- [ ] `tests/unit/entities/test_ship_classes.py:19` - Change to `ShipThemeManager.instance()`
- [ ] `tests/unit/regressions/test_regressions.py:55` - Change to `ShipThemeManager.instance()`
- [ ] Verify: Run `pytest tests/unit/entities/test_ship_theme_logic.py tests/unit/ui/test_theme_discovery.py -v` - all tests pass

**Notes:**

---

### Task 1.3: ScreenshotManager [Simple]
**File:** `game/core/screenshot_manager.py`
**Tests:** `pytest tests/unit/test_screenshot_manager.py -v`

- [ ] `game/core/screenshot_manager.py:47` - Delete line: `get_instance = instance`
- [ ] `game/ui/screens/workshop_screen.py:88` - Change `ScreenshotManager.get_instance()` to `ScreenshotManager.instance()`
- [ ] `tests/unit/test_screenshot_manager.py:16` - Change to `ScreenshotManager.instance()`
- [ ] Verify: Run `pytest tests/unit/test_screenshot_manager.py -v` - all tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No remaining `get_instance()` calls: `grep -r "get_instance" game/ --include="*.py" | grep -v __pycache__`
- [ ] Run: `pytest tests/unit/ui/ tests/unit/entities/test_ship_theme_logic.py tests/unit/test_screenshot_manager.py -v`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
