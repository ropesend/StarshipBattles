# Verifier Report — PROJ-374 OpenCode review

**Verifier:** Claude subagent
**Verified at:** 2026-05-05 (UTC)
**Report verified:** Reviews/results/2026-05-06_041155_code_proj-374-gridlayer-surface-cache-invalidation-corr_req-req_20260506_041152_762cfe/report.md

## Verdicts

| Finding | Verdict | Notes |
|---|---|---|
| MAJ-1 | CONFIRM | Round-trip test absent; current early return at line 161 does preserve cache. Worth adding. |
| MAJ-2 | CONFIRM_REMEDIATION_REVISE | Single-resize test exists; multi-resize would be defensive but not load-bearing — add only if cheap. |
| MIN-1 | CONFIRM | Discrepancy real; not load-bearing because `_render_grid_to_surface` is mocked. Documenting it suffices. |
| MIN-2 | CONFIRM | Camera reads at lines 64–67 are real; docstring at 131–136 omits the constant inputs. |
| MIN-3 | CONFIRM_REMEDIATION_REVISE | Memory waste claim correct; recommend NOT changing surface allocation — see below. |
| MIN-4 | CONFIRM | Naming inconsistency real but trivial; agree no action required. |
| INFO-1 | CONFIRM | Quantum analysis is correct; 0.1 world-unit ≈ 0.1–0.2 px at typical zoom. |
| INFO-2 | CONFIRM | `COLORS['border_subtle']` hardcoded at line 54; documented exclusion is consistent. |
| INFO-3 | CONFIRM | Single-allocation pattern verified at `_ensure_surface`; no back-reference to renderer. |
| INFO-4 | CONFIRM | No threading imports; pygame single-threaded convention applies. |
| INFO-5 | CONFIRM | `pixel_to_hex` is mocked to (0,0) in tests; 80000 guard not exercised. |
| INFO-6 | CONFIRM | `draw_grid` at lines 104–110 is a thin wrapper around `_render_grid_to_surface`; uncached by design. |

## Per-finding details

### MAJ-1 — CONFIRM

Verified `grid.py:161` is `if r.camera.zoom < 0.4: return` — it returns before touching `_cache_key` or `_cache_surface`, so cache state IS preserved across the cutoff transition. Searched `test_grid_cache.py` for "round_trip" and "0.5" / "0.3" sequence — only `test_zoom_below_cutoff_is_noop` (line 203) and `test_zoom_at_cutoff_renders` (line 218) exist; neither tests the round-trip sequence. The gap is real and the suggested test adds genuine regression coverage for a behavior that's currently invariant-by-construction (early return) but could regress under refactor (e.g., if someone moved the early return below `_compute_key`).

Remediation as proposed is sound and minimal — a 5-line additional test.

### MAJ-2 — CONFIRM_REMEDIATION_REVISE

Confirmed `test_viewport_resize_reallocates_surface` (line 269) only does one 800×600 → 1024×768 transition. `_ensure_surface` (lines 148–157) only depends on `self._cache_surface.get_size() != target_size`, which is a purely-local comparison — there is no cross-resize state that could go stale. Python GC reclamation of the previous surface is automatic; no explicit free is needed.

The gap is real but extremely thin: a chained-resize test would be testing Python GC + pygame.Surface allocator behavior, not GridLayer logic. **Recommend adding the test only if the cost is trivial** (it is — ~10 lines), but rate it lower than MAJ-1. Could also be downgraded to MIN.

### MIN-1 — CONFIRM

Verified: `strategy_screen.py:89-94` constructs `Camera(screen_width - SIDEBAR_WIDTH, screen_height - TOP_BAR_HEIGHT, offset_x=0, offset_y=TOP_BAR_HEIGHT)`. Test stub at `test_grid_cache.py:35-39` sets `camera.width = screen_width`, `camera.height = screen_height`, `offset_x=0`, `offset_y=0`.

The discrepancy is genuine but **not load-bearing for the current test suite** because `_render_grid_to_surface` is mocked in every test that exercises rendering. The cache key (lines 139–146) does NOT read `camera.width/height/offset_x/offset_y`, so the stub's incorrect values don't affect cache invalidation logic.

A short docstring note in the test file is the right minimal fix; the parameterized-fixture upgrade is gold-plating.

### MIN-2 — CONFIRM

