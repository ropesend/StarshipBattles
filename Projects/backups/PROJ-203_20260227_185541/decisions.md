# PROJ-203: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-27 | Project initialized | Starting point for Reduce complexity: StrategyRenderer._draw_systems (CC 29) |
| 2026-02-27 | Include test fortification phase | Safety analysis found missing test coverage for colony markers, star fallbacks, and viewport culling edge cases |
| 2026-02-27 | Extract in order: color mapping -> colony marker -> star rendering | Increasing risk order - pure function first, then simple block, then complex block |
| 2026-02-27 | Keep all extracted methods private (underscore prefix) | These are internal implementation details, not public API |
| 2026-02-27 | Preserve exact magic numbers (200, 100, 150, 0.5, 600) | Changing thresholds is behavioral change, not refactoring |
| 2026-02-27 | Do NOT extract zoom threshold constant | Minor benefit, adds indirection without significant clarity gain |
| 2026-02-27 | Preserve star color evaluation order exactly | White check (r>200, g>200, b>200) must come before orange check (r>200, g>150) due to overlapping conditions |
