# PROJ-298: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | Finish the Fleet/Planet*Order → Order migration started in archived PROJ-238. Confirmed via 2026-04-26 code review (claim 1.4a) |
| 2026-04-26 | Split out from PROJ-297 (companion project) | Original code review proposed bundling everything into one project. User selected "Split into Phase A + new PROJ-297" via AskUserQuestion. PROJ-298 is the dedicated FleetOrder rename; PROJ-297 is the smaller cleanups |
| 2026-04-26 | Symbol-level renames only — `fleet_orders` variable/function/file names stay | `fleet_orders` is a sensible domain term (the orders attached to a fleet) and not synonymous with the deprecated `FleetOrder` class. Renaming would create churn without value |
| 2026-04-26 | `fleet_id` field name (`commands.py:95`) is OUT OF SCOPE | Field-level rename touches serialized command data and save files; deeper risk than symbol-level renames. Separate project if desired |
| 2026-04-26 | Save-file compatibility is NOT required | Per CLAUDE.md: "Save files are disposable. Old saves are not migrated — they are discarded." |
| 2026-04-26 | `Tracking/`, `Reviews/results/`, `Projects/deep_archive/`, `coverage.json` are NOT renamed | Historical record should not be retroactively edited; aliases existed at the time, so historical mentions are accurate |
| 2026-04-26 | Original review's "726 usages" figure is unfiltered | Includes archives/Tracking/Reviews. True production+test count is smaller; Phase 1 will produce the filtered figure |
| 2026-04-26 | Code review missed `PlanetOrder` and `FleetOrdersWindow` aliases | Cross-checked grep before scoping. Project includes both. Original review only listed `FleetOrder` + three command aliases |
