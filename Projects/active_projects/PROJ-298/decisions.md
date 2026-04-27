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
| 2026-04-26 | Phase 1 discovered SIXTH alias: `FleetOrderSerializer = OrderSerializer` at `order_serializer.py:235` | Found during Phase 1 inventory grep. Production callers in `game/strategy/data/fleet.py` (7 usages) and tests (`test_roundtrip_orders.py`, 9 usages) still use the old name. Added to Phase 2/3 rename scope and Phase 4 deletion list. Same migration cadence as the other aliases. |
| 2026-04-26 | Phase 1 discovered `FleetOrder` re-export in `game/strategy/__init__.py` | Lines 13 (docstring), 34 (import), 64 (`__all__`). Added to Phase 4 deletion scope. |
| 2026-04-26 | Single `FleetOrderProcessor` runtime log message at `order_processor.py:770` IS in scope | The log message uses the old class name in a runtime-emitted string. Rename to `OrderProcessor`. The module docstring at line 4 (`PROJ-238: Renamed from FleetOrderProcessor.`) is historical — KEEP. |
| 2026-04-26 | Implementation will use IDE find-and-replace (whole word, case-sensitive), file by file | `findings/rename_plan.md` orders the work. Bulk regex sed risks corrupting the 1-of-684 case where a substring overlaps something else. The cost of careful per-file work is much less than the cost of one corruption. |
