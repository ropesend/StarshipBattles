# PROJ-288: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Project initialized | Starting point for Colony Output Projection Helpers |
| 2026-04-18 | `projected_growth_rate` returns per-capita rate (fraction), NOT absolute delta | Pure math; UI multiplies by count if it needs a population delta. Also lets the helper be reused by aggregation code that wants the rate directly. |
| 2026-04-18 | Helper DUPLICATES the math in `PopulationEngine._grow_species` rather than refactoring the engine to share code | Engine mutates state; helper doesn't. Merging them requires careful type / clamping review. Phase 1 adds an equivalence integration test that pins the two outputs must agree on identical inputs — if they drift, CI fails. |
| 2026-04-18 | `compute_planet_production` moves from `game/ui/panels/planet_report_panel.py` to `game/strategy/services/planet_economy_projector.py` | Non-UI services shouldn't import from UI. Current placement is a layer violation per docs/01_ARCHITECTURE.md. PROJ-288 fixes it. |
| 2026-04-18 | `PlanetEconomyProjector.project(planet)` returns `Dict[resource_id, ResourceProjection]` | Dict rather than list-of-tuples so UI can lookup specific resources efficiently. Frozen dataclass per-entry so the DTO is immutable. |
| 2026-04-18 | Yard projection uses MAX per-turn drain (assumes queue runs the full turn) | More pessimistic than the "item might complete mid-turn" case. Avoids flickering UI numbers. Documented; callers who want more precision can recompute. |
| 2026-04-18 | No per-turn caching on projections in v1 | O(species + resources + queues) per call is cheap. Adding cache introduces invalidation complexity. Profile first; optimize later. |
| 2026-04-18 | `ColonyDemographicView` species ordered largest-first | User confirmed sub-block layout for PROJ-289. Largest species is typically the most interesting. Ordering at the DTO level means all UI consumers see the same order. |
| 2026-04-18 | Blocked on PROJ-286 + PROJ-287 | Hard dependencies — consumes multi-resource `population_consumption` dict from PROJ-286 and `facade.get_race_registry()` / `Empire.resident_species()` from PROJ-287. Do not begin until both land. |
| 2026-04-18 | PROJ-289 and PROJ-290 are downstream consumers; both must wait for PROJ-288 | Both depend on `ColonyDemographicView` / `PlanetEconomyProjector` / `projected_growth_rate`. |
