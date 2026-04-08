# Phase 4: Migrate UI Singletons

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-258 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate 5 UI-layer singletons to ApplicationContext: AssetManager, SpriteManager, ShipThemeManager, ScreenshotManager, GameSettings. One singleton per commit.

---

## Tasks

### Task 4.1: Migrate AssetManager [Medium]
**Singleton file:** `game/assets/asset_manager.py`
**Production .instance() call sites (3 + 1 convenience function):**
- `game/assets/asset_manager.py:334` -- `get_asset_manager()` convenience function returns `AssetManager.instance()`
- `game/ui/screens/planet_data_source.py:196` -- `AssetManager.instance()`
- `game/ui/screens/planet_selection_window.py:139` -- `AssetManager.instance()`
- `game/ui/screens/star_data_source.py:107` -- `AssetManager.instance()`

**Test files that reset AssetManager:**
- `tests/unit/assets/test_asset_manager_resolutions.py` -- 2 `.reset()` calls (setup/teardown)
- `tests/unit/core/test_asset_manager.py` -- 4 `.reset()` calls (setup/teardown)

**TDD steps:**
- [ ] Write test: AssetManager can be instantiated without SingletonMeta
- [ ] Write test: ApplicationContext provides AssetManager instance
- [ ] Remove `metaclass=SingletonMeta` from AssetManager class definition
- [ ] Update or remove `get_asset_manager()` convenience function
- [ ] Update `game/ui/screens/planet_data_source.py` to receive AssetManager via DI
- [ ] Update `game/ui/screens/planet_selection_window.py` to receive AssetManager via DI
- [ ] Update `game/ui/screens/star_data_source.py` to receive AssetManager via DI
- [ ] Update `game/context.py` `create_production()` to create AssetManager directly
- [ ] Update `tests/unit/assets/test_asset_manager_resolutions.py` to use fresh instances
- [ ] Update `tests/unit/core/test_asset_manager.py` to use fresh instances
- [ ] Run: `pytest tests/unit/assets/ tests/unit/core/test_asset_manager.py -v` -- all pass
- [ ] Run: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass
- [ ] Commit: "refactor: migrate AssetManager from singleton to DI via ApplicationContext"

**Notes:** AssetManager loads star metadata in `__init__`. The `create_test()` factory should create an AssetManager that skips file I/O or uses test paths.

---

### Task 4.2: Migrate SpriteManager [Medium]
**Singleton file:** `game/ui/renderer/sprites.py`
**Production .instance() call sites (2):**
- `game/app.py:151` -- `SpriteManager.instance()` for sprite loading
- `game/ui/screens/workshop_screen.py:109` -- `SpriteManager.instance()`

**Test files that reset SpriteManager:**
- `tests/unit/ui/test_sprite_loading.py` -- 1 `.reset()` call
- `tests/unit/ui/test_sprites.py` -- 10 `.reset()` calls (setup/teardown)

**TDD steps:**
- [ ] Write test: SpriteManager can be instantiated without SingletonMeta
- [ ] Write test: ApplicationContext provides SpriteManager instance
- [ ] Remove `metaclass=SingletonMeta` from SpriteManager class definition
- [ ] Update `game/app.py` to use `ctx.sprite_manager` instead of `SpriteManager.instance()`
- [ ] Update `game/ui/screens/workshop_screen.py` to receive SpriteManager via DI (constructor or context)
- [ ] Update `game/context.py` `create_production()` to create SpriteManager directly
- [ ] Update `tests/unit/ui/test_sprite_loading.py` to use fresh instances
- [ ] Update `tests/unit/ui/test_sprites.py` to use fresh instances (replace all .reset() with fresh construction)
- [ ] Run: `pytest tests/unit/ui/test_sprites.py tests/unit/ui/test_sprite_loading.py -v` -- all pass
- [ ] Run: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass
- [ ] Commit: "refactor: migrate SpriteManager from singleton to DI via ApplicationContext"

**Notes:** SpriteManager is referenced by `game/ui/__init__.py` for eager import (race condition prevention). Verify that the eager import still works after removing SingletonMeta.

---

### Task 4.3: Migrate ShipThemeManager [Complex]
**Singleton file:** `game/ui/assets/ship_theme_manager.py`
**Production .instance() call sites (8):**
- `game/ui/renderer/game_renderer.py:74` -- `ShipThemeManager.instance()`
- `game/ui/panels/race_summary_panel.py:587` -- `ShipThemeManager.instance()`
- `game/ui/panels/ship_detail_panel.py:175` -- `ShipThemeManager.instance()`
- `game/ui/panels/race_theme_gallery.py:111` -- `ShipThemeManager.instance()`
- `game/ui/screens/fleet_data_source.py:291` -- `ShipThemeManager.instance()`
- `game/ui/screens/race_browser_dialog.py:131` -- `ShipThemeManager.instance()`
- `game/ui/screens/race_setup_screen.py:415` -- `ShipThemeManager.instance()`
- `game/ui/screens/workshop_screen.py:112` -- `ShipThemeManager.instance()`

**Test files that reset ShipThemeManager:**
- `tests/unit/entities/test_ship_theme_logic.py` -- 6 `.reset()` calls
- `tests/unit/ui/test_theme_discovery.py` -- 18 `.reset()` calls (setup/teardown)

