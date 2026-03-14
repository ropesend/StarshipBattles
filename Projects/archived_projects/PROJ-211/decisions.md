# PROJ-211: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-27 | Project created from DI inconsistency review | Review deployed 5 analysts + 3 validators (8 agents). Found ~59 raw findings across strategy, simulation, UI, test isolation, and architecture. 3 rejected, 8 downgraded by validators. |
| 2026-02-27 | 5-phase architecture-driven ordering | Architecture reviewer's roadmap orders phases by DI flow (foundation first, then data objects, init functions, UI services, leaf UI). This minimizes churn vs. severity-based ordering. |
| 2026-02-27 | VehicleClassService is the gold standard | Requires `registry_provider`, raises `ValidationException` if None. All services should match this pattern. |
| 2026-02-27 | Simulation test `get_default_registry_provider()` after `isolated_registry` is acceptable | Validators confirmed: sim tests using global accessor after `isolated_registry` fixture hydrates the singleton is the intended post-PROJ-181 pattern. Not a defect. |
| 2026-02-27 | StrategyMetadataService.instance() is acceptable | Read-only metadata singleton at UI boundary. Not part of mutable registry DI system. DI-UI-009/010 excluded from scope. |
| 2026-02-27 | Phase 2 (ShipInstance/Fleet) is the complex phase | 20+ call sites for get_calculated_stats(), Fleet constructed in many places. All other phases are Simple effort. |
| 2026-02-27 | Remove silent error swallowing in Facade | DI-S-004: The broad try/except in get_fleet_remaining_pods() masks real failures. Remove it, let errors propagate. |
