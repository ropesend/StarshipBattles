# Review Report: PROJ-374 GridLayer Surface Cache

**Review mode:** Code review (delegated by Claude Code)
**Scope:** `game/ui/screens/strategy_render/grid.py`, `game/ui/screens/strategy_renderer.py`, `tests/unit/ui/screens/strategy_render/test_grid_cache.py`
**Parent request:** None
**Checkout:** `feat/03c-phase-aware-execution` @ `0ce156fb334b121f2e2c966fb16c34aa23b0e04c`
**Reviewer:** OpenCode (inline — 3 primary files, no agent swarm needed)

---

## Findings

### MAJ — Should fix before merge

**MAJ-1: Missing zoom cutoff round-trip test** — Area 4 (Test coverage)

`tests/unit/ui/screens/strategy_render/test_grid_cache.py:203-217`

The test suite covers zoom below cutoff (`zoom=0.3` → no-op) and at cutoff (`zoom=0.4` → renders), but does NOT test the round-trip transition: `zoom=0.5` (cache populated) → `zoom=0.3` (early return, no draw) → `zoom=0.5` again (cache hit expected). The current code handles this correctly (`GridLayer.draw` returns early at `grid.py:161` before touching cache state), but the absence of this test means a future refactor could inadvertently clear the cache on the exit path, reintroducing unnecessary re-renders when zoom crosses the cutoff boundary and returns.

**Suggested remediation:** Add `test_zoom_cutoff_round_trip_preserves_cache` — render at zoom=0.5, draw at zoom=0.3 (assert no render), draw at zoom=0.5 again (assert single render across both 0.5 calls).

---

**MAJ-2: No test for multiple consecutive viewport resizes** — Area 4 (Test coverage)

`tests/unit/ui/screens/strategy_render/test_grid_cache.py:269-286`

`test_viewport_resize_reallocates_surface` tests one resize (800×600 → 1024×768). A rapid resize sequence (e.g., 800×600 → 1024×768 → 800×600 → 1280×720) could expose issues with stale surface references or missed reallocation that a single-resize test wouldn't catch. The `_ensure_surface` method at `grid.py:148-157` compares `self._cache_surface.get_size()` against `target_size` on every call, which is correct for the single-resize case, but a chain of resizes exercises the full lifecycle of GC on the replaced surface + re-allocation at the original size.

**Suggested remediation:** Add `test_multiple_consecutive_viewport_resizes` — resize 800×600 → 1024×768 → 800×600 → 1280×720, assert each resize produces a distinct surface of correct size and the second 800×600 surface is a new allocation (not the first one).

---

### MIN — Nice-to-have / follow-up

**MIN-1: Test stub camera dimensions don't match production** — Area 1 (Cache invalidation) / Area 4 (Test coverage)

`tests/unit/ui/screens/strategy_render/test_grid_cache.py:35-39` vs `game/ui/screens/strategy_screen.py:89-94`

The test stub `_make_renderer` sets `camera.width = screen_width` and `camera.height = screen_height` (line 37-38), but in production the `Camera` is constructed with `screen_width - UIConfig.STRATEGY_SIDEBAR_WIDTH` (600px) and `screen_height - TOP_BAR_HEIGHT` (50px), with `offset_y = TOP_BAR_HEIGHT` (strategy_screen.py:89-94). Since `_render_grid_to_surface` is mocked in all cache tests, this discrepancy doesn't affect cache behavior verification. However, if the mock were ever removed, tests would exercise a different coordinate base (`base_x = camera.width/2 - ...`) than production, potentially hiding rendering bugs.

The stub also sets `camera.offset_x=0` (correct) and `camera.offset_y=0` (incorrect — should be `TOP_BAR_HEIGHT=50`), and `camera.width`/`camera.height` to full screen dimensions (incorrect — should be viewport dimensions).

**Suggested remediation:** Update `_make_renderer` to accept optional `camera_width`, `camera_height`, `offset_x`, `offset_y` parameters, defaulting to `screen_width`/`screen_height`/0/0 for backward compatibility. Add a variant test or parameterized fixture that injects production-realistic camera dimensions. Alternatively, document in the test file why the stub diverges and that cache-only tests don't depend on these values.

