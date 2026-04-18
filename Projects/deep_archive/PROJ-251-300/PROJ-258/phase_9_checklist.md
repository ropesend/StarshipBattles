# Phase 9: Remove UI Singleton Shims

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-258 9`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove `.instance()` and `.reset()` compatibility shims from 5 UI-layer services: AssetManager, SpriteManager, ShipThemeManager, ScreenshotManager, GameSettings. Replace every call site with ApplicationContext access or direct construction.

---

## Tasks

### Task 9.1: Remove AssetManager shims [Simple]
**Files:** `game/assets/asset_manager.py` + ~7 test call sites
**Shim calls:** 5 production (get_asset_manager, planet/star data sources), 7 test

- [ ] Update `get_asset_manager()` convenience function — use `_default_asset_manager` directly
- [ ] Update `planet_data_source.py` — receive AssetManager via context or constructor
- [ ] Update `planet_selection_window.py` — receive via context
- [ ] Update `star_data_source.py` — receive via context (if applicable)
- [ ] Grep and update all test `.instance()` / `.reset()` calls
- [ ] Remove `instance()` and `reset()` classmethods from AssetManager
- [ ] Run: `pytest tests/ -x -q -n 4` — all pass
- [ ] Commit: "refactor: remove AssetManager .instance()/.reset() shims"

---

### Task 9.2: Remove SpriteManager shims [Simple]
**Files:** `game/ui/renderer/sprites.py` + ~31 test call sites
**Shim calls:** 3 production (app.py, workshop_screen.py), 31 test

- [ ] Update `game/app.py` — use `self.ctx.sprite_manager`
- [ ] Update `workshop_screen.py` — receive SpriteManager via context
- [ ] Grep and update all test `.instance()` / `.reset()` calls (31 sites)
- [ ] Remove `instance()` and `reset()` classmethods from SpriteManager
- [ ] Run: `pytest tests/ -x -q -n 4` — all pass
- [ ] Commit: "refactor: remove SpriteManager .instance()/.reset() shims"

---

### Task 9.3: Remove ShipThemeManager shims [Medium]
**Files:** `game/ui/assets/ship_theme_manager.py` + ~55 test call sites
**Shim calls:** 9 production (game_renderer, panels, screens), 55 test

- [ ] Grep all `ShipThemeManager.instance()` in game/ — catalog all 9 sites
- [ ] Update each production call site to receive ShipThemeManager via context or constructor
- [ ] Grep and update all test `.instance()` / `.reset()` calls (55 sites)
- [ ] Update `conftest.py` — replace `ShipThemeManager.reset()` with module-level reference reset or removal
- [ ] Remove `instance()` and `reset()` classmethods from ShipThemeManager
- [ ] Run: `pytest tests/ -x -q -n 4` — all pass
- [ ] Commit: "refactor: remove ShipThemeManager .instance()/.reset() shims"

---

### Task 9.4: Remove ScreenshotManager shims [Simple]
**Files:** `game/ui/services/screenshot_manager.py` + ~17 test call sites
**Shim calls:** 7 production (build_queue, planet_list, star_list, strategy_ui, workshop), 17 test

- [ ] Grep all `ScreenshotManager.instance()` in game/ — catalog all 7 sites
- [ ] Update each production call site to receive ScreenshotManager via context or constructor
- [ ] Grep and update all test `.instance()` / `.reset()` calls (17 sites)
- [ ] Update `conftest.py` — replace `ScreenshotManager.reset()` with module-level reference reset or removal
- [ ] Remove `instance()` and `reset()` classmethods from ScreenshotManager
- [ ] Run: `pytest tests/ -x -q -n 4` — all pass
- [ ] Commit: "refactor: remove ScreenshotManager .instance()/.reset() shims"

---

### Task 9.5: Remove GameSettings shims [Simple]
**Files:** `game/ui/services/game_settings.py` + 0 test call sites
**Shim calls:** 2 production (settings_window.py, strategy_renderer.py), 0 test

- [ ] Update `settings_window.py` — receive GameSettings via context
- [ ] Update `strategy_renderer.py` — receive GameSettings via context
- [ ] Remove `instance()` and `reset()` classmethods from GameSettings
- [ ] Remove `_default_game_settings` module-level variable
- [ ] Run: `pytest tests/ -x -q -n 4` — all pass
- [ ] Commit: "refactor: remove GameSettings .instance()/.reset() shims"

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `grep -rn "\(AssetManager\|SpriteManager\|ShipThemeManager\|ScreenshotManager\|GameSettings\)\.\(instance\|reset\)()" game/ tests/ conftest.py` — zero results
- [ ] Full test suite passes (14783+ tests, 0 failures)
- [ ] 5 commits (one per class)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 10
