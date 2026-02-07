# PROJ-55: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
<<<<<<< HEAD
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
=======
| 2026-02-01 | Project initialized | Starting point for Data-Driven Planet-Specific Colonization System |
| 2026-02-01 | All 11 planet types colonizable from start | User decision: Research system will gate components later, keep all types available initially for system testing |
| 2026-02-01 | Colony pods as ship components | User decision: Colony pods installed on ships in design workshop, ships designed with colony component like engines/bridges, entire colony ship consumed during colonization |
| 2026-02-01 | 11 separate components (not generic) | User decision: One component per planet type for easier balancing, modding, and visualization in ship designer |
| 2026-02-01 | Track pods, allow chaining | User decision: Fleet with 3 Ice pods can queue 3 ice colonizations, system validates to prevent over-commitment |
| 2026-02-01 | Remove single ship, not entire fleet | Design decision: Only the ship with colony pod is consumed on colonization, rest of fleet remains. If last ship, then fleet is removed. |
| 2026-02-01 | Use existing ability pattern | Design decision: Reuse `ResourceHarvesterAbility` pattern with type parameter for `ColonizePlanet` ability with `planet_type` parameter |
| 2026-02-01 | Two-stage validation (queue + execution) | Design decision: Validate pods at command time (before queueing) and re-validate at execution time (safety check if ship lost) |
| 2026-02-01 | UI filters planets by available pods | Design decision: Only show planets in selection that match fleet's available (uncommitted) colony pods for better UX |
| 2026-02-01 | AbilityLayer.STRATEGIC only | Design decision: Colony abilities are strategic-layer only (not used in tactical combat) |
| 2026-02-01 | "allowed_vehicle_types": ["Ship"] | Design decision: Colony pods only on ships, not planetary facilities (facilities come after colonization) |
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08
