# PROJ-55: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
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
