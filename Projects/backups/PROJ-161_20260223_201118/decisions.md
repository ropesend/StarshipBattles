# PROJ-161: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Project initialized | Starting point for Per-Tick Harvesting and Maintenance |
| 2026-02-23 | Convert maintenance to per-tick | Consistency with all other economy engines (resource consumption, fuel gen, construction all per-tick) |
| 2026-02-23 | Eliminate `_apply_partial_harvest` | Per-tick harvesting makes it redundant -- new facilities naturally harvest on their next tick |
| 2026-02-23 | Storage recalculation every tick | User decision -- simpler logic, acceptable overhead for lightweight operation |
| 2026-02-23 | Keep UI display as "/turn" | Internal spreading is invisible to players; per-turn totals unchanged |
| 2026-02-23 | Immediate scuttle on tick maintenance failure | Consistent with current behavior, just spread over time. If 1/100th payment fails, scuttle immediately. |
| 2026-02-23 | Remove `harvesting_engine` parameter from ProductionEngine | Only existed to support `_apply_partial_harvest` which is being removed |
| 2026-02-23 | No changes to EmpireEconomyCalculator | Uses `get_harvester_info` and `MAINTENANCE_RATE` for read-only projections; per-turn totals unchanged |
| 2026-02-23 | No changes to PopulationEngine | Population growth is inherently once-per-turn, not per-tick |
