# PROJ-20: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-26 | Project initialized | Starting point for Standardize Data Formats |
| 2026-01-26 | No save game migration | Per legacy cleanup README, backward compatibility for save files is NOT a concern |
| 2026-01-26 | 4-phase approach | Ordered by risk and dependency: (1) Production Queue, (2) Fleet Ships, (3) Design/Tech, (4) Legacy Stats |
| 2026-01-26 | Phase 4 last | Legacy stats affect 33 files; thorough testing needed after simpler phases complete |
| 2026-01-26 | Replace get_ship_instances() with fleet.ships | Direct access is cleaner; no need for filtering method when ships are always ShipInstance |
| 2026-01-26 | Production dict format only | `{"design_id": ..., "type": ..., "turns_remaining": N}` is already used by production code |
