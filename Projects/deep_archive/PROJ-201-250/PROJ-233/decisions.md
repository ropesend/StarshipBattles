# PROJ-233: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-28 | Project initialized | Starting point for Refactor ProductionEngine - Extract Oversized Methods and Deduplicate Spawn Logic |
| 2026-03-28 | Don't split `_process_queue_tick_dynamic` further | Already well-decomposed by PROJ-209; helpers are tightly coupled to the loop. Max nesting is 3 levels. The function reads well despite being 102 lines. |
| 2026-03-28 | Extract spawner as class, not free functions | Spawner needs `_registries` state for `ShipInstance.create()` and `DesignCostCalculator`; class is the natural container. Follows existing Delegate pattern (like Fleet delegates). |
| 2026-03-28 | Inline `_spawn_complex` rather than move it | It's a 1-line delegation to `_create_and_place_facility()` with identical args. Moving adds complexity; inlining eliminates a method. |
| 2026-03-28 | Use `ticks_per_turn=1` for forecast's call to shared formula | Forecast works in turn fractions, not tick fractions. Passing `ticks_per_turn=1` means `remaining / rate` gives turns directly, making the forecast code cleaner. Verified: `remaining / (rate / 1) = remaining / rate`, same as the original inline code. |
| 2026-03-28 | Keep 30-line fleet queue comment as 2-line summary | The conclusion is clear: multiple yards = more speed on a single queue, not parallel queues. The implementation at lines 193-196 already reflects this (`total_rate = base_rate * yard_count`). The 30-line comment is design-discovery notes from original implementation. |
| 2026-03-28 | Leave fleet resolution boilerplate out of scope | The 3-line `_resolve_fleet` + error check pattern is explicit, well-tested, and consistent with the codebase's Protocol+mixin style. Abstraction cost exceeds benefit. (Noted during code review as a separate potential target — PROJ-232.) |
| 2026-03-28 | Remove `harvesting_engine` from IProductionEngine | Parameter was removed from `ProductionEngine.process_construction_tick()` in PROJ-161. `TurnEngine` does not pass it. The interface is stale — two mock implementations need updating. |
| 2026-03-28 | QueueItemAction as Enum, not string constants | String constants would work but Enum provides: IDE autocomplete, typo protection, and explicit type in function signature. Low cost, high benefit. |
| 2026-03-28 | Phase ordering: enum → formula → spawner → cleanup → types | Lowest risk first. Enum and formula are isolated. Spawner extraction (Phase 3) is highest impact but also highest test churn — do it after simpler phases validate the approach. Types last since they're informational. |
