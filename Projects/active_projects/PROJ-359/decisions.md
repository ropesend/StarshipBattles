# PROJ-359: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project ID = PROJ-359 | User-directed sequence start at 356; this is #4 of 5 (largest). |
| 2026-05-04 | Project created from realtime-combat tech-debt review | Review finding #4 (P2 extensibility, largest leverage). |
| 2026-05-04 | Manual scaffolding (not via `create_project.py`) | Folder pre-existed with `plan.md`. Mirrored canonical templates. |
| 2026-05-04 | Opted into 03c phase-aware execution | Per `.claude/skills/claude-proj-start/SKILL.md` Phase D. Phase dependencies captured in each checklist. |
| 2026-05-04 | Four-phase split (golden / contract / migrate / delete) | Strict TDD; cross-cutting refactor risk; per-family migration enables one-file rollback. |
| 2026-05-04 | Sequence AFTER PROJ-356 / 357 / 358 | Smaller correctness fixes first; this is the only structural refactor in the batch and benefits from the test infrastructure those projects build out. |
| 2026-05-04 | Sequence BEFORE PROJ-360 | ShipStatsCalculator decomposition (PROJ-360) may want to consume the typed contract once it lands. |
| 2026-05-04 | Defer specific contract shape | `AttackRequest` / `AttackResolution` field set is best decided in Phase 2 against the actual call sites; do not over-specify in plan.md. |
