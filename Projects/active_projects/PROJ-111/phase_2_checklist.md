# Phase 2: UI Framework Complex (Singletons & Rendering)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-111 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add comprehensive tests for complex framework components: singleton managers with threading/caching (SpriteManager, ShipThemeManager) and the game renderer with real rendering logic.
**Findings covered:** TCG-UI2-001, TCG-UI2-002, TCG-UI2-003
**Estimated tests:** ~80-100

---

## Task 2.1: SpriteManager Singleton and Error Paths [Complex]
**Finding:** TCG-UI2-002
**Source:** `game/ui/renderer/sprites.py` (164 lines)
**Tests:** `tests/unit/ui/test_sprites.py` (existing, extend)
**Mocks:** Mock file system for error paths; real pygame for sprite loading

**Singleton lifecycle:**
- [ ] Test `instance()` returns same object on repeated calls
- [ ] Test `reset()` destroys instance, next `instance()` creates new one
- [ ] Test direct `__init__()` when instance exists raises Exception

**Error paths:**
- [ ] Test `load_sprites()` with non-existent directory path
- [ ] Test `_load_from_directory()` with empty directory (no image files)
- [ ] Test `_load_from_directory()` with corrupt/invalid image file (mock `pygame.image.load` to raise)
- [ ] Test `get_sprite()` with out-of-bounds index -> returns None or handles gracefully
- [ ] Test `get_sprite()` with negative index

**Naming convention parsing:**
- [ ] Test loading files matching `Comp_*` pattern
- [ ] Test loading files matching `2048Portrait_Comp_*` pattern
- [ ] Test loading files with unexpected prefixes (should be skipped)
- [ ] Test sparse sprite list (indices 0, 2, 5 with gaps)

**Thread safety:**
- [ ] Test concurrent `instance()` calls from multiple threads all return same instance
- [ ] Test concurrent `load_sprites()` calls don't corrupt state

**Teardown:** Every test must call `SpriteManager.reset()` in teardown.

- [ ] Verify: `pytest tests/unit/ui/test_sprites.py -v`

**Notes:** Thread tests use `threading.Thread` and `concurrent.futures.ThreadPoolExecutor`. Keep thread count small (4-8) to avoid CI flakiness.

---

## Task 2.2: ShipThemeManager Edge Cases [Complex]
**Finding:** TCG-UI2-003
**Source:** `game/ui/assets/ship_theme_manager.py` (150+ lines)
**Tests:** `tests/unit/ui/test_theme_discovery.py` (existing, extend)
**Mocks:** Mock file system for error paths; real pygame for image loading

**Singleton lifecycle:**
- [ ] Test `instance()` returns same object on repeated calls
- [ ] Test `reset()` destroys instance, next `instance()` creates new one
- [ ] Test `clear()` resets caches but preserves instance (themes dict cleared, loaded=False)
- [ ] Test direct `__init__()` when instance exists raises `StateException`

**Error paths - theme discovery:**
- [ ] Test `initialize()` with missing ShipThemes directory (no crash)
- [ ] Test `initialize()` with empty ShipThemes directory (no themes found)
- [ ] Test `initialize()` with theme directory missing `theme.json` (skip that theme)
- [ ] Test `initialize()` with malformed `theme.json` (invalid JSON) -> skip with log

**Error paths - image loading:**
- [ ] Test `load_image()` with non-existent theme_id -> returns None/fallback
- [ ] Test `load_image()` with non-existent ship_class within valid theme -> returns None/fallback
- [ ] Test `load_image()` with image file referenced in theme.json but missing on disk

**Caching:**
- [ ] Test `load_image()` caching: second call returns same surface (cache hit)
- [ ] Test `clear()` invalidates cache, next `load_image()` reloads from disk

**Metrics:**
- [ ] Test `get_metrics()` returns expected metrics dict for valid theme/class
- [ ] Test `get_metrics()` caching behavior (cached after first call)

**Thread safety:**
- [ ] Test concurrent `load_image()` calls from multiple threads don't corrupt cache
- [ ] Test concurrent `initialize()` calls (double-checked locking)

**Teardown:** Every test must call `ShipThemeManager.reset()` in teardown.

- [ ] Verify: `pytest tests/unit/ui/test_theme_discovery.py -v`

**Notes:** For file-system error tests, use `unittest.mock.patch` on `os.path.exists`, `os.listdir`, and `game.core.json_utils.load_json`. Thread tests keep thread count small.

---

## Task 2.3: Game Renderer Integration Tests [Complex]
**Finding:** TCG-UI2-001
**Source:** `game/ui/renderer/game_renderer.py` (~200 lines)
**Tests:** `tests/unit/ui/test_rendering_logic.py` (existing, extend)
**Mocks:** Mix of real pygame surfaces and mocked ship data

Existing tests cover: culling. Missing:

**draw_ship() tests:**
- [ ] Test draw_ship with alive ship inside camera bounds -> draws something (circle or image)
- [ ] Test draw_ship with dead ship -> returns early, no drawing calls
- [ ] Test draw_ship with theme image available (mock ShipThemeManager to return surface)
- [ ] Test draw_ship with no theme image (fallback to geometric rendering)
- [ ] Test draw_ship with different zoom levels (0.1x, 1.0x, 5.0x) -> verify scaled_radius changes
- [ ] Test draw_ship at camera boundary (partially visible) -> still draws

**draw_hud() tests:**
- [ ] Test draw_hud renders ship name text
- [ ] Test draw_hud renders HP bar
- [ ] Test draw_hud with zero HP ship
- [ ] Test draw_hud with shield display (ship with shields > 0)
- [ ] Test draw_hud resource display (fuel, energy, ammo)

**Layer rendering:**
- [ ] Test layer color mapping matches LAYER_COLORS constant
- [ ] Test all 4 layer types render with correct colors (ARMOR, OUTER, INNER, CORE)

- [ ] Verify: `pytest tests/unit/ui/test_rendering_logic.py -v`

**Notes:** Use real pygame surfaces (`pygame.Surface((800, 600))`) for draw targets. Mock the ship objects with required attributes. Use `mock.patch` for ShipThemeManager to control image availability.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All new tests passing: `pytest tests/unit/ui/test_sprites.py tests/unit/ui/test_theme_discovery.py tests/unit/ui/test_rendering_logic.py -v`
- [ ] No regressions: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
