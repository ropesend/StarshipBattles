# PROJ-374: Strategy grid surface cache

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-374` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-374 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Cache strategy grid surface with quantized camera-key invalidation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-05 (Phase 1 implementation complete)
**Active Phase:** Complete — ready for review.
**Last Action:** Phase 1 implemented end-to-end on `feat/03c-phase-aware-execution`. `GridLayer` introduced in `game/ui/screens/strategy_render/grid.py` with quantized property-keyed surface cache (position rounded to 0.1, zoom rounded to 0.01). `StrategyRenderer._draw_grid` delegates to `self._grid.draw(self, screen)`. 17 new cache tests in `tests/unit/ui/screens/strategy_render/test_grid_cache.py` cover idle hits, per-input invalidation (x/y/zoom/width/height/hex_size), sub-quantum jitter hit, zoom < 0.4 short-circuit, surface reuse, SRCALPHA flag, viewport-resize reallocation, blit target, render target, and transparent clear on miss. Focused suite green: 104 passed (17 new + 87 existing strategy renderer/render tests).
**Next Action:** User to run a re-profile session (Task 1.6) and visual smoke (Task 1.5) at their leisure; record before/after numbers.
**Blockers:** None.

**Profile baseline (from `findings/profile_summary.md`):**
- `_draw_grid` cumulative: 9.14s / 58s session = 15.8%
- Per-frame cost varies; target is to amortize to near-zero on cache hits

## Overview

The strategy-screen hex grid is rasterized via `pygame.draw.line` / `draw.lines` from scratch every frame, even when the camera and zoom haven't changed. Geometry is a pure function of camera position, zoom, viewport size, and hex size — none of which change frame-to-frame except during user-driven pan/zoom. A property-keyed surface cache (matching the existing pattern in `BackgroundLayer` and `HexOutlineLayer`) reduces per-frame cost to a single `screen.blit(cached_surface)` on hits.

The challenge is that camera position and zoom *do* change every frame during smooth animations, so the cache key must be **quantized** (rounded to a tolerance) to stay useful. Below the existing zoom-out cutoff (`zoom < 0.4`) the grid isn't drawn at all — the cache should respect that.

## Goals

- **Phase 1 closed:** `StrategyRenderer._draw_grid` (or a new `GridLayer` class following the existing layer pattern) maintains a viewport-sized cached surface keyed by `(round(camera.x, 1), round(camera.y, 1), round(zoom, 2), viewport_w, viewport_h, hex_size)`. On hit, `screen.blit(cached)`. On miss, render to the cached surface (re-using the same surface allocation), then blit. `zoom < 0.4` is a no-op short-circuit.
- **Cache memory ceiling:** one cache entry, surface allocated once, `surface.fill((0,0,0,0))` + redraw on miss. ≤ 33 MB at 4K.
- **Cache invalidation correctness:** every input that affects the bitmap is in the key. Verified by a unit test that varies each input one at a time and confirms the cache misses.
- **Acceptance:** re-profile a strategy-screen-only session of comparable length; `_draw_grid` cumulative time drops by **≥ 80%** (from ~9.14s/58s → under ~1.8s).

## Scope

**In:**
- `game/ui/screens/strategy_renderer.py` — `_draw_grid` (line 193) gains caching, OR is replaced by a thin call to a new layer class.
- `game/ui/screens/strategy_render/grid.py` — `draw_grid` (line 12) refactored so it can render to an arbitrary surface, not just `screen` directly.
- A new `GridLayer` class (optional — only if the in-place caching in `strategy_renderer.py` would push that file over the 500-LOC ceiling). Pattern: mirror `HexOutlineLayer` ([strategy_render/hex_outlines.py:20-80](../../../game/ui/screens/strategy_render/hex_outlines.py#L20)).
- `tests/unit/ui/screens/strategy_render/test_grid_cache.py` (new) — cache hit/miss/invalidate tests with mocked surfaces.
- `tests/unit/ui/screens/strategy_render/test_grid.py` (existing if present) — verify behavior unchanged on cache miss.

**Out:**
- Caching of other strategy-screen layers (system markers, ship icons, range overlays). Each is a separate engineering decision — measure first, then decide.
- Refactoring the camera or hex-math modules.
- Pre-rendering the *entire* map vs. viewport-only (rejected — see design.md alternative A).
- Persistent disk cache across sessions (overkill).

## Key Files

| Component | File Path |
|-----------|-----------|
| Strategy renderer (caller) | `game/ui/screens/strategy_renderer.py:193,260,275` |
| Grid render fn | `game/ui/screens/strategy_render/grid.py:12-85` |
| Existing cache precedent — background | `game/ui/screens/strategy_render/background.py:17-58` |
| Existing cache precedent — hex outlines | `game/ui/screens/strategy_render/hex_outlines.py:20-80` |
| Camera (input source) | `game/ui/renderer/camera.py` |
| Color constant | `game/ui/colors.py:22` |
| Profile evidence | `findings/profile_summary.md` |
| Grid render research | `findings/01_grid_render_research.md` |

## Related Documents
- [design.md](design.md) — diagnosis, cache key choice, alternatives, risks
- [decisions.md](decisions.md) — design choices and rejected alternatives
- [findings/profile_summary.md](findings/profile_summary.md) — originating pyinstrument evidence (side-finding from PROJ-373)
- [findings/01_grid_render_research.md](findings/01_grid_render_research.md) — render-path research from Explore subagent

## Phases

### Phase 1: Cache strategy grid surface [Simple]
**Objective:** Add property-keyed surface cache to the grid render path. Single cache entry, viewport-sized, re-rendered on cache miss. Quantized key prevents thrash on smooth animations.
**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md).

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`
- [ ] Read `findings/profile_summary.md` and `findings/01_grid_render_research.md`
- [ ] Read `BackgroundLayer` and `HexOutlineLayer` to understand the existing cache pattern
- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline pass count

### Final Verification
- [ ] Sharded suite green; pass count ≥ baseline + new tests
- [ ] Re-profile a strategy-screen session: `_draw_grid` cumulative drop ≥ 80%
- [ ] Visual smoke: pan, zoom in, zoom out across the cutoff (zoom = 0.4), resize window. Grid renders correctly in every case.
- [ ] No memory leak under sustained pan/zoom (allocate surface once, reuse)
- [ ] User verified

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] Phase 1 tasks all checked
- [ ] Tests passing
- [ ] Re-profile shows ≥ 80% drop in `_draw_grid`
- [ ] User verified
