# PROJ-374: Design — Strategy grid surface cache

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source: pyinstrument profile

`findings/profile_summary.md` documents the originating evidence —
`_draw_grid` consumed **9.14s of a 58s session (15.8%)** during a build-queue-focused
profile run. The grid was visible throughout but neither camera nor zoom
were touched, so every one of those samples represents wasted re-rasterization.

## Today's render path

`StrategyRenderer.draw()` ([strategy_renderer.py:260](../../../game/ui/screens/strategy_renderer.py#L260))
calls `self._draw_grid()` ([strategy_renderer.py:193](../../../game/ui/screens/strategy_renderer.py#L193)),
which calls `draw_grid(...)` in [strategy_render/grid.py:12-85](../../../game/ui/screens/strategy_render/grid.py#L12).
The grid function:

- Computes visible-column bounds via `camera.screen_to_world()` on the four screen corners (lines 14-31)
- Iterates columns within those bounds, building `snake_points` (a polyline tracing the column's left/bottom edges)
- Calls `pygame.draw.line()` per column for the horizontal segments (line 81)
- Calls `pygame.draw.lines()` per column for the snake polyline (line 84)

Output is drawn directly to the screen surface every frame.

## Target render path

```
StrategyRenderer._draw_grid(self):
    if camera.zoom < 0.4:                    # existing cutoff at line 274
        return

    key = self._compute_grid_cache_key()
    if key == self._grid_cache_key:
        self.screen.blit(self._grid_cache_surface, (0, 0))
        return

    # Cache miss: rebuild
    self._grid_cache_surface.fill((0, 0, 0, 0))   # transparent clear
    draw_grid(self._grid_cache_surface, ...)
    self._grid_cache_key = key
    self.screen.blit(self._grid_cache_surface, (0, 0))
```

`draw_grid` is refactored to render to a passed-in surface (the cache surface
on miss, the screen surface on edge cases) instead of unconditionally
`screen`.

## Cache key

```python
def _compute_grid_cache_key(self) -> tuple:
    cam = self.camera
    return (
        round(cam.position.x, 1),     # 0.1 world-unit tolerance
        round(cam.position.y, 1),     # 0.1 world-unit tolerance
        round(cam.zoom, 2),            # 1% zoom tolerance
        self.screen_width,
        self.screen_height,
        self.hex_size,
    )
```

Tolerances (0.1 world units, 1% zoom) are a starting point. They should be
re-tuned during Phase 1 based on a brief instrumentation pass measuring the
typical pan/zoom delta during smooth animations. A delta below the
tolerance produces a hit (the visual change is sub-pixel).

The grid color is hardcoded `COLORS['border_subtle']` =
`(42, 48, 64)` ([colors.py:22](../../../game/ui/colors.py#L22)) — not in the
key. If a future change makes color dynamic, the key must extend to include it.

## Surface allocation

One `pygame.Surface` of size `(screen_width, screen_height)` with
per-pixel alpha (`pygame.SRCALPHA`). Allocated once on first use; reused
across cache misses via `surface.fill((0, 0, 0, 0))` + redraw. On viewport
resize, the surface is reallocated.

Memory cost:
- 2560×1600 RGBA: ~16 MB
- 3840×2160 RGBA: ~33 MB

Single entry, single allocation. Acceptable.

## Existing cache precedent

The codebase already follows this exact pattern:

- [strategy_render/background.py:17-58](../../../game/ui/screens/strategy_render/background.py#L17)
  caches a scaled background surface, rebuilds on viewport-size or
  brightness change (tuple equality at lines 44-46).
- [strategy_render/hex_outlines.py:20-80](../../../game/ui/screens/strategy_render/hex_outlines.py#L20)
  caches `_hex_outline_cache` keyed by turn number; rebuilds occupancy
  data once per turn (lines 76-79); blits per frame.

The grid cache mirrors `BackgroundLayer`'s shape (property-keyed, surface-based).

## File-size choice: in-place vs. new layer class

`strategy_renderer.py` is the caller. Adding ~50 lines for the cache logic in-place is the simplest change. If the file is approaching the 500-LOC ceiling, factor into a new `GridLayer` class in `game/ui/screens/strategy_render/grid_layer.py` — same pattern as `HexOutlineLayer`. Decide at implementation time by reading the file's current line count.

## Phase 1 success criteria

- `_draw_grid` cumulative time in a re-profiled strategy-screen session drops **≥ 80%** vs. baseline.
- Cache hit ratio in steady state (camera idle for ≥ 1 frame): 100%.
- Visual regression test: render a fixed `(camera, zoom, viewport)` state to a known-good PNG and assert pixel equality on cache hits and on a fresh miss.
- All existing strategy-screen tests still green.
- Memory does not grow under sustained pan/zoom (single allocation; verified via repeated invalidations under instrumentation).

---

## Alternatives considered

### A. Pre-render the full map once; blit a viewport-sized crop per frame
- Pro: zero re-rasterization on pan/zoom (just an offset blit).
- Con: full-map surface at extreme zoom-in could be enormous (gigabytes). Even at typical zoom, a 50-radius galaxy at 100 px/hex is ~1500×1500 — fine — but at 4K zoom-in, the math grows fast. Hex math + culling already make per-frame rendering cheap *enough* for caching to dominate.
- **Rejected** — viewport-sized cache (current plan) is simpler and equally effective for the hit case.

### B. No caching; just optimize the per-frame draw_grid loop
- Pro: no memory cost, no invalidation logic.
- Con: the ~9s of cumulative cost is dominated by `pygame.draw` syscalls, not Python overhead. Hard to optimize further without dropping anti-aliasing or going to numpy/SDL2 batched draws.
- **Rejected** — caching produces a 10× win in the steady state; per-frame optimization gives at most ~30%.

### C. Cache without quantization; invalidate on any camera/zoom change
- Pro: simplest possible key.
- Con: smooth pan/zoom thrashes the cache every frame (camera changes per frame during animation). Net result: cache is useless during the most common interaction.
- **Rejected** — quantized key is the entire point.

### D. Tile-based cache (chunks of map pre-rendered, blitted in viewport tiles)
- Pro: best amortization across pan.
- Con: 10× more code; tile boundary handling is fiddly; tile-key invalidation is more complex than property-key.
- **Rejected** — premature optimization. Revisit only if Phase 1 hit rate is poor on real pan/zoom interactions.

### E. Add the grid color as a dynamic theme value (and to the cache key)
- Pro: future-proof.
- Con: speculative. Today the color is hardcoded. Adding theme support is a separate engineering decision unrelated to performance.
- **Rejected** — keep color out of the key; if it later becomes dynamic, this project documents that the key must extend.

---

## Risks

- **R1 — Tolerance too coarse.** Stale grid drifts from system markers / fleet icons drawn at exact camera position; visual jitter at low zoom. Mitigation: visual regression test at known camera state; tune tolerance if jitter visible. Floor: tolerance 0 (pixel-exact key) — works but reduces hit rate to zero on smooth pan.
- **R2 — Tolerance too tight.** Hit rate drops; cache becomes a no-op. Mitigation: instrumented hit-rate counter during dev; aim for ≥ 95% hit rate when camera idle, ≥ 50% during smooth pan.
- **R3 — Zoom cutoff (`< 0.4`).** Cache must respect the existing no-draw zone or it'll show a stale grid below the cutoff. Mitigation: short-circuit at top of `_draw_grid` before key check.
- **R4 — Surface allocation on resize.** If viewport resizes between frames, allocating a fresh surface mid-frame is fine but costly per resize event. Mitigation: detect via key change and reallocate; resize is rare so cost is acceptable.
- **R5 — Hidden inputs to `draw_grid`.** If `draw_grid` reads any state we missed in section "Cache key", cache becomes incorrect. Mitigation: re-read [grid.py:12-85](../../../game/ui/screens/strategy_render/grid.py#L12) carefully; assert all reads against the documented input list. The unit test at task 1.1 (vary each input → cache miss) catches this.