---

**MIN-2: Hidden inputs not documented in cache key invariant** — Area 1 (Cache invalidation)

`game/ui/screens/strategy_render/grid.py:64-67`

`_render_grid_to_surface` reads `r.camera.width`, `r.camera.height`, `r.camera.offset_x`, and `r.camera.offset_y` (lines 66-67) to compute `base_x` and `base_y`. None of these appear in the cache key at `grid.py:139-146`. They are benign today because:
- `camera.width` = `screen_width - 600` (screen_width is in the key)
- `camera.height` = `screen_height - 50` (screen_height is in the key)
- `camera.offset_x` = 0 (constant)
- `camera.offset_y` = 50 (constant)

The docstring at `grid.py:131-136` states "Every input that affects the rendered bitmap appears here. If a new input is introduced...it must be added." This correctly documents the contract but does not list the constant inputs that are intentionally excluded. The design.md (line 73) and decisions.md (line 16-17) mention the grid color exclusion but not the camera dimension/offset exclusion.

**Suggested remediation:** Extend the `_compute_key` docstring at `grid.py:131-136` to list the constant inputs read by `_render_grid_to_surface` that are intentionally excluded from the key: `camera.width` (derived from screen_width - SIDEBAR_WIDTH), `camera.height` (derived from screen_height - TOP_BAR_HEIGHT), `camera.offset_x` (fixed), `camera.offset_y` (fixed), `COLORS['border_subtle']` (fixed). This matches the documented risk management approach from design.md R5.

---

**MIN-3: Screen-sized cache surface wastes memory in sidebar/top-bar area** — Area 2 (Memory safety) / Area 1 (Cache invalidation)

`game/ui/screens/strategy_render/grid.py:148-157`

The cache surface is allocated at full screen dimensions (`r.screen_width × r.screen_height`) and blitted to screen at `(0, 0)`. The grid rendered in the sidebar area (columns where `cx > viewport_width`) and top bar area (where `cy < TOP_BAR_HEIGHT`) is never visible — it's clipped away by the viewport clip rect set in `StrategyRenderer.draw` at `strategy_renderer.py:270`. This wastes:
- Memory: ~600px × screen_height of the 2560px-width surface is sidebar (~23% of cache surface at typical resolution)
- Render time: every cache miss redraws hex columns that will be clipped

The memory impact is bounded (~8 MB wasted at 4K) and acceptable. The render time impact is amortized by the cache. However, `BackgroundLayer` (`background.py:41`) uses `viewport_rect` dimensions for its scaled surface — it allocates only what's needed. GridLayer could similarly allocate a viewport-sized surface and blit to `(0, TOP_BAR_HEIGHT)`.

**Suggested remediation:** Consider sizing the cache surface to the camera viewport (`camera.width × camera.height`) and blitting at `(0, camera.offset_y)` instead of `(0, 0)`. This would reduce memory and render cost and align with BackgroundLayer's approach. Low priority — correctness is not affected.

---

**MIN-4: Inconsistent naming convention with BackgroundLayer** — Area 5 (Pattern consistency)

`game/ui/screens/strategy_render/grid.py:128-129` vs `game/ui/screens/strategy_render/background.py:22-24`

GridLayer (`_cache_surface`, `_cache_key`) follows HexOutlineLayer's `_cache_*` naming. BackgroundLayer uses `_bg_scaled`, `_bg_scaled_size`, `_bg_brightness` — semantic names without the "cache" prefix. Both are internally consistent but the two naming schemes coexist. Not a bug, but worth noting for future layer additions.

**Suggested remediation:** No action required. For future layer classes, choose one convention and apply consistently. The `_cache_*` convention (GridLayer, HexOutlineLayer) is recommended as it's self-documenting.

---

### INFO — Observations

**INFO-1: Sub-quantum jitter tolerance visually safe for all reasonable pan/zoom speeds** — Area 1 (Cache invalidation)

`game/ui/screens/strategy_render/grid.py:20-21`