Verified `grid.py:64-67`:
```
cam_x = r.camera.position.x
cam_y = r.camera.position.y
base_x = (r.camera.width / 2) - cam_x * r.camera.zoom + r.camera.offset_x
base_y = (r.camera.height / 2) - cam_y * r.camera.zoom + r.camera.offset_y
```
These read `camera.width`, `camera.height`, `camera.offset_x`, `camera.offset_y`. The cache key at `grid.py:139-146` only contains position(x,y), zoom, screen_width, screen_height, hex_size. The docstring at lines 131–136 says "Every input that affects the rendered bitmap appears here" but does not document the implicit constant-input invariant.

Real documentation gap. Remediation as proposed is appropriate.

### MIN-3 — CONFIRM_REMEDIATION_REVISE

Verified `_ensure_surface` allocates `pygame.Surface((r.screen_width, r.screen_height), pygame.SRCALPHA)` and `draw` blits to `(0, 0)`. `BackgroundLayer.draw` at `background.py:33-58` does use viewport_rect.size and blits at `viewport_rect.topleft`. Memory math (~600×screen_height × 4 bytes ≈ 8 MB at 4K for the sidebar) is in the right ballpark.

**Recommend NOT making this change.** The current implementation is simpler, the cache key already keys on `screen_width`/`screen_height` (not viewport), and changing the blit destination would require also changing the cache-key inputs and the `_render_grid_to_surface` coordinate base. The render time is amortized away by the cache. Memory is not a bottleneck. Document the choice instead. (`StrategyRenderer.draw` already sets a viewport clip rect at line 270, so non-viewport pixels are clipped at blit time — correctness is preserved.)

### MIN-4 — CONFIRM

`_cache_surface`/`_cache_key` (GridLayer) vs `_bg_scaled`/`_bg_scaled_size`/`_bg_brightness` (BackgroundLayer) — confirmed. HexOutlineLayer uses `_hex_outline_cache`/`_hex_outline_cache_turn`. Inconsistency is real, action is "none recommended" — agree.

### INFO findings (one-sentence each)

- **INFO-1** CONFIRM: Quantum math (0.1 world-unit ≈ 0.1–0.2 screen px at zoom 1–2) is correct; max-zoom edge case noted appropriately.
- **INFO-2** CONFIRM: Verified `grid_color = COLORS['border_subtle']` at line 54; not in cache key, documented exclusion consistent with the design intent.
- **INFO-3** CONFIRM: `_ensure_surface` replaces `_cache_surface` on resize (Python GC handles old surface); `fill((0,0,0,0))` precedes redraw on miss; GridLayer holds no renderer back-reference.
- **INFO-4** CONFIRM: No threading imports anywhere in `grid.py`; pygame single-threaded convention is the project norm.
- **INFO-5** CONFIRM: `pixel_to_hex` is patched to return `(q=0, r=0)` in `_patch_inner_draw` (line 60), making `hex_count = 9` always — 80000 guard at line 51 is unreachable in unit tests.
- **INFO-6** CONFIRM: `draw_grid` at lines 104–110 is a 1-line passthrough to `_render_grid_to_surface(r, screen)`; cache state not shared, consistent with decisions.md.

## Recommended actions for Claude

In priority order:

1. **Fix MAJ-1**: add `test_zoom_cutoff_round_trip_preserves_cache` (5–10 lines). High value, low cost; locks in the early-return invariant.
2. **Fix MIN-2**: extend the `_compute_key` docstring at `grid.py:131-136` to list the constant inputs intentionally excluded (`camera.width`, `camera.height`, `camera.offset_x`, `camera.offset_y`, `COLORS['border_subtle']`). One docstring edit.
3. **Optional / defer MAJ-2**: add `test_multiple_consecutive_viewport_resizes` only if you want belt-and-braces. The single-resize test is structurally sufficient given how `_ensure_surface` is written.
4. **Document MIN-1**: add a short comment in `_make_renderer` noting that camera dims diverge from production but cache tests are insulated by the `_render_grid_to_surface` mock. No fixture refactor.
5. **Skip MIN-3**: do not change surface allocation. Optionally add a one-line comment explaining the screen-sized choice.
6. **Skip MIN-4**: noted, no action.
7. **All INFO**: no action.

Net: 1 new test + 1 docstring extension + 1 short test-stub comment. Skip the rest.
