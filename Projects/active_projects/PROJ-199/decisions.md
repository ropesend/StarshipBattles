# PROJ-199: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-25 | Scope limited to 2 categories: lazy init + comp_def centralization | PROJ-198 audit cleared remaining 113 patterns as legitimate; only these 2 have clean mechanical fixes |
| 2026-02-25 | Split lazy init into "true missing" (Phase 1) vs "unnecessary guard" (Phase 2) | Different fix types: add init + replace guard vs just remove guard |
| 2026-02-25 | Add `get_component_type()` and `get_component_threshold()` helpers | ship_stats_calculator has 2 non-abilities dual-format patterns following same isinstance/getattr pattern |
| 2026-02-25 | Keep `_get_numeric_value()` as-is | General-purpose dual-format getter at L459 — too broadly used and too generic to replace |
| 2026-02-25 | Keep ship_stats_renderer.py getattr calls out of scope | Component .status/.shots_fired/.shots_hit always exist — defensive but harmless, low value fix |
| 2026-02-25 | Keep component_resource_manager.py:97 out of scope | `evaluated_resource_cost` is genuinely optional dynamic attr set by ComponentStatsCalculator |
