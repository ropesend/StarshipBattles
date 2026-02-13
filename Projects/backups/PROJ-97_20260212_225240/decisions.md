# PROJ-97: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Project initialized | Starting point for Per-Resource Production Rate Limits for Build Queues |
| 2026-02-10 | Use JSON config file (`data/production_rates.json`) for planet yard rates, not hidden planet component | Hidden component approach is architecturally problematic: all engines iterate `planet.facilities` without filtering, maintenance would apply, UI would show it. JSON is simpler now and designed for easy migration to "Planetary Base" complex later. User accepted this approach. |
| 2026-02-10 | Per-turn cap rate model (not proportional spreading) | A 5500-metal item at 3000/turn = 3000 consumed turn 1, 2500 consumed turn 2. The bottleneck resource determines total turns. Non-bottleneck resources are capped to their per-turn max. User selected this as recommended approach. |
| 2026-02-10 | Remove ResourceStorage from shipyard components | Confirmed dead code by exhaustive swarm search: never read by ProductionEngine, HarvestingEngine, MaintenanceEngine, ResupplyEngine, any UI screen, or any test. Safe to remove. |
| 2026-02-10 | Zero changes to ProductionEngine | ProductionEngine only reads `cost_per_tick` from queue items, never `build_rate`. Rate limiting is fully handled at queue creation time via `_build_cost_tracking()`. |
| 2026-02-10 | Add `production_rates` field to SpaceShipyardAbility | Allows each shipyard component to define its own per-resource rates in components.json, with fallback to production_rates.json defaults. `construction_speed_bonus` acts as a multiplier on all rates. |
