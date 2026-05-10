# PROJ-79: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-08 | Project initialized | Starting point for Build Queue Screen & Production System Rework |
| 2026-02-08 | Planetary Yard build rate: 2000 units/turn per resource | User specified. Every planet has a default Planetary Yard that can only build complexes. |
| 2026-02-08 | Shipyard build rate: 3000 units/turn per resource | User specified. Shipyards (on planet or fleet) can build ships + complexes. Rate comes from SpaceShipyard component. |
| 2026-02-08 | Proportional resource consumption | Most expensive resource determines turns. Others consume proportionally. E.g., 100k Metals + 10k Organics at 2000/turn = 50 turns, consuming 2000 Met + 200 Org per turn. |
| 2026-02-08 | Tick-granular production completion | Items complete at exact tick when resources_consumed >= total_cost, not at end-of-turn. Next item in queue starts processing on the very next tick. |
| 2026-02-08 | Mid-turn spawned facilities produce proportionally | User wants completed harvesters to produce for remaining fraction of turn. Storage facilities also recalculate capacity immediately. |
| 2026-02-08 | Planet selection popup appears immediately | When a fleet shipyard at a multi-colony hex queues a complex, the PlanetSelectionWindow popup appears immediately to choose target planet. |
| 2026-02-08 | Reuse PlanetSelectionWindow for complex target selection | Generalize PlanetSelectionWindow with parameterized title, label, and "Any Planet" button visibility. Both colonization and complex-target flows use same class. |
| 2026-02-08 | Use existing resource portrait icons | Icons at `assets/Images/Resource Portraits/` (5 PNGs). Load as 20x20 icons for column headers in build queue display. |
| 2026-02-08 | Rename "Build Queues" to "Build Yards" | User requested. Reflects the distinction between Planetary Yards (complexes only) and Shipyards (can build anything). |
| 2026-02-08 | Display names: "Planetary Yard" and "Shipyard" | Base queue -> "Planet Name - Planetary Yard". Facility queue -> "Planet Name - Shipyard N". Fleet queue -> "Fleet Name - Shipyard". |
| 2026-02-08 | Legacy queue items (no cost tracking) fall through to end-of-turn processing | Existing save games have queue items without cost_per_tick fields. The tick processor skips these. End-of-turn process_production() still handles them with 1-turn decrement. No migration needed. |
