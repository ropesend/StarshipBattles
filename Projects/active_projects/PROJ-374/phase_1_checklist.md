# Phase 1: Cache strategy grid surface

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-374 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add property-keyed surface cache to the grid render path. On cache hit, `screen.blit(cached_surface)`. On miss, render to the cached surface via the existing `draw_grid` (refactored to accept a target surface), update the key, blit. Single entry, single surface allocation, quantized key prevents thrash on smooth animations.

---

## Pre-flight (TDD baseline)

- [ ] Re-read [findings/01_grid_render_research.md](findings/01_grid_render_research.md) end-to-end.
- [ ] Read [strategy_render/background.py:17-58](../../../game/ui/screens/strategy_render/background.py#L17) and [strategy_render/hex_outlines.py:20-80](../../../game/ui/screens/strategy_render/hex_outlines.py#L20) — understand the exact existing precedent before writing similar code.
- [ ] Read [strategy_render/grid.py:12-85](../../../game/ui/screens/strategy_render/grid.py#L12) end-to-end. Confirm the inputs match the documented list (camera position, zoom, viewport, hex size). If a hidden input is found, log it under `findings/` and update the cache key to include it.
- [ ] Check current LOC of `strategy_renderer.py` (`wc -l game/ui/screens/strategy_renderer.py`) to decide between in-place vs. new `GridLayer` class.
- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline pass count.

---

## Tasks

### Task 1.1: Add cache hit/miss/invalidation tests (TDD-first) [Simple]
**File:** `tests/unit/ui/screens/strategy_render/test_grid_cache.py` (new)
**Tests:** `pytest tests/unit/ui/screens/strategy_render/test_grid_cache.py -v`

- [ ] Add test class `TestGridCache`.
- [ ] `test_cache_hit_blits_existing_surface_without_redrawing` — set up renderer with a stub camera; call `_draw_grid` twice with no input change. Assert `draw_grid` (the underlying drawing fn) was invoked once; `screen.blit` called twice (or whatever pattern fits the implementation).
- [ ] `test_position_x_change_beyond_tolerance_invalidates` — first call at `cam.x = 0.0`, second at `cam.x = 0.2` (> 0.1 tolerance). Both calls invoke draw_grid.
- [ ] `test_position_x_change_within_tolerance_hits` — first at 0.0, second at 0.05. Only one draw_grid invocation.
- [ ] `test_zoom_change_beyond_tolerance_invalidates` — first at zoom=1.0, second at zoom=1.02 (> 1% tolerance). Two invocations.
- [ ] `test_zoom_change_within_tolerance_hits` — first at 1.0, second at 1.005. One invocation.
- [ ] `test_viewport_resize_invalidates` — change `screen_width`, expect a new draw and a re-allocated surface.
- [ ] `test_zoom_below_cutoff_is_noop` — set `zoom = 0.3`. `_draw_grid` returns without invoking `draw_grid` and without touching the cache.
- [ ] `test_cache_surface_reused_across_misses` — capture `id(self._grid_cache_surface)` after first miss; force 5 more misses; assert the surface object identity is unchanged (no leak).
- [ ] `test_cache_miss_content_matches_direct_draw` — render to a fresh surface via direct `draw_grid` and via the cache miss path; assert the resulting surfaces are pixel-equal.
- [ ] Run the tests; **confirm they fail** (no caching yet).
- [ ] **Verify:** failures match expected reasons.

**Notes:** Tests should not require a real pygame display init. Use `pygame.Surface` directly with `SRCALPHA`; stub or fake the camera as a small dataclass.

### Task 1.2: Refactor `draw_grid` to accept a target surface [Simple]
**File:** `game/ui/screens/strategy_render/grid.py`
**Tests:** existing tests + Task 1.1

- [ ] Modify the signature: change the first `screen` (or equivalent) parameter to `target_surface: pygame.Surface`. Inside the function, replace every `screen.<...>` with `target_surface.<...>`.
- [ ] Update the existing caller in `strategy_renderer.py` to still pass `self.screen` for now (no behavior change in this task).
- [ ] **Verify:** sharded suite still green; no visual change yet.

**Notes:** Strictly mechanical rename for now. Caching wiring lands in Task 1.3.

### Task 1.3: Add cache attributes and key computation [Simple]
**File:** `game/ui/screens/strategy_renderer.py` (or new `grid_layer.py`)

- [ ] In `__init__`, add:
  - `self._grid_cache_surface: pygame.Surface | None = None`
  - `self._grid_cache_key: tuple | None = None`
- [ ] Add private method `_compute_grid_cache_key(self) -> tuple`:
  ```python
  cam = self.camera
  return (
      round(cam.position.x, 1),
      round(cam.position.y, 1),
      round(cam.zoom, 2),
      self.screen_width,
      self.screen_height,
      self.hex_size,
  )
  ```
- [ ] Add private method `_ensure_grid_cache_surface(self) -> pygame.Surface`:
  - If `self._grid_cache_surface is None` OR its size != `(screen_width, screen_height)`, allocate a fresh `pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)`.
  - Return the surface.
- [ ] **Verify:** no regressions; tests for these helpers pass if covered.

**Notes:** The check on size handles viewport resize without a separate event hook.

### Task 1.4: Wire cache into `_draw_grid` [Simple]
**File:** `game/ui/screens/strategy_renderer.py` (or new `grid_layer.py`)

- [ ] Replace the body of `_draw_grid` with:
  ```python
  if self.camera.zoom < 0.4:    # existing cutoff
      return

  key = self._compute_grid_cache_key()
  if key == self._grid_cache_key and self._grid_cache_surface is not None:
      self.screen.blit(self._grid_cache_surface, (0, 0))
      return

  surface = self._ensure_grid_cache_surface()
  surface.fill((0, 0, 0, 0))
  draw_grid(surface, ...)        # existing args, but target_surface is `surface`
  self._grid_cache_key = key
  self.screen.blit(surface, (0, 0))
  ```
- [ ] **Verify:** Task 1.1 tests now pass.

**Notes:**

### Task 1.5: Visual smoke + manual zoom/pan checks [Simple]
**Tests:** Manual

- [ ] Launch the game; go to strategy screen.
- [ ] Idle camera 5 seconds → look at grid; should be visually identical.
- [ ] Smooth pan (hold WASD or middle-mouse drag) → grid should follow without visible jitter or tearing. Adjust position tolerance if jitter is visible (try 0.5 or 1.0 world units).
- [ ] Smooth zoom (mouse wheel) → grid scales smoothly. Adjust zoom tolerance if visibly jumpy.
- [ ] Cross the `zoom = 0.4` cutoff in both directions; grid disappears/reappears correctly.
- [ ] Resize the window → grid re-renders to the new viewport size.
- [ ] **Verify:** all behaviors correct.

**Notes:**

### Task 1.6: Re-profile and confirm gain [Simple]
**Tests:** `python Tools/profile_game/profile_game.py`

- [ ] Capture a strategy-screen-only profile of comparable length to the baseline (~58s; idle for most of it; some camera movement).
- [ ] In the resulting HTML, check `_draw_grid` cumulative time. Target: ≥ 80% drop (≤ ~1.8s).
- [ ] Capture before/after numbers and add to plan.md Current State.

**Notes:**

### Task 1.7: Full sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Pass count ≥ baseline + new tests from Task 1.1.

**Notes:**

### Task 1.8: Commit Phase 1 [Simple]

- [ ] `git status --short` — only Phase 1 files dirty.
- [ ] Commit message: `perf(PROJ-374): cache strategy hex-grid surface keyed by quantized camera state`
- [ ] Co-author trailer.
- [ ] Do NOT push.
- [ ] **Verify:** `git show --stat HEAD` shows only in-scope files.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `_draw_grid` short-circuits at zoom < 0.4
- [ ] Cache hits on idle camera; misses on quantized-key change
- [ ] Single surface allocation reused across misses
- [ ] Re-profile shows `_draw_grid` cumulative drop ≥ 80%
- [ ] Visual smoke (pan, zoom, cutoff, resize) passes
- [ ] Sharded suite green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State — project ready for user verification
