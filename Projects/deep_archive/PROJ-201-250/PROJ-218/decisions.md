# PROJ-218: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-28 | Project initialized | Starting point for Fix Production Queue Cost and Build Time Defaults |
| 2026-02-28 | Use Ship-loading approach (not simple registry lookup) | Component costs include formula-based values (e.g., `=50 * sqrt(ship_class_mass / 1000)`) and modifier multipliers (`cost_mult`). Only a loaded Ship object accurately calculates these. User explicitly requested costs reflect actual components and modifiers. |
| 2026-02-28 | Replace broken `calculate_total_cost()` entirely | Per CLAUDE.md: "When new system replaces old, ERADICATE the old completely." The old method has never worked for real design files — only passed tests because test data used inline `resource_cost`. |
| 2026-02-28 | Delete `Planet.add_production()` | Only called by 2 integration tests. Creates incomplete queue items without cost tracking. Per CLAUDE.md eradication policy — new system (AddToConstructionQueueCommand) fully replaces it. |
| 2026-02-28 | No save migration | Per CLAUDE.md: "Save files are disposable." Old saves with empty `total_cost` will have items skipped by hardened validation. |
| 2026-02-28 | Bug not caused by DI | Root cause is `DesignCostCalculator` assuming inline `resource_cost` in design JSON, which never existed. DI infrastructure actually helps the fix — `session.registries` provides clean registry access. |