Position quantum of 0.1 world-units and zoom quantum of 0.01 are visually safe. At typical zoom levels (1.0–2.0), a 0.1 world-unit shift corresponds to 0.1–0.2 screen pixels — below the threshold of visual perception. At zoom=25.0 (max strategy zoom), 0.1 world-units = 2.5 screen pixels — borderline visible but panning at max zoom is rare. The zoom quantum of 0.01 means a 1% zoom change before cache invalidation, which is imperceptible. No sub-quantum drift could align with other scene elements (systems, fleets) because those are drawn at exact camera position — the worst case is a grid that lags by up to ~2.5 px at extreme zoom, and even that corrects as soon as the pan crosses a quantum boundary. Acceptable.

---

**INFO-2: Grid color hardcoded — cache invariant documented** — Area 1 (Cache invalidation)

`game/ui/screens/strategy_render/grid.py:54`

`COLORS['border_subtle']` = `(42, 48, 64)` is hardcoded and not in the cache key. The design.md (alternative E) and decisions.md explicitly document this as a known exclusion with the condition: "if it later becomes dynamic, this project documents that the key must extend." This is consistent with the documented risk management approach.

---

**INFO-3: Memory safety — no leaks, no reference cycles** — Area 2 (Memory safety)

`game/ui/screens/strategy_render/grid.py:148-157`

Surface allocation follows the single-entry, single-allocation pattern from design.md (line 77-80). On viewport resize, the old surface is replaced (Python GC reclaims it). On cache miss, `surface.fill((0,0,0,0))` clears all RGBA channels before redraw. GridLayer holds no back-reference to the renderer (r is a parameter, never stored). `StrategyRenderer._grid` holds a forward reference but GridLayer has no reference back to StrategyRenderer. No reference cycles.

Verified by test `test_cache_clears_to_transparent_on_miss` (`test_grid_cache.py:323-342`) which confirms `fill((0,0,0,0))` produces fully transparent pixels.

---

**INFO-4: Concurrent access — no risk under pygame single-threaded convention** — Area 3 (Concurrent access)

`game/ui/screens/strategy_render/grid.py:159-173`

`GridLayer.draw` modifies instance state (`_cache_surface`, `_cache_key`) and calls `pygame.draw.line`/`pygame.draw.lines` (via `_render_grid_to_surface`). Pygame rendering is single-threaded by convention; all drawing happens on the main thread. No `threading` imports or synchronization primitives are present or needed. No finding.

---

**INFO-5: `_render_grid_to_surface` hex_count limit never exercised** — Area 4 (Test coverage)

`game/ui/screens/strategy_render/grid.py:51-52`

The 80000-hex short-circuit guard (`if hex_count > 80000: return`) is never reached in tests because `r.camera.screen_to_world` is mocked to return `(0,0)` for all corners, producing a trivial hexagonal range of (min_q=-1, max_q=1, min_r=-1, max_r=1 → hex_count=9). This path is a defensive guard against extreme zoom-out rendering massive grids; its correctness can only be verified via integration/visual testing, not unit tests.

---

**INFO-6: `draw_grid` back-compat fast path is thin wrapper — correct** — Area 5 (Pattern consistency)

`game/ui/screens/strategy_render/grid.py:104-110`

`draw_grid(r, screen)` delegates to `_render_grid_to_surface(r, screen)` — a thin wrapper preserved for existing test callers (`test_grid_and_storms.py`). Production code goes through `GridLayer.draw`. This is the documented strategy from decisions.md (line 21). The retained function does not share cache state with GridLayer, which is correct — it's explicitly an uncached fast path.

---

## Areas With No Findings

- **Area 3 (Concurrent access):** No issues. Code is single-threaded by pygame convention; all state mutation is on instance attributes only accessed from the main render thread.

---

## Summary

| Severity | Count |
|----------|-------|
| CRIT     | 0     |
| MAJ      | 2     |
| MIN      | 4     |
| INFO     | 6     |

**Assessment:** PROJ-374 implementation is solid. The cache key covers all runtime-varying inputs that affect the rendered bitmap. Memory management follows the documented single-entry/single-allocation pattern correctly. The two MAJ findings are test coverage gaps (zoom cutoff round-trip, multiple consecutive resizes) — neither indicates a production bug. The four MIN findings are documentation and test fixture fidelity improvements. Overall, the changes are safe to merge; addressing the two MAJ test gaps before merge is recommended for regression resilience.
