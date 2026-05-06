# PROJ-374: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-05 | Project initialized as PROJ-374 | Side-finding from the PROJ-373 build-queue profile: `_draw_grid` consumed 9.14s of a 58s session (15.8%), redrawing the grid every frame with idle camera. Numbers in `findings/profile_summary.md`. |
| 2026-05-05 | Single-phase project | Scope is one self-contained change: add a property-keyed surface cache to the grid render path, mirroring existing `BackgroundLayer` and `HexOutlineLayer` patterns. No phase split needed. |
| 2026-05-05 | Strategy: viewport-sized cache, regenerate on quantized camera/zoom change | Alternative A (pre-render full map) blows memory at high zoom-in; D (tile-based) is too much code for first iteration; C (no quantization) thrashes on smooth pan. Viewport-sized + quantized key is the simplest correct solution. |
| 2026-05-05 | Cache key tolerances: 0.1 world units for position, 0.01 (1%) for zoom | Starting point; subject to re-tuning during Phase 1 based on measured pan/zoom delta-per-frame. Below these tolerances, visual change is sub-pixel and the cache hit is correct. |
| 2026-05-05 | Single cache entry, single surface allocation | Memory ceiling at 4K: ~33 MB. Acceptable. Multi-entry cache (e.g., pan-history) would multiply memory and complicate eviction; not justified. Surface allocated once, `fill()` + redraw on miss. |
| 2026-05-05 | Cache lives on `StrategyRenderer` (or a new `GridLayer` class) | Mirrors existing precedent: `BackgroundLayer.cache` on the layer instance. Decision deferred to implementation: in-place if `strategy_renderer.py` LOC budget allows, else factor into `grid_layer.py` (same pattern as `HexOutlineLayer`). |
| 2026-05-05 | Zoom < 0.4 short-circuit (no draw, no cache check) | The existing cutoff at [strategy_renderer.py:274](../../../game/ui/screens/strategy_renderer.py#L274) means there's nothing to cache below this zoom. Short-circuit at top of `_draw_grid` before key computation. |
| 2026-05-05 | Grid color is NOT in the cache key (it's a hardcoded constant) | `COLORS['border_subtle']` = `(42, 48, 64)` ([colors.py:22](../../../game/ui/colors.py#L22)). If color ever becomes dynamic (theme-driven), the key must extend. |
| 2026-05-05 | Acceptance bar: ≥ 80% drop in `_draw_grid` cumulative time on a comparable strategy-screen profile | Baseline was 9.14s/58s = 15.8% of session. Target: < 1.8s on a comparable session. Verified by re-profiling, not by claims about hit rate. |
| 2026-05-05 | Profile evidence saved to `findings/profile_summary.md` (markdown) — original 22MB HTML kept in `AgentCoordination/Scratchpad/reports/profiles/` (gitignored) | Same convention as PROJ-373. Markdown summary captures all numeric claims used in plan/design. |
| 2026-05-05 | Code research delegated to one Explore subagent | Report saved as `findings/01_grid_render_research.md`. Covered render path, dependencies, surface size, cache strategy, risks. |
