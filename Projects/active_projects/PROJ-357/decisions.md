# PROJ-357: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project ID = PROJ-357 | User-directed sequence start at 356; this is #2 of 5. |
| 2026-05-04 | Project created from realtime-combat tech-debt review | Review finding #2 (P1 correctness): same-class multi-provider aura disable leaves stale value active. |
| 2026-05-04 | Manual scaffolding (not via `create_project.py`) | Folder pre-existed with `plan.md` from initial scaffold. Mirrored canonical templates from `Projects/scripts/create_project.py` and `Reviews/scripts/review_to_project.py`. |
| 2026-05-04 | Opted into 03c phase-aware execution | Per `.claude/skills/claude-proj-start/SKILL.md` Phase D, default for new projects. |
| 2026-05-04 | Two-phase split: characterization then rework | Strict-TDD per AGENTS.md — golden tests for current single-provider behavior must lock in before identity rework. |
| 2026-05-04 | Identity choice deferred to Phase 2 | Need to choose between (component id + ability instance index) vs (ability instance reference + "still present" check). Decision belongs with the rework, not in plan.md scaffolding. |
