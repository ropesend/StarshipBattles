# PROJ-74: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-07 | Project initialized | Starting point for Resupply System |
| 2026-02-07 | Resupply timing: Continuous (per-tick) | User preference for realistic simulation where ships refuel gradually during turn |
| 2026-02-07 | Production: Accumulate in tanks | Fuel synthesizer fills complex tanks; ships draw from storage. More realistic than instant production. |
| 2026-02-07 | Priority: Owner first | Complex owner's fleets refuel before other fleets. Prevents enemy from stealing fuel. |
| 2026-02-07 | Fleet distribution: Equalize range | Each ship gets fuel for same hex range. Tankers may be partial, combat ships fully fueled. User specified this requirement. |
| 2026-02-07 | Phase placement: Phase 0 (before movement) | Ships refuel then move with full tanks. Placed alongside ResourceManagementEngine for consistency. |
| 2026-02-07 | Initial output rate: 300/turn | Mid-range value (user specified 200-500). Configurable in components.json. |
| 2026-02-07 | Use existing fuel_tank component | Fuel tank already has `allowed_vehicle_types: ["Ship", "Satellite", "Planetary Complex"]`. No modification needed. |
| 2026-02-07 | Add resource_levels to PlanetaryFacility | Currently has no mechanism to track current fuel. Following ShipInstance.resource_levels pattern. |
| 2026-02-07 | Follow ResourceManagementEngine pattern | Use strict DI with GameRegistries, TypeError if None. Proven pattern in codebase. |
