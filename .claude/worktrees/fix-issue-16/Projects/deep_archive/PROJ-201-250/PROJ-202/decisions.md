# PROJ-202: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-27 | Project initialized | Starting point for Reduce complexity: StrategyRenderer._draw_systems (CC 29) |
| 2026-02-27 | Add Phase 1: Test Fortification | Safety analysis found no tests for star color classification - must add coverage BEFORE refactoring |
| 2026-02-27 | Extract `_classify_star_color` as static method | Pure function with no dependencies; easiest and safest extraction |
| 2026-02-27 | Use early returns in colony marker helper | Flattens 3-level nesting to linear flow; improves readability |
| 2026-02-27 | Keep selection highlight logic in `_draw_system_stars` | Dual condition (sys selected AND star is primary) is easy to break if separated |
| 2026-02-27 | Add ZOOM_DETAIL_THRESHOLD constant | Magic number 0.5 appears 3 times; named constant improves maintainability |
| 2026-02-27 | Preserve exact color classification order | The if-elif chain is order-dependent; white must be checked before orange |
| 2026-02-27 | Target CC < 10 for main function | Aggressive target allows room for future growth; current 29 is unacceptable |
| 2026-02-27 | Document color thresholds in docstring | Values (200, 100, 150) are intentional design; future maintainers need context |
