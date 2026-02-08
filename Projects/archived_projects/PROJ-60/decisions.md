# PROJ-60: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-06 | Project initialized | Starting point for Break Down GalaxyTestScreen |
| 2026-02-06 | 4-module package (not 7-8 modules) | User preference. 4 modules matches file complexity better than fine-grained split. |
| 2026-02-06 | Follow `formation/` package pattern | Absolute imports, `__all__`, docstring in `__init__.py`. Consistent with codebase. |
| 2026-02-06 | Mode-based split (galaxy_mode + system_mode) | Natural boundary: the two modes share almost no logic. Each has own UI, generation, rendering. |
| 2026-02-06 | Pass screen reference to mode helpers | Mode helpers need camera, ui_manager, canvas_width. Single ref avoids passing 5+ params. |
| 2026-02-06 | Delete original file completely | Per CLAUDE.md migration policy. Only 1 import to update (app.py line 31). |
| 2026-02-06 | Pre-existing test failures not PROJ-60 | `test_image_scale_factor` (FAILED) and `test_multi_selection_logic` (ERROR). Baseline: 1185 passed. |
