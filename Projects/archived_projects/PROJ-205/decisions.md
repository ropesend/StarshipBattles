# PROJ-205: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-27 | Project initialized | Created from verified legacy code audit findings |
| 2026-02-27 | Exclude TypeGuard functions (AIR-003) | All 4 are exported in `ai/interfaces/__init__.py` `__all__` - they're public API, not dead code |
| 2026-02-27 | Exclude economy placeholders (STR-003) | Rendered in `empire_treasury_panel.py:249-267` - removing causes `AttributeError` |
| 2026-02-27 | Exclude exit_dialog refactoring (AIR-002) | 102-line file, standard Pygame pattern, refactoring = churn for zero benefit |
| 2026-02-27 | Exclude research system removal (AIR-006) | Standalone sandbox feature accessible from main menu, not dead code |
| 2026-02-27 | Keep `scroll_bar` attribute (UIS-001) | Production code uses it at 4 call sites (lines 427, 429, 430, 451) for scroll wheel handling |
| 2026-02-27 | Downgrade SIM-001 from Critical to Major | Known documented tech debt, restructure branching rather than remove entirely |
| 2026-02-27 | 3-phase approach: placeholder → eradication → hygiene | Ordered by risk (lowest first) and logical grouping |
