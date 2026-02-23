# PROJ-138: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-13 | Project initialized | Starting point for Warp Point System Selection Dialog |
| 2026-02-13 | Follow PlanetSelectionWindow pattern for dialog | Closest existing dialog to our needs — UIWindow + UISelectionList + callback |
| 2026-02-13 | Use fire-and-forget (no stored reference) in WindowManager | Matches `prompt_planet_selection` pattern — one-shot dialog with callback |
| 2026-02-13 | Display format: `"Name (dist: N)"` with name→system mapping | User can see distance at a glance; mapping dict ensures we return actual system name to callback |
| 2026-02-13 | Alphabetical sort by system name | User specified "alphabetical list" in requirements |
| 2026-02-13 | Callback returns system name string (not object) | Matches existing contract in `strategy_superweapons.py:205` — `on_system_selected(system_name: str)` |
| 2026-02-13 | No changes to strategy_superweapons.py | Already uses `hasattr` discovery pattern — will auto-discover the new method |
| 2026-02-13 | No changes to superweapon_order_processor.py | Warp point placement logic is already correct (near-end at fleet, far-end at orbit_distance=6) |
| 2026-02-13 | Window size 450x500 | Simple list dialog doesn't need the full 950x650 of PlanetSelectionWindow |
| 2026-02-13 | Cancel / X-close silently aborts | No callback on cancel — order is simply not queued |
