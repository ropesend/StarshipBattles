# PROJ-374 — Strategy grid render research

> Source: Explore subagent run 2026-05-05.
> Read-only investigation; no files modified.

## 1. What `draw_grid` actually draws

[grid.py:12-85](../../../../game/ui/screens/strategy_render/grid.py#L12) renders the hex grid as **outlines only**: no filled hexes, no labels, no data-driven content. Two `pygame.draw` calls per visible column:

- Horizontal line segments (line 81: `pygame.draw.line(screen, grid_color, p1, p2, 1)`) connecting hex top edges across columns
- Polyline snake segments (line 84: `pygame.draw.lines(screen, grid_color, False, snake_points, 1)`) tracing left/bottom edges down each column

**Viewport-bounded** (lines 14-31): `camera.screen_to_world()` projects screen corners to world coords + 1-hex margin, then the column loop culls outside columns (lines 60-61). Pixel/vertex count depends only on viewport size and zoom — **not on map size**. Typically 50-500 hexes on screen.

## 2. Input dependencies (exhaustive — invalidation list)

The output bitmap is a pure function of these inputs:

| Input | Source | Volatility |
|-------|--------|-----------|
| `camera.position.x` | per-frame | volatile (smooth pan) |
| `camera.position.y` | per-frame | volatile (smooth pan) |
| `camera.zoom` | per-frame | volatile (smooth zoom) |
| `camera.offset_x` | UI layout | rare (sidebar/topbar) |
| `camera.offset_y` | UI layout | rare |
| `screen_width`, `screen_height` | resize event | rare |
| `hex_size` | session constant | never in-session |
| grid color | hardcoded `COLORS['border_subtle']` = `(42, 48, 64)` ([colors.py:22](../../../../game/ui/colors.py#L22)) | constant |

Map radius does **not** affect the bitmap (culling makes it irrelevant).

## 3. Per-frame vs. per-event

- **Per-frame volatile:** `camera.position.x`, `camera.position.y`, `camera.zoom` — change continuously during smooth pan/zoom animations and real-time user panning.
- **Per-event stable:** viewport dimensions, hex size, color.

**Key implication:** A naive "cache until invalidated" model thrashes on every micro-pan. The cache key must use **rounded/quantized camera state** so imperceptible motion is a hit.

## 4. Surface size

Grid renders directly to the screen surface — no offscreen buffer today. Natural cache size = viewport (after sidebar/top bar):

| Target | Viewport | RGBA cost |
|--------|----------|----------:|
| 2560×1600 minimum | ~2560×1550 | ~16 MB |
| 3840×2160 optimized | ~3840×2110 | ~33 MB |

One cache entry is the budget. Multiple entries (e.g., a pan history) would blow VRAM.

## 5. Existing cache precedents in the codebase

Two layers already follow the property-based invalidation pattern:

- `BackgroundLayer` ([strategy_render/background.py:17-58](../../../../game/ui/screens/strategy_render/background.py#L17)) — caches scaled surface, rebuilds on viewport size or brightness change (equality check on a tuple, lines 44-46).
- `HexOutlineLayer` ([strategy_render/hex_outlines.py:20-80](../../../../game/ui/screens/strategy_render/hex_outlines.py#L20)) — caches `_hex_outline_cache` keyed to turn number; rebuilds occupancy data once per turn (lines 76-79), draws from cache each frame.

The grid cache should follow the same idiom — instance attribute on the layer, plain equality check on a key tuple.

## 6. Recommended strategy

**Strategy (b): viewport-sized surface, regenerate on quantized camera/zoom change.**

Cache key:

```python
cache_key = (
    round(camera.position.x, 1),     # 0.1 world-unit tolerance
    round(camera.position.y, 1),
    round(camera.zoom, 2),           # 1% zoom tolerance
    viewport_width,
    viewport_height,
    hex_size,
)
```

Invalidation triggers (cache miss → re-render to off-screen surface, store, blit):

- Camera position drifts past 0.1 world units (≈ pixels at zoom=1)
- Zoom changes ≥ 1%
- Viewport resize
- Hex size changes (effectively never)

Below `zoom < 0.4` ([strategy_renderer.py:274](../../../../game/ui/screens/strategy_renderer.py#L274)) the grid is not drawn — cache should respect this as a no-op short-circuit.

## 7. Risks & mitigation

| Risk | Mitigation |
|------|-----------|
| Memory at 4K (~33 MB / cache entry) | Single entry only. Allocate once, reuse the same `pygame.Surface` and `surface.fill()` + redraw on miss instead of allocating fresh. |
| Stale grid (invalidation threshold too coarse) | Visual regression test on a known camera state — render to PNG, pixel-compare to baseline. |
| Threshold rounding collisions (different inputs → same key) | Unit test: positions within tolerance hash same; just outside hash differently. |
| Smooth pan/zoom thrash if threshold too tight | Tune thresholds based on a quick measurement of the pan/zoom delta-per-frame during typical animations. Default values above are an estimate; adjust if hit-rate is poor. |

## 8. Test approach

1. Pixel baseline: render at `(position=(0,0), zoom=2.0, viewport=2560×1550, hex_size=10)` → PNG reference.
2. Pan within tolerance → cache hit; pan beyond → miss.
3. Zoom within 1% → hit; beyond → miss.
4. Resize → invalidated.
5. Re-profile a 58s strategy session: expect `_draw_grid` cumulative drop from ~9.14s to under ~1.8s (≥ 80%).

## 9. Unanswered

- Typical camera pan/zoom delta-per-frame during smooth animation — sets the floor for hit-rate. May need a brief instrumentation pass during implementation to size the thresholds.
- Whether the renderer is called from anywhere besides the strategy `draw()`. (Spot-checked: only `strategy_renderer.py:275`.)
