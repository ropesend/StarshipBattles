# PROJ-162: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Project initialized | Starting point for Extract CargoTransferService from UI Dialogs |
| 2026-02-23 | Extract service + fix all 12 test failures (not just the 2 originally reported) | User chose full extraction over quick fix for long-term maintainability |
| 2026-02-23 | Service imported directly by UI, not exposed through facade | Precedent: UI already imports FleetSpeedCalculator/ShipStatsCalculator directly. Facade is for commands (writes), not query utilities (reads). |
| 2026-02-23 | Service uses static methods following FleetCargoProjector pattern | Stateless utility — no instance state needed, easy to test |
| 2026-02-23 | Fix all 12 failures across 5 files, not just cargo dialog tests | All failures are in scope since they're all in unit.ui.screens and share common root causes (inadequate mock setup) |
| 2026-02-23 | Clean up 18 DIAG log statements from cargo_quick_dialog.py | Leftover debug instrumentation polluting production logs |
| 2026-02-23 | TransferDialog `_session` access and debug label are out of scope | Separate concern — note in design.md but don't fix in this project |
