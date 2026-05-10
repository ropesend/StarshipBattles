# PROJ-69: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-07 | Project initialized | Starting point for Multi Build Queue Restructure |
| 2026-02-07 | Each shipyard facility = 1 build queue | User confirmed: each shipyard on a planet generates its own independent queue |
| 2026-02-07 | Planet always has 1 base queue + shipyard queues | User confirmed: base queue handles complexes (always available), shipyard queues handle ships+complexes |
| 2026-02-07 | Multi-select adds to ALL selected queues | User confirmed: design gets appended to every selected queue independently |
| 2026-02-07 | Independent parallel processing | User confirmed: each queue processes its front item independently each turn. 2 queues = 2 items building simultaneously |
| 2026-02-07 | Keep full-screen modal layout | User confirmed: reorganize panels within existing modal, add queue selector column |
| 2026-02-07 | Auto-generated queue names | User confirmed: names derived from entity + facility type + index, not user-editable |
| 2026-02-07 | Queues disappear when source removed | User confirmed: no "inactive/paused" display state for queues without valid source |
| 2026-02-07 | PlanetaryFacility gets construction_queue field | Simplest approach - queue is intrinsically tied to the facility that provides it |
| 2026-02-07 | Introduce BuildQueueSource data class | Lightweight abstraction to represent a single queue source, avoids heavy protocol changes |
| 2026-02-07 | collect_build_queues_at_hex() utility function | Clean separation of queue discovery logic from UI, enables testing independently |
| 2026-02-07 | Save files are disposable | Per CLAUDE.md policy - no migration code needed for old saves |
| 2026-02-07 | Fleet keeps single queue (no change) | Each fleet has at most one space yard, so one queue per fleet is correct |
| 2026-02-07 | Base queue only processes complexes | Ships in base queue would be stuck without shipyard; base queue restricted to complex type |