**TDD steps:**
- [ ] Write test: ShipThemeManager can be instantiated without SingletonMeta
- [ ] Write test: ApplicationContext provides ShipThemeManager instance
- [ ] Remove `metaclass=SingletonMeta` from ShipThemeManager class definition
- [ ] Update `game/ui/renderer/game_renderer.py` to receive ShipThemeManager via DI
- [ ] Update `game/ui/panels/race_summary_panel.py` to receive ShipThemeManager via DI
- [ ] Update `game/ui/panels/ship_detail_panel.py` to receive ShipThemeManager via DI
- [ ] Update `game/ui/panels/race_theme_gallery.py` to receive ShipThemeManager via DI
- [ ] Update `game/ui/screens/fleet_data_source.py` to receive ShipThemeManager via DI
- [ ] Update `game/ui/screens/race_browser_dialog.py` to receive ShipThemeManager via DI
- [ ] Update `game/ui/screens/race_setup_screen.py` to receive ShipThemeManager via DI
- [ ] Update `game/ui/screens/workshop_screen.py` to receive ShipThemeManager via DI
- [ ] Update `game/context.py` `create_production()` to create ShipThemeManager directly
- [ ] Update `tests/unit/entities/test_ship_theme_logic.py` to use fresh instances
- [ ] Update `tests/unit/ui/test_theme_discovery.py` to use fresh instances (replace all 18 .reset() calls)
- [ ] Run: `pytest tests/unit/entities/test_ship_theme_logic.py tests/unit/ui/test_theme_discovery.py -v` -- all pass
- [ ] Run: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass
- [ ] Commit: "refactor: migrate ShipThemeManager from singleton to DI via ApplicationContext"

**Notes:** ShipThemeManager has the most UI call sites (8). Each call site is in a different file, requiring each UI class to receive the manager via constructor or context. The `_init_lock` and `_io_lock` threading locks should remain as instance attributes.

---

### Task 4.4: Migrate ScreenshotManager [Medium]
**Singleton file:** `game/ui/services/screenshot_manager.py`
**Production .instance() call sites (6):**
- `game/ui/screens/build_queue_screen.py:539` -- `ScreenshotManager.instance()`
- `game/ui/screens/planet_list_window.py:493` -- `ScreenshotManager.instance()`
- `game/ui/screens/star_list_window.py:454` -- `ScreenshotManager.instance()`
- `game/ui/screens/strategy_ui_action_router.py:103,111` -- `ScreenshotManager.instance()` (2 calls)
- `game/ui/screens/workshop_screen.py:69` -- `ScreenshotManager.instance()`

**Test files that reset ScreenshotManager:**
- `tests/repro_issues/test_bug_15_screenshot_strategy.py` -- 1 `.reset()` call
- `tests/unit/ui/services/test_screenshot_manager.py` -- uses `.instance()` (11 calls)

**TDD steps:**
- [ ] Write test: ScreenshotManager can be instantiated without SingletonMeta
- [ ] Write test: ApplicationContext provides ScreenshotManager instance
- [ ] Remove `metaclass=SingletonMeta` from ScreenshotManager class definition
- [ ] Update `game/ui/screens/build_queue_screen.py` to receive ScreenshotManager via DI
- [ ] Update `game/ui/screens/planet_list_window.py` to receive ScreenshotManager via DI
- [ ] Update `game/ui/screens/star_list_window.py` to receive ScreenshotManager via DI
- [ ] Update `game/ui/screens/strategy_ui_action_router.py` to receive ScreenshotManager via DI
- [ ] Update `game/ui/screens/workshop_screen.py` to receive ScreenshotManager via DI
- [ ] Update `game/context.py` `create_production()` to create ScreenshotManager directly
- [ ] Update `tests/repro_issues/test_bug_15_screenshot_strategy.py` to use fresh instance
- [ ] Update `tests/unit/ui/services/test_screenshot_manager.py` to use fresh instances
- [ ] Run: `pytest tests/unit/ui/services/test_screenshot_manager.py tests/repro_issues/test_bug_15_screenshot_strategy.py -v` -- all pass
- [ ] Run: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass
- [ ] Commit: "refactor: migrate ScreenshotManager from singleton to DI via ApplicationContext"

**Notes:** ScreenshotManager creates directories in `__init__`. The `create_test()` factory should set `enabled=False` to avoid filesystem side effects in tests.

---

### Task 4.5: Migrate GameSettings [Simple]
**Singleton file:** `game/ui/services/game_settings.py`
**Production call sites (2, using `GameSettings()` not `.instance()`):**
- `game/ui/screens/settings_window.py:28` -- `self._settings = GameSettings()`
- `game/ui/screens/strategy_renderer.py:64` -- `self._settings = GameSettings()`

**Test files:** None (0 test files reference GameSettings)

**TDD steps:**
- [ ] Write test: GameSettings can be instantiated without SingletonMeta
- [ ] Write test: ApplicationContext provides GameSettings instance
- [ ] Write test: GameSettings does not auto-save in test mode (if applicable)
- [ ] Remove `metaclass=SingletonMeta` from GameSettings class definition
- [ ] Update `game/ui/screens/settings_window.py` to receive GameSettings via DI
- [ ] Update `game/ui/screens/strategy_renderer.py` to receive GameSettings via DI
- [ ] Update `game/context.py` `create_production()` to create GameSettings directly
- [ ] Run: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass
- [ ] Commit: "refactor: migrate GameSettings from singleton to DI via ApplicationContext"

**Notes:** GameSettings loads from disk in `__init__` and auto-saves on `set()`. The `create_test()` factory should create a GameSettings that uses in-memory defaults without disk I/O. Since GameSettings() call sites use direct construction (which SingletonMeta intercepts), after removing SingletonMeta these calls will create new instances each time -- they must be changed to receive a shared instance via DI.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] AssetManager no longer uses SingletonMeta
- [ ] SpriteManager no longer uses SingletonMeta
- [ ] ShipThemeManager no longer uses SingletonMeta
- [ ] ScreenshotManager no longer uses SingletonMeta
- [ ] GameSettings no longer uses SingletonMeta
- [ ] Full test suite passes (14783+ tests, 0 failures)
- [ ] 5 separate commits, one per singleton
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
