# Review Scope: PROJ-374 GridLayer surface cache — invalidation correctness, memory safety, test gaps
**Type:** code (delegated by Claude Code)
**Request ID:** req_20260506_041152_762cfe
**Scope:** Commit `0ce156fb334b121f2e2c966fb16c34aa23b0e04c` on `feat/03c-phase-aware-execution`
- `game/ui/screens/strategy_render/grid.py` — GridLayer + _render_grid_to_surface + draw_grid
- `game/ui/screens/strategy_renderer.py` — _draw_grid delegation
- `tests/unit/ui/screens/strategy_render/test_grid_cache.py` — 17 test cases
- Reference: `game/ui/screens/strategy_render/background.py` (BackgroundLayer cache)
- Reference: `game/ui/screens/strategy_render/hex_outlines.py` (HexOutlineLayer cache)

**Instructions:** Five focus areas: (1) cache invalidation correctness, (2) memory safety, (3) concurrent access, (4) test coverage gaps, (5) pattern consistency vs BackgroundLayer/HexOutlineLayer.

**Context:** Wave A of 8-project tech-debt sequence. Calibration review for PROJ-374 (single-phase, simplest project in the wave).
