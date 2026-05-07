# PROJ-374 File Manifest

> Generated during project scaffolding. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files modified or created

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/ui/screens/strategy_renderer.py` | Production (modify) | 1 | `_draw_grid` (line 193) gains cache logic OR delegates to a new `GridLayer` class. Add `_grid_cache_surface`, `_grid_cache_key`, `_compute_grid_cache_key()` instance attributes/methods. Wire into `__init__` and `draw()` (line 260). |
| `game/ui/screens/strategy_render/grid.py` | Production (modify) | 1 | `draw_grid` (line 12) refactored to accept a target surface as parameter, not unconditionally `screen`. Existing call site updated to pass `screen` until caching is integrated. |
| `game/ui/screens/strategy_render/grid_layer.py` | Production (new — optional) | 1 | New `GridLayer` class if `strategy_renderer.py` would exceed 500 LOC with in-place caching. Pattern: mirror [hex_outlines.py:20-80](../../../game/ui/screens/strategy_render/hex_outlines.py#L20). Decided at implementation time. |
| `tests/unit/ui/screens/strategy_render/test_grid_cache.py` | Test (new) | 1 | Cache hit on idle camera; miss when each individual key input changes (position, zoom, viewport, hex_size); short-circuit at zoom < 0.4; surface reuse (no leak under sustained invalidation); content correctness on miss matches direct `draw_grid` output. |
| `tests/unit/ui/screens/strategy_render/test_grid.py` | Test (modify if exists, otherwise skip) | 1 | If a `test_grid.py` exists, verify behavior unchanged on cache miss. If not, the new `test_grid_cache.py` covers the unit. |
| `findings/profile_summary.md` | Project doc (already created) | — | Originating profile evidence. |
| `findings/01_grid_render_research.md` | Project doc (already created) | — | Render-path research from Explore subagent. |
