# PROJ-360: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project ID = PROJ-360 | User-directed sequence start at 356; this is #5 of 5. |
| 2026-05-04 | Project created from realtime-combat tech-debt review | Review finding #5 (P2 maintainability): `ShipStatsCalculator` is monolithic and over the 500 LOC convention. |
| 2026-05-04 | Manual scaffolding (not via `create_project.py`) | Folder pre-existed with `plan.md`. Mirrored canonical templates. |
| 2026-05-04 | Opted into 03c phase-aware execution | Per `.claude/skills/claude-proj-start/SKILL.md` Phase D. |
| 2026-05-04 | Three-phase split (golden / extract behind API / replace hardcoded checks) | Strict TDD; preserve mutation-order semantics; mechanical extraction first, semantic replacement second. |
| 2026-05-04 | Sequence AFTER PROJ-359 | PROJ-359 introduces typed weapon contracts that some weapon/defense contributors will want to consume. |
| 2026-05-04 | `ship_design_stats.py` and `combat_endurance.py` excluded | Each has its own complexity score; not the immediate target. Surface as follow-ups if PROJ-360 reveals natural extraction points. |
| 2026-05-04 | Contributor module location TBD | Likely `game/simulation/entities/stat_contributors/` to mirror `combat/families/` from PROJ-359; finalize in Phase 2 once the first split lands. |
