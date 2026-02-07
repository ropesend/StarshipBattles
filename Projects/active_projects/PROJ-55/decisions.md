# PROJ-55: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-06 | Project initialized | Starting point for Test Lab Screen God Class Decomposition |
| 2026-02-06 | Package name: `test_lab/` (not `combat_lab/` or `test_lab_screen/`) | User preference. Clean name, matches existing naming. Requires deleting `test_lab.py` (dead) and `test_lab_screen.py` (replaced). |
| 2026-02-06 | Hybrid grouping: 8 modules + `__init__.py` | Balances file count, cohesion, and AI editability. One-class-per-file too granular (40-line files), flat grouping too coarse (1445-line results.py). Sweet spot: 110-830 lines per module. |
| 2026-02-06 | Group ShipPanel + TabbedShipPanel + ComponentPanel into `ship_panels.py` | All three created/destroyed together in `_create_ship_panels()`, ShipPanel is only 40 lines, ComponentPanel only 70 lines — too small for individual files. Combined: ~240 lines. |
| 2026-02-06 | Group JSONPopup + ConfirmationDialog into `dialogs.py` | Share modal overlay pattern (semi-transparent background, centered popup, escape-to-close). Both are leaf nodes used only by TestLabScreen. Combined: ~250 lines. |
| 2026-02-06 | Keep ScrollableJSONViewer in own file (`json_viewer.py`) | Despite being only ~110 lines, it's a shared dependency of 3 other classes (ShipPanel, TabbedShipPanel, ComponentPanel). Isolation makes import paths clear. |
| 2026-02-06 | Delete `game/ui/screens/test_lab.py` | Verified zero imports anywhere in codebase. Legacy artifact from PROJ-46 naming standardization. Per CLAUDE.md: "eradicate old systems completely." |
| 2026-02-06 | `get_test_data_dir()` stays in `screen.py` | Uses `__file__`-relative path calculation. Moving to a separate utils.py would require updating the path math regardless, and it's only used by TestLabScreen. |
| 2026-02-06 | Patch paths update to `game.ui.screens.test_lab.screen.*` | Since patched names (load_json, TestRunner, WIDTH, HEIGHT, JSONPopup) are imported at module level in screen.py, patches must target that module's namespace. |
| 2026-02-06 | Include package README.md for AI agent documentation | User requested accompanying documentation for maintainability. |
